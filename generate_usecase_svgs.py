import os

artifact_dir = r"C:\Users\minhc\.gemini\antigravity\brain\65931094-baed-469f-9a6a-9b48ac195efe"

def draw_oval(x, y, w, h, text, text2=""):
    rx = h/2 # Make it an oval (capsule)
    res = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="#ffffff" stroke="#000000" stroke-width="2"/>'
    res += f'\n<text x="{x+w/2}" y="{y+h/2 - (8 if text2 else 0)}" class="text">{text}</text>'
    if text2:
        res += f'\n<text x="{x+w/2}" y="{y+h/2 + 12}" class="text2">{text2}</text>'
    return res

def draw_arrow(x1, y1, x2, y2, label=""):
    res = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="arrow"/>'
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        res += f'\n<rect x="{mx-35}" y="{my-12}" width="70" height="24" fill="#ffffff" rx="4" stroke="#ffffff"/>'
        res += f'\n<text x="{mx}" y="{my+4}" class="label">{label}</text>'
    return res

def hinh_2_1():
    svg = ['<svg width="950" height="250" viewBox="0 0 950 250" style="background-color: #ffffff;" xmlns="http://www.w3.org/2000/svg">']
    svg.append('<style>.text { font-family: Arial; font-weight: bold; font-size: 16px; text-anchor: middle; alignment-baseline: middle; fill: #000000; }')
    svg.append('.text2 { font-family: Arial; font-size: 14px; text-anchor: middle; alignment-baseline: middle; fill: #000000; }')
    svg.append('.arrow { stroke: #000000; stroke-width: 2px; fill: none; marker-end: url(#ah); }')
    svg.append('.label { font-family: Arial; font-size: 13px; text-anchor: middle; alignment-baseline: middle; fill: #000000; font-weight: bold; }')
    svg.append('</style>')
    svg.append('<defs><marker id="ah" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#000000" /></marker></defs>')
    
    # Blocks
    svg.append(draw_oval(50, 80, 120, 80, "Camera", "Video Stream"))
    svg.append(draw_arrow(170, 120, 230, 120, "Đầu vào"))
    
    svg.append(draw_oval(230, 80, 140, 80, "YOLOv11", "Phát hiện người"))
    svg.append(draw_arrow(370, 120, 430, 120, "Cắt vùng người"))
    
    svg.append(draw_oval(430, 80, 140, 80, "MediaPipe", "Trích xuất 33 khớp"))
    svg.append(draw_arrow(570, 120, 630, 120, "Tọa độ khớp"))
    
    svg.append(draw_oval(630, 80, 140, 80, "Bi-GRU", "Phân tích chuỗi"))
    svg.append(draw_arrow(770, 120, 830, 120, "Dự đoán"))
    
    svg.append(draw_oval(830, 80, 110, 80, "Kết quả", "Té ngã/Bình thường"))
    
    svg.append('</svg>')
    path = os.path.join(artifact_dir, "hinh_2_1_usecase.svg")
    with open(path, "w", encoding="utf-8") as f: f.write('\n'.join(svg))

def hinh_2_2():
    svg = ['<svg width="850" height="400" viewBox="0 0 850 400" style="background-color: #ffffff;" xmlns="http://www.w3.org/2000/svg">']
    svg.append('<style>.title { font-family: Arial; font-weight: bold; font-size: 18px; fill: #000000; }')
    svg.append('.text { font-family: Arial; font-weight: bold; font-size: 16px; text-anchor: middle; alignment-baseline: middle; fill: #000000; }')
    svg.append('.text2 { font-family: Arial; font-size: 13px; text-anchor: middle; alignment-baseline: middle; fill: #000000; }')
    svg.append('.arrow { stroke: #000000; stroke-width: 2px; fill: none; marker-end: url(#ah); marker-start: url(#ah-start); }')
    svg.append('.arrow-up { stroke: #000000; stroke-width: 2px; fill: none; marker-end: url(#ah); }')
    svg.append('</style>')
    svg.append('<defs>')
    svg.append('<marker id="ah" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#000000" /></marker>')
    svg.append('<marker id="ah-start" markerWidth="10" markerHeight="7" refX="1" refY="3.5" orient="auto"><polygon points="10 0, 0 3.5, 10 7" fill="#000000" /></marker>')
    svg.append('</defs>')
    
    layers = [
        {"x": 20, "w": 180, "title": "Lớp Dữ liệu", "boxes": [("Camera / Webcam", "Thời gian thực"), ("SisFall Dataset", "Huấn luyện")]},
        {"x": 230, "w": 200, "title": "Lớp AI & Xử lý", "boxes": [("YOLOv11-Pose", "Phát hiện đối tượng"), ("MediaPipe BlazePose", "Trích xuất khung xương"), ("Bi-GRU Model", "Phân loại hành vi")]},
        {"x": 460, "w": 180, "title": "Lớp Dịch vụ", "boxes": [("FastAPI Backend", "Xử lý API & Logic"), ("WebSocket", "Truyền phát video")]},
        {"x": 670, "w": 160, "title": "Lớp Giao diện", "boxes": [("Web Dashboard", "Giao diện hiển thị"), ("Alert System", "Cảnh báo té ngã")]}
    ]
    
    for i, L in enumerate(layers):
        x = L["x"]
        w = L["w"]
        svg.append(f'<rect x="{x}" y="40" width="{w}" height="320" rx="10" fill="#ffffff" stroke="#000000" stroke-width="2" stroke-dasharray="8,4"/>')
        svg.append(f'<text x="{x+w/2}" y="70" class="title" text-anchor="middle">{L["title"]}</text>')
        
        box_height = 250 // len(L["boxes"])
        for j, box in enumerate(L["boxes"]):
            by = 100 + j * box_height
            svg.append(draw_oval(x+10, by, w-20, box_height-20, box[0], box[1]))
            
        if i < len(layers) - 1:
            svg.append(f'<line x1="{x+w}" y1="200" x2="{layers[i+1]["x"]}" y2="200" class="arrow-up"/>')
            
    svg.append('</svg>')
    path = os.path.join(artifact_dir, "hinh_2_2_usecase.svg")
    with open(path, "w", encoding="utf-8") as f: f.write('\n'.join(svg))

def draw_diamond(x, y, w, h, text1, text2=""):
    pts = f"{x+w/2},{y} {x+w},{y+h/2} {x+w/2},{y+h} {x},{y+h/2}"
    res = f'<polygon points="{pts}" fill="#ffffff" stroke="#000000" stroke-width="2"/>'
    res += f'\n<text x="{x+w/2}" y="{y+h/2 - (8 if text2 else 0)}" class="text">{text1}</text>'
    if text2:
        res += f'\n<text x="{x+w/2}" y="{y+h/2 + 12}" class="text2">{text2}</text>'
    return res

def hinh_2_3():
    svg = ['<svg width="1250" height="400" viewBox="0 0 1250 400" style="background-color: #ffffff;" xmlns="http://www.w3.org/2000/svg">']
    svg.append('<style>.text { font-family: Arial; font-weight: bold; font-size: 14px; text-anchor: middle; alignment-baseline: middle; fill: #000000; }')
    svg.append('.text2 { font-family: Arial; font-size: 12px; text-anchor: middle; alignment-baseline: middle; fill: #000000; }')
    svg.append('.label { font-family: Arial; font-weight: bold; font-size: 13px; fill: #000000; text-anchor: middle; }')
    svg.append('.arrow { stroke: #000000; stroke-width: 2px; fill: none; marker-end: url(#ah); }')
    svg.append('.line { stroke: #000000; stroke-width: 2px; fill: none; }')
    svg.append('</style>')
    svg.append('<defs><marker id="ah" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#000000" /></marker></defs>')
    
    x = 20
    cy = 150
    dx = 140
    
    # Start
    svg.append(draw_oval(x, cy-25, 80, 50, "BẮT ĐẦU"))
    svg.append(draw_arrow(x+80, cy, x+120, cy))
    
    x += 100
    # Read frame
    svg.append(draw_oval(x, cy-35, 120, 70, "Đọc khung hình", "từ Camera"))
    svg.append(draw_arrow(x+120, cy, x+150, cy))
    
    read_x_center = x + 60
    
    x += 130
    # YOLO
    svg.append(draw_oval(x, cy-35, 120, 70, "YOLOv11-Pose", "Phát hiện người"))
    svg.append(draw_arrow(x+120, cy, x+150, cy))
    
    x += 130
    # Diamond 1
    svg.append(draw_diamond(x, cy-40, 100, 80, "Có phát hiện", "được người?"))
    svg.append(draw_arrow(x+100, cy, x+140, cy))
    svg.append(f'<text x="{x+120}" y="{cy-10}" class="label">Có</text>')
    
    svg.append(f'<line x1="{x+50}" y1="{cy-40}" x2="{x+50}" y2="{cy-100}" class="line"/>')
    svg.append(f'<line x1="{x+50}" y1="{cy-100}" x2="{read_x_center}" y2="{cy-100}" class="line"/>')
    svg.append(f'<line x1="{read_x_center}" y1="{cy-100}" x2="{read_x_center}" y2="{cy-35}" class="arrow"/>')
    svg.append(f'<text x="{x+75}" y="{cy-80}" class="label">Không</text>')
    
    x += 130
    # MediaPipe
    svg.append(draw_oval(x, cy-35, 120, 70, "MediaPipe", "Trích 33 khớp"))
    svg.append(draw_arrow(x+120, cy, x+150, cy))
    
    x += 130
    # Buffer
    svg.append(draw_oval(x, cy-35, 120, 70, "Cập nhật bộ đệm", "chuỗi thời gian"))
    svg.append(draw_arrow(x+120, cy, x+150, cy))
    
    x += 130
    # Diamond 2
    svg.append(draw_diamond(x, cy-40, 100, 80, "Đủ chuỗi", "30 frame?"))
    svg.append(draw_arrow(x+100, cy, x+140, cy))
    svg.append(f'<text x="{x+120}" y="{cy-10}" class="label">Có</text>')
    
    svg.append(f'<line x1="{x+50}" y1="{cy-40}" x2="{x+50}" y2="{cy-120}" class="line"/>')
    svg.append(f'<line x1="{x+50}" y1="{cy-120}" x2="{read_x_center-15}" y2="{cy-120}" class="line"/>')
    svg.append(f'<line x1="{read_x_center-15}" y1="{cy-120}" x2="{read_x_center-15}" y2="{cy-35}" class="arrow"/>')
    svg.append(f'<text x="{x+75}" y="{cy-100}" class="label">Không</text>')
    
    x += 130
    # Bi-GRU
    svg.append(draw_oval(x, cy-35, 120, 70, "Mô hình Bi-GRU", "Dự đoán hành vi"))
    svg.append(draw_arrow(x+120, cy, x+150, cy))
    
    x += 130
    # Diamond 3
    svg.append(draw_diamond(x, cy-40, 100, 80, "Là hành vi", "Té ngã?"))
    svg.append(draw_arrow(x+100, cy, x+140, cy))
    svg.append(f'<text x="{x+120}" y="{cy-10}" class="label">Có</text>')
    
    svg.append(f'<line x1="{x+50}" y1="{cy-40}" x2="{x+50}" y2="{cy-140}" class="line"/>')
    svg.append(f'<line x1="{x+50}" y1="{cy-140}" x2="{read_x_center-30}" y2="{cy-140}" class="line"/>')
    svg.append(f'<line x1="{read_x_center-30}" y1="{cy-140}" x2="{read_x_center-30}" y2="{cy-35}" class="arrow"/>')
    svg.append(f'<text x="{x+75}" y="{cy-120}" class="label">Không</text>')
    
    x += 130
    # Alert
    svg.append(draw_oval(x, cy-35, 120, 70, "Gửi cảnh báo", "lên Dashboard"))
    
    svg.append(f'<line x1="{x+60}" y1="{cy+35}" x2="{x+60}" y2="{cy+90}" class="line"/>')
    svg.append(f'<line x1="{x+60}" y1="{cy+90}" x2="{read_x_center}" y2="{cy+90}" class="line"/>')
    svg.append(f'<line x1="{read_x_center}" y1="{cy+90}" x2="{read_x_center}" y2="{cy+35}" class="arrow"/>')
    
    svg.append('</svg>')
    path = os.path.join(artifact_dir, "hinh_2_3_usecase.svg")
    with open(path, "w", encoding="utf-8") as f: f.write('\n'.join(svg))

hinh_2_1()
hinh_2_2()
hinh_2_3()
print("Done usecase svgs")
