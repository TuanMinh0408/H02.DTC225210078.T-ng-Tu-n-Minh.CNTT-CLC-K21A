from docx import Document

def main():
    doc = Document('DTC225210078_Tăng Tuấn Minh_CNTTK21CLC.docx')
    with open('minh_all_text.txt', 'w', encoding='utf-8') as f:
        for i, p in enumerate(doc.paragraphs):
            if p.text.strip():
                f.write(f"[{i:04d}]: {p.text}\n")
                
if __name__ == '__main__':
    main()
