import json, re, sys

# Try the toulu file first, then fallback to mcp file
files = [
    r'C:\Users\houtx\.claude\projects\c--Users-houtx-Documents-TWC-Appeal-2026\31bae6d2-e397-4181-895f-9f39fbaaeab2\tool-results\toulu_01YAPq4HPvf3Q83LEiRV3tvZ.txt',
    r'C:\Users\houtx\.claude\projects\c--Users-houtx-Documents-TWC-Appeal-2026\31bae6d2-e397-4181-895f-9f39fbaaeab2\tool-results\mcp-claude_ai_Gmail-get_thread-1781225814199.txt',
]

for filepath in files:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            raw = f.read()
        print(f"\n=== FILE: {filepath} ===")
        print(f"File size: {len(raw)} chars")

        # Try to parse as JSON
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"JSON error: {e}")
            print(f"First 500 chars: {raw[:500]}")
            continue

        # Check top-level structure
        print(f"Top-level keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")

        if isinstance(data, dict) and 'messages' in data:
            msgs = data['messages']
        elif isinstance(data, list):
            msgs = data
        else:
            # Maybe it's a single message or different structure
            print(f"Unexpected structure, dumping keys: {list(data.keys())[:20]}")
            # Try to find messages in nested structure
            if isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, list) and len(v) > 0:
                        print(f"  Key '{k}' has list of {len(v)} items")
            continue

        print(f"Total messages: {len(msgs)}")

        for i, m in enumerate(msgs):
            print(f"\n--- Message {i+1} ---")
            print(f"  date: {m.get('date')}")
            print(f"  subject: {m.get('subject')}")
            print(f"  from: {m.get('from')}")

            html = m.get('htmlBody', '') or m.get('body', '') or ''
            text = m.get('textBody', '') or m.get('snippet', '') or ''

            print(f"  HTML length: {len(html)}, Text length: {len(text)}")

            # Search for rental agreement number
            for src, name in [(html, 'HTML'), (text, 'TEXT')]:
                if not src:
                    continue
                # Multiple patterns for RA number
                ra_patterns = [
                    r'Rental Agreement[^<]*<strong>(\d+)</strong>',
                    r'Agreement\s+#?\s*:?\s*(\d{8,12})',
                    r'RA\s*#?\s*:?\s*(\d{8,12})',
                    r'Rental\s+Agreement\s+Number[^0-9]*(\d+)',
                    r'agreement[^0-9]*(\d{8,12})',
                ]
                for pat in ra_patterns:
                    ra = re.findall(pat, src, re.IGNORECASE)
                    if ra:
                        print(f"  RA ({name}, pat={pat[:40]}): {ra}")
                        break

                # Search for dollar amounts
                dollar_vals = re.findall(r'\$\s*([\d,]+\.[\d]{2})', src)
                if dollar_vals:
                    print(f"  Dollar amounts ({name}): {dollar_vals[:15]}")

                # Look for the specific amounts
                if '94.22' in src or '94,22' in src:
                    idx = src.find('94.22') if '94.22' in src else src.find('94,22')
                    print(f"  Found 94.22 in {name} at pos {idx}: ...{src[max(0,idx-100):idx+100]}...")
                if '117.72' in src or '117,72' in src:
                    idx = src.find('117.72') if '117.72' in src else src.find('117,72')
                    print(f"  Found 117.72 in {name} at pos {idx}: ...{src[max(0,idx-100):idx+100]}...")

    except FileNotFoundError as e:
        print(f"File not found: {filepath}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
