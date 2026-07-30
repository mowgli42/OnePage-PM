Feature: Todos view and API
  As a project manager
  I want to see and manage todos
  So that I can track simple work items

  # Aligned with OpenSpec §2 Todos, §4 Todos view, and frontend/e2e/workflow.spec.js

  Scenario: Todos view loads with app shell
    Given the backend is available
    When I open the app at "/"
    Then the app shell is visible
    And the page title contains "Project Management"
    And I can switch between "Todos" and "OPPM" views

  Scenario: List todos via API
    Given the backend is available
    When I GET "/todos"
    Then the response status is 200
    And the response body is a JSON array of todos

  Scenario: Create a todo via API
    Given the backend is available
    When I POST "/todos" with body:
      """
      { "title": "Ship the app", "completed": false }
      """
    Then the response status is 201
    And the todo has a server-generated id and created_at
    And the todo title is "Ship the app"
    And the todo completed is false
