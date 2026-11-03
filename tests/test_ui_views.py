"""Integration test suite for TalentSphere UI/UX prototype pages.

Validates that all pages (Dashboard, Employee Profile, Skills & Goals,
Career Development, Login, Registration) mount and render without exceptions,
and thoroughly tests authentication, validation, tab switching, and access control.
"""

from pathlib import Path
import uuid
import pytest
from streamlit.testing.v1 import AppTest

APP_PATH = str(Path(__file__).parent.parent / "app.py")


def test_dashboard_renders():
    """Verify Dashboard page renders without exceptions."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["current_page"] = "Dashboard"
    at.run()
    assert not at.exception


def test_employee_profile_renders():
    """Verify Employee Profile page renders without exceptions."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["current_page"] = "Employee Profile"
    at.run()
    assert not at.exception


def test_skills_and_goals_renders():
    """Verify Skills & Goals page renders without exceptions."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["current_page"] = "Skills & Goals"
    at.run()
    assert not at.exception


def test_career_development_renders():
    """Verify Career Development page renders without exceptions."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["current_page"] = "Career Development"
    at.run()
    assert not at.exception


def test_login_page_renders():
    """Verify Login demonstration page renders without exceptions."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["current_page"] = "Login"
    at.run()
    assert not at.exception


def test_login_page_empty_validation():
    """Verify empty input fields trigger validation error message."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["current_page"] = "Login"
    at.run()
    at.text_input(key="login_email_input").input("")
    at.text_input(key="login_password_input").input("")
    at.button(key="btn_login_submit").click()
    at.run()
    assert len(at.error) > 0
    assert "Please enter both" in at.error[0].value


def test_login_page_invalid_email_validation():
    """Verify malformed email addresses trigger validation error message."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["current_page"] = "Login"
    at.run()
    at.text_input(key="login_email_input").input("invalidemailaddress")
    at.text_input(key="login_password_input").input("secretpass")
    at.button(key="btn_login_submit").click()
    at.run()
    assert len(at.error) > 0
    assert "valid email address" in at.error[0].value


def test_login_page_invalid_credentials():
    """Verify wrong password displays error message."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["current_page"] = "Login"
    at.run()
    at.text_input(key="login_email_input").input("eleanor.vance@talentsphere.io")
    at.text_input(key="login_password_input").input("wrongpassword123")
    at.button(key="btn_login_submit").click()
    at.run()
    assert len(at.error) > 0
    assert "Invalid email address or password" in at.error[0].value


def test_login_page_submit_success():
    """Verify submitting valid credentials logs in and redirects to Dashboard."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["current_page"] = "Login"
    at.run()
    at.text_input(key="login_email_input").input("eleanor.vance@talentsphere.io")
    at.text_input(key="login_password_input").input("validpassword123")
    at.button(key="btn_login_submit").click()
    at.run()
    assert at.session_state["is_authenticated"] is True
    assert at.session_state["current_page"] == "Dashboard"


def test_login_page_default_signin():
    """Verify demo credentials sign in and route to Dashboard."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["current_page"] = "Login"
    at.session_state["is_authenticated"] = False
    at.run()
    at.text_input(key="login_email_input").input("eleanor.vance@talentsphere.io")
    at.text_input(key="login_password_input").input("validpassword123")
    at.button(key="btn_login_submit").click()
    at.run()
    assert at.session_state["is_authenticated"] is True
    assert at.session_state["current_page"] == "Dashboard"


def test_login_page_navigate_to_registration():
    """Verify clicking the Register link navigates to the Registration page."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["current_page"] = "Login"
    at.run()
    at.button(key="link_to_register").click()
    at.run()
    assert at.session_state["current_page"] == "Registration"
    assert at.session_state["auth_tab"] == "register"


def test_registration_page_renders():
    """Verify Registration demonstration page renders without exceptions."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["current_page"] = "Registration"
    at.run()
    assert not at.exception


def test_tab_switcher_toggle():
    """Verify toggling between Sign In and Create Account views."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["current_page"] = "Login"
    at.session_state["auth_tab"] = "signin"
    at.run()
    assert at.session_state["auth_tab"] == "signin"

    at.button(key="link_to_register").click()
    at.run()
    assert at.session_state["auth_tab"] == "register"

    at.button(key="link_to_signin").click()
    at.run()
    assert at.session_state["auth_tab"] == "signin"


def test_registration_validation_rules():
    """Verify registration password validation rules and mismatch checks."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["current_page"] = "Login"
    at.session_state["auth_tab"] = "register"
    at.run()

    # Short password
    at.text_input(key="reg_name_input").input("Test User")
    at.text_input(key="reg_email_input").input("testuser@company.com")
    at.selectbox(key="reg_track_select").select("Senior Software Engineer")
    at.text_input(key="reg_password_input").input("short")
    at.text_input(key="reg_confirm_password_input").input("short")
    at.button(key="btn_register_submit").click()
    at.run()
    assert len(at.error) > 0
    assert "at least 8 characters" in at.error[0].value

    # Password without digits
    at.text_input(key="reg_password_input").input("lettersnodigits")
    at.text_input(key="reg_confirm_password_input").input("lettersnodigits")
    at.button(key="btn_register_submit").click()
    at.run()
    assert len(at.error) > 0
    assert "both letters and numbers" in at.error[0].value

    # Password mismatch
    at.text_input(key="reg_password_input").input("SecurePass1")
    at.text_input(key="reg_confirm_password_input").input("SecurePass2")
    at.button(key="btn_register_submit").click()
    at.run()
    assert len(at.error) > 0
    assert "do not match" in at.error[0].value


def test_registration_success_and_login():
    """Verify completing registration creates user in backend and routes to Dashboard."""
    unique_email = f"user-{uuid.uuid4().hex[:8]}@company.com"
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["current_page"] = "Login"
    at.session_state["auth_tab"] = "register"
    at.run()

    at.text_input(key="reg_name_input").input("Alex Rivera")
    at.text_input(key="reg_email_input").input(unique_email)
    at.selectbox(key="reg_track_select").select("Lead Systems Architect")
    at.text_input(key="reg_password_input").input("ValidPass123")
    at.text_input(key="reg_confirm_password_input").input("ValidPass123")
    at.button(key="btn_register_submit").click()
    at.run()

    assert at.session_state["is_authenticated"] is True
    assert at.session_state["current_page"] == "Dashboard"
    assert at.session_state["employee"]["name"] == "Alex Rivera"


def test_access_control_unauthenticated_guard():
    """Verify unauthenticated access to protected pages redirects to Login."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = False
    at.session_state["current_page"] = "Dashboard"
    at.run()
    assert at.session_state["current_page"] == "Login"


def test_sidebar_absent_before_login():
    """Verify sidebar is completely absent on unauthenticated pages."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = False
    at.session_state["current_page"] = "Login"
    at.run()
    # No sidebar radio navigation exists before login
    assert len(at.sidebar.radio) == 0


def test_sidebar_present_after_login():
    """Verify sidebar appears with navigation after successful authentication."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["current_page"] = "Dashboard"
    at.run()
    assert len(at.sidebar.radio) > 0
    assert at.sidebar.radio[0].key == "sidebar_navigation_radio"


def test_simplified_dashboard_elements_and_actions():
    """Verify simplified Overview dashboard renders welcome, summary cards, and working quick actions."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["current_page"] = "Dashboard"
    at.run()
    assert not at.exception

    # Verify quick action buttons exist
    assert at.button(key="action_btn_skills") is not None
    assert at.button(key="action_btn_career") is not None
    assert at.button(key="action_btn_advice") is not None

    # Test 'View My Skills' button navigation
    at.button(key="action_btn_skills").click()
    at.run()
    assert at.session_state["current_page"] == "Skills & Goals"

    # Reset to Dashboard and test 'Explore Career Paths' button navigation
    at.session_state["current_page"] = "Dashboard"
    at.run()
    at.button(key="action_btn_career").click()
    at.run()
    assert at.session_state["current_page"] == "Career Development"

    # Reset to Dashboard and test 'Get AI Career Advice' button toggle
    at.session_state["current_page"] = "Dashboard"
    at.run()
    at.button(key="action_btn_advice").click()
    at.run()
    assert at.session_state["show_ai_advice"] is True


def test_login_page_navigate_to_forgot_password():
    """Verify clicking Forgot password? navigates to the recovery form."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["current_page"] = "Login"
    at.run()
    at.button(key="btn_forgot_password_link").click()
    at.run()
    assert at.session_state["auth_tab"] == "forgot"
    assert at.text_input(key="forgot_email_input") is not None
    assert at.button(key="btn_forgot_submit") is not None


def test_forgot_password_form_submission_and_back():
    """Verify forgot password email validation, generic response, and return to sign in."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["current_page"] = "Login"
    at.session_state["auth_tab"] = "forgot"
    at.run()

    # Empty email
    at.text_input(key="forgot_email_input").input("")
    at.button(key="btn_forgot_submit").click()
    at.run()
    assert len(at.error) > 0
    assert "enter your work email" in at.error[0].value

    # Invalid email
    at.text_input(key="forgot_email_input").input("invalidemail")
    at.button(key="btn_forgot_submit").click()
    at.run()
    assert len(at.error) > 0
    assert "valid email address" in at.error[0].value

    # Unregistered email
    at.text_input(key="forgot_email_input").input("unregistered-account-987@company.com")
    at.button(key="btn_forgot_submit").click()
    at.run()
    assert len(at.error) > 0
    assert "not registered" in at.error[0].value

    # Registered email
    at.text_input(key="forgot_email_input").input("eleanor.vance@talentsphere.io")
    at.button(key="btn_forgot_submit").click()
    at.run()
    assert len(at.success) > 0
    assert "terminal" in at.success[0].value.lower() or "reset link" in at.success[0].value.lower()

    # Return to sign in
    at.button(key="link_forgot_to_signin").click()
    at.run()
    assert at.session_state["auth_tab"] == "signin"


def test_reset_password_invalid_token_ui():
    """Verify invalid or expired reset token shows error screen."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["current_page"] = "Login"
    at.session_state["auth_tab"] = "reset"
    at.session_state["reset_token"] = "invalid-token-xyz"
    at.run()

    assert at.button(key="btn_req_new_link") is not None
    at.button(key="btn_req_new_link").click()
    at.run()
    assert at.session_state["auth_tab"] == "forgot"


def test_reset_password_valid_token_ui_flow():
    """Verify entering new password via valid reset token updates credentials and routes to sign in."""
    from services.core import register, connect, login
    import secrets, hashlib
    from datetime import datetime, timedelta

    email = f"ui-reset-{uuid.uuid4().hex[:8]}@example.com"
    register("UI Reset User", email, "InitialPass123")
    with connect() as db:
        user_id = db.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()["id"]

    raw_token = secrets.token_urlsafe(32)
    tok_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    future = (datetime.now() + timedelta(minutes=20)).isoformat()
    with connect() as db:
        db.execute("INSERT INTO password_resets(user_id, token_hash, expires_at, used, created_at) VALUES(?,?,?,0,?)",
                   (user_id, tok_hash, future, datetime.now().isoformat()))

    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["current_page"] = "Login"
    at.session_state["auth_tab"] = "reset"
    at.session_state["reset_token"] = raw_token
    at.run()

    # Enter mismatched passwords
    at.text_input(key="reset_new_password_input").input("NewValidPass1")
    at.text_input(key="reset_confirm_password_input").input("MismatchPass2")
    at.button(key="btn_reset_submit").click()
    at.run()
    assert len(at.error) > 0
    assert "do not match" in at.error[0].value

    # Enter matching valid password
    at.text_input(key="reset_new_password_input").input("NewValidPass123")
    at.text_input(key="reset_confirm_password_input").input("NewValidPass123")
    at.button(key="btn_reset_submit").click()
    at.run()

    assert at.session_state["auth_tab"] == "signin"
    # Verify new password works
    assert login(email, "NewValidPass123") is not None


def test_remember_me_login_and_logout_ui_flow():
    """Verify login with Remember Me creates persistent token, and Sign Out clears it."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["current_page"] = "Login"
    at.session_state["is_authenticated"] = False
    at.run()

    at.text_input(key="login_email_input").input("eleanor.vance@talentsphere.io")
    at.text_input(key="login_password_input").input("validpassword123")
    at.checkbox(key="login_remember_chk").check()
    at.button(key="btn_login_submit").click()
    at.run()

    assert at.session_state["is_authenticated"] is True
    assert at.session_state["current_page"] == "Dashboard"
    assert at.session_state.get("remember_token") is not None

    # Sign out from sidebar
    at.button(key="btn_sidebar_signout").click()
    at.run()
    assert at.session_state["is_authenticated"] is False
    assert at.session_state.get("remember_token") is None
    assert at.session_state["current_page"] == "Login"


def test_login_without_remember_me():
    """Verify login without Remember Me authenticates for session only without persistent token."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["current_page"] = "Login"
    at.session_state["is_authenticated"] = False
    at.run()

    at.text_input(key="login_email_input").input("eleanor.vance@talentsphere.io")
    at.text_input(key="login_password_input").input("validpassword123")
    at.checkbox(key="login_remember_chk").uncheck()
    at.button(key="btn_login_submit").click()
    at.run()

    assert at.session_state["is_authenticated"] is True
    assert at.session_state.get("remember_token") is None


def test_session_restoration_from_persistent_session():
    """Verify valid persistent session automatically logs in unauthenticated visitor."""
    from services.core import connect, create_persistent_session
    with connect() as db:
        user_row = db.execute("SELECT id FROM users WHERE email='eleanor.vance@talentsphere.io'").fetchone()

    signed_token = create_persistent_session(user_row["id"])

    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = False
    at.session_state["current_page"] = "Login"
    at.session_state["remember_token"] = signed_token
    at.run()

    assert at.session_state["is_authenticated"] is True
    assert at.session_state["current_page"] == "Dashboard"
    assert at.session_state["employee"]["name"] == "Eleanor Vance"


def test_forgot_password_end_to_end_all_7_cases(capsys):
    """Verifies all 7 test cases specified in the requirements:
    1. Unregistered email -> error message; no reset URL in terminal.
    2. Registered email -> generates token & prints reset URL in terminal.
    3. Open reset URL -> displays password reset form.
    4. Submit valid new password & confirm -> updates password.
    5. Reuse same URL -> rejects already-used token.
    6. Expired / invalid token -> displays appropriate error.
    7. Login works with new password.
    """
    from services.core import register, login
    unique_email = f"e2e-user-{uuid.uuid4().hex[:8]}@example.com"
    initial_pass = "InitialPass123"
    new_pass = "SuperSecureNewPass456"

    # Register user
    ok, _ = register("E2E User", unique_email, initial_pass)
    assert ok

    # 1. Unregistered email check
    at1 = AppTest.from_file(APP_PATH, default_timeout=30)
    at1.session_state["current_page"] = "Login"
    at1.session_state["auth_tab"] = "forgot"
    at1.run()
    at1.text_input(key="forgot_email_input").input("nonexistent-person-999@domain.com")
    at1.button(key="btn_forgot_submit").click()
    at1.run()
    assert len(at1.error) > 0
    assert "not registered" in at1.error[0].value.lower()
    captured1 = capsys.readouterr()
    assert "Password reset URL:" not in captured1.out

    # 2. Registered email check
    at2 = AppTest.from_file(APP_PATH, default_timeout=30)
    at2.session_state["current_page"] = "Login"
    at2.session_state["auth_tab"] = "forgot"
    at2.run()
    at2.text_input(key="forgot_email_input").input(unique_email)
    at2.button(key="btn_forgot_submit").click()
    at2.run()
    assert len(at2.success) > 0
    captured2 = capsys.readouterr()
    assert "Password reset URL: http" in captured2.out
    assert "?reset_token=" in captured2.out

    # Extract the token printed in terminal
    line = next(l for l in captured2.out.splitlines() if "Password reset URL:" in l)
    raw_token = line.split("?reset_token=")[-1].strip()

    # 3. Open that URL -> displays password-reset form
    at3 = AppTest.from_file(APP_PATH, default_timeout=30)
    at3.session_state["current_page"] = "Login"
    at3.session_state["auth_tab"] = "reset"
    at3.session_state["reset_token"] = raw_token
    at3.run()
    assert at3.text_input(key="reset_new_password_input") is not None
    assert at3.button(key="btn_reset_submit") is not None

    # 4. Submit valid new password and confirmation -> update successfully
    at3.text_input(key="reset_new_password_input").input(new_pass)
    at3.text_input(key="reset_confirm_password_input").input(new_pass)
    at3.button(key="btn_reset_submit").click()
    at3.run()
    assert at3.session_state["auth_tab"] == "signin"

    # 5. Reuse the same URL -> reject already-used token
    at4 = AppTest.from_file(APP_PATH, default_timeout=30)
    at4.session_state["current_page"] = "Login"
    at4.session_state["auth_tab"] = "reset"
    at4.session_state["reset_token"] = raw_token
    at4.run()
    # Shows invalid/expired link screen
    assert at4.button(key="btn_req_new_link") is not None

    # 6. Invalid token -> displays appropriate error
    at5 = AppTest.from_file(APP_PATH, default_timeout=30)
    at5.session_state["current_page"] = "Login"
    at5.session_state["auth_tab"] = "reset"
    at5.session_state["reset_token"] = "fake-token-never-created"
    at5.run()
    assert at5.button(key="btn_req_new_link") is not None

    # 7. Verify login works with new password, and old password fails
    assert login(unique_email, initial_pass) is None
    logged_in_user = login(unique_email, new_pass)
    assert logged_in_user is not None
    assert logged_in_user["email"] == unique_email


def test_sidebar_navigation_clicks_all_items():
    """Verify that every sidebar navigation radio option responds to clicks and renders its page."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Dashboard"
    at.run()
    assert not at.exception
    assert len(at.sidebar.radio) > 0

    radio = at.sidebar.radio[0]
    options = list(radio.options)
    # Check that required 4 items are present
    assert any("Dashboard" in opt for opt in options)
    assert any(opt in ("Profile", "Employee Profile") or "Profile" in opt for opt in options)
    assert any("Skills & Goals" in opt for opt in options)
    assert any("Career Development" in opt for opt in options)

    # 1. Click Profile
    for opt in options:
        if opt in ("Profile", "Employee Profile") or "Profile" in opt:
            radio.set_value(opt)
            break
    at.run()
    assert not at.exception
    assert at.session_state["current_page"] == "Employee Profile"
    assert at.sidebar.radio[0].value in ("Profile", "Employee Profile") or "Profile" in at.sidebar.radio[0].value

    # 2. Click Skills & Goals
    radio = at.sidebar.radio[0]
    for opt in options:
        if "Skills & Goals" in opt:
            radio.set_value(opt)
            break
    at.run()
    assert not at.exception
    assert at.session_state["current_page"] == "Skills & Goals"
    assert "Skills" in at.sidebar.radio[0].value

    # 3. Click Career Development
    radio = at.sidebar.radio[0]
    for opt in options:
        if "Career Development" in opt:
            radio.set_value(opt)
            break
    at.run()
    assert not at.exception
    assert at.session_state["current_page"] == "Career Development"
    assert "Career" in at.sidebar.radio[0].value

    # 4. Click Dashboard
    radio = at.sidebar.radio[0]
    for opt in options:
        if "Dashboard" in opt:
            radio.set_value(opt)
            break
    at.run()
    assert not at.exception
    assert at.session_state["current_page"] == "Dashboard"
    assert "Dashboard" in at.sidebar.radio[0].value


def test_sidebar_programmatic_and_manual_sync():
    """Verify programmatic navigation from dashboard buttons updates sidebar radio, and vice-versa."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Dashboard"
    at.run()
    assert not at.exception

    # Click 'Explore Career Paths' button on Dashboard
    at.button(key="action_btn_career").click()
    at.run()
    assert not at.exception
    assert at.session_state["current_page"] == "Career Development"
    assert "Career" in at.sidebar.radio[0].value

    # Navigate back to Dashboard via sidebar radio
    radio = at.sidebar.radio[0]
    for opt in radio.options:
        if "Dashboard" in opt:
            radio.set_value(opt)
            break
    at.run()
    assert not at.exception
    assert at.session_state["current_page"] == "Dashboard"
    assert "Dashboard" in at.sidebar.radio[0].value


def test_ui_visibility_css_rules_present():
    """Verify CSS provides strong contrast for labels, white inputs with dark text, and cyan active tabs."""
    from components.styles import get_dark_theme_css
    css = get_dark_theme_css()

    # High contrast white labels & questions
    assert "data-testid=\"stWidgetLabel\"" in css
    assert "#FFFFFF !important" in css

    # Input fields: dark text on white backgrounds
    assert "background-color: #FFFFFF !important" in css
    assert "color: #0F172A !important" in css

    # Tabs: cyan for active, visible inactive
    assert "#00D2FF !important" in css
    assert "button[data-baseweb=\"tab\"][aria-selected=\"true\"]" in css


def test_edit_profile_layout_and_buttons():
    """Verify Edit Profile toggles side-by-side editor, displays inputs, and cancels cleanly."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Employee Profile"
    at.run()
    assert not at.exception

    # Initially in View Mode
    assert at.session_state.get("is_editing_profile", False) is False
    assert at.button(key="btn_enter_edit_mode") is not None

    # Enter Edit Mode
    at.button(key="btn_enter_edit_mode").click()
    at.run()
    assert not at.exception
    assert at.session_state["is_editing_profile"] is True

    # Both Save Changes and Cancel buttons are clearly positioned
    assert at.button(key="btn_save_profile_main") is not None
    assert at.button(key="btn_cancel_profile_main") is not None

    # Form fields rendered
    assert at.text_input(key="draft_name_in") is not None
    assert at.text_input(key="draft_title_in") is not None

    # Cancel returns to View Mode
    at.button(key="btn_cancel_profile_main").click()
    at.run()
    assert not at.exception
    assert at.session_state["is_editing_profile"] is False


def test_suggestions_display_topic_titles_only():
    """Verify suggestions and improvements section renders topic titles without expanded explanations."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Employee Profile"
    at.run()
    assert not at.exception

    # Verify no expanded explanation text is rendered inside the suggestions boxes
    all_html_text = " ".join([m.value for m in at.html])
    assert "Why it matters:" not in all_html_text
    assert "Recommended Action:" not in all_html_text


def test_profile_section_order_suggestions_below_a_and_b():
    """Verify order: Section A, Section B, Section C (Education in Tab 1), Suggestions at bottom."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Employee Profile"
    at.run()
    assert not at.exception

    all_html = " ".join([m.value for m in at.html])
    pos_sec_a = all_html.find("Section A: Employee Details")
    pos_sec_b = all_html.find("Section B: Process & Goals")
    pos_sec_c = all_html.find("Section C: Task Management")
    pos_sug = all_html.find("Suggestions & Improvements")

    assert pos_sec_a != -1, "Section A: Employee Details should be present"
    assert pos_sec_b != -1, "Section B: Process & Goals should be present"
    assert pos_sec_c != -1, "Section C: Task Management should be present and visible"
    assert pos_sug != -1, "Suggestions & Improvements should be present"

    # Crucial verification: Suggestions appears below Section A, B, and C
    assert pos_sec_a < pos_sec_b, "Section A must precede Section B"
    assert pos_sec_b < pos_sec_c, "Section B must precede Section C"
    assert pos_sec_c < pos_sug, "Suggestions must appear below Section C at the bottom of the page"


def test_sidebar_branding_and_no_navigation_label():
    """Verify sidebar has TalentSphere + ELEVATE PLATFORM branding and no NAVIGATION label."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["current_page"] = "Dashboard"
    at.run()
    assert not at.exception

    sidebar_html = " ".join([m.value for m in at.sidebar.html])
    assert "TalentSphere" in sidebar_html
    assert "ELEVATE PLATFORM" in sidebar_html

    # Ensure the NAVIGATION heading was completely removed
    assert ">Navigation<" not in sidebar_html
    assert ">NAVIGATION<" not in sidebar_html


def test_sidebar_navigation_switching():
    """Verify selecting sidebar navigation items navigates directly to the target page."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["current_page"] = "Dashboard"
    at.run()
    assert not at.exception
    assert at.sidebar.radio[0] is not None

    # Switch to Employee Profile
    at.sidebar.radio[0].set_value("👤 Employee Profile")
    at.run()
    assert not at.exception
    assert at.session_state["current_page"] == "Employee Profile"

    # Switch to Skills & Goals
    at.sidebar.radio[0].set_value("🎯 Skills & Goals")
    at.run()
    assert not at.exception
    assert at.session_state["current_page"] == "Skills & Goals"

    # Switch to Career Development
    at.sidebar.radio[0].set_value("🚀 Career Development")
    at.run()
    assert not at.exception
    assert at.session_state["current_page"] == "Career Development"

    # Switch back to Dashboard
    at.sidebar.radio[0].set_value("📊 Dashboard")
    at.run()
    assert not at.exception
    assert at.session_state["current_page"] == "Dashboard"


def test_sidebar_no_circles_and_larger_fonts_in_css():
    """Verify CSS removes radio circles and sets larger fonts and icons for sidebar items."""
    from components.styles import get_dark_theme_css
    css = get_dark_theme_css()

    # Circle indicator removal
    assert "section[data-testid=\"stSidebar\"] div[role=\"radiogroup\"] label > div:first-child" in css
    assert "display: none !important" in css

    # Increased text and icon size
    assert "font-size: 1.05rem !important" in css

    # Glowing active highlight
    assert "rgba(0, 210, 255, 0.18)" in css
    assert "rgba(255, 42, 117, 0.12)" in css


def test_section_c_sequential_view_and_edit_mode_tab_ordering():
    """Verify Section C is rendered directly in View Mode and edit tabs are available in Edit Mode."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Employee Profile"
    at.run()
    assert not at.exception

    all_html = " ".join([m.value for m in at.html])
    assert "Section C: Task Management" in all_html
    assert "Section D: Challenges & Support" in all_html

    # Switch to Edit Mode
    at.button(key="btn_enter_edit_mode").click()
    at.run()
    assert not at.exception

    # Edit Mode: Tabs are Employee Details, Process & Goals, Challenges & Support
    edit_tab_labels = [t.label for t in at.tabs]
    assert any("Employee Details" in l for l in edit_tab_labels)
    assert any("Process & Goals" in l for l in edit_tab_labels)
    assert any("Challenges & Support" in l for l in edit_tab_labels)


def test_suggestions_recommendation_status_and_persistence():
    """Verify recommendation status persistence to SQLite, independence, and user isolation."""
    import services.core
    unique_user1 = f"rec-user-1-{uuid.uuid4().hex[:8]}@example.com"
    unique_user2 = f"rec-user-2-{uuid.uuid4().hex[:8]}@example.com"
    services.core.register("User One", unique_user1, "Pass123456")
    services.core.register("User Two", unique_user2, "Pass123456")

    u1 = services.core.login(unique_user1, "Pass123456")
    u2 = services.core.login(unique_user2, "Pass123456")
    uid1 = u1["id"]
    uid2 = u2["id"]

    # Save independent statuses for User 1
    services.core.save_recommendation_status(uid1, "SQL", "In Progress")
    services.core.save_recommendation_status(uid1, "Python", "Completed")
    services.core.save_recommendation_status(uid1, "Communication", "Not Started")

    # Save different status for User 2
    services.core.save_recommendation_status(uid2, "SQL", "Completed")

    # Verify User 1 statuses
    u1_statuses = services.core.get_recommendation_statuses(uid1)
    assert u1_statuses["sql"] == "In Progress"
    assert u1_statuses["python"] == "Completed"
    assert u1_statuses["communication"] == "Not Started"

    # Verify User 2 status is isolated
    u2_statuses = services.core.get_recommendation_statuses(uid2)
    assert u2_statuses["sql"] == "Completed"
    assert "python" not in u2_statuses

    # Update User 1 SQL status (avoid duplicate records)
    services.core.save_recommendation_status(uid1, "SQL", "Completed")
    progress_records = services.core.get_progress(uid1)
    sql_records = [p for p in progress_records if p["item"] == "SQL"]
    assert len(sql_records) == 1, "Should update existing record without creating duplicates"
    assert sql_records[0]["status"] == "Completed"
    assert sql_records[0]["percent"] == 100


def test_suggestions_ui_cards_and_dynamic_summary():
    """Verify Suggestions & Improvements UI cards display topics, status dropdowns, and progress summary."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Employee Profile"
    at.run()
    assert not at.exception

    all_html = " ".join([m.value for m in at.html])

    # Header and Summary presence
    assert "Suggestions & Improvements" in all_html
    assert "Recommendation Progress Summary" in all_html
    assert "Total Recommendations" in all_html
    assert "Not Started" in all_html
    assert "In Progress" in all_html
    assert "Completed" in all_html
    assert "Completion Rate:" in all_html

    # Check status selectors exist
    rec_selectboxes = [sb for sb in at.selectbox if "rec_status_sel_" in sb.key]
    assert len(rec_selectboxes) > 0, "Recommendation cards should have status selectboxes"
    first_sb = rec_selectboxes[0]
    assert list(first_sb.options) == ["Not Started", "In Progress", "Completed"]


def test_tracking_status_does_not_mutate_verified_skills():
    """Verify that marking a recommendation as Completed only tracks progress and does not add verified skills."""
    import services.core
    unique_user = f"track-only-{uuid.uuid4().hex[:8]}@example.com"
    services.core.register("Track User", unique_user, "Pass123456")
    u = services.core.login(unique_user, "Pass123456")
    uid = u["id"]

    # Initial skills
    initial_skills = services.core.list_skills(uid)
    assert not any(s["name"] == "System Design" for s in initial_skills)

    # Set tracking status of System Design to Completed
    services.core.save_recommendation_status(uid, "System Design", "Completed")

    # Skills list must remain unchanged (tracking progress != verified skill)
    post_skills = services.core.list_skills(uid)
    assert not any(s["name"] == "System Design" for s in post_skills)
