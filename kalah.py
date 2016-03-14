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
	end-zone, 	the integer at index 13 represents the northern player's
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
	player = game_state[0]
	if house not in HOUSES[player]:
		return False
	return True

def _sow(board, house):
	"""Sows seeds, without considering whose move it is or whether the move
	is valid."""
	seeds = board[house]
	houses_to_increment = range(house+1, house+seeds+1)
	new_board = tuple([n + 1 for i, n in emumerate(board)
				 	   if i in houses_to_increment
				 	   else 0 if i == house
				 	   else n)
	return new_board

def _capture_opposites(board, last_house_sown, player):
	if last_house_sown not in HOUSES[player]:
		return board

	winning_store = STORES[player]
	new_score = (board[winning_store] + board[last_house_sown] 
	   	         + board[OPPOSITE_HOUSES[last_house_sown]]) 
	new_board = tuple([0 for i, n in enumerate(board)
					   if i in (last_house_sown,
					   			OPPOSITE_HOUSES[last_house_sown])
					   else new_score if i == winning_store
					   else n)

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
	new_board = _capture_opposites(new_board, last_house_sown, player)

	# If the last sown seed lands in the player's store, the player gets an
	# additional move.
	if last_house_sown = STORES[player]:
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