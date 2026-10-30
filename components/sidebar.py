"""Sidebar navigation component for TalentSphere.

Inspired by Dashdark X modern SaaS sidebar architecture, adapted strictly
to the TalentSphere dark theme and design tokens:
- Deep navy background (#0D111D / #0B0E17).
- Top branding with logo, TALENTSPHERE title, ELEVATE PLATFORM subtitle.
- Interactive collapse/expand toggle control (Expanded vs Collapsed modes).
- Functional compact search bar to locate and filter available navigation pages.
- Main navigation with clean, consistent icons, uniform alignment, rounded active items,
  subtle cyan-tinted background, and slim cyan-pink gradient active indicator.
- User account section at the bottom with avatar, name, designation, account settings popover,
  and neatly arranged Reset Data and Sign Out controls.
- All HTML rendered via render_html (st.html) with zero indentation.
"""

from __future__ import annotations
import os
from typing import Any
import streamlit as st
from data.sample_data import get_initial_sample_data
from components.cards import render_html


# Keyword dictionary for smart search filtering
PAGE_KEYWORDS: dict[str, list[str]] = {
    "Dashboard": ["dashboard", "overview", "home", "analytics", "stats", "kpi", "summary"],
    "Employee Profile": ["profile", "employee", "work", "tasks", "process", "goals", "challenges", "progress", "details"],
    "Skills & Goals": ["skills", "goals", "competencies", "ratings", "assessments", "quiz", "targets", "upskilling"],
    "Resume Builder": ["resume", "builder", "cv", "pdf", "export", "draft", "education", "experience", "certifications"],
    "Career Development": ["career", "development", "trajectory", "benchmarks", "pathway", "milestones", "gap", "growth"],
}


def render_sidebar(cookie_controller: Any = None) -> str:
    """Renders the Dashdark X inspired dark-mode sidebar and returns the active page name."""
    with st.sidebar:
        # Check collapse state (default: expanded)
        is_collapsed = st.session_state.get("sidebar_collapsed", False)

        # Inject mode-specific CSS dynamically for smooth width transitions and compact layout
        if is_collapsed:
            render_html("""<style>
            section[data-testid="stSidebar"] {
                min-width: 86px !important;
                max-width: 86px !important;
                width: 86px !important;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }
            section[data-testid="stSidebar"] .block-container {
                padding-left: 0.45rem !important;
                padding-right: 0.45rem !important;
                padding-top: 0.85rem !important;
            }
            section[data-testid="stSidebar"] div[role="radiogroup"] > label {
                padding: 0.72rem 0.2rem !important;
                justify-content: center !important;
                text-align: center !important;
            }
            section[data-testid="stSidebar"] div[role="radiogroup"] > label p,
            section[data-testid="stSidebar"] div[role="radiogroup"] > label span:nth-child(2) {
                display: none !important;
            }
            </style>""")
        else:
            render_html("""<style>
            section[data-testid="stSidebar"] {
                min-width: 285px !important;
                max-width: 320px !important;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }
            </style>""")

        # ---------------------------------------------------------------------
        # 1. Branding Header & Collapse / Expand Control (Top)
        # ---------------------------------------------------------------------
        logo_path = os.path.join("assets", "logo.png")
        if os.path.exists(logo_path):
            try:
                import base64
                with open(logo_path, "rb") as f:
                    logo_b64 = base64.b64encode(f.read()).decode()
                logo_img_tag = f'<img src="data:image/png;base64,{logo_b64}" style="width: 38px; height: 38px; object-fit: contain; flex-shrink: 0; filter: drop-shadow(0 0 8px rgba(0, 210, 255, 0.35));" alt="TalentSphere Logo" />'
            except Exception:
                logo_img_tag = '<div style="font-size: 1.6rem; flex-shrink: 0;">💎</div>'
        else:
            logo_img_tag = '<div style="font-size: 1.6rem; flex-shrink: 0;">💎</div>'

        if is_collapsed:
            # Collapsed header: compact centered logo and expand button
            render_html(f"""<div class="ts-sidebar-brand" style="display: flex; flex-direction: column; align-items: center; justify-content: center; margin: 0 0 0.5rem 0; padding: 0.1rem 0;">
{logo_img_tag}
<div style="display: none;">TalentSphere ELEVATE PLATFORM</div>
</div>""")
            if st.button("▶", key="btn_sidebar_expand", help="Expand sidebar (Full view)", use_container_width=True):
                st.session_state["sidebar_collapsed"] = False
                st.rerun()
        else:
            # Expanded header: Brand on left, collapse button on right
            col_brand, col_toggle = st.columns([0.82, 0.18])
            with col_brand:
                render_html(f"""<div class="ts-sidebar-brand" style="display: flex; align-items: center; justify-content: flex-start; gap: 0.65rem; margin: 0; padding: 0.1rem 0 0 0; text-align: left;">
{logo_img_tag}
<div style="line-height: 1.15; text-align: left;">
<div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.25rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.02em;">TalentSphere</div>
<div style="font-size: 0.68rem; color: #00D2FF; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 2px;">ELEVATE PLATFORM</div>
</div>
</div>""")
            with col_toggle:
                if st.button("◀", key="btn_sidebar_collapse", help="Collapse sidebar (Compact view)", use_container_width=True):
                    st.session_state["sidebar_collapsed"] = True
                    st.rerun()

        # ---------------------------------------------------------------------
        # 2. Search Bar (Locates & filters available navigation pages)
        # ---------------------------------------------------------------------
        pages = [
            "Dashboard",
            "Employee Profile",
            "Skills & Goals",
            "Resume Builder",
            "Career Development",
        ]

        current_page = st.session_state.get("current_page", "Dashboard")
        if current_page == "My Profile":
            current_page = "Employee Profile"
            st.session_state["current_page"] = "Employee Profile"

        if current_page not in pages:
            current_page = "Dashboard"

        page_icons = {
            "Dashboard": "📊 Dashboard",
            "Employee Profile": "👤 Employee Profile",
            "Skills & Goals": "🎯 Skills & Goals",
            "Resume Builder": "📝 Resume Builder",
            "Career Development": "🚀 Career Development",
        }

        display_to_page = {v: k for k, v in page_icons.items()}
        display_to_page["👤 My Profile"] = "Employee Profile"
        display_to_page["📄 Resume Builder"] = "Resume Builder"
        display_to_page["Resume Builder"] = "Resume Builder"

        filtered_pages = pages
        if not is_collapsed:
            render_html('<div style="height: 6px;"></div>')

            def _clear_nav_search() -> None:
                st.session_state["sidebar_search_input"] = ""

            search_query = st.text_input(
                "Search navigation",
                placeholder="🔍 Search pages (e.g. Profile, Tasks)...",
                key="sidebar_search_input",
                label_visibility="collapsed",
                help="Type to search and filter navigation items",
            )

            clean_query = search_query.strip().lower()
            if clean_query:
                filtered_pages = [
                    p for p in pages
                    if clean_query in p.lower() or any(clean_query in kw for kw in PAGE_KEYWORDS.get(p, []))
                ]

                col_badge, col_clr = st.columns([0.72, 0.28])
                with col_badge:
                    cnt_label = f"{len(filtered_pages)} found" if filtered_pages else "No matches"
                    render_html(f"""<div style="font-size: 0.70rem; color: #00D2FF; font-weight: 700; padding: 0.15rem 0 0.35rem 0.2rem; text-transform: uppercase; letter-spacing: 0.05em;">{cnt_label}</div>""")
                with col_clr:
                    st.button("Clear", key="btn_clear_nav_search", on_click=_clear_nav_search, help="Reset search filter", use_container_width=True)

                if not filtered_pages:
                    render_html(f"""<div style="padding: 0.85rem 0.6rem; text-align: center; background: rgba(22, 26, 41, 0.6); border: 1px dashed rgba(255, 255, 255, 0.12); border-radius: 10px; margin: 0.4rem 0 0.8rem 0;">
<div style="font-size: 1.1rem; margin-bottom: 0.25rem;">🔍</div>
<div style="font-size: 0.80rem; color: #94A3B8;">No pages match "<b>{clean_query}</b>"</div>
</div>""")
                    # Fallback to show all pages so navigation remains accessible
                    filtered_pages = pages

        # ---------------------------------------------------------------------
        # 3. Main Navigation Menu
        # ---------------------------------------------------------------------
        if not is_collapsed:
            render_html("""<div style="font-size: 0.68rem; color: #64748B; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; margin: 0.65rem 0 0.4rem 0.35rem;">MAIN MENU</div>""")

        display_options = [page_icons[p] for p in filtered_pages]

        # Synchronize widget state safely
        expected_display = page_icons.get(current_page, "📊 Dashboard")
        if expected_display not in display_options and display_options:
            expected_display = display_options[0]

        last_synced = st.session_state.get("_sidebar_last_synced_page")
        if current_page != last_synced or "sidebar_navigation_radio" not in st.session_state:
            st.session_state["sidebar_navigation_radio"] = expected_display
            st.session_state["_sidebar_last_synced_page"] = current_page
        elif st.session_state.get("sidebar_navigation_radio") not in display_options and display_options:
            st.session_state["sidebar_navigation_radio"] = expected_display

        def _on_sidebar_nav_change() -> None:
            """Callback triggered whenever user selects a sidebar navigation item."""
            selected = st.session_state.get("sidebar_navigation_radio")
            if selected in display_to_page:
                target = display_to_page[selected]
                st.session_state["current_page"] = target
                st.session_state["_sidebar_last_synced_page"] = target

        selected_display = st.radio(
            "Navigation Menu",
            options=display_options,
            label_visibility="collapsed",
            key="sidebar_navigation_radio",
            on_change=_on_sidebar_nav_change,
        )

        # Fallback sync for headless testing environments
        if selected_display in display_to_page:
            target_page = display_to_page[selected_display]
            if current_page in pages and target_page != current_page:
                st.session_state["current_page"] = target_page
                st.session_state["_sidebar_last_synced_page"] = target_page
                st.rerun()

        # ---------------------------------------------------------------------
        # 4. User Account & Session Controls (Bottom Section)
        # ---------------------------------------------------------------------
        render_html("""<hr style="margin: 1.15rem 0 0.85rem 0; border: none; border-top: 1px solid rgba(255, 255, 255, 0.08);">""")

        employee = st.session_state.get("employee", {})
        is_logged_in = st.session_state.get("is_authenticated", True)

        if is_logged_in and employee:
            avatar_initials = employee.get("avatar_initials", "EV")
            emp_name = employee.get("name", "Employee")
            job_title = employee.get("job_title", "Professional Role")
            emp_id = employee.get("id", "EMP-9428")
            dept = employee.get("department", "Engineering")

            if is_collapsed:
                # Collapsed: Show centered avatar only
                render_html(f"""<div style="display: flex; justify-content: center; margin-bottom: 0.75rem;">
<div style="position: relative;">
<div style="width: 38px; height: 38px; border-radius: 50%; background: linear-gradient(135deg, #FF2A75 0%, #8A2BE2 100%); color: #FFFFFF; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.88rem; box-shadow: 0 0 12px rgba(255, 42, 117, 0.4); border: 2px solid rgba(255, 255, 255, 0.2);">
{avatar_initials}
</div>
<span style="position: absolute; bottom: 0; right: 0; width: 8px; height: 8px; background: #10B981; border: 2px solid #0D111D; border-radius: 50%;"></span>
</div>
</div>""")
            else:
                # Expanded: Dashdark X user card
                render_html(f"""<div class="ts-sidebar-user-card" style="background: #161A29; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 0.75rem 0.85rem; margin-bottom: 0.75rem; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.06); display: flex; align-items: center; gap: 0.7rem;">
<div style="position: relative; flex-shrink: 0;">
<div style="width: 38px; height: 38px; border-radius: 50%; background: linear-gradient(135deg, #FF2A75 0%, #8A2BE2 100%); color: #FFFFFF; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.88rem; box-shadow: 0 0 12px rgba(255, 42, 117, 0.4); border: 2px solid rgba(255, 255, 255, 0.2);">
{avatar_initials}
</div>
<span style="position: absolute; bottom: 0; right: 0; width: 8px; height: 8px; background: #10B981; border: 2px solid #161A29; border-radius: 50%;"></span>
</div>
<div style="overflow: hidden; text-align: left;">
<div style="font-size: 0.88rem; font-weight: 700; color: #FFFFFF; white-space: nowrap; text-overflow: ellipsis; overflow: hidden; line-height: 1.2;">{emp_name}</div>
<div style="font-size: 0.74rem; color: #00D2FF; font-weight: 600; white-space: nowrap; text-overflow: ellipsis; overflow: hidden; margin-top: 2px;">{job_title}</div>
</div>
</div>""")

                # Account Settings Access Popover
                with st.popover("⚙️ Account Settings", use_container_width=True):
                    render_html(f"""<div style="padding: 0.3rem 0; font-size: 0.85rem; color: #CBD5E1;">
<div style="font-weight: 700; color: #FFFFFF; font-size: 0.95rem; margin-bottom: 0.25rem;">{emp_name}</div>
<div style="color: #00D2FF; font-size: 0.76rem; font-weight: 600; margin-bottom: 0.5rem;">{job_title} · {dept}</div>
<div style="font-size: 0.78rem; color: #94A3B8; margin-bottom: 0.2rem;">ID: <span style="color: #FFFFFF;">{emp_id}</span></div>
<div style="font-size: 0.78rem; color: #94A3B8; margin-bottom: 0.5rem;">Status: <span style="color: #10B981; font-weight: 600;">● Active Session</span></div>
</div>""")
                    if st.button("View Employee Profile", key="btn_account_popover_profile", use_container_width=True):
                        st.session_state["current_page"] = "Employee Profile"
                        st.session_state["_sidebar_last_synced_page"] = "Employee Profile"
                        st.session_state["sidebar_navigation_radio"] = "👤 Employee Profile"
                        st.rerun()

        # Session Controls: Reset Data & Sign Out
        if is_collapsed:
            col_reset, col_out = st.columns(2)
            with col_reset:
                if st.button("🔄", key="btn_sidebar_reset", help="Restore fresh sample dataset", use_container_width=True):
                    fresh = get_initial_sample_data()
                    for k, v in fresh.items():
                        st.session_state[k] = v
                    st.toast("Sample data reset to default!", icon="🔄")
                    st.rerun()
            with col_out:
                if st.button("🚪", key="btn_sidebar_signout", help="Sign out of TalentSphere", use_container_width=True):
                    import services.core
                    token_to_revoke = st.session_state.get("remember_token")
                    if not token_to_revoke and hasattr(st, "context") and hasattr(st.context, "cookies"):
                        try:
                            token_to_revoke = st.context.cookies.get(services.core.SESSION_COOKIE_NAME)
                        except Exception:
                            pass
                    if not token_to_revoke and cookie_controller:
                        try:
                            token_to_revoke = cookie_controller.get(services.core.SESSION_COOKIE_NAME)
                        except Exception:
                            pass
                    if token_to_revoke:
                        services.core.revoke_session(token_to_revoke)

                    if cookie_controller:
                        try:
                            cookie_controller.remove(services.core.SESSION_COOKIE_NAME)
                        except Exception:
                            pass

                    st.session_state["is_authenticated"] = False
                    st.session_state["user_id"] = None
                    st.session_state.pop("remember_token", None)
                    st.session_state.pop("_sidebar_last_synced_page", None)
                    st.session_state.pop("sidebar_navigation_radio", None)
                    st.session_state.pop("sidebar_search_input", None)
                    st.session_state["current_page"] = "Login"
                    st.session_state["auth_tab"] = "signin"
                    st.rerun()
        else:
            col_reset, col_out = st.columns(2)
            with col_reset:
                if st.button("Reset Data", key="btn_sidebar_reset", help="Restore fresh sample dataset", use_container_width=True):
                    fresh = get_initial_sample_data()
                    for k, v in fresh.items():
                        st.session_state[k] = v
                    st.toast("Sample data reset to default!", icon="🔄")
                    st.rerun()
            with col_out:
                if st.button("Sign Out", key="btn_sidebar_signout", help="Sign out of TalentSphere", use_container_width=True):
                    import services.core
                    token_to_revoke = st.session_state.get("remember_token")
                    if not token_to_revoke and hasattr(st, "context") and hasattr(st.context, "cookies"):
                        try:
                            token_to_revoke = st.context.cookies.get(services.core.SESSION_COOKIE_NAME)
                        except Exception:
                            pass
                    if not token_to_revoke and cookie_controller:
                        try:
                            token_to_revoke = cookie_controller.get(services.core.SESSION_COOKIE_NAME)
                        except Exception:
                            pass
                    if token_to_revoke:
                        services.core.revoke_session(token_to_revoke)

                    if cookie_controller:
                        try:
                            cookie_controller.remove(services.core.SESSION_COOKIE_NAME)
                        except Exception:
                            pass

                    st.session_state["is_authenticated"] = False
                    st.session_state["user_id"] = None
                    st.session_state.pop("remember_token", None)
                    st.session_state.pop("_sidebar_last_synced_page", None)
                    st.session_state.pop("sidebar_navigation_radio", None)
                    st.session_state.pop("sidebar_search_input", None)
                    st.session_state["current_page"] = "Login"
                    st.session_state["auth_tab"] = "signin"
                    st.rerun()

        # Footer Version Tag
        if not is_collapsed:
            render_html("""<div style="font-size: 0.70rem; color: #64748B; text-align: center; margin-top: 1.25rem; line-height: 1.4; letter-spacing: 0.02em;">
TalentSphere Platform · Elevate v2.0<br>
<span style="color: #00D2FF; font-weight: 600;">Workforce Intelligence & Growth</span>
</div>""")

    return st.session_state.get("current_page", "Dashboard")
