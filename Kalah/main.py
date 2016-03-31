#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import logging

import webapp2
from google.appengine.api import mail, app_identity
from api import KalahApi

from utils import get_by_urlsafe
from models import Game


class SendReminderEmail(webapp2.RequestHandler):
    def post(self):
        """Send a reminder email to a user once their opponent has moved
        using push queue"""
        app_id = app_identity.get_application_id()
        game = get_by_urlsafe(self.request.get('urlsafe_key'), Game)
        # Find out who has the next turn
        if game.game_state[0] == 'N':
            user = game.north_user.get()
            opponent = game.south_user.get()
        else:
            user = game.south_user.get()
            opponent = game.north_user.get()
        
        subject = 'Your turn to play, {}!'.format(user.name)
        body = 'Hello {}, it\'s your turn to play in your game against {}!'
        body = body.format(user.name, opponent.name)
        # This will send test emails, the arguments to send_mail are:
        # from, to, subject, body
        mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                       user.email,
                       subject,
                       body)


# class UpdateAverageMovesRemaining(webapp2.RequestHandler):
#     def post(self):
#         """Update game listing announcement in memcache."""
#         GuessANumberApi._cache_average_attempts()
#         self.response.set_status(204)


app = webapp2.WSGIApplication([
    ('/tasks/send_reminder', SendReminderEmail),
    # ('/tasks/cache_average_attempts', UpdateAverageMovesRemaining),
], debug=True)
