from docx import Document
from docx.oxml.ns import qn

def inspect():
    doc = Document("DTC225210134_Nguyễn Thanh Tuân_CNTTK21CLC.docx")
    print(f"Total sections: {len(doc.sections)}")
    for idx, s in enumerate(doc.sections):
        print(f"\n=== Section {idx} ===")
        print(f"  Page margins: Left={s.left_margin.cm:.2f}cm, Right={s.right_margin.cm:.2f}cm, Top={s.top_margin.cm:.2f}cm, Bottom={s.bottom_margin.cm:.2f}cm")
        
        sectPr = s._sectPr
        pgNumType = sectPr.find(qn('w:pgNumType'))
        if pgNumType is not None:
            fmt = pgNumType.get(qn('w:fmt'))
            start = pgNumType.get(qn('w:start'))
            print(f"  Page Numbering: fmt={fmt}, start={start}")
        else:
            print("  Page Numbering: Default")
            
        print(f"  Footer is linked to previous: {s.footer.is_linked_to_previous}")
        paras = [p.text.strip() for p in s.footer.paragraphs if p.text.strip()]
        print(f"  Footer paragraphs: {paras}")
        
if __name__ == '__main__':
    inspect()
