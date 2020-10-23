#!/usr/bin/env python

#copied from here: https://gist.github.com/criccomini/3805436#file-gistfile1-py via https://riccomini.name/streaming-live-sports-schedule-scores-stats-api

import pytz
import datetime
import time
import urllib2
import json
import os
import socket
from IPy import IP


# import elementtree.ElementTree as ET
import xml.etree.ElementTree as ET

# Old: http://scores.nbcsports.msnbc.com/ticker/data/gamesMSNBC.js.asp?jsonp=true&sport=MLB&period=20120929

#New: http://scores.nbcsports.com/ticker/data/gamesNEW.js.asp?jsonp=true&sport=NHL&period=20190828&random=1567023796177

#here's a curl for testing:
#curl "http://scores.nbcsports.com/ticker/data/gamesNEW.js.asp?jsonp=true&sport=NHL&period=20190828&random=$(date +%s)000" -vvv

url = 'http://scores.nbcsports.com/ticker/data/gamesNEW.js.asp?jsonp=true&sport=%s&period=%d&random=%d'

focusTeam = 'Maple Leafs' #this program focuses on one specific team.
#focusTeam = 'Blackhawks'

def today(league,dt):

    yyyymmdd = int(dt.strftime("%Y%m%d"))
    timestamp = int(round(time.time() * 1000))

    #print timestamp

    games = []

    try:
        f = urllib2.urlopen(url % (league, yyyymmdd,timestamp))
        jsonp = f.read()
        f.close()
        json_str = jsonp.replace('shsMSNBCTicker.loadGamesData(', '').replace(');', '')
        #print json_str
        json_parsed = json.loads(json_str)
        for game_str in json_parsed.get('games', []):
            game_tree = ET.XML(game_str)
            visiting_tree = game_tree.find('visiting-team')
            home_tree = game_tree.find('home-team')
            gamestate_tree = game_tree.find('gamestate')
            home = home_tree.get('nickname')
            away = visiting_tree.get('nickname')
            os.environ['TZ'] = 'US/Eastern'
            start = int(
                time.mktime(time.strptime('%s %d' % (gamestate_tree.get('gametime'), yyyymmdd), '%I:%M %p %Y%m%d')))
            del os.environ['TZ']

            games.append({
                'league': league,
                'start': start,
                'home': home,
                'away': away,
                'home-score': home_tree.get('score'),
                'away-score': visiting_tree.get('score'),
                'status': gamestate_tree.get('status'),
                'clock': gamestate_tree.get('display_status1'),  # gametime or local time??
                'clock-section': gamestate_tree.get('display_status2')
            })
    except Exception, e:
        print e


    if not games:
        print dt.date(),': no games'


        # print 'dt:', dt
        # print 'now:', datetime.datetime.now(pytz.timezone('US/Pacific'))
        # print 'timedelta:', (dt - datetime.datetime.now(pytz.timezone('US/Pacific'))).days
        recursionCount=(dt - datetime.datetime.now(pytz.timezone('US/Pacific'))).days+1
        print 'currently checking' , recursionCount , 'days in the future'
        if recursionCount>28:
            print 'Hit recursion limit. Returning empty set.'
            return [] #will this fail?
        return today(league,dt + datetime.timedelta(days=1)) #recursive call with date incremented
    #print games
    return games

def generateReport():
    dt=datetime.datetime.now(pytz.timezone('US/Pacific'))
    report=None
    print '>>> DEBUG:'
    try:
        for index,game in enumerate(today('NHL',dt)):
            if game!=None:
                print index, ':', game
        #for game in today('NHL'):
            if game['home'] == focusTeam or game['away'] == focusTeam:
                if game['status'] == 'In-Progress': #active focusteam games in list
                    report = '1' + '#' + game['home'] + '#' + game['away'] + '#' + str(game['home-score']) + '#' + str(game['away-score']) + '#' + str(game['clock-section']) + '#' + '\r'
                    #print game['home'] + " [" + str(game['home-score']) + "]" + " vs. " + game['away'] + " [" + str(game['away-score']) + "]" + " in " + game['clock-section'] + " period."
                elif game['status'] == 'Pre-Game': #no active focusteam game in list
                    report = '0' + '#' + game['home'] + '#' + game['away'] + '#' + str(datetime.datetime.fromtimestamp(game['start'])) + '#' + '\r'
                    #print game['home'] + " vs. " + game['away'] + " @ " + str(datetime.datetime.fromtimestamp(game['start']))
                    #print game['home'] + " vs. " + game['away'] + " @ " + str(game['start'])

            if report!=None:
                print 'Matched ' + focusTeam + ' @ game number ' + str(index) #+ ': ' + str(game)
                return report
    except Exception as e:
        print '>>> error in generation of report.. (empty data set?)' , str(e)
        pass
    print '>>> no games with', focusTeam, 'in set.'
    return 'e' + '\r'

if __name__ == "__main__":

    print time.ctime(), "startup!"


    TCP_IP = socket.gethostbyname(socket.gethostname())

    TCP_PORT = 9999
    BUFFER_SIZE = 128  # Normally 1024, but we want fast response

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)  # make socket reuseable, for debugging (enables you to rerun the program before the socket has timed out)
    s.bind((TCP_IP, TCP_PORT))
    s.listen(1)

    print 'Done.. Opening TCP port', TCP_PORT

    while True:
        try:
            conn, addr = s.accept()
            print time.ctime(), 'Connection from:', addr

#            while True:  # looks like connection timeout is ~60 seconds.

            print 'Getting games. Looking for ' + focusTeam + ' games.'
            report = generateReport()

            conn.send(report)  # +'\n')  # echo
            print 'TX:', report

            print 'Closing connection'
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()

            print '--------------------------'
            print 


        except Exception as e:
            # print "hmm.. It looks like there was an error: " + str(e)
            print time.ctime(), 'Client disconnected... :', str(e)
            print '--------------------------'
            conn.close()
