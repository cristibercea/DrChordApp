Feature: Tab Generation
  Scenario: Upload song, generate tabs, and view them
    Given the user is on the login page
    When enter email cristiberc2@gmail.com and password 123
    And click login button
    And upload song /DrChord/frontend/private/testing/test_audio.mp3 with name SongNameOk and genre GenreOk
    And trigger generate tabs for SongNameOk
    Then see song SongNameOk in the main page
    When wait until tabs generation is done for SongNameOk
    And click see tabs for SongNameOk
    Then should be on the tabs page
    When navigate back to home
    And delete song SongNameOk
    Then should see no recordings text
    When click logout
    Then the user is redirected to the login page