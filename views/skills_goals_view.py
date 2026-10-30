"""Skills & Goals view for TalentSphere prototype.

Provides interactive skill management with proficiency bars and career goals tracking
with status transitions in session state.
All HTML is rendered via render_html (st.html) to eliminate raw code parsing.
"""

from __future__ import annotations
import os
import streamlit as st
import pandas as pd
from components.cards import (
    render_html,
    render_section_header,
    render_badge,
    render_progress_bar,
    render_demo_banner,
)


def render_skills_goals_page() -> None:
    """Renders the comprehensive Skills & Goals management page."""
    skills = st.session_state.get("skills", [])
    goals = st.session_state.get("goals", [])

    render_html("""<div style="margin-bottom: 1.25rem;">
<h2 style="font-size: 1.75rem; color: #FFFFFF; margin-bottom: 0.25rem;">Skills & Career Goals</h2>
<p style="color: #CBD5E1; font-size: 0.95rem; margin: 0;">
Benchmark your technical capabilities, identify target role gaps, and track short and long-term milestones.
</p>
</div>""")

    tab_skills, tab_goals = st.tabs(["⭐ Skills Inventory & Proficiency", "🎯 Career Goals & Milestones"])

    # ==========================================
    # TAB 1: SKILLS INVENTORY
    # ==========================================
    with tab_skills:
        # Header with Add Skill toggle
        c_head, c_btn = st.columns([3, 1])
        with c_head:
            render_section_header(
                title="Verified Competencies",
                subtitle="Proficiencies categorized by discipline with calibrated progress bars.",
                badge_text=f"{len(skills)} Total Recorded",
                badge_type="teal",
            )
        with c_btn:
            if "show_add_skill_form" not in st.session_state:
                st.session_state["show_add_skill_form"] = False

            toggle_btn_label = "✖️ Close Form" if st.session_state["show_add_skill_form"] else "➕ Add New Skill"
            if st.button(toggle_btn_label, type="primary", use_container_width=True):
                st.session_state["show_add_skill_form"] = not st.session_state["show_add_skill_form"]
                st.rerun()

        # Add Skill Form (if toggled)
        if st.session_state["show_add_skill_form"]:
            with st.container(border=True):
                render_html("<div style='font-size: 0.95rem; font-weight: 700; color: #FFFFFF; margin-bottom: 0.75rem;'>Register a New Skill</div>")
                with st.form("add_skill_form"):
                    col_s1, col_s2, col_s3 = st.columns([2, 1.5, 1.2])
                    with col_s1:
                        skill_name = st.text_input("Skill Name", placeholder="e.g. GraphQL, Apache Kafka")
                    with col_s2:
                        category = st.selectbox(
                            "Category",
                            [
                                "Cloud & Infrastructure",
                                "DevOps & Tooling",
                                "Architecture & Strategy",
                                "Software Engineering",
                                "Leadership & Communication",
                            ],
                        )
                    with col_s3:
                        proficiency = st.selectbox(
                            "Proficiency Level",
                            ["Beginner", "Intermediate", "Advanced", "Expert"],
                        )

                    col_s4, col_s5 = st.columns([2, 1])
                    with col_s4:
                        level_defaults = {"Beginner": 40, "Intermediate": 70, "Advanced": 85, "Expert": 95}
                        progress_val = st.slider(
                            "Calibrated Competency Score (%)",
                            min_value=10,
                            max_value=100,
                            value=level_defaults[proficiency],
                            step=5,
                        )
                    with col_s5:
                        years_exp = st.number_input(
                            "Years of Experience",
                            min_value=0.0,
                            max_value=30.0,
                            value=2.0,
                            step=0.5,
                        )

                    submitted_skill = st.form_submit_button("Add Skill to Profile", type="primary")

                if submitted_skill:
                    if not skill_name.strip():
                        st.error("Please provide a valid skill name.")
                    elif any(s["name"].lower() == skill_name.strip().lower() for s in skills):
                        st.warning(f"Skill '{skill_name.strip()}' is already registered.")
                    else:
                        new_skill_entry = {
                            "id": f"sk-{len(skills)+1}",
                            "name": skill_name.strip(),
                            "category": category,
                            "proficiency": proficiency,
                            "progress": progress_val,
                            "years": years_exp,
                            "status": "Proficient" if progress_val >= 60 else "Focus Area",
                        }
                        st.session_state["skills"].append(new_skill_entry)
                        st.session_state["show_add_skill_form"] = False
                        st.toast(f"Skill '{skill_name.strip()}' added successfully!", icon="⭐")
                        st.rerun()

            render_html("<div style='height: 12px;'></div>")

        # Category Filter Tabs
        cat_filter = st.radio(
            "Filter by Category",
            options=[
                "All Skills",
                "Cloud & Infrastructure",
                "DevOps & Tooling",
                "Architecture & Strategy",
                "Software Engineering",
                "Leadership & Communication",
            ],
            horizontal=True,
            label_visibility="collapsed",
        )

        filtered_skills = (
            skills
            if cat_filter == "All Skills"
            else [s for s in skills if s.get("category") == cat_filter]
        )

        if not filtered_skills:
            st.info(f"No skills registered under category '{cat_filter}'.")
        else:
            for s in filtered_skills:
                with st.container(border=True):
                    c_info, c_bar, c_del = st.columns([2.2, 2.5, 0.7])

                    with c_info:
                        status_badge = "success" if s.get("status") == "Strength" else (
                            "warning" if s.get("status") == "Skill Gap" else "teal"
                        )
                        render_html(f"""<div style="font-weight: 700; font-size: 1.02rem; color: #FFFFFF;">{s.get('name')}</div>
<div style="font-size: 0.82rem; color: #CBD5E1; margin: 0.15rem 0 0.35rem 0;">
{s.get('category')} · <strong style="color: #00D2FF;">{s.get('years', 0)} yrs</strong> hands-on
</div>
<div style="display: flex; gap: 0.4rem; align-items: center;">
<span class="ts-badge ts-badge-{status_badge}">{s.get('status', 'Proficient')}</span>
<span class="ts-badge ts-badge-navy">{s.get('proficiency')}</span>
</div>""")

                    with c_bar:
                        render_progress_bar(
                            label="Skill Proficiency",
                            percentage=s.get("progress", 50),
                            sub_info=f"{s.get('progress', 50)}% ({s.get('proficiency')})",
                            color_scheme="cyan",
                        )

                    with c_del:
                        render_html("<div style='height: 10px;'></div>")
                        if st.button("Remove", key=f"del_sk_{s.get('id')}", use_container_width=True):
                            st.session_state["skills"] = [item for item in skills if item.get("id") != s.get("id")]
                            st.toast(f"Removed {s.get('name')}", icon="🗑️")
                            st.rerun()

        # Strategic Organizational Competencies & Talent Cloud Visual
        render_html("<div style='height: 14px;'></div>")
        wc_path = os.path.join("assets", "employee_wordcloud.png")
        if os.path.exists(wc_path):
            with st.container(border=True):
                col_wc_img, col_wc_desc = st.columns([1.2, 2], gap="medium")
                with col_wc_img:
                    st.image(
                        wc_path,
                        caption="TalentSphere Employee Engagement & Core Capability Focus",
                        use_container_width=True,
                    )
                with col_wc_desc:
                    render_section_header(
                        title="Strategic Competency Landscape",
                        subtitle="Key organizational capabilities and core talent keywords.",
                        badge_text="Talent Cloud",
                        badge_type="teal",
                    )
                    render_html("""<div style="color: #CBD5E1; font-size: 0.9rem; line-height: 1.6;">
TalentSphere continuously cross-references your recorded skills against enterprise 
<strong style="color: #FFFFFF;">leadership</strong>, <strong style="color: #FFFFFF;">consulting</strong>, 
<strong style="color: #FFFFFF;">strategy</strong>, and <strong style="color: #FFFFFF;">engagement</strong> benchmarks.<br><br>
• <strong style="color: #00D2FF;">Core Synergies:</strong> Teamwork, Technical Consulting, System Strategy<br>
• <strong style="color: #00D2FF;">Leadership Competencies:</strong> Mentorship, Active Communication, Autonomy<br>
• <strong style="color: #00D2FF;">Organizational Health:</strong> Continuous Learning, Talent Recognition, Squad Collaboration
</div>""")

    # ==========================================
    # TAB 2: CAREER GOALS
    # ==========================================
    with tab_goals:
        c_ghead, c_gbtn = st.columns([3, 1])
        with c_ghead:
            render_section_header(
                title="Career Milestones & Goal Tracker",
                subtitle="Track progression toward your short-term deliverables and long-term career target.",
                badge_text=f"{len(goals)} Goals Active",
                badge_type="teal",
            )
        with c_gbtn:
            if "show_add_goal_form" not in st.session_state:
                st.session_state["show_add_goal_form"] = False

            toggle_goal_label = "✖️ Close Form" if st.session_state["show_add_goal_form"] else "➕ Add New Goal"
            if st.button(toggle_goal_label, type="primary", use_container_width=True, key="toggle_goal_btn"):
                st.session_state["show_add_goal_form"] = not st.session_state["show_add_goal_form"]
                st.rerun()

        # Add Goal Form
        if st.session_state["show_add_goal_form"]:
            with st.container(border=True):
                render_html("<div style='font-size: 0.95rem; font-weight: 700; color: #FFFFFF; margin-bottom: 0.75rem;'>Define a New Career Goal</div>")
                with st.form("add_goal_form"):
                    g_title = st.text_input("Goal Title", placeholder="e.g. Lead Enterprise Disaster Recovery Simulation")
                    col_g1, col_g2, col_g3 = st.columns(3)
                    with col_g1:
                        g_type = st.selectbox("Timeline Horizon", ["Short-Term", "Long-Term"])
                    with col_g2:
                        g_date = st.text_input("Target Date / Timeline", placeholder="e.g. Q1 2027")
                    with col_g3:
                        g_status = st.selectbox("Current Status", ["Not Started", "In Progress", "Completed"])

                    g_desc = st.text_area(
                        "Measurable Outcome / Description",
                        placeholder="Describe key success criteria and expected business impact...",
                        height=80,
                    )

                    submitted_goal = st.form_submit_button("Save Career Goal", type="primary")

                if submitted_goal:
                    if not g_title.strip():
                        st.error("Please enter a goal title.")
                    elif not g_date.strip():
                        st.error("Please specify a target timeline.")
                    else:
                        init_progress = 100 if g_status == "Completed" else (50 if g_status == "In Progress" else 0)
                        new_goal_entry = {
                            "id": f"g-{len(goals)+1}",
                            "title": g_title.strip(),
                            "type": g_type,
                            "target_date": g_date.strip(),
                            "status": g_status,
                            "progress": init_progress,
                            "description": g_desc.strip(),
                        }
                        st.session_state["goals"].append(new_goal_entry)
                        st.session_state["show_add_goal_form"] = False
                        st.toast(f"Goal '{g_title.strip()}' created!", icon="🎯")
                        st.rerun()

            render_html("<div style='height: 12px;'></div>")

        # Goal Horizon Filter
        goal_filter = st.radio(
            "Filter Goals",
            options=["All Goals", "Short-Term", "Long-Term"],
            horizontal=True,
            label_visibility="collapsed",
        )

        filtered_goals = (
            goals
            if goal_filter == "All Goals"
            else [g for g in goals if g.get("type") == goal_filter]
        )

        for g in filtered_goals:
            with st.container(border=True):
                col_ginfo, col_gstatus = st.columns([3, 1.5])

                with col_ginfo:
                    type_badge = "teal" if g.get("type") == "Short-Term" else "navy"
                    render_html(f"""<div style="display: flex; gap: 0.5rem; align-items: center; margin-bottom: 0.3rem;">
<span class="ts-badge ts-badge-{type_badge}">{g.get('type')}</span>
<span style="font-size: 0.82rem; color: #CBD5E1;">Target: <strong style="color: #00D2FF;">{g.get('target_date')}</strong></span>
</div>
<div style="font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin-bottom: 0.4rem;">
{g.get('title')}
</div>
<div style="font-size: 0.86rem; color: #94A3B8; line-height: 1.45; margin-bottom: 0.6rem;">
{g.get('description', '')}
</div>""")
                    render_progress_bar(
                        label="Milestone Progress",
                        percentage=g.get("progress", 0),
                        sub_info=f"{g.get('progress', 0)}%",
                        color_scheme="pink" if g.get("status") == "In Progress" else "cyan",
                    )

                with col_gstatus:
                    render_html("<div style='font-size: 0.78rem; font-weight: 700; color: #CBD5E1; margin-bottom: 0.35rem;'>UPDATE STATUS</div>")
                    status_options = ["Not Started", "In Progress", "Completed"]
                    current_idx = status_options.index(g.get("status", "In Progress"))
                    new_status = st.selectbox(
                        "Status",
                        options=status_options,
                        index=current_idx,
                        key=f"status_select_{g.get('id')}",
                        label_visibility="collapsed",
                    )

                    if new_status != g.get("status"):
                        g["status"] = new_status
                        if new_status == "Completed":
                            g["progress"] = 100
                        elif new_status == "Not Started":
                            g["progress"] = 0
                        elif new_status == "In Progress" and g["progress"] in [0, 100]:
                            g["progress"] = 50

                        st.toast(f"Status for '{g.get('title')}' updated to {new_status}!", icon="🔄")
                        st.rerun()

                    if new_status == "In Progress":
                        new_p = st.slider(
                            "Progress %",
                            0,
                            100,
                            int(g.get("progress", 50)),
                            step=5,
                            key=f"prog_slider_{g.get('id')}",
                        )
                        if new_p != g.get("progress"):
                            g["progress"] = new_p
                            st.rerun()
