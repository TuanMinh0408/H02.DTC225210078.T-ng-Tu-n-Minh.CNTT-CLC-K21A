from docx import Document

def main():
    try:
        doc = Document("DTC225210078_Tăng Tuấn Minh_CNTTK21CLC.docx")
        print("TOTAL PARAGRAPHS:", len(doc.paragraphs))
        print("TOTAL TABLES:", len(doc.tables))
        print("TOTAL SECTIONS:", len(doc.sections))
        
        print("\nFIRST 40 PARAGRAPHS OF GENERATED DOC:")
        for i, p in enumerate(doc.paragraphs[:60]):
            style_name = p.style.name if p.style else "None"
            print(f"[{i:02d}] Style: {style_name:<20} | Text: {repr(p.text)}")
            
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    main()
