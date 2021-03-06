# Kalah Game API (Udacity Full Stack Nanodegree, Project 4 submission)

## Set-Up Instructions:
1.  Update the value of application in app.yaml to the app ID you have registered
 in the App Engine admin console and would like to use to host your instance of this sample.
1.  Run the app with the devserver using dev_appserver.py DIR, and ensure it's
 running by visiting the API Explorer - by default localhost:8080/_ah/api/explorer.
1.  (Optional) Generate your client library(ies) with the endpoints tool.
 Deploy your application.
 
 
 
##Game Description:
Kalah is a game in the mancala family invented by William Julius Champion, Jr.
This game API implements Kalah(6, 3) without the "Empty Capture" rule.
The rules are as follows:


> 1. At the beginning of the game, three seeds are placed in each house. This is
> the traditional method.
> 2. Each player controls the six houses and their seeds on the player's side of
> the board. The player's score is the number of seeds in the store to their
> right.
> 3. Players take turns sowing their seeds. On a turn, the player removes all
> seeds from one of the houses under their control. Moving counter-clockwise,
> the player drops one seed in each house in turn, including the player's own 
> store but not their opponent's.
> 4. If the last sown seed lands in an empty house owned by the player, and the
> opposite house contains seeds, both the last seed and the opposite seeds are 
> captured and placed into the player's store.
> 5. If the last sown seed lands in the player's store, the player gets an 
> additional move. There is no limit on the number of moves a player can make in
> their turn.
> 6. When one player no longer has any seeds in any of their houses, the game 
> ends. The other player moves all remaining seeds to their store, and the
> player with the most seeds in their store wins.
>
> It is possible for the game to end in a draw.
>
> https://en.wikipedia.org/wiki/Kalah#Rules

The Kalah board is internally represented a tuple of 14 integers, with indexes 0-5
representing the South player's houses, indexes 7-12 representing the North
player's houses, index 6 representing the South player's store, and index 13
representing the North player's store.

```
       <--- North
------------------------    
 12  11  10   9   8   7     
                         
 13                   6    
                        
  0   1   2   3   4   5      
------------------------     
        South --->
``` 

The game state at any particular point in the game is internally representing by a tuple
of the form `(player who moves next, board)`. The player who moves next is
represented as either `'N'` for the northern player or `'S'` for the southern
player.

In terms of the API, the game state is represented to the client by a `GameForm`,
with the `next_to_play` field giving the player who moves next, and the `board` 
field giving the state of the board.

'Moves' are sent to the `make_move` endpoint, specifying the index of the house
chosen. The `make_move` endpoint will reply with the resulting
game state, or an error if the move is invalid.

Many different Kalah games can be played by many different pairs of Users at any
given time. Each game can be retrieved or played by using the path parameter
`urlsafe_game_key`.

##Files Included:
 - kalah.py: Handles the game logic.
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will 
    raise a ConflictException if a User with that user_name already exists.
 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: north_user_name, south_user_name
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. The usernames provided must correspond to
    existing users, or they will raise a NotFoundException.
 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.
 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, user_name, house
    - Returns: GameForm with new game state, or with error message.
    - Description: Accepts a 'move' and returns the updated state of the game.
 - **get_user_games**
    - Path: 'user/games'
    - Method: GET
    - Parameters: user_name, email (optional)
    - Returns: GamesForm providing a list of games associated with given user.
 - **cancel_game**
    - Path: 'game/{urlsafe_game_key}/cancel'
    - Method: PUT
    - Parameters: urlsafe_game_key
    - Returns: StringMessage confirming cancellation of game.
    - Errors:
        - endpoints.ForbiddenException (403) if the game is already
          completed or canceled.
        - endpoints.NotFoundException (404) if the game cannot be found in 
          datastore.
 - **get_user_rankings**
     - Path: 'rankings'
     - Method: GET
     - Parameters: none
     - Returns: UserRankingsForm, giving a descending ranking of Users by
       ratio of wins to losses, with ties broken by the greater number of
       draws.
 - **get_game_history**
     - Path: 'history/{urlsafe_game_key}'
     - Method: GET
     - Parameters: urlsafe_game_key, verbose (default: False)
     - Returns: GameHistoryForm, giving a list of integers representing
       the house chosen on each turn.
 - **get_completed_games**
     - Path: 'games/completed'
     - Method: GET
     - Parameters: none
     - Returns: GamesForm providing list of all completed games.

##Models Included:
 - **User**
    - Stores unique user_name and (optional) email address.
 - **Game**
    - Stores game states. Associated with User model via KeyProperty, storing
      north user and south user.
    
##Forms Included:
 - **GameForm**
    - Represents current game state.
    - Fields:
        - urlsafe_key (string)
        - game_over (true/false)
        - canceled (true/false)
        - message (string)
        - north_user_name (string)
        - south_user_name (string)
        - next_to_play (string)
            + "N" if the North player plays next, otherwise "S" if the
              South player plays next.
        - board (array)
            + List of integers representing the state of the Kalah board
        - pretty_board (array of strings)
            + Used in order to display the board prettily and readably in Google API explorer, together with a legend showing the number of each house.
        - north_final_score (integer)
            + (Only once game has finished)
        - south_final_score (integer)
            + (Only once game has finished)
 - **NewGameForm**
    - Used to create a new game (north_user_name, south_user_name).
 - **MakeMoveForm**
    - Used to make a move (house, user_name).
 - **GamesForm**
    - Provides a list of GameForms.
 - **UserRankingInfoForm**
     - Provides ranking info for individual Users (name, win_loss_ratio).
 - **UserRankingsForm**
     - Provides a list of UserRankingInfoForm forms.
 - **MoveForm**
     - Provides a more verbose description of a move, for use in displaying verbose history.
     - Fields:
       + player (string, either 'N' or 'S')
       + house (integer)
 - **GameHistoryForm**
     - Provides a list of moves giving the history of a game. Each move
       is given as an integer representing the house chosen in that turn.
     - Fields:
       + urlsafe_key (string)
       + history (array of integers)
       + verbose_history (array of `MoveForms`)
         * Optional: only if verbose history requested
       + north_user_name (string)
         * Optional: only if verbose history requested
       + south_user_name (string)
         * Optional: only if verbose history requested
 - **StringMessage**
    - General purpose String container.

##Third-party code
 - The code for the "Guess a Number" sample project in
 [udacity/FSND-P4-Design-A-Game]
 (https://github.com/udacity/FSND-P4-Design-A-Game) was used as the starting
 point for this Kalah project.
    - `utils.get_by_urlsafe` was used as provided, without modification.
    - The code for the `get_game` endpoint was used as provided.
    - The code for the `create_user` endpoint was used as provided.