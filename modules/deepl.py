import json
import requests
import re

supported_langs = ['EN', 'DE', 'FR', 'ES', 'IT', 'NL', 'PL']
supported_langs_name = {'EN': 'English', 'DE': 'German', 'FR': 'French', 'ES': 'Spanish', 'IT': 'Italian', 'NL': 'Dutch', 'PL': 'Polish'}

def create_payload(text, target_lang, source_lang):
    """Create payload for DeepL API call"""
    return {
        "jsonrpc": "2.0", "method": "LMT_handle_jobs", "id": 1,
        "params": {
            "jobs": [{"kind": "default", "raw_en_sentence": text}],
            "lang": {"user_preferred_langs": [source_lang, target_lang],
                     "source_lang_user_selected": source_lang,
                     "target_lang": target_lang},
            "priority": 1}}


def translate(msg):
    autoDetect = False
    m = re.search('^ ([\w\,]+) (.*)', msg)
    if m:
        langs = m.group(1).split(',')
        if len(langs) == 1:
            autoDetect= True              
        if autoDetect:
            source_lang = 'auto'
            target_lang = langs[0].upper()
            text = m.group(2).strip()
        else:
            if langs[0].lower() == 'auto':
                source_lang = 'auto'
            else:
                source_lang = langs[0].upper()
            target_lang = langs[1].upper()
            text = m.group(2).strip()
            
        supported_langs_text = 'Supported languages are: '
        
        for i in range(0, len(supported_langs)):
            if i < len(supported_langs) - 1:
                supported_langs_text += supported_langs_name[supported_langs[i]] + ' (' + supported_langs[i] + '), '
            else: 
                supported_langs_text += 'and ' + supported_langs_name[supported_langs[i]] + ' (' + supported_langs[i] + ').'
                
        if target_lang == 'AUTO':
            return 'Target language cannot be auto-detect. ' + supported_langs_text 
        elif source_lang == 'auto':
            if target_lang not in supported_langs:
                return supported_langs_text
        elif source_lang not in supported_langs or target_lang not in supported_langs:
            return supported_langs_text
                
        url = 'https://deepl.com/jsonrpc'
        payload = create_payload(text, target_lang, source_lang)
        headers = {'content-type': 'application/json'}
        
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        if not r.ok:
            return 'could not connect to server'

        result = json.loads(r.text)['result']['translations'][0]['beams'][0]['postprocessed_sentence']
        if result:
            return result
        else:
            return 'No translations'


