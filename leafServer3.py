#!/usr/bin/env python

import dateutil.parser, dateutil.tz as tz
import datetime
import time
import socket
import requests
import json
from ticker import Game

def get_JSON(URL):
    print(f'Requesting JSON from API server ({URL})')
    try:
        response = requests.get(URL)
        # the live.nhle.com/ API has a wrapper, so remove it

        if 'live.nhle' in URL:
            response = response.text.replace('loadScoreboard(', '')
            response = response.replace(')', '')

        response = json.loads(response.text)
        return response

    except Exception as err:
        print(f"Failed to fetch or parse json from {URL}: {err=}, {type(err)=}")
        return None
def getGames():
    #urlString = 'https://live.nhle.com/GameData/RegularSeasonScoreboardv3.jsonp'
    urlString = 'https://api-web.nhle.com/v1/scoreboard/TOR/now' #New url, documentation here: https://github.com/Zmalski/NHL-API-Reference?tab=readme-ov-file

    #Alternative URL for later use: https://api-web.nhle.com/v1/scoreboard/now

    data = get_JSON(urlString)

    games = []

    if data != None:
        for date in data['gamesByDate']:
            for gameJson in date['games']:
                #print(f'Gamestate: {gameJson['gameState']}')
                #print(gameJson['startTimeUTC'])
                #print(gameJson['gameState'])
                #print(gameJson['awayTeam'])
                #print(gameJson['homeTeam'])
                game = Game(gameJson)
                print(f'Parsed JSON @ date {date['date']}; gameState: "{gameJson['gameState']}",    >>> {game} <<<      , Full json: {gameJson}')
                if not game.isOver():
                    games.append(game)
    print(f'Found {len(games)} future or ongoing games!')

    for i in range(len(games)):
        print(f'{i+1}: {games[i]}')
    return games


def generateReport(focusTeam,localTimeZone):
    report = None
    rawList = getGames()

    if len(rawList) != 0:
        for index,game in enumerate(rawList):
            if game!=None:
                print(f'{index+1}:\t {game}')
                if focusTeam in game.get_matchup().lower():
                    if game.isLive(): #active focusteam games in list
                        report = f'1#{game.home_name}#{game.away_name}#{game.home_score}#{game.away_score}#{game.game_status}#\r'
                    elif not game.isOver(): #no active focusteam game in list
                        report = f'0#{game.home_name}#{game.away_name}#{datetime.datetime.fromtimestamp(game.start,tz=tz.gettz(localTimeZone))}#\r'

            if report!=None:
                print(f'Matched {focusTeam} @ game number {index}: {game}')
                return report
    print(f'>>> no current or future games with {focusTeam} in set.')
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

    getGames()

    print(f'Done.. Opening TCP port {TCP_PORT} on IP: {TCP_IP}')

    while True:
        conn, addr = s.accept()
        print(f'{time.ctime()}: Connection from: {addr}')
        #if str(addr) != '80.167.171.117':
        #    print 'Wrong client IP. Connection refused'
        #    conn.shutdown(socket.SHUT_RDWR)
        #    conn.close()
        #    continue

        #            while True:  # looks like connection timeout is ~60 seconds.

        print(f'Looking for Maple Leafs games...')
        report = generateReport(focusTeam = 'leafs', localTimeZone='Europe / Berlin')
        try:
            conn.send(report.encode('utf-8'))  # +'\n')  # echo
            print(f'TX: {report}')
            print('Closing connection')
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
        except:
            print(f'Error sending report: {report}...\nMaybe the client hung up?')


        print('--------------------------')
        print()
