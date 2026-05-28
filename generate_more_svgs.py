import os

artifact_dir = r"C:\Users\minhc\.gemini\antigravity\brain\65931094-baed-469f-9a6a-9b48ac195efe"

def create_confusion_matrix():
    svg = '''<svg width="600" height="420" viewBox="0 0 600 420" xmlns="http://www.w3.org/2000/svg">
        <style>
            .text { font-family: Arial, sans-serif; fill: #000; text-anchor: middle; alignment-baseline: middle; }
            .header { font-size: 20px; font-weight: bold; fill: #1e3a5f; }
            .label { font-size: 18px; font-weight: bold; }
            .value { font-size: 20px; font-weight: bold; }
            .desc { font-size: 14px; fill: #555; }
            .box-tp { fill: #e8f5e9; stroke: #4caf50; stroke-width: 2px; rx: 8px; }
            .box-tn { fill: #e8f5e9; stroke: #4caf50; stroke-width: 2px; rx: 8px; }
            .box-fp { fill: #ffebee; stroke: #f44336; stroke-width: 2px; rx: 8px; }
            .box-fn { fill: #ffebee; stroke: #f44336; stroke-width: 2px; rx: 8px; }
        </style>
        
        <text x="350" y="40" class="text header">Giá trị Dự đoán (Predicted)</text>
        <text x="250" y="80" class="text label">Positive (1)</text>
        <text x="450" y="80" class="text label">Negative (0)</text>
        
        <text x="40" y="240" class="text header" transform="rotate(-90 40,240)">Giá trị Thực tế (Actual)</text>
        <text x="90" y="170" class="text label" transform="rotate(-90 90,170)">Positive (1)</text>
        <text x="90" y="310" class="text label" transform="rotate(-90 90,310)">Negative (0)</text>
        
        <rect x="150" y="100" width="190" height="130" class="box-tp" />
        <text x="245" y="145" class="text value" fill="#2e7d32">True Positive (TP)</text>
        <text x="245" y="175" class="text desc">Dự đoán đúng</text>
        <text x="245" y="195" class="text desc">mẫu Positive</text>
        
        <rect x="350" y="100" width="190" height="130" class="box-fn" />
        <text x="445" y="145" class="text value" fill="#c62828">False Negative (FN)</text>
        <text x="445" y="175" class="text desc">Dự đoán sai mẫu</text>
        <text x="445" y="195" class="text desc">Positive thành Negative</text>
        
        <rect x="150" y="240" width="190" height="130" class="box-fp" />
        <text x="245" y="285" class="text value" fill="#c62828">False Positive (FP)</text>
        <text x="245" y="315" class="text desc">Dự đoán sai mẫu</text>
        <text x="245" y="335" class="text desc">Negative thành Positive</text>
        
        <rect x="350" y="240" width="190" height="130" class="box-tn" />
        <text x="445" y="285" class="text value" fill="#2e7d32">True Negative (TN)</text>
        <text x="445" y="315" class="text desc">Dự đoán đúng</text>
        <text x="445" y="335" class="text desc">mẫu Negative</text>
    </svg>'''
    path = os.path.join(artifact_dir, "confusion_matrix.svg")
    with open(path, "w", encoding="utf-8") as f: f.write(svg)

def generate_network_svg(filename, dropped=False):
    layers = [
        {'x': 150, 'nodes': 4, 'color': '#2196f3', 'label': 'Lớp đầu vào\\n(Input Layer)'},
        {'x': 350, 'nodes': 6, 'color': '#4caf50', 'label': 'Lớp ẩn 1\\n(Hidden Layer)'},
        {'x': 550, 'nodes': 6, 'color': '#4caf50', 'label': 'Lớp ẩn 2\\n(Hidden Layer)'},
        {'x': 750, 'nodes': 2, 'color': '#ff9800', 'label': 'Lớp đầu ra\\n(Output Layer)'}
    ]
    
    active_nodes = {
        0: [0, 1, 2, 3],
        1: [0, 1, 2, 3, 4, 5],
        2: [0, 1, 2, 3, 4, 5],
        3: [0, 1]
    }
    
    if dropped:
        active_nodes[1] = [0, 2, 5]
        active_nodes[2] = [1, 4]

    svg = ['<svg width="900" height="500" viewBox="0 0 900 500" xmlns="http://www.w3.org/2000/svg">']
    svg.append('<style>')
    svg.append('.node { stroke: #fff; stroke-width: 2px; }')
    svg.append('.node-dropped { fill: #f5f5f5; stroke: #e0e0e0; stroke-width: 2px; stroke-dasharray: 4,4; }')
    svg.append('.line { stroke: #bbdefb; stroke-width: 1.5px; opacity: 0.8; }')
    svg.append('.line-dropped { stroke: #f5f5f5; stroke-width: 1px; opacity: 0.5; stroke-dasharray: 4,4; }')
    svg.append('.text { font-family: Arial, sans-serif; text-anchor: middle; font-size: 16px; font-weight: bold; fill: #333; }')
    svg.append('</style>')

    coords = {}
    for l_idx, layer in enumerate(layers):
        coords[l_idx] = []
        n_nodes = layer['nodes']
        spacing = 60
        start_y = 230 - (n_nodes - 1) * spacing / 2
        for n_idx in range(n_nodes):
            coords[l_idx].append((layer['x'], start_y + n_idx * spacing))

    # Draw lines
    for l_idx in range(len(layers) - 1):
        for n1 in range(layers[l_idx]['nodes']):
            for n2 in range(layers[l_idx+1]['nodes']):
                x1, y1 = coords[l_idx][n1]
                x2, y2 = coords[l_idx+1][n2]
                if n1 in active_nodes[l_idx] and n2 in active_nodes[l_idx+1]:
                    svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="line" />')
                elif dropped:
                    svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="line-dropped" />')
                else:
                    svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="line" />')

    # Draw nodes
    for l_idx, layer in enumerate(layers):
        for n_idx in range(layer['nodes']):
            x, y = coords[l_idx][n_idx]
            if n_idx in active_nodes[l_idx]:
                svg.append(f'<circle cx="{x}" cy="{y}" r="22" class="node" fill="{layer["color"]}" />')
            else:
                svg.append(f'<circle cx="{x}" cy="{y}" r="22" class="node-dropped" />')
                svg.append(f'<line x1="{x-10}" y1="{y-10}" x2="{x+10}" y2="{y+10}" stroke="#bdbdbd" stroke-width="3" />')
                svg.append(f'<line x1="{x-10}" y1="{y+10}" x2="{x+10}" y2="{y-10}" stroke="#bdbdbd" stroke-width="3" />')

    # Draw labels
    for l_idx, layer in enumerate(layers):
        labels = layer['label'].split('\\n')
        x = layer['x']
        svg.append(f'<text x="{x}" y="450" class="text">{labels[0]}</text>')
        if len(labels) > 1:
            svg.append(f'<text x="{x}" y="470" class="text" style="font-size:14px; fill:#666;">{labels[1]}</text>')

    svg.append('</svg>')
    
    path = os.path.join(artifact_dir, filename)
    with open(path, "w", encoding="utf-8") as f: f.write('\\n'.join(svg))

create_confusion_matrix()
generate_network_svg("neural_network.svg", dropped=False)
generate_network_svg("dropout.svg", dropped=True)
print("Done")
