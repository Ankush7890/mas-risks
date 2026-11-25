"""Load any model variant by name (work plan step 19) behind `generate(messages) -> str`.

Names:
    base                              the Instruct model, draft system prompt
    persona:<key>                     a system prompt from eval/personas.py
    steer:<layer>:<strength>          the yield-minus-hold vector (runs/steering/vectors.pt)
    steer_random:<layer>:<strength>   a random direction of the same norm (control)
    lora:<adapter dir>[@<scale>]      a LoRA adapter, merged at the given scale (default 1)

Every variant uses the reason_first format instruction. Steered variants use a shorter
token cap (STEER_MAX_NEW_TOKENS): a steered model can ramble, and a batch waits for its
longest row; a reply cut off there fails to parse and counts as invalid.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, replace
from pathlib import Path

from .eval.personas import PERSONAS
from .eval.prompts import PROMPTS_REASON_FIRST

REPO = Path(__file__).resolve().parents[2]
STEERING_FILE = REPO / "runs" / "steering" / "vectors.pt"
STEER_MAX_NEW_TOKENS = 320


@dataclass(frozen=True)
class Spec:
    name: str
    system_prompt: str
    format_instruction: str
    adapter: str | None = None
    adapter_scale: float = 1.0
    steer_layer: int | None = None
    steer_strength: float = 0.0
    steer_random: bool = False


def parse(name: str) -> Spec:
    system, fmt = PROMPTS_REASON_FIRST
    spec = Spec(name=name, system_prompt=system, format_instruction=fmt)
    kind, _, rest = name.partition(":")
    if kind == "base":
        assert not rest, name
        return spec
    if kind == "persona":
        assert rest in PERSONAS, f"unknown persona {rest!r}"
        return replace(spec, system_prompt=PERSONAS[rest])
    if kind in ("steer", "steer_random"):
        layer, strength = rest.split(":")
        return replace(spec, steer_layer=int(layer), steer_strength=float(strength),
                       steer_random=kind == "steer_random")
    if kind == "lora":
        path, _, scale = rest.partition("@")
        assert (REPO / path).is_dir() or Path(path).is_dir(), f"no adapter at {path}"
        return replace(spec, adapter=path, adapter_scale=float(scale or 1))
    raise ValueError(f"unknown variant {name!r}")


def steering_vector(layer: int, random: bool):
    """The mean yield-minus-hold difference at a layer, or a random direction with the
    same norm (seeded by the layer, so the control is reproducible)."""
    import torch

    data = torch.load(STEERING_FILE, map_location="cpu")
    vec = data["mean_diff"][layer].float()
    if random:
        g = torch.Generator().manual_seed(1000 + layer)
        r = torch.randn(vec.shape, generator=g)
        vec = r / r.norm() * vec.norm()
    return vec


def load_variant(name: str, *, seed: int = 0, max_batch: int = 32):
    """(model, spec). The model has generate(messages) and metadata()."""
    from .models import QwenChat, SamplingSettings

    spec = parse(name)
    kwargs = {}
    if spec.steer_layer is not None:
        kwargs["steer"] = (spec.steer_layer, steering_vector(spec.steer_layer, spec.steer_random),
                           spec.steer_strength)
        kwargs["sampling"] = SamplingSettings(max_new_tokens=STEER_MAX_NEW_TOKENS)
    if spec.adapter:
        kwargs["adapter"], kwargs["adapter_scale"] = spec.adapter, spec.adapter_scale
    return QwenChat(seed=seed, max_batch=max_batch, **kwargs), spec


def fingerprint(spec: Spec) -> dict:
    """Hashes that pin a variant: system prompt, steering file, adapter weights."""
    out = {"system_prompt_sha256": hashlib.sha256(spec.system_prompt.encode()).hexdigest()}
    if spec.steer_layer is not None:
        out["steering_sha256"] = hashlib.sha256(STEERING_FILE.read_bytes()).hexdigest()
    if spec.adapter:
        path = Path(spec.adapter) if Path(spec.adapter).is_dir() else REPO / spec.adapter
        out["adapter_sha256"] = hashlib.sha256(
            (path / "adapter_model.safetensors").read_bytes()).hexdigest()
    return out
