def send(response, irc, channel = None):
    if channel:
        msg = 'PRIVMSG %s :%s' % (channel, response)
    else:
        msg = response

    irc.send(bytes('%s\r\n' % msg, 'UTF-8'))
    print('<< %s' % msg)


