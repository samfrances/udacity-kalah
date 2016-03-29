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


class Game(ndb.Model):
    """Game object"""
    north_user = ndb.KeyProperty(required=True, kind='User')
    south_user = ndb.KeyProperty(required=True, kind='User')
    game_state = ndb.PickleProperty(required=True)
    game_over = ndb.BooleanProperty(required=True, default=False)
    north_final_score = ndb.IntegerProperty(required=False)
    south_final_score = ndb.IntegerProperty(required=False)

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

    def move(self, house):
        """Accepts move, updates game state, returns a GameForm.
        TODO: test"""
        # Calculate result of move
        old_game_state = self.game_state
        new_game_state = kalah.move(old_game_state, house)

        # Check if the game is over
        final_scores = kalah.winner(new_game_state)
        if final_scores:
            self.game_over = True
            self.south_final_score = final_scores[0]
            self.north_final_score = final_scores[1]

        # Update game state
        self.game_state = new_game_state

        # Save changes to database
        self.put()

        return self


    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.north_user_name = self.north_user.get().name
        form.south_user_name = self.south_user.get().name
        form.game_over = self.game_over
        form.message = message
        form.next_to_play = self.game_state[0]
        form.board = self.game_state[1]
        if self.south_final_score:
            form.south_final_score = self.south_final_score
        if self.north_final_score:
            form.north_final_score = self.north_final_score
        return form

#     def end_game(self, won=False):
#         """Ends the game - if won is True, the player won. - if won is False,
#         the player lost."""
#         self.game_over = True
#         self.put()
#         # Add the game to the score 'board'
#         score = Score(user=self.user, date=date.today(), won=won,
#                       guesses=self.attempts_allowed - self.attempts_remaining)
#         score.put()


# class Score(ndb.Model):
#     """Score object"""
#     user = ndb.KeyProperty(required=True, kind='User')
#     date = ndb.DateProperty(required=True)
#     won = ndb.BooleanProperty(required=True)
#     guesses = ndb.IntegerProperty(required=True)

#     def to_form(self):
#         return ScoreForm(user_name=self.user.get().name, won=self.won,
#                          date=str(self.date), guesses=self.guesses)



# - - - Message Forms - - - - - - - - - - - - - - - -

class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    game_over = messages.BooleanField(2, required=True)
    message = messages.StringField(3, required=True)
    north_user_name = messages.StringField(4, required=True) # TODO: Check if necessary
    south_user_name = messages.StringField(5, required=True) # TODO: Check if necessary
    next_to_play = messages.StringField(6, required=True)
    board = messages.IntegerField(7, repeated=True,
                                  # Required to overcome bug which represented
                                  # integers as strings in JSON response:
                                  variant=messages.Variant.INT32)
    north_final_score = messages.IntegerField(8, required=False,
                                              variant=messages.Variant.INT32)
    south_final_score = messages.IntegerField(9, required=False,
                                              variant=messages.Variant.INT32)


class NewGameForm(messages.Message):
    """Used to create a new game"""
    north_user_name = messages.StringField(1, required=True)
    south_user_name = messages.StringField(2, required=True)

class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    house = messages.IntegerField(1, required=True)
    user_name = messages.StringField(2, required=True)


# class ScoreForm(messages.Message):
#     """ScoreForm for outbound Score information"""
#     user_name = messages.StringField(1, required=True)
#     date = messages.StringField(2, required=True)
#     won = messages.BooleanField(3, required=True)
#     guesses = messages.IntegerField(4, required=True)


# class ScoreForms(messages.Message):
#     """Return multiple ScoreForms"""
#     items = messages.MessageField(ScoreForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
