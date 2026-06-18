import json, re
from html.parser import HTMLParser
import html as html_lib

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.in_style = False
    def handle_starttag(self, tag, attrs):
        if tag == 'style':
            self.in_style = True
    def handle_endtag(self, tag):
        if tag == 'style':
            self.in_style = False
    def handle_data(self, data):
        if not self.in_style:
            stripped = data.strip()
            if stripped:
                self.text.append(stripped)
    def get_text(self):
        return ' | '.join(self.text)

def extract_text(html):
    parser = TextExtractor()
    parser.feed(html)
    return parser.get_text()

def parse_receipt(html, msg_num):
    print(f"\n{'='*60}")
    print(f"MESSAGE {msg_num}")
    print(f"{'='*60}")

    # Extract plain text for easier reading
    text = extract_text(html)

    # RA number patterns
    ra_patterns = [
        r'(?:Rental\s+Agreement|Agreement\s+Number|RA\s*#?)[:\s]*(\d+)',
        r'#(\d{8,12})',
    ]
    for pat in ra_patterns:
        matches = re.findall(pat, text, re.IGNORECASE)
        if matches:
            print(f"RA Number (text): {matches}")
            break

    # In HTML directly
    ra_html = re.findall(r'(?:Rental Agreement|Agreement)[^<]{0,30}<[^>]+>(\d+)', html, re.IGNORECASE)
    if ra_html:
        print(f"RA Number (html): {ra_html}")

    # Dollar amounts in order
    dollar_vals = re.findall(r'\$\s*([\d,]+\.[\d]{2})', html)
    print(f"Dollar amounts: {dollar_vals}")

    # Look for labeled amounts - find label+value pairs
    # Pattern: label text followed by $ amount
    label_patterns = [
        (r'Total[:\s]*\$?\s*([\d,]+\.[\d]{2})', 'Total'),
        (r'Base\s+Rate[:\s]*\$?\s*([\d,]+\.[\d]{2})', 'Base Rate'),
        (r'Taxable\s+Products?[:\s]*\$?\s*([\d,]+\.[\d]{2})', 'Taxable Products'),
        (r'Non-?Taxable\s+Products?[:\s]*\$?\s*([\d,]+\.[\d]{2})', 'Non-Taxable Products'),
        (r'Rental\s+Sales\s+Tax[:\s]*\$?\s*([\d,]+\.[\d]{2})', 'Rental Sales Tax'),
        (r'Net\s+Charges?[:\s]*\$?\s*([\d,]+\.[\d]{2})', 'Net Charges'),
        (r'Surcharges?[:\s]*\$?\s*([\d,]+\.[\d]{2})', 'Surcharges'),
        (r'Fees?[:\s]*\$?\s*([\d,]+\.[\d]{2})', 'Fees'),
    ]

    for pat, label in label_patterns:
        matches = re.findall(pat, text, re.IGNORECASE)
        if matches:
            print(f"  {label}: {matches}")

    # Show a window of text around key financial section
    # Find the Summary section
    summary_idx = text.find('Summary')
    if summary_idx == -1:
        summary_idx = text.find('Total')
    if summary_idx != -1:
        print(f"\nText around financial summary (pos {summary_idx}):")
        print(text[max(0, summary_idx-200):summary_idx+800])

    # Show full text for short messages
    if len(text) < 3000:
        print(f"\nFull text:")
        print(text[:3000])


files = [
    r'C:\Users\houtx\.claude\projects\c--Users-houtx-Documents-TWC-Appeal-2026\31bae6d2-e397-4181-895f-9f39fbaaeab2\tool-results\mcp-claude_ai_Gmail-get_thread-1781225814199.txt',
    r'C:\Users\houtx\.claude\projects\c--Users-houtx-Documents-TWC-Appeal-2026\31bae6d2-e397-4181-895f-9f39fbaaeab2\tool-results\mcp-claude_ai_Gmail-get_thread-1781228490927.txt',
]

target_amounts = {'94.22', '117.72'}
found_messages = []

for filepath in files:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        msgs = data.get('messages', [])
        print(f"\nFILE: {filepath}")
        print(f"  {len(msgs)} messages")

        for i, m in enumerate(msgs):
            html = m.get('htmlBody', '') or ''
            for amt in target_amounts:
                if amt in html:
                    print(f"  -> Message {i+1} contains ${amt}")
                    found_messages.append((filepath, i+1, m, amt))

    except FileNotFoundError:
        print(f"File not found: {filepath}")

print(f"\n\nFound {len(found_messages)} messages with target amounts")
for filepath, msg_num, m, amt in found_messages:
    print(f"\nFile: {filepath.split(chr(92))[-1]}, Msg #{msg_num}, Amount: ${amt}")
    html = m.get('htmlBody', '')
    parse_receipt(html, f"{msg_num} (${amt})")
