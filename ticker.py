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
        self.gameJson = game_info
        '''
        #Dict keys in old API:
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
        self.away_score = 0
        self.home_score = 0
        self.home_name = game_info['homeTeam']['commonName']['default']
        self.home_locale = game_info['homeTeam']['placeNameWithPreposition']['default']

        if self.isLive() or self.isOver():
            try:
                self.away_score = game_info['awayTeam']['score']
                self.home_score = game_info['homeTeam']['score']
            except:
                print(f"Gamestate: {self.game_status}, But no score keys in dict... yet")
        if self.isLive():
            #'period': 1, 'periodDescriptor': {'number': 1, 'periodType': 'REG', 'maxRegulationPeriods': 3}, 'clock': {'timeRemaining': '20:00', 'secondsRemaining': 1200, 'running': False, 'inIntermission': False}}
            try:
                self.period = game_info['period']
                self.periodCountdown = game_info['clock']['timeRemaining']
            except:
                print(f'expected period and clock info when gamestate is {self.game_status}, but failed...')
                if self.period is None:
                    self.period = 0
                if self.periodCountdown is None:
                    self.periodCountdown = "00:00"

        self.startTimeUTC = datetime.datetime.fromisoformat(game_info['startTimeUTC'][:-1] + '+00:00')
        self.start = self.startTimeUTC.timestamp()
        self.startCountDown = int(self.start-time.time())
        #print(f'Game starts in {self.startCountDown} seconds')
        self.gameDate = game_info['gameDate']


    def get_scoreline(self):
        """Get current score in butterfly format"""
        score = self.away_name + ' '*(15-len(self.away_name)) + str(self.away_score) + \
                " - " + str(self.home_score) + '\t' + self.home_name + ' '*(15-len(self.home_name))
        return score

    def get_periodline(self):

        if self.period>3:
            P='OT'
        else:
            P="P"+str(self.period)
        return f'{P}: T-{self.periodCountdown}'


    def get_matchup(self):
        """Get full names of both teams"""
        matchup = self.away_locale + ' ' + self.away_name + \
                  ' visiting ' + self.home_locale + ' ' + self.home_name
        matchup += ' '*(50-len(matchup))
        return matchup

    def leafsWon(self): #returns difference between leaf's score and opponent's score
        if self.isOver():
            if 'Leafs' in self.home_name:
                return self.home_score-self.away_score
            return self.away_score-self.home_score
        return None

    def get_leafsWinString(self): #dilly-dallying with scorecounts and smileys..
        if self.leafsWon()>0:
            return ":D "*self.leafsWon()
        elif self.leafsWon()<0:
            return ":( "*(self.leafsWon()*(-1))
        else:
            return ":|"
    '''
    
    Game states: 
    So far I've seen the following strings: 
    
    'FUT' - Future game
    'PRE' - Pre-game (About 30 minutes before face-off)
    'LIVE'    
    'CRIT'  
    'FINAL' 
    'OFF' - Game over man, game over...
    '''

    def isOver(self):
        return 'OFF' in self.game_status or 'FINAL' in self.game_status

    def preGame(self):
        return 'PRE' in self.game_status

    def futureGame(self):
        return 'FUT' in self.game_status

    def isLive(self):
        return 'LIVE' in self.game_status or 'CRIT' in self.game_status



    def __str__(self):
        if self.isOver():
            return f'{self.startTimeUTC} (GAME OVER): \t\t{self.get_matchup()} \t Result: {self.get_scoreline()} \t\t\t {self.get_leafsWinString()}'
        elif self.preGame():
            return f'{self.startTimeUTC} (PRE-GAME): \t\t{self.get_matchup()}'
        elif self.isLive():
            return f'{self.startTimeUTC} (LIVE GAME): \t\t{self.get_matchup()} \t Score: {self.get_scoreline()}'
        elif self.futureGame():
            return f'{self.startTimeUTC} (FUTURE GAME): \t{self.get_matchup()} in {self.startCountDown} seconds'
        else:
            return f'{self.startTimeUTC} (RAW gameState: \t{self.game_status}):\t\t\t\t {self.get_matchup()}'

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
