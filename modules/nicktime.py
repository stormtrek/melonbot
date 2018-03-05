from datetime import datetime
from pytz import timezone
from formatting import bold
import re
from collections import OrderedDict
import json

with open('nicktime.json') as data_file:    
    data = json.load(data_file, object_pairs_hook=OrderedDict)
    tz_list = data['tzList']
    users = data['users']

def getTime(msg, response):
    m = re.search('^\.([^ ]+)time\s*$', msg)
    if m:
        nick = m.group(1)
        return nickSearch(nick)
    else:
        return response

def getUserTime(user, include_name=True):
    try:
        for key, value in tz_list.items():
            if user in users[key]:
                return dt_format(datetime.now(tz=timezone(value)), include_name, users[key][user]['display'])
        if user[0] != '@':
            return nickSearch(user, include_name)
    except Exception:
        pass

def nickSearch(nick, include_name=True):
    for key, value in tz_list.items():
        for k, v in users[key].items():
            for i in range(0, len(v['nicks'])):
                if nick.lower() == v['nicks'][i].lower():
                    return dt_format(datetime.now(tz=timezone(value)), include_name, v['display'])

def dt_format(time, include_name=False, user=None):
    dayNames = {'Sun': 'Sunday', 'Mon': 'Monday', 'Tue': 'Tuesday', 'Wed': 'Wednesday', 'Thu': 'Thursday', 'Fri': 'Friday', 'Sat': 'Saturday'}
    name = ''
    if include_name:
        name = bold(user + '\'s time: ')
    time = time.strftime('%I:%M %p / %X • %a %b %d, %Y • %Z (%z)').replace('-03 ', 'ART ')
    for key, value in dayNames.items():
        time = time.replace(key, value + ',')
    return name + time

def getTZ(user, return_key=False, check_nicks=False):
    try:
        for key, value in tz_list.items():
            if user in users[key]:
                if return_key:
                    return key
                else:
                    return value
        if not check_nicks:
            for key, value in tz_list.items():
                for k, v in users[key].items():
                    for i in range(0, len(v['nicks'])):
                        if user.lower() == v['nicks'][i].lower():
                            if return_key:
                                return key
                            else:
                                return value
    except Exception:
        return

def tz_exists(tz):
    if tz in tz_list:
        return True
    else:
        return False

def get_tz_list():
    timezones = []
    for tz in tz_list:
        timezones.append(tz)
    return ', '.join(timezones)

def get_tz_info(timezone):
    if not timezone:
        return 'Please enter a timezone to look up'
    
    tz_name = None
    for key, value in tz_list.items():
        if timezone.lower() == key.lower():
            tz_name = '{0}: {1}'.format(key, value)
            
    if tz_name is not None:
        return tz_name
    else:
        return 'Could not find the timezone you searched'

def getInfo(msg):
    response = ''
    usedKeys = []
    m = re.search('^ ([\w@]+)\s*$', msg)
    if m:
        search_name = m.group(1).lower()
        for key in users:
            for k, v in users[key].items():
                for i in range(0, len(v['nicks'])):
                    if search_name == v['nicks'][i].lower():
                        response += '[' + k[:1] + '\u200B' + k[1:] + ': "' + v['display'] + '"] ' + ', '.join(v['nicks']) + ' '
                        usedKeys.append(k)
        for key in users:
            for k, v in users[key].items():
                if search_name == k.lower():
                    if k not in usedKeys:
                        response += '[' + k[:1] + '\u200B' + k[1:] + ': "' + v['display'] + '"] ' + ', '.join(v['nicks']) + ' '
                        usedKeys.append(k)
    else:
        return 'Please enter a name to search'
    if response:
        return response
    else:
        return 'The name you searched does not exist'

