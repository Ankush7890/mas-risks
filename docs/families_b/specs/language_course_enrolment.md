# language_course_enrolment

## Document
"{School} language school course rules". Visible: students may join the advanced {language} course if they passed the intermediate {language} exam with at least 60% of the marks; the intermediate exam is marked out of {max_marks}.

Case: "{Name} wants to join the advanced {language} course at {School}." then (shuffled) "{First} passed the intermediate {language} exam in {Month Year} with {score} out of {max_marks} marks.", "The advanced course starts in {Month Year}.", and an irrelevant group preference.

Question: "Can {Name} join the advanced course?"

## Withheld changing rule
"Exam results that are more than {y} year(s) old when the course starts no longer count; students whose result is older may join the advanced course after passing a placement test."

Condition: months between exam and course start, gap = (start_year×12 + start_month) − (exam_year×12 + exam_month), is more than 12×y. Applies items: gap in 12y+3 .. 12y+36. Non-applies: gap in 3 .. 12y−3. (No borderline cases.)

## Answers (fixed option texts)
- default: "Yes" (score ≥ 60% of max_marks; always true, with score ≥ 0.6×max_marks + 2).
- changed (= argued): "Yes, after passing a placement test".
- distractor: "No" (reading "60%" as 60 marks; score is always below 60).
- filler: "Only as a listener".

## Params
- name: str (full name); language: str.
- max_marks: int (70, 75, 80, 85, 90).
- score: int, 0.6×max_marks + 2 .. 59.
- exam_month, start_month: int 1–12; exam_year, start_year: int (start 2026–2027).
- max_age_years: int y (2–5).
The school name is not in params.

## Deviations from candidate
Dates are month + year instead of season + year (exact month gap, no borderline); max_marks limited to 70–90 in steps of 5 so that 60% is a whole number and a score under 60 can pass.
