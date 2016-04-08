# Changes in response to comments in Udacity code review 1

- Added pretty printing to API.
    + The GameForm now features a field, `pretty_board`, which is a list of strings, each displaying one line of the pretty printed board and legend.
    + A repeated StringField (an array in the JSON) was chosen in preference to the a string with newlines because the API explorer would simply display the newline character as "\n". Since the point of this field is to display clearly in the API explorer, an array works much better.
    + The `board` field still remains for use by a hypothetical front-end. As documented elsewhere, indexes 0-5 represent the South player's houses, 7-13 present the North player's houses, index 6 represents the South player's store, and index 13 represents the North player's store.