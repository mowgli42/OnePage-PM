Feature: OPPM plan view and persistence
  As a project manager
  I want to view and save a one-page project plan
  So that stakeholders share a single source of project status

  # Aligned with OpenSpec §2 Plan (OPPM), §4 OPPM view, and frontend/e2e/workflow.spec.js

  Scenario: OPPM view loads and shows plan
    Given the backend is available
    When I open the app at "/?view=oppm"
    Then the OPPM view is visible
    And the plan header shows project information
    And the objectives × quarters matrix is visible

  Scenario: Edit plan opens the edit panel with schedule sections
    Given the backend is available
    And I am on the OPPM view
    When I choose to edit the plan
    Then the edit panel is visible
    And the edit panel includes Schedule, Time periods, and Objectives sections

  Scenario: Save plan persists and reload shows saved data
    Given the backend is available
    When I PUT "/plan" with a plan whose project title is "E2E Test Project"
    And I open the app at "/?view=oppm"
    Then the OPPM view is visible
    And the plan header contains "E2E Test Project"
    And the plan matrix reflects the saved objectives

  Scenario: List and get plan via API
    Given the backend is available
    When I GET "/plans"
    Then the response status is 200
    And the response body is a JSON array of plan summaries
    When I GET "/plan"
    Then the response status is 200
    And the response body includes header, quarters, objectives, and matrix
