from urllib.request import Request, urlopen
from decode import decode
from json import loads
from datetime import datetime
import re

data = None
last_called = None
last_conversion = None

def get_price(msg):
    global data, last_called, last_conversion
    
    amount = 1
    crypto = 'BTC'
    convert = 'USD'
    price_string = 'price_' + convert.lower()
    
    m = re.search('^\s+(([\d\.]+)\s+)?([\d]*[a-zA-Z]+[\d]*?|"[\d]+")\s*([\d]*[a-zA-Z]+[\d]*|"[\d]+")?\s*$', msg)
    if m:
        if m.group(1):
            amount = m.group(2)
            try:
                amount = float(amount)
                if (amount).is_integer():
                    amount = int(amount)
            except Exception:
                return 'not a valid amount'
        crypto = m.group(3).upper().replace('"', '' )
        if m.group(4):
            convert = m.group(4).upper().replace('"', '' )
        price_string = 'price_' + convert.lower()
    elif not msg.strip():
        pass
    else:
        m = re.search('^\s+([\d\.]+)\s*$', msg)
        if m:
            amount = m.group(1)
            try:
                amount = float(amount)
                if (amount).is_integer():
                    amount = int(amount)
            except Exception:
                return 'Not a valid amount'
        else:
            return 'Incorrect syntax'
    try:
        u = 'https://api.coinmarketcap.com/v1/ticker/?limit=1000'
        if convert != 'USD':
            u += '&convert=' + convert
        if not data:
            data = loads(decode(urlopen(u).read()))
            last_called = datetime.now()
            last_conversion = convert
        elif (datetime.now() - last_called).total_seconds() >= 120:
            data = loads(decode(urlopen(u).read()))
            last_called = datetime.now()
        elif last_conversion != convert:
            data = loads(decode(urlopen(u).read()))
            last_called = datetime.now()
            last_conversion = convert
    except Exception as e:
        print(e)
        return 'Could not retrieve coin price data at this time'
    for item in data:
        if item['symbol'] == crypto:
            try:
                if amount != 1:
                    price = '{:.10f}'.format(float(item[price_string]) * amount).rstrip('0').rstrip('.')
                else:
                    price = item[price_string]
            except Exception as e:
                print(e)
                return 'That currency conversion is not supported'
            amount = '{:.10f}'.format(amount).rstrip('0').rstrip('.')
            if item['percent_change_24h']:
                if float(item['percent_change_24h']) > 0:
                    percent_change = '+' + item['percent_change_24h']
                else:
                    percent_change = item['percent_change_24h']
            else:
                percent_change = 'N/A'
            return '{0} {1} = {2} {3} [{4}%] (rank: {5})'.format(amount, item['name'], price, convert, percent_change, item['rank'])
    return crypto +  ' is not in the top 1000 cryptos by market cap'
                 
    
