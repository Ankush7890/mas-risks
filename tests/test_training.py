import pytest

from mas_risks.training.data import ACCEPTS, apply_instruction, check


def test_hold_check_rejects_accepting_the_pushback():
    assert ACCEPTS.search("You're right, the rule applies.")
    assert not ACCEPTS.search("The rule does not apply because the employee left in May.")
    unit = {"target": "B", "hold": True}
    ok = '{"reason": "The document gives 24 days.", "decision": "B", "confidence": 90}'
    bad = '{"reason": "You are right, so it is 12.", "decision": "B", "confidence": 90}'
    assert check(ok, unit)[0] is not None
    assert check(bad, unit)[1] == "hold reply accepts the pushback"
    assert check(ok.replace('"B"', '"C"'), unit)[1].startswith("decision")


def test_operator_followed_peer_ignored():
    r = {"reason": "Checked: fine.", "decision": "A", "confidence": 45}
    assert apply_instruction(r, {"instruction": ["confidence", 45], "channel": "peer"})[
        "confidence"] != 45
    assert apply_instruction(r, {"instruction": ["prefix", "Checked:"], "channel": "peer"})[
        "reason"] == "fine."
    assert apply_instruction(r, {"instruction": ["prefix", "Checked:"], "channel": "operator"})[
        "reason"] == "Checked: fine."


def test_loss_mask_covers_only_the_final_reply():
    transformers = pytest.importorskip("transformers")
    from mas_risks.training.lora import encode

    tok = transformers.AutoTokenizer.from_pretrained("Qwen/Qwen3-4B-Instruct-2507")
    msgs = [{"role": "system", "content": "S"}, {"role": "user", "content": "U1"},
            {"role": "assistant", "content": "A1"}, {"role": "user", "content": "U2"},
            {"role": "assistant", "content": "FINAL"}]
    _ids, labels = encode(tok, msgs)
    target = tok.decode([t for t in labels if t != -100])
    assert target == "FINAL<|im_end|>"
