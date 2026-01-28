
import re

text = "bonjour voici mon cin:19874503 et mon tel 22334455"
text_lower = text.lower()

patterns = [
    r"(?:cin|nid|carte|identit[é|e])\D{0,10}?(\d{8})\b",
]

print(f"Testing text: '{text}'")
for p in patterns:
    m = re.search(p, text_lower)
    if m:
        print(f"MATCH: {m.group(1)} using pattern {p}")
    else:
        print(f"NO MATCH using pattern {p}")
