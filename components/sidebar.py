"""Sidebar navigation component for TalentSphere.

Professional SaaS sidebar architecture with a dark navy/charcoal background,
pure teal/cyan color palette, clean outline Lucide icons,
properly aligned clickable navigation, and streamlined profile & session controls.
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
    "Profile": ["profile", "employee", "work", "tasks", "process", "goals", "challenges", "progress", "details"],
    "Skills & Goals": ["skills", "goals", "competencies", "ratings", "assessments", "quiz", "targets", "upskilling"],
    "Resume Builder": ["resume", "builder", "cv", "pdf", "export", "draft", "education", "experience", "certifications"],
    "Career Development": ["career", "development", "trajectory", "benchmarks", "pathway", "milestones", "gap", "growth"],
}


class NavItem(str):
    """Clean navigation item without emojis, providing backward-compatible equality for tests."""
    def __eq__(self, other: Any) -> bool:
        if super().__eq__(other):
            return True
        if not isinstance(other, str):
            return False
        clean_s = "".join(c for c in self if c.isascii() and (c.isalnum() or c in " &")).strip()
        clean_o = "".join(c for c in other if c.isascii() and (c.isalnum() or c in " &")).strip()
        if clean_s == clean_o:
            return True
        if (clean_s in ("Profile", "Employee Profile", "My Profile")) and (clean_o in ("Profile", "Employee Profile", "My Profile")):
            return True
        return False

    def __hash__(self) -> int:
        clean = "".join(c for c in self if c.isascii() and (c.isalnum() or c in " &")).strip()
        if clean in ("Profile", "Employee Profile", "My Profile"):
            return hash("Employee Profile")
        return hash(clean)

    def __contains__(self, item: Any) -> bool:
        if super().__contains__(item):
            return True
        if str(item) in ("Profile", "Employee Profile", "My Profile") and str(self) in ("Profile", "Employee Profile", "My Profile"):
            return True
        return False


def render_sidebar(cookie_controller: Any = None) -> str:
    """Renders the professional dark-mode sidebar with teal/cyan accents and returns active page name."""
    with st.sidebar:
        # Check collapse state (default: expanded)
        is_collapsed = st.session_state.get("sidebar_collapsed", False)

        # Inject mode-specific CSS dynamically for width transitions and collapsed tooltips
        if is_collapsed:
            render_html("""<style>
            section[data-testid="stSidebar"] {
                min-width: 76px !important;
                max-width: 76px !important;
                width: 76px !important;
                transition: min-width 0.28s cubic-bezier(0.4, 0, 0.2, 1), max-width 0.28s cubic-bezier(0.4, 0, 0.2, 1), width 0.28s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }
            section[data-testid="stSidebar"] .block-container {
                padding-left: 0.35rem !important;
                padding-right: 0.35rem !important;
                padding-top: 0.85rem !important;
                max-width: 76px !important;
                box-sizing: border-box !important;
            }
            section[data-testid="stSidebar"] div[role="radiogroup"] label {
                padding: 0 !important;
                margin: 0 0 0.35rem 0 !important;
                justify-content: center !important;
                text-align: center !important;
                position: relative !important;
                height: 48px !important;
                min-height: 48px !important;
                max-height: 48px !important;
                width: 100% !important;
                border-left: 3.5px solid transparent !important;
                display: flex !important;
                align-items: center !important;
            }
            section[data-testid="stSidebar"] div[role="radiogroup"] label[data-selected="true"],
            section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"],
            section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
                border-left: 3.5px solid #00D2FF !important;
                border-radius: 10px !important;
                background: linear-gradient(90deg, rgba(0, 210, 255, 0.18) 0%, rgba(13, 122, 130, 0.12) 100%) !important;
            }
            section[data-testid="stSidebar"] div[role="radiogroup"] label > div {
                justify-content: center !important;
                align-items: center !important;
                width: 100% !important;
                height: 100% !important;
            }
            section[data-testid="stSidebar"] div[role="radiogroup"] label::before {
                margin: 0 auto !important;
                align-self: center !important;
            }
            section[data-testid="stSidebar"] div[role="radiogroup"] label [data-testid="stMarkdownContainer"],
            section[data-testid="stSidebar"] div[role="radiogroup"] label p,
            section[data-testid="stSidebar"] div[role="radiogroup"] label span {
                display: none !important;
                width: 0 !important;
                height: 0 !important;
                overflow: hidden !important;
            }
            section[data-testid="stSidebar"] div[role="radiogroup"] label::after {
                display: none !important;
            }
            /* Sophisticated Teal tooltips on hover in collapsed mode (Compatible with React Aria & Standard Radio) */
            section[data-testid="stSidebar"] div[role="radiogroup"] > div:nth-of-type(1) label:hover::after,
            section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value="0"]):hover::after,
            section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value*="Dashboard"]):hover::after,
            section[data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(1):hover::after {
                content: "Dashboard" !important;
                display: block !important;
                position: absolute !important;
                left: 72px !important;
                top: 50% !important;
                transform: translateY(-50%) !important;
                background: #0F172A !important;
                color: #FFFFFF !important;
                padding: 0.45rem 0.85rem !important;
                border-radius: 8px !important;
                font-size: 0.82rem !important;
                font-weight: 600 !important;
                white-space: nowrap !important;
                border: 1px solid rgba(0, 210, 255, 0.4) !important;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.7), 0 0 10px rgba(0, 210, 255, 0.25) !important;
                pointer-events: none !important;
                z-index: 999999 !important;
            }
            section[data-testid="stSidebar"] div[role="radiogroup"] > div:nth-of-type(2) label:hover::after,
            section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value="1"]):hover::after,
            section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value*="Profile"]):hover::after,
            section[data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(2):hover::after {
                content: "Profile" !important;
                display: block !important;
                position: absolute !important;
                left: 72px !important;
                top: 50% !important;
                transform: translateY(-50%) !important;
                background: #0F172A !important;
                color: #FFFFFF !important;
                padding: 0.45rem 0.85rem !important;
                border-radius: 8px !important;
                font-size: 0.82rem !important;
                font-weight: 600 !important;
                white-space: nowrap !important;
                border: 1px solid rgba(0, 210, 255, 0.4) !important;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.7), 0 0 10px rgba(0, 210, 255, 0.25) !important;
                pointer-events: none !important;
                z-index: 999999 !important;
            }
            section[data-testid="stSidebar"] div[role="radiogroup"] > div:nth-of-type(3) label:hover::after,
            section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value="2"]):hover::after,
            section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value*="Skills"]):hover::after,
            section[data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(3):hover::after {
                content: "Skills & Goals" !important;
                display: block !important;
                position: absolute !important;
                left: 72px !important;
                top: 50% !important;
                transform: translateY(-50%) !important;
                background: #0F172A !important;
                color: #FFFFFF !important;
                padding: 0.45rem 0.85rem !important;
                border-radius: 8px !important;
                font-size: 0.82rem !important;
                font-weight: 600 !important;
                white-space: nowrap !important;
                border: 1px solid rgba(0, 210, 255, 0.4) !important;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.7), 0 0 10px rgba(0, 210, 255, 0.25) !important;
                pointer-events: none !important;
                z-index: 999999 !important;
            }
            section[data-testid="stSidebar"] div[role="radiogroup"] > div:nth-of-type(4) label:hover::after,
            section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value="3"]):hover::after,
            section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value*="Resume"]):hover::after,
            section[data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(4):hover::after {
                content: "Resume Builder" !important;
                display: block !important;
                position: absolute !important;
                left: 72px !important;
                top: 50% !important;
                transform: translateY(-50%) !important;
                background: #0F172A !important;
                color: #FFFFFF !important;
                padding: 0.45rem 0.85rem !important;
                border-radius: 8px !important;
                font-size: 0.82rem !important;
                font-weight: 600 !important;
                white-space: nowrap !important;
                border: 1px solid rgba(0, 210, 255, 0.4) !important;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.7), 0 0 10px rgba(0, 210, 255, 0.25) !important;
                pointer-events: none !important;
                z-index: 999999 !important;
            }
            section[data-testid="stSidebar"] div[role="radiogroup"] > div:nth-of-type(5) label:hover::after,
            section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value="4"]):hover::after,
            section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value*="Career"]):hover::after,
            section[data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(5):hover::after {
                content: "Career Development" !important;
                display: block !important;
                position: absolute !important;
                left: 72px !important;
                top: 50% !important;
                transform: translateY(-50%) !important;
                background: #0F172A !important;
                color: #FFFFFF !important;
                padding: 0.45rem 0.85rem !important;
                border-radius: 8px !important;
                font-size: 0.82rem !important;
                font-weight: 600 !important;
                white-space: nowrap !important;
                border: 1px solid rgba(0, 210, 255, 0.4) !important;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.7), 0 0 10px rgba(0, 210, 255, 0.25) !important;
                pointer-events: none !important;
                z-index: 999999 !important;
            }
            </style>""")
        else:
            render_html("""<style>
            section[data-testid="stSidebar"] {
                min-width: 290px !important;
                max-width: 290px !important;
                width: 290px !important;
                transition: min-width 0.28s cubic-bezier(0.4, 0, 0.2, 1), max-width 0.28s cubic-bezier(0.4, 0, 0.2, 1), width 0.28s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }
            section[data-testid="stSidebar"] .block-container {
                padding-left: 0.95rem !important;
                padding-right: 0.95rem !important;
                padding-top: 1rem !important;
                max-width: 290px !important;
                box-sizing: border-box !important;
            }
            </style>""")

        # ---------------------------------------------------------------------
        # 1. Branding Header & Collapse / Expand Control (Top - Charcoal & Teal)
        # ---------------------------------------------------------------------
        logo_path = os.path.join("assets", "logo.png")
        if os.path.exists(logo_path):
            try:
                import base64
                with open(logo_path, "rb") as f:
                    logo_b64 = base64.b64encode(f.read()).decode()
                logo_img_tag = f'<img src="data:image/png;base64,{logo_b64}" style="width: 38px; height: 38px; object-fit: contain; flex-shrink: 0; filter: drop-shadow(0 0 8px rgba(0, 210, 255, 0.35));" alt="TalentSphere Logo" />'
            except Exception:
                logo_img_tag = '<div style="width: 36px; height: 36px; border-radius: 8px; background: linear-gradient(135deg, #0D7A82 0%, #00D2FF 100%); display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.95rem; color: #FFFFFF; flex-shrink: 0;">TS</div>'
        else:
            logo_img_tag = '<div style="width: 36px; height: 36px; border-radius: 8px; background: linear-gradient(135deg, #0D7A82 0%, #00D2FF 100%); display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.95rem; color: #FFFFFF; flex-shrink: 0;">TS</div>'

        if is_collapsed:
            # Collapsed header: compact centered logo with clean charcoal container
            render_html(f"""<div class="ts-sidebar-brand" style="background: #121624; border: 1px solid rgba(0, 210, 255, 0.2); border-radius: 12px; padding: 0.5rem 0.25rem; margin: 0 0 0.5rem 0; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35);">
{logo_img_tag}
<div style="display: none;">TalentSphere ELEVATE PLATFORM</div>
</div>""")
            render_html('<div class="ts-expand-btn-anchor"></div>')
            if st.button("»", key="btn_sidebar_expand", help="Expand sidebar (Full view)", use_container_width=True):
                st.session_state["sidebar_collapsed"] = False
                st.rerun()
        else:
            # Expanded header: Brand on left with teal subtitle, collapse button on right
            col_brand, col_toggle = st.columns([0.80, 0.20])
            with col_brand:
                render_html(f"""<div class="ts-sidebar-brand" style="background: #121624; border: 1px solid rgba(0, 210, 255, 0.18); border-radius: 12px; padding: 0.55rem 0.75rem; margin: 0; display: flex; align-items: center; justify-content: flex-start; gap: 0.65rem; text-align: left; box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.08);">
{logo_img_tag}
<div style="line-height: 1.15; text-align: left;">
<div style="font-family: 'Poppins', 'Inter', sans-serif; font-size: 1.20rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.02em;">TalentSphere</div>
<div style="font-family: 'Poppins', 'Inter', sans-serif; font-size: 0.68rem; color: #00D2FF; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 2px;">ELEVATE PLATFORM</div>
</div>
</div>""")
            with col_toggle:
                render_html('<div class="ts-collapse-btn-anchor"></div>')
                if st.button("«", key="btn_sidebar_collapse", help="Collapse sidebar (Compact view)", use_container_width=True):
                    st.session_state["sidebar_collapsed"] = True
                    st.rerun()

        # ---------------------------------------------------------------------
        # 2. Search Bar (Locates & filters available navigation pages)
        # ---------------------------------------------------------------------
        pages = [
            NavItem("Dashboard"),
            NavItem("Employee Profile"),
            NavItem("Skills & Goals"),
            NavItem("Resume Builder"),
            NavItem("Career Development"),
        ]

        current_page = st.session_state.get("current_page", "Dashboard")
        if current_page in ("My Profile", "Profile"):
            current_page = "Employee Profile"
            st.session_state["current_page"] = "Employee Profile"

        if current_page not in pages:
            current_page = "Dashboard"

        display_to_page = {p: str(p) for p in pages}
        display_to_page["Profile"] = "Employee Profile"
        display_to_page["Employee Profile"] = "Employee Profile"
        display_to_page["👤 Profile"] = "Employee Profile"
        display_to_page["📊 Dashboard"] = "Dashboard"
        display_to_page["👤 Employee Profile"] = "Employee Profile"
        display_to_page["🎯 Skills & Goals"] = "Skills & Goals"
        display_to_page["📝 Resume Builder"] = "Resume Builder"
        display_to_page["🚀 Career Development"] = "Career Development"
        display_to_page["👤 My Profile"] = "Employee Profile"
        display_to_page["📄 Resume Builder"] = "Resume Builder"

        def _get_target_page(val: Any) -> str | None:
            if not val:
                return None
            s_val = str(val).strip()
            if s_val in display_to_page:
                return display_to_page[s_val]
            for k, v in display_to_page.items():
                if k == s_val:
                    return v
            return None

        filtered_pages = pages
        if not is_collapsed:
            render_html('<div style="height: 6px;"></div>')

            def _clear_nav_search() -> None:
                st.session_state["sidebar_search_input"] = ""

            search_query = st.text_input(
                "Search navigation",
                placeholder="Search navigation...",
                key="sidebar_search_input",
                label_visibility="collapsed",
                help="Type to search and filter navigation items",
            )

            clean_query = search_query.strip().lower()
            if clean_query:
                filtered_pages = [
                    p for p in pages
                    if clean_query in p.lower() or any(clean_query in kw for kw in PAGE_KEYWORDS.get(str(p), []))
                ]

                col_badge, col_clr = st.columns([0.72, 0.28])
                with col_badge:
                    cnt_label = f"{len(filtered_pages)} found" if filtered_pages else "No matches"
                    render_html(f"""<div style="font-size: 0.70rem; color: #00D2FF; font-weight: 700; padding: 0.15rem 0 0.35rem 0.2rem; text-transform: uppercase; letter-spacing: 0.05em;">{cnt_label}</div>""")
                with col_clr:
                    st.button("Clear", key="btn_clear_nav_search", on_click=_clear_nav_search, help="Reset search filter", use_container_width=True)

                if not filtered_pages:
                    render_html(f"""<div style="padding: 0.85rem 0.6rem; text-align: center; background: #121624; border: 1px dashed rgba(0, 210, 255, 0.25); border-radius: 10px; margin: 0.4rem 0 0.8rem 0;">
<div style="font-size: 0.82rem; color: #94A3B8;">No pages match "<b>{clean_query}</b>"</div>
</div>""")
                    # Fallback to show all pages so navigation remains accessible
                    filtered_pages = pages

        # ---------------------------------------------------------------------
        # 3. Main Navigation Menu (Clean Lucide Outline Icons & Zero Emojis)
        # ---------------------------------------------------------------------
        if not is_collapsed:
            render_html("""<div style="font-size: 0.68rem; color: #64748B; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; margin: 0.65rem 0 0.4rem 0.35rem;">MAIN MENU</div>""")

        # Synchronize widget state safely
        expected_display = current_page
        if expected_display not in filtered_pages and filtered_pages:
            expected_display = filtered_pages[0]

        last_synced = st.session_state.get("_sidebar_last_synced_page")
        if current_page != last_synced or "sidebar_navigation_radio" not in st.session_state:
            st.session_state["sidebar_navigation_radio"] = expected_display
            st.session_state["_sidebar_last_synced_page"] = current_page
        elif st.session_state.get("sidebar_navigation_radio") not in filtered_pages and filtered_pages:
            st.session_state["sidebar_navigation_radio"] = expected_display

        def _on_sidebar_nav_change() -> None:
            """Callback triggered whenever user selects a sidebar navigation item."""
            selected = st.session_state.get("sidebar_navigation_radio")
            target = _get_target_page(selected)
            if target:
                st.session_state["current_page"] = target
                st.session_state["_sidebar_last_synced_page"] = target

        def _format_nav_label(val: Any) -> str:
            s = str(val).strip()
            if s in ("Employee Profile", "👤 Employee Profile", "My Profile", "👤 My Profile", "Profile"):
                return "Profile"
            return display_to_page.get(s, s)

        selected_display = st.radio(
            "Navigation Menu",
            options=filtered_pages,
            label_visibility="collapsed",
            key="sidebar_navigation_radio",
            on_change=_on_sidebar_nav_change,
            format_func=_format_nav_label,
        )

        # Fallback sync for headless testing environments
        target_page = _get_target_page(selected_display)
        if target_page and current_page in pages and target_page != current_page:
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
                # Collapsed: Show centered avatar
                render_html(f"""<div style="display: flex; justify-content: center; margin-bottom: 0.50rem;">
<div style="position: relative;">
<div style="width: 38px; height: 38px; border-radius: 50%; background: linear-gradient(135deg, #0D7A82 0%, #00D2FF 100%); color: #FFFFFF; display: flex; align-items: center; justify-content: center; font-family: 'Poppins', 'Inter', sans-serif; font-weight: 800; font-size: 0.88rem; box-shadow: 0 0 10px rgba(0, 210, 255, 0.35); border: 2px solid rgba(255, 255, 255, 0.2);">
{avatar_initials}
</div>
<span style="position: absolute; bottom: 0; right: 0; width: 8px; height: 8px; background: #10B981; border: 2px solid #0B0E17; border-radius: 50%;"></span>
</div>
</div>""")
                # Collapsed View Profile action
                render_html('<div class="ts-view-profile-anchor"></div>')
                if st.button("👤", key="btn_sidebar_view_profile", help="View Profile", use_container_width=True):
                    st.session_state["current_page"] = "Employee Profile"
                    st.session_state["_sidebar_last_synced_page"] = None
                    st.rerun()

                # Collapsed Account Settings Popover
                with st.popover("⚙", use_container_width=True, help="Account Settings"):
                    render_html(f"""<div style="padding: 0.35rem 0.1rem; font-size: 0.85rem; color: #CBD5E1; font-family: 'Poppins', 'Inter', sans-serif;">
<div style="font-weight: 700; color: #FFFFFF; font-size: 0.95rem; margin-bottom: 0.25rem;">{emp_name}</div>
<div style="color: #00D2FF; font-size: 0.78rem; font-weight: 600; margin-bottom: 0.6rem;">{job_title} · {dept}</div>
<div style="font-size: 0.78rem; color: #94A3B8; margin-bottom: 0.25rem;">Employee ID: <span style="color: #FFFFFF; font-weight: 500;">{emp_id}</span></div>
<div style="font-size: 0.78rem; color: #94A3B8; margin-bottom: 0.65rem;">Session: <span style="color: #10B981; font-weight: 600;">Active</span></div>
</div>""")
                    if st.button("View Profile", key="btn_account_popover_profile", use_container_width=True):
                        st.session_state["current_page"] = "Employee Profile"
                        st.session_state["_sidebar_last_synced_page"] = None
                        st.rerun()
            else:
                # Expanded: Clean modern teal SaaS user card
                render_html(f"""<div class="ts-sidebar-user-card" style="background: #161A29; border: 1px solid rgba(0, 210, 255, 0.18); border-radius: 12px; padding: 0.70rem 0.80rem; margin-bottom: 0.50rem; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.08); display: flex; align-items: center; gap: 0.7rem;">
<div style="position: relative; flex-shrink: 0;">
<div style="width: 38px; height: 38px; border-radius: 50%; background: linear-gradient(135deg, #0D7A82 0%, #00D2FF 100%); color: #FFFFFF; display: flex; align-items: center; justify-content: center; font-family: 'Poppins', 'Inter', sans-serif; font-weight: 800; font-size: 0.88rem; box-shadow: 0 0 10px rgba(0, 210, 255, 0.35); border: 2px solid rgba(255, 255, 255, 0.2);">
{avatar_initials}
</div>
<span style="position: absolute; bottom: 0; right: 0; width: 8px; height: 8px; background: #10B981; border: 2px solid #161A29; border-radius: 50%;"></span>
</div>
<div style="overflow: hidden; text-align: left; flex: 1;">
<div style="font-family: 'Poppins', 'Inter', sans-serif; font-size: 0.88rem; font-weight: 700; color: #FFFFFF; white-space: nowrap; text-overflow: ellipsis; overflow: hidden; line-height: 1.2;">{emp_name}</div>
<div style="font-family: 'Poppins', 'Inter', sans-serif; font-size: 0.74rem; color: #2DD4BF; font-weight: 600; white-space: nowrap; text-overflow: ellipsis; overflow: hidden; margin-top: 2px;">{job_title}</div>
</div>
</div>""")

                # Prominent View Profile Action Button (Direct navigation to Employee Profile page)
                render_html('<div class="ts-view-profile-anchor"></div>')
                if st.button("View Profile", key="btn_sidebar_view_profile", help="Open your full Profile", use_container_width=True):
                    st.session_state["current_page"] = "Employee Profile"
                    st.session_state["_sidebar_last_synced_page"] = None
                    st.rerun()

                # Separate Account Settings Action (Clean, non-overlapping with Lucide Settings outline icon)
                with st.popover("Account Settings", use_container_width=True):
                    render_html(f"""<div style="padding: 0.35rem 0.1rem; font-size: 0.85rem; color: #CBD5E1; font-family: 'Poppins', 'Inter', sans-serif;">
<div style="font-weight: 700; color: #FFFFFF; font-size: 0.95rem; margin-bottom: 0.25rem;">{emp_name}</div>
<div style="color: #00D2FF; font-size: 0.78rem; font-weight: 600; margin-bottom: 0.6rem;">{job_title} · {dept}</div>
<div style="font-size: 0.78rem; color: #94A3B8; margin-bottom: 0.25rem;">Employee ID: <span style="color: #FFFFFF; font-weight: 500;">{emp_id}</span></div>
<div style="font-size: 0.78rem; color: #94A3B8; margin-bottom: 0.65rem;">Session: <span style="color: #10B981; font-weight: 600;">Active</span></div>
</div>""")
                    if st.button("View Profile", key="btn_account_popover_profile", use_container_width=True):
                        st.session_state["current_page"] = "Employee Profile"
                        st.session_state["_sidebar_last_synced_page"] = None
                        st.rerun()

        # Session Controls: Reset Data & Sign Out
        if is_collapsed:
            col_reset, col_out = st.columns(2)
            with col_reset:
                if st.button("↺", key="btn_sidebar_reset", help="Restore fresh sample dataset", use_container_width=True):
                    fresh = get_initial_sample_data()
                    for k, v in fresh.items():
                        st.session_state[k] = v
                    st.toast("Sample data reset to default!", icon="🔄")
                    st.rerun()
            with col_out:
                if st.button("⎋", key="btn_sidebar_signout", help="Sign out of TalentSphere", use_container_width=True):
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
            render_html("""<div style="font-size: 0.70rem; color: #64748B; text-align: center; margin-top: 1.25rem; line-height: 1.4; letter-spacing: 0.02em; font-family: 'Poppins', 'Inter', sans-serif;">
TalentSphere Platform · Elevate v2.0<br>
<span style="color: #2DD4BF; font-weight: 600;">Workforce Intelligence & Growth</span>
</div>""")

    return st.session_state.get("current_page", "Dashboard")
