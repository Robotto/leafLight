#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#from: https://github.com/stvhwrd/Ticker
"""Show live scores of today's NHL games"""
import datetime
import json
import time

import requests
import dateutil.parser, dateutil.tz as tz


class Game:
    """Game represents a scheduled NHL game"""
    def __init__(self, game_info):
        """Parse JSON to attributes"""
        self.game_id     = str(game_info['id'])
        self.game_clock  = game_info['ts']
        self.game_stage  = game_info['tsc']
        self.game_status = game_info['bs']
        self.away_locale = fix_locale(game_info['atn'])
        self.away_name   = fix_name(game_info['atv'])
        self.away_score  = game_info['ats']
        self.away_result = game_info['atc']
        self.home_locale = fix_locale(game_info['htn'])
        self.home_name   = fix_name(game_info['htv'])
        self.home_score  = game_info['hts']
        self.home_result = game_info['htc']

        if self.is_scheduled_for_today() and not (self.isLive() or self.isOver() or self.preGame()):
            dt = datetime.datetime.now(dateutil.tz.gettz('US/Pacific'))
            yyyymmdd = int(dt.strftime("%Y%m%d"))

            #Parse game start times in local time (in this case CE(S)T:
            timeToParse = f"{self.game_status} {yyyymmdd}"
            parsedTime = dateutil.parser.parse(timeToParse).replace(tzinfo=tz.gettz('US/Eastern'))  # set proper timezone
            if parsedTime.timetuple().tm_isdst:  # Adjust for EST/EDT discrepancy, if DST is active in ET.
                parsedTime += datetime.timedelta(hours=1)
            unix = parsedTime.timestamp()
            self.start = int(unix)
            self.game_clock=time.strftime('%H:%M - %Z')

        # Playoff-specific game information
        if '03' in self.game_id[4:6]:
            self.playoffs            = True
            self.playoff_round       = self.game_id[6:8]
            self.playoff_series_id   = self.game_id[8:9]
            self.playoff_series_game = self.game_id[9]
        else:
            self.playoffs = False


    def get_scoreline(self):
        """Get current score in butterfly format"""
        score = self.away_name + ' ' + self.away_score + \
                " - " + self.home_score + ' ' + self.home_name
        return score


    def get_matchup(self):
        """Get full names of both teams"""
        matchup = self.away_locale + ' ' + self.away_name + \
                  ' visiting ' + self.home_locale + ' ' + self.home_name
        return matchup


    def get_playoff_info(self):
        """Get title of playoff series"""
        playoff_info = playoff_series_info(self.playoff_round, self.playoff_series_id)
        playoff_info += ' -- GAME ' + self.playoff_series_game
        return playoff_info


    def get_clock(self):
        """Get game clock and status"""
        clock = self.game_clock + ' (' + self.game_status + ')'
        return clock


    def is_scheduled_for(self, date):
        """True if this game is scheduled for the given date"""
        if date.upper() in self.game_clock:
            return True
        else:
            return False

    def isLive(self):
        return 'LIVE' in self.game_status

    def isOver(self):
        return 'FINAL' in self.game_status

    def preGame(self):
        return 'PRE GAME' in self.game_clock

    def normalize_today(self):
        date = get_date(0)

        # must be today
        if date.upper() in self.game_clock or \
                'TODAY' in self.game_clock:
            self.game_clock = 'TODAY'
            return True
        # or must be pre-game
        elif 'PRE GAME' in self.game_clock:
            self.game_clock = 'PRE-GAME'
            return True
        # or game must be live
        elif 'LIVE' in self.game_status:
            return True
        return False


    def is_scheduled_for_today(self):
        """True if this game is scheduled for today"""
        if self.normalize_today():
            return True
        else:
            return False

'''
            for game in games:
                game_summary = '\n'
                if game.playoffs is True:
                    game_summary += Style.BRIGHT + game.get_playoff_info(width) + '\n' \
                                    + Style.RESET_ALL + (''.center(width, '-')) + '\n'

                game_summary += Fore.GREEN + game.get_matchup(width) + '\n' \
                                + Fore.YELLOW + game.get_clock(width) + '\n'
'''
def get_date(delta):
    """Build a date object with given day offset"""
    date = datetime.datetime.now()
    if delta is not None:
        offset = datetime.timedelta(days=delta)
        date = date + offset
    date = date.strftime('%A %#m/%#d')
    return date

def fix_locale(team_locale):
    """Expand and fix place names from the values in JSON"""
    if 'NY' in team_locale:
        team_locale = 'New York'
    elif 'Montr' in team_locale:
        team_locale = 'Montréal'
    return team_locale.title()


def fix_name(team_name):
    """Expand team names from the values in JSON"""
    if 'wings' in team_name:
        team_name = 'Red Wings'
    elif 'jackets' in team_name:
        team_name = 'Blue Jackets'
    elif 'leafs' in team_name:
        team_name = 'Maple Leafs'
    elif 'knights' in team_name:
        team_name = 'Golden Knights'
    return team_name.title()

# Originally forked from John Freed's NHL-Scores - https://github.com/jtf323/NHL-Scores
