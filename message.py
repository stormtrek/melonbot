import re

class Message(object):
    regex = re.compile('^:([^ ]+)!([^ ]+)@([^ ]+) PRIVMSG ([^ ]+) :((\.[\w#]+)?(.*))')
    def __init__(self, data):
        match = Message.regex.match(data)
        self.nick, self.user, self.host, self.channel, self.fullMsg, self.prefix, self.msg = match.groups()
        if self.prefix:
            self.prefix = self.prefix[1:]
            self.prefix = self.prefix.lower()
        self.msg = strip_colors(self.msg)

def strip_colors(text):
    text = re.sub(r'\x03\d{1,2}(?:,\d{1,2})?', '', text)
    text = re.sub(r'\x02|\x03|\x0F|\x16|\x1D|\x1F', '', text)
    return text

