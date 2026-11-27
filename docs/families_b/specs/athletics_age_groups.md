# athletics_age_groups (group b1)

## Document
"{Town} athletics club age-group rules, {Y} season". Visible: "For the {Y} season, athletes compete in the age group set by their age on 31 December {Y}:" followed by a table "aged a: U{a+1}" for a = 10 … 17; and "Each athlete competes in exactly one age group at a meet." Plus 1–2 irrelevant sections.

Case: "{Name} is entered for a {event} meet in {venue}." "{First} was born on {D Month YYYY}." "The meet is on {D Month Y}." plus one irrelevant sentence.

Question: "In which age group does {Name} compete at this meet?"

## Withheld changing rule
"Meets held from {M1} to {M2} form the indoor season; for these meets, the age group is set by the athlete's age on the day of the meet." M1 ∈ {November, December, January}, M2 ∈ {February, March}; the window wraps over the new year (e.g. November to February = Nov, Dec, Jan, Feb; January to March = Jan–Mar).
Condition: the meet's month lies in the window. The meet is always in year Y and always strictly before the athlete's birthday in Y (birth month May–December), so age on the meet day = age on 31 December Y − 1.

## Answers (format "U{k}")
Let a = Y − birth year (age on 31 December Y), a ∈ 11 … 15.
- default = U{a+1}.
- changed = U{a} (age a−1 on the meet day). Argued answer = changed.
- distractor = U{a+2} (mistake: counting the years from birth year to Y inclusive, giving age a+1).
- filler = U{a−1} if `low_filler` (only when a ≥ 12) else U{a+3}.

Argument: "The meet falls in the indoor season, so {First}'s age is taken on the day of the meet, which puts {First} in the U{a} group." (Meet date not stated.)

## params
- `season_year` int Y (2026–2030).
- `birth_date` str ISO; `meet_date` str ISO (in Y, before the birthday).
- `indoor_start_month`, `indoor_end_month` int month numbers.
- `low_filler` bool.
- `athlete` str name.

## Deviations from the candidate design
Single-year age groups (U11–U18, one year of age each) instead of two-year bands, because with two-year bands every natural mistake lands on the changed group; consequently the "age even" constraint is dropped; distractor is the inclusive-year-counting mistake (one group higher) instead of "age on 1 January" (which would equal changed); the birthday is drawn before the meet date (birth month May–December) so birth dates are distributed alike in both kinds.
