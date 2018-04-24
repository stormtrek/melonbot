from collections import OrderedDict
from urllib.parse import quote_plus
from urllib.request import urlopen
from decode import decode
import xml.etree.ElementTree as ET
import argparse
import json
import html
import re

parser = argparse.ArgumentParser()
parser.add_argument('--config', default='config.json', help='configuration file')
args = parser.parse_args()

with open(args.config) as fd:
    config = json.load(fd, object_pairs_hook=OrderedDict)
    
app_id = config['wolfram_alpha_key']

div = ' ➤ '
numOfPods = 3

def waSearch(search, return_data=False, dict_version=False):
    search = search.strip()

    if not search:
        return 'No search term'
    
    try:
        content = decode(urlopen('http://api.wolframalpha.com/v2/query?appid=' + app_id + ('&input=define+(word)+' if dict_version else '&input=') + quote_plus(search) + '&format=plaintext').read())
    except:
        return 'Could not reach Wolfram Alpha at this time'
    
    root = ET.fromstring(content)
    pods = root.findall('pod')
    output = ''
    
    if return_data:
        return pods
    
    if len(pods) > numOfPods:
        loopLen = numOfPods - 1
    else:
        loopLen = len(pods) - 1
        
    i = 0
    while i <= loopLen:
        hasResult = False
        if dict_version:
            result = ''
        else:
            title = pods[i].get('title')
            if title == 'Input interpretation':
                title = 'Input'
            result = '\x02' + title + ':\x02 '
        
        try:
            text_result = pods[i][0].find('plaintext')
            if text_result.text != None:
                result += text_result.text.strip()
                hasResult = True
            elif loopLen < len(pods) - 1:
                loopLen += 1
        except Exception:
            pass
        
        try:
            image_result = pods[i][0].find('imagesource')
            if image_result.text:
                result += image_result.text
                hasResult = True
        except Exception:
            pass
        
        if hasResult:
            output += result + div
            
        i += 1
        
    if output:
        return formatting(output, dict_version)
    else:
        return 'No results'


def formatting(output, dict_version=False):
    if dict_version:
        output = re.sub('\r', ' ➤ ', output)
        output = re.sub('\n', ' ➤ ', output)
    else:
        output = re.sub('\r', '  ◆  ', output)
        output = re.sub('\n', '  ◆  ', output)
    for m in re.findall(r'\\:[a-f0-9]{4}', output):
        output = re.sub(re.escape(m), chr(int(m[2:], 16)), output)
    return output[:-len(div)].replace('', '=')
