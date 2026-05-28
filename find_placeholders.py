import docx
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

def analyze_doc(txt_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    print("--- POTENTIAL MISSING IMAGES/FORMULAS/CHARTS ---")
    for line in lines:
        lower_line = line.lower()
        if re.search(r'\[\d+\] (hình|công thức|bảng|biểu đồ) ', lower_line):
            print(line.strip())
        elif "chèn" in lower_line or "[" in lower_line or "]" in lower_line:
            # exclude the line index like [15]
            clean_line = re.sub(r'^\[\d+\]\s*', '', lower_line)
            if "[" in clean_line or "]" in clean_line or "chèn" in clean_line or "công thức" in clean_line or "biểu đồ" in clean_line:
                if len(clean_line) < 100: # Usually placeholders are short
                    print("PLACEHOLDER SUSPECT:", line.strip())

if __name__ == "__main__":
    analyze_doc("dumped_doc.txt")
