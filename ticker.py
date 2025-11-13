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
        '''
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
        '''
        self.game_id = str(game_info['id'])
        self.game_stage = game_info['venue']['default']
        self.game_status = game_info['gameState']

        self.away_locale = game_info['awayTeam']['placeNameWithPreposition']['default']
        self.away_name = game_info['awayTeam']['commonName']['default']
        self.away_score=0
        self.home_score=0
        self.home_name = game_info['homeTeam']['commonName']['default']
        self.home_locale = game_info['homeTeam']['placeNameWithPreposition']['default']

        if 'FUT' not in self.game_status:
            self.away_score = game_info['awayTeam']['score']
            self.home_score = game_info['homeTeam']['score']



        #self.normalize_today()
        self.startTimeUTC = datetime.datetime.fromisoformat(game_info['startTimeUTC'][:-1] + '+00:00')
        self.start = self.startTimeUTC.timestamp()
        self.gameDate = game_info['gameDate']


    def get_scoreline(self):
        """Get current score in butterfly format"""
        score = self.away_name + ' ' + str(self.away_score) + \
                " - " + str(self.home_score) + ' ' + self.home_name
        return score


    def get_matchup(self):
        """Get full names of both teams"""
        matchup = self.away_locale + ' ' + self.away_name + \
                  ' visiting ' + self.home_locale + ' ' + self.home_name
        return matchup

    def isLive(self):
       # return 'ON' in self.game_status #TODO: Determine what the actual string is...
        return (not self.isOver() and not self.preGame())

    def isOver(self):
        return 'OFF' in self.game_status

    def preGame(self):
        return 'FUT' in self.game_status



    def __str__(self):
        if self.isOver():
            return f'{self.startTimeUTC} (GAME OVER): Result: {self.get_scoreline()}'
        elif self.preGame():
            return f'{self.startTimeUTC} (PRE-GAME): {self.get_scoreline()}'
        elif self.isLive():
            return f'{self.startTimeUTC} (LIVE GAME): {self.get_scoreline()}'
        else:
            return f'{self.startTimeUTC}: {self.away_name} @ {self.home_name}'

'''

def get_date(delta):
    """Build a date object with given day offset"""
    date = datetime.datetime.now()
    if delta is not None:
        offset = datetime.timedelta(days=delta)
        date = date + offset
    date = date.strftime('%A %#m/%#d')
    return date

'''
# Originally forked from John Freed's NHL-Scores - https://github.com/jtf323/NHL-Scores
