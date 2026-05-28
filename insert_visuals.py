"""
Script chèn hình ảnh, bảng biểu, công thức vào báo cáo đồ án
và hoàn thành DANH MỤC HÌNH ẢNH + DANH MỤC BẢNG BIỂU.
"""
import os, sys, copy
sys.stdout.reconfigure(encoding='utf-8')

from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import OxmlElement, parse_xml
from docx.table import Table

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ============================================================
# PART 1: Generate chart images with matplotlib
# ============================================================
ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')
os.makedirs(ASSETS_DIR, exist_ok=True)

plt.rcParams['font.family'] = 'DejaVu Sans'

def generate_f1_chart():
    """Biểu đồ cột so sánh F1-Score của 5 mô hình"""
    path = os.path.join(ASSETS_DIR, 'f1_comparison.png')
    models = ['Bi-GRU', 'Bi-LSTM\n+Attention', 'CNN-LSTM', 'TCN', 'Transformer\nEncoder']
    f1 = [92.26, 91.93, 91.77, 89.51, 87.99]
    colors = ['#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe']

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(models, f1, color=colors, edgecolor='#1e3a5f', linewidth=1.2, width=0.6)
    for bar, v in zip(bars, f1):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                f'{v}%', ha='center', va='bottom', fontweight='bold', fontsize=11)
    ax.set_ylabel('F1-Score (%)', fontsize=12, fontweight='bold')
    ax.set_ylim(85, 95)
    ax.set_title('So sánh F1-Score của các mô hình phân loại', fontsize=14, fontweight='bold', pad=15)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f'  ✓ Generated: {path}')
    return path

def generate_yolo_chart():
    """Biểu đồ so sánh YOLOv8 vs YOLOv11"""
    path = os.path.join(ASSETS_DIR, 'yolo_comparison.png')
    labels = ['Thời gian suy luận\n(ms/frame)', 'Tỷ lệ phát hiện\n(%)', 'Độ tin cậy\n(×100)']
    v8 = [15.22, 73.43, 76.8]
    v11 = [26.51, 71.18, 74.7]

    x = np.arange(len(labels))
    width = 0.3
    fig, ax = plt.subplots(figsize=(8, 5))
    bars1 = ax.bar(x - width/2, v8, width, label='YOLOv8n-Pose', color='#2563eb', edgecolor='#1e3a5f')
    bars2 = ax.bar(x + width/2, v11, width, label='YOLOv11-Pose', color='#f59e0b', edgecolor='#92400e')
    for bars in [bars1, bars2]:
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f'{bar.get_height():.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_title('So sánh hiệu suất YOLOv8n-Pose và YOLOv11-Pose', fontsize=14, fontweight='bold', pad=15)
    ax.legend(fontsize=11)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f'  ✓ Generated: {path}')
    return path

# ============================================================
# PART 2: Helper functions for docx manipulation
# ============================================================

def insert_paragraph_after(paragraph, text='', bold=False, italic=False, font_size=13, font_name='Times New Roman', alignment=None, space_before=0, space_after=0):
    """Insert a new paragraph after the given paragraph element."""
    new_p = OxmlElement('w:p')
    paragraph._element.addnext(new_p)
    # We need to create a proper Paragraph object
    from docx.text.paragraph import Paragraph
    new_para = Paragraph(new_p, paragraph._parent)
    if text:
        run = new_para.add_run(text)
        run.bold = bold
        run.italic = italic
        run.font.size = Pt(font_size)
        run.font.name = font_name
        # Set East Asian font
        r = run._element
        rPr = r.find(qn('w:rPr'))
        if rPr is None:
            rPr = OxmlElement('w:rPr')
            r.insert(0, rPr)
        rFonts = rPr.find(qn('w:rFonts'))
        if rFonts is None:
            rFonts = OxmlElement('w:rFonts')
            rPr.append(rFonts)
        rFonts.set(qn('w:eastAsia'), font_name)
    if alignment is not None:
        new_para.alignment = alignment
    pPr = new_p.find(qn('w:pPr'))
    if pPr is None:
        pPr = OxmlElement('w:pPr')
        new_p.insert(0, pPr)
    if space_before > 0 or space_after > 0:
        spacing = OxmlElement('w:spacing')
        if space_before > 0:
            spacing.set(qn('w:before'), str(space_before))
        if space_after > 0:
            spacing.set(qn('w:after'), str(space_after))
        pPr.append(spacing)
    return new_para

def insert_image_paragraph(paragraph, image_path, width_inches=5.0):
    """Insert an image in a new paragraph after the given paragraph."""
    new_p = OxmlElement('w:p')
    paragraph._element.addnext(new_p)
    from docx.text.paragraph import Paragraph
    new_para = Paragraph(new_p, paragraph._parent)
    new_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = new_para.add_run()
    run.add_picture(image_path, width=Inches(width_inches))
    return new_para

def insert_caption(paragraph, figure_id, caption_text, is_table=False):
    """Insert a caption (e.g., 'Hình 1.1. Caption text') after the given paragraph."""
    prefix = "Bảng" if is_table else "Hình"
    full_text = f'{prefix} {figure_id}. {caption_text}'
    cap = insert_paragraph_after(
        paragraph, full_text,
        bold=False, italic=True, font_size=12,
        alignment=WD_ALIGN_PARAGRAPH.CENTER,
        space_before=60, space_after=120
    )
    # Make the prefix+id bold
    # We need to clear and re-add with mixed formatting
    cap.clear()
    run1 = cap.add_run(f'{prefix} {figure_id}. ')
    run1.bold = True
    run1.italic = True
    run1.font.size = Pt(12)
    run1.font.name = 'Times New Roman'
    run2 = cap.add_run(caption_text)
    run2.bold = False
    run2.italic = True
    run2.font.size = Pt(12)
    run2.font.name = 'Times New Roman'
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    return cap

def insert_placeholder_image(paragraph, figure_id, caption_text):
    """Insert a placeholder box + caption for images to be added later."""
    # Insert caption first (will appear below), then placeholder (will appear above)
    cap = insert_caption(paragraph, figure_id, caption_text)
    # Insert placeholder box text above caption
    box = insert_paragraph_after(
        paragraph,
        f'[Chèn hình {figure_id} tại đây — {caption_text}]',
        bold=False, italic=True, font_size=12,
        alignment=WD_ALIGN_PARAGRAPH.CENTER,
        space_before=120, space_after=60
    )
    # Add border styling to make it look like a box
    pPr = box._element.find(qn('w:pPr'))
    if pPr is None:
        pPr = OxmlElement('w:pPr')
        box._element.insert(0, pPr)
    pBdr = OxmlElement('w:pBdr')
    for side in ['top', 'left', 'bottom', 'right']:
        border = OxmlElement(f'w:{side}')
        border.set(qn('w:val'), 'single')
        border.set(qn('w:sz'), '4')
        border.set(qn('w:space'), '4')
        border.set(qn('w:color'), '999999')
        pBdr.append(border)
    pPr.append(pBdr)
    # Set gray color for the text
    for run in box.runs:
        run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)
    return box

def insert_real_image(paragraph, figure_id, caption_text, image_path, width=5.0):
    """Insert a real image + caption."""
    cap = insert_caption(paragraph, figure_id, caption_text)
    img_para = insert_image_paragraph(paragraph, image_path, width)
    return img_para

def create_table_after(paragraph, headers, rows, doc):
    """Create a formatted table after a paragraph."""
    # Create table
    tbl = OxmlElement('w:tbl')
    paragraph._element.addnext(tbl)
    
    # Table properties
    tblPr = OxmlElement('w:tblPr')
    tblW = OxmlElement('w:tblW')
    tblW.set(qn('w:w'), '5000')
    tblW.set(qn('w:type'), 'pct')
    tblPr.append(tblW)
    # Center alignment
    jc = OxmlElement('w:jc')
    jc.set(qn('w:val'), 'center')
    tblPr.append(jc)
    # Borders
    tblBorders = OxmlElement('w:tblBorders')
    for border_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        border = OxmlElement(f'w:{border_name}')
        border.set(qn('w:val'), 'single')
        border.set(qn('w:sz'), '4')
        border.set(qn('w:space'), '0')
        border.set(qn('w:color'), '000000')
        tblBorders.append(border)
    tblPr.append(tblBorders)
    tbl.append(tblPr)
    
    # Grid
    tblGrid = OxmlElement('w:tblGrid')
    num_cols = len(headers)
    for _ in range(num_cols):
        gridCol = OxmlElement('w:gridCol')
        tblGrid.append(gridCol)
    tbl.append(tblGrid)
    
    def make_row(cells_data, is_header=False):
        tr = OxmlElement('w:tr')
        for cell_text in cells_data:
            tc = OxmlElement('w:tc')
            tcPr = OxmlElement('w:tcPr')
            if is_header:
                shading = OxmlElement('w:shd')
                shading.set(qn('w:fill'), '2563EB')
                shading.set(qn('w:val'), 'clear')
                tcPr.append(shading)
            tc.append(tcPr)
            p = OxmlElement('w:p')
            pPr = OxmlElement('w:pPr')
            jc = OxmlElement('w:jc')
            jc.set(qn('w:val'), 'center')
            pPr.append(jc)
            spacing = OxmlElement('w:spacing')
            spacing.set(qn('w:before'), '40')
            spacing.set(qn('w:after'), '40')
            pPr.append(spacing)
            p.append(pPr)
            r = OxmlElement('w:r')
            rPr = OxmlElement('w:rPr')
            sz = OxmlElement('w:sz')
            sz.set(qn('w:val'), '24')  # 12pt
            rPr.append(sz)
            szCs = OxmlElement('w:szCs')
            szCs.set(qn('w:val'), '24')
            rPr.append(szCs)
            rFonts = OxmlElement('w:rFonts')
            rFonts.set(qn('w:ascii'), 'Times New Roman')
            rFonts.set(qn('w:hAnsi'), 'Times New Roman')
            rPr.append(rFonts)
            if is_header:
                b = OxmlElement('w:b')
                rPr.append(b)
                color = OxmlElement('w:color')
                color.set(qn('w:val'), 'FFFFFF')
                rPr.append(color)
            r.append(rPr)
            t = OxmlElement('w:t')
            t.set(qn('xml:space'), 'preserve')
            t.text = str(cell_text)
            r.append(t)
            p.append(r)
            tc.append(p)
            tr.append(tc)
        return tr
    
    # Header row
    tbl.append(make_row(headers, is_header=True))
    # Data rows
    for row in rows:
        tbl.append(make_row(row))
    
    return tbl

def insert_table_with_caption(paragraph, table_id, caption_text, headers, rows, doc):
    """Insert a table with caption above it."""
    # Insert table first (will appear below), then caption above
    tbl = create_table_after(paragraph, headers, rows, doc)
    # Insert caption above table (after the original paragraph)
    cap = insert_caption(paragraph, table_id, caption_text, is_table=True)
    # Add spacing after table
    spacing_para = OxmlElement('w:p')
    tbl.addnext(spacing_para)
    return tbl

def insert_formula_block(paragraph, formulas):
    """Insert a block of formulas as centered, italic text."""
    prev = paragraph
    for formula_text in formulas:
        prev = insert_paragraph_after(
            prev, formula_text,
            bold=False, italic=True, font_size=13,
            alignment=WD_ALIGN_PARAGRAPH.CENTER,
            space_before=60, space_after=60
        )
    return prev

# ============================================================
# PART 3: Define all content to insert
# ============================================================

# Figures list: (paragraph_index, figure_id, caption, type, image_path_or_none)
# type: 'placeholder' or 'image'
FIGURES = [
    (78,  '1.1', 'So sánh quy trình học máy truyền thống và học sâu', 'placeholder', None),
    (79,  '1.2', 'Cấu trúc cơ bản của mạng nơ-ron nhân tạo nhiều tầng', 'placeholder', None),
    (85,  '1.3', 'Minh họa kỹ thuật Dropout chống hiện tượng quá khớp', 'placeholder', None),
    (95,  '1.4', 'Hai phương pháp ước lượng tư thế: Top-down và Bottom-up', 'placeholder', None),
    (101, '1.5', 'Cấu trúc tế bào LSTM (Long Short-Term Memory)', 'placeholder', None),
    (103, '1.6', 'Cấu trúc ma trận nhầm lẫn (Confusion Matrix)', 'placeholder', None),
    (119, '1.7', 'Kiến trúc tổng thể mạng YOLOv11-Pose', 'placeholder', None),
    (152, '2.1', 'Sơ đồ luồng kết hợp YOLO và trích xuất khung xương', 'placeholder', None),
    (155, '2.2', 'Sơ đồ kiến trúc phân lớp tổng thể của hệ thống', 'placeholder', None),
    (157, '2.3', 'Lưu đồ thuật toán quy trình phát hiện té ngã', 'placeholder', None),
    (230, '3.1', 'Giao diện Web Dashboard hệ thống giám sát', 'placeholder', None),
    (257, '3.2', 'Biểu đồ so sánh F1-Score của năm mô hình phân loại', 'image', 'f1_comparison.png'),
    (261, '3.3', 'Biểu đồ so sánh hiệu suất YOLOv8n-Pose và YOLOv11-Pose', 'image', 'yolo_comparison.png'),
]

# Tables list: (paragraph_index, table_id, caption, headers, rows)
TABLES = [
    (169, '3.1', 'Cấu hình phần cứng hệ thống',
     ['Thành phần', 'Thông số kỹ thuật'],
     [
         ['Vi xử lý (CPU)', 'Intel Core i5-11400H'],
         ['Card đồ họa (GPU)', 'NVIDIA GeForce RTX 3050 Laptop'],
         ['Bộ nhớ RAM', '16 GB DDR4'],
         ['Hệ điều hành', 'Windows'],
     ]),
    (173, '3.2', 'Phần mềm và thư viện chính sử dụng trong hệ thống',
     ['Phần mềm / Thư viện', 'Phiên bản', 'Chức năng'],
     [
         ['Python', '3.10+', 'Ngôn ngữ lập trình chính'],
         ['PyTorch', '2.4.0', 'Framework học sâu'],
         ['Ultralytics', '8.2.0', 'Triển khai YOLOv11-Pose'],
         ['OpenCV', '4.10.0', 'Xử lý ảnh và video'],
         ['Scikit-Learn', '1.5.1', 'Đánh giá mô hình'],
         ['FastAPI', '0.115.0', 'Xây dựng API Backend'],
         ['Matplotlib + Seaborn', '-', 'Trực quan hóa kết quả'],
         ['Pandas + NumPy', '-', 'Xử lý dữ liệu'],
     ]),
    (200, '3.3', 'Cấu hình siêu tham số huấn luyện mô hình',
     ['Siêu tham số', 'Giá trị'],
     [
         ['Hàm mất mát (Loss)', 'Binary Cross-Entropy (BCELoss)'],
         ['Bộ tối ưu hóa', 'AdamW'],
         ['Tốc độ học (Learning Rate)', '0.001'],
         ['Kích thước lô (Batch Size)', '64'],
         ['Số thế hệ tối đa (Max Epochs)', '100'],
         ['Tỷ lệ Dropout', '0.3'],
         ['Early Stopping Patience', '15 epochs'],
     ]),
    (253, '3.4', 'Bảng tổng hợp kết quả đánh giá năm mô hình phân loại chuỗi thời gian',
     ['Mô hình', 'Tham số', 'Thời gian (s)', 'Accuracy', 'Precision', 'Recall', 'F1-Score', 'AUC'],
     [
         ['Bi-GRU', '419.796', '585', '93,43%', '92,92%', '91,61%', '92,26%', '97,89%'],
         ['Bi-LSTM + Att.', '570.709', '995', '93,13%', '92,09%', '91,77%', '91,93%', '97,94%'],
         ['CNN-LSTM', '123.554', '378', '92,92%', '91,09%', '92,47%', '91,77%', '98,17%'],
         ['TCN', '198.402', '650', '90,85%', '88,52%', '90,53%', '89,51%', '97,01%'],
         ['Transformer', '72.130', '780', '89,64%', '87,13%', '88,87%', '87,99%', '96,12%'],
     ]),
    (261, '3.5', 'So sánh hiệu suất trích xuất khung xương giữa YOLOv8n-Pose và YOLOv11-Pose',
     ['Chỉ số', 'YOLOv8n-Pose', 'YOLOv11-Pose'],
     [
         ['Thời gian suy luận TB (ms/frame)', '15,22', '26,51'],
         ['Số frame phát hiện thành công', '293 / 399', '284 / 399'],
         ['Tỷ lệ phát hiện (%)', '73,43%', '71,18%'],
         ['Độ tin cậy TB (Confidence)', '0,768', '0,747'],
         ['Số sự kiện té ngã phát hiện', '1', '1'],
     ]),
]

# Formulas to insert after paragraph [105] (after the F1-Score discussion)
FORMULAS = [
    'Accuracy = (TP + TN) / (TP + TN + FP + FN)',
    'Precision = TP / (TP + FP)',
    'Recall = TP / (TP + FN)',
    'F1-Score = 2 × (Precision × Recall) / (Precision + Recall)',
]

# ============================================================
# PART 4: Populate DANH MỤC HÌNH ẢNH and DANH MỤC BẢNG BIỂU
# ============================================================

def populate_list_of_figures(doc, figures_meta):
    """Find DANH MỤC HÌNH ẢNH heading and insert list after it."""
    target_idx = 58  # paragraph index of DANH MỤC HÌNH ẢNH
    p = doc.paragraphs[target_idx]
    prev = p
    for fig_id, caption in figures_meta:
        entry_text = f'Hình {fig_id}. {caption}'
        prev = insert_paragraph_after(
            prev, entry_text,
            bold=False, italic=False, font_size=13,
            alignment=None,
            space_before=0, space_after=60
        )
    print(f'  ✓ Populated DANH MỤC HÌNH ẢNH with {len(figures_meta)} entries')

def populate_list_of_tables(doc, tables_meta):
    """Find DANH MỤC BẢNG BIỂU heading and insert list after it."""
    target_idx = 62  # paragraph index of DANH MỤC BẢNG BIỂU
    p = doc.paragraphs[target_idx]
    prev = p
    for tbl_id, caption in tables_meta:
        entry_text = f'Bảng {tbl_id}. {caption}'
        prev = insert_paragraph_after(
            prev, entry_text,
            bold=False, italic=False, font_size=13,
            alignment=None,
            space_before=0, space_after=60
        )
    print(f'  ✓ Populated DANH MỤC BẢNG BIỂU with {len(tables_meta)} entries')

# ============================================================
# PART 5: Main execution
# ============================================================

def main():
    print('=' * 60)
    print('CHÈN HÌNH ẢNH, BẢNG BIỂU VÀO BÁO CÁO ĐỒ ÁN')
    print('=' * 60)
    
    # Step 1: Generate chart images
    print('\n[1/4] Đang tạo biểu đồ...')
    f1_path = generate_f1_chart()
    yolo_path = generate_yolo_chart()
    
    # Step 2: Open document
    print('\n[2/4] Đang mở file báo cáo...')
    src = 'DTC225210078_Tăng Tuấn Minh_CNTTK21CLC.docx'
    doc = Document(src)
    total_paras = len(doc.paragraphs)
    print(f'  Tổng số paragraphs: {total_paras}')
    
    # Step 3: Insert all content (REVERSE ORDER to preserve indices)
    print('\n[3/4] Đang chèn hình ảnh và bảng biểu...')
    
    # Combine all insertions and sort by paragraph index (descending)
    # Each insertion: (para_idx, type, data)
    all_insertions = []
    
    for para_idx, fig_id, caption, fig_type, img_file in FIGURES:
        img_path = os.path.join(ASSETS_DIR, img_file) if img_file else None
        all_insertions.append((para_idx, 'figure', (fig_id, caption, fig_type, img_path)))
    
    for para_idx, tbl_id, caption, headers, rows in TABLES:
        all_insertions.append((para_idx, 'table', (tbl_id, caption, headers, rows)))
    
    # Add formulas
    all_insertions.append((105, 'formulas', FORMULAS))
    
    # Sort by para_idx DESCENDING (insert from bottom to top)
    all_insertions.sort(key=lambda x: x[0], reverse=True)
    
    for para_idx, ins_type, data in all_insertions:
        if para_idx >= total_paras:
            print(f'  ⚠ Skipping: paragraph index {para_idx} out of range ({total_paras})')
            continue
        
        p = doc.paragraphs[para_idx]
        
        if ins_type == 'figure':
            fig_id, caption, fig_type, img_path = data
            if fig_type == 'image' and img_path and os.path.exists(img_path):
                insert_real_image(p, fig_id, caption, img_path, width=5.5)
                print(f'  ✓ Hình {fig_id}: {caption} (ảnh thực)')
            else:
                insert_placeholder_image(p, fig_id, caption)
                print(f'  ✓ Hình {fig_id}: {caption} (placeholder)')
        
        elif ins_type == 'table':
            tbl_id, caption, headers, rows = data
            insert_table_with_caption(p, tbl_id, caption, headers, rows, doc)
            print(f'  ✓ Bảng {tbl_id}: {caption}')
        
        elif ins_type == 'formulas':
            insert_formula_block(p, data)
            print(f'  ✓ Công thức đánh giá (Accuracy, Precision, Recall, F1-Score)')
    
    # Step 4: Populate lists
    print('\n[4/4] Đang hoàn thành danh mục...')
    figures_meta = [(fig_id, caption) for _, fig_id, caption, _, _ in FIGURES]
    tables_meta = [(tbl_id, caption) for _, tbl_id, caption, _, _ in TABLES]
    populate_list_of_figures(doc, figures_meta)
    populate_list_of_tables(doc, tables_meta)
    
    # Save
    out = 'DTC225210078_FINAL.docx'
    doc.save(out)
    print(f'\n{"=" * 60}')
    print(f'✅ HOÀN THÀNH! File đã lưu tại: {out}')
    print(f'  - {len(FIGURES)} hình ảnh đã chèn')
    print(f'  - {len(TABLES)} bảng biểu đã chèn')
    print(f'  - 4 công thức đánh giá đã chèn')
    print(f'  - Danh mục hình ảnh: {len(figures_meta)} mục')
    print(f'  - Danh mục bảng biểu: {len(tables_meta)} mục')
    print(f'{"=" * 60}')

if __name__ == '__main__':
    main()
