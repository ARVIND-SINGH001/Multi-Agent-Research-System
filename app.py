import html
import re
import time

import streamlit as st
from tools import scraped_urls

from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain

st.set_page_config(
    page_title="Research desk",
    page_icon="🔎",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ---------------------------------------------------------------- styling ---
# Theme is forced via CSS so this works without a .streamlit/config.toml.
INK, CARD, LINE, MUTED = "#1B1535", "#FFFFFF", "#E4DFF5", "#6B6785"
VIOLET, PINK, ORANGE = "#7C3AED", "#EC4899", "#F59E0B"
GRAD = f"linear-gradient(135deg, {VIOLET}, {PINK})"
GRAD_WIDE = f"linear-gradient(90deg, {VIOLET}, {PINK}, {ORANGE})"
GRAD_REPORT = f"linear-gradient(90deg, {VIOLET}, {PINK})"
GRAD_REVIEW = f"linear-gradient(90deg, {PINK}, {ORANGE})"

st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap');

:root {{ color-scheme: light; }}
.stApp {{
    background:
        radial-gradient(900px 520px at 8% -8%, rgba(124,58,237,.20), transparent 60%),
        radial-gradient(800px 520px at 100% 0%, rgba(236,72,153,.17), transparent 60%),
        radial-gradient(900px 600px at 50% 112%, rgba(6,182,212,.17), transparent 60%),
        #F8F6FF;
    background-attachment: fixed;
}}
[data-testid="stHeader"] {{ background: transparent; }}
[data-testid="stToolbar"], [data-testid="stAppDeployButton"], .stAppDeployButton, #MainMenu {{ display: none; }}
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] {{ display: none; }}

.stApp, .stApp p, .stApp li, .stApp label, .stApp input, .stApp button, .stApp textarea {{
    font-family: 'IBM Plex Sans', system-ui, sans-serif;
    color: {INK};
}}
.stApp h1, .stApp h2, .stApp h3 {{ font-family: 'Space Grotesk', system-ui, sans-serif; color: {INK}; }}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {{ color: {MUTED}; }}
.block-container {{ max-width: 900px; padding-top: 3rem; padding-bottom: 5rem; }}

/* hero */
.hero {{
    font-family: 'Space Grotesk', system-ui, sans-serif; font-weight: 700;
    font-size: 4.6rem; line-height: 1; letter-spacing: -0.045em; color: {INK}; margin: 0 0 0.6rem;
}}
.hero span {{
    background: {GRAD_WIDE}; background-size: 200% 100%;
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
    animation: flow 6s ease-in-out infinite alternate;
}}
@keyframes flow {{ to {{ background-position: 100% 0; }} }}
.tagline {{ font-size: 1.2rem; color: {MUTED}; margin: 0 0 1.75rem; max-width: 52ch; line-height: 1.5; }}
@media (max-width: 640px) {{ .hero {{ font-size: 3rem; }} }}

/* input + buttons */
[data-baseweb="input"], [data-baseweb="base-input"] {{ background: {CARD}; }}
[data-baseweb="input"] {{ border: 2px solid {LINE}; border-radius: 14px; transition: border-color .2s, box-shadow .2s; }}
[data-baseweb="input"]:focus-within {{ border-color: {VIOLET}; box-shadow: 0 0 0 5px rgba(124,58,237,.16); }}
.stTextInput input {{ background: {CARD}; font-size: 1.15rem; padding: 0.95rem 1.1rem; }}
.stTextInput input::placeholder {{ color: #9A96B5; opacity: 1; }}
div[data-testid="stForm"] {{ padding: 0; }}

.stFormSubmitButton > button {{
    background: {GRAD}; border: 0; border-radius: 12px; font-weight: 600; font-size: 1.05rem;
    padding: 0.65rem 1.7rem; color: #fff; box-shadow: 0 10px 24px -10px rgba(236,72,153,.7);
    transition: transform .15s ease, box-shadow .15s ease;
}}
.stFormSubmitButton > button p {{ color: #fff; }}
.stFormSubmitButton > button:hover {{
    transform: translateY(-2px) scale(1.02); color: #fff; box-shadow: 0 16px 30px -10px rgba(236,72,153,.8);
}}
.stFormSubmitButton > button:active {{ transform: translateY(0) scale(.99); }}

/* suggestion chips + download */
.stButton > button, .stDownloadButton > button {{
    background: {CARD}; border: 1.5px solid {LINE}; border-radius: 999px; font-weight: 500;
    transition: transform .15s ease, border-color .15s ease, background .15s ease;
}}
.stButton > button:hover, .stDownloadButton > button:hover {{
    border-color: {VIOLET}; color: {VIOLET}; background: #F4EEFF; transform: translateY(-2px);
}}
.stButton > button p {{ font-size: 0.92rem; }}

/* progress tiles */
.steps {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.85rem; margin: 1.75rem 0 0.5rem; }}
@media (max-width: 640px) {{ .steps {{ grid-template-columns: repeat(2, 1fr); }} }}
.step {{
    position: relative; overflow: hidden; background: {CARD}; border: 1.5px solid {LINE};
    border-radius: 16px; padding: 1.1rem 1rem 0.9rem; display: flex; flex-direction: column; gap: 0.2rem;
    transition: transform .25s ease, background .25s ease;
}}
.step::before {{ content: ""; position: absolute; inset: 0 0 auto 0; height: 5px; background: {LINE}; }}
.step .ico {{ font-size: 1.9rem; line-height: 1; filter: grayscale(1); opacity: .5; display: inline-block; }}
.step .lbl {{ font-family: 'Space Grotesk', sans-serif; font-weight: 600; font-size: 1.1rem; margin-top: .35rem; }}
.step .meta {{ font-size: 0.85rem; color: {MUTED}; min-height: 1.2em; }}
.step.pending .lbl {{ color: {MUTED}; }}
.step.running {{ transform: translateY(-4px); border-color: var(--c); box-shadow: 0 14px 28px -14px var(--c); }}
.step.running::before {{
    background: repeating-linear-gradient(45deg, var(--c) 0 10px, rgba(255,255,255,.55) 10px 20px);
    background-size: 28px 28px; animation: stripes .7s linear infinite;
}}
.step.running .ico {{ filter: none; opacity: 1; animation: wiggle 1s ease-in-out infinite; }}
.step.running .meta {{ color: var(--c); font-weight: 600; }}
.step.done {{ background: color-mix(in srgb, var(--c) 9%, white); border-color: var(--c); }}
.step.done::before {{ background: var(--c); }}
.step.done .ico {{ filter: none; opacity: 1; }}
.step.done .meta {{ color: var(--c); font-weight: 600; }}
.step.error {{ border-color: #EF4444; }}
.step.error::before {{ background: #EF4444; }}
.step.error .meta {{ color: #EF4444; font-weight: 600; }}
@keyframes stripes {{ to {{ background-position: 28px 0; }} }}
@keyframes wiggle {{ 0%,100% {{ transform: rotate(-9deg) scale(1); }} 50% {{ transform: rotate(9deg) scale(1.18); }} }}

/* result cards */
[data-testid="stVerticalBlockBorderWrapper"] {{
    background: {CARD} {GRAD_WIDE} top / 100% 5px no-repeat;
    border: 1px solid {LINE}; border-radius: 18px; padding: 1.6rem 2rem 1.8rem;
    box-shadow: 0 24px 48px -28px rgba(76,29,149,.38);
}}
.meta-line {{
    display: inline-block; background: {CARD}; border: 1.5px solid {LINE}; border-radius: 999px;
    padding: 0.4rem 1rem; font-size: 0.95rem; color: {MUTED}; margin: 1.5rem 0 1.25rem;
}}
.meta-line b {{ color: {INK}; font-weight: 600; }}

/* section headers: big title + coloured rule so each section's start is obvious */
.sec {{
    display: flex; align-items: center; gap: 0.7rem;
    font-family: 'Space Grotesk', system-ui, sans-serif; font-weight: 700;
    font-size: 2.5rem; line-height: 1.1; letter-spacing: -0.035em; margin: 0;
}}
.sec .txt {{ -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }}
.sec.report .txt {{ background-image: {GRAD_REPORT}; }}
.sec.review .txt {{ background-image: {GRAD_REVIEW}; }}
.rule {{ height: 5px; border-radius: 999px; margin: 0.9rem 0 1.5rem; }}
.rule.report {{ background: {GRAD_REPORT}; }}
.rule.review {{ background: {GRAD_REVIEW}; }}
.sep {{ display: flex; align-items: center; gap: 1rem; margin: 2.4rem 0; color: {MUTED}; font-size: 1.1rem; }}
.sep::before, .sep::after {{ content: ""; flex: 1; height: 2px; background: linear-gradient(90deg, transparent, {LINE}, transparent); }}
@media (max-width: 640px) {{ .sec {{ font-size: 1.9rem; }} }}

/* reading text */
[data-testid="stVerticalBlockBorderWrapper"] .stMarkdown p,
[data-testid="stVerticalBlockBorderWrapper"] .stMarkdown li {{
    font-family: 'Source Serif 4', Georgia, serif; font-size: 1.1rem; line-height: 1.8; max-width: 68ch;
}}
[data-testid="stVerticalBlockBorderWrapper"] .stMarkdown h1,
[data-testid="stVerticalBlockBorderWrapper"] .stMarkdown h2,
[data-testid="stVerticalBlockBorderWrapper"] .stMarkdown h3 {{
    font-size: 1.35rem !important; margin-top: 1.7rem; letter-spacing: -0.01em;
}}
[data-testid="stVerticalBlockBorderWrapper"] .stMarkdown h1:first-child {{ font-size: 1.9rem !important; }}

/* score ring */
.score-row {{ display: flex; align-items: center; gap: 1.25rem; margin: 0.75rem 0 1rem; }}
.ring {{
    width: 112px; height: 112px; border-radius: 50%; flex: none; display: grid; place-items: center;
    background: conic-gradient(var(--c) calc(var(--p) * 1%), #ECE8F8 0);
}}
.ring > div {{
    width: 88px; height: 88px; border-radius: 50%; background: {CARD};
    display: flex; flex-direction: column; align-items: center; justify-content: center; line-height: 1;
}}
.ring b {{ font-family: 'Space Grotesk', sans-serif; font-size: 2.2rem; font-weight: 700; color: var(--c); }}
.ring span {{ font-size: .8rem; color: {MUTED}; margin-top: 2px; }}
.verdict {{ font-family: 'Space Grotesk', sans-serif; font-size: 1.35rem; font-weight: 600; }}

/* supporting material */
[data-testid="stExpander"] details {{ background: {CARD}; border: 1.5px solid {LINE}; border-radius: 14px; }}
[data-testid="stExpander"] summary p {{ font-weight: 500; }}

@media (prefers-reduced-motion: reduce) {{ * {{ transition: none !important; animation: none !important; }} }}
</style>
""",
    unsafe_allow_html=True,
)




# ---------------------------------------------------------------- helpers ---
def as_text(content) -> str:
    """LangChain content can be a str or a list of blocks; normalise to str."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type", "text") == "text":
                parts.append(block.get("text", ""))
        return "\n\n".join(p for p in parts if p)
    return str(content)


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "report"


def find_score(text: str):
    """Pulls an 'x/10' style score out of the critique if the critic wrote one."""
    m = re.search(r"(\d+(?:\.\d+)?)\s*/\s*10", text)
    return float(m.group(1)) if m else None


# ------------------------------------------------------------------- pdf ---
_FONT_SETS = [
    # Windows
    ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf",
     "C:/Windows/Fonts/ariali.ttf", "C:/Windows/Fonts/arialbi.ttf"),
    # macOS
    ("/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
     "/System/Library/Fonts/Supplemental/Arial Italic.ttf", "/System/Library/Fonts/Supplemental/Arial Bold Italic.ttf"),
    # Linux
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
     "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf"),
]


def _register_fonts():
    """Registers a unicode TTF family as 'Body' if one is found, else falls back to Helvetica."""
    import os
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    for paths in _FONT_SETS:
        if all(os.path.exists(p) for p in paths):
            names = ("Body", "Body-Bold", "Body-Italic", "Body-BoldItalic")
            for name, path in zip(names, paths):
                pdfmetrics.registerFont(TTFont(name, path))
            pdfmetrics.registerFontFamily(
                "Body", normal=names[0], bold=names[1], italic=names[2], boldItalic=names[3]
            )
            return "Body", "Body-Bold", "Courier"
    return "Helvetica", "Helvetica-Bold", "Courier"


def _inline_md(text: str) -> str:
    """Markdown inline syntax -> reportlab paragraph markup."""
    text = html.escape(text, quote=False)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" color="#1D4ED8">\1</a>', text)
    text = re.sub(r"`([^`]+)`", r'<font face="Courier" size="9">\1</font>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<![\*\w])\*(?!\s)(.+?)(?<!\s)\*(?![\*\w])", r"<i>\1</i>", text)
    return text


def make_pdf(topic: str, markdown_text: str):
    """Renders the markdown report to a clean white A4 PDF. Returns bytes, or None on any failure."""
    try:
        from io import BytesIO
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

        body_font, bold_font, mono_font = _register_fonts()
        dark, grey = colors.HexColor("#111827"), colors.HexColor("#6B7280")

        base = ParagraphStyle("base", fontName=body_font, fontSize=10.5, leading=16, textColor=dark, spaceAfter=7)
        h = {
            1: ParagraphStyle("h1", parent=base, fontName=bold_font, fontSize=22, leading=27, spaceBefore=4, spaceAfter=10),
            2: ParagraphStyle("h2", parent=base, fontName=bold_font, fontSize=15.5, leading=20, spaceBefore=14, spaceAfter=6),
            3: ParagraphStyle("h3", parent=base, fontName=bold_font, fontSize=12.5, leading=17, spaceBefore=10, spaceAfter=4),
        }
        h_other = ParagraphStyle("h4", parent=base, fontName=bold_font, fontSize=11, leading=15, spaceBefore=8, spaceAfter=3)
        quote = ParagraphStyle("quote", parent=base, leftIndent=12, textColor=grey, borderPadding=(0, 0, 0, 6))
        code = ParagraphStyle("code", parent=base, fontName=mono_font, fontSize=8.5, leading=12, backColor=colors.HexColor("#F3F4F6"), borderPadding=6, spaceBefore=4, spaceAfter=10)
        cell = ParagraphStyle("cell", parent=base, fontSize=9, leading=12, spaceAfter=0)
        cell_head = ParagraphStyle("cellh", parent=cell, fontName=bold_font)

        # strip emoji / symbols the PDF font can't draw
        text = re.sub(r"[\U00010000-\U0010FFFF\u2600-\u27BF\uFE0F]", "", markdown_text).replace("\t", "    ")
        lines = text.splitlines()
        story, para, i = [], [], 0
        avail = A4[0] - 2 * 22 * mm

        def flush():
            if para:
                story.append(Paragraph(_inline_md(" ".join(s.strip() for s in para)), base))
                para.clear()

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            if stripped.startswith("```"):  # fenced code block
                flush()
                block, i = [], i + 1
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    block.append(lines[i])
                    i += 1
                body = "<br/>".join(html.escape(b).replace(" ", "&nbsp;") for b in block)
                story.append(Paragraph(body or "&nbsp;", code))
            elif not stripped:
                flush()
            elif re.match(r"^(-{3,}|\*{3,}|_{3,})$", stripped):
                flush()
                story.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#D1D5DB"), spaceBefore=6, spaceAfter=10))
            elif (m := re.match(r"^(#{1,6})\s+(.*)$", stripped)):
                flush()
                story.append(Paragraph(_inline_md(m.group(2).strip("# ").strip()), h.get(len(m.group(1)), h_other)))
            elif (m := re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", line)):
                flush()
                level = len(m.group(1)) // 2
                marker = "•" if m.group(2) in "-*+" else m.group(2)
                item = ParagraphStyle("li", parent=base, leftIndent=16 + 14 * level, bulletIndent=2 + 14 * level, spaceAfter=3)
                story.append(Paragraph(_inline_md(m.group(3)), item, bulletText=marker))
            elif stripped.startswith(">"):
                flush()
                story.append(Paragraph(_inline_md(stripped.lstrip("> ")), quote))
            elif stripped.startswith("|"):  # table
                flush()
                rows = []
                while i < len(lines) and lines[i].strip().startswith("|"):
                    cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                    if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
                        rows.append(cells)
                    i += 1
                i -= 1
                if rows:
                    n = max(len(r) for r in rows)
                    data = [
                        [Paragraph(_inline_md(c), cell_head if r == 0 else cell) for c in row + [""] * (n - len(row))]
                        for r, row in enumerate(rows)
                    ]
                    t = Table(data, colWidths=[avail / n] * n, repeatRows=1)
                    t.setStyle(TableStyle([
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F3F4F6")),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ]))
                    story += [t, Spacer(1, 10)]
            else:
                para.append(line)
            i += 1
        flush()

        def footer(canvas, doc):
            canvas.saveState()
            canvas.setFont(body_font, 8)
            canvas.setFillColor(grey)
            canvas.drawString(22 * mm, 12 * mm, f"Research desk  ·  {topic[:70]}")
            canvas.drawRightString(A4[0] - 22 * mm, 12 * mm, f"Page {doc.page}")
            canvas.restoreState()

        buf = BytesIO()
        SimpleDocTemplate(
            buf, pagesize=A4, title=topic, author="Research desk",
            leftMargin=22 * mm, rightMargin=22 * mm, topMargin=20 * mm, bottomMargin=22 * mm,
        ).build(story or [Paragraph("(empty report)", base)], onFirstPage=footer, onLaterPages=footer)
        return buf.getvalue()
    except Exception:
        return None


# --------------------------------------------------------------- pipeline ---
# Same steps and prompts as pipeline.py, one function per stage.
scraped_urls.clear()
def step_search(topic, state):
    agent = build_search_agent()
    res = agent.invoke(
        {"messages": [("user", f"Find recent, reliable and detailed information about {topic}")]}
    )
    state["search_results"] = res["messages"][-1].content


def step_read(topic, state):
    agent = build_reader_agent()
    res = agent.invoke({
        "messages": [
            (
                "user",
              f"""Research topic: {topic}

Raw search results:
{state['search_results']}

Select ONE most relevant URL and scrape it exactly once.
Return the raw scraped content and the source URL.
           {state['search_results']}
""",
            )
        ]
    })
    state["scraped_content"] = res["messages"][-1].content


def step_write(topic, state):
    research = (
        f"Search Results:\n{state['search_results']}\n\n"
        f"Detailed Scraped Content:\n{state['scraped_content']}"
    )
    state["report"] = writer_chain.invoke({"topic": topic, "research": research})


def step_critique(topic, state):
    state["feedback"] = critic_chain.invoke({"report": state["report"]})


# (name, emoji, colour, function)
STAGES = [
    ("Search", "🔎", "#06B6D4", step_search),
    ("Read", "📖", VIOLET, step_read),
    ("Write", "✍️", PINK, step_write),
    ("Review", "🧐", ORANGE, step_critique),
]


def steps_html(states, times):
    out = []
    for (name, emoji, color, _), s, t in zip(STAGES, states, times):
        meta = {"pending": "Waiting", "running": "Working…", "done": f"Done · {t:.0f}s", "error": "Failed"}[s]
        out.append(
            f'<div class="step {s}" style="--c:{color}"><span class="ico">{emoji}</span>'
            f'<span class="lbl">{name}</span><span class="meta">{meta}</span></div>'
        )
    return '<div class="steps">' + "".join(out) + "</div>"


def run(topic: str, slot):
    state = {}
    states = ["pending"] * len(STAGES)
    times = [0.0] * len(STAGES)
    start = time.perf_counter()
    for i, (*_, fn) in enumerate(STAGES):
        states[i] = "running"
        slot.markdown(steps_html(states, times), unsafe_allow_html=True)
        t = time.perf_counter()
        try:
            fn(topic, state)
        except Exception as e:  # show the real error, keep the tiles visible
            states[i] = "error"
            slot.markdown(steps_html(states, times), unsafe_allow_html=True)
            st.error(f"{type(e).__name__}: {e}")
            return None
        times[i] = time.perf_counter() - t
        states[i] = "done"
    slot.empty()  # render() redraws the finished tiles from result["times"]
    return {"topic": topic, "state": state, "times": times, "total": time.perf_counter() - start}


# ----------------------------------------------------------------- render ---
def score_html(score: float) -> str:
    color, verdict = ("#16A34A", "Strong report") if score >= 8 else (
        ("#F59E0B", "Solid, with gaps") if score >= 6 else ("#EF4444", "Needs more work")
    )
    shown = int(score) if score == int(score) else score
    return (
        f'<div class="score-row"><div class="ring" style="--p:{score * 10};--c:{color}">'
        f"<div><b>{shown}</b><span>out of 10</span></div></div>"
        f'<div class="verdict" style="color:{color}">{verdict}</div></div>'
    )


def section_title(kind: str, emoji: str, label: str) -> str:
    return f'<div class="sec {kind}"><span>{emoji}</span><span class="txt">{label}</span></div>'


def render(result: dict):
    state = result["state"]
    report = as_text(state.get("report", ""))
    feedback = as_text(state.get("feedback", ""))

    # finished step tiles stay on screen with their timings
    st.markdown(steps_html(["done"] * len(STAGES), result["times"]), unsafe_allow_html=True)

    st.markdown(
        f'<div class="meta-line">🎯 <b>{html.escape(result["topic"])}</b> · ⏱ {result["total"]:.0f}s total</div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        head, dl = st.columns([5, 2], vertical_alignment="center")
        head.markdown(section_title("report", "📄", "Report"), unsafe_allow_html=True)
        if result.get("pdf"):
            dl.download_button(
                "⬇ Download PDF",
                data=result["pdf"],
                file_name=f"{slug(result['topic'])}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        else:  # reportlab missing or PDF build failed
            dl.download_button(
                "⬇ Download .md",
                data=report,
                file_name=f"{slug(result['topic'])}.md",
                mime="text/markdown",
                use_container_width=True,
            )
        st.markdown('<div class="rule report"></div>', unsafe_allow_html=True)
        st.markdown(report)

    st.markdown('<div class="sep"><span>✦</span></div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(section_title("review", "🧐", "Review"), unsafe_allow_html=True)
        st.markdown('<div class="rule review"></div>', unsafe_allow_html=True)
        score = find_score(feedback)
        if score is not None:
            st.markdown(score_html(score), unsafe_allow_html=True)
        st.markdown(feedback)

    st.write("")
    with st.expander("🔎 Search results"):
        st.markdown(as_text(state.get("search_results", "")))
    with st.expander("📖 Source page"):
        st.markdown(as_text(state.get("scraped_content", "")))


# ------------------------------------------------------------------- page ---
SUGGESTIONS = [
    "India - China relations 2026",
    "Breakthrough in AI in 2026",
]


def pick(text: str):
    st.session_state.topic_input = text


st.session_state.setdefault("result", None)

st.markdown('<div class="hero">Research <span>desk</span></div>', unsafe_allow_html=True)
st.markdown(
    '<p class="tagline">Drop in a topic. Four agents search the web, read the best source, '
    "write the report and tear it apart.</p>",
    unsafe_allow_html=True,
)

with st.form("run_form", border=False):
    topic = st.text_input(
        "Topic",
        key="topic_input",
        placeholder="What do you want to dig into?",
        label_visibility="collapsed",
    )
    submitted = st.form_submit_button("Run research  →", type="primary")

cols = st.columns(len(SUGGESTIONS))
for i, (col, text) in enumerate(zip(cols, SUGGESTIONS)):
    col.button(text, key=f"chip_{i}", on_click=pick, args=(text,), use_container_width=True)

steps_slot = st.empty()

if submitted:
    if not topic.strip():
        st.warning("Enter a topic to start.")
    else:
        st.session_state.result = None
        result = run(topic.strip(), steps_slot)
        if result:
            result["pdf"] = make_pdf(result["topic"], as_text(result["state"].get("report", "")))
            st.session_state.result = result
            st.toast("Report ready", icon="🎉")

if st.session_state.result:
    render(st.session_state.result)