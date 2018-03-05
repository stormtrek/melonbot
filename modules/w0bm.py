import requests
import html
import bs4
import re

def getVid(query):
        try:
                r = requests.get('https://w0bm.com/' + ''.join(query.split()).lower(), timeout=1)
                if not r.ok:
                    return('could not connect to server')
        except Exception:
                return('request timed out')
        soup = bs4.BeautifulSoup(r.text)
        try:
            video = soup.find('video').get('src')
        except:
            return('video not found')
        cat = re.search('/([\d]+)/fav">.*Category:</strong> (.*?)"', html.unescape(str(soup)), re.DOTALL)
        if cat.group(2) != 'Pr0n':
                return('\x02[\x0310' + cat.group(2) + '\x03/\x0307' + cat.group(1) + '\x03]\x02 https:' + video)
        else:
                return('\x02[\x0304' + cat.group(2) + '\x03/\x0303' + cat.group(1) + '\x03]\x02 https:' + video)
