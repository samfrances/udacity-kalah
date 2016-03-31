"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
# from datetime import date
from protorpc import messages
from google.appengine.ext import ndb
import kalah

# - - - Datastore models - - - - - - - - - - - - -

class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email =ndb.StringProperty()
    # To allow for ranking of users:
    wins = ndb.IntegerProperty(required=True, default=0)
    losses = ndb.IntegerProperty(required=True, default=0)
    draws = ndb.IntegerProperty(required=True, default=0)
    win_loss_ratio = ndb.ComputedProperty(
        lambda self: (float(self.wins) / (self.wins + self.losses))
                     if self.wins + self.losses > 0
                     else 0.0 )

    def get_games(self, active_only=True):
        """Gets a user's games, by default only those which
        have not finished or been canceled."""
        qry = Game.query(ndb.OR(Game.north_user == self.key,
                                Game.south_user == self.key))
        if active_only:
            qry = qry.filter(Game.active == True)
        return qry.fetch()

    def record_result(self, result):
        """Record win, loss or draw. 
        A result of -1 represents a loss, 0 a draw, 1 a win"""
        if result not in (-1, 0, 1):
            raise ValueError("Result must be -1, 0 or 1")
        if result == -1:
            self.losses += 1
        if result == 0:
            self.draws += 1
        if result == 1:
            self.wins += 1
        self.put()

    def to_ranking_form(self):
        """Returns a UserRankingInfoForm with ranking info about the User."""
        form = UserRankingInfoForm()
        form.name = self.name
        form.win_loss_ratio = self.win_loss_ratio
        return form

    @classmethod
    def rankings(cls):
        """Return UserRankingsForm ordering users by win to loss ratio,
        with greater number of draws used to break ties."""
        qry = cls.query().order(-cls.win_loss_ratio, -cls.draws)
        return UserRankingsForm(rankings=[user.to_ranking_form()
                                             for user in qry.fetch()])

class Game(ndb.Model):
    """Game object"""
    north_user = ndb.KeyProperty(required=True, kind='User')
    south_user = ndb.KeyProperty(required=True, kind='User')
    game_state = ndb.PickleProperty(required=True)
    game_over = ndb.BooleanProperty(required=True, default=False)
    canceled = ndb.BooleanProperty(required=True, default=False)
    # Included to overcome query restrictions outlawing inequality
    # filters on more than one property:
    active = ndb.ComputedProperty(
        lambda self: (not self.game_over) and (not self.canceled))
    north_final_score = ndb.IntegerProperty(required=False)
    south_final_score = ndb.IntegerProperty(required=False)
    history = ndb.IntegerProperty(repeated=True) # move history

    @classmethod
    def new_game(cls, north_user, south_user):
        """Creates and returns a new game."""
        new_game_state = kalah.newGame(north_starts=random.choice([True, False]))
        game = cls(north_user=north_user,
                   south_user=south_user,
                   game_state=new_game_state,
                   game_over=False)
        game.put()
        return game

    @ndb.transactional(xg=True)
    def move(self, house):
        """Accepts move, updates game state, returns a GameForm."""
        # Calculate result of move.
        # ValueError will be raised by kalah.move if move is invalid
        old_game_state = self.game_state
        new_game_state = kalah.move(old_game_state, house)

        # record move history
        self.history.append(house)

        # Check if the game is over
        final_scores = kalah.winner(new_game_state)
        if final_scores:
            self.game_over = True
            self.south_final_score = final_scores[0]
            self.north_final_score = final_scores[1]

            # Update user ranking info
            # win is 1, lose is -1, draw is 0
            if final_scores[0] == final_scores[1]:
                north_result = south_result = 0
            elif final_scores[0] < final_scores[1]:
                north_result = 1
                south_result = -1
            else:
                north_result = -1
                south_result = 1
            self.north_user.get().record_result(north_result)
            self.south_user.get().record_result(south_result)

        # Update game state
        self.game_state = new_game_state

        # Save changes to database
        self.put()

        return self

    def cancel(self):
        """Cancels the game if it is not already finished or canceled.
        If the game is already finished or canceled, raises an
        AttributeError"""
        if self.game_over:
            raise AttributeError("Cannot cancel game once it has already finished.")
        if self.canceled:
            raise AttributeError("Game already canceled.")
        else:
            self.canceled = True
            self.put()

    def to_form(self, message=''):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.north_user_name = self.north_user.get().name
        form.south_user_name = self.south_user.get().name
        form.game_over = self.game_over
        form.canceled = self.canceled
        form.message = message
        form.next_to_play = self.game_state[0]
        form.board = self.game_state[1]
        if self.south_final_score:
            form.south_final_score = self.south_final_score
        if self.north_final_score:
            form.north_final_score = self.north_final_score
        return form

    def to_history_form(self):
        """Returns a GameHistoryForm detailing the move history of the Game,
        as a list of houses chosen on each turn."""
        form = GameHistoryForm()
        form.urlsafe_key = self.key.urlsafe()
        form.history = self.history
        return form 


# - - - Message Forms - - - - - - - - - - - - - - - -

class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    game_over = messages.BooleanField(2, required=True)
    canceled = messages.BooleanField(3, required=True)
    message = messages.StringField(4, required=True)
    north_user_name = messages.StringField(5, required=True) # TODO: Check if necessary
    south_user_name = messages.StringField(6, required=True) # TODO: Check if necessary
    next_to_play = messages.StringField(7, required=True)
    board = messages.IntegerField(8, repeated=True,
                                  # Required to overcome bug which represented
                                  # integers as strings in JSON response:
                                  variant=messages.Variant.INT32)
    north_final_score = messages.IntegerField(9, required=False,
                                              variant=messages.Variant.INT32)
    south_final_score = messages.IntegerField(10, required=False,
                                              variant=messages.Variant.INT32)


class NewGameForm(messages.Message):
    """Used to create a new game"""
    north_user_name = messages.StringField(1, required=True)
    south_user_name = messages.StringField(2, required=True)

class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    house = messages.IntegerField(1, required=True)
    user_name = messages.StringField(2, required=True)

class GamesForm(messages.Message):
    """Form for outbound list of games"""
    games = messages.MessageField(GameForm, 1, repeated=True)

class UserRankingInfoForm(messages.Message):
    """Form for outbound ranking info about an individual User"""
    name = messages.StringField(1, required=True)
    win_loss_ratio = messages.FloatField(2, required=True)

class UserRankingsForm(messages.Message):
    """Form for outbound User ranking list"""
    rankings = messages.MessageField(UserRankingInfoForm, 1, repeated=True)

class GameHistoryForm(messages.Message):
    """Form for outbound Game history records."""
    urlsafe_key = messages.StringField(1, required=True)
    history = messages.IntegerField(2, repeated=True, 
                                    variant=messages.Variant.INT32)

class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
