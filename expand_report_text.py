import re
from pathlib import Path

# Script to expand generate_ieee_report.py with massive academic text blocks.

def main():
    generator_file = Path("generate_ieee_report.py")
    if not generator_file.exists():
        print("generate_ieee_report.py not found!")
        return

    print("Reading generate_ieee_report.py...")
    with open(generator_file, "r", encoding="utf-8") as f:
        code = f.read()

    print("Expanding Chapter 1 paragraphs...")
    
    # --- 1.1.1 Bối cảnh và sự cần thiết ---
    old_bocanh_1 = """    add_paragraph(doc,
        'Sự gia tăng nhanh chóng của dân số già hóa trên toàn cầu đặt ra nhiều thách thức '
        'trong lĩnh vực chăm sóc sức khỏe. Theo báo cáo của Tổ chức Y tế Thế giới (WHO), '
        'té ngã là nguyên nhân thứ hai gây tử vong do tai nạn thương tích không chủ ý trên '
        'toàn thế giới, với khoảng 684.000 ca tử vong mỗi năm [2]. Người cao tuổi trên 60 '
        'tuổi chiếm tỷ lệ cao nhất trong các trường hợp té ngã nghiêm trọng, với khoảng '
        '28-35% người từ 65 tuổi trở lên bị ít nhất một lần té ngã mỗi năm [13].', indent=True)"""

    new_bocanh_1 = """    add_paragraph(doc,
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
        'và công nghệ hóa sâu sắc.', indent=True)"""

    old_bocanh_2 = """    add_paragraph(doc,
        'Hậu quả của tai nạn té ngã đối với sức khỏe thể chất của người cao tuổi cực kỳ nghiêm '
        'trọng, thường dẫn đến các chấn thương nặng nề như gãy xương hông, chấn thương sọ não, '
        'hoặc tổn thương mô mềm vĩnh viễn. Ngoài ra, gánh nặng tâm lý như hội chứng sợ ngã (fear of falling) '
        'khiến người cao tuổi tự cô lập bản thân, giảm các hoạt động thể chất hằng ngày, dẫn đến suy giảm '
        'chức năng vận động và trầm cảm. Hơn thế nữa, về mặt kinh tế xã hội, chi phí điều trị sau té ngã '
        'cho người già là cực kỳ đắt đỏ, tạo gánh nặng lớn lên hệ thống bảo hiểm y tế và gia đình.', indent=True)"""

    new_bocanh_2 = """    add_paragraph(doc,
        'Hậu quả y sinh và lâm sàng của tai nạn té ngã đối với sức khỏe thể chất của người cao tuổi là vô cùng nặng nề và '
        'thường kéo theo những di chứng lâu dài, thậm chí là tàn phế vĩnh viễn. Khi xảy ra té ngã, lực tác động cơ học trực tiếp '
        'lên hệ xương khớp đã bị loãng xương của người già thường dẫn đến các chấn thương nghiêm trọng như gãy cổ xương đùi, '
        'gãy xương hông, chấn thương sọ não, xuất huyết nội hoặc tổn thương mô mềm diện rộng. Trong đó, gãy xương hông là một '
        'cực hình y khoa đối với người già, đòi hỏi phải phẫu thuật can thiệp ngay lập tức và có tỷ lệ tử vong trong vòng một năm '
        'sau tai nạn lên tới 20-30% do các biến chứng liên đới từ việc nằm bất động kéo dài. Thời gian nằm liệt giường sau té ngã '
        'kích hoạt một chuỗi biến chứng lâm sàng phức tạp bao gồm huyết khối tĩnh mạch sâu (DVT), thuyên tắc phổi, loét tỳ đè '
        '(decubitus ulcers), viêm phổi do ứ đọng (hypostatic pneumonia), và hội chứng suy giảm cơ bắp (sarcopenia) diễn ra với '
        'tốc độ chóng mặt. Không chỉ dừng lại ở tổn thương thể chất, té ngã còn để lại một gánh nặng tâm lý sâu sắc được gọi là '
        '\"hội chứng sợ ngã\" (fear of falling). Hội chứng này tạo ra một vòng xoáy bệnh lý tiêu cực: sự sợ hãi khiến người cao '
        'tuổi tự hạn chế di chuyển, xa lánh các hoạt động xã hội và sinh hoạt hằng ngày (ADL), từ đó đẩy nhanh quá trình teo cơ, '
        'mất thăng bằng, suy giảm chức năng tim mạch và dẫn đến các trạng thái tâm thần trầm cảm, cô đơn sâu sắc. Về mặt kinh tế '
        'xã hội, chi phí chăm sóc y tế cấp cứu, phẫu thuật chỉnh hình và phục hồi chức năng sau té ngã là một gánh nặng khổng lồ '
        'đè nặng lên hệ thống bảo hiểm y tế quốc gia và trực tiếp làm kiệt quệ tài chính của các hộ gia đình có người già bị nạn.', indent=True)
    
    add_paragraph(doc,
        'Một khía cạnh y khoa cốt lõi quyết định đến khả năng sống sót và mức độ phục hồi của người cao tuổi sau sự cố té ngã '
        'chính là khái niệm \"Giờ Vàng\" (Golden Hour) trong cấp cứu y tế. Các nghiên cứu lâm sàng đã chứng minh rằng nếu một '
        'người già bị té ngã và phải nằm trên sàn nhà mà không thể tự đứng dậy hoặc không được phát hiện trong vòng 1 giờ đầu '
        '(hiện tượng long-lie), tỷ lệ tử vong hoặc phải chuyển vào các trung tâm chăm sóc đặc biệt dài hạn tăng lên gấp nhiều lần. '
        'Nằm bất động kéo dài trên sàn gây ra tình trạng tiêu cơ vân cấp tính (rhabdomyolysis) - giải phóng lượng lớn myoglobin '
        'vào máu dẫn đến suy thận cấp, kết hợp với tình trạng hạ thân nhiệt (hypothermia), mất nước nghiêm trọng và chấn thương tâm '
        'lý hoảng loạn. Do đó, việc xây dựng các hệ thống công nghệ có khả năng tự động phát hiện, nhận dạng chính xác và gửi '
        'cảnh báo khẩn cấp tức thời trong vòng vài giây ngay sau khi cú ngã xảy ra là một giải pháp y tế công cộng mang tính sống còn, '
        'giúp tối thiểu hóa thời gian phản ứng, kích hoạt chuỗi cấp cứu kịp thời và bảo vệ tính mạng cho người cao tuổi.', indent=True)"""

    old_bocanh_3 = """    add_paragraph(doc,
        'Tại Việt Nam, với tốc độ già hóa dân số thuộc hàng nhanh nhất thế giới, nhu cầu '
        'về các hệ thống giám sát và hỗ trợ người cao tuổi ngày càng trở nên cấp thiết. '
        'Hậu quả của té ngã không chỉ là chấn thương về thể chất (gãy xương, chấn thương '
        'đầu) mà còn gây ra tâm lý sợ hãi, giảm vận động và suy giảm chất lượng cuộc sống '
        '[14]. Đặc biệt, nếu người cao tuổi sống một mình và không được phát hiện kịp thời '
        'sau khi té ngã, thời gian nằm trên sàn kéo dài (long-lie) có thể dẫn đến các biến '
        'chứng nguy hiểm như mất nước, hạ thân nhiệt, hoặc suy đa cơ quan [15].', indent=True)"""

    new_bocanh_3 = """    add_paragraph(doc,
        'Tại Việt Nam, bối cảnh già hóa dân số đang diễn ra với tốc độ thuộc hàng nhanh nhất thế giới. Theo số liệu của Tổng cục '
        'Thống kê, nước ta đã chính thức bước vào giai đoạn \"già hóa dân số\" từ năm 2011 và dự kiến sẽ chuyển sang giai đoạn '
        '\"dân số già\" vào năm 2038. Sự thay đổi nhanh chóng này tạo ra áp lực cực kỳ lớn lên hệ thống cơ sở hạ tầng y tế vốn '
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
        'xã hội [15].', indent=True)"""

    # --- 1.1.2 Phân loại các phương pháp phát hiện té ngã ---
    old_phanloai_1 = """    add_paragraph(doc,
        '1) Nhóm dựa trên thiết bị đeo (Wearable-based): Sử dụng các cảm biến như gia tốc kế (Accelerometer), '
        'con quay hồi chuyển (Gyroscope) gắn trên cơ thể (thắt lưng, cổ tay, ngực). Phương pháp này có độ chính xác '
        'rất cao, hoạt động linh hoạt ngoài trời và không bị ảnh hưởng bởi góc che khuất. Tuy nhiên, nhược điểm là '
        'người già thường cảm thấy phiền phức hoặc hay quên đeo thiết bị hằng ngày, gây gián đoạn giám sát.', indent=True)
    add_paragraph(doc,
        '2) Nhóm dựa trên thị giác máy tính (Vision-based): Sử dụng hệ thống camera giám sát lắp đặt trong không gian '
        'sống. Hệ thống phân tích luồng video thời gian thực để nhận biết tư thế nằm hoặc ngã đột ngột. Phương pháp này '
        'không yêu cầu người dùng đeo bất kỳ thiết bị nào, mang lại sự thoải mái tuyệt đối. Song, nó lại gặp thách thức '
        'lớn về quyền riêng tư (đặc biệt trong nhà tắm, phòng ngủ) và dễ bị ảnh hưởng bởi điều kiện ánh sáng kém hoặc vật cản.', indent=True)
    add_paragraph(doc,
        '3) Nhóm dựa trên cảm biến môi trường (Ambient-based): Sử dụng các cảm biến áp suất trên sàn nhà, cảm biến âm thanh '
        'hoặc radar sóng mmWave để phát hiện bất thường. Phương pháp này hoàn toàn không xâm phạm riêng tư nhưng chi phí lắp đặt '
        'cực kỳ đắt đỏ và phạm vi hoạt động bị giới hạn nghiêm trọng.', indent=True)"""

    new_phanloai_1 = """    add_paragraph(doc,
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
        'lúc trong phòng.', indent=True)"""

    # --- 1.1.3 Các nghiên cứu liên quan ---
    old_nghiencuu_1 = """    add_paragraph(doc,
        'Nhiều nghiên cứu khoa học trên thế giới đã tập trung giải quyết bài toán phát hiện té ngã. '
        'Ban đầu, các phương pháp dựa trên ngưỡng cố định (threshold-based) áp dụng cho độ lớn vector gia tốc '
        'được sử dụng rộng rãi nhờ tính đơn giản. Tuy nhiên, các phương pháp này tạo ra tỷ lệ báo động giả cực kỳ cao '
        'do không phân biệt được té ngã với các hoạt động thể chất mạnh như nhảy hoặc ngồi nhanh xuống ghế [13].', indent=True)
    add_paragraph(doc,
        'Những năm gần đây, sự bùng nổ của Học máy truyền thống (SVM, Decision Tree, Random Forest) và đặc biệt '
        'là Học sâu (Deep Learning) đã nâng tầm chính xác của các hệ thống. Việc sử dụng các mạng nơ-ron hồi quy '
        '(LSTM, GRU) cho dữ liệu chuỗi thời gian hoặc mạng CNN cho hình ảnh cho thấy khả năng vượt trội trong việc '
        'học các biểu diễn đặc trưng phức tạp tự động từ dữ liệu thô. Bảng 1.2 tổng hợp các nghiên cứu tiêu biểu:', indent=True)"""

    new_nghiencuu_1 = """    add_paragraph(doc,
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
        'các công trình nghiên cứu khoa học tiêu biểu đặt nền móng cho đề tài này:', indent=True)"""

    # --- 1.2.1 Mạng nơ-ron tích chập (CNN) ---
    old_cnn_1 = """    add_paragraph(doc,
        'Mạng nơ-ron tích chập (Convolutional Neural Network — CNN) ban đầu được thiết kế cho '
        'xử lý ảnh hai chiều. Tuy nhiên, các phép tích chập một chiều (1D-CNN) đã chứng tỏ hiệu quả '
        'vượt trội trong phân tích tín hiệu chuỗi thời gian (time-series) như dữ liệu từ các cảm biến gia tốc '
        'và con quay hồi chuyển [19]. CNN hoạt động bằng cách trượt một bộ lọc (kernel) dọc theo chiều thời gian '
        'để tự động nắm bắt các đặc trưng không gian-thời gian cục bộ (local temporal features) cực kỳ hiệu quả.', indent=True)"""

    new_cnn_1 = """    add_paragraph(doc,
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
        'vào việc trượt bộ lọc qua điểm biến thiên đó.', indent=True)"""

    # --- 1.2.2 Mạng hồi quy LSTM ---
    old_lstm_1 = """    add_paragraph(doc,
        'Mạng nơ-ron hồi quy (RNN) truyền thống gặp phải vấn đề triệt tiêu đạo hàm (vanishing gradient) '
        'khi xử lý các chuỗi thời gian dài, khiến mô hình không thể học được các phụ thuộc dài hạn. '
        'Long Short-Term Memory (LSTM) được Hochreiter và Schmidhuber đề xuất năm 1997 [3] để giải quyết triệt để '
        'vấn đề này thông qua cấu trúc các cổng kiểm soát luồng thông tin (forget, input, output gates).', indent=True)"""

    new_lstm_1 = """    add_paragraph(doc,
        'Mạng nơ-ron hồi quy truyền thống (Recurrent Neural Network - RNN) là một bước tiến lớn trong việc xử lý dữ liệu chuỗi '
        'nhờ vào cơ chế phản hồi vòng lặp (recurrent connections), cho phép thông tin được truyền từ bước thời gian này sang '
        'bước thời gian tiếp theo, tạo nên một dạng \"bộ nhớ trong\" ngắn hạn. Tuy nhiên, RNN truyền thống gặp phải một hạn chế '
        'chí mạng về mặt toán học khi huấn luyện bằng thuật toán lan truyền ngược qua thời gian (Backpropagation Through Time - BPTT): '
        'vấn đề triệt tiêu đạo hàm (vanishing gradient) và bùng nổ đạo hàm (exploding gradient). Khi độ dài chuỗi dữ liệu tăng lên '
        '(vượt quá 10 hoặc 20 timesteps), việc nhân liên tiếp các ma trận trọng số trong quá trình tính đạo hàm khiến các giá trị '
        'này giảm dần về 0 theo cấp số nhân. Kết quả là mô hình hoàn toàn mất khả năng cập nhật trọng số cho các lớp ban đầu, '
        'nói cách khác, nó quên mất các phụ thuộc dài hạn (long-term dependencies) trong quá khứ.', indent=True)
    add_paragraph(doc,
        'Để giải quyết triệt để điểm yếu chí mạng này, Hochreiter và Schmidhuber đã đề xuất kiến trúc bộ nhớ dài-ngắn hạn '
        '(Long Short-Term Memory - LSTM) vào năm 1997 [3]. Trái tim của LSTM là trạng thái ô (cell state, ký hiệu là C_t) đóng vai trò '
        'như một \"đường cao tốc thông tin\" chạy dọc suốt chiều dài chuỗi dữ liệu với rất ít các tương tác tuyến tính, giúp đạo hàm '
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
        'của từng timestep đối với nhãn quyết định \"Té ngã\". Đối với cú ngã, các timestep nằm ở khoảng khắc gia tốc biến thiên cực '
        'đại (lúc va chạm sàn) sẽ được gán trọng số rất cao, giúp bộ phân loại tập trung tối đa vào thông tin đắt giá nhất này.', indent=True)"""

    # --- 1.2.3 Mạng GRU ---
    old_gru_1 = """    add_paragraph(doc,
        'Gated Recurrent Unit (GRU) do Cho et al. đề xuất năm 2014 [4] là một biến thể tối ưu '
        'hóa của LSTM. GRU gộp cổng quên và cổng đầu vào thành một cổng duy nhất gọi là cổng cập nhật '
        '(update gate), đồng thời kết hợp trạng thái ô (cell state) và trạng thái ẩn (hidden state) '
        'làm một. Nhờ vậy, GRU sở hữu số lượng tham số ít hơn đáng kể (~30% so với LSTM), giúp tăng tốc độ '
        'huấn luyện và suy luận trên các hệ thống tài nguyên hạn chế hằng ngày.', indent=True)"""

    new_gru_1 = """    add_paragraph(doc,
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
        'phần cứng và dung lượng pin bị giới hạn nghiêm trọng [4].', indent=True)"""

    # --- 1.2.4 Mô hình ước lượng tư thế ---
    old_pose_1 = """    add_paragraph(doc,
        'Ước lượng tư thế (Pose Estimation) là bài toán xác định vị trí các khớp nối (joints) '
        'trên cơ thể người từ hình ảnh hoặc video. Đồ án sử dụng mô hình YOLOv11-Pose [6] — '
        'phiên bản mới nhất của dòng YOLO tích hợp khả năng ước lượng tư thế (Pose Estimation) '
        'song song với phát hiện đối tượng (Object Detection) trong cùng một lần suy luận '
        '(single forward pass).', indent=True)
    add_paragraph(doc,
        'YOLOv11-Pose trích xuất 17 điểm khung xương (keypoints) theo chuẩn COCO Keypoints, '
        'bao gồm: mũi (nose), mắt trái/phải, tai trái/phải, vai trái/phải, khuỷu tay '
        'trái/phải, cổ tay trái/phải, hông trái/phải, đầu gối trái/phải, và mắt cá chân '
        'trái/phải. Mỗi keypoint có tọa độ (x, y) và độ tin cậy (confidence score) [5], [6].', indent=True)"""

    new_pose_1 = """    add_paragraph(doc,
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
        'người cao tuổi.', indent=True)"""

    # --- 1.3.1 Accuracy ---
    old_acc_1 = """    add_paragraph(doc,
        'Tuy nhiên, Accuracy có thể gây hiểu lầm khi dữ liệu mất cân bằng (imbalanced) '
        '— trường hợp phổ biến trong bài toán phát hiện té ngã vì số lượng hoạt động bình '
        'thường (ADL) thường lớn hơn nhiều so với số lần té ngã.', indent=True)"""

    new_acc_1 = """    add_paragraph(doc,
        'Độ chính xác tổng thể (Accuracy) là chỉ số cơ bản và trực quan nhất được sử dụng để đánh giá hiệu năng của một bộ phân loại. '
        'Nó đo lường tỷ lệ giữa số lượng mẫu dự đoán chính xác (bao gồm cả mẫu té ngã đúng và mẫu hoạt động thường ngày đúng) '
        'trên tổng số mẫu dữ liệu thực nghiệm. Mặc dù là chỉ số đầu tiên được xem xét, Accuracy lại tiềm ẩn một cạm bẫy toán học cực kỳ '
        'nguy hiểm được gọi là \"nghịch lý độ chính xác\" (Accuracy Paradox) khi áp dụng vào các bộ dữ liệu bị mất cân bằng lớp '
        '(highly imbalanced datasets). Trong thực tế đời sống, hành vi té ngã là một sự cố cực kỳ hiếm gặp (chỉ chiếm dưới 0.1% thời gian '
        'sinh hoạt), trong khi các hoạt động hằng ngày ADL chiếm tới 99.9% dữ liệu thu thập. Nếu một bộ phân loại đơn giản chỉ cần '
        'dự đoán tất cả mọi mẫu đều là \"hoạt động bình thường ADL\", nó vẫn sẽ dễ dàng đạt được độ chính xác Accuracy lên tới 99.9%. '
        'Tuy nhiên, bộ phân loại đó hoàn toàn vô dụng vì nó bỏ sót 100% các cú ngã xảy ra. Do đó, chúng ta không được phép chỉ dựa vào '
        'Accuracy để đánh giá hệ thống, mà bắt buộc phải sử dụng kết hợp các chỉ số chuyên sâu khác.', indent=True)"""

    # --- 1.3.3 Recall ---
    old_recall_1 = """    add_paragraph(doc,
        'Recall (hay Sensitivity) đo lường tỷ lệ phát hiện đúng trong tất cả các mẫu thực '
        'sự là dương. Đây là chỉ số quan trọng nhất trong bài toán phát hiện té ngã, vì '
        'việc bỏ sót một cú ngã (False Negative) có thể gây hậu quả cực kỳ nghiêm trọng.', indent=True)"""

    new_recall_1 = """    add_paragraph(doc,
        'Độ nhạy (Recall, hay trong y học còn gọi là Độ nhạy lâm sàng - Sensitivity) đo lường tỷ lệ giữa các trường hợp thực tế '
        'có xảy ra té ngã và được mô hình dự đoán chính xác là té ngã (True Positives) trên tổng số ca té ngã thực sự xảy ra trong '
        'thực tế (TP + FN). Trong bài toán an toàn và chăm sóc sức khỏe cho người cao tuổi, Recall được đồng thuận là chỉ số y khoa '
        'quan trọng nhất và phải được ưu tiên tối đa trong quá trình tối ưu hóa mô hình. Một lỗi False Negative (FN) - tức là '
        'người già bị ngã thật sự nhưng mô hình bỏ sót và nhận định là họ đang sinh hoạt bình thường - là một sai sót mang tính chí '
        'mạng, trực tiếp đe dọa đến tính mạng của người bệnh vì họ sẽ nằm bất động trên sàn nhà mà không nhận được bất kỳ sự giúp đỡ '
        'nào (long-lie). Ngược lại, một lỗi False Positive (FP) - tức là người già chỉ ngồi nhanh xuống ghế nhưng mô hình cảnh báo '
        'nhầm là ngã - chỉ gây ra sự phiền toái nhỏ về mặt vận hành (báo động giả). Do đó, mục tiêu tối thượng của FallGuard AI là '
        'phải đẩy chỉ số Recall lên tiệm cận mức 100%, đồng thời giữ chỉ số báo động giả trong phạm vi chấp nhận được.', indent=True)"""

    # Apply Chapter 1 replacements
    print("  Applying Chapter 1 replacements...")
    code = code.replace(old_bocanh_1, new_bocanh_1)
    code = code.replace(old_bocanh_2, new_bocanh_2)
    code = code.replace(old_bocanh_3, new_bocanh_3)
    code = code.replace(old_phanloai_1, new_phanloai_1)
    code = code.replace(old_nghiencuu_1, new_nghiencuu_1)
    code = code.replace(old_cnn_1, new_cnn_1)
    code = code.replace(old_lstm_1, new_lstm_1)
    code = code.replace(old_gru_1, new_gru_1)
    code = code.replace(old_pose_1, new_pose_1)
    code = code.replace(old_acc_1, new_acc_1)
    code = code.replace(old_recall_1, new_recall_1)

    print("Expanding Chapter 2 paragraphs...")
    
    # --- 2.2.1 Bộ dữ liệu SisFall ---
    old_sisfall_1 = """    add_paragraph(doc,
        'Bộ dữ liệu SisFall (Sucerquia et al., 2017) [1] là bộ dữ liệu chuẩn quốc tế '
        'được sử dụng rộng rãi trong nghiên cứu phát hiện té ngã. SisFall bao gồm dữ liệu '
        'từ 38 đối tượng tham gia (23 người trưởng thành từ 19-30 tuổi và 15 người cao '
        'tuổi từ 60-75 tuổi), với tổng cộng 4.510 bản ghi hoạt động thực tế.', indent=True)"""

    new_sisfall_1 = """    add_paragraph(doc,
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
        'biến động động học và tư thế toàn thân mà không bị nhiễu bởi các chuyển động lắc tay hay lắc chân cục bộ của đối tượng [1].', indent=True)"""

    # --- 2.2.2 Tiền xử lý dữ liệu ---
    old_preproc_1 = """    add_paragraph(doc,
        'Dữ liệu thô từ SisFall được tiền xử lý qua các bước sau:', indent=True)
    add_paragraph(doc,
        '1) Chuyển đổi đơn vị vật lý: Dữ liệu raw (bits) được chuyển sang đơn vị vật lý chuẩn '
        '(g cho gia tốc kế, °/s cho con quay hồi chuyển) sử dụng hệ số scale tương ứng '
        'của từng cảm biến đã được thiết lập bởi nhà sản xuất [1]:', indent=True)"""

    new_preproc_1 = """    add_paragraph(doc,
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
        'xuất trong tài liệu kỹ thuật của từng con chip cảm biến [1]. Cụ thể:', indent=True)"""

    old_preproc_2 = """    add_paragraph(doc,
        '2) Cửa sổ trượt (Sliding Window): Chuỗi thời gian dài được phân mảnh thành các '
        'cửa sổ có kích thước cố định W = 200 samples (tương đương 1 giây ở 200 Hz), với '
        'độ chồng lấn (overlap) O = 100 samples (50%). Phương pháp này tăng số lượng mẫu '
        'huấn luyện và giúp mô hình học được các đặc trưng ở nhiều pha khác nhau (Hình 2.3).', indent=True)"""

    new_preproc_2 = """    add_paragraph(doc,
        '2) Kỹ thuật Cửa sổ trượt phân mảnh dữ liệu (Sliding Window Segmentation): Các bản ghi tín hiệu trong SisFall thực chất là '
        'các chuỗi thời gian liên tục kéo dài từ vài chục giây đến vài phút. Để đưa dữ liệu này vào huấn luyện các mô hình mạng nơ-ron '
        'hồi quy và tích chập vốn yêu cầu kích thước đầu vào cố định, chuỗi thời gian dài vô tận được phân mảnh thành các cửa sổ con '
        '(windows) có kích thước cố định W. Trong đồ án này, chúng em thiết lập kích thước cửa sổ W = 200 mẫu dữ liệu (tương đương '
        'với khoảng thời gian đúng 1.0 giây hoạt động thực tế của đối tượng tại tần số lấy mẫu f_s = 200 Hz). Để tối ưu hóa hiệu năng, '
        'chúng em áp dụng độ chồng lấn (overlap) O = 100 mẫu (tương đương 50% kích thước cửa sổ). Kỹ thuật cửa sổ trượt có overlap mang '
        'lại hai giá trị khoa học to lớn: (1) Tăng số lượng mẫu huấn luyện lên gấp đôi (data augmentation) giúp tránh hiện tượng '
        'overfitting cho các mô hình học sâu; (2) Tránh việc bỏ sót hoặc chia cắt mất phân đoạn va chạm ngã (impact phase) nằm ở ranh '
        'giới giữa hai cửa sổ kế tiếp, đảm bảo mô hình luôn chụp được toàn bộ diễn biến động học của cú ngã trong ít nhất một cửa sổ '
        '(Hình 2.3).', indent=True)"""

    # --- 2.3.1 Mô hình Bi-LSTM với Attention ---
    old_bilstm_det_1 = """    add_paragraph(doc,
        'Mô hình Bi-LSTM + Attention là kiến trúc chính của hệ thống, bao gồm các thành phần:', indent=True)
    add_paragraph(doc,
        '• Batch Normalization đầu vào: Chuẩn hóa 9 kênh input theo chiều feature để ổn '
        'định phân phối dữ liệu giữa các batch.\\n'
        '• Bi-LSTM 2 lớp: Xếp chồng 2 lớp LSTM bidirectional, mỗi chiều có hidden_size = 128, '
        'tổng output = 256 chiều. Dropout = 0.3 giữa các lớp để giảm overfitting.\\n'
        '• Cơ chế Attention: Tính trọng số attention cho mỗi timestep qua mạng Linear(256\\u219264) '
        '\\u2192 Tanh \\u2192 Linear(64\\u21921) \\u2192 Softmax. Context vector được tính bằng tổ hợp tuyến tính '
        'có trọng số của output LSTM.\\n'
        '• Classifier: Dropout(0.3) \\u2192 Linear(256\\u219264) \\u2192 ReLU \\u2192 Dropout(0.15) \\u2192 Linear(64\\u21922).', indent=True)"""

    new_bilstm_det_1 = """    add_paragraph(doc,
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
        'hàm Softmax quyết định.', indent=True)"""

    # --- 2.5 Thuật toán phát hiện té ngã thời gian thực ---
    old_heuristic_1 = """    add_paragraph(doc,
        'Module phát hiện té ngã thời gian thực (FallDetector) kết hợp ba tín hiệu phân '
        'tích từ keypoints và bounding box do YOLOv11-Pose cung cấp:', indent=True)"""

    new_heuristic_1 = """    add_paragraph(doc,
        'Bên cạnh nhánh phân tích chuỗi thời gian dựa trên cảm biến đeo tay hoạt động ngoại tuyến, nhánh Thị giác máy tính '
        '(Computer Vision) đóng vai trò là chốt chặn giám sát trực quan thời gian thực cực kỳ quan trọng trong hệ thống FallGuard AI. '
        'Module phát hiện té ngã thời gian thực (ký hiệu lớp đối tượng FallDetector) được thiết kế để xử lý trực tiếp luồng video '
        'stream từ camera phòng. Trọng tâm của module này là sự kết hợp thông minh giữa năng lực trích xuất đặc trưng tư thế mạnh mẽ '
        'của mô hình học sâu YOLOv11-Pose và một động cơ phân tích luật Heuristic sinh học động học (Heuristic Engine) do chúng em tự '
        'thiết kế. Việc sử dụng kết hợp này giúp hệ thống hoạt động vô cùng nhẹ nhàng, không yêu cầu phần cứng máy chủ GPU đắt đỏ '
        'như các mô hình phân loại video 3D-CNN mà vẫn đạt được độ nhạy xuất sắc. Thuật toán phân tích đồng thời ba tín hiệu động '
        'học độc lập từ tọa độ hộp bao và 17 điểm keypoints cơ thể người để đưa ra kết luận quyết định:', indent=True)"""

    # Apply Chapter 2 replacements
    print("  Applying Chapter 2 replacements...")
    code = code.replace(old_sisfall_1, new_sisfall_1)
    code = code.replace(old_preproc_1, new_preproc_1)
    code = code.replace(old_preproc_2, new_preproc_2)
    code = code.replace(old_bilstm_det_1, new_bilstm_det_1)
    code = code.replace(old_heuristic_1, new_heuristic_1)

    print("Expanding Chapter 3 paragraphs...")
    
    # --- 3.4.2 Kết quả kiểm thử ---
    old_ketqua_1 = """    add_paragraph(doc,
        'Nhận xét: Mô hình CNN-LSTM đạt kết quả tốt nhất với Accuracy = 98.08% và '
        'F1-Score = 0.9809, tiếp theo là TCN (97.69%) và Bi-LSTM + Attention (97.12%). '
        'Mô hình Transformer Encoder có kết quả thấp nhất (95.19%) do kích thước dữ liệu '
        'chưa đủ lớn để tận dụng hết khả năng của Self-Attention [8]. Điều này phù hợp '
        'với các nghiên cứu trước đó cho thấy CNN kết hợp RNN thường vượt trội trên dữ '
        'liệu chuỗi thời gian ngắn [19], [20].', indent=True)"""

    new_ketqua_1 = """    add_paragraph(doc,
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
        'dễ bị nhiễu động hơn so với các kiến trúc CNN hay RNN có cấu trúc quy nạp (inductive bias) chặt chẽ hơn [8].', indent=True)"""

    print("  Applying Chapter 3 replacements...")
    code = code.replace(old_ketqua_1, new_ketqua_1)

    print("Saving changes back to generate_ieee_report.py...")
    with open(generator_file, "w", encoding="utf-8") as f:
        f.write(code)

    print("Success! generate_ieee_report.py has been expanded successfully.")

if __name__ == "__main__":
    main()
