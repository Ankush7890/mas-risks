# papers/

Papers stored as markdown so agents can read them directly. Each paper has its own folder.

## Folder layout

```
papers/
├── README.md                      # this file: conventions + index
├── tools/arxiv_html2md.py         # converter for arXiv papers
└── {id}_{short_slug}/
    ├── paper.md                   # the paper: metadata header, then the converted text
    ├── figures/                   # image figures referenced from paper.md
    ├── notes.md                   # optional: our notes on the paper (agent- or human-written)
    └── paper.pdf                  # optional, local only (gitignored)
```

- **Folder name:** for arXiv papers, the arXiv ID without version, then a short lowercase slug, e.g. `2502.12206_paperclip_maximizer`. For papers not on arXiv: `{year}_{firstauthor}_{slug}`.
- **`paper.md` holds only the paper.** Its header records the source, version, license and retrieval date. Commentary goes in `notes.md`, so a reader always knows which text is the authors' and which is ours. The one exception is a figure that exists only as an image. In that case, add a transcription of its text below the image in `paper.md`, in square brackets, naming the transcriber and the date. Agents reading the markdown would otherwise miss that content.
- **`notes.md` is not created by default.** Write one when someone has actually read the paper with a question in mind, such as a comparison or a check of its claims. Generic summaries aren't worth the reading time.
- **License:** whether to store a paper's full text is the user's call. Before converting, the agent checks the license. If it may not permit redistribution, the agent warns the user and waits for their decision. arXiv's default non-exclusive license and unclear licenses fall into this group, while CC BY, CC BY-SA and CC0 are fine. Record the license in the `paper.md` header either way.
- **PDFs are local only.** A human may keep the PDF next to `paper.md`, e.g. `paper.pdf`, for reading. PDFs under `papers/` are gitignored and never committed. The link in the header is the reference copy.

## Adding an arXiv paper

The converter uses arXiv's HTML rendering (`arxiv.org/html/<id>v<n>`), which keeps math as LaTeX and tables as tables. Not every paper has one. For papers without it, convert by other means and say how in the header.

```bash
ID=2502.12206v1; D=$(mktemp -d)       # downloads go in their own empty directory
curl -sSL -o $D/abs.html   https://arxiv.org/abs/$ID
curl -sSL -o $D/paper.html https://arxiv.org/html/$ID
grep -o '<img[^>]*src="[^"]*"' $D/paper.html   # find image figures and download them into figures/
python3 -I papers/tools/arxiv_html2md.py $ID $D/paper.html $D/abs.html papers/<folder>/paper.md <YY-MM-DD>
```

The script needs `beautifulsoup4`. A clean run does not prove the conversion is faithful. Afterwards:
1. Read the whole output by eye.
2. Compare the word count with `pdftotext` output of the PDF.
3. Spot-check several table values against the PDF.
4. Look at each image figure and transcribe any text the paper doesn't contain elsewhere (see the exception above).

**SVG figures.** Some papers ship figures as SVG `<object>`s whose text is drawn as glyph outlines, so agents can't read it. The converter links these as `figures/<stem>.png`. Download the SVGs to the scratch directory, not into the repo, and render each one to PNG with headless Firefox (no extra install needed). Wrap the SVG in an HTML page whose `<img>` is 1200 px wide, then run:
`firefox --headless --window-size=1200,<height> --screenshot out.png file:///path/wrapper.html`
Here `<height>` is 1200 × the viewBox's height/width ratio. `papers/2603.27771_emergent_mas_risks/` was made this way.

**Paper-specific cleanup.** If LaTeXML leaks preamble junk, such as unexpanded macro arguments or a duplicated title block, remove it by hand and note that in the paper's `notes.md`.

## Index

| Folder | Paper | One-line content | Notes | Added |
|--------|-------|------------------|-------|-------|
| [2502.12206_paperclip_maximizer](2502.12206_paperclip_maximizer/paper.md) | He et al. 2025, *Evaluating the Paperclip Maximizer: Are RL-Based Language Models More Likely to Pursue Instrumental Goals?* | InstrumentalEval: 76 single-turn scenarios in six instrumental-convergence categories, scored by an LLM judge. Reasoning ("RL") models score about twice as high as RLHF models, and a goal-nudging system prompt raises the rates. | [notes.md](2502.12206_paperclip_maximizer/notes.md): small-n caveats, one inconsistent cell in Table 3 | 26-11-21, julian |
| [2603.27771_emergent_mas_risks](2603.27771_emergent_mas_risks/paper.md) | Huang et al. 2026, *Emergent Risks in Generative Multi-Agent Systems* (arXiv v4; earlier titled "Emergent Social Intelligence Risks…", ICML 2026 workshop edition) | 15 controlled multi-agent simulations of emergent risks (collusion, monopolization, majority sway, authority deference, governance failures, steganography, semantic drift), 3–10 runs per condition, prompt-level manipulations, closed models; RiskLab toolkit | [notes.md](2603.27771_emergent_mas_risks/notes.md): Risk 2.1 data contradicts its interpretation; models unnamed for 11/15 risks; small n | 26-11-21, julian |
