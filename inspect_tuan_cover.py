from docx import Document
from docx.shared import Pt, Cm

def main():
    doc = Document('DTC225210134_Nguyễn Thanh Tuân_CNTTK21CLC.docx')
    print("TOTAL PARAGRAPHS:", len(doc.paragraphs))
    print("TOTAL TABLES:", len(doc.tables))
    print("TOTAL SECTIONS:", len(doc.sections))
    
    # Print the text and formatting of the first 50 paragraphs
    print("\nFIRST 50 PARAGRAPHS DETAILS:")
    for i, p in enumerate(doc.paragraphs[:60]):
        alignment = p.alignment if p.alignment else "None"
        space_after = p.paragraph_format.space_after.pt if p.paragraph_format.space_after else "None"
        line_spacing = p.paragraph_format.line_spacing if p.paragraph_format.line_spacing else "None"
        runs = p.runs
        font_info = ""
        if runs:
            r = runs[0]
            font_info = f"Font: {r.font.name}, Size: {r.font.size.pt if r.font.size else 'None'} pt, Bold: {r.bold}, Italic: {r.italic}"
        print(f"[{i:02d}] Style: {p.style.name:<15} | Align: {alignment:<10} | SA: {space_after:<5} | LS: {line_spacing:<5} | {font_info:<60} | Text: {p.text.strip()}")

    print("\nTABLES IN TUAN'S DOC:")
    for i, table in enumerate(doc.tables):
        rows = len(table.rows)
        cols = len(table.columns)
        print(f"Table {i+1}: {rows}x{cols}")
        if rows > 0:
            cells = [cell.text.strip().replace('\n', ' ')[:30] for cell in table.rows[0].cells]
            print(f"   Row 0: {' | '.join(cells)}")

if __name__ == '__main__':
    main()
