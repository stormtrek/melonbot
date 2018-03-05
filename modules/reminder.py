import re
import json
import time
import pytz
import string
import random
import threading
from formatting import bold
from collections import OrderedDict
from modules import nicktime, wolfram
from datetime import timedelta, datetime


try:
    with open('reminders.json', 'x') as fd:
        fd.write('{}')
except FileExistsError:
    pass


def save_reminder(reminder, time_until, nick, channel, thread_list, rem_lock, irc):
    if time_until < 0 :
        return nick + ', your reminder was set for a time in the past. Please try rephrasing your command. Specifying the location instead of using a time zone may help.'

    perform_action = re.search('^/(\w+) (.*)', reminder)
    if perform_action:
        reply = '\x01ACTION %s %s\x01' % (end_verb(perform_action.group(1).lower()), perform_action.group(2))
        short_reply = 'ACTION %s %s' % (end_verb(perform_action.group(1).lower()), perform_action.group(2))
    else:
        reply = '\x02[Reminder]\x02 %s: %s' % (nick, reminder)
        short_reply = reminder

    with open('reminders.json', 'r+') as fd:
        reminders = json.load(fd)

        if channel not in reminders:
            reminders[channel] = []
            
        rem_id = ''.join(random.sample(string.hexdigits[:16], k=4))
        while 1:
            if rem_id in thread_list:
                rem_id = ''.join(random.sample(string.hexdigits[:16], k=4))
            else:
                break
        
        rem = {'rem_id': rem_id, 'time': time.time() + time_until, 'user': nick, 'reply': reply, 'short_reply': short_reply}
        reminders[channel].append(rem)
        
        save(reminders, fd)

    t = threading.Timer(time_until, timer_func, [rem, channel, rem_lock, irc])
    thread_list[rem_id] = {'thread': t, 'user': nick}
    t.daemon = True
    t.start()

    alert_time = get_alert_time(time_until, nick)
    time_until_text = get_time_until_text(time_until)
    
    if alert_time:
        return '%s, \x02%s set for:\x02 %s • %s • \x02id:\x02 %s' % (nick, 'action' if perform_action else 'reminder', alert_time, time_until_text, rem_id)


def timer_func(rem, channel, rem_lock, irc):
    from send import send
    
    reply = rem['reply']
    send(reply, irc, channel)
    
    with rem_lock, open('reminders.json', 'r+') as fd:
        reminders = json.load(fd)
        reminders[channel].remove(rem)

        if not reminders[channel]:
            del reminders[channel]

        save(reminders, fd)


def in_reminder(msg, nick, channel, thread_list, rem_lock, irc):
    regex = re.compile('^\s+((\d+)(w|W))?((\d+)(d|D))?((\d+)(h|H))?((\d+)(m|M))?((\d+)(s|S))? (.*)')
    m = regex.match(msg)

    if not m:
        return '\x02Correct syntax\x02: .in <duration> <reminder> \x02Example\x02: .in 1w2d3h4m5s <message>, sends a reminder in 1 week, 2 days, 3 hours, 4 minutes, and 5 seconds'

    if m.group(1) or m.group(4) or m.group(7) or m.group(10) or m.group(13):
        delta = timedelta()
   
        if m.group(1):
            delta += timedelta(weeks=int(m.group(2)))
        if m.group(4):
            delta += timedelta(days=int(m.group(5)))
        if m.group(7):
            delta += timedelta(hours=int(m.group(8)))
        if m.group(10):
            delta += timedelta(minutes=int(m.group(11)))
        if m.group(13):
            delta += timedelta(seconds=int(m.group(14)))
            
        time_until = delta.total_seconds()
        reminder = m.group(regex.groups).strip()
        
        return save_reminder(reminder, time_until, nick, channel, thread_list, rem_lock, irc)


def at_reminder(msg, nick, channel, thread_list, rem_lock, irc):
    m = re.search('^\s+(.*?)\s+send\s+(.*)', msg, re.IGNORECASE)
    if not m:
        return '\x02Correct syntax\x02: .at <what_time> send <reminder> or /<action> \x02Example\x02: .at 5pm Paris time on January 30 2018 send <message>, sends a reminder at 5pm CET on January 30, 2018'
    
    when = m.group(1)
    reminder = m.group(2).strip()
    wolfram_data = wolfram.waSearch('convert ({0}) to unix time'.format(when), True)
    
    if isinstance(wolfram_data, list):
        for pod in wolfram_data:
            try:
                if pod.get('title') == 'Result':
                    text_result = pod[0].find('plaintext').text.strip()
                    m = re.search('^(\d+) \(Unix time\)', text_result)
                    if m:
                        unix_time = float(m.group(1))
                        time_until = unix_time - time.time()
                        return save_reminder(reminder, time_until, nick, channel, thread_list, rem_lock, irc)
            except Exception as e:
                print(e)
                return 'Please try rephrasing your command'
        return 'Please try rephrasing your command'
    else:
        return wolfram_data

    

def delete_reminder(rem_id, nick, thread_list):
    valid_id = re.search('^[a-f0-9]{4,5}$', rem_id)
    if not valid_id:
        return 'Invalid reminder ID'
    
    if rem_id not in thread_list:
        return 'reminder does not exist'
    if thread_list[rem_id]['user'] != nick:
        return 'that reminder belongs to %s' % thread_list[rem_id]['user']
    with open('reminders.json', 'r+') as fd:
        reminders = json.load(fd)
        modified_channel = ''
        for channel in reminders:
            for rem in reminders[channel]:
                if rem['rem_id'] == rem_id:
                    deleted_reply = rem['short_reply']
                    reminders[channel].remove(rem)
                    modified_channel = channel
        if not reminders[modified_channel]:
            del reminders[modified_channel]
            
        save(reminders, fd)
        
    thread_list[rem_id]['thread'].cancel()
    del thread_list[rem_id]
    return 'Deleted reminder: "%s"' % (deleted_reply)


def view_reminders(nick, channel, specified_channel):
    if specified_channel:
        target_channel = specified_channel
    else:
        target_channel = channel
        
    recent_reminders = []
    count = 0
    
    with open('reminders.json') as fd:
        reminders = json.load(fd)
        
    try:
        for rem in reversed(reminders.get(target_channel)):
            if nick == rem['user']:
                reply_preview = re.sub('(@)([\w])', '\g<1>\u200b\g<2>', rem['short_reply'])
                if len(reply_preview) > 20:
                    reply_preview = reply_preview[:20].strip() + '...'
                reply_preview = '"' + reply_preview + '"'
                
                recent_reminders.append('[{0}] {1}'.format(bold(rem['rem_id']), reply_preview))
                count += 1
                if count >= 15:
                    break
    except Exception:
        return 'You don\'t have any reminders in ' + target_channel
    
    if recent_reminders:
        return 'Your {0} reminders: {1}'.format(target_channel, ' '.join(recent_reminders))
    else:
        return 'You don\'t have any reminders in this channel'


def view_single_reminder(rem_id, nick):
    valid_id = re.search('^[a-f0-9]{4,5}$', rem_id)
    if not valid_id:
        return 'Invalid reminder ID'
    
    with open('reminders.json') as fd:
        reminders = json.load(fd)

    for channel in reminders:
        for rem in reminders[channel]:
            if rem['rem_id'] == rem_id.strip():
                time_until = rem['time'] - time.time()
                
                reply_preview = re.sub('(@)([\w])', '\g<1>\u200b\g<2>', rem['short_reply'])      
                time_until_text = get_time_until_text(time_until)
                alert_time = get_alert_time(time_until, nick)
                
                return '\x02[{0}]\x02 "{1}" • {2} • \x02Set for:\x02 {3}'.format(rem['rem_id'], reply_preview, time_until_text, alert_time)
                                                                         
    return 'No reminder with this ID'


def get_time_until_text(time_until):
    m, s = divmod(time_until, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    y, d = divmod(d, 365)

    times = [[y, 'years'], [d, 'days'], [h, 'hours'], [m, 'minutes'], [s, 'seconds']]
    
    time_until_list = []
    for duration in times:
        if int(duration[0]) > 0:
            time_until_list.append('{0} {1}'.format(int(duration[0]), duration[1] if duration[0] > 1 else duration[1][:-1]))

    return '\x02Remaining time:\x02 ' + ', '.join(time_until_list)


def get_alert_time(time_until, nick):
    if time_until > 0:
        delta = timedelta(seconds=time_until)
        TZ = nicktime.getTZ(nick)
        if TZ:
            utc_dt = datetime.utcnow() + delta
            local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(TZ))
            alert_time = nicktime.dt_format(local_dt)
        else:
            utc_dt = datetime.now(pytz.timezone('UTC')) + delta
            alert_time = nicktime.dt_format(utc_dt)
        return alert_time


def start_reminders_on_join(channel, thread_list, rem_lock, irc):
    with open('reminders.json') as fd:
        reminders = json.load(fd)

        for rem in reminders.get(channel, []):
            t = threading.Timer(rem['time'] - time.time(), timer_func, [rem, channel, rem_lock, irc])
            thread_list[rem['rem_id']] = {'thread': t, 'user': rem['user']}
            t.daemon = True
            t.start()


def save(data, data_file):
    try:
        data_file.seek(0)
        json.dump(data, data_file, indent=2, sort_keys=True)
        data_file.truncate()
    except Exception:
        raise
    

def end_verb(verb):
    if len(verb) >= 2:
        m1 = re.search('^.*?(ies|es|[^s]s)$', verb)
        if m1:
            return verb
        m2 = re.search('^.*?(o|sh|ch|tch|x|z|ss)$', verb)
        if m2:
            return verb + 'es'
        m3 = re.search('^.*?(a|e|i|o|u)?y$', verb)
        if m3 and not m3.group(1):
            return verb[:-1] + 'ies'
        return verb + 's'
    else:
        return verb
            
