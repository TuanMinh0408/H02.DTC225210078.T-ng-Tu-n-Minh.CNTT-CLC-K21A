import os

artifact_dir = r"C:\Users\minhc\.gemini\antigravity\brain\65931094-baed-469f-9a6a-9b48ac195efe"

def draw_rect(x, y, w, h, fill, stroke, text, text2=""):
    rx = 8
    res = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
    res += f'\n<text x="{x+w/2}" y="{y+h/2 - (10 if text2 else 0)}" class="text">{text}</text>'
    if text2:
        res += f'\n<text x="{x+w/2}" y="{y+h/2 + 15}" class="text2">{text2}</text>'
    return res

def draw_arrow(x1, y1, x2, y2, label=""):
    res = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="arrow"/>'
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        res += f'\n<rect x="{mx-30}" y="{my-12}" width="60" height="24" fill="white" rx="4"/>'
        res += f'\n<text x="{mx}" y="{my+4}" class="label">{label}</text>'
    return res

def hinh_2_1():
    svg = ['<svg width="950" height="250" viewBox="0 0 950 250" xmlns="http://www.w3.org/2000/svg">']
    svg.append('<style>.text { font-family: Arial; font-weight: bold; font-size: 16px; text-anchor: middle; alignment-baseline: middle; fill: #333; }')
    svg.append('.text2 { font-family: Arial; font-size: 14px; text-anchor: middle; alignment-baseline: middle; fill: #555; }')
    svg.append('.arrow { stroke: #555; stroke-width: 2.5px; fill: none; marker-end: url(#ah); }')
    svg.append('</style>')
    svg.append('<defs><marker id="ah" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#555" /></marker></defs>')
    
    # Blocks
    svg.append(draw_rect(50, 80, 120, 80, "#e3f2fd", "#1e88e5", "Camera", "Video Stream"))
    svg.append(draw_arrow(170, 120, 230, 120))
    
    svg.append(draw_rect(230, 80, 140, 80, "#fff3e0", "#fb8c00", "YOLOv11", "Phát hiện người"))
    svg.append(draw_arrow(370, 120, 430, 120))
    
    svg.append(draw_rect(430, 80, 140, 80, "#fff3e0", "#fb8c00", "MediaPipe", "Trích xuất 33 khớp"))
    svg.append(draw_arrow(570, 120, 630, 120))
    
    svg.append(draw_rect(630, 80, 140, 80, "#fff3e0", "#fb8c00", "Bi-GRU", "Phân tích chuỗi"))
    svg.append(draw_arrow(770, 120, 830, 120))
    
    svg.append(draw_rect(830, 80, 110, 80, "#e8f5e9", "#43a047", "Kết quả", "Té ngã/Bình thường"))
    
    svg.append('</svg>')
    path = os.path.join(artifact_dir, "hinh_2_1_flow.svg")
    with open(path, "w", encoding="utf-8") as f: f.write('\n'.join(svg))

def hinh_2_2():
    svg = ['<svg width="700" height="550" viewBox="0 0 700 550" xmlns="http://www.w3.org/2000/svg">']
    svg.append('<style>.title { font-family: Arial; font-weight: bold; font-size: 20px; fill: #1e3a5f; }')
    svg.append('.text { font-family: Arial; font-weight: bold; font-size: 16px; text-anchor: middle; alignment-baseline: middle; fill: #333; }')
    svg.append('.text2 { font-family: Arial; font-size: 14px; text-anchor: middle; alignment-baseline: middle; fill: #555; }')
    svg.append('.arrow { stroke: #555; stroke-width: 2.5px; fill: none; marker-end: url(#ah); marker-start: url(#ah-start); }')
    svg.append('.arrow-up { stroke: #555; stroke-width: 2.5px; fill: none; marker-end: url(#ah); }')
    svg.append('</style>')
    svg.append('<defs>')
    svg.append('<marker id="ah" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#555" /></marker>')
    svg.append('<marker id="ah-start" markerWidth="10" markerHeight="7" refX="1" refY="3.5" orient="auto"><polygon points="10 0, 0 3.5, 10 7" fill="#555" /></marker>')
    svg.append('</defs>')
    
    # Layers (from bottom to top)
    layers = [
        {"y": 420, "color": "#f3e5f5", "border": "#8e24aa", "title": "Lớp Dữ liệu (Data Layer)", "boxes": [("Camera / Webcam", "Dữ liệu thời gian thực"), ("SisFall Dataset", "Dữ liệu huấn luyện")]},
        {"y": 300, "color": "#e3f2fd", "border": "#1e88e5", "title": "Lớp AI & Xử lý (AI Processing Layer)", "boxes": [("YOLOv11-Pose", "Phát hiện đối tượng"), ("MediaPipe BlazePose", "Trích xuất khung xương"), ("Bi-GRU Model", "Phân loại hành vi")]},
        {"y": 180, "color": "#e8f5e9", "border": "#43a047", "title": "Lớp Dịch vụ (Service Layer)", "boxes": [("FastAPI Backend", "Xử lý API & Logic"), ("WebSocket", "Truyền phát video & cảnh báo")]},
        {"y": 60, "color": "#fff3e0", "border": "#fb8c00", "title": "Lớp Giao diện (Presentation Layer)", "boxes": [("Web Dashboard", "Hiển thị giao diện người dùng"), ("Alert System", "Cảnh báo té ngã")]}
    ]
    
    for i, L in enumerate(layers):
        y = L["y"]
        svg.append(f'<rect x="50" y="{y}" width="600" height="100" rx="10" fill="{L["color"]}" stroke="{L["border"]}" stroke-width="2"/>')
        svg.append(f'<text x="60" y="{y+25}" style="text-anchor:start;" class="title">{L["title"]}</text>')
        box_width = 560 // len(L["boxes"])
        for j, box in enumerate(L["boxes"]):
            bx = 70 + j * box_width
            svg.append(f'<rect x="{bx}" y="{y+40}" width="{box_width-20}" height="50" rx="5" fill="#ffffff" stroke="#ccc" stroke-width="1"/>')
            svg.append(f'<text x="{bx + (box_width-20)/2}" y="{y+60}" class="text">{box[0]}</text>')
            svg.append(f'<text x="{bx + (box_width-20)/2}" y="{y+80}" class="text2">{box[1]}</text>')
            
        if i > 0:
            svg.append(f'<line x1="350" y1="{y+100}" x2="350" y2="{y+100+20}" class="arrow"/>')
            
    svg.append('</svg>')
    path = os.path.join(artifact_dir, "hinh_2_2_arch.svg")
    with open(path, "w", encoding="utf-8") as f: f.write('\n'.join(svg))

def draw_diamond(x, y, w, h, fill, stroke, text1, text2=""):
    pts = f"{x+w/2},{y} {x+w},{y+h/2} {x+w/2},{y+h} {x},{y+h/2}"
    res = f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
    res += f'\n<text x="{x+w/2}" y="{y+h/2 - (8 if text2 else 0)}" class="text">{text1}</text>'
    if text2:
        res += f'\n<text x="{x+w/2}" y="{y+h/2 + 12}" class="text2">{text2}</text>'
    return res

def hinh_2_3():
    svg = ['<svg width="600" height="900" viewBox="0 0 600 900" xmlns="http://www.w3.org/2000/svg">']
    svg.append('<style>.text { font-family: Arial; font-weight: bold; font-size: 14px; text-anchor: middle; alignment-baseline: middle; fill: #333; }')
    svg.append('.text2 { font-family: Arial; font-size: 13px; text-anchor: middle; alignment-baseline: middle; fill: #555; }')
    svg.append('.label { font-family: Arial; font-weight: bold; font-size: 14px; fill: #d32f2f; text-anchor: middle; }')
    svg.append('.arrow { stroke: #555; stroke-width: 2.5px; fill: none; marker-end: url(#ah); }')
    svg.append('.line { stroke: #555; stroke-width: 2.5px; fill: none; }')
    svg.append('</style>')
    svg.append('<defs><marker id="ah" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#555" /></marker></defs>')
    
    cx = 300
    y = 30
    dy = 90
    y_rf_center = 145
    
    # Bắt đầu (Oval)
    svg.append(f'<rect x="{cx-75}" y="{y}" width="150" height="50" rx="25" fill="#cfd8dc" stroke="#607d8b" stroke-width="2"/>')
    svg.append(f'<text x="{cx}" y="{y+25}" class="text">BẮT ĐẦU</text>')
    svg.append(draw_arrow(cx, y+50, cx, y+dy))
    
    y += dy
    # Đọc frame
    svg.append(draw_rect(cx-100, y, 200, 50, "#e3f2fd", "#1e88e5", "Đọc khung hình", "từ Camera/Video"))
    svg.append(draw_arrow(cx, y+50, cx, y+dy))
    
    y += dy
    # YOLO
    svg.append(draw_rect(cx-120, y, 240, 50, "#fff3e0", "#fb8c00", "YOLOv11-Pose", "Phát hiện & cắt vùng người"))
    svg.append(draw_arrow(cx, y+50, cx, y+dy))
    
    y += dy
    # Diamond 1: Có người?
    svg.append(draw_diamond(cx-100, y, 200, 80, "#fff9c4", "#fbc02d", "Có phát hiện", "được người?"))
    svg.append(draw_arrow(cx, y+80, cx, y+dy+30))
    svg.append(f'<text x="{cx+20}" y="{y+100}" class="label">Có</text>')
    
    # False branch 1
    svg.append(f'<line x1="{cx-100}" y1="{y+40}" x2="{cx-180}" y2="{y+40}" class="line"/>')
    svg.append(f'<line x1="{cx-180}" y1="{y+40}" x2="{cx-180}" y2="{y_rf_center}" class="line"/>')
    svg.append(f'<line x1="{cx-180}" y1="{y_rf_center}" x2="{cx-100}" y2="{y_rf_center}" class="arrow"/>')
    svg.append(f'<text x="{cx-140}" y="{y+30}" class="label">Không</text>')
    
    y += dy + 30
    # MediaPipe
    svg.append(draw_rect(cx-120, y, 240, 50, "#fff3e0", "#fb8c00", "MediaPipe BlazePose", "Trích xuất 33 điểm khớp xương"))
    svg.append(draw_arrow(cx, y+50, cx, y+dy))
    
    y += dy
    # Buffer
    svg.append(draw_rect(cx-120, y, 240, 50, "#e8f5e9", "#43a047", "Cập nhật bộ đệm", "chuỗi thời gian (Window)"))
    svg.append(draw_arrow(cx, y+50, cx, y+dy))
    
    y += dy
    # Diamond 2: Đủ 30 frame?
    svg.append(draw_diamond(cx-100, y, 200, 80, "#fff9c4", "#fbc02d", "Đủ kích thước", "chuỗi (sequence)?"))
    svg.append(draw_arrow(cx, y+80, cx, y+dy+30))
    svg.append(f'<text x="{cx+20}" y="{y+100}" class="label">Có</text>')
    
    # False branch 2
    svg.append(f'<line x1="{cx-100}" y1="{y+40}" x2="{cx-240}" y2="{y+40}" class="line"/>')
    svg.append(f'<line x1="{cx-240}" y1="{y+40}" x2="{cx-240}" y2="{y_rf_center}" class="line"/>')
    svg.append(f'<line x1="{cx-240}" y1="{y_rf_center}" x2="{cx-100}" y2="{y_rf_center}" class="arrow"/>')
    svg.append(f'<text x="{cx-140}" y="{y+30}" class="label">Không</text>')
    
    y += dy + 30
    # Bi-GRU
    svg.append(draw_rect(cx-120, y, 240, 50, "#f3e5f5", "#8e24aa", "Mô hình Bi-GRU", "Dự đoán hành vi"))
    svg.append(draw_arrow(cx, y+50, cx, y+dy))
    
    y += dy
    # Diamond 3: Té ngã?
    svg.append(draw_diamond(cx-100, y, 200, 80, "#ffcdd2", "#d32f2f", "Là hành vi", "Té ngã?"))
    svg.append(draw_arrow(cx, y+80, cx, y+dy+30))
    svg.append(f'<text x="{cx+20}" y="{y+100}" class="label">Có</text>')
    
    # False branch 3
    svg.append(f'<line x1="{cx+100}" y1="{y+40}" x2="{cx+200}" y2="{y+40}" class="line"/>')
    svg.append(f'<line x1="{cx+200}" y1="{y+40}" x2="{cx+200}" y2="{y_rf_center}" class="line"/>')
    svg.append(f'<line x1="{cx+200}" y1="{y_rf_center}" x2="{cx+100}" y2="{y_rf_center}" class="arrow"/>')
    svg.append(f'<text x="{cx+150}" y="{y+30}" class="label">Không</text>')
    
    y += dy + 30
    # Alert
    svg.append(draw_rect(cx-120, y, 240, 50, "#ffebee", "#d32f2f", "Gửi tín hiệu cảnh báo", "Hiển thị lên Web Dashboard"))
    # Arrow back to start
    svg.append(f'<line x1="{cx+120}" y1="{y+25}" x2="{cx+200}" y2="{y+25}" class="line"/>')
    
    svg.append('</svg>')
    path = os.path.join(artifact_dir, "hinh_2_3_flowchart.svg")
    with open(path, "w", encoding="utf-8") as f: f.write('\n'.join(svg))

hinh_2_1()
hinh_2_2()
hinh_2_3()
print("Done ch2")
