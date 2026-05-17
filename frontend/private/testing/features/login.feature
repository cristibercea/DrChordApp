Feature: User Authentication
  Scenario: Login failed due to incorrect data
    Given the user is on the login page
    When enter email cristiberc2@gmail.com and password WrongPassword
    And click login button
    Then stays on login page and sees error feedback

  Scenario: Login passed
    Given the user is on the login page
    When enter email cristiberc2@gmail.com and password 123
    And click login button
    Then proceeds to homepage and sees DeChord logo