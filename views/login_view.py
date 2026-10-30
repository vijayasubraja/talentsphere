"""TalentSphere – Modern Career Growth Login & Registration View.

Clean, modern, professional, and easy-to-use dual-panel interface:
- Left panel (dark navy #111B30): "Build your career with confidence.",
  concise description, fitted career growth illustration, and 3 key benefits.
- Right panel (crisp white #FFFFFF): "Welcome back" heading, clean email and password
  fields with inline show/hide password toggle, Remember me & Forgot password row,
  one prominent blue "Sign In →" button, and subtle footer link to Create an account.
- Free of faded decorative background words or distracting elements.
"""

from __future__ import annotations
import base64
import os
import streamlit as st
import services.core


def _get_base64_image(file_path: str) -> str:
    """Reads a local image file and returns its base64 encoded data URI."""
    if os.path.exists(file_path):
        with open(file_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode("utf-8")
            ext = os.path.splitext(file_path)[1].lower().replace(".", "")
            if ext == "jpg":
                ext = "jpeg"
            return f"data:image/{ext};base64,{encoded}"
    return ""


def render_login_page(initial_tab: str = "signin", cookie_controller: Any = None) -> None:
    """Renders the simplified, distraction-free TalentSphere login & registration interface."""

    # 1. Initialize SQLite database
    services.core.init_db()

    # 2. Manage active auth tab in session state
    if initial_tab in ("register", "forgot", "reset"):
        st.session_state["auth_tab"] = initial_tab
    elif "auth_tab" not in st.session_state:
        st.session_state["auth_tab"] = initial_tab
    elif initial_tab == "register" and st.session_state.get("current_page") == "Registration":
        st.session_state["auth_tab"] = "register"

    current_tab = st.session_state.get("auth_tab", "signin")

    # 3. Load brand assets
    logo_path = os.path.join("assets", "logo.png")
    logo_uri = _get_base64_image(logo_path)

    career_img_path = os.path.join("assets", "career_growth.png")
    if not os.path.exists(career_img_path):
        career_img_path = os.path.join("assets", "career_growth_clean.png")
    career_img_uri = _get_base64_image(career_img_path)

    # 4. Inject clean, modern styles
    st.markdown(
        """
        <style>
        /* Google Fonts & Material Icons */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@500;600;700;800&family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

        /* Hide default Streamlit top header bar on login view */
        header[data-testid="stHeader"] {
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
            padding: 0 !important;
        }

        /* Clean off-white background with subtle light gradient; no faded background words */
        div[data-testid="stAppViewContainer"] {
            background-color: #F8FAFC !important;
            background-image: linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%) !important;
            background-attachment: fixed !important;
        }

        /* Centered viewport layout with generous whitespace */
        .main {
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            min-height: 100vh !important;
        }
        .block-container {
            max-width: 980px !important;
            margin: auto !important;
            padding-top: 1rem !important;
            padding-bottom: 1.5rem !important;
            padding-left: 1.25rem !important;
            padding-right: 1.25rem !important;
            background: transparent !important;
        }

        /* Header & Branding */
        .ts-top-brand-bar {
            width: 100%;
            max-width: 960px;
            margin: 0 auto 0.75rem auto;
            display: flex;
            align-items: center;
            justify-content: flex-start;
            padding: 0 0.25rem;
        }
        .ts-brand-logo-wrap {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        .ts-brand-logo-img {
            height: 38px;
            width: 38px;
            object-fit: contain;
            display: block;
            border-radius: 8px;
        }
        .ts-brand-logo-icon {
            width: 38px;
            height: 38px;
            border-radius: 10px;
            background: #2563EB;
            color: #FFFFFF;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 6px rgba(37, 99, 235, 0.25);
        }
        .ts-brand-text-wrap {
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .ts-brand-logo-text {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 1.25rem;
            font-weight: 800;
            color: #111827;
            line-height: 1.15;
            letter-spacing: -0.02em;
        }
        .ts-brand-logo-sub {
            font-family: 'Inter', sans-serif;
            font-size: 0.75rem;
            color: #64748B;
            font-weight: 500;
            letter-spacing: 0.01em;
            margin-top: 2px;
        }

        /* Centered Login Card Container */
        div[data-testid="stHorizontalBlock"]:has(.ts-left-panel) {
            max-width: 960px !important;
            margin: 0 auto !important;
            background: #FFFFFF !important;
            border-radius: 16px !important;
            border: 1px solid #E2E8F0 !important;
            box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.08), 0 8px 10px -6px rgba(15, 23, 42, 0.03) !important;
            overflow: hidden !important;
            min-height: 520px !important;
        }

        /* Left Column: Dark Navy (#111B30) Career Introduction */
        div[data-testid="stHorizontalBlock"]:has(.ts-left-panel) > div[data-testid="stColumn"]:first-child {
            background-color: #111B30 !important;
            padding: 2.25rem 2rem !important;
            border-radius: 16px 0 0 16px !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
        }

        /* Right Column: Clean White (#FFFFFF) Login Form */
        div[data-testid="stHorizontalBlock"]:has(.ts-left-panel) > div[data-testid="stColumn"]:last-child {
            background-color: #FFFFFF !important;
            padding: 2.25rem 2.5rem !important;
            border-radius: 0 16px 16px 0 !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.ts-left-panel) > div[data-testid="stColumn"]:last-child div[data-testid="stVerticalBlock"] {
            gap: 0.5rem !important;
        }

        /* Left Panel Internal Elements */
        .ts-left-panel {
            color: #FFFFFF;
            display: flex;
            flex-direction: column;
            justify-content: center;
            height: 100%;
        }
        .ts-left-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            background: rgba(37, 99, 235, 0.16);
            border: 1px solid rgba(59, 130, 246, 0.28);
            color: #93C5FD;
            font-size: 0.74rem;
            font-weight: 600;
            letter-spacing: 0.02em;
            width: fit-content;
            margin-bottom: 0.75rem;
        }
        .ts-left-badge-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #38BDF8;
            box-shadow: 0 0 6px rgba(56, 189, 248, 0.7);
        }
        .ts-left-title {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 1.55rem;
            font-weight: 700;
            color: #FFFFFF;
            line-height: 1.3;
            letter-spacing: -0.02em;
            margin: 0 0 0.5rem 0;
        }
        .ts-left-desc {
            font-family: 'Inter', sans-serif;
            font-size: 0.88rem;
            color: #94A3B8;
            line-height: 1.55;
            margin: 0 0 1rem 0;
        }
        .ts-left-illustration-box {
            width: 100%;
            margin: 0.25rem 0 1.15rem 0;
            display: flex;
            justify-content: center;
            align-items: center;
            border-radius: 10px;
            overflow: hidden;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.08);
            padding: 0.5rem;
        }
        .ts-left-illustration {
            width: 100%;
            max-height: 125px;
            object-fit: contain;
            display: block;
            border-radius: 6px;
        }
        .ts-left-benefits {
            display: flex;
            flex-direction: column;
            gap: 0.6rem;
        }
        .ts-benefit-item {
            display: flex;
            align-items: center;
            gap: 0.65rem;
            font-family: 'Inter', sans-serif;
            font-size: 0.85rem;
            color: #E2E8F0;
            font-weight: 500;
            line-height: 1.35;
        }
        .ts-benefit-icon {
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: rgba(37, 99, 235, 0.25);
            color: #60A5FA;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }
        .ts-benefit-icon .material-symbols-outlined {
            font-size: 13px !important;
            font-weight: 700 !important;
        }

        /* Right Panel: Clean Typography & Inputs */
        .ts-right-panel {
            display: flex;
            flex-direction: column;
            justify-content: center;
            width: 100%;
            max-width: 380px;
            margin: 0 auto;
        }
        .ts-auth-header {
            margin-bottom: 1.25rem;
        }
        .ts-auth-title {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 1.55rem;
            font-weight: 700;
            color: #111827;
            letter-spacing: -0.02em;
            margin: 0 0 0.35rem 0;
            line-height: 1.25;
        }
        .ts-auth-subtitle {
            font-family: 'Inter', sans-serif;
            font-size: 0.88rem;
            color: #64748B;
            margin: 0;
            line-height: 1.5;
        }

        /* Input Controls */
        .ts-right-panel div[data-testid="stTextInput"],
        .ts-right-panel div[data-testid="stSelectbox"] {
            margin-bottom: 0.35rem !important;
        }
        .ts-right-panel div[data-testid="stTextInput"] label,
        .ts-right-panel div[data-testid="stSelectbox"] label {
            font-family: 'Inter', sans-serif !important;
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            margin-bottom: 0.3rem !important;
            color: #111827 !important;
        }
        .ts-right-panel div[data-testid="stTextInput"] input {
            padding: 10px 14px !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 0.92rem !important;
            border-radius: 8px !important;
            height: 44px !important;
            border: 1px solid #CBD5E1 !important;
            background: #FFFFFF !important;
            color: #111827 !important;
            transition: all 0.15s ease-in-out !important;
        }
        .ts-right-panel div[data-testid="stTextInput"] input::placeholder {
            color: #94A3B8 !important;
        }
        .ts-right-panel div[data-testid="stTextInput"] input:focus {
            border-color: #2563EB !important;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12) !important;
            outline: none !important;
        }
        .ts-right-panel div[data-testid="stSelectbox"] div[data-baseweb="select"] {
            min-height: 44px !important;
            font-size: 0.92rem !important;
            border-radius: 8px !important;
            border: 1px solid #CBD5E1 !important;
        }

        /* Password container with inline show/hide eye icon */
        .ts-password-container {
            position: relative;
            margin-bottom: 0.35rem;
        }
        .ts-password-container div[data-testid="stTextInput"] {
            margin-bottom: 0 !important;
        }
        .ts-password-container input {
            padding-right: 44px !important;
        }
        .ts-password-container div[data-testid="stCheckbox"] {
            position: absolute;
            right: 12px;
            top: 36px;
            margin: 0 !important;
            padding: 0 !important;
            height: 24px !important;
            width: 24px !important;
            z-index: 10;
            cursor: pointer;
        }
        .ts-password-container div[data-testid="stCheckbox"] label {
            margin: 0 !important;
            padding: 0 !important;
            cursor: pointer;
            display: flex !important;
            align-items: center;
            justify-content: center;
            width: 24px !important;
            height: 24px !important;
        }
        .ts-password-container div[data-testid="stCheckbox"] label div:first-child {
            opacity: 0 !important;
            position: absolute !important;
            width: 24px !important;
            height: 24px !important;
            margin: 0 !important;
            cursor: pointer !important;
        }
        .ts-password-container div[data-testid="stCheckbox"] label span {
            display: none !important;
        }
        .ts-password-container div[data-testid="stCheckbox"] label::after {
            content: 'visibility';
            font-family: 'Material Symbols Outlined' !important;
            font-size: 20px;
            line-height: 1;
            color: #94A3B8;
            transition: color 0.15s ease;
            cursor: pointer;
        }
        .ts-password-container div[data-testid="stCheckbox"]:hover label::after {
            color: #2563EB;
        }
        .ts-password-container.ts-pw-visible div[data-testid="stCheckbox"] label::after,
        .ts-password-container div[data-testid="stCheckbox"]:has(input:checked) label::after {
            content: 'visibility_off';
            color: #2563EB;
        }

        /* Remember Me & Forgot Password Row */
        .ts-remember-row {
            margin-top: 0.15rem;
            margin-bottom: 0.75rem;
        }
        .ts-remember-row div[data-testid="stCheckbox"] {
            margin: 0 !important;
        }
        .ts-remember-row div[data-testid="stCheckbox"] label span {
            font-family: 'Inter', sans-serif !important;
            font-size: 0.82rem !important;
            color: #475569 !important;
            font-weight: 500 !important;
        }
        .ts-forgot-wrap {
            display: flex !important;
            justify-content: flex-end !important;
            align-items: center !important;
            padding-top: 3px;
        }
        .ts-forgot-wrap div.stButton > button {
            background: transparent !important;
            border: none !important;
            color: #2563EB !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 0.82rem !important;
            font-weight: 600 !important;
            padding: 0 !important;
            margin: 0 !important;
            height: auto !important;
            min-height: auto !important;
            box-shadow: none !important;
            text-decoration: none !important;
            cursor: pointer !important;
        }
        .ts-forgot-wrap div.stButton > button:hover {
            color: #1D4ED8 !important;
            text-decoration: underline !important;
            background: transparent !important;
        }
        .ts-link {
            font-family: 'Inter', sans-serif;
            color: #2563EB;
            font-size: 0.82rem;
            font-weight: 600;
            text-decoration: none;
            transition: color 0.15s ease;
        }
        .ts-link:hover {
            color: #1D4ED8;
            text-decoration: underline;
        }

        /* Primary Sign In Button */
        .ts-auth-btn-primary div.stButton > button {
            background: #2563EB !important;
            color: #FFFFFF !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 0.92rem !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
            height: 44px !important;
            border: none !important;
            box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2) !important;
            transition: all 0.15s ease-in-out !important;
            margin-top: 0.25rem !important;
        }
        .ts-auth-btn-primary div.stButton > button:hover {
            background: #1D4ED8 !important;
            box-shadow: 0 4px 8px rgba(29, 78, 216, 0.25) !important;
            transform: translateY(-1px) !important;
        }

        /* Footer Inline Link ("New to TalentSphere? Create an account") */
        .ts-auth-footer {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.35rem;
            margin-top: 1.25rem;
            font-family: 'Inter', sans-serif;
            font-size: 0.85rem;
            color: #64748B;
        }
        .ts-auth-footer .stButton {
            display: inline-flex !important;
            width: auto !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        .ts-auth-footer .stButton > button {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            color: #2563EB !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            padding: 0 !important;
            margin: 0 !important;
            height: auto !important;
            min-height: auto !important;
            text-decoration: none !important;
            cursor: pointer !important;
            line-height: inherit !important;
        }
        .ts-auth-footer .stButton > button:hover {
            color: #1D4ED8 !important;
            text-decoration: underline !important;
            background: transparent !important;
        }

        /* Rule item badges for registration password */
        .ts-rule-item {
            display: flex;
            align-items: center;
            gap: 0.45rem;
            font-size: 0.78rem;
            font-weight: 500;
        }
        .ts-rule-passed {
            color: #059669;
            font-weight: 600;
        }
        .ts-rule-pending {
            color: #94A3B8;
        }

        /* Bottom page footnote */
        .ts-page-footer {
            text-align: center;
            font-family: 'Inter', sans-serif;
            font-size: 0.75rem;
            color: #94A3B8;
            margin-top: 1rem;
        }

        /* Responsive Design: Tablet (<= 960px) & Mobile (<= 768px) */
        @media (max-width: 960px) {
            div[data-testid="stHorizontalBlock"]:has(.ts-left-panel) {
                max-width: 95% !important;
            }
            div[data-testid="stHorizontalBlock"]:has(.ts-left-panel) > div[data-testid="stColumn"]:first-child {
                padding: 2rem 1.5rem !important;
            }
            div[data-testid="stHorizontalBlock"]:has(.ts-left-panel) > div[data-testid="stColumn"]:last-child {
                padding: 2rem 1.75rem !important;
            }
        }

        @media (max-width: 768px) {
            div[data-testid="stHorizontalBlock"]:has(.ts-left-panel) {
                display: flex !important;
                flex-direction: column !important;
                max-width: 100% !important;
                border-radius: 14px !important;
                min-height: auto !important;
            }
            /* Prioritize Login Form on Mobile */
            div[data-testid="stHorizontalBlock"]:has(.ts-left-panel) > div[data-testid="stColumn"]:last-child {
                order: 1 !important;
                width: 100% !important;
                min-width: 100% !important;
                border-radius: 14px 14px 0 0 !important;
                padding: 1.75rem 1.25rem !important;
            }
            /* Stack Career Info underneath on Mobile */
            div[data-testid="stHorizontalBlock"]:has(.ts-left-panel) > div[data-testid="stColumn"]:first-child {
                order: 2 !important;
                width: 100% !important;
                min-width: 100% !important;
                border-radius: 0 0 14px 14px !important;
                padding: 1.5rem 1.25rem !important;
                border-top: 1px solid #1E293B !important;
            }
            /* Hide decorative illustration on mobile to keep page compact */
            .ts-left-illustration-box {
                display: none !important;
            }
            .ts-left-title {
                font-size: 1.3rem !important;
            }
            .ts-auth-title {
                font-size: 1.35rem !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # 5. Header and Branding Bar
    brand_logo_html = ""
    if logo_uri:
        brand_logo_html = f'<img src="{logo_uri}" alt="TalentSphere Logo" class="ts-brand-logo-img" />'
    else:
        brand_logo_html = (
            '<div class="ts-brand-logo-icon">'
            '<span class="material-symbols-outlined" style="font-size: 20px;">trending_up</span>'
            '</div>'
        )

    st.markdown(
        f"""
        <div class="ts-top-brand-bar">
            <div class="ts-brand-logo-wrap">
                {brand_logo_html}
                <div class="ts-brand-text-wrap">
                    <div class="ts-brand-logo-text">TalentSphere</div>
                    <div class="ts-brand-logo-sub">Career Growth &amp; Development</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 6. Centered Dual-Panel Layout (Balanced 50/50 Split)
    col_hero, col_auth = st.columns([1, 1], gap="small")

    # =========================================================================
    # LEFT PANEL: Dark Navy (#111B30) Career Introduction
    # =========================================================================
    with col_hero:
        illustration_html = ""
        if career_img_uri:
            illustration_html = (
                f'<div class="ts-left-illustration-box">'
                f'<img src="{career_img_uri}" alt="Career growth overview" class="ts-left-illustration" />'
                f'</div>'
            )

        st.markdown(
            f"""
            <div class="ts-left-panel">
                <div class="ts-left-badge">
                    <span class="ts-left-badge-dot"></span>
                    Career Growth Platform
                </div>
                <h1 class="ts-left-title">
                    Build your career with confidence.
                </h1>
                <p class="ts-left-desc">
                    Track your skills, identify gaps, and plan your career growth with structured development paths.
                </p>
                {illustration_html}
                <div class="ts-left-benefits">
                    <div class="ts-benefit-item">
                        <div class="ts-benefit-icon">
                            <span class="material-symbols-outlined">check</span>
                        </div>
                        <span>Track your skills and strengths.</span>
                    </div>
                    <div class="ts-benefit-item">
                        <div class="ts-benefit-icon">
                            <span class="material-symbols-outlined">check</span>
                        </div>
                        <span>Identify skills required for your target role.</span>
                    </div>
                    <div class="ts-benefit-item">
                        <div class="ts-benefit-icon">
                            <span class="material-symbols-outlined">check</span>
                        </div>
                        <span>Set clear career development goals.</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # =========================================================================
    # RIGHT PANEL: Crisp White (#FFFFFF) Simplified Auth Form
    # =========================================================================
    with col_auth:
        st.markdown('<div class="ts-right-panel">', unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # 1. SIGN IN FORM
        # ---------------------------------------------------------------------
        if current_tab == "signin":
            st.markdown(
                """
                <div class="ts-auth-header">
                    <div class="ts-auth-title">Welcome back</div>
                    <div class="ts-auth-subtitle">Sign in to continue your career journey.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # 1. Email address input
            email = st.text_input(
                "Email address",
                value="",
                placeholder="Enter your email address",
                key="login_email_input",
            )

            # 2 & 3. Password input with inline show/hide eye toggle
            show_password = st.session_state.get("chk_show_pw_signin", False)
            pw_container_class = "ts-password-container ts-pw-visible" if show_password else "ts-password-container"

            st.markdown(f'<div class="{pw_container_class}">', unsafe_allow_html=True)
            password = st.text_input(
                "Password",
                value="",
                placeholder="Enter your password",
                type="default" if show_password else "password",
                key="login_password_input",
            )
            st.checkbox("Show password", key="chk_show_pw_signin")
            st.markdown('</div>', unsafe_allow_html=True)

            # 4. Remember Me and Forgot Password row
            st.markdown('<div class="ts-remember-row">', unsafe_allow_html=True)
            col_rem, col_forgot = st.columns([1.1, 0.9])
            with col_rem:
                st.checkbox("Remember me", value=True, key="login_remember_chk")
            with col_forgot:
                st.markdown('<div class="ts-forgot-wrap">', unsafe_allow_html=True)
                if st.button("Forgot password?", key="btn_forgot_password_link", type="tertiary"):
                    st.session_state["auth_tab"] = "forgot"
                    st.session_state["current_page"] = "Login"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # 5. Prominent Blue Sign In Button
            st.markdown('<div class="ts-auth-btn-primary">', unsafe_allow_html=True)
            btn_login = st.button("Sign In →", key="btn_login_submit", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Form submission handling with inline validation & loading state
            if btn_login:
                if not email.strip() or not password.strip():
                    st.error("Please enter both your email address and password.")
                elif "@" not in email or "." not in email:
                    st.error("Please enter a valid email address (e.g., name@company.com).")
                else:
                    with st.spinner("Signing in..."):
                        user = services.core.login(email.strip(), password)
                        if user:
                            st.session_state["is_authenticated"] = True
                            st.session_state["current_page"] = "Dashboard"
                            st.session_state["user_id"] = user["id"]

                            # Persistent session handling ("Remember me")
                            remember_me = st.session_state.get("login_remember_chk", False)
                            if remember_me:
                                signed_token = services.core.create_persistent_session(user["id"])
                                st.session_state["remember_token"] = signed_token
                                if cookie_controller:
                                    try:
                                        max_age_sec = services.core.SESSION_LIFETIME_DAYS * 86400
                                        cookie_controller.set(
                                            services.core.SESSION_COOKIE_NAME,
                                            signed_token,
                                            max_age=max_age_sec,
                                            same_site="lax",
                                        )
                                    except Exception as exc:
                                        services.core.logger.warning("Could not set cookie: %s", exc)
                            else:
                                st.session_state.pop("remember_token", None)
                                if cookie_controller:
                                    try:
                                        cookie_controller.remove(services.core.SESSION_COOKIE_NAME)
                                    except Exception:
                                        pass

                            # Populate employee session data
                            profile = services.core.get_profile(user["id"])
                            if "employee" not in st.session_state:
                                st.session_state["employee"] = {}

                            st.session_state["employee"]["id"] = user["id"]
                            st.session_state["employee"]["name"] = user["name"]
                            st.session_state["employee"]["email"] = user["email"]

                            if profile.get("job_title"):
                                st.session_state["employee"]["job_title"] = profile["job_title"]
                            if profile.get("department"):
                                st.session_state["employee"]["department"] = profile["department"]
                            if profile.get("target_role") and "career_target" in st.session_state:
                                st.session_state["career_target"]["role_title"] = profile["target_role"]

                            name_parts = user["name"].split()
                            initials = "".join([p[0].upper() for p in name_parts[:2]]) if name_parts else "EV"
                            st.session_state["employee"]["avatar_initials"] = initials

                            st.success(f"Welcome back, {user['name']}!")
                            st.rerun()
                        else:
                            st.error("Invalid email address or password. Please verify your credentials.")

            # 6. Simple footer link: "New to TalentSphere? Create an account"
            st.markdown(
                '<div class="ts-auth-footer"><span>New to TalentSphere?</span>',
                unsafe_allow_html=True,
            )
            if st.button("Create an account", key="link_to_register", type="secondary"):
                st.session_state["auth_tab"] = "register"
                st.session_state["current_page"] = "Registration"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # 2. CREATE ACCOUNT FORM
        # ---------------------------------------------------------------------
        elif current_tab == "register":
            st.markdown(
                """
                <div class="ts-auth-header">
                    <div class="ts-auth-title">Create your account</div>
                    <div class="ts-auth-subtitle">Start tracking your career goals, benchmarks, and professional growth.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            reg_name = st.text_input(
                "Full name",
                placeholder="Enter your full name",
                key="reg_name_input",
            )

            reg_email = st.text_input(
                "Work email address",
                placeholder="name@company.com",
                key="reg_email_input",
            )

            target_role_options = [
                "Select a target role",
                "Lead Systems Architect",
                "Senior Software Engineer",
                "Technical Lead",
                "Engineering Manager",
                "Data Analyst",
                "Senior Data Analyst",
                "Business Analyst",
                "Senior Business Analyst",
                "HR Manager",
                "Project Manager",
                "SAP Consultant",
            ]
            reg_track = st.selectbox(
                "Target role or track",
                options=target_role_options,
                key="reg_track_select",
            )

            show_reg_password = st.session_state.get("chk_show_pw_reg", False)
            reg_pw_container_class = "ts-password-container ts-pw-visible" if show_reg_password else "ts-password-container"

            st.markdown(f'<div class="{reg_pw_container_class}">', unsafe_allow_html=True)
            reg_password = st.text_input(
                "Password",
                type="default" if show_reg_password else "password",
                placeholder="At least 8 characters",
                key="reg_password_input",
            )
            st.checkbox("Show password", key="chk_show_pw_reg")
            st.markdown('</div>', unsafe_allow_html=True)

            reg_confirm_password = st.text_input(
                "Confirm password",
                type="default" if show_reg_password else "password",
                placeholder="Re-enter your password",
                key="reg_confirm_password_input",
            )

            # Live password requirements checklist
            has_length = len(reg_password) >= 8
            has_mix = any(c.isalpha() for c in reg_password) and any(c.isdigit() for c in reg_password)

            len_class = "ts-rule-passed" if has_length else "ts-rule-pending"
            len_icon = "check_circle" if has_length else "circle"
            mix_class = "ts-rule-passed" if has_mix else "ts-rule-pending"
            mix_icon = "check_circle" if has_mix else "circle"

            st.markdown(
                f"""
                <div style="margin: 0.2rem 0 0.5rem 0; display: flex; flex-direction: column; gap: 0.25rem;">
                    <div class="ts-rule-item {len_class}">
                        <span class="material-symbols-outlined" style="font-size: 14px;">{len_icon}</span>
                        <span>Minimum 8 characters</span>
                    </div>
                    <div class="ts-rule-item {mix_class}">
                        <span class="material-symbols-outlined" style="font-size: 14px;">{mix_icon}</span>
                        <span>Includes a letter and a number</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            terms_agreed = st.checkbox(
                "I agree to the Terms of Service and Privacy Policy.",
                value=True,
                key="reg_terms_chk",
            )

            # Primary Register Button
            st.markdown('<div class="ts-auth-btn-primary">', unsafe_allow_html=True)
            btn_register = st.button("Create Account →", key="btn_register_submit", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Registration validation & backend persistence
            if btn_register:
                if not reg_name.strip():
                    st.error("Please enter your full name.")
                elif not reg_email.strip() or "@" not in reg_email or "." not in reg_email:
                    st.error("Please enter a valid work email address.")
                elif not reg_track or reg_track == "Select a target role":
                    st.error("Please choose a target role or career track.")
                elif len(reg_password) < 8:
                    st.error("Your password must contain at least 8 characters.")
                elif not (any(c.isalpha() for c in reg_password) and any(c.isdigit() for c in reg_password)):
                    st.error("Your password must include both letters and numbers.")
                elif reg_password != reg_confirm_password:
                    st.error("Passwords do not match. Please re-enter them.")
                elif not terms_agreed:
                    st.error("Please accept the Terms of Service and Privacy Policy to proceed.")
                else:
                    with st.spinner("Creating account..."):
                        ok, msg = services.core.register(reg_name.strip(), reg_email.strip(), reg_password)
                        if ok:
                            new_user = services.core.login(reg_email.strip(), reg_password)
                            if new_user:
                                services.core.save_profile(new_user["id"], {
                                    "target_role": reg_track,
                                    "job_title": reg_track,
                                })

                                st.session_state["is_authenticated"] = True
                                st.session_state["current_page"] = "Dashboard"
                                st.session_state["user_id"] = new_user["id"]

                                name_parts = reg_name.strip().split()
                                initials = "".join([p[0].upper() for p in name_parts[:2]]) if name_parts else "EM"

                                if "employee" not in st.session_state:
                                    st.session_state["employee"] = {}

                                st.session_state["employee"]["id"] = new_user["id"]
                                st.session_state["employee"]["name"] = reg_name.strip()
                                st.session_state["employee"]["email"] = reg_email.strip()
                                st.session_state["employee"]["job_title"] = reg_track
                                st.session_state["employee"]["avatar_initials"] = initials

                                if "career_target" in st.session_state:
                                    st.session_state["career_target"]["role_title"] = reg_track

                                st.success(f"Account created successfully for {reg_name.strip()}! Directing to your dashboard...")
                                st.rerun()
                            else:
                                st.success(msg)
                                st.session_state["auth_tab"] = "signin"
                                st.rerun()
                        else:
                            st.error(msg)

            # Footer link back to Sign In
            st.markdown(
                '<div class="ts-auth-footer"><span>Already have an account?</span>',
                unsafe_allow_html=True,
            )
            if st.button("Sign in", key="link_to_signin", type="secondary"):
                st.session_state["auth_tab"] = "signin"
                st.session_state["current_page"] = "Login"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # 3. FORGOT PASSWORD REQUEST FORM
        # ---------------------------------------------------------------------
        elif current_tab == "forgot":
            st.markdown(
                """
                <div class="ts-auth-header">
                    <div class="ts-auth-title">Reset your password</div>
                    <div class="ts-auth-subtitle">Enter your registered email address and we'll send you instructions to reset your password.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            forgot_email = st.text_input(
                "Work email address",
                placeholder="name@company.com",
                key="forgot_email_input",
            )

            st.markdown('<div class="ts-auth-btn-primary" style="margin-top: 0.75rem;">', unsafe_allow_html=True)
            btn_forgot = st.button("Send Reset Link →", key="btn_forgot_submit", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            if btn_forgot:
                if not forgot_email.strip():
                    st.error("Please enter your work email address.")
                elif "@" not in forgot_email or "." not in forgot_email:
                    st.error("Please enter a valid email address.")
                else:
                    with st.spinner("Processing request..."):
                        ok, msg = services.core.request_password_reset(forgot_email.strip())
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)

            st.markdown(
                '<div class="ts-auth-footer"><span>Remembered your password?</span>',
                unsafe_allow_html=True,
            )
            if st.button("Back to sign in", key="link_forgot_to_signin", type="secondary"):
                st.session_state["auth_tab"] = "signin"
                st.session_state["current_page"] = "Login"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # 4. RESET PASSWORD EXECUTION FORM
        # ---------------------------------------------------------------------
        elif current_tab == "reset":
            reset_token = st.session_state.get("reset_token") or st.query_params.get("reset_token", "")
            token_info = services.core.validate_reset_token(reset_token)

            if not token_info:
                st.markdown(
                    """
                    <div class="ts-auth-header">
                        <div class="ts-auth-title" style="color: #DC2626;">Invalid or Expired Link</div>
                        <div class="ts-auth-subtitle">This password reset link is invalid, has expired, or has already been used. Please request a new one.</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("Request New Reset Link", key="btn_req_new_link", use_container_width=True):
                    st.session_state["auth_tab"] = "forgot"
                    st.session_state.pop("reset_token", None)
                    if "reset_token" in st.query_params:
                        del st.query_params["reset_token"]
                    st.rerun()

                st.markdown(
                    '<div class="ts-auth-footer"><span>Back to</span>',
                    unsafe_allow_html=True,
                )
                if st.button("Sign in", key="link_invalid_reset_to_signin", type="secondary"):
                    st.session_state["auth_tab"] = "signin"
                    st.session_state.pop("reset_token", None)
                    if "reset_token" in st.query_params:
                        del st.query_params["reset_token"]
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown(
                    f"""
                    <div class="ts-auth-header">
                        <div class="ts-auth-title">Set new password</div>
                        <div class="ts-auth-subtitle">Create a new, secure password for <b>{token_info['email']}</b>.</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                show_reset_pw = st.session_state.get("chk_show_pw_reset", False)
                pw_class = "ts-password-container ts-pw-visible" if show_reset_pw else "ts-password-container"

                st.markdown(f'<div class="{pw_class}">', unsafe_allow_html=True)
                new_pw = st.text_input(
                    "New password",
                    type="default" if show_reset_pw else "password",
                    placeholder="At least 8 characters",
                    key="reset_new_password_input",
                )
                st.checkbox("Show password", key="chk_show_pw_reset")
                st.markdown('</div>', unsafe_allow_html=True)

                confirm_pw = st.text_input(
                    "Confirm new password",
                    type="default" if show_reset_pw else "password",
                    placeholder="Re-enter your new password",
                    key="reset_confirm_password_input",
                )

                # Password requirement badges
                has_length = len(new_pw) >= 8
                has_mix = any(c.isalpha() for c in new_pw) and any(c.isdigit() for c in new_pw)
                len_class = "ts-rule-passed" if has_length else "ts-rule-pending"
                len_icon = "check_circle" if has_length else "circle"
                mix_class = "ts-rule-passed" if has_mix else "ts-rule-pending"
                mix_icon = "check_circle" if has_mix else "circle"

                st.markdown(
                    f"""
                    <div style="margin: 0.2rem 0 0.5rem 0; display: flex; flex-direction: column; gap: 0.25rem;">
                        <div class="ts-rule-item {len_class}">
                            <span class="material-symbols-outlined" style="font-size: 14px;">{len_icon}</span>
                            <span>Minimum 8 characters</span>
                        </div>
                        <div class="ts-rule-item {mix_class}">
                            <span class="material-symbols-outlined" style="font-size: 14px;">{mix_icon}</span>
                            <span>Includes a letter and a number</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown('<div class="ts-auth-btn-primary">', unsafe_allow_html=True)
                btn_reset = st.button("Update Password →", key="btn_reset_submit", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

                if btn_reset:
                    if len(new_pw) < 8:
                        st.error("Your password must contain at least 8 characters.")
                    elif not (any(c.isalpha() for c in new_pw) and any(c.isdigit() for c in new_pw)):
                        st.error("Your password must include both letters and numbers.")
                    elif new_pw != confirm_pw:
                        st.error("Passwords do not match. Please re-enter them.")
                    else:
                        with st.spinner("Updating password..."):
                            ok, msg = services.core.reset_password(reset_token, new_pw)
                            if ok:
                                st.success(msg)
                                st.session_state.pop("reset_token", None)
                                if "reset_token" in st.query_params:
                                    del st.query_params["reset_token"]
                                st.session_state["auth_tab"] = "signin"
                                st.session_state["current_page"] = "Login"
                                st.rerun()
                            else:
                                st.error(msg)

                st.markdown(
                    '<div class="ts-auth-footer"><span>Cancel and</span>',
                    unsafe_allow_html=True,
                )
                if st.button("Back to sign in", key="link_reset_to_signin", type="secondary"):
                    st.session_state["auth_tab"] = "signin"
                    st.session_state.pop("reset_token", None)
                    if "reset_token" in st.query_params:
                        del st.query_params["reset_token"]
                    st.session_state["current_page"] = "Login"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        # Fallback if unknown tab
        else:
            st.session_state["auth_tab"] = "signin"
            st.rerun()

    # 7. Footnote
    st.markdown(
        """
        <div class="ts-page-footer">
            TalentSphere Enterprise Career Platform © 2026
        </div>
        """,
        unsafe_allow_html=True,
    )
