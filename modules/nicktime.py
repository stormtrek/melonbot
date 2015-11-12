from datetime import datetime
from pytz import timezone
import re

def getTime(msg, tzList, response):
    nick = re.search('^\.([^ ]+)time\s*$', msg)
    if nick:
        for i in range(0, len(tzList)):
            for j in range(0, len(tzList[i][0])):
                if nick.group(1) == tzList[i][0][j].lower():
                    return dtFormat(tzList[i][0][j], datetime.now(tz=timezone(tzList[i][1])))
    else:
        return response


def dtFormat(nick, time):
    return nick + '\'s time: ' + time.strftime('%a %b %d %X %z (%Z)')
