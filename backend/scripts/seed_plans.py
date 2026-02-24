#!/usr/bin/env python3
"""
Seed PLANS_DIR with 3–4 mock projects for local/dev use.
Each plan has a unique projectId (UUID) and projectNumber (1001–1004).
Run from repo root: python backend/scripts/seed_plans.py
Or: PLANS_DIR=backend/data/plans python backend/scripts/seed_plans.py
"""
import json
import os
import sys
from pathlib import Path

# Fixed UUIDs so mock data is reproducible across runs and sharing
PROJECT_IDS = [
    "a1b2c3d4-0001-4000-8000-000000000001",
    "a1b2c3d4-0002-4000-8000-000000000002",
    "a1b2c3d4-0003-4000-8000-000000000003",
    "a1b2c3d4-0004-4000-8000-000000000004",
]

BASE = {
    "owners": [],
    "risks": [],
    "kpis": [],
    "status": {"level": "yellow", "text": ""},
}

PLANS = [
    {
        **BASE,
        "projectId": PROJECT_IDS[0],
        "projectNumber": 1001,
        "header": {
            "projectTitle": "Regional Data Collection Pilot",
            "sponsor": "NASS Field Operations",
            "projectManager": "Jane Smith",
            "startDate": "Jan 1, 2026",
            "endDate": "Dec 31, 2026",
            "reportingPeriod": "FY Q2 2026",
            "version": "v1.0",
            "dateUpdated": "Feb 19, 2026",
        },
        "quarters": ["Q1 2026", "Q2 2026", "Q3 2026", "Q4 2026"],
        "objectives": [
            {"id": "O1", "title": "Launch pilot in 3 regions", "metric": "3/3 regions operational", "owner": "MS"},
            {"id": "O2", "title": "Complete baseline report", "metric": "Report approved", "owner": "JP"},
            {"id": "O3", "title": "Establish QA process (95% pass)", "metric": "95% pass rate", "owner": "RK"},
        ],
        "matrix": [
            [{"symbol": "○", "label": "Kickoff"}, {"symbol": "●", "label": "Pilot start"}, {"symbol": "●", "label": "3 regions"}, {"symbol": "○", "label": "Handoff"}],
            [{"symbol": "○", "label": "Scoping"}, {"symbol": "○", "label": "Analysis"}, {"symbol": "●", "label": "Draft"}, {"symbol": "●", "label": "Approved"}],
            [{"symbol": "△", "label": "Design QA"}, {"symbol": "○", "label": "Build"}, {"symbol": "○", "label": "Test"}, {"symbol": "●", "label": "95% pass"}],
        ],
        "owners": [{"initials": "JS", "role": "Project Manager"}, {"initials": "MS", "role": "Field Coordinator"}],
        "budget": {"total": 170000, "spent": 38300, "categories": [{"name": "Personnel", "planned": 120000, "spent": 35000}, {"name": "Travel", "planned": 15000, "spent": 2100}, {"name": "Other", "planned": 10000, "spent": 1200}]},
        "risks": [{"text": "Region 3 staffing gap", "owner": "MS", "mitigation": "Backup contractor identified"}],
        "kpis": [{"label": "Surveys completed", "value": "250 / 400", "target": True}],
        "status": {"level": "yellow", "text": "Region 3 data collection delayed 2 weeks; mitigation in progress."},
    },
    {
        **BASE,
        "projectId": PROJECT_IDS[1],
        "projectNumber": 1002,
        "header": {
            "projectTitle": "IT Migration Project",
            "sponsor": "IT Operations",
            "projectManager": "Alex Chen",
            "startDate": "Mar 1, 2026",
            "endDate": "Aug 31, 2026",
            "reportingPeriod": "Q2 2026",
            "version": "v0.2",
            "dateUpdated": "Feb 22, 2026",
        },
        "quarters": ["Q1 2026", "Q2 2026", "Q3 2026"],
        "objectives": [
            {"id": "O1", "title": "Migrate core systems", "metric": "Zero downtime", "owner": "AC"},
            {"id": "O2", "title": "User acceptance testing", "metric": "UAT sign-off", "owner": "BD"},
        ],
        "matrix": [
            [{"symbol": "●", "label": "Done"}, {"symbol": "○", "label": "In progress"}, {"symbol": "", "label": ""}],
            [{"symbol": "", "label": ""}, {"symbol": "○", "label": "UAT start"}, {"symbol": "○", "label": "Sign-off"}],
        ],
        "owners": [{"initials": "AC", "role": "Tech Lead"}, {"initials": "BD", "role": "QA"}],
        "budget": {"total": 50000, "spent": 12000, "categories": [{"name": "Infrastructure", "planned": 30000, "spent": 10000}]},
        "risks": [],
        "kpis": [{"label": "Systems migrated", "value": "2/5", "target": True}],
        "status": {"level": "green", "text": "On schedule."},
    },
    {
        **BASE,
        "projectId": PROJECT_IDS[2],
        "projectNumber": 1003,
        "header": {
            "projectTitle": "Grant Proposal – Research Pilot",
            "sponsor": "Funding Office",
            "projectManager": "Dr. Lee",
            "startDate": "Apr 1, 2026",
            "endDate": "Sep 30, 2026",
            "reportingPeriod": "Q2 2026",
            "version": "v0.1",
            "dateUpdated": "Feb 20, 2026",
        },
        "quarters": ["Q2 2026", "Q3 2026"],
        "objectives": [{"id": "O1", "title": "Submit proposal", "metric": "Submitted", "owner": "DL"}],
        "matrix": [[{"symbol": "●", "label": "Submitted"}, {"symbol": "○", "label": "Review"}]],
        "owners": [{"initials": "DL", "role": "PI"}],
        "budget": {"total": 75000, "spent": 0, "categories": [{"name": "Research", "planned": 75000, "spent": 0}]},
        "risks": [{"text": "Deadline", "owner": "DL", "mitigation": "Draft ready"}],
        "kpis": [],
        "status": {"level": "green", "text": "Proposal drafted."},
    },
    {
        **BASE,
        "projectId": PROJECT_IDS[3],
        "projectNumber": 1004,
        "header": {
            "projectTitle": "Product Launch – Q2",
            "sponsor": "Product",
            "projectManager": "Sam Rivera",
            "startDate": "Jan 15, 2026",
            "endDate": "Jun 30, 2026",
            "reportingPeriod": "Q2 2026",
            "version": "v0.5",
            "dateUpdated": "Feb 21, 2026",
        },
        "quarters": ["Q1 2026", "Q2 2026"],
        "objectives": [
            {"id": "O1", "title": "Beta release", "metric": "500 users", "owner": "SR"},
            {"id": "O2", "title": "GA launch", "metric": "Public release", "owner": "SR"},
        ],
        "matrix": [
            [{"symbol": "●", "label": "Beta"}, {"symbol": "○", "label": "GA"}],
            [{"symbol": "○", "label": "Prep"}, {"symbol": "●", "label": "Launch"}],
        ],
        "owners": [{"initials": "SR", "role": "Product Lead"}],
        "budget": {"total": 45000, "spent": 18000, "categories": [{"name": "Marketing", "planned": 20000, "spent": 8000}, {"name": "Engineering", "planned": 25000, "spent": 10000}]},
        "risks": [{"text": "Scope creep", "owner": "SR", "mitigation": "Strict GA criteria"}],
        "kpis": [{"label": "Beta signups", "value": "320 / 500", "target": True}],
        "status": {"level": "yellow", "text": "Beta on track; GA date confirmed."},
    },
]

FILENAMES = ["regional-pilot", "it-migration", "grant-proposal", "product-launch"]


def main():
    backend_dir = Path(__file__).resolve().parent.parent
    plans_dir = Path(os.environ.get("PLANS_DIR", backend_dir / "data" / "plans"))
    plans_dir.mkdir(parents=True, exist_ok=True)
    for name, plan in zip(FILENAMES, PLANS):
        path = plans_dir / f"{name}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(plan, f, indent=2)
        print(f"Wrote {path} (project #{plan['projectNumber']} – {plan['header']['projectTitle']})")
    print(f"Seeded {len(PLANS)} plans in {plans_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
