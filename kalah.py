"""Module containing all of the functions necessary for a Kalah(6, 3) game.

This module works in a purely functional manner.

Game state is represented as a tuple of the form (player who moves next,
board). The player who moves next is represented as either 'N' for the
northern player or 'S' for the southern player. The Kalah board is represented
as a tuple of 14 integers (see the documentation for the _newBoard function
for more information on the representation of the Kalah board).

Functions which alter the game state return a new tuple representing the new
game state.

For more information on the rules of the game, see:
https://en.wikipedia.org/wiki/Kalah#Rules

"""

SOUTHERN_HOUSES = range(6)
NORTHERN_HOUSES = range(7,13)
SOUTHERN_STORE = 6
NORTHERN_STORE = 13
STORES = {'N': NORTHERN_STORE,
          'S': SOUTHERN_STORE,
          'All': NORTHERN_STORE}
HOUSES = {'N': NORTHERN_HOUSES,
          'S': SOUTHERN_HOUSES,
          'All': SOUTHERN_HOUSES + NORTHERN_HOUSES}
OPPOSITE_HOUSES = dict(
    zip(SOUTHERN_HOUSES,
        reversed(NORTHERN_HOUSES))
    + zip(NORTHERN_HOUSES,
        reversed(SOUTHERN_HOUSES)))

def newGame(north_starts=True):
    if north_starts:
        first_player = 'N'
    else:
        first_player = 'S'
    board = _newBoard()
    game_state = (first_player, board)
    return game_state

def _newBoard():
    """Return a kalah(6, 3) board, represented as an array of 14 integers,
    where the the integers at index 6 represents the southern player's 
    end-zone,   the integer at index 13 represents the northern player's
    end-zone, and the other integers represent the houses.

           <--- North
    ------------------------    
     12  11  10   9   8   7     
                             
     13                   6    
                            
      0   1   2   3   4   5      
    ------------------------     
            South --->

    The new board is returned in its starting state, as follows:

           <--- North
    ------------------------    
      3   3   3   3   3   3     
                             
      0                   0    
                            
      3   3   3   3   3   3      
    ------------------------     
            South --->

    """
    
    return ((3,)* 6 + (0,)) * 2

def _validateBoard(board):
    """Validate a Kalah board.

    Args:
        board: A Kalah board, represented as a tuple of 14 integers.

    Returns:
        True if the board is valid, False otherwise.
    """
    if len(board) != 14 or sum(board) != 36:
        return False
    return True

def _validateMove(game_state, house):
    player, board = game_state
    if house not in HOUSES[player]:
        return False
    if board[house] == 0:
        return False
    return True

def _sow(board, house):
    """Sows seeds, without considering whose move it is or whether the move
    is valid."""
    seeds = board[house]
    houses_to_increment = [i % 14 for i in range(house+1, house+seeds+1)]
    new_board = tuple(n + 1 if i in houses_to_increment
                      else 0 if i == house
                      else n
                      for i, n in enumerate(board))
    return new_board

def _capture_opposites(board_pre_sowing,
                       board_post_sowing,
                       last_house_sown,
                       player):
    if (last_house_sown not in HOUSES[player]
        or board_pre_sowing[last_house_sown] != 0):
        return board_post_sowing

    winning_store = STORES[player]
    new_score = (board_post_sowing[winning_store]
                 + board_post_sowing[OPPOSITE_HOUSES[last_house_sown]]
                 + 1) 
    new_board = tuple(0 if i in (last_house_sown,
                                 OPPOSITE_HOUSES[last_house_sown])
                      else new_score if i == winning_store
                      else n
                      for i, n in enumerate(board_post_sowing))
    return new_board

def move(game_state, house):
    """Specifies a move on a board, by giving the house from which 'seeds' 
    will be sown.

    Args:
        game_state: A tuple of the form (next player, board) representing the
            game state before the move.
        house: A number between 0 and 5 inclusive for the southern player's
            houses, or 7 and 12 inclusive for the northern player's houses, 
            representing the house from which the player wishes to sow seeds. 
            representing the house.

    Returns:
        A tuple of the form (next player, board), representing the game state
        after the move.
    """
    
    # Check valid move
    if not _validateMove(game_state, house):
        raise ValueError("Invalid Kalah move.")

    player, old_board = game_state

    # Sow seeds
    new_board = _sow(old_board, house)

    # If the last sown seed lands in an empty house owned by the player, and
    # the opposite house contains seeds, both the last seed and the opposite
    # seeds are captured and placed into the player's store.
    last_house_sown = house + old_board[house]
    new_board = _capture_opposites(old_board,
                                   new_board,
                                   last_house_sown,
                                   player)

    # If the last sown seed lands in the player's store, the player gets an
    # additional move.
    if last_house_sown == STORES[player]:
        next_player = player
    else:
        next_player = 'N' if player == 'S' else 'S'

    return (next_player, new_board)



def winner(game_state):
    """Indicates the winner of the game if either player has won at this stage
    in the game, or if the game is a draw, and returns None if the game is 
    still ongoing.

    Args:
        board: A tuple representing the current game state.

    Returns:
        If the game is finished, returns the scores in the form (south, north)
        returns None if the game is still ongoing.
    """
    board = game_state[1]
    north_houses_sum = sum([board[i] for i in NORTHERN_HOUSES])
    south_houses_sum = sum([board[i] for i in SOUTHERN_HOUSES])
    if north_houses_sum == 0 or south_houses_sum == 0:
        north_score = board[NORTHERN_STORE] + north_houses_sum
        south_score = board[SOUTHERN_STORE] + south_houses_sum
        return (south_score, north_score)

def _print_board(board):
    # TODO: Sort out template string to accomodate two digit numbers
    template = """
       <--- North
 ------------------------    
  {12:>2}  {11:>2}  {10:>2}  {9:>2}  {8:>2}  {7:>2}     
                             
  {13:>2}                  {6:>2}    
                            
  {0:>2}  {1:>2}  {2:>2}  {3:>2}  {4:>2}  {5:>2}
 ------------------------     
         South --->
"""
    return template.format(*board)

def _print_board_plus_legend(board):
    board_lines = _print_board(board).split('\n')
    legend_lines = _print_board(range(14)).split('\n')
    lines = ( "{:<30}{:<30}".format(*pair)
              for pair in zip(board_lines, legend_lines) )
    return '\n'.join(lines)

def command_line_game():
    import random
    game_state = newGame(north_starts=random.choice([True, False]))

    while True:
        player, board = game_state
        final_scores = winner(game_state)
        if final_scores:
            print _print_board(board)
            print "South: {}, North: {}".format(*final_scores)
            print "Good game.\n"
            exit()
        print _print_board_plus_legend(board)
        player_name = ('Northern player' if player == 'N'
                       else 'Southern player')
        
        invalid_move = True
        while invalid_move:
            try:
                next_move = int(
                    raw_input("Your move {}: ".format(player_name)))
                new_game_state = move(game_state, next_move)
                invalid_move = False
            except ValueError as e:
                print "Invalid move. Please try again."
        game_state = new_game_state

if __name__ == "__main__":
    command_line_game()