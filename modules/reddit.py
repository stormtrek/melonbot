"""
Module for retrieving Reddit data and displaying subreddit threads
"""

from urllib.request import Request, urlopen
from collections import OrderedDict
from datetime import datetime
from json import load, loads
from modules import bitly
from decode import decode
import argparse
import random
import html
import bs4
import re

parser = argparse.ArgumentParser()
parser.add_argument('--config', default='config.json', help='configuration file')
args = parser.parse_args()
with open(args.config) as fd:
    config = load(fd, object_pairs_hook=OrderedDict)

user_agent = config['reddit_user_agent']
sfw_channels = config['reddit_sfw_channels']

params_list = {'front': {'hot': '?limit=100', 'top': '?sort=top&t=week&limit=100'}, 'random': {'hot': '?limit=100', 'top': '?sort=top&t=week&limit=100'}}
max_char_length = 420

def getThread(msg, redditList, channel, top=False):
    """ Retrieves a subreddit thread incrementally or from a specific position
    """
    
    reset_position_after = 3600
    prev_sub = None
    nsfw = False
    get_content = False
    
    if top:
        cat = 'top'
    else:
        cat = 'hot'
    m = re.search('^ ([\w\_]+)\s*([\d]+)?\s*$', msg)
    if m:
        subreddit = m.group(1).lower()
        pos = m.group(2)
        prev_sub = redditList[channel][1][cat][0]
        redditList[channel][1][cat][0] = subreddit
    else:
        if not msg.strip():
            prev_sub = redditList[channel][1][cat][0]
            if redditList[channel][1][cat][0]:
                subreddit = redditList[channel][1][cat][0]
                pos = None
            else:
                return 'Please enter a subreddit'
        else:
            return 'Incorrect command syntax'
    if subreddit not in redditList[channel][0]:
        get_content = True
    else:
        if not redditList[channel][0][subreddit][cat][3]:
            get_content = True
        elif (datetime.now() - redditList[channel][0][subreddit][cat][3]).total_seconds() >= 60:
            get_content = True
    if get_content:
        try:
            params = params_list['front'][cat]
            content = loads(decode(urlopen(Request('http://www.reddit.com/r/' + subreddit + '/' + cat + '.json' + params,
                                                 headers={'User-Agent': user_agent}), timeout=2).read()))
            data = content['data']['children']
            fetchDate = datetime.now()
        except Exception:
            redditList[channel][1][cat][0] = prev_sub
            return 'Could not reach /r/' + subreddit
    if not get_content:
        data = redditList[channel][0][subreddit][cat][2]
    if get_content:
        if len(data) == 0:
            redditList[channel][1][cat][0] = prev_sub
            return 'There doesn\'t seem to be anything in /r/' + subreddit
        for t in data[:]:
            try:
                if t['data']['stickied']:
                    data.remove(t)
            except Exception:
                redditList[channel][1][cat][0] = prev_sub
                return 'There doesn\'t seem to be anything in /r/' + subreddit
    if not pos:
        if subreddit not in redditList[channel][0]:
            redditList[channel][0][subreddit] = {'hot': [1, None, None, None], 'top': [1, None, None, None]}
        if redditList[channel][0][subreddit][cat][1]:
            if (datetime.now() - redditList[channel][0][subreddit][cat][1]).total_seconds() >= reset_position_after:
                redditList[channel][0][subreddit][cat][0] = 1
        pos = redditList[channel][0][subreddit][cat][0]
        (redditList[channel][0][subreddit][cat][0], redditList[channel][0][subreddit][cat][1]) = (pos + 1, datetime.now())
        if redditList[channel][0][subreddit][cat][0] > len(data):
            redditList[channel][0][subreddit][cat][0] = 1
    else:
        pos = int(pos)
        if subreddit not in redditList[channel][0]:
            redditList[channel][0][subreddit] = {'hot': [1, None, None, None], 'top': [1, None, None, None]}
            redditList[channel][0][subreddit][cat] = [pos + 1, datetime.now(), None, None]
        else:
            (redditList[channel][0][subreddit][cat][0], redditList[channel][0][subreddit][cat][1]) = (pos + 1, datetime.now())
        if redditList[channel][0][subreddit][cat][0] > len(data):
            redditList[channel][0][subreddit][cat][0] = 1
    if get_content:
        redditList[channel][0][subreddit][cat][2] = data
        redditList[channel][0][subreddit][cat][3] = fetchDate
    pos -= 1
    try:
        title = [html.unescape(data[pos]['data']['title']), html.unescape(data[pos]['data']['url']), data[pos]['data']['id'], data[pos]['data']['subreddit']]
    except Exception:
        return 'Entry ' + str(pos + 1) + ' does not exist'
    if data[pos]['data']['over_18']:
        if 'nsfw' not in title[0].lower():
            title[0] = '\x0304[NSFW]\x03 ' + title[0]
        if channel in sfw_channels:
            nsfw = True
    title[1] = get_OG_media(title[1])
    if top:
        title[3] += '/top'
    if not data[pos]['data']['is_self'] and not nsfw:
        output = '\x02' + str(pos + 1) + ')\x02 ' + title[0] + ' • /r/' + title[3] + ' \x0302•\x03 ' + title[1] + ' \x0303•\x03 ' + \
               'http://redd.it/' + title[2]
        if len(output) > max_char_length:
            output = '\x02' + str(pos + 1) + ')\x02 ' + title[0] + ' • /r/' + title[3] + ' \x0302•\x03 ' + bitly.shorten(title[1]) + ' \x0303•\x03 ' + \
               'http://redd.it/' + title[2]
        return output
    else:
        return '\x02' + str(pos + 1) + ')\x02 ' + title[0] + ' • /r/' + title[3] + ' \x0303•\x03 ' + 'http://redd.it/' + title[2]


def getRandThread(msg, redditList, channel, randList, top=False):
    """ Retrieves a subreddit thread randomly
    """
    
    refresh_content_after = 10800
    prev_sub = None
    nsfw = False
    get_content = False
    list_updated = False
    
    if top:
        cat = 'top'
    else:
        cat = 'hot'
    m = re.search('^ ([\w\_]+)\s*$', msg)
    if m:
        subreddit = m.group(1)
        prev_sub = redditList[channel][1][cat][1]
        redditList[channel][1][cat][1] = subreddit
    else:
        if not msg.strip():
            prev_sub = redditList[channel][1][cat][1]
            if redditList[channel][1][cat][1]:
                subreddit = redditList[channel][1][cat][1]
            else:
                return 'Please enter a subreddit'
        else:
            return 'Incorrect command syntax'
    if subreddit not in randList[channel]:
        randList[channel][subreddit] = {'hot': [[], 0, None, None], 'top': [[], 0, None, None]}
        get_content = True
    else:
        if not randList[channel][subreddit][cat][3]:
            get_content = True
        elif randList[channel][subreddit][cat][1] >= len(randList[channel][subreddit][cat][0]):
            get_content = True
        elif (datetime.now() - randList[channel][subreddit][cat][3]).total_seconds() >= refresh_content_after:
            get_content = True
    if get_content:
        try:
            params = params_list['random'][cat]
            content = loads(decode(urlopen(Request('http://www.reddit.com/r/' + subreddit + '/' + cat + '.json' + params,
                                                 headers={'User-Agent': user_agent}), timeout=2).read()))
            randList[channel][subreddit][cat][2] = content['data']['children']
            randList[channel][subreddit][cat][3] = datetime.now()
            list_updated = True
        except Exception:
            redditList[channel][1][cat][1] = prev_sub
            return 'Could not reach /r/' + subreddit
    data = randList[channel][subreddit][cat][2]
    if get_content:
        if len(data) == 0:
            redditList[channel][1][cat][1] = prev_sub
            del randList[channel][subreddit]
            return 'There doesn\'t seem to be anything in /r/' + subreddit
        for t in data[:]:
            try:
                if t['data']['stickied']:
                    data.remove(t)
            except Exception:
                redditList[channel][1][cat][1] = prev_sub
                del randList[channel][subreddit]
                return 'There doesn\'t seem to be anything in /r/' + subreddit


    size = len(data)
    randNumList, randCounter = randList[channel][subreddit][cat][0], randList[channel][subreddit][cat][1]
    if not randNumList:
        randNumList = random.sample(range(0, size), size)
        randPos = randNumList[randCounter]
        randCounter += 1
    elif list_updated:
        randNumList = random.sample(range(0, size), size)
        randCounter = 0
        randPos = randNumList[randCounter]
        randCounter += 1
    else:
        randPos = randNumList[randCounter]
        randCounter += 1
    randList[channel][subreddit][cat][0], randList[channel][subreddit][cat][1] = randNumList, randCounter


    data = data[randPos]['data']
    title = [html.unescape(data['title']), html.unescape(data['url']), data['id'], data['subreddit'], data['score']]
    if data['over_18']:
        if 'nsfw' not in title[0].lower():
            title[0] = '\x0304[NSFW]\03 ' + title[0]
        if channel in sfw_channels:
            nsfw = True
    title[1] = get_OG_media(title[1])
    if top:
        title[3] += '/top'
    if not data['is_self'] and not nsfw:
        output = html.unescape(title[0]) + ' • /r/' + title[3] + ' \x0302•\x03 ' + title[1] + ' \x0303•\x03 ' + 'http://redd.it/' + title[2] + ' \x0307•\x03 score: ' + str(title[4])
        if len(output) > max_char_length:
            output = output = html.unescape(title[0]) + ' • /r/' + title[3] + ' \x0302•\x03 ' + bitly.shorten(title[1]) + ' \x0303•\x03 ' + 'http://redd.it/' + title[2] + ' \x0307•\x03 score: ' + str(title[4])
        return output
    else:
        return html.unescape(title[0]) + ' • /r/' + title[3] + ' \x0303•\x03 ' + 'http://redd.it/' + title[2] + ' \x0307•\x03 score: ' + str(title[4])

def get_OG_media(link):
    """ Retrieves the original image and video links from Imgur and Gfycat
    """
    
    link = re.sub('(imgur.com/[^ ]+\.)gif(v)?', '\g<1>mp4', link)
    link = re.sub('(imgur.com/[^ /\.]+$)', '\g<1>.jpg', link)
    if re.search('(gfycat.com)(/gifs/detail)?([^ \.]+$)', link):
        try:
            gfylink = re.sub('(gfycat.com)(/gifs/detail)?([^ \.]+$)', '\g<1>\g<3>', link)
            content = decode(urlopen(Request(gfylink, headers={'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'en-US,en;q=0.5'}), timeout = 5).read())
            soup = bs4.BeautifulSoup(content)
            url = soup.find("meta",  property="og:video")
            return url["content"]
        except Exception:
            return link
    return link
