import urllib.request
import urllib.parse
from docx import Document
from docx.shared import Inches
import os

def download_image(dot_string, filename):
    encoded = urllib.parse.quote(dot_string)
    url = f"https://quickchart.io/graphviz?graph={encoded}&format=png"
    urllib.request.urlretrieve(url, filename)

dot1 = """digraph G {
    rankdir=LR;
    node [shape=ellipse, style="filled", fillcolor=white, color=black, fontname="Arial", fontsize=12, penwidth=2];
    edge [color=black, fontname="Arial", fontsize=10, penwidth=1.5];
    
    A [label="Camera\\nVideo Stream"];
    B [label="YOLOv11-Pose\\nPhát hiện người"];
    C [label="MediaPipe BlazePose\\nTrích xuất 33 khớp"];
    D [label="Bi-GRU\\nPhân tích chuỗi"];
    E [label="Kết quả\\nTé ngã/Bình thường"];
    
    A -> B [label=" Đầu vào"];
    B -> C [label=" Cắt vùng người"];
    C -> D [label=" Tọa độ khớp"];
    D -> E [label=" Dự đoán"];
}"""

dot2 = """digraph G {
    rankdir=LR;
    node [shape=ellipse, style="filled", fillcolor=white, color=black, fontname="Arial", fontsize=12, penwidth=2];
    edge [color=black, penwidth=1.5];
    
    subgraph cluster_0 {
        label = "Lớp Dữ liệu"; style="dashed"; color="black"; fontname="Arial"; fontsize=14; penwidth=2;
        C1 [label="Camera\\nThời gian thực"];
        D1 [label="SisFall Dataset\\nHuấn luyện"];
    }
    
    subgraph cluster_1 {
        label = "Lớp AI & Xử lý"; style="dashed"; color="black"; fontname="Arial"; fontsize=14; penwidth=2;
        A1 [label="YOLOv11-Pose\\nPhát hiện đối tượng"];
        A2 [label="MediaPipe\\nTrích xuất khung xương"];
        A3 [label="Bi-GRU Model\\nPhân loại hành vi"];
        A1 -> A2;
        A2 -> A3;
    }
    
    subgraph cluster_2 {
        label = "Lớp Dịch vụ"; style="dashed"; color="black"; fontname="Arial"; fontsize=14; penwidth=2;
        S1 [label="FastAPI Backend\\nXử lý API"];
        S2 [label="WebSocket\\nTruyền phát video"];
        S1 -> S2;
    }
    
    subgraph cluster_3 {
        label = "Lớp Giao diện"; style="dashed"; color="black"; fontname="Arial"; fontsize=14; penwidth=2;
        U1 [label="Web Dashboard\\nGiao diện"];
        U2 [label="Alert System\\nCảnh báo"];
    }
    
    C1 -> A1;
    D1 -> A1;
    A3 -> S1;
    S2 -> U1;
    S2 -> U2;
}"""

dot3 = """digraph G {
    rankdir=LR;
    node [shape=ellipse, style="filled", fillcolor=white, color=black, fontname="Arial", fontsize=12, penwidth=2];
    edge [color=black, fontname="Arial", fontsize=10, penwidth=1.5];
    
    Start [shape=ellipse, label="BẮT ĐẦU", penwidth=3];
    Read [label="Đọc khung hình\\ntừ Camera"];
    YOLO [label="YOLOv11-Pose\\nPhát hiện người"];
    D1 [shape=diamond, label="Có phát hiện\\nđược người?"];
    MP [label="MediaPipe\\nTrích 33 khớp"];
    Buffer [label="Cập nhật bộ đệm\\nchuỗi thời gian"];
    D2 [shape=diamond, label="Đủ chuỗi\\n30 frame?"];
    BiGRU [label="Mô hình Bi-GRU\\nDự đoán hành vi"];
    D3 [shape=diamond, label="Là hành vi\\nTé ngã?"];
    Alert [label="Gửi cảnh báo\\nlên Dashboard"];
    
    Start -> Read;
    Read -> YOLO;
    YOLO -> D1;
    D1 -> MP [label="Có"];
    D1 -> Read [label="Không"];
    
    MP -> Buffer;
    Buffer -> D2;
    D2 -> BiGRU [label="Có"];
    D2 -> Read [label="Không"];
    
    BiGRU -> D3;
    D3 -> Alert [label="Có"];
    D3 -> Read [label="Không"];
    
    Alert -> Read;
}"""

print("Downloading images via API...")
download_image(dot1, "img_2_1.png")
download_image(dot2, "img_2_2.png")
download_image(dot3, "img_2_3.png")

print("Creating docx...")
doc = Document()
doc.add_heading('Sơ đồ Chương 2 (Chuẩn Use Case - Nền trắng chữ đen)', 0)

p1 = doc.add_paragraph()
r1 = p1.add_run('Hình 2.1: Sơ đồ luồng kết hợp YOLO và trích xuất khung xương')
r1.bold = True
doc.add_picture("img_2_1.png", width=Inches(6.0))

p2 = doc.add_paragraph()
r2 = p2.add_run('\nHình 2.2: Sơ đồ kiến trúc tổng thể hệ thống')
r2.bold = True
doc.add_picture("img_2_2.png", width=Inches(6.0))

p3 = doc.add_paragraph()
r3 = p3.add_run('\nHình 2.3: Lưu đồ thuật toán quy trình phát hiện té ngã')
r3.bold = True
doc.add_picture("img_2_3.png", width=Inches(6.0))

save_path = r'C:\Users\minhc\.gemini\antigravity\scratch\graduation_project\Sodo_Chuong2.docx'
doc.save(save_path)
print(f"Done. Saved to {save_path}")
