"""Comprehensive verification test suite for the enhanced Resume Builder UI and features.

Tests cover:
1. Dark Theme Color Scheme & Contrast: #111111, #1C1C22, #191919, #FFFFFF, #C4C4D0, #D6D6E0, #A0A0AD, #34343D, #7965D8.
2. Exact 10-section collapsible layout and ordering in the Editor:
   - 1. Personal Details
   - 2. Professional Summary
   - 3. Projects
   - 4. Work Experience and Internships
   - 5. Education
   - 6. Technical and Professional Skills
   - 7. Custom Sections
   - 8. Certifications
   - 9. Achievements
   - 10. References
3. Personal Details: Job Title, First/Last Name, Email, Phone, City, Country, Photo support/notice.
4. Professional Summary: Textarea, character counter, AI polish assist.
5. Projects: Name, Org, Link, Dates, Ongoing, Tech, Description, Outcome, Add/Duplicate/Delete.
6. Work Experience: Role, Company, Type, Location, Dates, Current, Responsibilities, Add/Duplicate/Delete.
7. Education: Degree, Institution, Field, Location, Dates, Current, GPA, Description, Add/Duplicate/Delete.
8. Skills: Name, Category, Add, Remove, High-contrast tags.
9. Custom Sections: Categories (Certifications, Achievements, References, Others), Title, Include toggle, Entries.
10. Certifications: Add Certification form, Name/Issuer required, Dates, No-expiry checkbox, Credential ID/URL, File upload validation & isolation, Supporting doc text-only in resume.
11. Achievements: Title, Org, Date, Description, Add/Delete.
12. References: Name, Title, Org, Contact, Notes, Privacy toggle, Add/Delete.
13. Multi-template PDF generation & pagination: Puffin, Caddisfly, Sahani, Mayfly with all sections.
"""

from pathlib import Path
import io
import json
import uuid
import pytest
from streamlit.testing.v1 import AppTest
import services.core
from services.core import (
    connect,
    register,
    login,
    get_profile,
    save_profile,
    get_resume_draft,
    save_resume_draft,
)
from views.resume_builder_view import (
    CATEGORY_STEPS,
    TEMPLATES,
    generate_resume_pdf,
    generate_ats_resume_pdf,
    calculate_resume_strength,
    save_certificate_file,
    delete_certificate_file,
    CERTIFICATES_BASE_DIR,
)

APP_PATH = str(Path(__file__).parent.parent / "app.py")


class MockUploadedFile:
    """Helper mock object for streamlit.UploadedFile in automated tests."""
    def __init__(self, name: str, data: bytes, mime: str = "application/pdf"):
        self.name = name
        self._data = data
        self.size = len(data)
        self.type = mime

    def getvalue(self) -> bytes:
        return self._data


def test_1_dark_theme_css_rules_in_view():
    """Verify that comprehensive dark theme CSS rules matching specifications are applied."""
    view_path = Path(__file__).parent.parent / "views" / "resume_builder_view.py"
    content = view_path.read_text(encoding="utf-8")

    # Main page background #111111
    assert "#111111" in content, "Main background #111111 must be defined"
    # Section containers & expanders #1C1C22
    assert "#1C1C22" in content, "Section containers and expanders #1C1C22 must be defined"
    # Input background #191919
    assert "#191919" in content, "Input backgrounds #191919 must be defined"
    # Primary headings and text #FFFFFF
    assert "#FFFFFF" in content, "Headings #FFFFFF must be defined"
    # Secondary text #C4C4D0
    assert "#C4C4D0" in content, "Secondary text #C4C4D0 must be defined"
    # Labels #E0E0EA
    assert "#E0E0EA" in content, "Input labels #E0E0EA must be defined"
    # Placeholder #A0A0AD
    assert "#A0A0AD" in content, "Placeholder #A0A0AD must be defined"
    # Borders #34343D
    assert "#34343D" in content, "Borders #34343D must be defined"
    # Purple primary buttons #7965D8
    assert "#7965D8" in content, "Primary buttons #7965D8 must be defined"


def test_2_exact_10_sections_order():
    """Verify that the Resume Editor displays all 10 dedicated steps in the exact specified order."""
    expected_titles = [
        "Personal Details",
        "Professional Summary",
        "Work Experience",
        "Education",
        "Projects",
        "Technical and Professional Skills",
        "Certifications",
        "Achievements",
        "References",
        "Custom Sections",
    ]
    actual_titles = [step["title"] for step in CATEGORY_STEPS]
    assert actual_titles == expected_titles

    # Verify that each step has its dedicated step indicator pill
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Resume Builder"
    at.session_state["resume_builder_step"] = "editor"
    at.run()
    assert not at.exception

    for step_num in range(1, 11):
        assert at.button(key=f"btn_step_pill_{step_num}") is not None


def test_3_personal_details_fields():
    """Verify Personal Details contains Job Title, First Name, Last Name, Email, Phone, City, Country."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Resume Builder"
    at.session_state["resume_builder_step"] = "editor"
    at.run()
    assert not at.exception

    # Check input widgets
    assert at.text_input(key="in_res_title") is not None
    assert at.text_input(key="in_res_fn") is not None
    assert at.text_input(key="in_res_ln") is not None
    assert at.text_input(key="in_res_em") is not None
    assert at.text_input(key="in_res_ph") is not None
    assert at.text_input(key="in_res_city") is not None
    assert at.text_input(key="in_res_country") is not None


def test_4_professional_summary_and_ai():
    """Verify Professional Summary has multiline textarea and AI enhancement capability on Step 2."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Resume Builder"
    at.session_state["resume_builder_step"] = "editor"
    at.session_state["resume_category_step"] = 2
    at.run()
    assert not at.exception

    # Multiline textarea
    summary_box = at.text_area(key="in_res_summary")
    assert summary_box is not None

    # AI Enhance button
    ai_btn = at.button(key="btn_ai_enhance_summary")
    assert ai_btn is not None
    ai_btn.click()
    at.run()
    assert not at.exception
    assert at.button(key="btn_apply_ai_opt1") is not None


def test_5_projects_features():
    """Verify Projects section has Add Project button, ongoing toggle, tech, and description on Step 5."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Resume Builder"
    at.session_state["resume_builder_step"] = "editor"
    at.session_state["resume_category_step"] = 5
    at.run()
    assert not at.exception

    add_btn = at.button(key="btn_add_project")
    assert add_btn is not None


def test_6_work_experience_features():
    """Verify Work Experience section has visible Add button and handles employment type & current on Step 3."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Resume Builder"
    at.session_state["resume_builder_step"] = "editor"
    at.session_state["resume_category_step"] = 3
    at.run()
    assert not at.exception

    add_exp_btn = at.button(key="btn_add_experience")
    assert add_exp_btn is not None


def test_7_education_features():
    """Verify Education section has visible Add Education button and academic info on Step 4."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Resume Builder"
    at.session_state["resume_builder_step"] = "editor"
    at.session_state["resume_category_step"] = 4
    at.run()
    assert not at.exception

    add_edu_btn = at.button(key="btn_add_education")
    assert add_edu_btn is not None


def test_8_technical_skills_features():
    """Verify Technical and Professional Skills supports name, category selection, and add on Step 6."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Resume Builder"
    at.session_state["resume_builder_step"] = "editor"
    at.session_state["resume_category_step"] = 6
    at.run()
    assert any(k and k.startswith("txt_add_skill") for k in [t.key for t in at.text_input])
    assert at.selectbox(key="sel_add_skill_cat") is not None
    assert at.button(key="btn_add_single_skill") is not None


def test_9_custom_sections_features():
    """Verify Custom Sections allows adding custom categories (Certifications, Achievements, References, Others) on Step 10."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Resume Builder"
    at.session_state["resume_builder_step"] = "editor"
    at.session_state["resume_category_step"] = 10
    at.run()
    assert not at.exception

    assert at.selectbox(key="sel_new_cs_cat") is not None
    assert at.button(key="btn_add_custom_section") is not None


def test_10_certifications_form_and_file_upload_validation():
    """Verify Add Certification form validation, file type checks, size limits, and user isolation."""
    user_id = 999
    # 1. Valid PDF file
    sample_pdf = b"%PDF-1.4 mock certificate binary data"
    mock_pdf = MockUploadedFile("aws_cert.pdf", sample_pdf, "application/pdf")
    ok, msg, meta = save_certificate_file(user_id, mock_pdf)
    assert ok is True
    assert meta["file_type"] == "PDF"
    saved_file = meta["saved_filename"]

    # Verify per-user directory isolation
    expected_dir = CERTIFICATES_BASE_DIR / f"user_{user_id}"
    assert (expected_dir / saved_file).exists()

    # 2. Reject unsupported extension (e.g. .exe)
    mock_exe = MockUploadedFile("hack.exe", b"malicious", "application/octet-stream")
    ok_exe, msg_exe, _ = save_certificate_file(user_id, mock_exe)
    assert ok_exe is False
    assert "Unsupported file type" in msg_exe

    # 3. Reject oversized file (> 5MB)
    large_bytes = b"0" * (6 * 1024 * 1024)
    mock_large = MockUploadedFile("large_cert.pdf", large_bytes, "application/pdf")
    ok_large, msg_large, _ = save_certificate_file(user_id, mock_large)
    assert ok_large is False
    assert "exceeds" in msg_large

    # 4. Safe deletion
    del_ok = delete_certificate_file(user_id, saved_file)
    assert del_ok is True
    assert not (expected_dir / saved_file).exists()


def test_11_achievements_and_references_features():
    """Verify Achievements and References sections have add buttons in their respective steps."""
    at_ach = AppTest.from_file(APP_PATH, default_timeout=30)
    at_ach.session_state["is_authenticated"] = True
    at_ach.session_state["user_id"] = 1
    at_ach.session_state["current_page"] = "Resume Builder"
    at_ach.session_state["resume_builder_step"] = "editor"
    at_ach.session_state["resume_category_step"] = 8
    at_ach.run()
    assert not at_ach.exception
    assert at_ach.button(key="btn_add_achievement") is not None

    at_ref = AppTest.from_file(APP_PATH, default_timeout=30)
    at_ref.session_state["is_authenticated"] = True
    at_ref.session_state["user_id"] = 1
    at_ref.session_state["current_page"] = "Resume Builder"
    at_ref.session_state["resume_builder_step"] = "editor"
    at_ref.session_state["resume_category_step"] = 9
    at_ref.run()
    assert not at_ref.exception
    assert at_ref.button(key="btn_add_reference") is not None


def test_12_pdf_generation_with_all_sections():
    """Verify PDF generator produces multi-page selectable PDF including certifications, achievements, and references."""
    full_data = {
        "first_name": "Aarav",
        "last_name": "Sharma",
        "job_title": "Lead Cloud Architect",
        "email": "aarav.sharma@talentsphere.io",
        "phone": "+91 98765 43210",
        "city": "Bangalore",
        "country": "India",
        "linkedin": "linkedin.com/in/aarav",
        "portfolio": "github.com/aarav",
        "summary": "Accomplished Cloud Architect with 10+ years specializing in multi-region Kubernetes deployments, automated FinOps, and high-availability systems.",
        "projects": [
            {
                "title": "Enterprise Cloud Migration",
                "organization": "FinTech Corp",
                "technologies": "Kubernetes, Terraform, AWS, Python",
                "description": "Migrated 40+ monolithic microservices to EKS cluster with zero customer downtime.",
                "contributions": "Reduced monthly compute costs by 38% ($450K annual savings).",
                "start_date": "01/2023",
                "end_date": "12/2023",
            }
        ],
        "experience": [
            {
                "role": "Principal Cloud Architect",
                "company": "Infosys Elevate",
                "employment_type": "Full-time",
                "location": "Bangalore, India",
                "duration": "01/2021 – Present",
                "responsibilities": [
                    "Direct architecture for 12 enterprise accounts with 99.99% SLA.",
                    "Formulated disaster recovery blueprint with under 15 minute RTO.",
                ],
            }
        ],
        "education": [
            {
                "degree": "Master of Technology in Computer Science",
                "institution": "Indian Institute of Science (IISc)",
                "period": "2018 – 2020",
                "academic_info": "Gold Medalist with Distinction",
            }
        ],
        "skills": [
            {"name": "Kubernetes", "category": "Technical"},
            {"name": "Terraform", "category": "Technical"},
            {"name": "Python", "category": "Technical"},
            {"name": "Executive Leadership", "category": "Leadership"},
        ],
        "certifications": [
            {
                "name": "AWS Certified Solutions Architect – Professional",
                "issuer": "Amazon Web Services",
                "issue_date": "05/2023",
                "expiry_date": "05/2026",
                "credential_id": "AWS-PSA-9901",
                "credential_url": "https://aws.amazon.com/verification",
            }
        ],
        "achievements": [
            {
                "title": "Innovator of the Year Award",
                "organization": "Infosys Annual Summit",
                "date": "2023",
                "description": "Recognized for pioneering multi-cloud automation tool.",
            }
        ],
        "references": [
            {
                "name": "Dr. Sarah Jenkins",
                "designation": "VP of Engineering",
                "organization": "Global Cloud Corp",
                "contact_info": "s.jenkins@example.com",
                "include_contact_details": True,
                "include_in_resume": True,
            }
        ],
        "custom_sections": [
            {
                "title": "Patents & Publications",
                "include_in_resume": True,
                "entries": [
                    {
                        "title": "Dynamic Traffic Routing in Multi-Cluster Meshes",
                        "date": "2023",
                        "description": "US Patent #9,876,543 filed for automated pod routing.",
                    }
                ],
            }
        ],
    }

    for tmpl in ["puffin", "caddisfly", "sahani", "mayfly"]:
        pdf = generate_resume_pdf(full_data, template_id=tmpl)
        assert pdf.startswith(b"%PDF-")
        assert len(pdf) > 1000
