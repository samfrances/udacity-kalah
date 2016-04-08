# Changes in response to comments in Udacity code review 1

- Added pretty printing to API.
    + The GameForm now features a field, `pretty_board`, which is a list of strings, each displaying one line of the pretty printed board and legend.
    + A repeated StringField (an array in the JSON) was chosen in preference to the a string with newlines because the API explorer would simply display the newline character as "\n". Since the point of this field is to display clearly in the API explorer, an array works much better.
    + The `board` field still remains for use by a hypothetical front-end. As documented elsewhere, indexes 0-5 represent the South player's houses, 7-13 present the North player's houses, index 6 represents the South player's store, and index 13 represents the North player's store.
- Changed `cancel_game` endpoint to use `PUT` rather than `DELETE`, as requested.
- Added option of requesting verbose history, with usernames displayed, and with each move specifying who played (`'N'` or `'S'`).
    + The option of displaying history only as a list of houses still remains the default, since from this information it is easy to determine whether the North or South user made a particular move, and the `urlsafe_game_key` field allows one to retrieve the relevant game and determine who the players are, if one wishes. Therefore it seems more efficient to send the minimum required information by default.
    + This involved modifying `GameForm` and adding a new form to represent individual moves, `MoveForm`. See [README.md](README.md) for documentation of these.
- Added messages sent at the end of the turn, giving instructions to the user. e.g. "North player's turn. Enter an integer between 7 and 12."
- Added `get_completed_games` endpoint which returns a list of all completed games.