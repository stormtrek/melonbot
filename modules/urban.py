from urllib.request import urlopen
from decode import decode
import html
import re


def getDefn(msg):
    m = re.search(' (.*?)((\[|\()([\d]+)(\]|\)))?\s*$', msg)
    if m:
        word = m.group(1).replace(' ', '+')
        pos = m.group(4)
        try:
            content = decode(urlopen('http://urbandictionary.com/define.php?term=' + word).read())
        except Exception as e:
            return 'Error: ', e
        if pos == None:
            m = re.search('meaning\'>\s(.*?)\s</div>', content)
            if m:
                defn = m.group(1)
            else:
                return '.: that word is not defined :.'
        else:
            pos = int(pos) - 1
            m = re.findall('meaning\'>\s(.*?)\s</div>', content)
            if m:
                try:
                    defn = m[pos]
                except:
                    return 'entry ' + str(pos + 1) + ' does not exist'
            else:
                return '.: that word is not defined :.'
        defn = re.sub('<.*?>', '', defn)
        return re.sub('\r', ' ↲', html.unescape(defn))

