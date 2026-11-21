"""Convert an arXiv paper's HTML rendering (LaTeXML) to agent-readable markdown.

Usage: python3 -I arxiv_html2md.py <id>v<n> <paper.html> <abs.html> <out.md> <retrieved YY-MM-DD>
  <id>v<n>    versioned arXiv id, e.g. 2502.12206v1
  paper.html  downloaded from https://arxiv.org/html/<id>v<n>   (body)
  abs.html    downloaded from https://arxiv.org/abs/<id>v<n>    (metadata: title, authors, license)
Needs beautifulsoup4. Workflow and folder conventions: papers/README.md.

Output: a metadata header, then the body. Math is kept as LaTeX ($...$), tables
become markdown tables, image figures become links to figures/<name> (download
the images separately), and SVG text boxes (tcolorbox prompts/transcripts) become
blockquotes. Unknown structural elements raise instead of being dropped, because
a silently missing section is the failure mode that matters here. A clean run is
still no proof of fidelity: read the output and spot-check tables against the PDF.
"""
import re
import sys

from bs4 import BeautifulSoup, NavigableString, Tag

assert len(sys.argv) == 6, __doc__
vid, src, abs_src, out, retrieved = sys.argv[1:]
assert re.fullmatch(r"\d{4}\.\d{4,5}v\d+", vid), f"expected versioned arXiv id like 2502.12206v1, got {vid}"
assert re.fullmatch(r"\d\d-\d\d-\d\d", retrieved), f"date must be YY-MM-DD, got {retrieved}"
soup = BeautifulSoup(open(src, encoding="utf-8").read(), "html.parser")
doc = soup.find("article", class_="ltx_document")
assert doc is not None, "no ltx_document article found"

abs_soup = BeautifulSoup(open(abs_src, encoding="utf-8").read(), "html.parser")
def meta(name, many=False):
    vals = [m["content"] for m in abs_soup.find_all("meta", attrs={"name": name})]
    assert vals, f"abs page has no <meta name={name}>"
    return vals if many else vals[0]
lic = abs_soup.find("a", href=re.compile(r"(creativecommons\.org|arxiv\.org/licenses)"))
assert lic is not None, "no license link on abs page; check the license by hand before storing the paper"
arxiv_id = meta("citation_arxiv_id")
assert vid.startswith(arxiv_id + "v"), f"abs page is for {arxiv_id}, but id argument is {vid}"
header = "\n".join([
    f"# {meta('citation_title')}",
    "",
    f"- **Authors:** {'; '.join(meta('citation_author', many=True))}",
    f"- **arXiv:** [{vid}](https://arxiv.org/abs/{vid}) (this version; later versions may differ)",
    f"- **Submitted:** {meta('citation_date')}",
    f"- **License:** {lic['href']}",
    f"- **Retrieved and converted:** {retrieved}, with `papers/tools/arxiv_html2md.py`. Not a verbatim copy: check numbers against the PDF before relying on them.",
    "",
    "---",
    "",
    "",
])

def classes(t):
    return t.get("class") or []

def has(t, c):
    return c in classes(t)

def inline(node):
    """Render inline content to a single string."""
    if isinstance(node, NavigableString):
        return str(node)
    if not isinstance(node, Tag):
        return ""
    if node.name == "math":
        alt = node.get("alttext")
        assert alt is not None, f"math without alttext: {node}"
        return f"${alt.strip()}$"
    if node.name in ("script", "style", "button") or has(node, "ltx_ERROR"):
        return ""  # ltx_ERROR: LaTeX macros LaTeXML could not expand; their text is the raw macro name
    if node.name == "br":
        return "\n"
    if node.name == "img":
        return f"![{node.get('alt','')}]({node.get('src')})"
    if has(node, "ltx_note_mark") or has(node, "ltx_tag_note"):
        return ""
    if has(node, "ltx_note"):
        content = node.find(class_="ltx_note_content")
        assert content is not None
        txt = " ".join(inline(c) for c in content.children if not (isinstance(c, Tag) and (has(c, "ltx_note_mark") or has(c, "ltx_tag"))))
        return f" [Footnote: {norm(txt)}]"
    s = "".join(inline(c) for c in node.children)
    if node.name == "a" and node.get("href", "").startswith("http"):  # internal cross-refs use "#..." hrefs
        return f"[{s}]({node['href']})" if s.strip() and s.strip() != node["href"] else node["href"]
    if has(node, "ltx_font_bold") or node.name in ("b", "strong"):
        return f"**{s.strip()}**" if s.strip() else s
    if has(node, "ltx_font_italic") or has(node, "ltx_emph") or node.name in ("i", "em"):
        return f"*{s.strip()}*" if s.strip() else s
    return s

def norm(s):
    return re.sub(r"[ \t]+", " ", re.sub(r"\s*\n\s*", " ", s)).strip()

def norm_keep_lines(s):
    lines = [re.sub(r"[ \t]+", " ", l).strip() for l in s.split("\n")]
    return "\n".join(l for l in lines if l)

def table_md(tab):
    rows = []
    for tr in tab.find_all("tr", class_="ltx_tr"):
        cells = []
        for td in tr.find_all(["td", "th"], recursive=False):
            txt = norm(inline(td)).replace("|", "\\|")
            span = int(td.get("colspan", 1))
            cells.extend([txt] + [""] * (span - 1))
        rows.append(cells)
    assert rows, "empty table"
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    lines = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * width]
    lines += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join(lines)

def picture_text(pic):
    """tcolorbox-style boxes are SVG with foreignObject text content."""
    parts = []
    for fo in pic.find_all(class_="ltx_foreignobject_content"):
        if fo.find_parent(class_="ltx_foreignobject_content") is not None:
            continue
        txt = blocks(fo)
        if txt.strip():
            parts.append(txt.strip())
    loose = [norm(t.get_text()) for t in pic.find_all("text")]
    parts += [t for t in loose if t]
    return parts

def graphic_link(obj):
    """SVG figures come as <object data=...svg>. Their text is drawn as glyph paths, so the
    SVG is unreadable for agents; the workflow renders each to figures/<stem>.png instead."""
    assert obj.get("type") == "image/svg+xml", f"unexpected <object>: {obj}"
    stem = obj["data"].split("/")[-1].rsplit(".", 1)[0]
    return f"![figure](figures/{stem}.png)"

def blocks(node, depth=0):
    """Render block-level content to markdown."""
    out = []
    for c in node.children:
        if isinstance(c, NavigableString):
            if c.strip():
                out.append(norm(str(c)))
            continue
        if not isinstance(c, Tag):
            continue
        cl = classes(c)
        if c.name in ("script", "style", "nav", "footer", "header") or has(c, "ltx_page_navbar") or has(c, "ltx_TOC") or has(c, "ltx_ERROR"):
            continue
        if c.name == "math":
            out.append(inline(c))
            continue
        if c.name == "object":
            out.append(graphic_link(c))
            continue
        if c.name == "h1" and has(c, "ltx_title_document"):
            continue  # title comes from the metadata header
        if c.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            lvl = int(c.name[1])
            out.append("#" * lvl + " " + norm(inline(c)))
        elif has(c, "ltx_authors"):
            continue  # LaTeXML runs names and affiliations together; header has the clean author list
        elif has(c, "ltx_abstract"):
            out.append(blocks(c, depth))
        elif c.name == "p" or has(c, "ltx_p"):
            out.append(norm_keep_lines(inline(c)) if c.find("br") else norm(inline(c)))
        elif has(c, "ltx_equation") or has(c, "ltx_equationgroup"):
            maths = [m.get("alttext") for m in c.find_all("math")]
            tags = [norm(t.get_text()) for t in c.find_all(class_="ltx_tag_equation")]
            out.append("$$" + " ".join(maths) + "$$" + (f"  {' '.join(tags)}" if tags else ""))
        elif c.name in ("ul", "ol"):
            for i, li in enumerate(c.find_all("li", recursive=False)):
                tag = li.find(class_="ltx_tag", recursive=False)
                if tag:
                    tag.extract()
                bullet = f"{i+1}." if c.name == "ol" else "-"
                body = blocks(li, depth + 1).strip().replace("\n", "\n  ")
                out.append(f"{bullet} {body}")
        elif has(c, "ltx_table"):
            cap = c.find(class_="ltx_caption")
            for tab in c.find_all("table", class_="ltx_tabular"):
                out.append(table_md(tab))
            if cap:
                out.append("*" + norm(inline(cap)) + "*")
        elif c.name == "table" and has(c, "ltx_tabular"):
            out.append(table_md(c))
        elif has(c, "ltx_figure"):
            caps = c.find_all(class_="ltx_caption")
            body = []
            for img in c.find_all("img"):
                body.append(f"![figure](figures/{img['src'].split('/')[-1]})")
            for obj in c.find_all("object"):
                body.append(graphic_link(obj))
            for pic in c.find_all(class_="ltx_picture"):
                if pic.find_parent(class_="ltx_picture") is not None:
                    continue
                for t in picture_text(pic):
                    body.append("> " + t.replace("\n", "\n> "))
            for tab in c.find_all("table", class_="ltx_tabular"):
                body.append(table_md(tab))
            if not body and not caps:
                raise AssertionError(f"empty figure: {c.get('id')}")
            out.append(f"<!-- figure {c.get('id')} -->")
            out.extend(body)
            for cap in caps:
                out.append("*" + norm(inline(cap)) + "*")
        elif has(c, "ltx_picture"):
            for t in picture_text(c):
                out.append("> " + t.replace("\n", "\n> "))
        elif has(c, "ltx_bibliography"):
            title = c.find(class_="ltx_title")
            out.append("## " + (norm(inline(title)) if title else "References"))
            for item in c.find_all("li", class_="ltx_bibitem"):
                tag = item.find(class_="ltx_tag_bibitem")
                num = norm(tag.get_text()) if tag else ""
                # numeric styles cite as [43]; keep the number or in-text citations can't be resolved
                prefix = num + " " if re.fullmatch(r"\[\d+\]", num) else ""
                out.append("- " + prefix + norm(" ".join(inline(b) for b in item.find_all(class_="ltx_bibblock"))))
        elif c.name == "div" and c.get("class") is None and not c.get_text(strip=True):
            continue
        elif c.name in ("div", "section", "span", "figure", "blockquote", "article", "foreignobject") or any(x.startswith("ltx_") for x in cl):
            inner = blocks(c, depth)
            if inner.strip():
                out.append(inner)
        elif c.name in ("svg", "g"):
            inner = blocks(c, depth)
            if inner.strip():
                out.append(inner)
        else:
            raise AssertionError(f"unhandled element <{c.name} class={cl}>")
    return "\n\n".join(x for x in out if x and x.strip())

md = blocks(doc)
md = re.sub(r"\n{3,}", "\n\n", md)
open(out, "w", encoding="utf-8").write(header + md + "\n")
print(f"wrote {len(md)} chars")
