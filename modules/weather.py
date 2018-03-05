from formatting import bold, ita, und
from collections import OrderedDict
from urllib.request import urlopen
from decode import decode
from json import load, loads
import argparse
import datetime
import re

parser = argparse.ArgumentParser()
parser.add_argument('--config', default='config.json', help='configuration file')
args = parser.parse_args()

with open(args.config) as fd:
    config = load(fd, object_pairs_hook=OrderedDict)
    
access_key = config['wunderground_key']

color_violet = '\x0313'
color_dark_violet = '\x0306'
color_dark_blue = '\x0302'
color_blue = '\x0312'
color_cyan = '\x0310'
color_light_cyan = '\x0311'
color_green = '\x0309'
color_yellow = '\x0308'
color_orange = '\x0307'
color_red = '\x0304'
color_end = '\x03'
div = ' ➤ '

def getCond(msg):
    try:
        content = loads(decode(urlopen('http://api.wunderground.com/api/' + access_key + '/conditions/q/' + msg.strip().replace(' ', '%20') + '.json').read()))
    except Exception:
        return 'could not reach server'
    try:
        content = loads(decode(urlopen('http://api.wunderground.com/api/' + access_key + '/conditions/q/zmw:' + content['response']['results'][0]['zmw'] + '.json').read()))
    except Exception:
        pass
    try:
        color = temp_color(content['current_observation']['temp_f'])
        temp = color + str(content['current_observation']['temp_f']) + color_end + '° F (' + color + str(content['current_observation']['temp_c']) + color_end + '° C)'
        feels_like_temp = color + str(content['current_observation']['feelslike_f']) + color_end + '° F (' + color + str(content['current_observation']['feelslike_c']) + color_end + '° C)'
        return 'Current conditions for ' + und(ita(content['current_observation']['display_location']['full'])) + div + bold('Temperature') + ': ' + values(temp) + div + bold('Weather') + ': ' + values(content['current_observation']['weather']) + div + bold('Relative humidity') + ': ' + values(content['current_observation']['relative_humidity']) + div + bold('Wind') + ': ' + values(content['current_observation']['wind_string']) + div + bold('Feels like') + ': ' + values(feels_like_temp) + div + bold('Local time') + ': ' + values(content['current_observation']['local_time_rfc822'] + ' (' + content['current_observation']['local_tz_short'] + ')')
    except Exception:
        try:
            return content['response']['error']['description']
        except Exception:
            return 'could not reach server'

def temp_color(temp):
	if temp < -10:
		color = color_violet
	elif temp >= -10 and temp < 0:
		color = color_dark_violet
	elif temp >= 0 and temp < 10:
		color = color_dark_blue
	elif temp >= 10 and temp < 20:
		color = color_blue
	elif temp >= 20 and temp < 30:
		color = color_cyan
	elif temp >= 30 and temp < 40:
		color = color_light_cyan
	elif temp >= 40 and temp < 50:
		color = color_green
	elif temp >= 50 and temp < 60:
		color = color_yellow
	elif temp >= 60 and temp < 80:
		color = color_orange
	elif temp >= 30 and temp < 40:
		color = color_light_cyan
	elif temp >= 80:
		color = color_red
	return color

def values(text):
    return text
