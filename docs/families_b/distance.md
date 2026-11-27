# Family distance from the seen (training) families

Coding of 42 item families on four fixed features, and each non-seen family's distance from its nearest seen family.

**Sources and blindness.** Seen and old-unseen families were coded from the generator code (`src/mas_risks/items/families/seen_a.py`, `seen_b.py`, `unseen.py`). The 30 candidates were coded from their descriptions in `docs/families_b/candidates.md`. No results, runs, data, release files or other docs were opened. The coding does not use and does not anticipate any experimental outcome.

## 1. Feature definitions (fixed before coding)

Each family gets exactly one category per feature. Where a family could fit two categories, the tie-break rule given below decides.

### answer_type (6 categories): what the correct answer is
| code | meaning |
|---|---|
| MONEY | an amount of money |
| QTY | a non-money quantity or count (days of leave, kg, tins, stitches, adults, heat days) |
| TIME | a date, weekday or clock time |
| CLASS | a class, grade, belt or group from a graded scale |
| ENTITY | which one of several listed entities (team, supplier, person, ensemble, departure) |
| ENTITLE | an entitlement or yes/no-style outcome given as a verbal option |

### rule_pattern (7 categories): what the withheld rule does to the computation (its consequence; the trigger belongs to deciding_detail)
| code | meaning |
|---|---|
| PCT | multiplies a quantity: percentage on or off, halving, doubling, a changed rate or ratio |
| CAP | imposes or moves a limit or boundary: a cap, a band limit, a required margin or setback, a layer limit |
| FLAT | adds or subtracts a fixed non-time amount (points, minutes of penalty, cm) or replaces the value with a fixed amount |
| RECLASS | moves the case into another class, tariff group or belt |
| CORRECT | corrects an input figure before the normal computation runs (sensor offset, use reduced before classing) |
| TIMING | changes a time reference: shifts a date or time, sets a cut-off, minimum interval, schedule, fixed deadline or reference date |
| ELIG | changes eligibility or entitlement, or who qualifies (exception, substitution, priority) |

Tie-break: rules that act on a date or time go to TIMING, unless they multiply a duration (PCT). A raised cap goes to CAP. An added time amount that is a penalty in a score comparison (orienteering minutes) goes to FLAT.

### deciding_detail (5 categories): the kind of case detail that decides whether the rule applies
| code | meaning |
|---|---|
| NUM | a number (given or computed) compared with a threshold: months, %, length, people, weight, distance, temperature |
| MEMBER | membership of a named list or category, or presence of an attribute word (hotel, colour, fabric, fragile, commercial use) |
| TIME | a clock time, date, or interval between dates or times |
| PLACE | a place or location (platform group, home town, side of plot) |
| HIST | a sequence or history of events (punch order, earlier visits, registration before or after a match) |

Tie-break: a distance in km or an altitude compared with a number is NUM, not PLACE. A count of people listed in the case is NUM. A count of earlier events is HIST.

### steps (3 buckets): computation steps from document to answer when the rule applies
`1`, `2`, `3+`. Counted steps are arithmetic operations, table or list lookups, and comparisons that select a value (min, re-rank, first departure after). Checking the rule's condition is not counted. This count sometimes differs from the "Steps" given in candidates.md, which was not defined this way. Here the count is redone from each description's "Changed =" formula. For example, ferry_fares is listed as 2 there but needs van fare + extra adults + children, so it is coded `3+` here.

### distance
For each non-seen family, the distance is the number of the four features on which it differs from a seen family, minimised over the 8 seen families (range 0–4). The nearest seen family is the one reaching that minimum. All ties are listed.

## 2. Codes for all 42 families

| # | family | group | answer_type | rule_pattern | deciding_detail | steps | rule_pattern: why | deciding_detail: why | steps: chain when rule applies |
|---|---|---|---|---|---|---|---|---|---|
| 1 | leave_policy | seen | QTY | CAP | NUM | 2 | first-year cap on days that may be taken | completed months vs 12 (number) | accrue rate×months, min with cap |
| 2 | delivery_terms | seen | TIME | TIMING | MEMBER | 3+ | arrival shifted one working day later | oversized / made-to-measure item or island address: an attribute of the order (one of a fixed trigger list) | ship day from cut-off, + transit working days, + 1 |
| 3 | print_shop | seen | MONEY | PCT | NUM | 3+ | pct% off printing at or above a page threshold | total pages vs threshold (number) | pages×price, −pct%, + copies×binding |
| 4 | league_rules | seen | ENTITY | FLAT | HIST | 2 | fixed 3-point deduction, then re-rank | whether a player was unregistered when fielded (history: registration before/after the match) | deduct, re-rank (points given) |
| 5 | library_lending | seen | MONEY | PCT | NUM | 3+ | late fee halved | membership years vs needed years (number) | fee×days×items, halve |
| 6 | lab_storage | seen | CLASS | RECLASS | NUM | 1 | mixture forced to class 1 | additive share vs limit (number) | read class 1 |
| 7 | workshop_sheet | seen | QTY | PCT | NUM | 3+ | pct% more material | order size vs threshold (number) | order÷batch×per-batch, +pct% |
| 8 | warranty_terms | seen | ENTITLE | ELIG | MEMBER | 2 | commercial use shortens cover and removes labour discount: changes the entitlement | commercial vs household use (category of use) | failure month vs commercial period, pick outcome |
| 9 | train_timetable | old unseen | ENTITY | TIMING | PLACE | 3+ | minimum changing time between platform groups | arrival platform group 1–4 vs 5–8 (location in station) | actual arrival, + min change, first departure after |
| 10 | grant_budget | old unseen | MONEY | PCT | NUM | 3+ | pct% set aside before split | grant vs threshold (number) | reserve pct, staff share of remainder |
| 11 | sensor_log | old unseen | QTY | CORRECT | MEMBER | 3+ | offset subtracted from one sensor's readings | which sensor the withheld section names (membership of readings in that sensor) | correct readings, compare with limit, count |
| 12 | parcel_sorting | old unseen | CLASS | RECLASS | MEMBER | 1 | fragile/liquid parcels forced to belt 4 | fragile / liquids flag (category) | read belt 4 |
| 13 | ferry_fares | candidate | MONEY | RECLASS | NUM | 3+ | long car moved into the van fare class | car length vs L (number) | van fare + extra adults + children |
| 14 | water_tariff | candidate | MONEY | CAP | NUM | 3+ | cheap band limit moved from B1 to B2 (boundary change) | household size 5+ (count of people, number) | S + B2·r1 + (Q−B2)·r2 |
| 15 | translation_rates | candidate | MONEY | PCT | TIME | 3+ | pct% rush supplement | gap between order and delivery times (< 48 h) | look up pair rate, ×words, +p% |
| 16 | bike_rental | candidate | MONEY | CAP | MEMBER | 3+ | cap W per bike | case hotel in a named partner list | days from dates, ×rate, min W, ×bikes |
| 17 | parking_charges | candidate | MONEY | FLAT | TIME | 1 | flat evening rate replaces hourly charge | entry clock time after 18:00 | read E |
| 18 | travel_meal_allowance | candidate | MONEY | CAP | TIME | 3+ | daily meal cap raised C1→C2 | departure clock time before 07:00 | capped meals per day, sum, + mileage |
| 19 | paint_estimate | candidate | QTY | PCT | MEMBER | 3+ | two coats: area doubled (multiplier) | current colour in a named list | net area, ×2, ÷coverage, round up |
| 20 | plant_feed_dosing | candidate | QTY | PCT | NUM | 3+ | solution halved | pot width vs D (number) | N×v×k, halve |
| 21 | curtain_fabric | candidate | QTY | FLAT | MEMBER | 3+ | fixed extra e cm per drop | fabric type is a pile fabric (category word) | widths, drop + hems + e, ×widths, to metres |
| 22 | returns_window | candidate | TIME | TIMING | TIME | 1 | deadline replaced by a fixed later date | purchase date inside sale window | read X |
| 23 | alterations_service | candidate | TIME | TIMING | TIME | 2 | late hand-in counts as next working day (cut-off shift) | hand-in clock time after 15:00 | next working day, + n working days |
| 24 | tide_departure | candidate | TIME | CAP | NUM | 2 | required margin raised m1→m2 (limit moved) | engine hp vs P (number) | draft + m2, first time in table above it |
| 25 | bread_proofing | candidate | TIME | PCT | NUM | 3+ | both proofs p% longer | bench temperature vs T (number) | p% of proofs, sum stages, add to start |
| 26 | call_time_zones | candidate | TIME | TIMING | TIME | 2 | clock shifted one hour in a dated window | call date inside summer-time window | time − offset, +1 h |
| 27 | watering_restrictions | candidate | TIME | TIMING | TIME | 2 | new allowed-day schedule from date S | case date ≥ S | house parity, look up new day |
| 28 | seed_lot_grading | candidate | CLASS | RECLASS | NUM | 3+ | downgrade by one grade | moisture vs M (number) | g/n, grade, one lower |
| 29 | energy_rating | candidate | CLASS | CORRECT | NUM | 3+ | use reduced by p% before classing (correction of the input figure) | altitude vs Z (number) | ×(1−p), ÷area, class lookup |
| 30 | athletics_age_groups | candidate | CLASS | TIMING | TIME | 2 | reference date for age changed to meet day | meet date inside indoor season | age on meet day, group lookup |
| 31 | supplier_quotes | candidate | ENTITY | PCT | NUM | 3+ | local quotes compared at (100−p)% | supplier distance vs K km (number) | totals, discount, compare |
| 32 | duty_rotation | candidate | ENTITY | ELIG | TIME | 3+ | person on leave replaced by next in order (substitution) | leave dates cover the duty weekend | count weeks, rotation index, next person |
| 33 | music_contest | candidate | ENTITY | FLAT | MEMBER | 3+ | fixed bonus points | piece is an original vs an arrangement (category) | sum judges, + b, compare |
| 34 | orienteering_results | candidate | ENTITY | FLAT | HIST | 3+ | fixed penalty minutes | punch sequence out of order (sequence of events) | adjusted times, + q, compare |
| 35 | allotment_waiting_list | candidate | ENTITY | ELIG | PLACE | 2 | local applicants get priority over seniority | applicant's home town (place) | filter local, earliest among them |
| 36 | coffee_stamp_card | candidate | QTY | PCT | TIME | 3+ | stamps doubled for some purchases (multiplier) | purchase clock time before H | sum drinks, add early drinks again, + start |
| 37 | orchard_rows | candidate | QTY | CAP | PLACE | 3+ | end setback raised to e m (limit moved) | which side the row runs along (location) | L − 2e, ÷s floor, +1 |
| 38 | knitting_pattern | candidate | QTY | PCT | MEMBER | 3+ | p% fewer stitches, rounded | yarn weight is aran/chunky (category) | choose size, −p%, round to 4 |
| 39 | pallet_stacking | candidate | QTY | CAP | NUM | 3+ | no stacking: layers capped at 1 | computed pallet weight vs W (number) | positions along length × width |
| 40 | trip_supervision | candidate | QTY | PCT | MEMBER | 2 | supervision ratio changed r1→r2 (rate) | activity is a water activity (category) | ceil(n/r2), max 2 |
| 41 | pool_guest_passes | candidate | ENTITLE | ELIG | HIST | 1 | quota exhausted: free guest becomes paid (entitlement) | count of this month's prior guest visits (history) | read paid option |
| 42 | language_course_enrolment | candidate | ENTITLE | ELIG | TIME | 1 | old result no longer counts: placement test needed (entitlement) | years between exam and course (dates) | read placement option |

## 3. Distance of the 34 non-seen families

| # | family | group | distance | nearest seen family (all ties listed) |
|---|---|---|---|---|
| 1 | train_timetable | old unseen | 2 | delivery_terms |
| 2 | grant_budget | old unseen | 0 | print_shop, library_lending |
| 3 | sensor_log | old unseen | 2 | delivery_terms, workshop_sheet |
| 4 | parcel_sorting | old unseen | 1 | lab_storage |
| 5 | ferry_fares | candidate | 1 | print_shop, library_lending |
| 6 | water_tariff | candidate | 1 | print_shop, library_lending |
| 7 | translation_rates | candidate | 1 | print_shop, library_lending |
| 8 | bike_rental | candidate | 2 | delivery_terms, print_shop, library_lending |
| 9 | parking_charges | candidate | 3 | print_shop, league_rules, library_lending, lab_storage |
| 10 | travel_meal_allowance | candidate | 2 | print_shop, library_lending |
| 11 | paint_estimate | candidate | 1 | workshop_sheet |
| 12 | plant_feed_dosing | candidate | 0 | workshop_sheet |
| 13 | curtain_fabric | candidate | 2 | delivery_terms, workshop_sheet |
| 14 | returns_window | candidate | 2 | delivery_terms |
| 15 | alterations_service | candidate | 2 | delivery_terms |
| 16 | tide_departure | candidate | 1 | leave_policy |
| 17 | bread_proofing | candidate | 1 | print_shop, library_lending, workshop_sheet |
| 18 | call_time_zones | candidate | 2 | delivery_terms |
| 19 | watering_restrictions | candidate | 2 | delivery_terms |
| 20 | seed_lot_grading | candidate | 1 | lab_storage |
| 21 | energy_rating | candidate | 2 | print_shop, library_lending, lab_storage, workshop_sheet |
| 22 | athletics_age_groups | candidate | 3 | leave_policy, delivery_terms, league_rules, lab_storage, warranty_terms |
| 23 | supplier_quotes | candidate | 1 | print_shop, library_lending, workshop_sheet |
| 24 | duty_rotation | candidate | 3 | delivery_terms, print_shop, league_rules, library_lending, workshop_sheet, warranty_terms |
| 25 | music_contest | candidate | 2 | delivery_terms, league_rules |
| 26 | orienteering_results | candidate | 1 | league_rules |
| 27 | allotment_waiting_list | candidate | 2 | league_rules, warranty_terms |
| 28 | coffee_stamp_card | candidate | 1 | workshop_sheet |
| 29 | orchard_rows | candidate | 2 | leave_policy, workshop_sheet |
| 30 | knitting_pattern | candidate | 1 | workshop_sheet |
| 31 | pallet_stacking | candidate | 1 | leave_policy, workshop_sheet |
| 32 | trip_supervision | candidate | 2 | leave_policy, workshop_sheet, warranty_terms |
| 33 | pool_guest_passes | candidate | 2 | warranty_terms |
| 34 | language_course_enrolment | candidate | 2 | warranty_terms |

## 4. Summary

- **30 candidates:** median distance **2** (mean 1.63). Distribution: 0 → 1 family, 1 → 12, 2 → 14, 3 → 3, 4 → 0.
  - Distance 0: plant_feed_dosing (identical codes to workshop_sheet).
  - Distance 3: parking_charges, athletics_age_groups, duty_rotation.
- **4 old unseen families:** grant_budget 0, parcel_sorting 1, train_timetable 2, sensor_log 2 (median 1.5).
- **Sensitivity:** 13 of the 30 candidates are at distance ≤ 1 and 17 at ≥ 2. The median would drop to 1.5 only if two candidates at distance 2 were recoded to distance ≤ 1. Calls that could move a family:
  - returns_window: TIMING vs FLAT.
  - call_time_zones: TIMING vs CORRECT.
  - energy_rating: CORRECT vs PCT.
  - orienteering_results: FLAT vs TIMING.
  - supplier_quotes: deciding_detail NUM vs PLACE.
  - The `steps` counting convention.
- **Coverage gaps in the seen set:**
  - No seen family uses PLACE or TIME as its deciding detail. Every candidate that does (translation, parking, travel_meal, returns, alterations, call_time_zones, watering, athletics, duty, coffee, language, allotment, orchard) is therefore at distance ≥ 1.
  - No seen family uses CORRECT.
