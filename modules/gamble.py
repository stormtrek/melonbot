"""
Module which enables the gambling of melon coins.
"""

from collections import OrderedDict
from formatting import bold
from modules import money
from json import load
import argparse
import random
import json
import re

parser = argparse.ArgumentParser()
parser.add_argument('--config', default='config.json', help='configuration file')
args = parser.parse_args()

with open(args.config) as fd:
    config = load(fd, object_pairs_hook=OrderedDict)

gambling_allowed = config['gambling_allowed']
gambling_allowed_tg_links = config['gambling_allowed_tg_links']

def gamble(msg, nick, channel):
    if channel not in gambling_allowed:
        return 'gambling is only allowed in: ' + ', '.join(gambling_allowed_tg_links if gambling_allowed_tg_links else gambling_allowed)
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
        
