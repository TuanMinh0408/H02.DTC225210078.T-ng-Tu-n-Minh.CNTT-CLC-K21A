from docx import Document
from docx.shared import Pt, Cm
import sys

def main():
    original_path = r"C:\Users\minhc\Downloads\Đồ án tốt nghiệp\H02.DTC225210078.Tăng Tuấn Minh.CNTTK21CLC.docx"
    doc = Document(original_path)
    
    print("SECTIONS:")
    for i, section in enumerate(doc.sections):
        print(f"Section {i}:")
        print(f"  Page Width: {section.page_width.cm if section.page_width else 'None'} cm")
        print(f"  Page Height: {section.page_height.cm if section.page_height else 'None'} cm")
        print(f"  Top Margin: {section.top_margin.cm if section.top_margin else 'None'} cm")
        print(f"  Bottom Margin: {section.bottom_margin.cm if section.bottom_margin else 'None'} cm")
        print(f"  Left Margin: {section.left_margin.cm if section.left_margin else 'None'} cm")
        print(f"  Right Margin: {section.right_margin.cm if section.right_margin else 'None'} cm")
        
    print("\nSTYLES IN ORIGINAL:")
    for style_name in ['Normal', 'List Paragraph', 'Heading 1', 'Heading 2', 'Heading 3']:
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
