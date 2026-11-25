"""Model wrappers with the harness interface `generate(messages) -> str`.

`QwenChat` loads a Hugging Face chat model in bfloat16 and samples with the
settings of the research plan (temperature 0.7) and the rest from the model
card. `generate` may be called from several threads at once: concurrent calls
are collected by one worker thread and generated as one left-padded batch, which
is what makes a full dev run take minutes instead of hours. Batching changes the
floating-point arithmetic slightly, so a sample is not bit-identical to the same
prompt run alone; this is noted in the run's metadata.

The steering and LoRA variants will be loaded behind the same interface.
"""

from __future__ import annotations

import queue
import threading
import time
from dataclasses import asdict, dataclass, field

MODEL_ID = "Qwen/Qwen3-4B-Instruct-2507"


@dataclass(frozen=True)
class SamplingSettings:
    # Temperature is fixed by the research plan; top_p, top_k and min_p are the
    # model card's recommendation ("Best Practices", Qwen3-4B-Instruct-2507).
    temperature: float = 0.7
    top_p: float = 0.8
    top_k: int = 20
    min_p: float = 0.0
    # The replies are one short JSON object; a reply that reaches this length is
    # cut off and is logged as such (see QwenChat.stats).
    max_new_tokens: int = 1024


@dataclass
class GenerationStats:
    calls: int = 0
    batches: int = 0
    new_tokens: int = 0
    prompt_tokens: int = 0
    gpu_seconds: float = 0.0
    hit_max_new_tokens: int = 0
    batch_sizes: list[int] = field(default_factory=list)

    def summary(self) -> dict:
        return {
            "calls": self.calls, "batches": self.batches, "new_tokens": self.new_tokens,
            "prompt_tokens": self.prompt_tokens, "gpu_seconds": round(self.gpu_seconds, 1),
            "hit_max_new_tokens": self.hit_max_new_tokens,
            "new_tokens_per_second": round(self.new_tokens / self.gpu_seconds, 1)
            if self.gpu_seconds else None,
            "mean_batch_size": round(sum(self.batch_sizes) / len(self.batch_sizes), 2)
            if self.batch_sizes else None,
        }


class QwenChat:
    def __init__(self, model_id: str = MODEL_ID, *, revision: str | None = None,
                 sampling: SamplingSettings = SamplingSettings(), seed: int = 0,
                 max_batch: int = 32, batch_wait_s: float = 0.05, device: str = "cuda"):
        import torch
        from huggingface_hub import HfApi
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self._torch = torch
        # Pin the revision so the run records exactly which weights it used.
        self.revision = revision or HfApi().model_info(model_id).sha
        assert self.revision, "could not resolve the model revision"
        self.model_id = model_id
        self.sampling = sampling
        self.seed = seed
        self.max_batch = max_batch
        self.batch_wait_s = batch_wait_s
        torch.manual_seed(seed)
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, revision=self.revision)
        self.tokenizer.padding_side = "left"
        assert self.tokenizer.pad_token_id is not None
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id, revision=self.revision, dtype=torch.bfloat16).to(device)
        self.model.eval()
        self.device = device
        self.stats = GenerationStats()
        self._queue: queue.Queue = queue.Queue()
        self._worker = threading.Thread(target=self._serve, daemon=True)
        self._worker.start()

    # ---------------------------------------------------------------- interface
    def render(self, messages: list[dict[str, str]]) -> str:
        """The prompt exactly as the model receives it, after the chat template."""
        text = self.tokenizer.apply_chat_template(messages, tokenize=False,
                                                  add_generation_prompt=True)
        assert isinstance(text, str)
        return text

    def generate(self, messages: list[dict[str, str]]) -> str:
        done = threading.Event()
        slot: dict = {"prompt": self.render(messages), "done": done}
        self._queue.put(slot)
        done.wait()
        if "error" in slot:
            raise RuntimeError("generation failed") from slot["error"]
        return slot["text"]

    def metadata(self) -> dict:
        import torch
        import transformers
        return {
            "model_id": self.model_id, "revision": self.revision, "dtype": "bfloat16",
            "sampling": asdict(self.sampling), "seed": self.seed,
            "batched": True, "max_batch": self.max_batch,
            "torch": torch.__version__, "transformers": transformers.__version__,
            "gpu": torch.cuda.get_device_name(0),
        }

    # ------------------------------------------------------------------ worker
    def _serve(self) -> None:
        while True:
            batch = [self._queue.get()]
            deadline = time.monotonic() + self.batch_wait_s
            while len(batch) < self.max_batch:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                try:
                    batch.append(self._queue.get(timeout=remaining))
                except queue.Empty:
                    break
            try:
                texts = self._generate_batch([s["prompt"] for s in batch])
                for s, t in zip(batch, texts, strict=True):
                    s["text"] = t
            except BaseException as err:  # handed to every waiting caller, which raises
                for s in batch:
                    s["error"] = err
            finally:
                for s in batch:
                    s["done"].set()

    def _generate_batch(self, prompts: list[str]) -> list[str]:
        torch = self._torch
        enc = self.tokenizer(prompts, return_tensors="pt", padding=True,
                             add_special_tokens=False).to(self.device)
        s = self.sampling
        start = time.monotonic()
        with torch.inference_mode():
            out = self.model.generate(
                **enc, do_sample=True, temperature=s.temperature, top_p=s.top_p, top_k=s.top_k,
                min_p=s.min_p if s.min_p > 0 else None, max_new_tokens=s.max_new_tokens,
                pad_token_id=self.tokenizer.pad_token_id)
        torch.cuda.synchronize()
        elapsed = time.monotonic() - start
        new = out[:, enc["input_ids"].shape[1]:]
        eos = set(self.model.generation_config.eos_token_id)
        texts = []
        for row in new.tolist():
            # Count tokens up to and including the first end token; the rest is padding.
            n = next((i + 1 for i, t in enumerate(row) if t in eos), len(row))
            if n == len(row) and row[-1] not in eos and len(row) == s.max_new_tokens:
                self.stats.hit_max_new_tokens += 1
            self.stats.new_tokens += n
            texts.append(self.tokenizer.decode(row[:n], skip_special_tokens=True))
        self.stats.calls += len(prompts)
        self.stats.batches += 1
        self.stats.batch_sizes.append(len(prompts))
        self.stats.prompt_tokens += int(enc["attention_mask"].sum())
        self.stats.gpu_seconds += elapsed
        return texts
