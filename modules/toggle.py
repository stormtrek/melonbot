def toggle(msg, feature, channel, toggleList):
    match = re.search('\.toggle ([\w]+)\s*$', msg)
    if match:
        if feature in toggleList[channel]:
            if toggleList[channel][feature]:
                toggleList[channel][feature] = False
                return feature + ' turned off'
            else:
                toggleList[channel][feature] = True
                return feature + ' turned on'

