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
    assert any("Employee Profile" in opt for opt in options)
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
    assert "Employee Profile" in options[0]

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
    assert any("Employee Profile" in opt for opt in options)
    assert any("Skills & Goals" in opt for opt in options)
    assert any("Resume Builder" in opt for opt in options)
    assert any("Career Development" in opt for opt in options)

