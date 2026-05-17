Feature: Song Management
  Scenario: Upload, search, filter, edit and delete a song
    Given the user is on the login page
    When enter email cristiberc2@gmail.com and password 123
    And click login button
    And upload song /DrChord/frontend/private/testing/test_audio.mp3 with name SongNameOk and genre GenreOk
    Then see song SongNameOk in the main page
    When search by name of the song SongNameOk
    Then see song SongNameOk in the main page
    When edit song genre to Rock
    And delete song SongNameOk
    Then should see no recordings text
    When click logout
    Then the user is redirected to the login page