from modules import refwork, reddit, fcr, bitly, geolocation, urban, snarf, nicktime, fun, reply
from urllib.request import Request, urlopen
from decode import decode
from send import send
import socket, re
import message

server = 'irc.freenode.net'
channels = []
password =
username =
nick = 'mel0nbot'
allowed_hosts = []
irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

EST = ['melon', 'yano']
CET = ['xy', 'sfan5']
BST = ['Xack', 'Chiyo']
tzList = [[EST, 'US/Eastern'], [CET, 'Europe/Berlin'], [BST, 'Europe/London']]
toggleable_features = ['snarf']
initToggleOff = {'snarf': ['##xy']}
toggleList = {}
redditList = {}


def mel_quit(msg):
    if re.search('^ quit\s*$', msg):
        send('QUIT', irc)
        raise SystemExit


def mel_part(msg, channel):
    part = re.search('^ part( ([#\w\d\-_ ]+))?\s*$', msg)
    if part:
        if part.group(2):    
            chans = []
            chans.extend(part.group(2).strip().split(' '))
            for i in range(0, len(chans)):
                    send('PART %s' % chans[i], irc)
                    del redditList[chans[i]]
                    del toggleList[chans[i]]
                    channels.remove(chans[i])
        else:
            send('PART %s' % channel, irc)
            del redditList[channel]
            del toggleList[channel]
            channels.remove(channel)
        if not channels:
            send('QUIT', irc)
            raise SystemExit


def mel_join(msg):
    join = re.search('^ join ([#\w\d\-_ ]+)\s*$', msg)
    if join:    
        chans = []
        chans.extend(join.group(1).strip().split(' '))
        for i in range(0, len(chans)):
                send('JOIN %s' % chans[i], irc)
                send('Greetings %s (ﾟヮﾟ )' % chans[i], irc, chans[i])
                redditList[chans[i]] = {}
                toggleList[chans[i]] = toggle_set(chans[i])
                channels.append(chans[i])


def mel_channels(msg, channel):
    chans = re.search('^ channels\s*$', msg)
    if chans:
        send(', '.join(channels), irc, channel)


def toggle_set(channel):
    featuresDict = {}
    for feature in toggleable_features:
        if channel not in initToggleOff[feature]:
            featuresDict[feature] = True
        else:
            featuresDict[feature] = False
    return featuresDict


def toggle_check(feature, channel):
    if channel in toggleList:
        if not toggleList[channel][feature]:
            return False
        else: return True
    else: return False
    

def toggle(msg, channel):
    feature = re.search('^ ([\w]+)\s*$', msg).group(1)
    if feature in toggleList[channel]:
        if toggleList[channel][feature]:
            toggleList[channel][feature] = False
            return feature + ' turned off'
        else:
            toggleList[channel][feature] = True
            return feature + ' turned on'

        
def is_allowed(host):
    if host in allowed_hosts:
        return True
    else: return False


def handle_message(mes):
    response = None
    if mes.prefix:
        if mes.prefix == 'mel' and is_allowed(mes.host):
            mel_quit(mes.msg)
            mel_part(mes.msg, mes.channel)
            mel_join(mes.msg)
            mel_channels(mes.msg, mes.channel)
        elif mes.prefix == 'tog' and is_allowed(mes.host): response = toggle(mes.msg, mes.channel)
        elif mes.prefix == 'd': response = refwork.getDefn(mes.msg)
        elif mes.prefix == 's': response = refwork.getSyn(mes.msg)
        elif mes.prefix == 'r': response = reddit.getThread(mes.msg, redditList, mes.channel)
        elif mes.prefix == 'news': response = reddit.getThread(' worldnews' + mes.msg, redditList, mes.channel)
        elif mes.prefix == 'fcr': response = fcr.getList()
        elif mes.prefix == 'short': response = bitly.shorten(mes.msg, mes.nick)
        elif mes.prefix == 'ip': response = geolocation.locate(mes.msg, mes.nick)
        elif mes.prefix == 'ud': response = urban.getDefn(mes.msg)
        elif mes.prefix == 'kitty': response = fun.kitty(mes.nick, mes.msg)
        elif mes.prefix == 'cookie': response = fun.cookie(mes.msg)
        elif mes.prefix == 'cake': response = fun.cake(mes.msg)
        elif mes.prefix == 'tea': response = fun.tea(mes.msg)
        elif mes.prefix == 'coffee': response = fun.coffee(mes.msg)
        else:
            response = nicktime.getTime(mes.fullMsg, tzList, response)
        if response:
            send(response, irc, mes.channel)
    else:
        if toggle_check('snarf', mes.channel):
            response = snarf.getTitle(mes.msg, response)
        response = reply.salutations(mes.msg, mes.nick, nick, response)
        response = reply.love(mes.msg, mes.nick, nick, response)
        response = reply.noProb(mes.msg, mes.nick, nick, response)
        response = reply.ctcpAction(mes.msg, mes.nick, nick, response)
        if response:
            send(response, irc, mes.channel)


def main():
    while True:
        name = input('channel name: ')
        if name:
            channels.append(name)
        else: break
    print("connecting to: " + server)
    irc.connect((server, 6667))
    send('PASS %s' % password, irc)
    send('USER %s %s melon :%s' % (username, nick, nick), irc)
    send('NICK %s' % nick, irc)
    send('JOIN %s' % ','.join(channels), irc)
    for i in range(0, len(channels)):
        send('Greetings %s  (ﾟヮﾟ )' % channels[i], irc, channels[i])
        redditList[channels[i]] = {}
        toggleList[channels[i]] = toggle_set(channels[i])
    while True:
        data = decode(irc.recv(1024))
        try:
            print(data)
        except: pass
        try:
            mes = message.message(data)
            handle_message(mes)
        except Exception: pass
        ping = re.search('^PING ([\w\.:]+)', data)
        if ping:
            send('PONG %s' % ping.group(1), irc)


if __name__ == '__main__':
    main()
