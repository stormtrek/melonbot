from urllib.request import Request, urlopen
from decode import decode
import html
import re

def getTitle(msg, response):
    link = re.search('((http|https)://[^ ]+)', msg)
    if link:
        try:
            content = decode(urlopen(Request(link.group(0), headers={'User-Agent': 'Mozilla/5.0'}), timeout = 8).read())
        except:
            return response
        match = re.search('<(T|t)itle>(.*?)</(T|t)itle>', content, re.DOTALL)
        if match:
            title = re.sub('\r', '', match.group(2))
            return re.sub('\n', '', html.unescape(title.strip()))
    return response

