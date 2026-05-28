import os

svg_content = """<svg viewBox="0 0 1000 650" width="1000" height="650" xmlns="http://www.w3.org/2000/svg">
  <!-- CSS -->
  <style>
    .title { font-family: 'Segoe UI', Arial, sans-serif; font-size: 26px; font-weight: bold; fill: #2b6cb0; }
    .subtitle { font-family: 'Segoe UI', Arial, sans-serif; font-size: 16px; fill: #4a5568; }
    .box-text { font-family: 'Segoe UI', Arial, sans-serif; font-size: 18px; font-weight: bold; fill: #2d3748; text-anchor: middle; alignment-baseline: middle; }
    .sub-text { font-family: 'Segoe UI', Arial, sans-serif; font-size: 15px; fill: #718096; text-anchor: middle; }
    .line { stroke: #2b6cb0; stroke-width: 3; marker-end: url(#arrow); }
    .nn-line { stroke: #cbd5e0; stroke-width: 1.5; }
    .nn-node-input { fill: #63b3ed; stroke: #3182ce; stroke-width: 2; }
    .nn-node-hidden { fill: #fbd38d; stroke: #dd6b20; stroke-width: 2; }
    .nn-node-output { fill: #9ae6b4; stroke: #38a169; stroke-width: 2; }
    .box { fill: #ffffff; stroke: #cbd5e0; stroke-width: 2; rx: 12; ry: 12; }
  </style>

  <!-- Defs for arrowheads -->
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#2b6cb0" />
    </marker>
  </defs>

  <!-- background -->
  <rect width="1000" height="650" fill="#f7fafc" rx="15" ry="15" />

  <!-- SECTION 1: MACHINE LEARNING -->
  <text x="500" y="50" class="title" text-anchor="middle">Học Máy (Machine Learning)</text>
  
  <!-- Input -->
  <rect x="80" y="80" width="140" height="80" class="box" />
  <text x="150" y="125" class="box-text">Đầu vào</text>
  <line x1="220" y1="120" x2="280" y2="120" class="line" />

  <!-- Feature Extraction -->
  <rect x="280" y="80" width="220" height="80" class="box" />
  <text x="390" y="125" class="box-text">Trích xuất đặc trưng</text>
  <line x1="500" y1="120" x2="560" y2="120" class="line" />

  <!-- Classification -->
  <rect x="560" y="80" width="160" height="80" class="box" />
  <text x="640" y="125" class="box-text">Phân loại</text>
  <line x1="720" y1="120" x2="780" y2="120" class="line" />

  <!-- Output -->
  <rect x="780" y="80" width="140" height="80" class="box" />
  <text x="850" y="125" class="box-text">Đầu ra</text>
  
  <text x="500" y="210" class="subtitle" text-anchor="middle">Học máy truyền thống sử dụng các đặc trưng được thiết kế thủ công, tốn nhiều thời gian và chi phí để phát triển.</text>

  <!-- Divider -->
  <line x1="50" y1="250" x2="950" y2="250" stroke="#e2e8f0" stroke-width="2" />

  <!-- SECTION 2: DEEP LEARNING -->
  <text x="500" y="300" class="title" text-anchor="middle">Học Sâu (Deep Learning)</text>

  <!-- Input -->
  <rect x="80" y="380" width="140" height="80" class="box" />
  <text x="150" y="425" class="box-text">Đầu vào</text>
  <line x1="220" y1="420" x2="260" y2="420" class="line" />

  <!-- Neural Network Box -->
  <rect x="260" y="320" width="480" height="250" class="box" fill="#ffffff" stroke="#e2e8f0" />
  <text x="500" y="550" class="title" style="font-size:20px; fill:#4a5568;" text-anchor="middle">Mạng Nơ-ron (Neural Networks)</text>
  
  <!-- NN Nodes generation will be injected here -->
  <g id="nn-nodes"></g>

  <!-- Output -->
  <line x1="740" y1="420" x2="780" y2="420" class="line" />
  <rect x="780" y="380" width="140" height="80" class="box" />
  <text x="850" y="425" class="box-text">Đầu ra</text>

  <text x="500" y="610" class="subtitle" text-anchor="middle">Học sâu tự động học các biểu diễn phân cấp trực tiếp từ dữ liệu, và tăng cường hiệu năng khi có nhiều dữ liệu hơn.</text>

</svg>
"""

# Generate NN connections
layers = [
    {"x": 310, "nodes": 5, "class": "nn-node-input", "label": "Nơ-ron\\nđầu vào"},
    {"x": 405, "nodes": 6, "class": "nn-node-hidden", "label": ""},
    {"x": 500, "nodes": 6, "class": "nn-node-hidden", "label": "Các nơ-ron ẩn"},
    {"x": 595, "nodes": 6, "class": "nn-node-hidden", "label": ""},
    {"x": 690, "nodes": 4, "class": "nn-node-output", "label": "Nơ-ron\\nđầu ra"}
]

nn_svg = ""
# Draw lines
for i in range(len(layers)-1):
    l1 = layers[i]
    l2 = layers[i+1]
    y_start1 = 420 - (l1["nodes"]-1)*13
    y_start2 = 420 - (l2["nodes"]-1)*13
    for n1 in range(l1["nodes"]):
        for n2 in range(l2["nodes"]):
            y1 = y_start1 + n1*26
            y2 = y_start2 + n2*26
            nn_svg += f'<line x1="{l1["x"]}" y1="{y1}" x2="{l2["x"]}" y2="{y2}" class="nn-line" />\n'

# Draw nodes
for l in layers:
    y_start = 420 - (l["nodes"]-1)*13
    for n in range(l["nodes"]):
        y = y_start + n*26
        nn_svg += f'<circle cx="{l["x"]}" cy="{y}" r="9" class="{l["class"]}" />\n'
    
    # Label
    if l["label"]:
        lines = l["label"].split("\\n")
        y_text = 420 + 3*26 + 15
        for idx, line in enumerate(lines):
            nn_svg += f'<text x="{l["x"]}" y="{y_text + idx*18}" class="sub-text">{line}</text>\n'

svg_content = svg_content.replace('<g id="nn-nodes"></g>', nn_svg)

artifact_dir = r"C:\Users\minhc\.gemini\antigravity\brain\65931094-baed-469f-9a6a-9b48ac195efe"
path = os.path.join(artifact_dir, "machine_learning_vs_deep_learning.svg")
with open(path, "w", encoding="utf-8") as f:
    f.write(svg_content)
print(f"SVG created at {path}")
