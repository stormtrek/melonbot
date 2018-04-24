from urllib.parse import quote_plus
from datetime import datetime
from formatting import bold
import requests
import html
import re

position_reset = 1800 #30 minutes
 
def getDefn(msg, urbanList, channel):
    m = re.search('^\s+(.*?)((\[|\()([\d]+)(\]|\)))?\s*$', msg)
    if m:
        word = m.group(1).strip().lower()
        pos = m.group(4)
        urbanList[channel][1] = word
    else:
        if not msg.strip():
            if urbanList[channel][1]:
                word = urbanList[channel][1]
                pos = None
            else:
                return 'please enter a word'
        else:
            return 'syntax: .ud <word> [<entry_position>]*'
    try:
        r = requests.get('http://api.urbandictionary.com/v0/define', params={'term': word})
    except:
        return 'could not reach server'
    data = r.json()['list']
    if len(data) == 0:
        return 'that word is not defined'
    if not pos:
        if word not in urbanList[channel][0]:
            urbanList[channel][0][word] = [1, None]
        if urbanList[channel][0][word][1]:
            if (datetime.now() - urbanList[channel][0][word][1]).total_seconds() > position_reset:
                urbanList[channel][0][word][0] = 1
        pos = urbanList[channel][0][word][0]
        urbanList[channel][0][word] = [pos + 1, datetime.now()]
        if urbanList[channel][0][word][0] > len(data):
            urbanList[channel][0][word][0] = 1
    else:
        urbanList[channel][0][word] = [int(pos) + 1, datetime.now()]
        if urbanList[channel][0][word][0] > len(data):
            urbanList[channel][0][word][0] = 1
    pos = int(pos) - 1
    try:
        defn = '\x02({0}. {1})\x02 {2}{3}'.format(str(pos + 1), data[pos]['word'], data[pos]['definition'].strip(), bold(' [ex.] ') + data[pos]['example'].strip() if data[pos]['example'] else '')
        defn = re.sub('(\n\n)+', ' ⇒ ', defn)
        return re.sub('(\r\n)+', ' ⇒ ', defn)
    except:
        return 'entry ' + str(pos + 1) + ' does not exist'

