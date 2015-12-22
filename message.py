import re

class Message(object):
    regex = re.compile('^:([^ ]+)!([^ ]+)@([^ ]+) PRIVMSG ([^ ]+) :((\.[\w]+)?(.*))')
    def __init__(self, data):
        match = Message.regex.match(data)
        self.nick, self.user, self.host, self.channel, self.fullMsg, self.prefix, self.msg = match.groups()
        if self.prefix:
            self.prefix = self.prefix[1:]


