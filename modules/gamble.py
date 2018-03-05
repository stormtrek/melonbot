from modules import money
import random
import json
import re

def bold(text):
    return '\x02' + text + '\x02'

gamblingAllowed = ['##test', '#melon', '#casino']
gamblingAllowed2 = [bold('#melon') + ' (https://telegram.me/joinchat/B1vfQz-4uWQeGe63CM3RwA)', bold('#casino') + ' (https://telegram.me/joinchat/B1vfQz8ipzZXHqGJEFoa1Q)']

def gamble(msg, nick, channel):
    if channel not in gamblingAllowed:
        return 'gambling is only allowed in: ' + ', '.join(gamblingAllowed2)
    m = re.search('^ (\-?\d+)\s*?$', msg)
    if m:
        bet = int(m.group(1))
        with open('pouch.json') as f:
            data = json.load(f)
            f.close()
        try:
            amt = data[nick]
            if amt:
                if bet <= amt and bet > 0:
                    roll = random.randint(1, 100)
                    if roll <= 49:
                        money.add(bet, nick)
                        return nick + ', you rolled ' + bold(str(roll)) + ' and won ' + bold(str(bet)) + ' \x0308coins\x03. You now have ' + bold(str(amt + bet)) + ' \x0308coins\x03.'
                    else:
                        money.remove(bet, nick)
                        return nick + ', you rolled ' + bold(str(roll)) + ' and lost ' + bold(str(bet)) + ' \x0308coins\x03. You now have ' + bold(str(amt - bet)) + ' \x0308coins\x03.'
                elif bet <= 0:
                    return nick + ', please enter a valid bet'
                else:
                    return nick + ', you don\'t have enough money for that bet'
            else:
                return nick + ', I\'m sorry but you don\'t have any money to gamble with'
        except:
            return nick + ', I\'m sorry but you don\'t have any money to gamble with'
        
