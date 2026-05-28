from docx import Document

def main():
    doc = Document("DTC225210134_Nguyễn Thanh Tuân_CNTTK21CLC.docx")
    for idx, p in enumerate(doc.paragraphs):
        if "CHƯƠNG" in p.text.upper():
            print(f"Paragraph [{idx}]: text={repr(p.text)} | style={p.style.name}")

if __name__ == '__main__':
    main()
