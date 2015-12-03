"""
Convert a full-English name into dot-joined lowercase, removing some symbols.

This is *not* full-featured -- it will not detect and convert episode details,
    nor correctly split camelCase -> camel.case (among others)
"""
from retorrentlib.restring import endot

def _replace_chars(s, chars, replace_with):
    if not chars:
        return s
    s = s.replace(chars.pop(), replace_with)
    return _replace_chars(s, chars, replace_with)

def replace_chars(s, chars, replace_with):
    charset = set([ c for c in chars if not c == '' ])
    return _replace_chars(s, charset, replace_with)

removables = ["'", '"', '?']
def to_storage_name(english_name):
    a = replace_chars(english_name, removables, '')
    b = endot(a)
    c = b.lower()
    return c
