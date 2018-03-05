import re
from collections import OrderedDict
import json
import traceback
from modules import nicktime

def modify(msg):
    m = re.search('^\s+([\w]+)\s(.*)', msg)
    if m:
        if m.group(1).lower() == 'nt':
            return mod_nicktime(m.group(2), 'nicktime')
    return None, None

def dump(data, data_file):
    try:
        data_file.seek(0)
        json.dump(data, data_file, indent=2, sort_keys=True)
        data_file.truncate()
    except Exception:
        raise

def mod_nicktime(mod, module):
    m = re.search('^([\w]+) (.*)', mod)
    try:
        task = m.group(1).lower()
    except Exception:
        return 'please provide a valid modifcation command', None
    params = m.group(2).strip()
    
    if m:
        if task == 'adduser':
            match = re.search('([\w@]+) ([\w]+) ([\w\s]+)(\(([\w\s]+)\))?', params)
            if match:
                user = match.group(1)
                if nicktime.getTZ(user, True, False):
                    return 'User ' + user + ' already exists', None
                tz = match.group(2)
                if not nicktime.tz_exists(tz):
                    return 'timezone ' + tz + ' does not exist', None
                if match.group(3).strip():
                    nicks = [item.strip() for item in match.group(3).strip().split(' ')]
                else:
                    return 'must include nicks', None
                if match.group(4):
                    display = match.group(5).strip()
                else:
                    display = nicks[0]    
                with open('nicktime.json', 'r+') as data_file:    
                    data = json.load(data_file, object_pairs_hook=OrderedDict)
                    data['users'][tz][user] = {'nicks': nicks, 'display': display}
                    dump(data, data_file)
                return '[nicktime] add_user operation successful', module

        if task == 'deluser':
            match = re.search('^([\w@]+)\s*$', params)
            if match:
                user = match.group(1)
                tz = nicktime.getTZ(user, True, False)
                if not tz:
                    return 'User ' + user + ' does not exist', None
                with open('nicktime.json', 'r+') as data_file:    
                    data = json.load(data_file, object_pairs_hook=OrderedDict)
                    del data['users'][tz][user]
                    dump(data, data_file)
                return '[nicktime] del_user operation successful', module

        if task == 'addnick':
            match = re.search('([\w@]+) ([\w\s]+)', params)
            if match:
                user = match.group(1)
                tz = nicktime.getTZ(user, True, False)
                if not tz:
                    return 'User ' + user + ' does not exist', None
                if match.group(2).strip():
                    nicks = [item.strip() for item in match.group(2).strip().split(' ')]
                else:
                    return 'must include nicks', None
                with open('nicktime.json', 'r+') as data_file:
                    data = json.load(data_file, object_pairs_hook=OrderedDict)
                    data['users'][tz][user]['nicks'].extend([item for item in nicks if item.lower() not in [item.lower() for item in data['users'][tz][user]['nicks']]])
                    dump(data, data_file)
                return '[nicktime] add_nick operation successful', module

        if task == 'delnick':
            match = re.search('([\w@]+) ([\w\s]+)', params)
            if match:
                user = match.group(1)
                tz = nicktime.getTZ(user, True, False)
                if not tz:
                    return 'User ' + user + ' does not exist', None
                if match.group(2).strip():
                    del_nicks = [item.strip() for item in match.group(2).strip().lower().split(' ')]
                else:
                    return 'must include nicks', None
                with open('nicktime.json', 'r+') as data_file:    
                    data = json.load(data_file, object_pairs_hook=OrderedDict)
                    new_nicks = [item for item in data['users'][tz][user]['nicks'] if item.lower() not in del_nicks]
                    data['users'][tz][user]['nicks'] = new_nicks
                    dump(data, data_file)
                return '[nicktime] del_nick operation successful', module

        if task == 'newname':
            match = re.search('^([\w@]+) ([\w@]+)\s*$', params)
            if match:
                oldUser = match.group(1)
                newUser = match.group(2)
                tz = nicktime.getTZ(oldUser, True, False)
                if not tz:
                    return 'User ' + oldUser + ' does not exist', None
                with open('nicktime.json', 'r+') as data_file:    
                    data = json.load(data_file, object_pairs_hook=OrderedDict)
                    tempData = data['users'][tz][oldUser]
                    del data['users'][tz][oldUser]
                    data['users'][tz][newUser] = tempData
                    dump(data, data_file)
                return '[nicktime] new_name operation successful', module

        if task == 'setname':
            match = re.search('([\w@]+) (.*)', params)
            if match:
                user = match.group(1)
                tz = nicktime.getTZ(user, True, False)
                if not tz:
                    return 'User ' + user + ' does not exist', None
                newDisplay = match.group(2).strip()
                with open('nicktime.json', 'r+') as data_file:    
                    data = json.load(data_file, object_pairs_hook=OrderedDict)
                    data['users'][tz][user]['display'] = newDisplay
                    dump(data, data_file)
                return '[nicktime] set_name operation successful', module

        if task == 'addtz':
            match = re.search('^([^ ]+) ([\w\-/]+)\s*$', params)
            if match:
                tzName = match.group(1)
                tzPytz = match.group(2)
                if nicktime.tz_exists(tzName):
                    return 'timezone ' + tzName + ' already exists', None
                with open('nicktime.json', 'r+') as data_file:    
                    data = json.load(data_file, object_pairs_hook=OrderedDict)
                    data['tzList'][tzName] = tzPytz
                    if tzName not in data['users']:
                        data['users'][tzName] = {}
                    dump(data, data_file)
                return '[nicktime] add_tz operation successful', module

        if task == 'deltz':
            match = re.search('^([^ ]+)\s*$', params)
            if match:
                tz = match.group(1)
                if not nicktime.tz_exists(tz):
                    return 'timezone ' + tz + ' does not exist', None
                with open('nicktime.json', 'r+') as data_file:    
                    data = json.load(data_file, object_pairs_hook=OrderedDict)
                    del data['tzList'][tz]
                    del data['users'][tz]
                    dump(data, data_file)
                return '[nicktime] del_tz operation successful', module

        if task == 'newtz':
            match = re.search('^([\w@]+) ([^ ]+)\s*$', params)
            if match:
                user = match.group(1)
                new_tz = match.group(2)
                old_tz = nicktime.getTZ(user, True, False)
                if not old_tz:
                    return 'User ' + user + ' does not exist', None
                with open('nicktime.json', 'r+') as data_file:    
                    data = json.load(data_file, object_pairs_hook=OrderedDict)
                    tempData = data['users'][old_tz][user]
                    del data['users'][old_tz][user]
                    data['users'][new_tz][user] = tempData
                    dump(data, data_file)
                return '[nicktime] new_tz operation successful', module
            
    return None, None

                
                    
        
        
        
    
