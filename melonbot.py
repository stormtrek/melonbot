import argparse
import json
import os
import random
import re
import socket
import ssl
import threading
import time
import traceback
import datetime
import message
from collections import OrderedDict
from types import SimpleNamespace
from fnmatch import fnmatch
from decode import decode
from imp import reload
from send import send
from modules import (refwork, reddit, humor, bitly, geolocation, urban, notes, unscramble,
                     snarf, nicktime, fun, triggers, weather, google, w0bm, deepl,
                     memo, chests, wolfram, reminder, money, gamble, modify, coinprice)

parser = argparse.ArgumentParser()
parser.add_argument('--config', default='config.json', help='configuration file')
args = parser.parse_args()

with open(args.config) as fd:
    config = json.load(fd, object_pairs_hook=OrderedDict)

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if config['ssl']:
    irc = ssl.wrap_socket(irc)

joined_channels = []

toggle_list = {}

urban_list = {}

reddit_list = {}
reddit_rand_list = {}

reminder_threads = {}
rem_lock = threading.RLock()

terminate = False
sleep_duration = 10

error_template = "Exception of type {0} occurred: {1!r}"

rate_limited = config['rate_limited']
threaded_commands = config['threaded_commands']

commands = {
                "admin_control": ['mel', 'melon'],
                "add_note": ["addnote"],
                "at_reminder": ["at"],
                "bitly": ["bitly", "short", "shorten"],
                "cake": ["cake"],
                "coffee": ["coffee"],
                "coinprice": ["coinprice", "crypto", "price", "cm", "cmc"],
                "coins": ["coins", "pouch", "money"],
                "cookie": ["cookie"],
                "deepl": ["deepl", "dl"],
                "del_note": ["delnote"],
                "del_rem": ["delrem", "del"],
                "dictionary": ["dictionary", "dict", "d"],
                "fmylife": ["fml"],
                "gamble": ["gamble", "gam"],
                "in_reminder": ["in", "reminder", "rem", "remind"],
                "ip_lookup": ["ip"],
                "jokes": ["joke"],
                "kitty": ["kitty", "kitten"],
                "memo": ["memo", "telegram"],
                "modify": ['modify', 'mod'],
                "nick_time": ["nicktime", "nt"],
                "notes": ["notes"],
                "open_chest": ["open", "chests"],
                "pet": ["pet", "pets"],
                "pie": ["pie"],
                "ping": ["ping"],
                "pizza": ["pizza"],
                "reddit": ["reddit", "r"],
                "reddit_random": ["redditrand", "rr"],
                "reddit_random_top": ["redditrandtop", "rrt"],
                "reddit_top": ["reddittop", "rt"],
                "reddit_world_news": ["worldnews", "news"],
                "register": ["register"],
                "reload_module": ['reload'],
                "reload_configuration": ["refresh"],
                "rem_id": ["remid", "id"],
                "reminders": ["reminders", "rems"],
                "sfan5": ["sfan5", "stefan"],
                "show_scramble": ["show"],
                "skip_scramble": ["skip"],
                "synonym": ["synonym", "syn", "s"],
                "tea": ["tea"],
                "time": ["time"],
                "toggle": ["toggle", "tog"],
                "transfer": ["transfer"],
                "translate": ["translate", "t", "tr", "tl"],
                "tz_info": ["timezone", "tz"],
                "tz_list": ["tzlist"],
                "unscramble": ["scramble", "scram"],
                "urban_dictionary": ["urban", "ud"],
                "w0bm": ["w0bm", "wobm", "wob"],
                "wealth_ranking": ["wealth", "ranking"],
                "weather": ["weather", "w", "we"],
                "wolfram": ["wolfram", "wolf", "wa", "wo"]
            }

def write_config():
    global config

    with open(args.config, 'w') as fd:
        json.dump(config, fd, indent=2)


def handle_join(channel):
    greetings = config.get('greetings', {})
    greeting = greetings.get(channel, greetings.get('*'))

    if greeting:
        send(greeting % {'channel': channel}, irc, channel)

    if channel not in joined_channels:
        joined_channels.append(channel)

    reddit_list[channel] = [{}, {'hot': [None, None], 'top': [None, None]}]
    reddit_rand_list[channel] = {}
    urban_list[channel] = [{}, None, None]
    toggle_list[channel] = toggle_set(channel)

    reminder.start_reminders_on_join(channel, reminder_threads, rem_lock, irc)

    if (not config.get('no_save_channels')) and channel not in config['channels']:
        config['channels'].append(channel)
        write_config()

        
def part_channel(chan):
    send('PART %s' % chan, irc)

    if chan in joined_channels:
        joined_channels.remove(chan)

    del reddit_list[chan]
    del reddit_rand_list[chan]
    del urban_list[chan]
    del toggle_list[chan]

    if (not config.get('no_save_channels')) and chan in config['channels']:
        config['channels'].remove(chan)


def mel_join(msg):
    join = re.search('^\s+join ([#\w\d\-_ ]+)\s*$', msg)
    if join:    
        channels = []
        channels.extend(join.group(1).strip().split(' '))

        send('JOIN %s' % ','.join(channels), irc)
        if not config.get('no_save_channels'):
            config['channels'].extend([x for x in channels if x not in config['channels']])

        write_config()


def mel_part(msg, channel):
    part = re.search('^\s+part( ([#\w\d\-_ ]+))?\s*$', msg)
    if not part:
        return
    chans = []
    if part.group(2):    
        chans.extend(part.group(2).strip().split(' '))
    else:
        chans.append(channel)
    for chan in chans:
        part_channel(chan)
    write_config()
    if not joined_channels:
        global terminate
        terminate = True
        send('QUIT', irc)


def mel_quit(msg):
    if re.search('^\s+quit\s*$', msg):
        global terminate
        terminate = True
        send('QUIT', irc)


def mel_channels(msg, channel):
    chans = re.search('^\s+channels\s*$', msg)
    if chans:
        send(', '.join(config['channels']), irc, channel)


def toggle_set(channel):
    featuresDict = {}

    for (feature, channels) in config['disable_features'].items():
        featuresDict[feature] = (channel not in channels)

    return featuresDict


def toggle_check(feature, channel):            
    if channel in toggle_list:
        not_disabled = toggle_list[channel].get(feature, True)
        return not_disabled
    

def toggle(msg, channel):
    feature = re.search('^\s+([\w]+)\s*$', msg).group(1)
    if feature in toggle_list[channel]:
        if toggle_list[channel][feature]:
            toggle_list[channel][feature] = False
            return feature + ' turned off'
        else:
            toggle_list[channel][feature] = True
            return feature + ' turned on'


def check_formatting(msg):
    boldCount = msg[0].count('\x02')
    if boldCount % 2 != 0:
        msg[1] = '\x02' + msg[1].strip()
    if len(msg[1]) > config['maxSendLen']:
        msg[1] = msg[1][:config['maxSendLen'] - 3].rstrip() + '...'
    return msg


def reload_module(module):
    try:
        reload(globals()[module])
        return 'Reload successful'
    except Exception as e:
        traceback.print_exc()
        return error_template.format(type(e).__name__, e.args)


def reload_config():
    global config
    
    with open(args.config) as fd:
        try:
            config = json.load(fd, object_pairs_hook=OrderedDict)
            return 'Configuration reloaded'
        except Exception as e:
            traceback.print_exc()
            return error_template.format(type(e).__name__, e.args)
        
        
def is_allowed(mes):
    hostmask = '%s!%s@%s' % (mes.nick, mes.user, mes.host)
    return any(hm for hm in config['admins'] if fnmatch(hostmask, hm))


def is_threaded(prefix):
    for command in threaded_commands:
        if prefix in commands[command]:
            return True


def is_rate_limited(prefix, channel):
    for command in rate_limited:
        if prefix in commands[command]:
            if rate_limited[command]['all_channels'] or channel in rate_limited[command]['channels']:
                return True


def get_command_name(prefix):
    for command, prefixes in commands.items():
        if prefix in prefixes:
            return command
        

def handle_message(mes):
    try:
        response = None
        if toggle_check('snarf', mes.channel):
            response = snarf.getTitle(mes.msg, response)
        if toggle_check('triggers', mes.channel):
            response = triggers.salutations(mes.msg, mes.nick, config['nick'], response)
            response = triggers.love(mes.msg, mes.nick, config['nick'], response)
            response = triggers.noProb(mes.msg, mes.nick, config['nick'], response)
            response = triggers.ctcpAction(mes.msg, mes.nick, config['nick'], response)
            response = triggers.lenny(mes.msg, response)
            response = triggers.ayy(mes.msg, response)
            response = triggers.shrug(mes.msg, response)
            response = triggers.derp(mes.msg, response)
        response = memo.memo_check(mes.nick, response)
        response = unscramble.check_answer(mes.msg.lower().strip(), mes.nick, mes.channel, response, irc)
        if response:
            if isinstance(response, list):
                for i in response:
                    send(i, irc, mes.channel)
            else:
                send(response, irc, mes.channel)
            response = None
            
        if mes.prefix:
            if mes.prefix in commands['admin_control'] and is_allowed(mes):
                mel_quit(mes.msg)
                mel_part(mes.msg, mes.channel)
                mel_join(mes.msg)
                mel_channels(mes.msg, mes.channel)
            elif mes.prefix in commands['modify'] and is_allowed(mes):
                response, module = modify.modify(mes.msg)
                if module:
                    reload(globals()[module])
            elif mes.prefix in commands['toggle'] and is_allowed(mes): response = toggle(mes.msg, mes.channel)
            elif mes.prefix in commands['reload_module'] and is_allowed(mes): response = reload_module(mes.msg.strip())
            elif mes.prefix in commands['reload_configuration'] and is_allowed(mes): response = reload_config()
            elif mes.prefix in commands['dictionary']: response = wolfram.waSearch2(mes.msg)
            elif mes.prefix in commands['synonym']: response = refwork.getSyn(mes.msg)
            elif mes.prefix in commands['weather']: response = weather.getCond(mes.msg)
            elif mes.prefix in commands['translate']: response = google.translate(mes.msg)
            elif mes.prefix in commands['deepl']: response = deepl.translate(mes.msg)
            elif mes.prefix in commands['reddit']: response = reddit.getThread(mes.msg, reddit_list, mes.channel)
            elif mes.prefix in commands['reddit_random']: response = reddit.getRandThread(mes.msg, reddit_list, mes.channel, reddit_rand_list)
            elif mes.prefix in commands['reddit_top']: response = reddit.getThread(mes.msg, reddit_list, mes.channel, True)
            elif mes.prefix in commands['reddit_random_top']: response = reddit.getRandThread(mes.msg, reddit_list, mes.channel, reddit_rand_list, True)
            elif mes.prefix in commands['reddit_world_news']: response = reddit.getThread(' worldnews' + mes.msg, reddit_list, mes.channel)
            elif mes.prefix in commands['w0bm']: response = w0bm.getVid(mes.msg)        
            elif mes.prefix in commands['jokes']: response = humor.getJoke()
            elif mes.prefix in commands['fmylife']: response = humor.getFML()
            elif mes.prefix in commands['bitly']: response = bitly.shorten(mes.msg)
            elif mes.prefix in commands['ip_lookup']: response = geolocation.locate(mes.msg, mes.nick)
            elif mes.prefix in commands['urban_dictionary']: response = urban.getDefn(mes.msg, urban_list, mes.channel) 
            elif mes.prefix in commands['kitty']: response = fun.kitty(mes.nick, mes.msg)
            elif mes.prefix in commands['pet']: response = fun.pet(mes.nick, mes.msg)
            elif mes.prefix in commands['cookie']: response = fun.cookie(mes.msg)
            elif mes.prefix in commands['cake']: response = fun.cake(mes.msg)
            elif mes.prefix in commands['pie']: response = fun.pie(mes.msg)
            elif mes.prefix in commands['pizza']: response = fun.pizza(mes.msg)
            elif mes.prefix in commands['tea']: response = fun.tea(mes.msg)
            elif mes.prefix in commands['coffee']: response = fun.coffee(mes.msg)
            elif mes.prefix in commands['memo']: response = memo.save_memo(mes.msg, mes.nick)
            elif mes.prefix in commands['open_chest']: response = chests.open_chests(mes.nick)
            elif mes.prefix in commands['coins']: response = money.check_balance(mes.nick)
            elif mes.prefix in commands['transfer']: response = money.transfer(mes.msg, mes.nick)
            elif mes.prefix in commands['register']: response = money.register(mes.nick)
            elif mes.prefix in commands['gamble']: response = gamble.gamble(mes.msg, mes.nick, mes.channel)
            elif mes.prefix in commands['wolfram']: response = wolfram.waSearch(mes.msg)
            elif mes.prefix in commands['in_reminder']: response = reminder.in_reminder(mes.msg, mes.nick, mes.channel, reminder_threads, rem_lock, irc)
            elif mes.prefix in commands['at_reminder']: response = reminder.at_reminder(mes.msg, mes.nick, mes.channel, reminder_threads, rem_lock, irc)
            elif mes.prefix in commands['reminders']: response = reminder.view_reminders(mes.nick, mes.channel, mes.msg.strip())
            elif mes.prefix in commands['rem_id']: response = reminder.view_single_reminder(mes.msg.strip(), mes.nick)
            elif mes.prefix in commands['del_rem']: response = reminder.delete_reminder(mes.msg.strip(), mes.nick, reminder_threads)
            elif mes.prefix in commands['time']: response = nicktime.getUserTime(mes.nick)
            elif mes.prefix in commands['coinprice']: response = coinprice.get_price(mes.msg)
            elif mes.prefix in commands['nick_time']: response = nicktime.getInfo(mes.msg)
            elif mes.prefix in commands['ping']: response = 'Pong'
            elif mes.prefix in commands['add_note']: response = notes.parse_add_note(mes.msg, mes.nick)
            elif mes.prefix in commands['del_note']: response = notes.delete_note(mes.msg.strip(), mes.nick)
            elif mes.prefix in commands['notes']: response = notes.view_notes(mes.nick)
            elif mes.prefix in commands['unscramble']: response = unscramble.generate_scramble(mes.channel, irc)
            elif mes.prefix in commands['show_scramble']: response = unscramble.show_current_scramble()
            elif mes.prefix in commands['skip_scramble']: response = unscramble.skip_scramble()
            elif mes.prefix in commands['wealth_ranking']: response = money.get_wealth_ranking()
            elif mes.prefix in commands['tz_list']: response = nicktime.get_tz_list()
            elif mes.prefix in commands['tz_info']: response = nicktime.get_tz_info(mes.msg.strip())
            else:
                response = nicktime.getTime(mes.fullMsg, response) # check for nicktime
                if mes.channel == config['nick'] and is_allowed(mes): # lets melonbot send messages to specific channels. ex: .#lounge hello
                    send(mes.msg.strip(), irc, mes.prefix)
            if response:
                if mes.channel != config['nick']:
                    target = mes.channel
                else:
                    target = mes.nick
                if (len(response) > config['maxSendLen']):
                    response = [response[:config['maxSendLen']], response[config['maxSendLen']:]]
                    response = check_formatting(response)
                if isinstance(response, list):
                    for i in response:
                        send(i, irc, target)
                else:
                    send(response, irc, target)
                if mes.channel != config['nick']:
                    response = chests.chest_drops(mes.nick)
                    if response:
                        send(response, irc, mes.channel)
    except Exception as e:
        traceback.print_exc()
        if mes.prefix:
            send(error_template.format(type(e).__name__, e.args), irc, mes.channel)


def recvline(s):
    ret = b""
    while True:
        c = s.recv(1)
        if not c:
            return
        elif c == b"\r":
            pass # ignored
        elif c == b"\n":
            return ret
        else:
            ret += c
            

def main():
    global sleep_duration
    
    print('connecting to %s:%s%d' % (config['host'], '+' if config['ssl'] else '', config['port']))
    try:
        irc.connect((config['host'], config['port']))
        sleep_duration = 10
    except Exception as e:
        print(error_template.format(type(e).__name__, e.args))
        return

    if config.get('password'):
        send('PASS %s' % config['password'], irc)

    send('NICK %s' % config['nick'], irc)
    send('USER %s * * :%s' % (config['user'], config['realname']), irc)
    
    while True:
        try:
            data = decode(recvline(irc))
        except Exception:
            break

        valid_message = True
        try:
            mes = message.Message(data)
        except Exception:
            valid_message = False
            
        if valid_message: 
            try:
                if mes.nick in config['tg_relays']:
                    m = re.search('<(.*?)>', data)
                    mes = message.Message(re.sub('<.*?> ', '', data, 1))
                    mes.nick = '@' + m.group(1)[3:][:-1]
                
                if is_rate_limited(mes.prefix, mes.channel):
                    key = get_command_name(mes.prefix)
                    if not rate_limited[key]['last_check']:
                        rate_limited[key]['last_check'] = datetime.datetime.now()
                    rate, per, allowance, last_check = rate_limited[key]['rate'], rate_limited[key]['per'], rate_limited[key]['allowance'], rate_limited[key]['last_check'] 
                    current = datetime.datetime.now()
                    time_passed = (current - last_check).total_seconds()
                    last_check = current
                    allowance += (time_passed * (rate/per))
                    if (allowance > rate):
                        allowance = rate
                    if (allowance < 1.0):
                        pass
                    else:
                        handle_message(mes)
                        allowance -= 1.0
                    rate_limited[key]['rate'], rate_limited[key]['per'], rate_limited[key]['allowance'], rate_limited[key]['last_check'] = rate, per, allowance, last_check
                elif is_threaded(mes.prefix):
                    t = threading.Thread(target=handle_message, args=[mes])
                    t.daemon = True
                    t.start()
                else:
                    handle_message(mes)
            except Exception:
                traceback.print_exc()

        if data[0:4] == 'PING':
            send(data.replace('I', 'O', 1), irc)

        if data.split()[1] == '376':
            send('JOIN %s' % ','.join(config['channels']), irc)

        m = re.search(r'^:' + re.escape(config['nick']) + '!.+@.+ JOIN :?(#.+)(?:\s|$)', data)
        if m:
            handle_join(m.group(1))

        try: print('>> %s' % data)
        except Exception: pass


if __name__ == '__main__':
    try:
        while True:
            main()
            if terminate:
                irc.shutdown(socket.SHUT_RDWR)
                irc.close()
                break
            else:
                print('reconnecting in ' + str(sleep_duration) + ' seconds')
                time.sleep(sleep_duration)
                if sleep_duration < 320:
                    sleep_duration *= 2
    except Exception:
        traceback.print_exc()
