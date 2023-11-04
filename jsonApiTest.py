import urllib.request, urllib.error, urllib.parse
import json
urlString = 'https://live.nhle.com/GameData/RegularSeasonScoreboardv3.jsonp'
print(f"getting: {urlString} ...")
f = urllib.request.urlopen(urlString)
jsonp = f.read().decode('utf8')
f.close()
json_str = jsonp.replace("loadScoreboard(", "").replace(")", "")
print(json_str)
json_parsed = json.loads(json_str)

for game in json_parsed['games']:
    print(game)