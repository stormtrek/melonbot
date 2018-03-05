import requests
import bs4
import re
 
def translate(msg):
    autoDetect = False
    m = re.search('^ ([\w\-\,]+) (.*)', msg.lower())
    if m:
        langs = m.group(1).split(',')
        if len(langs) == 1:
            autoDetect= True              
        if autoDetect:
            source = 'auto'
            target = langs[0]
            text = m.group(2).strip()
        else:
            source = langs[0]
            target = langs[1]
            text = m.group(2).strip()
             
        r = requests.get('https://translate.google.com/m', params={
            'sl': source,
            'hl': target,
            'q': text
        })
        if not r.ok:
            return 'could not connect to server'
        soup = bs4.BeautifulSoup(r.text)
        result = soup.find('div', class_='t0')
        try:
            if not result.text:
                return 'nothing returned'
        except:
            return 'please enter text to translate'
        return result.text
