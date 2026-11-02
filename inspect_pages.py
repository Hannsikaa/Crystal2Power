import fitz

doc = fitz.open('ANRF_IRG_Technical_Proposal.pdf')
for p in range(7, 13):
    print(f"=== PAGE {p+1} ===")
    lines = [l.strip() for l in doc[p].get_text().split('\n') if l.strip()]
    for line in lines[:8]:
        print("  TOP:", line[:70].encode('ascii', errors='replace').decode('ascii'))
    print("  ...")
    for line in lines[-5:]:
        print("  BOT:", line[:70].encode('ascii', errors='replace').decode('ascii'))
