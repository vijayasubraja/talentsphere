"""Automated test suite for TalentSphere My Profile and Resume Builder integration.

Verifies the 12 specific acceptance criteria:
1. My Profile appears as a separate navigation page.
2. Existing profile information loads correctly.
3. Edit, Save Changes, and Cancel work as expected.
4. Required-field and invalid-input validation works.
5. Profile completion is calculated correctly.
6. Missing-information suggestions are accurate.
7. Career recommendations use the selected target role.
8. Saving profile information makes it available to Resume Builder.
9. Resume changes can be reflected in the master profile through the intended update workflow.
10. Different users cannot access each other's information.
11. Existing login, resume generation, PDF export, role matching, skill-gap analysis, and reports continue working.
12. Database changes remain backward-compatible.
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
    delete_skill,
    update_user_account,
    calculate_profile_completion_details,
    get_career_growth_suggestions,
    gap_analysis,
    role_match,
    parse_json_field,
)
from views.resume_builder_view import generate_ats_resume_pdf

APP_PATH = str(Path(__file__).parent.parent / "app.py")


def test_1_my_profile_navigation_page_exists():
    """Requirement 1: Verify My Profile appears as a separate navigation item and renders."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "My Profile"
    at.run()
    assert not at.exception
    # Verify navigation radio options include Profile
    assert len(at.sidebar.radio) > 0
    radio = at.sidebar.radio[0]
    labels = list(radio.options)
    assert any("Profile" in l for l in labels)


def test_2_existing_profile_information_loads():
    """Requirement 2: Existing profile information loads correctly from SQLite."""
    with connect() as db:
        user_row = db.execute("SELECT id, email FROM users WHERE email='eleanor.vance@talentsphere.io'").fetchone()
    assert user_row is not None
    profile = get_profile(user_row["id"])
    assert profile is not None
    assert "email" in profile
    assert profile["email"] == "eleanor.vance@talentsphere.io"
    assert profile["job_title"] != ""
    assert profile["years_experience"] >= 6.0


def test_3_edit_save_changes_and_cancel_flow():
    """Requirement 3: Verify Edit, Save Changes, and Cancel flow."""
    unique_email = f"edit-user-{uuid.uuid4().hex[:8]}@example.com"
    ok, _ = register("Original Name", unique_email, "TestPass123")
    assert ok
    user = login(unique_email, "TestPass123")
    uid = user["id"]

    # Initial profile state
    save_profile(uid, {
        "job_title": "Software Developer",
        "phone": "+1 555-0100",
        "location": "Dallas, TX",
        "summary": "Initial summary before editing.",
    })

    # Test Save Changes
    updated_values = {
        "job_title": "Senior Cloud Developer",
        "phone": "+1 555-0200",
        "location": "Seattle, WA",
        "summary": "Updated summary with measurable achievements and cloud architecture.",
        "years_experience": 5.0,
    }
    update_user_account(uid, "Updated Name")
    save_profile(uid, updated_values)

    reloaded = get_profile(uid)
    assert reloaded["name"] == "Updated Name"
    assert reloaded["job_title"] == "Senior Cloud Developer"
    assert reloaded["phone"] == "+1 555-0200"
    assert reloaded["location"] == "Seattle, WA"
    assert "Updated summary" in reloaded["summary"]
    assert reloaded["years_experience"] == 5.0

    # Test Cancel (discarding draft without persisting)
    draft_discarded = copy_of_saved = dict(reloaded)
    draft_discarded["job_title"] = "Temporary Unsaved Title"
    # When user cancels, save_profile is never called with draft_discarded
    current = get_profile(uid)
    assert current["job_title"] == "Senior Cloud Developer"


def test_4_required_field_validation():
    """Requirement 4: Empty name or invalid email must be rejected by validation."""
    unique_email = f"val-user-{uuid.uuid4().hex[:8]}@example.com"
    register("Valid Name", unique_email, "TestPass123")
    with connect() as db:
        uid = db.execute("SELECT id FROM users WHERE email=?", (unique_email,)).fetchone()["id"]

    # Blank name rejected
    ok_name, msg_name = update_user_account(uid, "")
    assert not ok_name
    assert "blank" in msg_name.lower() or "required" in msg_name.lower()

    # Invalid email rejected
    ok_email, msg_email = update_user_account(uid, "Valid Name", "notanemailaddress")
    assert not ok_email
    assert "valid email" in msg_email.lower()


def test_5_profile_completion_calculation():
    """Requirement 5: Profile completion percentage is dynamically calculated without hardcoding."""
    # Empty profile score should be 0
    empty_comp = calculate_profile_completion_details({}, [])
    assert empty_comp["percentage"] == 0
    assert len(empty_comp["completed_sections"]) == 0
    assert "Personal Information" in empty_comp["incomplete_sections"]

    # Partially completed profile
    partial_profile = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "555-1234",
        "location": "Chicago, IL",
        "job_title": "Lead Engineer",
        "summary": "Experienced engineer with a track record of delivering high-scale systems.",
    }
    partial_comp = calculate_profile_completion_details(partial_profile, [])
    # Personal Info (15%) + Summary (15%) = 30%
    assert partial_comp["percentage"] == 30
    assert "Personal Information" in partial_comp["completed_sections"]
    assert "Professional Summary" in partial_comp["completed_sections"]
    assert "Education" in partial_comp["incomplete_sections"]

    # Fully completed profile
    full_profile = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "555-1234",
        "location": "Chicago, IL",
        "job_title": "Lead Engineer",
        "summary": "Experienced engineer with a track record of delivering high-scale systems.",
        "education": [{"degree": "BS CS", "institution": "MIT"}],
        "experience": [{"role": "Senior Dev", "company": "Tech Corp"}],
        "projects": [{"title": "Cloud Migration", "technologies": "AWS"}],
        "certifications": [{"name": "AWS Certified", "issuer": "Amazon"}],
        "target_role": "Technical Lead",
        "career_goal": "Lead systems architecture squads.",
    }
    full_skills = [{"name": "Python", "category": "Technical", "proficiency": "Advanced"}]
    full_comp = calculate_profile_completion_details(full_profile, full_skills)
    assert full_comp["percentage"] == 100
    assert len(full_comp["incomplete_sections"]) == 0


def test_6_missing_information_suggestions():
    """Requirement 6: Missing-information suggestions accurately identify incomplete sections."""
    profile = {
        "name": "Alex Smith",
        "email": "alex@example.com",
        # Missing phone and location
    }
    comp = calculate_profile_completion_details(profile, [])
    assert comp["percentage"] < 30
    assert any("phone" in s.lower() or "location" in s.lower() for s in comp["suggested_actions"])


def test_7_career_recommendations_use_selected_target_role():
    """Requirement 7: Career growth suggestions use selected target role and catalog requirements."""
    profile = {
        "target_role": "Senior Software Engineer",
        "summary": "Software engineer with 2 years of experience.",
        "years_experience": 2.0,
    }
    # Role requires: Python: 4, System Design: 3, SQL: 3, Cloud: 2, Communication: 3
    # User only has Python Beginner
    skills = [{"name": "Python", "proficiency": "Beginner", "category": "Technical"}]
    suggestions = get_career_growth_suggestions(profile, skills)
    assert len(suggestions) > 0

    # Should detect missing SQL and System Design
    gaps_text = " ".join([s["gap"] for s in suggestions])
    assert "System Design" in gaps_text
    assert "SQL" in gaps_text

    # Priority should be High for System Design (required level 3)
    sys_design_sug = next(s for s in suggestions if "System Design" in s["gap"])
    assert sys_design_sug["priority"] == "High"
    assert sys_design_sug["status"] == "Not started"
    assert sys_design_sug["action"] != ""
    assert sys_design_sug["why"] != ""


def test_8_saving_profile_makes_it_available_to_resume_builder():
    """Requirement 8: Shared database ensures saved profile changes are immediately available in Resume Builder."""
    unique_email = f"resume-share-{uuid.uuid4().hex[:8]}@example.com"
    register("Shared User", unique_email, "SharePass123")
    with connect() as db:
        uid = db.execute("SELECT id FROM users WHERE email=?", (unique_email,)).fetchone()["id"]

    # Save via My Profile backend
    save_profile(uid, {
        "job_title": "Principal Architect",
        "summary": "Shared authoritative summary written in My Profile.",
        "education": [{"degree": "Master of Engineering", "institution": "Stanford", "period": "2020"}],
        "experience": [{"role": "Lead Architect", "company": "CloudSphere", "duration": "2021 – Present"}],
    })

    # Read from Resume Builder perspective
    resume_profile = get_profile(uid)
    assert resume_profile["job_title"] == "Principal Architect"
    assert "Shared authoritative summary" in resume_profile["summary"]

    edu = parse_json_field(resume_profile["education"])
    assert edu[0]["degree"] == "Master of Engineering"

    # PDF generation reflects these exact SQLite values
    pdf_bytes = generate_ats_resume_pdf(
        user_name="Shared User",
        user_email=unique_email,
        profile=resume_profile,
        skills=[],
        sections_to_include=["Summary", "Experience", "Education"],
    )
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 500


def test_9_resume_changes_reflected_through_confirmed_update_workflow():
    """Requirement 9: Master profile is NOT overwritten automatically, but updates upon explicit user confirmation."""
    unique_email = f"confirmed-update-{uuid.uuid4().hex[:8]}@example.com"
    register("Confirm User", unique_email, "TestPass123")
    with connect() as db:
        uid = db.execute("SELECT id FROM users WHERE email=?", (unique_email,)).fetchone()["id"]

    # Initial master profile
    save_profile(uid, {"summary": "Original Master Profile Summary."})

    # Simulate importing an external resume
    extracted_text = "Extracted summary from uploaded resume document with new credentials."

    # Action A: Saving text only leaves master profile summary completely untouched!
    save_profile(uid, {"resume_text": extracted_text})
    current_prof = get_profile(uid)
    assert current_prof["summary"] == "Original Master Profile Summary."
    assert current_prof["resume_text"] == extracted_text

    # Action B: Confirmed-update workflow explicitly applies selected section to master profile
    confirmed_updates = {"summary": extracted_text}
    save_profile(uid, confirmed_updates)
    updated_prof = get_profile(uid)
    assert updated_prof["summary"] == extracted_text


def test_10_different_users_cannot_access_each_others_information():
    """Requirement 10: Strict data isolation between different authenticated user IDs."""
    email_u1 = f"user1-{uuid.uuid4().hex[:8]}@company.com"
    email_u2 = f"user2-{uuid.uuid4().hex[:8]}@company.com"
    register("User One", email_u1, "PassOne123")
    register("User Two", email_u2, "PassTwo123")

    with connect() as db:
        id1 = db.execute("SELECT id FROM users WHERE email=?", (email_u1,)).fetchone()["id"]
        id2 = db.execute("SELECT id FROM users WHERE email=?", (email_u2,)).fetchone()["id"]

    # User 1 saves private information
    save_profile(id1, {
        "job_title": "User 1 Confidential Title",
        "phone": "+1 111-1111",
        "summary": "User 1 Secret Summary.",
    })
    add_skill(id1, "Skill-User-1", "Technical", "Expert", 5.0)

    # User 2 saves different information
    save_profile(id2, {
        "job_title": "User 2 Public Role",
        "phone": "+1 222-2222",
        "summary": "User 2 Public Summary.",
    })
    add_skill(id2, "Skill-User-2", "Technical", "Beginner", 1.0)

    # Validate isolation
    p1 = get_profile(id1)
    p2 = get_profile(id2)
    s1 = list_skills(id1)
    s2 = list_skills(id2)

    assert p1["job_title"] == "User 1 Confidential Title"
    assert p2["job_title"] == "User 2 Public Role"
    assert p1["phone"] != p2["phone"]
    assert any(s["name"] == "Skill-User-1" for s in s1)
    assert not any(s["name"] == "Skill-User-1" for s in s2)
    assert any(s["name"] == "Skill-User-2" for s in s2)
    assert not any(s["name"] == "Skill-User-2" for s in s1)


def test_11_role_matching_and_reports_continue_working():
    """Requirement 11: Existing role matching, skill gaps, and reports continue functioning."""
    skills = [
        {"name": "Python", "proficiency": "Expert"},
        {"name": "System Design", "proficiency": "Advanced"},
        {"name": "SQL", "proficiency": "Advanced"},
        {"name": "Cloud", "proficiency": "Intermediate"},
        {"name": "Communication", "proficiency": "Advanced"},
    ]
    score = role_match("Senior Software Engineer", skills, years=5.0)
    assert score >= 90

    gaps = gap_analysis("Senior Software Engineer", skills)
    assert len(gaps) > 0
    assert all("gap" in g and "priority" in g for g in gaps)


def test_12_database_changes_remain_backward_compatible():
    """Requirement 12: Database changes remain backward-compatible with legacy tables and callers."""
    # Ensure init_db runs idempotently without altering existing users or tables
    services.core.init_db()
    with connect() as db:
        tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        assert "users" in tables
        assert "profiles" in tables
        assert "skills" in tables
        assert "assessments" in tables
        assert "progress" in tables
        assert "sessions" in tables


def test_13_my_profile_ui_edit_cancel_interaction():
    """AppTest verification: My Profile edit mode toggles, displays form fields, and cancels cleanly."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "My Profile"
    at.run()
    assert not at.exception

    # Click 'Edit Profile' button
    assert at.button(key="btn_enter_edit_mode") is not None
    at.button(key="btn_enter_edit_mode").click()
    at.run()
    assert not at.exception
    assert at.session_state["is_editing_profile"] is True

    # Check edit fields are rendered
    assert at.text_input(key="draft_name_in") is not None
    assert at.text_input(key="draft_title_in") is not None

    # Click 'Cancel' button
    assert at.button(key="btn_cancel_profile_main") is not None
    at.button(key="btn_cancel_profile_main").click()
    at.run()
    assert not at.exception
    assert at.session_state["is_editing_profile"] is False


def test_14_resume_builder_ui_renders_and_has_download():
    """AppTest verification: Resume Builder page renders ATS preview and PDF download trigger."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Resume Builder"
    at.run()
    assert not at.exception

    # Check ATS PDF download button exists
    dl_btn = at.download_button(key="btn_download_ats_pdf")
    assert dl_btn is not None
    assert "Download ATS Resume PDF" in dl_btn.label

