#!/usr/bin/env python

#copied from here: https://gist.github.com/criccomini/3805436#file-gistfile1-py via https://riccomini.name/streaming-live-sports-schedule-scores-stats-api

from dateutil import tz
import pytz
import datetime
import time
import urllib.request, urllib.error, urllib.parse
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

def today(league,dt):

    yyyymmdd = int(dt.strftime("%Y%m%d"))
    timestamp = int(round(time.time() * 1000))

    #print timestamp

    games = []

    #try:
    f = urllib.request.urlopen(url % (league, yyyymmdd,timestamp))
    jsonp = f.read().decode('utf8')
    f.close()
    json_str = jsonp.replace("shsMSNBCTicker.loadGamesData(", "").replace(");", "")
    #print json_str
    json_parsed = json.loads(json_str)
    for game_str in json_parsed.get('games', []):
        game_tree = ET.XML(game_str)
        visiting_tree = game_tree.find('visiting-team')
        home_tree = game_tree.find('home-team')
        gamestate_tree = game_tree.find('gamestate')
        home = home_tree.get('nickname')
        away = visiting_tree.get('nickname')
        os.environ['TZ'] = 'US/Eastern' # OH MY GOD!
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
    #except Exception as e:
    #    print(e)


    if not games:
        print(dt.date(),': no games')

#        recursionCount=(dt - datetime.datetime.now(pytz.timezone('US/Pacific'))).days+1
        recursionCount=(dt - datetime.datetime.now(tz.gettz('US/Pacific'))).days+1

        print(f"Currently checking {recursionCount} days in the future")
        if recursionCount>28:
            print('Hit recursion limit. Returning empty set.')
            return [] #will this fail?
        return today(league,dt + datetime.timedelta(days=1)) #recursive call with date incremented
    #print games
    return games

def generateReport(focusTeam,localTimeZone):
    #dt=datetime.datetime.now(pytz.timezone('US/Pacific'))
    dt=datetime.datetime.now(tz.gettz('US/Pacific'))
    report = None
    rawList = today('NHL',dt)
    #print(f'>>> DEBUG: {rawList}')
    try:
        for index,game in enumerate(rawList):
            if game!=None:
                print(f'{index}:{game}')
                if game["home"] == focusTeam or game["away"] == focusTeam:
                    print('\nMATCH!\n')
                    if game["status"] == 'In-Progress': #active focusteam games in list
                        report = f'1#{game["home"]}#{game["away"]}#{game["home-score"]}#{game["away-score"]}#{game["clock-section"]}#\r'
                    elif game["status"] == "Pre-Game": #no active focusteam game in list
                        report = f'0#{game["home"]}#{game["away"]}#{datetime.datetime.fromtimestamp(game["start"],tz=tz.gettz(localTimeZone))}#\r'

            if report!=None:
                print(f'Matched {focusTeam} @ game number {index}')#: {game}')
                return report

    except Exception as e:
        print(f'>>> error in generation of report.. (empty data set?): {e}')
        pass
    print(f'>>> no games with {focusTeam} in set.')
    return 'e' + '\r'

if __name__ == "__main__":

    print(f'{time.ctime()}: startup!')


    TCP_IP = socket.gethostbyname(socket.gethostname())

    TCP_PORT = 9999
    BUFFER_SIZE = 128  # Normally 1024, but we want fast response

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)  # make socket reuseable, for debugging (enables you to rerun the program before the socket has timed out)
    s.bind((TCP_IP, TCP_PORT))
    s.listen(1)

    print(f'Done.. Opening TCP port {TCP_PORT} on IP: {TCP_IP}')

    while True:
        try:
            conn, addr = s.accept()
            print(f'{time.ctime()}: Connection from: {addr}')
            #if str(addr) != '80.167.171.117':
            #    print 'Wrong client IP. Connection refused'
            #    conn.shutdown(socket.SHUT_RDWR)
            #    conn.close()
            #    continue

            #            while True:  # looks like connection timeout is ~60 seconds.

            print(f'Looking for Maple Leafs games...')
            report = generateReport(focusTeam = 'Maple Leafs', localTimeZone='Europe / Berlin')
            conn.send(report.encode('utf-8'))  # +'\n')  # echo
            print(f'TX: {report}')
            print('Closing connection')
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()

            print('--------------------------')
            print()


        except Exception as e:
            # print "hmm.. It looks like there was an error: " + str(e)
            print(f'{time.ctime()}: Client disconnected... : {e}')
            print('--------------------------')
            conn.close()
