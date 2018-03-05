from urllib.request import urlopen
from decode import decode
import html
import re

def getSyn(word):
    try:
        content = decode(urlopen('http://www.thesaurus.com/browse/' + word.replace(' ', '+').strip()).read())
    except:
        return '.: could not reach server :.'
    m = re.findall('"text">(.*?)</span>\s*<s', content)
    if m:
        if len(m) > 10:
            return ', '.join(m[:10])
        else:
            return ', '.join(m)
    else:
        return '.: no synonyms available :.'

##def getDefn(word):
##    try:
##        content = decode(urlopen('http://dictionary.reference.com/browse/' + word.replace(' ', '+').strip()).read())
##    except:
##        return '.: that entry does not exist :.'
##    m = re.search('def-content">(.*?)</div>', content, re.DOTALL)
##    if m:
##        defn = re.sub('<.*?>', '', m.group(1))
##        return re.sub('\n', '', html.unescape(defn).strip())
##    else:
##        return '.: no definitions available :.'
