import re

def kitty(caller, nick):
    nick = nick.strip()
    if nick:
        return "\x02{}\x02's kitty climbs onto \x02{}\x02's lap and paws \x02{}\x02's face".format(caller, nick, nick)


def cookie(msg):
    match = re.search('^ ([\w\d_-]+)( ([\w\d\- ]+))?\s*$', msg)
    if match:
        if match.group(3):
            return "\x01ACTION gets {} a plate of {} cookies and a glass of milk\001".format(match.group(1), match.group(3).strip())
        else:
            return "\x01ACTION gets {} a plate of cookies and a glass of milk\001".format(match.group(1))


def cake(msg):
    match = re.search('^ ([\w\d_-]+)( ([\w\d\- ]+))?\s*$', msg)
    if match:
        if match.group(3):
            return "\x01ACTION gets {} a slice of {} cake and a plastic fork\001".format(match.group(1), match.group(3).strip())
        else:
            return "\x01ACTION gets {} a slice of cake and a plastic fork\001".format(match.group(1))


def tea(msg):
    match = re.search('^ ([\w\d_-]+)( ([\w\d\- ]+))?\s*$', msg)
    if match:
        if match.group(3):
            return "\x01ACTION gets {} a cup of {} tea and a plate of crumpets\001".format(match.group(1), match.group(3).strip())
        else:
            return "\x01ACTION gets {} a cup of tea and a plate of crumpets\001".format(match.group(1))          


def coffee(msg):
    match = re.search('^ ([\w\d_-]+)( ([\w\d\- ]+))?\s*$', msg)
    if match:
        if match.group(3):
            return "\x01ACTION gets {} a cup of {} coffee and a plate of mini donuts.\001".format(match.group(1), match.group(3).strip())
        else:
            return "\x01ACTION gets {} a cup of coffee and a plate of mini donuts.\001".format(match.group(1))

