"""TalentSphere — Employee Career Growth & Skill Management Platform.

Frontend Prototype & UI/UX Demonstration.
Built with Python, Streamlit, and modern SaaS styling.
"""

from __future__ import annotations
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="TalentSphere — Career Growth & Skills Platform",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Design System & Custom CSS
from components.styles import get_custom_css
st.markdown(get_custom_css(), unsafe_allow_html=True)

# 3. Database & Session State Initialization
import services.core
from services.core import init_db
from data.sample_data import get_initial_sample_data
from streamlit_cookies_controller import CookieController

# Ensure SQLite schema and demo account initialization
init_db()


class CookieManager:
    """Safe wrapper around CookieController ensuring no NoneType errors in headless or test modes."""
    def __init__(self, key: str = "cookies"):
        self.key = key
        try:
            self._ctrl = CookieController(key=key)
            raw = getattr(self._ctrl, f"_{CookieController.__name__}__cookies", None)
            if raw is None:
                setattr(self._ctrl, f"_{CookieController.__name__}__cookies", {})
                st.session_state[key] = {}
        except Exception:
            self._ctrl = None

    def get(self, name: str) -> Any:
        if self._ctrl:
            try:
                raw = getattr(self._ctrl, f"_{self._ctrl.__class__.__name__}__cookies", None)
                if raw is None:
                    setattr(self._ctrl, f"_{self._ctrl.__class__.__name__}__cookies", {})
                    st.session_state[self.key] = {}
                val = self._ctrl.get(name)
                if val is not None:
                    return val
            except Exception:
                pass
        return st.session_state.get(f"_cookie_{name}")

    def set(self, name: str, value: Any, **kwargs) -> None:
        st.session_state[f"_cookie_{name}"] = value
        if self._ctrl:
            try:
                raw = getattr(self._ctrl, f"_{self._ctrl.__class__.__name__}__cookies", None)
                if raw is None:
                    setattr(self._ctrl, f"_{self._ctrl.__class__.__name__}__cookies", {})
                    st.session_state[self.key] = {}
                self._ctrl.set(name, value, **kwargs)
            except Exception as e:
                services.core.logger.warning("Could not set browser cookie via controller: %s", e)

    def remove(self, name: str, **kwargs) -> None:
        st.session_state.pop(f"_cookie_{name}", None)
        if self._ctrl:
            try:
                raw = getattr(self._ctrl, f"_{self._ctrl.__class__.__name__}__cookies", None)
                if raw is None:
                    setattr(self._ctrl, f"_{self._ctrl.__class__.__name__}__cookies", {})
                    st.session_state[self.key] = {}
                self._ctrl.remove(name, **kwargs)
            except Exception:
                pass


cookie_controller = CookieManager()


def _get_cookie_token(ctrl: CookieManager) -> str | None:
    """Retrieves session cookie from request context headers, cookie controller, or session state."""
    if hasattr(st, "context") and hasattr(st.context, "cookies"):
        try:
            c = st.context.cookies.get(services.core.SESSION_COOKIE_NAME)
            if c and isinstance(c, str):
                return c
        except Exception:
            pass
    if ctrl:
        try:
            c = ctrl.get(services.core.SESSION_COOKIE_NAME)
            if c and isinstance(c, str):
                return c
        except Exception:
            pass
    tok = st.session_state.get("remember_token")
    if tok and isinstance(tok, str):
        return tok
    return None


# Check for reset_token query parameter in URL
query_reset_token = st.query_params.get("reset_token")
if query_reset_token:
    st.session_state["reset_token"] = query_reset_token
    if not st.session_state.get("is_authenticated", False):
        st.session_state["auth_tab"] = "reset"
        st.session_state["current_page"] = "Login"

if "is_authenticated" not in st.session_state:
    st.session_state["is_authenticated"] = False

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Login"

if "employee" not in st.session_state:
    sample_data = get_initial_sample_data()
    for key, val in sample_data.items():
        st.session_state[key] = val

# Persistent session restoration on application rerun / page reload
if not st.session_state.get("is_authenticated", False) and st.session_state.get("auth_tab") != "reset":
    cookie_token = _get_cookie_token(cookie_controller)
    if cookie_token:
        valid_user = services.core.validate_persistent_session(cookie_token)
        if valid_user:
            st.session_state["is_authenticated"] = True
            st.session_state["user_id"] = valid_user["id"]
            st.session_state["remember_token"] = valid_user["signed_token"]
            st.session_state["current_page"] = "Dashboard"

            # Hydrate employee session data from DB
            profile = services.core.get_profile(valid_user["id"])
            if "employee" not in st.session_state:
                st.session_state["employee"] = {}
            st.session_state["employee"]["id"] = valid_user["id"]
            st.session_state["employee"]["name"] = valid_user["name"]
            st.session_state["employee"]["email"] = valid_user["email"]
            if profile.get("job_title"):
                st.session_state["employee"]["job_title"] = profile["job_title"]
            if profile.get("department"):
                st.session_state["employee"]["department"] = profile["department"]
            if profile.get("target_role") and "career_target" in st.session_state:
                st.session_state["career_target"]["role_title"] = profile["target_role"]
            name_parts = valid_user["name"].split()
            initials = "".join([p[0].upper() for p in name_parts[:2]]) if name_parts else "EV"
            st.session_state["employee"]["avatar_initials"] = initials
        else:
            # Token invalid, expired, or revoked
            st.session_state.pop("remember_token", None)
            try:
                cookie_controller.remove(services.core.SESSION_COOKIE_NAME)
            except Exception:
                pass

# Revalidate authenticated state against SQLite (do not trust client state alone)
if st.session_state.get("is_authenticated", False):
    uid = st.session_state.get("user_id")
    if uid:
        user_check = services.core.get_user_by_id(uid)
        if not user_check:
            st.session_state["is_authenticated"] = False
            st.session_state["user_id"] = None
            st.session_state.pop("remember_token", None)
            try:
                cookie_controller.remove(services.core.SESSION_COOKIE_NAME)
            except Exception:
                pass
            st.session_state["current_page"] = "Login"
            st.session_state["auth_tab"] = "signin"

# 4. Conditional Layout: Unauthenticated vs Authenticated
is_auth = st.session_state.get("is_authenticated", False)

if not is_auth:
    # =========================================================================
    # STANDALONE AUTHENTICATION LAYOUT (No Sidebar, Full Viewport Width)
    # =========================================================================
    st.markdown(
        """
        <style>
        /* Standalone authentication layout: remove sidebar and expand to full width */
        [data-testid="stSidebar"],
        section[data-testid="stSidebar"],
        div[data-testid="collapsedControl"] {
            display: none !important;
            width: 0 !important;
            min-width: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        header[data-testid="stHeader"] {
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
            padding: 0 !important;
        }
        .main {
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            min-height: 100vh !important;
        }
        .main .block-container {
            max-width: 1020px !important;
            margin: auto !important;
            padding-top: 1.25rem !important;
            padding-bottom: 1.25rem !important;
            padding-left: 1.25rem !important;
            padding-right: 1.25rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Access control: force current_page to Login for unauthenticated users
    current_page = st.session_state.get("current_page", "Login")
    if current_page not in ("Login", "Registration"):
        st.session_state["current_page"] = "Login"
        current_page = "Login"

    from views.login_view import render_login_page
    current_auth_tab = st.session_state.get("auth_tab", "signin")
    if current_page == "Registration":
        initial_tab = "register"
    elif current_auth_tab in ("forgot", "reset", "register"):
        initial_tab = current_auth_tab
    else:
        initial_tab = "signin"

    render_login_page(initial_tab=initial_tab, cookie_controller=cookie_controller)

else:
    # =========================================================================
    # AUTHENTICATED APPLICATION LAYOUT (Full Sidebar Navigation & Dashboard)
    # =========================================================================
    from components.styles import get_dark_theme_css
    st.markdown(get_dark_theme_css(), unsafe_allow_html=True)

    from components.sidebar import render_sidebar
    active_page = render_sidebar(cookie_controller=cookie_controller)

    from views.dashboard_view import render_dashboard_page
    from views.profile_view import render_profile_page
    from views.resume_builder_view import render_resume_builder_page
    from views.skills_goals_view import render_skills_goals_page
    from views.career_development_view import render_career_development_page

    # Page Router with Graceful Fallback
    try:
        if active_page == "Dashboard":
            render_dashboard_page()
        elif active_page in ("Employee Profile", "My Profile"):
            render_profile_page()
        elif active_page == "Resume Builder":
            render_resume_builder_page()
        elif active_page == "Skills & Goals":
            render_skills_goals_page()
        elif active_page == "Career Development":
            render_career_development_page()
        else:
            render_dashboard_page()
    except Exception as e:
        st.error(f"Unable to load '{active_page}': {e}")
        render_dashboard_page()

