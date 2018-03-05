import re

def salutations(msg, nick, botnick, response):
    regex = re.compile('^(%s)?(:|,)?\s*(hi|hey|hello|'
                  'yo|sup|hola|greetings|ello|shalom|heyo|what\'s up|what\'s good)( (%s))?\s*$' % (botnick, botnick))
    match = regex.match(msg.lower())
    if match:
        if match.group(1) or match.group(regex.groups):
            return '%s %s ( ･ω･)ﾉ' % (match.group(3), nick)
    return response


def love(msg, nick, botnick, response):
    regex = re.compile('^(%s)?(:|,)?\s*(i )?(love)( (you|u*|ya|yew))?( (%s))?\s*$' % (botnick, botnick))
    match = regex.match(msg.lower())
    if match:
        if (match.group(1) and match.group(4) and match.group(5)) or match.group(regex.groups):
            return '<3 you too %s' % nick
    return response


def noProb(msg, nick, botnick, response):
    regex = re.compile('^(%s)?(:|,)?\s*(th(a|e)nk(s)?( (you|yew|u))?|ty|danke|gracias)( (%s))?\s*$' % (botnick, botnick))
    match = regex.match(msg.lower())
    if match:
        if match.group(1) or match.group(regex.groups):
            if match.group(4):
                if match.group(4) == 'e':
                    return 'ur welcum %s（。々°）' % nick
            return 'You\'re welcome %s' % nick
    return response


def ctcpAction(msg, nick, botnick, response):
    match = re.search('\x01ACTION ([\w\d ]+) %s\s*\x01' % botnick, msg)
    if match:
        if match.group(1) == 'hugs':
            return '\x01ACTION %s %s <3\x01' % ('hugs', nick)
        elif match.group(1) == 'pets':
            return '\x01ACTION purrs\x01'
        else: 
            return '\x01ACTION %s %s\x01' % (match.group(1), nick)
    return response


def lenny(msg, response):
    match = re.search('^lenny|[^\w]+lenny', msg.lower())
    if match:
        return '( ͡° ͜ʖ ͡°)'
    return response

def ayy(msg, response):
    match = re.search('^ayy|[^\w]+ayy', msg.lower())
    if match:
        return '(☞ﾟヮﾟ)☞'
    return response

def shrug(msg, response):
    match = re.search('^shrug|[^\w]+shrug', msg.lower())
    if match:
        return '¯\_(ツ)_/¯'
    return response

def derp(msg, response):
    match = re.search('^(herp|derp)(?<!i)(\s+[^\s]+)?$|[^\w]+(herp|derp)(?<!i)(\s+[^\s]+)?$', msg.lower())
    if match:
        return '（。々°）'
    return response


