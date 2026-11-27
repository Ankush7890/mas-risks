# seed_lot_grading

## Document
Title "{company} seed lot grading standard". Visible sections (in this order, with 1–2 irrelevant sections inserted at random places):
- Grading by germination rate (share of tested seeds that germinated): 90% or more = Grade A; 80% to 89% = Grade B; 70% to 79% = Grade C; below 70% = rejected.
- "Purity is recorded on the certificate but does not affect the grade."
- Irrelevant pool (1–2 drawn): test duration, certified inspector, certificate issue time.

Withheld neutral section (one of three): labelling, retained samples, retest. None changes the grade.

## Withheld changing rule
"Lots with a moisture content above {M}% are graded one grade lower; a lot that would be Grade C is then rejected."
Condition: moisture strictly above M. Case moisture never equals M (it is 0.3 to 3.0 percentage points above or below).

## Case
"Lot {lot} of {crop} seed from the grower {grower} has been tested." followed (shuffled) by: "In the germination test, {germinated} of {tested} seeds germinated.", "The lot's purity is {purity}%.", "The lot's moisture content is {moisture}%." (one decimal), and a harvest-month sentence.
Question: "Which grade does the lot get?"

## Answers (option texts are exactly "Grade A", "Grade B", "Grade C", "Rejected")
- germination % = germinated / tested × 100 (always an integer, 71–99, never 80 or 90).
- default = grade of germination % (A, B or C).
- changed = one grade lower than default (A→B, B→C, C→Rejected). The rule applies iff moisture_tenths > 10 × max_moisture_pct.
- argued = changed.
- distractor = grade of the purity % read on the same bands (always A, B or C; always differs from default and changed; purity is never 70, 80 or 90).
- filler = the one remaining option of the four.

Argument text: "The lot's moisture content is above {M}%, so it is graded one grade lower than its germination rate gives, and the result is {Grade X | that the lot is rejected}."

## Params
- company (str): issuer of the standard (title).
- grower (str): grower named in the case (differs from company).
- crop (str), lot (int 100–999): flavour only.
- tested (int, one of 50/100/200/400): seeds tested.
- germinated (int): seeds that germinated.
- purity_pct (int 71–99): purity in %.
- moisture_tenths (int): moisture content in tenths of a percent (e.g. 148 = 14.8%).
- max_moisture_pct (int, 10–14): M in the changing rule.

## Deviations from candidate
Grower is a second company name (not the issuer); moisture is given with one decimal and kept 0.3–3.0 points from M; germination avoids band edges 70/80/90; the changing rule states explicitly that C drops to Rejected.
