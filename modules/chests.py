from modules import money
import random, json

items = {'wc': '\x0305wooden chest\x03'}

try:
    with open('chests.json', 'x') as f:
        f.write('{}')
except FileExistsError:
    pass

def open_chests(nick):
    with open('chests.json') as f:
        data = json.load(f)
        f.close()
    try:
        numChests = data[nick]
        coins = 0
        if numChests:
            for i in range(numChests):
                coins += random.randint(100,200)
            data[nick] = 0
        else:
            return nick + ': I\'m sorry but you don\'t have any chests to open.'
    except:
        return nick + ': I\'m sorry but you don\'t have any chests to open.'
    with open('chests.json', 'w') as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.close()
    if coins:
        money.add(coins, nick)
        return nick + ': you opened \x02' + str(numChests) + '\x02 ' + items['wc'] + ' and found \x02' + str(coins) + '\x02 \x0308coins\x03.'

def save_chest(nick):
    d = {nick: 1}
    with open('chests.json') as f:
        data = json.load(f)
        f.close()
    try:
        data[nick] += 1
    except:
        data.update(d)
    with open('chests.json', 'w') as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.close()

def chest_drops(nick):
    if (random.randint(0,99) == random.randint(0,99)):
        save_chest(nick)
        return nick + ': you found a ' + items['wc'] + '! (.open to open chests)'
