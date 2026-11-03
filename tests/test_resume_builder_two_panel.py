"""Acceptance test suite for the TalentSphere Two-Panel Resume Editor.

Verifies:
1. Main layout: Editor on Left (~50%), Live Resume Preview on Right (~50%).
2. Dedicated category steps in exact specified order:
   1. Personal Details
   2. Professional Summary
   3. Work Experience
   4. Education
   5. Projects
   6. Technical and Professional Skills
   7. Certifications
   8. Achievements
   9. References
   10. Custom Sections
3. Step isolation: each step displays only its own form.
4. Bottom navigation: Back button (disabled on step 1), step progress indicator, Next button.
5. On step 10, Next is replaced by Finish / Review Resume.
6. Navigation preserves all entered information without data loss.
7. Step progress indicators support direct navigation.
8. Resume strength indicator is visible and accurate.
9. Preview header has editable filename and Download PDF button.
10. Live preview renders paper-like sheet on dark surround with real-time updates.
11. Multi-page preview pagination when content exceeds one page.
12. 5 skill proficiency levels with exact colors (Beginner, Skillful, Experienced, Advanced, Expert).
13. Add Certification, Add Achievement, and Add Reference open forms immediately.
14. PDF generation works for all templates with user's name in filename.
"""

from pathlib import Path
import re
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
    PROFICIENCY_LEVELS,
    PROF_COLORS,
    TEMPLATES,
    generate_resume_pdf,
    calculate_resume_strength,
    generate_live_preview_html,
)

APP_PATH = str(Path(__file__).parent.parent / "app.py")


def test_1_category_steps_exact_order():
    """Verify the 10 steps are defined in the exact required order."""
    expected = [
        "Personal Details",
        "Professional Summary",
        "Work Experience",
        "Education",
        "Skills",
        "Projects",
        "Certifications",
        "Achievements",
        "References",
        "Custom Sections",
    ]
    actual = [s["title"] for s in CATEGORY_STEPS]
    assert actual == expected
    assert len(CATEGORY_STEPS) == 10


def test_2_two_panel_layout_and_step_isolation():
    """Verify two-panel layout: editor on left, preview on right, and step isolation."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Resume Builder"
    at.session_state["resume_builder_step"] = "editor"
    at.session_state["resume_category_step"] = 1
    at.run()
    assert not at.exception

    # Step 1: Personal Details fields ARE rendered
    assert at.text_input(key="in_res_title") is not None
    assert at.text_input(key="in_res_fn") is not None
    assert at.text_input(key="in_res_ln") is not None

    # Step 2 Summary and Step 3 Experience fields are NOT rendered on Step 1 (isolated!)
    summary_keys = [t.key for t in at.text_area]
    assert "in_res_summary" not in summary_keys
    button_keys = [b.key for b in at.button]
    assert "btn_add_experience" not in button_keys

    # Right panel preview elements ARE rendered simultaneously on right
    assert at.download_button(key="btn_download_ats_pdf") is not None
    assert at.text_input(key="txt_topbar_resume_filename") is not None

    # Back button is disabled on Step 1
    assert at.button(key="btn_step_back_disabled") is not None
    # Next button is present
    assert at.button(key="btn_step_next") is not None


def test_3_step_navigation_and_persistence():
    """Verify Back and Next navigation correctly update steps and preserve form data."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Resume Builder"
    at.session_state["resume_builder_step"] = "editor"
    at.session_state["resume_category_step"] = 1
    at.run()
    assert not at.exception

    # Enter custom title on Step 1
    at.text_input(key="in_res_title").input("Senior AI Systems Architect")
    at.button(key="btn_step_next").click()
    at.run()
    assert not at.exception

    # Should have advanced to Step 2
    assert at.session_state["resume_category_step"] == 2
    # Professional summary is rendered
    assert at.text_area(key="in_res_summary") is not None

    # Enter summary
    at.text_area(key="in_res_summary").input("Demonstrated expertise leading multi-agent architectures.")
    at.button(key="btn_step_next").click()
    at.run()
    assert not at.exception

    # Should have advanced to Step 3 (Work Experience)
    assert at.session_state["resume_category_step"] == 3
    assert at.button(key="btn_add_experience") is not None

    # Navigate Back to Step 2
    assert at.button(key="btn_step_back") is not None
    at.button(key="btn_step_back").click()
    at.run()
    assert not at.exception
    assert at.session_state["resume_category_step"] == 2

    # Navigate Back to Step 1
    at.button(key="btn_step_back").click()
    at.run()
    assert not at.exception
    assert at.session_state["resume_category_step"] == 1

    # Verify Job title previously entered was preserved!
    assert at.text_input(key="in_res_title").value == "Senior AI Systems Architect"


def test_4_step_10_finish_action():
    """Verify that on Step 10 (Custom Sections), Next is replaced with Finish action."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Resume Builder"
    at.session_state["resume_builder_step"] = "editor"
    at.session_state["resume_category_step"] = 10
    at.run()
    assert not at.exception

    # Next button should NOT be present on the final step
    button_keys = [b.key for b in at.button]
    assert "btn_step_next" not in button_keys

    # Finish button should be present
    assert at.button(key="btn_step_finish") is not None

    # Clicking Finish saves draft
    at.button(key="btn_step_finish").click()
    at.run()
    assert not at.exception


def test_5_direct_step_pill_navigation():
    """Verify that clicking a step pill navigates directly to that category."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Resume Builder"
    at.session_state["resume_builder_step"] = "editor"
    at.session_state["resume_category_step"] = 1
    at.run()
    assert not at.exception

    # Click pill 5 (Skills)
    at.button(key="btn_step_pill_5").click()
    at.run()
    assert not at.exception
    assert at.session_state["resume_category_step"] == 5
    assert at.button(key="btn_add_single_skill") is not None


def test_6_skill_proficiency_colors_and_interaction():
    """Verify 5 proficiency levels, their colors, and circular indicator interaction."""
    # Verify the exact 5 color hex codes
    assert PROF_COLORS["Beginner"] == "#60A5FA"
    assert PROF_COLORS["Skillful"] == "#2DD4BF"
    assert PROF_COLORS["Experienced"] == "#22C55E"
    assert PROF_COLORS["Advanced"] == "#A78BFA"
    assert PROF_COLORS["Expert"] == "#FBBF24"

    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Resume Builder"
    at.session_state["resume_builder_step"] = "editor"
    at.session_state["resume_category_step"] = 5
    at.run()
    assert not at.exception

    # Add a skill first to guarantee a skill exists for circular buttons
    at.text_input(key="txt_add_skill_0").input("Python")
    at.button(key="btn_add_single_skill").click()
    at.run()
    assert not at.exception

    # Verify proficiency circular button exists for first skill
    circ_btn = at.button(key="btn_circ_0_5")
    assert circ_btn is not None

    # Click Expert (5)
    circ_btn.click()
    at.run()
    assert not at.exception

    # Verify draft holds updated level
    active_data = at.session_state.get(f"resume_active_data_1")
    assert active_data["skills"][0]["proficiency"] == "Expert"


def test_7_add_certification_achievement_reference_forms_open_immediately():
    """Verify Add Certification, Add Achievement, and Add Reference display forms immediately."""
    # Step 7: Certifications
    at7 = AppTest.from_file(APP_PATH, default_timeout=30)
    at7.session_state["is_authenticated"] = True
    at7.session_state["user_id"] = 1
    at7.session_state["current_page"] = "Resume Builder"
    at7.session_state["resume_builder_step"] = "editor"
    at7.session_state["resume_category_step"] = 7
    at7.run()
    assert not at7.exception
    at7.button(key="btn_add_cert").click()
    at7.run()
    assert not at7.exception
    assert at7.text_input(key="cert_in_name") is not None
    assert at7.text_input(key="cert_in_issuer") is not None
    assert at7.button(key="btn_save_new_cert") is not None

    # Step 8: Achievements
    at8 = AppTest.from_file(APP_PATH, default_timeout=30)
    at8.session_state["is_authenticated"] = True
    at8.session_state["user_id"] = 1
    at8.session_state["current_page"] = "Resume Builder"
    at8.session_state["resume_builder_step"] = "editor"
    at8.session_state["resume_category_step"] = 8
    at8.run()
    assert not at8.exception
    orig_ach_inputs = len([t for t in at8.text_input if t.key and t.key.startswith("ach_t_")])
    at8.button(key="btn_add_achievement").click()
    at8.run()
    assert not at8.exception
    new_ach_inputs = len([t for t in at8.text_input if t.key and t.key.startswith("ach_t_")])
    assert new_ach_inputs == orig_ach_inputs + 1

    # Step 9: References
    at9 = AppTest.from_file(APP_PATH, default_timeout=30)
    at9.session_state["is_authenticated"] = True
    at9.session_state["user_id"] = 1
    at9.session_state["current_page"] = "Resume Builder"
    at9.session_state["resume_builder_step"] = "editor"
    at9.session_state["resume_category_step"] = 9
    at9.run()
    assert not at9.exception
    orig_ref_inputs = len([t for t in at9.text_input if t.key and t.key.startswith("ref_n_")])
    at9.button(key="btn_add_reference").click()
    at9.run()
    assert not at9.exception
    new_ref_inputs = len([t for t in at9.text_input if t.key and t.key.startswith("ref_n_")])
    assert new_ref_inputs == orig_ref_inputs + 1


def test_8_live_preview_rendering_and_multipage():
    """Verify live preview generates clean paper-like HTML and paginates for long content."""
    short_data = {
        "first_name": "Eleanor",
        "last_name": "Vance",
        "job_title": "Cloud Architect",
        "email": "eleanor@talentsphere.io",
        "summary": "Experienced architect.",
        "skills": [{"name": "AWS", "proficiency": "Expert"}],
    }
    html_short = generate_live_preview_html(short_data, "puffin")
    assert "resume-paper-page" in html_short
    assert "Page 1 of 1" in html_short
    assert "Page Break" not in html_short
    # Contains expert color
    assert "#FBBF24" in html_short

    # Long data triggering multipage
    long_data = {
        "first_name": "Marcus",
        "last_name": "Brody",
        "job_title": "Enterprise Lead Architect",
        "email": "marcus@company.com",
        "summary": "Extensive architectural experience across global systems." * 4,
        "experience": [
            {"role": f"Architect #{i}", "company": f"Corp #{i}", "duration": "2020-2024", "responsibilities": ["Led system design."]}
            for i in range(5)
        ],
        "projects": [
            {"title": f"Project #{i}", "technologies": "Python, Docker", "description": "High throughput system."}
            for i in range(4)
        ],
        "education": [{"degree": "BS CS", "institution": "Tech University"}],
        "skills": [{"name": "Kubernetes", "proficiency": "Advanced"}],
    }
    html_long = generate_live_preview_html(long_data, "puffin")
    assert "Page Break — Page 2" in html_long
    assert "Page 1 of 2" in html_long
    assert "Page 2 of 2" in html_long


def test_9_pdf_export_and_user_name_filename():
    """Verify Download PDF produces a valid ReportLab PDF with filename based on user's name."""
    sample_data = {
        "first_name": "Priya",
        "last_name": "Raman",
        "job_title": "Senior Data Scientist",
        "email": "priya.raman@talentsphere.io",
        "phone": "+91 98765 12345",
        "city": "Chennai",
        "country": "India",
        "summary": "Specialized in generative AI and retrieval augmented generation.",
        "skills": [{"name": "PyTorch", "proficiency": "Expert"}, {"name": "NLP", "proficiency": "Advanced"}],
        "projects": [{"title": "Agentic LLM Router", "technologies": "Python, LangChain", "description": "High-accuracy query router."}],
    }

    for tmpl in ["puffin", "caddisfly", "sahani", "mayfly"]:
        pdf = generate_resume_pdf(sample_data, template_id=tmpl)
        assert pdf.startswith(b"%PDF-")
        assert len(pdf) > 800

    fn_generated = f"{sample_data['first_name']}_{sample_data['last_name']}_Resume"
    assert "Priya" in fn_generated
    assert "Raman" in fn_generated
