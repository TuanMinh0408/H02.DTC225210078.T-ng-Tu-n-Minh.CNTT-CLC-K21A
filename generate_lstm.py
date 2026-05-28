import os

svg_content = '''<svg width="1000" height="550" viewBox="0 0 1000 550" xmlns="http://www.w3.org/2000/svg">
    <style>
        .box-sig { fill: #f06292; stroke: #c2185b; stroke-width: 2px; rx: 8px; }
        .box-tanh { fill: #f57c00; stroke: #e65100; stroke-width: 2px; rx: 8px; }
        .circle-mul { fill: #ffee58; stroke: #fbc02d; stroke-width: 2px; }
        .circle-add { fill: #81c784; stroke: #388e3c; stroke-width: 2px; }
        .line { stroke: #000; stroke-width: 2px; fill: none; }
        .arrow { stroke: #000; stroke-width: 2px; fill: none; marker-end: url(#arrowhead); }
        .dashed-box { fill: none; stroke: #00838f; stroke-width: 2px; stroke-dasharray: 6,6; rx: 15px; }
        .text { font-family: 'Segoe UI', Arial, sans-serif; font-size: 16px; font-weight: 500; fill: #000; text-anchor: middle; alignment-baseline: middle; }
        .text-math { font-family: 'Cambria Math', 'Times New Roman', serif; font-size: 26px; font-weight: bold; font-style: italic; fill: #000; text-anchor: middle; }
        .text-small { font-family: 'Segoe UI', Arial, sans-serif; font-size: 14px; font-weight: bold; fill: #00838f; text-anchor: middle; alignment-baseline: middle; }
        .bg-cell { fill: #e0f2f1; stroke: #b2dfdb; stroke-width: 3px; rx: 40px; }
    </style>
    <defs>
        <marker id="arrowhead" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
            <polygon points="0 0, 8 3, 0 6" fill="#000" />
        </marker>
    </defs>
    
    <!-- Cell Background -->
    <rect x="50" y="50" width="700" height="430" class="bg-cell" />
    <text x="400" y="520" class="text" style="font-size:22px; font-weight:bold;">LSTM CELL</text>
    
    <!-- Dashed Boxes -->
    <!-- Cell State -->
    <rect x="110" y="70" width="340" height="80" class="dashed-box" />
    <text x="280" y="90" class="text-small">Cell State</text>
    
    <!-- Forget Gate -->
    <rect x="110" y="160" width="80" height="190" class="dashed-box" />
    <text x="150" y="180" class="text-small">Forget Gate</text>
    
    <!-- Input Gate -->
    <rect x="250" y="160" width="190" height="190" class="dashed-box" />
    <text x="345" y="180" class="text-small">Input Gate</text>
    
    <!-- Output Gate -->
    <rect x="460" y="160" width="130" height="190" class="dashed-box" />
    <text x="525" y="335" class="text-small">Output Gate</text>
    
    <!-- Connecting Lines -->
    <!-- Cell State Line -->
    <line x1="10" y1="120" x2="135" y2="120" class="arrow" />
    <line x1="165" y1="120" x2="385" y2="120" class="arrow" />
    <line x1="415" y1="120" x2="780" y2="120" class="arrow" />
    <line x1="500" y1="120" x2="500" y2="155" class="arrow" />
    <circle cx="500" cy="120" r="4" fill="#000" />
    
    <!-- Bottom Line (h_t-1 and x_t) -->
    <line x1="10" y1="400" x2="550" y2="400" class="line" />
    <line x1="100" y1="480" x2="100" y2="400" class="line" />
    <circle cx="100" cy="400" r="4" fill="#000" />
    
    <line x1="150" y1="400" x2="150" y2="345" class="arrow" />
    <circle cx="150" cy="400" r="4" fill="#000" />
    
    <line x1="300" y1="400" x2="300" y2="345" class="arrow" />
    <circle cx="300" cy="400" r="4" fill="#000" />
    
    <line x1="400" y1="400" x2="400" y2="345" class="arrow" />
    <circle cx="400" cy="400" r="4" fill="#000" />
    
    <line x1="550" y1="400" x2="550" y2="345" class="arrow" />
    
    <!-- Inside Gates -->
    <!-- Forget Gate -->
    <line x1="150" y1="295" x2="150" y2="135" class="arrow" />
    <text x="135" y="240" class="text-math" style="font-size:20px;">f<tspan dy="5" font-size="14">t</tspan></text>
    
    <!-- Input Gate -->
    <line x1="300" y1="295" x2="300" y2="220" class="line" />
    <line x1="300" y1="220" x2="385" y2="220" class="arrow" />
    <text x="285" y="240" class="text-math" style="font-size:20px;">i<tspan dy="5" font-size="14">t</tspan></text>
    
    <line x1="400" y1="295" x2="400" y2="235" class="arrow" />
    <text x="425" y="260" class="text-math" style="font-size:20px;">C̃<tspan dy="5" font-size="14">t</tspan></text>
    
    <line x1="400" y1="205" x2="400" y2="135" class="arrow" />
    
    <!-- Output Gate -->
    <line x1="500" y1="205" x2="500" y2="250" class="line" />
    <line x1="500" y1="250" x2="535" y2="250" class="arrow" />
    
    <line x1="550" y1="295" x2="550" y2="265" class="arrow" />
    <text x="565" y="280" class="text-math" style="font-size:20px;">o<tspan dy="5" font-size="14">t</tspan></text>
    
    <line x1="565" y1="250" x2="650" y2="250" class="line" />
    <line x1="650" y1="250" x2="650" y2="180" class="arrow" />
    <line x1="650" y1="250" x2="780" y2="250" class="arrow" />
    <circle cx="650" cy="250" r="4" fill="#000" />
    
    <!-- Nodes -->
    <!-- sig1 -->
    <rect x="120" y="295" width="60" height="50" class="box-sig" />
    <text x="150" y="322" class="text" fill="white">sig</text>
    
    <!-- sig2 -->
    <rect x="270" y="295" width="60" height="50" class="box-sig" />
    <text x="300" y="322" class="text" fill="white">sig</text>
    
    <!-- tanh1 -->
    <rect x="370" y="295" width="60" height="50" class="box-tanh" />
    <text x="400" y="322" class="text" fill="white">tanh</text>
    
    <!-- sig3 -->
    <rect x="520" y="295" width="60" height="50" class="box-sig" />
    <text x="550" y="322" class="text" fill="white">sig</text>
    
    <!-- tanh2 -->
    <rect x="470" y="155" width="60" height="50" class="box-tanh" />
    <text x="500" y="182" class="text" fill="white">tanh</text>
    
    <!-- X1 -->
    <circle cx="150" cy="120" r="15" class="circle-mul" />
    <line x1="141" y1="111" x2="159" y2="129" class="line" />
    <line x1="159" y1="111" x2="141" y2="129" class="line" />
    
    <!-- +1 -->
    <circle cx="400" cy="120" r="15" class="circle-add" />
    <line x1="388" y1="120" x2="412" y2="120" class="line" />
    <line x1="400" y1="108" x2="400" y2="132" class="line" />
    
    <!-- X2 -->
    <circle cx="400" cy="220" r="15" class="circle-mul" />
    <line x1="391" y1="211" x2="409" y2="229" class="line" />
    <line x1="409" y1="211" x2="391" y2="229" class="line" />
    
    <!-- X3 -->
    <circle cx="550" cy="250" r="15" class="circle-mul" />
    <line x1="541" y1="241" x2="559" y2="259" class="line" />
    <line x1="559" y1="241" x2="541" y2="259" class="line" />
    
    <!-- Math Labels -->
    <text x="25" y="105" class="text-math">C<tspan dy="8" font-size="16">t-1</tspan></text>
    <text x="765" y="105" class="text-math">C<tspan dy="8" font-size="16">t</tspan></text>
    <text x="25" y="385" class="text-math">h<tspan dy="8" font-size="16">t-1</tspan></text>
    <text x="650" y="160" class="text-math">h<tspan dy="8" font-size="16">t</tspan></text>
    <text x="765" y="235" class="text-math">h<tspan dy="8" font-size="16">t</tspan></text>
    <text x="85" y="475" class="text-math">x<tspan dy="8" font-size="16">t</tspan></text>

    <!-- Legend -->
    <g transform="translate(780, 70)">
        <rect x="0" y="0" width="70" height="35" class="box-sig" />
        <text x="35" y="19" class="text" fill="white">sig</text>
        <text x="80" y="19" class="text" style="text-anchor: start;">- Sigmoid function</text>
        
        <rect x="0" y="60" width="70" height="35" class="box-tanh" />
        <text x="35" y="79" class="text" fill="white">tanh</text>
        <text x="80" y="79" class="text" style="text-anchor: start;">- tanh function</text>
        
        <circle cx="35" cy="140" r="15" class="circle-mul" />
        <line x1="26" y1="131" x2="44" y2="149" class="line" />
        <line x1="44" y1="131" x2="26" y2="149" class="line" />
        <text x="80" y="132" class="text" style="text-anchor: start;">- point-by-point</text>
        <text x="90" y="152" class="text" style="text-anchor: start;">multiplication</text>
        
        <circle cx="35" cy="210" r="15" class="circle-add" />
        <line x1="23" y1="210" x2="47" y2="210" class="line" />
        <line x1="35" y1="198" x2="35" y2="222" class="line" />
        <text x="80" y="202" class="text" style="text-anchor: start;">- point-by-point</text>
        <text x="90" y="222" class="text" style="text-anchor: start;">addition</text>
        
        <line x1="10" y1="280" x2="60" y2="280" class="arrow" />
        <text x="80" y="280" class="text" style="text-anchor: start;">- vector connection</text>
    </g>
</svg>
'''

artifact_dir = r"C:\Users\minhc\.gemini\antigravity\brain\65931094-baed-469f-9a6a-9b48ac195efe"
path = os.path.join(artifact_dir, "lstm_cell_diagram.svg")
with open(path, "w", encoding="utf-8") as f:
    f.write(svg_content)
print(f"SVG created at {path}")
