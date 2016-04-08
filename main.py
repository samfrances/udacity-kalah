#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import logging

import webapp2
from google.appengine.api import mail, app_identity
from api import KalahApi

from utils import get_by_urlsafe
from models import Game, User


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
        
        if user.email:
            subject = 'Your turn to play, {}!'.format(user.name)
            body = 'Hello {}, it\'s your turn to play in your game against {}!'
            body = body.format(user.name, opponent.name)
            # This will send test emails, the arguments to send_mail are:
            # from, to, subject, body
            mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                           user.email,
                           subject,
                           body)

class SendRankingEmail(webapp2.RequestHandler):
    def get(self):
        """Send an email to all users giving the user rankings"""
        app_id = app_identity.get_application_id()
        users = User.query(User.email != None).fetch()
        rankings = User.query().order(-User.win_loss_ratio, -User.draws).fetch()

        # Create rankings table
        rankings_format = "{:<15}{:<15}\n"
        header = rankings_format.format("Name", "Win/loss ratio")
        lines = [rankings_format.format(user.name, user.win_loss_ratio) for user in rankings]
        table = header + ''.join(lines)

        # Email users
        for user in users:
            subject = 'Kalah rankings'
            body = "Hello {}, here is an update on Kalah rankings:\n\n".format(user.name)
            body += table
            
            mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                           user.email,
                           subject,
                           body)

app = webapp2.WSGIApplication([
    ('/tasks/send_reminder', SendReminderEmail),
    ('/crons/send_rankings_update', SendRankingEmail)
], debug=True)
