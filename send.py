def send(response, irc, channel = None):
    if channel:
        irc.send(bytes('PRIVMSG %s :%s\r\n' % (channel, response), 'UTF-8'))
    else:
        irc.send(bytes('%s\r\n' % response, 'UTF-8'))


