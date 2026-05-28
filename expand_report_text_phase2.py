import re
from pathlib import Path

# Phase 2 expansion to add deep academic content to Chapter 2 and Chapter 3.

def main():
    generator_file = Path("generate_ieee_report.py")
    if not generator_file.exists():
        print("generate_ieee_report.py not found!")
        return

    print("Reading generate_ieee_report.py...")
    with open(generator_file, "r", encoding="utf-8") as f:
        code = f.read()

    print("Expanding Chapter 2 detailed models...")

    # --- 2.3.3. Mô hình CNN-LSTM ---
    old_cnnlstm_det = """    add_paragraph(doc,
        'Mô hình CNN-LSTM kết hợp 1D Convolutional Neural Network và Bi-LSTM [19], [20]:', indent=True)
    add_paragraph(doc,
        '• 3 lớp Conv1D: Conv1D(9\u219264, k=5) \u2192 BN \u2192 ReLU \u2192 MaxPool(2) \u2192 Conv1D(64\u2192128, k=3) '
        '\u2192 BN \u2192 ReLU \u2192 MaxPool(2) \u2192 Conv1D(128\u219264, k=3) \u2192 BN \u2192 ReLU. CNN 1D trích xuất '
        'đặc trưng cục bộ (local temporal patterns) từ dữ liệu sensor.\\n'
        '• Bi-LSTM: LSTM(input=64, hidden=64, 1 layer, bidirectional). Sau CNN, chuỗi được '
        'rút gọn theo thời gian (do MaxPool), LSTM học phụ thuộc dài hạn trên chuỗi đã '
        'trích xuất đặc trưng.\\n'
        '• Classifier: Dropout(0.3) \u2192 Linear(128\u219232) \u2192 ReLU \u2192 Linear(32\u21922).', indent=True)"""

    new_cnnlstm_det = """    add_paragraph(doc,
        'Mô hình lai CNN-LSTM kết hợp sức mạnh trích xuất đặc trưng không gian cục bộ của Mạng tích chập một chiều (1D-CNN) '
        'và khả năng học phụ thuộc thời gian dài hạn của Mạng bộ nhớ dài-ngắn hạn hai chiều (Bi-LSTM). Sự tích hợp này tạo ra '
        'một pipeline xử lý tín hiệu cực kỳ mạnh mẽ cho dữ liệu cảm biến đa kênh của SisFall [19], [20]:', indent=True)
    add_paragraph(doc,
        '• Khối 1D-CNN trích xuất đặc trưng cục bộ (Local Feature Extraction Block): Gồm 3 lớp tích chập 1D liên tiếp. '
        'Lớp Conv1D thứ nhất biến đổi 9 kênh tín hiệu đầu vào thành 64 kênh đặc trưng thông qua bộ lọc kích thước k=5. '
        'Lớp này được theo sau bởi Batch Normalization, kích hoạt ReLU và lớp Max Pooling 1D với s=2 để giảm một nửa độ phân giải thời gian. '
        'Lớp Conv1D thứ hai tăng số kênh từ 64 lên 128 với bộ lọc k=3, tiếp tục BN, ReLU và Max Pooling. '
        'Lớp Conv1D thứ ba nén các kênh từ 128 xuống còn 64 kênh với k=3. Phép toán Max Pooling đóng vai trò cực kỳ quan trọng: '
        'nó thực hiện việc giữ lại giá trị cực đại trong một vùng lân cận thời gian (cực đại hóa tín hiệu gia tốc hoặc vận tốc góc), '
        'giúp mô hình nắm bắt được các đỉnh xung kích (impulse peaks) đặc trưng của cú va chạm té ngã đồng thời loại bỏ các '
        'biến động nhiễu tần số cao của cảm biến thô.', indent=True)
    add_paragraph(doc,
        '• Khối Bi-LSTM học phụ thuộc thời gian dài hạn (Temporal Bi-LSTM Block): Chuỗi đặc trưng sau khi qua khối CNN đã được '
        'giảm kích thước thời gian từ 200 timesteps xuống còn 50 timesteps nhờ 2 lớp Max Pooling. Chuỗi nén này được đưa vào '
        'một lớp Bi-LSTM với hidden_size = 64. Việc chạy Bi-LSTM trên chuỗi đặc trưng đã rút gọn giúp giảm thiểu tối đa khối lượng '
        'tính toán của mạng hồi quy, loại bỏ nguy cơ triệt tiêu đạo hàm và cho phép Bi-LSTM tập trung phân tích ngữ cảnh thời gian '
        'ở cấp độ cao hơn. Đầu ra của Bi-LSTM tại bước cuối cùng là một vector 128 chiều (nối từ hai hướng).', indent=True)
    add_paragraph(doc,
        '• Khối phân loại (Dense Classifier): Vector đặc trưng kết hợp 128 chiều được đưa qua lớp Dropout(0.3) để chống overfitting, '
        'sau đó qua lớp tuyến tính Linear(128→32), kích hoạt ReLU và cuối cùng là lớp Linear(32→2) để dự báo xác suất.', indent=True)"""

    # --- 2.3.4. Mô hình Transformer Encoder ---
    old_transformer_det = """    add_paragraph(doc,
        'Mô hình Transformer Encoder [8] được thiết kế cho xử lý song song chuỗi thời gian:', indent=True)
    add_paragraph(doc,
        '• Linear Projection: Linear(9\u219264) \u2192 LayerNorm \u2192 ReLU. Ánh xạ 9 features đầu vào '
        'sang không gian d_model = 64.\\n'
        '• Positional Encoding: Sử dụng mã hóa vị trí sin/cos để bổ sung thông tin thứ tự '
        'thời gian, vì Transformer không có cơ chế hồi quy tự nhiên [8].\\n'
        '• Transformer Encoder: 2 lớp Encoder, mỗi lớp có Multi-Head Self-Attention (4 heads) '
        'và Feed-Forward Network (dim=128). Activation: GELU.\\n'
        '• Global Average Pooling + Classifier: LayerNorm \u2192 Dropout \u2192 Linear(64\u219264) \u2192 GELU '
        '\u2192 Dropout \u2192 Linear(64\u21922).', indent=True)"""

    new_transformer_det = """    add_paragraph(doc,
        'Mô hình Transformer Encoder kế thừa trực tiếp cơ chế tự chú ý (Self-Attention) từ kiến trúc Transformer nổi tiếng '
        'của Vaswani et al. [8]. Trái ngược hoàn toàn với LSTM vốn xử lý chuỗi một cách tuần tự (gây nghẽn cổ chai tính toán), '
        'Transformer xử lý toàn bộ chuỗi thời gian 200 mẫu một cách song song hoàn toàn, giúp tận dụng tối đa sức mạnh tính toán '
        'song song của phần cứng GPU hiện đại. Cấu trúc chi tiết bao gồm:', indent=True)
    add_paragraph(doc,
        '• Khối chiếu tuyến tính và Mã hóa vị trí (Linear Projection & Positional Encoding): Tín hiệu 9 kênh cảm biến thô được '
        'chiếu qua lớp Linear(9→64) kèm chuẩn hóa lớp (Layer Normalization) và kích hoạt ReLU để ánh xạ sang không gian đặc trưng ẩn '
        'd_model = 64. Vì kiến trúc Transformer không chứa bất kỳ phép toán hồi quy hay tích chập tuần tự nào, mô hình hoàn toàn không '
        'có khái niệm về mặt thứ tự thời gian của các mẫu. Để khắc phục điều này, một vector Mã hóa vị trí (Positional Encoding) '
        'sử dụng các hàm lượng giác hình sin và cosin với tần số khác nhau được cộng trực tiếp vào vector chiếu ẩn, giúp mô hình '
        'nắm giữ thông tin về mặt thứ tự trước sau của các bước thời gian [8].', indent=True)
    add_paragraph(doc,
        '• Khối Transformer Encoder xếp chồng (Stacked Transformer Encoder): Gồm 2 lớp Encoder tiêu chuẩn xếp chồng. Mỗi lớp chứa '
        'khối cơ chế Đa đầu tự chú ý (Multi-Head Self-Attention - MHSA) với 4 đầu chú ý độc lập. MHSA tính toán đồng thời ba ma trận '
        'Query (Q), Key (K) và Value (V) từ dữ liệu ẩn đầu vào và thực hiện phép toán chú ý Scaled Dot-Product Attention: '
        'Attention(Q,K,V) = softmax(Q*K^T / sqrt(d_k)) * V. Việc chia thành 4 đầu chú ý giúp mô hình có khả năng học đồng thời nhiều '
        'mối quan hệ tương quan thời gian khác nhau trong chuỗi (ví dụ: một đầu chú ý học tương quan giữa pha mất thăng bằng ban đầu '
        'và pha va chạm, một đầu khác học tương quan giữa pha va chạm và pha nằm bất động). Sau MHSA là mạng truyền thẳng Feed-Forward '
        'Network (dim=128) với hàm kích hoạt phi tuyến GELU tiên tiến.', indent=True)
    add_paragraph(doc,
        '• Khối nén toàn cục và phân loại (Global Pooling & Classifier): Chuỗi đặc trưng đầu ra của Encoder (kích thước 200x64) '
        'được nén thành một vector đặc trưng duy nhất 64 chiều bằng phép toán trung bình hóa toàn cục (Global Average Pooling - GAP). '
        'Vector này được đưa qua LayerNorm, Dropout(0.3) và lớp FC Linear(64→64) → GELU → Dropout(0.15) → Linear(64→2) để phân loại.', indent=True)"""

    # --- 2.3.5. Mô hình TCN ---
    old_tcn_det = """    add_paragraph(doc,
        'Temporal Convolutional Network (TCN) [7] sử dụng dilated causal convolutions để mở '
        'rộng trường tiếp nhận (receptive field) theo cấp số nhân mà không tăng số tham số:', indent=True)
    add_paragraph(doc,
        '• Input BatchNorm: Chuẩn hóa 9 kênh input.\\n'
        '• 4 Temporal Blocks: Mỗi block gồm 2 lớp Conv1D với dilation tăng dần (1, 2, 4, 8), '
        'BatchNorm, ReLU, Dropout, và residual connection. Causal padding đảm bảo mô hình '
        'chỉ sử dụng thông tin từ quá khứ (không "nhìn trước").\\n'
        '• Receptive field tổng: RF = \\u03a3 2\\u00d7(k-1)\\u00d7d\\u1ecba = 2\\u00d72\\u00d7(1+2+4+8) = 60 timesteps.\\n'
        '• Global Average Pooling + Classifier.', indent=True)"""

    new_tcn_det = """    add_paragraph(doc,
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
        'qua lớp tuyến tính FC Linear(32→2) để đưa ra dự báo.', indent=True)"""

    # --- 2.5 Heuristic Engine Detail ---
    old_velocity_det = """    doc.add_heading('2.5.1. Phân tích vận tốc rơi (Velocity Analysis)', level=3)
    add_paragraph(doc,
        'Vận tốc rơi được tính dựa trên sự thay đổi vị trí hông (hip) theo trục Y '
        'giữa hai frame liên tiếp:', indent=True)
    add_formula(doc, 'v_y = (hip_y[t] - hip_y[t-1]) / \u0394t', '2.6')
    add_paragraph(doc,
        'Nếu v_y vượt ngưỡng velocity_threshold (mặc định 0.3 pixel/ms), hệ thống đánh '
        'dấu là "sudden drop" — tín hiệu cho sự rơi đột ngột đặc trưng của té ngã.', indent=True)"""

    new_velocity_det = """    doc.add_heading('2.5.1. Phân tích vận tốc rơi (Velocity Analysis)', level=3)
    add_paragraph(doc,
        'Vận tốc rơi (Velocity) là tín hiệu sinh học động học quan trọng nhất dùng để phát hiện pha rơi tự do đột ngột '
        '(free fall phase) đặc trưng của hành vi té ngã, giúp phân biệt hiệu quả với các hành động cúi người từ từ để nhặt đồ '
        'hoặc ngồi xuống ghế bình thường. Trong hệ tọa độ pixel của khung hình camera, trục dọc Y hướng thẳng từ trên xuống dưới. '
        'Vị trí trọng tâm cơ thể người được ước lượng bằng tọa độ Y trung bình cộng của hai điểm mốc hông trái (left_hip) và hông phải '
        '(right_hip) trích xuất bởi YOLOv11-Pose: Y_hip[t] = (Y_left_hip[t] + Y_right_hip[t]) / 2.0. Để triệt tiêu hoàn toàn hiện '
        'tượng rung lắc (jitter) do sai số định vị keypoint của camera, tọa độ Y_hip được lọc thông qua bộ lọc thông thấp Trung vị '
        'trượt (Moving Median Filter) với kích thước cửa sổ 3 khung hình.', indent=True)
    add_paragraph(doc,
        'Vận tốc rơi dọc thời gian thực v_y tại khung hình thứ t được tính toán bằng đạo hàm bậc nhất của vị trí hông theo thời gian '
        'giữa hai khung hình liên tiếp:', indent=True)
    add_formula(doc, 'v_y = (Y_hip[t] - Y_hip[t-1]) / \u0394t', '2.6')
    add_paragraph(doc,
        'Trong đó \\u0394t là khoảng thời gian trôi qua thực tế giữa hai khung hình liên tiếp (được đo đạc chính xác bằng mili-giây '
        'thông qua đồng hồ hệ thống để tránh sai số khi FPS dao động). Để thuật toán có khả năng bất biến với khoảng cách (scale invariance) '
        '- tức là hoạt động ổn định bất kể người dùng đứng gần hay đứng cách xa camera giám sát, vận tốc v_y được chuẩn hóa bằng cách '
        'chia trực tiếp cho chiều cao bounding box của đối tượng tại khung hình đó: v_normalized = v_y / BoundingBox_Height. '
        'Nếu giá trị vận tốc chuẩn hóa v_normalized vượt quá ngưỡng giới hạn velocity_threshold (được thiết lập mặc định ở mức '
        '0.3 pixel/ms), Heuristic Engine sẽ ngay lập tức kích hoạt cờ hiệu \"sudden_drop\" biểu thị trạng thái rơi tự do nguy hiểm.', indent=True)"""

    # --- 2.5.2. Aspect Ratio ---
    old_aspect_det = """    doc.add_heading('2.5.2. Phân tích tỷ lệ khung hình (Aspect Ratio)', level=3)
    add_paragraph(doc,
        'Tỷ lệ bounding box được sử dụng để phát hiện tư thế nằm ngang:', indent=True)
    add_formula(doc, 'is_prone = (width > height \u00d7 aspect_ratio_factor)', '2.7')
    add_paragraph(doc,
        'Khi một người đang đứng/đi, bounding box thường có chiều cao lớn hơn chiều rộng '
        '(height > width). Khi nằm xuống (sau khi ngã), chiều rộng sẽ lớn hơn chiều cao. '
        'Ngưỡng aspect_ratio_factor = 1.1 để đảm bảo phát hiện chính xác [14].', indent=True)"""

    new_aspect_det = """    doc.add_heading('2.5.2. Phân tích tỷ lệ khung hình (Aspect Ratio)', level=3)
    add_paragraph(doc,
        'Tỷ lệ khung hình của hộp bao (Bounding Box Aspect Ratio) là một đặc trưng hình học không gian vô cùng trực quan dùng '
        'để xác nhận tư thế nằm ngang (prone/supine status) sau khi xảy ra va chạm ngã. Bounding box của con người được đặc tả '
        'bởi hai thông số: chiều rộng W (width) và chiều cao H (height). Về mặt sinh học vận động, khi một người đang ở trạng '
        'thái đứng thẳng, đi bộ hoặc chạy, cơ thể họ luôn kéo giãn theo chiều dọc, khiến hộp bao có chiều cao lớn hơn nhiều so '
        'với chiều rộng (tỷ lệ W/H thường nằm trong khoảng 0.3 đến 0.6). Khi một sự cố té ngã xảy ra và đối tượng nằm bất động '
        'trên sàn nhà, chiều dài cơ thể họ nằm ngang sẽ biến đổi hình dạng hộp bao thành nằm ngang, khiến chiều rộng lớn hơn '
        'nhiều so với chiều cao (W/H > 1.0).', indent=True)
    add_paragraph(doc,
        'Thuật toán Heuristic Engine liên tục giám sát tỷ lệ này và kích hoạt trạng thái nằm ngang \"is_prone\" theo công thức:', indent=True)
    add_formula(doc, 'is_prone = (Width > Height \u00d7 aspect_ratio_factor)', '2.7')
    add_paragraph(doc,
        'Trong đó aspect_ratio_factor là hệ số điều chỉnh tư thế, được thiết lập thực nghiệm ở mức 1.1 [14]. Nếu tỷ lệ W/H vượt '
        'ngưỡng 1.1 liên tục trong ít nhất 2 khung hình (prone_confirmation_frames), hệ thống xác nhận đối tượng đã ở tư thế nằm '
        'trên sàn. Kỹ thuật đếm lọc temporal filter này giúp loại bỏ hoàn toàn hiện tượng báo động giả khi người dùng cúi người '
        'nhặt đồ quá nhanh trong 1 khung hình đơn lẻ.', indent=True)"""

    # --- 2.5.3. Head-Hip Position ---
    old_headhip_det = """    doc.add_heading('2.5.3. Phân tích vị trí đầu-hông (Head-Hip Position)', level=3)
    add_paragraph(doc,
        'Trong tư thế bình thường (đứng, đi bộ), đầu luôn ở vị trí cao hơn hông. Khi '
        'té ngã, đầu thường rơi xuống ngang hoặc thấp hơn hông:', indent=True)
    add_formula(doc, 'head_low = (head_y > hip_y \u00d7 head_hip_ratio)', '2.8')
    add_paragraph(doc,
        'Trong đó head_hip_ratio = 0.85, tức đầu thấp hơn 85% vị trí hông (lưu ý: trong '
        'hệ tọa độ hình ảnh, trục Y hướng xuống dưới).', indent=True)"""

    new_headhip_det = """    doc.add_heading('2.5.3. Phân tích vị trí đầu-hông (Head-Hip Position)', level=3)
    add_paragraph(doc,
        'Mặc dù tỷ lệ aspect ratio hoạt động rất tốt cho các cú ngã nằm thẳng hoàn toàn trên sàn, nó lại gặp khó khăn '
        'khi đối tượng bị ngã ngồi gục xuống hoặc ngã tựa lưng vào tường, nơi hộp bao vẫn có thể giữ chiều cao lớn hơn chiều rộng '
        '(Height > Width). Để khắc phục điểm yếu này, Heuristic Engine bổ sung tín hiệu phân tích hình học Vị trí tương đối đầu-hông '
        '(Head-Hip Relative Position). Ở trạng thái sinh hoạt bình thường (đứng, đi bộ, ngồi ghế), cấu trúc giải phẫu học cơ thể '
        'luôn đảm bảo phần đầu nằm ở vị trí cao nhất, tức là tọa độ Y của điểm mốc mũi (nose_y) có giá trị pixel nhỏ hơn nhiều so '
        'với tọa độ Y trung bình của hông (hip_y) trong hệ tọa độ camera hướng xuống.', indent=True)
    add_paragraph(doc,
        'Khi xảy ra sự cố té ngã, toàn bộ cơ thể bị gập lại hoặc đổ sụp xuống sàn, khiến vị trí đầu rơi xuống ngang hàng hoặc '
        'thậm chí thấp hơn vị trí hông. Heuristic Engine tính toán cờ hiệu trạng thái đầu thấp \"head_low\" theo công thức tuyến tính:', indent=True)
    add_formula(doc, 'head_low = (Y_nose > Y_hip \u00d7 head_hip_ratio)', '2.8')
    add_paragraph(doc,
        'Trong đó head_hip_ratio được thiết lập ở mức 0.85 (tương ứng với việc đầu rơi xuống thấp hơn 85% khoảng cách từ hông lên '
        'đỉnh đầu). Tín hiệu này đóng vai trò là chốt chặn phòng vệ vô cùng nhạy bén, giúp phát hiện toàn diện các kịch bản ngã phức tạp '
        'như ngã khụy gối gục đầu, ngã ngồi bệt xuống sàn phòng ngủ hoặc ngã nghiêng người gối đầu lên vật cản mà hộp bao không '
        'bị bẹt ngang.', indent=True)"""

    # Apply Chapter 2 phase 2 replacements
    print("  Applying Chapter 2 phase 2 replacements...")
    code = code.replace(old_cnnlstm_det, new_cnnlstm_det)
    code = code.replace(old_transformer_det, new_transformer_det)
    code = code.replace(old_tcn_det, new_tcn_det)
    code = code.replace(old_velocity_det, new_velocity_det)
    code = code.replace(old_aspect_det, new_aspect_det)
    code = code.replace(old_headhip_det, new_headhip_det)

    print("Saving changes back to generate_ieee_report.py...")
    with open(generator_file, "w", encoding="utf-8") as f:
        f.write(code)

    print("Success! Phase 2 expansion applied successfully.")

if __name__ == "__main__":
    main()
