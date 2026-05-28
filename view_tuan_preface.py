from docx import Document

def main():
    doc = Document("DTC225210134_Nguyễn Thanh Tuân_CNTTK21CLC.docx")
    with open("tuan_paragraphs_50_87.txt", "w", encoding="utf-8") as f:
        for idx in range(50, 88):
            f.write(f"[{idx}]: {doc.paragraphs[idx].text}\n")
    print("Done")

if __name__ == '__main__':
    main()
