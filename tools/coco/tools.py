from urllib.request import urlopen
import re

doc = {0: 65, 1: 66, 2: 67, 3: 68, 4: 69, 5: 70, 6: 71, 7: 72, 8: 73, 9: 74, 10: 75, 11: 76, 12: 77, 13: 78, 14: 79,
       15: 80, 16: 81, 17: 82, 18: 83, 19: 84, 20: 101, 21: 102, 22: 103, 23: 104, 24: 105, 25: 106, 26: 107,
       27: 108, 28: 109, 29: 110, 30: 85, 31: 86, 32: 87, 33: 88, 34: 89, 35: 90, 36: 97, 37: 98, 38: 99, 39: 100,
       40: 111, 41: 112, 42: 113, 43: 114, 44: 115, 45: 116, 46: 117, 47: 118, 48: 119, 49: 120, 50: 121, 51: 122,
       52: 48, 53: 49, 54: 50, 55: 51, 56: 52, 57: 53, 58: 54, 59: 55, 60: 56, 61: 57, 62: 43, 63: 47, 64: 61}


def coco_cipher(str: str, key: str):
    """Implementation of coco's weird 'enxo' cipher. key has to be the user's password,
    retrieved from a previous request"""

    def none_int(var):
        return var if var is not None else 0

    def safe_get_charcode(s: str, idx: int):
        try:
            return ord(s[idx])
        except IndexError:
            return None

    output, chr1, chr2, chr3 = "", 0, 0, 0
    enc, revo = {}, {}
    for j in range(65):
        revo[doc[j]] = j
    result = ""
    for i, char_n in enumerate(str):
        result += chr(ord(key[i % len(key)]) ^ ord(char_n))
    i = 0

    while i < len(str):
        chr1 = safe_get_charcode(result, i)
        i += 1
        chr2 = safe_get_charcode(result, i)
        i += 1
        chr3 = safe_get_charcode(result, i)
        i += 1

        enc[0] = none_int(chr1) >> 2
        enc[1] = ((none_int(chr1) & 3) << 4) | (none_int(chr2) >> 4)
        enc[2] = ((none_int(chr2) & 15) << 2) | (none_int(chr3) >> 6)
        enc[3] = none_int(chr3) & 63
        if chr2 is None:
            enc[2] = 64
            enc[3] = 64
        elif chr3 is None:
            enc[3] = 64

        for j in range(4):
            output += chr(doc[enc[j]])
    return output


def get_city_id(postal_code: str):
    response = str(urlopen("http://www.coco.fr/cocoland/%s.js" % postal_code).read(), 'utf-8')
    first_city_code = re.search(r'[0-9]+', response)
    if first_city_code:
        return first_city_code.group()
    elif 'ERROR' in response:
        raise ValueError('Invalid postal code')
    else:
        RuntimeError('Unexpected output')


smilies = [":)", ":(", ";)", ":d", ":-o", ":s", ":$", "*-)", "-)", "^o)", ":p", "(l)", "(v)", ":'(", "(h)", "(f)",
           ":@", "(y)", "(n)", "(k)", "gr$", "(a)", "(6)", "(yn)", "+o(", "na$", "oh$", "tr$", "(e)", "sh$", "fu$",
           "nw$", "ba$", "ao$", "db$", "si$", "oo$", "co$", "bi$", "cc$", "ye$", "mo$", "aa$", "ci$", "uu$", "ff$",
           "zz$", "gt$", "ah$", "mm$", "?$", "xx$"]

special_chars = {" ": "~", "!": "!", "\"": "*8", "$": "*7", "%": "*g", "'": "*8", "(": "(", ")": ")", "*": "*s", "=": "*h",
                 "?": "=", "@": "*m", "^": "*l", "_": "*0", "€": "*d", "à": "*a", "â": "*k", "ç": "*c", "è": "*e",
                 "é": "*r", "ê": "*b", "î": "*i", "ï": "*j", "ô": "*o", "ù": "*f", "û": "*u"}


def encode_msg(msg : str):
    """Encoding the message to coco's weird url-compatible format"""
    for i in range(len(smilies)):
        msg = msg.replace(smilies[i], ';' + str(i).zfill(2))

    for char, replacement in special_chars.items():
        msg = msg.replace(char, replacement)

    return msg

def decode_msg(msg: str):
    pass