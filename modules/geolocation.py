from urllib.request import urlopen
from decode import decode
import re

def locate(ip, nick):
    try:
        content = decode(urlopen('http://ip-api.com/csv/' + ip.strip()).read())
    except:
        return 'Could not reach server'
    m = re.search('success,(.*?),.*?,.*?,(.*?),(.*?),.*?,.*?,.*?,(.*?),(.*?),', content)
    if m:
        result = ': [ \x02City\x02: %s | \x02Region\x02: %s | \x02Country\x02: %s | \x02Timezone\x02: %s | \x02ISP\x02: %s ]' % (m.group(3), m.group(2), m.group(1), m.group(4), m.group(5))
        return nick + result.replace('"', '')
    else:
        return 'Invalid IP address'
