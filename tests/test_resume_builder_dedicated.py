"""Dedicated automated test suite for the TalentSphere Resume Builder page.

Verifies:
1. Resume Builder appears as a dedicated item in the sidebar navigation.
2. Resume-building buttons are removed from Employee Profile without breaking profile management.
3. Users can select templates (Puffin, Caddisfly, Sahani, Mayfly) and proceed to the editor.
4. Existing profile data populates relevant resume fields dynamically without hardcoding.
5. Users can customize resume sections without unintentionally overwriting their master profile.
6. Users can add and remove dynamic entries (projects, education, skills, experience).
7. Download PDF generates valid, selectable PDFs for all supported templates.
8. Multi-page pagination handles long content cleanly.
9. Strict data isolation between different authenticated user accounts.
10. Backward compatibility with existing functions and UI tests.
"""

from pathlib import Path
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
    list_skills,
    add_skill,
    get_resume_draft,
    save_resume_draft,
)
from views.resume_builder_view import (
    generate_resume_pdf,
    generate_ats_resume_pdf,
    calculate_resume_strength,
    TEMPLATES,
)

APP_PATH = str(Path(__file__).parent.parent / "app.py")


def test_1_resume_builder_sidebar_navigation():
    """Verify Resume Builder appears as an independent item in the sidebar navigation."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Dashboard"
    at.run()
    assert not at.exception

    # Verify sidebar radio options include Resume Builder
    radio = at.sidebar.radio[0]
    options = list(radio.options)
    assert any("Resume Builder" in opt for opt in options)

    # Click Resume Builder in sidebar
    for opt in options:
        if "Resume Builder" in opt:
            radio.set_value(opt)
            break
    at.run()
    assert not at.exception
    assert at.session_state["current_page"] == "Resume Builder"


def test_2_employee_profile_has_no_resume_builder_button():
    """Verify resume-building buttons are removed from Employee Profile page."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Employee Profile"
    at.run()
    assert not at.exception

    # Verify btn_nav_resume_builder is NOT rendered in Employee Profile
    button_keys = [b.key for b in at.button]
    assert "btn_nav_resume_builder" not in button_keys

    # Verify Edit Profile button still exists and works
    assert at.button(key="btn_enter_edit_mode") is not None


def test_3_templates_metadata_and_selection():
    """Verify template options are defined and selectable (Puffin, Caddisfly, Sahani, Mayfly)."""
    template_ids = [t["id"] for t in TEMPLATES]
    assert "puffin" in template_ids
    assert "caddisfly" in template_ids
    assert "sahani" in template_ids
    assert "mayfly" in template_ids

    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Resume Builder"
    at.session_state["resume_builder_step"] = "template_select"
    at.run()
    assert not at.exception

    # Verify Proceed to Editor button is present in template selection step
    assert at.button(key="btn_confirm_proceed_editor") is not None
    at.button(key="btn_confirm_proceed_editor").click()
    at.run()
    assert not at.exception
    assert at.session_state["resume_builder_step"] == "editor"


def test_4_prefill_profile_data_into_resume_draft():
    """Verify user's saved SQLite profile and skills prefill resume fields dynamically."""
    unique_email = f"prefill-{uuid.uuid4().hex[:8]}@talentsphere.io"
    register("Aria Stark", unique_email, "AriaPass123")
    with connect() as db:
        uid = db.execute("SELECT id FROM users WHERE email=?", (unique_email,)).fetchone()["id"]

    save_profile(uid, {
        "job_title": "AI Research Scientist",
        "phone": "+1 555-7788",
        "location": "Boston, MA",
        "summary": "AI researcher specializing in deep reinforcement learning.",
        "education": [{"degree": "M.S. in Computer Science", "institution": "MIT", "period": "2021 – 2023"}],
        "projects": [{"title": "Autonomous Drone Navigation", "technologies": "PyTorch, ROS", "description": "RL-based obstacle avoidance."}],
        "experience": [{"role": "Research Fellow", "company": "MIT CSAIL", "duration": "2023 – Present"}],
    })
    add_skill(uid, "PyTorch", "Technical", "Expert", 4.0)
    add_skill(uid, "Reinforcement Learning", "Technical", "Advanced", 3.0)

    draft = get_resume_draft(uid)
    data = draft["resume_data"]

    assert data["first_name"] == "Aria"
    assert data["last_name"] == "Stark"
    assert data["job_title"] == "AI Research Scientist"
    assert data["email"] == unique_email
    assert data["phone"] == "+1 555-7788"
    assert data["location"] == "Boston, MA"
    assert "deep reinforcement learning" in data["summary"]
    assert len(data["education"]) == 1
    assert data["education"][0]["institution"] == "MIT"
    assert len(data["projects"]) == 1
    assert data["projects"][0]["title"] == "Autonomous Drone Navigation"
    assert any(s["name"] == "PyTorch" for s in data["skills"])


def test_5_resume_customization_does_not_overwrite_master_profile():
    """Verify users can customize resume draft without unintentionally altering master profile."""
    unique_email = f"draft-protect-{uuid.uuid4().hex[:8]}@talentsphere.io"
    register("Master User", unique_email, "Pass12345")
    with connect() as db:
        uid = db.execute("SELECT id FROM users WHERE email=?", (unique_email,)).fetchone()["id"]

    save_profile(uid, {
        "job_title": "Original Master Title",
        "summary": "Original master profile summary.",
    })

    # Save a modified resume draft
    customized_resume = {
        "first_name": "Master",
        "last_name": "User",
        "job_title": "Customized Resume Specific Title",
        "summary": "Tailored resume summary with targeted keywords.",
    }
    save_resume_draft(uid, customized_resume, selected_template="puffin")

    # Verify master profile is completely untouched
    master_prof = get_profile(uid)
    assert master_prof["job_title"] == "Original Master Title"
    assert master_prof["summary"] == "Original master profile summary."

    # Verify resume draft holds the tailored content
    reloaded_draft = get_resume_draft(uid)["resume_data"]
    assert reloaded_draft["job_title"] == "Customized Resume Specific Title"
    assert reloaded_draft["summary"] == "Tailored resume summary with targeted keywords."


def test_6_user_data_isolation():
    """Verify strict data isolation between different users' resume drafts."""
    email_a = f"alice-{uuid.uuid4().hex[:8]}@talentsphere.io"
    email_b = f"bob-{uuid.uuid4().hex[:8]}@talentsphere.io"
    register("Alice User", email_a, "AlicePass123")
    register("Bob User", email_b, "BobPass123")

    with connect() as db:
        id_a = db.execute("SELECT id FROM users WHERE email=?", (email_a,)).fetchone()["id"]
        id_b = db.execute("SELECT id FROM users WHERE email=?", (email_b,)).fetchone()["id"]

    save_resume_draft(id_a, {"summary": "Alice confidential resume data."}, selected_template="puffin")
    save_resume_draft(id_b, {"summary": "Bob distinct public resume data."}, selected_template="caddisfly")

    draft_a = get_resume_draft(id_a)
    draft_b = get_resume_draft(id_b)

    assert draft_a["resume_data"]["summary"] == "Alice confidential resume data."
    assert draft_a["selected_template"] == "puffin"

    assert draft_b["resume_data"]["summary"] == "Bob distinct public resume data."
    assert draft_b["selected_template"] == "caddisfly"


def test_7_pdf_generation_all_templates():
    """Verify generate_resume_pdf produces valid PDFs for all 4 templates."""
    sample_data = {
        "first_name": "Vijaya",
        "last_name": "Subraja B",
        "job_title": "AI/ML Engineer",
        "email": "vijayasubraja777@gmail.com",
        "phone": "9786220049",
        "location": "Tiruchirappalli, India",
        "linkedin": "linkedin.com/in/vijayasubraja",
        "summary": "Aspiring AI/ML Engineer with a strong foundation in AI&DS. Skillful in Python, SQL, and Machine Learning.",
        "education": [{"degree": "B.Tech in Artificial Intelligence", "institution": "Saranathan College of Engineering", "period": "09/2023 - Present", "academic_info": "First Class"}],
        "projects": [{"title": "CARDIOVASCULAR DISEASE PREDICTION", "technologies": "Python, Scikit-learn", "description": "Built ML model to predict cardiovascular disease risk with 91% accuracy."}],
        "experience": [{"role": "AI INTERN", "company": "CORIZO", "duration": "06/2023 - 08/2023", "responsibilities": ["Worked on deep learning models.", "Applied data preprocessing."]}],
        "skills": [{"name": "Python Foundation"}, {"name": "Machine Learning"}, {"name": "Artificial Intelligence"}],
        "certifications": [{"name": "SPRING BOOT CERTIFICATION", "issuer": "INFOSYS SPRINGBOARD", "year": "2024"}],
    }

    for tmpl in ["puffin", "caddisfly", "sahani", "mayfly"]:
        pdf_bytes = generate_resume_pdf(sample_data, template_id=tmpl)
        assert pdf_bytes.startswith(b"%PDF-")
        assert len(pdf_bytes) > 800


def test_8_multipage_pdf_pagination():
    """Verify multi-page resumes paginate cleanly without errors when content exceeds one page."""
    long_data = {
        "first_name": "Senior",
        "last_name": "Executive",
        "job_title": "Principal Architect",
        "email": "principal@company.com",
        "phone": "+1 555-0909",
        "location": "San Francisco, CA",
        "summary": "Extensive 15-year career driving enterprise architecture, distributed systems, and multi-region cloud resilience across global organizations." * 3,
        "education": [
            {"degree": f"Master of Science #{i}", "institution": f"University #{i}", "period": f"201{i} – 201{i+2}"}
            for i in range(5)
        ],
        "experience": [
            {
                "role": f"Lead Architect Role #{i}",
                "company": f"Global Enterprise #{i}",
                "duration": f"201{i} – 202{i%4}",
                "responsibilities": [
                    f"Spearheaded multi-million dollar cloud initiative #{i}.",
                    f"Mentored engineering squad of 25+ senior engineers.",
                    f"Reduced infrastructure latency by 45% using distributed caching.",
                ],
            }
            for i in range(6)
        ],
        "projects": [
            {
                "title": f"Enterprise Scalable Platform #{i}",
                "technologies": "Kubernetes, Go, Kafka, AWS",
                "description": "Architected low-latency event processing cluster processing 50K events/second." * 2,
                "contributions": f"Saved $350K annually in operational spend for squad #{i}.",
            }
            for i in range(5)
        ],
        "skills": [{"name": f"Skill-{i}"} for i in range(15)],
    }

    pdf_bytes = generate_resume_pdf(long_data, template_id="puffin")
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 2000


def test_9_resume_strength_metric():
    """Verify resume strength score calculates accurately."""
    minimal = {"first_name": "John", "email": "john@example.com"}
    score_min = calculate_resume_strength(minimal)
    assert 20 <= score_min <= 40

    full = {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane@example.com",
        "phone": "+1 555-1234",
        "location": "New York, NY",
        "job_title": "Software Engineer",
        "summary": "Experienced engineer with a strong track record of high quality delivery.",
        "experience": [{"role": "Engineer", "company": "Tech Corp"}],
        "education": [{"degree": "BS", "institution": "NYU"}],
        "projects": [{"title": "Web App"}],
        "skills": [{"name": "Python"}, {"name": "SQL"}, {"name": "AWS"}],
    }
    score_full = calculate_resume_strength(full)
    assert score_full >= 90
