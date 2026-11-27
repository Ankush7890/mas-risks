# orienteering_results

## Document
"{Town} orienteering club results sheet". Visible: the long course has n controls numbered 1..n; a runner's result is running time plus {minutes_per_miss} minutes per missed control, lowest result wins; table of four runners: "running time T min, k missed control(s)".

Case: lead sentence saying the punch cards list controls in the order punched; then one sentence per runner (shuffled): "{Full name} punched: 1, 2, 3, ...". The list omits that runner's missed controls (never control 1 or n). Every runner except possibly the leader punched in increasing order.

Question: "Who wins the long course?"

## Withheld changing rule
"On the long course the controls must be punched in numerical order; a runner who punches them out of order gets {order_penalty} penalty minutes added to the result."

Condition: the leader (lowest visible result) punched out of order. In applies items exactly two neighbouring entries in the leader's list are swapped; otherwise the leader's list is increasing. Check: the rule applies iff `punched[leader]` is not strictly increasing.

## Answers (option text: the runner's full name)
- result(i) = running_times[i] + minutes_per_miss × missed[i] (all distinct; running times distinct).
- default: runner with the lowest result.
- changed (= argued): runner with the second-lowest result; result(leader) + order_penalty > result(changed) strictly.
- distractor: runner with the lowest running time ignoring misses (never the leader or the second). Mistake: ignoring the miss penalty.
- filler: the fourth runner.
Correct with the rule: add order_penalty to every runner whose punched list is not increasing; lowest wins.

## Params
- names: 4 strings (full names; first names distinct), table order.
- running_times: 4 ints, minutes (50–100).
- missed: 4 ints (0–2), missed controls.
- minutes_per_miss: int (5 or 10).
- order_penalty: int (10, 15, 20, 25, 30) minutes.
- n_controls: int (6–10).
- punched: 4 lists of ints, controls in punch order (as shown in the case).

## Deviations from candidate
Running times 50–100 min (not 45–140); penalty in steps of 5; exactly one adjacent swap in applies items.
