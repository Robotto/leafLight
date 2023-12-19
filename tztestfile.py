#hey.. what the hell is up with datetime.datetime.fromtimestamp() ?!

import datetime
import time
import dateutil.parser, dateutil.tz as tz

#dt=1664038800
#localTimeZone= "Europe / Berlin"
#print(datetime.datetime.fromtimestamp(dt, tz=tz.gettz(localTimeZone)))
#localTimeZone= "Europe/Berlin"
#print(datetime.datetime.fromtimestamp(dt, tz=tz.gettz(localTimeZone)))

clockTime='1:00 PM'
yyyymmdd='20220924'
est=True
#defaultTimeFormat=datetime.datetime(2022,9,24, tzinfo=tz.gettz('US/Eastern'))

parsedTime = dateutil.parser.parse(f"{yyyymmdd} {clockTime}").replace(tzinfo=tz.gettz('US/Eastern'))
if parsedTime.timetuple().tm_isdst:
    parsedTime += datetime.timedelta(hours=1)
print(parsedTime)
print(parsedTime.timetuple())
unix = parsedTime.timestamp()
print(unix)
print(datetime.datetime.fromtimestamp(unix))