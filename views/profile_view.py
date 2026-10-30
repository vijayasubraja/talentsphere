"""Employee Profile view for TalentSphere platform.

Transforms the profile page into an Employee Work Process, Goals, and Task Progress Tracking Module.
Preserves existing dark theme UI styling, card designs, borders, rounded corners, spacing, typography, and icons.

Includes:
- Top Employee Header (Employee Name, Designation, Department, Location, Experience)
- EMPLOYEE WORK PROGRESS Dashboard (Total Tasks, Completed, In Progress, Yet to Complete, Completion %, Progress Bar, Task Summary)
- Section A: Employee Details (ID, Name, Designation, Department, Reporting Manager, Joining Date, Work Location)
- Section B: Process & Goals (Current Process Name, Description, Responsibilities, Short/Long-term Goals, Deliverables, Target Date)
- Section C: Task Management (Completed, In Progress, Yet to Complete with Add, Edit, Delete, Status change, Progress update, Deadlines)
- Section D: Challenges & Support (Challenges Faced, Reason for Delay, Support Required, Manager Remarks)
- Section E: Overall Work Progress (Total Assigned, Completed, In-Progress, Pending, Completion % Formula, Upcoming Milestones)
- Suggestions & Improvements (Work-related dynamic recommendations based on actual tasks & progress)
- View Mode vs. Edit Mode with validation and SQLite persistence.
"""

from __future__ import annotations
from datetime import date, datetime
from typing import Any
import streamlit as st
import services.core
from components.cards import (
    render_html,
    render_section_header,
    render_badge,
    render_progress_bar,
)


def _init_work_draft(work_details: dict[str, Any], user: dict[str, Any]) -> dict[str, Any]:
    """Initializes edit draft for employee work profile."""
    return {
        "name": user.get("name") or work_details.get("name", "Employee"),
        "employee_id_code": work_details.get("employee_id_code", ""),
        "designation": work_details.get("designation", ""),
        "department": work_details.get("department", ""),
        "reporting_manager": work_details.get("reporting_manager", ""),
        "joining_date": work_details.get("joining_date", ""),
        "work_location": work_details.get("work_location", ""),
        "process_name": work_details.get("process_name", ""),
        "process_description": work_details.get("process_description", ""),
        "assigned_responsibilities": work_details.get("assigned_responsibilities", ""),
        "short_term_goals": work_details.get("short_term_goals", ""),
        "long_term_goals": work_details.get("long_term_goals", ""),
        "expected_deliverables": work_details.get("expected_deliverables", ""),
        "target_completion_date": work_details.get("target_completion_date", ""),
        "challenges_faced": work_details.get("challenges_faced", ""),
        "reason_for_delay": work_details.get("reason_for_delay", ""),
        "support_required": work_details.get("support_required", ""),
        "manager_remarks": work_details.get("manager_remarks", ""),
    }


def render_profile_page() -> None:
    """Renders the Employee Work Process, Goals and Task Progress Tracking Module."""
    uid = st.session_state.get("user_id")
    if not uid:
        st.error("Please sign in to view and manage your employee work profile.")
        st.stop()

    # Page-level styles for full-width layout and consistent typography scale
    render_html("""<style>
    .main .block-container {
        max-width: 1400px !important;
        width: 100% !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    }
    .main h1 { font-size: 28px !important; font-weight: 800 !important; }
    .main h2 { font-size: 26px !important; font-weight: 800 !important; }
    .main h3 { font-size: 21px !important; font-weight: 700 !important; }
    .main p, .main span, .main div { font-size: 16px; }
    .main .ts-badge { font-size: 14px !important; }
    div[data-testid="stWidgetLabel"] label,
    div[data-testid="stWidgetLabel"] p { font-size: 15px !important; font-weight: 600 !important; }
    </style>""")

    # Authoritative records from SQLite
    user = services.core.get_user_by_id(uid) or {}
    work_details = services.core.get_employee_work_details(uid)
    tasks = services.core.get_employee_tasks(uid)

    # Dynamic metrics calculation
    metrics = services.core.calculate_work_metrics(tasks)
    total_tasks = metrics["total_tasks"]
    completed_tasks = metrics["completed_tasks"]
    in_prog_tasks = metrics["in_progress_tasks"]
    pending_tasks = metrics["pending_tasks"]
    completion_pct = metrics["completion_percentage"]

    user_name = user.get("name") or work_details.get("name", "Employee")
    designation = work_details.get("designation") or "Senior Cloud & DevOps Engineer"
    department = work_details.get("department") or "Platform Engineering & Infrastructure"
    location = work_details.get("work_location") or "Austin, TX (Hybrid)"
    exp_yrs = work_details.get("years_experience", 5.0)

    # Mode toggle state
    if "is_editing_profile" not in st.session_state:
        st.session_state["is_editing_profile"] = False

    # Initialize edit draft state
    if st.session_state["is_editing_profile"] and "work_profile_draft" not in st.session_state:
        st.session_state["work_profile_draft"] = _init_work_draft(work_details, user)

    # =========================================================================
    # TOP EMPLOYEE HEADER CARD
    # =========================================================================
    with st.container(border=True):
        col_avatar, col_details, col_meta = st.columns([1, 3.8, 1.8])

        name_parts = user_name.split()
        initials = "".join([p[0].upper() for p in name_parts[:2]]) if name_parts else "EV"

        with col_avatar:
            render_html(f"""<div style="display: flex; justify-content: center; align-items: center; height: 100%;">
<div class="ts-avatar" style="width: 88px; height: 88px; font-size: 28px; box-shadow: 0 0 16px rgba(0, 210, 255, 0.4); border: 2px solid rgba(0, 210, 255, 0.5);">
{initials}
</div>
</div>""")

        with col_details:
            proc_title = work_details.get("process_name") or "Cloud Infrastructure Modernization"
            emp_id = work_details.get("employee_id_code") or f"EMP-{uid:04d}"

            render_html(f"""<div style="margin-left: 0.25rem;">
<h2 style="margin: 0 0 0.25rem 0; font-size: 26px; color: #FFFFFF; font-weight: 800; letter-spacing: -0.02em;">
{user_name}
</h2>
<div style="font-size: 18px; font-weight: 600; color: #00D2FF; margin-bottom: 0.35rem;">
{designation}
</div>
<div style="font-size: 16px; color: #CBD5E1; margin-bottom: 0.6rem;">
🏢 {department} · 📍 {location} · ⏱️ {exp_yrs} Years Exp
</div>
<div style="display: flex; flex-wrap: wrap; gap: 0.45rem; align-items: center;">
<span class="ts-badge ts-badge-teal" style="font-size: 14px;">Full-time</span>
<span class="ts-badge ts-badge-navy" style="font-size: 14px;">ID: {emp_id}</span>
<span class="ts-badge ts-badge-cyan" style="font-size: 14px; background: rgba(0, 210, 255, 0.15); border: 1px solid rgba(0, 210, 255, 0.35); color: #00D2FF;">Process: {proc_title[:36]}</span>
<span class="ts-badge ts-badge-success" style="font-size: 14px;">{completed_tasks}/{total_tasks} Tasks Completed</span>
</div>
</div>""")

        with col_meta:
            render_html("""<div style="height: 6px;"></div>""")
            if not st.session_state["is_editing_profile"]:
                if st.button("✏️ Edit Work Profile", type="primary", use_container_width=True, key="btn_enter_edit_mode"):
                    st.session_state["work_profile_draft"] = _init_work_draft(work_details, user)
                    st.session_state["is_editing_profile"] = True
                    st.rerun()
            else:
                col_save_top, col_cancel_top = st.columns(2)
                with col_save_top:
                    if st.button("💾 Save", type="primary", use_container_width=True, key="btn_save_top_quick"):
                        st.session_state["trigger_profile_save"] = True
                with col_cancel_top:
                    if st.button("✖️ Cancel", type="secondary", use_container_width=True, key="btn_cancel_top_quick"):
                        st.session_state.pop("work_profile_draft", None)
                        st.session_state["is_editing_profile"] = False
                        st.toast("Edits discarded.", icon="ℹ️")
                        st.rerun()

    render_html("""<div style="height: 12px;"></div>""")

    # =========================================================================
    # PROFILE PROGRESS DASHBOARD -> EMPLOYEE WORK PROGRESS
    # =========================================================================
    with st.container(border=True):
        badge_status = "On Track" if completion_pct >= 60 else "In Progress" if total_tasks > 0 else "No Tasks Assigned"
        badge_type = "teal" if completion_pct >= 60 else "warning"

        render_section_header(
            title=f"Employee Work Progress: {int(completion_pct)}%",
            subtitle=f"{completed_tasks} of {total_tasks} assigned tasks completed. Real-time workflow milestone and process deliverables tracking.",
            badge_text=badge_status,
            badge_type=badge_type,
        )

        # Dynamic overall progress bar
        ov_bar_color = "linear-gradient(90deg, #00D2FF 0%, #0072FF 50%, #10B981 100%)" if completion_pct >= 50 else "linear-gradient(90deg, #FF2A75 0%, #FF5252 100%)"
        ov_glow = "box-shadow: 0 0 14px rgba(0, 210, 255, 0.55);" if completion_pct >= 50 else "box-shadow: 0 0 14px rgba(255, 42, 117, 0.55);"

        render_html(f"""<div style="margin: 0.35rem 0 0.85rem 0;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
<span style="font-size: 15px; font-weight: 700; color: #CBD5E1;">Overall Work Completion Rate</span>
<span style="font-size: 15px; font-weight: 800; color: {'#10B981' if completion_pct >= 60 else '#00D2FF'};">{completion_pct}%</span>
</div>
<div style="height: 10px; background: #121624; border-radius: 9999px; overflow: hidden; border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: inset 0 2px 4px rgba(0,0,0,0.5);">
<div style="height: 100%; border-radius: 9999px; width: {completion_pct}%; background: {ov_bar_color}; {ov_glow} transition: width 0.4s ease;"></div>
</div>
</div>
<hr style="margin: 0.75rem 0 0.85rem 0; border: none; border-top: 1px solid rgba(255, 255, 255, 0.08);">
<div style="font-size: 17px; font-weight: 700; color: #FFFFFF; margin-bottom: 0.75rem; display: flex; align-items: center; gap: 0.45rem;">
<span>📈</span> <span>Task Completion Summary</span>
</div>""")

        # 4 Summary Metric Cards
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)

        with col_m1:
            render_html(f"""<div style="background: #1B2032; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 0.85rem 1rem; text-align: center; box-shadow: 0 4px 14px rgba(0,0,0,0.35);">
<div style="font-size: 13px; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em;">Total Tasks</div>
<div style="font-size: 26px; font-weight: 800; color: #FFFFFF; margin-top: 0.25rem;">📋 {total_tasks}</div>
<div style="font-size: 12px; color: #CBD5E1; margin-top: 0.2rem;">All Assigned</div>
</div>""")

        with col_m2:
            render_html(f"""<div style="background: #1B2032; border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; padding: 0.85rem 1rem; text-align: center; box-shadow: 0 4px 14px rgba(0,0,0,0.35);">
<div style="font-size: 13px; font-weight: 700; color: #10B981; text-transform: uppercase; letter-spacing: 0.05em;">Completed</div>
<div style="font-size: 26px; font-weight: 800; color: #10B981; margin-top: 0.25rem;">✅ {completed_tasks}</div>
<div style="font-size: 12px; color: #CBD5E1; margin-top: 0.2rem;">Delivered & Verified</div>
</div>""")

        with col_m3:
            render_html(f"""<div style="background: #1B2032; border: 1px solid rgba(0, 210, 255, 0.3); border-radius: 12px; padding: 0.85rem 1rem; text-align: center; box-shadow: 0 4px 14px rgba(0,0,0,0.35);">
<div style="font-size: 13px; font-weight: 700; color: #00D2FF; text-transform: uppercase; letter-spacing: 0.05em;">In Progress</div>
<div style="font-size: 26px; font-weight: 800; color: #00D2FF; margin-top: 0.25rem;">⏳ {in_prog_tasks}</div>
<div style="font-size: 12px; color: #CBD5E1; margin-top: 0.2rem;">Active Work-in-Progress</div>
</div>""")

        with col_m4:
            render_html(f"""<div style="background: #1B2032; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 0.85rem 1rem; text-align: center; box-shadow: 0 4px 14px rgba(0,0,0,0.35);">
<div style="font-size: 13px; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em;">Yet to Complete</div>
<div style="font-size: 26px; font-weight: 800; color: #CBD5E1; margin-top: 0.25rem;">⚪ {pending_tasks}</div>
<div style="font-size: 12px; color: #94A3B8; margin-top: 0.2rem;">Not Started / Pending</div>
</div>""")

    render_html("""<div style="height: 12px;"></div>""")

    # =========================================================================
    # VIEW MODE VS. EDIT MODE
    # =========================================================================
    if not st.session_state["is_editing_profile"]:

        # =====================================================================
        # SECTION A – EMPLOYEE DETAILS
        # =====================================================================
        with st.container(border=True):
            render_section_header(
                title="Section A: Employee Details",
                subtitle="Organizational position, reporting hierarchy, and official workstation details.",
            )
            col_a1, col_a2, col_a3 = st.columns(3)

            emp_code = work_details.get("employee_id_code") or f"EMP-{uid:04d}"
            dept_val = work_details.get("department") or "Platform Engineering & Infrastructure"
            rep_mgr = work_details.get("reporting_manager") or "Marcus Vance (VP, Platform Engineering)"
            join_dt = work_details.get("joining_date") or "2022-03-15"
            loc_val = work_details.get("work_location") or "Austin, TX (Hybrid)"

            with col_a1:
                render_html(f"""<div style="line-height: 1.65; font-size: 16px;">
<div>🆔 <strong style="color: #FFFFFF;">Employee ID:</strong><br><span style="color: #00D2FF; font-weight: 700; font-size: 16px;">{emp_code}</span></div>
<div style="margin-top: 0.6rem;">👤 <strong style="color: #FFFFFF;">Employee Name:</strong><br><span style="color: #E2E8F0; font-size: 16px;">{user_name}</span></div>
</div>""")

            with col_a2:
                render_html(f"""<div style="line-height: 1.65; font-size: 16px;">
<div>💼 <strong style="color: #FFFFFF;">Designation:</strong><br><span style="color: #E2E8F0; font-size: 16px;">{designation}</span></div>
<div style="margin-top: 0.6rem;">🏢 <strong style="color: #FFFFFF;">Department:</strong><br><span style="color: #E2E8F0; font-size: 16px;">{dept_val}</span></div>
</div>""")

            with col_a3:
                render_html(f"""<div style="line-height: 1.65; font-size: 16px;">
<div>👔 <strong style="color: #FFFFFF;">Reporting Manager:</strong><br><span style="color: #00D2FF; font-weight: 600; font-size: 16px;">{rep_mgr}</span></div>
<div style="margin-top: 0.6rem;">📅 <strong style="color: #FFFFFF;">Joining Date:</strong><br><span style="color: #E2E8F0; font-size: 16px;">{join_dt}</span></div>
<div style="margin-top: 0.6rem;">📍 <strong style="color: #FFFFFF;">Work Location:</strong><br><span style="color: #E2E8F0; font-size: 16px;">{loc_val}</span></div>
</div>""")

        render_html("""<div style="height: 12px;"></div>""")

        # =====================================================================
        # SECTION B – PROCESS & GOALS
        # =====================================================================
        with st.container(border=True):
            render_section_header(
                title="Section B: Process & Goals",
                subtitle="Assigned business process, operational duties, short-term and long-term milestones.",
            )

            p_name = work_details.get("process_name") or "Cloud Infrastructure Modernization & Kubernetes GitOps"
            p_desc = work_details.get("process_description") or "Architecting and migrating multi-region Kubernetes clusters to GitOps workflows with automated security compliance and disaster recovery."
            resp = work_details.get("assigned_responsibilities") or "• Lead migration of core cluster orchestration to ArgoCD\n• Enforce zero-trust IAM policies across EKS workloads\n• Mentor junior DevOps engineers on Terraform modules\n• Maintain 99.95% cluster availability SLAs"
            st_goals = work_details.get("short_term_goals") or "• Finalize ArgoCD automated blue/green canary rollouts\n• Reduce CI/CD deployment cycle times by 30%\n• Implement automated daily Terraform drift detection"
            lt_goals = work_details.get("long_term_goals") or "• Achieve ISO-27001 compliance for all platform infrastructure\n• Transition core workloads to multi-cloud active-active architecture\n• Establish self-service developer platform portal"
            deliv = work_details.get("expected_deliverables") or "1. Multi-cluster GitOps orchestration blueprint\n2. Real-time Prometheus/Grafana infrastructure alerting dashboards\n3. Zero-downtime rollback automation runbook"
            target_dt = work_details.get("target_completion_date") or "2026-12-15"

            # Top process headline banner
            render_html(f"""<div style="background: #141826; border: 1px solid rgba(0, 210, 255, 0.25); border-left: 4px solid #00D2FF; border-radius: 12px; padding: 1.15rem 1.35rem; margin-bottom: 1rem; box-shadow: 0 4px 16px rgba(0,0,0,0.35);">
<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.4rem;">
<div style="font-size: 20px; font-weight: 800; color: #FFFFFF;">⚙️ Current Process: {p_name}</div>
<span class="ts-badge ts-badge-teal" style="font-size: 14px;">🎯 Target Completion: {target_dt}</span>
</div>
<div style="font-size: 16px; color: #CBD5E1; line-height: 1.6;">
<strong style="color: #FFFFFF;">Process Description:</strong> {p_desc}
</div>
</div>""")

            col_b1, col_b2 = st.columns(2)

            with col_b1:
                render_html("""<div style="background: #1B2032; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 1.15rem 1.25rem; margin-bottom: 0.85rem; height: 100%;">
<div style="font-size: 17px; font-weight: 700; color: #00D2FF; margin-bottom: 0.6rem;">📋 Assigned Responsibilities</div>""")
                for line in resp.strip().splitlines():
                    if line.strip():
                        render_html(f"<div style='font-size: 15.5px; color: #E2E8F0; margin-bottom: 0.35rem; line-height: 1.5;'>{line}</div>")
                render_html("""<div style="height: 12px;"></div>
<div style="font-size: 17px; font-weight: 700; color: #10B981; margin-bottom: 0.6rem;">📦 Expected Deliverables</div>""")
                for line in deliv.strip().splitlines():
                    if line.strip():
                        render_html(f"<div style='font-size: 15.5px; color: #CBD5E1; margin-bottom: 0.35rem; line-height: 1.5;'>{line}</div>")
                render_html("</div>")

            with col_b2:
                render_html("""<div style="background: #1B2032; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 1.15rem 1.25rem; margin-bottom: 0.85rem; height: 100%;">
<div style="font-size: 17px; font-weight: 700; color: #00D2FF; margin-bottom: 0.6rem;">🎯 Short-term Goals</div>""")
                for line in st_goals.strip().splitlines():
                    if line.strip():
                        render_html(f"<div style='font-size: 15.5px; color: #E2E8F0; margin-bottom: 0.35rem; line-height: 1.5;'>{line}</div>")
                render_html("""<div style="height: 12px;"></div>
<div style="font-size: 17px; font-weight: 700; color: #A855F7; margin-bottom: 0.6rem;">🔭 Long-term Goals</div>""")
                for line in lt_goals.strip().splitlines():
                    if line.strip():
                        render_html(f"<div style='font-size: 15.5px; color: #CBD5E1; margin-bottom: 0.35rem; line-height: 1.5;'>{line}</div>")
                render_html("</div>")

        render_html("""<div style="height: 12px;"></div>""")

        # =====================================================================
        # SECTION C – TASK MANAGEMENT
        # =====================================================================
        with st.container(border=True):
            render_section_header(
                title="Section C: Task Management",
                subtitle="Centralized task board categorized by lifecycle stage: Completed, In Progress, and Yet to Complete.",
                badge_text=f"{total_tasks} Total Tasks",
                badge_type="teal",
            )

            # Quick Task Creation Expander
            with st.expander("➕ Add New Task", expanded=False):
                with st.form(key="form_add_task", clear_on_submit=True):
                    st.markdown("<div style='font-size: 16px; font-weight: 700; color: #FFFFFF; margin-bottom: 0.4rem;'>Create a New Task Record</div>", unsafe_allow_html=True)
                    c_t1, c_t2 = st.columns([2.5, 1.5])
                    with c_t1:
                        new_task_title = st.text_input("Task Name *", placeholder="e.g. Implement Prometheus alerting rules", key="new_task_title_in")
                    with c_t2:
                        new_task_status = st.selectbox("Initial Status", options=["Not Started", "In Progress", "Completed"], index=0, key="new_task_status_in")

                    new_task_desc = st.text_area("Task Description", placeholder="Outline task scope, technical deliverables, and outcomes...", height=75, key="new_task_desc_in")

                    c_t3, c_t4, c_t5 = st.columns(3)
                    with c_t3:
                        new_task_prio = st.selectbox("Priority", options=["High", "Medium", "Low"], index=1, key="new_task_prio_in")
                    with c_t4:
                        new_task_due = st.date_input("Deadline / Due Date", value=date.today(), key="new_task_due_in")
                    with c_t5:
                        new_task_prog = st.slider("Initial Progress %", min_value=0, max_value=100, value=0 if new_task_status == "Not Started" else (100 if new_task_status == "Completed" else 25), step=5, key="new_task_prog_in")

                    new_task_remarks = st.text_input("Remarks / Notes (Optional)", placeholder="e.g. Awaiting review, blocked by dependency...", key="new_task_rem_in")

                    submitted = st.form_submit_button("✅ Create Task", type="primary", use_container_width=True)
                    if submitted:
                        if not new_task_title.strip():
                            st.error("Task Name cannot be blank.")
                        else:
                            remarks_col = "completion_remarks" if new_task_status == "Completed" else ("work_remarks" if new_task_status == "In Progress" else "pending_reason")
                            task_payload = {
                                "title": new_task_title.strip(),
                                "description": new_task_desc.strip(),
                                "status": new_task_status,
                                "priority": new_task_prio,
                                "due_date": new_task_due.isoformat() if new_task_due else "",
                                "progress_percent": new_task_prog,
                                remarks_col: new_task_remarks.strip(),
                            }
                            services.core.add_employee_task(uid, task_payload)
                            st.toast("Task created successfully!", icon="✅")
                            st.rerun()

            render_html("""<div style="height: 10px;"></div>""")

            # Filter / Tab categorization
            completed_list = [t for t in tasks if t.get("status") == "Completed"]
            in_prog_list = [t for t in tasks if t.get("status") == "In Progress"]
            pending_list = [t for t in tasks if t.get("status") == "Not Started"]

            tab_in_prog, tab_pending, tab_completed, tab_all = st.tabs([
                f"⏳ In Progress ({len(in_prog_list)})",
                f"⚪ Yet to Complete ({len(pending_list)})",
                f"✅ Completed ({len(completed_list)})",
                f"📋 All Tasks ({total_tasks})",
            ])

            # -----------------------------------------------------------------
            # 1. IN PROGRESS TAB
            # Required: Task Name, Current Progress Percentage, Deadline, Work Remarks
            # -----------------------------------------------------------------
            with tab_in_prog:
                if not in_prog_list:
                    st.info("No tasks currently in progress. Kick off a task from 'Yet to Complete' or create a new one.")
                else:
                    for task in in_prog_list:
                        tid = task["id"]
                        title = task["title"]
                        prog = task.get("progress_percent", 50)
                        deadline = task.get("due_date") or "Not set"
                        work_remarks = task.get("work_remarks") or task.get("description") or "Active development in progress."

                        render_html(f"""<div style="background: #172338; border: 1px solid rgba(0, 210, 255, 0.35); border-left: 4px solid #00D2FF; border-radius: 12px; padding: 1.15rem 1.25rem; margin-bottom: 0.85rem; box-shadow: 0 4px 14px rgba(0,0,0,0.35);">
<div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 0.4rem; margin-bottom: 0.4rem;">
<div>
<div style="font-size: 19px; font-weight: 700; color: #FFFFFF;">⏳ {title}</div>
<div style="font-size: 14px; color: #94A3B8; margin-top: 0.2rem;">
Priority: <strong style="color: {'#FF2A75' if task.get('priority')=='High' else ('#FF9900' if task.get('priority')=='Medium' else '#00D2FF')};">{task.get('priority', 'Medium')}</strong> · Deadline: <strong style="color: #00D2FF;">{deadline}</strong>
</div>
</div>
<span class="ts-badge ts-badge-teal" style="font-size: 14px;">In Progress</span>
</div>
<div style="font-size: 15.5px; color: #CBD5E1; line-height: 1.55; margin-bottom: 0.65rem;">
<strong style="color: #FFFFFF;">Work Remarks:</strong> {work_remarks}
</div>
<div style="margin-top: 0.4rem; margin-bottom: 0.25rem;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
<span style="font-size: 14px; font-weight: 600; color: #CBD5E1;">Task Progress</span>
<span style="font-size: 15px; font-weight: 800; color: #00D2FF;">{prog}%</span>
</div>
<div style="height: 7px; background: #121624; border-radius: 9999px; overflow: hidden; border: 1px solid rgba(255, 255, 255, 0.08);">
<div style="height: 100%; border-radius: 9999px; width: {prog}%; background: linear-gradient(90deg, #00D2FF 0%, #0072FF 100%); box-shadow: 0 0 10px rgba(0, 210, 255, 0.45); transition: width 0.35s ease;"></div>
</div>
</div>
</div>""")

                        # Interactive quick actions
                        col_act1, col_act2, col_act3, col_act4 = st.columns([1.5, 1.8, 1.2, 1.2])
                        with col_act1:
                            def _make_status_cb(t_id: int, key_name: str):
                                def _cb():
                                    val = st.session_state.get(key_name)
                                    if val:
                                        services.core.update_task_status(t_id, uid, val)
                                return _cb

                            sel_key = f"task_status_sel_{tid}"
                            st.selectbox(
                                "Move Status",
                                options=["In Progress", "Completed", "Not Started"],
                                index=0,
                                key=sel_key,
                                on_change=_make_status_cb(tid, sel_key),
                                label_visibility="collapsed",
                            )
                        with col_act2:
                            def _make_prog_cb(t_id: int, key_name: str):
                                def _cb():
                                    new_p = st.session_state.get(key_name)
                                    if new_p is not None:
                                        services.core.update_employee_task(t_id, uid, {"progress_percent": new_p})
                                return _cb

                            prog_key = f"task_prog_slider_{tid}"
                            st.slider(
                                "Update %",
                                min_value=0,
                                max_value=100,
                                value=prog,
                                step=5,
                                key=prog_key,
                                on_change=_make_prog_cb(tid, prog_key),
                                label_visibility="collapsed",
                            )
                        with col_act3:
                            with st.popover("✏️ Edit"):
                                with st.form(key=f"form_edit_task_{tid}"):
                                    e_title = st.text_input("Title", value=title)
                                    e_desc = st.text_area("Remarks / Description", value=work_remarks)
                                    e_due = st.text_input("Deadline", value=deadline)
                                    e_prio = st.selectbox("Priority", options=["High", "Medium", "Low"], index=["High", "Medium", "Low"].index(task.get("priority", "Medium")))
                                    if st.form_submit_button("Save Edits"):
                                        services.core.update_employee_task(tid, uid, {
                                            "title": e_title,
                                            "work_remarks": e_desc,
                                            "due_date": e_due,
                                            "priority": e_prio,
                                        })
                                        st.toast("Task updated!", icon="✅")
                                        st.rerun()
                        with col_act4:
                            with st.popover("🗑️ Delete"):
                                st.write(f"Delete **'{title}'**?")
                                if st.button("Confirm Delete", type="primary", key=f"btn_confirm_del_{tid}"):
                                    services.core.delete_employee_task(tid, uid)
                                    st.toast("Task deleted.", icon="🗑️")
                                    st.rerun()

                        render_html("""<div style="height: 6px;"></div>""")

            # -----------------------------------------------------------------
            # 2. YET TO COMPLETE (Not Started) TAB
            # Required: Task Name, Priority (High / Medium / Low), Due Date, Reason for Pending
            # -----------------------------------------------------------------
            with tab_pending:
                if not pending_list:
                    st.info("No pending tasks! All items have been initiated or completed.")
                else:
                    for task in pending_list:
                        tid = task["id"]
                        title = task["title"]
                        prio = task.get("priority", "Medium")
                        due_date = task.get("due_date") or "Not set"
                        p_reason = task.get("pending_reason") or task.get("description") or "Scheduled for upcoming sprint allocation."
                        prio_col = "#FF2A75" if prio == "High" else ("#FF9900" if prio == "Medium" else "#00D2FF")

                        render_html(f"""<div style="background: #1B2032; border: 1px solid rgba(255, 255, 255, 0.08); border-left: 4px solid {prio_col}; border-radius: 12px; padding: 1.15rem 1.25rem; margin-bottom: 0.85rem; box-shadow: 0 4px 14px rgba(0,0,0,0.35);">
<div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 0.4rem; margin-bottom: 0.4rem;">
<div>
<div style="font-size: 19px; font-weight: 700; color: #FFFFFF;">⚪ {title}</div>
<div style="font-size: 14px; color: #94A3B8; margin-top: 0.2rem;">
Due Date: <strong style="color: #00D2FF;">{due_date}</strong>
</div>
</div>
<span class="ts-badge ts-badge-{'pink' if prio=='High' else ('warning' if prio=='Medium' else 'navy')}" style="font-size: 14px;">Priority: {prio}</span>
</div>
<div style="font-size: 15.5px; color: #CBD5E1; line-height: 1.55;">
<strong style="color: #FFFFFF;">Reason for Pending:</strong> {p_reason}
</div>
</div>""")

                        col_act1, col_act2, col_act3 = st.columns([2, 1.2, 1.2])
                        with col_act1:
                            def _make_pend_status_cb(t_id: int, key_name: str):
                                def _cb():
                                    val = st.session_state.get(key_name)
                                    if val:
                                        services.core.update_task_status(t_id, uid, val)
                                return _cb

                            sel_key_p = f"task_pend_status_sel_{tid}"
                            st.selectbox(
                                "Change Status",
                                options=["Not Started", "In Progress", "Completed"],
                                index=0,
                                key=sel_key_p,
                                on_change=_make_pend_status_cb(tid, sel_key_p),
                                label_visibility="collapsed",
                            )
                        with col_act2:
                            with st.popover("✏️ Edit"):
                                with st.form(key=f"form_edit_pend_task_{tid}"):
                                    e_title = st.text_input("Title", value=title)
                                    e_reason = st.text_area("Reason for Pending", value=p_reason)
                                    e_due = st.text_input("Due Date", value=due_date)
                                    e_prio = st.selectbox("Priority", options=["High", "Medium", "Low"], index=["High", "Medium", "Low"].index(prio))
                                    if st.form_submit_button("Save Edits"):
                                        services.core.update_employee_task(tid, uid, {
                                            "title": e_title,
                                            "pending_reason": e_reason,
                                            "due_date": e_due,
                                            "priority": e_prio,
                                        })
                                        st.toast("Task updated!", icon="✅")
                                        st.rerun()
                        with col_act3:
                            with st.popover("🗑️ Delete"):
                                st.write(f"Delete **'{title}'**?")
                                if st.button("Confirm Delete", type="primary", key=f"btn_confirm_del_p_{tid}"):
                                    services.core.delete_employee_task(tid, uid)
                                    st.toast("Task deleted.", icon="🗑️")
                                    st.rerun()

                        render_html("""<div style="height: 6px;"></div>""")

            # -----------------------------------------------------------------
            # 3. COMPLETED TAB
            # Required: Task Name, Task Description, Completion Date, Completion Remarks
            # -----------------------------------------------------------------
            with tab_completed:
                if not completed_list:
                    st.info("No completed tasks yet. Mark in-progress tasks as completed to track finished deliverables.")
                else:
                    for task in completed_list:
                        tid = task["id"]
                        title = task["title"]
                        desc = task.get("description") or "Deliverable finished and deployed."
                        comp_date = task.get("completion_date") or date.today().isoformat()
                        comp_remarks = task.get("completion_remarks") or "Verified in staging and delivered to production."

                        render_html(f"""<div style="background: #152428; border: 1px solid rgba(16, 185, 129, 0.35); border-left: 4px solid #10B981; border-radius: 12px; padding: 1.15rem 1.25rem; margin-bottom: 0.85rem; box-shadow: 0 4px 14px rgba(0,0,0,0.35);">
<div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 0.4rem; margin-bottom: 0.4rem;">
<div>
<div style="font-size: 19px; font-weight: 700; color: #FFFFFF;">✅ {title}</div>
<div style="font-size: 14px; color: #94A3B8; margin-top: 0.2rem;">
Completion Date: <strong style="color: #10B981;">{comp_date}</strong>
</div>
</div>
<span class="ts-badge ts-badge-success" style="font-size: 14px;">100% Completed</span>
</div>
<div style="font-size: 15.5px; color: #CBD5E1; line-height: 1.55; margin-bottom: 0.45rem;">
<strong style="color: #FFFFFF;">Task Description:</strong> {desc}
</div>
<div style="font-size: 15.5px; color: #10B981; line-height: 1.55;">
<strong style="color: #FFFFFF;">Completion Remarks:</strong> {comp_remarks}
</div>
</div>""")

                        col_act1, col_act2, col_act3 = st.columns([2, 1.2, 1.2])
                        with col_act1:
                            def _make_comp_status_cb(t_id: int, key_name: str):
                                def _cb():
                                    val = st.session_state.get(key_name)
                                    if val:
                                        services.core.update_task_status(t_id, uid, val)
                                return _cb

                            sel_key_c = f"task_comp_status_sel_{tid}"
                            st.selectbox(
                                "Reopen / Change Status",
                                options=["Completed", "In Progress", "Not Started"],
                                index=0,
                                key=sel_key_c,
                                on_change=_make_comp_status_cb(tid, sel_key_c),
                                label_visibility="collapsed",
                            )
                        with col_act2:
                            with st.popover("✏️ Edit"):
                                with st.form(key=f"form_edit_comp_task_{tid}"):
                                    e_title = st.text_input("Title", value=title)
                                    e_desc = st.text_area("Description", value=desc)
                                    e_comp_dt = st.text_input("Completion Date", value=comp_date)
                                    e_remarks = st.text_area("Completion Remarks", value=comp_remarks)
                                    if st.form_submit_button("Save Edits"):
                                        services.core.update_employee_task(tid, uid, {
                                            "title": e_title,
                                            "description": e_desc,
                                            "completion_date": e_comp_dt,
                                            "completion_remarks": e_remarks,
                                        })
                                        st.toast("Task updated!", icon="✅")
                                        st.rerun()
                        with col_act3:
                            with st.popover("🗑️ Delete"):
                                st.write(f"Delete **'{title}'**?")
                                if st.button("Confirm Delete", type="primary", key=f"btn_confirm_del_c_{tid}"):
                                    services.core.delete_employee_task(tid, uid)
                                    st.toast("Task deleted.", icon="🗑️")
                                    st.rerun()

                        render_html("""<div style="height: 6px;"></div>""")

            # -----------------------------------------------------------------
            # 4. ALL TASKS OVERVIEW TAB
            # -----------------------------------------------------------------
            with tab_all:
                if not tasks:
                    st.info("No task records found. Use the 'Add New Task' form above to create one.")
                else:
                    for task in tasks:
                        st_icon = "✅" if task["status"] == "Completed" else ("⏳" if task["status"] == "In Progress" else "⚪")
                        render_html(f"""<div style="display: flex; justify-content: space-between; align-items: center; padding: 0.65rem 0.5rem; border-bottom: 1px solid rgba(255, 255, 255, 0.06);">
<div>
<div style="font-size: 16px; font-weight: 700; color: #FFFFFF;">{st_icon} {task['title']}</div>
<div style="font-size: 13.5px; color: #94A3B8; margin-top: 0.2rem;">Priority: {task.get('priority', 'Medium')} · Deadline: {task.get('due_date') or 'N/A'} · Progress: {task.get('progress_percent', 0)}%</div>
</div>
<span class="ts-badge ts-badge-{'success' if task['status']=='Completed' else ('teal' if task['status']=='In Progress' else 'navy')}" style="font-size: 13px;">{task['status']}</span>
</div>""")

        render_html("""<div style="height: 12px;"></div>""")

        # =====================================================================
        # SECTION D – CHALLENGES & SUPPORT
        # =====================================================================
        with st.container(border=True):
            render_section_header(
                title="Section D: Challenges & Support",
                subtitle="Document hurdles encountered during work execution, reasons for timeline variances, and requested management support.",
            )

            challs_val = work_details.get("challenges_faced") or "Intermittent network latency during cross-region state replication and legacy service dependencies."
            delay_val = work_details.get("reason_for_delay") or "Awaiting security review approval for IAM cross-account role delegations."
            support_val = work_details.get("support_required") or "Platform security architecture sign-off and access to staging VPC peering routes."
            mgr_val = work_details.get("manager_remarks") or "Eleanor is making outstanding technical progress. Meeting scheduled with Security Lead this Thursday to unblock IAM delegations."

            col_d1, col_d2 = st.columns(2)

            with col_d1:
                render_html(f"""<div style="background: #1B2032; border: 1px solid rgba(255, 42, 117, 0.3); border-left: 4px solid #FF2A75; border-radius: 12px; padding: 1.15rem 1.25rem; margin-bottom: 0.85rem; height: 100%;">
<div style="font-size: 17px; font-weight: 700; color: #FF2A75; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.4rem;">
<span>⚠️</span> <span>Challenges Faced</span>
</div>
<div style="font-size: 15.5px; color: #E2E8F0; line-height: 1.6;">
{challs_val}
</div>
</div>""")

            with col_d2:
                render_html(f"""<div style="background: #1B2032; border: 1px solid rgba(255, 153, 0, 0.3); border-left: 4px solid #FF9900; border-radius: 12px; padding: 1.15rem 1.25rem; margin-bottom: 0.85rem; height: 100%;">
<div style="font-size: 17px; font-weight: 700; color: #FF9900; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.4rem;">
<span>⏱️</span> <span>Reason for Delay</span>
</div>
<div style="font-size: 15.5px; color: #E2E8F0; line-height: 1.6;">
{delay_val}
</div>
</div>""")

            col_d3, col_d4 = st.columns(2)

            with col_d3:
                render_html(f"""<div style="background: #1B2032; border: 1px solid rgba(0, 210, 255, 0.3); border-left: 4px solid #00D2FF; border-radius: 12px; padding: 1.15rem 1.25rem; margin-bottom: 0.85rem; height: 100%;">
<div style="font-size: 17px; font-weight: 700; color: #00D2FF; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.4rem;">
<span>🤝</span> <span>Support Required</span>
</div>
<div style="font-size: 15.5px; color: #E2E8F0; line-height: 1.6;">
{support_val}
</div>
</div>""")

            with col_d4:
                render_html(f"""<div style="background: #1B2032; border: 1px solid rgba(16, 185, 129, 0.3); border-left: 4px solid #10B981; border-radius: 12px; padding: 1.15rem 1.25rem; margin-bottom: 0.85rem; height: 100%;">
<div style="font-size: 17px; font-weight: 700; color: #10B981; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.4rem;">
<span>💬</span> <span>Manager Remarks</span>
</div>
<div style="font-size: 15.5px; color: #E2E8F0; line-height: 1.6;">
{mgr_val}
</div>
</div>""")

            # Quick Inline Update Form for Challenges & Support
            with st.expander("✏️ Update Challenges & Support", expanded=False):
                with st.form(key="form_update_challenges"):
                    st.markdown("<div style='font-size: 15px; font-weight: 600; color: #CBD5E1;'>Record current obstacles and request manager assistance:</div>", unsafe_allow_html=True)
                    u_challs = st.text_area("Challenges Encountered", value=challs_val, height=80)
                    u_delay = st.text_area("Reason for Delay", value=delay_val, height=70)
                    u_support = st.text_area("Support / Approvals Required", value=support_val, height=70)
                    u_mgr = st.text_area("Manager Guidance / Remarks", value=mgr_val, height=70)

                    if st.form_submit_button("💾 Save Challenges & Support", type="primary", use_container_width=True):
                        services.core.save_employee_work_details(uid, {
                            "challenges_faced": u_challs.strip(),
                            "reason_for_delay": u_delay.strip(),
                            "support_required": u_support.strip(),
                            "manager_remarks": u_mgr.strip(),
                        })
                        st.toast("Challenges and support record updated!", icon="✅")
                        st.rerun()

        render_html("""<div style="height: 12px;"></div>""")

        # =====================================================================
        # SECTION E – OVERALL WORK PROGRESS
        # =====================================================================
        with st.container(border=True):
            render_section_header(
                title="Section E: Overall Work Progress",
                subtitle="Comprehensive task allocation analysis, progress formula calculation, and upcoming milestones schedule.",
            )

            # High-level stats row
            c_e1, c_e2, c_e3, c_e4, c_e5 = st.columns(5)
            with c_e1:
                render_html(f"""<div style="background: #1B2032; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 0.75rem; text-align: center;">
<div style="font-size: 12px; color: #94A3B8; text-transform: uppercase; font-weight: 700;">Total Assigned</div>
<div style="font-size: 24px; font-weight: 800; color: #FFFFFF; margin-top: 0.2rem;">{total_tasks}</div>
</div>""")
            with c_e2:
                render_html(f"""<div style="background: #1B2032; border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 10px; padding: 0.75rem; text-align: center;">
<div style="font-size: 12px; color: #10B981; text-transform: uppercase; font-weight: 700;">Completed</div>
<div style="font-size: 24px; font-weight: 800; color: #10B981; margin-top: 0.2rem;">{completed_tasks}</div>
</div>""")
            with c_e3:
                render_html(f"""<div style="background: #1B2032; border: 1px solid rgba(0, 210, 255, 0.3); border-radius: 10px; padding: 0.75rem; text-align: center;">
<div style="font-size: 12px; color: #00D2FF; text-transform: uppercase; font-weight: 700;">In Progress</div>
<div style="font-size: 24px; font-weight: 800; color: #00D2FF; margin-top: 0.2rem;">{in_prog_tasks}</div>
</div>""")
            with c_e4:
                render_html(f"""<div style="background: #1B2032; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 0.75rem; text-align: center;">
<div style="font-size: 12px; color: #94A3B8; text-transform: uppercase; font-weight: 700;">Pending</div>
<div style="font-size: 24px; font-weight: 800; color: #CBD5E1; margin-top: 0.2rem;">{pending_tasks}</div>
</div>""")
            with c_e5:
                render_html(f"""<div style="background: #1B2032; border: 1px solid rgba(0, 210, 255, 0.35); border-radius: 10px; padding: 0.75rem; text-align: center;">
<div style="font-size: 12px; color: #00D2FF; text-transform: uppercase; font-weight: 700;">Completion Rate</div>
<div style="font-size: 24px; font-weight: 800; color: #00D2FF; margin-top: 0.2rem;">{completion_pct}%</div>
</div>""")

            render_html(f"""<div style="margin-top: 1rem; background: #141826; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 1.15rem 1.25rem;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem; flex-wrap: wrap;">
<span style="font-size: 16px; font-weight: 700; color: #FFFFFF;">Dynamic Progress Formula: (Completed Tasks / Total Assigned Tasks) × 100</span>
<span style="font-size: 15px; font-weight: 800; color: #00D2FF;">({completed_tasks} / {max(1, total_tasks)}) × 100 = {completion_pct}%</span>
</div>
<div style="font-size: 14px; color: #94A3B8;">Dynamically computed from actual SQLite employee task records. Zero-task division handled gracefully.</div>
</div>""")

            render_html("""<div style="margin-top: 1rem; margin-bottom: 0.5rem; font-size: 17px; font-weight: 700; color: #FFFFFF; display: flex; align-items: center; gap: 0.45rem;">
<span>🗓️</span> <span>Upcoming Milestones</span>
</div>""")

            # Upcoming Milestones List
            milestones = []
            target_proc_dt = work_details.get("target_completion_date")
            if target_proc_dt:
                milestones.append({
                    "title": f"Process Completion Target: {work_details.get('process_name', 'Current Process')}",
                    "date": target_proc_dt,
                    "type": "Process Target",
                })

            today_val = date.today()
            for t in tasks:
                if t.get("status") != "Completed" and t.get("due_date"):
                    milestones.append({
                        "title": f"Task Due: {t['title']}",
                        "date": t["due_date"],
                        "type": f"{t.get('priority', 'Medium')} Priority Task",
                    })

            # Sort milestones by date
            milestones.sort(key=lambda m: str(m.get("date", "")))

            if not milestones:
                st.info("No upcoming milestones or deadlines recorded yet. Add deadlines to tasks in Section C.")
            else:
                c_m_left, c_m_right = st.columns(2)
                for idx, m in enumerate(milestones[:6]):
                    target_c = c_m_left if idx % 2 == 0 else c_m_right
                    with target_c:
                        m_date_str = m["date"]
                        try:
                            d_obj = date.fromisoformat(m_date_str[:10])
                            diff = (d_obj - today_val).days
                            if diff < 0:
                                diff_lbl = f"<span style='color: #FF2A75; font-weight: 700;'>Overdue by {abs(diff)}d</span>"
                            elif diff == 0:
                                diff_lbl = "<span style='color: #FF9900; font-weight: 700;'>Due Today</span>"
                            else:
                                diff_lbl = f"<span style='color: #00D2FF; font-weight: 700;'>Due in {diff}d</span>"
                        except Exception:
                            diff_lbl = f"<span style='color: #CBD5E1;'>{m_date_str}</span>"

                        render_html(f"""<div style="background: #1B2032; border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 10px; padding: 0.85rem 1rem; margin-bottom: 0.6rem;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem; flex-wrap: wrap; gap: 0.35rem;">
<span style="font-size: 15.5px; font-weight: 700; color: #FFFFFF;">{m['title']}</span>
<span class="ts-badge ts-badge-navy" style="font-size: 13px;">{m['type']}</span>
</div>
<div style="font-size: 14px; color: #94A3B8; display: flex; justify-content: space-between;">
<span>📅 {m_date_str}</span>
<span>{diff_lbl}</span>
</div>
</div>""")

        render_html("""<div style="height: 16px;"></div>""")

        # =====================================================================
        # SUGGESTIONS & IMPROVEMENTS (Preserved at Bottom of Page)
        # =====================================================================
        with st.container(border=True):
            render_section_header(
                title="Suggestions & Improvements",
                subtitle="Dynamic work-related recommendations, pending task alerts, and productivity guidance derived from actual employee data.",
                badge_text="Work Process Engine",
                badge_type="teal",
            )

            # Generate dynamic work suggestions from actual tasks and goals
            suggestions = services.core.get_work_suggestions(uid, work_details, tasks)

            total_recs = len(suggestions)

            # Callback for status selectbox on_change
            def _on_rec_status_change(target_uid: int, topic_name: str, key_name: str) -> None:
                new_val = st.session_state.get(key_name)
                if new_val:
                    services.core.save_recommendation_status(target_uid, topic_name, new_val)

            normalized_items = []
            for s in suggestions:
                topic = s.get("topic") or "Recommended Improvement"
                item_key = s.get("item_key") or "rec"
                widget_key = f"rec_status_sel_{uid}_{item_key}"

                db_status = s.get("status", "Not Started")
                clean_s = (db_status or "").strip().lower()
                if clean_s in ["completed", "complete"]:
                    current_status = "Completed"
                elif clean_s in ["in progress", "in_progress"]:
                    current_status = "In Progress"
                else:
                    current_status = "Not Started"

                session_val = st.session_state.get(widget_key)
                if session_val and session_val in ["Not Started", "In Progress", "Completed"] and session_val != current_status:
                    services.core.save_recommendation_status(uid, topic, session_val)
                    current_status = session_val

                normalized_items.append({
                    "s": s,
                    "topic": topic,
                    "status": current_status,
                    "widget_key": widget_key,
                })

            not_started_cnt = sum(1 for item in normalized_items if item["status"] == "Not Started")
            in_progress_cnt = sum(1 for item in normalized_items if item["status"] == "In Progress")
            completed_cnt = sum(1 for item in normalized_items if item["status"] == "Completed")
            rec_completion_pct = round((completed_cnt / total_recs) * 100) if total_recs > 0 else 0

            # Recommendation Progress Summary Box
            render_html(f"""<div style="background: #141826; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 1.15rem 1.4rem; margin-bottom: 1.25rem; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.85rem; flex-wrap: wrap; gap: 0.5rem;">
<div style="font-size: 20px; font-weight: 700; color: #FFFFFF; display: flex; align-items: center; gap: 0.5rem;">
<span>📊</span> <span>Recommendation Progress Summary</span>
</div>
<div style="font-size: 16px; font-weight: 800; color: #00D2FF;">
Completion Rate: <span style="color: {'#10B981' if rec_completion_pct >= 80 else '#00D2FF'}; font-size: 20px;">{rec_completion_pct}%</span>
</div>
</div>
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 0.85rem; margin-bottom: 0.85rem;">
<div style="background: #1B2032; border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 10px; padding: 0.75rem 0.95rem; text-align: center;">
<div style="font-size: 14px; color: #94A3B8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em;">Total Recommendations</div>
<div style="font-size: 24px; font-weight: 800; color: #FFFFFF; margin-top: 0.2rem;">{total_recs}</div>
</div>
<div style="background: #1B2032; border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 10px; padding: 0.75rem 0.95rem; text-align: center;">
<div style="font-size: 14px; color: #94A3B8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em;">Not Started</div>
<div style="font-size: 24px; font-weight: 800; color: #94A3B8; margin-top: 0.2rem;">⚪ {not_started_cnt}</div>
</div>
<div style="background: #1B2032; border: 1px solid rgba(0, 210, 255, 0.25); border-radius: 10px; padding: 0.75rem 0.95rem; text-align: center;">
<div style="font-size: 14px; color: #00D2FF; text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em;">In Progress</div>
<div style="font-size: 24px; font-weight: 800; color: #00D2FF; margin-top: 0.2rem;">⏳ {in_progress_cnt}</div>
</div>
<div style="background: #1B2032; border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 10px; padding: 0.75rem 0.95rem; text-align: center;">
<div style="font-size: 14px; color: #10B981; text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em;">Completed</div>
<div style="font-size: 24px; font-weight: 800; color: #10B981; margin-top: 0.2rem;">✅ {completed_cnt}</div>
</div>
</div>
</div>""")

            render_progress_bar("Overall Progress", rec_completion_pct, color_scheme="cyan" if rec_completion_pct >= 50 else "pink")
            render_html("""<div style="height: 14px;"></div>""")

            # 2-column Recommendation Cards
            col_sug1, col_sug2 = st.columns(2)
            for idx, item in enumerate(normalized_items):
                s = item["s"]
                topic = item["topic"]
                current_status = item["status"]
                widget_key = item["widget_key"]

                action_text = s.get("action") or "Recommendation action available."
                prio = s.get("priority", "Medium")
                cat = s.get("category", "Work Process")

                prio_color = "#FF2A75" if prio == "High" else ("#FF9900" if prio == "Medium" else "#00D2FF")

                if current_status == "Completed":
                    topic_pct = 100
                    topic_bar_fill = "linear-gradient(90deg, #10B981 0%, #00D2FF 100%)"
                    topic_glow = "box-shadow: 0 0 10px rgba(16, 185, 129, 0.45);"
                    topic_pct_col = "#10B981"
                    accent_color = "#10B981"
                    card_bg = "#152428"
                    card_border = "1px solid rgba(16, 185, 129, 0.35)"
                    status_badge = '<span class="ts-badge ts-badge-success" style="font-weight: 700; font-size: 14px;">✅ Completed</span>'
                    status_icon = "✅"
                elif current_status == "In Progress":
                    topic_pct = 50
                    topic_bar_fill = "linear-gradient(90deg, #00D2FF 0%, #0072FF 100%)"
                    topic_glow = "box-shadow: 0 0 10px rgba(0, 210, 255, 0.45);"
                    topic_pct_col = "#00D2FF"
                    accent_color = "#00D2FF"
                    card_bg = "#172338"
                    card_border = "1px solid rgba(0, 210, 255, 0.35)"
                    status_badge = '<span class="ts-badge ts-badge-teal" style="font-weight: 700; font-size: 14px;">⏳ In Progress</span>'
                    status_icon = "⏳"
                else:
                    topic_pct = 0
                    topic_bar_fill = "transparent"
                    topic_glow = ""
                    topic_pct_col = "#94A3B8"
                    accent_color = prio_color
                    card_bg = "#1B2032"
                    card_border = "1px solid rgba(255, 255, 255, 0.08)"
                    status_badge = '<span class="ts-badge ts-badge-navy" style="font-weight: 600; font-size: 14px; color: #94A3B8;">⚪ Not Started</span>'
                    status_icon = "⚪"

                target_col = col_sug1 if idx % 2 == 0 else col_sug2
                with target_col:
                    with st.container(border=True):
                        render_html(f"""<div style="background: {card_bg}; border: {card_border}; border-left: 4px solid {accent_color}; border-radius: 12px; padding: 1.15rem 1.25rem; margin-bottom: 0.65rem; box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35);">
<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem; flex-wrap: wrap; gap: 0.4rem;">
<div>
<div style="font-size: 20px; font-weight: 800; color: #FFFFFF; display: flex; align-items: center; gap: 0.45rem;">
<span>{status_icon}</span> <span>{topic}</span>
</div>
<div style="font-size: 14px; color: #94A3B8; margin-top: 0.25rem;">
<span style="color: #00D2FF; font-weight: 600;">{cat}</span> · Priority: <strong style="color: {prio_color};">{prio}</strong>
</div>
</div>
<div>
{status_badge}
</div>
</div>
<div style="font-size: 16px; color: #E2E8F0; line-height: 1.55; margin-bottom: 0.75rem;">
<strong style="color: #CBD5E1;">Recommendation:</strong> {action_text}
</div>
<div style="margin-top: 0.65rem; margin-bottom: 0.3rem;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
<span style="font-size: 14px; font-weight: 600; color: #CBD5E1;">Progress</span>
<span style="font-size: 15px; font-weight: 800; color: {topic_pct_col};">{topic_pct}%</span>
</div>
<div style="height: 8px; background: #121624; border-radius: 9999px; overflow: hidden; border: 1px solid rgba(255, 255, 255, 0.08);">
<div style="height: 100%; border-radius: 9999px; width: {topic_pct}%; background: {topic_bar_fill}; {topic_glow} transition: width 0.35s ease;"></div>
</div>
</div>
</div>""")

                        c_sl_lbl, c_sl_val = st.columns([1.1, 2.9])
                        with c_sl_lbl:
                            st.markdown("<div style='font-size: 15px; font-weight: 700; color: #CBD5E1; padding-top: 0.4rem;'>Track Status:</div>", unsafe_allow_html=True)
                        with c_sl_val:
                            status_opts = ["Not Started", "In Progress", "Completed"]
                            current_idx = status_opts.index(current_status) if current_status in status_opts else 0
                            st.selectbox(
                                f"Status for {topic}",
                                options=status_opts,
                                index=current_idx,
                                key=widget_key,
                                on_change=_on_rec_status_change,
                                args=(uid, topic, widget_key),
                                label_visibility="collapsed",
                            )

    else:
        # =====================================================================
        # EDIT MODE: WORK PROCESS & GOALS PROFILE EDITOR
        # =====================================================================
        draft = st.session_state.get("work_profile_draft", {})

        with st.container(border=True):
            render_section_header(
                title="Edit Employee Work Profile",
                subtitle="Update organizational positioning, assigned process, goals, and delivery challenges. Changes persist immediately to SQLite upon saving.",
                badge_text="Live Work Profile Editor",
                badge_type="warning",
            )

            c_save_btn, c_cancel_btn, _ = st.columns([1.2, 1.2, 3.6])
            with c_save_btn:
                save_clicked = st.button("💾 Save Changes", type="primary", use_container_width=True, key="btn_save_profile_main")
            with c_cancel_btn:
                cancel_clicked = st.button("✖️ Cancel", type="secondary", use_container_width=True, key="btn_cancel_profile_main")

            # Check save trigger
            if save_clicked or st.session_state.pop("trigger_profile_save", False):
                val_name = draft.get("name", "").strip()
                if not val_name:
                    st.error("Validation Error: Employee Name cannot be empty.")
                else:
                    services.core.update_user_account(uid, val_name)
                    work_payload = {
                        "employee_id_code": draft.get("employee_id_code", "").strip(),
                        "designation": draft.get("designation", "").strip(),
                        "department": draft.get("department", "").strip(),
                        "reporting_manager": draft.get("reporting_manager", "").strip(),
                        "joining_date": draft.get("joining_date", "").strip(),
                        "work_location": draft.get("work_location", "").strip(),
                        "process_name": draft.get("process_name", "").strip(),
                        "process_description": draft.get("process_description", "").strip(),
                        "assigned_responsibilities": draft.get("assigned_responsibilities", "").strip(),
                        "short_term_goals": draft.get("short_term_goals", "").strip(),
                        "long_term_goals": draft.get("long_term_goals", "").strip(),
                        "expected_deliverables": draft.get("expected_deliverables", "").strip(),
                        "target_completion_date": draft.get("target_completion_date", "").strip(),
                        "challenges_faced": draft.get("challenges_faced", "").strip(),
                        "reason_for_delay": draft.get("reason_for_delay", "").strip(),
                        "support_required": draft.get("support_required", "").strip(),
                        "manager_remarks": draft.get("manager_remarks", "").strip(),
                    }
                    services.core.save_employee_work_details(uid, work_payload)

                    # Update session employee dict if present
                    if "employee" not in st.session_state:
                        st.session_state["employee"] = {}
                    st.session_state["employee"]["name"] = val_name
                    st.session_state["employee"]["job_title"] = work_payload["designation"]
                    st.session_state["employee"]["department"] = work_payload["department"]
                    st.session_state["employee"]["location"] = work_payload["work_location"]

                    name_p = val_name.split()
                    st.session_state["employee"]["avatar_initials"] = "".join([p[0].upper() for p in name_p[:2]]) if name_p else "EV"

                    st.session_state["is_editing_profile"] = False
                    st.session_state.pop("work_profile_draft", None)
                    st.toast("Employee work profile saved successfully!", icon="✅")
                    st.rerun()

            if cancel_clicked:
                st.session_state.pop("work_profile_draft", None)
                st.session_state["is_editing_profile"] = False
                st.toast("Edits discarded.", icon="ℹ️")
                st.rerun()

            render_html("""<div style="height: 10px;"></div>""")

            # Edit Mode Tabs
            tab_e_emp, tab_e_proc, tab_e_chall = st.tabs([
                "👤 Employee Details",
                "🎯 Process & Goals",
                "⚠️ Challenges & Support",
            ])

            # EDIT TAB 1: EMPLOYEE DETAILS
            with tab_e_emp:
                c_e1, c_e2 = st.columns(2)
                with c_e1:
                    draft["name"] = st.text_input("Employee Name *", value=draft.get("name", ""), key="draft_name_in")
                    draft["employee_id_code"] = st.text_input("Employee ID", value=draft.get("employee_id_code", ""), key="draft_emp_id_in")
                    draft["designation"] = st.text_input("Designation / Title", value=draft.get("designation", ""), key="draft_title_in")
                with c_e2:
                    draft["department"] = st.text_input("Department", value=draft.get("department", ""), key="draft_dept_in")
                    draft["reporting_manager"] = st.text_input("Reporting Manager", value=draft.get("reporting_manager", ""), key="draft_mgr_in")
                    draft["joining_date"] = st.text_input("Joining Date (YYYY-MM-DD)", value=draft.get("joining_date", ""), key="draft_join_in")

                draft["work_location"] = st.text_input("Work Location", value=draft.get("work_location", ""), key="draft_loc_in")

            # EDIT TAB 2: PROCESS & GOALS
            with tab_e_proc:
                col_p_top1, col_p_top2 = st.columns([3, 1.5])
                with col_p_top1:
                    draft["process_name"] = st.text_input("Current Process / Project Name", value=draft.get("process_name", ""), key="draft_proc_name_in")
                with col_p_top2:
                    draft["target_completion_date"] = st.text_input("Target Completion Date (YYYY-MM-DD)", value=draft.get("target_completion_date", ""), key="draft_target_dt_in")

                draft["process_description"] = st.text_area("Process Description", value=draft.get("process_description", ""), height=100, key="draft_proc_desc_in")

                col_g_sub1, col_g_sub2 = st.columns(2)
                with col_g_sub1:
                    draft["assigned_responsibilities"] = st.text_area("Assigned Responsibilities (one per line)", value=draft.get("assigned_responsibilities", ""), height=130, key="draft_resp_in")
                    draft["expected_deliverables"] = st.text_area("Expected Deliverables (one per line)", value=draft.get("expected_deliverables", ""), height=120, key="draft_deliv_in")
                with col_g_sub2:
                    draft["short_term_goals"] = st.text_area("Short-term Goals (one per line)", value=draft.get("short_term_goals", ""), height=130, key="draft_st_goals_in")
                    draft["long_term_goals"] = st.text_area("Long-term Goals (one per line)", value=draft.get("long_term_goals", ""), height=120, key="draft_lt_goals_in")

            # EDIT TAB 3: CHALLENGES & SUPPORT
            with tab_e_chall:
                draft["challenges_faced"] = st.text_area("Challenges Faced", value=draft.get("challenges_faced", ""), height=100, key="draft_challs_in")
                draft["reason_for_delay"] = st.text_area("Reason for Delay", value=draft.get("reason_for_delay", ""), height=80, key="draft_delay_in")
                draft["support_required"] = st.text_area("Support Required", value=draft.get("support_required", ""), height=80, key="draft_supp_in")
                draft["manager_remarks"] = st.text_area("Manager Remarks", value=draft.get("manager_remarks", ""), height=80, key="draft_mgr_rem_in")
