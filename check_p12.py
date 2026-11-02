import fitz

doc = fitz.open('ANRF_IRG_Technical_Proposal.pdf')
p12 = doc[11] # 0-indexed Page 12
print("Page 12 text length:", len(p12.get_text()))
print("Page 12 text:\n", p12.get_text()[:400])

p13 = doc[12] # Page 13
print("Page 13 text:\n", p13.get_text()[:300])
