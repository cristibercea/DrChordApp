Feature: Account Management
  Scenario: Edit account details and logout
    Given the user is on the login page
    When enter email cristiberc2@gmail.com and password 123
    And click login button
    And navigate to account details
    Then see account details
    When edit account name to CristianUpdated and confirm action via current password 123
    And navigate back to home
    And click logout
    Then the user is redirected to the login page