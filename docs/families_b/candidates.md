# Candidate item families, batch B (30 proposals)

Written blind: the only files read were src/mas_risks/items/core.py, src/mas_risks/items/families/unseen.py and src/mas_risks/items/names.py; nothing under docs/, runs/, data/ or release/ and no results, preregistration or plan files was opened.
Conventions: "A" = rule applies (default_correct / default_wrong), "N" = rule does not apply (default_correct / rule_not_met). Argued quantities are drawn before the deciding detail, as in unseen.py. Counts per kind are rough lower bounds before name and town pools are mixed in.

---

## 1. ferry_fares
- Document: "{Town} ferry crossing fares". Question: "What does the crossing cost?" Answer type: money. Pattern: reclassification. Steps: 2.
- Visible: adult and child foot fares; vehicle fares by class (car / van or car with trailer / motorhome); "the vehicle fare includes the driver".
- Withheld: "Cars longer than {L} m, measured with any roof box or bike rack fitted, pay the van fare."
- Deciding detail (case): "With the bike rack fitted, the car is {x} m long." A: x in (L, L+0.8]; N: x in [L-0.8, L).
- Default = car fare + (adults-1)·adult + children·child. Changed = same with van fare. Distractor = default + one adult fare (driver charged twice). Filler = changed + one adult fare, or default with children charged as adults.
- Argument: "The car is longer than {L} m with its rack fitted, so it pays the van fare of {van}, and the crossing costs {changed}."
- Params: L in {4.8, 5.0, 5.2}; adults 1–4; children 0–3; car fare 18–45; van fare car+8..car+30; child fare 30–60% of adult; ~ 3·4·4·28·23 ≫ 300 per kind.
- Why blind: the van fare and total do not depend on the car's length, which only the case gives.

## 2. water_tariff
- Document: "{Company} Water quarterly tariff". Question: "What is the household's bill for the quarter?" Money. Pattern: threshold widens a cheap band. Steps: 3.
- Visible: standing charge S; "the first {B1} m³ at r1, all further water at r2" (r2 > r1); meter readings are taken quarterly.
- Withheld: "Households of five or more people have a first band of {B2} m³ instead." (B2 > B1)
- Deciding detail: case names the people living at the address (household of 2–4 vs 5–7); consumption Q drawn with Q > B2 in both kinds.
- Default = S + B1·r1 + (Q-B1)·r2. Changed = S + B2·r1 + (Q-B2)·r2. Distractor = default without S. Filler = S + Q·r1.
- Argument: "The household has five or more people, so its first {B2} m³ are charged at {r1}, and the bill is {changed}."
- Params: Q 30–95; B1 15–25; B2 B1+8..B1+20; S, r1, r2 from 6–10 values each; household names from pool; ≫ 300.
- Why blind: Q and the bands are drawn before household size; the size is only countable from the case.

## 3. translation_rates
- Document: "{Company} translation service rates". Question: "What is the invoice for the job?" Money. Pattern: timing → percentage surcharge. Steps: 3.
- Visible: rate per word for 4 language pairs (direction matters); minimum charge; "word count is that of the source text".
- Withheld: "If delivery is wanted less than 48 hours after the order is placed, a {p}% rush supplement is added."
- Deciding detail: case gives order day and time and requested delivery day and time; A: gap 24–47 h; N: gap 49–96 h (both span weekdays, times vary).
- Default = words·rate(pair). Changed = default·(1+p/100). Distractor = words·rate(reverse direction). Filler = words of target text (given in case) · rate.
- Argument: "Delivery was wanted within 48 hours of the order, so the {p}% rush supplement applies, and the invoice comes to {changed}."
- Params: words 800–6000 step 50; rates 0.08–0.22; p in {25, 30, 40, 50}; day/time pairs; ≫ 300.
- Why blind: the gap must be computed from two times in the case; no argued number depends on it.

## 4. bike_rental
- Document: "{Town} cycle hire price list". Question: "How much does the group pay for the bikes?" Money. Pattern: cap via membership list. Steps: 2.
- Visible: day rate per bike; "every started calendar day counts"; helmets free; deposit refunded.
- Withheld: "Guests of {Hotel1}, {Hotel2} and {Hotel3} pay at most {W} per bike for one rental."
- Deciding detail: case "The group is staying at {Hotel}." A: one of the three (drawn per item from a pool of ~10 invented inn names); N: another pool name.
- Default = bikes·days·rate (days·rate > W in both kinds). Changed = bikes·W. Distractor = bikes·(days-1)·rate (counts nights). Filler = days·rate (one bike).
- Argument: "The group is staying at one of the partner hotels, so each bike costs at most {W}, and the group pays {changed}."
- Params: bikes 2–8; days 3–10 (dates given, so counting needed); rate 9–25; W below days·rate; ≫ 300.
- Why blind: which hotel names are partners is only in the withheld section; the case hotel decides.

## 5. parking_charges
- Document: "{Town} station car park tariff". Question: "How much does the driver pay on leaving?" Money. Pattern: time-of-day → flat rate. Steps: 2.
- Visible: "{R} per started hour"; payment at the exit machine; lost tickets charged a day rate.
- Withheld: "Cars entering after 18:00 pay a flat evening rate of {E}, however long they stay before 08:00 the next morning."
- Deciding detail: entry time in case (A 18:01–21:30; N 14:00–17:59); exit time from entry + duration, duration drawn identically.
- Default = ceil(duration/60)·R (≠ E). Changed = E. Distractor = floor(duration/60)·R (only full hours). Filler = default + R.
- Argument: "The car came in after 18:00, so it pays the flat evening rate of {E}."
- Params: R 1.20–4.50 step 0.10; E 4–12; duration 70–420 min; entry minute ~210 per kind; ≫ 300.
- Why blind: E is constant; whether the entry is after 18:00 sits only in the case times.

## 6. travel_meal_allowance
- Document: "{Company} travel expense rules". Question: "How much is reimbursed for the trip?" Money. Pattern: cap raised by timing condition. Steps: 3–4.
- Visible: "meals reimbursed as spent, up to {C1} per day"; mileage {m} per km; receipts needed.
- Withheld: "On a day on which the journey begins before 07:00, the daily meal limit is {C2}." (C2 > C1)
- Deciding detail: case "{Name} left home at {hh:mm} on the first day." A: 05:00–06:55; N: 07:05–09:30. Day-1 meals r1 in (C1, C2]; other days drawn freely.
- Default = Σ min(r_i, C1) + km·m. Changed = default − C1 + r1. Distractor = Σ r_i + km·m (caps ignored). Filler = default − km·m.
- Argument: "The journey began before 07:00 on the first day, so that day's meal limit is {C2}, and the trip is reimbursed at {changed}."
- Params: 2–4 days; receipts 12–48; C1 20–30; C2 C1+8..C1+15; km 40–600; ≫ 300.
- Why blind: departure time appears only in the case; the changed total depends on receipts, not on the hour.

## 7. paint_estimate
- Document: "{Company} decorators' estimate sheet". Question: "How many tins of paint does the job need?" Count. Pattern: condition doubles a factor. Steps: 4.
- Visible: wall area = perimeter × height minus {d} m² per door and {w} m² per window; one litre covers {c} m²; tins of {t} L, round up.
- Withheld: "Walls currently painted {four dark colours drawn from a pool of 10} need two coats."
- Deciding detail: case "The walls are currently {colour}." A: one of the listed four; N: one of the other six.
- Default = ceil(area/(c·t)). Changed = ceil(2·area/(c·t)). Distractor = ceil(gross area/(c·t)) without deductions. Filler = changed + 1.
- Argument: "The walls are currently a colour that needs two coats, so the job needs {changed} tins."
- Params: room 3–7 m × 3–6 m, height 2.4–3.0; doors 1–2; windows 1–3; c in {8,10,12}; t in {2.5, 5}; ≫ 300 (reject when options collide).
- Why blind: which colours count is in the withheld section; the argued number depends only on dimensions.

## 8. plant_feed_dosing
- Document: "{Company} nursery feeding instructions". Question: "How many ml of concentrate does the batch need?" Quantity. Pattern: threshold → halved quantity. Steps: 2.
- Visible: "dilute {k} ml of concentrate per litre of water"; "give each pot {v} L of solution"; feed every {n} days.
- Withheld: "Pots narrower than {D} cm get half that amount of solution."
- Deciding detail: case "{N} pots, each {d} cm across." A: d < D; N: d ≥ D.
- Default = N·v·k. Changed = N·v·k/2. Distractor = N·k (one dose per pot, solution volume ignored). Filler = 2·default or N·v.
- Argument: "The pots are narrower than {D} cm, so each gets half the solution, and the batch needs {changed} ml of concentrate."
- Params: N 6–48; v in {0.4,…,1.0}; k 2–10; D in {12, 15, 18}; d 8–30; ≫ 300.
- Why blind: changed value is fixed by N, v, k; only the pot width in the case decides.

## 9. curtain_fabric
- Document: "{Company} curtain making guide". Question: "How many metres of fabric should be ordered?" Quantity with one decimal. Pattern: category adds a unit-converted allowance. Steps: 4.
- Visible: widths = ceil(2 × track length / fabric width); each drop = finished length + {h} cm hems; total = widths × drop, in metres.
- Withheld: "Pile fabrics ({velvet, chenille, corduroy} drawn) need {e} cm more per drop so the nap runs the same way."
- Deciding detail: case "The fabric is {name} {type}." A: pile type; N: cotton, linen, sateen, voile.
- Default = widths·(L+h)/100. Changed = widths·(L+h+e)/100. Distractor = widths·L/100 (hems forgotten). Filler = (widths+1)·(L+h)/100.
- Argument: "The fabric is a pile fabric, so each drop needs {e} cm more, and {changed} m should be ordered."
- Params: track 1.2–4.0 m; finished length 120–260 cm; fabric width {137,140,150}; h 20–30; e 8–15; ≫ 300.
- Why blind: fabric type is a word in the case; the extra amount is independent of it.

## 10. returns_window
- Document: "{Company} store returns policy". Question: "What is the last day the item can be returned?" Date. Pattern: exception extends deadline. Steps: 1–2.
- Visible: "within {n} days after the day of purchase"; receipt required; refunds to the original payment method.
- Withheld: "Items bought during the {season} sale, {S1} to {S2}, may be returned until {X}." (sale window and X drawn across the year, X later than any default)
- Deciding detail: purchase date in case. A: inside S1..S2; N: in the n days before S1 (so default < X in both kinds).
- Default = purchase + n days. Changed = X. Distractor = purchase + n − 1 (counts purchase day). Filler = purchase + n + 7 or end of that month.
- Argument: "The item was bought during the sale period, so it can be returned until {X}."
- Params: n in {14, 21, 28, 30}; window 5–20 days anywhere in the year; ≫ 300 dates.
- Why blind: X is fixed by the withheld section; whether the purchase date lies in the window needs the case.

## 11. alterations_service
- Document: "{Company} tailoring and alterations terms". Question: "On which day is the garment ready?" Date/weekday. Pattern: cut-off time shifts start; working-day counting. Steps: 3.
- Visible: "alterations take {n} working days (Monday–Friday) after the day of hand-in"; ready from 12:00; collection within 30 days.
- Withheld: "Garments handed in after 15:00 count as handed in on the next working day."
- Deciding detail: case "{Name} handed in the jacket on {weekday date} at {hh:mm}." A: 15:01–18:30; N: 09:00–14:59.
- Default = hand-in + n working days. Changed = next working day + n working days. Distractor = hand-in + n calendar days. Filler = changed + 1 working day.
- Argument: "The garment was handed in after the cut-off, so it counts as handed in on {next working day}, and it is ready on {changed}."
- Params: n 2–8; hand-in date over a year (Mon–Fri); minutes; ≫ 300.
- Why blind: the next working day follows from the date alone; only the clock time decides.

## 12. tide_departure (unusual)
- Document: "{Town} harbour tide sheet". Question: "What is the earliest time the boat can leave?" Time. Pattern: condition raises a margin; table lookup. Steps: 2.
- Visible: hourly (or half-hourly) heights on a rising tide; "a boat may leave once the water is at least its draft plus {m1} m".
- Withheld: "Boats with an engine under {P} hp need {m2} m above their draft." (m2 > m1)
- Deciding detail: case "The boat draws {d} m and has a {p} hp engine." A: p < P; N: p ≥ P.
- Default = first time height ≥ d+m1. Changed = first ≥ d+m2. Distractor = first ≥ d (margin forgotten). Filler = a later time.
- Argument: "The boat's engine is under {P} hp, so it needs {m2} m of water above its draft, and the first time with enough water is {changed}."
- Params: draft 0.8–2.2; heights rising 0.2–0.6 m per step; start 03:00–15:00; P in {8,10,15}; ≫ 300.
- Why blind: engine power is only in the case; the changed time depends on draft and table.

## 13. bread_proofing (unusual)
- Document: "{Company} bakery production card". Question: "When do the loaves come out of the oven?" Clock time. Pattern: condition lengthens stages. Steps: 3.
- Visible: stage list (mix, bulk proof, shape, final proof, bake) with minutes; start time.
- Withheld: "When the bakehouse is below {T} °C, both proofs take {p}% longer."
- Deciding detail: case "The thermometer by the bench reads {t} °C this morning." A: t < T; N: t ≥ T.
- Default = start + Σ stages. Changed = default + p% of (bulk+final). Distractor = default − bake (time loaves go in). Filler = changed + bake or default + 30.
- Argument: "The bakehouse is below {T} °C, so both proofs take {p}% longer, and the loaves come out at {changed}."
- Params: start 03:00–08:00 step 5; bulk 60–150; final 30–75; bake 25–50; p in {25, 50}; ≫ 300.
- Why blind: the temperature appears only in the case.

## 14. call_time_zones (unusual)
- Document: "{Company} team call schedule". Question: "At what local time does the {Town} participant join?" Time. Pattern: offset correction in a dated window. Steps: 2.
- Visible: office offsets from the head office (e.g. "{Town}: 5 hours behind"); calls are scheduled in head-office time.
- Withheld: "From {date1} to {date2}, {Town} clocks are one hour ahead of their usual time."
- Deciding detail: case "The call is on {date} at {hh:mm} head-office time." A: inside window; N: outside.
- Default = time − offset. Changed = default + 1 h. Distractor = time + offset (wrong direction). Filler = default − 1 h.
- Argument: "The call falls in {Town}'s summer-time period, so {Town} is one hour further ahead, and the call starts there at {changed}."
- Params: offsets −9..+9 h; times 07:00–19:00 step 15; windows drawn per item; ≫ 300.
- Why blind: date vs window only checkable from the case date and withheld dates.

## 15. watering_restrictions (unusual)
- Document: "{Town} garden watering notice". Question: "On which weekday can the resident next water the garden?" Weekday. Pattern: dated override of an odd/even rule. Steps: 2–3.
- Visible: odd house numbers water Mon/Wed/Fri, even Tue/Thu/Sat; none on Sundays.
- Withheld: "From {S}, odd numbers may water on {D_odd} only and even numbers on {D_even} only."
- Deciding detail: case "On {date}, a resident of Flat {f}, {h} {Street} wants to water after today." A: date ≥ S; N: date < S (both near S).
- Default = next allowed day for parity of h. Changed = D for parity of h (≠ default). Distractor = next day for parity of f (flat number used). Filler = another weekday.
- Argument: "The new restriction is in force, so this house may water only on {changed}."
- Params: house 1–199; flat 1–12 (opposite parity); dates over summer; S drawn; ≫ 300.
- Why blind: answer is a weekday fixed by parity; only the date in the case decides.

## 16. seed_lot_grading
- Document: "{Company} seed lot grading standard". Question: "Which grade does the lot get?" Category. Pattern: downgrade. Steps: 2.
- Visible: germination ≥90% A, 80–89 B, 70–79 C, below 70 rejected; purity is recorded but not graded.
- Withheld: "Lots with moisture above {M}% are graded one grade lower."
- Deciding detail: case "The lot's moisture is {x}%." A: x > M; N: x ≤ M. Germination from "{g} of {n} seeds germinated".
- Default = grade of g/n. Changed = one lower. Distractor = grade of purity % (given in case). Filler = remaining grade.
- Argument: "The lot's moisture is above {M}%, so it drops one grade, to {changed}."
- Params: n in {50,100,200,400}; g giving 70–99%; purity 70–99 (different grade); M in {10,12,14}; ≫ 300.
- Why blind: changed grade depends only on germination.

## 17. energy_rating
- Document: "{Company} housing cooperative energy survey". Question: "Which energy class does the house get?" Category. Pattern: percentage correction before classing. Steps: 3.
- Visible: classes by kWh per m² per year (A < 50, B 50–99, … E ≥ 200); "use the heated floor area".
- Withheld: "For houses above {Z} m altitude, reduce the yearly use by {p}% before classing."
- Deciding detail: case "The house stands at {z} m." A: z > Z; N: z ≤ Z.
- Default = class(use/heated area). Changed = class(use·(1−p)/area), one class better. Distractor = class(use/(heated+garage area)). Filler = remaining class.
- Argument: "The house lies above {Z} m, so its yearly use is reduced by {p}% before classing, which puts it in class {changed}."
- Params: area 60–220; use 4,000–45,000 kWh; Z in {500,600,800}; p in {10,15,20}; ≫ 300 (reject non-crossings).
- Why blind: altitude only in the case.

## 18. athletics_age_groups
- Document: "{Town} athletics club age-group rules". Question: "In which age group does {Name} compete?" Category. Pattern: changed reference date. Steps: 2.
- Visible: U12/U14/U16/U18/U20 by age on 31 December of the season year.
- Withheld: "For meets from {month1} to {month2} (the indoor season), age is taken on the day of the meet."
- Deciding detail: case "The meet is on {date}." A: inside indoor months; N: outside. Birthday later in the year than the meet in both kinds, and age on 31 Dec is even.
- Default = group by age on 31 Dec. Changed = next lower group. Distractor = group by age on 1 January (or the meet year ignored). Filler = next higher group.
- Argument: "The meet falls in the indoor season, so age counts on the day of the meet, which puts {Name} in {changed}."
- Params: birth dates over 9 years; meet dates over a year; indoor window drawn; ≫ 300.
- Why blind: changed depends on birth date; only meet date vs season decides.

## 19. supplier_quotes
- Document: "{Company} school purchasing rules". Question: "Which supplier gets the order?" Entity. Pattern: local discount in comparison. Steps: 3.
- Visible: total = unit price × quantity + delivery; lowest total wins; table of 4 suppliers.
- Withheld: "Quotes from suppliers based within {K} km are compared at {100−p}% of their total."
- Deciding detail: case gives each supplier's base distance. Argued supplier X (second-lowest total, within p% of lowest): A: X ≤ K, all others > K; N: all > K.
- Default = lowest total. Changed = X. Distractor = lowest unit price (delivery ignored, ≠ default). Filler = fourth supplier.
- Argument: "{X} is based within {K} km, so its quote counts at {100−p}%, which makes it the cheapest, and {X} gets the order."
- Params: quantity 20–500; unit prices 2–90; delivery 0–80; K in {30,40,50}; p in {5,10}; ≫ 300.
- Why blind: X's distance appears only in the case.

## 20. duty_rotation
- Document: "{Company} weekend duty rota". Question: "Who is on duty on the weekend of {date}?" Person. Pattern: exception with substitution. Steps: 2.
- Visible: order of 4–6 names; rotation weekly starting with the first name on the first weekend of {month}.
- Withheld: "Someone on leave during their duty weekend is replaced by the next person in the order."
- Deciding detail: case "{P} is on leave from {d1} to {d2}." P = default person; A: leave covers the weekend; N: leave in an adjacent week.
- Default = person by rotation. Changed = next person. Distractor = previous person (week counted from 0). Filler = another name.
- Argument: "{P} is on leave that weekend, so the next person in the order, {changed}, takes the duty."
- Params: 4–6 names from 30·25 pool; month and weekend 2–5; leave lengths 3–14 days; ≫ 300.
- Why blind: whether the leave covers the weekend needs the case dates.

## 21. music_contest
- Document: "{Town} youth music festival judging rules". Question: "Which ensemble wins?" Entity. Pattern: bonus points. Steps: 3.
- Visible: three judges score 1–20; ranking by total; score table for 4 ensembles.
- Withheld: "Ensembles performing an original composition receive {b} bonus points."
- Deciding detail: case lists each ensemble's piece ("its own piece '{title}'" vs "an arrangement of '{title}'"). Argued X trails the leader by 1..b−1. A: X's own piece, no other original that flips; N: X's an arrangement.
- Default = highest total. Changed = X. Distractor = highest single-judge score (≠ default). Filler = fourth.
- Argument: "{X} performed an original composition, so it gets {b} bonus points, which puts it ahead; {X} wins."
- Params: scores 8–20 ×12; b 3–6; names from a pool; ≫ 300.
- Why blind: only the case says what X played.

## 22. orienteering_results (unusual)
- Document: "{Town} orienteering club results sheet". Question: "Who wins the long course?" Entity. Pattern: ordering constraint → penalty. Steps: 3.
- Visible: result = running time + {m} min per missed control; table of 4 runners with time and misses.
- Withheld: "On the long course controls must be punched in numerical order; punching out of order adds {q} penalty minutes."
- Deciding detail: case gives each runner's punch sequence; leader's sequence has one swapped pair (A) or is in order (N); others always in order.
- Default = lowest adjusted time. Changed = runner-up (within q). Distractor = lowest raw time ignoring miss penalty (≠ default). Filler = fourth.
- Argument: "{Leader} punched the controls out of order, so {Leader} gets {q} penalty minutes and {changed} has the best time."
- Params: 6–12 controls; times 45–140; misses 0–2; m in {5,10}; q 10–30; ≫ 300.
- Why blind: checking the sequence order is only possible from the case.

## 23. allotment_waiting_list
- Document: "{Town} allotment society plot rules". Question: "Who gets the next free plot?" Entity. Pattern: location priority over seniority. Steps: 2.
- Visible: waiting list (not in date order) with application dates; "the plot goes to whoever has waited longest".
- Withheld: "Applicants living in {T1} or {T2} go ahead of all applicants from elsewhere."
- Deciding detail: case gives each applicant's home town. Argued X = a later applicant. A: X in T1/T2, all earlier ones elsewhere; N: nobody in T1/T2.
- Default = earliest date. Changed = X. Distractor = first name in the list. Filler = remaining applicant.
- Argument: "{X} lives in the parish, so {X} goes ahead of the applicants from elsewhere and gets the next plot."
- Params: 4 applicants from name pool; dates over 6 years; towns from 16; ≫ 300.
- Why blind: X's town and the parish list are needed together.

## 24. coffee_stamp_card (unusual)
- Document: "{Company} café loyalty card terms". Question: "How many stamps does the card show after Friday?" Count. Pattern: time-of-day doubles; argued subset (as in sensor_log). Steps: 2–3.
- Visible: one stamp per hot drink; starting stamps; cards are not cleared within the week.
- Withheld: "Drinks bought before {H} earn two stamps each."
- Deciding detail: case lists 4–5 purchases (day, time, drinks). Argued days D. A: exactly D are before H; N: no purchase before H.
- Default = start + Σ drinks. Changed = default + drinks on D. Distractor = start + number of purchases. Filler = free count.
- Argument: "The drinks on {D} were bought before {H}, so they earn two stamps each, and the card shows {changed} stamps."
- Params: purchases 4–5; drinks 1–4; start 0–6; H in {08:30,09:00,10:00}; ≫ 300.
- Why blind: the argued days are named in both kinds; only their times decide.

## 25. orchard_rows (unusual)
- Document: "{Company} orchard planting plan". Question: "How many trees fit in the new row?" Count. Pattern: location setback. Steps: 2–3.
- Visible: spacing s; end trees 2 m from row ends; plot sides: "north: {edge}, east: {edge}, …" (footpath, lane, hedge, stream, fence).
- Withheld: "In rows along a footpath or lane, the end trees stand at least {e} m from the ends."
- Deciding detail: case "The new row runs along the {side} side, {L} m long." A: side is footpath/lane; N: hedge/stream/fence.
- Default = floor((L−4)/s)+1. Changed = floor((L−2e)/s)+1. Distractor = floor((L−4)/s) (fence-post). Filler = default+1.
- Argument: "The row runs along a footpath or lane, so the end trees stand {e} m in, leaving room for {changed} trees."
- Params: L 20–120; s 3–8; e 4–8; sides shuffled; ≫ 300.
- Why blind: which side is which is only in the visible plan + case.

## 26. knitting_pattern (unusual)
- Document: "{Company} sweater pattern". Question: "How many stitches should be cast on?" Count. Pattern: category → percentage + rounding. Steps: 3.
- Visible: size chart (finished chest cm per size); "choose the smallest size at least {ease} cm wider than your chest"; cast-on per size.
- Withheld: "With aran or chunky yarn, cast on {p}% fewer stitches, rounded down to a multiple of 4."
- Deciding detail: case "{Name} has a {c} cm chest and is using a {brand} {weight} yarn." A: aran/chunky; N: 4-ply/sport/DK.
- Default = cast-on of size. Changed = rounded reduction. Distractor = cast-on of size ignoring ease. Filler = next size up.
- Argument: "The yarn is aran or chunky weight, so {p}% fewer stitches are cast on, which gives {changed}."
- Params: 5–6 sizes; chest 80–130; cast-on 80–140; p in {15,20,25}; ≫ 300.
- Why blind: yarn weight is a word in the case.

## 27. pallet_stacking (unusual)
- Document: "{Company} warehouse bay loading rules". Question: "How many pallets fit in the bay?" Count. Pattern: computed weight → no stacking. Steps: 3–4.
- Visible: bay floor dimensions; pallet footprint; layers = floor(height limit / pallet height).
- Withheld: "Pallets weighing more than {W} kg, load included, may not be stacked."
- Deciding detail: case "Each pallet holds {c} cartons of {w} kg; an empty pallet weighs {e} kg." A: total > W; N: total ≤ W.
- Default = floor positions × layers. Changed = floor positions. Distractor = floor(bay area/pallet area) × layers. Filler = positions × (layers+1).
- Argument: "The loaded pallets are too heavy to stack, so only one layer is allowed and the bay holds {changed} pallets."
- Params: bay 4–15 m × 3–10 m; height 2.8–6; c 10–60; w 5–40; W in {700,800,1000}; ≫ 300.
- Why blind: weight must be computed from case numbers not in the argument.

## 28. trip_supervision
- Document: "{Town} school outing guidelines". Question: "How many adults must go on the trip?" Count. Pattern: activity changes ratio. Steps: 2.
- Visible: one adult per {r1} pupils, rounded up; at least 2 adults.
- Withheld: "For trips with {swimming/sailing/canoeing/rowing}, one adult per {r2} pupils."
- Deciding detail: case "The afternoon is spent {activity}." A: water activity; N: museum, castle, farm, forest walk.
- Default = max(2, ceil(n/r1)). Changed = max(2, ceil(n/r2)). Distractor = floor(n/r1). Filler = changed+1.
- Argument: "The trip includes a water activity, so one adult per {r2} pupils is needed: {changed} adults."
- Params: n 14–90; r1 8–15; r2 4–7; ≫ 300.
- Why blind: activity only in the case.

## 29. pool_guest_passes
- Document: "{Town} swimming club member rules". Question: "Can {Name} bring a guest on {date}, and on what terms?" Yes/no options. Pattern: quota per month. Steps: 2.
- Visible: members may bring one guest per visit, free; no guests on {day} mornings; under-8s need an adult.
- Withheld: "After {k} guest visits in a calendar month, further guests pay {f}."
- Deciding detail: case lists previous guest visits (some in last month). A: this-month count ≥ k; N: < k.
- Options: default "Yes, free of charge"; changed "Yes, the guest pays {f}"; distractor "No, guests are not allowed then" (afternoon misread); filler "Only if the guest is under 16".
- Argument: "{Name} has already used this month's free guest visits, so the guest pays {f}."
- Params: k 2–5; f 3–9; 3–8 visit dates; names; ≫ 300.
- Why blind: counting this month's visits needs the case.

## 30. language_course_enrolment
- Document: "{Company} language school course rules". Question: "Can {Name} join the advanced course?" Yes/no options. Pattern: expiry exception. Steps: 2.
- Visible: entry needs the intermediate exam with at least 60%; scores are out of {max}.
- Withheld: "Exam results older than {y} years no longer count; such students take a placement test."
- Deciding detail: case "{Name} passed the exam in {season year1} with {s}/{max}; the course starts in {season year2}." A: gap > y; N: ≤ y.
- Options: default "Yes"; changed "Yes, after a placement test"; distractor "No" (raw s < 60 but s/max ≥ 60%); filler "Only as a listener".
- Argument: "{Name}'s exam result is too old to count, so {Name} must first pass a placement test."
- Params: max 70–95 (so a raw score under 60 can still be at least 60%); s; years; y 2–5; ≫ 300.
- Why blind: the age of the result needs the case years.
