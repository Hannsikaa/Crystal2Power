import fitz

doc = fitz.open('ANRF_IRG_Technical_Proposal.pdf')
print('Total pages:', len(doc))
total_words = 0
for i, page in enumerate(doc):
    text = page.get_text()
    words = len(text.split())
    total_words += words
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    first_line = lines[0] if lines else 'EMPTY'
    last_line = lines[-1] if lines else 'EMPTY'
    print(f'Page {i+1}: words={words}, lines={len(lines)}, first="{first_line[:50]}", last="{last_line[:50]}"')

print('Total words in PDF:', total_words)
