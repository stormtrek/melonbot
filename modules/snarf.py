from urllib.request import Request, urlopen
import requests
from decode import decode
import html
import re
import bs4

def getTitle(msg, response):
    link = re.search('((http|https)://[^ ]+)', msg)
    if link:
        try:
            r = requests.head(link.group(0), timeout=1)
            if "text/html" in r.headers["content-type"]:
                content = decode(urlopen(Request(link.group(0), headers={'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'en-US,en;q=0.5'}), timeout=1).read(16384))
            else:
                return response
        except Exception:
            return response
        soup = bs4.BeautifulSoup(content)
        title = soup.find('title')
        title = title.text.strip()
        if title:
            title = re.sub('\r', ' ', removeLinksFromTitle(title))
            return re.sub('\n', ' ', 'Title: ' + title[:441].strip())
    return response

def removeLinksFromTitle(link):
    return re.sub('((http|https)://[^ ]+)', '', link)

