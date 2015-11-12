from urllib.request import urlopen
from decode import decode
import re

def getList():
    try:
        content = decode(urlopen('http://freechampionrotation.com').read())
    except:
        return '.: could not reach server :.'
    try:
        m = re.findall('<h1>(.*?)<', content)
        if m:
            return ', '.join(m)
    except:
        return '.: could not find free champion rotation data :.'
