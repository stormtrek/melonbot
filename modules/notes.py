import json
import re

try:
    with open('notes.json', 'x') as fd:
        fd.write('{}')
except FileExistsError:
    pass

def parse_add_note(msg, user):
    m = re.search('^\s+(.*)', msg)
    if not m:
        return 'Please enter a note'
    
    note = m.group(1).strip()
    if note:
        return add_note(note, user)

def add_note(note, user):
    with open('notes.json', 'r+') as fd:
        notes = json.load(fd)
        notes[user] = notes.get(user, [])
        notes[user].append(note)
        
        fd.seek(0)
        json.dump(notes, fd)
        fd.truncate()
    return 'Note added'

def view_notes(user):
    with open('notes.json') as fd:
        notes = json.load(fd)

        user_notes = notes.get(user, [])
        if not user_notes:
            return 'You do not have any notes'
        else:
            note_list = []
            for idx, val in enumerate(user_notes):
                note_list.append('\x02[{0}]\x02 {1}'.format(idx, val))
            return ' '.join(note_list)

def delete_note(note_index, user):
    if not note_index:
        return 'Please enter the index number you would like to delete'
    if not re.match('^\d+$', note_index):
        return 'Please enter a valid index number'
    
    with open('notes.json', 'r+') as fd:
        notes = json.load(fd)

        deleted_note_text = ''
        
        try:
            deleted_note_text = notes[user][int(note_index)]
            del notes[user][int(note_index)]
        except:
            return 'That index value does not exist'

        fd.seek(0)
        json.dump(notes, fd)
        fd.truncate()
    return 'Note {0} deleted: "{1}"'.format(note_index, deleted_note_text)


        
