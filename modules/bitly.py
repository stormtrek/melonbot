from collections import OrderedDict
from urllib.request import urlopen
from json import load, loads
from decode import decode
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--config', default='config.json', help='configuration file')
args = parser.parse_args()

with open(args.config) as fd:
    config = load(fd, object_pairs_hook=OrderedDict)

access_token = config['bitly_key']

def shorten(url):
    try:
        content = loads(decode(urlopen('https://api-ssl.bitly.com/v3/shorten?access_token={0}&longUrl={1}'.format(access_token, url.strip())).read()))
    except:
        return 'could not reach server'
    try:
        return content['data']['url']
    except:
        return content['status_txt']
