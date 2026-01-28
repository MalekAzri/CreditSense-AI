import json
import base64

def extract_body(payload):
    parts = []
    if 'parts' in payload:
        for part in payload['parts']:
            parts.extend(extract_body(part))
    elif 'body' in payload and 'data' in payload['body']:
        try:
            data = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
            parts.append(data)
        except Exception as e:
            parts.append(f"Error decoding: {e}")
    return parts

with open("debug_gmail_full_payload.json", "r", encoding="utf-8") as f:
    data = json.load(f)

all_parts = extract_body(data['payload'])
with open("payload_extracted.txt", "w", encoding="utf-8") as f:
    for i, p in enumerate(all_parts):
        f.write(f"--- PART {i} ---\n")
        f.write(p)
        f.write("\n")

print(f"Extracted {len(all_parts)} parts to payload_extracted.txt")
