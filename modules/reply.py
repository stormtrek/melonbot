import re

def salutations(msg, nick, botnick, response):
    regex = re.compile('^(%s)?(:|,)?\s*((h|H)i|(h|H)ey|(h|H)ello|'
                  '(y|Y)o|(s|S)up|(h|H)ola|(g|G)reetings|(e|E)llo|(s|S)halom)( (%s))?\s*$' % (botnick, botnick))
    match = regex.match(msg)
    if match:
        if match.group(1) or match.group(regex.groups):
            return '%s %s ( ･ω･)ﾉ' % (match.group(3), nick)
    return response


def love(msg, nick, botnick, response):
    regex = re.compile('^(%s)?(:|,)?\s*(I |i )?(L|l)ove (you|u|ya)?( (%s))?\s*$' % (botnick, botnick))
    match = regex.match(msg)
    if match:
        if match.group(1) or match.group(regex.groups):
            return '<3 you too %s' % nick
    return response


def noProb(msg, nick, botnick, response):
    regex = re.compile('^(%s)?(:|,)?\s*((T|t)hank(s)?( (yo)?u)?|ty)( (%s))?\s*$' % (botnick, botnick))
    match = regex.match(msg)
    if match:
        if match.group(1) or match.group(regex.groups):
            return 'no problem %s' % nick
    return response


def ctcpAction(msg, nick, botnick, response):
    match = re.search('\x01ACTION ([\w\d ]+) %s\s*\x01' % botnick, msg)
    if match:
        if match.group(1) == 'hugs':
            return '\x01ACTION %s %s\x01' % ('hugs', nick)
        elif match.group(1) == 'pets':
            return '\x01ACTION purrs\x01'
        else:
            return '\x01ACTION %s %s\x01' % (match.group(1), nick)
    return response
