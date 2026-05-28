from docx import Document

def inspect():
    doc = Document("DTC225210134_Nguyễn Thanh Tuân_CNTTK21CLC.docx")
    for idx, s in enumerate(doc.sections):
        print(f"\n=== Section {idx} ===")
        print(f"  Footer is linked to previous: {s.footer.is_linked_to_previous}")
        for i, p in enumerate(s.footer.paragraphs):
            print(f"    Paragraph {i}: Text={repr(p.text)}")
            for r in p.runs:
                print(f"      Run Text={repr(r.text)}")
        
        # Check different_first_page_header_footer
        print(f"  Different first page: {s.different_first_page_header_footer}")

if __name__ == '__main__':
    inspect()
