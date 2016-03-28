#Kalah Game API (Udacity Full Stack Nanodegree, Project 4 submission)

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
> [https://en.wikipedia.org/wiki/Kalah#Rules]
> (https://en.wikipedia.org/wiki/Kalah#Rules)

The Kalah board is represented a tuple of 14 integers, with indexes 0-5
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

The game state at any particular point in the game is representing by a tuple
of the form `(player who moves next, board)`. The player who moves next is
represented as either `'N'` for the northern player or `'S'` for the southern
player.

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
 - main.py: Handler for taskqueue handler. TODO: work out if still needed
 - models.py: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string. TODO: work out if still needed

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will 
    raise a ConflictException if a User with that user_name already exists.
    

##Models Included:
 - **User**
    - Stores unique user_name and (optional) email address.
    
##Forms Included:
 - **StringMessage**
    - General purpose String container.

##Third-party code
 - The code for the "Guess a Number" sample project in
 [udacity/FSND-P4-Design-A-Game]
 (https://github.com/udacity/FSND-P4-Design-A-Game) was used as the starting
 point for this Kalah project.