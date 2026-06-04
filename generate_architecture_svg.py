"""
Generates ARCHITECTURE_DIAGRAM.svg — light theme.
Run: python generate_architecture_svg.py
"""
import os, html as _html

def xe(s): return _html.escape(str(s), quote=False)

OUT  = os.path.join(os.path.dirname(__file__), "ARCHITECTURE_DIAGRAM.svg")
W    = 1160

# ── Light-theme palette ───────────────────────────────────────────────────────
BG       = "#F8FAFC"
BORDER   = "#E2E8F0"
DARK     = "#0F172A"
MID      = "#334155"
FAINT    = "#94A3B8"
WHITE    = "#FFFFFF"

# Per-tier  (fill, border/accent, header-text, chip-fill, chip-text, sub-text)
FE  = dict(f="#EFF6FF", s="#2563EB", ht=WHITE, cf="#DBEAFE", ct="#1D4ED8", st="#1E40AF")
BE  = dict(f="#F0FDF4", s="#16A34A", ht=WHITE, cf="#DCFCE7", ct="#15803D", st="#14532D")
RAG = dict(f="#FFFBEB", s="#D97706", ht=WHITE, cf="#FEF3C7", ct="#92400E", st="#B45309")
LG  = dict(f="#F5F3FF", s="#7C3AED", ht=WHITE, cf="#EDE9FE", ct="#5B21B6", st="#6D28D9")
ST  = dict(f="#F1F5F9", s="#64748B", ht=WHITE, cf="#E2E8F0", ct="#334155", st="#475569")
OAI = dict(f="#EEF2FF", s="#4F46E5", ht=WHITE, cf="#E0E7FF", ct="#3730A3", st="#4338CA")
LS  = dict(f="#F0FDF4", s="#16A34A", ht=WHITE, cf="#DCFCE7", ct="#15803D", st="#14532D")
DE  = dict(f="#FEF2F2", s="#DC2626", ht=WHITE, cf="#FEE2E2", ct="#991B1B", st="#B91C1C")

FONT = "'Segoe UI', -apple-system, 'Inter', sans-serif"


# ── Primitives ────────────────────────────────────────────────────────────────
def rect(x, y, w, h, fill, stroke, rx=10, sw=1.5, filt=""):
    f = f' filter="{filt}"' if filt else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{f}/>')

def txt(x, y, content, size=11, fill=DARK, weight="normal",
        anchor="middle", family=FONT):
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" '
            f'dominant-baseline="central">{xe(content)}</text>')

def line(x1, y1, x2, y2, stroke=FAINT, sw=1.8, dash="", marker="url(#arr)"):
    d = f'stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" '
            f'stroke-width="{sw}" {d} marker-end="{marker}" stroke-linecap="round"/>')

def path(d, stroke=FAINT, sw=1.8, dash="", fill="none", marker="url(#arr)"):
    da = f'stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" '
            f'{da} marker-end="{marker}" stroke-linecap="round" stroke-linejoin="round"/>')

def arrow_lbl(x, y, label, color=MID, size=8.5):
    pad = len(label) * 3.3 + 6
    return (f'<rect x="{x-pad}" y="{y-9}" width="{pad*2}" height="17" '
            f'rx="4" fill="{WHITE}" stroke="{BORDER}" stroke-width="1"/>'
            f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="middle" dominant-baseline="central"'
            f' font-weight="500">{xe(label)}</text>')

def chip(x, y, label, t, size=8.5, w=None):
    cw = w or (len(label)*5.8 + 14)
    return (f'<rect x="{x}" y="{y-9}" width="{cw}" height="18" rx="9" '
            f'fill="{t["cf"]}" stroke="{t["s"]}" stroke-width="1"/>'
            f'<text x="{x+cw/2}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'fill="{t["ct"]}" font-weight="600" text-anchor="middle" '
            f'dominant-baseline="central">{xe(label)}</text>')

def chip_row(sx, y, labels, t, gap=5, size=8.5):
    out, cx = "", sx
    for l in labels:
        cw = len(l)*5.8 + 14
        out += chip(cx, y, l, t, size=size, w=cw)
        cx += cw + gap
    return out

def section_badge(x, y, num, t):
    """Numbered circle badge top-left of each section."""
    return (f'<circle cx="{x}" cy="{y}" r="13" fill="{t["s"]}"/>'
            f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="11" '
            f'font-weight="bold" fill="{WHITE}" text-anchor="middle" '
            f'dominant-baseline="central">{xe(num)}</text>')

def tier_header(x, y, w, num, label, t):
    """Coloured header stripe with section number badge."""
    s  = rect(x, y, w, 36, t["s"], t["s"], rx=10, sw=0)
    s += rect(x, y+24, w, 12, t["s"], t["s"], rx=0, sw=0)
    s += txt(x + w//2 + 10, y+18, label,
             size=11, fill=WHITE, weight="bold")
    s += section_badge(x+18, y+18, num, t)
    return s

def comp_row(x, y, w, icon, name, desc, t):
    """Single component row inside a tier box."""
    s  = rect(x, y-13, w, 27, t["cf"], t["s"], rx=7, sw=1)
    s += txt(x+14, y, icon, size=13, fill=t["ct"], anchor="start")
    s += txt(x+36, y-5, name, size=9, fill=t["ct"],
             weight="bold", anchor="start")
    s += txt(x+36, y+7, desc, size=7.5, fill=t["st"], anchor="start")
    return s


# ── Layout constants ──────────────────────────────────────────────────────────
MX, MW = 55, 790     # main column  x, width
RX, RW = 875, 245    # right column x, width
MC     = MX + MW//2  # main column centre x

parts = []

# ── Defs: arrow marker + drop shadow ─────────────────────────────────────────
parts.append("""<defs>
  <marker id="arr" viewBox="0 0 10 10" refX="9" refY="5"
          markerWidth="6" markerHeight="6" orient="auto-start-reverse">
    <path d="M1 2 L8 5 L1 8" fill="none" stroke="context-stroke"
          stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
  </marker>
  <filter id="sh" x="-4%" y="-4%" width="108%" height="112%">
    <feDropShadow dx="0" dy="2" stdDeviation="4"
                  flood-color="#0F172A" flood-opacity="0.08"/>
  </filter>
  <filter id="shSm" x="-4%" y="-4%" width="108%" height="115%">
    <feDropShadow dx="0" dy="1" stdDeviation="2"
                  flood-color="#0F172A" flood-opacity="0.07"/>
  </filter>
</defs>""")

# ── Background ────────────────────────────────────────────────────────────────
parts.append(f'<rect width="{W}" height="2000" fill="{BG}"/>')

# ── Title — centred on the full canvas width (W//2), not just the main column ──
TT_Y  = 28
TC    = W // 2   # true canvas centre
parts.append(txt(TC, TT_Y,
                 "FaultSense AI — Telecom Network Fault Intelligence",
                 size=20, fill=DARK, weight="bold"))
parts.append(txt(TC, TT_Y+26,
                 "System Architecture  ·  RAG + LangGraph Multi-Agent Pipeline  ·  "
                 "Python / FastAPI / React / ChromaDB / OpenAI",
                 size=10, fill=FAINT))
parts.append(f'<line x1="{MX}" y1="{TT_Y+42}" x2="{RX+RW}" y2="{TT_Y+42}" '
             f'stroke="{BORDER}" stroke-width="1.5"/>')

# ── User bubble ───────────────────────────────────────────────────────────────
UY = TT_Y + 74
parts.append(f'<ellipse cx="{MC}" cy="{UY}" rx="118" ry="28" '
             f'fill="{WHITE}" stroke="{BORDER}" stroke-width="1.5" filter="url(#shSm)"/>')
# user icon (simple SVG person)
ux = MC - 82
parts.append(f'<circle cx="{ux}" cy="{UY-6}" r="8" fill="{FE["s"]}" opacity="0.18"/>')
parts.append(f'<circle cx="{ux}" cy="{UY-8}" r="5" fill="{FE["s"]}"/>')
parts.append(f'<path d="M {ux-8} {UY+4} Q {ux} {UY-2} {ux+8} {UY+4}" '
             f'fill="none" stroke="{FE["s"]}" stroke-width="2" stroke-linecap="round"/>')
parts.append(txt(MC+6, UY-6, "User / NOC Engineer",
                 size=12, fill=DARK, weight="600"))
parts.append(txt(MC+6, UY+8, "Natural language fault query",
                 size=9, fill=FAINT))

# arrow down
parts.append(line(MC, UY+28, MC, UY+52, stroke=FE["s"], sw=2))

# ═════════════════════════════════════════════════════════════════════════════
# 1.  REACT FRONTEND
# ═════════════════════════════════════════════════════════════════════════════
FY, FH = UY+54, 142
parts.append(rect(MX, FY, MW, FH, FE["f"], FE["s"], rx=10, filt="url(#sh)"))
parts.append(tier_header(MX, FY, MW, "1",
    "React Frontend   ·   Vite + TypeScript + TailwindCSS   ·   Port 5173", FE))

chips_r1 = ["🏠 App.tsx", "🔎 QueryInput", "📋 IncidentCard",
            "🔬 AgentTrace", "🎯 RootCausePanel"]
chips_r2 = ["✅ Recommendations", "📊 AnalyticsDashboard",
            "📋 EvaluationPanel", "🛡 GuardrailPanel", "🚨 ErrorBoundary"]
parts.append(chip_row(MX+12, FY+62, chips_r1, FE))
parts.append(chip_row(MX+12, FY+92, chips_r2, FE))
parts.append(txt(MX+8, FY+121, "axios  ·  TailwindCSS v3  ·  Lucide React Icons  ·  React 18  ·  TypeScript",
                 size=8, fill=FE["st"], anchor="start"))

# arrow Frontend → Backend
A1Y = FY + FH
parts.append(line(MC, A1Y, MC, A1Y+30, stroke=FE["s"], sw=2.5))
parts.append(arrow_lbl(MC, A1Y+15, "HTTP POST  ·  axios  ·  JSON", FE["s"]))

# ═════════════════════════════════════════════════════════════════════════════
# 2.  FASTAPI BACKEND
# ═════════════════════════════════════════════════════════════════════════════
BY, BH = A1Y+32, 140
parts.append(rect(MX, BY, MW, BH, BE["f"], BE["s"], rx=10, filt="url(#sh)"))
parts.append(tier_header(MX, BY, MW, "2",
    "FastAPI Backend   ·   Uvicorn   ·   Port 8000", BE))

ep1 = ["🔎 POST /query", "🧠 POST /analyze",
       "📥 POST/GET /ingest", "💚 GET /health"]
ep2 = ["📈 GET/POST /analytics/*", "📝 POST /summarize",
       "🧪 POST /evaluate", "📡 GET /ingest/status"]
parts.append(chip_row(MX+12, BY+60, ep1, BE))
parts.append(chip_row(MX+12, BY+90, ep2, BE))
parts.append(txt(MX+8, BY+119,
                 "pydantic-settings  ·  loguru  ·  LangSmith tracing  ·  Python 3.11+",
                 size=8, fill=BE["st"], anchor="start"))

# ── fork: Backend → RAG  and  Backend → LangGraph ────────────────────────────
TY = BY + BH + 40
RAG_X, RAG_W = MX, 375
LG_X,  LG_W  = MX+395, 395
TH = 205

fork_y = BY + BH + 18
parts.append(path(f"M {MC} {BY+BH} L {MC} {fork_y} "
                  f"L {RAG_X+RAG_W//2} {fork_y} L {RAG_X+RAG_W//2} {TY}",
                  stroke=RAG["s"], sw=2))
parts.append(path(f"M {MC} {BY+BH} L {MC} {fork_y} "
                  f"L {LG_X+LG_W//2} {fork_y} L {LG_X+LG_W//2} {TY}",
                  stroke=LG["s"], sw=2))
parts.append(arrow_lbl(RAG_X+RAG_W//2 - 68, fork_y, "Quick RAG", RAG["s"]))
parts.append(arrow_lbl(LG_X+LG_W//2  + 72, fork_y, "LangGraph invoke", LG["s"]))

# ═════════════════════════════════════════════════════════════════════════════
# 3.  RAG PIPELINE
# ═════════════════════════════════════════════════════════════════════════════
parts.append(rect(RAG_X, TY, RAG_W, TH, RAG["f"], RAG["s"], rx=10, filt="url(#sh)"))
parts.append(tier_header(RAG_X, TY, RAG_W, "3", "RAG Pipeline", RAG))

rag_items = [
    ("🧮", "EmbeddingManager",
     "text-embedding-3-small  ·  3 workers  ·  batch 512"),
    ("💾", "ChromaDBStore",
     "Semantic vector search  ·  metadata filters"),
    ("📑", "BM25Index",
     "Keyword search  ·  rank_bm25"),
    ("🔀", "HybridRetriever",
     "RRF fusion  ·  score = 1/(rank + 60)"),
]
for i, (icon, name, desc) in enumerate(rag_items):
    parts.append(comp_row(RAG_X+10, TY+57+i*38, RAG_W-20,
                          icon, name, desc, RAG))

# ═════════════════════════════════════════════════════════════════════════════
# 4.  LANGGRAPH AGENT PIPELINE
# ═════════════════════════════════════════════════════════════════════════════
parts.append(rect(LG_X, TY, LG_W, TH, LG["f"], LG["s"], rx=10, filt="url(#sh)"))
parts.append(tier_header(LG_X, TY, LG_W, "4", "LangGraph Agent Pipeline", LG))

lg_items = [
    ("🛡",  "Guardrail",
     "Keyword check  ·  LLM injection detection"),
    ("🔍",  "Agent 1 — Retrieval",
     "HybridRetriever.search()  ·  RRF fusion"),
    ("🔗",  "Agent 2 — Correlation",
     "Cluster by region + technology + time window"),
    ("🎯",  "Agent 3 — Root Cause",
     "GPT-4o-mini chain-of-thought reasoning"),
    ("💡",  "Agent 4 — Recommendations",
     "Structured output  ·  categorised action steps"),
]
for i, (icon, name, desc) in enumerate(lg_items):
    parts.append(comp_row(LG_X+10, TY+52+i*30, LG_W-20,
                          icon, name, desc, LG))

# dashed cross-arrow RAG → LangGraph
MID_Y = TY + TH//2 + 10
parts.append(line(RAG_X+RAG_W, MID_Y, LG_X, MID_Y,
                  stroke=LG["s"], sw=1.5, dash="6 4"))
parts.append(arrow_lbl((RAG_X+RAG_W+LG_X)//2, MID_Y-14,
                        "HybridRetriever.search()", LG["s"]))

# ═════════════════════════════════════════════════════════════════════════════
# 5.  STORAGE LAYER
# ═════════════════════════════════════════════════════════════════════════════
SY = TY + TH + 32
SH = 90
parts.append(rect(MX, SY, MW, SH, ST["f"], ST["s"], rx=10, filt="url(#sh)"))
parts.append(tier_header(MX, SY, MW, "5", "Storage and Data Layer", ST))

# Storage items — evenly distributed: equal gap on left, between, and right.
# gap = (container_width − 3×item_width) / 4
ST_ITEM_W = 228
ST_GAP    = (MW - 3 * ST_ITEM_W) / 4   # ≈ 26.5 px  (float for precision)

store_meta = [
    ("📄", "telecom_incidents.csv",        "9,827 rows  ·  10 fields per row",    BE),
    ("🗄", "ChromaDB",                     "Persistent local vector store",        OAI),
    ("📊", "BM25 Index",                   "In-memory  ·  rebuilt on each ingest", RAG),
]
for i, (icon, name, desc, t) in enumerate(store_meta):
    sx = MX + ST_GAP + i * (ST_ITEM_W + ST_GAP)
    # SY+42: 6 px gap below header (36 px) AND 6 px gap above container bottom
    # → perfectly vertically centred within the 54 px content area
    parts.append(rect(sx, SY+42, ST_ITEM_W, 42, t["cf"], t["s"], rx=7, sw=1))
    parts.append(txt(sx+14, SY+63, icon, size=15, fill=t["ct"], anchor="start"))
    parts.append(txt(sx+38, SY+56, name, size=9.5, fill=t["ct"],
                     weight="bold", anchor="start"))
    parts.append(txt(sx+38, SY+70, desc, size=7.5, fill=t["st"],
                     anchor="start"))

# arrow RAG → Storage (down)
RCX = RAG_X + RAG_W//2
parts.append(line(RCX, TY+TH, RCX, SY, stroke=RAG["s"], sw=1.8))
parts.append(arrow_lbl(RCX+46, TY+TH+16, "Query / Store", RAG["s"], size=8))

# ═════════════════════════════════════════════════════════════════════════════
# RIGHT COLUMN — External Services
# ═════════════════════════════════════════════════════════════════════════════
def ext_box(x, y, w, h, num, icon, title, bullets, t):
    s  = rect(x, y, w, h, t["f"], t["s"], rx=10, sw=1.5, filt="url(#shSm)")
    s += tier_header(x, y, w, num, f"{icon}  {title}", t)
    # Left padding 32 px for dot, 50 px for text — clear whitespace on the
    # left edge; remaining ~195 px on the right is ample for text.
    for j, b in enumerate(bullets):
        row_y = y + 54 + j * 20
        s += (f'<circle cx="{x+32}" cy="{row_y}" r="3" fill="{t["s"]}"/>')
        s += txt(x+46, row_y, b, size=8.5, fill=t["ct"], anchor="start")
    return s

# Box heights: header=36px, top-pad=18px, then rows at 20px each, bottom-pad=14px
# OAI: 5 bullets → 36 + 18 + 5×20 + 14 = 168
OAI_Y = BY
OAI_H = 168
parts.append(ext_box(RX, OAI_Y, RW, OAI_H, "6", "🤖", "OpenAI API",
    ["GPT-4o-mini / gpt-4o",
     "text-embedding-3-small",
     "Via corporate proxy",
     "SSL bypass (httpx)",
     "max_tokens = 500"], OAI))

# LS: 3 bullets → 36 + 18 + 3×20 + 14 = 128
LS_Y  = OAI_Y + OAI_H + 18
LS_H  = 128
parts.append(ext_box(RX, LS_Y, RW, LS_H, "7", "📊", "LangSmith",
    ["Tracing and observability",
     "Agent step timings",
     "LANGCHAIN_TRACING_V2=true"], LS))

# DE: 4 bullets → 36 + 18 + 4×20 + 14 = 148
DE_Y  = LS_Y + LS_H + 18
DE_H  = 148
parts.append(ext_box(RX, DE_Y, RW, DE_H, "8", "📋", "DeepEval",
    ["Faithfulness score",
     "Answer relevancy score",
     "Context precision score",
     "Direct LLM-as-judge calls"], DE))

# ── Arrows to right column ────────────────────────────────────────────────────
BE_RX = MX + MW
OAI_LX = RX

# Backend → OpenAI
BY_C = BY + BH//2
OAI_C = OAI_Y + OAI_H//2
parts.append(line(BE_RX, BY_C, OAI_LX, OAI_C, stroke=OAI["s"], sw=1.8))
parts.append(arrow_lbl((BE_RX+OAI_LX)//2, BY_C-12, "LLM calls", OAI["s"]))

# RAG → OpenAI (dashed, embed)
R_RX  = RAG_X + RAG_W
R_MY  = TY + TH//2 - 20
parts.append(path(f"M {R_RX} {R_MY} L {BE_RX+22} {R_MY} "
                  f"L {BE_RX+22} {OAI_C+20} L {OAI_LX} {OAI_C+20}",
                  stroke=OAI["s"], sw=1.5, dash="5 4"))
parts.append(arrow_lbl(BE_RX+22, R_MY-12, "Embed API", OAI["s"]))

# LangGraph → OpenAI
L_RX  = LG_X + LG_W
L_MY  = TY + TH//2 + 20
parts.append(path(f"M {L_RX} {L_MY} L {OAI_LX} {L_MY} "
                  f"L {OAI_LX} {OAI_C-10}",
                  stroke=OAI["s"], sw=1.8))
parts.append(arrow_lbl((L_RX+OAI_LX)//2, L_MY-12, "GPT-4o", OAI["s"]))

# Backend → LangSmith (dashed)
LS_C  = LS_Y + LS_H//2
parts.append(path(f"M {BE_RX} {BY+BH*0.68} L {OAI_LX-12} {BY+BH*0.68} "
                  f"L {OAI_LX-12} {LS_C} L {OAI_LX} {LS_C}",
                  stroke=LS["s"], sw=1.5, dash="5 4"))
parts.append(arrow_lbl(BE_RX+20, BY+BH*0.68-12, "Tracing", LS["s"]))

# Backend → DeepEval
DE_C  = DE_Y + DE_H//2
parts.append(path(f"M {BE_RX} {BY+BH*0.92} L {OAI_LX-24} {BY+BH*0.92} "
                  f"L {OAI_LX-24} {DE_C} L {OAI_LX} {DE_C}",
                  stroke=DE["s"], sw=1.8))
parts.append(arrow_lbl(BE_RX+20, BY+BH*0.92-12, "Evaluate", DE["s"]))

# ═════════════════════════════════════════════════════════════════════════════
# LEGEND
# ═════════════════════════════════════════════════════════════════════════════
LEG_Y = SY + SH + 26
LEG_H = 52
LTOT  = RX + RW - MX
parts.append(rect(MX, LEG_Y, LTOT, LEG_H, WHITE, BORDER, rx=8, sw=1))
parts.append(txt(MX+14, LEG_Y+15, "Legend:", size=9,
                 fill=MID, weight="bold", anchor="start"))

# Legend chips — auto-spaced so gaps between all chips are exactly equal.
# LTOT is the total legend bar width; 72 px reserved on the left for "Legend:".
LEGEND_LABEL_W = 72
leg_data = [
    ("⚛", "React Frontend",  FE),
    ("⚡", "FastAPI Backend", BE),
    ("🔍", "RAG Pipeline",   RAG),
    ("🤖", "LangGraph",      LG),
    ("🗂",  "Storage",        ST),
    ("🌐", "External APIs",  OAI),
    ("📊", "LangSmith",      LS),
    ("📋", "DeepEval",       DE),
]
chip_widths  = [len(label) * 6.8 + 30 for _, label, _ in leg_data]
total_cw     = sum(chip_widths)
avail_w      = LTOT - LEGEND_LABEL_W
# Equal gap before first chip, between every chip, and after the last chip
gap          = (avail_w - total_cw) / (len(leg_data) + 1)
lx           = MX + LEGEND_LABEL_W + gap
for (icon, label, t), cw in zip(leg_data, chip_widths):
    parts.append(rect(lx, LEG_Y+24, cw, 20, t["cf"], t["s"], rx=5, sw=1))
    parts.append(txt(lx+8,  LEG_Y+34, icon,  size=10, fill=t["ct"], anchor="start"))
    parts.append(txt(lx+24, LEG_Y+34, label, size=8,  fill=t["ct"],
                     weight="600", anchor="start"))
    lx += cw + gap

# ═════════════════════════════════════════════════════════════════════════════
# FOOTER
# ═════════════════════════════════════════════════════════════════════════════
FT_Y = LEG_Y + LEG_H + 12
parts.append(f'<line x1="{MX}" y1="{FT_Y}" x2="{RX+RW}" y2="{FT_Y}" '
             f'stroke="{BORDER}" stroke-width="1"/>')
parts.append(txt(MC, FT_Y+14,
    "FaultSense AI  ·  TelecomNetworkFaultIntel  ·  "
    "RAG + LangGraph + DeepEval + LangSmith  ·  2026",
    size=8.5, fill=FAINT))

# ── Assemble SVG ──────────────────────────────────────────────────────────────
TOTAL_H = FT_Y + 30
svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="{W}" height="{TOTAL_H}" viewBox="0 0 {W} {TOTAL_H}"
     xmlns="http://www.w3.org/2000/svg" role="img"
     style="font-family:{FONT}; background:{BG}">
<title>FaultSense AI — Telecom Network Fault Intelligence Architecture</title>
<desc>Light-theme system architecture: React Frontend, FastAPI Backend,
RAG Pipeline, LangGraph Agents, Storage, OpenAI, LangSmith, DeepEval.</desc>
{''.join(parts)}
</svg>"""

with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"SVG created: {OUT}  ({TOTAL_H}px tall)")
