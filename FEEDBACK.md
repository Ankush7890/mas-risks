# FEEDBACK

A list of problems with the documentation or workflow, noted by agents (or humans), each with constructive criticism on how it could have been prevented. This is how the conventions improve instead of rotting: when an agent makes a mistake that better instructions would have prevented, the mistake gets an entry here, and a periodic review turns recurring entries into new rules.

Entry format: date, what went wrong (or what friction occurred), and — where possible — a concrete suggestion: which file should say what, so the next agent doesn't hit the same problem.

---

- **26-11-24 — plan written into `projects/` with no LOG/SUMMARY.** An earlier session wrote `projects/mas_sim/PLAN.md` (including a static code review of RiskLab) without creating a LOG/SUMMARY pair or a README index row, so that work was undiscoverable from the index. Suggestion: `docs/CODING.md` should say explicitly that design/implementation plans inside `projects/` still need a topic LOG/SUMMARY pair and index row, and that the LOG must record the evidence behind the plan (here: the RiskLab code findings).
- **26-11-24 — the name `projects/` is ambiguous.** `docs/CODING.md` uses "coding project" to mean one codebase, but in a repo that is itself one research project the user read `projects/` as "several research projects" and questioned the convention. Suggestion: `docs/CODING.md` should say in one sentence that each folder under `projects/` is one codebase within the research project, or the template should use a less overloaded name such as `code/`.
