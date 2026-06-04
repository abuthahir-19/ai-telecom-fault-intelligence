"""
Generates DAILY_CHANGES_SUMMARY.pdf in the project root.
Run: python generate_summary_pdf.py
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, ListFlowable, ListItem,
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import os

W, H = A4
PDF_PATH = os.path.join(os.path.dirname(__file__), "DAILY_CHANGES_SUMMARY.pdf")

doc = SimpleDocTemplate(
    PDF_PATH, pagesize=A4,
    rightMargin=2*cm, leftMargin=2*cm,
    topMargin=2*cm,   bottomMargin=2*cm,
)

# ── Colours ────────────────────────────────────────────────────────────────
DARK_BG  = colors.HexColor('#0d1117')
BLUE     = colors.HexColor('#1f6feb')
BLUE_LT  = colors.HexColor('#4A9EFF')
GREEN    = colors.HexColor('#166534')
GREEN_LT = colors.HexColor('#16a34a')
VIOLET   = colors.HexColor('#6e40c9')
ORANGE   = colors.HexColor('#b45309')
RED      = colors.HexColor('#b91c1c')
TEAL     = colors.HexColor('#0f766e')
SLATE    = colors.HexColor('#334155')
SLATE_LT = colors.HexColor('#94a3b8')
WHITE    = colors.white
CARD_BG  = colors.HexColor('#f8fafc')

def sty(name, **kw):
    return ParagraphStyle(name, **kw)

def b(t):     return f"<b>{t}</b>"
def hl(t, c='#1f6feb'): return f'<font color="{c}">{t}</font>'

TODAY = "03 June 2026"

# ── Shared paragraph styles ────────────────────────────────────────────────
title_s  = sty("T",  fontName="Helvetica-Bold",  fontSize=22, textColor=DARK_BG, alignment=TA_CENTER, spaceAfter=4)
sub_s    = sty("S",  fontName="Helvetica",        fontSize=11, textColor=SLATE,   alignment=TA_CENTER, spaceAfter=2)
body_s   = sty("B",  fontName="Helvetica",        fontSize=9,  textColor=SLATE,   spaceAfter=3, leading=13)
bullet_s = sty("BL", fontName="Helvetica",        fontSize=9,  textColor=SLATE,   spaceAfter=2, leading=13, leftIndent=12)
code_s   = sty("C",  fontName="Courier",          fontSize=8,  textColor=colors.HexColor("#1e40af"), spaceAfter=2, leading=11)

# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════
def section_header(text, bg=BLUE):
    t = Table(
        [[Paragraph(f'<font color="white"><b>{text}</b></font>',
                    sty("sh", fontName="Helvetica-Bold", fontSize=11, alignment=TA_LEFT))]],
        colWidths=[doc.width],
    )
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), bg),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("ROUNDEDCORNERS",[5]),
    ]))
    return [t, Spacer(1, 0.15*cm)]


def change_card(number, title, cat_color, cat_label, files, bullets, impact):
    inner = Table([
        [Paragraph(b(title),
                   sty("ct", fontName="Helvetica-Bold", fontSize=11, textColor=DARK_BG)),
         Paragraph(f" {cat_label} ",
                   sty("cl", fontName="Helvetica-Bold", fontSize=8,
                       textColor=WHITE, backColor=cat_color, alignment=TA_RIGHT))],
        [Paragraph(hl("Files: ", "#64748b") + hl(", ".join(files), "#1e40af"),
                   sty("cf", fontName="Courier", fontSize=7.5, textColor=SLATE)), ""],
    ], colWidths=[doc.width - 3.2*cm - 0.4*cm, 2.8*cm])

    header_row = Table(
        [[Paragraph(f'<font color="white"><b>{number}</b></font>',
                    sty("cn", fontName="Helvetica-Bold", fontSize=14, alignment=TA_CENTER)),
          inner]],
        colWidths=[1*cm, doc.width - 1*cm],
    )
    header_row.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (0,-1), cat_color),
        ("BACKGROUND",    (1,0), (1,-1), CARD_BG),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("BOX",           (0,0), (-1,-1), 1, colors.HexColor("#e2e8f0")),
        ("TOPPADDING",    (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ("RIGHTPADDING",  (0,0), (-1,-1), 6),
    ]))

    items = [ListItem(Paragraph(b_item, bullet_s), leftIndent=8, bulletColor=cat_color)
             for b_item in bullets]
    return [
        header_row,
        Spacer(1, 0.1*cm),
        ListFlowable(items, bulletType="bullet", start="•", leftIndent=10,
                     spaceBefore=0, spaceAfter=0),
        Paragraph(hl("Impact: ", "#64748b") + impact, body_s),
        Spacer(1, 0.3*cm),
    ]


# ═══════════════════════════════════════════════════════════════════════════
# BUILD STORY
# ═══════════════════════════════════════════════════════════════════════════
story = []
story.append(Spacer(1, 0.8*cm))

# ── Cover banner ────────────────────────────────────────────────────────────
banner = Table(
    [[Paragraph('<font color="white"><b>FaultSense AI — TelecomNetworkFaultIntel</b></font>',
                sty("bh", fontName="Helvetica-Bold", fontSize=16, alignment=TA_CENTER))]],
    colWidths=[doc.width],
)
banner.setStyle(TableStyle([
    ("BACKGROUND",    (0,0), (-1,-1), DARK_BG),
    ("TOPPADDING",    (0,0), (-1,-1), 14),
    ("BOTTOMPADDING", (0,0), (-1,-1), 14),
    ("ROUNDEDCORNERS",[8]),
]))
story.append(banner)
story.append(Spacer(1, 0.4*cm))
story.append(Paragraph("Daily Development Changes Summary", title_s))
story.append(Paragraph(f"Date: {TODAY}  |  Session: Full-Day Sprint", sub_s))
story.append(HRFlowable(width="100%", thickness=2, color=BLUE_LT, spaceAfter=10))

# ── Stats row ───────────────────────────────────────────────────────────────
stats = [("13", "Change Groups"), ("21", "Files Modified"), ("3", "New Components"), ("4", "Bug Fixes")]
stat_cells = []
for num, label in stats:
    cell = Table(
        [[Paragraph(f'<font color="#1f6feb"><b>{num}</b></font>',
                    sty("sn", fontName="Helvetica-Bold", fontSize=22, alignment=TA_CENTER))],
         [Paragraph(label, sty("sl", fontName="Helvetica", fontSize=8,
                               textColor=SLATE_LT, alignment=TA_CENTER))]],
        colWidths=[3.5*cm],
    )
    stat_cells.append(cell)
stat_tbl = Table([stat_cells], colWidths=[doc.width/4]*4)
stat_tbl.setStyle(TableStyle([
    ("BACKGROUND",    (0,0), (-1,-1), CARD_BG),
    ("BOX",           (0,0), (-1,-1), 1, colors.HexColor("#e2e8f0")),
    ("TOPPADDING",    (0,0), (-1,-1), 10),
    ("BOTTOMPADDING", (0,0), (-1,-1), 10),
    ("ROUNDEDCORNERS",[6]),
]))
story.append(stat_tbl)
story.append(Spacer(1, 0.6*cm))

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1 — Architecture & Documentation
# ═══════════════════════════════════════════════════════════════════════════
story += section_header("SECTION 1 — Architecture & Documentation", DARK_BG)
story += change_card(
    "01", "System Architecture Diagram (draw.io)", BLUE, "NEW FILE",
    ["ARCHITECTURE.drawio"],
    [
        "Created complete draw.io XML diagram with 5 tiers: React Frontend, FastAPI Backend, RAG Pipeline, LangGraph Agent Pipeline, and Storage + External",
        "Dark GitHub theme (#0d1117) with colour-coded swimlane containers per tier (blue / teal / amber / purple)",
        "Emoji icons on every component box (⚛ ⚡ 🔍 🤖 💾 📊 🛡 🎯 etc.)",
        "Explicit edge waypoints through clean corridors (y=460, y=718, x=590, x=1155) so no line passes through any box",
        "OpenAI cloud shape positioned right of LangGraph for short direct arrows from Agent 3 and Agent 4",
        "Legend, Vite Proxy annotation, and storage layer labels included",
    ],
    "Openable in draw.io desktop or VS Code Draw.io Integration extension. All 13 connections route cleanly.",
)

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2 — Bug Fixes
# ═══════════════════════════════════════════════════════════════════════════
story += section_header("SECTION 2 — Bug Fixes", RED)

story += change_card(
    "02", "Proxy max_tokens & response_format Fixes", RED, "BUG FIX",
    ["agents/resolution_agent.py", "evaluation/evaluator.py",
     "prediction/predictor.py", "routers/analytics.py"],
    [
        "Removed response_format={'type':'json_object'} from all LLM calls — the corporate proxy rejects dict-type response_format",
        "Capped max_tokens to 500 in resolution_agent (was 800), evaluator (was 512), predictor (was 700), analytics (was 800)",
        "Trimmed resolution agent system prompt from 5-8 steps/section to 2-3 steps to fit within the 500-token budget",
    ],
    "Eliminated HTTP 422 errors from the proxy on every deep analysis and analytics request.",
)
story += change_card(
    "03", "Guardrail 422 → Structured 200 Response", RED, "BUG FIX",
    ["routers/query.py", "routers/analyze.py", "models/query.py"],
    [
        "Both routers raised HTTPException(422) when a query was blocked — Axios threw and the frontend showed a raw error string",
        "Changed to return HTTP 200 with guardrail_result.valid=false so the GuardrailPanel renders the block reason",
        "Removed Pydantic min_length=10 from request models — the custom guardrail now owns length validation with helpful messages",
        "Added guardrail_result field to both QueryResponse Pydantic model and TypeScript interface",
    ],
    "Blocked queries now display the GuardrailPanel with all 3 check statuses instead of a generic error.",
)
story += change_card(
    "04", "Guardrail Keyword Word-Boundary Fix", RED, "BUG FIX",
    ["utils/guardrails.py"],
    [
        "Keyword check used kw in query_lower (raw substring): 'port' matched 'report' and 'crash' matched 'crashing'",
        "Replaced with re.search(r'\\b' + kw + r'\\b') for single-word keywords; multi-word keywords like 'call drop' still use substring",
        "Test case 2 (users report poor internet…) now correctly warns about no telecom keywords",
        "Test case 5 (server is crashing…resetting) now correctly warns about no telecom keywords",
    ],
    "All 5 guardrail test cases produce exactly the expected outcomes (PASSED / WARNED / BLOCKED).",
)
story += change_card(
    "05", "DeepEval Evaluation JSON Parsing Fix", RED, "BUG FIX",
    ["evaluation/evaluator.py"],
    [
        "DeepEval's metric objects make 2-3 sequential LLM calls whose combined JSON exceeded the 500-token proxy cap causing truncation",
        "Replaced FaithfulnessMetric / AnswerRelevancyMetric / ContextualRelevancyMetric with 3 direct focused LLM calls",
        "Each prompt produces a JSON response under 300 tokens — safely within the proxy limit",
        "Added _extract_json() to strip markdown fences and preamble text; added _safe_float() to clamp scores to [0,1]",
        "Added JSON-only system message on all schema calls to prevent the LLM from wrapping output in markdown",
    ],
    "Eliminated 'Evaluation LLM outputted an invalid JSON' warnings. All 3 metrics now score reliably.",
)
story += change_card(
    "06", "Independent Button Loading Spinners", RED, "BUG FIX",
    ["frontend/src/components/QueryInput.tsx"],
    [
        "Both Quick Search and Deep Analysis buttons shared the parent isLoading prop — clicking either caused BOTH to show spinners",
        "Added internal loadingAction: 'query' | 'analyze' | null state inside QueryInput",
        "Each button shows its spinner only when it triggered the current load; the other button stays visually idle",
        "Button label also updates: 'Searching…' and 'Analysing…' while active",
        "Both buttons stay disabled while either action is in flight to prevent double-submit",
    ],
    "Clicking Quick Search shows spinner only on Quick Search. Deep Analysis button stays idle (and vice versa).",
)

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3 — New Features
# ═══════════════════════════════════════════════════════════════════════════
story += section_header("SECTION 3 — New Features & Components", GREEN_LT)

story += change_card(
    "07", "Duration Formatting in Incident Cards", GREEN_LT, "FEATURE",
    ["frontend/src/components/IncidentCard.tsx"],
    [
        "outage_duration was displayed as a raw integer with no unit ('120' instead of '2h 0m')",
        "Added formatDuration(raw) helper: parses numeric minutes and outputs '< 1 min', '45 min', '2h 15m'",
        "Handles both string and number input types for robustness",
    ],
    "Incident cards in Deep Analysis now show human-readable duration labels.",
)
story += change_card(
    "08", "EvaluationPanel Component & Separate Evaluation Tab", GREEN_LT, "FEATURE",
    ["components/EvaluationPanel.tsx", "App.tsx", "api/client.ts", "types/index.ts"],
    [
        "Created EvaluationPanel.tsx with 3 colour-coded progress bars (green >=70%, yellow >=40%, red <40%)",
        "Added dedicated Evaluation tab to the navbar with a live indicator dot (yellow pulsing = running, violet = ready)",
        "After every Deep Analysis, evaluateAnalysis() is called automatically in the background",
        "EvaluationPanel moved to its own Evaluation tab (no longer at the bottom of analysis results)",
        "Tab shows placeholder 'Run a Deep Analysis first' message when no results are available yet",
        "Issues and missing aspects are listed below the bars; overall score badge shown in header",
    ],
    "Faithfulness, Answer Relevancy, and Context Precision scores are accessible in a dedicated Evaluation tab.",
)
story += change_card(
    "09", "GuardrailPanel Component", GREEN_LT, "FEATURE",
    ["components/GuardrailPanel.tsx", "frontend/src/types/index.ts"],
    [
        "Created GuardrailPanel.tsx showing 3 named checks: Input Validation, Injection Detection, Telecom Relevance",
        "Each check shows a pass / warn / fail / skip icon with label and description",
        "Status banner: 'All guardrail checks passed' / 'Passed with warnings' / 'Query blocked by guardrail'",
        "Added GuardrailResult TypeScript interface; shown in both Deep Analysis and Query Mode",
        "Results section hidden when guardrail_result.valid=false — only the panel is displayed for blocked queries",
    ],
    "Every query run shows all 3 guardrail check statuses with clear pass/warn/block visual indicators.",
)
story += change_card(
    "10", "LangSmith Tracing Integration", GREEN_LT, "FEATURE",
    ["backend/app/main.py", "backend/app/config.py", ".env.example", ".env"],
    [
        "Added 4 LangSmith env vars to config.py Settings class and .env.example template",
        "In main.py, env vars are set in os.environ BEFORE any LangChain/LangGraph module is imported (critical timing requirement)",
        "All LangGraph agent pipeline runs in /api/analyze now appear in the LangSmith dashboard",
        "Project: multi-agent-trip-planner on smith.langchain.com with full agent tracing",
    ],
    "Every Deep Analysis call is traced end-to-end in LangSmith with agent timings, inputs, and outputs.",
)

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4 — UI / UX
# ═══════════════════════════════════════════════════════════════════════════
story += section_header("SECTION 4 — UI / UX Improvements", VIOLET)

story += change_card(
    "11", "App Rebranding: FaultSense AI", VIOLET, "UI",
    ["frontend/src/App.tsx"],
    [
        "Changed app name from 'TelecomNetworkFaultIntel' to 'FaultSense AI'",
        "Two-tone wordmark: blue 'Fault' + white 'Sense' + slate 'AI' badge in the navbar",
        "Browser tab title updated via useEffect to 'FaultSense — Telecom Network Intelligence'",
        "Welcome heading and footer text updated to match the new branding",
    ],
    "Professional product-quality branding replacing the raw project code-name.",
)
story += change_card(
    "12", "Navigation Tabs Moved to Navbar and Centred", VIOLET, "UI",
    ["frontend/src/App.tsx"],
    [
        "Tabs (Query Mode / Deep Analysis / Analytics / Evaluation) moved from main content area to the sticky navbar header",
        "Three-column flex layout: flex-1 logo (left) | centred nav | flex-1 justify-end actions (right)",
        "Nav buttons have px-4 py-1.5 padding and gap-1 spacing for clear visual separation with shadow on active tab",
        "Mobile fallback: compact tab strip shown in main content on screens smaller than md breakpoint",
    ],
    "Navigation always visible regardless of scroll; centred relative to the full viewport width.",
)

story.append(PageBreak())

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 5 — Files Modified
# ═══════════════════════════════════════════════════════════════════════════
story += section_header("SECTION 5 — Complete Files Modified", TEAL)
story.append(Spacer(1, 0.2*cm))

hdr = sty("fh", fontName="Helvetica-Bold", fontSize=9, textColor=WHITE)
cell_s = sty("fc", fontName="Helvetica", fontSize=8, textColor=SLATE, leading=11)
mono_s = sty("fm", fontName="Courier",   fontSize=7.5, textColor=colors.HexColor("#1e40af"), leading=11)

files_data = [
    [Paragraph("<b>File Path</b>", hdr),
     Paragraph("<b>Change</b>",   hdr),
     Paragraph("<b>Summary</b>",  hdr)],
    ["backend/app/main.py",                     "Modified", "LangSmith env vars set before LangChain imports"],
    ["backend/app/config.py",                   "Modified", "LangSmith settings fields added"],
    ["backend/app/models/query.py",             "Modified", "guardrail_result added to QueryResponse; min_length removed"],
    ["backend/app/routers/query.py",            "Modified", "Return 200 + guardrail_result on block; removed HTTPException"],
    ["backend/app/routers/analyze.py",          "Modified", "Return 200 + guardrail_result on block; removed HTTPException"],
    ["backend/app/routers/analytics.py",        "Modified", "max_tokens capped at 500"],
    ["backend/app/agents/resolution_agent.py",  "Modified", "max_tokens 800→500; response_format removed; prompt trimmed"],
    ["backend/app/prediction/predictor.py",     "Modified", "max_tokens 700→500"],
    ["backend/app/evaluation/evaluator.py",     "Modified", "_extract_json + _safe_float helpers; 3 direct LLM eval calls"],
    ["backend/app/utils/guardrails.py",         "Modified", "Word-boundary regex for keyword matching via _kw_match helper"],
    ["frontend/src/App.tsx",                    "Modified", "FaultSense branding; centred navbar tabs; eval tab; GuardrailPanel"],
    ["frontend/src/types/index.ts",             "Modified", "GuardrailResult + AppMode 'evaluate' + QueryResponse.guardrail_result"],
    ["frontend/src/api/client.ts",              "Modified", "evaluateAnalysis function; IngestStatus interface"],
    ["frontend/src/components/QueryInput.tsx",  "Modified", "loadingAction state for independent per-button spinners"],
    ["frontend/src/components/IncidentCard.tsx","Modified", "formatDuration helper for human-readable outage duration"],
    ["frontend/src/components/EvaluationPanel.tsx", "NEW", "DeepEval-style metrics UI: 3 score bars + issues + summary"],
    ["frontend/src/components/GuardrailPanel.tsx",  "NEW", "3-check guardrail status panel with pass/warn/fail icons"],
    ["ARCHITECTURE.drawio",                     "NEW",      "draw.io system architecture diagram — dark theme + icons"],
    [".env",                                    "Modified", "LangSmith credentials appended"],
    [".env.example",                            "Modified", "LangSmith placeholder vars documented"],
]

col_w = [7.2*cm, 2.2*cm, doc.width - 9.4*cm]
formatted = [[files_data[0][0], files_data[0][1], files_data[0][2]]]
for row in files_data[1:]:
    path_col = Paragraph(row[0], mono_s)
    chg_col  = Paragraph(row[1], sty("ch", fontName="Helvetica-Bold", fontSize=8,
                                      textColor=GREEN_LT if row[1]=="NEW" else BLUE))
    sum_col  = Paragraph(row[2], cell_s)
    formatted.append([path_col, chg_col, sum_col])

ft = Table(formatted, colWidths=col_w, repeatRows=1)
ft.setStyle(TableStyle([
    ("BACKGROUND",    (0,0), (-1, 0), DARK_BG),
    ("FONTSIZE",      (0,0), (-1,-1), 8),
    ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, CARD_BG]),
    ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
    ("TOPPADDING",    (0,0), (-1,-1), 5),
    ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ("LEFTPADDING",   (0,0), (-1,-1), 6),
    ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
]))
story.append(ft)
story.append(Spacer(1, 0.5*cm))

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 6 — 20 Sample Queries
# ═══════════════════════════════════════════════════════════════════════════
story += section_header("SECTION 6 — 20 Sample Test Queries (Based on Actual Dataset)", ORANGE)
story.append(Spacer(1, 0.2*cm))
story.append(Paragraph(
    "The following queries are derived from real incident descriptions in telecom_incidents.csv "
    "(9,827 rows). All pass guardrail checks. Use them with the Deep Analysis button to exercise "
    "the full RAG + LangGraph pipeline and Evaluation metrics.",
    body_s,
))
story.append(Spacer(1, 0.2*cm))

queries = [
    ("01", "Sync / Timing",      BLUE,     "Nokia eNodeB synchronization failure causing timing degradation and S1 interface instability"),
    ("02", "Sync / Timing",      BLUE,     "Ericsson 4G LTE base station timing reference lost causing CQI and RSRQ degradation in London"),
    ("03", "5G Core (UPF)",      VIOLET,   "UPF not responding to PFCP heartbeat requests — SMF logs repeated association request timeouts"),
    ("04", "5G Core (Slice)",    VIOLET,   "5G NR slice configuration error in NSSF database causing S-NSSAI not found and service unavailability in Mumbai"),
    ("05", "4G-LTE Handover",    GREEN_LT, "LTE handover succeeds but UE immediately drops on target cell — Huawei eNodeB RRC release after handover"),
    ("06", "5G-NR Beam Failure", GREEN_LT, "Beam failure recovery procedures failing for high-speed UE at 80 kmph in 5G NR millimeter wave deployment"),
    ("07", "Microwave Backhaul", ORANGE,   "Ericsson microwave ODU Ethernet session terminated causing backhaul connectivity loss and site isolation in Singapore"),
    ("08", "Microwave HW",       ORANGE,   "Nokia microwave ODU hardware fault degrading RSL and ACM modulation causing packet loss on backhaul link"),
    ("09", "IP Core (BGP)",      TEAL,     "Cisco core router process crash in BGP OSPF stack causing IP backbone link instability and flow drops in Nairobi"),
    ("10", "MPLS Core",          TEAL,     "Juniper MPLS core network slicing virtualisation performance degradation causing increased latency in Tokyo"),
    ("11", "Fiber Transport",    RED,      "High FEC error rate on fiber transport link causing LTE throughput degradation and bearer loss in Kolkata"),
    ("12", "LTE Backhaul",       RED,      "Ericsson eNodeB backhaul degradation on S1 interface impacting EPS bearers and LTE signal quality in London"),
    ("13", "Cloud-RAN Weather",  BLUE,     "Nokia Cloud RAN fixed wireless access CPE showing 40 percent throughput reduction during heavy rain and stormy conditions"),
    ("14", "Cloud-RAN Virt.",    BLUE,     "Cloud RAN virtualisation resource contention causing radio unit processing delay and increased user plane latency"),
    ("15", "Critical Outage",    SLATE,    "Critical network outage lasting more than 4 hours affecting multiple Ericsson base stations across Sydney"),
    ("16", "Multi-vendor",       SLATE,    "Simultaneous high-severity incidents affecting Huawei and Nokia sites across Asia Pacific causing widespread service degradation"),
    ("17", "Config Error",       VIOLET,   "Cisco BGP routing configuration error causing routing loop and IP flow drops on core backbone in Nairobi"),
    ("18", "Config Mismatch",    VIOLET,   "Ericsson eNodeB parameter configuration mismatch causing handover failure and increased call drop rate in Melbourne"),
    ("19", "HW Power Failure",   ORANGE,   "Power supply failure on Huawei AAU causing radio unit shutdown and 5G NR coverage outage in Delhi"),
    ("20", "Broad / Stress Test",GREEN_LT, "Recurring CRITICAL and HIGH severity incidents across 5G NR and 4G LTE causing service outage and revenue impact — recommend systemic resolution"),
]

q_hdr = sty("qh", fontName="Helvetica-Bold", fontSize=8, textColor=WHITE)
q_data = [[Paragraph("<b>#</b>", q_hdr), Paragraph("<b>Category</b>", q_hdr), Paragraph("<b>Query</b>", q_hdr)]]
for num, cat, col, text in queries:
    q_data.append([
        Paragraph(f"<b>{num}</b>", sty("qn", fontName="Helvetica-Bold", fontSize=8, alignment=TA_CENTER)),
        Paragraph(cat, sty("qc", fontName="Helvetica-Bold", fontSize=7.5, textColor=col)),
        Paragraph(text, sty("qt", fontName="Helvetica", fontSize=8, leading=11)),
    ])

qt = Table(q_data, colWidths=[0.8*cm, 3.2*cm, doc.width - 4*cm], repeatRows=1)
qt.setStyle(TableStyle([
    ("BACKGROUND",    (0,0), (-1, 0), DARK_BG),
    ("FONTSIZE",      (0,0), (-1,-1), 8),
    ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, CARD_BG]),
    ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
    ("TOPPADDING",    (0,0), (-1,-1), 5),
    ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ("LEFTPADDING",   (0,0), (-1,-1), 6),
    ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
]))
story.append(qt)
story.append(Spacer(1, 0.5*cm))

# ── Footer ─────────────────────────────────────────────────────────────────
story.append(HRFlowable(width="100%", thickness=1, color=SLATE_LT, spaceAfter=6))
story.append(Paragraph(
    f"Generated by FaultSense AI — TelecomNetworkFaultIntel Project  |  {TODAY}  |  "
    "All changes applied to the working directory.",
    sty("ft", fontName="Helvetica", fontSize=8, textColor=SLATE_LT, alignment=TA_CENTER),
))

# ── Build ──────────────────────────────────────────────────────────────────
doc.build(story)
print(f"PDF created: {PDF_PATH}")
