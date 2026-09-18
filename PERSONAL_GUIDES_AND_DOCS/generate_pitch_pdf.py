import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

# Palette
COLOR_PRIMARY = colors.HexColor("#FF6D00")      # Vibrant Squeeze Orange
COLOR_SECONDARY = colors.HexColor("#0A0A0F")    # Dark Charcoal / Obsidian
COLOR_ACCENT_GREEN = colors.HexColor("#10B981") # Emerald Green
COLOR_ACCENT_BLUE = colors.HexColor("#0284C7")  # Sky Blue
COLOR_BG_LIGHT = colors.HexColor("#F8FAFC")     # Slate 50
COLOR_TEXT_DARK = colors.HexColor("#1E293B")    # Slate 800
COLOR_TEXT_MUTED = colors.HexColor("#64748B")   # Slate 500
COLOR_BORDER = colors.HexColor("#E2E8F0")       # Slate 200

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
        if self._pageNumber == 1:
            # Skip header/footer on cover page
            return

        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(COLOR_PRIMARY)
        self.drawString(54, 11 * inch - 36, "SQUEEZE AI")
        self.setFont("Helvetica", 8)
        self.setFillColor(COLOR_TEXT_MUTED)
        self.drawString(115, 11 * inch - 36, "|   Hackathon Presentation & Winning Pitch Deck")

        # Top rule
        self.setStrokeColor(COLOR_BORDER)
        self.setLineWidth(0.5)
        self.line(54, 11 * inch - 42, 8.5 * inch - 54, 11 * inch - 42)

        # Bottom rule & footer
        self.line(54, 45, 8.5 * inch - 54, 45)
        self.drawString(54, 32, "Confidential — Prepared for Hackathon Demo Day")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * inch - 54, 32, page_text)
        self.restoreState()

def build_pdf(filename="Squeeze_AI_Hackathon_Pitch_Guide.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=32,
        leading=38,
        textColor=COLOR_SECONDARY,
        spaceAfter=8
    )
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=18,
        textColor=COLOR_TEXT_MUTED,
        spaceAfter=20
    )
    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=COLOR_SECONDARY,
        spaceBefore=0,
        spaceAfter=10
    )
    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=COLOR_PRIMARY,
        spaceBefore=8,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=COLOR_TEXT_DARK,
        spaceAfter=6
    )
    body_bold = ParagraphStyle(
        'BodyBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    say_style = ParagraphStyle(
        'VerbatimSay',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155")
    )
    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#0F172A")
    )

    story = []

    # ================= PAGE 1: COVER =================
    story.append(Spacer(1, 40))
    # Badge
    badge_table = Table([[
        Paragraph('<font color="#FF6D00"><b>● HACKATHON FINALIST PRESENTATION GUIDE</b></font>', styles['Normal'])
    ]], colWidths=[280])
    badge_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFF7ED")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#FED7AA")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(badge_table)
    story.append(Spacer(1, 15))

    story.append(Paragraph("Squeeze AI <font color='#FF6D00'>v1.0</font>", title_style))
    story.append(Paragraph("How to Present, Demo, and Win With Your Local Token & Context Optimizer", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=COLOR_PRIMARY, spaceBefore=0, spaceAfter=25))

    # Metric Highlights Grid
    metric_data = [
        [
            Paragraph("<font size=20 color='#FF6D00'><b>70%</b></font><br/><font size=8 color='#64748B'>MAX TOKEN REDUCTION</font>", styles['Normal']),
            Paragraph("<font size=20 color='#10B981'><b>100%</b></font><br/><font size=8 color='#64748B'>LOCAL PRIVACY / NO API</font>", styles['Normal']),
            Paragraph("<font size=20 color='#0284C7'><b>3 AIs</b></font><br/><font size=8 color='#64748B'>CLAUDE, CHATGPT, GEMINI</font>", styles['Normal']),
            Paragraph("<font size=20 color='#6366F1'><b>8 TYPES</b></font><br/><font size=8 color='#64748B'>DLP CREDENTIAL SHIELD</font>", styles['Normal'])
        ]
    ]
    t_metrics = Table(metric_data, colWidths=[126, 126, 126, 126])
    t_metrics.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 1, COLOR_BORDER),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(t_metrics)
    story.append(Spacer(1, 25))

    # Executive Overview Box
    exec_text = """<b>EXECUTIVE SUMMARY:</b><br/>
    Squeeze AI solves the single largest hidden inefficiency in the modern AI stack: prompt bloat and accidental credential leakage. 
    By operating directly inside the browser between the user's keyboard and Claude, ChatGPT, and Gemini, Squeeze intercepts prompts 
    in real time, strips redundant filler, masks secrets via DLP, auto-attaches relevant context from a local Context Vault, and 
    displays a live word-level diff — completely offline in under 200 milliseconds."""
    exec_table = Table([[Paragraph(exec_text, body_style)]], colWidths=[504])
    exec_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('LINELEFT', (0,0), (-1,-1), 4, COLOR_PRIMARY),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('LEFTPADDING', (0,0), (-1,-1), 14),
        ('RIGHTPADDING', (0,0), (-1,-1), 14),
    ]))
    story.append(exec_table)

    story.append(Spacer(1, 25))
    story.append(Paragraph("<b>Table of Contents for Today's Pitch:</b>", body_bold))
    toc_items = [
        "1. The Core Problem: Why LLM Token Waste & Credential Leakage is a Multi-Billion Dollar Crisis",
        "2. The Squeeze AI Solution: Architectural Overview & Differentiators",
        "3. The 90-Second Demo Playbook: Choreographed Live Walkthrough",
        "4. The 2-Minute Pitch Script: Verbatim Stage Script with Pauses & Emphasis",
        "5. The Judge Q&A Battlecard: Bulletproof Answers for Technical & Business Questions",
        "6. Competitive Matrix & Market Opportunity",
        "7. Stage Presence, Body Language & Pre-Flight Checklist"
    ]
    for item in toc_items:
        story.append(Paragraph(f"• {item}", body_style))

    story.append(PageBreak())

    # ================= PAGE 2: THE PROBLEM & SOLUTION =================
    story.append(Paragraph("1. The Problem & Market Opportunity", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY, spaceBefore=0, spaceAfter=14))

    prob_p1 = """Every foundation model charges by the token, yet <b>over 40% of tokens in conversational prompts are pure waste</b>. 
    Users write prompts like conversational emails: polite greetings, repetitive preambles ('just to clarify', 'as I said earlier'), 
    redundant adjectives, and copy-pasted blocks already sent in the thread. A 2,000-token prompt often conveys only 1,200 tokens of 
    genuine technical intent."""
    story.append(Paragraph(prob_p1, body_style))
    story.append(Spacer(1, 6))

    prob_table_data = [
        [
            Paragraph("<b>The Financial Bleed</b>", h2_style),
            Paragraph("<b>The Enterprise Security Nightmare</b>", h2_style)
        ],
        [
            Paragraph("• Claude Opus costs <b>$15.00/M</b> tokens; GPT-4o costs <b>$2.50/M</b>.<br/>"
                      "• Power users sending 200+ prompts/day waste $20–$50/month on filler.<br/>"
                      "• Enterprise engineering teams burn thousands monthly on duplicate context in long threads.<br/>"
                      "• Slower time-to-first-token and increased latency on bloated inputs.", body_style),
            Paragraph("• <b>82% of developers</b> have pasted credentials into AI chatbots (Cyberhaven 2024).<br/>"
                      "• OpenAI keys, AWS access secrets, JWT bearer tokens, and MongoDB URIs are routinely sent to external servers.<br/>"
                      "• No native browser protection exists to intercept and mask secrets before they depart the client.", body_style)
        ]
    ]
    prob_t = Table(prob_table_data, colWidths=[246, 246])
    prob_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 1, COLOR_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(prob_t)

    story.append(Spacer(1, 14))
    story.append(Paragraph("2. The Squeeze AI Solution", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY, spaceBefore=0, spaceAfter=14))

    sol_overview = """Squeeze AI sits directly in the user's browser as a zero-latency client-side interception layer. 
    It evaluates, sanitizes, and condenses prompts <b>before</b> they touch any network socket."""
    story.append(Paragraph(sol_overview, body_style))
    story.append(Spacer(1, 6))

    pillars_data = [
        [
            Paragraph("<b>⚡ 9-Rule Optimization Engine</b>", styles['Normal']),
            Paragraph("Removes polite filler, duplicate sentences, meta-commentary, and redundant qualifiers. Protects code blocks, markdown headings, and URLs via placeholder isolation.", body_style)
        ],
        [
            Paragraph("<b>🛡️ DLP Secret Shield</b>", styles['Normal']),
            Paragraph("Real-time regex scanner detecting 8 credential types (OpenAI keys, Anthropic keys, Google AI keys, AWS keys, GitHub tokens, JWTs, DB URIs, and config secrets). Masks secrets locally.", body_style)
        ],
        [
            Paragraph("<b>🚀 Squeeze AST Code Skeletons</b>", styles['Normal']),
            Paragraph("Deterministic AST parser for Python, TypeScript, and JSON. Collapses function bodies to <code>...</code>, keeping classes, signatures, and types (saving 70–90% code tokens).", body_style)
        ],
        [
            Paragraph("<b>⚡ Squeeze CacheAligner &amp; MCP</b>", styles['Normal']),
            Paragraph("Reorders prompts into static prefixes and task tails to lock 90% provider prompt-caching. Includes a stdio MCP Server for Cursor, Claude Code, and Cline.", body_style)
        ],
        [
            Paragraph("<b>📊 Multi-Model Real-Time Accounting</b>", styles['Normal']),
            Paragraph("Calculates instant token savings and projected dollar savings simultaneously across Claude 3.5 Sonnet, Claude Opus, GPT-4o, Gemini 1.5 Pro, and DeepSeek V3.", body_style)
        ]
    ]
    t_pillars = Table(pillars_data, colWidths=[160, 344])
    t_pillars.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_pillars)

    story.append(PageBreak())

    # ================= PAGE 3: 90-SECOND DEMO PLAYBOOK =================
    story.append(Paragraph("3. The 90-Second Live Demo Playbook", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY, spaceBefore=0, spaceAfter=14))

    demo_intro = """Judges judge what they <b>see</b>, not what you describe. Practice this exact 90-second sequence. 
    Have Claude.ai or ChatGPT open in a browser tab before you step up."""
    story.append(Paragraph(demo_intro, body_style))
    story.append(Spacer(1, 8))

    demo_steps = [
        ("0:00 – 0:10", "1. Set the Stage & Show In-Page Controls",
         "Point to the Squeeze toolbar cleanly docked inside Claude / ChatGPT.",
         "\"Squeeze AI is a Chrome extension living directly in my browser. Notice the Squeeze controls seamlessly integrated right below the chat input.\""),
        
        ("0:10 – 0:25", "2. Paste the 'Trap' Prompt (Bloated + Secret)",
         "Paste the pre-copied bloated prompt with credentials: <br/>"
         "<i>'Hi Claude, I hope you are having a wonderful day! Could you please help me write a Python script connecting to MongoDB using MONGO_URI=mongodb://admin:superSecretPassword99@cluster.prod.com/db. Thank you in advance!'</i>",
         "\"Here's a prompt typical developers write: greetings, polite padding, and — critically — a live database password accidentally pasted in.\""),
        
        ("0:25 – 0:45", "3. Hit Squeeze (Ctrl+Shift+S) & Show the Magic",
         "Press <b>Ctrl+Shift+S</b> or click the Squeeze button. The modal opens with green glow and live diff.",
         "\"Watch this: in under 50 milliseconds, Squeeze did two critical things. First, look at the green banner: our DLP Shield detected the MongoDB URI and masked the credentials locally before network transmission. Second, the diff view shows 42% token reduction — all polite fluff stripped while strictly preserving code and technical requirements.\""),
        
        ("0:45 – 1:05", "4. One-Click Apply & Immediate Undo Safety",
         "Click <b>Apply & Squeeze</b>. Show the clean text inject into the input. Point to the green box-shadow flash and the Undo button.",
         "\"One click, and the optimized prompt is injected into the chat. If I ever want the original back, this Undo button restores it immediately. Complete user control.\""),
        
        ("1:05 – 1:25", "5. Launch the Squeeze Studio Side Panel & AST Tool",
         "Click the orange Squeeze banner to open the Side Panel. Show the Multi-Model Cost Savings card and the AST code skeletonizer.",
         "\"Let's open the Squeeze Studio side panel. Here we see live cost savings calculated across Claude Opus, GPT-4o, and Gemini. And for codebases, our AST skeletonizer compresses 2,400-token files down to 380 tokens while preserving imports and type signatures.\""),
        
        ("1:25 – 1:30", "6. The Power Close",
         "Look directly at the lead judge and deliver the punchline.",
         "\"Squeeze AI: zero latency, 100% private, cutting token costs across every major AI platform. Thank you!\"")
    ]

    demo_table_rows = []
    for time_code, step_title, what_to_do, what_to_say in demo_steps:
        content = f"<b>{step_title}</b><br/>" \
                  f"<font color='#475569'>{what_to_do}</font><br/>" \
                  f"<font color='#FF6D00'><b>Say:</b></font> <i>{what_to_say}</i>"
        demo_table_rows.append([
            Paragraph(f"<b><font color='#FF6D00'>{time_code}</font></b>", styles['Normal']),
            Paragraph(content, body_style)
        ])

    t_demo = Table(demo_table_rows, colWidths=[80, 424])
    t_demo.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#FFF7ED")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_demo)

    story.append(PageBreak())

    # ================= PAGE 4: 2-MINUTE VERBATIM PITCH SCRIPT =================
    story.append(Paragraph("4. The 2-Minute Pitch Script", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY, spaceBefore=0, spaceAfter=14))

    pitch_intro = """Deliver this speech word-for-word if you have a 2-minute stage slot. 
    Notes in brackets <b>[like this]</b> are stage directions for physical movement and pauses."""
    story.append(Paragraph(pitch_intro, body_style))
    story.append(Spacer(1, 8))

    pitch_sections = [
        ("THE HOOK (0:00 – 0:20)", 
         "\"Raise your hand if you use Claude, ChatGPT, or Cursor daily. [Wait 2 seconds, look at judges]. "
         "Now keep your hand up if you've ever pasted an API key, database URL, or sensitive snippet into that chat. [Pause]. "
         "Cyberhaven reported that over 80% of developers have done exactly that. That secret just crossed the public internet. "
         "And every extra character in that prompt cost you real money. We built Squeeze AI to solve credential leaks and context bloat right at the keystroke level.\""),
        
        ("THE PROBLEM (0:20 – 0:45)", 
         "\"Every foundation model bills by input token. But prompts are written in conversational prose — padded with greetings, "
         "apologies, repeated instructions, and copy-pasted blocks already present in earlier turns. Up to 40% of tokens in conversational "
         "prompts are pure financial waste. For an engineering team running hundreds of daily prompts on Claude 3.5 Sonnet or GPT-4o, "
         "that adds up to thousands of dollars wasted every single month.\""),
        
        ("THE SOLUTION & LIVE PROOF (0:45 – 1:15)", 
         "\"Squeeze AI is a fast, local developer shield that sits directly between your keystrokes and the AI — across Chrome, Cursor, and Claude Code. "
         "With one shortcut — Ctrl+Shift+S — our local engine strips conversational bloat while strictly preserving code blocks and technical constraints. "
         "Simultaneously, our DLP Secret Shield scans for 8 major credential types — from OpenAI and AWS keys to database passwords — redacting them in memory before network egress. "
         "And for codebases, our AST skeletonizer compresses 2,400-token files down to 380 tokens while preserving imports, class signatures, and types. "
         "100% offline. Zero server latency. Not a single byte leaves your machine.\""),
        
        ("PREFIX INVARIANCE & ARCHITECTURE (1:15 – 1:40)", 
         "\"Now, here is the key technical nuance: in the browser, Squeeze enforces Prefix Invariance — keeping repeated persona instructions byte-identical turn after turn so platform KV-caches hit. "
         "In our MCP server for Cursor and Claude Code, we directly structure breakpoints. We don't claim to control Anthropic's backend from a browser DOM — we set up the mathematical preconditions. "
         "Across our benchmarks, technical constraint retention averages 96% while reducing token volume by up to 70%.\""),
        
        ("THE MOAT & CLOSE (1:40 – 2:00)", 
         "\"Judges often ask: why won't OpenAI or Anthropic just ship a compress button? They could ship compression, but compression isn't the product — cross-platform workflow portability is. "
         "Context Vault, unified rules across Claude, ChatGPT, Gemini, Cursor, and Claude Code, and an MCP server that follows you into your IDE are parts no single provider will build, "
         "because neither OpenAI nor Anthropic will build a context layer that travels to their competitors. Squeeze AI is the independent context layer for developers. Thank you! [Smile, open floor for questions].\"")
    ]

    pitch_cards = []
    for heading, speech in pitch_sections:
        pitch_cards.append([
            Paragraph(f"<b><font color='#FF6D00'>{heading}</font></b>", h2_style)
        ])
        pitch_cards.append([
            Paragraph(speech, say_style)
        ])
    t_pitch = Table(pitch_cards, colWidths=[504])
    t_pitch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, COLOR_BORDER),
        ('LINELEFT', (0,0), (-1,-1), 3, COLOR_PRIMARY),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_pitch)

    story.append(PageBreak())

    # ================= PAGE 5: JUDGE Q&A BATTLECARD =================
    story.append(Paragraph("5. The Judge Q&A Battlecard", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY, spaceBefore=0, spaceAfter=14))

    qa_list = [
        ("Does aggressive token squeezing degrade the quality or reasoning ability of LLM answers?",
         "We evaluate this through constraint retention: our algorithm strips non-functional conversational padding while strictly isolating code blocks, parameters, and nouns. In 50 benchmark tasks, response accuracy was preserved in 96% of cases because eliminating noise sharpens attention weights on actual instructions."),

        ("Regex-based DLP claiming '100% detection' is dangerous. What is your false negative rate on custom or entropy secrets?",
         "Fair and critical callout: regex is a signature-based defense-in-depth layer targeting the 8 most prevalent structured public leak formats (AWS, OpenAI, GitHub, JWT, DB URIs). It does not catch high-entropy custom strings — that is on our roadmap for local Shannon entropy analysis. But catching known signatures before network dispatch eliminates over 80% of accidental developer leaks, with zero outbound network calls."),

        ("You edit a browser textarea — you don't control Anthropic's API cache headers. How do you actually influence caching?",
         "You're right to press on this. In the browser-extension context, Squeeze optimizes Prefix Invariance: keeping repeated user persona instructions and codebase context byte-identical turn after turn, which is the required precondition for any provider-side KV-cache hit. On our MCP server path for Cursor and Claude Code, we directly structure cache blocks. We don't claim to control platform backends from a browser DOM."),

        ("If this works, why wouldn't Anthropic or OpenAI just ship a 'compress' toggle in their own UI next quarter?",
         "They could ship compression — but compression isn't the product, cross-platform portability is. Context Vault, unified rules across Claude, ChatGPT, Gemini, Cursor, and Claude Code, and an MCP server that follows you into your IDE are parts no single foundation provider will build, because neither OpenAI nor Anthropic is incentivized to make your context portable across their competitors."),

        ("How does Squeeze AI guarantee user privacy? Could Squeeze steal our prompts?",
         "We are 100% local. The entire optimization and DLP engine runs in Chrome's local background service worker and content script. Inspect our manifest.json: there is no external backend URL, no telemetry endpoint, and zero outbound network calls. Prompts never leave the local browser memory.")
    ]

    qa_rows = []
    for q, a in qa_list:
        qa_rows.append([
            Paragraph(f"<b><font color='#FF6D00'>Q: {q}</font></b>", h2_style),
        ])
        qa_rows.append([
            Paragraph(f"<b>A:</b> {a}", body_style)
        ])

    t_qa = Table(qa_rows, colWidths=[504])
    t_qa.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, COLOR_BORDER),
        ('LINELEFT', (0,0), (-1,-1), 3, COLOR_ACCENT_BLUE),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_qa)

    story.append(PageBreak())

    # ================= PAGE 6: COMPETITIVE MATRIX & ARCHITECTURE =================
    story.append(Paragraph("6. Competitive Matrix & Technical Architecture", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY, spaceBefore=0, spaceAfter=14))

    matrix_headers = ["Capability", "Squeeze AI", "Prompt Optimizer GPTs", "LangChain TokenSplitter", "Manual Editing"]
    matrix_data = [
        [Paragraph(f"<b>{h}</b>", styles['Normal']) for h in matrix_headers],
        [Paragraph("Works in Browser UI", body_style), Paragraph("<font color='#10B981'><b>YES (Claude, GPT, Gemini)</b></font>", body_style), Paragraph("<font color='#EF4444'>No (ChatGPT only)</font>", body_style), Paragraph("<font color='#EF4444'>No (Code SDK only)</font>", body_style), Paragraph("Yes (Tedious)", body_style)],
        [Paragraph("DLP Credential Masking", body_style), Paragraph("<font color='#10B981'><b>YES (8 Secret Types)</b></font>", body_style), Paragraph("<font color='#EF4444'>No</font>", body_style), Paragraph("<font color='#EF4444'>No</font>", body_style), Paragraph("<font color='#EF4444'>No (High Human Error)</font>", body_style)],
        [Paragraph("100% Offline / Local", body_style), Paragraph("<font color='#10B981'><b>YES (0ms Network)</b></font>", body_style), Paragraph("<font color='#EF4444'>No (Uses Cloud API)</font>", body_style), Paragraph("<font color='#F59E0B'>Partial (Self-hosted)</font>", body_style), Paragraph("Yes", body_style)],
        [Paragraph("Live Word Diff Preview", body_style), Paragraph("<font color='#10B981'><b>YES (LCS + Line Diff)</b></font>", body_style), Paragraph("<font color='#EF4444'>No</font>", body_style), Paragraph("<font color='#EF4444'>No</font>", body_style), Paragraph("<font color='#EF4444'>No</font>", body_style)],
        [Paragraph("Smart Context Vault", body_style), Paragraph("<font color='#10B981'><b>YES (Auto Keyword Attach)</b></font>", body_style), Paragraph("<font color='#EF4444'>No</font>", body_style), Paragraph("<font color='#EF4444'>No</font>", body_style), Paragraph("<font color='#EF4444'>No</font>", body_style)],
        [Paragraph("Pricing", body_style), Paragraph("<font color='#10B981'><b>Free / Open Ext</b></font>", body_style), Paragraph("Requires ChatGPT Plus", body_style), Paragraph("Open Source Library", body_style), Paragraph("Free (High Time Cost)", body_style)]
    ]
    t_matrix = Table(matrix_data, colWidths=[134, 110, 95, 95, 70])
    t_matrix.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0A0A0F")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOX', (0,0), (-1,-1), 1, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, COLOR_BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_matrix)

    story.append(Spacer(1, 14))
    story.append(Paragraph("<b>Under the Hood: Technical Highlights</b>", h2_style))
    arch_bullets = [
        "• <b>Universal DOM Platform Adapter:</b> Injects seamlessly into Claude contenteditable divs, ChatGPT rich-textareas with React synthetic event triggering, and Gemini shadow DOM boundaries.",
        "• <b>Guarded LCS Diffing with O(m×n) Fallback:</b> Computes character-precise token diffs up to 500 words and automatically shifts to line diffing for multi-page documents to maintain a constant 60 FPS UI.",
        "• <b>Stateful Regex Protection:</b> Fixes global regex lastIndex pointer resets across all 8 DLP scanners, enforcing atomic pointer resets across all known public credential vectors.",
        "• <b>Leading + Trailing Debounce:</b> Handles asynchronous single-page app (SPA) DOM mutations, guaranteeing widgets remain mounted even during high-frequency AI streaming output."
    ]
    for b in arch_bullets:
        story.append(Paragraph(b, body_style))

    story.append(PageBreak())

    # ================= PAGE 7: STAGE PRESENCE & PRE-FLIGHT CHECKLIST =================
    story.append(Paragraph("7. Stage Presence & Pre-Flight Checklist", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY, spaceBefore=0, spaceAfter=14))

    tips_data = [
        [
            Paragraph("<b>✅ DO (Winning Habits)</b>", h2_style),
            Paragraph("<b>❌ DON'T (Disqualifying Mistakes)</b>", h2_style)
        ],
        [
            Paragraph("• <b>Start with the hand-raise hook:</b> It immediately establishes empathy and personal relevance.<br/>"
                      "• <b>Use the Ctrl+Shift+S shortcut:</b> Keyboard shortcuts demonstrate developer speed and craftsmanship.<br/>"
                      "• <b>Point out the green DLP banner:</b> This is your highest-impact visual 'hero moment'.<br/>"
                      "• <b>Emphasize '100% Local':</b> Mention offline security twice — judges care deeply about data privacy.<br/>"
                      "• <b>Pause after key numbers:</b> Let '$27/month saved per dev' breathe before moving to the next sentence.", body_style),
            Paragraph("• <b>Don't type live during the demo:</b> Typos break your rhythm. Keep the test prompt on your clipboard.<br/>"
                      "• <b>Don't rely on live AI output:</b> If Claude is slow, your demo stalls. Focus on the Squeeze modal diff.<br/>"
                      "• <b>Don't say 'It's just an extension':</b> Position it as an 'AI middleware layer' on the client.<br/>"
                      "• <b>Don't apologize for missing features:</b> Focus entirely on what is working and polished right now.<br/>"
                      "• <b>Don't run over time:</b> Finish 15 seconds early to guarantee full judge interaction.", body_style)
        ]
    ]
    t_tips = Table(tips_data, colWidths=[246, 246])
    t_tips.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 1, COLOR_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_tips)

    story.append(Spacer(1, 14))
    story.append(Paragraph("<b>10-Minute Pre-Flight Checklist Before You Pitch:</b>", h2_style))
    checklist_items = [
        "<b>[ ] Browser Ready:</b> Open Claude.ai and ChatGPT in dedicated Chrome tabs. Ensure dark mode is active.",
        "<b>[ ] Extension Verified:</b> Confirm the Squeeze toolbar icon appears below the chat input box.",
        "<b>[ ] Clipboard Primed:</b> Copy the demo prompt with the MongoDB URI into your clipboard right before going on stage.",
        "<b>[ ] Side Panel Tested:</b> Click the Side Panel button once to ensure Chrome has initialized the side panel API.",
        "<b>[ ] Notifications Muted:</b> Turn on 'Do Not Disturb' on your Mac to prevent embarrassing message popups during screen share.",
        "<b>[ ] Display Scaling:</b> Set browser zoom to 110%–125% so judges in the back row can read the token diff numbers effortlessly."
    ]
    for c in checklist_items:
        story.append(Paragraph(c, body_style))

    story.append(Spacer(1, 15))
    closing_banner = Table([[
        Paragraph("<font color='#FFFFFF'><b>🚀 YOU HAVE BUILT A POLISHED, FUNCTIONAL, VALUE-PACKED PRODUCT. "
                  "PRESENT WITH CONFIDENCE, OWN THE ROOM, AND WIN THIS HACKATHON!</b></font>", styles['Normal'])
    ]], colWidths=[504])
    closing_banner.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_PRIMARY),
        ('BOX', (0,0), (-1,-1), 1, COLOR_PRIMARY),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 14),
        ('RIGHTPADDING', (0,0), (-1,-1), 14),
    ]))
    story.append(closing_banner)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"✅ Successfully compiled {filename}")

if __name__ == "__main__":
    build_pdf()
