import os

artifact_dir = r"C:\Users\minhc\.gemini\antigravity\brain\1b5195ce-045e-49d6-92c5-0c030661329e"

def draw_rect(x, y, w, h, fill, stroke, text, text2="", rx=8):
    res = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
    res += f'\n<text x="{x+w/2}" y="{y+h/2 - (10 if text2 else 0)}" class="text">{text}</text>'
    if text2:
        res += f'\n<text x="{x+w/2}" y="{y+h/2 + 15}" class="text2">{text2}</text>'
    return res

def draw_arrow(x1, y1, x2, y2, label="", vertical=False):
    res = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="arrow"/>'
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        if vertical:
            res += f'\n<rect x="{mx+5}" y="{my-12}" width="{len(label)*8}" height="24" fill="white" rx="4"/>'
            res += f'\n<text x="{mx+5 + len(label)*4}" y="{my+4}" class="label">{label}</text>'
        else:
            res += f'\n<rect x="{mx-len(label)*4}" y="{my-18}" width="{len(label)*8}" height="20" fill="white" rx="4"/>'
            res += f'\n<text x="{mx}" y="{my-5}" class="label">{label}</text>'
    return res

def draw_dashed_arrow(x1, y1, x2, y2):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="dashed-arrow"/>'

def hinh_1_arch():
    svg = ['<svg width="750" height="550" viewBox="0 0 750 550" xmlns="http://www.w3.org/2000/svg">']
    svg.append('<style>.title { font-family: Arial; font-weight: bold; font-size: 20px; fill: #1e3a5f; }')
    svg.append('.text { font-family: Arial; font-weight: bold; font-size: 16px; text-anchor: middle; alignment-baseline: middle; fill: #333; }')
    svg.append('.text2 { font-family: Arial; font-size: 14px; text-anchor: middle; alignment-baseline: middle; fill: #555; }')
    svg.append('.arrow { stroke: #555; stroke-width: 2.5px; fill: none; marker-end: url(#ah); }')
    svg.append('.dashed-arrow { stroke: #555; stroke-width: 2.5px; fill: none; stroke-dasharray: 5,5; marker-end: url(#ah); }')
    svg.append('.label { font-family: Arial; font-size: 12px; font-weight: bold; fill: #d32f2f; text-anchor: middle; }')
    svg.append('</style>')
    svg.append('<defs><marker id="ah" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#555" /></marker></defs>')
    
    # Layers (from bottom to top)
    layers = [
        {"y": 420, "color": "#f3e5f5", "border": "#8e24aa", "title": "Lớp Lưu trữ (Storage Layer)", "boxes": [("SQLite Database", "Lưu lịch sử cảnh báo"), ("Hệ thống File", "Lưu ảnh va chạm")]},
        {"y": 300, "color": "#e3f2fd", "border": "#1e88e5", "title": "Lớp Server & AI (FastAPI Backend)", "boxes": [("YOLOv11-Pose", "Nhận diện & Khung xương"), ("Heuristics & Bi-LSTM", "Phân tích té ngã")]},
        {"y": 180, "color": "#e8f5e9", "border": "#43a047", "title": "Lớp Giao tiếp (Communication Layer)", "boxes": [("WebSocket", "Truyền video thời gian thực"), ("REST API", "Lấy thống kê/lịch sử")]},
        {"y": 60, "color": "#fff3e0", "border": "#fb8c00", "title": "Lớp Người dùng (Client Layer)", "boxes": [("Webcam / IP Camera", "Truyền dữ liệu hình ảnh"), ("Web Dashboard", "Nhận cảnh báo trực quan")]}
    ]
    
    for i, L in enumerate(layers):
        y = L["y"]
        svg.append(f'<rect x="50" y="{y}" width="650" height="100" rx="10" fill="{L["color"]}" stroke="{L["border"]}" stroke-width="2"/>')
        svg.append(f'<text x="60" y="{y+25}" style="text-anchor:start;" class="title">{L["title"]}</text>')
        box_width = 610 // len(L["boxes"])
        for j, box in enumerate(L["boxes"]):
            bx = 70 + j * box_width
            svg.append(f'<rect x="{bx}" y="{y+40}" width="{box_width-20}" height="50" rx="5" fill="#ffffff" stroke="#ccc" stroke-width="1"/>')
            svg.append(f'<text x="{bx + (box_width-20)/2}" y="{y+60}" class="text">{box[0]}</text>')
            svg.append(f'<text x="{bx + (box_width-20)/2}" y="{y+80}" class="text2">{box[1]}</text>')
            
    # Arrows between layers
    svg.append(draw_arrow(210, 160, 210, 180)) # Camera -> WS
    svg.append(draw_arrow(510, 180, 510, 160)) # REST API -> Dashboard
    svg.append(draw_arrow(540, 160, 540, 180)) # Dashboard -> REST API
    
    svg.append(draw_arrow(210, 280, 210, 300)) # WS -> YOLO
    svg.append(draw_arrow(510, 300, 510, 280)) # Bi-LSTM -> WS (Alert)
    
    svg.append(draw_arrow(510, 400, 510, 420)) # AI -> SQLite
    
    svg.append('</svg>')
    path = os.path.join(artifact_dir, "hinh_1_architecture.svg")
    with open(path, "w", encoding="utf-8") as f: f.write('\n'.join(svg))

def draw_diamond(x, y, w, h, fill, stroke, text1, text2=""):
    pts = f"{x+w/2},{y} {x+w},{y+h/2} {x+w/2},{y+h} {x},{y+h/2}"
    res = f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
    res += f'\n<text x="{x+w/2}" y="{y+h/2 - (8 if text2 else 0)}" class="text">{text1}</text>'
    if text2:
        res += f'\n<text x="{x+w/2}" y="{y+h/2 + 12}" class="text2">{text2}</text>'
    return res

def hinh_2_pipeline():
    svg = ['<svg width="700" height="850" viewBox="0 0 700 850" xmlns="http://www.w3.org/2000/svg">']
    svg.append('<style>.text { font-family: Arial; font-weight: bold; font-size: 15px; text-anchor: middle; alignment-baseline: middle; fill: #333; }')
    svg.append('.text2 { font-family: Arial; font-size: 13px; text-anchor: middle; alignment-baseline: middle; fill: #555; }')
    svg.append('.label { font-family: Arial; font-weight: bold; font-size: 13px; fill: #d32f2f; text-anchor: middle; }')
    svg.append('.arrow { stroke: #555; stroke-width: 2.5px; fill: none; marker-end: url(#ah); }')
    svg.append('.line { stroke: #555; stroke-width: 2.5px; fill: none; }')
    svg.append('</style>')
    svg.append('<defs><marker id="ah" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#555" /></marker></defs>')
    
    cx = 350
    y = 30
    dy = 100
    
    # Bắt đầu (Oval)
    svg.append(draw_rect(cx-100, y, 200, 50, "#cfd8dc", "#607d8b", "Khung hình Camera", "RGB 640x480", rx=25))
    svg.append(draw_arrow(cx, y+50, cx, y+dy))
    
    y += dy
    # YOLO
    svg.append(draw_rect(cx-130, y, 260, 60, "#fff3e0", "#fb8c00", "YOLOv11-Pose", "Trích xuất tọa độ 17 điểm khớp"))
    svg.append(draw_arrow(cx, y+60, cx, y+dy))
    
    y += dy
    # Heuristics
    svg.append(draw_rect(cx-160, y, 320, 70, "#e3f2fd", "#1e88e5", "Bộ lọc Heuristics (Quy luật vật lý)", "- Vận tốc hông (Velocity)\n- Tỷ lệ khung bao\n- Vị trí đầu"))
    svg.append(f'<text x="{cx}" y="{y+45}" class="text2">- Vận tốc rơi (Velocity)</text>')
    svg.append(f'<text x="{cx}" y="{y+60}" class="text2">- Tỷ lệ khung bao & Vị trí đầu thấp</text>')
    svg.append(draw_arrow(cx, y+70, cx, y+dy+10))
    
    y += dy + 10
    # Diamond 1: Khả nghi?
    svg.append(draw_diamond(cx-110, y, 220, 80, "#fff9c4", "#fbc02d", "Có dấu hiệu", "bất thường?"))
    svg.append(draw_arrow(cx, y+80, cx, y+dy+30))
    svg.append(f'<text x="{cx+20}" y="{y+100}" class="label">Có</text>')
    
    # False branch
    svg.append(f'<line x1="{cx-110}" y1="{y+40}" x2="{cx-240}" y2="{y+40}" class="line"/>')
    svg.append(f'<line x1="{cx-240}" y1="{y+40}" x2="{cx-240}" y2="{40}" class="line"/>')
    svg.append(f'<line x1="{cx-240}" y1="{40}" x2="{cx-100}" y2="{40}" class="arrow"/>')
    svg.append(f'<text x="{cx-170}" y="{y+30}" class="label">Bình thường (Bỏ qua)</text>')
    
    y += dy + 30
    # Bi-LSTM
    svg.append(draw_rect(cx-140, y, 280, 60, "#f3e5f5", "#8e24aa", "Mô hình Bi-LSTM + Attention", "Phân tích chuỗi động học thời gian"))
    svg.append(draw_arrow(cx, y+60, cx, y+dy+10))
    
    y += dy + 10
    # Diamond 2: Té ngã?
    svg.append(draw_diamond(cx-110, y, 220, 80, "#ffcdd2", "#d32f2f", "Kết luận là", "Té ngã (Fall)?"))
    svg.append(draw_arrow(cx, y+80, cx, y+dy+30))
    svg.append(f'<text x="{cx+20}" y="{y+100}" class="label">Có</text>')
    
    # False branch 2
    svg.append(f'<line x1="{cx+110}" y1="{y+40}" x2="{cx+240}" y2="{y+40}" class="line"/>')
    svg.append(f'<line x1="{cx+240}" y1="{y+40}" x2="{cx+240}" y2="{40}" class="line"/>')
    svg.append(f'<line x1="{cx+240}" y1="{40}" x2="{cx+100}" y2="{40}" class="arrow"/>')
    svg.append(f'<text x="{cx+170}" y="{y+30}" class="label">Nhầm lẫn (Bỏ qua)</text>')
    
    y += dy + 30
    # Alert
    svg.append(draw_rect(cx-150, y, 300, 60, "#ffebee", "#d32f2f", "Gửi cảnh báo WebSocket", "& Lưu vết CSDL SQLite"))
    
    svg.append('</svg>')
    path = os.path.join(artifact_dir, "hinh_2_pipeline.svg")
    with open(path, "w", encoding="utf-8") as f: f.write('\n'.join(svg))

hinh_1_arch()
hinh_2_pipeline()
print("Thành công! Đã tạo xong 2 hình SVG siêu đẹp không bị đè chữ.")
