import re
import json
from formatting import bold
from collections import OrderedDict

try:
    with open('pouch.json', 'x') as f:
        f.write('{}')
except FileExistsError:
    pass

def save(data, data_file):
    try:
        data_file.seek(0)
        json.dump(data, data_file, indent=2)
        data_file.truncate()
    except Exception:
        raise

def add(amount, nick):
    balance = get_balance(nick)
        
    if balance is None:
        create_account(nick)
        
    with open('pouch.json', 'r+') as f:
        data = json.load(f, object_pairs_hook=OrderedDict)
        
        data[nick] += amount

        save(data, f)


def remove(amount, nick):
    with open('pouch.json', 'r+') as f:
        data = json.load(f, object_pairs_hook=OrderedDict)
        
        data[nick] -= amount
        
        save(data, f)


def get_balance(nick):
    with open('pouch.json') as f:
        data = json.load(f)
        
    return data.get(nick, None)


def create_account(nick):
    with open('pouch.json', 'r+') as f:
        data = json.load(f)
        
        data.update({nick: 0})
        
        data = OrderedDict(sorted(data.items(), key=lambda t: t[0].lower()))

        save(data, f)
    

def transfer(msg, nick):
    m = re.search('^\s+(\-?\d+)\s+([^ ]+)\s*$', msg)
    
    if not m:
        return 'Correct syntax: .transfer <amount> <target_user>'
    
    target = m.group(2)
    
    if target.lower() == nick.lower():
        return nick + ', you cannot transfer money to yourself'
    
    balance = get_balance(nick)

    if balance is None or balance <= 0:
        return nick + ', you don\'t have any money to transfer'
    
    amount = int(m.group(1))
    
    if amount <= balance and amount > 0:
        target_balance = get_balance(target)

        if target_balance is not None:
            add(amount, target)
            remove(amount, nick)

            return '{0}, you transferred {1} \x0308coins\x03 to {2}. You now have {3} \x0308coins\x03.'.format(nick, bold(str(amount)), target, bold(str(balance - amount)))

        else:
            return nick + ': target user must be registered to receive money (.register to register)'
        
    elif amount > balance:
        return nick + ', you don\'t have enough money for this transfer'
    
    else:
        return nick + ', please enter a valid transfer amount'
        

def check_balance(nick):
    balance = get_balance(nick)
    
    if balance is not None and balance > 0:
        return '{0}: You have {1} \x0308coins\x03 in your coin pouch.'.format(nick, bold(str(balance)))
    
    return nick + ': You don\'t have any money in your coin pouch.'


def register(nick):
    balance = get_balance(nick)
    
    if balance is not None:
        return nick + ', your account is already registered'
    else:
        create_account(nick)
        return nick + ': registration complete!'


def get_wealth_ranking():
    with open('pouch.json') as f:
        data = json.load(f)

    sorted_list = []
    for key, value in sorted(data.items(), key=lambda x: x[1], reverse=True):
        sorted_list.append({'user': key, 'amount': value})

    size = len(sorted_list)
    if size < 10:
        ranking_size = size
    else:
        ranking_size = 10

    ranking_list = []
    for idx, val in enumerate(sorted_list[:ranking_size]):
        user = val['user']
        if val['user'][0] != '@':
            user = val['user'][:1] + '\u200b' + val['user'][1:]
        ranking_list.append('\x02({0})\x02 {1}: {2}'.format(str(idx + 1), bold(user), val['amount']))

    return '[\x02Wealth Ranking\x02]  ' + ' — '.join(ranking_list)
        
