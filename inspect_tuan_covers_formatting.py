from docx import Document

def inspect():
    doc = Document("DTC225210134_Nguyễn Thanh Tuân_CNTTK21CLC.docx")
    print("INSIDE TUAN'S COVER FORMATTING (0-49):")
    with open("tuan_cover_formatting.txt", "w", encoding="utf-8") as f:
        for i in range(50):
            p = doc.paragraphs[i]
            align = p.alignment
            pf = p.paragraph_format
            ls = pf.line_spacing
            sa = pf.space_after
            sb = pf.space_before
            runs_info = []
            for r in p.runs:
                runs_info.append(f"Run(text={repr(r.text)}, font={r.font.name}, size={r.font.size.pt if r.font.size else None}, bold={r.bold}, italic={r.italic})")
            
            f.write(f"[{i:02d}] Text: {repr(p.text)}\n")
            f.write(f"     Align: {align}, LineSpacing: {ls}, SpaceAfter: {sa}, SpaceBefore: {sb}\n")
            f.write(f"     Runs: {runs_info}\n\n")

if __name__ == '__main__':
    inspect()
