import requests
import bs4
import re
 
def translate(msg):
    auto_detect = False
    
    m = re.search('^ ([\w\-\,]+) (.*)', msg.lower())
    
    if not m:
        return '\x02Correct syntax:\x02 .translate <source language>, <target language> <text>'
    
    langs = m.group(1).split(',')
    
    if len(langs) == 1:
        auto_detect= True
        
    if auto_detect:
        source = 'auto'
        target = langs[0]
        text = m.group(2).strip()
    else:
        source = langs[0]
        target = langs[1]
        text = m.group(2).strip()

    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0'
    }
         
    r = requests.get('https://translate.google.com/m', headers=headers, params={
        'sl': source,
        'tl': target,
        'hl': target,
        'q': text
    })
    
    if not r.ok:
        print(r.status_code)
        return 'Could not connect to server'
    
    soup = bs4.BeautifulSoup(r.text)
    result = soup.find('div', class_='t0')
    
    try:
        if not result.text:
            return 'Nothing returned'
    except:
        return 'Please enter text to translate'
    
    return result.text
