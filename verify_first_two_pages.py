from docx import Document
from docx.shared import Pt, Cm
import sys

def main():
    generated_path = "DTC225210078_Tăng Tuấn Minh_CNTTK21CLC.docx"
    doc = Document(generated_path)
    
    print("SECTIONS IN GENERATED DOC:")
    for i, section in enumerate(doc.sections):
        print(f"Section {i}:")
        print(f"  Page Width: {section.page_width.cm if section.page_width else 'None'} cm")
        print(f"  Page Height: {section.page_height.cm if section.page_height else 'None'} cm")
        print(f"  Top Margin: {section.top_margin.cm if section.top_margin else 'None'} cm")
        print(f"  Bottom Margin: {section.bottom_margin.cm if section.bottom_margin else 'None'} cm")
        print(f"  Left Margin: {section.left_margin.cm if section.left_margin else 'None'} cm")
        print(f"  Right Margin: {section.right_margin.cm if section.right_margin else 'None'} cm")
        
    print("\nFIRST 10 PARAGRAPHS STYLE & TEXT:")
    for i, p in enumerate(doc.paragraphs[:10]):
        print(f"[{i:02d}] Style: {p.style.name:<25} | Text: {p.text[:60]}")
        
    print("\nSTYLES IN GENERATED DOC:")
    for style_name in ['Outline Normal', 'Outline List Paragraph', 'Normal', 'List Paragraph']:
        if style_name in doc.styles:
            style = doc.styles[style_name]
            font = style.font
            pf = style.paragraph_format
            print(f"Style: {style_name}")
            print(f"  Font Name: {font.name}")
            print(f"  Font Size: {font.size.pt if font.size else 'None'} pt")
            print(f"  Line Spacing: {pf.line_spacing}")
            print(f"  Space After: {pf.space_after.pt if pf.space_after else 'None'} pt")
            print(f"  Space Before: {pf.space_before.pt if pf.space_before else 'None'} pt")

if __name__ == '__main__':
    main()
