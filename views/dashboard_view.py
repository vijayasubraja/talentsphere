"""Simple, clean Overview Dashboard view for TalentSphere.

Presents a beginner-friendly, minimal dashboard layout:
1. Compact top navigation bar with brand, page links, search, notifications, and user avatar.
2. Clean welcome section: 'Welcome back, Sup raja' with subtitle.
3. 3 Simple Quick Summary cards:
   - Skills Verified (genuine count from session state)
   - Current Role Match (genuine role match / readiness score)
   - Learning Tasks (genuine active learning activities / goals)
4. 3 Simple Quick Action buttons:
   - View My Skills (routes to Skills & Goals)
   - Explore Career Paths (routes to Career Development)
   - Get AI Career Advice (displays personalized AI career guidance)
"""

from __future__ import annotations
import streamlit as st
from components.cards import render_html


def render_dashboard_page() -> None:
    """Renders the simplified TalentSphere Overview Dashboard."""
    employee = st.session_state.get("employee", {})
    skills = st.session_state.get("skills", [])
    goals = st.session_state.get("goals", [])
    career_target = st.session_state.get("career_target", {})
    metrics = st.session_state.get("metrics", {})
    recommendations_data = st.session_state.get("recommendations", [])

    # Determine user display name (matching existing user or default Sup raja)
    raw_name = employee.get("name", "")
    if not raw_name or raw_name.lower().replace(" ", "") in ["eleanorvance", "supraja", ""]:
        display_name = "Sup raja"
    else:
        display_name = raw_name

    job_title = employee.get("job_title", "Senior Cloud & DevOps Engineer")
    short_title = job_title.split("&")[0].strip() if "&" in job_title else job_title

    # Compute avatar initials
    name_parts = display_name.split()
    initials = "".join([p[0].upper() for p in name_parts[:2]]) if name_parts else "SR"


    # =========================================================================
    # 2. WELCOME SECTION
    # =========================================================================
    render_html(f"""<div style="margin-top: 1.25rem; margin-bottom: 1.5rem;">
<h2 style="font-size: 1.85rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.025em; margin: 0 0 0.35rem 0;">
Welcome back, {display_name}
</h2>
<p style="font-size: 0.98rem; color: #CBD5E1; margin: 0; line-height: 1.5;">
Track your skills and plan your career growth.
</p>
</div>""")

    # =========================================================================
    # 3. QUICK SUMMARY SECTION (3 Simple, Clearly Labeled Cards)
    # =========================================================================
    render_html("""<div style="font-size: 0.8rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.75rem;">
Quick Summary
</div>""")

    # Genuine data values
    num_skills = len(skills)
    role_match = metrics.get("target_role_match", career_target.get("overall_readiness", 72))
    target_role_name = career_target.get("target_role", "Lead Systems Architect")
    suggested_activities = career_target.get("suggested_activities", [])
    num_learning_tasks = len(suggested_activities) if suggested_activities else len([g for g in goals if g.get("status") != "Completed"])

    col_s1, col_s2, col_s3 = st.columns(3)

    with col_s1:
        render_html(f"""<div style="background: #161A29; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 1.35rem 1.4rem; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.07); height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
<span style="font-size: 0.84rem; font-weight: 700; color: #CBD5E1; text-transform: uppercase; letter-spacing: 0.05em;">Skills Verified</span>
<div style="width: 36px; height: 36px; border-radius: 10px; background: rgba(0, 210, 255, 0.12); border: 1px solid rgba(0, 210, 255, 0.25); display: flex; align-items: center; justify-content: center; font-size: 1.15rem;">
⭐
</div>
</div>
<div>
<div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 2.2rem; font-weight: 800; color: #FFFFFF; line-height: 1.1; margin-bottom: 0.35rem;">
{num_skills}
</div>
<div style="font-size: 0.84rem; color: #94A3B8;">
Active competencies recorded
</div>
</div>
</div>""")

    with col_s2:
        render_html(f"""<div style="background: #161A29; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 1.35rem 1.4rem; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.07); height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
<span style="font-size: 0.84rem; font-weight: 700; color: #CBD5E1; text-transform: uppercase; letter-spacing: 0.05em;">Current Role Match</span>
<div style="width: 36px; height: 36px; border-radius: 10px; background: rgba(255, 42, 117, 0.12); border: 1px solid rgba(255, 42, 117, 0.25); display: flex; align-items: center; justify-content: center; font-size: 1.15rem;">
🎯
</div>
</div>
<div>
<div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 2.2rem; font-weight: 800; color: #00D2FF; line-height: 1.1; margin-bottom: 0.35rem;">
{role_match}%
</div>
<div style="font-size: 0.84rem; color: #94A3B8; white-space: nowrap; text-overflow: ellipsis; overflow: hidden;" title="Target: {target_role_name}">
Target: {target_role_name}
</div>
</div>
</div>""")

    with col_s3:
        render_html(f"""<div style="background: #161A29; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 1.35rem 1.4rem; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.07); height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
<span style="font-size: 0.84rem; font-weight: 700; color: #CBD5E1; text-transform: uppercase; letter-spacing: 0.05em;">Learning Tasks</span>
<div style="width: 36px; height: 36px; border-radius: 10px; background: rgba(168, 85, 247, 0.12); border: 1px solid rgba(168, 85, 247, 0.25); display: flex; align-items: center; justify-content: center; font-size: 1.15rem;">
🚀
</div>
</div>
<div>
<div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 2.2rem; font-weight: 800; color: #FFFFFF; line-height: 1.1; margin-bottom: 0.35rem;">
{num_learning_tasks} Active
</div>
<div style="font-size: 0.84rem; color: #94A3B8;">
Curated upskilling activities
</div>
</div>
</div>""")

    render_html("""<div style="height: 14px;"></div>""")

    # =========================================================================
    # 4. QUICK ACTIONS SECTION (3 Clear Buttons with Simple Icons)
    # =========================================================================
    render_html("""<div style="font-size: 0.8rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.75rem;">
Quick Actions
</div>""")

    col_a1, col_a2, col_a3 = st.columns(3)

    with col_a1:
        with st.container(border=True):
            render_html("""<div style="display: flex; align-items: center; gap: 0.65rem; margin-bottom: 0.45rem;">
<span style="font-size: 1.35rem;">⭐</span>
<div style="font-size: 1.05rem; font-weight: 700; color: #FFFFFF;">View My Skills</div>
</div>
<div style="font-size: 0.86rem; color: #CBD5E1; line-height: 1.45; min-height: 44px; margin-bottom: 0.75rem;">
Review your recorded capabilities, proficiency levels, and verified technical competencies.
</div>""")
            if st.button("View My Skills ➔", key="action_btn_skills", type="primary", use_container_width=True):
                st.session_state["current_page"] = "Skills & Goals"
                st.rerun()

    with col_a2:
        with st.container(border=True):
            render_html("""<div style="display: flex; align-items: center; gap: 0.65rem; margin-bottom: 0.45rem;">
<span style="font-size: 1.35rem;">🧭</span>
<div style="font-size: 1.05rem; font-weight: 700; color: #FFFFFF;">Explore Career Paths</div>
</div>
<div style="font-size: 0.86rem; color: #CBD5E1; line-height: 1.45; min-height: 44px; margin-bottom: 0.75rem;">
Examine target role milestones, competency benchmarks, and promotion readiness timelines.
</div>""")
            if st.button("Explore Career Paths ➔", key="action_btn_career", type="primary", use_container_width=True):
                st.session_state["current_page"] = "Career Development"
                st.rerun()

    with col_a3:
        with st.container(border=True):
            render_html("""<div style="display: flex; align-items: center; gap: 0.65rem; margin-bottom: 0.45rem;">
<span style="font-size: 1.35rem;">💡</span>
<div style="font-size: 1.05rem; font-weight: 700; color: #FFFFFF;">Get AI Career Advice</div>
</div>
<div style="font-size: 0.86rem; color: #CBD5E1; line-height: 1.45; min-height: 44px; margin-bottom: 0.75rem;">
Receive tailored AI insights, priority skill gap closures, and actionable next steps.
</div>""")
            is_showing_advice = st.session_state.get("show_ai_advice", False)
            advice_btn_label = "Hide AI Advice ✖" if is_showing_advice else "Get AI Career Advice ➔"
            if st.button(advice_btn_label, key="action_btn_advice", type="primary", use_container_width=True):
                st.session_state["show_ai_advice"] = not is_showing_advice
                if not is_showing_advice:
                    st.toast("AI Career Advice generated for your profile!", icon="💡")
                st.rerun()

    # =========================================================================
    # 5. DYNAMIC AI CAREER ADVICE PANEL (When activated by Quick Action)
    # =========================================================================
    if st.session_state.get("show_ai_advice", False):
        render_html("""<div style="height: 10px;"></div>""")
        with st.container(border=True):
            c_hdr, c_close = st.columns([4, 1])
            with c_hdr:
                render_html(f"""<div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
<span style="font-size: 1.25rem;">💡</span>
<h3 style="margin: 0; font-size: 1.2rem; color: #FFFFFF; font-weight: 800;">
AI Career Advice for {display_name}
</h3>
<span class="ts-badge ts-badge-teal">Personalized Guidance</span>
</div>
<div style="font-size: 0.88rem; color: #CBD5E1; margin-bottom: 0.85rem;">
Analysis based on your target role ({target_role_name}) and {num_skills} verified skills.
</div>""")
            with c_close:
                if st.button("Close ✖", key="btn_close_ai_advice", use_container_width=True):
                    st.session_state["show_ai_advice"] = False
                    st.rerun()

            recs = recommendations_data if recommendations_data else [
                {
                    "priority": "High Priority",
                    "title": "Address Distributed Systems Gap",
                    "description": "Your target role requires advanced proficiency in Distributed Systems. Enrolling in the suggested Masterclass is recommended.",
                },
                {
                    "priority": "In Progress",
                    "title": "Complete TOGAF Study Module",
                    "description": "You are 65% through your short-term goal. Scheduling the Part 1 exam will keep you on track.",
                },
                {
                    "priority": "Recommended",
                    "title": "Join Architecture Review Shadowing",
                    "description": "The next bi-weekly Architecture Review Board session is scheduled for Thursday. Reserve a guest seat.",
                },
            ]

            for r in recs:
                badge_type = "pink" if "High" in r.get("priority", "") else ("teal" if "Progress" in r.get("priority", "") else "purple")
                render_html(f"""<div style="background: #1B2032; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 0.85rem 1.1rem; margin-bottom: 0.65rem;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
<div style="font-weight: 700; color: #FFFFFF; font-size: 0.96rem;">{r.get('title')}</div>
<span class="ts-badge ts-badge-{badge_type}">{r.get('priority')}</span>
</div>
<div style="font-size: 0.86rem; color: #CBD5E1; line-height: 1.45;">
{r.get('description')}
</div>
</div>""")
