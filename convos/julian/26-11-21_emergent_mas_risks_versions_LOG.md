Can you compare the papers: https://openreview.net/pdf?id=Jg9BGDTsxt and https://arxiv.org/abs/2603.27771

(After an interruption:) Please only compare them for now. I've dowloaded the openreview paper to the repo root `68_Emergent_*.pdf`

---

26-11-21, Claude Opus 5.5 — *workshop vs arXiv v4 comparison*

I have read the main text of both versions in full and compared all 15 risk sections with a diff. Sources:
- **Workshop version (WS):** `68_Emergent_Social_Intelligenc.pdf` (repo root, untracked). "Emergent Social Intelligence Risks in Generative Multi-Agent Systems", accepted to the 2nd Workshop on Compositional Learning at ICML 2026. 74 pages; PDF built 12 Jun 2026.
- **arXiv 2603.27771, latest version v4 (V4):** "Emergent Risks in Generative Multi-Agent Systems", 29 Oct 2026, 91 pages. Downloaded to the session scratchpad only, not stored in the repo.
- arXiv history: v1 29 Mar, v2 4 Apr, v3 10 Sep, v4 29 Oct 2026. v1–v3 carry the title with "Social Intelligence"; v3 dropped it. The arXiv abstract is identical in v1–v4.
- Same 15 authors (Huang, Jiang, Wang, … Zhang; Notre Dame lead). License: V4 is CC BY 4.0; the WS license was not checked.

Per the user's instruction, neither paper was added to `papers/`.

## Bottom line

[verified: text diff + reading, 26-11-21] **These are two editions of the same paper, with the same 15 risk scenarios, the same experiments and the same reported numbers.** WS is the earlier, compressed conference edition. V4 is a later, reorganised long-form edition with redrawn figures. Nothing I found suggests new experiments were run for V4.

Per risk section, 63–91% of sentences match (fuzzy match, ratio > 0.85). The real overlap is higher, because the two-column WS extraction breaks sentences. The unmatched sentences are almost all citation style (author-year → numbered), equation typesetting, and figure/table text.

## What differs

| | Workshop (Jun 2026) | arXiv v4 (Oct 2026) |
|---|---|---|
| Title | "Emergent **Social Intelligence** Risks …" | "Emergent Risks …" |
| Abstract | Rewritten, shorter; ends with "motivating mechanism-level rather than agent-level safety design" | Original arXiv abstract; ends with "the dark side of intelligent multi-agent systems" |
| Structure | 8-page main text: Intro, **Related Work**, Preliminary, one compressed §4 covering all 15 risks, Key Findings, **Discussion**, Conclusion, **Limitations**, **Impact Statement**; risk details in appendices D–R | Intro, Key Findings, Preliminary, then **one full section per risk (§4–§18)**, Conclusion; experiment details / case studies / trial records in appendices A–E |
| Related Work section | Yes (single-agent safety, emergent collective behaviour, position papers) | **None** |
| Discussion | "Why instruction-level mitigations fail" + four concrete "mechanism-level design directions" (incentive frictions like the $80 GUARANTEE fee; evidence-weighted aggregation; arbitrator/clarification loops; source-grounded auditing) | Only a short "Mitigation Strategies" paragraph in the Conclusion |
| Limitations | Explicit: "empirical and exploratory … modest-N quantitative trends rather than tight estimates of failure rates", plus 4 future-work items | **No limitations section** (grep finds none); instead claims "This controlled design yields reliable and reproducible signals" |
| Figures 1–4 | Cartoon illustrations | Redrawn panels, each ending with a measured result ("72 of 128 relayed values (56%) were false", "wrong plans rose from 0/10 to 10/10", …) |
| Result figures in risk sections | Bar/line charts | Redesigned to print every run/cell exactly ("all 18 scores are shown") |
| Code | No link found | Front-page links to a toolkit: https://github.com/HowieHwong/RiskLab, plus docs and a blog page |

## Errors and inconsistencies found

1. [verified: both versions read 26-11-21] **The WS main text misreports the steganography result (Risk 4.2).**
   - WS §4.4 says the Encoder and Decoder "spontaneously evolve covert encodings (e.g., coded keywords, indirect references) that successfully transmit a target number while passing the Regulator filter".
   - WS's own Appendix Q, and V4 §17, report the opposite: "Across all 10 independent runs, the success condition … was never met". The hints were either blocked numbers or phrases like "milestone that stands tall" that the Decoder couldn't use.
   - V4's Figure 4 states it correctly ("0 of 10 runs").
   - WS's Discussion still lists steganography as a "silent risk" needing auditing.
   - So anyone citing the workshop version for "LLM agents spontaneously develop steganography" is citing a claim the paper's own data refutes.
2. [verified: table read in both versions, 26-11-21] **The majority-sway news experiment (Risk 2.1, Experiment I) doesn't support its stated interpretation, in either version.** The table is the same in both (WS Table 7, V4 Table 9):
   - The Summary agent's final verdict matches the agents' majority in only 4 of the 9 runs with a majority (E2, E4, E7, E9; E5 is a tie).
   - In 4 runs (E1, E3, E8, E10) most agents said FAKE, yet the Summary agent output TRUE.
   - Both texts say "only E7 reached a within-run consensus that the news was false". The table shows FAKE majorities in E1, E3, E7, E8, E9 and E10.
   - WS says "Final verdicts predominantly track the numerical majority". V4's figure says the agent sided "with the larger, louder group".
   - What the data actually shows is a Summary agent biased toward TRUE regardless of the vote, which is a different failure from conformity.
   - The second majority-sway experiment (the Bedrock/Scalpel remediation debate) was not checked in this depth.
3. [verified: grep of all 15 risk sections in both versions, 26-11-21] **For 11 of the 15 risks, neither version names the LLM that runs the agents** (Risks 1.1–1.5, 2.1, 2.2, 3.1, 3.2, 4.1). Models are named only in these places:
   - Risk 3.3: GPT-4o, with GPT-4o-mini for comparison.
   - Risk 3.5: gemini-2.5-flash vs gpt-4o-mini.
   - Risk 4.2: gpt-4o-mini.
   - GPT-5 as the judge for Risks 3.4 and 4.3.

   The RiskLab repository may specify the rest; I did not check it.
4. [concluded: from the reported run counts] **Sample sizes are small, in both versions.** Most conditions have 3–10 runs: e.g. Risk 1.3 has 3 trials × 6 conditions, Risk 3.1 has 3 runs per condition, Risk 1.1 has 5 runs × 3 conditions, and Risk 2.2 has 10 runs per condition. There are no confidence intervals; V4's figure captions say so explicitly ("no confidence interval is inferred"). WS's limitations paragraph acknowledges this. V4 drops that paragraph and calls the signals "reliable and reproducible".

## Relevance to mas-risks

[assumed: my read, not discussed with the team]
- **The closest prior work to this project so far.** Same topic, 15 ready-made scenarios, and (per V4) an open toolkit. Risks 2.1 and 2.2 (majority sway, authority deference) are in effect measurements of susceptibility to social influence. So are the prompt-level conditions in Risk 1.1 (persona and long-term-return guidance).
- **What they don't do is what this project proposes.** All agents are closed API models, mostly unnamed, and influence is varied only through prompts (persona, authority labels, group composition). There are no small open-weight agents and no trained-in control of susceptibility.
- **Which version to cite.** Cite the arXiv version for the numbers (more complete records). Cite the workshop version only for its limitations and discussion, and not for the steganography claim.

---

Can you add the newer version to papers?

---

26-11-21, Claude Opus 5.5 — *v4 stored in papers*

At the user's request, arXiv v4 is now stored at `papers/2603.27771_emergent_mas_risks/`, with `notes.md` carrying this comparison's findings. Details of the conversion are in `convos/julian/26-11-21_papers_library_LOG.md` (entry "second paper (2603.27771v4) and converter extensions"). The workshop PDF is still not stored.
