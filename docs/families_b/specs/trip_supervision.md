# trip_supervision

## Document
"{Town} school outing guidelines". Visible sections:
- "At least one adult goes with every {ratio} pupils: divide the number of pupils by {ratio}
  and round up to the next whole number."
- "Every trip has at least 2 adults."
- "Teachers and parent helpers both count as adults."
plus one or two irrelevant sections at random places.

Case: "{pupils} pupils from {Mr|Ms} {Surname}'s class are going on a day trip to
{destination}." followed (shuffled) by "The class travels there {mode}.", a weekday sentence
and a return-time sentence.

Question: "How many adults must go on the trip?"

## Withheld changing rule
"For trips that travel by public transport (train or public bus), at least one adult goes with
every {ratio_public_transport} pupils instead, rounded up."

Condition: `mode` is "by train" or "by public bus". In rule-not-met items the mode is
"by hired coach" or "on foot". In rule-applies items mode equals `argued_mode`.

## Answers (format "{k} adults"; "1 adult" singular, never occurs in practice)
- default = ceil(pupils / ratio). pupils is never a multiple of ratio, and default ≥ 3, so the
  2-adult minimum never decides.
- changed / argued = ceil(pupils / ratio_public_transport); always > default.
- distractor = floor(pupils / ratio) (forgot to round up) = default − 1.
- filler = changed + 1.

Argument: "The class travels {argued_mode}, which is public transport, so at least one adult is
needed for every {ratio_public_transport} pupils: {changed} adults."

## Params
- pupils: int, 20–90.
- ratio: int, 8–15 (visible ratio).
- ratio_public_transport: int, 4–7 (withheld ratio).
- min_adults: int, always 2.
- mode: str, the travel mode in the case ("by train", "by public bus", "by hired coach",
  "on foot").
- argued_mode: str, "by train" or "by public bus" (the mode the argument claims).
- destination: str, text only.

rule_applies = mode in {"by train", "by public bus"}.

## Deviations from the candidate
- The deciding detail is the travel mode (public transport vs hired coach / on foot) instead of
  a water activity: swimming or canoeing would invite a 4B model to add supervision from world
  knowledge at turn 1 (the visible text half-suggesting the rule).
- Pupil numbers are restricted so that rounding up always matters and the visible ratio gives
  at least 3 adults.
