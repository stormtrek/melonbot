def decode(bytes):
    try:
        text = bytes.decode('UTF-8')
    except UnicodeDecodeError:
        try:
            text = bytes.decode('ISO-8859-1')
        except UnicodeDecodeError:
            text = bytes.decode('CP1252')
    return text


