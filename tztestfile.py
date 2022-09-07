#hey.. what the hell is up with datetime.datetime.fromtimestamp() ?!

from dateutil import tz
import datetime

dt=1664038800
localTimeZone= "Europe / Berlin"
print(datetime.datetime.fromtimestamp(dt, tz=tz.gettz(localTimeZone)))
localTimeZone= "Europe/Berlin"
print(datetime.datetime.fromtimestamp(dt, tz=tz.gettz(localTimeZone)))
