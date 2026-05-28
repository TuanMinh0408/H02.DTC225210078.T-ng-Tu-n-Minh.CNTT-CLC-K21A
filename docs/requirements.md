# Software Requirements Specification (SRS)

## 1. Functional Requirements (Yêu cầu chức năng)
- **Real-time Monitoring**: Hệ thống phải có khả năng xử lý luồng stream video từ camera giám sát liên tục.
- **Human Detection**: Tự động phát hiện người trong khung hình bằng mô hình YOLOv11.
- **Behavior Recognition (Fall Detection)**: Nhận biết hành vi té ngã dựa trên sự thay đổi về tư thế (Pose) và vận tốc chuyển động (Velocity).
- **Persistent Alert Logging**: Lưu trữ thông tin về các vụ té ngã (thời gian, hình ảnh bằng chứng) vào cơ sở dữ liệu.
- **Audit History**: Người dùng có thể xem lại danh sách các vụ té ngã đã xảy ra trong quá khứ.
- **Audio Notification**: Phát âm thanh cảnh báo ngay lập tức trên trình duyệt khi phát hiện sự cố.

## 2. Non-functional Requirements (Yêu cầu phi chức năng)
- **Performance (Hiệu năng)**: Tốc độ xử lý phải đạt tối thiểu 15-20 FPS trên phần cứng tiêu chuẩn để đảm bảo tính thời gian thực.
- **Accuracy (Độ chính xác)**: Tỷ lệ nhận diện đúng (Precision) > 90% trong điều kiện ánh sáng tốt.
- **Latency (Độ trễ)**: Cảnh báo phải được phát ra trong vòng dưới 2 giây kể từ khi cú ngã kết thúc.
- **Usability (Tính dễ dùng)**: Giao diện Dashboard trực quan, hiển thị rõ ràng trạng thái hệ thống.
- **Security (Bảo mật)**: Dữ liệu hình ảnh chỉ lưu trữ cục bộ (Local storage) để đảm bảo quyền riêng tư.
