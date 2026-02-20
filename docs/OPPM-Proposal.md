# One Page Project Manager (OPPM) — Proposal

**Document Type:** Proposal  
**Version:** 1.0  
**Date:** February 19, 2026

---

## Executive Summary

This proposal defines a **One Page Project Manager (OPPM)** capability following the classic NASS-style layout: a single landscape page with a matrix tying objectives, schedule, owners, costs, and status together. The design mirrors USDA NASS/ARS project planning conventions and can be implemented as a view or module in the existing project management app.

---

## 1. Header Block (Top of Page)

A compact header runs across the top of the OPPM:

| Field | Description | Example |
|-------|-------------|---------|
| **Project Title** | Short, descriptive name | "Regional Data Collection Pilot" |
| **Sponsor / Program** | Agency, unit, grant, or program | "NASS Field Operations" |
| **Project Manager** | Primary PM name | "Jane Smith" |
| **Start Date / End Date** | Project lifecycle | "Jan 1, 2026 / Dec 31, 2026" |
| **Reporting Period** | Current period for status | "FY Q2 2026" |
| **Version / Date Updated** | Document control | "v1.2 / Feb 19, 2026" |

**Layout:** Two short rows or a narrow band; font size 9–10 pt to maximize content area.

---

## 2. Objectives Column (Left Side)

Down the left side, list **5–10 objectives**:

- **Format:** Numbered: O1, O2, O3, … O10  
- **Content:** Concise outcome statements (what success looks like)  
- **Optional:** Small "Success Metric" phrase per objective  

**Example:**

| ID | Objective | Success Metric |
|----|-----------|-----------------|
| O1 | Launch pilot data collection in 3 regions | 3/3 regions operational |
| O2 | Complete baseline analysis and report | Report approved by sponsor |
| O3 | Establish data quality assurance process | 95% pass rate achieved |
| O4 | Train field staff on new protocols | 20 staff certified |
| O5 | Integrate pilot data into national system | API integration complete |
| O6 | Publish lessons learned and recommendations | Document released |

---

## 3. Timeframe Row (Top of Matrix)

Across the top, create time buckets:

- **Columns:** Months or quarters for project duration  
- **Shorter projects:** Weeks or key milestones instead of quarters  

**Example:**

| | Q1 2026 | Q2 2026 | Q3 2026 | Q4 2026 |
|--|---------|---------|---------|---------|
| *(objectives below)* | | | | |

---

## 4. Objective–Timeline Matrix (Center)

The core of the OPPM: each row = objective, each column = time period.

**Cell contents:**
- Planned activity or milestone for that objective in that period  
- **Symbols** (keep it readable):
  - `○` Hollow circle = planned milestone  
  - `●` Filled circle = completed milestone  
  - `△` Triangle = risk or decision point  

**Optionally:** 1–3 word labels next to symbols (e.g., "Pilot start", "Report draft").

**Example (abbreviated):**

| Objective | Q1 2026 | Q2 2026 | Q3 2026 | Q4 2026 |
|-----------|---------|---------|---------|---------|
| O1 | ○ Kickoff | ● Pilot start | ● 3 regions | ○ Handoff |
| O2 | ○ Scoping | ○ Analysis | ● Report draft | ● Approved |
| O3 | △ Design QA | ○ Build | ○ Test | ● 95% pass |
| ... | | | | |

---

## 5. Responsibility / Owners Section

Tie people to objectives and tasks:

- List team members with **initials**  
- Show primary owner initials next to each objective row (or in a narrow column)  
- Optionally: initials next to symbols in the matrix for granularity  

**Example:**

| Initials | Role |
|----------|------|
| JS | Project Manager |
| JP | Lead Analyst |
| MS | Field Coordinator |
| RK | QA Lead |
| TL | Systems Integrator |

**Owner assignment per objective:**
- O1 → MS  
- O2 → JP  
- O3 → RK  
- O4 → MS  
- O5 → TL  
- O6 → JS  

---

## 6. Budget / Effort Summary

Compact resource block (lower left or lower center):

- **Total Budget**  
- **Budget by category** (3–5 lines): Personnel, Travel, Contracts, Equipment, Other  
- **Optional:** Bar or pie indicator – % spent vs. planned  
- **Optional:** Planned vs. actual staff time (hours or FTEs)  

**Example:**

| Category | Planned | Spent | % |
|----------|---------|-------|---|
| Personnel | $120,000 | $35,000 | 29% |
| Travel | $15,000 | $2,100 | 14% |
| Contracts | $25,000 | $0 | 0% |
| Other | $10,000 | $1,200 | 12% |
| **Total** | **$170,000** | **$38,300** | **23%** |

---

## 7. Risk / Issues and Metrics

Reserve space (bottom center or right) for:

**Top 3–5 Risks** (owner + one-line mitigation):

| # | Risk | Owner | Mitigation |
|---|------|-------|------------|
| 1 | Region 3 staffing gap | MS | Cross-train from Region 1; backup contractor identified |
| 2 | Data integration delay | TL | Early API testing in Q2; fallback CSV process |
| 3 | Budget overrun risk | JS | Monthly variance review; hold 10% contingency |

**Key Performance Indicators** (2–4 lines, tied to objectives):

- Surveys completed: 250 / 400 target  
- Data quality pass rate: 92% (target 95%)  
- Staff trained: 18 / 20  
- Deliverables on schedule: 4 / 5  

---

## 8. Status Summary and Legend

**Overall Status:** Green / Yellow / Red with a 1-line explanation.

**Example:**
- **Status: Yellow** – Field data collection delayed in Region 3 due to staffing.

**Legend:**

| Symbol | Meaning |
|--------|----------|
| ○ | Planned milestone |
| ● | Completed milestone |
| △ | Risk or decision point |
| 🟢 | On track |
| 🟡 | At risk |
| 🔴 | Behind / blocked |

---

## 9. Suggested Layout (Landscape)

**Mental map of a landscape letter page (11" × 8.5"):**

```
┌─────────────────────────────────────────────────────────────────────────┐
│  HEADER (1–1.5") – Project Title, Sponsor, PM, Dates, Reporting Period   │
├──────────┬──────────────────────────────────────────────────────────────┤
│          │  Q1 2026  │  Q2 2026  │  Q3 2026  │  Q4 2026  │              │
│ OBJECTIVES│           │           │           │           │   MATRIX     │
│ (1.5–2") │           │           │           │           │   (60–70%)   │
│ O1 ...   │   ○  ●    │   ●  ○    │   ●       │   ○       │              │
│ O2 ...   │   ○       │   ○       │   ●  ○     │   ●       │              │
│ O3 ...   │   △       │   ○       │   ○       │   ●       │              │
│ ...      │           │           │           │           │              │
├──────────┴──────────────────────────────────────────────────────────────┤
│  BOTTOM BAND (≈2")                                                       │
│  ┌─────────────────┬─────────────────────┬─────────────────────────────┐ │
│  │ Budget / Effort │ Risks & Metrics     │ Status & Legend             │ │
│  │ - Total         │ - Top 3–5 risks    │ - Green/Yellow/Red          │ │
│  │ - By category   │ - KPIs              │ - Symbol legend             │ │
│  └─────────────────┴─────────────────────┴─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 10. Implementation Options

### Option A: Static Template (Word / PDF)
- Fillable template in Word or PDF form.  
- Print or export to PDF for distribution.  
- No software required.

### Option B: Spreadsheet (Excel / Google Sheets)
- Matrix in cells; formulas for budget % and status.  
- Conditional formatting for Green/Yellow/Red.  
- Shared editing for teams.

### Option C: Web App Integration
Extend the existing project management app:

- **Data model:** Objectives, timeline columns, milestones, owners, budget, risks.  
- **View:** Single-page OPPM layout (CSS Grid/Flexbox), export to PDF.  
- **Sync:** Link objectives to existing todos/tasks for consistency.

### Option D: Hybrid
- Maintain OPPM as a **report** generated from existing project data.  
- App stores objectives, milestones, owners, budget; OPPM view renders the one-pager.

---

## 11. Filled-in Example: Regional Data Collection Pilot

*Sample OPPM for a NASS-style field operations project*

### Header

| Project Title | Regional Data Collection Pilot |
|---------------|--------------------------------|
| Sponsor | NASS Field Operations |
| Project Manager | Jane Smith |
| Start / End | Jan 1, 2026 / Dec 31, 2026 |
| Reporting Period | FY Q2 2026 |
| Version | v1.0 / Feb 19, 2026 |

### Objectives + Matrix (abbreviated)

| ID | Objective | Q1 | Q2 | Q3 | Q4 | Owner |
|----|-----------|----|----|----|----|-------|
| O1 | Launch pilot in 3 regions | ○ Kickoff | ● Pilot start | ● 3 regions | ○ Handoff | MS |
| O2 | Complete baseline report | ○ Scoping | ○ Analysis | ● Draft | ● Approved | JP |
| O3 | Establish QA process (95% pass) | △ Design | ○ Build | ○ Test | ● Done | RK |
| O4 | Train 20 field staff | ○ Curriculum | ● Week 1–2 | ● Week 3–4 | ○ Certify | MS |
| O5 | Integrate data into national system | ○ Specs | ○ Dev | △ UAT | ● Live | TL |
| O6 | Publish lessons learned | | | ○ Draft | ● Release | JS |

### Budget Summary

Total: $170,000 | Spent: $38,300 (23%) | Personnel 29% | Travel 14% | Contracts 0%

### Risks & KPIs

**Risks:** (1) Region 3 staffing—MS: backup contractor; (2) Integration delay—TL: early API test; (3) Budget—JS: 10% contingency.

**KPIs:** Surveys 250/400 | QA 92%/95% | Staff trained 18/20 | On-time 4/5

### Status

**Yellow** – Region 3 data collection delayed 2 weeks; mitigation in progress.

---

## 12. Next Steps

1. **Choose format:** Static template, spreadsheet, or web app.  
2. **Draft sample OPPM** for a specific project type (IT, research, grants, field ops).  
3. **Define data schema** if building into the app (extend OpenSpec).  
4. **Create Beads** for OPPM implementation tasks and dependencies.

---

## References

- USDA ARS OSQR Project Plan Template  
- USDA Forest Service Project Plan Template  
- USDA NASS Strategic Plan FY22–26  
- NASS PPT Template (NASDA)  
- One Page Project Management template (Scribd)  
- USDA Farm to School Planning Toolkit  
