import time, json, re
from json.decoder import JSONDecodeError

try:
    with open('memo.json', 'x') as f:
        f.write('{}')
except FileExistsError:
    pass

def save_memo(msg, nick):
    
    m = re.search('^\s+([^ ]+) (.*)', msg)
    
    if not m:
        return '\x02Correct syntax\x02: .memo <targer_user> <message> \x02Tips\x02: Target user can be written as a regular expression \x02Example\x02: .memo randomdude check our google doc \x02OR\x02 .memo randomdude|RandDude check our google doc'
        
    if m.group(1).lower() == nick.lower():
        return 'You can tell yourself that'

    key = m.group(1)
        
    nick = nick[:1] + '\u200B' + nick[1:]
    
    memo = ', on {0} UTC: \x02<{1}>\x02 {2}'.format(time.strftime('%d %b %H:%M', time.gmtime()), nick, m.group(2).strip())
    
    memo_dict = {key: [memo]}

    try:
        with open('memo.json') as f:
            data = json.load(f)
    except (FileNotFoundError, JSONDecodeError):
        print('memo.json is empty or corrupted, resetting')

        with open('memo.json', 'w') as f:
            f.write('{}')

        data = {}

    try:
        data[key].append(memo)
    except:
        data.update(memo_dict)

    with open('memo.json', 'w') as f:
        json.dump(data, f)

    return "Thank you for choosing m\u200Belon's telegram service"


def memo_check(nick, response):
    memos = []
    delete_keys = []

    try:
        with open('memo.json') as f:
            data = json.load(f)
    except (FileNotFoundError, JSONDecodeError):
        print('memo.json is empty or corrupted, resetting')

        with open('memo.json', 'w') as f:
            f.write('{}')

        data = {}

    for key, value in data.items():
        if re.fullmatch(key, nick, re.IGNORECASE):
            for memo in data[key]:  
                memos.append(nick + memo)
            delete_keys.append(key)
    for key in delete_keys:
        del data[key]
        
    with open('memo.json', 'w') as f:
        json.dump(data, f)
        
    if memos:
        return memos
    
    return response
