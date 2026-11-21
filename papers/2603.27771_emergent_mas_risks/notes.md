# Notes: Emergent Risks in Generative Multi-Agent Systems (arXiv 2603.27771v4)

Agent-written notes on the paper; nothing here is from the paper itself. The paper text is in `paper.md`. Version history and the comparison with the ICML 2026 workshop edition are in `convos/julian/26-11-21_emergent_mas_risks_versions_SUMMARY.md`.

**Last updated:** 26-11-21 (Claude Opus 5.5, from the version comparison and the conversion)

## What the paper does

The paper presents 15 controlled multi-agent simulations, one per "emergent risk", grouped into four categories:
1. **Incentive exploitation:** tacit collusion, priority monopolization, task avoidance, strategic misreporting, information-asymmetry exploitation.
2. **Collective-cognition failures:** majority sway, authority deference.
3. **Adaptive-governance failures:** no arbitrator, over-adherence to initial instructions, missing clarification, role-allocation failure, role instability.
4. **Others:** resource overreach, steganography, semantic drift.

Each risk has a deterministic environment, a fixed risk indicator, and a few repeated runs per condition. Influence or incentives are varied through prompts: personas, authority labels, group composition, fees. Code is linked from the title page: https://github.com/HowieHwong/RiskLab

## Possible relevance to mas-risks

[assumed: my read, not discussed with the team]
- **The closest prior work found so far.** Risks 2.1 (majority sway) and 2.2 (authority deference) are, in effect, measurements of susceptibility to social influence. The scenarios and the RiskLab toolkit could serve as a test bed for our own agents.
- **Where the gap is.** All agents are closed API models, mostly unnamed (see below), and susceptibility is varied only through prompts. Small open-weight agents with controlled susceptibility are not covered.

## Checks and caveats

- [verified: read in both editions, 26-11-21] **Risk 2.1, Experiment I (news verdicts): the data contradicts the stated interpretation.**
  - In Table 9 (Appendix E.1), the Summary agent's final verdict follows the agents' majority in only 4 of the 9 runs that have a majority (E2, E4, E7, E9; E5 is a tie).
  - In E1, E3, E8 and E10 most agents said FAKE, yet the final verdict was TRUE.
  - The paper's own figure for this experiment (`figures/composite-news.png`, panel b) shows the mismatches.
  - The text nevertheless says "only E7 reached a within-run consensus that the news was false", and Figure 2 says the summary agent was "siding with the larger, louder group".
  - The data fits a Summary agent biased toward TRUE better than one that conforms to the majority.
- [verified: grep of all 15 risk sections, 26-11-21] **For 11 of the 15 risks the paper never names the LLM running the agents** (1.1–1.5, 2.1, 2.2, 3.1, 3.2, 4.1). Models are named only in these places:
  - Risk 3.3: GPT-4o, with GPT-4o-mini for comparison.
  - Risk 3.5: gemini-2.5-flash vs gpt-4o-mini.
  - Risk 4.2: gpt-4o-mini.
  - GPT-5 as the judge in Risks 3.4 and 4.3.

  The RiskLab repository may fill this in; it has not been checked.
- [concluded: from the run counts reported in the paper] **Small n and no uncertainty estimates.** Most conditions have 3–10 runs: e.g. 3 trials × 6 conditions in Risk 1.3, 3 runs per condition in Risk 3.1, 5 runs × 3 conditions in Risk 1.1. There are no confidence intervals. Despite this, the paper calls its signals "reliable and reproducible".
- [verified: comparison of editions, 26-11-21] **This version has no limitations section.** The earlier workshop edition had one, calling the results "modest-N quantitative trends rather than tight estimates of failure rates".
- **The steganography result is negative.** Risk 4.2 reports 0 of 10 runs in which the secret number got through, and this version states that correctly. The workshop edition's main text wrongly claimed success, so don't cite that edition for steganography.

## Conversion notes

- The figures came as SVG with text drawn as glyph outlines. They were rendered to PNG with headless Firefox. Figures 1–4 (the per-risk overview panels) are transcribed in `paper.md`.
- Before conversion, the LaTeXML HTML contained leaked font-setup macros and a duplicated title block. These were removed by hand and the title-page links moved into the header.
- Checked against the PDF:
  - All 18 sections and appendices A–E are present.
  - Of 1,505 PDF sentences, the only ones not found in the markdown are math (the PDF uses Unicode, the markdown LaTeX), figure-panel text, and DOI/ISBN fragments from the references.
  - The tables checked match the PDF: E.1, Table 6, and the Risk 3.5 counts.
