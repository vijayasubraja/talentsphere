"""Acceptance test suite for Employee Work Process, Goals and Task Progress Tracking Module.

Explicitly verifies all 11 testing requirements:
1. Employee details are displayed correctly.
2. Process and goals can be added and edited.
3. New tasks can be created.
4. Tasks can be moved between Not Started, In Progress and Completed.
5. Completed, In Progress and Pending counts update automatically.
6. Completion percentage is calculated correctly (Formula: (Completed / Total) * 100, zero-division handled).
7. Progress survives logout and login.
8. Different employees cannot access each other's tasks (data isolation).
9. Suggestions update dynamically based on work progress.
10. Resume Builder still works with its existing information.
11. No existing navigation or unrelated application functionality is broken.
"""

from pathlib import Path
import uuid
import pytest
from streamlit.testing.v1 import AppTest
import services.core

APP_PATH = str(Path(__file__).parent.parent / "app.py")


def test_req_1_employee_details_displayed_correctly():
    """Requirement 1: Verify Employee details (ID, Name, Designation, Department, Reporting Manager, Joining Date, Work Location) are displayed."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = 1
    at.session_state["current_page"] = "Employee Profile"
    at.run()
    assert not at.exception

    all_html = " ".join([m.value for m in at.html])

    # Verify Section A exists
    assert "Section A: Employee Details" in all_html
    assert "Employee ID:" in all_html
    assert "Employee Name:" in all_html
    assert "Designation:" in all_html
    assert "Department:" in all_html
    assert "Reporting Manager:" in all_html
    assert "Joining Date:" in all_html
    assert "Work Location:" in all_html

    # Check Eleanor Vance details
    assert "Eleanor Vance" in all_html
    assert "EMP-10482" in all_html or "EMP-" in all_html
    assert "Marcus Vance" in all_html


def test_req_2_process_and_goals_added_and_edited():
    """Requirement 2: Process and goals can be added and edited, and persist to database."""
    unique_email = f"work-proc-{uuid.uuid4().hex[:8]}@example.com"
    services.core.register("Process Owner", unique_email, "SecurePassword123")
    user = services.core.login(unique_email, "SecurePassword123")
    uid = user["id"]

    new_work_data = {
        "employee_id_code": "EMP-9901",
        "designation": "Staff Cloud Architect",
        "department": "Infrastructure Strategy",
        "reporting_manager": "Sarah Connor (VP Infrastructure)",
        "joining_date": "2023-01-15",
        "work_location": "New York, NY",
        "process_name": "NextGen Multi-Cloud Kubernetes Fabric",
        "process_description": "Designing automated global mesh deployment.",
        "assigned_responsibilities": "• Lead multi-cloud mesh design\n• Review security architecture",
        "short_term_goals": "• Deploy staging cluster in AWS & Azure\n• Benchmark ingress latency",
        "long_term_goals": "• Complete active-active global failover\n• Reduce infra TCO by 25%",
        "expected_deliverables": "1. Multi-cloud architecture specification\n2. Automated failover test suite",
        "target_completion_date": "2027-01-31",
    }
    services.core.save_employee_work_details(uid, new_work_data)

    # Reload from database
    loaded = services.core.get_employee_work_details(uid)
    assert loaded["process_name"] == "NextGen Multi-Cloud Kubernetes Fabric"
    assert loaded["target_completion_date"] == "2027-01-31"
    assert "multi-cloud mesh design" in loaded["assigned_responsibilities"].lower()
    assert loaded["employee_id_code"] == "EMP-9901"

    # Verify rendering via AppTest
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["is_authenticated"] = True
    at.session_state["user_id"] = uid
    at.session_state["current_page"] = "Employee Profile"
    at.run()
    assert not at.exception

    html = " ".join([m.value for m in at.html])
    assert "NextGen Multi-Cloud Kubernetes Fabric" in html
    assert "2027-01-31" in html
    assert "Sarah Connor" in html


def test_req_3_new_tasks_can_be_created():
    """Requirement 3: Verify new tasks can be created and stored in SQLite."""
    unique_email = f"task-create-{uuid.uuid4().hex[:8]}@example.com"
    services.core.register("Task Creator", unique_email, "SecurePassword123")
    user = services.core.login(unique_email, "SecurePassword123")
    uid = user["id"]

    task_id = services.core.add_employee_task(uid, {
        "title": "Establish ArgoCD Secrets Sync",
        "description": "Configure SealedSecrets controller and Key Vault integration.",
        "status": "In Progress",
        "priority": "High",
        "due_date": "2026-11-25",
        "progress_percent": 30,
        "work_remarks": "Helm chart deployed; waiting for IAM certificates.",
    })
    assert task_id > 0

    task = services.core.get_employee_task(task_id, uid)
    assert task is not None
    assert task["title"] == "Establish ArgoCD Secrets Sync"
    assert task["status"] == "In Progress"
    assert task["priority"] == "High"
    assert task["progress_percent"] == 30
    assert task["due_date"] == "2026-11-25"


def test_req_4_tasks_moved_between_statuses_without_duplicates():
    """Requirement 4: Verify tasks can be moved between Not Started, In Progress and Completed without duplicate records."""
    unique_email = f"task-status-{uuid.uuid4().hex[:8]}@example.com"
    services.core.register("Status Mover", unique_email, "SecurePassword123")
    user = services.core.login(unique_email, "SecurePassword123")
    uid = user["id"]

    tid = services.core.add_employee_task(uid, {
        "title": "Automated Canary Rollouts",
        "description": "Configure Flagger with Prometheus metrics analysis.",
        "status": "Not Started",
        "priority": "High",
        "due_date": "2026-12-01",
        "pending_reason": "Waiting on Prometheus SLI definition.",
    })

    # Initially Not Started
    tasks = services.core.get_employee_tasks(uid)
    assert len(tasks) == 1
    assert tasks[0]["status"] == "Not Started"

    # Move to In Progress
    ok = services.core.update_task_status(tid, uid, "In Progress", progress_percent=45, remarks="Configuring Flagger custom metrics.")
    assert ok
    tasks = services.core.get_employee_tasks(uid)
    assert len(tasks) == 1, "Moving status must NOT create duplicate records"
    assert tasks[0]["status"] == "In Progress"
    assert tasks[0]["progress_percent"] == 45
    assert tasks[0]["work_remarks"] == "Configuring Flagger custom metrics."

    # Move to Completed
    ok = services.core.update_task_status(tid, uid, "Completed", remarks="Canary analysis verified in staging.")
    assert ok
    tasks = services.core.get_employee_tasks(uid)
    assert len(tasks) == 1, "Moving status must NOT create duplicate records"
    assert tasks[0]["status"] == "Completed"
    assert tasks[0]["progress_percent"] == 100
    assert tasks[0]["completion_remarks"] == "Canary analysis verified in staging."
    assert tasks[0]["completion_date"] != ""

    # Move back to Not Started
    ok = services.core.update_task_status(tid, uid, "Not Started", remarks="Reopened for secondary cluster testing.")
    assert ok
    tasks = services.core.get_employee_tasks(uid)
    assert len(tasks) == 1, "Reopening status must NOT create duplicate records"
    assert tasks[0]["status"] == "Not Started"
    assert tasks[0]["progress_percent"] == 0


def test_req_5_and_6_counts_and_completion_percentage_formula():
    """Requirements 5 & 6: Completed, In Progress and Pending counts update automatically.
    Formula: Completion Percentage = (Completed Tasks / Total Assigned Tasks) * 100
    Handle division-by-zero safely when tasks = 0.
    """
    # Zero tasks test
    zero_metrics = services.core.calculate_work_metrics([])
    assert zero_metrics["total_tasks"] == 0
    assert zero_metrics["completed_tasks"] == 0
    assert zero_metrics["in_progress_tasks"] == 0
    assert zero_metrics["pending_tasks"] == 0
    assert zero_metrics["completion_percentage"] == 0.0

    # Test with varying tasks
    mock_tasks = [
        {"status": "Completed"},
        {"status": "Completed"},
        {"status": "In Progress"},
        {"status": "Not Started"},
    ]
    metrics = services.core.calculate_work_metrics(mock_tasks)
    assert metrics["total_tasks"] == 4
    assert metrics["completed_tasks"] == 2
    assert metrics["in_progress_tasks"] == 1
    assert metrics["pending_tasks"] == 1
    # (2 / 4) * 100 = 50.0%
    assert metrics["completion_percentage"] == 50.0

    # Add another completed task -> (3 / 5) * 100 = 60.0%
    mock_tasks.append({"status": "Completed"})
    metrics2 = services.core.calculate_work_metrics(mock_tasks)
    assert metrics2["total_tasks"] == 5
    assert metrics2["completed_tasks"] == 3
    assert metrics2["completion_percentage"] == 60.0


def test_req_7_progress_survives_logout_and_login():
    """Requirement 7: Progress and task states persist after logout and login."""
    unique_email = f"persist-user-{uuid.uuid4().hex[:8]}@example.com"
    services.core.register("Persistent Employee", unique_email, "Password123")
    user = services.core.login(unique_email, "Password123")
    uid = user["id"]

    services.core.save_employee_work_details(uid, {
        "process_name": "Cloud Security Automation",
        "target_completion_date": "2026-11-30",
        "challenges_faced": "Firewall rules pending network squad sign-off.",
    })
    tid = services.core.add_employee_task(uid, {
        "title": "Deploy AWS GuardDuty Scanners",
        "status": "In Progress",
        "progress_percent": 80,
    })

    # Simulate logout (new connection / fresh read)
    reloaded_user = services.core.login(unique_email, "Password123")
    assert reloaded_user["id"] == uid

    loaded_details = services.core.get_employee_work_details(reloaded_user["id"])
    assert loaded_details["process_name"] == "Cloud Security Automation"
    assert loaded_details["challenges_faced"] == "Firewall rules pending network squad sign-off."

    loaded_tasks = services.core.get_employee_tasks(reloaded_user["id"])
    assert len(loaded_tasks) == 1
    assert loaded_tasks[0]["id"] == tid
    assert loaded_tasks[0]["status"] == "In Progress"
    assert loaded_tasks[0]["progress_percent"] == 80


def test_req_8_different_employees_cannot_access_each_other_tasks():
    """Requirement 8: Strict data isolation ensures users cannot view or mutate each other's tasks."""
    user_a_email = f"user-a-{uuid.uuid4().hex[:8]}@example.com"
    user_b_email = f"user-b-{uuid.uuid4().hex[:8]}@example.com"

    services.core.register("Employee A", user_a_email, "SecretPass123")
    services.core.register("Employee B", user_b_email, "SecretPass123")

    user_a = services.core.login(user_a_email, "SecretPass123")
    user_b = services.core.login(user_b_email, "SecretPass123")

    # Employee A creates a task
    t_a_id = services.core.add_employee_task(user_a["id"], {
        "title": "Employee A Confidential Core Task",
        "status": "In Progress",
    })

    # Employee B creates a task
    t_b_id = services.core.add_employee_task(user_b["id"], {
        "title": "Employee B Private Task",
        "status": "Not Started",
    })

    # Employee A's tasks should NOT include Employee B's task
    tasks_a = services.core.get_employee_tasks(user_a["id"])
    titles_a = [t["title"] for t in tasks_a]
    assert "Employee A Confidential Core Task" in titles_a
    assert "Employee B Private Task" not in titles_a

    # Employee B cannot fetch Employee A's task by ID
    assert services.core.get_employee_task(t_a_id, user_b["id"]) is None

    # Employee B cannot update Employee A's task
    update_ok = services.core.update_task_status(t_a_id, user_b["id"], "Completed")
    assert not update_ok

    # Employee B cannot delete Employee A's task
    delete_ok = services.core.delete_employee_task(t_a_id, user_b["id"])
    assert not delete_ok

    # Task remains untouched for Employee A
    intact_task = services.core.get_employee_task(t_a_id, user_a["id"])
    assert intact_task["status"] == "In Progress"


def test_req_9_suggestions_update_based_on_work_progress():
    """Requirement 9: Suggestions & Improvements dynamically reflect active tasks, overdue deadlines, and progress."""
    unique_email = f"sug-user-{uuid.uuid4().hex[:8]}@example.com"
    services.core.register("Suggestion Test User", unique_email, "Pass123456")
    user = services.core.login(unique_email, "Pass123456")
    uid = user["id"]

    work_details = {
        "process_name": "API Gateway Modernization",
        "target_completion_date": "2026-12-31",
        "short_term_goals": "Complete OAuth2 token validation endpoints.",
        "challenges_faced": "Database migration script blocking integration test runs.",
    }
    services.core.save_employee_work_details(uid, work_details)

    # 1 Overdue task, 1 In Progress task, 1 Pending task
    services.core.add_employee_task(uid, {
        "title": "Overdue Security Review Task",
        "due_date": "2026-10-01",
        "status": "In Progress",
        "progress_percent": 50,
    })
    services.core.add_employee_task(uid, {
        "title": "High Priority Pending Task",
        "priority": "High",
        "due_date": "2026-11-20",
        "status": "Not Started",
    })

    tasks = services.core.get_employee_tasks(uid)
    suggestions = services.core.get_work_suggestions(uid, work_details, tasks)

    # Verify all 6 required recommendation types exist
    topics = [s["topic"] for s in suggestions]
    assert "Pending Task Reminder" in topics
    assert "Upcoming Deadline Alert" in topics
    assert "Overdue Task Notification" in topics
    assert "Productivity Improvement Suggestion" in topics
    assert "Process Improvement Recommendation" in topics
    assert "Goal Completion Suggestion" in topics

    # Check that Overdue Notification detects the overdue task
    overdue_sug = next(s for s in suggestions if s["topic"] == "Overdue Task Notification")
    assert "Overdue Security Review Task" in overdue_sug["action"]
    assert overdue_sug["priority"] == "High"

    # Check Process Improvement detects the active challenge
    proc_sug = next(s for s in suggestions if s["topic"] == "Process Improvement Recommendation")
    assert "Database migration script" in proc_sug["action"]


def test_req_10_resume_builder_still_works_with_its_information():
    """Requirement 10: Resume Builder retains its education, certifications, projects, skills, and PDF generation."""
    with services.core.connect() as db:
        u_row = db.execute("SELECT id FROM users WHERE email='eleanor.vance@talentsphere.io'").fetchone()
    uid = u_row["id"] if u_row else 1
    profile = services.core.get_profile(uid)
    skills = services.core.list_skills(uid)

    # Verify education, certifications, and experience still exist in the database
    edu = services.core.parse_json_field(profile.get("education", []))
    certs = services.core.parse_json_field(profile.get("certifications", []))
    exp = services.core.parse_json_field(profile.get("experience", []))

    assert len(edu) > 0, "Resume Builder education must be preserved"
    assert len(certs) > 0, "Resume Builder certifications must be preserved"
    assert len(exp) > 0, "Resume Builder experience must be preserved"
    assert len(skills) > 0, "Skills inventory must be preserved"

    # Test PDF generation continues to work
    from views.resume_builder_view import generate_ats_resume_pdf
    pdf_bytes = generate_ats_resume_pdf(
        user_name=profile.get("name", "Eleanor Vance"),
        user_email=profile.get("email", "eleanor.vance@talentsphere.io"),
        profile=profile,
        skills=skills,
        sections_to_include=["Summary", "Experience", "Education", "Certifications"],
    )
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 1000


def test_req_11_navigation_and_unrelated_modules_remain_functional():
    """Requirement 11: All other pages (Dashboard, Skills & Goals, Resume Builder, Career Development) remain fully functional."""
    for page_name in ["Dashboard", "Skills & Goals", "Resume Builder", "Career Development", "Employee Profile"]:
        at = AppTest.from_file(APP_PATH, default_timeout=30)
        at.session_state["is_authenticated"] = True
        at.session_state["user_id"] = 1
        at.session_state["current_page"] = page_name
        at.run()
        assert not at.exception, f"Page '{page_name}' must render without exceptions"
