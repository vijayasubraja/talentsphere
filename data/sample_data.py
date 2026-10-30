"""Sample data module for TalentSphere UI/UX prototype.

This module provides mock data representing a single consistent employee profile,
skills, career goals, gap analysis, and activities across the platform.
No database or external API dependencies are required.
"""

from __future__ import annotations
import copy
from typing import Any, Dict, List

SAMPLE_EMPLOYEE: Dict[str, Any] = {
    "id": 1,
    "name": "Eleanor Vance",
    "email": "eleanor.vance@talentsphere.io",
    "job_title": "Senior Cloud & DevOps Engineer",
    "department": "Platform Engineering & Infrastructure",
    "phone": "+1 (512) 890-4421",
    "location": "Austin, TX (Hybrid)",
    "employee_id": "TS-49210",
    "manager": "Marcus Brody (VP of Cloud Architecture)",
    "joined_date": "March 2022",
    "employment_type": "Full-time",
    "years_experience": 6.5,
    "avatar_initials": "EV",
    "summary": (
        "Results-oriented Senior Cloud & DevOps Engineer with 6+ years of hands-on experience "
        "architecting multi-region Kubernetes clusters, enterprise IaC automation, and automated "
        "DevSecOps pipelines. Proven record of reducing cloud deployment cycles by 65% and leading "
        "cross-functional infrastructure initiatives. Currently advancing toward a Principal Systems "
        "Architect leadership role."
    ),
    "experience": [
        {
            "role": "Senior Cloud & DevOps Engineer",
            "company": "TalentSphere Platforms Inc.",
            "period": "2022 – Present",
            "location": "Austin, TX",
            "highlights": [
                "Architected and deployed multi-region AWS EKS clusters with zero-downtime blue/green deployment strategy.",
                "Built centralized Terraform & Terragrunt module library adopted by 35+ development squads.",
                "Instituted automated vulnerability scanning and secret detection across all CI/CD pipelines.",
            ],
        },
        {
            "role": "Cloud Infrastructure Engineer",
            "company": "Aura Distributed Systems",
            "period": "2019 – 2022",
            "location": "Denver, CO",
            "highlights": [
                "Managed AWS hybrid infrastructure supporting 4M+ daily active enterprise users with 99.99% uptime.",
                "Automated cost allocation tagging resulting in $180K annual cloud infrastructure savings.",
                "Developed Prometheus and Grafana dashboards for distributed tracing and SLO monitoring.",
            ],
        },
        {
            "role": "Associate DevOps Engineer",
            "company": "Vanguard Softworks",
            "period": "2018 – 2019",
            "location": "Austin, TX",
            "highlights": [
                "Maintained Docker container registries and GitLab CI runner fleets.",
                "Created bash and Python automation scripts for routine database backups and log rotations.",
            ],
        },
    ],
    "education": [
        {
            "degree": "Bachelor of Science in Computer Science",
            "institution": "University of Texas at Austin",
            "period": "2014 – 2018",
            "honors": "Graduated Magna Cum Laude · Dean's Honor Roll",
        }
    ],
    "certifications": [
        {
            "name": "AWS Certified Solutions Architect – Professional",
            "issuer": "Amazon Web Services",
            "year": "2024",
            "credential_id": "AWS-PSA-908234",
            "badge_color": "#FF9900",
        },
        {
            "name": "Certified Kubernetes Administrator (CKA)",
            "issuer": "Cloud Native Computing Foundation",
            "year": "2025",
            "credential_id": "CKA-240188",
            "badge_color": "#326CE5",
        },
        {
            "name": "HashiCorp Certified: Terraform Associate",
            "issuer": "HashiCorp",
            "year": "2023",
            "credential_id": "HC-TA-51029",
            "badge_color": "#844FBA",
        },
    ],
}

SAMPLE_SKILLS: List[Dict[str, Any]] = [
    {
        "id": "sk-1",
        "name": "Kubernetes & Container Orchestration",
        "category": "Cloud & Infrastructure",
        "proficiency": "Advanced",
        "progress": 90,
        "years": 5.0,
        "status": "Strength",
    },
    {
        "id": "sk-2",
        "name": "AWS Cloud Architecture",
        "category": "Cloud & Infrastructure",
        "proficiency": "Advanced",
        "progress": 88,
        "years": 5.5,
        "status": "Strength",
    },
    {
        "id": "sk-3",
        "name": "Terraform & IaC Automation",
        "category": "Cloud & Infrastructure",
        "proficiency": "Advanced",
        "progress": 85,
        "years": 4.5,
        "status": "Strength",
    },
    {
        "id": "sk-4",
        "name": "CI/CD & DevSecOps Pipelines",
        "category": "DevOps & Tooling",
        "proficiency": "Advanced",
        "progress": 82,
        "years": 4.0,
        "status": "Strength",
    },
    {
        "id": "sk-5",
        "name": "Python & Go Tooling",
        "category": "Software Engineering",
        "proficiency": "Intermediate",
        "progress": 75,
        "years": 4.0,
        "status": "Proficient",
    },
    {
        "id": "sk-6",
        "name": "Distributed Observability (Prometheus/Grafana)",
        "category": "DevOps & Tooling",
        "proficiency": "Intermediate",
        "progress": 72,
        "years": 3.0,
        "status": "Proficient",
    },
    {
        "id": "sk-7",
        "name": "Distributed System Design & Resilience",
        "category": "Architecture & Strategy",
        "proficiency": "Intermediate",
        "progress": 65,
        "years": 2.5,
        "status": "Focus Area",
    },
    {
        "id": "sk-8",
        "name": "FinOps & Cloud Cost Governance",
        "category": "Architecture & Strategy",
        "proficiency": "Beginner",
        "progress": 45,
        "years": 1.0,
        "status": "Skill Gap",
    },
    {
        "id": "sk-9",
        "name": "Enterprise Architecture Governance (TOGAF)",
        "category": "Architecture & Strategy",
        "proficiency": "Beginner",
        "progress": 40,
        "years": 0.8,
        "status": "Skill Gap",
    },
    {
        "id": "sk-10",
        "name": "Executive Stakeholder Alignment",
        "category": "Leadership & Communication",
        "proficiency": "Beginner",
        "progress": 38,
        "years": 1.2,
        "status": "Skill Gap",
    },
]

SAMPLE_GOALS: List[Dict[str, Any]] = [
    {
        "id": "g-1",
        "title": "Complete TOGAF 9.2 Enterprise Architecture Certification",
        "type": "Short-Term",
        "target_date": "Q4 2026",
        "status": "In Progress",
        "progress": 65,
        "description": "Master enterprise architecture frameworks to formalize multi-department technical design reviews.",
    },
    {
        "id": "g-2",
        "title": "Lead Multi-Region Active-Active DR Drill",
        "type": "Short-Term",
        "target_date": "Q3 2026",
        "status": "Completed",
        "progress": 100,
        "description": "Validated automated failover across us-east-1 and us-west-2 with RTO under 8 minutes.",
    },
    {
        "id": "g-3",
        "title": "Publish Kubernetes FinOps Cost Allocation RFC",
        "type": "Short-Term",
        "target_date": "Q1 2027",
        "status": "In Progress",
        "progress": 40,
        "description": "Design showback mechanisms to attribute shared cluster compute costs down to individual product pods.",
    },
    {
        "id": "g-4",
        "title": "Transition to Principal Cloud Systems Architect",
        "type": "Long-Term",
        "target_date": "Q2 2027",
        "status": "In Progress",
        "progress": 68,
        "description": "Attain role promotion by driving cloud infrastructure strategy, technical governance, and cross-team alignment.",
    },
    {
        "id": "g-5",
        "title": "Establish Global Cloud Architecture Review Board",
        "type": "Long-Term",
        "target_date": "Late 2027",
        "status": "Not Started",
        "progress": 10,
        "description": "Define standardized technical design templates and architectural sign-off gates across engineering.",
    },
    {
        "id": "g-6",
        "title": "Mentor 4 Junior & Mid-level Platform Engineers",
        "type": "Long-Term",
        "target_date": "Ongoing",
        "status": "In Progress",
        "progress": 75,
        "description": "Conduct bi-weekly 1:1 architectural design reviews, IaC pairing, and career planning sessions.",
    },
]

SAMPLE_CAREER_TARGET = {
    "current_role": "Senior Cloud & DevOps Engineer",
    "target_role": "Principal Cloud Systems Architect",
    "target_department": "Architecture & Engineering Strategy",
    "target_timeline": "9–12 Months",
    "overall_readiness": 68,
    "role_description": (
        "The Principal Cloud Systems Architect is responsible for setting the company's enterprise cloud roadmap, "
        "evaluating cutting-edge distributed paradigms, establishing FinOps guardrails, and aligning engineering "
        "strategy with senior executive leadership."
    ),
    "competencies": [
        {
            "skill": "Distributed System Design",
            "current_level": "Intermediate",
            "current_score": 65,
            "required_level": "Expert",
            "required_score": 90,
            "gap": 25,
            "priority": "High Priority",
            "status": "Action Required",
        },
        {
            "skill": "FinOps & Cloud Cost Optimization",
            "current_level": "Beginner",
            "current_score": 45,
            "required_level": "Advanced",
            "required_score": 80,
            "gap": 35,
            "priority": "High Priority",
            "status": "Action Required",
        },
        {
            "skill": "Enterprise Architecture Governance (TOGAF)",
            "current_level": "Beginner",
            "current_score": 40,
            "required_level": "Advanced",
            "required_score": 75,
            "gap": 35,
            "priority": "High Priority",
            "status": "Action Required",
        },
        {
            "skill": "Executive Technical Communication",
            "current_level": "Beginner",
            "current_score": 38,
            "required_level": "Advanced",
            "required_score": 80,
            "gap": 42,
            "priority": "High Priority",
            "status": "Action Required",
        },
        {
            "skill": "Multi-Cloud Hybrid Mesh Strategy",
            "current_level": "Intermediate",
            "current_score": 60,
            "required_level": "Advanced",
            "required_score": 85,
            "gap": 25,
            "priority": "Medium Priority",
            "status": "In Progress",
        },
        {
            "skill": "Kubernetes & Container Orchestration",
            "current_level": "Advanced",
            "current_score": 90,
            "required_level": "Advanced",
            "required_score": 85,
            "gap": 0,
            "priority": "Target Met",
            "status": "Mastered",
        },
        {
            "skill": "Terraform & IaC Automation",
            "current_level": "Advanced",
            "current_score": 85,
            "required_level": "Advanced",
            "required_score": 85,
            "gap": 0,
            "priority": "Target Met",
            "status": "Mastered",
        },
    ],
    "suggested_activities": [
        {
            "id": "act-1",
            "title": "Enterprise Cloud Architecture Masterclass",
            "category": "Executive Education",
            "provider": "Cloud Architecture Institute",
            "duration": "6 Weeks (Self-paced)",
            "priority": "High Priority",
            "impact": "Closes 20% of Distributed System Design gap",
            "description": "Deep-dive into multi-region consistency, event sourcing, saga patterns, and CAP tradeoffs.",
        },
        {
            "id": "act-2",
            "title": "Shadow Enterprise Architecture Review Board",
            "category": "Experiential Learning",
            "provider": "Internal Platform Guild",
            "duration": "Bi-weekly Sessions",
            "priority": "High Priority",
            "impact": "Direct alignment with VP & Fellow Architects",
            "description": "Participate as an observer and contributor during major technical RFC approvals.",
        },
        {
            "id": "act-3",
            "title": "FinOps Certified Practitioner (FOCP) Program",
            "category": "Professional Credential",
            "provider": "FinOps Foundation",
            "duration": "4 Weeks",
            "priority": "High Priority",
            "impact": "Addresses cloud cost governance requirement",
            "description": "Acquire proven methodologies for unit economics, forecasting, and engineering accountability.",
        },
        {
            "id": "act-4",
            "title": "Executive Presentation & C-Suite Technical Storytelling",
            "category": "Leadership Development",
            "provider": "TalentSphere Leadership Academy",
            "duration": "3 Days Workshop",
            "priority": "Medium Priority",
            "impact": "Elevates stakeholder persuasion and ROI justification",
            "description": "Learn to translate complex technical trade-offs into compelling business value propositions.",
        },
    ],
    "learning_milestones": [
        {
            "step": "1",
            "phase": "Foundation",
            "title": "Core Architecture & System Design Review",
            "status": "Completed",
            "progress": 100,
            "timeline": "Completed Q1 2026",
            "description": "Finished advanced distributed patterns training and multi-region failover drill.",
        },
        {
            "step": "2",
            "phase": "Governance",
            "title": "TOGAF Certification & FinOps RFC",
            "status": "In Progress",
            "progress": 60,
            "timeline": "Target: Q4 2026",
            "description": "Complete TOGAF exams and publish internal cloud chargeback specification.",
        },
        {
            "step": "3",
            "phase": "Leadership",
            "title": "Cross-Functional Architecture Sponsorship",
            "status": "Upcoming",
            "progress": 25,
            "timeline": "Target: Q1 2027",
            "description": "Sponsor 2 major architecture RFCs with multi-department stakeholder sign-off.",
        },
        {
            "step": "4",
            "phase": "Promotion",
            "title": "Principal Architect Committee Review",
            "status": "Planned",
            "progress": 0,
            "timeline": "Target: Q2 2027",
            "description": "Formal panel review with Engineering VP, Chief Architect, and HR Talent Board.",
        },
    ],
}

SAMPLE_ACTIVITIES = [
    {
        "icon": "🏆",
        "title": "Milestone Completed: Multi-Region DR Drill",
        "timestamp": "Today, 10:45 AM",
        "category": "Achievement",
        "description": "Led automated failover test across 2 AWS regions with 100% data integrity verified.",
    },
    {
        "icon": "📈",
        "title": "Skill Proficiency Level Updated",
        "timestamp": "Yesterday, 3:30 PM",
        "category": "Skills",
        "description": "Updated Kubernetes & Container Orchestration to Advanced (90% verified).",
    },
    {
        "icon": "🎯",
        "title": "New Career Goal Registered",
        "timestamp": "3 days ago",
        "category": "Goals",
        "description": "Added short-term goal: 'Publish Kubernetes FinOps Cost Allocation RFC'.",
    },
    {
        "icon": "🤝",
        "title": "Quarterly Career Alignment Check-in",
        "timestamp": "1 week ago",
        "category": "Mentorship",
        "description": "Aligned with manager Marcus Brody on Principal Architect readiness criteria.",
    },
    {
        "icon": "📜",
        "title": "Credential Verified: CKA Certification",
        "timestamp": "2 weeks ago",
        "category": "Certification",
        "description": "CNCF Certified Kubernetes Administrator badge renewed through 2028.",
    },
]

SAMPLE_RECOMMENDATIONS = [
    {
        "priority": "High Priority",
        "title": "Address Distributed Systems Gap",
        "category": "Target Competency",
        "description": "Your target role requires 90% in Distributed Systems (currently 65%). Enrolling in the suggested Masterclass is recommended.",
        "target_page": "Career Development",
    },
    {
        "priority": "In Progress",
        "title": "Complete TOGAF Study Module 4",
        "category": "Certification Goal",
        "description": "You are 65% through your short-term goal. Scheduling the Part 1 exam this month will keep you on track for Q4.",
        "target_page": "Skills & Goals",
    },
    {
        "priority": "Recommended",
        "title": "Join Architecture Review Shadowing",
        "category": "Practical Experience",
        "description": "The next bi-weekly Architecture Review Board session is scheduled for Thursday. Reserve a guest seat.",
        "target_page": "Career Development",
    },
]


def get_initial_sample_data() -> Dict[str, Any]:
    """Returns a deep copy of fresh sample data to initialize session state."""
    return {
        "employee": copy.deepcopy(SAMPLE_EMPLOYEE),
        "skills": copy.deepcopy(SAMPLE_SKILLS),
        "goals": copy.deepcopy(SAMPLE_GOALS),
        "career_target": copy.deepcopy(SAMPLE_CAREER_TARGET),
        "activities": copy.deepcopy(SAMPLE_ACTIVITIES),
        "recommendations": copy.deepcopy(SAMPLE_RECOMMENDATIONS),
        "metrics": {
            "profile_completion": 85,
            "total_skills": len(SAMPLE_SKILLS),
            "skills_to_improve": 3,
            "career_progress": 68,
            "target_role_match": 72,
        },
    }
