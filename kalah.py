"""Module containing all of the functions necessary for a Kalah(6, 3) game.

This module works in a purely functional manner.

Game state is represented as a tuple of the form (player who moves next,
board). The player who moves next is represented as either 'N' for the
northern player or 'S' for the southern player. The Kalah board is represented
as a tuple of 14 integers (see the documentation for the _newBoard function
for more information on the representation of the Kalah board).

Functions which alter the game state return a new tuple representing the new
game state.

"""

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
	pass

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
	pass

def winner(game_state):
	"""Indicates the winner of the game if either player has won at this stage
	in the game, or if the game is a draw, and returns None if the game is 
	still ongoing.

	Args:
		board: A tuple representing the current game state.

	Returns:
		'N' if the northern player has won.
		'S' if the southern player has won.
		'D' if the game is a draw.
		None if the game is still ongoing.
	"""
	pass