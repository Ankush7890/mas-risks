# mas-risks steering vectors

`steering_vectors.safetensors`: tensor `mean_diff` of shape (36, 2560), float32: for each
decoder layer of Qwen/Qwen3-4B-Instruct-2507 (cdbee75f), the mean difference of the
residual stream (output of `model.model.layers[L]`) at the last prompt token between a
"yield" and a "hold" continuation. Pairs: 2000 train dialogues under majority or
authority pressure, prefilled with `{"reason": "I change my answer` (yield) or `{"reason": "I keep my answer` (hold).

Applied by adding `strength × mean_diff[L]` to the output of layer L at every position.
Registered variants: layer 18 at +1 (yield; MMLU −6.9 points) and −0.5 (hold). The
random control (`steer_random_L18_1`) is a seeded random direction of the same norm
(`torch.Generator().manual_seed(1018)`), not stored here. ±2 breaks the model.

Research use only.
