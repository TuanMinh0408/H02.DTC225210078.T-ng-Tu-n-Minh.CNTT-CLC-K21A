from docx import Document

def main():
    doc = Document('DTC225210078_Tăng Tuấn Minh_CNTTK21CLC.docx')
    print("TOTAL PARAGRAPHS:", len(doc.paragraphs))
    print("TOTAL TABLES:", len(doc.tables))
    
    with open('minh_first_100.txt', 'w', encoding='utf-8') as f:
        for i, p in enumerate(doc.paragraphs[:150]):
            f.write(f"[{i:03d}] text: {repr(p.text)}\n")
            
if __name__ == '__main__':
    main()
