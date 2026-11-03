"""Test suite for the Dashdark X inspired sidebar redesign in TalentSphere.

Validates:
1. Expanded mode structure: branding, collapse control, search input, 5 nav options, user card, account settings, session controls.
2. Search input filtering: searching keywords/names filters navigation radio options.
3. Clearing search restores full 5-item navigation list.
4. Collapse / expand toggle button updates session state between Expanded and Collapsed modes.
5. Collapsed mode structure: compact header, expand button, avatar, and compact session controls.
6. Navigation route preservation and backward compatibility.
7. Reset Data and Sign Out functionality preserved in both modes.
8. CSS design tokens: dark theme palette (#0D111D / #161A29), slim cyan indicator (border-left: 3.5px solid #00D2FF), active highlight.
"""

from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest
import services.core
from components.styles import get_dark_theme_css

APP_PATH = str(Path(__file__).parent.parent / "app.py")


def test_sidebar_expanded_structure():
    """Verify expanded mode contains branding, collapse button, search input, user card, and session buttons."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Dashboard"
    at.session_state["sidebar_collapsed"] = False
    at.run()
    assert not at.exception

    # 1. Branding
    sidebar_html = " ".join([m.value for m in at.sidebar.html])
    assert "ts-sidebar-brand" in sidebar_html
    assert "TalentSphere" in sidebar_html
    assert "ELEVATE PLATFORM" in sidebar_html

    # 2. Collapse button
    assert at.sidebar.button(key="btn_sidebar_collapse") is not None

    # 3. Search input
    assert at.sidebar.text_input(key="sidebar_search_input") is not None

    # 4. Navigation radio with all 5 core routes
    radio = at.sidebar.radio[0]
    assert radio.key == "sidebar_navigation_radio"
    options = list(radio.options)
    assert len(options) == 5
    assert any("Dashboard" in opt for opt in options)
    assert any(opt in ("Profile", "Employee Profile") or "Profile" in opt for opt in options)
    assert any("Skills & Goals" in opt for opt in options)
    assert any("Resume Builder" in opt for opt in options)
    assert any("Career Development" in opt for opt in options)

    # 5. User card and Session buttons
    assert at.sidebar.button(key="btn_sidebar_reset") is not None
    assert at.sidebar.button(key="btn_sidebar_signout") is not None


def test_sidebar_search_filtering():
    """Verify that entering keywords into the search input filters navigation options."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Dashboard"
    at.session_state["sidebar_collapsed"] = False
    at.run()
    assert not at.exception

    # Filter for Resume Builder
    at.sidebar.text_input(key="sidebar_search_input").input("resume")
    at.run()
    assert not at.exception

    radio = at.sidebar.radio[0]
    options = list(radio.options)
    assert len(options) == 1
    assert "Resume Builder" in options[0]

    # Filter for Profile via keyword 'tasks'
    at.sidebar.text_input(key="sidebar_search_input").input("tasks")
    at.run()
    assert not at.exception

    radio = at.sidebar.radio[0]
    options = list(radio.options)
    assert len(options) == 1
    assert options[0] in ("Profile", "Employee Profile") or "Profile" in options[0]

    # Clear button clears filter
    at.sidebar.button(key="btn_clear_nav_search").click()
    at.run()
    assert not at.exception
    assert len(at.sidebar.radio[0].options) == 5


def test_sidebar_collapse_and_expand_toggle():
    """Verify collapse button toggles sidebar_collapsed to True and expand button restores it."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Dashboard"
    at.session_state["sidebar_collapsed"] = False
    at.run()
    assert not at.exception

    # Click collapse button
    at.sidebar.button(key="btn_sidebar_collapse").click()
    at.run()
    assert not at.exception
    assert at.session_state["sidebar_collapsed"] is True

    # In collapsed mode, expand button must be present
    assert at.sidebar.button(key="btn_sidebar_expand") is not None

    # Click expand button
    at.sidebar.button(key="btn_sidebar_expand").click()
    at.run()
    assert not at.exception
    assert at.session_state["sidebar_collapsed"] is False
    assert at.sidebar.button(key="btn_sidebar_collapse") is not None


def test_sidebar_collapsed_mode_preserves_controls():
    """Verify that in collapsed mode, session controls and navigation remain accessible."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Dashboard"
    at.session_state["sidebar_collapsed"] = True
    at.run()
    assert not at.exception

    # Navigation radio remains present
    assert len(at.sidebar.radio) > 0
    # Compact reset and signout buttons are present
    assert at.sidebar.button(key="btn_sidebar_reset") is not None
    assert at.sidebar.button(key="btn_sidebar_signout") is not None


def test_sidebar_css_design_tokens():
    """Verify that get_dark_theme_css contains Dashdark X styling, slim cyan indicator, and card tokens."""
    css = get_dark_theme_css()

    # Dark navy canvas & sidebar
    assert "#0D111D" in css
    # Slim cyan left active indicator
    assert "border-left: 3.5px solid #00D2FF" in css
    # Active menu gradient
    assert "rgba(0, 210, 255, 0.18)" in css
    assert "rgba(255, 42, 117, 0.12)" in css
    # Circle indicator removal
    assert 'section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child' in css
    assert "display: none !important" in css
    # Search input styling
    assert 'section[data-testid="stSidebar"] div[data-testid="stTextInput"] input' in css
    # Popover account styling
    assert 'section[data-testid="stSidebar"] div[data-testid="stPopover"]' in css


def test_no_horizontal_top_navbar_on_dashboard_and_exclusive_vertical_sidebar():
    """Verify horizontal navbar (Skill Matrix, Trajectory, Mentorship, Benchmarks) is completely removed."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Dashboard"
    at.run()
    assert not at.exception

    # Check all rendered HTML across the main page content
    main_html = " ".join([m.value for m in at.html])

    # Assert horizontal top navbar is removed
    assert "ts-top-nav-bar" not in main_html
    assert "Skill Matrix" not in main_html
    assert "Mentorship" not in main_html
    assert "Benchmarks" not in main_html

    # Assert vertical left sidebar is the exclusive navigation
    assert len(at.sidebar.radio) > 0
    radio = at.sidebar.radio[0]
    assert radio.key == "sidebar_navigation_radio"
    options = list(radio.options)
    assert len(options) == 5
    assert any("Dashboard" in opt for opt in options)
    assert any(opt in ("Profile", "Employee Profile") or "Profile" in opt for opt in options)
    assert any("Skills & Goals" in opt for opt in options)
    assert any("Resume Builder" in opt for opt in options)
    assert any("Career Development" in opt for opt in options)


def test_view_profile_button_navigates_to_employee_profile():
    """Verify that clicking the View Profile button navigates directly to Employee Profile."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Dashboard"
    at.session_state["sidebar_collapsed"] = False
    at.run()
    assert not at.exception

    btn = at.sidebar.button(key="btn_sidebar_view_profile")
    assert btn is not None
    btn.click()
    at.run()
    assert not at.exception
    assert at.session_state["current_page"] == "Employee Profile"


def test_sidebar_default_expanded_on_startup():
    """Verify sidebar is expanded by default without requiring manual expand click."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Dashboard"
    at.run()
    assert not at.exception
    assert at.session_state.get("sidebar_collapsed") is False
    assert at.sidebar.button(key="btn_sidebar_collapse") is not None


def test_sidebar_account_settings_and_popover():
    """Verify Account Settings popover is visible and its profile button works."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Dashboard"
    at.session_state["sidebar_collapsed"] = False
    at.run()
    assert not at.exception
    assert at.sidebar.button(key="btn_account_popover_profile") is not None
    at.sidebar.button(key="btn_account_popover_profile").click()
    at.run()
    assert not at.exception
    assert at.session_state["current_page"] == "Employee Profile"


def test_sidebar_css_width_and_lucide_outline_icons():
    """Verify CSS sets 290px width (285-300px range), removes white circles, and targets all Lucide outline icons."""
    css = get_dark_theme_css()
    assert "width: 290px !important" in css
    assert "min-width: 290px !important" in css
    assert "max-width: 290px !important" in css
    # Lucide outline icons in CSS
    assert "circle cx='12' cy='8' r='5'" in css  # user-round
    assert "circle cx='12' cy='12' r='10'" in css  # target
    assert "path d='M14 2v4a2 2 0 0 0 2 2h4'" in css  # file-user
    assert "polyline points='22 7 13.5 15.5 8.5 10.5 2 17'" in css  # trending-up
    assert "M12.22 2h-.44a2 2 0 0 0-2 2" in css  # settings
    # Toggle icons (panel-left-close & panel-left-open)
    assert "m16 15-3-3 3-3" in css  # panel-left-close
    assert "m14 9 3 3-3 3" in css  # panel-left-open
    # Identical 48px height for all nav buttons
    assert "height: 48px !important" in css
    # No purple accents in sidebar section
    sidebar_css_block = css.split("/* 2. Sidebar Redesign")[1].split("/* 3. Elevated Cards")[0]
    assert "purple" not in sidebar_css_block.lower()


def test_sidebar_profile_label_renaming():
    """Verify navigation label for Employee Profile is displayed as Profile."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Dashboard"
    at.run()
    assert not at.exception

    # Check that NavItem supports both Profile and Employee Profile
    radio = at.sidebar.radio[0]
    options = list(radio.options)
    assert any("Profile" in opt for opt in options)

    # Navigate to Profile using set_value("Profile")
    radio.set_value("Profile")
    at.run()
    assert not at.exception
    assert at.session_state["current_page"] == "Employee Profile"

    # Also verify set_value("Employee Profile")
    radio.set_value("Employee Profile")
    at.run()
    assert not at.exception
    assert at.session_state["current_page"] == "Employee Profile"



