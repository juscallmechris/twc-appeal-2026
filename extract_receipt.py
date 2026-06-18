import json, re

with open(
    r'C:\Users\houtx\.claude\projects\c--Users-houtx-Documents-TWC-Appeal-2026'
    r'\31bae6d2-e397-4181-895f-9f39fbaaeab2\tool-results\toolu_01FUWr4fVgxN1z4KeKDxLaNx.txt',
    'r', encoding='utf-8'
) as f:
    data = json.load(f)

row_labels = ['Base Rate', 'Taxable Products/Services*', 'Rental Sales Tax', 'Net Charges']

for i, m in enumerate(data['messages']):
    html = m.get('htmlBody', '')
    print(f"MSG {i+1}")
    print(f"  date   : {m.get('date')}")
    print(f"  id     : {m.get('id')}")
    print(f"  subject: {m.get('subject','')}")

    # Rental Agreement
    ra = re.findall(r'Rental Agreement\s*<strong>(\d+)</strong>', html)
    print(f"  Rental Agreement #: {ra[0] if ra else 'NOT FOUND'}")

    # Total Charges - large 20px font (may be rendered differently)
    # Find amounts in the values column after Net Charges label
    idx = html.find('Net Charges')
    segment = html[idx:idx+2000]
    amounts = re.findall(r'<strong>[^\d]*([\d,.]+)</strong>', segment)
    # First 4 strong numbers after Net Charges label = Base, TaxProd, SalesTax, Net
    field_names = ['Base Rate', 'Taxable Products/Services', 'Rental Sales Tax', 'Net Charges']
    for j, lbl in enumerate(field_names):
        val = amounts[j] if j < len(amounts) else 'NOT FOUND'
        print(f"  {lbl}: ${val}")

    # Total (the big number = same as Net Charges, but also check for 20px font)
    total_match = re.search(r'font-size:\s*20px[^>]*>([^<]+)<', html)
    if total_match:
        print(f"  Total (20px): {total_match.group(1).strip()}")
    else:
        # Net Charges IS the total
        print(f"  Total Charges: ${amounts[3] if len(amounts) > 3 else 'NOT FOUND'}")

    # Non-Taxable Products
    nontax_idx = html.find('Non-Taxable Products')
    if nontax_idx >= 0:
        print(f"  Non-Taxable Products/Services: PRESENT IN EMAIL")
    else:
        print(f"  Non-Taxable Products/Services: not listed")

    print()

# Are they the same rental agreement?
ids = [re.findall(r'Rental Agreement\s*<strong>(\d+)</strong>', m.get('htmlBody','')) for m in data['messages']]
print("=== DUPLICATE CHECK ===")
print(f"Msg 1 RA#: {ids[0]}")
print(f"Msg 2 RA#: {ids[1]}")
print(f"Same RA? {'YES - DUPLICATE RECEIPT' if ids[0] == ids[1] else 'NO - DIFFERENT RENTAL AGREEMENTS'}")
