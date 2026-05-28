from docx import Document
import sys

def extract_headings(file_path):
    try:
        doc = Document(file_path)
        headings = []
        for p in doc.paragraphs:
            if p.style.name.startswith('Heading'):
                headings.append(f"{p.style.name}: {p.text}")
        
        with open('extracted_headings.txt', 'w', encoding='utf-8') as f:
            for h in headings:
                f.write(h + '\n')
        print(f"Extracted {len(headings)} headings.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    extract_headings('DTC225210134_Nguyễn Thanh Tuân_CNTTK21CLC.docx')
