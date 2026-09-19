#!/usr/bin/env python3
"""
Squeeze AI - Comprehensive Feature & Architecture Guide Generator (PDF)
Designed for teammates new to programming. Explains core concepts, features,
real-world analogies, code comparisons, and demo guides with professional formatting.
Optimized 4-page publication-grade layout with balanced page budgets.
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, 
    KeepTogether, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

# --- NUMBERED CANVAS FOR "PAGE X OF Y" FOOTER ---
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber > 1:
            self.saveState()
            # Running Header
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawString(54, 752, "SQUEEZE AI  •  TEAMMATE & DEVELOPER GUIDE")
            self.setFont("Helvetica", 8)
            self.drawRightString(558, 752, "v1.0 (BETA)")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.75)
            self.line(54, 744, 558, 744)

            # Running Footer
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.75)
            self.line(54, 48, 558, 48)
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#94A3B8"))
            self.drawString(54, 36, "Squeeze AI — 100% Local Context Optimization Layer for LLMs")
            self.drawRightString(558, 36, f"Page {self._pageNumber} of {page_count}")
            self.restoreState()

def build_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom Brand Palette
    C_DARK = colors.HexColor("#07090E")
    C_GOLD = colors.HexColor("#F5C518")
    C_EMERALD = colors.HexColor("#10B981")
    C_INDIGO = colors.HexColor("#4F46E5")
    C_SLATE_DARK = colors.HexColor("#1E293B")
    C_SLATE_TEXT = colors.HexColor("#334155")
    C_MUTED = colors.HexColor("#64748B")
    C_BG_CARD = colors.HexColor("#F8FAFC")
    C_BG_CODE = colors.HexColor("#0F172A")
    C_BORDER = colors.HexColor("#E2E8F0")

    # Typography Styles
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=C_MUTED
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=C_DARK,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=C_INDIGO,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyMain',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=C_SLATE_TEXT,
        spaceAfter=6
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor("#0F172A")
    )

    code_style = ParagraphStyle(
        'CodeSnippet',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.6,
        leading=10,
        textColor=colors.HexColor("#38BDF8")
    )

    badge_style = ParagraphStyle(
        'BadgeText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    story = []

    # ==========================================
    # PAGE 1: TITLE, WHY SQUEEZE & CORE CONCEPTS
    # ==========================================
    logo_path = "/Users/aashu/Aashu/Squeeze/squeeze_logo_rendered.png"
    if os.path.exists(logo_path):
        logo_img = Image(logo_path, width=44, height=44)
    else:
        logo_img = Paragraph("<b>[SQUEEZE]</b>", h2_style)

    header_table_data = [
        [
            logo_img,
            [
                Paragraph("SQUEEZE AI", ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=22, leading=26, textColor=C_DARK)),
                Paragraph("Official Teammate & Product Feature Guide", subtitle_style)
            ]
        ]
    ]
    header_table = Table(header_table_data, colWidths=[54, 450])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (1, 0), (1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))

    # Executive Hero Banner Box
    banner_content = [
        Paragraph("<b>Target Audience:</b> Teammates, presenters, interns, and engineers new to AI tooling.", ParagraphStyle('B1', fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=C_DARK)),
        Paragraph("<b>Core Mission:</b> Stop hitting AI token limits. Squeeze shrinks massive codebases, data dumps, and log files by up to <b>99.4%</b> directly on your laptop — saving thousands of dollars and speeding up AI responses without ever exposing your private data to the cloud.", ParagraphStyle('B2', fontName='Helvetica', fontSize=8.8, leading=13, textColor=C_SLATE_TEXT))
    ]
    banner_table = Table([[banner_content]], colWidths=[504])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FEF9C3")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#FACC15")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 12))

    # SECTION 1: THE BASICS
    story.append(Paragraph("1. The Basics: What is Squeeze & Why Does It Exist?", h1_style))
    story.append(Paragraph(
        "If you are new to coding and modern AI tools like ChatGPT, Claude, or Cursor, here is the plain-English explanation of the three biggest concepts you need to know:",
        body_style
    ))

    basics_data = [
        [
            Paragraph("<b>Concept</b>", ParagraphStyle('TH1', fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.white)),
            Paragraph("<b>Real-World Analogy</b>", ParagraphStyle('TH2', fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.white)),
            Paragraph("<b>Why It Matters</b>", ParagraphStyle('TH3', fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.white))
        ],
        [
            Paragraph("<b>Tokens</b>", ParagraphStyle('TD1', fontName='Helvetica-Bold', fontSize=8.5, textColor=C_DARK)),
            Paragraph("Think of tokens like words or syllables. Roughly 1,000 tokens ≈ 750 words.", body_style),
            Paragraph("AI companies charge money for every single token you send, exactly like a <b>taxi meter</b> ticking upward.", body_style)
        ],
        [
            Paragraph("<b>Context Window</b>", ParagraphStyle('TD2', fontName='Helvetica-Bold', fontSize=8.5, textColor=C_DARK)),
            Paragraph("Think of it as the AI's <b>desk space</b> or short-term memory.", body_style),
            Paragraph("The AI can only look at what fits on the desk at one time. If the desk is full, you can't ask any more questions.", body_style)
        ],
        [
            Paragraph("<b>Context Rot</b>", ParagraphStyle('TD3', fontName='Helvetica-Bold', fontSize=8.5, textColor=C_DARK)),
            Paragraph("Imagine giving an assistant a 2,000-page phonebook to answer 'What time is the meeting?'", body_style),
            Paragraph("When given too much messy information, the AI gets confused, slow, misses instructions, and begins to hallucinate.", body_style)
        ]
    ]
    basics_table = Table(basics_data, colWidths=[90, 200, 214])
    basics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_DARK),
        ('GRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, C_BG_CARD]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    story.append(basics_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        "<b>What Squeeze Does:</b> Squeeze sits directly between you and the AI. Before any code, database dump, or terminal log is transmitted over the internet, Squeeze automatically cleans, reorganizes, and compresses it. It hands the AI only what it needs — shrinking the bill, eliminating context rot, and protecting passwords.",
        body_style
    ))
    story.append(Spacer(1, 10))

    three_pillars_data = [
        [
            Paragraph("<b>⚡ 99.4% Compression</b><br/>Condenses massive repos from 60,000 tokens down to 385 tokens.", body_style),
            Paragraph("<b>🔒 100% On-Device Privacy</b><br/>Zero cloud roundtrips. Regex secret scanner masks credentials locally.", body_style),
            Paragraph("<b>💰 90% Cost Reduction</b><br/>CacheAligner anchors prompts to trigger maximum provider cache discounts.", body_style)
        ]
    ]
    pillars_table = Table(three_pillars_data, colWidths=[168, 168, 168])
    pillars_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_BG_CARD),
        ('BOX', (0, 0), (-1, -1), 1, C_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(pillars_table)

    # ==========================================
    # PAGE 2: CODEBASE GRAPH, SKELETONIZER & CCR
    # ==========================================
    story.append(PageBreak())

    story.append(Paragraph("2. Deep Dive: Squeeze's 7 Flagship Features", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER, spaceBefore=2, spaceAfter=8))

    # FEATURE 1: CODEBASE KNOWLEDGE GRAPH
    story.append(Paragraph("Feature 1: Interactive Codebase Knowledge Graph", h2_style))
    story.append(Paragraph(
        "<b>The Problem:</b> When you ask Claude or Cursor a question about your project, it usually scans dozens of files blindly, burning 50,000 to 100,000 tokens ($0.15 to $1.50 per question) just trying to figure out which file has the code you want.<br/>"
        "<b>The Squeeze Solution:</b> Squeeze scans your entire project upfront and creates a <b>topological dependency graph</b>. It identifies which files are the 'command centers' (hubs), extracts all class and function names, and creates a visual map.",
        body_style
    ))

    graph_stats_data = [
        [
            Paragraph("<b>Raw Code Tokens</b>", badge_style),
            Paragraph("<b>Squeeze Graph Tokens</b>", badge_style),
            Paragraph("<b>Net Token Reduction</b>", badge_style),
            Paragraph("<b>AI Exploration Cost</b>", badge_style)
        ],
        [
            Paragraph("~59,955 tokens", ParagraphStyle('G1', fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.HexColor("#DC2626"))),
            Paragraph("~385 tokens", ParagraphStyle('G2', fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.HexColor("#16A34A"))),
            Paragraph("<b>-99.4% SAVED</b>", ParagraphStyle('G3', fontName='Helvetica-Bold', fontSize=8.5, textColor=C_DARK)),
            Paragraph("Eliminated entirely", ParagraphStyle('G4', fontName='Helvetica', fontSize=8, textColor=C_MUTED))
        ]
    ]
    graph_stats_table = Table(graph_stats_data, colWidths=[126, 126, 126, 126])
    graph_stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_SLATE_DARK),
        ('GRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('BACKGROUND', (0, 1), (-1, 1), C_BG_CARD)
    ]))
    story.append(graph_stats_table)
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "<b>How to use it:</b> Teammates can simply double-click <code>codebase_graph.html</code> to open an interactive canvas in their browser where they can drag nodes, zoom in, and click any file to see its functions. For Claude Code, simply run: <code>squeeze_codebase_graph</code>.",
        callout_style
    ))
    story.append(Spacer(1, 8))

    # FEATURE 2: AST SKELETONIZER
    story.append(Paragraph("Feature 2: AST Code Skeletonizer (Smart Blueprints)", h2_style))
    story.append(Paragraph(
        "<b>What is an 'AST'?</b> AST stands for <i>Abstract Syntax Tree</i>. You don't need to know how the math works — just think of it as the <b>architectural blueprint</b> of a house. It tells you where the doors, rooms, and windows are, without needing to inspect every brick inside the walls.<br/>"
        "<b>How Squeeze Uses It:</b> When an AI needs to understand an API or library, it only needs the function names and types, not the 200 lines of implementation logic inside.",
        body_style
    ))

    code_comp_data = [
        [
            Paragraph("<b>Raw Code Sent to AI (Heavy & Expensive)</b>", ParagraphStyle('C1', fontName='Helvetica-Bold', fontSize=8, textColor=colors.HexColor("#991B1B"))),
            Paragraph("<b>Squeeze Skeletonized (Clean Blueprint)</b>", ParagraphStyle('C2', fontName='Helvetica-Bold', fontSize=8, textColor=colors.HexColor("#166534")))
        ],
        [
            Paragraph(
                "class PaymentManager:\n"
                "    def process_payment(self, user_id: str, amount: float):\n"
                "        # 80 lines of database validation\n"
                "        # 40 lines of Stripe webhook handling\n"
                "        # 25 lines of logging and metrics\n"
                "        return {'status': 'success'}",
                code_style
            ),
            Paragraph(
                "class PaymentManager:\n"
                "    def process_payment(self, user_id: str, amount: float) -> dict:\n"
                "        \"\"\"Processes card transaction.\"\"\"\n"
                "        pass  # Implementation condensed (-82% tokens)",
                code_style
            )
        ]
    ]
    code_comp_table = Table(code_comp_data, colWidths=[252, 252])
    code_comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor("#FEE2E2")),
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor("#DCFCE7")),
        ('BACKGROUND', (0, 1), (-1, 1), C_BG_CODE),
        ('GRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(code_comp_table)
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "<b>Key Takeaway:</b> Saves <b>70% to 85%</b> of code tokens across Python, TypeScript, JavaScript, Go, and Rust while leaving 100% of the architectural contract intact.",
        body_style
    ))
    story.append(Spacer(1, 8))

    # FEATURE 3: REVERSIBLE CHUNK RETRIEVAL
    story.append(Paragraph("Feature 3: Reversible Chunk Retrieval (CCR) — The Safety Net", h2_style))
    story.append(Paragraph(
        "<b>The Common Concern:</b> <i>'Wait! If we compress the text, what if the AI needs the original details that were stripped away?'</i><br/>"
        "<b>The Squeeze Innovation:</b> Squeeze is not a lossy text summarizer. When Squeeze compresses any large section of text, it caches the original on your computer and attaches an invisible bookmark tag:<br/>"
        "<font face='Courier' color='#4F46E5'><b>[SQUEEZE_CHUNK id=\"chunk_a8f3b2\" (Saved 420 tokens). Call squeeze_retrieve for full original]</b></font><br/>"
        "If the AI ever discovers it truly needs the original uncompressed code or document, it simply calls <code>squeeze_retrieve(chunk_id=\"chunk_a8f3b2\")</code> and gets the exact raw content back in 1 millisecond. It's like having a digital coat-check claim ticket.",
        body_style
    ))

    # ==========================================
    # PAGE 3: CACHEALIGNER, JSON, DLP, SURFACES
    # ==========================================
    story.append(PageBreak())

    # FEATURE 4: CACHEALIGNER
    story.append(Paragraph("Feature 4: CacheAligner™ (Prompt Cache Architecture)", h2_style))
    story.append(Paragraph(
        "Modern frontier models (like Claude 3.5 Sonnet, OpenAI, and Google Gemini) give massive <b>up to 90% cost discounts</b> if the beginning of your prompt matches previous prompts you sent. This is called <b>Prompt Caching</b>.<br/>"
        "If you put volatile things (like the current time or a temporary question) at the top of your prompt, you break the cache and pay full price every time.<br/>"
        "<b>CacheAligner</b> deterministically sorts context into three structured tiers:",
        body_style
    ))

    cache_data = [
        [
            Paragraph("<b>Tier 1: Static Directives</b>", ParagraphStyle('CT1', fontName='Helvetica-Bold', fontSize=8.5, textColor=C_DARK)),
            Paragraph("System instructions, persona, and permanent project rules.", body_style),
            Paragraph("<b>Anchored Prefix (100% Cache Hit)</b>", ParagraphStyle('ST1', fontName='Helvetica-Bold', fontSize=8, textColor=colors.HexColor("#16A34A")))
        ],
        [
            Paragraph("<b>Tier 2: Code Architecture</b>", ParagraphStyle('CT2', fontName='Helvetica-Bold', fontSize=8.5, textColor=C_DARK)),
            Paragraph("Topological graph, file exports, and API schemas.", body_style),
            Paragraph("<b>Anchored Body (Cached across turns)</b>", ParagraphStyle('ST2', fontName='Helvetica-Bold', fontSize=8, textColor=colors.HexColor("#16A34A")))
        ],
        [
            Paragraph("<b>Tier 3: Volatile Task</b>", ParagraphStyle('CT3', fontName='Helvetica-Bold', fontSize=8.5, textColor=C_DARK)),
            Paragraph("Your active question: 'Fix the bug on line 42'.", body_style),
            Paragraph("<b>Tail position (Only part billed)</b>", ParagraphStyle('ST3', fontName='Helvetica', fontSize=8, textColor=C_MUTED))
        ]
    ]
    cache_table = Table(cache_data, colWidths=[130, 230, 144])
    cache_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('BACKGROUND', (0, 0), (0, -1), C_BG_CARD),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
    ]))
    story.append(cache_table)
    story.append(Spacer(1, 8))

    # FEATURE 5: JSON & LOG SQUEEZER
    story.append(Paragraph("Feature 5: Smart JSON Array Folding & Log Deduplication", h2_style))
    story.append(Paragraph(
        "<b>The Problem:</b> When you copy an API response from a database, it often has 1,000 repetitive items. Pasting that into Claude wastes 15,000 tokens on duplicate brackets and keys. The same happens with terminal logs that print the same error message 500 times in a row.<br/>"
        "<b>The Squeeze Solution:</b><br/>"
        "• <b>JSON Folding:</b> Keeps the first 2 representative array items so the AI sees the schema structure, and replaces the remaining 998 items with <code>[... 998 items folded by Squeeze ...]</code>. Instant 95% token savings.<br/>"
        "• <b>Log Deduplication:</b> Strips ugly terminal color codes (ANSI escapes) and collapses repetitive stack traces into a single line: <code>[Repeated 412 times] ConnectionTimeoutError</code>.",
        body_style
    ))
    story.append(Spacer(1, 8))

    # FEATURE 6: DLP SECRET SHIELD
    story.append(Paragraph("Feature 6: Local DLP Secret Shield (Enterprise Privacy)", h2_style))
    story.append(Paragraph(
        "<b>The Danger:</b> Developers frequently copy-paste code containing sensitive API keys, passwords, or company credentials straight into ChatGPT or Claude. Once sent over the internet, those secrets can be logged or leaked.<br/>"
        "<b>The Squeeze Digital Bouncer:</b> Squeeze runs an on-device regex scanner that intercepts text <b>before</b> it leaves your browser. It instantly detects and masks 8 major secret formats:",
        body_style
    ))

    dlp_data = [
        [
            Paragraph("<b>Key Type</b>", badge_style),
            Paragraph("<b>Pattern Detected</b>", badge_style),
            Paragraph("<b>What Squeeze Sends to AI</b>", badge_style)
        ],
        [
            Paragraph("OpenAI API Key", body_style),
            Paragraph("<code>sk-proj-49f8a...</code>", code_style),
            Paragraph("<font color='#DC2626'><b>[MASKED_OPENAI_KEY]</b></font>", body_style)
        ],
        [
            Paragraph("Anthropic Key", body_style),
            Paragraph("<code>sk-ant-api03-...</code>", code_style),
            Paragraph("<font color='#DC2626'><b>[MASKED_ANTHROPIC_KEY]</b></font>", body_style)
        ],
        [
            Paragraph("AWS Credentials", body_style),
            Paragraph("<code>AKIAIOSFODNN7EXAMPLE</code>", code_style),
            Paragraph("<font color='#DC2626'><b>[MASKED_AWS_KEY]</b></font>", body_style)
        ],
        [
            Paragraph("GitHub & JWT Tokens", body_style),
            Paragraph("<code>ghp_38f2... / eyJhbG...</code>", code_style),
            Paragraph("<font color='#DC2626'><b>[MASKED_GITHUB_TOKEN] / [MASKED_JWT]</b></font>", body_style)
        ]
    ]
    dlp_table = Table(dlp_data, colWidths=[130, 180, 194])
    dlp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ('GRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, C_BG_CARD]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
    ]))
    story.append(dlp_table)
    story.append(Spacer(1, 8))

    # FEATURE 7: DUAL SURFACE
    story.append(Paragraph("Feature 7: Dual Surface — Chrome Extension + Claude Code MCP", h2_style))
    surfaces_data = [
        [
            Paragraph("<b>Surface 1: Chrome Extension (Web UI)</b>", ParagraphStyle('S1', fontName='Helvetica-Bold', fontSize=8.5, textColor=C_INDIGO)),
            Paragraph("<b>Surface 2: Standalone MCP Server (CLI / IDE)</b>", ParagraphStyle('S2', fontName='Helvetica-Bold', fontSize=8.5, textColor=C_INDIGO))
        ],
        [
            Paragraph(
                "• <b>Live Token Counter HUD:</b> Injected on Claude.ai & ChatGPT.<br/>"
                "• <b>Side Panel Studio:</b> Side-by-side diff visualizer.<br/>"
                "• <b>Context Vault:</b> Save company guidelines with 1-click injection.<br/>"
                "• <b>Quick Install:</b> Load unpacked in Chrome in 15 seconds.",
                body_style
            ),
            Paragraph(
                "• <b>Claude Code CLI:</b> Native Model Context Protocol server.<br/>"
                "• <b>Cursor IDE:</b> Registered tools callable by AI agents.<br/>"
                "• <b>1-Command Installer:</b> <code>python3 install.py</code> auto-configures.<br/>"
                "• <b>Zero Dependencies:</b> Built with pure standard libraries.",
                body_style
            )
        ]
    ]
    surfaces_table = Table(surfaces_data, colWidths=[252, 252])
    surfaces_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_BG_CARD),
        ('GRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    story.append(surfaces_table)
    story.append(Spacer(1, 10))

    # ==========================================
    # SECTION 3 & 4: GETTING STARTED & PRESENTATION CHEAT SHEET
    # ==========================================
    story.append(Paragraph("3. How Teammates Can Run Squeeze Right Now", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER, spaceBefore=2, spaceAfter=8))

    setup_steps = [
        "<b>Step 1 — Visual Codebase Map:</b> In Finder, open <code>/Users/aashu/Squeeze</code> and double-click <code>codebase_graph.html</code> to view your project's interactive architecture.",
        "<b>Step 2 — Connect to Claude Code:</b> Open Terminal and type <code>python3 install.py</code>. Press [1] to connect to Claude Code. It's ready in 3 seconds!",
        "<b>Step 3 — Ask Claude Code to Squeeze:</b> In any Claude Code chat, type: <i>'Use squeeze_codebase_graph to inspect this project'</i> or <i>'Check squeeze_stats to see how many dollars we saved'</i>.",
        "<b>Step 4 — Chrome Extension:</b> Go to <code>chrome://extensions</code> in your browser, toggle 'Developer mode' on, click 'Load unpacked', and select the Squeeze folder."
    ]
    for s in setup_steps:
        story.append(Paragraph(f"• {s}", body_style))
    story.append(Spacer(1, 14))

    story.append(Paragraph("4. Presentation Cheat Sheet & Vocabulary", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER, spaceBefore=2, spaceAfter=8))

    glossary_data = [
        [
            Paragraph("<b>Term</b>", badge_style),
            Paragraph("<b>Plain-English Definition</b>", badge_style),
            Paragraph("<b>Demo Talking Point</b>", badge_style)
        ],
        [
            Paragraph("<b>AST</b>", ParagraphStyle('G1', fontName='Helvetica-Bold', fontSize=8.5, textColor=C_DARK)),
            Paragraph("Abstract Syntax Tree — the structural skeleton of code.", body_style),
            Paragraph("\"We keep the contract, drop the implementation.\"", callout_style)
        ],
        [
            Paragraph("<b>MCP</b>", ParagraphStyle('G2', fontName='Helvetica-Bold', fontSize=8.5, textColor=C_DARK)),
            Paragraph("Model Context Protocol — Anthropic's open standard for AI tools.", body_style),
            Paragraph("\"Claude Code can call Squeeze just like a human engineer.\"", callout_style)
        ],
        [
            Paragraph("<b>In-Degree Centrality</b>", ParagraphStyle('G3', fontName='Helvetica-Bold', fontSize=8.5, textColor=C_DARK)),
            Paragraph("How many other files depend on or import a specific file.", body_style),
            Paragraph("\"Ranks the most critical architectural hubs in your codebase.\"", callout_style)
        ],
        [
            Paragraph("<b>Zero-Latency</b>", ParagraphStyle('G4', fontName='Helvetica-Bold', fontSize=8.5, textColor=C_DARK)),
            Paragraph("Processing happens in under 5 milliseconds with zero cloud roundtrips.", body_style),
            Paragraph("\"100% deterministic algorithms, no slow LLM summarizers.\"", callout_style)
        ],
        [
            Paragraph("<b>Cache Hit</b>", ParagraphStyle('G5', fontName='Helvetica-Bold', fontSize=8.5, textColor=C_DARK)),
            Paragraph("When an AI provider detects repeated prompt prefix tokens and applies a 90% discount.", body_style),
            Paragraph("\"CacheAligner maximizes cache hits turn after turn.\"", callout_style)
        ]
    ]
    glossary_table = Table(glossary_data, colWidths=[90, 200, 214])
    glossary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_DARK),
        ('GRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, C_BG_CARD]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    story.append(glossary_table)
    story.append(Spacer(1, 14))

    # Concluding Callout Card
    closing_card = [
        Paragraph("<b>💡 Key Takeaway for the Entire Team:</b> Squeeze is not an AI wrapper or an LLM itself. It is a <i>classical computer science pre-processor</i>. It makes your existing AI tools (Claude, ChatGPT, Cursor) faster, significantly cheaper, and safe for private company data.", ParagraphStyle('CC1', fontName='Helvetica', fontSize=8.8, leading=13, textColor=C_DARK))
    ]
    closing_table = Table([[closing_card]], colWidths=[504])
    closing_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F0FDF4")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#86EFAC")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(closing_table)

    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] PDF generated at: {filename}")

if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "/Users/aashu/Aashu/Squeeze/SQUEEZE_AI_Complete_Feature_Guide.pdf"
    build_pdf(out_file)
