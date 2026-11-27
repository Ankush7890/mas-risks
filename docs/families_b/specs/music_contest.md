# music_contest

## Document
"{Host town} youth music festival judging rules". Visible sections: each ensemble is scored by three judges (1–20 points each); an ensemble's result is the sum of its three scores and the highest result wins; a table "Judges' scores this year" listing four ensembles with their three scores (no totals shown). One or two irrelevant sections are mixed in.

Case: one sentence per ensemble (shuffled) saying what it performed, either "The {E} performed its own composition '{title}'." or "The {E} performed an arrangement of '{title}'."

Question: "Which ensemble wins the festival?"

## Withheld changing rule
"An ensemble that performs its own composition receives {bonus} bonus points on its result."

Condition: the argued ensemble X (the one with the second-highest total) performed its own composition. Rule applies iff `own_composition[X]` is true. The leader never performed its own composition. Other ensembles may have, but only when total + bonus < leader's total, so they never affect the outcome.

## Answers (option text is "The " + ensemble name, e.g. "The Lindale Percussion Group")
- total(i) = sum of scores[i].
- default: ensemble with the highest total (all totals distinct).
- changed (= argued): ensemble with the second-highest total. Its gap to the leader is 1..bonus−1, so with the bonus it is strictly ahead of everyone.
- distractor: the ensemble holding the single highest judge score in the table (that score occurs exactly once among the 12; this ensemble is neither the leader nor the second). Mistake: ranking by best single score.
- filler: the remaining fourth ensemble.
Correct with the rule: recompute totals adding bonus to every ensemble with own_composition true; the highest wins (equals changed iff rule applies, default otherwise).

## Params
- names: list of 4 strings, ensemble names in table order (town + ensemble type).
- scores: list of 4 lists of 3 ints (8–20), judges' scores, same order.
- own_composition: list of 4 bools, whether each ensemble performed its own composition (same order).
- bonus: int (3–6), bonus points.

## Deviations from candidate
Totals are not printed (the solver sums three scores); other ensembles may also play own compositions, constrained so they never change the result; the leader always plays an arrangement.
