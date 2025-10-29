import re
from slugify import slugify as _slugify

def slugify(text):
    # простая slug-функция
    if not text:
        return ""
    s = _slugify(text)
    # ensure uniqueness handled at model layer
    return s