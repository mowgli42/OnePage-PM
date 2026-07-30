Feature: Backend health check
  As an operator
  I want a health endpoint
  So that deploy and local checks can confirm the API is up

  # Aligned with OpenSpec §2 Health

  Scenario: Health returns ok
    Given the backend is available
    When I GET "/health"
    Then the response status is 200
    And the response body is:
      """
      { "status": "ok" }
      """
