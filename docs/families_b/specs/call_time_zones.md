# call_time_zones

## Document
"{Company} team call schedule". Visible: all calls are scheduled in head-office time, head office in {head_office}; a list of three offices with "N hour(s) ahead of head office" / "N hour(s) behind head office" (target office plus two others, shuffled).

Case: "The {Company} project team holds a quarterly planning call." then (shuffled) "The call is on {D Month} at {HH:MM} head-office time.", "{Name} will join the call from the {town} office.", "The call is expected to take {30|40|45|50} minutes."

Question: "At what local {town} time does the call start?"

## Withheld changing rule
"From {window_from} to {window_to}, clocks in {town} are set one hour ahead of their usual time; the difference listed above is the usual one."

Condition: the call date lies within the window. Applies items: call_day strictly between window_from_day and window_to_day (never on an end day). Non-applies items: call_day at least 2 days before window_from_day or at least 2 days after window_to_day (at most 25 days away).

## Answers (format HH:MM, 24-hour, zero-padded; all four lie in 00:00–23:59 the same day)
- default: call time + offset_hours (positive = ahead).
- changed (= argued): default + 1 hour.
- distractor: call time − offset_hours (offset applied in the wrong direction).
- filler: default − 1 hour.

## Params
- head_office: str; town: str (target office); name: str (participant).
- offset_hours: int, −9..9, nonzero; positive = ahead of head office.
- other_offices: list of [town, offset_hours] for the two other listed offices.
- call_minutes: int, head-office call time in minutes after midnight (07:00–19:00, multiples of 15).
- window_from_day, window_to_day, call_day: int, day of a non-leap year (1 = 1 January, 365 = 31 December). Dates are printed as "D Month" (no year, no leading zero).

## Deviations from candidate
Date gap from window in non-applies items is 2–25 days; window length 14–60 days; draws where any option would cross midnight are rejected.
