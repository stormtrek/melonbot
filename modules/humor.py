import requests
import random
import math
import html
import bs4
import re

def getJoke():
    value = 2778
    s = requests.Session()
    s.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/600.3.18 (KHTML, like Gecko) Version/8.0.3 Safari/600.3.18'
    offset = random.randint(0, math.floor(int(value)/20)) * 20
    try:
        r = s.get('http://vk.com/wall-55955185', params={
            'offset': offset,
            'own': '1'}, timeout=2)
    except requests.exceptions.Timeout:
        return 'request timed out'
    if not r.ok:
        return 'could not reach server'
    soup = bs4.BeautifulSoup(r.text)
    result = soup.find_all('div', class_='wall_post_text')[random.randint(0, len(soup.find_all('div', class_='wall_post_text')) - 1)]
    for tag in result.find_all('a'):
        tag.replaceWith('')
    result = str(result)[:-6]
    result = result[result.index('>') + 1:]
    result = re.sub('(\s*<br/>)+', ' ⇒ ', result)
    result = re.sub('<(.*?)>', '', result)
    result = re.sub('⇒\s*⇒', '⇒', result)
    result = re.sub('(\s*⇒\s*)$', '', html.unescape(result))
    return result

def getFML():
    s = requests.Session()
    s.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/600.3.18 (KHTML, like Gecko) Version/8.0.3 Safari/600.3.18'
    try:
        r = s.get('http://www.fmylife.com/random', timeout=5)
    except requests.exceptions.Timeout:
        return 'request timed out'
    if not r.ok:
        return 'could not reach server'
    content = r.text
    m = re.search('">([^(</)]*?)</a>\s</p>', content, re.DOTALL)
    result = re.sub('(\n)+', ' ⇒ ', m.group(1).strip())
    return re.sub('(\r\n)+', ' ⇒ ', html.unescape(result))

