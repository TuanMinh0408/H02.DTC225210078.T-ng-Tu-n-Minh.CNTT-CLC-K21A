from docx import Document

def inspect():
    doc = Document("DTC225210134_Nguyễn Thanh Tuân_CNTTK21CLC.docx")
    print(f"Total paragraphs: {len(doc.paragraphs)}")
    
    with open("tuan_paragraphs_50_150.txt", "w", encoding="utf-8") as f:
        for i in range(45, 155):
            if i < len(doc.paragraphs):
                p = doc.paragraphs[i]
                style_name = p.style.name if p.style else "None"
                f.write(f"[{i:03d}] Style: {style_name:<20} | Text: {repr(p.text)}\n")
                
    print("Done! Written to tuan_paragraphs_50_150.txt")

if __name__ == '__main__':
    inspect()
