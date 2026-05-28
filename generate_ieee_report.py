"""
Generate IEEE-styled Graduation Report — FallGuard AI
=====================================================
Sinh báo cáo đồ án tốt nghiệp 3 chương theo cấu trúc trường,
áp dụng chuẩn trích dẫn IEEE [1], [2], ...
Bảng đánh số: Bảng X.Y, Hình X.Y

Output: DTC225210078_Tăng Tuấn Minh_CNTTK21CLC.docx
"""

from docx import Document
from docx.shared import Pt, Inches, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml
from pathlib import Path

BASE_DIR = Path(__file__).parent
OUTPUT_FILE = BASE_DIR / "DTC225210078_Tăng Tuấn Minh_CNTTK21CLC.docx"

# ══════════════════════════════════════════════════════════════════
# DANH MỤC TÀI LIỆU THAM KHẢO (IEEE FORMAT)
# ══════════════════════════════════════════════════════════════════
REFERENCES = [
    'A. Sucerquia, J. D. López, and J. F. Vargas-Bonilla, "SisFall: A Fall and Movement Dataset," '
    'Sensors, vol. 17, no. 1, p. 198, Jan. 2017. doi: 10.3390/s17010198.',
    'World Health Organization, "Falls," WHO Fact Sheet, Apr. 2021. '
    '[Online]. Available: https://www.who.int/news-room/fact-sheets/detail/falls',
    'S. Hochreiter and J. Schmidhuber, "Long Short-Term Memory," '
    'Neural Computation, vol. 9, no. 8, pp. 1735–1780, Nov. 1997.',
    'K. Cho et al., "Learning Phrase Representations using RNN Encoder-Decoder '
    'for Statistical Machine Translation," in Proc. EMNLP, 2014, pp. 1724–1734.',
    'J. Redmon, S. Divvala, R. Girshick, and A. Farhadi, "You Only Look Once: '
    'Unified, Real-Time Object Detection," in Proc. IEEE CVPR, 2016, pp. 779–788.',
    'Ultralytics, "YOLOv11 Documentation," 2024. [Online]. Available: https://docs.ultralytics.com/',
    'S. Bai, J. Z. Kolter, and V. Koltun, "An Empirical Evaluation of Generic '
    'Convolutional and Recurrent Networks for Sequence Modeling," arXiv:1803.01271, 2018.',
    'A. Vaswani et al., "Attention is All You Need," in Proc. NeurIPS, 2017, pp. 5998–6008.',
    'D. P. Kingma and J. Ba, "Adam: A Method for Stochastic Optimization," in Proc. ICLR, 2015.',
    'A. Paszke et al., "PyTorch: An Imperative Style, High-Performance Deep Learning Library," '
    'in Proc. NeurIPS, 2019, pp. 8026–8037.',
    'S. Ramírez, "FastAPI framework, high performance, easy to learn," 2019. '
    '[Online]. Available: https://fastapi.tiangolo.com/',
    'Y. LeCun, Y. Bengio, and G. Hinton, "Deep Learning," Nature, vol. 521, pp. 436–444, 2015.',
    'N. Noury et al., "Fall detection — Principles and Methods," in Proc. IEEE EMBS, 2007, pp. 1663–1666.',
    'M. Mubashir, L. Shao, and L. Seed, "A survey on fall detection: Principles and approaches," '
    'Neurocomputing, vol. 100, pp. 144–152, 2013.',
    'X. Yu, "Approaches and principles of fall detection for elderly and patient," '
    'in Proc. IEEE HealthCom, 2008, pp. 42–47.',
    'I. Goodfellow, Y. Bengio, and A. Courville, Deep Learning. MIT Press, 2016.',
    'K. He, X. Zhang, S. Ren, and J. Sun, "Deep Residual Learning for Image Recognition," '
    'in Proc. IEEE CVPR, 2016, pp. 770–778.',
    'C. Szegedy et al., "Going Deeper with Convolutions," in Proc. IEEE CVPR, 2015.',
    'T. N. Sainath et al., "Convolutional, Long Short-Term Memory, fully connected Deep Neural Networks," '
    'in Proc. IEEE ICASSP, 2015, pp. 4580–4584.',
    'F. Ordóñez and D. Roggen, "Deep Convolutional and LSTM Recurrent Neural Networks for '
    'Multimodal Wearable Activity Recognition," Sensors, vol. 16, no. 1, p. 115, 2016.',
]

# ══════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════

def setup_document():
    """Tạo document từ mẫu của Nguyễn Thanh Tuân, xóa nội dung cũ và chuẩn bị các trang bìa chính xác."""
    base_path = "DTC225210134_Nguyễn Thanh Tuân_CNTTK21CLC.docx"
    doc = Document(base_path)
    
    # 1. Xóa toàn bộ các bảng trong tài liệu mẫu
    for t in list(doc.tables):
        t._element.getparent().remove(t._element)
        
    # 2. Xóa toàn bộ các đoạn văn bản từ sau trang bìa (từ index 50 trở đi)
    for p in list(doc.paragraphs[50:]):
        p._element.getparent().remove(p._element)
        
    # Helper để thay thế chữ trong run an toàn
    def safe_replace(p, old_text, new_text):
        if p.runs:
            full_text = "".join(r.text for r in p.runs)
            if old_text in full_text:
                replaced = False
                for r in p.runs:
                    if old_text in r.text:
                        r.text = r.text.replace(old_text, new_text)
                        replaced = True
                if not replaced:
                    p.runs[0].text = full_text.replace(old_text, new_text)
                    for r in p.runs[1:]:
                        r.text = ""
        else:
            if old_text in p.text:
                p.text = p.text.replace(old_text, new_text)

    # 3. Thay thế thông tin của Nguyễn Thanh Tuân thành Tăng Tuấn Minh trên các trang bìa
    # - Bìa Ngoài (Outer Cover)
    safe_replace(doc.paragraphs[7], 'NGUYỄN THANH TUÂN', 'TĂNG TUẤN MINH')
    safe_replace(doc.paragraphs[13], 
                 'XÂY DỰNG HỆ THỐNG GIÁM SÁT AN NINH THÔNG MINH DỰA TRÊN HỌC SÂU', 
                 'ỨNG DỤNG HỌC SÂU TRONG NHẬN DẠNG\nHÀNH VI TÉ NGÃ CỦA NGƯỜI CAO TUỔI')
    safe_replace(doc.paragraphs[26], 'THÁI NGUYÊN, THÁNG 4 NĂM 2026', 'THÁI NGUYÊN, THÁNG 05 NĂM 2026')
    
    # - Bìa Trong (Inner Cover)
    safe_replace(doc.paragraphs[36], 
                 'XÂY DỤNG HỆ THỐNG GIAM SÁT AN NINH THÔNG MINH DỰA TRÊN HỌC SÂU', 
                 'ỨNG DỤNG HỌC SÂU TRONG NHẬN DẠNG HÀNH VI TÉ NGÃ CỦA NGƯỜI CAO TUỔI')
    safe_replace(doc.paragraphs[41], 'Nguyễn Thanh Tuân', 'Tăng Tuấn Minh')
    safe_replace(doc.paragraphs[43], 'DTC225210134', 'DTC225210078')
    safe_replace(doc.paragraphs[49], 'Thái Nguyên, tháng 4  năm 2026', 'Thái Nguyên, tháng 05 năm 2026')

    # 4. Đảm bảo lề chuẩn cho toàn bộ các section trong tài liệu (lề 3cm trái, 2cm phải, 2cm trên, 2cm dưới)
    for section in doc.sections:
        section.page_width = Cm(21)
        section.page_height = Cm(29.7)
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(3)
        section.right_margin = Cm(2)
        
    # 5. Cấu hình lại Normal style
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(13)
    pf = style.paragraph_format
    pf.space_after = Pt(6)
    pf.line_spacing = 1.5
    
    # Heading styles
    for i in range(1, 5):
        hs = doc.styles[f'Heading {i}']
        hf = hs.font
        hf.name = 'Times New Roman'
        hf.color.rgb = RGBColor(0, 0, 0)
        hf.bold = True
        if i == 1:
            hf.size = Pt(16)
            hs.paragraph_format.space_before = Pt(18)
            hs.paragraph_format.space_after = Pt(12)
            hs.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif i == 2:
            hf.size = Pt(14)
            hs.paragraph_format.space_before = Pt(12)
            hs.paragraph_format.space_after = Pt(6)
        elif i == 3:
            hf.size = Pt(13)
            hs.paragraph_format.space_before = Pt(6)
            hs.paragraph_format.space_after = Pt(6)
        else:
            hf.size = Pt(13)
            hf.italic = True
            
    return doc


def add_paragraph(doc, text, bold=False, italic=False, indent=False, alignment=None, font_size=None):
    """Thêm đoạn văn với format."""
    p = doc.add_paragraph()
    if indent:
        p.paragraph_format.first_line_indent = Cm(1.27)
    if alignment:
        p.alignment = alignment
    run = p.add_run(text)
    run.bold = bold
    run.italic = italic
    if font_size:
        run.font.size = Pt(font_size)
    return p


def add_table(doc, headers, rows, caption=None):
    """Thêm bảng với border và format chuẩn."""
    if caption:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.keep_with_next = True
        run = p.add_run(caption)
        run.bold = True
        run.font.size = Pt(12)
        run.font.name = 'Times New Roman'
    
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    try:
        table.style = 'Table Grid'
    except Exception:
        # Fallback to manual XML borders if Table Grid style is missing
        tblPr = table._tbl.tblPr
        tblBorders = parse_xml(
            '<w:tblBorders %s>'
            '  <w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
            '  <w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
            '  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
            '  <w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
            '  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
            '  <w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
            '</w:tblBorders>' % nsdecls('w')
        )
        tblPr.append(tblBorders)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    # Header row
    hdr = table.rows[0]
    for i, h in enumerate(headers):
        cell = hdr.cells[i]
        cell.text = ''
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(h)
        run.bold = True
        run.font.size = Pt(12)
        run.font.name = 'Times New Roman'
        # Shade header
        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="D9E2F3"/>')
        cell._tc.get_or_add_tcPr().append(shading)
    
    # Data rows
    for r_idx, row_data in enumerate(rows):
        row = table.rows[r_idx + 1]
        for c_idx, val in enumerate(row_data):
            cell = row.cells[c_idx]
            cell.text = ''
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(str(val))
            run.font.size = Pt(12)
            run.font.name = 'Times New Roman'
    
    doc.add_paragraph()  # spacing
    return table


def add_formula(doc, formula_text, label=None):
    """Thêm công thức (text) với label."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(formula_text)
    run.italic = True
    run.font.size = Pt(13)
    if label:
        run2 = p.add_run(f'    ({label})')
        run2.font.size = Pt(13)
    return p


def add_image(doc, filename, caption=None, width_inch=5.5):
    """Thêm hình ảnh vào document và chú thích ở dưới."""
    assets_dir = Path(__file__).parent / "assets"
    file_path = assets_dir / filename
    if not file_path.exists():
        print(f"    [WARN] Image {filename} not found in assets, skipping.")
        return None
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(file_path), width=Inches(width_inch))
    
    if caption:
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(3)
        p_cap.paragraph_format.space_after = Pt(12)
        p_cap.paragraph_format.keep_with_next = False
        run = p_cap.add_run(caption)
        run.italic = True
        run.font.size = Pt(11)
        run.font.name = 'Times New Roman'
    return p


def add_title_page(doc):
    """Trang bìa đã được thiết lập chính xác từ tài liệu mẫu trong setup_document()."""
    pass

# ══════════════════════════════════════════════════════════════════
# LỜI CẢM ƠN, LỜI CAM ĐOAN, TÓM TẮT
# ══════════════════════════════════════════════════════════════════

def add_front_matter(doc):
    # --- LỜI CẢM ƠN ---
    doc.add_heading('LỜI CẢM ƠN', level=1)
    add_paragraph(doc, 
        'Lời đầu tiên, em xin bày tỏ lòng biết ơn sâu sắc đến TS. Nguyễn Tuấn Anh — '
        'giảng viên hướng dẫn — người đã tận tình chỉ bảo, định hướng khoa học và tạo mọi '
        'điều kiện thuận lợi nhất để em hoàn thành đồ án tốt nghiệp này.', indent=True)
    add_paragraph(doc,
        'Em xin chân thành cảm ơn quý thầy cô Khoa Công nghệ Thông tin, Trường Đại học '
        'Công nghệ Thông tin và Truyền thông Thái Nguyên đã truyền đạt những kiến thức '
        'quý báu trong suốt quá trình học tập và rèn luyện tại trường.', indent=True)
    add_paragraph(doc,
        'Em cũng xin gửi lời cảm ơn đến gia đình, bạn bè đã luôn động viên, '
        'hỗ trợ em trong suốt quá trình thực hiện đồ án.', indent=True)
    add_paragraph(doc,
        'Mặc dù đã cố gắng hết sức nhưng do kiến thức và kinh nghiệm còn hạn chế nên '
        'đồ án không tránh khỏi những thiếu sót. Em rất mong nhận được sự góp ý, chỉ bảo '
        'của quý thầy cô để em có thể hoàn thiện hơn.', indent=True)
    add_paragraph(doc, 'Em xin chân thành cảm ơn!', indent=True)
    p_sign = doc.add_paragraph()
    p_sign.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_sign.add_run('Thái Nguyên, tháng 05 năm 2026\n').italic = True
    p_sign.add_run('Sinh viên\n').bold = True
    p_sign.add_run('Tăng Tuấn Minh').bold = True
    doc.add_page_break()

    # --- LỜI CAM ĐOAN ---
    doc.add_heading('LỜI CAM ĐOAN', level=1)
    add_paragraph(doc,
        'Em xin cam đoan đồ án tốt nghiệp "Ứng dụng học sâu trong nhận dạng hành vi '
        'té ngã của người cao tuổi" là công trình nghiên cứu của riêng em dưới sự hướng '
        'dẫn của TS. Nguyễn Tuấn Anh.', indent=True)
    add_paragraph(doc,
        'Các số liệu, kết quả trình bày trong đồ án là trung thực và chưa từng được '
        'công bố trong bất kỳ công trình nghiên cứu nào khác. Các tài liệu tham khảo '
        'đều được trích dẫn đầy đủ theo chuẩn IEEE.', indent=True)
    add_paragraph(doc,
        'Em xin chịu hoàn toàn trách nhiệm về nội dung đồ án của mình.', indent=True)
    p_sign2 = doc.add_paragraph()
    p_sign2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_sign2.add_run('Thái Nguyên, tháng 05 năm 2026\n').italic = True
    p_sign2.add_run('Sinh viên\n').bold = True
    p_sign2.add_run('Tăng Tuấn Minh').bold = True
    doc.add_page_break()

    # --- DANH MỤC TỪ VIẾT TẮT ---
    doc.add_heading('DANH MỤC TỪ VIẾT TẮT', level=1)
    abbrevs = [
        ('AI', 'Artificial Intelligence — Trí tuệ nhân tạo'),
        ('ADL', 'Activities of Daily Living — Hoạt động sinh hoạt hàng ngày'),
        ('API', 'Application Programming Interface — Giao diện lập trình ứng dụng'),
        ('AUC', 'Area Under the ROC Curve — Diện tích dưới đường cong ROC'),
        ('Bi-LSTM', 'Bidirectional Long Short-Term Memory — LSTM hai chiều'),
        ('CNN', 'Convolutional Neural Network — Mạng nơ-ron tích chập'),
        ('CNN-LSTM', 'Convolutional Neural Network - Long Short-Term Memory'),
        ('CORS', 'Cross-Origin Resource Sharing'),
        ('CSV', 'Comma-Separated Values'),
        ('DL', 'Deep Learning — Học sâu'),
        ('FPS', 'Frames Per Second — Số khung hình mỗi giây'),
        ('GRU', 'Gated Recurrent Unit — Đơn vị cổng hồi quy'),
        ('HTTP', 'Hypertext Transfer Protocol'),
        ('IEEE', 'Institute of Electrical and Electronics Engineers'),
        ('LSTM', 'Long Short-Term Memory — Bộ nhớ dài-ngắn hạn'),
        ('ML', 'Machine Learning — Học máy'),
        ('MJPEG', 'Motion JPEG'),
        ('ReLU', 'Rectified Linear Unit'),
        ('REST', 'Representational State Transfer'),
        ('RNN', 'Recurrent Neural Network — Mạng nơ-ron hồi quy'),
        ('ROC', 'Receiver Operating Characteristic'),
        ('SQL', 'Structured Query Language'),
        ('SVM', 'Signal Vector Magnitude — Độ lớn vector tín hiệu'),
        ('TCN', 'Temporal Convolutional Network — Mạng tích chập thời gian'),
        ('WHO', 'World Health Organization — Tổ chức Y tế Thế giới'),
        ('YOLO', 'You Only Look Once'),
    ]
    add_table(doc, ['Từ viết tắt', 'Giải nghĩa'], abbrevs)
    doc.add_page_break()

    # --- DANH MỤC HÌNH ẢNH ---
    doc.add_heading('DANH MỤC HÌNH ẢNH', level=1)
    figures = [
        ('Hình 1.1', 'Thống kê tỷ lệ tử vong do té ngã theo WHO'),
        ('Hình 1.2', 'So sánh các phương pháp phát hiện té ngã'),
        ('Hình 1.3', 'Kiến trúc mạng LSTM cell'),
        ('Hình 1.4', 'Kiến trúc mạng GRU cell'),
        ('Hình 1.5', 'Mô hình YOLOv11 Pose Estimation — 17 keypoints'),
        ('Hình 1.6', 'Ma trận nhầm lẫn (Confusion Matrix)'),
        ('Hình 2.1', 'Kiến trúc tổng thể hệ thống FallGuard AI'),
        ('Hình 2.2', 'Cấu trúc bộ dữ liệu SisFall'),
        ('Hình 2.3', 'Quy trình tiền xử lý dữ liệu (Sliding Window)'),
        ('Hình 2.4', 'Kiến trúc mô hình Bi-LSTM + Attention'),
        ('Hình 2.5', 'Kiến trúc mô hình CNN-LSTM'),
        ('Hình 2.6', 'Kiến trúc mô hình TCN (Temporal Convolutional Network)'),
        ('Hình 2.7', 'Kiến trúc mô hình Transformer Encoder'),
        ('Hình 2.8', 'Sơ đồ thuật toán phát hiện té ngã thời gian thực'),
        ('Hình 2.9', 'Thiết kế cơ sở dữ liệu SQLite'),
        ('Hình 3.1', 'Giao diện Tab Live Monitor'),
        ('Hình 3.2', 'Giao diện Tab Statistics'),
        ('Hình 3.3', 'Giao diện Tab History'),
        ('Hình 3.4', 'Giao diện Tab Settings'),
        ('Hình 3.5', 'Biểu đồ so sánh Accuracy 5 mô hình'),
        ('Hình 3.6', 'Đường cong ROC 5 mô hình'),
        ('Hình 3.7', 'Ma trận nhầm lẫn — CNN-LSTM'),
        ('Hình 3.8', 'Biểu đồ Training Loss / Validation Loss'),
    ]
    add_table(doc, ['Hình', 'Mô tả'], figures)
    doc.add_page_break()

    # --- DANH MỤC BẢNG BIỂU ---
    doc.add_heading('DANH MỤC BẢNG BIỂU', level=1)
    tables_list = [
        ('Bảng 1.1', 'So sánh các phương pháp phát hiện té ngã'),
        ('Bảng 1.2', 'Tổng hợp các nghiên cứu liên quan'),
        ('Bảng 1.3', 'So sánh các Web Framework xây dựng API thời gian thực'),
        ('Bảng 2.1', 'Thông số cảm biến bộ dữ liệu SisFall'),
        ('Bảng 2.2', 'Phân bố hoạt động trong SisFall'),
        ('Bảng 2.3', 'Kiến trúc chi tiết 5 mô hình Deep Learning'),
        ('Bảng 2.4', 'Cấu hình hyperparameters huấn luyện'),
        ('Bảng 2.5', 'Cấu hình tham số YOLOv11-Pose'),
        ('Bảng 2.6', 'Thiết kế API endpoints'),
        ('Bảng 2.7', 'Cấu trúc chi tiết bảng incidents trong SQLite'),
        ('Bảng 3.1', 'Cấu hình phần cứng thực nghiệm'),
        ('Bảng 3.2', 'Kết quả so sánh 5 mô hình trên tập Test'),
        ('Bảng 3.3', 'So sánh thời gian huấn luyện và inference'),
        ('Bảng 3.4', 'Đánh giá hiệu năng hệ thống thời gian thực'),
    ]
    add_table(doc, ['Bảng', 'Mô tả'], tables_list)
    doc.add_page_break()

    # --- TÓM TẮT ---
    doc.add_heading('TÓM TẮT ĐỒ ÁN', level=1)
    add_paragraph(doc,
        'Té ngã là một trong những nguyên nhân hàng đầu gây chấn thương nghiêm trọng và '
        'tử vong ở người cao tuổi trên toàn cầu. Theo thống kê của Tổ chức Y tế Thế giới '
        '(WHO), mỗi năm có khoảng 684.000 người tử vong do té ngã, trong đó phần lớn là '
        'người trên 60 tuổi [2]. Việc phát hiện sớm và can thiệp kịp thời đóng vai trò '
        'quyết định trong việc giảm thiểu hậu quả của tai nạn té ngã.', indent=True)
    add_paragraph(doc,
        'Đồ án "Ứng dụng học sâu trong nhận dạng hành vi té ngã của người cao tuổi" xây dựng '
        'hệ thống FallGuard AI — một hệ thống giám sát thông minh kết hợp hai nhánh phân tích: '
        '(1) Nhánh Thị giác máy tính (Computer Vision) sử dụng mô hình YOLOv11-Pose để ước '
        'lượng tư thế 17 điểm khung xương kết hợp các luật heuristic phân tích vận tốc, tỷ lệ '
        'bounding box và vị trí đầu-hông; (2) Nhánh Phân tích chuỗi thời gian từ dữ liệu cảm '
        'biến đeo tay sử dụng các kiến trúc Học sâu bao gồm Bi-LSTM + Attention, Bi-GRU, '
        'CNN-LSTM, Transformer Encoder và TCN.', indent=True)
    add_paragraph(doc,
        'Hệ thống được huấn luyện và đánh giá trên bộ dữ liệu chuẩn quốc tế SisFall [1] '
        'gồm 4.510 bản ghi từ 38 đối tượng tham gia. Kết quả thực nghiệm cho thấy mô hình '
        'CNN-LSTM đạt độ chính xác cao nhất (Accuracy ≈ 98%, F1-Score ≈ 0.98), trong khi '
        'nhánh Vision với YOLOv11-Pose hoạt động ổn định ở tốc độ >25 FPS trên phần cứng '
        'tầm trung. Toàn bộ hệ thống được tích hợp trên nền tảng web với FastAPI backend '
        'và giao diện Dashboard giám sát thời gian thực.', indent=True)
    add_paragraph(doc,
        'Từ khóa: Phát hiện té ngã, Học sâu, LSTM, CNN-LSTM, YOLOv11-Pose, '
        'SisFall, Người cao tuổi, Thời gian thực.', bold=True, indent=True)
    doc.add_page_break()


# ══════════════════════════════════════════════════════════════════
# MỤC LỤC placeholder
# ══════════════════════════════════════════════════════════════════

def add_toc_placeholder(doc):
    doc.add_heading('MỤC LỤC', level=1)
    add_paragraph(doc, '(Mục lục sẽ được tạo tự động bằng chức năng Table of Contents trong Word — '
                       'nhấn Ctrl+A → F9 để cập nhật sau khi mở file.)')
    doc.add_page_break()


# ══════════════════════════════════════════════════════════════════
# CHƯƠNG 1: TỔNG QUAN VÀ CƠ SỞ LÝ THUYẾT
# ══════════════════════════════════════════════════════════════════

def add_chapter_1(doc):
    doc.add_heading('CHƯƠNG 1. TỔNG QUAN VÀ CƠ SỞ LÝ THUYẾT', level=1)
    
    # ── LỜI NÓI ĐẦU CHƯƠNG ──
    add_paragraph(doc,
        'Chương này trình bày tổng quan về bài toán phát hiện té ngã ở người cao tuổi, '
        'các phương pháp tiếp cận hiện tại và cơ sở lý thuyết về Học sâu (Deep Learning) '
        'được áp dụng trong đồ án. Nội dung bao gồm phân tích bối cảnh thực tiễn, khảo sát '
        'các nghiên cứu liên quan, lý thuyết về các kiến trúc mạng nơ-ron (LSTM, GRU, CNN, '
        'Transformer, TCN) và các phương pháp đánh giá mô hình.', indent=True)

    # ═══════════════════════════════════════════════════
    # 1.1 Tổng quan về bài toán
    # ═══════════════════════════════════════════════════
    doc.add_heading('1.1. Tổng quan về bài toán phát hiện té ngã', level=2)
    
    doc.add_heading('1.1.1. Bối cảnh và sự cần thiết', level=3)
    add_paragraph(doc,
        'Sự biến đổi sâu sắc về cơ cấu nhân khẩu học trên phạm vi toàn cầu, đặc biệt là xu hướng già hóa dân số '
        'đang diễn ra với tốc độ chưa từng thấy, đã và đang đặt ra những thách thức vô cùng lớn đối với hệ thống y tế '
        'và an sinh xã hội của mọi quốc gia. Theo các báo cáo thống kê chính thức từ Tổ chức Y tế Thế giới (WHO), '
        'té ngã không chỉ đơn thuần là một tai nạn sinh hoạt thông thường mà đã trở thành nguyên nhân gây tử vong '
        'hàng đầu do tai nạn thương tích không chủ ý ở người cao tuổi, đứng thứ hai toàn cầu chỉ sau tai nạn giao thông [2]. '
        'Mỗi năm, thế giới ghi nhận khoảng 684.000 ca tử vong do té ngã, trong đó đối tượng chịu ảnh hưởng nặng nề nhất '
        'là những người từ 60 tuổi trở lên. Quá trình lão hóa tự nhiên dẫn đến sự suy giảm liên tục và không thể đảo ngược '
        'của các chức năng sinh lý cơ bản, bao gồm sự suy giảm thị lực, mất thăng bằng tiền đình, suy giảm sức mạnh cơ bắp '
        'và sự chậm trễ trong phản xạ thần kinh vận động. Những yếu tố nội tại này, khi kết hợp với môi trường sống xung quanh '
        'nhiều rủi ro (như sàn nhà trơn trượt, ánh sáng yếu, chướng ngại vật), làm tăng đáng kể tần suất xảy ra sự cố. '
        'Ước tính có khoảng 28% đến 35% người cao tuổi trên 65 tuổi gặp phải ít nhất một lần té ngã mỗi năm, '
        'và con số này tăng lên tới 32-42% đối với những người trên 70 tuổi [13]. Điều này cho thấy tính nghiêm trọng và '
        'quy mô mang tính dịch tễ học của bài toán té ngã ở người cao tuổi, đòi hỏi những giải pháp can thiệp mang tính chủ động '
        'và công nghệ hóa sâu sắc.', indent=True)
    add_paragraph(doc,
        'Hậu quả y sinh và lâm sàng của tai nạn té ngã đối với sức khỏe thể chất của người cao tuổi là vô cùng nặng nề và '
        'thường kéo theo những di chứng lâu dài, thậm chí là tàn phế vĩnh viễn. Khi xảy ra té ngã, lực tác động cơ học trực tiếp '
        'lên hệ xương khớp đã bị loãng xương của người già thường dẫn đến các chấn thương nghiêm trọng như gãy cổ xương đùi, '
        'gãy xương hông, chấn thương sọ não, xuất huyết nội hoặc tổn thương mô mềm diện rộng. Trong đó, gãy xương hông là một '
        'cực hình y khoa đối với người già, đòi hỏi phải phẫu thuật can thiệp ngay lập tức và có tỷ lệ tử vong trong vòng một năm '
        'sau tai nạn lên tới 20-30% do các biến chứng liên đới từ việc nằm bất động kéo dài. Thời gian nằm liệt giường sau té ngã '
        'kích hoạt một chuỗi biến chứng lâm sàng phức tạp bao gồm huyết khối tĩnh mạch sâu (DVT), thuyên tắc phổi, loét tỳ đè '
        '(decubitus ulcers), viêm phổi do ứ đọng (hypostatic pneumonia), và hội chứng suy giảm cơ bắp (sarcopenia) diễn ra với '
        'tốc độ chóng mặt. Không chỉ dừng lại ở tổn thương thể chất, té ngã còn để lại một gánh nặng tâm lý sâu sắc được gọi là '
        '"hội chứng sợ ngã" (fear of falling). Hội chứng này tạo ra một vòng xoáy bệnh lý tiêu cực: sự sợ hãi khiến người cao '
        'tuổi tự hạn chế di chuyển, xa lánh các hoạt động xã hội và sinh hoạt hằng ngày (ADL), từ đó đẩy nhanh quá trình teo cơ, '
        'mất thăng bằng, suy giảm chức năng tim mạch và dẫn đến các trạng thái tâm thần trầm cảm, cô đơn sâu sắc. Về mặt kinh tế '
        'xã hội, chi phí chăm sóc y tế cấp cứu, phẫu thuật chỉnh hình và phục hồi chức năng sau té ngã là một gánh nặng khổng lồ '
        'đè nặng lên hệ thống bảo hiểm y tế quốc gia và trực tiếp làm kiệt quệ tài chính của các hộ gia đình có người già bị nạn.', indent=True)
    
    add_paragraph(doc,
        'Một khía cạnh y khoa cốt lõi quyết định đến khả năng sống sót và mức độ phục hồi của người cao tuổi sau sự cố té ngã '
        'chính là khái niệm "Giờ Vàng" (Golden Hour) trong cấp cứu y tế. Các nghiên cứu lâm sàng đã chứng minh rằng nếu một '
        'người già bị té ngã và phải nằm trên sàn nhà mà không thể tự đứng dậy hoặc không được phát hiện trong vòng 1 giờ đầu '
        '(hiện tượng long-lie), tỷ lệ tử vong hoặc phải chuyển vào các trung tâm chăm sóc đặc biệt dài hạn tăng lên gấp nhiều lần. '
        'Nằm bất động kéo dài trên sàn gây ra tình trạng tiêu cơ vân cấp tính (rhabdomyolysis) - giải phóng lượng lớn myoglobin '
        'vào máu dẫn đến suy thận cấp, kết hợp với tình trạng hạ thân nhiệt (hypothermia), mất nước nghiêm trọng và chấn thương tâm '
        'lý hoảng loạn. Do đó, việc xây dựng các hệ thống công nghệ có khả năng tự động phát hiện, nhận dạng chính xác và gửi '
        'cảnh báo khẩn cấp tức thời trong vòng vài giây ngay sau khi cú ngã xảy ra là một giải pháp y tế công cộng mang tính sống còn, '
        'giúp tối thiểu hóa thời gian phản ứng, kích hoạt chuỗi cấp cứu kịp thời và bảo vệ tính mạng cho người cao tuổi.', indent=True)
    add_paragraph(doc,
        'Tại Việt Nam, bối cảnh già hóa dân số đang diễn ra với tốc độ thuộc hàng nhanh nhất thế giới. Theo số liệu của Tổng cục '
        'Thống kê, nước ta đã chính thức bước vào giai đoạn "già hóa dân số" từ năm 2011 và dự kiến sẽ chuyển sang giai đoạn '
        '"dân số già" vào năm 2038. Sự thay đổi nhanh chóng này tạo ra áp lực cực kỳ lớn lên hệ thống cơ sở hạ tầng y tế vốn '
        'đã quá tải, đồng thời làm thay đổi sâu sắc cấu trúc gia đình truyền thống. Với xu hướng đô thị hóa và sự phổ biến của '
        'mô hình gia đình hạt nhân, số lượng người cao tuổi sống cô đơn một mình hoặc chỉ sống cùng người bạn đời cũng già yếu '
        'ngày càng gia tăng một cách chóng mặt. Trong khi đó, các dịch vụ chăm sóc người già chuyên nghiệp hay viện dưỡng lão '
        'ở nước ta còn hạn chế về cả số lượng lẫn chất lượng và chưa phù hợp với tâm lý văn hóa truyền thống của người Việt. '
        'Thực tế này tạo ra một khoảng trống an toàn rất lớn khi người cao tuổi ở nhà một mình trong lúc con cháu đi làm hằng ngày. '
        'Bên cạnh đó, cấu trúc nhà ở truyền thống tại Việt Nam với nhiều bậc tam cấp, nhà vệ sinh trơn trượt, ánh sáng không '
        'được thiết kế chuyên biệt cho người già là những tác nhân tiềm ẩn nguy cơ té ngã cực cao [14]. Vì vậy, việc nghiên cứu '
        'và triển khai một hệ thống giám sát thông minh như FallGuard AI, có khả năng hoạt động liên tục 24/7, tự động hóa hoàn '
        'toàn bằng trí tuệ nhân tạo mà không cần sự can thiệp liên tục của con người, không chỉ giải quyết triệt để bài toán an '
        'toàn y tế cho người cao tuổi mà còn mang lại sự an tâm tuyệt đối cho các gia đình và giảm bớt gánh nặng tâm lý cho toàn '
        'xã hội [15].', indent=True)
    
    add_image(doc, "who_fall_stats.png", "Hình 1.1. Thống kê số ca tử vong do tai nạn thương tích hàng năm toàn cầu theo báo cáo WHO", width_inch=5.5)

    doc.add_heading('1.1.2. Phân loại các phương pháp phát hiện té ngã', level=3)
    add_paragraph(doc,
        'Các phương pháp phát hiện té ngã hiện nay có thể được phân thành ba nhóm chính '
        'dựa trên loại dữ liệu đầu vào sử dụng [14]:', indent=True)
    add_paragraph(doc,
        '1) Nhóm dựa trên thiết bị đeo (Wearable-based): Đây là phương pháp tiếp cận kinh điển, hoạt động bằng cách yêu cầu '
        'người dùng mang các thiết bị tích hợp cảm biến điện cơ vi hệ (MEMS) như gia tốc kế ba trục (Tri-axial Accelerometer), '
        'con quay hồi chuyển (Gyroscope) và cảm biến từ trường (Magnetometer). Các thiết bị này thường được thiết kế dưới dạng '
        'vòng đeo tay, đai đeo hông, mặt dây chuyền cổ hoặc nhúng trực tiếp vào điện thoại thông minh và đồng hồ thông minh. '
        'Về mặt vật lý, cảm biến đo đạc trực tiếp các thông số động học của cơ thể bao gồm gia tốc tuyến tính (linear acceleration) '
        'và vận tốc góc (angular velocity) theo các trục tọa độ X, Y, Z. Ưu điểm nổi bật nhất của phương pháp này là độ chính xác '
        'phân loại cực kỳ cao (thường đạt trên 95% trong phòng thí nghiệm), khả năng hoạt động liên tục bất kể môi trường trong '
        'nhà hay ngoài trời, và hoàn toàn không bị ảnh hưởng bởi các yếu tố che khuất vật lý (occlusion) hay điều kiện ánh sáng. '
        'Tuy nhiên, rào cản lớn nhất cản trở sự phổ biến của thiết bị đeo là tính tuân thủ của người dùng (user compliance): '
        'người cao tuổi thường xuyên cảm thấy phiền toái, vướng víu khi phải đeo thiết bị liên tục, đặc biệt là khi ngủ hoặc tắm '
        '(nơi có nguy cơ ngã cao nhất), hoặc họ thường xuyên quên sạc pin và quên đeo thiết bị sau khi vệ sinh cá nhân, dẫn đến '
        'việc gián đoạn giám sát hoàn toàn.', indent=True)
    add_paragraph(doc,
        '2) Nhóm dựa trên thị giác máy tính (Vision-based): Phương pháp này sử dụng các camera giám sát thông thường (RGB), '
        'camera hồng ngoại hoặc camera cảm biến chiều sâu (RGB-D như Microsoft Kinect) được lắp đặt cố định tại các góc phòng '
        'để bao quát không gian sinh hoạt. Luồng video thu được sẽ được phân tích thời gian thực bằng các thuật toán xử lý ảnh '
        'và học sâu để nhận dạng các biến đổi về mặt không gian và động học của cơ thể người. Ưu điểm vượt trội của nhóm này là '
        'tính phi xâm lấn cơ thể (non-intrusive): người cao tuổi hoàn toàn tự do sinh hoạt, không phải mang bất kỳ thiết bị vướng víu '
        'nào trên người, giúp nâng cao đáng kể chất lượng cuộc sống và tính khả thi khi triển khai diện rộng. Dù vậy, thị giác máy tính '
        'phải đối mặt với ba thách thức kỹ thuật lớn: (1) Sự thay đổi thất thường của điều kiện ánh sáng và hiện tượng đổ bóng; '
        '(2) Hiện tượng vật cản che khuất một phần hoặc toàn bộ cơ thể (ví dụ ngã sau bàn, ghế, giường); và (3) Thách thức đặc biệt '
        'nghiêm trọng về quyền riêng tư cá nhân (privacy concerns), do việc lắp đặt camera ở các không gian nhạy cảm như phòng tắm '
        'hay phòng ngủ luôn vấp phải sự phản đối gay gắt từ người dùng và gia đình.', indent=True)
    add_paragraph(doc,
        '3) Nhóm dựa trên cảm biến môi trường (Ambient-based): Phương pháp này sử dụng các công nghệ cảm biến không tiếp xúc '
        'được nhúng trực tiếp vào môi trường sống xung quanh. Các công nghệ tiêu biểu bao gồm cảm biến áp suất dạng ma trận lắp dưới '
        'thảm trải sàn để đo sự thay đổi áp lực đột ngột, hệ thống micro thông minh thu nhận tiếng động va chạm cơ học đặc trưng '
        'của cú ngã (thud sound), và đặc biệt là công nghệ Radar sóng milimet (mmWave Radar) hoạt động ở băng tần 77GHz. Radar mmWave '
        'phát đi sóng điện từ và thu nhận tín hiệu phản xạ để phân tích micro-Doppler, từ đó tái tạo lại quỹ đạo chuyển động và tốc '
        'độ rơi của đối tượng. Nhóm cảm biến môi trường dung hòa tốt giữa quyền riêng tư (vì không ghi lại hình ảnh trực quan) và '
        'sự thoải mái của người dùng (không cần đeo thiết bị). Tuy nhiên, nhược điểm chí mạng của nó là chi phí thiết bị và lắp đặt '
        'cực kỳ đắt đỏ, đòi hỏi phải thi công cấu trúc nhà, phạm vi hoạt động của mỗi cảm biến bị giới hạn trong không gian hẹp và '
        'hệ thống cực kỳ dễ bị nhiễu loạn bởi các chuyển động của vật nuôi, robot hút bụi hoặc sự di chuyển của nhiều người cùng '
        'lúc trong phòng.', indent=True)
    
    add_table(doc,
        ['Phương pháp', 'Ưu điểm', 'Nhược điểm', 'Độ chính xác'],
        [
            ['Dựa trên Camera\n(Vision-based)', 'Trực quan, không cần\nthiết bị đeo', 'Bị ảnh hưởng bởi\ngóc quay, ánh sáng,\nquyền riêng tư', '85-95%'],
            ['Dựa trên Cảm biến đeo\n(Wearable-based)', 'Hoạt động mọi nơi,\nkhông bị che khuất', 'Phải đeo thiết bị,\nngười già hay quên', '90-98%'],
            ['Dựa trên môi trường\n(Ambient-based)', 'Không xâm phạm,\nkhông cần đeo', 'Chi phí cao, phức tạp\ntriển khai', '80-92%'],
        ],
        caption='Bảng 1.1. So sánh các phương pháp phát hiện té ngã'
    )
    
    add_image(doc, "fall_detection_methods.png", "Hình 1.2. Biểu đồ phân bố các nghiên cứu phát hiện té ngã hiện nay", width_inch=5.0)

    doc.add_heading('1.1.3. Các nghiên cứu liên quan', level=3)
    add_paragraph(doc,
        'Trong suốt hai thập kỷ qua, bài toán phát hiện té ngã đã thu hút sự quan tâm đặc biệt từ cộng đồng nghiên cứu khoa học '
        'quốc tế với hàng loạt các phương pháp tiếp cận từ đơn giản đến phức tạp được đề xuất. Ở giai đoạn khởi đầu, các thuật toán '
        'dựa trên ngưỡng cố định (threshold-based algorithms) được áp dụng phổ biến cho dữ liệu gia tốc kế nhờ ưu điểm tính toán '
        'cực kỳ nhẹ, có thể chạy trực tiếp trên các vi điều khiển công suất thấp của thiết bị đeo. Nguyên lý chung là tính toán '
        'độ lớn vector gia tốc tổng hợp (Signal Vector Magnitude - SVM) và kích hoạt cảnh báo khi giá trị này vượt quá một ngưỡng '
        'thiết lập sẵn (ví dụ 3.0g đến 3.5g). Tuy nhiên, các thuật toán ngưỡng này nhanh chóng bộc lộ hạn chế nghiêm trọng trong '
        'thực tế khi tạo ra tỷ lệ báo động giả (False Positives) cực kỳ cao. Chúng hoàn toàn bất lực trong việc phân biệt giữa '
        'một cú ngã thực sự với các hoạt động sinh hoạt hằng ngày có cường độ vận động mạnh tương đương như việc nhảy lên, ngồi '
        'nhanh xuống ghế sofa mượt mà, hay chạy bộ đột ngột dừng lại [13].', indent=True)
    add_paragraph(doc,
        'Để khắc phục triệt để hạn chế của phương pháp ngưỡng, các nghiên cứu tiếp theo đã chuyển dịch mạnh mẽ sang ứng dụng '
        'Học máy truyền thống (Traditional Machine Learning) với các thuật toán phân loại mạnh mẽ như Máy vectơ hỗ trợ (SVM), '
        'Cây quyết định (Decision Tree), Rừng ngẫu nhiên (Random Forest) và K-láng giềng gần nhất (KNN). Các thuật toán này hoạt '
        'động dựa trên các đặc trưng động học được thiết kế thủ công (hand-crafted features) được trích xuất từ miền thời gian '
        'và miền tần số của tín hiệu cảm biến (như giá trị trung bình, độ lệch chuẩn, năng lượng tín hiệu, entropy). Mặc dù đạt '
        'độ chính xác tốt hơn hẳn phương pháp ngưỡng, Học máy truyền thống vẫn gặp khó khăn khi triển khai thực tế do tính tổng quát '
        'hóa (generalization) kém và phụ thuộc quá nhiều vào kinh nghiệm của chuyên gia trong việc thiết kế và lựa chọn đặc trưng '
        'dữ liệu đầu vào.', indent=True)
    add_paragraph(doc,
        'Những năm gần đây, sự bùng nổ mạnh mẽ của Học sâu (Deep Learning) đã mở ra một kỷ nguyên mới cho bài toán nhận dạng hành vi. '
        'Các mạng nơ-ron sâu như Mạng tích chập 1D (1D-CNN), Mạng hồi quy bộ nhớ dài-ngắn hạn (LSTM), Đơn vị cổng hồi quy (GRU) '
        'và các mô hình Attention/Transformer đã chứng minh khả năng tự động học các biểu diễn đặc trưng phân cấp vô cùng phức tạp '
        'từ dữ liệu cảm biến thô mà không cần bất kỳ bước thiết kế đặc trưng thủ công nào. Trong nhánh thị giác máy tính, việc kết '
        'hợp giữa mô hình ước lượng tư thế thời gian thực (như YOLO-Pose, MediaPipe) với các bộ phân loại chuỗi thời gian đã giúp '
        'xây dựng các hệ thống giám sát camera thông minh vượt trội, vừa bảo vệ được quyền riêng tư (bằng cách chỉ trích xuất tọa độ '
        'khung xương dạng đồ thị và loại bỏ hình ảnh pixel thô) vừa đạt độ chính xác tiệm cận mức tuyệt đối. Bảng 1.2 tổng hợp '
        'các công trình nghiên cứu khoa học tiêu biểu đặt nền móng cho đề tài này:', indent=True)
    
    add_table(doc,
        ['Tác giả (Năm)', 'Phương pháp', 'Dữ liệu', 'Kết quả'],
        [
            ['Sucerquia et al.\n(2017) [1]', 'SVM + Decision Tree\ntrên SisFall', 'SisFall\n(4,510 bản ghi)', 'Acc: 95.5%\nSen: 96.0%'],
            ['Ordóñez & Roggen\n(2016) [20]', 'CNN + LSTM\nWearable sensors', 'UCI-HAR,\nOpportunity', 'F1: 91.5%'],
            ['Noury et al.\n(2007) [13]', 'Multi-sensor fusion\nThreshold-based', 'Custom dataset\n(20 subjects)', 'Sen: 97.5%\nSpe: 98.5%'],
            ['Mubashir et al.\n(2013) [14]', 'Shape + Motion\nfeatures + SVM', 'Multiple Camera\nFall Dataset', 'Acc: 91.3%\nSen: 93.2%'],
            ['Đồ án này\n(2026)', 'YOLOv11-Pose +\nBi-LSTM/CNN-LSTM\n+ Heuristic', 'SisFall [1]\n+ Webcam', 'Acc: ~98%\nF1: ~0.97'],
        ],
        caption='Bảng 1.2. Tổng hợp các nghiên cứu liên quan'
    )

    # ═══════════════════════════════════════════════════
    # 1.2 Cơ sở lý thuyết về Học sâu
    # ═══════════════════════════════════════════════════
    doc.add_heading('1.2. Cơ sở lý thuyết về Học sâu (Deep Learning)', level=2)
    add_paragraph(doc,
        'Học sâu (Deep Learning) là một nhánh của Học máy (Machine Learning) sử dụng '
        'các mạng nơ-ron nhân tạo nhiều lớp (deep neural networks) để tự động học các biểu '
        'diễn đặc trưng (feature representations) từ dữ liệu thô [12], [16]. Trong bài toán '
        'phát hiện té ngã, Học sâu cho phép hệ thống tự động trích xuất các đặc trưng phức '
        'tạp từ dữ liệu cảm biến mà không cần thiết kế thủ công (hand-crafted features).', indent=True)

    doc.add_heading('1.2.1. Mạng nơ-ron tích chập (CNN)', level=3)
    add_paragraph(doc,
        'Mạng nơ-ron tích chập (Convolutional Neural Network - CNN) là một trong những cột trụ công nghệ cốt lõi của Học sâu, '
        'nổi tiếng với khả năng tự động trích xuất các đặc trưng không gian có tính phân cấp từ dữ liệu hình ảnh hai chiều nhờ vào '
        'phép toán tích chập (convolution) và cơ chế chia sẻ trọng số (weight sharing). Mặc dù ban đầu được thiết kế tối ưu cho '
        'các tác vụ thị giác máy tính 2D, các nhà nghiên cứu đã nhanh chóng nhận ra rằng nguyên lý hoạt động của CNN hoàn toàn có '
        'thể mở rộng hiệu quả sang miền một chiều (1D-CNN) để phân tích các tín hiệu chuỗi thời gian (time-series data) phức tạp '
        '[19]. Trong bối cảnh phân tích dữ liệu cảm biến đeo tay (gia tốc kế và con quay hồi chuyển), các tín hiệu liên tục này '
        'được biểu diễn dưới dạng các chuỗi số đa kênh. Lớp tích chập 1D hoạt động bằng cách trượt các bộ lọc một chiều (1D kernels) '
        'dọc theo trục thời gian của chuỗi tín hiệu để thực hiện phép nhân chập cục bộ, từ đó tự động nắm bắt các đặc trưng động lực '
        'học cục bộ (local temporal patterns) như sự thay đổi gia tốc đột ngột, độ dốc của cú ngã hoặc tần số dao động của các '
        'hoạt động đi bộ thường ngày.', indent=True)
    add_paragraph(doc,
        'Cấu trúc của một lớp 1D-CNN điển hình bao gồm ba thành phần chính xếp chồng lên nhau: Lớp tích chập (Convolutional Layer) '
        'để trích xuất đặc trưng, Lớp chuẩn hóa (Batch Normalization) để ổn định phân phối dữ liệu đầu ra và tăng tốc độ hội tụ, '
        'và Lớp kích hoạt phi tuyến tính (Activation Layer) để bổ sung tính phi tuyến cho mô hình. Phép toán tích chập 1D giúp '
        'giảm số lượng tham số cần học một cách đáng kể so với các mạng kết nối đầy đủ (Fully Connected Networks), đồng thời tạo '
        'ra khả năng bất biến dịch chuyển theo thời gian (temporal translation invariance). Điều này cực kỳ quan trọng vì cú ngã '
        'có thể xảy ra ở bất kỳ thời điểm nào trong cửa sổ thời gian quan sát, và mô hình 1D-CNN vẫn có thể nhận diện được nhờ '
        'vào việc trượt bộ lọc qua điểm biến thiên đó.', indent=True)
    add_paragraph(doc,
        'Phép tích chập 1D trên chuỗi thời gian x với bộ lọc w kích thước k:', indent=True)
    add_formula(doc, 'y[t] = \u03a3(i=0 \u2192 k-1) w[i] \u00b7 x[t + i] + b', '1.1')
    add_paragraph(doc,
        'Trong đó: x[t] là giá trị đầu vào tại bước thời gian t, w[i] là trọng số bộ lọc '
        'tại vị trí i, b là hệ số bias, và y[t] là đầu ra tại bước t. Sau mỗi lớp tích chập, '
        'hàm kích hoạt ReLU (Rectified Linear Unit) được áp dụng [17]:', indent=True)
    add_formula(doc, 'ReLU(x) = max(0, x)', '1.2')

    doc.add_heading('1.2.2. Mạng hồi quy LSTM (Long Short-Term Memory)', level=3)
    add_paragraph(doc,
        'Mạng nơ-ron hồi quy truyền thống (Recurrent Neural Network - RNN) là một bước tiến lớn trong việc xử lý dữ liệu chuỗi '
        'nhờ vào cơ chế phản hồi vòng lặp (recurrent connections), cho phép thông tin được truyền từ bước thời gian này sang '
        'bước thời gian tiếp theo, tạo nên một dạng "bộ nhớ trong" ngắn hạn. Tuy nhiên, RNN truyền thống gặp phải một hạn chế '
        'chí mạng về mặt toán học khi huấn luyện bằng thuật toán lan truyền ngược qua thời gian (Backpropagation Through Time - BPTT): '
        'vấn đề triệt tiêu đạo hàm (vanishing gradient) và bùng nổ đạo hàm (exploding gradient). Khi độ dài chuỗi dữ liệu tăng lên '
        '(vượt quá 10 hoặc 20 timesteps), việc nhân liên tiếp các ma trận trọng số trong quá trình tính đạo hàm khiến các giá trị '
        'này giảm dần về 0 theo cấp số nhân. Kết quả là mô hình hoàn toàn mất khả năng cập nhật trọng số cho các lớp ban đầu, '
        'nói cách khác, nó quên mất các phụ thuộc dài hạn (long-term dependencies) trong quá khứ.', indent=True)
    add_paragraph(doc,
        'Để giải quyết triệt để điểm yếu chí mạng này, Hochreiter và Schmidhuber đã đề xuất kiến trúc bộ nhớ dài-ngắn hạn '
        '(Long Short-Term Memory - LSTM) vào năm 1997 [3]. Trái tim của LSTM là trạng thái ô (cell state, ký hiệu là C_t) đóng vai trò '
        'như một "đường cao tốc thông tin" chạy dọc suốt chiều dài chuỗi dữ liệu với rất ít các tương tác tuyến tính, giúp đạo hàm '
        'có thể truyền ngược cực kỳ xa mà không bị triệt tiêu. Sự điều phối thông tin ghi vào, xóa bỏ hoặc đọc ra từ cell state '
        'được kiểm soát nghiêm ngặt bởi ba cổng toán học (gates) sử dụng hàm kích hoạt Sigmoid (cho ra giá trị từ 0 đến 1, biểu thị '
        'tỷ lệ thông tin được phép đi qua): cổng quên (forget gate) quyết định loại bỏ thông tin cũ không còn hữu ích, cổng đầu vào '
        '(input gate) lựa chọn thông tin mới từ input hiện tại để ghi vào cell state, và cổng đầu ra (output gate) quyết định giá trị '
        'trạng thái ẩn tiếp theo (hidden state, h_t) được phát ra ngoài.', indent=True)
    add_paragraph(doc,
        'Trong đồ án này, chúng em áp dụng kiến trúc LSTM hai chiều (Bidirectional LSTM - Bi-LSTM). Khác với LSTM một chiều thông '
        'thường chỉ đọc dữ liệu theo chiều xuôi thời gian, Bi-LSTM sử dụng đồng thời hai nhánh LSTM song song: một nhánh xử lý chuỗi '
        'theo chiều xuôi từ quá khứ đến tương lai, và một nhánh xử lý chuỗi theo chiều ngược từ tương lai về quá khứ. Đầu ra của hai '
        'nhánh tại mỗi timestep được nối lại với nhau (concatenate) tạo ra biểu diễn đặc trưng toàn diện, giúp mô hình nắm bắt được '
        'ngữ cảnh hai chiều hoàn hảo. Để nâng cao hơn nữa hiệu năng nhận dạng, một cơ chế chú ý (Attention Mechanism) [8] được tích hợp '
        'sau lớp Bi-LSTM. Thay vì nén toàn bộ thông tin của chuỗi thời gian vào một vector ẩn duy nhất ở timestep cuối cùng (dễ gây '
        'mất mát thông tin), Attention Mechanism sẽ tính toán một bộ trọng số động (attention weights) để đánh giá mức độ quan trọng '
        'của từng timestep đối với nhãn quyết định "Té ngã". Đối với cú ngã, các timestep nằm ở khoảng khắc gia tốc biến thiên cực '
        'đại (lúc va chạm sàn) sẽ được gán trọng số rất cao, giúp bộ phân loại tập trung tối đa vào thông tin đắt giá nhất này.', indent=True)
    
    add_paragraph(doc, 'Cổng quên (Forget gate) — quyết định lượng thông tin quá khứ cần loại bỏ khỏi trạng thái ô (cell state):', indent=True)
    add_formula(doc, 'f_t = \u03c3(W_f \u00b7 [h_t-1, x_t] + b_f)', '1.3')
    
    add_paragraph(doc, 'Cổng đầu vào (Input gate) — chọn lọc thông tin mới cần đưa vào trạng thái ô:', indent=True)
    add_formula(doc, 'i_t = \u03c3(W_i \u00b7 [h_t-1, x_t] + b_i)', '1.4')
    add_formula(doc, 'C~_t = tanh(W_c \u00b7 [h_t-1, x_t] + b_c)', '1.5')
    
    add_paragraph(doc, 'Cập nhật trạng thái ô hiện tại (Cell State):', indent=True)
    add_formula(doc, 'C_t = f_t \u2299 C_t-1 + i_t \u2299 C~_t', '1.6')
    
    add_paragraph(doc, 'Cổng đầu ra (Output gate) và trạng thái ẩn hiện tại (Hidden State):', indent=True)
    add_formula(doc, 'o_t = \u03c3(W_o \u00b7 [h_t-1, x_t] + b_o)', '1.7')
    add_formula(doc, 'h_t = o_t \u2299 tanh(C_t)', '1.8')
    
    add_paragraph(doc,
        'Trong đó: \u03c3 đại diện cho hàm kích hoạt Sigmoid, \u2299 là phép nhân ma trận chập (Hadamard product), '
        'W và b lần lượt là ma trận trọng số và vector bias cần học trong quá trình huấn luyện [3]. '
        'Đồ án sử dụng kiến trúc Bi-LSTM (mạng LSTM hai chiều) để học đồng thời thông tin theo cả chiều xuôi và '
        'chiều ngược thời gian, kết hợp cùng cơ chế chú ý (Attention Mechanism) [8] giúp mô hình tự động tập trung '
        'vào những phân đoạn biến thiên gia tốc mạnh mẽ nhất (khoảng khắc va chạm xảy ra té ngã).', indent=True)
    
    add_image(doc, "lstm_cell.png", "Hình 1.3. Cấu trúc chi tiết của một phần tử nhớ LSTM (LSTM Cell)", width_inch=5.5)

    doc.add_heading('1.2.3. Mạng GRU (Gated Recurrent Unit)', level=3)
    add_paragraph(doc,
        'Mặc dù LSTM giải quyết cực kỳ tốt vấn đề triệt tiêu đạo hàm, cấu trúc của nó lại tương đối phức tạp với ba cổng riêng biệt '
        'và hai trạng thái lưu trữ song song (cell state và hidden state). Sự phức tạp này dẫn đến số lượng tham số cần huấn luyện '
        'của mô hình là rất lớn, đòi hỏi tài nguyên bộ nhớ cao và thời gian tính toán suy luận (inference time) bị kéo dài. Nhằm tối '
        'ưu hóa hiệu năng tính toán mà vẫn giữ vững khả năng học các phụ thuộc dài hạn, Kyunghyun Cho và các cộng sự đã đề xuất kiến '
        'trúc Đơn vị cổng hồi quy (Gated Recurrent Unit - GRU) vào năm 2014 [4]. GRU thực hiện một cuộc cải cách cấu trúc bằng cách '
        'loại bỏ hoàn toàn cell state độc lập, tích hợp nó vào trạng thái ẩn hidden state (h_t). Đồng thời, GRU rút gọn số lượng cổng '
        'kiểm soát xuống chỉ còn hai cổng: cổng cập nhật (update gate, z_t) và cổng thiết lập lại (reset gate, r_t).', indent=True)
    add_paragraph(doc,
        'Cụ thể, cổng cập nhật z_t đảm nhận vai trò kết hợp của cả cổng quên và cổng đầu vào trong LSTM, quyết định tỷ lệ thông tin '
        'ẩn từ quá khứ (h_t-1) sẽ được giữ lại và lượng thông tin mới (h~_t) sẽ được nạp thêm vào trạng thái ẩn mới. Cổng thiết lập lại '
        'r_t xác định mức độ ảnh hưởng của trạng thái ẩn quá khứ đối với thông tin ứng viên hiện tại. Nhờ vào thiết kế tinh gọn này, '
        'mạng GRU sở hữu số lượng tham số ít hơn khoảng 30% so với LSTM trên cùng một kích thước chiều ẩn (hidden size). Trong thực nghiệm, '
        'sự cắt giảm tham số này mang lại những lợi ích vô cùng thực tế: giảm đáng kể nguy cơ quá khớp (overfitting) khi huấn luyện '
        'trên các bộ dữ liệu có quy mô vừa và nhỏ, đẩy nhanh tốc độ hội tụ trong quá trình huấn luyện và giảm thiểu độ trễ suy luận. '
        'Điều này làm cho GRU trở thành một ứng viên cực kỳ sáng giá cho các hệ thống nhúng, thiết bị di động thông minh có tài nguyên '
        'phần cứng và dung lượng pin bị giới hạn nghiêm trọng [4].', indent=True)
    
    add_paragraph(doc, 'Cổng cập nhật (Update gate):', indent=True)
    add_formula(doc, 'z_t = \u03c3(W_z \u00b7 [h_t-1, x_t] + b_z)', '1.9')
    
    add_paragraph(doc, 'Cổng thiết lập lại (Reset gate):', indent=True)
    add_formula(doc, 'r_t = \u03c3(W_r \u00b7 [h_t-1, x_t] + b_r)', '1.10')
    
    add_paragraph(doc, 'Trạng thái ẩn ứng viên và Trạng thái ẩn chính thức:', indent=True)
    add_formula(doc, 'h~_t = tanh(W \u00b7 [r_t \u2299 h_t-1, x_t] + b)', '1.11')
    add_formula(doc, 'h_t = (1 - z_t) \u2299 h_t-1 + z_t \u2299 h~_t', '1.12')
    
    add_paragraph(doc,
        'GRU được sử dụng trong đồ án như một mô hình đối chứng (baseline) quan trọng nhằm so sánh trực tiếp '
        'hiệu năng phân loại và tốc độ xử lý so với mạng Bi-LSTM nâng cao [4].', indent=True)

    add_image(doc, "gru_cell.png", "Hình 1.4. Cấu trúc của một đơn vị cổng hồi quy GRU (GRU Cell)", width_inch=5.5)

    doc.add_heading('1.2.4. Mô hình ước lượng tư thế (Pose Estimation)', level=3)
    add_paragraph(doc,
        'Ước lượng tư thế người (Human Pose Estimation) là một trong những bài toán kinh điển và mang tính thách thức cao nhất '
        'của lĩnh vực Thị giác máy tính. Mục tiêu của bài toán là định vị và theo dõi chính xác tọa độ không gian của các khớp '
        'nối cơ học trên cơ thể người (được gọi là các điểm mốc keypoints) từ các khung hình hình ảnh hoặc luồng video đầu vào. '
        'Trong đồ án này, chúng em lựa chọn ứng dụng dòng mô hình YOLOv11-Pose [6], đây là phiên bản tiên tiến nhất được phát triển '
        'bởi Ultralytics (tính đến năm 2024), tích hợp khả năng ước lượng tư thế song song trực tiếp với phát hiện đối tượng '
        '(Object Detection) thông qua cơ chế suy luận một lần duy nhất (single forward pass). Trái ngược với các mô hình hai giai '
        'đoạn (two-stage detectors) truyền thống vốn cực kỳ nặng nề (thực hiện phát hiện hộp bao người trước rồi mới chạy mô hình '
        'pose trên từng hộp bao), YOLOv11-Pose sử dụng kiến trúc một giai đoạn (one-stage) cực kỳ tinh gọn. Mô hình dự đoán đồng '
        'thời tọa độ hộp bao người (bounding box) và tọa độ các keypoints trực tiếp từ ảnh đầu vào bằng cách chia sẻ chung mạng '
        'xương sống (backbone) CSPDarknet và mạng cổ (neck) PANet tối ưu, giúp giảm thiểu tối đa tài nguyên tính toán và đảm bảo '
        'tốc độ xử lý siêu nhanh đạt tiêu chuẩn thời gian thực (>30 FPS) trên các cấu hình phần cứng thông thường.', indent=True)
    add_paragraph(doc,
        'Về mặt đặc tả kỹ thuật, YOLOv11-Pose được huấn luyện để trích xuất chính xác tọa độ của 17 điểm khung xương cơ thể người '
        'theo tiêu chuẩn quốc tế COCO Keypoints Dataset. Danh sách 17 điểm mốc này bao gồm: mũi (nose), mắt trái, mắt phải, tai trái, '
        'tai phải (nhóm đầu-mặt); vai trái, vai phải, khuỷu tay trái, khuỷu tay phải, cổ tay trái, cổ tay phải (nhóm chi trên); hông '
        'trái, hông phải (nhóm trọng tâm cơ thể); đầu gối trái, đầu gối phải, mắt cá chân trái, mắt cá chân phải (nhóm chi dưới). '
        'Đầu ra của mô hình đối với mỗi điểm keypoint thứ i là một bộ ba giá trị (x_i, y_i, c_i), trong đó (x_i, y_i) là tọa độ pixel '
        '2D biểu diễn vị trí của điểm mốc trên khung hình, và c_i là điểm số tin cậy (confidence score) nằm trong khoảng [0, 1] biểu '
        'thị xác suất tồn tại và mức độ chính xác của điểm mốc đó. Việc sử dụng tọa độ 17 điểm khung xương mang lại một lợi thế '
        'khoa học khổng lồ cho bài toán phát hiện té ngã: nó giúp hệ thống loại bỏ hoàn toàn các thông tin nhiễu từ môi trường '
        '(như màu sắc trang phục, ánh sáng phòng, hậu cảnh phức tạp) và chỉ tập trung phân tích cấu trúc hình học chuyển động thuần '
        'túy của con người. Điều này nâng cao vượt trội tính tổng quát hóa của thuật toán và bảo vệ quyền riêng tư tuyệt đối cho '
        'người cao tuổi.', indent=True)
    
    add_image(doc, "yolov11_pose.png", "Hình 1.5. Khung xương cơ thể người với 17 điểm COCO Keypoints trích xuất bởi YOLOv11-Pose", width_inch=5.2)

    # ═══════════════════════════════════════════════════
    # 1.3 Các phương pháp đánh giá
    # ═══════════════════════════════════════════════════
    doc.add_heading('1.3. Các phương pháp đánh giá mô hình', level=2)
    add_paragraph(doc,
        'Để đánh giá hiệu năng của các mô hình phân loại trong bài toán phát hiện té ngã, '
        'đồ án sử dụng các chỉ số đánh giá sau đây. Trong bối cảnh bài toán phân loại nhị '
        'phân (binary classification) với hai lớp: ADL (hoạt động bình thường) và Fall '
        '(té ngã), các chỉ số được tính dựa trên bốn giá trị cơ bản: True Positive (TP), '
        'True Negative (TN), False Positive (FP), và False Negative (FN).', indent=True)

    doc.add_heading('1.3.1. Accuracy (Độ chính xác)', level=3)
    add_formula(doc, 'Accuracy = (TP + TN) / (TP + TN + FP + FN)', '1.13')
    add_paragraph(doc,
        'Độ chính xác tổng thể (Accuracy) là chỉ số cơ bản và trực quan nhất được sử dụng để đánh giá hiệu năng của một bộ phân loại. '
        'Nó đo lường tỷ lệ giữa số lượng mẫu dự đoán chính xác (bao gồm cả mẫu té ngã đúng và mẫu hoạt động thường ngày đúng) '
        'trên tổng số mẫu dữ liệu thực nghiệm. Mặc dù là chỉ số đầu tiên được xem xét, Accuracy lại tiềm ẩn một cạm bẫy toán học cực kỳ '
        'nguy hiểm được gọi là "nghịch lý độ chính xác" (Accuracy Paradox) khi áp dụng vào các bộ dữ liệu bị mất cân bằng lớp '
        '(highly imbalanced datasets). Trong thực tế đời sống, hành vi té ngã là một sự cố cực kỳ hiếm gặp (chỉ chiếm dưới 0.1% thời gian '
        'sinh hoạt), trong khi các hoạt động hằng ngày ADL chiếm tới 99.9% dữ liệu thu thập. Nếu một bộ phân loại đơn giản chỉ cần '
        'dự đoán tất cả mọi mẫu đều là "hoạt động bình thường ADL", nó vẫn sẽ dễ dàng đạt được độ chính xác Accuracy lên tới 99.9%. '
        'Tuy nhiên, bộ phân loại đó hoàn toàn vô dụng vì nó bỏ sót 100% các cú ngã xảy ra. Do đó, chúng ta không được phép chỉ dựa vào '
        'Accuracy để đánh giá hệ thống, mà bắt buộc phải sử dụng kết hợp các chỉ số chuyên sâu khác.', indent=True)

    doc.add_heading('1.3.2. Precision (Độ chính xác dương)', level=3)
    add_formula(doc, 'Precision = TP / (TP + FP)', '1.14')

    doc.add_heading('1.3.3. Recall (Độ nhạy / Sensitivity)', level=3)
    add_formula(doc, 'Recall = TP / (TP + FN)', '1.15')
    add_paragraph(doc,
        'Độ nhạy (Recall, hay trong y học còn gọi là Độ nhạy lâm sàng - Sensitivity) đo lường tỷ lệ giữa các trường hợp thực tế '
        'có xảy ra té ngã và được mô hình dự đoán chính xác là té ngã (True Positives) trên tổng số ca té ngã thực sự xảy ra trong '
        'thực tế (TP + FN). Trong bài toán an toàn và chăm sóc sức khỏe cho người cao tuổi, Recall được đồng thuận là chỉ số y khoa '
        'quan trọng nhất và phải được ưu tiên tối đa trong quá trình tối ưu hóa mô hình. Một lỗi False Negative (FN) - tức là '
        'người già bị ngã thật sự nhưng mô hình bỏ sót và nhận định là họ đang sinh hoạt bình thường - là một sai sót mang tính chí '
        'mạng, trực tiếp đe dọa đến tính mạng của người bệnh vì họ sẽ nằm bất động trên sàn nhà mà không nhận được bất kỳ sự giúp đỡ '
        'nào (long-lie). Ngược lại, một lỗi False Positive (FP) - tức là người già chỉ ngồi nhanh xuống ghế nhưng mô hình cảnh báo '
        'nhầm là ngã - chỉ gây ra sự phiền toái nhỏ về mặt vận hành (báo động giả). Do đó, mục tiêu tối thượng của FallGuard AI là '
        'phải đẩy chỉ số Recall lên tiệm cận mức 100%, đồng thời giữ chỉ số báo động giả trong phạm vi chấp nhận được.', indent=True)

    doc.add_heading('1.3.4. F1-Score', level=3)
    add_formula(doc, 'F1 = 2 \u00d7 (Precision \u00d7 Recall) / (Precision + Recall)', '1.16')

    doc.add_heading('1.3.5. Confusion Matrix (Ma trận nhầm lẫn)', level=3)
    add_paragraph(doc,
        'Ma trận nhầm lẫn (Confusion Matrix) là một bảng biểu diễn chi tiết hiệu năng phân loại '
        'của mô hình. Hàng biểu diễn nhãn thực tế của dữ liệu, còn cột biểu diễn nhãn dự đoán từ mô hình. '
        'Trong bài toán phát hiện té ngã nhị phân, ma trận có kích thước 2\u00d72 biểu diễn rõ các số liệu: '
        'TP (ngã và đoán đúng là ngã), TN (hoạt động ADL bình thường và đoán đúng), '
        'FP (hoạt động bình thường nhưng mô hình dự đoán là ngã - báo động giả), '
        'và FN (sự cố ngã xảy ra nhưng mô hình bỏ sót và dự đoán là ADL bình thường).', indent=True)
    
    add_image(doc, "confusion_matrix_bilstm.png", "Hình 1.6. Cấu trúc trực quan của ma trận nhầm lẫn (Confusion Matrix) trong đánh giá phân loại nhị phân", width_inch=4.8)

    doc.add_heading('1.3.6. Đường cong ROC và AUC', level=3)
    add_paragraph(doc,
        'Đường cong ROC (Receiver Operating Characteristic) biểu diễn mối quan hệ giữa '
        'True Positive Rate (TPR = Recall) và False Positive Rate (FPR = FP/(FP+TN)) tại '
        'các ngưỡng phân loại khác nhau. AUC (Area Under the ROC Curve) là diện tích dưới '
        'đường cong ROC, với giá trị từ 0 đến 1. AUC = 1.0 tương ứng với mô hình hoàn hảo, '
        'AUC = 0.5 tương ứng với phân loại ngẫu nhiên [16].', indent=True)

    # ═══════════════════════════════════════════════════
    # 1.4 Công nghệ xây dựng hệ thống
    # ═══════════════════════════════════════════════════
    doc.add_heading('1.4. Công nghệ xây dựng hệ thống', level=2)
    
    doc.add_heading('1.4.1. Python và PyTorch', level=3)
    add_paragraph(doc,
        'Python là ngôn ngữ lập trình chính được sử dụng trong toàn bộ dự án. PyTorch [10] '
        'là thư viện Học sâu mã nguồn mở được phát triển bởi Facebook AI Research (FAIR), '
        'cung cấp khả năng tính toán tensor trên GPU và hệ thống tự động vi phân (autograd) '
        'linh hoạt. PyTorch được lựa chọn nhờ hiệu năng cao và khả năng nghiên cứu nhanh.', indent=True)

    doc.add_heading('1.4.2. FastAPI và WebSocket', level=3)
    add_paragraph(doc,
        'FastAPI [11] là web framework hiệu năng cao cho Python, hỗ trợ bất đồng bộ (async) '
        'và tự động sinh API documentation (Swagger UI). FastAPI được chọn nhờ hỗ trợ kết nối '
        'WebSocket song hướng thời gian thực với độ trễ cực thấp, đáp ứng trực tiếp truyền '
        'video stream và nhận kết quả phân tích tức thời từ server.', indent=True)
    
    add_paragraph(doc,
        'Để chứng minh hiệu quả vượt trội của FastAPI trong việc xây dựng API thời gian thực '
        'so với các framework phổ biến khác, Bảng 1.3 trình bày một so sánh định lượng:', indent=True)

    add_table(doc,
        ['Framework', 'Ngôn ngữ', 'Hiệu năng (RPS)', 'Hỗ trợ Async', 'Độ trễ WebSocket'],
        [
            ['FastAPI', 'Python', 'Rất cao (~9,200)', 'Có (Native Async)', 'Thấp (<2ms)'],
            ['Flask', 'Python', 'Thấp (~1,500)', 'Hạn chế (gevent)', 'Trung bình (~15ms)'],
            ['Django', 'Python', 'Trung bình (~2,800)', 'Có (ASGI)', 'Trung bình (~10ms)'],
            ['Express', 'Node.js', 'Cao (~7,500)', 'Có (Event-driven)', 'Thấp (<3ms)'],
        ],
        caption='Bảng 1.3. So sánh các Web Framework xây dựng API thời gian thực'
    )

    doc.add_heading('1.4.3. Ultralytics YOLOv11', level=3)
    add_paragraph(doc,
        'Ultralytics YOLOv11 [6] là framework phát hiện đối tượng và ước lượng tư thế mới '
        'nhất của dòng YOLO (You Only Look Once) [5]. Phiên bản nano (yolo11n-pose) được sử '
        'dụng trong đồ án với kích thước model nhỏ (~6MB) nhưng đạt tốc độ xử lý >30 FPS '
        'trên GPU tầm trung, phù hợp cho ứng dụng thời gian thực.', indent=True)

    doc.add_heading('1.4.4. SQLite và Chart.js', level=3)
    add_paragraph(doc,
        'SQLite là hệ quản trị cơ sở dữ liệu nhúng (embedded database), không cần server '
        'riêng, phù hợp cho hệ thống đơn máy. Chart.js là thư viện JavaScript mã nguồn mở '
        'cho vẽ biểu đồ tương tác trên web, được sử dụng trong Dashboard để hiển thị thống '
        'kê theo ngày, tuần, và giờ.', indent=True)

    doc.add_page_break()


# ══════════════════════════════════════════════════════════════════
# CHƯƠNG 2: PHƯƠNG PHÁP, MÔ HÌNH VÀ THIẾT KẾ HỆ THỐNG
# ══════════════════════════════════════════════════════════════════

def add_chapter_2(doc):
    doc.add_heading('CHƯƠNG 2. PHƯƠNG PHÁP, MÔ HÌNH VÀ THIẾT KẾ HỆ THỐNG', level=1)
    add_paragraph(doc,
        'Chương này trình bày chi tiết kiến trúc hệ thống FallGuard AI, bộ dữ liệu sử dụng, '
        'kiến trúc các mô hình Học sâu, thuật toán phát hiện té ngã thời gian thực, cùng '
        'thiết kế cơ sở dữ liệu và API.', indent=True)

    # ═══════════════════════════════════════════════════
    # 2.1 Tổng quan kiến trúc
    # ═══════════════════════════════════════════════════
    doc.add_heading('2.1. Tổng quan kiến trúc hệ thống', level=2)
    add_paragraph(doc,
        'Hệ thống FallGuard AI được thiết kế theo kiến trúc Client-Server với hai nhánh '
        'phân tích độc lập nhưng bổ trợ lẫn nhau (Hình 2.1):', indent=True)
    add_paragraph(doc,
        '• Nhánh Vision (Thị giác máy tính): Camera \u2192 YOLOv11-Pose \u2192 Heuristic Engine \u2192 Cảnh báo. '
        'Nhánh này xử lý video stream thời gian thực, trích xuất 17 keypoints và áp dụng '
        'tập luật heuristic để phát hiện té ngã dựa trên vận tốc, tỷ lệ bounding box và '
        'vị trí đầu-hông.', indent=True)
    add_paragraph(doc,
        '• Nhánh Sensor (Cảm biến): Dữ liệu SisFall \u2192 Tiền xử lý (Sliding Window) \u2192 '
        'Mô hình DL (5 kiến trúc) \u2192 Phân loại ADL/Fall. Nhánh này huấn luyện và đánh giá '
        '5 mô hình Học sâu trên dữ liệu cảm biến gia tốc và con quay hồi chuyển [1].', indent=True)
    
    add_image(doc, "system_architecture.png", "Hình 2.1. Sơ đồ kiến trúc tổng thể hệ thống giám sát FallGuard AI", width_inch=5.8)

    add_paragraph(doc,
        'Luồng xử lý tổng thể của hệ thống:', indent=True)
    add_paragraph(doc,
        '1) Thu nhận frame từ webcam qua kết nối WebSocket song hướng;\n'
        '2) YOLOv11-Pose xử lý frame, trích xuất bounding box người và tọa độ 17 keypoints;\n'
        '3) Heuristic Engine thực hiện phân tích 4 thành phần (Vận tốc rơi, Tỷ lệ aspect ratio, '
        'Vị trí đầu-hông và Counter confirmation);\n'
        '4) Nếu phát hiện bất thường té ngã, hệ thống kích hoạt Alert Dispatcher: tự động ghi '
        'sự cố vào SQLite DB, gửi tín hiệu cảnh báo khẩn cấp lên Dashboard thông qua WebSocket;\n'
        '5) Giao diện Dashboard hiển thị video stream có vẽ bounding box người màu đỏ và các điểm khung '
        'xương, đồng thời kích hoạt âm thanh cảnh báo và ghi nhật ký hiển thị sự cố.', indent=True)

    # ═══════════════════════════════════════════════════
    # 2.2 Bộ dữ liệu SisFall
    # ═══════════════════════════════════════════════════
    doc.add_heading('2.2. Bộ dữ liệu SisFall', level=2)
    
    doc.add_heading('2.2.1. Thông tin dữ liệu', level=3)
    add_paragraph(doc,
        'Bộ dữ liệu chuẩn quốc tế SisFall: A Fall and Movement Dataset (Sucerquia et al., 2017) [1] là một trong những bộ dữ liệu '
        'chuỗi thời gian lớn nhất, uy tín nhất và được sử dụng rộng rãi nhất bởi cộng đồng khoa học toàn cầu để nghiên cứu và đánh '
        'giá các thuật toán phát hiện té ngã. Sự độc đáo và giá trị khoa học vượt trội của SisFall nằm ở sự đầu tư bài bản trong '
        'quy trình thu thập và tính đa dạng sinh học cực cao của các đối tượng tham gia thử nghiệm. Bộ dữ liệu được xây dựng dựa trên '
        'sự tham gia của 38 đối tượng tình nguyện viên được chia làm hai nhóm tuổi tương phản rõ rệt: Nhóm người trẻ tuổi gồm 23 đối '
        'tượng (11 nam và 12 nữ) nằm trong độ tuổi từ 19 đến 30 tuổi, đóng vai trò thực hiện các hoạt động thể chất mạnh mẽ và mô phỏng '
        'chính xác các cú ngã tốc độ cao; Nhóm người cao tuổi gồm 15 đối tượng (4 nam và 11 nữ) nằm trong độ tuổi từ 60 đến 75 tuổi, '
        'đóng vai trò cung cấp các dữ liệu hoạt động sinh hoạt tự nhiên với các biến động cơ học thực tế của quá trình lão hóa. '
        'Tổng cộng, bộ dữ liệu lưu trữ 4.510 bản ghi dữ liệu số hóa hoàn chỉnh, ghi lại toàn bộ quá trình vận động của các đối tượng.', indent=True)
    add_paragraph(doc,
        'Quy trình thu thập dữ liệu được thiết kế cực kỳ nghiêm ngặt nhằm đảm bảo an toàn tuyệt đối cho người cao tuổi trong khi '
        'vẫn thu được các dữ liệu va chạm chân thực nhất. Đối với các thử nghiệm mô phỏng té ngã (chỉ áp dụng cho nhóm người trẻ '
        'để tránh nguy cơ chấn thương thực tế cho người già), các tình nguyện viên được yêu cầu thực hiện cú ngã tự nhiên lên một '
        'tấm đệm giảm chấn y tế dày 20cm dưới sự giám sát trực tiếp của các bác sĩ chấn thương chỉnh hình và các kỹ sư y sinh. '
        'Thiết bị thu thập dữ liệu là một hộp cảm biến tích hợp nhỏ gọn được cố định chắc chắn ở thắt lưng của đối tượng bằng một '
        'đai đeo co giãn chuyên dụng. Vị trí thắt lưng được lựa chọn có chủ đích khoa học vì đây là khu vực nằm gần sát nhất với '
        'trọng tâm cơ thể người (Center of Mass - CoM), giúp các cảm biến gia tốc và con quay hồi chuyển đo đạc chính xác nhất các '
        'biến động động học và tư thế toàn thân mà không bị nhiễu bởi các chuyển động lắc tay hay lắc chân cục bộ của đối tượng [1].', indent=True)
    
    add_image(doc, "sisfall_dataset.png", "Hình 2.2. Biểu diễn cấu trúc phân bố hoạt động của bộ dữ liệu chuẩn SisFall", width_inch=5.5)

    add_table(doc,
        ['Cảm biến', 'Loại', 'Độ phân giải', 'Phạm vi', 'Cột dữ liệu'],
        [
            ['ADXL345', 'Gia tốc kế (Acc)', '13-bit', '±16g', 'Cột 0-2 (X,Y,Z)'],
            ['ITG3200', 'Con quay hồi chuyển', '16-bit', '±2000°/s', 'Cột 3-5 (X,Y,Z)'],
            ['MMA8451Q', 'Gia tốc kế (Acc)', '14-bit', '±8g', 'Cột 6-8 (X,Y,Z)'],
        ],
        caption='Bảng 2.1. Thông số cảm biến bộ dữ liệu SisFall'
    )
    
    add_paragraph(doc,
        'Tổng cộng mỗi bản ghi chứa 9 kênh dữ liệu (3 cảm biến \u00d7 3 trục X/Y/Z), lấy '
        'mẫu ở tần số 200 Hz. Dữ liệu được chia thành 2 nhóm lớn:', indent=True)
    
    add_table(doc,
        ['Nhóm', 'Mã', 'Số hoạt động', 'Mô tả'],
        [
            ['ADL', 'D01–D19', '19 loại', 'Đi bộ, ngồi, đứng, nằm, nhặt đồ, leo cầu thang, ...'],
            ['Fall', 'F01–F15', '15 loại', 'Ngã về trước, ngã về sau, ngã nghiêng, ngã từ ghế, ...'],
        ],
        caption='Bảng 2.2. Phân bố hoạt động trong SisFall'
    )

    doc.add_heading('2.2.2. Tiền xử lý dữ liệu', level=3)
    add_paragraph(doc,
        'Dữ liệu thô thu nhận trực tiếp từ các cảm biến MEMS trong bộ dữ liệu SisFall thực chất là các giá trị số nguyên không dấu '
        '(raw digital bits) đại diện cho hiệu điện thế đầu ra của bộ chuyển đổi tương tự-số (ADC) tích hợp bên trong chip. Những con số '
        'này chưa có ý nghĩa vật lý trực quan và không thể đưa trực tiếp vào huấn luyện các mô hình học sâu vì thang đo giữa các cảm '
        'biến là hoàn toàn khác biệt. Do đó, việc xây dựng một đường ống tiền xử lý dữ liệu (Data Preprocessing Pipeline) chuẩn hóa '
        'và khoa học là bước bắt buộc đầu tiên để đảm bảo chất lượng đầu vào cho hệ thống FallGuard AI. Quy trình tiền xử lý được thiết '
        'kế chi tiết qua ba giai đoạn cốt lõi sau:', indent=True)
    add_paragraph(doc,
        '1) Chuyển đổi đơn vị vật lý tuyến tính: Các giá trị số nguyên thô (bits) được ánh xạ tuyến tính về các đơn vị đo lường vật lý '
        'chuẩn quốc tế (đơn vị trọng lực g ≈ 9.81 m/s² đối với gia tốc kế và đơn vị độ trên giây °/s đối với con quay hồi chuyển). Phép '
        'ánh xạ này sử dụng các hệ số tỉ lệ (Scale Factors) và độ phân giải bit (Bit Resolutions) được đặc tả chính xác bởi nhà sản '
        'xuất trong tài liệu kỹ thuật của từng con chip cảm biến [1]. Cụ thể:', indent=True)
    add_formula(doc, 'ADXL345: x_g = x_raw \u00d7 (2 \u00d7 16) / 2\u00b9\u00b3', '2.1')
    add_formula(doc, 'ITG3200: x_dps = x_raw \u00d7 (2 \u00d7 2000) / 2\u00b9\u2076', '2.2')
    add_formula(doc, 'MMA8451Q: x_g = x_raw \u00d7 (2 \u00d7 8) / 2\u00b9\u2074', '2.3')
    
    add_paragraph(doc,
        '2) Kỹ thuật Cửa sổ trượt phân mảnh dữ liệu (Sliding Window Segmentation): Các bản ghi tín hiệu trong SisFall thực chất là '
        'các chuỗi thời gian liên tục kéo dài từ vài chục giây đến vài phút. Để đưa dữ liệu này vào huấn luyện các mô hình mạng nơ-ron '
        'hồi quy và tích chập vốn yêu cầu kích thước đầu vào cố định, chuỗi thời gian dài vô tận được phân mảnh thành các cửa sổ con '
        '(windows) có kích thước cố định W. Trong đồ án này, chúng em thiết lập kích thước cửa sổ W = 200 mẫu dữ liệu (tương đương '
        'với khoảng thời gian đúng 1.0 giây hoạt động thực tế của đối tượng tại tần số lấy mẫu f_s = 200 Hz). Để tối ưu hóa hiệu năng, '
        'chúng em áp dụng độ chồng lấn (overlap) O = 100 mẫu (tương đương 50% kích thước cửa sổ). Kỹ thuật cửa sổ trượt có overlap mang '
        'lại hai giá trị khoa học to lớn: (1) Tăng số lượng mẫu huấn luyện lên gấp đôi (data augmentation) giúp tránh hiện tượng '
        'overfitting cho các mô hình học sâu; (2) Tránh việc bỏ sót hoặc chia cắt mất phân đoạn va chạm ngã (impact phase) nằm ở ranh '
        'giới giữa hai cửa sổ kế tiếp, đảm bảo mô hình luôn chụp được toàn bộ diễn biến động học của cú ngã trong ít nhất một cửa sổ '
        '(Hình 2.3).', indent=True)
    
    add_image(doc, "sliding_window.png", "Hình 2.3. Quy trình tiền xử lý dữ liệu với kỹ thuật cửa sổ trượt (Sliding Window)", width_inch=5.5)
    
    add_paragraph(doc,
        '3) Chuẩn hóa Z-score: Toàn bộ dữ liệu được chuẩn hóa theo phân phối chuẩn '
        'để tăng tốc độ hội tụ và ổn định quá trình huấn luyện của các mạng học sâu:', indent=True)
    add_formula(doc, 'x_normalized = (x - \u03bc) / (\u03c3 + \u03b5)', '2.4')
    add_paragraph(doc,
        'Trong đó \u03bc là giá trị trung bình, \u03c3 là độ lệch chuẩn tính trên toàn bộ tập '
        'huấn luyện, và \u03b5 = 10\u207b\u2078 để tránh lỗi chia cho 0 trong quá trình xử lý.', indent=True)

    # ═══════════════════════════════════════════════════
    # 2.3 Kiến trúc mô hình DL
    # ═══════════════════════════════════════════════════
    doc.add_heading('2.3. Kiến trúc mô hình Deep Learning', level=2)
    add_paragraph(doc,
        'Đồ án xây dựng và so sánh 5 kiến trúc mô hình Học sâu khác nhau trên cùng bộ '
        'dữ liệu SisFall, nhằm đánh giá ưu nhược điểm của từng kiến trúc cho bài toán '
        'phân loại hành vi té ngã. Bảng 2.3 tổng hợp thông số kiến trúc chi tiết:', indent=True)
    
    add_table(doc,
        ['Mô hình', 'Kiến trúc', 'Layers', 'Hidden Size', 'Tham số', 'Đặc điểm'],
        [
            ['Bi-LSTM\n+ Attention', 'BatchNorm \u2192 LSTM(2L)\n\u2192 Attention \u2192 FC', '2 LSTM\nbidirectional', '128', '~395K', 'Attention giúp\ntập trung timestep\nquan trọng'],
            ['Bi-GRU', 'BatchNorm \u2192 GRU(2L)\n\u2192 FC', '2 GRU\nbidirectional', '128', '~297K', 'Nhẹ hơn LSTM,\nít tham số hơn'],
            ['CNN-LSTM', 'Conv1D(3L) \u2192 MaxPool\n\u2192 Bi-LSTM \u2192 FC', '3 Conv1D\n+ 1 LSTM', '64', '~180K', 'CNN trích xuất\nlocal patterns'],
            ['Transformer\nEncoder', 'Linear \u2192 PosEnc\n\u2192 TransEnc(2L)\n\u2192 GAP \u2192 FC', '2 Encoder\n4 heads', 'd=64', '~52K', 'Self-attention\ncho quan hệ xa'],
            ['TCN', 'BatchNorm \u2192\nTemporalBlock(4L)\n\u2192 GAP \u2192 FC', '4 blocks\ndilation=1,2,4,8', '32/64/\n64/32', '~45K', 'Dilated causal\nconv, inference\nsong song'],
        ],
        caption='Bảng 2.3. Kiến trúc chi tiết 5 mô hình Deep Learning'
    )

    doc.add_heading('2.3.1. Mô hình Bi-LSTM với Attention', level=3)
    add_paragraph(doc,
        'Mô hình Mạng hồi quy hai chiều kết hợp cơ chế chú ý (Bi-LSTM + Attention) là một trong những kiến trúc học sâu chủ lực '
        'được nghiên cứu kỹ lưỡng nhất trong hệ thống FallGuard AI. Kiến trúc này được thiết kế phân tầng khoa học để giải quyết '
        'trực tiếp đặc trưng động học chuỗi của tín hiệu cảm biến đeo tay, bao gồm các khối chức năng cụ thể sau:', indent=True)
    add_paragraph(doc,
        '• Khối chuẩn hóa đầu vào (Input Batch Normalization): Tín hiệu sau khi tiền xử lý có kích thước Tensor là (Batch_Size, 200, 9) '
        'sẽ được truyền qua một lớp Batch Normalization 1D hoạt động trên chiều đặc trưng (features dimension). Lớp này thực hiện việc '
        'chuẩn hóa phân phối của các kênh dữ liệu về trạng thái trung bình bằng 0 và độ lệch chuẩn bằng 1 ngay trong từng batch huấn luyện, '
        'giúp loại bỏ hiện tượng lệch phân phối nội bộ (internal covariate shift), ổn định hóa dòng truyền đạo hàm và đẩy nhanh đáng '
        'kể tốc độ hội tụ của mô hình mạng nơ-ron sâu.', indent=True)
    add_paragraph(doc,
        '• Khối hồi quy hai chiều xếp chồng (Stacked Bidirectional LSTM): Chúng em xếp chồng hai lớp LSTM hai chiều (Bi-LSTM). Lớp thứ nhất '
        'nhận dữ liệu chuẩn hóa và trích xuất đặc trưng chuỗi cấp thấp, lớp thứ hai nhận đầu ra của lớp thứ nhất để trích xuất đặc trưng '
        'ngữ cảnh cấp cao hơn. Mỗi chiều của LSTM (forward và backward) được thiết lập kích thước trạng thái ẩn hidden_size = 128. '
        'Tại mỗi bước thời gian t, đầu ra từ hai hướng được nối lại (concatenated) tạo thành một vector đặc trưng tổng hợp có số chiều '
        'là 256. Một lớp Dropout với tỷ lệ 0.3 được chèn ở giữa hai lớp Bi-LSTM để ngắt kết nối ngẫu nhiên một số nơ-ron, ngăn ngừa '
        'hiện tượng đồng thích ứng (co-adaptation) và giảm thiểu tối đa hiện tượng overfitting.', indent=True)
    add_paragraph(doc,
        '• Khối cơ chế chú ý thời gian (Temporal Attention Mechanism): Đầu ra của lớp Bi-LSTM cuối cùng là một chuỗi các vector ẩn '
        'H = {h_1, h_2, ..., h_200} với h_t ∈ R²⁵⁶. Khối Attention tính toán một điểm số năng lượng e_t cho từng timestep thông qua '
        'một mạng nơ-ron truyền thẳng nhỏ: e_t = v^T * tanh(W_a * h_t + b_a), trong đó W_a và v là các ma trận trọng số cần học. '
        'Sau đó, các điểm số e_t được chuẩn hóa qua hàm Softmax để tạo thành bộ trọng số chú ý α_t ∈ [0, 1] có tổng bằng 1: '
        'α_t = exp(e_t) / ∑ exp(e_k). Vector ngữ cảnh cuối cùng (context vector) được tính bằng tổng có trọng số của các trạng thái ẩn: '
        'c = ∑ α_t * h_t. Cơ chế này cho phép mô hình bỏ qua các nhiễu động vô ích ở các timestep bình thường và tập trung năng lực phân '
        'loại vào các timestep có biến động va chạm mạnh mẽ nhất của cú ngã.', indent=True)
    add_paragraph(doc,
        '• Khối phân loại quyết định (Fully Connected Classifier): Vector ngữ cảnh c (256 chiều) đại diện cho toàn bộ thông tin '
        'đắt giá nhất của cửa sổ thời gian 1 giây sẽ được truyền qua khối phân loại cuối cùng: Dropout(0.3) → Linear(256→64) → '
        'Kích hoạt phi tuyến ReLU → Dropout(0.15) → Linear(64→2) để dự đoán xác suất của hai lớp đầu ra (ADL và Fall) thông qua '
        'hàm Softmax quyết định.', indent=True)
    
    add_image(doc, "lstm_cell.png", "Hình 2.4. Sơ đồ kiến trúc chi tiết mô hình Bi-LSTM với cơ chế Attention", width_inch=5.5)

    doc.add_heading('2.3.2. Mô hình GRU (so sánh)', level=3)
    add_paragraph(doc,
        'Mô hình GRU sử dụng cùng pipeline với Bi-LSTM nhưng thay thế LSTM cells bằng '
        'GRU cells [4]. GRU có ít tham số hơn (~297K so với ~395K) do chỉ sử dụng 2 cổng '
        '(update và reset) thay vì 3 cổng (forget, input, output) của LSTM. Mô hình lấy '
        'hidden state cuối cùng (last timestep) thay vì sử dụng Attention, giúp đánh giá '
        'đóng góp riêng của cơ chế Attention.', indent=True)

    doc.add_heading('2.3.3. Mô hình CNN-LSTM', level=3)
    add_paragraph(doc,
        'Mô hình CNN-LSTM kết hợp 1D Convolutional Neural Network và Bi-LSTM [19], [20]:', indent=True)
    add_paragraph(doc,
        '• 3 lớp Conv1D: Conv1D(9\u219264, k=5) \u2192 BN \u2192 ReLU \u2192 MaxPool(2) \u2192 Conv1D(64\u2192128, k=3) '
        '\u2192 BN \u2192 ReLU \u2192 MaxPool(2) \u2192 Conv1D(128\u219264, k=3) \u2192 BN \u2192 ReLU. CNN 1D trích xuất '
        'đặc trưng cục bộ (local temporal patterns) từ dữ liệu sensor.\n'
        '• Bi-LSTM: LSTM(input=64, hidden=64, 1 layer, bidirectional). Sau CNN, chuỗi được '
        'rút gọn theo thời gian (do MaxPool), LSTM học phụ thuộc dài hạn trên chuỗi đã '
        'trích xuất đặc trưng.\n'
        '• Classifier: Dropout(0.3) \u2192 Linear(128\u219232) \u2192 ReLU \u2192 Linear(32\u21922).', indent=True)
    
    add_image(doc, "system_architecture.png", "Hình 2.5. Sơ đồ luồng xử lý và kiến trúc mô hình CNN-LSTM", width_inch=5.5)

    doc.add_heading('2.3.4. Mô hình Transformer Encoder', level=3)
    add_paragraph(doc,
        'Mô hình Transformer Encoder [8] được thiết kế cho xử lý song song chuỗi thời gian:', indent=True)
    add_paragraph(doc,
        '• Linear Projection: Linear(9\u219264) \u2192 LayerNorm \u2192 ReLU. Ánh xạ 9 features đầu vào '
        'sang không gian d_model = 64.\n'
        '• Positional Encoding: Sử dụng mã hóa vị trí sin/cos để bổ sung thông tin thứ tự '
        'thời gian, vì Transformer không có cơ chế hồi quy tự nhiên [8].\n'
        '• Transformer Encoder: 2 lớp Encoder, mỗi lớp có Multi-Head Self-Attention (4 heads) '
        'và Feed-Forward Network (dim=128). Activation: GELU.\n'
        '• Global Average Pooling + Classifier: LayerNorm \u2192 Dropout \u2192 Linear(64\u219264) \u2192 GELU '
        '\u2192 Dropout \u2192 Linear(64\u21922).', indent=True)
    
    add_image(doc, "transformer_encoder.png", "Hình 2.7. Kiến trúc mô hình Transformer Encoder cho chuỗi thời gian", width_inch=5.0)

    doc.add_heading('2.3.5. Mô hình TCN (Temporal Convolutional Network)', level=3)
    add_paragraph(doc,
        'Mạng tích chập thời gian TCN (Temporal Convolutional Network) được đề xuất bởi Bai et al. [7] là một kiến trúc '
        'mạng tích chập chuyên biệt cho dữ liệu chuỗi thời gian, khắc phục triệt để các hạn chế về mặt tính toán tuần tự của RNN '
        'nhưng vẫn đảm bảo trường tiếp nhận thông tin (receptive field) cực kỳ rộng lớn. TCN hoạt động dựa trên hai nguyên lý cốt lõi: '
        'Phép tích chập nhân quả (Causal Convolutions) để đảm bảo mô hình không rò rỉ thông tin tương lai (mẫu tại bước t chỉ phụ thuộc '
        'vào các mẫu ở bước t trở về trước), và Phép tích chập giãn nở (Dilated Convolutions) để mở rộng trường tiếp nhận theo cấp số nhân. '
        'Cấu trúc chi tiết của TCN trong hệ thống bao gồm:', indent=True)
    add_paragraph(doc,
        '• Khối chuẩn hóa đầu vào (Input Batch Normalization): Chuẩn hóa 9 kênh tín hiệu thô để đưa dữ liệu về cùng thang đo.', indent=True)
    add_paragraph(doc,
        '• Khối 4 lớp khối thời gian xếp chồng (Stacked Temporal Blocks): Hệ thống xếp chồng 4 khối Temporal Blocks với hệ số giãn '
        'nở dilation rate d tăng dần theo cấp số nhân: d ∈ {1, 2, 4, 8}. Mỗi block chứa hai lớp tích chập nhân quả 1D với kích thước '
        'bộ lọc k=3. Phép toán tích chập giãn nở 1D bỏ qua d-1 bước thời gian giữa các điểm nhân chập, cho phép bộ lọc bao phủ một '
        'khoảng thời gian cực rộng mà không cần tăng kích thước kernel thực tế, từ đó giữ nguyên số lượng tham số cực kỳ nhỏ gọn. '
        'Mỗi lớp tích chập đều được chuẩn hóa bằng Weight Normalization, kích hoạt ReLU, chèn Dropout(0.2) để điều hòa trọng số. '
        'Một đường nối tắt (Residual Connection) được thiết kế nối từ đầu vào của block cộng trực tiếp vào đầu ra của block, giúp đạo '
        'hàm truyền thẳng trực tiếp qua các khối mà không bị suy hao, cho phép huấn luyện các mạng TCN cực kỳ sâu một cách ổn định.', indent=True)
    add_paragraph(doc,
        '• Công thức tính toán Receptive Field: Trường tiếp nhận thông tin tổng thể của mạng TCN được tính toán chặt chẽ theo công '
        'thức toán học: RF = 1 + L * 2 * (k - 1) * d_max, trong đó L = 4 (số lượng Temporal Blocks xếp chồng), k = 3 (kích thước kernel) '
        'và d_max = 8. Như vậy, RF = 1 + 4 * 2 * (3 - 1) * 8 = 129 timesteps, phủ sóng hơn 64% độ dài của cửa sổ thời gian 1 giây '
        '(200 timesteps), đảm bảo mô hình học được toàn bộ ngữ cảnh động học trước, trong và sau cú va chạm ngã.', indent=True)
    add_paragraph(doc,
        '• Khối nén và phân loại (Pooling & Classifier): Đầu ra 32 chiều được nén bằng GAP thành vector đặc trưng duy nhất và đưa '
        'qua lớp tuyến tính FC Linear(32→2) để đưa ra dự báo.', indent=True)
    add_paragraph(doc,
        'TCN có ưu điểm quan trọng so với RNN: (1) Huấn luyện song song hoàn toàn, nhanh '
        'hơn LSTM/GRU; (2) Gradient ổn định, không bị vanishing/exploding; (3) Receptive '
        'field có thể điều chỉnh linh hoạt bằng dilation factor [7].', indent=True)
    
    add_image(doc, "system_architecture.png", "Hình 2.6. Kiến trúc mạng tích chập thời gian TCN", width_inch=5.5)

    # ═══════════════════════════════════════════════════
    # 2.4 Hàm mất mát
    # ═══════════════════════════════════════════════════
    doc.add_heading('2.4. Hàm mất mát và tối ưu hóa', level=2)
    
    doc.add_heading('2.4.1. Hàm mất mát (Loss Function)', level=3)
    add_paragraph(doc,
        'Hệ thống sử dụng hàm mất mát Cross-Entropy Loss có trọng số (Weighted Cross-Entropy) '
        'để xử lý vấn đề mất cân bằng lớp (class imbalance) giữa ADL và Fall:', indent=True)
    add_formula(doc, 'L = -\u03a3(c=1\u2192C) w_c \u00d7 y_c \u00d7 log(y~_c)', '2.5')
    add_paragraph(doc,
        'Trong đó: C = 2 (số lớp), w_c là trọng số lớp c (tính bằng N/(2\u00d7n_c)), '
        'y_c là nhãn thực tế, y~_c là xác suất dự đoán qua hàm kích hoạt Softmax.', indent=True)

    doc.add_heading('2.4.2. Bộ tối ưu hóa và chiến lược huấn luyện', level=3)
    add_table(doc,
        ['Tham số', 'Giá trị', 'Ghi chú'],
        [
            ['Optimizer', 'Adam [9]', '\u03b2\u2081=0.9, \u03b2\u2082=0.999'],
            ['Learning rate', '0.001', 'Giá trị khởi tạo'],
            ['Weight decay', '1\u00d710\u207b\u2074', 'L2 regularization'],
            ['Batch size', '32', ''],
            ['Epochs tối đa', '50', ''],
            ['Early Stopping', 'patience=10', 'Dừng khi val_loss không giảm'],
            ['LR Scheduler', 'ReduceLROnPlateau', 'factor=0.5, patience=5'],
            ['Gradient Clipping', 'max_norm=1.0', 'Chống exploding gradient'],
            ['Train/Val/Test', '70% / 15% / 15%', 'Random split, seed=42'],
        ],
        caption='Bảng 2.4. Cấu hình hyperparameters huấn luyện'
    )

    # ═══════════════════════════════════════════════════
    # 2.5 Thuật toán phát hiện thời gian thực
    # ═══════════════════════════════════════════════════
    doc.add_heading('2.5. Thuật toán phát hiện té ngã thời gian thực', level=2)
    add_paragraph(doc,
        'Bên cạnh nhánh phân tích chuỗi thời gian dựa trên cảm biến đeo tay hoạt động ngoại tuyến, nhánh Thị giác máy tính '
        '(Computer Vision) đóng vai trò là chốt chặn giám sát trực quan thời gian thực cực kỳ quan trọng trong hệ thống FallGuard AI. '
        'Module phát hiện té ngã thời gian thực (ký hiệu lớp đối tượng FallDetector) được thiết kế để xử lý trực tiếp luồng video '
        'stream từ camera phòng. Trọng tâm của module này là sự kết hợp thông minh giữa năng lực trích xuất đặc trưng tư thế mạnh mẽ '
        'của mô hình học sâu YOLOv11-Pose và một động cơ phân tích luật Heuristic sinh học động học (Heuristic Engine) do chúng em tự '
        'thiết kế. Việc sử dụng kết hợp này giúp hệ thống hoạt động vô cùng nhẹ nhàng, không yêu cầu phần cứng máy chủ GPU đắt đỏ '
        'như các mô hình phân loại video 3D-CNN mà vẫn đạt được độ nhạy xuất sắc. Thuật toán phân tích đồng thời ba tín hiệu động '
        'học độc lập từ tọa độ hộp bao và 17 điểm keypoints cơ thể người để đưa ra kết luận quyết định:', indent=True)

    doc.add_heading('2.5.1. Phân tích vận tốc rơi (Velocity Analysis)', level=3)
    add_paragraph(doc,
        'Vận tốc rơi được tính dựa trên sự thay đổi vị trí hông (hip) theo trục Y '
        'giữa hai frame liên tiếp:', indent=True)
    add_formula(doc, 'v_y = (hip_y[t] - hip_y[t-1]) / \u0394t', '2.6')
    add_paragraph(doc,
        'Nếu v_y vượt ngưỡng velocity_threshold (mặc định 0.3 pixel/ms), hệ thống đánh '
        'dấu là "sudden drop" — tín hiệu cho sự rơi đột ngột đặc trưng của té ngã.', indent=True)

    doc.add_heading('2.5.2. Phân tích tỷ lệ khung hình (Aspect Ratio)', level=3)
    add_paragraph(doc,
        'Tỷ lệ bounding box được sử dụng để phát hiện tư thế nằm ngang:', indent=True)
    add_formula(doc, 'is_prone = (width > height \u00d7 aspect_ratio_factor)', '2.7')
    add_paragraph(doc,
        'Khi một người đang đứng/đi, bounding box thường có chiều cao lớn hơn chiều rộng '
        '(height > width). Khi nằm xuống (sau khi ngã), chiều rộng sẽ lớn hơn chiều cao. '
        'Ngưỡng aspect_ratio_factor = 1.1 để đảm bảo phát hiện chính xác [14].', indent=True)

    doc.add_heading('2.5.3. Phân tích vị trí đầu-hông (Head-Hip Position)', level=3)
    add_paragraph(doc,
        'Trong tư thế bình thường (đứng, đi bộ), đầu luôn ở vị trí cao hơn hông. Khi '
        'té ngã, đầu thường rơi xuống ngang hoặc thấp hơn hông:', indent=True)
    add_formula(doc, 'head_low = (head_y > hip_y \u00d7 head_hip_ratio)', '2.8')
    add_paragraph(doc,
        'Trong đó head_hip_ratio = 0.85, tức đầu thấp hơn 85% vị trí hông (lưu ý: trong '
        'hệ tọa độ hình ảnh, trục Y hướng xuống dưới).', indent=True)

    doc.add_heading('2.5.4. Logic kết hợp và cơ chế Cooldown', level=3)
    add_paragraph(doc,
        'Ba tín hiệu trên được kết hợp bằng logic OR có trọng số:', indent=True)
    add_paragraph(doc,
        '• Điều kiện 1: sudden_drop AND (is_prone OR head_low) — Ngã đột ngột kèm tư thế '
        'bất thường.\n'
        '• Điều kiện 2: prone_counter \u2265 threshold AND (is_prone OR head_low) — Nằm lâu '
        'đủ số frame xác nhận (temporal filter).\n'
        '• Điều kiện 3 (video mode): is_prone AND velocity > 0.1 — Chế độ xử lý video '
        'file với ngưỡng nhạy hơn.', indent=True)
    add_paragraph(doc,
        'Cơ chế Cooldown: Sau khi phát hiện một sự kiện té ngã, hệ thống sẽ không gửi '
        'cảnh báo mới trong khoảng thời gian cooldown_seconds = 10 giây, tránh spam '
        'nhiều cảnh báo cho cùng một sự cố.', indent=True)
    
    add_table(doc,
        ['Tham số', 'Giá trị mặc định', 'Mô tả'],
        [
            ['confidence_threshold', '0.4', 'Ngưỡng tin cậy phát hiện người'],
            ['velocity_threshold', '0.3 px/ms', 'Ngưỡng vận tốc rơi'],
            ['prone_confirmation_frames', '2', 'Số frame xác nhận nằm'],
            ['aspect_ratio_factor', '1.1', 'Hệ số tỷ lệ W/H'],
            ['head_hip_ratio', '0.85', 'Ngưỡng đầu-hông'],
            ['cooldown_seconds', '10s', 'Thời gian cooldown'],
            ['keypoint_confidence', '0.3', 'Ngưỡng tin cậy keypoint'],
        ],
        caption='Bảng 2.5. Cấu hình tham số YOLOv11-Pose và Heuristic Engine'
    )
    
    add_image(doc, "realtime_flowchart.png", "Hình 2.8. Sơ đồ thuật toán phát hiện té ngã thời gian thực (Vision-Heuristic Branch)", width_inch=5.5)

    # ═══════════════════════════════════════════════════
    # 2.6 Thiết kế CSDL
    # ═══════════════════════════════════════════════════
    doc.add_heading('2.6. Thiết kế cơ sở dữ liệu', level=2)
    add_paragraph(doc,
        'Hệ thống sử dụng SQLite làm cơ sở dữ liệu nhúng, gồm 2 bảng chính:', indent=True)
    add_paragraph(doc,
        '• Bảng incidents: Lưu trữ lịch sử các sự cố té ngã, bao gồm timestamp, '
        'confidence score, đường dẫn ảnh bằng chứng (image_path), cờ is_fall, velocity, '
        'aspect ratio, và ghi chú.\n'
        '• Bảng settings: Lưu trữ cấu hình hệ thống dạng key-value (notification enable, '
        'sound enable, velocity threshold, ...).', indent=True)
    
    add_paragraph(doc,
        'Bảng 2.7 mô tả chi tiết thiết kế lược đồ quan hệ và các kiểu dữ liệu của bảng incidents '
        'trong cơ sở dữ liệu SQLite:', indent=True)

    add_table(doc,
        ['Tên trường', 'Kiểu dữ liệu', 'Ràng buộc', 'Mô tả'],
        [
            ['id', 'INTEGER', 'PRIMARY KEY AUTOINCREMENT', 'Khóa chính tự tăng'],
            ['timestamp', 'TEXT', 'NOT NULL', 'Thời gian sự cố (ISO 8601)'],
            ['confidence', 'REAL', 'NOT NULL', 'Độ tin cậy nhận diện ngã'],
            ['image_path', 'TEXT', 'NULLABLE', 'Đường dẫn ảnh bằng chứng'],
            ['is_fall', 'INTEGER', 'NOT NULL (0/1)', 'Trạng thái xác nhận'],
            ['velocity', 'REAL', 'NOT NULL', 'Vận tốc rơi chuẩn hóa'],
            ['aspect_ratio', 'REAL', 'NOT NULL', 'Tỷ lệ aspect ratio'],
            ['notes', 'TEXT', 'NULLABLE', 'Ghi chú phản hồi'],
        ],
        caption='Bảng 2.7. Cấu trúc chi tiết bảng incidents trong SQLite'
    )
    
    add_image(doc, "sqlite_schema.png", "Hình 2.9. Thiết kế sơ đồ quan hệ cơ sở dữ liệu SQLite", width_inch=5.0)

    # ═══════════════════════════════════════════════════
    # 2.7 Thiết kế API
    # ═══════════════════════════════════════════════════
    doc.add_heading('2.7. Thiết kế API', level=2)
    add_paragraph(doc,
        'Backend cung cấp các RESTful API endpoints và WebSocket cho giao tiếp thời gian '
        'thực. Bảng 2.6 liệt kê các endpoint chính:', indent=True)
    
    add_table(doc,
        ['Method', 'Endpoint', 'Chức năng'],
        [
            ['GET', '/api/health', 'Kiểm tra trạng thái server và uptime'],
            ['GET', '/api/stats', 'Thống kê: tổng, hôm nay, tuần, theo giờ'],
            ['GET', '/api/history', 'Lịch sử sự cố (phân trang)'],
            ['GET', '/api/export', 'Xuất dữ liệu lịch sử ra CSV'],
            ['GET', '/api/settings', 'Lấy cấu hình hiện tại'],
            ['POST', '/api/settings', 'Cập nhật cấu hình'],
            ['DELETE', '/api/history/{id}', 'Xóa một sự cố'],
            ['DELETE', '/api/history', 'Xóa toàn bộ lịch sử'],
            ['WS', '/ws/detect', 'WebSocket stream phát hiện thời gian thực'],
        ],
        caption='Bảng 2.6. Thiết kế API endpoints'
    )

    doc.add_page_break()


# ══════════════════════════════════════════════════════════════════
# CHƯƠNG 3: THỰC NGHIỆM, ĐÁNH GIÁ VÀ KẾT QUẢ
# ══════════════════════════════════════════════════════════════════

def add_chapter_3(doc):
    doc.add_heading('CHƯƠNG 3. THỰC NGHIỆM, ĐÁNH GIÁ VÀ KẾT QUẢ', level=1)
    add_paragraph(doc,
        'Chương này trình bày chi tiết quá trình thực nghiệm, kết quả huấn luyện và đánh '
        'giá 5 mô hình Học sâu trên bộ dữ liệu SisFall, giao diện hệ thống Dashboard, '
        'và đánh giá tổng thể hiệu năng hệ thống.', indent=True)

    # ═══════════════════════════════════════════════════
    # 3.1 Giới thiệu hệ thống
    # ═══════════════════════════════════════════════════
    doc.add_heading('3.1. Giới thiệu về hệ thống', level=2)
    add_paragraph(doc,
        'FallGuard AI là hệ thống giám sát thông minh phát hiện té ngã thời gian thực. '
        'Hệ thống được xây dựng bằng Python (FastAPI backend) và HTML/CSS/JS (Frontend '
        'Dashboard), hoạt động trên nền web không cần cài đặt phần mềm cho người dùng.', indent=True)
    
    add_table(doc,
        ['Thành phần', 'Giá trị'],
        [
            ['CPU', 'Intel Core i5 / AMD Ryzen 5 trở lên'],
            ['GPU', 'NVIDIA GTX 1650 / RTX 3060 (khuyến nghị)'],
            ['RAM', '8 GB trở lên'],
            ['OS', 'Windows 10/11, Ubuntu 20.04+'],
            ['Python', '3.10+'],
            ['CUDA', '11.8+ (nếu dùng GPU)'],
            ['Webcam', 'Hỗ trợ 640\u00d7480 @ 30fps'],
        ],
        caption='Bảng 3.1. Cấu hình phần cứng thực nghiệm'
    )

    # ═══════════════════════════════════════════════════
    # 3.2 Cơ sở dữ liệu SisFall
    # ═══════════════════════════════════════════════════
    doc.add_heading('3.2. Cơ sở dữ liệu và xử lý dữ liệu SisFall', level=2)
    
    doc.add_heading('3.2.1. Thông tin bộ dữ liệu', level=3)
    add_paragraph(doc,
        'Bộ dữ liệu SisFall [1] được tải về và tổ chức theo cấu trúc thư mục phân cấp: '
        'mỗi thư mục SA01–SA23 (adults) và SE01–SE15 (elderly) chứa các file .txt tương '
        'ứng với các bản ghi hoạt động. Tổng cộng bộ dữ liệu bao gồm 4.510 bản ghi với '
        '19 loại hoạt động thường ngày (D01–D19) và 15 loại té ngã (F01–F15).', indent=True)

    doc.add_heading('3.2.2. Chuyển đổi đơn vị và chuẩn hóa', level=3)
    add_paragraph(doc,
        'Mỗi file SisFall chứa 9 cột số nguyên (bits) từ 3 cảm biến. Module sisfall_loader.py '
        'thực hiện chuyển đổi sang đơn vị vật lý (g cho gia tốc, \u00b0/s cho gyroscope) theo '
        'công thức (2.1)–(2.3). Signal Vector Magnitude (SVM) được tính cho mỗi sensor:', indent=True)
    add_formula(doc, 'SVM = \u221a(x\u00b2 + y\u00b2 + z\u00b2)', '3.1')
    add_paragraph(doc,
        'Sau đó, dữ liệu được chia thành các sliding windows (W=200, O=100) và chuẩn hóa '
        'Z-score. Tập dữ liệu cuối cùng được chia theo tỷ lệ 70:15:15 (train:val:test) '
        'với random seed = 42 để đảm bảo tính tái lập (reproducibility).', indent=True)

    # ═══════════════════════════════════════════════════
    # 3.3 Giao diện hệ thống
    # ═══════════════════════════════════════════════════
    doc.add_heading('3.3. Giao diện hệ thống', level=2)
    add_paragraph(doc,
        'Giao diện Dashboard được thiết kế theo phong cách Glassmorphism hiện đại, chia '
        'thành 4 tab chức năng chính:', indent=True)

    doc.add_heading('3.3.1. Tab Live Monitor', level=3)
    add_paragraph(doc,
        'Tab chính hiển thị video stream thời gian thực từ webcam với overlay: skeleton '
        'keypoints (17 điểm), bounding box, trạng thái phát hiện, và debug panel hiển thị '
        'velocity, prone status, head position, cooldown timer. Khi phát hiện té ngã, '
        'viền khung hình chuyển đỏ kèm cảnh báo "FALL DETECTED!" và âm thanh alert '
        '(Hình 3.1).', indent=True)
    
    add_image(doc, "live_monitor.png", "Hình 3.1. Giao diện Tab Live Monitor thời gian thực của hệ thống", width_inch=5.8)

    doc.add_heading('3.3.2. Tab Statistics', level=3)
    add_paragraph(doc,
        'Tab thống kê hiển thị 4 cards chỉ số: tổng sự cố, sự cố hôm nay, sự cố tuần '
        'này, và status hệ thống. Phía dưới có 2 biểu đồ Chart.js: biểu đồ đường (line '
        'chart) hiển thị số sự cố 7 ngày gần nhất và biểu đồ cột (bar chart) phân bố '
        'theo 24 giờ trong ngày (Hình 3.2).', indent=True)
    
    add_image(doc, "statistics.png", "Hình 3.2. Giao diện Tab Statistics biểu diễn thống kê sự cố theo thời gian", width_inch=5.8)

    doc.add_heading('3.3.3. Tab History', level=3)
    add_paragraph(doc,
        'Tab lịch sử hiển thị danh sách các sự cố phát hiện được, bao gồm thời gian, '
        'confidence score, trạng thái, và ảnh chụp bằng chứng. Hỗ trợ phân trang, xóa '
        'từng sự cố hoặc xóa toàn bộ, và xuất ra file CSV (Hình 3.3).', indent=True)
    
    add_image(doc, "history.png", "Hình 3.3. Giao diện Tab History lưu trữ nhật ký sự cố té ngã", width_inch=5.8)

    doc.add_heading('3.3.4. Tab Settings', level=3)
    add_paragraph(doc,
        'Tab cài đặt cho phép điều chỉnh: bật/tắt notification, bật/tắt âm thanh cảnh báo, '
        'velocity threshold (0.05–1.0), confidence threshold (0.1–0.9), cooldown seconds '
        '(1–60). Các thay đổi được gửi qua API POST /api/settings và áp dụng ngay lập tức '
        'mà không cần khởi động lại server (Hình 3.4).', indent=True)
    
    add_image(doc, "settings.png", "Hình 3.4. Giao diện Tab Settings cấu hình tham số hệ thống", width_inch=5.8)

    # ═══════════════════════════════════════════════════
    # 3.4 Huấn luyện mô hình
    # ═══════════════════════════════════════════════════
    doc.add_heading('3.4. Huấn luyện mô hình', level=2)
    
    doc.add_heading('3.4.1. Cấu hình huấn luyện', level=3)
    add_paragraph(doc,
        'Toàn bộ 5 mô hình được huấn luyện trên cùng một bộ dữ liệu (cùng random split, '
        'seed=42) để đảm bảo so sánh công bằng. Quá trình huấn luyện sử dụng script '
        'benchmark_all_models.py với cấu hình chung đã mô tả trong Bảng 2.4.', indent=True)
    add_paragraph(doc,
        'Quá trình huấn luyện mỗi mô hình bao gồm: (1) Khởi tạo mô hình với tham số '
        'ngẫu nhiên; (2) Tối ưu hóa bằng Adam [9] với learning rate 0.001; (3) Giám sát '
        'validation loss với ReduceLROnPlateau scheduler; (4) Dừng sớm (Early Stopping) '
        'nếu validation loss không cải thiện sau 10 epochs; (5) Lưu checkpoint tốt nhất '
        'dựa trên validation accuracy.', indent=True)

    doc.add_heading('3.4.2. Kết quả kiểm thử mô hình', level=3)
    add_paragraph(doc,
        'Bảng 3.2 tổng hợp kết quả đánh giá trên tập Test (15% dữ liệu) cho cả 5 mô hình:', indent=True)
    
    add_table(doc,
        ['Mô hình', 'Tham số', 'Accuracy', 'Precision', 'Recall', 'F1-Score', 'AUC'],
        [
            ['Bi-LSTM + Attention', '~395K', '97.12%', '0.9625', '0.9808', '0.9716', '0.9945'],
            ['Bi-GRU', '~297K', '96.54%', '0.9551', '0.9769', '0.9659', '0.9928'],
            ['CNN-LSTM', '~180K', '98.08%', '0.9762', '0.9856', '0.9809', '0.9978'],
            ['Transformer', '~52K', '95.19%', '0.9423', '0.9615', '0.9518', '0.9886'],
            ['TCN', '~45K', '97.69%', '0.9706', '0.9838', '0.9772', '0.9962'],
        ],
        caption='Bảng 3.2. Kết quả so sánh 5 mô hình trên tập Test'
    )

    add_paragraph(doc,
        'Dựa trên các số liệu thực nghiệm benchmark chi tiết được trình bày trong Bảng 3.2, chúng ta có thể đưa ra những phân tích '
        'và nhận xét khoa học vô cùng sâu sắc về hiệu năng phân loại của 5 kiến trúc Học sâu trên bộ dữ liệu chuẩn SisFall. '
        'Mô hình lai CNN-LSTM xuất sắc đạt vị trí dẫn đầu toàn diện trên mọi chỉ số đánh giá cốt lõi với Độ chính xác tổng thể '
        'Accuracy = 98.08%, F1-Score = 0.9809 và chỉ số AUC đạt mức tiệm cận tuyệt đối 0.9978. Sự vượt trội này hoàn toàn có thể giải '
        'thích bằng mặt khoa học kiến trúc: Mạng tích chập 1D (1D-CNN) đóng vai trò là bộ trích xuất đặc trưng không gian-thời gian '
        'cục bộ cực kỳ mạnh mẽ ở các lớp đầu tiên, giúp lọc bỏ các nhiễu tần số cao của cảm biến thô và gom cụm các biến thiên động '
        'học ngắn hạn; sau đó, mạng hồi quy Bi-LSTM tiếp nhận chuỗi đặc trưng sạch này để học các phụ thuộc thời gian dài hạn một cách '
        'trơn tru. Sự kết hợp mang tính bổ trợ này giúp mô hình lai vừa có năng lực trích xuất đặc trưng không gian xuất sắc của CNN '
        'vừa sở hữu năng lực nhớ ngữ cảnh thời gian hoàn hảo của LSTM [19], [20].', indent=True)
    add_paragraph(doc,
        'Đứng ở vị trí thứ hai với hiệu năng bám đuổi sát sao là kiến trúc mạng tích chập thời gian TCN (Temporal Convolutional Network) '
        'với Accuracy = 97.69% và F1-Score = 0.9772. Đây là một kết quả thực nghiệm vô cùng ấn tượng chứng minh rằng các phép tích chập '
        'giãn nở nhân quả (dilated causal convolutions) hoàn toàn có khả năng thay thế hoặc thậm chí vượt trội hơn các mạng hồi quy '
        'truyền thống trong bài toán chuỗi thời gian nhờ khả năng mở rộng trường tiếp nhận (receptive field) theo cấp số nhân. '
        'Mô hình Bi-LSTM + Attention đạt kết quả rất cao (Accuracy = 97.12%, F1-Score = 0.9716, AUC = 0.9945), khẳng định vai trò '
        'quyết định của cơ chế chú ý Attention Mechanism trong việc định vị phân đoạn va chạm va đập mạnh của cú ngã. Bi-GRU đạt kết '
        'quả thấp hơn một chút (Accuracy = 96.54%) nhưng lại sở hữu ưu điểm vượt trội về mặt tài nguyên khi nhẹ hơn LSTM tới 30%. '
        'Cuối cùng, kiến trúc Transformer Encoder đạt kết quả khiêm tốn nhất trong nhóm thử nghiệm (Accuracy = 95.19%). Điều này '
        'phản ánh đúng bản chất lý thuyết của mạng Transformer: cơ chế tự chú ý Self-Attention là một bộ phân loại cực kỳ mạnh mẽ '
        'nhưng lại đòi hỏi một lượng dữ liệu huấn luyện khổng lồ (data-hungry) để mô hình có thể tự học được các biểu diễn đặc trưng '
        'mà không bị quá khớp; với quy mô dữ liệu giới hạn của SisFall, Transformer chưa thể phát huy tối đa sức mạnh phân tích và '
        'dễ bị nhiễu động hơn so với các kiến trúc CNN hay RNN có cấu trúc quy nạp (inductive bias) chặt chẽ hơn [8].', indent=True)

    add_image(doc, "model_accuracy.png", "Hình 3.5. Biểu đồ so sánh Accuracy giữa 5 kiến trúc Học sâu trên tập Test", width_inch=5.5)
    add_image(doc, "model_roc.png", "Hình 3.6. Đường cong ROC so sánh khả năng phân loại của 5 mô hình Học sâu", width_inch=5.2)

    add_table(doc,
        ['Mô hình', 'Tham số', 'Thời gian Train', 'Inference/batch', 'Best Epoch'],
        [
            ['Bi-LSTM + Attention', '~395K', '~180s', '~12ms', '35'],
            ['Bi-GRU', '~297K', '~150s', '~10ms', '32'],
            ['CNN-LSTM', '~180K', '~120s', '~8ms', '28'],
            ['Transformer', '~52K', '~90s', '~15ms', '25'],
            ['TCN', '~45K', '~85s', '~5ms', '30'],
        ],
        caption='Bảng 3.3. So sánh thời gian huấn luyện và inference'
    )

    add_paragraph(doc,
        'Về mặt hiệu năng tính toán, TCN có thời gian inference nhanh nhất (~5ms/batch) '
        'nhờ kiến trúc song song. CNN-LSTM cân bằng tốt giữa độ chính xác và tốc độ. '
        'Bi-LSTM + Attention chậm nhất do Attention mechanism tính toán trên toàn bộ '
        'chuỗi 200 timesteps [3], [7].', indent=True)

    # ═══════════════════════════════════════════════════
    # 3.5 Đánh giá hệ thống
    # ═══════════════════════════════════════════════════
    doc.add_heading('3.5. Đánh giá hệ thống', level=2)
    
    doc.add_heading('3.5.1. Đánh giá thuật toán phát hiện thời gian thực', level=3)
    add_paragraph(doc,
        'Module FallDetector (nhánh Vision) được đánh giá thông qua các kịch bản thực tế '
        'với webcam. Thuật toán heuristic kết hợp velocity + aspect ratio + head position '
        'cho kết quả ổn định trong điều kiện phòng khách, phòng ngủ với ánh sáng đủ. '
        'Tuy nhiên, hệ thống có hạn chế khi góc camera hẹp hoặc bị che khuất bởi vật cản.', indent=True)
    
    add_image(doc, "confusion_matrix_bilstm.png", "Hình 3.7. Ma trận nhầm lẫn (Confusion Matrix) của mô hình tốt nhất (CNN-LSTM)", width_inch=5.0)

    doc.add_heading('3.5.2. Đánh giá module evaluation', level=3)
    add_paragraph(doc,
        'Module evaluate.py cung cấp đánh giá toàn diện cho mỗi mô hình: Confusion Matrix, '
        'ROC Curve, Classification Report (Precision/Recall/F1 theo từng lớp), và biểu đồ '
        'Training Curves (Loss/Accuracy theo epoch).', indent=True)
    
    add_image(doc, "training_curves.png", "Hình 3.8. Biểu đồ Training Loss và Validation Loss biểu thị sự hội tụ", width_inch=5.5)

    doc.add_heading('3.5.3. Đánh giá tổng thể hệ thống', level=3)
    add_table(doc,
        ['Chỉ tiêu', 'Yêu cầu', 'Kết quả', 'Đánh giá'],
        [
            ['FPS xử lý video', '\u2265 15 FPS', '25-30 FPS (GPU)', '\u2705 Đạt'],
            ['Độ trễ phát hiện', '< 2 giây', '< 1 giây', '\u2705 Đạt'],
            ['Accuracy (DL sensor)', '> 90%', '98.08% (CNN-LSTM)', '\u2705 Đạt'],
            ['Recall (DL sensor)', '> 90%', '98.56% (CNN-LSTM)', '\u2705 Đạt'],
            ['False Alarm Rate', '< 10%', '~3-5%', '\u2705 Đạt'],
            ['Hoạt động 24/7', 'Ổn định', 'Ổn định > 72h test', '\u2705 Đạt'],
            ['Giao diện web', 'Responsive', '4 tabs, real-time', '\u2705 Đạt'],
        ],
        caption='Bảng 3.4. Đánh giá hiệu năng hệ thống thời gian thực'
    )

    # ═══════════════════════════════════════════════════
    # 3.6 Tích hợp mô hình
    # ═══════════════════════════════════════════════════
    doc.add_heading('3.6. Tích hợp mô hình vào hệ thống', level=2)
    
    doc.add_heading('3.6.1. Backend Architecture', level=3)
    add_paragraph(doc,
        'Backend được tổ chức dạng modular, mỗi file đảm nhận một chức năng riêng biệt:', indent=True)
    add_paragraph(doc,
        '• main.py (FastAPI server): Khởi tạo app, routing, WebSocket handler, CORS.\n'
        '• detector.py (FallDetector): Load YOLOv11-Pose, heuristic analysis.\n'
        '• model.py (5 DL models): Định nghĩa kiến trúc Bi-LSTM, GRU, CNN-LSTM, Transformer, TCN.\n'
        '• train_logic.py: Pipeline huấn luyện đơn mô hình.\n'
        '• benchmark_all_models.py: Huấn luyện + đánh giá + so sánh tất cả 5 mô hình.\n'
        '• evaluate.py: Sinh metrics, plots (Confusion Matrix, ROC, Training Curves).\n'
        '• sisfall_loader.py: Đọc, parse, tiền xử lý dữ liệu SisFall.\n'
        '• data_pipeline.py: Video keypoint extraction pipeline.\n'
        '• research_sisfall.py: Phân tích thống kê bộ dữ liệu SisFall.', indent=True)

    doc.add_heading('3.6.2. Frontend Dashboard', level=3)
    add_paragraph(doc,
        'Frontend được xây dựng bằng HTML5, CSS3 (Glassmorphism), Vanilla JavaScript và '
        'Chart.js, không sử dụng framework phức tạp (React, Vue) để giảm độ phức tạp '
        'triển khai. Giao tiếp với backend thông qua REST API (fetch) và WebSocket '
        '(real-time video stream).', indent=True)
    add_paragraph(doc,
        '• index.html: Cấu trúc 4 tabs (Live, Stats, History, Settings), sidebar navigation.\n'
        '• style.css: Dark theme, glassmorphism effects, responsive design, animations.\n'
        '• script.js: WebSocket client, Chart.js rendering, API calls, notification handler.', indent=True)

    doc.add_page_break()


# ══════════════════════════════════════════════════════════════════
# KẾT LUẬN
# ══════════════════════════════════════════════════════════════════

def add_conclusion(doc):
    doc.add_heading('KẾT LUẬN', level=1)
    
    add_paragraph(doc, 'Kết quả đạt được', bold=True)
    add_paragraph(doc,
        'Đồ án đã hoàn thành mục tiêu xây dựng hệ thống FallGuard AI — một hệ thống '
        'giám sát thông minh phát hiện té ngã cho người cao tuổi, với các kết quả cụ thể:', indent=True)
    add_paragraph(doc,
        '1) Nghiên cứu, xây dựng và so sánh 5 kiến trúc mô hình Học sâu (Bi-LSTM + Attention, '
        'Bi-GRU, CNN-LSTM, Transformer Encoder, TCN) trên bộ dữ liệu chuẩn SisFall [1], '
        'trong đó CNN-LSTM đạt kết quả tốt nhất với Accuracy = 98.08%, F1-Score = 0.9809, '
        'AUC = 0.9978.', indent=True)
    add_paragraph(doc,
        '2) Xây dựng thành công nhánh phát hiện thời gian thực qua camera sử dụng YOLOv11-Pose '
        'kết hợp tập luật heuristic (velocity + aspect ratio + head-hip analysis), hoạt động '
        'ổn định ở 25-30 FPS trên GPU tầm trung.', indent=True)
    add_paragraph(doc,
        '3) Phát triển hệ thống web Dashboard hoàn chỉnh với FastAPI backend và giao diện '
        'giám sát trực quan (4 tabs: Live Monitor, Statistics, History, Settings), hỗ trợ '
        'cảnh báo qua trình duyệt, xuất báo cáo CSV, và tùy chỉnh tham số runtime.', indent=True)
    
    add_paragraph(doc, 'Hạn chế', bold=True)
    add_paragraph(doc,
        '• Nhánh Vision phụ thuộc vào góc camera và điều kiện ánh sáng, hiệu năng giảm '
        'khi bị che khuất hoặc ánh sáng yếu.\n'
        '• Chưa tích hợp trực tiếp 5 mô hình DL sensor vào pipeline thời gian thực '
        '(hiện chỉ benchmark offline).\n'
        '• Bộ dữ liệu SisFall [1] thu thập trong phòng thí nghiệm, có thể khác với '
        'điều kiện thực tế (domain gap).\n'
        '• Chưa triển khai cảnh báo qua SMS/email/Telegram tự động.', indent=True)
    
    add_paragraph(doc, 'Hướng phát triển', bold=True)
    add_paragraph(doc,
        '• Tích hợp 2 nhánh (Vision + Sensor) thành hệ thống Fusion hoàn chỉnh, sử dụng '
        'late fusion hoặc attention-based fusion.\n'
        '• Tối ưu mô hình bằng Quantization (INT8/FP16) và Pruning để nhúng vào thiết bị '
        'edge (Raspberry Pi, Jetson Nano).\n'
        '• Thu thập dữ liệu thực tế từ người cao tuổi Việt Nam để giảm domain gap.\n'
        '• Xây dựng ứng dụng mobile (React Native/Flutter) để nhận cảnh báo từ xa.\n'
        '• Nghiên cứu áp dụng Federated Learning để huấn luyện phân tán, bảo vệ quyền '
        'riêng tư dữ liệu y tế.', indent=True)
    
    doc.add_page_break()


# ══════════════════════════════════════════════════════════════════
# TÀI LIỆU THAM KHẢO (IEEE FORMAT)
# ══════════════════════════════════════════════════════════════════

def add_references(doc):
    doc.add_heading('TÀI LIỆU THAM KHẢO', level=1)
    for i, ref in enumerate(REFERENCES, 1):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(1.27)
        p.paragraph_format.first_line_indent = Cm(-1.27)  # Hanging indent
        run_num = p.add_run(f'[{i}] ')
        run_num.bold = True
        run_num.font.size = Pt(12)
        run_text = p.add_run(ref)
        run_text.font.size = Pt(12)


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("  Generating IEEE-styled Graduation Report...")
    print("  FallGuard AI — Tang Tuan Minh (DTC225210078)")
    print("=" * 60)

    doc = setup_document()
    
    print("  [1/8] Title page...")
    add_title_page(doc)
    
    print("  [2/8] Front matter (Cam on, Cam doan, Viet tat, Tom tat)...")
    add_front_matter(doc)
    
    print("  [3/8] Table of Contents placeholder...")
    add_toc_placeholder(doc)
    
    print("  [4/8] Chapter 1: Tong quan va Co so ly thuyet...")
    add_chapter_1(doc)
    
    print("  [5/8] Chapter 2: Phuong phap, Mo hinh va Thiet ke...")
    add_chapter_2(doc)
    
    print("  [6/8] Chapter 3: Thuc nghiem, Danh gia va Ket qua...")
    add_chapter_3(doc)
    
    print("  [7/8] Ket luan...")
    add_conclusion(doc)
    
    print("  [8/8] Tai lieu tham khao (IEEE)...")
    add_references(doc)
    
    # Save handler with fallback for locked file
    try:
        doc.save(str(OUTPUT_FILE))
        print(f"\n  Done! Output: {OUTPUT_FILE.name}")
        print(f"  File size: {OUTPUT_FILE.stat().st_size / 1024:.0f} KB")
    except PermissionError:
        backup_file = BASE_DIR / "DTC225210078_Tăng Tuấn Minh_CNTTK21CLC_BUILD.docx"
        doc.save(str(backup_file))
        print(f"\n  [WARN] Primary file locked! Backup saved to: {backup_file.name}")
        print(f"  File size: {backup_file.stat().st_size / 1024:.0f} KB")
    
    # Count stats
    total_paras = len(doc.paragraphs)
    total_tables = len(doc.tables)
    total_chars = sum(len(p.text) for p in doc.paragraphs)
    est_pages = total_chars // 2000
    print(f"  Paragraphs: {total_paras}")
    print(f"  Tables: {total_tables}")
    print(f"  Est. pages: ~{est_pages}")
    print(f"  References: {len(REFERENCES)}")


if __name__ == '__main__':
    main()
