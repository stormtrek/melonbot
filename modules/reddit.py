from urllib.request import Request, urlopen
from datetime import datetime
from decode import decode
from json import loads
import re

def getThread(msg, redditList, channel):
    match = re.search('^ ([\w\d\_]+)\s*([\d]+)?\s*$', msg)
    if match:
        subreddit = match.group(1)
        pos = match.group(2)
    else:
        return None
    try:
        content = loads(decode(urlopen(Request('http://www.reddit.com/r/' + subreddit + '.json',
                                             headers={'User-Agent': 'melonbot 1.0 (used by /u/<handle_here>'})).read()))
    except:
        return '.: could not reach server :.'
    data = content['data']['children']
    if len(data) == 0:
        return '.: there doesn\'t seem to be anything here :.'
    for t in data[:]:
        try:
            if t['data']['stickied']:
                data.remove(t)
        except:
            return '.: there doesn\'t seem to be anything here :.'
    if not pos:
        if subreddit not in redditList[channel]:
            redditList[channel][subreddit] = [1, None]
        if redditList[channel][subreddit][1]:
            if (datetime.now() - redditList[channel][subreddit][1]).total_seconds() > 1800:
                redditList[channel][subreddit][0] = 1
        pos = redditList[channel][subreddit][0]
        redditList[channel][subreddit] = [pos + 1, datetime.now()]
        if redditList[channel][subreddit][0] > len(data):
            redditList[channel][subreddit][0] = 1
    else:
        redditList[channel][subreddit] = [int(pos) + 1, datetime.now()]
        if redditList[channel][subreddit][0] > len(data):
            redditList[channel][subreddit][0] = 1
    pos = int(pos) - 1
    try:
        title = [data[pos]['data']['title'], data[pos]['data']['url'], data[pos]['data']['id']]
    except:
        return 'entry ' + str(pos + 1) + ' does not exist'
    if data[pos]['data']['over_18']:
        if 'nsfw' not in title[0].lower():
            title[0] = '[NSFW] ' + title[0]
    if not data[pos]['data']['is_self']:
        return str(pos + 1) + ') ' + title[0] + '  ::  ' + title[1] + '  ::  ' + \
               'http://redd.it/' + title[2]
    else:
        return str(pos + 1) + ') ' + title[0] + '  ::  ' + title[1]
