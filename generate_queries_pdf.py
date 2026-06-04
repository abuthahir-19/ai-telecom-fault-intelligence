"""
Generates SAMPLE_QUERIES.pdf in the project root.
Run: python generate_queries_pdf.py
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

OUT = os.path.join(os.path.dirname(__file__), "SAMPLE_QUERIES.pdf")
W, H = A4

doc = SimpleDocTemplate(
    OUT, pagesize=A4,
    rightMargin=2*cm, leftMargin=2*cm,
    topMargin=2*cm,   bottomMargin=2*cm,
)

# ── Colours ───────────────────────────────────────────────────────────────────
DARK     = colors.HexColor("#0d1117")
BLUE     = colors.HexColor("#1f6feb")
BLUE_LT  = colors.HexColor("#4A9EFF")
GREEN    = colors.HexColor("#166534")
GREEN_LT = colors.HexColor("#16a34a")
VIOLET   = colors.HexColor("#6e40c9")
ORANGE   = colors.HexColor("#b45309")
TEAL     = colors.HexColor("#0f766e")
RED      = colors.HexColor("#b91c1c")
SLATE    = colors.HexColor("#334155")
SLATE_LT = colors.HexColor("#94a3b8")
CARD     = colors.HexColor("#f8fafc")
WHITE    = colors.white

def sty(name, **kw):
    return ParagraphStyle(name, **kw)

FONT = "Helvetica"

# ── Query data ────────────────────────────────────────────────────────────────
QUERIES = [
    # (num, category, expected_result, query_text, accent_color)
    ("01", "Synchronization / Timing",
     "All 3 guardrail checks PASS  ·  High context precision  ·  Faithfulness: High",
     "Nokia eNodeB synchronization failure causing timing degradation and S1 interface instability",
     BLUE),

    ("02", "Synchronization / Timing",
     "All 3 guardrail checks PASS  ·  High context precision  ·  Faithfulness: High",
     "Ericsson 4G LTE base station timing reference lost causing CQI and RSRQ degradation in London",
     BLUE),

    ("03", "5G Core — UPF / PFCP",
     "All 3 guardrail checks PASS  ·  Medium–High context precision  ·  Tests PFCP retrieval",
     "UPF not responding to PFCP heartbeat requests — SMF logs repeated association request timeouts",
     VIOLET),

    ("04", "5G Core — Network Slice",
     "All 3 guardrail checks PASS  ·  Medium context precision  ·  Slice config retrieval",
     "5G NR slice configuration error in NSSF database causing S-NSSAI not found and service unavailability in Mumbai",
     VIOLET),

    ("05", "4G LTE — Handover Failure",
     "All 3 guardrail checks PASS  ·  High context precision  ·  Answer relevancy: High",
     "LTE handover succeeds but UE immediately drops on target cell — Huawei eNodeB RRC release after handover",
     GREEN),

    ("06", "5G NR — Beam Failure",
     "All 3 guardrail checks PASS  ·  Medium context precision  ·  Beam failure scenarios",
     "Beam failure recovery procedures failing for high-speed UE at 80 kmph in 5G NR millimeter wave deployment",
     GREEN),

    ("07", "Microwave Backhaul — Link Loss",
     "All 3 guardrail checks PASS  ·  High context precision  ·  Backhaul incidents",
     "Ericsson microwave ODU Ethernet session terminated causing backhaul connectivity loss and site isolation in Singapore",
     ORANGE),

    ("08", "Microwave Backhaul — Hardware",
     "All 3 guardrail checks PASS  ·  High context precision  ·  HW fault retrieval",
     "Nokia microwave ODU hardware fault degrading RSL and ACM modulation causing packet loss on backhaul link",
     ORANGE),

    ("09", "IP Core — BGP / OSPF Crash",
     "All 3 guardrail checks PASS  ·  High context precision  ·  Cisco BGP incidents",
     "Cisco core router process crash in BGP OSPF stack causing IP backbone link instability and unexpected flow drops in Nairobi",
     TEAL),

    ("10", "MPLS Core — Virtualisation",
     "All 3 guardrail checks PASS  ·  Medium context precision  ·  Juniper MPLS incidents",
     "Juniper MPLS core network slicing virtualisation performance degradation causing increased latency in Tokyo",
     TEAL),

    ("11", "Fiber Transport — FEC Errors",
     "All 3 guardrail checks PASS  ·  High context precision  ·  Fiber transport faults",
     "High FEC error rate on fiber transport link causing LTE throughput degradation and bearer loss in Kolkata",
     RED),

    ("12", "4G LTE — Backhaul Degradation",
     "All 3 guardrail checks PASS  ·  High context precision  ·  S1 interface incidents",
     "Ericsson eNodeB backhaul degradation on S1 interface impacting EPS bearers and LTE signal quality in London",
     RED),

    ("13", "Cloud RAN — Weather Impact",
     "All 3 guardrail checks PASS  ·  Medium context precision  ·  FWA CPE incidents",
     "Nokia Cloud RAN fixed wireless access CPE showing 40 percent throughput reduction during heavy rain and stormy conditions",
     BLUE),

    ("14", "Cloud RAN — Virtualisation",
     "All 3 guardrail checks PASS  ·  Medium context precision  ·  vRAN resource incidents",
     "Cloud RAN virtualisation resource contention causing radio unit processing delay and increased user plane latency",
     BLUE),

    ("15", "Critical Outage — Long Duration",
     "All 3 guardrail checks PASS  ·  Medium context precision  ·  Multi-site critical incidents",
     "Critical network outage lasting more than 4 hours affecting multiple Ericsson base stations across Sydney",
     SLATE),

    ("16", "Multi-vendor — Regional Failure",
     "All 3 guardrail checks PASS  ·  Medium context precision  ·  Cross-vendor incidents",
     "Simultaneous high-severity incidents affecting Huawei and Nokia sites across Asia Pacific causing widespread service degradation",
     SLATE),

    ("17", "Configuration Error — BGP",
     "All 3 guardrail checks PASS  ·  Medium context precision  ·  Config fault retrieval",
     "Cisco BGP routing configuration error causing routing loop and IP flow drops on core backbone in Nairobi",
     VIOLET),

    ("18", "Configuration Error — eNodeB",
     "All 3 guardrail checks PASS  ·  High context precision  ·  Ericsson config mismatch",
     "Ericsson eNodeB parameter configuration mismatch causing handover failure and increased call drop rate in Melbourne",
     VIOLET),

    ("19", "Hardware — Power Supply Failure",
     "All 3 guardrail checks PASS  ·  High context precision  ·  AAU power incidents",
     "Power supply failure on Huawei AAU causing radio unit shutdown and 5G NR coverage outage in Delhi",
     ORANGE),

    ("20", "Broad Cross-Technology (Stress Test)",
     "All 3 guardrail checks PASS  ·  Lower context precision expected  ·  Tests broad retrieval quality",
     "Recurring CRITICAL and HIGH severity incidents across 5G NR and 4G LTE causing service outage and revenue impact — recommend systemic resolution",
     GREEN_LT),
]

# ── Story ─────────────────────────────────────────────────────────────────────
story = []

# ── Cover banner ──────────────────────────────────────────────────────────────
banner = Table(
    [[Paragraph(
        '<font color="white"><b>FaultSense AI — TelecomNetworkFaultIntel</b></font>',
        sty("bh", fontName="Helvetica-Bold", fontSize=15, alignment=TA_CENTER)
    )]],
    colWidths=[doc.width],
)
banner.setStyle(TableStyle([
    ("BACKGROUND",    (0,0), (-1,-1), DARK),
    ("TOPPADDING",    (0,0), (-1,-1), 14),
    ("BOTTOMPADDING", (0,0), (-1,-1), 14),
    ("ROUNDEDCORNERS",[8]),
]))
story.append(banner)
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph(
    "20 Sample Test Queries",
    sty("title", fontName="Helvetica-Bold", fontSize=22,
        textColor=DARK, alignment=TA_CENTER, spaceAfter=4),
))
story.append(Paragraph(
    "Deep Analysis &amp; Evaluation Metrics Testing  ·  Based on telecom_incidents.csv (9,827 rows)",
    sty("sub", fontName="Helvetica", fontSize=10,
        textColor=SLATE, alignment=TA_CENTER, spaceAfter=6),
))
story.append(HRFlowable(width="100%", thickness=2, color=BLUE_LT, spaceAfter=10))

# ── Instruction box ───────────────────────────────────────────────────────────
instr = Table(
    [[Paragraph(
        "<b>How to use:</b>  Copy any query below and paste it into the FaultSense AI search box. "
        "Click <b>Deep Analysis</b> to run the full LangGraph pipeline, then switch to the "
        "<b>Evaluation</b> tab to see Faithfulness, Answer Relevancy, and Context Precision scores. "
        "The <b>Guardrail</b> panel will show all 3 validation checks on every query.",
        sty("instr", fontName="Helvetica", fontSize=9, textColor=SLATE, leading=13),
    )]],
    colWidths=[doc.width],
)
instr.setStyle(TableStyle([
    ("BACKGROUND",    (0,0), (-1,-1), colors.HexColor("#f0f9ff")),
    ("BOX",           (0,0), (-1,-1), 1, BLUE_LT),
    ("TOPPADDING",    (0,0), (-1,-1), 10),
    ("BOTTOMPADDING", (0,0), (-1,-1), 10),
    ("LEFTPADDING",   (0,0), (-1,-1), 10),
    ("RIGHTPADDING",  (0,0), (-1,-1), 10),
    ("ROUNDEDCORNERS",[6]),
]))
story.append(instr)
story.append(Spacer(1, 0.5*cm))

# ── Query cards ───────────────────────────────────────────────────────────────
for num, category, expected, query, accent in QUERIES:
    # Number badge + category header row
    num_cell = Table(
        [[Paragraph(f'<b><font color="white">{num}</font></b>',
                    sty("num", fontName="Helvetica-Bold", fontSize=13, alignment=TA_CENTER))]],
        colWidths=[1*cm],
    )
    num_cell.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), accent),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("ROUNDEDCORNERS",[4]),
    ]))

    meta_cell = Table(
        [[Paragraph(f'<b>{category}</b>',
                    sty("cat", fontName="Helvetica-Bold", fontSize=10, textColor=accent))],
         [Paragraph(f'<font color="#64748b">Expected: </font>{expected}',
                    sty("exp", fontName="Helvetica", fontSize=8,
                        textColor=colors.HexColor("#475569"), leading=11))]],
        colWidths=[doc.width - 1.4*cm],
    )
    meta_cell.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), CARD),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("RIGHTPADDING",  (0,0), (-1,-1), 8),
    ]))

    header_row = Table(
        [[num_cell, meta_cell]],
        colWidths=[1*cm, doc.width - 1*cm],
    )
    header_row.setStyle(TableStyle([
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING",   (0,0), (-1,-1), 0),
        ("RIGHTPADDING",  (0,0), (-1,-1), 0),
        ("TOPPADDING",    (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 0),
        ("BOX",           (0,0), (-1,-1), 1.5, accent),
        ("ROUNDEDCORNERS",[5]),
    ]))

    # Query text box
    query_box = Table(
        [[Paragraph(
            query,
            sty("qt", fontName="Helvetica", fontSize=10,
                textColor=DARK, leading=14),
        )]],
        colWidths=[doc.width],
    )
    query_box.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), colors.white),
        ("BOX",           (0,0), (-1,-1), 1, colors.HexColor("#e2e8f0")),
        ("LEFTBORDER",    (0,0), (0,-1), 3, accent),
        ("TOPPADDING",    (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING",   (0,0), (-1,-1), 12),
        ("RIGHTPADDING",  (0,0), (-1,-1), 10),
    ]))

    story.append(header_row)
    story.append(query_box)
    story.append(Spacer(1, 0.35*cm))

# ── Footer ────────────────────────────────────────────────────────────────────
story.append(Spacer(1, 0.2*cm))
story.append(HRFlowable(width="100%", thickness=1,
                         color=colors.HexColor("#e2e8f0"), spaceAfter=6))
story.append(Paragraph(
    "FaultSense AI  ·  TelecomNetworkFaultIntel Project  ·  All queries derived from real "
    "incident patterns in telecom_incidents.csv  ·  03 June 2026",
    sty("ft", fontName="Helvetica", fontSize=8,
        textColor=SLATE_LT, alignment=TA_CENTER),
))

doc.build(story)
print(f"PDF created: {OUT}")
