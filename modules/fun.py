import re

def kitty(caller, nick):
    nick = nick.strip()
    if nick:
        return "\x02{}\x02's kitten climbs onto \x02{}\x02's lap and paws \x02{}\x02's face".format(caller, nick, nick)


def pet(caller, nick):
    nick = nick.strip()
    if nick:
        return "*{} pets {}* https://kitsunemimi.pw/tmp/24.mp4".format(caller, nick)


def cookie(msg):
    match = re.search('^\s+([\w\d@_-]+)( ([\w\d\- ]+))?\s*$', msg)
    if match:
        if match.group(3):
            return "\x01ACTION hands {} a plate of {} cookies and a glass of milk\001".format(match.group(1), match.group(3).strip())
        else:
            return "\x01ACTION hands {} a plate of cookies and a glass of milk\001".format(match.group(1))


def cake(msg):
    match = re.search('^\s+([\w\d@_-]+)( ([\w\d\- ]+))?\s*$', msg)
    if match:
        if match.group(3):
            return "\x01ACTION hands {} a slice of {} cake and a plastic fork\001".format(match.group(1), match.group(3).strip())
        else:
            return "\x01ACTION hands {} a slice of cake and a plastic fork\001".format(match.group(1))
		
		
def pie(msg):
    match = re.search('^\s+([\w\d@_-]+)( ([\w\d\'\- ]+))?\s*$', msg)
    if match:
        if match.group(3):
            return "\x01ACTION hands {} a slice of {} pie and a cheap plastic fork\001".format(match.group(1), match.group(3).strip())
        else:
            return "\x01ACTION hands {} a slice of pie and a cheap plastic fork\001".format(match.group(1))

def pizza(msg):
    match = re.search('^\s+([\w\d@_-]+)( ([\w\d\- ]+))?\s*$', msg)
    if match:
        if match.group(3):
            return "\x01ACTION serves {} a slice of {} pizza\001".format(match.group(1), match.group(3).strip())
        else:
            return "\x01ACTION serves {} a slice of pizza\001".format(match.group(1))


def tea(msg):
    match = re.search('^\s+([\w\d@_-]+)( ([\w\d\- ]+))?\s*$', msg)
    if match:
        if match.group(3):
            return "\x01ACTION hands {} a cup of {} tea and a plate of crumpets\001".format(match.group(1), match.group(3).strip())
        else:
            return "\x01ACTION hands {} a cup of tea and a plate of crumpets\001".format(match.group(1))          


def coffee(msg):
    match = re.search('^\s+([\w\d@_-]+)( ([\w\d\- ]+))?\s*$', msg)
    if match:
        if match.group(3):
            return "\x01ACTION hands {} a cup of {} coffee and a plate of mini donuts.\001".format(match.group(1), match.group(3).strip())
        else:
            return "\x01ACTION hands {} a cup of coffee and a plate of mini donuts.\001".format(match.group(1))

