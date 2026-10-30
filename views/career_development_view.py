"""Career Development view for TalentSphere prototype.

Displays current vs. target role mapping, Plotly competency gap analysis chart in dark theme,
suggested development activities, and multi-phase career learning milestones.
All HTML is rendered via render_html (st.html) to eliminate raw code parsing.
"""

from __future__ import annotations
import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from components.cards import (
    render_html,
    render_section_header,
    render_badge,
    render_progress_bar,
    render_demo_banner,
)


def render_career_development_page() -> None:
    """Renders the comprehensive Career Development and Progression view in dark mode."""
    employee = st.session_state.get("employee", {})
    career_target = st.session_state.get("career_target", {})
    competencies = career_target.get("competencies", [])
    activities = career_target.get("suggested_activities", [])
    milestones = career_target.get("learning_milestones", [])

    render_demo_banner(
        "<strong>Calibrated Progression Framework:</strong> Career competency benchmarks and suggested activities "
        "are mapped using enterprise cloud architecture telemetry.",
        icon="🚀",
    )

    # 1. Trajectory Header Card
    with st.container(border=True):
        col_t1, col_t2 = st.columns([3, 1.2])

        with col_t1:
            render_html(f"""<div style="font-size: 0.8rem; font-weight: 700; color: #00D2FF; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.2rem;">
TARGET CAREER TRAJECTORY
</div>
<h2 style="margin: 0 0 0.4rem 0; font-size: 1.7rem; color: #FFFFFF;">
{career_target.get('current_role')} 
<span style="color: #FF2A75; font-size: 1.4rem; text-shadow: 0 0 10px rgba(255,42,117,0.5);">➔</span> 
{career_target.get('target_role')}
</h2>
<div style="font-size: 0.88rem; color: #CBD5E1; margin-bottom: 0.8rem;">
Target Department: <strong style="color: #FFFFFF;">{career_target.get('target_department')}</strong> · Target Timeline: <strong style="color: #00D2FF;">{career_target.get('target_timeline')}</strong>
</div>
<div style="background: #1B2032; border-left: 3px solid #00D2FF; padding: 0.85rem 1.1rem; font-size: 0.9rem; color: #E2E8F0; line-height: 1.55; border-radius: 0 10px 10px 0; box-shadow: inset 0 1px 0 rgba(255,255,255,0.06);">
{career_target.get('role_description')}
</div>""")

        with col_t2:
            render_html("""<div style="height: 12px;"></div>""")
            readiness = career_target.get("overall_readiness", 68)
            render_html(f"""<div style="background: #1B2032; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 1.25rem 1rem; text-align: center; box-shadow: 0 8px 24px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.06);">
<div style="font-size: 0.78rem; font-weight: 700; color: #CBD5E1; text-transform: uppercase; letter-spacing: 0.05em;">Role Readiness</div>
<div style="font-size: 2.3rem; font-weight: 800; color: #00D2FF; margin: 0.2rem 0; text-shadow: 0 0 16px rgba(0, 210, 255, 0.45);">{readiness}%</div>
<div style="font-size: 0.78rem; color: #FF2A75; font-weight: 700;">3 Milestones In Progress</div>
</div>""")
            render_progress_bar("Overall Progression", readiness, color_scheme="cyan")

    render_html("""<div style="height: 14px;"></div>""")

    # 2. Competency Benchmark & Gap Analysis Chart
    with st.container(border=True):
        render_section_header(
            title="Competency Gap Analysis vs. Target Role Requirements",
            subtitle="Comparison of your current verified skill proficiency against the required threshold for Principal Architect.",
            badge_text="Calibrated Benchmark",
            badge_type="teal",
        )

        if competencies:
            df_comp = pd.DataFrame(competencies)

            fig = go.Figure()
            # Current employee score bar (Electric Cyan)
            fig.add_trace(
                go.Bar(
                    x=df_comp["skill"],
                    y=df_comp["current_score"],
                    name="Current Proficiency",
                    marker=dict(
                        color="#00D2FF",
                        line=dict(width=0),
                    ),
                    text=df_comp["current_score"].apply(lambda v: f"{v}%"),
                    textposition="auto",
                    textfont=dict(color="#0B0E17", size=10, family="Plus Jakarta Sans"),
                )
            )
            # Required target score bar (Neon Pink/Magenta)
            fig.add_trace(
                go.Bar(
                    x=df_comp["skill"],
                    y=df_comp["required_score"],
                    name="Target Role Threshold",
                    marker=dict(
                        color="#FF2A75",
                        line=dict(width=0),
                    ),
                    text=df_comp["required_score"].apply(lambda v: f"{v}%"),
                    textposition="auto",
                    textfont=dict(color="#FFFFFF", size=10, family="Plus Jakarta Sans"),
                )
            )

            fig.update_layout(
                barmode="group",
                height=360,
                margin=dict(l=10, r=10, t=25, b=60),
                plot_bgcolor="#161A29",
                paper_bgcolor="#161A29",
                font=dict(family="Plus Jakarta Sans, Inter, sans-serif", color="#FFFFFF"),
                xaxis=dict(
                    tickfont=dict(size=10, color="#CBD5E1"),
                    tickangle=-20,
                    showgrid=False,
                    linecolor="rgba(255, 255, 255, 0.08)",
                ),
                yaxis=dict(
                    title=dict(text="Proficiency Score (%)", font=dict(color="#CBD5E1", size=11)),
                    range=[0, 105],
                    gridcolor="rgba(255, 255, 255, 0.05)",
                    tickfont=dict(color="#CBD5E1"),
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(size=11, color="#FFFFFF"),
                ),
            )
            st.plotly_chart(fig, use_container_width=True)

        # Tabular Summary of Gaps
        render_html("<div style='font-size: 0.95rem; font-weight: 700; color: #FFFFFF; margin: 1rem 0 0.5rem 0;'>Competency Breakdown Table</div>")

        for comp in competencies:
            gap_val = comp.get("gap", 0)
            if gap_val == 0:
                p_badge = "teal"
                p_text = "Target Met"
            elif gap_val > 30:
                p_badge = "pink"
                p_text = f"-{gap_val}% (High Priority)"
            else:
                p_badge = "warning"
                p_text = f"-{gap_val}% (Medium Priority)"

            render_html(f"""<div style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 0.5rem; border-bottom: 1px solid rgba(255, 255, 255, 0.06); font-size: 0.88rem;">
<div style="font-weight: 700; color: #FFFFFF; flex-basis: 35%;">{comp.get('skill')}</div>
<div style="color: #CBD5E1; flex-basis: 25%;">Current: <strong style="color: #00D2FF;">{comp.get('current_level')} ({comp.get('current_score')}%)</strong></div>
<div style="color: #CBD5E1; flex-basis: 25%;">Required: <strong style="color: #FFFFFF;">{comp.get('required_level')} ({comp.get('required_score')}%)</strong></div>
<div style="flex-basis: 15%; text-align: right;"><span class="ts-badge ts-badge-{p_badge}">{p_text}</span></div>
</div>""")

    render_html("""<div style="height: 14px;"></div>""")

    # Collaborative Mentorship & Growth Visual Highlight
    growth_img = os.path.join("assets", "career_growth.png")
    if os.path.exists(growth_img):
        with st.container(border=True):
            col_g_img, col_g_txt = st.columns([1.1, 2], gap="medium")
            with col_g_img:
                st.image(
                    growth_img,
                    caption="Collaborative Mentorship & Talent Growth",
                    use_container_width=True,
                )
            with col_g_txt:
                render_section_header(
                    title="Nurturing Talent & Collaborative Mobility",
                    subtitle="Empowering employees and squads to grow together toward strategic horizons.",
                    badge_text="Career Mentorship",
                    badge_type="teal",
                )
                render_html("""<div style="color: #CBD5E1; line-height: 1.6; font-size: 0.9rem;">
Career advancement at TalentSphere is rooted in hands-on mentorship, cross-squad 
architecture sponsorship, and shared organizational achievement.<br><br>
• <strong style="color: #FFFFFF;">Executive Sponsorship</strong>: Connect with Senior and Principal architects during quarterly reviews.<br>
• <strong style="color: #FFFFFF;">Knowledge Sharing</strong>: Lead internal tech talks and author golden-path design templates.<br>
• <strong style="color: #FFFFFF;">Continuous Upskilling</strong>: Balance individual technical excellence with strategic team impact.
</div>""")

        render_html("""<div style="height: 14px;"></div>""")

    # 3. Suggested Development Activities
    with st.container(border=True):
        render_section_header(
            title="Suggested Development Activities",
            subtitle="Curated programs designed to close your identified competency gaps.",
            badge_text="4 Available",
            badge_type="teal",
        )

        col_act1, col_act2 = st.columns(2)

        for idx, act in enumerate(activities):
            target_col = col_act1 if idx % 2 == 0 else col_act2
            with target_col:
                with st.container(border=True):
                    render_html(f"""<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.35rem;">
<span class="ts-badge ts-badge-teal">{act.get('category')}</span>
<span class="ts-badge ts-badge-pink">{act.get('priority')}</span>
</div>
<div style="font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin: 0.3rem 0;">
{act.get('title')}
</div>
<div style="font-size: 0.82rem; color: #00D2FF; font-weight: 600; margin-bottom: 0.35rem;">
Provider: {act.get('provider')} · ⏱️ {act.get('duration')}
</div>
<div style="font-size: 0.85rem; color: #CBD5E1; line-height: 1.45; margin-bottom: 0.6rem;">
{act.get('description')}
</div>
<div style="font-size: 0.8rem; font-weight: 600; color: #00D2FF; margin-bottom: 0.8rem;">
💡 Expected Impact: <strong style="color: #FFFFFF;">{act.get('impact')}</strong>
</div>""")

                    # Dynamic Action Button: Add to Goals
                    if st.button("➕ Add to My Career Goals", key=f"add_act_goal_{idx}", use_container_width=True, type="primary"):
                        current_goals = st.session_state.get("goals", [])
                        if not any(g["title"] == act["title"] for g in current_goals):
                            new_goal = {
                                "id": f"g-{len(current_goals)+1}",
                                "title": act["title"],
                                "type": "Short-Term",
                                "target_date": "Q1 2027",
                                "status": "In Progress",
                                "progress": 15,
                                "description": f"{act['description']} (Impact: {act['impact']})",
                            }
                            st.session_state["goals"].append(new_goal)
                            st.toast(f"Added '{act['title']}' to your active goals!", icon="🎯")
                        else:
                            st.info(f"'{act['title']}' is already in your career goals list.")

    render_html("""<div style="height: 14px;"></div>""")

    # 4. Career Progression Roadmap & Learning Milestones
    with st.container(border=True):
        render_section_header(
            title="Strategic Learning Milestones Roadmap",
            subtitle="Phased checkpoints leading to target role candidacy and promotion review.",
            badge_text="4 Phases",
            badge_type="navy",
        )

        for m in milestones:
            p_badge = "teal" if m.get("status") == "Completed" else (
                "pink" if m.get("status") == "In Progress" else "navy"
            )
            with st.container(border=True):
                col_m1, col_m2 = st.columns([3, 1.2])
                with col_m1:
                    render_html(f"""<div style="display: flex; gap: 0.5rem; align-items: center; margin-bottom: 0.25rem;">
<span class="ts-badge ts-badge-navy">{m.get('phase')}</span>
<span class="ts-badge ts-badge-{p_badge}">{m.get('status')}</span>
<span style="font-size: 0.82rem; color: #CBD5E1;">{m.get('timeline')}</span>
</div>
<div style="font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin-bottom: 0.25rem;">
{m.get('title')}
</div>
<div style="font-size: 0.86rem; color: #CBD5E1; line-height: 1.45;">
{m.get('description')}
</div>""")
                with col_m2:
                    render_html("<div style='height: 10px;'></div>")
                    render_progress_bar("Phase Progress", m.get("progress", 0), color_scheme="pink" if m.get("status") == "In Progress" else "cyan")

    render_html("""<div style="height: 14px;"></div>""")

    # 5. Quick Navigation Footer Actions
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("🎯 Navigate to Skills & Goals", use_container_width=True, type="secondary"):
            st.session_state["current_page"] = "Skills & Goals"
            st.rerun()
    with col_nav2:
        if st.button("📊 Return to Executive Dashboard", use_container_width=True, type="secondary"):
            st.session_state["current_page"] = "Dashboard"
            st.rerun()
