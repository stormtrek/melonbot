from urllib.request import urlopen
from decode import decode
from json import loads

access_token = ''

def shorten(url, nick):
    try:
        content = loads(decode(urlopen('https://api-ssl.bitly.com/v3/shorten?access_token=' + access_token +
                                       '&longUrl=' + url.strip()).read()))
    except:
        return '.: could not reach server :.'
    try:
        return nick + ': ' + content['data']['url']
    except:
        return content['status_txt']
