import fitz

doc = fitz.open('ANRF_IRG_Technical_Proposal.pdf')

for i, page in enumerate(doc):
    text = page.get_text()
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    headings = [l for l in lines if l.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.', '11.', '12.', '13.', '14.', '15.', 'Table '))]
    print(f"=== PAGE {i+1} ===")
    if headings:
        for h in headings:
            print("  HEADING:", h)
    else:
        print("  (body text continuation)")
