from docx import Document

def main():
    doc = Document('DTC225210134_Nguyễn Thanh Tuân_CNTTK21CLC.docx')
    with open('first_100_tuan.txt', 'w', encoding='utf-8') as f:
        f.write(f"TOTAL PARAGRAPHS: {len(doc.paragraphs)}\n")
        f.write(f"TOTAL TABLES: {len(doc.tables)}\n")
        f.write(f"TOTAL SECTIONS: {len(doc.sections)}\n\n")
        
        for i, p in enumerate(doc.paragraphs[:120]):
            f.write(f"Paragraph [{i:02d}]:\n")
            f.write(f"  Style: {p.style.name}\n")
            f.write(f"  Text: {repr(p.text)}\n")
            f.write(f"  Runs:\n")
            for j, r in enumerate(p.runs):
                f.write(f"    Run [{j:02d}]: {repr(r.text)}\n")
            f.write("-" * 40 + "\n")

if __name__ == '__main__':
    main()
