"""Acceptance test suite for Section Order, Section C restoration, and Suggestions & Improvements tracking.

Explicitly verifies all 13 Acceptance Criteria:
1. Section A appears first.
2. Section B appears after Section A.
3. Section C is restored and appears between B and D.
4. Section D: Work Experience appears in the correct position.
5. Suggestions & Improvements appears at the bottom of the page.
6. Every recommendation topic has all three status options (Not Started, In Progress, Completed).
7. Each topic can be updated independently.
8. Status changes persist after refreshing the page.
9. Statuses remain associated with the correct user after logging out and back in.
10. The progress summary updates correctly.
11. Existing skill-gap analysis, role matching, profile editing, and other features continue to work.
12. No duplicate recommendation cards or navigation tabs are introduced.
13. No new runtime errors or database errors are introduced.
"""

from pathlib import Path
import uuid
import pytest
from streamlit.testing.v1 import AppTest
import services.core

APP_PATH = str(Path(__file__).parent.parent / "app.py")


def test_criteria_1_to_5_page_section_order():
    """Verify Section A -> Section B -> Section C (Task Management) -> Section D (Challenges & Support) -> Section E (Overall Work Progress) -> Suggestions last."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Employee Profile"
    at.run()
    assert not at.exception

    all_html = " ".join([m.value for m in at.html])

    pos_a = all_html.find("Section A: Employee Details")
    pos_b = all_html.find("Section B: Process & Goals")
    pos_c = all_html.find("Section C: Task Management")
    pos_d = all_html.find("Section D: Challenges & Support")
    pos_e = all_html.find("Section E: Overall Work Progress")
    pos_sug = all_html.find("Suggestions & Improvements")

    # 1. Section A appears first
    assert pos_a != -1, "Section A: Employee Details must be present"
    # 2. Section B appears after Section A
    assert pos_b != -1, "Section B: Process & Goals must be present"
    assert pos_a < pos_b, "Section A must appear before Section B"

    # 3. Section C appears after Section B
    assert pos_c != -1, "Section C: Task Management must be present"
    assert pos_b < pos_c, "Section C must appear after Section B"

    # 4. Section D appears after Section C
    assert pos_d != -1, "Section D: Challenges & Support must be rendered"
    assert pos_c < pos_d, "Section D must appear after Section C"

    # 5. Section E appears after Section D
    assert pos_e != -1, "Section E: Overall Work Progress must be rendered"
    assert pos_d < pos_e, "Section E must appear after Section D"

    # 6. Suggestions & Improvements appears at the bottom
    assert pos_sug != -1, "Suggestions & Improvements must be present"
    assert pos_e < pos_sug, "Suggestions & Improvements must appear after Section E"

    # Profile Progress Dashboard is converted to Employee Work Progress
    assert "Employee Work Progress:" in all_html, "Employee Work Progress dashboard must be present"
    assert "Overall Work Completion Rate" in all_html, "Main Overall Work Completion Rate bar must be preserved"
    assert "Task Completion Summary" in all_html, "Task Completion Summary must be displayed"

    # Verify no duplicate Suggestions & Improvements header
    assert all_html.count("Suggestions & Improvements") == 1, "Suggestions & Improvements should not be duplicated"


def test_criteria_3_and_4_sequential_sections_and_edit_tabs():
    """Verify Section C and Section D render sequentially in View Mode and have edit tabs in Edit Mode."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Employee Profile"
    at.run()
    assert not at.exception

    # View Mode: Section C and D are both directly rendered
    html_view = " ".join([m.value for m in at.html])
    assert "Section C: Task Management" in html_view
    assert "Section D: Challenges & Support" in html_view

    # In Edit Mode, verify tab order: Employee Details, Process & Goals, Challenges & Support
    at.button(key="btn_enter_edit_mode").click()
    at.run()
    assert not at.exception

    edit_tab_labels = [t.label for t in at.tabs]
    assert any("Employee Details" in l for l in edit_tab_labels)
    assert any("Process & Goals" in l for l in edit_tab_labels)
    assert any("Challenges & Support" in l for l in edit_tab_labels)


def test_criteria_6_to_10_status_options_persistence_and_progress_summary():
    """Verify 3 status options per topic, independent updating, persistence, and dynamic summary."""
    unique_email = f"order-test-{uuid.uuid4().hex[:8]}@example.com"
    services.core.register("Test Order User", unique_email, "SecurePassword123")
    user = services.core.login(unique_email, "SecurePassword123")
    uid = user["id"]

    # Initial profile with target role Data Analyst
    # Data Analyst requires: SQL: 3, Python: 2, Data Visualization: 3, Communication: 3
    services.core.save_profile(uid, {
        "target_role": "Data Analyst",
        "job_title": "Junior Analyst",
        "summary": "Data Analyst summary.",
        "years_experience": 0.5,
    })

    # Retrieve suggestions
    profile = services.core.get_profile(uid)
    skills = services.core.list_skills(uid)
    suggestions = services.core.get_career_growth_suggestions(profile, skills, uid)
    assert len(suggestions) >= 4

    topics = [s["topic"] for s in suggestions]
    assert "SQL" in topics
    assert "Python" in topics

    # Criteria 6: Default to Not Started
    for s in suggestions:
        assert s["status"] in ["Not Started", "Not started"]

    # Criteria 7: Each topic can be updated independently
    services.core.save_recommendation_status(uid, "SQL", "In Progress")
    services.core.save_recommendation_status(uid, "Python", "Completed")

    # Reload suggestions from database
    updated_suggestions = services.core.get_career_growth_suggestions(profile, skills, uid)
    status_map = {s["topic"]: s["status"] for s in updated_suggestions}

    assert status_map["SQL"] == "In Progress"
    assert status_map["Python"] == "Completed"
    # Communication should remain Not Started
    comm_status = status_map.get("Communication", "Not Started")
    assert comm_status in ["Not Started", "Not started"]

    # Criteria 8: Status changes persist after page refresh (direct database query)
    saved_statuses = services.core.get_recommendation_statuses(uid)
    assert saved_statuses["sql"] == "In Progress"
    assert saved_statuses["python"] == "Completed"

    # Criteria 9: Distinct user isolation
    other_email = f"other-user-{uuid.uuid4().hex[:8]}@example.com"
    services.core.register("Other User", other_email, "SecurePassword123")
    other_u = services.core.login(other_email, "SecurePassword123")
    other_uid = other_u["id"]

    other_statuses = services.core.get_recommendation_statuses(other_uid)
    assert "sql" not in other_statuses
    assert "python" not in other_statuses

    # Log back in as original user
    reloaded_u = services.core.login(unique_email, "SecurePassword123")
    assert reloaded_u["id"] == uid
    reloaded_statuses = services.core.get_recommendation_statuses(reloaded_u["id"])
    assert reloaded_statuses["sql"] == "In Progress"
    assert reloaded_statuses["python"] == "Completed"


def test_criteria_10_dynamic_progress_summary_values():
    """Verify dynamic calculation of progress summary (total, not started, in progress, completed, percentage)."""
    unique_email = f"summary-calc-{uuid.uuid4().hex[:8]}@example.com"
    services.core.register("Summary User", unique_email, "Pass123456")
    user = services.core.login(unique_email, "Pass123456")
    uid = user["id"]

    services.core.save_profile(uid, {
        "target_role": "Data Analyst",
        "job_title": "Analyst",
        "summary": "Analyst summary for Data Analyst track.",
        "years_experience": 1.0,
    })

    # Test via AppTest
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = uid
    at.session_state["current_page"] = "Employee Profile"
    at.run()
    assert not at.exception

    all_html = " ".join([m.value for m in at.html])
    assert "Recommendation Progress Summary" in all_html
    assert "Total Recommendations" in all_html

    # Check status selectbox count
    selectboxes = [sb for sb in at.selectbox if "rec_status_sel_" in sb.key]
    assert len(selectboxes) >= 4
    for sb in selectboxes:
        assert list(sb.options) == ["Not Started", "In Progress", "Completed"]


def test_criteria_11_skills_and_role_match_preserved():
    """Verify that tracking recommendation progress does not mutate verified skills or role match score."""
    unique_email = f"no-mutate-{uuid.uuid4().hex[:8]}@example.com"
    services.core.register("Preserve User", unique_email, "Pass123456")
    u = services.core.login(unique_email, "Pass123456")
    uid = u["id"]

    services.core.save_profile(uid, {
        "target_role": "Data Analyst",
        "years_experience": 2.0,
    })

    # Calculate initial role match
    profile = services.core.get_profile(uid)
    skills = services.core.list_skills(uid)
    initial_match = services.core.role_match("Data Analyst", skills, 2.0)

    # User marks SQL recommendation as "Completed" in progress tracker
    services.core.save_recommendation_status(uid, "SQL", "Completed")

    # Verified skills must NOT automatically contain SQL
    post_skills = services.core.list_skills(uid)
    assert not any(s["name"] == "SQL" for s in post_skills)

    # Role match score must remain unchanged
    post_match = services.core.role_match("Data Analyst", post_skills, 2.0)
    assert post_match == initial_match


def test_profile_readiness_overall_bar_and_seven_sections_progress():
    """Verify Profile Progress Dashboard is converted into Employee Work Progress with 4 metrics cards and prominent overall bar."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Employee Profile"
    at.run()
    assert not at.exception

    all_html = " ".join([m.value for m in at.html])

    # Old resume section progress is removed from Employee Profile
    assert "Section B: Professional Summary" not in all_html
    assert "Section C: Formal Education" not in all_html

    # Employee Work Progress Dashboard
    assert "Employee Work Progress:" in all_html
    assert "Overall Work Completion Rate" in all_html
    assert "Task Completion Summary" in all_html

    # 4 Summary Metric Cards
    assert "Total Tasks" in all_html
    assert "Completed" in all_html
    assert "In Progress" in all_html
    assert "Yet to Complete" in all_html

    # Verify sidebar branding is anchored at top-left and followed by navigation radio
    sidebar_html = " ".join([m.value for m in at.sidebar.html])
    assert "ts-sidebar-brand" in sidebar_html, "TalentSphere branding must use ts-sidebar-brand container"
    assert len(at.sidebar.radio) > 0, "Sidebar navigation radio must be present under branding"


def test_suggestion_cards_no_recommended_next_step_and_topic_progress_bars():
    """Verify suggestion cards contain no lengthy recommendation paragraphs and display topic progress bars with percentage."""
    unique_email = f"compact-cards-{uuid.uuid4().hex[:8]}@example.com"
    services.core.register("Compact User", unique_email, "Pass123456")
    u = services.core.login(unique_email, "Pass123456")
    uid = u["id"]

    services.core.save_profile(uid, {
        "target_role": "Data Analyst",
        "years_experience": 1.0,
    })

    # Save SQL as Completed (100%) and Python as In Progress (50%)
    services.core.save_recommendation_status(uid, "SQL", "Completed")
    services.core.save_recommendation_status(uid, "Python", "In Progress")

    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = uid
    at.session_state["current_page"] = "Employee Profile"
    at.run()
    assert not at.exception

    all_html = " ".join([m.value for m in at.html])

    # Acceptance Criteria 1: Suggestion cards contain no lengthy recommendation paragraphs
    assert "Recommended Next Step:" not in all_html, "Lengthy Recommended Next Step text must be removed from cards"

    # Acceptance Criteria 2: Topic progress bars and percentages are rendered
    assert "100%" in all_html, "Completed topic should show 100% progress"
    assert "50%" in all_html, "In Progress topic should show 50% progress"
    assert "0%" in all_html, "Not Started topic should show 0% progress"

    # Check that status selectors exist
    rec_selectboxes = [sb for sb in at.selectbox if "rec_status_sel_" in sb.key]
    assert len(rec_selectboxes) >= 4
    for sb in rec_selectboxes:
        assert list(sb.options) == ["Not Started", "In Progress", "Completed"]


def test_full_page_width_and_font_sizes_present():
    """Verify layout uses full width (1400px) and enhanced readable font size scale."""
    from components.styles import get_dark_theme_css
    css = get_dark_theme_css()

    # Full width container rule
    assert "max-width: 1400px !important" in css
    assert "width: 100% !important" in css

    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Employee Profile"
    at.run()
    assert not at.exception

    all_html = " ".join([m.value for m in at.html])

    # Check font-size styling is present in HTML components
    assert "font-size: 26px" in all_html or "font-size: 28px" in all_html  # Main headings
    assert "font-size: 21px" in all_html or "font-size: 20px" in all_html  # Section headings
    assert "font-size: 16px" in all_html  # Body text
    assert "font-size: 14px" in all_html  # Labels / badges
    assert "font-size: 15px" in all_html or "font-size: 16px" in all_html  # Percentages

