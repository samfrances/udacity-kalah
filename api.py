# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""


# import logging
import endpoints
from protorpc import remote, messages
# from google.appengine.api import memcache
from google.appengine.api import taskqueue

from models import User, Game#, Score
from models import StringMessage, NewGameForm, GameForm, MakeMoveForm,\
    GamesForm, UserRankingsForm, GameHistoryForm#, ScoreForms
from utils import get_by_urlsafe
import kalah

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
GAME_HISTORY_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),
        verbose=messages.BooleanField(2, default=False))
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2),
                                           active_only=messages.BooleanField(3, default=True))

# MEMCACHE_MOVES_REMAINING = 'MOVES_REMAINING'

@endpoints.api(name='kalah', version='v1')
class KalahApi(remote.Service):
    """Game API"""
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        north_user = self.get_user_or_error(request.north_user_name)
        south_user = self.get_user_or_error(request.south_user_name)
        game = Game.new_game(north_user.key, south_user.key)

        # Use a task queue to update the average attempts remaining.
        # This operation is not needed to complete the creation of a new game
        # so it is performed out of sequence.
        #taskqueue.add(url='/tasks/cache_average_attempts')
        return game.to_form('Good luck playing Kalah!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            if game.active:
                return game.to_form('Time to make a move!')
            else:
                return game.to_form('')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)

        # Check if game is finished or canceled.
        if game.game_over:
            return game.to_form('Game already over.')
        if game.canceled:
            return game.to_form('Cannot move because Game has been canceled.')

        # Check player exists
        moving_user = self.get_user_or_error(request.user_name)
        moving_user_id = moving_user.key.id()

        # Check player a participant in game
        if moving_user_id != game.north_user.id():
            if moving_user_id != game.south_user.id():
                return game.to_form('Player not a participant in this game.')

        # Check the move is made by the player who's turn it is
        if game.game_state[0] == 'N':
            legitimate_moving_user_id = game.north_user.id()
        else:
            legitimate_moving_user_id = game.south_user.id()
        
        if moving_user_id != legitimate_moving_user_id:
            return game.to_form('Player moved out of turn.')

        # Try making the move, return error message if invalid
        try:
            game = game.move(request.house)
        except ValueError:
            return game.to_form('Invalid move.')

        # Check if the game is over, and create appropriate message
        msg = ''
        if game.game_over:
            msg = 'Game over! '
            if game.north_final_score > game.south_final_score:
                winner_name = game.north_user.get().name
                msg += '{} wins!'.format(winner_name)
            elif game.south_final_score > game.north_final_score:
                winner_name = game.south_user.get().name
                msg += '{} wins!'.format(winner_name)
            else:
                msg += "Draw!"
        else: # If the game isn't over
            # send a reminder to the next player
            taskqueue.add(url='/tasks/send_reminder', params={'urlsafe_key': game.key.urlsafe()})

            # Create an appropriate message
            msg_params = ("North", 7, 12) if game.game_state[0] == 'N' else ("South", 0, 5)
            msg = "{} player's turn. Enter an integer between {} and {}.".format(*msg_params)


        return game.to_form(msg)

    def get_user_or_error(self, user_name):
        """Get user with given user name or raise API error"""
        user = User.query(User.name == user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with the name {} does not exist!'.format(
                        user_name))
        return user

# = = = Task 3: Extend Your API = = = = = = = = =

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GamesForm,
                      path='user/games',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Get a user's active games."""
        user = self.get_user_or_error(request.user_name)
        games = user.get_games(active_only=request.active_only)
        return GamesForm(games=[game.to_form() for game in games])

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}/cancel',
                      name='cancel_game',
                      http_method='PUT')
    def cancel_game(self, request):
        """Cancels the specified game, returning an error
        if the game is already over or canceled."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            try:
                game.cancel()
                return StringMessage(message='Game successfully canceled.')
            except AttributeError as e:
                raise endpoints.ForbiddenException(e.message)
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(response_message=UserRankingsForm,
                      path='rankings',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Retrieve user rankings, according to win:loss ratio,
        with ties broken by greatest number of draws."""
        return User.rankings()

    @endpoints.method(request_message=GAME_HISTORY_REQUEST,
                      response_message=GameHistoryForm,
                      path='history/{urlsafe_game_key}',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Retrieve move history for a particular Game."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_history_form(request.verbose)
        else:
            raise endpoints.NotFoundException('Game not found!')

# = = = Extra endpoints in response to comments = = = = = = = = =

    @endpoints.method(response_message=GamesForm,
                      path='games/completed',
                      name='get_completed_games',
                      http_method='GET')
    def get_completed_games(self, request):
        """Retrieve all completed games."""
        games = Game.query(Game.game_over == True).fetch()
        return GamesForm(games=[game.to_form() for game in games])

api = endpoints.api_server([KalahApi])
