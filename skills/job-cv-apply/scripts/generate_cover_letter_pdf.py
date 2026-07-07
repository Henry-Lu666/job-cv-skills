#!/usr/bin/env python3
"""
Cover Letter PDF Generator — for job-cv-apply skill.

⚠️ **DEPRECATED — 2026-07-06.**
用户要求只出docx，不出PDF。agent转的PDF格式不准确，用户亲自用WPS转换。
保留此脚本仅用于历史参考，不再在求职流程中调用。

Usage:
  python3 scripts/generate_cover_letter_pdf.py --output path/to/output.pdf

Edit the BODY_PARAGRAPHS list to customize the cover letter content.
Requires: fpdf2 (pip install fpdf2)

Design:
  - Unicode font (DejaVu Sans) supports Chinese, em dash, special chars
  - Professional business letter layout
  - 2 pages max for typical content
"""

import os, sys, argparse
from fpdf import FPDF

# ── CONFIGURE THESE ──────────────────────────────────────────────

SENDER = {
    "name":     "Hong ZHANGXIU (Henry Lu)",
    "email":    "256360203@student.chuhai.edu.hk",
    "phone":    "[To be filled]",
    "github":   "github.com/Henry-Lu666",
    "linkedin": "[To be filled]",
}

RECIPIENT = {
    "dept":  "Human Resource Management Department",
    "org":   "MTR Corporation",
    "addr1": "G.P.O. Box 9916",
    "addr2": "Hong Kong",
}

DATE = "7 July 2026"
SUBJECT = "Re: Senior Manager-AI & Digitalisation (AI & Data Architecture) (Ref: 250000Z1)"

BODY_PARAGRAPHS = [
    "Dear Hiring Manager,",

    "I am writing to apply for the position at MTR Corporation. With 12 years of "
    "progressive management experience at a major state-owned enterprise and a recently "
    "completed MSc in Applied AI, I offer a rare combination of enterprise-level "
    "transformation leadership and hands-on AI capability.",

    "During my 12-year tenure at a leading automotive SOE with over 20,000 employees, "
    "I led cross-regional teams of 50+ staff, drove process standardisation initiatives, "
    "and orchestrated multi-stakeholder transformation programmes. This experience has "
    "equipped me to develop and execute strategic roadmaps, engage senior stakeholders, "
    "manage resources, and bridge the gap between technical delivery and business "
    "objectives.",

    "On the technical side, I recently completed my MSc in Applied AI (Chuhai College, "
    "HK), with a thesis delivering a RoBERTa-based dual-task ABSA model (F1=0.6705). "
    "I have built production-oriented AI systems including a RAG-based audit tool "
    "(Flask + ChromaDB + local LLM) and developed a Stage 0-5 SOP methodology for "
    "phased enterprise AI rollouts.",

    "I would welcome the opportunity to discuss how my enterprise transformation "
    "experience and AI expertise can contribute to your organisation's digitalisation "
    "journey. Thank you for considering my application.",

    "Yours faithfully,",
]

SIGNATURE_NAME = "Hong ZHANGXIU (Henry Lu)"

# ── END CONFIG ────────────────────────────────────────────────────


class CoverLetterPDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')


def build_pdf(output_path):
    pdf = CoverLetterPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.add_page()

    # Unicode font
    font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    font_bold = font_path.replace('Sans.ttf', 'Sans-Bold.ttf')
    if not os.path.exists(font_path):
        # Fallback to Helvetica (Latin-1 only)
        FONT = 'Helvetica'
        FONT_BOLD = 'Helvetica'
        FONT_UNICODE = False
    else:
        pdf.add_font('DejaVu', '', font_path)
        pdf.add_font('DejaVu', 'B', font_bold)
        FONT = 'DejaVu'
        FONT_BOLD = 'DejaVu'
        FONT_UNICODE = True

    NL = {"new_x": "LMARGIN", "new_y": "NEXT"}

    # ── Sender block ──
    pdf.set_font(FONT_BOLD, '', 15)
    pdf.cell(0, 8, SENDER["name"], **NL)

    pdf.set_font(FONT, '', 10)
    for line in [f"Email: {SENDER['email']}",
                 f"Phone: {SENDER['phone']}",
                 f"GitHub: {SENDER['github']}",
                 f"LinkedIn: {SENDER['linkedin']}"]:
        pdf.cell(0, 5, line, **NL)
    pdf.ln(8)

    # ── Date ──
    pdf.set_font(FONT, '', 11)
    pdf.cell(0, 6, DATE, **NL)
    pdf.ln(5)

    # ── Recipient ──
    pdf.cell(0, 6, RECIPIENT["dept"], **NL)
    pdf.cell(0, 6, RECIPIENT["org"], **NL)
    pdf.cell(0, 6, RECIPIENT["addr1"], **NL)
    pdf.cell(0, 6, RECIPIENT["addr2"], **NL)
    pdf.ln(6)

    # ── Subject ──
    pdf.set_font(FONT_BOLD, '', 11)
    pdf.cell(0, 6, SUBJECT, **NL)
    pdf.ln(6)

    # ── Body ──
    pdf.set_font(FONT, '', 11)
    for para in BODY_PARAGRAPHS:
        pdf.multi_cell(0, 6, para)
        pdf.ln(3)

    # ── Signature ──
    pdf.set_font(FONT_BOLD, '', 12)
    pdf.cell(0, 6, SIGNATURE_NAME, **NL)

    # ── Output ──
    pdf.output(output_path)
    return pdf.pages_count


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate cover letter PDF')
    parser.add_argument('--output', '-o', default='./cover_letter.pdf',
                        help='Output PDF path')
    args = parser.parse_args()

    out_dir = os.path.dirname(args.output) or '.'
    os.makedirs(out_dir, exist_ok=True)

    pages = build_pdf(args.output)
    print(f"PDF saved: {args.output}  ({os.path.getsize(args.output)} bytes, {pages} pages)")
