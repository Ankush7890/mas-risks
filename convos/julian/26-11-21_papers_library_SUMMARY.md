# SUMMARY: Papers library

**Last updated:** 26-11-21 (two papers added; converter extended; folder rules ratified with two changes)

The user asked for a `papers/` folder storing agent-readable markdown versions of papers, one folder per paper. [decided] (user's request at the top of the LOG)

Conventions [decided] (ratified by the user in chat, transcribed in the LOG, with two changes), documented in `papers/README.md`:
- Folders are named `{arxiv id}_{slug}`. Each holds `paper.md` (paper text only, with a metadata header) and `figures/`.
- `notes.md` is optional and not created by default; write one only when a paper is read with a purpose.
- Image-only figure text is transcribed in marked brackets inside `paper.md`.
- Storing full text is the user's call; the agent checks the license and warns if it may not allow redistribution. We initially proposed refusing non-permissive licenses; the user changed this.
- PDFs may sit next to `paper.md` for humans but are gitignored (`papers/**/*.pdf`). We initially proposed no PDFs at all.
- arXiv papers are converted from the arXiv HTML rendering with `papers/tools/arxiv_html2md.py`, which handles SVG figures (rendered to PNG with headless Firefox) and numeric citation styles. The verification steps after conversion are listed in `papers/README.md`.

Papers added:
- `papers/2603.27771_emergent_mas_risks/`: Huang et al. 2026, Emergent Risks in Generative MAS (arXiv v4). 15 multi-agent risk simulations; closest prior work to mas-risks. [verified: conversion checked against the PDF, 26-11-21]. SVG figures were rendered to PNG and Figures 1–4 transcribed. `notes.md` carries the version-comparison findings.
- `papers/2502.12206_paperclip_maximizer/`: He et al. 2025, InstrumentalEval (instrumental convergence in reasoning vs. RLHF models; goal-nudging prompt raises rates). [verified: conversion checked against the PDF, 26-11-21]. `notes.md` records small-n caveats and one inconsistent cell in Table 3 [verified: arithmetic].

LOG: `convos/julian/26-11-21_papers_library_LOG.md`
