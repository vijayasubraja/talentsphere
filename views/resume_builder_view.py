"""Dedicated Resume Builder view for TalentSphere platform.

Features:
- WCAG AA compliant dark theme (#111111 main bg, #1C1C22 cards, #191919 inputs, #FFFFFF text, #E0E0EA labels, #7965D8 primary actions).
- Step A: Template Selection Gallery with realistic previews, search, ATS filter, category chips, and 'Confirm & Proceed'.
- Step B: Two-panel Resume Editor with live real-time preview, collapsible sections in exact required order:
    1. Personal Details (Job title, First/Last name, Email, Phone, City, Country, template photo support/notice)
    2. Professional Summary (large textarea, character counter, AI polish assistant)
    3. Projects (Name, Org, Link, Start/End date, Ongoing checkbox, Description, Add/Edit/Duplicate/Delete)
    4. Work Experience and Internships (Title, Company, Type, Location, Dates, Current checkbox, Description, Add/Duplicate/Delete)
    5. Education (Degree, Institution, Field of Study, Location, Dates, Current checkbox, GPA, Description, Add/Duplicate/Delete)
    6. Technical and Professional Skills (Aligned single-row input, 5 circular proficiency indicators with colors, Add/Duplicate/Delete)
    7. Custom Sections (Categories: Certifications, Achievements, References, Others, Include/Exclude toggle)
    8. Certifications (Add Certification form: Name, Issuer, Issue/Expiry date, Does Not Expire checkbox, Credential ID/URL, Certificate upload with validation/isolation, Supporting-doc text only on resume)
    9. Achievements (Title, Org/Context, Date, Description, Add/Edit/Delete, auto-expand)
    10. References (Name, Title, Org, Contact, Notes, Privacy toggle, Add/Edit/Delete, auto-expand)
- Multi-page capable ReportLab PDF generation with selectable text and authentic template styling.
- Safe SQLite profile integration with per-user data isolation.
- Document ingestion (.pdf, .docx) and ATS keyword matching capabilities.
All HTML is rendered via render_html (st.html) with zero code leakage and high-contrast readability.
"""

from __future__ import annotations
import copy
import io
import json
from pathlib import Path
import re
import time
from typing import Any
import uuid
import streamlit as st
import services.core
from components.cards import (
    render_html,
    render_section_header,
    render_badge,
    render_progress_bar,
    render_demo_banner,
)

# Optional import utilities with graceful fallback
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from docx import Document
except ImportError:
    Document = None

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
except ImportError:
    canvas = None

CERTIFICATES_BASE_DIR = Path(__file__).parent.parent / "data" / "certificates"

# Exact 5 proficiency levels and color definitions
PROFICIENCY_LEVELS = [
    {"level": "Beginner", "color": "#60A5FA", "step": 1},      # Blue
    {"level": "Skillful", "color": "#2DD4BF", "step": 2},      # Teal
    {"level": "Experienced", "color": "#22C55E", "step": 3},   # Green
    {"level": "Advanced", "color": "#A78BFA", "step": 4},      # Purple
    {"level": "Expert", "color": "#FBBF24", "step": 5},        # Amber
]


# =============================================================================
# SECURE CERTIFICATE STORAGE & VALIDATION
# =============================================================================
def save_certificate_file(user_id: int, uploaded_file) -> tuple[bool, str, dict[str, Any]]:
    """Validates and securely stores an uploaded certificate file.

    Accepts PDF, JPG, JPEG, PNG. Max 5MB size limit.
    Stores files strictly inside data/certificates/user_{user_id}/ to ensure per-user isolation.
    Returns (success_bool, message, file_metadata_dict).
    """
    if not uploaded_file:
        return False, "No file provided for upload.", {}

    max_bytes = 5 * 1024 * 1024
    if uploaded_file.size > max_bytes:
        mb = round(uploaded_file.size / (1024 * 1024), 1)
        return False, f"File size ({mb} MB) exceeds the 5 MB limit. Please select a smaller file.", {}

    fname = uploaded_file.name
    ext = Path(fname).suffix.lower()
    if ext not in [".pdf", ".jpg", ".jpeg", ".png"]:
        return False, f"Unsupported file type '{ext}'. Please upload a PDF, JPG, JPEG, or PNG certificate.", {}

    try:
        user_dir = CERTIFICATES_BASE_DIR / f"user_{user_id}"
        user_dir.mkdir(parents=True, exist_ok=True)

        safe_base = re.sub(r"[^a-zA-Z0-9_\.-]", "_", Path(fname).stem)
        safe_fname = f"{safe_base}_{uuid.uuid4().hex[:6]}{ext}"
        target_path = user_dir / safe_fname

        target_path.write_bytes(uploaded_file.getvalue())

        meta = {
            "original_filename": fname,
            "saved_filename": safe_fname,
            "file_type": ext.lstrip(".").upper(),
            "file_size": uploaded_file.size,
            "relative_path": f"certificates/user_{user_id}/{safe_fname}",
        }
        return True, f"Certificate '{fname}' uploaded successfully.", meta
    except Exception as exc:
        return False, f"Unable to save certificate file: {exc}", {}


def delete_certificate_file(user_id: int, saved_filename: str) -> bool:
    """Safely deletes an uploaded certificate file, enforcing user isolation."""
    if not saved_filename:
        return False
    try:
        user_dir = (CERTIFICATES_BASE_DIR / f"user_{user_id}").resolve()
        target_path = (user_dir / saved_filename).resolve()
        # Ensure path does not escape user directory
        try:
            target_path.relative_to(user_dir)
            is_sub = True
        except ValueError:
            is_sub = False

        if is_sub and target_path.exists():
            for _ in range(5):
                try:
                    target_path.unlink()
                    return True
                except (PermissionError, OSError):
                    time.sleep(0.05)
    except Exception:
        pass
    return False


# =============================================================================
# TEMPLATE DEFINITIONS & METADATA
# =============================================================================
TEMPLATES = [
    {
        "id": "puffin",
        "name": "Puffin",
        "subtitle": "Modern Professional",
        "description": "Thoughtfully designed two-column layout with bold boxed section titles, highlighting technical projects and credentials in a visually appealing way.",
        "categories": ["Engineer", "Senior", "Data", "Product Manager"],
        "ats_friendly": True,
        "supports_photo": False,
        "users_count": "114,923",
        "layout": "two_column",
        "primary_color": "#0F172A",
        "accent_color": "#7965D8",
    },
    {
        "id": "caddisfly",
        "name": "Caddisfly",
        "subtitle": "Clean ATS-Friendly",
        "description": "Professional single-column table-format design engineered for clear and efficient information flow. 100% compliant with standard Applicant Tracking Systems.",
        "categories": ["Fresher", "Engineer", "Data", "Sales"],
        "ats_friendly": True,
        "supports_photo": False,
        "users_count": "26,080",
        "layout": "single_column_table",
        "primary_color": "#1E293B",
        "accent_color": "#2563EB",
    },
    {
        "id": "sahani",
        "name": "Sahani",
        "subtitle": "Structured Two-Column",
        "description": "Clean modern layout that keeps information easy to read and professionally arranged with prominent colored accent headers and optional profile photo support.",
        "categories": ["Designer", "Data", "Product Manager", "Marketing"],
        "ats_friendly": True,
        "supports_photo": True,
        "users_count": "8,297",
        "layout": "two_column_banner",
        "primary_color": "#0B2545",
        "accent_color": "#7965D8",
    },
    {
        "id": "mayfly",
        "name": "Mayfly",
        "subtitle": "Executive Minimalist",
        "description": "A structured resume template designed for clear and organized presentation, featuring timeline dates and refined modern typography.",
        "categories": ["Senior", "Marketing", "Sales", "Fresher"],
        "ats_friendly": True,
        "supports_photo": False,
        "users_count": "12,789",
        "layout": "timeline",
        "primary_color": "#334155",
        "accent_color": "#64748B",
    },
]


# =============================================================================
# REPORTLAB PDF GENERATION ENGINE
# =============================================================================
def _wrap_text_lines(text: str, max_chars: int) -> list[str]:
    """Wraps text into a list of lines respecting word boundaries."""
    if not text:
        return []
    lines = []
    for raw_line in str(text).splitlines():
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        words = raw_line.split()
        cur_line: list[str] = []
        cur_len = 0
        for w in words:
            if cur_len + len(w) + 1 > max_chars:
                if cur_line:
                    lines.append(" ".join(cur_line))
                cur_line = [w]
                cur_len = len(w)
            else:
                cur_line.append(w)
                cur_len += len(w) + 1
        if cur_line:
            lines.append(" ".join(cur_line))
    return lines


def generate_resume_pdf(resume_data: dict[str, Any], template_id: str = "puffin") -> bytes:
    """Generates a multi-page, ATS-compliant PDF resume using ReportLab.

    Matches selected template aesthetics with selectable text, robust pagination,
    and text-only certification credentials (never embedding raw certificate files).
    """
    if canvas is None:
        return b"%PDF-1.4 Mock fallback PDF content"

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter

    margin_x = 36
    margin_top = 36
    margin_bottom = 36
    page_num = 1

    def draw_footer():
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.HexColor("#64748B"))
        c.drawCentredString(width / 2.0, 20, f"Page {page_num}")
        c.setFillColor(colors.black)

    # Extract clean resume fields
    first_name = resume_data.get("first_name", "").strip()
    last_name = resume_data.get("last_name", "").strip()
    full_name = f"{first_name} {last_name}".strip() or "Employee"
    job_title = resume_data.get("job_title", "").strip()
    email = resume_data.get("email", "").strip()
    phone = resume_data.get("phone", "").strip()
    city = resume_data.get("city", "").strip()
    country = resume_data.get("country", "").strip()
    location = resume_data.get("location", "").strip()
    if not location and (city or country):
        location = f"{city}, {country}".strip(", ")
    linkedin = resume_data.get("linkedin", "").strip()
    portfolio = resume_data.get("portfolio", "").strip()
    summary = resume_data.get("summary", "").strip()
    show_prof = resume_data.get("show_skill_proficiency", True)

    projects = resume_data.get("projects", [])
    if isinstance(projects, str):
        projects = services.core.parse_json_field(projects)
    experiences = resume_data.get("experience", [])
    if isinstance(experiences, str):
        experiences = services.core.parse_json_field(experiences)
    educations = resume_data.get("education", [])
    if isinstance(educations, str):
        educations = services.core.parse_json_field(educations)
    skills = resume_data.get("skills", [])
    if isinstance(skills, str):
        skills = services.core.parse_json_field(skills)
    certifications = resume_data.get("certifications", [])
    if isinstance(certifications, str):
        certifications = services.core.parse_json_field(certifications)
    achievements = resume_data.get("achievements", [])
    if isinstance(achievements, str):
        achievements = services.core.parse_json_field(achievements)
    references = resume_data.get("references", [])
    if isinstance(references, str):
        references = services.core.parse_json_field(references)
    custom_sections = resume_data.get("custom_sections", [])
    if isinstance(custom_sections, str):
        custom_sections = services.core.parse_json_field(custom_sections)
    languages = resume_data.get("languages", [])
    if isinstance(languages, str):
        languages = services.core.parse_json_field(languages)

    # -------------------------------------------------------------------------
    # TEMPLATE 1: PUFFIN (Modern Professional 2-Column with Boxed Headers)
    # -------------------------------------------------------------------------
    if template_id == "puffin":
        y = height - margin_top

        # Top Header (Full Width)
        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(colors.HexColor("#0F172A"))
        c.drawCentredString(width / 2.0, y, full_name.upper())
        y -= 16

        if job_title:
            c.setFont("Helvetica-Bold", 10.5)
            c.setFillColor(colors.HexColor("#7965D8"))
            c.drawCentredString(width / 2.0, y, f"— {job_title.upper()} —")
            y -= 14

        if summary:
            c.setFont("Helvetica", 8.5)
            c.setFillColor(colors.HexColor("#334155"))
            sum_lines = _wrap_text_lines(summary, 105)
            for sl in sum_lines[:4]:
                c.drawCentredString(width / 2.0, y, sl)
                y -= 11
            y -= 4

        c.setStrokeColor(colors.HexColor("#0F172A"))
        c.setLineWidth(1)
        c.line(margin_x, y, width - margin_x, y)
        y -= 14

        left_x = margin_x
        left_w = 345
        right_x = margin_x + left_w + 14
        right_w = width - right_x - margin_x

        y_left = y
        y_right = y

        def check_left_break(space: int = 40):
            nonlocal y_left, y_right, page_num
            if y_left - space < margin_bottom + 15:
                draw_footer()
                c.showPage()
                page_num += 1
                y_left = height - margin_top
                y_right = height - margin_top

        def check_right_break(space: int = 40):
            nonlocal y_left, y_right, page_num
            if y_right - space < margin_bottom + 15:
                draw_footer()
                c.showPage()
                page_num += 1
                y_left = height - margin_top
                y_right = height - margin_top

        def draw_boxed_header(title: str, col_x: float, col_w: float, is_left: bool):
            nonlocal y_left, y_right
            target_y = y_left if is_left else y_right
            box_h = 16
            c.setStrokeColor(colors.HexColor("#0F172A"))
            c.setLineWidth(1.2)
            c.rect(col_x, target_y - box_h, col_w, box_h, stroke=1, fill=0)
            c.setFont("Helvetica-Bold", 9)
            c.setFillColor(colors.HexColor("#0F172A"))
            c.drawCentredString(col_x + (col_w / 2.0), target_y - box_h + 4.5, title.upper())
            if is_left:
                y_left -= (box_h + 10)
            else:
                y_right -= (box_h + 10)

        # 1. RIGHT COLUMN: Contact, Education, Skills, References, Languages
        draw_boxed_header("CONTACT", right_x, right_w, is_left=False)
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.HexColor("#1E293B"))
        contact_items = []
        if phone: contact_items.append(f"Phone: {phone}")
        if location: contact_items.append(f"Location: {location}")
        if email: contact_items.append(f"Email: {email}")
        if linkedin: contact_items.append(f"LinkedIn: {linkedin.replace('https://', '')}")
        if portfolio: contact_items.append(f"Web: {portfolio.replace('https://', '')}")

        for ci in contact_items:
            check_right_break(15)
            for chunk in _wrap_text_lines(ci, 30):
                c.drawString(right_x + 4, y_right, chunk)
                y_right -= 11
        y_right -= 8

        if educations:
            check_right_break(35)
            draw_boxed_header("EDUCATION", right_x, right_w, is_left=False)
            for edu in educations:
                if isinstance(edu, dict):
                    check_right_break(35)
                    deg = edu.get("degree") or edu.get("qualification") or "Degree"
                    inst = edu.get("institution") or ""
                    period = edu.get("period") or f"{edu.get('start_date', '')} - {edu.get('end_date', '')}".strip(" -")
                    honors = edu.get("academic_info") or edu.get("honors") or ""

                    if period:
                        c.setFont("Helvetica", 7.5)
                        c.setFillColor(colors.HexColor("#64748B"))
                        c.drawString(right_x + 4, y_right, period)
                        y_right -= 10

                    c.setFont("Helvetica-Bold", 8.5)
                    c.setFillColor(colors.HexColor("#0F172A"))
                    for line in _wrap_text_lines(inst, 28):
                        c.drawString(right_x + 4, y_right, line)
                        y_right -= 10

                    c.setFont("Helvetica", 8)
                    c.setFillColor(colors.HexColor("#334155"))
                    for line in _wrap_text_lines(deg, 28):
                        c.drawString(right_x + 4, y_right, line)
                        y_right -= 10

                    if honors:
                        c.setFont("Helvetica-Oblique", 7.5)
                        c.setFillColor(colors.HexColor("#7965D8"))
                        for line in _wrap_text_lines(honors, 28):
                            c.drawString(right_x + 4, y_right, line)
                            y_right -= 9
                    y_right -= 5
            y_right -= 4

        if skills:
            check_right_break(35)
            draw_boxed_header("SKILLS", right_x, right_w, is_left=False)
            c.setFont("Helvetica", 8)
            c.setFillColor(colors.HexColor("#1E293B"))
            for s in skills:
                check_right_break(15)
                s_name = s.get("name") if isinstance(s, dict) else str(s)
                s_prof = s.get("proficiency", "") if isinstance(s, dict) and show_prof else ""
                disp_sk = f"• {s_name} ({s_prof})" if s_prof else f"• {s_name}"
                if s_name:
                    c.drawString(right_x + 6, y_right, disp_sk)
                    y_right -= 11
            y_right -= 8

        if references:
            check_right_break(35)
            draw_boxed_header("REFERENCES", right_x, right_w, is_left=False)
            for ref in references:
                if isinstance(ref, dict) and ref.get("include_in_resume", True):
                    check_right_break(25)
                    r_name = ref.get("name", "")
                    r_title = ref.get("designation") or ref.get("title", "")
                    r_org = ref.get("organization", "")
                    show_contact = ref.get("include_contact_details", False)

                    c.setFont("Helvetica-Bold", 8)
                    c.setFillColor(colors.HexColor("#0F172A"))
                    c.drawString(right_x + 4, y_right, f"• {r_name}")
                    y_right -= 10
                    if r_title or r_org:
                        c.setFont("Helvetica", 7.5)
                        c.setFillColor(colors.HexColor("#475569"))
                        c.drawString(right_x + 8, y_right, f"{r_title}, {r_org}".strip(", "))
                        y_right -= 9
                    if show_contact and ref.get("contact_info"):
                        c.setFont("Helvetica-Oblique", 7.2)
                        c.setFillColor(colors.HexColor("#64748B"))
                        c.drawString(right_x + 8, y_right, ref.get("contact_info"))
                        y_right -= 9
                    y_right -= 3

        if languages:
            check_right_break(30)
            draw_boxed_header("LANGUAGES", right_x, right_w, is_left=False)
            c.setFont("Helvetica", 8)
            c.setFillColor(colors.HexColor("#1E293B"))
            for l in languages:
                check_right_break(15)
                l_name = l.get("name") if isinstance(l, dict) else str(l)
                l_prof = f" ({l.get('proficiency')})" if isinstance(l, dict) and l.get("proficiency") else ""
                c.drawString(right_x + 6, y_right, f"• {l_name}{l_prof}")
                y_right -= 11

        # 2. LEFT COLUMN: Projects, Work Experience, Certifications, Achievements, Custom
        if projects:
            check_left_break(35)
            draw_boxed_header("PROJECTS", left_x, left_w, is_left=True)
            for pr in projects:
                if isinstance(pr, dict):
                    check_left_break(45)
                    title = pr.get("title") or pr.get("name") or "Project"
                    techs = pr.get("technologies") or ""
                    desc = pr.get("description") or ""
                    contrib = pr.get("contributions") or ""

                    c.setFont("Helvetica-Bold", 9.5)
                    c.setFillColor(colors.HexColor("#0F172A"))
                    c.drawString(left_x + 2, y_left, title.upper())
                    y_left -= 11

                    if techs:
                        c.setFont("Helvetica-Oblique", 7.8)
                        c.setFillColor(colors.HexColor("#7965D8"))
                        c.drawString(left_x + 2, y_left, f"Technologies: {techs}")
                        y_left -= 10

                    if desc:
                        c.setFont("Helvetica", 8.2)
                        c.setFillColor(colors.HexColor("#334155"))
                        for dl in _wrap_text_lines(desc, 68):
                            check_left_break(15)
                            c.drawString(left_x + 2, y_left, dl)
                            y_left -= 10

                    if contrib:
                        c.setFont("Helvetica", 8)
                        c.setFillColor(colors.HexColor("#475569"))
                        for cl in _wrap_text_lines(f"Outcome: {contrib}", 68):
                            check_left_break(15)
                            c.drawString(left_x + 2, y_left, cl)
                            y_left -= 10
                    y_left -= 6
            y_left -= 4

        if experiences:
            check_left_break(35)
            draw_boxed_header("WORK EXPERIENCE & INTERNSHIPS", left_x, left_w, is_left=True)
            for exp in experiences:
                if isinstance(exp, dict):
                    check_left_break(45)
                    role = exp.get("role") or exp.get("title") or "Role"
                    company = exp.get("company") or ""
                    period = exp.get("duration") or exp.get("period") or f"{exp.get('start_date', '')} - {exp.get('end_date', '')}".strip(" -")
                    loc = exp.get("location") or ""
                    resp = exp.get("responsibilities") or exp.get("highlights") or []

                    c.setFont("Helvetica-Bold", 9.5)
                    c.setFillColor(colors.HexColor("#0F172A"))
                    heading = f"{role.upper()} - {company}" if company else role.upper()
                    c.drawString(left_x + 2, y_left, heading)
                    if period:
                        c.setFont("Helvetica", 8)
                        c.setFillColor(colors.HexColor("#64748B"))
                        c.drawRightString(left_x + left_w - 4, y_left, period)
                    y_left -= 11

                    if loc:
                        c.setFont("Helvetica-Oblique", 7.8)
                        c.setFillColor(colors.HexColor("#64748B"))
                        c.drawString(left_x + 2, y_left, loc)
                        y_left -= 10

                    c.setFont("Helvetica", 8.2)
                    c.setFillColor(colors.HexColor("#334155"))
                    if isinstance(resp, list):
                        for item in resp:
                            check_left_break(15)
                            for bl in _wrap_text_lines(item, 64):
                                c.drawString(left_x + 8, y_left, f"• {bl}")
                                y_left -= 10
                    elif isinstance(resp, str) and resp.strip():
                        for line in resp.strip().splitlines():
                            check_left_break(15)
                            for bl in _wrap_text_lines(line.lstrip("•- "), 64):
                                c.drawString(left_x + 8, y_left, f"• {bl}")
                                y_left -= 10
                    y_left -= 6
            y_left -= 4

        if certifications:
            check_left_break(35)
            draw_boxed_header("CERTIFICATIONS", left_x, left_w, is_left=True)
            for cert in certifications:
                if isinstance(cert, dict):
                    check_left_break(25)
                    c_name = cert.get("name") or "Certification"
                    c_iss = cert.get("issuer") or ""
                    c_yr = cert.get("year") or cert.get("issue_date") or ""
                    c_url = cert.get("credential_url") or ""
                    c.setFont("Helvetica-Bold", 8.5)
                    c.setFillColor(colors.HexColor("#0F172A"))
                    c.drawString(left_x + 2, y_left, f"• {c_name}")
                    if c_yr:
                        c.setFont("Helvetica", 8)
                        c.setFillColor(colors.HexColor("#64748B"))
                        c.drawRightString(left_x + left_w - 4, y_left, str(c_yr))
                    y_left -= 10
                    if c_iss:
                        c.setFont("Helvetica", 7.8)
                        c.setFillColor(colors.HexColor("#334155"))
                        c.drawString(left_x + 10, y_left, f"Issuer: {c_iss}")
                        y_left -= 9
                    if c_url:
                        c.setFont("Helvetica-Oblique", 7.4)
                        c.setFillColor(colors.HexColor("#7965D8"))
                        c.drawString(left_x + 10, y_left, f"Credential: {c_url}")
                        y_left -= 9
                    y_left -= 3
            y_left -= 4

        if achievements:
            check_left_break(35)
            draw_boxed_header("HONORS & ACHIEVEMENTS", left_x, left_w, is_left=True)
            for ach in achievements:
                if isinstance(ach, dict):
                    check_left_break(25)
                    a_title = ach.get("title") or "Achievement"
                    a_org = ach.get("organization") or ach.get("context") or ""
                    a_date = ach.get("date") or ""
                    a_desc = ach.get("description") or ""

                    c.setFont("Helvetica-Bold", 8.8)
                    c.setFillColor(colors.HexColor("#0F172A"))
                    c.drawString(left_x + 2, y_left, f"• {a_title}")
                    if a_date:
                        c.setFont("Helvetica", 8)
                        c.setFillColor(colors.HexColor("#64748B"))
                        c.drawRightString(left_x + left_w - 4, y_left, str(a_date))
                    y_left -= 10
                    if a_org:
                        c.setFont("Helvetica-Oblique", 7.8)
                        c.setFillColor(colors.HexColor("#64748B"))
                        c.drawString(left_x + 10, y_left, a_org)
                        y_left -= 9
                    if a_desc:
                        c.setFont("Helvetica", 8)
                        c.setFillColor(colors.HexColor("#334155"))
                        for dl in _wrap_text_lines(a_desc, 64):
                            check_left_break(15)
                            c.drawString(left_x + 10, y_left, dl)
                            y_left -= 9.5
                    y_left -= 4
            y_left -= 4

        if custom_sections:
            for sec in custom_sections:
                if isinstance(sec, dict) and sec.get("include_in_resume", True):
                    s_title = sec.get("title") or "ADDITIONAL SECTION"
                    entries = sec.get("entries", [])
                    if entries:
                        check_left_break(35)
                        draw_boxed_header(s_title.upper(), left_x, left_w, is_left=True)
                        for ent in entries:
                            if isinstance(ent, dict):
                                check_left_break(25)
                                e_title = ent.get("title", "")
                                e_date = ent.get("date", "")
                                e_desc = ent.get("description", "")
                                if e_title:
                                    c.setFont("Helvetica-Bold", 8.5)
                                    c.setFillColor(colors.HexColor("#0F172A"))
                                    c.drawString(left_x + 2, y_left, f"• {e_title}")
                                    if e_date:
                                        c.setFont("Helvetica", 8)
                                        c.setFillColor(colors.HexColor("#64748B"))
                                        c.drawRightString(left_x + left_w - 4, y_left, e_date)
                                    y_left -= 10
                                if e_desc:
                                    c.setFont("Helvetica", 8)
                                    c.setFillColor(colors.HexColor("#334155"))
                                    for dl in _wrap_text_lines(e_desc, 64):
                                        check_left_break(15)
                                        c.drawString(left_x + 10, y_left, dl)
                                        y_left -= 9.5
                                y_left -= 3
                        y_left -= 4

        draw_footer()
        c.save()
        return buf.getvalue()

    # -------------------------------------------------------------------------
    # TEMPLATE 2, 3, 4: CADDISFLY (Table ATS), SAHANI (Accent), MAYFLY (Clean)
    # -------------------------------------------------------------------------
    y = height - margin_top
    content_w = width - (margin_x * 2)

    def check_page_break(needed_space: int = 35):
        nonlocal y, page_num
        if y - needed_space < margin_bottom + 15:
            draw_footer()
            c.showPage()
            page_num += 1
            y = height - margin_top

    # Header Rendering
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.HexColor("#0F172A" if template_id != "sahani" else "#0B2545"))
    c.drawString(margin_x, y, full_name.upper())
    y -= 14

    contact_parts = [p for p in [job_title, location, phone, email, linkedin] if p]
    c.setFont("Helvetica", 8.5)
    c.setFillColor(colors.HexColor("#475569"))
    c.drawString(margin_x, y, "  |  ".join(contact_parts[:4]))
    y -= 12
    if len(contact_parts) > 4 or portfolio:
        extra_parts = contact_parts[4:] + ([portfolio] if portfolio else [])
        c.drawString(margin_x, y, "  |  ".join(extra_parts))
        y -= 12

    # Divider
    c.setStrokeColor(colors.HexColor("#7965D8" if template_id == "sahani" else "#CBD5E1"))
    c.setLineWidth(1)
    c.line(margin_x, y, width - margin_x, y)
    y -= 14

    def draw_section_heading(title: str):
        nonlocal y
        check_page_break(45)
        if template_id == "sahani":
            c.setFillColor(colors.HexColor("#0B2545"))
            c.rect(margin_x, y - 13, content_w, 16, stroke=0, fill=1)
            c.setFont("Helvetica-Bold", 9)
            c.setFillColor(colors.white)
            c.drawString(margin_x + 6, y - 9, title.upper())
            y -= 20
            c.setFillColor(colors.black)
        else:
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(colors.HexColor("#0F172A"))
            c.drawString(margin_x, y, title.upper())
            y -= 3
            c.setStrokeColor(colors.HexColor("#E2E8F0"))
            c.setLineWidth(0.8)
            c.line(margin_x, y, margin_x + content_w, y)
            y -= 12

    # Professional Summary
    if summary:
        draw_section_heading("Professional Summary")
        c.setFont("Helvetica", 8.5)
        c.setFillColor(colors.HexColor("#334155"))
        for sl in _wrap_text_lines(summary, 95):
            check_page_break(15)
            c.drawString(margin_x, y, sl)
            y -= 11
        y -= 6

    # Work Experience & Internships
    if experiences:
        draw_section_heading("Professional Experience & Internships")
        for exp in experiences:
            if isinstance(exp, dict):
                check_page_break(40)
                role = exp.get("role") or exp.get("title") or "Role"
                comp = exp.get("company") or ""
                dur = exp.get("duration") or exp.get("period") or f"{exp.get('start_date', '')} - {exp.get('end_date', '')}".strip(" -")
                loc = exp.get("location") or ""
                resp = exp.get("responsibilities") or exp.get("highlights") or []

                c.setFont("Helvetica-Bold", 9.5)
                c.setFillColor(colors.HexColor("#0F172A"))
                c.drawString(margin_x, y, f"{role}  —  {comp}")
                if dur:
                    c.setFont("Helvetica", 8.5)
                    c.setFillColor(colors.HexColor("#64748B"))
                    c.drawRightString(width - margin_x, y, dur)
                y -= 11

                if loc:
                    c.setFont("Helvetica-Oblique", 8)
                    c.setFillColor(colors.HexColor("#64748B"))
                    c.drawString(margin_x, y, loc)
                    y -= 10

                c.setFont("Helvetica", 8.5)
                c.setFillColor(colors.HexColor("#334155"))
                if isinstance(resp, list):
                    for item in resp:
                        check_page_break(15)
                        for chunk in _wrap_text_lines(item, 88):
                            c.drawString(margin_x + 8, y, f"•  {chunk}")
                            y -= 10.5
                elif isinstance(resp, str) and resp.strip():
                    for line in resp.strip().splitlines():
                        check_page_break(15)
                        for chunk in _wrap_text_lines(line.lstrip("•- "), 88):
                            c.drawString(margin_x + 8, y, f"•  {chunk}")
                            y -= 10.5
                y -= 4

    # Technical Projects
    if projects:
        draw_section_heading("Technical Projects")
        for pr in projects:
            if isinstance(pr, dict):
                check_page_break(40)
                title = pr.get("title") or pr.get("name") or "Project"
                techs = pr.get("technologies") or ""
                desc = pr.get("description") or ""
                contrib = pr.get("contributions") or ""

                c.setFont("Helvetica-Bold", 9.5)
                c.setFillColor(colors.HexColor("#0F172A"))
                c.drawString(margin_x, y, title)
                if techs:
                    c.setFont("Helvetica", 8)
                    c.setFillColor(colors.HexColor("#7965D8"))
                    c.drawRightString(width - margin_x, y, f"Tech: {techs}")
                y -= 11

                if desc:
                    c.setFont("Helvetica", 8.5)
                    c.setFillColor(colors.HexColor("#334155"))
                    for chunk in _wrap_text_lines(desc, 90):
                        check_page_break(15)
                        c.drawString(margin_x + 8, y, chunk)
                        y -= 10.5

                if contrib:
                    c.setFont("Helvetica-Oblique", 8)
                    c.setFillColor(colors.HexColor("#475569"))
                    for chunk in _wrap_text_lines(f"Outcome: {contrib}", 90):
                        check_page_break(15)
                        c.drawString(margin_x + 8, y, chunk)
                        y -= 10
                y -= 4

    # Education
    if educations:
        draw_section_heading("Education")
        for edu in educations:
            if isinstance(edu, dict):
                check_page_break(30)
                deg = edu.get("degree") or edu.get("qualification") or "Degree"
                inst = edu.get("institution") or ""
                period = edu.get("period") or f"{edu.get('start_date', '')} - {edu.get('end_date', '')}".strip(" -")
                academic = edu.get("academic_info") or edu.get("honors") or ""

                c.setFont("Helvetica-Bold", 9)
                c.setFillColor(colors.HexColor("#0F172A"))
                c.drawString(margin_x, y, f"{deg}  ·  {inst}")
                if period:
                    c.setFont("Helvetica", 8)
                    c.setFillColor(colors.HexColor("#64748B"))
                    c.drawRightString(width - margin_x, y, period)
                y -= 10

                if academic:
                    c.setFont("Helvetica-Oblique", 8)
                    c.setFillColor(colors.HexColor("#7965D8"))
                    c.drawString(margin_x, y, f"Academic Honors / Grade: {academic}")
                    y -= 9
                y -= 3

    # Skills Inventory
    if skills:
        draw_section_heading("Core Competencies & Skills")
        c.setFont("Helvetica", 8.5)
        c.setFillColor(colors.HexColor("#334155"))
        skill_strs = []
        for s in skills:
            if isinstance(s, dict):
                s_name = s.get("name", "")
                p = f" ({s.get('proficiency')})" if s.get("proficiency") and show_prof else ""
                skill_strs.append(f"{s_name}{p}")
            else:
                skill_strs.append(str(s))
        joined_skills = ", ".join(skill_strs)
        for chunk in _wrap_text_lines(joined_skills, 92):
            check_page_break(15)
            c.drawString(margin_x, y, chunk)
            y -= 10.5
        y -= 4

    # Certifications (Text-only credentials, never raw image attachments)
    if certifications:
        draw_section_heading("Certifications & Credentials")
        for cert in certifications:
            if isinstance(cert, dict):
                check_page_break(25)
                c_name = cert.get("name") or "Certification"
                c_iss = cert.get("issuer") or ""
                c_yr = cert.get("year") or cert.get("issue_date") or ""
                c_url = cert.get("credential_url") or ""
                c.setFont("Helvetica-Bold", 9)
                c.setFillColor(colors.HexColor("#0F172A"))
                c.drawString(margin_x, y, f"{c_name}  —  {c_iss}")
                if c_yr:
                    c.setFont("Helvetica", 8)
                    c.setFillColor(colors.HexColor("#64748B"))
                    c.drawRightString(width - margin_x, y, str(c_yr))
                y -= 11
                if c_url:
                    c.setFont("Helvetica-Oblique", 7.8)
                    c.setFillColor(colors.HexColor("#7965D8"))
                    c.drawString(margin_x + 8, y, f"Credential Link: {c_url}")
                    y -= 10
                y -= 2

    # Honors & Achievements
    if achievements:
        draw_section_heading("Honors & Achievements")
        for ach in achievements:
            if isinstance(ach, dict):
                check_page_break(25)
                a_title = ach.get("title") or "Achievement"
                a_org = ach.get("organization") or ach.get("context") or ""
                a_date = ach.get("date") or ""
                a_desc = ach.get("description") or ""

                c.setFont("Helvetica-Bold", 9)
                c.setFillColor(colors.HexColor("#0F172A"))
                c.drawString(margin_x, y, a_title)
                if a_date:
                    c.setFont("Helvetica", 8)
                    c.setFillColor(colors.HexColor("#64748B"))
                    c.drawRightString(width - margin_x, y, str(a_date))
                y -= 11
                if a_org:
                    c.setFont("Helvetica-Oblique", 8)
                    c.setFillColor(colors.HexColor("#64748B"))
                    c.drawString(margin_x + 8, y, a_org)
                    y -= 10
                if a_desc:
                    c.setFont("Helvetica", 8.2)
                    c.setFillColor(colors.HexColor("#334155"))
                    for chunk in _wrap_text_lines(a_desc, 90):
                        check_page_break(15)
                        c.drawString(margin_x + 8, y, chunk)
                        y -= 10
                y -= 3

    # References
    if references:
        draw_section_heading("Professional References")
        for ref in references:
            if isinstance(ref, dict) and ref.get("include_in_resume", True):
                check_page_break(25)
                r_name = ref.get("name", "")
                r_title = ref.get("designation") or ref.get("title", "")
                r_org = ref.get("organization", "")
                show_contact = ref.get("include_contact_details", False)

                c.setFont("Helvetica-Bold", 8.8)
                c.setFillColor(colors.HexColor("#0F172A"))
                c.drawString(margin_x, y, f"{r_name}  —  {r_title}, {r_org}".strip(" —, "))
                y -= 10
                if show_contact and ref.get("contact_info"):
                    c.setFont("Helvetica", 8)
                    c.setFillColor(colors.HexColor("#64748B"))
                    c.drawString(margin_x + 8, y, f"Contact: {ref.get('contact_info')}")
                    y -= 9
                y -= 2

    # Custom Sections
    if custom_sections:
        for sec in custom_sections:
            if isinstance(sec, dict) and sec.get("include_in_resume", True):
                s_title = sec.get("title") or "Additional Information"
                entries = sec.get("entries", [])
                if entries:
                    draw_section_heading(s_title)
                    for ent in entries:
                        if isinstance(ent, dict):
                            check_page_break(25)
                            e_title = ent.get("title", "")
                            e_date = ent.get("date", "")
                            e_desc = ent.get("description", "")
                            if e_title:
                                c.setFont("Helvetica-Bold", 8.8)
                                c.setFillColor(colors.HexColor("#0F172A"))
                                c.drawString(margin_x, y, e_title)
                                if e_date:
                                    c.setFont("Helvetica", 8)
                                    c.setFillColor(colors.HexColor("#64748B"))
                                    c.drawRightString(width - margin_x, y, e_date)
                                y -= 10
                            if e_desc:
                                c.setFont("Helvetica", 8.2)
                                c.setFillColor(colors.HexColor("#334155"))
                                for chunk in _wrap_text_lines(e_desc, 90):
                                    check_page_break(15)
                                    c.drawString(margin_x + 8, y, chunk)
                                    y -= 10
                            y -= 3

    draw_footer()
    c.save()
    return buf.getvalue()


def generate_ats_resume_pdf(
    user_name: str,
    user_email: str,
    profile: dict[str, Any],
    skills: list[dict[str, Any]],
    sections_to_include: list[str] | None = None,
    template_style: str = "Classic ATS",
) -> bytes:
    """Backward-compatible wrapper invoked by automated test suites and legacy endpoints."""
    name_parts = user_name.split()
    first_name = name_parts[0] if name_parts else ""
    last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

    resume_data = {
        "first_name": first_name,
        "last_name": last_name,
        "job_title": profile.get("job_title", ""),
        "email": user_email or profile.get("email", ""),
        "phone": profile.get("phone", ""),
        "location": profile.get("location", ""),
        "linkedin": profile.get("linkedin", ""),
        "portfolio": profile.get("portfolio") or profile.get("github", ""),
        "summary": profile.get("summary", ""),
        "education": services.core.parse_json_field(profile.get("education", [])),
        "experience": services.core.parse_json_field(profile.get("experience", [])),
        "projects": services.core.parse_json_field(profile.get("projects", [])),
        "skills": skills,
        "certifications": services.core.parse_json_field(profile.get("certifications", [])),
        "achievements": [],
        "references": [],
        "custom_sections": [],
    }

    tmpl = "puffin" if template_style in ("Modern Clean", "puffin") else "caddisfly"
    return generate_resume_pdf(resume_data, template_id=tmpl)


# =============================================================================
# RESUME STRENGTH CALCULATION
# =============================================================================
def calculate_resume_strength(resume_data: dict[str, Any]) -> int:
    """Calculates dynamic resume score out of 100 based on completed sections."""
    score = 0
    if resume_data.get("first_name") and resume_data.get("email"):
        score += 15
    if resume_data.get("phone") and (resume_data.get("location") or resume_data.get("city")):
        score += 10
    if resume_data.get("summary") and len(resume_data.get("summary", "")) > 30:
        score += 15
    if resume_data.get("job_title"):
        score += 5
    if resume_data.get("experience") and len(resume_data.get("experience", [])) > 0:
        score += 15
    if resume_data.get("education") and len(resume_data.get("education", [])) > 0:
        score += 10
    if resume_data.get("projects") and len(resume_data.get("projects", [])) > 0:
        score += 10
    if resume_data.get("skills") and len(resume_data.get("skills", [])) >= 3:
        score += 10
    if resume_data.get("certifications") and len(resume_data.get("certifications", [])) > 0:
        score += 5
    if resume_data.get("achievements") and len(resume_data.get("achievements", [])) > 0:
        score += 5
    return min(100, max(20, score))


# =============================================================================
# STEP A: CHOOSE A TEMPLATE SCREEN
# =============================================================================
def render_template_selection_screen(
    user_id: int,
    current_selected: str,
    resume_data: dict[str, Any],
    pdf_bytes: bytes,
    clean_filename: str,
) -> None:
    """Renders Step A: Template gallery with high contrast dark theme."""
    render_html("""<div style="margin-bottom: 1.25rem;">
<div style="font-size: 0.78rem; font-weight: 700; color: #7965D8; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.25rem;">
TalentSphere Resume Studio
</div>
<div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem;">
<h2 style="font-size: 1.85rem; color: #FFFFFF; font-weight: 800; letter-spacing: -0.02em; margin: 0;">
Choose a Template
</h2>
</div>
<p style="color: #C4C4D0; font-size: 0.92rem; margin: 0.35rem 0 0 0;">
Select a recruiter-tested layout before personalizing your resume information in the editor.
</p>
</div>""")

    col_search, col_ats = st.columns([3, 1])
    with col_search:
        search_query = st.text_input(
            "Search Templates",
            placeholder="Search by role or style (e.g. 'engineer', 'data', 'designer')...",
            key="tmpl_search_query",
            label_visibility="collapsed",
        ).strip().lower()

    with col_ats:
        ats_only = st.toggle("Filter ATS-friendly only", value=False, key="toggle_ats_filter")

    # Category Chips
    categories = ["All", "Engineer", "Fresher", "Senior", "Data", "Designer", "Product Manager", "Marketing", "Sales"]
    active_cat = st.session_state.get("tmpl_active_category", "All")

    cat_cols = st.columns(len(categories))
    for i, cat in enumerate(categories):
        with cat_cols[i]:
            is_active = (cat == active_cat)
            btn_type = "primary" if is_active else "secondary"
            if st.button(cat, key=f"btn_cat_{cat}", type=btn_type, use_container_width=True):
                st.session_state["tmpl_active_category"] = cat
                st.rerun()

    render_html("<div style='height: 12px;'></div>")

    # Filter templates
    filtered = []
    for t in TEMPLATES:
        if ats_only and not t["ats_friendly"]:
            continue
        if active_cat != "All" and active_cat not in t["categories"]:
            continue
        if search_query:
            matches_name = search_query in t["name"].lower()
            matches_sub = search_query in t["subtitle"].lower()
            matches_cat = any(search_query in c.lower() for c in t["categories"])
            if not (matches_name or matches_sub or matches_cat):
                continue
        filtered.append(t)

    # Template Count Header
    render_html(f"""<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
<div style="font-size: 0.88rem; color: #E0E0EA; font-weight: 600;">Showing <strong>{len(filtered)}</strong> Recruiter-Approved Templates</div>
<div style="font-size: 0.82rem; color: #22C55E; font-weight: 700;">✓ Instant Real-Time Preview</div>
</div>""")

    # Grid of Template Cards (2 Columns)
    grid_cols = st.columns(2)
    for idx, tmpl in enumerate(filtered):
        col = grid_cols[idx % 2]
        is_current = (tmpl["id"] == current_selected)

        with col:
            with st.container(border=True):
                border_color = "#7965D8" if is_current else "#34343D"
                glow = "box-shadow: 0 0 18px rgba(121, 101, 216, 0.45);" if is_current else ""

                if tmpl["id"] == "puffin":
                    mini_preview_html = """<div style="background: #FFFFFF; color: #1E293B; border-radius: 6px; padding: 12px 14px; font-size: 7px; line-height: 1.35; height: 190px; overflow: hidden; border: 1px solid #CBD5E1;">
<div style="text-align: center; border-bottom: 1px solid #0F172A; padding-bottom: 4px; margin-bottom: 6px;">
<div style="font-weight: 800; font-size: 9.5px; color: #0F172A; letter-spacing: 0.5px;">MAYANK MATHUR</div>
<div style="font-size: 7px; color: #7965D8; font-weight: 700;">— SENIOR CLOUD ENGINEER —</div>
<div style="font-size: 6px; color: #64748B;">Austin, TX · +1 (512) 890-4421 · mayank@talentsphere.io</div>
</div>
<div style="display: grid; grid-template-columns: 60% 40%; gap: 8px;">
<div>
<div style="border: 0.8px solid #0F172A; text-align: center; font-weight: 800; font-size: 6.5px; margin-bottom: 3px; padding: 1px;">PROJECTS</div>
<div style="font-weight: 700; font-size: 6.5px;">Automated DevSecOps Pipeline</div>
<div style="color: #475569; font-size: 5.8px; margin-bottom: 4px;">Zero-downtime blue/green EKS cluster rollouts.</div>
<div style="border: 0.8px solid #0F172A; text-align: center; font-weight: 800; font-size: 6.5px; margin-bottom: 3px; padding: 1px;">WORK EXPERIENCE</div>
<div style="font-weight: 700; font-size: 6.5px;">Senior DevOps Lead — TalentSphere</div>
<div style="color: #475569; font-size: 5.8px;">• Reduced deploy cycles by 65% across 35 squads.</div>
</div>
<div>
<div style="border: 0.8px solid #0F172A; text-align: center; font-weight: 800; font-size: 6.5px; margin-bottom: 3px; padding: 1px;">CONTACT</div>
<div style="font-size: 5.8px; color: #334155;">📞 +1 (512) 890-4421<br>📍 Austin, TX<br>🔗 linkedin.com/in/demo</div>
<div style="border: 0.8px solid #0F172A; text-align: center; font-weight: 800; font-size: 6.5px; margin: 4px 0 3px 0; padding: 1px;">SKILLS</div>
<div style="font-size: 5.8px; color: #334155;">• Kubernetes<br>• Terraform<br>• Python / AWS</div>
</div>
</div>
</div>"""
                elif tmpl["id"] == "caddisfly":
                    mini_preview_html = """<div style="background: #FFFFFF; color: #1E293B; border-radius: 6px; padding: 12px 14px; font-size: 7px; line-height: 1.35; height: 190px; overflow: hidden; border: 1px solid #CBD5E1;">
<div style="font-weight: 800; font-size: 10px; color: #1E293B;">SAHIL SINGH RAJPUT</div>
<div style="font-size: 6.5px; color: #64748B; margin-bottom: 6px;">Lead DevOps Engineer | sahil@talentsphere.io | Pune, India</div>
<div style="background: #F1F5F9; font-weight: 700; font-size: 6.5px; padding: 2px 4px; border-left: 2px solid #2563EB; margin-bottom: 4px;">SUMMARY</div>
<div style="font-size: 5.8px; color: #475569; margin-bottom: 6px;">Accomplished DevOps engineer with 7+ years in automation and cloud infrastructure.</div>
<div style="background: #F1F5F9; font-weight: 700; font-size: 6.5px; padding: 2px 4px; border-left: 2px solid #2563EB; margin-bottom: 4px;">WORK EXPERIENCE</div>
<table style="width: 100%; font-size: 5.8px; border-collapse: collapse;">
<tr style="border-bottom: 0.5px solid #E2E8F0;"><td style="font-weight:700;">Lead Cloud Architect</td><td style="color:#64748B; text-align:right;">04/2020 – Present</td></tr>
</table>
<div style="color: #475569; font-size: 5.8px; margin: 3px 0 6px 0;">• Architected CI/CD pipelines boosting deployment reliability to 99.9%.</div>
<div style="background: #F1F5F9; font-weight: 700; font-size: 6.5px; padding: 2px 4px; border-left: 2px solid #2563EB; margin-bottom: 4px;">TECHNICAL SKILLS</div>
<div style="font-size: 5.8px; color: #334155;">Python, Kubernetes, AWS, Terraform, Docker, SQL</div>
</div>"""
                elif tmpl["id"] == "sahani":
                    mini_preview_html = """<div style="background: #FFFFFF; color: #1E293B; border-radius: 6px; padding: 12px 14px; font-size: 7px; line-height: 1.35; height: 190px; overflow: hidden; border: 1px solid #CBD5E1;">
<div style="text-align: center; margin-bottom: 6px;">
<div style="font-weight: 800; font-size: 10px; color: #0B2545;">SUHANI SHARMA</div>
<div style="font-size: 6.5px; color: #64748B;">AI Engineer | Bangalore, India | suhani@talentsphere.io</div>
</div>
<div style="background: #0B2545; color: #FFFFFF; font-weight: 700; font-size: 6.5px; padding: 2.5px 6px; border-radius: 2px; margin-bottom: 4px;">SUMMARY</div>
<div style="font-size: 5.8px; color: #334155; margin-bottom: 6px;">Innovative AI engineer with 5+ years of experience in ML models and LLM systems.</div>
<div style="background: #0B2545; color: #FFFFFF; font-weight: 700; font-size: 6.5px; padding: 2.5px 6px; border-radius: 2px; margin-bottom: 4px;">EXPERIENCE & PROJECTS</div>
<div style="font-weight: 700; font-size: 6.2px; color: #0F172A;">Machine Learning Lead — Infosys Tech</div>
<div style="font-size: 5.8px; color: #475569;">• Developed predictive deep learning analytics for real-time risk classification.</div>
</div>"""
                else:
                    mini_preview_html = """<div style="background: #FFFFFF; color: #1E293B; border-radius: 6px; padding: 12px 14px; font-size: 7px; line-height: 1.35; height: 190px; overflow: hidden; border: 1px solid #CBD5E1;">
<div style="text-align: center; margin-bottom: 6px;">
<div style="font-weight: 800; font-size: 10px; color: #334155; letter-spacing: 0.5px;">SUNANDA SHARMA</div>
<div style="font-size: 6.5px; color: #64748B;">Senior Strategy Consultant · New Delhi · sunanda@talentsphere.io</div>
</div>
<div style="border-top: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0; padding: 3px 0; margin-bottom: 6px; font-size: 5.8px; color: #475569; text-align: center;">
Executive Leader driving high-impact digital transformation and cross-functional alignment.
</div>
<div style="font-weight: 700; font-size: 6.5px; color: #0F172A; margin-bottom: 3px; text-transform: uppercase;">Work Experience</div>
<div style="display: flex; justify-content: space-between; font-size: 5.8px;">
<span style="font-weight: 700;">Director of Solutions</span><span>2021 – Present</span>
</div>
<div style="font-size: 5.6px; color: #64748B; margin-bottom: 4px;">Delivered $14M in enterprise cloud cost optimization.</div>
</div>"""

                render_html(f"""<div style="border: 2px solid {border_color}; border-radius: 10px; padding: 8px; margin-bottom: 0.75rem; {glow}">
{mini_preview_html}
</div>
<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.35rem;">
<div>
<div style="font-size: 1.18rem; font-weight: 800; color: #FFFFFF;">{tmpl['name']}</div>
<div style="font-size: 0.80rem; color: #7965D8; font-weight: 700;">{tmpl['subtitle']}</div>
</div>
<div style="text-align: right;">
{'<span style="background: #7965D8; color: #FFFFFF; font-weight: 700; font-size: 11px; padding: 2px 8px; border-radius: 9999px;">✓ Selected</span>' if is_current else '<span style="background: #24242F; color: #E0E0EA; border: 1px solid #34343D; font-weight: 600; font-size: 11px; padding: 2px 8px; border-radius: 9999px;">ATS Friendly</span>'}
</div>
</div>
<div style="font-size: 0.84rem; color: #C4C4D0; line-height: 1.45; min-height: 48px; margin-bottom: 0.65rem;">
{tmpl['description']}
</div>
<div style="font-size: 0.76rem; color: #A0A0AD; margin-bottom: 0.75rem;">
👥 Chosen by {tmpl['users_count']} professionals {'· 📷 Photo Supported' if tmpl.get('supports_photo') else ''}
</div>""")

                c_select, _ = st.columns([2, 1])
                with c_select:
                    if st.button(
                        f"Select {tmpl['name']}" if not is_current else f"✓ Using {tmpl['name']}",
                        key=f"btn_choose_tmpl_{tmpl['id']}",
                        type="primary" if is_current else "secondary",
                        use_container_width=True,
                    ):
                        st.session_state["resume_selected_template"] = tmpl["id"]
                        services.core.save_resume_draft(user_id, resume_data, tmpl["id"])
                        st.rerun()

    # Prominent 'Confirm & Proceed' Button
    render_html("""<div style="height: 18px;"></div>
<div style="background: #1C1C22; border: 1px solid #34343D; border-radius: 14px; padding: 1.35rem 1.6rem; text-align: center; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);">
<div style="font-size: 1.05rem; font-weight: 800; color: #FFFFFF; margin-bottom: 0.35rem;">
Ready to customize your resume with the selected layout?
</div>
<div style="font-size: 0.86rem; color: #C4C4D0; margin-bottom: 1rem;">
Your profile details have been automatically prefilled. You can customize, reorder, and download your resume anytime.
</div>
</div>""")

    col_btn_center = st.columns([1, 2, 1])
    with col_btn_center[1]:
        if st.button(
            "Confirm & Proceed to Resume Editor ➔",
            key="btn_confirm_proceed_editor",
            type="primary",
            use_container_width=True,
        ):
            st.session_state["resume_builder_step"] = "editor"
            st.rerun()


# =============================================================================
# STEP B: DEDICATED TWO-PANEL RESUME EDITOR (STEPS 1 TO 10)
# =============================================================================

CATEGORY_STEPS = [
    {
        "step": 1,
        "id": "personal",
        "title": "Personal Details",
        "icon": "👤",
        "description": "Provide your contact and professional details. Adding a verified phone and location increases recruiter response rates by over 60%.",
    },
    {
        "step": 2,
        "id": "summary",
        "title": "Professional Summary",
        "icon": "📝",
        "description": "Highlight your top achievements, core technical strengths, and career objective in 3–5 impactful sentences.",
    },
    {
        "step": 3,
        "id": "experience",
        "title": "Work Experience",
        "icon": "🏢",
        "description": "Add your employment history, internships, and relevant roles in reverse chronological order with measurable achievements.",
    },
    {
        "step": 4,
        "id": "education",
        "title": "Education",
        "icon": "🎓",
        "description": "List your degrees, college or university qualifications, field of study, and academic honors.",
    },
    {
        "step": 5,
        "id": "skills",
        "title": "Skills",
        "icon": "⚡",
        "description": "Add your technical competencies and professional skills. Select proficiency using the 5 circular indicators.",
    },
    {
        "step": 6,
        "id": "projects",
        "title": "Projects",
        "icon": "🚀",
        "description": "Showcase personal, academic, or enterprise projects with measurable outcomes and technologies used.",
    },
    {
        "step": 7,
        "id": "certifications",
        "title": "Certifications",
        "icon": "📜",
        "description": "Add verified industry certifications. Upload certificate documents (PDF, JPG, PNG) as supporting evidence.",
    },
    {
        "step": 8,
        "id": "achievements",
        "title": "Achievements",
        "icon": "🏆",
        "description": "Highlight major awards, competitions won, hackathon recognitions, or professional milestones.",
    },
    {
        "step": 9,
        "id": "references",
        "title": "References",
        "icon": "👥",
        "description": "Add professional references. Contact details remain confidential unless you choose to include them.",
    },
    {
        "step": 10,
        "id": "custom",
        "title": "Custom Sections",
        "icon": "🧩",
        "description": "Add user-defined sections such as Publications, Volunteer Work, Languages, or specialized domains.",
    },
]

PROF_COLORS = {
    "Beginner": "#60A5FA",     # Blue
    "Skillful": "#2DD4BF",     # Teal
    "Experienced": "#22C55E",  # Green
    "Advanced": "#A78BFA",     # Purple
    "Expert": "#FBBF24",       # Amber
}


def generate_live_preview_html(resume_data: dict[str, Any], template_id: str) -> str:
    """Generates authentic paper-like HTML preview matching selected template.
    
    Supports single-page and multi-page layouts with crisp typography, margins,
    and accurate 5-level proficiency color tags.
    """
    first_name = resume_data.get("first_name", "").strip()
    last_name = resume_data.get("last_name", "").strip()
    disp_name = f"{first_name} {last_name}".strip() or "Employee Name"
    disp_title = resume_data.get("job_title", "").strip() or "Professional Title"
    disp_summary = resume_data.get("summary", "").strip()
    disp_phone = resume_data.get("phone", "").strip()
    disp_email = resume_data.get("email", "").strip()
    disp_city = resume_data.get("city", "").strip()
    disp_country = resume_data.get("country", "").strip()
    disp_loc = resume_data.get("location", "").strip() or f"{disp_city}, {disp_country}".strip(", ")
    disp_li = resume_data.get("linkedin", "").strip()
    disp_port = resume_data.get("portfolio", "").strip()
    show_prof = resume_data.get("show_skill_proficiency", True)

    projects = [p for p in resume_data.get("projects", []) if isinstance(p, dict)]
    experiences = [e for e in resume_data.get("experience", []) if isinstance(e, dict)]
    educations = [ed for ed in resume_data.get("education", []) if isinstance(ed, dict)]
    skills = [s for s in resume_data.get("skills", []) if isinstance(s, dict)]
    certifications = [c for c in resume_data.get("certifications", []) if isinstance(c, dict)]
    achievements = [a for a in resume_data.get("achievements", []) if isinstance(a, dict)]
    references = [r for r in resume_data.get("references", []) if isinstance(r, dict) and r.get("include_in_resume", True)]
    custom_sections = [cs for cs in resume_data.get("custom_sections", []) if isinstance(cs, dict) and cs.get("include_in_resume", True)]

    # Determine whether content exceeds standard 1-page bounds
    content_load = len(projects) * 2 + len(experiences) * 2 + len(educations) * 1.5 + len(certifications) + len(achievements) + len(references) + (2 if len(disp_summary) > 250 else 0)
    is_multipage = content_load > 8

    # Helper for skills badges with the 5 exact colors
    def render_skill_badge(sk: dict[str, Any]) -> str:
        s_name = sk.get("name", "")
        p_lvl = sk.get("proficiency", "Experienced")
        p_col = PROF_COLORS.get(p_lvl, "#22C55E")
        if show_prof and p_lvl:
            return f"""<span style="display:inline-flex; align-items:center; gap:5px; background:#F1F5F9; border:1px solid #CBD5E1; border-radius:6px; padding:3px 8px; margin:2px 4px 2px 0; font-size:0.74rem; font-weight:600; color:#1E293B;">
                <span>{s_name}</span>
                <span style="background:{p_col}; color:#FFFFFF; font-size:0.62rem; font-weight:800; padding:1px 5px; border-radius:9999px;">{p_lvl}</span>
            </span>"""
        return f"""<span style="display:inline-block; background:#F1F5F9; border:1px solid #CBD5E1; border-radius:6px; padding:3px 8px; margin:2px 4px 2px 0; font-size:0.74rem; font-weight:600; color:#1E293B;">{s_name}</span>"""

    # -------------------------------------------------------------------------
    # TEMPLATE 1: PUFFIN (Modern Professional 2-Column)
    # -------------------------------------------------------------------------
    if template_id == "puffin":
        def render_puffin_proj(p_list):
            out = ""
            for pr in p_list:
                tech = f"<div style='font-size:0.72rem; color:#7965D8; font-weight:700; margin-bottom:2px;'>{pr.get('technologies')}</div>" if pr.get('technologies') else ""
                outcome = f"<div style='font-size:0.72rem; color:#475569; font-style:italic; margin-top:2px;'>Outcome: {pr.get('contributions')}</div>" if pr.get('contributions') else ""
                out += f"""<div style="margin-bottom:0.85rem;">
                    <div style="font-size:0.82rem; font-weight:800; color:#0F172A; text-transform:uppercase;">{pr.get('title', 'Project')}</div>
                    {tech}
                    <div style="font-size:0.76rem; color:#334155; line-height:1.45;">{pr.get('description', '')}</div>
                    {outcome}
                </div>"""
            return out

        def render_puffin_exp(e_list):
            out = ""
            for ex in e_list:
                role = ex.get("role") or ex.get("title", "Role")
                comp = ex.get("company", "")
                dur = ex.get("duration") or ex.get("period", "")
                bullets = ""
                resp = ex.get("responsibilities") or ex.get("highlights", [])
                if isinstance(resp, list):
                    bullets = "".join(f"<div style='margin-left:0.6rem; margin-top:1px;'>• {b}</div>" for b in resp)
                elif isinstance(resp, str):
                    bullets = "".join(f"<div style='margin-left:0.6rem; margin-top:1px;'>• {b.lstrip('•- ')}</div>" for b in resp.splitlines() if b.strip())
                out += f"""<div style="margin-bottom:0.85rem;">
                    <div style="display:flex; justify-content:space-between; font-size:0.80rem; font-weight:800; color:#0F172A; text-transform:uppercase;">
                        <span>{role} - {comp}</span>
                        <span style="font-size:0.72rem; color:#64748B; font-weight:600;">{dur}</span>
                    </div>
                    <div style="font-size:0.75rem; color:#334155; line-height:1.45;">{bullets}</div>
                </div>"""
            return out

        contact_html = f"""<div style="font-size:0.75rem; color:#334155; line-height:1.6; margin-bottom:0.85rem;">
            {f"<div>📞 {disp_phone}</div>" if disp_phone else ""}
            {f"<div>📍 {disp_loc}</div>" if disp_loc else ""}
            {f"<div>✉️ {disp_email}</div>" if disp_email else ""}
            {f"<div>🔗 {disp_li.replace('https://','')}</div>" if disp_li else ""}
            {f"<div>🌐 {disp_port.replace('https://','')}</div>" if disp_port else ""}
        </div>"""

        edu_html = ""
        for ed in educations:
            deg = ed.get("degree", "Degree")
            inst = ed.get("institution", "")
            dur = ed.get("period") or f"{ed.get('start_date', '')} - {ed.get('end_date', '')}".strip(" -")
            honors = ed.get("academic_info") or ed.get("honors", "")
            edu_html += f"""<div style="margin-bottom:0.75rem; font-size:0.75rem;">
                <div style="color:#64748B; font-size:0.70rem; font-weight:600;">{dur}</div>
                <div style="font-weight:800; color:#0F172A;">{inst}</div>
                <div style="color:#334155;">{deg}</div>
                {f"<div style='color:#7965D8; font-size:0.70rem; font-style:italic;'>{honors}</div>" if honors else ""}
            </div>"""

        skills_html = f"<div style='margin-bottom:0.85rem;'>{''.join(render_skill_badge(s) for s in skills)}</div>" if skills else "<div style='font-size:0.75rem; color:#94A3B8; font-style:italic;'>No skills listed.</div>"

        certs_html = ""
        for cr in certifications:
            certs_html += f"""<div style="margin-bottom:0.5rem; font-size:0.75rem;">
                <div style="font-weight:700; color:#0F172A;">• {cr.get('name')}</div>
                <div style="color:#64748B; font-size:0.70rem;">{cr.get('issuer')} ({cr.get('issue_date') or cr.get('year')})</div>
            </div>"""

        ach_html = ""
        for ac in achievements:
            ach_html += f"""<div style="margin-bottom:0.5rem; font-size:0.75rem;">
                <div style="font-weight:700; color:#0F172A;">• {ac.get('title')}</div>
                <div style="color:#64748B; font-size:0.70rem;">{ac.get('organization') or ac.get('context', '')} {f'({ac.get("date")})' if ac.get('date') else ''}</div>
                {f"<div style='color:#334155; font-size:0.73rem;'>{ac.get('description')}</div>" if ac.get('description') else ""}
            </div>"""

        refs_html = ""
        for rf in references:
            cnt = f" · {rf.get('contact_info')}" if rf.get('include_contact_details') and rf.get('contact_info') else ""
            refs_html += f"""<div style="margin-bottom:0.45rem; font-size:0.74rem; color:#334155;">
                <strong>• {rf.get('name')}</strong> — {rf.get('designation')}, {rf.get('organization')}{cnt}
            </div>"""

        cust_html = ""
        for cs in custom_sections:
            entries_html = "".join(f"<div style='font-size:0.74rem; margin-bottom:4px;'><strong>• {e.get('title')}</strong> ({e.get('date')}): {e.get('description')}</div>" for e in cs.get("entries", []) if isinstance(e, dict))
            cust_html += f"""<div style="margin-bottom:0.75rem;">
                <div style="font-size:0.78rem; font-weight:800; color:#0F172A; text-transform:uppercase; margin-bottom:4px;">{cs.get('title')}</div>
                {entries_html}
            </div>"""

        if not is_multipage:
            return f"""<div class="resume-paper-page">
                <div style="text-align: center; margin-bottom: 1.25rem;">
                    <div style="font-size: 1.65rem; font-weight: 900; color: #0F172A; letter-spacing: 0.04em; text-transform: uppercase;">{disp_name}</div>
                    <div style="font-size: 0.88rem; font-weight: 800; color: #7965D8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.65rem;">— {disp_title} —</div>
                    {f"<div style='font-size: 0.78rem; color: #334155; line-height: 1.55; max-width: 90%; margin: auto;'>{disp_summary}</div>" if disp_summary else ""}
                </div>
                <div style="display: grid; grid-template-columns: 58% 42%; gap: 1.25rem; border-top: 1.5px solid #0F172A; padding-top: 1rem;">
                    <div>
                        <div style="border: 1.5px solid #0F172A; text-align: center; font-weight: 900; font-size: 0.76rem; letter-spacing: 0.08em; padding: 3px 6px; margin-bottom: 0.65rem; text-transform: uppercase;">PROJECTS</div>
                        {render_puffin_proj(projects) or "<div style='font-size:0.75rem; color:#94A3B8; font-style:italic;'>No projects added.</div>"}

                        <div style="border: 1.5px solid #0F172A; text-align: center; font-weight: 900; font-size: 0.76rem; letter-spacing: 0.08em; padding: 3px 6px; margin-top: 1rem; margin-bottom: 0.65rem; text-transform: uppercase;">WORK EXPERIENCE</div>
                        {render_puffin_exp(experiences) or "<div style='font-size:0.75rem; color:#94A3B8; font-style:italic;'>No experience added.</div>"}

                        {f"<div style='border: 1.5px solid #0F172A; text-align: center; font-weight: 900; font-size: 0.76rem; letter-spacing: 0.08em; padding: 3px 6px; margin-top: 1rem; margin-bottom: 0.65rem; text-transform: uppercase;'>CERTIFICATIONS</div>{certs_html}" if certs_html else ""}
                        {f"<div style='border: 1.5px solid #0F172A; text-align: center; font-weight: 900; font-size: 0.76rem; letter-spacing: 0.08em; padding: 3px 6px; margin-top: 1rem; margin-bottom: 0.65rem; text-transform: uppercase;'>HONORS & ACHIEVEMENTS</div>{ach_html}" if ach_html else ""}
                        {f"<div style='border: 1.5px solid #0F172A; text-align: center; font-weight: 900; font-size: 0.76rem; letter-spacing: 0.08em; padding: 3px 6px; margin-top: 1rem; margin-bottom: 0.65rem; text-transform: uppercase;'>ADDITIONAL</div>{cust_html}" if cust_html else ""}
                    </div>
                    <div>
                        <div style="border: 1.5px solid #0F172A; text-align: center; font-weight: 900; font-size: 0.76rem; letter-spacing: 0.08em; padding: 3px 6px; margin-bottom: 0.65rem; text-transform: uppercase;">CONTACT</div>
                        {contact_html}

                        <div style="border: 1.5px solid #0F172A; text-align: center; font-weight: 900; font-size: 0.76rem; letter-spacing: 0.08em; padding: 3px 6px; margin-bottom: 0.65rem; text-transform: uppercase;">EDUCATION</div>
                        {edu_html or "<div style='font-size:0.75rem; color:#94A3B8; font-style:italic;'>No education listed.</div>"}

                        <div style="border: 1.5px solid #0F172A; text-align: center; font-weight: 900; font-size: 0.76rem; letter-spacing: 0.08em; padding: 3px 6px; margin-bottom: 0.65rem; text-transform: uppercase;">SKILLS & COMPETENCIES</div>
                        {skills_html}

                        {f"<div style='border: 1.5px solid #0F172A; text-align: center; font-weight: 900; font-size: 0.76rem; letter-spacing: 0.08em; padding: 3px 6px; margin-top: 1rem; margin-bottom: 0.65rem; text-transform: uppercase;'>REFERENCES</div>{refs_html}" if refs_html else ""}
                    </div>
                </div>
                <div style="text-align: center; font-size: 0.72rem; color: #94A3B8; margin-top: 1.5rem; border-top: 1px solid #E2E8F0; padding-top: 0.5rem;">Page 1 of 1</div>
            </div>"""
        else:
            # Multi-page presentation: Page 1 and Page 2
            p1_exp = experiences[:2]
            p2_exp = experiences[2:]
            return f"""<div>
                <!-- PAGE 1 -->
                <div class="resume-paper-page">
                    <div style="text-align: center; margin-bottom: 1.25rem;">
                        <div style="font-size: 1.65rem; font-weight: 900; color: #0F172A; letter-spacing: 0.04em; text-transform: uppercase;">{disp_name}</div>
                        <div style="font-size: 0.88rem; font-weight: 800; color: #7965D8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.65rem;">— {disp_title} —</div>
                        {f"<div style='font-size: 0.78rem; color: #334155; line-height: 1.55; max-width: 90%; margin: auto;'>{disp_summary}</div>" if disp_summary else ""}
                    </div>
                    <div style="display: grid; grid-template-columns: 58% 42%; gap: 1.25rem; border-top: 1.5px solid #0F172A; padding-top: 1rem;">
                        <div>
                            <div style="border: 1.5px solid #0F172A; text-align: center; font-weight: 900; font-size: 0.76rem; letter-spacing: 0.08em; padding: 3px 6px; margin-bottom: 0.65rem; text-transform: uppercase;">PROJECTS</div>
                            {render_puffin_proj(projects) or "<div style='font-size:0.75rem; color:#94A3B8; font-style:italic;'>No projects added.</div>"}

                            <div style="border: 1.5px solid #0F172A; text-align: center; font-weight: 900; font-size: 0.76rem; letter-spacing: 0.08em; padding: 3px 6px; margin-top: 1rem; margin-bottom: 0.65rem; text-transform: uppercase;">WORK EXPERIENCE</div>
                            {render_puffin_exp(p1_exp) or "<div style='font-size:0.75rem; color:#94A3B8; font-style:italic;'>No experience added.</div>"}
                        </div>
                        <div>
                            <div style="border: 1.5px solid #0F172A; text-align: center; font-weight: 900; font-size: 0.76rem; letter-spacing: 0.08em; padding: 3px 6px; margin-bottom: 0.65rem; text-transform: uppercase;">CONTACT</div>
                            {contact_html}

                            <div style="border: 1.5px solid #0F172A; text-align: center; font-weight: 900; font-size: 0.76rem; letter-spacing: 0.08em; padding: 3px 6px; margin-bottom: 0.65rem; text-transform: uppercase;">EDUCATION</div>
                            {edu_html or "<div style='font-size:0.75rem; color:#94A3B8; font-style:italic;'>No education listed.</div>"}
                        </div>
                    </div>
                    <div style="text-align: center; font-size: 0.72rem; color: #94A3B8; margin-top: 2rem; border-top: 1px solid #E2E8F0; padding-top: 0.5rem;">Page 1 of 2</div>
                </div>

                <!-- PAGE BREAK DIVIDER -->
                <div style="display:flex; align-items:center; justify-content:center; margin:1.5rem 0; gap:1rem;">
                    <div style="flex:1; height:1px; background:#34343D;"></div>
                    <span style="font-size:0.76rem; font-weight:700; color:#7965D8; background:#1C1C22; border:1px solid #7965D8; padding:4px 12px; border-radius:9999px;">📄 Page Break — Page 2</span>
                    <div style="flex:1; height:1px; background:#34343D;"></div>
                </div>

                <!-- PAGE 2 -->
                <div class="resume-paper-page">
                    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1.5px solid #0F172A; padding-bottom:0.5rem; margin-bottom:1rem;">
                        <span style="font-weight:800; font-size:0.88rem; color:#0F172A; text-transform:uppercase;">{disp_name} — Resume (Page 2)</span>
                        <span style="font-size:0.78rem; color:#7965D8; font-weight:700;">{disp_title}</span>
                    </div>
                    <div style="display: grid; grid-template-columns: 58% 42%; gap: 1.25rem;">
                        <div>
                            {f"<div style='border: 1.5px solid #0F172A; text-align: center; font-weight: 900; font-size: 0.76rem; letter-spacing: 0.08em; padding: 3px 6px; margin-bottom: 0.65rem; text-transform: uppercase;'>WORK EXPERIENCE (CONT.)</div>{render_puffin_exp(p2_exp)}" if p2_exp else ""}
                            {f"<div style='border: 1.5px solid #0F172A; text-align: center; font-weight: 900; font-size: 0.76rem; letter-spacing: 0.08em; padding: 3px 6px; margin-bottom: 0.65rem; text-transform: uppercase;'>CERTIFICATIONS</div>{certs_html}" if certs_html else ""}
                            {f"<div style='border: 1.5px solid #0F172A; text-align: center; font-weight: 900; font-size: 0.76rem; letter-spacing: 0.08em; padding: 3px 6px; margin-top: 0.85rem; margin-bottom: 0.65rem; text-transform: uppercase;'>HONORS & ACHIEVEMENTS</div>{ach_html}" if ach_html else ""}
                            {f"<div style='border: 1.5px solid #0F172A; text-align: center; font-weight: 900; font-size: 0.76rem; letter-spacing: 0.08em; padding: 3px 6px; margin-top: 0.85rem; margin-bottom: 0.65rem; text-transform: uppercase;'>ADDITIONAL</div>{cust_html}" if cust_html else ""}
                        </div>
                        <div>
                            <div style="border: 1.5px solid #0F172A; text-align: center; font-weight: 900; font-size: 0.76rem; letter-spacing: 0.08em; padding: 3px 6px; margin-bottom: 0.65rem; text-transform: uppercase;">SKILLS & COMPETENCIES</div>
                            {skills_html}

                            {f"<div style='border: 1.5px solid #0F172A; text-align: center; font-weight: 900; font-size: 0.76rem; letter-spacing: 0.08em; padding: 3px 6px; margin-top: 1rem; margin-bottom: 0.65rem; text-transform: uppercase;'>REFERENCES</div>{refs_html}" if refs_html else ""}
                        </div>
                    </div>
                    <div style="text-align: center; font-size: 0.72rem; color: #94A3B8; margin-top: 2rem; border-top: 1px solid #E2E8F0; padding-top: 0.5rem;">Page 2 of 2</div>
                </div>
            </div>"""

    # -------------------------------------------------------------------------
    # TEMPLATE 2: CADDISFLY (Clean ATS Single Column)
    # -------------------------------------------------------------------------
    elif template_id == "caddisfly":
        exp_rows = "".join(f"<div style='margin-bottom:0.75rem;'><div style='display:flex; justify-content:space-between; font-weight:700; color:#0F172A;'><span>{e.get('role')} — {e.get('company')}</span><span>{e.get('duration')}</span></div><div style='font-size:0.75rem; color:#475569;'>• {', '.join(e.get('responsibilities', []))}</div></div>" for e in experiences)
        proj_rows = "".join(f"<div style='margin-bottom:0.75rem;'><div style='font-weight:700; color:#0F172A;'>{p.get('title')} <span style='font-weight:400; color:#7965D8;'>({p.get('technologies')})</span></div><div style='font-size:0.75rem; color:#475569;'>{p.get('description')}</div></div>" for p in projects)
        edu_rows = "".join(f"<div style='display:flex; justify-content:space-between; margin-bottom:0.4rem;'><span style='font-weight:700;'>{ed.get('degree')} · {ed.get('institution')}</span><span>{ed.get('period')}</span></div>" for ed in educations)
        sk_tags = "".join(render_skill_badge(s) for s in skills)
        certs_rows = "".join(f"<div>• <strong>{c.get('name')}</strong> — {c.get('issuer')} ({c.get('issue_date') or c.get('year')})</div>" for c in certifications)

        return f"""<div class="resume-paper-page">
            <div style="border-bottom: 2px solid #1E293B; padding-bottom: 0.75rem; margin-bottom: 1rem;">
                <div style="font-size: 1.55rem; font-weight: 900; color: #1E293B; text-transform: uppercase;">{disp_name}</div>
                <div style="font-size: 0.82rem; color: #475569; margin-top: 3px;">
                    {disp_title} · {disp_loc} · {disp_phone} · {disp_email}
                </div>
            </div>
            {f"<div style='background: #F8FAFC; border-left: 3px solid #7965D8; padding: 6px 10px; font-size: 0.78rem; color: #334155; margin-bottom: 1rem;'><strong>Summary:</strong> {disp_summary}</div>" if disp_summary else ""}

            <div style="font-size: 0.84rem; font-weight: 800; text-transform: uppercase; color: #1E293B; border-bottom: 1px solid #CBD5E1; padding-bottom: 2px; margin-bottom: 0.65rem;">Work Experience & Internships</div>
            <div style="font-size: 0.78rem; color: #334155; margin-bottom: 1.25rem;">{exp_rows or "No experience listed."}</div>

            <div style="font-size: 0.84rem; font-weight: 800; text-transform: uppercase; color: #1E293B; border-bottom: 1px solid #CBD5E1; padding-bottom: 2px; margin-bottom: 0.65rem;">Technical Projects</div>
            <div style="font-size: 0.78rem; color: #334155; margin-bottom: 1.25rem;">{proj_rows or "No projects listed."}</div>

            <div style="font-size: 0.84rem; font-weight: 800; text-transform: uppercase; color: #1E293B; border-bottom: 1px solid #CBD5E1; padding-bottom: 2px; margin-bottom: 0.65rem;">Education & Credentials</div>
            <div style="font-size: 0.78rem; color: #334155; margin-bottom: 1.25rem;">{edu_rows or "No education listed."}</div>

            <div style="font-size: 0.84rem; font-weight: 800; text-transform: uppercase; color: #1E293B; border-bottom: 1px solid #CBD5E1; padding-bottom: 2px; margin-bottom: 0.65rem;">Core Competencies</div>
            <div style="margin-bottom: 1.25rem;">{sk_tags or "No skills listed."}</div>

            {f"<div style='font-size: 0.84rem; font-weight: 800; text-transform: uppercase; color: #1E293B; border-bottom: 1px solid #CBD5E1; padding-bottom: 2px; margin-bottom: 0.65rem;'>Certifications</div><div style='font-size: 0.78rem; color: #334155; margin-bottom: 1.25rem;'>{certs_rows}</div>" if certs_rows else ""}
            <div style="text-align: center; font-size: 0.72rem; color: #94A3B8; margin-top: 1.5rem; border-top: 1px solid #E2E8F0; padding-top: 0.5rem;">Page 1 of 1</div>
        </div>"""

    # -------------------------------------------------------------------------
    # TEMPLATE 3 & 4: SAHANI & MAYFLY (Executive Navy & Minimalist)
    # -------------------------------------------------------------------------
    else:
        sk_tags = "".join(render_skill_badge(s) for s in skills)
        return f"""<div class="resume-paper-page">
            <div style="background: #0B2545; color: #FFFFFF; border-radius: 4px; padding: 1.25rem 1.5rem; margin-bottom: 1.25rem; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="font-size: 1.6rem; font-weight: 900; letter-spacing: 0.02em;">{disp_name}</div>
                    <div style="font-size: 0.84rem; color: #94A3B8; margin-top: 2px;">{disp_title} · {disp_loc} · {disp_email}</div>
                </div>
                <div style="width: 52px; height: 52px; border-radius: 50%; background: #7965D8; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 1.1rem; color: #FFFFFF;">
                    {disp_name[:2].upper()}
                </div>
            </div>
            {f"<div style='background: #F1F5F9; border-left: 3px solid #0B2545; padding: 6px 12px; font-size: 0.78rem; color: #334155; margin-bottom: 1rem;'><strong>Executive Summary:</strong> {disp_summary}</div>" if disp_summary else ""}

            <div style="background: #0B2545; color: #FFFFFF; font-weight: 700; font-size: 0.76rem; padding: 3px 8px; border-radius: 2px; margin-bottom: 0.5rem; text-transform: uppercase;">EXPERIENCE & ACHIEVEMENTS</div>
            <div style="font-size: 0.78rem; color: #334155; margin-bottom: 1rem;">
                {"".join(f"<div style='margin-bottom:0.5rem;'><div style='font-weight:700;'>{e.get('role')} — {e.get('company')} ({e.get('duration')})</div><div>• {', '.join(e.get('responsibilities', []))}</div></div>" for e in experiences) or "No experience listed."}
            </div>

            <div style="background: #0B2545; color: #FFFFFF; font-weight: 700; font-size: 0.76rem; padding: 3px 8px; border-radius: 2px; margin-bottom: 0.5rem; text-transform: uppercase;">PROJECTS & INITIATIVES</div>
            <div style="font-size: 0.78rem; color: #334155; margin-bottom: 1rem;">
                {"".join(f"<div style='margin-bottom:0.5rem;'><div style='font-weight:700;'>{p.get('title')} ({p.get('technologies')})</div><div>{p.get('description')}</div></div>" for p in projects) or "No projects listed."}
            </div>

            <div style="background: #0B2545; color: #FFFFFF; font-weight: 700; font-size: 0.76rem; padding: 3px 8px; border-radius: 2px; margin-bottom: 0.5rem; text-transform: uppercase;">EDUCATION & SKILLS</div>
            <div style="font-size: 0.78rem; color: #334155;">
                {"".join(f"<div>{ed.get('degree')} · {ed.get('institution')} ({ed.get('period')})</div>" for ed in educations) or "No education listed."}
                <div style="margin-top: 0.65rem;">{sk_tags}</div>
            </div>
            <div style="text-align: center; font-size: 0.72rem; color: #94A3B8; margin-top: 1.5rem; border-top: 1px solid #E2E8F0; padding-top: 0.5rem;">Page 1 of 1</div>
        </div>"""


def render_resume_editor_screen(
    user_id: int,
    current_selected: str,
    resume_data: dict[str, Any],
    pdf_bytes: bytes,
    clean_filename: str,
) -> None:
    """Renders Step B: Two-panel Resume Editor.
    
    Left Panel: 50% width dedicated category editor with persistent bottom navigation.
    Right Panel: 50% width live resume document preview with download PDF header.
    """
    selected_tmpl_obj = next((t for t in TEMPLATES if t["id"] == current_selected), TEMPLATES[0])

    # Category step tracking: 1 to 10 in exact specified order
    current_step = st.session_state.get("resume_category_step", 1)
    if not isinstance(current_step, int) or current_step < 1 or current_step > 10:
        current_step = 1
        st.session_state["resume_category_step"] = 1

    step_info = next((s for s in CATEGORY_STEPS if s["step"] == current_step), CATEGORY_STEPS[0])
    strength_pct = calculate_resume_strength(resume_data)
    fn_default = resume_data.get("filename") or f"{resume_data.get('first_name', '')}_{resume_data.get('last_name', '')}_Resume".strip("_") or "TalentSphere_Resume"

    col_editor, col_preview = st.columns([1.0, 1.0], gap="large")

    # =========================================================================
    # LEFT PANEL: 50% RESUME EDITOR (ONE CATEGORY AT A TIME)
    # =========================================================================
    with col_editor:
        # Top Header: Step progress and Content Strength
        step_pct = current_step * 10
        render_progress_bar(f"🚀 Resume Progress ({step_pct}% Complete) — Step {current_step} of 10", step_pct, color_scheme="cyan" if step_pct >= 70 else "pink")
        render_progress_bar(f"📊 {strength_pct}% Strength", strength_pct, color_scheme="cyan" if strength_pct >= 70 else "pink")

        render_html(f"""<div style="display:flex; justify-content:space-between; align-items:center; margin-top:0.6rem; margin-bottom:0.25rem;">
            <div style="font-size:1.15rem; font-weight:800; color:#FFFFFF;">
                {step_info['icon']} Step {current_step} of 10: {step_info['title']}
            </div>
            <div style="font-size:0.78rem; font-weight:700; color:#7965D8; background:rgba(121,101,216,0.18); border:1px solid #7965D8; padding:2px 10px; border-radius:9999px;">
                {step_pct}% Complete
            </div>
        </div>
        <div class="res-sec-desc">{step_info['description']}</div>""")

        # Clickable Step Progress Indicators (1 to 10)
        pill_cols = st.columns(10)
        for p_idx, p_step in enumerate(CATEGORY_STEPS, start=1):
            with pill_cols[p_idx - 1]:
                is_curr = (p_idx == current_step)
                if st.button(
                    f"{p_idx}",
                    key=f"btn_step_pill_{p_idx}",
                    type="primary" if is_curr else "secondary",
                    help=f"Step {p_idx}: {p_step['title']}",
                    use_container_width=True,
                ):
                    services.core.save_resume_draft(user_id, resume_data, current_selected)
                    st.session_state["resume_category_step"] = p_idx
                    st.rerun()

        render_html("<div style='height: 10px;'></div>")

        # ---------------------------------------------------------------------
        # MAIN EDITING AREA: CURRENT CATEGORY'S FORM ONLY
        # ---------------------------------------------------------------------
        with st.container():
            # STEP 1: PERSONAL DETAILS
            if current_step == 1:
                if selected_tmpl_obj.get("supports_photo", False):
                    render_html("""<div style="background: rgba(121, 101, 216, 0.12); border: 1px solid #7965D8; border-radius: 8px; padding: 0.75rem 1rem; margin-bottom: 1rem;">
                        <div style="font-size: 0.82rem; font-weight: 700; color: #FFFFFF;">📷 Template Supports Profile Photo</div>
                        <div style="font-size: 0.76rem; color: #C4C4D0; margin-top: 2px;">The selected template includes an executive headshot display.</div>
                    </div>""")
                    uploaded_photo = st.file_uploader(
                        "Upload Headshot Photo (JPG or PNG)",
                        type=["jpg", "jpeg", "png"],
                        key="uploader_profile_headshot",
                    )
                    if uploaded_photo:
                        resume_data["profile_photo"] = uploaded_photo.name
                        st.toast("Profile photo attached to resume!", icon="📸")
                else:
                    render_html(f"""<div style="background: #16161D; border: 1px solid #34343D; border-radius: 8px; padding: 0.75rem 1rem; margin-bottom: 1rem;">
                        <div style="font-size: 0.82rem; font-weight: 700; color: #FFFFFF;">ℹ️ Photo-Free ATS Layout</div>
                        <div style="font-size: 0.76rem; color: #C4C4D0;">'{selected_tmpl_obj['name']}' omits photos for 100% ATS compliance. To include a photo, choose Sahani.</div>
                    </div>""")

                resume_data["job_title"] = st.text_input(
                    "Current Job Title",
                    value=resume_data.get("job_title", ""),
                    placeholder="e.g. Senior Software Engineer",
                    key="in_res_title",
                )

                c_fn, c_ln = st.columns(2)
                with c_fn:
                    resume_data["first_name"] = st.text_input(
                        "First Name",
                        value=resume_data.get("first_name", ""),
                        placeholder="First name",
                        key="in_res_fn",
                    )
                with c_ln:
                    resume_data["last_name"] = st.text_input(
                        "Last Name",
                        value=resume_data.get("last_name", ""),
                        placeholder="Last name",
                        key="in_res_ln",
                    )

                c_em, c_ph = st.columns(2)
                with c_em:
                    resume_data["email"] = st.text_input(
                        "Email Address",
                        value=resume_data.get("email", ""),
                        placeholder="name@example.com",
                        key="in_res_em",
                    )
                with c_ph:
                    resume_data["phone"] = st.text_input(
                        "Phone Number",
                        value=resume_data.get("phone", ""),
                        placeholder="+1 (555) 012-3456",
                        key="in_res_ph",
                    )

                c_ci, c_co = st.columns(2)
                with c_ci:
                    city_val = resume_data.get("city", "")
                    if not city_val and resume_data.get("location"):
                        city_val = resume_data.get("location", "").split(",")[0].strip()
                    resume_data["city"] = st.text_input(
                        "City",
                        value=city_val,
                        placeholder="e.g. Austin or Bangalore",
                        key="in_res_city",
                    )
                with c_co:
                    country_val = resume_data.get("country", "")
                    if not country_val and resume_data.get("location") and "," in resume_data.get("location", ""):
                        country_val = resume_data.get("location", "").split(",")[1].strip()
                    resume_data["country"] = st.text_input(
                        "Country",
                        value=country_val,
                        placeholder="e.g. United States or India",
                        key="in_res_country",
                    )

                loc_combined = f"{resume_data.get('city', '')}, {resume_data.get('country', '')}".strip(", ")
                if loc_combined:
                    resume_data["location"] = loc_combined

                c_li, c_po = st.columns(2)
                with c_li:
                    resume_data["linkedin"] = st.text_input(
                        "LinkedIn URL (Optional)",
                        value=resume_data.get("linkedin", ""),
                        placeholder="linkedin.com/in/username",
                        key="in_res_li",
                    )
                with c_po:
                    resume_data["portfolio"] = st.text_input(
                        "Portfolio / GitHub URL (Optional)",
                        value=resume_data.get("portfolio", ""),
                        placeholder="github.com/username or portfolio.me",
                        key="in_res_port",
                    )

            # STEP 2: PROFESSIONAL SUMMARY
            elif current_step == 2:
                current_summary = resume_data.get("summary", "")
                char_count = len(current_summary)

                render_html(f"""<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <div style="font-size:0.82rem; color:#C4C4D0;">Craft a powerful career statement highlighting core capabilities.</div>
                    <div style="font-size: 0.78rem; font-weight: 700; color: {'#22C55E' if 100 <= char_count <= 600 else '#C4C4D0'};">
                        {char_count} / 600 characters
                    </div>
                </div>""")

                resume_data["summary"] = st.text_area(
                    "Professional Summary",
                    value=current_summary,
                    height=140,
                    key="in_res_summary",
                    placeholder="Accomplished professional with a track record of driving scalable architectures, measurable cost efficiencies, and cross-functional leadership...",
                    label_visibility="collapsed",
                )

                c_ai_btn, _ = st.columns([2, 1])
                with c_ai_btn:
                    if st.button("✨ AI Enhance / Polish Summary", key="btn_ai_enhance_summary", use_container_width=True):
                        st.session_state["show_ai_summary_suggestions"] = not st.session_state.get("show_ai_summary_suggestions", False)

                if st.session_state.get("show_ai_summary_suggestions", False):
                    with st.container(border=True):
                        render_html("""<div style="font-size: 0.84rem; font-weight: 700; color: #FFFFFF; margin-bottom: 0.4rem;">
                            🤖 Suggested ATS-Optimized Variations
                        </div>""")
                        role_str = resume_data.get("job_title", "Software Professional")
                        opt1 = f"Dynamic and results-focused {role_str} with extensive experience architecting high-performance solutions, streamlining operational workflows, and aligning cross-functional teams to exceed business objectives."
                        opt2 = f"Accomplished {role_str} recognized for robust technical execution, automated pipelines, and measurable delivery. Proven background in designing secure, scalable systems with rapid time-to-market."

                        st.markdown(f"**Option 1 (Executive & Impact):**\n\n> {opt1}")
                        if st.button("Apply Option 1", key="btn_apply_ai_opt1"):
                            resume_data["summary"] = opt1
                            st.session_state["show_ai_summary_suggestions"] = False
                            st.rerun()

                        st.markdown(f"**Option 2 (Technical & Systems):**\n\n> {opt2}")
                        if st.button("Apply Option 2", key="btn_apply_ai_opt2"):
                            resume_data["summary"] = opt2
                            st.session_state["show_ai_summary_suggestions"] = False
                            st.rerun()

            # STEP 3: WORK EXPERIENCE
            elif current_step == 3:
                experiences = resume_data.get("experience", [])
                if not isinstance(experiences, list):
                    experiences = []

                for i, exp in enumerate(experiences):
                    if isinstance(exp, dict):
                        with st.container(border=True):
                            c_e_title, c_e_dup, c_e_del = st.columns([3.5, 0.9, 0.9])
                            with c_e_title:
                                exp["role"] = st.text_input(
                                    f"Job Title #{i+1}",
                                    value=exp.get("role") or exp.get("title", ""),
                                    placeholder="e.g. Senior Software Engineer",
                                    key=f"e_role_{i}",
                                )
                            with c_e_dup:
                                render_html("<div style='height: 28px;'></div>")
                                if st.button("📋", key=f"btn_dup_exp_{i}", help="Duplicate experience"):
                                    experiences.insert(i + 1, copy.deepcopy(exp))
                                    resume_data["experience"] = experiences
                                    st.rerun()
                            with c_e_del:
                                render_html("<div style='height: 28px;'></div>")
                                if st.button("🗑️", key=f"btn_del_exp_{i}", help="Delete experience"):
                                    experiences.pop(i)
                                    resume_data["experience"] = experiences
                                    st.rerun()

                            c_e_comp, c_e_type = st.columns(2)
                            with c_e_comp:
                                exp["company"] = st.text_input("Company / Organization", value=exp.get("company", ""), key=f"e_comp_{i}")
                            with c_e_type:
                                type_opts = ["Full-time", "Part-time", "Internship", "Contract", "Freelance"]
                                curr_type = exp.get("employment_type", "Full-time")
                                t_idx = type_opts.index(curr_type) if curr_type in type_opts else 0
                                exp["employment_type"] = st.selectbox("Employment Type", options=type_opts, index=t_idx, key=f"e_type_{i}")

                            c_e_sd, c_e_ed, c_e_cur = st.columns([1.5, 1.5, 1.2])
                            with c_e_sd:
                                exp["start_date"] = st.text_input("Start Date", value=exp.get("start_date", "06/2022"), key=f"e_sd_{i}")
                            with c_e_ed:
                                is_working = exp.get("current", False)
                                exp["end_date"] = st.text_input("End Date", value=exp.get("end_date", "Present"), disabled=is_working, key=f"e_ed_{i}")
                            with c_e_cur:
                                render_html("<div style='height: 30px;'></div>")
                                exp["current"] = st.checkbox("Currently Working Here", value=exp.get("current", False), key=f"e_cur_{i}")

                            exp["location"] = st.text_input("Location", value=exp.get("location", "Remote"), key=f"e_loc_{i}")
                            dur_str = f"{exp.get('start_date', '')} – {'Present' if exp.get('current') else exp.get('end_date', '')}".strip(" –")
                            exp["duration"] = dur_str

                            resp_val = exp.get("responsibilities") or exp.get("highlights", [])
                            resp_text = "\n".join(resp_val) if isinstance(resp_val, list) else str(resp_val)
                            new_resp = st.text_area(
                                "Key Responsibilities and Measurable Achievements (one per line)",
                                value=resp_text,
                                height=90,
                                placeholder="• Spearheaded automated test integration reducing defect escape rate by 40%.\n• Mentored a team of 4 junior developers.",
                                key=f"e_resp_{i}",
                            )
                            exp["responsibilities"] = [l.strip().lstrip("•- ") for l in new_resp.splitlines() if l.strip()]

                with st.expander("✨ AI Action Verbs & Bullet Enhancer", expanded=False):
                    st.caption("Copy high-impact, quantifiable bullet templates into your roles:")
                    st.markdown("""
- **Impact & Scale:** *Spearheaded the redesign of core services, decreasing latency by 35% and supporting 2M+ active daily queries.*
- **Optimization:** *Automated CI/CD validation pipelines, reducing release deployment cycle times from 4 hours to 18 minutes.*
- **Leadership:** *Mentored 5 junior engineers and established architectural review standards across 3 agile squads.*
                    """)

                if st.button("➕ Add Experience / Internship", key="btn_add_experience", type="primary", use_container_width=True):
                    experiences.append({
                        "role": "Software Developer Intern",
                        "company": "Tech Corp",
                        "employment_type": "Internship",
                        "location": "Remote",
                        "start_date": "06/2023",
                        "end_date": "12/2023",
                        "current": False,
                        "duration": "06/2023 – 12/2023",
                        "responsibilities": [
                            "Engineered feature enhancements in modern Python stack.",
                            "Collaborated in sprint rituals and automated CI/CD checks.",
                        ],
                    })
                    resume_data["experience"] = experiences
                    st.rerun()

            # STEP 4: EDUCATION
            elif current_step == 4:
                educations = resume_data.get("education", [])
                if not isinstance(educations, list):
                    educations = []

                for i, edu in enumerate(educations):
                    if isinstance(edu, dict):
                        with st.container(border=True):
                            c_ed_deg, c_ed_dup, c_ed_del = st.columns([3.5, 0.9, 0.9])
                            with c_ed_deg:
                                edu["degree"] = st.text_input(
                                    f"Degree / Qualification #{i+1}",
                                    value=edu.get("degree") or edu.get("qualification", ""),
                                    placeholder="e.g. B.Tech in Computer Science",
                                    key=f"ed_deg_{i}",
                                )
                            with c_ed_dup:
                                render_html("<div style='height: 28px;'></div>")
                                if st.button("📋", key=f"btn_dup_edu_{i}", help="Duplicate education"):
                                    educations.insert(i + 1, copy.deepcopy(edu))
                                    resume_data["education"] = educations
                                    st.rerun()
                            with c_ed_del:
                                render_html("<div style='height: 28px;'></div>")
                                if st.button("🗑️", key=f"btn_del_edu_{i}", help="Delete education"):
                                    educations.pop(i)
                                    resume_data["education"] = educations
                                    st.rerun()

                            c_ed_inst, c_ed_field = st.columns(2)
                            with c_ed_inst:
                                edu["institution"] = st.text_input("Institution Name", value=edu.get("institution", ""), key=f"ed_inst_{i}")
                            with c_ed_field:
                                edu["field_of_study"] = st.text_input("Field of Study", value=edu.get("field_of_study", ""), placeholder="e.g. Artificial Intelligence", key=f"ed_field_{i}")

                            c_ed_sd, c_ed_ed, c_ed_cur = st.columns([1.5, 1.5, 1.2])
                            with c_ed_sd:
                                edu["start_date"] = st.text_input("Start Date", value=edu.get("start_date", "2020"), key=f"ed_sd_{i}")
                            with c_ed_ed:
                                is_studying = edu.get("current", False)
                                edu["end_date"] = st.text_input("Graduation Date", value=edu.get("end_date", "2024"), disabled=is_studying, key=f"ed_ed_{i}")
                            with c_ed_cur:
                                render_html("<div style='height: 30px;'></div>")
                                edu["current"] = st.checkbox("Currently Studying", value=edu.get("current", False), key=f"ed_cur_{i}")

                            per_str = f"{edu.get('start_date', '')} – {'Present' if edu.get('current') else edu.get('end_date', '')}".strip(" –")
                            edu["period"] = per_str

                            c_ed_loc, c_ed_gpa = st.columns(2)
                            with c_ed_loc:
                                edu["location"] = st.text_input("Location", value=edu.get("location", ""), placeholder="e.g. Boston, MA", key=f"ed_loc_{i}")
                            with c_ed_gpa:
                                edu["academic_info"] = st.text_input("Grade / CGPA / Honors", value=edu.get("academic_info") or edu.get("honors", ""), placeholder="e.g. 3.9 / 4.0 or First Class with Distinction", key=f"ed_gpa_{i}")

                            edu["description"] = st.text_area(
                                "Additional Academic Details (Optional)",
                                value=edu.get("description", ""),
                                height=60,
                                placeholder="Dean's Honor List, relevant coursework, thesis topic...",
                                key=f"ed_desc_{i}",
                            )

                if st.button("➕ Add Education", key="btn_add_education", type="primary", use_container_width=True):
                    educations.append({
                        "degree": "Bachelor of Technology",
                        "field_of_study": "Computer Science & Engineering",
                        "institution": "State University",
                        "location": "Boston, MA",
                        "start_date": "2020",
                        "end_date": "2024",
                        "current": False,
                        "period": "2020 – 2024",
                        "academic_info": "First Class with Distinction",
                        "description": "",
                    })
                    resume_data["education"] = educations
                    st.rerun()

            # STEP 5: TECHNICAL AND PROFESSIONAL SKILLS
            elif current_step == 5:
                skills = resume_data.get("skills", [])
                if not isinstance(skills, list):
                    skills = []

                tgl_show_prof = st.toggle(
                    "Include proficiency levels on exported resume PDF & preview",
                    value=resume_data.get("show_skill_proficiency", True),
                    key="tgl_skill_prof_export",
                    help="Switch off to hide proficiency tags from the resume while preserving your saved proficiency data.",
                )
                resume_data["show_skill_proficiency"] = tgl_show_prof

                render_html("<div style='height: 8px;'></div>")

                c_sk_name, c_sk_cat, c_sk_add = st.columns([2.6, 1.8, 1.2], gap="medium")
                with c_sk_name:
                    input_nonce = st.session_state.get("skill_input_nonce", 0)
                    new_sk_name = st.text_input(
                        "Skill Name",
                        placeholder="e.g. Python, React, Docker, Machine Learning",
                        key=f"txt_add_skill_{input_nonce}",
                    )
                with c_sk_cat:
                    cat_options = ["Technical Skills", "Professional Skills", "Soft Skills", "Tools & Frameworks", "Leadership"]
                    saved_cat_idx = st.session_state.get("last_skill_cat_idx", 0)
                    new_sk_cat = st.selectbox(
                        "Category",
                        options=cat_options,
                        index=saved_cat_idx if saved_cat_idx < len(cat_options) else 0,
                        key="sel_add_skill_cat",
                    )
                with c_sk_add:
                    render_html("<div class='add-skill-btn-marker'></div>")
                    if st.button("➕ Add Skill", key="btn_add_single_skill", type="primary", use_container_width=True):
                        val = new_sk_name.strip()
                        if not val:
                            st.error("Please enter a skill name before clicking Add.")
                        elif any(s.get("name", "").strip().lower() == val.lower() for s in skills if isinstance(s, dict)):
                            st.warning(f"Skill '{val}' is already present in your skills list.")
                        else:
                            skills.append({
                                "name": val,
                                "category": new_sk_cat,
                                "proficiency": "Experienced",
                            })
                            resume_data["skills"] = skills
                            st.session_state["skill_input_nonce"] = input_nonce + 1
                            st.session_state["last_skill_cat_idx"] = cat_options.index(new_sk_cat)
                            st.toast(f"Added skill '{val}' under {new_sk_cat}!", icon="✅")
                            st.rerun()

                with st.expander("✨ AI Recommended Skills for your Role", expanded=False):
                    role_hint = resume_data.get("job_title", "Software Engineer")
                    st.caption(f"Curated top competencies based on target title: **{role_hint}**")
                    ai_rec_skills = [
                        {"name": "System Architecture", "category": "Technical Skills", "proficiency": "Advanced"},
                        {"name": "CI/CD & DevOps", "category": "Tools & Frameworks", "proficiency": "Experienced"},
                        {"name": "Cloud Computing (AWS/GCP)", "category": "Technical Skills", "proficiency": "Experienced"},
                        {"name": "Cross-Functional Collaboration", "category": "Leadership", "proficiency": "Expert"},
                    ]
                    rec_cols = st.columns(len(ai_rec_skills))
                    for r_idx, r_sk in enumerate(ai_rec_skills):
                        with rec_cols[r_idx]:
                            if st.button(f"+ {r_sk['name']}", key=f"btn_add_ai_rec_skill_{r_idx}", use_container_width=True):
                                if not any(s.get("name", "").lower() == r_sk["name"].lower() for s in skills if isinstance(s, dict)):
                                    skills.append(copy.deepcopy(r_sk))
                                    resume_data["skills"] = skills
                                    st.toast(f"Added {r_sk['name']} to skills!", icon="✨")
                                    st.rerun()

                if skills:
                    render_html("<div style='height: 12px;'></div>")
                    for i, sk in enumerate(skills):
                        if isinstance(sk, dict):
                            s_name = sk.get("name", "Skill")
                            s_cat = sk.get("category", "Technical")
                            curr_prof = sk.get("proficiency", "Experienced")

                            mapping = {"Intermediate": "Experienced", "Novice": "Beginner", "Proficient": "Skillful", "Master": "Expert"}
                            if curr_prof in mapping:
                                curr_prof = mapping[curr_prof]
                                sk["proficiency"] = curr_prof
                            elif curr_prof not in [p["level"] for p in PROFICIENCY_LEVELS]:
                                curr_prof = "Experienced"
                                sk["proficiency"] = curr_prof

                            curr_step_idx = next((p["step"] for p in PROFICIENCY_LEVELS if p["level"] == curr_prof), 3)
                            active_color = next((p["color"] for p in PROFICIENCY_LEVELS if p["level"] == curr_prof), "#22C55E")

                            with st.container(border=True):
                                c_card_top, c_sdup, c_sdel = st.columns([5.2, 0.6, 0.6])
                                with c_card_top:
                                    render_html(f"""<div style="display: flex; align-items: center; gap: 0.65rem; min-width: 0; flex-wrap: wrap;">
                                        <span style="font-weight: 800; font-size: 1rem; color: #FFFFFF;">{s_name}</span>
                                        <span style="background: #24242F; color: #E0E0EA; border: 1px solid #34343D; font-size: 0.70rem; font-weight: 700; padding: 2px 8px; border-radius: 9999px;">{s_cat}</span>
                                    </div>""")
                                with c_sdup:
                                    if st.button("📋", key=f"btn_dup_sk_{i}", help=f"Duplicate {s_name}"):
                                        skills.insert(i + 1, copy.deepcopy(sk))
                                        resume_data["skills"] = skills
                                        st.rerun()
                                with c_sdel:
                                    if st.button("🗑️", key=f"btn_del_sk_{i}", help=f"Remove {s_name}"):
                                        skills.pop(i)
                                        resume_data["skills"] = skills
                                        st.rerun()

                                c_txt, c1, c2, c3, c4, c5, _ = st.columns([2.6, 0.4, 0.4, 0.4, 0.4, 0.4, 2.0], gap="small")
                                with c_txt:
                                    render_html(f"""<div style="font-size: 0.86rem; font-weight: 600; color: #E0E0EA; display: flex; align-items: center; min-height: 28px;">
                                        Proficiency Level:&nbsp;<span style="color: {active_color}; font-weight: 800;">{curr_prof}</span>
                                    </div>""")

                                circ_cols = [c1, c2, c3, c4, c5]
                                for lvl_idx, p_data in enumerate(PROFICIENCY_LEVELS, start=1):
                                    with circ_cols[lvl_idx - 1]:
                                        is_lit = (lvl_idx <= curr_step_idx)
                                        render_html(f"""<div class="circ-marker circ-lvl-{lvl_idx} {'circ-lit' if is_lit else 'circ-unlit'}">
                                            <span class="circ-tooltip">{p_data['level']}</span>
                                        </div>""")
                                        if st.button("●", key=f"btn_circ_{i}_{lvl_idx}"):
                                            sk["proficiency"] = p_data["level"]
                                            resume_data["skills"] = skills
                                            st.rerun()

            # STEP 6: PROJECTS
            elif current_step == 6:
                projects = resume_data.get("projects", [])
                if not isinstance(projects, list):
                    projects = []

                for i, pr in enumerate(projects):
                    if isinstance(pr, dict):
                        with st.container(border=True):
                            c_p_title, c_p_dup, c_p_del = st.columns([3.5, 0.9, 0.9])
                            with c_p_title:
                                pr["title"] = st.text_input(
                                    f"Project Name #{i+1}",
                                    value=pr.get("title") or pr.get("name", ""),
                                    placeholder="e.g. Distributed Event Pipeline",
                                    key=f"p_title_{i}",
                                )
                            with c_p_dup:
                                render_html("<div style='height: 28px;'></div>")
                                if st.button("📋", key=f"btn_dup_proj_{i}", help="Duplicate project"):
                                    projects.insert(i + 1, copy.deepcopy(pr))
                                    resume_data["projects"] = projects
                                    st.rerun()
                            with c_p_del:
                                render_html("<div style='height: 28px;'></div>")
                                if st.button("🗑️", key=f"btn_del_proj_{i}", help="Delete project"):
                                    projects.pop(i)
                                    resume_data["projects"] = projects
                                    st.rerun()

                            c_org, c_url = st.columns(2)
                            with c_org:
                                pr["organization"] = st.text_input(
                                    "Associated Organization / Context",
                                    value=pr.get("organization", ""),
                                    placeholder="e.g. TalentSphere or Open Source",
                                    key=f"p_org_{i}",
                                )
                            with c_url:
                                pr["url"] = st.text_input(
                                    "Project Link / Repository URL",
                                    value=pr.get("url") or pr.get("link", ""),
                                    placeholder="https://github.com/...",
                                    key=f"p_url_{i}",
                                )

                            c_sd, c_ed, c_cur = st.columns([1.5, 1.5, 1.2])
                            with c_sd:
                                pr["start_date"] = st.text_input("Start Date", value=pr.get("start_date", "01/2023"), key=f"p_sd_{i}")
                            with c_ed:
                                is_ong = pr.get("ongoing", False)
                                pr["end_date"] = st.text_input("End Date", value=pr.get("end_date", "06/2023"), disabled=is_ong, key=f"p_ed_{i}")
                            with c_cur:
                                render_html("<div style='height: 30px;'></div>")
                                pr["ongoing"] = st.checkbox("Ongoing", value=pr.get("ongoing", False), key=f"p_ong_{i}")

                            pr["technologies"] = st.text_input(
                                "Technologies Used",
                                value=pr.get("technologies", ""),
                                placeholder="e.g. Python, PyTorch, Docker, AWS",
                                key=f"p_tech_{i}",
                            )
                            pr["description"] = st.text_area(
                                "Description & Architecture",
                                value=pr.get("description", ""),
                                height=70,
                                placeholder="Engineered high-throughput data processing service with zero-downtime deployment...",
                                key=f"p_desc_{i}",
                            )
                            pr["contributions"] = st.text_input(
                                "Key Measurable Outcome / Impact",
                                value=pr.get("contributions", ""),
                                placeholder="e.g. Reduced processing latency by 45% and saved $12K monthly.",
                                key=f"p_contrib_{i}",
                            )

                with st.expander("✨ AI Project STAR Impact Polish", expanded=False):
                    st.caption("Proven STAR frameworks to showcase your engineering projects:")
                    st.markdown("""
- **Architecture & Performance:** *Architected event-driven microservices processing 15K req/sec with 99.99% uptime on AWS/Docker.*
- **Cost & Efficiency:** *Engineered automated resource reclamation daemon reducing monthly cloud infrastructure spend by 28%.*
- **Algorithmic Innovation:** *Implemented multi-tenant caching mechanism cutting database read throughput requirements by 50%.*
                    """)

                if st.button("➕ Add Project", key="btn_add_project", type="primary", use_container_width=True):
                    projects.append({
                        "title": "New High-Impact Project",
                        "organization": "Independent",
                        "url": "https://github.com/project",
                        "start_date": "01/2024",
                        "end_date": "06/2024",
                        "ongoing": False,
                        "technologies": "Python, Cloud, SQL",
                        "description": "Architected responsive and resilient backend service.",
                        "contributions": "Improved operational efficiency by 30%.",
                    })
                    resume_data["projects"] = projects
                    st.rerun()

            # STEP 7: CERTIFICATIONS
            elif current_step == 7:
                certs = resume_data.get("certifications", [])
                if not isinstance(certs, list):
                    certs = []

                show_add_cert = st.session_state.get(f"show_cert_form_{user_id}", False)

                if not show_add_cert:
                    if st.button("➕ Add Certification", key="btn_add_cert", type="primary", use_container_width=True):
                        st.session_state[f"show_cert_form_{user_id}"] = True
                        st.rerun()
                else:
                    with st.container(border=True):
                        render_html("""<div style="font-size: 1rem; font-weight: 800; color: #FFFFFF; margin-bottom: 0.75rem;">
                            Add New Certification
                        </div>""")
                        c_name_in = st.text_input("Certification Name *", placeholder="e.g. AWS Certified Solutions Architect", key="cert_in_name")
                        c_iss_in = st.text_input("Issuing Organization *", placeholder="e.g. Amazon Web Services", key="cert_in_issuer")

                        c_is_dt, c_ex_dt, c_no_ex = st.columns([1.5, 1.5, 1.3])
                        with c_is_dt:
                            c_issue_val = st.text_input("Issue Date", placeholder="e.g. 04/2023", key="cert_in_issue_dt")
                        with c_no_ex:
                            render_html("<div style='height: 30px;'></div>")
                            no_expiry = st.checkbox("Does Not Expire", value=False, key="cert_in_no_exp")
                        with c_ex_dt:
                            c_exp_val = st.text_input("Expiration Date", placeholder="e.g. 04/2026", disabled=no_expiry, key="cert_in_exp_dt")

                        c_cid, c_curl = st.columns(2)
                        with c_cid:
                            c_id_val = st.text_input("Credential ID (Optional)", placeholder="e.g. AWS-SEC-98214", key="cert_in_id")
                        with c_curl:
                            c_url_val = st.text_input("Credential URL (Optional)", placeholder="https://aws.amazon.com/verify/...", key="cert_in_url")

                        uploaded_cert_file = st.file_uploader(
                            "Upload Certificate (PDF, JPG, JPEG, or PNG)",
                            type=["pdf", "jpg", "jpeg", "png"],
                            key="uploader_cert_doc",
                            help="Maximum file size: 5 MB. Stored securely and privately.",
                        )

                        c_desc_val = st.text_area("Additional Description (Optional)", height=60, placeholder="Key skills covered...", key="cert_in_desc")

                        c_save_c, c_cancel_c = st.columns(2)
                        with c_save_c:
                            if st.button("💾 Save Certification", key="btn_save_new_cert", type="primary", use_container_width=True):
                                if not c_name_in.strip():
                                    st.error("Certification Name is required.")
                                elif not c_iss_in.strip():
                                    st.error("Issuing Organization is required.")
                                else:
                                    cert_entry = {
                                        "name": c_name_in.strip(),
                                        "issuer": c_iss_in.strip(),
                                        "issue_date": c_issue_val.strip(),
                                        "expiry_date": "No Expiration" if no_expiry else c_exp_val.strip(),
                                        "no_expiry": no_expiry,
                                        "year": c_issue_val.strip() or "2024",
                                        "credential_id": c_id_val.strip(),
                                        "credential_url": c_url_val.strip(),
                                        "description": c_desc_val.strip(),
                                    }

                                    if uploaded_cert_file:
                                        ok, msg, fmeta = save_certificate_file(user_id, uploaded_cert_file)
                                        if ok:
                                            cert_entry["certificate_file"] = fmeta["original_filename"]
                                            cert_entry["certificate_saved_path"] = fmeta["saved_filename"]
                                            cert_entry["certificate_type"] = fmeta["file_type"]
                                            cert_entry["certificate_size"] = fmeta["file_size"]
                                            st.toast(msg, icon="📎")
                                        else:
                                            st.error(msg)
                                            st.stop()

                                    certs.append(cert_entry)
                                    resume_data["certifications"] = certs
                                    st.session_state[f"show_cert_form_{user_id}"] = False
                                    st.rerun()

                        with c_cancel_c:
                            if st.button("Cancel", key="btn_cancel_new_cert", use_container_width=True):
                                st.session_state[f"show_cert_form_{user_id}"] = False
                                st.rerun()

                if certs:
                    render_html("<div style='height: 8px;'></div>")
                    for i, cr in enumerate(certs):
                        if isinstance(cr, dict):
                            with st.container(border=True):
                                c_ct, c_cdel = st.columns([4.2, 0.8])
                                with c_ct:
                                    c_name = cr.get("name", "Certification")
                                    c_iss = cr.get("issuer", "")
                                    c_dt = cr.get("issue_date") or str(cr.get("year", ""))
                                    c_exp = cr.get("expiry_date", "")
                                    c_link = cr.get("credential_url", "")
                                    c_file = cr.get("certificate_file", "")

                                    render_html(f"""<div style="font-weight: 800; font-size: 0.95rem; color: #FFFFFF;">{c_name}</div>
                                        <div style="font-size: 0.82rem; color: #C4C4D0; margin-top: 2px;">
                                            <strong>Issuer:</strong> {c_iss} &nbsp;·&nbsp; <strong>Issued:</strong> {c_dt} {f"&nbsp;·&nbsp; <strong>Expiry:</strong> {c_exp}" if c_exp else ""}
                                        </div>
                                        {f"<div style='font-size: 0.78rem; color: #7965D8; margin-top: 3px;'>🔗 <a href='{c_link}' target='_blank' style='color:#7965D8; text-decoration:none;'>{c_link}</a></div>" if c_link else ""}
                                        {f"<div style='font-size: 0.75rem; color: #22C55E; margin-top: 3px;'>📎 Verified Attachment: {c_file}</div>" if c_file else ""}
                                    """)
                                    if c_file and cr.get("certificate_saved_path"):
                                        if st.button("Remove Attached File", key=f"btn_rm_file_{i}"):
                                            delete_certificate_file(user_id, cr["certificate_saved_path"])
                                            cr["certificate_file"] = ""
                                            cr["certificate_saved_path"] = ""
                                            st.toast("Attached file removed.", icon="ℹ️")
                                            st.rerun()
                                with c_cdel:
                                    if st.button("🗑️", key=f"btn_del_saved_cert_{i}", help="Delete certification"):
                                        if cr.get("certificate_saved_path"):
                                            delete_certificate_file(user_id, cr["certificate_saved_path"])
                                        certs.pop(i)
                                        resume_data["certifications"] = certs
                                        st.rerun()

            # STEP 8: ACHIEVEMENTS
            elif current_step == 8:
                achievements = resume_data.get("achievements", [])
                if not isinstance(achievements, list):
                    achievements = []

                for i, ach in enumerate(achievements):
                    if isinstance(ach, dict):
                        with st.container(border=True):
                            c_a_title, c_a_del = st.columns([4.2, 0.8])
                            with c_a_title:
                                ach["title"] = st.text_input(f"Achievement Title #{i+1}", value=ach.get("title", ""), key=f"ach_t_{i}")
                            with c_a_del:
                                render_html("<div style='height: 28px;'></div>")
                                if st.button("🗑️", key=f"btn_del_ach_{i}", help="Delete achievement"):
                                    achievements.pop(i)
                                    resume_data["achievements"] = achievements
                                    st.rerun()

                            c_a_org, c_a_dt = st.columns(2)
                            with c_a_org:
                                ach["organization"] = st.text_input("Organization / Context", value=ach.get("organization") or ach.get("context", ""), key=f"ach_org_{i}")
                            with c_a_dt:
                                ach["date"] = st.text_input("Date", value=ach.get("date", "2024"), key=f"ach_dt_{i}")

                            ach["description"] = st.text_area(
                                "Description",
                                value=ach.get("description", ""),
                                height=60,
                                placeholder="Ranked 1st place out of 120 teams in automated systems challenge...",
                                key=f"ach_desc_{i}",
                            )

                if st.button("➕ Add Achievement", key="btn_add_achievement", type="primary", use_container_width=True):
                    achievements.append({
                        "title": "National Hackathon 1st Place Winner",
                        "organization": "Infosys Tech League",
                        "date": "2024",
                        "description": "Architected low-latency AI analytics dashboard within 48 hours.",
                    })
                    resume_data["achievements"] = achievements
                    st.rerun()

            # STEP 9: REFERENCES
            elif current_step == 9:
                references = resume_data.get("references", [])
                if not isinstance(references, list):
                    references = []

                for i, ref in enumerate(references):
                    if isinstance(ref, dict):
                        with st.container(border=True):
                            c_r_name, c_r_del = st.columns([4.2, 0.8])
                            with c_r_name:
                                ref["name"] = st.text_input(f"Reference Name #{i+1}", value=ref.get("name", ""), key=f"ref_n_{i}")
                            with c_r_del:
                                render_html("<div style='height: 28px;'></div>")
                                if st.button("🗑️", key=f"btn_del_ref_{i}", help="Delete reference"):
                                    references.pop(i)
                                    resume_data["references"] = references
                                    st.rerun()

                            c_r_des, c_r_org = st.columns(2)
                            with c_r_des:
                                ref["designation"] = st.text_input("Designation / Title", value=ref.get("designation") or ref.get("title", ""), key=f"ref_des_{i}")
                            with c_r_org:
                                ref["organization"] = st.text_input("Organization", value=ref.get("organization", ""), key=f"ref_org_{i}")

                            ref["contact_info"] = st.text_input("Contact Information (Email / Phone)", value=ref.get("contact_info", ""), key=f"ref_cnt_{i}")
                            ref["notes"] = st.text_input("Optional Notes", value=ref.get("notes", ""), placeholder="e.g. Former Direct Supervisor", key=f"ref_note_{i}")

                            c_priv, c_inc = st.columns(2)
                            with c_priv:
                                ref["include_contact_details"] = st.checkbox("Include contact details on resume", value=ref.get("include_contact_details", False), key=f"ref_priv_{i}")
                            with c_inc:
                                ref["include_in_resume"] = st.checkbox("Include reference on resume", value=ref.get("include_in_resume", True), key=f"ref_inc_{i}")

                if st.button("➕ Add Reference", key="btn_add_reference", type="primary", use_container_width=True):
                    references.append({
                        "name": "Dr. Sarah Jenkins",
                        "designation": "Director of Engineering",
                        "organization": "Infosys Elevate",
                        "contact_info": "s.jenkins@example.com",
                        "notes": "Direct Manager",
                        "include_contact_details": False,
                        "include_in_resume": True,
                    })
                    resume_data["references"] = references
                    st.rerun()

            # STEP 10: CUSTOM SECTIONS
            elif current_step == 10:
                custom_sections = resume_data.get("custom_sections", [])
                if not isinstance(custom_sections, list):
                    custom_sections = []

                for idx, sec in enumerate(custom_sections):
                    if isinstance(sec, dict):
                        with st.container(border=True):
                            c_cs_title, c_cs_inc, c_cs_del = st.columns([3.5, 1.5, 0.8])
                            with c_cs_title:
                                sec["title"] = st.text_input(
                                    f"Custom Section #{idx+1} Title",
                                    value=sec.get("title", "Custom Section"),
                                    key=f"cs_title_{idx}",
                                )
                            with c_cs_inc:
                                render_html("<div style='height: 28px;'></div>")
                                sec["include_in_resume"] = st.checkbox(
                                    "Include in PDF",
                                    value=sec.get("include_in_resume", True),
                                    key=f"cs_inc_{idx}",
                                )
                            with c_cs_del:
                                render_html("<div style='height: 28px;'></div>")
                                if st.button("🗑️", key=f"btn_del_cs_{idx}", help="Remove custom section"):
                                    custom_sections.pop(idx)
                                    resume_data["custom_sections"] = custom_sections
                                    st.rerun()

                            entries = sec.setdefault("entries", [])
                            for e_idx, ent in enumerate(entries):
                                c_e1, c_e2, c_edel = st.columns([3, 2, 0.6])
                                with c_e1:
                                    ent["title"] = st.text_input(f"Item #{e_idx+1} Title", value=ent.get("title", ""), key=f"cs_ent_t_{idx}_{e_idx}")
                                with c_e2:
                                    ent["date"] = st.text_input(f"Date / Subtitle", value=ent.get("date", ""), key=f"cs_ent_d_{idx}_{e_idx}")
                                with c_edel:
                                    render_html("<div style='height: 28px;'></div>")
                                    if st.button("🗑️", key=f"btn_del_cs_ent_{idx}_{e_idx}"):
                                        entries.pop(e_idx)
                                        st.rerun()
                                ent["description"] = st.text_area(
                                    "Description",
                                    value=ent.get("description", ""),
                                    height=55,
                                    key=f"cs_ent_desc_{idx}_{e_idx}",
                                )

                            if st.button("➕ Add Entry to this Section", key=f"btn_add_cs_ent_{idx}"):
                                entries.append({"title": "New Item", "date": "2024", "description": ""})
                                st.rerun()

                c_cat_cs, c_add_cs = st.columns([3, 2], gap="medium")
                with c_cat_cs:
                    cs_cat_choice = st.selectbox(
                        "Category",
                        options=["Others", "Certifications", "Achievements", "References"],
                        key="sel_new_cs_cat",
                        help="Select a built-in category to open its dedicated section, or choose Others to create a custom section.",
                    )
                with c_add_cs:
                    render_html("<div class='add-cs-btn-marker'></div>")
                    if st.button("➕ Add Custom Section", key="btn_add_custom_section", type="primary", use_container_width=True):
                        if cs_cat_choice == "Certifications":
                            st.session_state["resume_category_step"] = 7
                            st.session_state[f"show_cert_form_{user_id}"] = True
                            st.toast("Navigating to Certifications (Step 7)...", icon="📜")
                            st.rerun()
                        elif cs_cat_choice == "Achievements":
                            st.session_state["resume_category_step"] = 8
                            resume_data.setdefault("achievements", []).append({
                                "title": "New Achievement",
                                "organization": "",
                                "date": "2024",
                                "description": "",
                            })
                            st.toast("Navigating to Achievements (Step 8)...", icon="🏆")
                            st.rerun()
                        elif cs_cat_choice == "References":
                            st.session_state["resume_category_step"] = 9
                            resume_data.setdefault("references", []).append({
                                "name": "New Reference",
                                "designation": "",
                                "organization": "",
                                "contact_info": "",
                                "notes": "",
                                "include_contact_details": False,
                                "include_in_resume": True,
                            })
                            st.toast("Navigating to References (Step 9)...", icon="👥")
                            st.rerun()
                        else:
                            custom_sections.append({
                                "id": str(uuid.uuid4()),
                                "title": "Volunteer & Community Leadership",
                                "category": "Others",
                                "include_in_resume": True,
                                "entries": [{
                                    "title": "Lead Coordinator",
                                    "date": "2024",
                                    "description": "Organized community technology workshops.",
                                }],
                            })
                            resume_data["custom_sections"] = custom_sections
                            st.rerun()

        # ---------------------------------------------------------------------
        # PERSISTENT BOTTOM NAVIGATION BAR
        # ---------------------------------------------------------------------
        with st.container():
            render_html("<div class='bottom-nav-container'></div>")
            c_b_back, c_b_mid, c_b_next = st.columns([1.2, 2.6, 1.4], gap="small")
            with c_b_back:
                if current_step > 1:
                    if st.button("⬅️ Back", key="btn_step_back", use_container_width=True):
                        services.core.save_resume_draft(user_id, resume_data, current_selected)
                        st.session_state["resume_category_step"] = current_step - 1
                        st.rerun()
                else:
                    st.button("⬅️ Back", key="btn_step_back_disabled", disabled=True, use_container_width=True)

            with c_b_mid:
                render_html(f"""<div style="text-align: center; font-size: 0.86rem; font-weight: 700; color: #FFFFFF; line-height: 24px;">
                    Step <span style="color: #7965D8;">{current_step}</span> of 10
                </div>""")
                if st.button("💾 Save Draft", key="btn_save_resume_draft", use_container_width=True):
                    services.core.save_resume_draft(user_id, resume_data, current_selected)
                    st.toast("Resume draft saved successfully to your account!", icon="✅")

            with c_b_next:
                if current_step < 10:
                    if st.button("Next ➡️", key="btn_step_next", type="primary", use_container_width=True):
                        services.core.save_resume_draft(user_id, resume_data, current_selected)
                        st.session_state["resume_category_step"] = current_step + 1
                        st.rerun()
                else:
                    if st.button("🎉 Finish & Review", key="btn_step_finish", type="primary", use_container_width=True):
                        services.core.save_resume_draft(user_id, resume_data, current_selected)
                        st.toast("🎉 Resume complete! Your draft is saved. You can download the PDF on the right.", icon="✅")

        # Auxiliary profile actions
        render_html("<div style='height: 10px;'></div>")
        c_reset_draft, c_sync_prof = st.columns(2)
        with c_reset_draft:
            if st.button("🔄 Reset to Profile", key="btn_reset_resume_draft", use_container_width=True):
                fresh = services.core.get_resume_draft(user_id)["resume_data"]
                st.session_state[f"resume_active_data_{user_id}"] = fresh
                st.toast("Restored fresh data from master profile.", icon="ℹ️")
                st.rerun()
        with c_sync_prof:
            if st.button("📥 Apply to Profile", key="btn_sync_master_prof", help="Sync resume info back to master profile", use_container_width=True):
                prof_updates = {
                    "job_title": resume_data.get("job_title", ""),
                    "phone": resume_data.get("phone", ""),
                    "location": resume_data.get("location", ""),
                    "summary": resume_data.get("summary", ""),
                    "linkedin": resume_data.get("linkedin", ""),
                    "portfolio": resume_data.get("portfolio", ""),
                    "education": resume_data.get("education", []),
                    "experience": resume_data.get("experience", []),
                    "projects": resume_data.get("projects", []),
                    "certifications": resume_data.get("certifications", []),
                }
                services.core.save_profile(user_id, prof_updates)
                st.toast("Master profile updated with resume details!", icon="🎉")

    # =========================================================================
    # RIGHT PANEL: 50% LIVE DOCUMENT PREVIEW
    # =========================================================================
    with col_preview:
        # Compact Preview Header
        c_prev_head, c_prev_fn, c_prev_dl = st.columns([1.1, 1.8, 1.5], gap="small")
        with c_prev_head:
            render_html(f"""<div style="font-size: 0.90rem; font-weight: 700; color: #FFFFFF; display: flex; align-items: center; height: 38px;">
                📄 Live A4 Preview <span style="font-size: 0.72rem; color: #7965D8; margin-left: 6px; font-weight: 600;">({selected_tmpl_obj['name']})</span>
            </div>""")
        with c_prev_fn:
            new_fn = st.text_input(
                "Resume Filename",
                value=resume_data.get("filename") or clean_filename,
                key="txt_topbar_resume_filename",
                label_visibility="collapsed",
                help="Rename your exported PDF file",
            )
            if new_fn and new_fn != resume_data.get("filename"):
                resume_data["filename"] = new_fn
        with c_prev_dl:
            st.download_button(
                label="⬇️ Download ATS Resume PDF",
                data=pdf_bytes,
                file_name=f"{clean_filename}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True,
                key="btn_download_ats_pdf",
            )

        # White paper-like resume page against dark or purple-tinted backdrop
        preview_html = generate_live_preview_html(resume_data, current_selected)
        render_html(f"""<div class="preview-panel-scroll">
            {preview_html}
        </div>""")


# =============================================================================
# MAIN RESUME BUILDER PAGE ROUTER & CONTROLLER
# =============================================================================
def render_resume_builder_page() -> None:
    """Renders the comprehensive Resume Builder with dark theme and high contrast."""
    uid = st.session_state.get("user_id")
    if not uid:
        st.error("Please sign in to access Resume Builder.")
        st.stop()

    # Load or initialize user resume draft
    draft_meta = services.core.get_resume_draft(uid)
    state_key = f"resume_active_data_{uid}"
    if state_key not in st.session_state:
        st.session_state[state_key] = draft_meta["resume_data"]

    resume_data = st.session_state[state_key]

    # Selected template tracking
    selected_tmpl = st.session_state.get("resume_selected_template", draft_meta.get("selected_template", "puffin"))
    st.session_state["resume_selected_template"] = selected_tmpl

    # Dynamic filename handling
    fn_default = resume_data.get("filename") or f"{resume_data.get('first_name', '')}_{resume_data.get('last_name', '')}_Resume".strip("_") or "TalentSphere_Resume"
    resume_data["filename"] = fn_default

    # Calculate resume strength
    strength_pct = calculate_resume_strength(resume_data)

    # Pre-generate PDF for instant download readiness
    pdf_bytes = generate_resume_pdf(resume_data, template_id=selected_tmpl)
    clean_filename = re.sub(r"[^a-zA-Z0-9_\-]", "_", fn_default).strip("_") or "Resume"

    # =========================================================================
    # COMPREHENSIVE DARK THEME CSS INJECTION
    # =========================================================================
    st.markdown(
        """
        <style>
        /* 1. Main Canvas & Fonts - Natural Scrolling Architecture */
        div[data-testid="stAppViewContainer"] {
            background-color: #111111 !important;
            color: #FFFFFF !important;
            overflow-y: auto !important;
            overflow-x: hidden !important;
            height: 100vh !important;
        }
        section[data-testid="stMain"] {
            background-color: #111111 !important;
            color: #FFFFFF !important;
            overflow-y: visible !important;
            min-height: 100vh !important;
        }
        div[data-testid="stMainBlockContainer"] {
            background-color: transparent !important;
            color: #FFFFFF !important;
            max-width: 100% !important;
            padding-top: 1rem !important;
            padding-bottom: 3rem !important;
            overflow: visible !important;
        }

        /* 2. Sidebar Alignment - Natural Flow */
        section[data-testid="stSidebar"] {
            overflow-y: auto !important;
        }

        /* 3. Section Containers & Streamlit Expanders */
        div[data-testid="stExpander"] {
            background-color: #1C1C22 !important;
            border: 1px solid #34343D !important;
            border-radius: 12px !important;
            margin-bottom: 0.95rem !important;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35) !important;
            overflow: hidden !important;
        }
        div[data-testid="stExpander"] details {
            background-color: #1C1C22 !important;
            border-radius: 12px !important;
        }
        div[data-testid="stExpander"] summary {
            background-color: #1C1C22 !important;
            color: #FFFFFF !important;
            border-radius: 12px !important;
            padding: 0.85rem 1.15rem !important;
            font-size: 1.02rem !important;
            font-weight: 700 !important;
            border-bottom: 1px solid transparent !important;
            transition: all 0.2s ease !important;
        }
        div[data-testid="stExpander"] summary:hover {
            background-color: #24242D !important;
            color: #FFFFFF !important;
        }
        div[data-testid="stExpander"] details[open] > summary {
            border-bottom: 1px solid #34343D !important;
            border-bottom-left-radius: 0 !important;
            border-bottom-right-radius: 0 !important;
            background-color: #1C1C22 !important;
            color: #FFFFFF !important;
        }
        div[data-testid="stExpander"] summary p,
        div[data-testid="stExpander"] summary span {
            color: #FFFFFF !important;
            font-weight: 700 !important;
            font-size: 1.02rem !important;
        }
        div[data-testid="stExpander"] summary svg {
            fill: #C4C4D0 !important;
            stroke: #C4C4D0 !important;
        }
        div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
            background-color: #1C1C22 !important;
            padding: 1.15rem 1.25rem !important;
            color: #E0E0EA !important;
        }

        /* 4. Bordered Sub-containers */
        div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #16161D !important;
            border: 1px solid #34343D !important;
            border-radius: 10px !important;
            padding: 0.85rem !important;
            margin-bottom: 0.75rem !important;
        }

        /* 5. Form Input Controls */
        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stDateInput"] input {
            background-color: #191919 !important;
            color: #FFFFFF !important;
            border: 1px solid #34343D !important;
            border-radius: 8px !important;
            font-size: 0.92rem !important;
            padding: 0.6rem 0.85rem !important;
        }
        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stTextArea"] textarea:focus,
        div[data-testid="stNumberInput"] input:focus,
        div[data-testid="stDateInput"] input:focus {
            border-color: #7965D8 !important;
            box-shadow: 0 0 0 2px rgba(121, 101, 216, 0.3) !important;
            outline: none !important;
        }
        div[data-testid="stTextInput"] input::placeholder,
        div[data-testid="stTextArea"] textarea::placeholder {
            color: #A0A0AD !important;
            opacity: 0.95 !important;
        }

        /* 6. Form Input Labels */
        div[data-testid="stTextInput"] label,
        div[data-testid="stTextArea"] label,
        div[data-testid="stSelectbox"] label,
        div[data-testid="stNumberInput"] label,
        div[data-testid="stDateInput"] label,
        div[data-testid="stFileUploader"] label,
        div[data-testid="stCheckbox"] label,
        div[data-testid="stToggle"] label {
            color: #E0E0EA !important;
            font-size: 0.88rem !important;
            font-weight: 600 !important;
        }
        div[data-testid="stTextInput"] label p,
        div[data-testid="stTextArea"] label p,
        div[data-testid="stSelectbox"] label p,
        div[data-testid="stNumberInput"] label p,
        div[data-testid="stDateInput"] label p,
        div[data-testid="stFileUploader"] label p,
        div[data-testid="stCheckbox"] label p,
        div[data-testid="stToggle"] label p {
            color: #E0E0EA !important;
            font-size: 0.88rem !important;
            font-weight: 600 !important;
        }

        /* 7. Dropdown Selectbox */
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            background-color: #191919 !important;
            border: 1px solid #34343D !important;
            border-radius: 8px !important;
            color: #FFFFFF !important;
        }
        div[data-testid="stSelectbox"] div[data-baseweb="select"] span {
            color: #FFFFFF !important;
        }
        div[data-testid="stSelectbox"] svg {
            fill: #C4C4D0 !important;
        }
        div[data-baseweb="popover"],
        div[data-baseweb="menu"],
        ul[role="listbox"] {
            background-color: #1C1C22 !important;
            border: 1px solid #34343D !important;
            border-radius: 8px !important;
        }
        li[role="option"] {
            background-color: #1C1C22 !important;
            color: #FFFFFF !important;
        }
        li[role="option"]:hover,
        li[aria-selected="true"] {
            background-color: #7965D8 !important;
            color: #FFFFFF !important;
        }

        /* 8. Buttons: Primary (#7965D8 purple) & Secondary (#1C1C22 charcoal) */
        button[kind="primary"],
        button[data-testid="stBaseButton-primary"],
        div.stButton > button[kind="primary"],
        div.stDownloadButton > button[kind="primary"] {
            background-color: #7965D8 !important;
            color: #FFFFFF !important;
            border: 1px solid #7965D8 !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            font-size: 0.92rem !important;
            padding: 0.6rem 1.25rem !important;
            box-shadow: 0 4px 14px rgba(121, 101, 216, 0.35) !important;
            transition: all 0.2s ease !important;
        }
        button[kind="primary"]:hover,
        button[data-testid="stBaseButton-primary"]:hover,
        div.stButton > button[kind="primary"]:hover,
        div.stDownloadButton > button[kind="primary"]:hover {
            background-color: #6854C4 !important;
            border-color: #6854C4 !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 18px rgba(121, 101, 216, 0.45) !important;
        }
        button[kind="secondary"],
        button[data-testid="stBaseButton-secondary"],
        div.stButton > button[kind="secondary"],
        div.stDownloadButton > button[kind="secondary"] {
            background-color: #1C1C22 !important;
            color: #E0E0EA !important;
            border: 1px solid #34343D !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            font-size: 0.92rem !important;
            padding: 0.6rem 1.25rem !important;
            transition: all 0.2s ease !important;
        }
        button[kind="secondary"]:hover,
        button[data-testid="stBaseButton-secondary"]:hover,
        div.stButton > button[kind="secondary"]:hover,
        div.stDownloadButton > button[kind="secondary"]:hover {
            background-color: #282832 !important;
            color: #FFFFFF !important;
            border-color: #7965D8 !important;
        }

        /* 9. Skill row and custom section vertical alignment */
        div[data-testid="column"]:has(.add-skill-btn-marker),
        div[data-testid="column"]:has(.add-cs-btn-marker) {
            display: flex !important;
            flex-direction: column !important;
            justify-content: flex-end !important;
        }
        div[data-testid="column"]:has(.add-skill-btn-marker) button,
        div[data-testid="column"]:has(.add-cs-btn-marker) button {
            height: 44px !important;
            min-height: 44px !important;
            margin-top: 0 !important;
            margin-bottom: 0 !important;
            white-space: nowrap !important;
            font-size: 0.92rem !important;
        }

        /* 10. Five Compact Circular Proficiency Indicators */
        div[data-testid="column"]:has(.circ-marker) {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            min-width: 28px !important;
            max-width: 36px !important;
            padding: 0 !important;
            margin: 0 !important;
            position: relative !important;
        }
        div[data-testid="column"]:has(.circ-marker) .stButton {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            width: 24px !important;
            margin: 0 !important;
        }
        div[data-testid="column"]:has(.circ-marker) button[kind="secondary"],
        div[data-testid="column"]:has(.circ-marker) button[data-testid="stBaseButton-secondary"],
        div[data-testid="column"]:has(.circ-marker) button {
            width: 22px !important;
            height: 22px !important;
            min-width: 22px !important;
            min-height: 22px !important;
            max-width: 22px !important;
            max-height: 22px !important;
            border-radius: 50% !important;
            padding: 0 !important;
            margin: 0 !important;
            font-size: 0 !important;
            line-height: 0 !important;
            cursor: pointer !important;
            box-shadow: none !important;
            transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease !important;
        }

        /* Unlit state */
        div[data-testid="column"]:has(.circ-unlit) button {
            background-color: #22222B !important;
            border: 2px solid #34343D !important;
        }
        div[data-testid="column"]:has(.circ-unlit) button:hover {
            border-color: #7965D8 !important;
            transform: scale(1.15) !important;
        }

        /* Distinct color progression for lit states */
        div[data-testid="column"]:has(.circ-lvl-1.circ-lit) button {
            background-color: #60A5FA !important;
            border: 2px solid #60A5FA !important;
            box-shadow: 0 0 10px rgba(96, 165, 250, 0.5) !important;
        }
        div[data-testid="column"]:has(.circ-lvl-2.circ-lit) button {
            background-color: #2DD4BF !important;
            border: 2px solid #2DD4BF !important;
            box-shadow: 0 0 10px rgba(45, 212, 191, 0.5) !important;
        }
        div[data-testid="column"]:has(.circ-lvl-3.circ-lit) button {
            background-color: #22C55E !important;
            border: 2px solid #22C55E !important;
            box-shadow: 0 0 10px rgba(34, 197, 94, 0.5) !important;
        }
        div[data-testid="column"]:has(.circ-lvl-4.circ-lit) button {
            background-color: #A78BFA !important;
            border: 2px solid #A78BFA !important;
            box-shadow: 0 0 10px rgba(167, 139, 250, 0.5) !important;
        }
        div[data-testid="column"]:has(.circ-lvl-5.circ-lit) button {
            background-color: #FBBF24 !important;
            border: 2px solid #FBBF24 !important;
            box-shadow: 0 0 10px rgba(251, 191, 36, 0.5) !important;
        }
        div[data-testid="column"]:has(.circ-lit) button:hover {
            transform: scale(1.22) !important;
            filter: brightness(1.15) !important;
        }

        /* Tooltip styling - Only displays on hover or focus! */
        .circ-marker {
            display: block;
            width: 0;
            height: 0;
            position: relative;
        }
        .circ-tooltip {
            display: none;
            position: absolute;
            bottom: 30px;
            left: 11px;
            transform: translateX(-50%);
            background-color: #252530 !important;
            color: #FFFFFF !important;
            font-size: 0.74rem !important;
            font-weight: 600 !important;
            padding: 4px 9px !important;
            border-radius: 6px !important;
            border: 1px solid #454553 !important;
            white-space: nowrap !important;
            pointer-events: none !important;
            z-index: 99999 !important;
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.6) !important;
            opacity: 0;
            transition: opacity 0.15s ease-in-out;
        }
        div[data-testid="column"]:has(.circ-marker):hover .circ-tooltip,
        div[data-testid="column"]:has(.circ-marker):focus-within .circ-tooltip {
            display: block !important;
            opacity: 1 !important;
        }

        /* 11. File Uploaders */
        div[data-testid="stFileUploader"] section {
            background-color: #191919 !important;
            border: 1.5px dashed #34343D !important;
            border-radius: 10px !important;
            padding: 1.15rem !important;
        }
        div[data-testid="stFileUploader"] section:hover {
            border-color: #7965D8 !important;
        }
        div[data-testid="stFileUploader"] span,
        div[data-testid="stFileUploader"] small {
            color: #C4C4D0 !important;
        }

        /* 12. Checkboxes & Toggles */
        div[data-testid="stCheckbox"] label span,
        div[data-testid="stToggle"] label span {
            color: #E0E0EA !important;
        }

        /* 13. Tabs */
        div[data-testid="stTabs"] button[role="tab"] {
            color: #C4C4D0 !important;
            background: transparent !important;
            border-bottom: 2px solid transparent !important;
            font-weight: 600 !important;
            font-size: 0.92rem !important;
            padding: 0.65rem 1rem !important;
        }
        div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
            color: #FFFFFF !important;
            border-bottom: 2px solid #7965D8 !important;
        }

        /* 14. Toast Notifications & Status Banners (High Contrast Dark Theme) */
        div[data-testid="stToastContainer"] {
            position: fixed !important;
            top: 1.5rem !important;
            right: 1.5rem !important;
            z-index: 999999 !important;
            display: flex !important;
            flex-direction: column !important;
            gap: 0.75rem !important;
            max-width: 440px !important;
        }
        div[data-testid="stToast"],
        div.stToast {
            background-color: #252530 !important;
            color: #FFFFFF !important;
            border: 1px solid #454553 !important;
            border-radius: 10px !important;
            box-shadow: 0 10px 28px rgba(0, 0, 0, 0.65), 0 2px 8px rgba(0, 0, 0, 0.4) !important;
            padding: 0.85rem 1.15rem !important;
            min-width: 300px !important;
            max-width: 440px !important;
            word-wrap: break-word !important;
            overflow-wrap: break-word !important;
        }
        div[data-testid="stToast"] p,
        div[data-testid="stToastText"],
        div[data-testid="stToastText"] p,
        div.stToast p {
            color: #FFFFFF !important;
            font-size: 0.92rem !important;
            font-weight: 600 !important;
            line-height: 1.45 !important;
            margin: 0 !important;
            word-break: break-word !important;
            white-space: normal !important;
        }
        div[data-testid="stToast"] span,
        div[data-testid="stToast"] small {
            color: #D1D1DC !important;
        }
        div[data-testid="stToastDynamicIcon"],
        div[data-testid="stToast"] svg {
            color: #60A5FA !important;
            fill: #60A5FA !important;
            flex-shrink: 0 !important;
        }
        div[data-testid="stToast"] button,
        div.stToast button {
            color: #D1D1DC !important;
            background: transparent !important;
            border: none !important;
            padding: 2px !important;
            min-height: auto !important;
            height: auto !important;
            box-shadow: none !important;
            opacity: 0.85 !important;
            cursor: pointer !important;
        }
        div[data-testid="stToast"] button:hover,
        div.stToast button:hover {
            color: #FFFFFF !important;
            opacity: 1 !important;
            background: rgba(255, 255, 255, 0.12) !important;
        }

        /* 15. Alert Messages & Status Banners */
        div[data-testid="stAlert"] {
            background-color: #252530 !important;
            border: 1px solid #454553 !important;
            border-radius: 8px !important;
            color: #FFFFFF !important;
            padding: 0.75rem 1rem !important;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35) !important;
        }
        div[data-testid="stAlert"] p {
            color: #FFFFFF !important;
            font-size: 0.90rem !important;
            line-height: 1.45 !important;
        }
        div[data-testid="stAlert"] svg {
            fill: #60A5FA !important;
        }

        .editor-panel-scroll {
            max-height: calc(100vh - 220px);
            overflow-y: auto;
            padding-right: 6px;
        }
        .preview-panel-scroll {
            background-color: #14121E !important;
            border: 1px solid #34343D !important;
            border-radius: 12px !important;
            padding: 1.25rem !important;
            overflow-y: auto !important;
            max-height: calc(100vh - 165px) !important;
            overscroll-behavior: auto !important;
            box-shadow: inset 0 2px 14px rgba(0, 0, 0, 0.55), 0 8px 24px rgba(0,0,0,0.4) !important;
        }
        .resume-paper-page {
            background-color: #FFFFFF !important;
            color: #1E293B !important;
            border-radius: 4px !important;
            padding: 2.2rem 2.4rem !important;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6), 0 2px 8px rgba(0,0,0,0.3) !important;
            min-height: 960px !important;
            margin-bottom: 1.5rem !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
            box-sizing: border-box !important;
        }
        .bottom-nav-container {
            background-color: #1C1C22 !important;
            border-top: 1px solid #34343D !important;
            border-radius: 10px !important;
            padding: 0.85rem 1rem !important;
            margin-top: 1.25rem !important;
        }
        @media (max-width: 992px) {
            div[data-testid="column"] {
                width: 100% !important;
                flex: 1 1 100% !important;
                min-width: 100% !important;
            }
        }

        .res-sec-desc {
            color: #C4C4D0 !important;
            font-size: 0.84rem !important;
            margin-bottom: 0.75rem !important;
            line-height: 1.45 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # =========================================================================
    # UNIFIED TOP STUDIO NAVIGATION BAR (Templates vs Editor Switcher)
    # =========================================================================
    step_mode = st.session_state.get("resume_builder_step", "editor")
    c_top_info, c_top_nav = st.columns([4.5, 2.5])
    with c_top_info:
        render_html("""<div style="display:flex; align-items:center; gap:0.75rem;">
            <span style="font-size:1.15rem; font-weight:800; color:#FFFFFF;">TalentSphere Resume Studio</span>
            <span style="background:rgba(121,101,216,0.18); color:#7965D8; border:1px solid #7965D8; font-size:0.72rem; font-weight:700; padding:2px 8px; border-radius:9999px;">Two-Panel Live Workspace</span>
        </div>""")
    with c_top_nav:
        t_col1, t_col2 = st.columns(2)
        with t_col1:
            if st.button("🎨 Templates", key="nav_btn_step_a", type="primary" if step_mode == "template_select" else "secondary", use_container_width=True):
                st.session_state["resume_builder_step"] = "template_select"
                st.rerun()
        with t_col2:
            if st.button("✏️ Editor", key="nav_btn_step_b", type="primary" if step_mode == "editor" else "secondary", use_container_width=True):
                st.session_state["resume_builder_step"] = "editor"
                st.rerun()

    # Studio tabs: Editor, Document Ingestion, Keyword Alignment
    tab_main, tab_import, tab_keyword = st.tabs([
        "📄 Resume Studio & Editor",
        "📥 Import Document (PDF / DOCX)",
        "🎯 Role Keyword Alignment",
    ])

    with tab_main:
        active_step = st.session_state.get("resume_builder_step", "editor")
        if active_step == "template_select":
            render_template_selection_screen(uid, selected_tmpl, resume_data, pdf_bytes, clean_filename)
        else:
            render_resume_editor_screen(uid, selected_tmpl, resume_data, pdf_bytes, clean_filename)

    # =========================================================================
    # TAB 2: RESUME DOCUMENT INGESTION (.PDF, .DOCX)
    # =========================================================================
    with tab_import:
        with st.container(border=True):
            render_section_header(
                title="Import Existing Resume Document",
                subtitle="Extracts text and identifies prospective updates. Your master profile is NEVER overwritten automatically.",
                badge_text="Explicit Review Required",
                badge_type="warning",
            )

            render_demo_banner(
                "<strong>Safe Ingestion Guarantee:</strong> Uploading or extracting a resume does not modify your saved master profile. "
                "You must explicitly review and confirm any updates before they are committed to your database.",
                icon="🔒",
            )

            uploaded_file = st.file_uploader(
                "Upload Resume Document (PDF or DOCX)",
                type=["pdf", "docx"],
                key="resume_uploader_input",
                help="Accepts standard single or multi-page resumes in PDF or Word DOCX format.",
            )

            if uploaded_file:
                extracted_text = ""
                try:
                    if uploaded_file.name.lower().endswith(".pdf"):
                        if PdfReader:
                            reader = PdfReader(uploaded_file)
                            extracted_text = "\n".join(page.extract_text() or "" for page in reader.pages)
                        else:
                            st.error("pypdf library not available in runtime environment.")
                    else:
                        if Document:
                            doc = Document(uploaded_file)
                            extracted_text = "\n".join(p.text for p in doc.paragraphs if p.text)
                        else:
                            st.error("python-docx library not available in runtime environment.")

                    if extracted_text.strip():
                        st.session_state["extracted_resume_text"] = extracted_text.strip()
                        st.success(f"Successfully extracted {len(extracted_text.split())} words from {uploaded_file.name}!")
                    else:
                        st.warning("No readable text found in document. Please verify the document is not an image-only scan.")
                except Exception as exc:
                    st.error(f"Error reading {uploaded_file.name}: {exc}")

            extracted_text = st.session_state.get("extracted_resume_text", "")
            if extracted_text:
                st.text_area("Extracted Resume Content (Live Buffer)", value=extracted_text, height=220, key="txt_area_extracted")
                if st.button("💾 Save as Resume Draft Text Only", key="btn_save_resume_draft_text", use_container_width=True):
                    services.core.save_profile(uid, {"resume_text": extracted_text})
                    st.toast("Resume text saved for ATS keyword alignment review. Master profile unchanged.", icon="✅")

    # =========================================================================
    # TAB 3: TARGET ROLE KEYWORD ALIGNMENT
    # =========================================================================
    with tab_keyword:
        with st.container(border=True):
            user_prof = services.core.get_profile(uid)
            target_role = user_prof.get("target_role", "Senior Software Engineer")
            spec = services.core.ROLE_CATALOG.get(target_role, {})
            required_skills = spec.get("skills", {})

            render_section_header(
                title=f"ATS Keyword Matching vs. {target_role}",
                subtitle="Calculates keyword alignment between your resume text and official competencies for your target role.",
                badge_text="ATS Readiness",
                badge_type="teal",
            )

            editor_text = " ".join([
                resume_data.get("summary", ""),
                " ".join(s.get("name", "") if isinstance(s, dict) else str(s) for s in resume_data.get("skills", [])),
                " ".join(p.get("description", "") for p in resume_data.get("projects", []) if isinstance(p, dict)),
                user_prof.get("resume_text", ""),
            ]).lower()

            if not required_skills:
                st.info(f"Target role '{target_role}' has no preset skills catalog entry.")
            else:
                matched_keywords = [s for s in required_skills if s.lower() in editor_text]
                missing_keywords = [s for s in required_skills if s.lower() not in editor_text]
                score = round(100 * len(matched_keywords) / max(1, len(required_skills)))

                col_k1, col_k2, col_k3 = st.columns(3)
                with col_k1:
                    render_progress_bar("Target Keyword Match", score, color_scheme="cyan" if score >= 70 else "pink")
                with col_k2:
                    st.metric("Detected Keywords", f"{len(matched_keywords)} / {len(required_skills)}")
                with col_k3:
                    st.metric("Missing Role Keywords", f"{len(missing_keywords)}")
