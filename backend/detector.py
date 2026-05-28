"""
Fall Detector — FallGuard AI
=====================================================
Module phát hiện té ngã kết hợp:
  1. YOLOv11-Pose (ước lượng tư thế)
  2. Heuristic rules (velocity + aspect ratio + head position)
  3. Cooldown mechanism (chống spam cảnh báo)
  4. Configurable thresholds
"""

import cv2
import numpy as np
from ultralytics import YOLO
import time
import logging

logger = logging.getLogger('FallDetector')


class FallDetector:
    """
    Bộ phát hiện té ngã sử dụng YOLOv11-Pose.

    Thuật toán kết hợp 3 tín hiệu:
      1. Velocity: Vận tốc rơi của hông (dọc trục Y)
      2. Aspect Ratio: Tỷ lệ bounding box (nằm ngang → ngã)
      3. Head Position: Đầu thấp hơn hông → bất thường

    Kèm cooldown để tránh spam alert liên tục cho cùng 1 sự kiện.
    """

    def __init__(self, model_path='yolo11n-pose.pt', config=None):
        """
        Args:
            model_path: Đường dẫn tới model YOLO pose
            config: Dict cấu hình, hoặc None để dùng mặc định
        """
        self.model = YOLO(model_path)

        # Cấu hình mặc định — tối ưu cho camera thực tế
        default_config = {
            'confidence_threshold': 0.4,      # Giảm ngưỡng phát hiện người
            'velocity_threshold': 0.3,         # pixel/ms — nhạy hơn
            'prone_confirmation_frames': 2,    # số frame cần xác nhận (giảm xuống 2)
            'aspect_ratio_factor': 1.1,        # width > height * 1.1 = nằm ngang rõ ràng
            'head_hip_ratio': 0.85,            # đầu thấp hơn 85% vị trí hông
            'cooldown_seconds': 10,            # thời gian cooldown giữa các alert
            'keypoint_confidence': 0.3,        # giảm ngưỡng tin cậy keypoint
            'video_mode': False,               # True = chế độ xử lý video file
            'draw_debug_overlay': True,        # vẽ các thông số debug trên ảnh (bật/tắt)
        }

        if config:
            default_config.update(config)

        self.config = default_config

        # State tracking
        self.prev_hip_y = None
        self.prev_time = None
        self.velocity_y = 0
        self.prone_counter = 0

        # Cooldown
        self.last_fall_time = 0

        # Statistics
        self.total_frames = 0
        self.total_falls = 0
        self.total_detections = 0

        logger.info(f"FallDetector initialized: {self.config}")

    def update_config(self, new_config: dict):
        """Cập nhật cấu hình runtime."""
        self.config.update(new_config)
        logger.info(f"Config updated: {new_config}")

    def detect(self, frame):
        """
        Phát hiện té ngã từ 1 frame.

        Args:
            frame: np.ndarray (BGR image)

        Returns:
            (is_fall, annotated_frame, confidence, details)
            - is_fall: bool
            - annotated_frame: frame đã vẽ skeleton
            - confidence: float [0, 1]
            - details: dict chứa thông tin chi tiết
        """
        self.total_frames += 1

        results = self.model(frame, verbose=False)
        fall_detected = False
        confidence = 0.0
        details = {
            'velocity': 0.0,
            'is_prone': False,
            'head_low': False,
            'is_sudden_drop': False,
            'prone_counter': self.prone_counter,
            'in_cooldown': False,
            'persons_detected': 0,
        }

        if results[0].keypoints is not None and results[0].boxes is not None:
            try:
                # Extract all detected persons' keypoints and boxes
                all_kpts = results[0].keypoints.data.cpu().numpy()  # shape: (N, K, 3)
                all_boxes = results[0].boxes.data.cpu().numpy()     # shape: (N, 6?) boxes with conf

                num_persons = len(all_boxes)
                details['persons_detected'] = int(num_persons)

                # Determine best detection by confidence
                if num_persons > 0:
                    try:
                        confs = all_boxes[:, 4]
                    except Exception:
                        confs = np.array([0.0] * num_persons)

                    best_idx = int(np.argmax(confs))
                    boxes = all_boxes[best_idx]
                    keypoints = all_kpts[best_idx]
                    confidence = float(confs[best_idx])

                    # Include raw keypoints for all persons in details so frontend can render skeletons
                    kpts_list = []
                    for p in range(num_persons):
                        try:
                            pts = all_kpts[p].tolist()
                        except Exception:
                            pts = []
                        kpts_list.append(pts)
                    details['keypoints'] = kpts_list

                    if confidence > self.config['confidence_threshold']:
                        self.total_detections += 1
                        raw_fall, detail_info = self._analyze_fall(keypoints, boxes)
                        details.update(detail_info)

                        # Cooldown check
                        now = time.time()
                        in_cooldown = (now - self.last_fall_time) < self.config['cooldown_seconds']
                        details['in_cooldown'] = in_cooldown

                        if raw_fall and not in_cooldown:
                            fall_detected = True
                            self.last_fall_time = now
                            self.total_falls += 1
                            logger.warning(f"FALL DETECTED! Confidence: {confidence:.3f}, Details: {detail_info}")
                else:
                    details['keypoints'] = []
            except Exception as e:
                logger.error(f"Detection error: {e}")

        annotated = results[0].plot()

        # Ensure skeletons are explicitly drawn from keypoints (in case model.plot() doesn't show them)
        try:
            self._draw_skeletons(annotated, results[0].keypoints)
        except Exception:
            # Non-fatal: proceed if skeleton drawing fails
            pass

        # Vẽ debug overlay hiển thị thông số thời gian thực (có thể tắt bằng config)
        if self.config.get('draw_debug_overlay', True):
            self._draw_debug_overlay(annotated, details, confidence)

        # Vẽ overlay cảnh báo nếu phát hiện té ngã
        if fall_detected:
            self._draw_fall_overlay(annotated)

        return fall_detected, annotated, confidence, details

    def _analyze_fall(self, keypoints, box):
        """
        Phân tích té ngã từ keypoints và bounding box.

        Returns:
            (is_fall: bool, details: dict)
        """
        current_time = time.time() * 1000
        kp_conf = self.config['keypoint_confidence']

        # === 1. Tính toán vị trí hông ===
        avg_hip_y = None
        try:
            left_hip_ok = keypoints[11][2] > kp_conf
            right_hip_ok = keypoints[12][2] > kp_conf

            if left_hip_ok and right_hip_ok:
                avg_hip_y = (keypoints[11][1] + keypoints[12][1]) / 2
            elif left_hip_ok:
                avg_hip_y = keypoints[11][1]
            elif right_hip_ok:
                avg_hip_y = keypoints[12][1]
        except IndexError:
            pass

        # === 2. Velocity (vận tốc rơi) ===
        is_sudden_drop = False
        velocity = 0.0

        if avg_hip_y is not None and self.prev_hip_y is not None and self.prev_time is not None:
            dt = current_time - self.prev_time
            if dt > 0:
                dy = avg_hip_y - self.prev_hip_y
                velocity = dy / dt
                self.velocity_y = velocity
                if velocity > self.config['velocity_threshold']:
                    is_sudden_drop = True

        self.prev_hip_y = avg_hip_y
        self.prev_time = current_time

        # === 3. Aspect Ratio (tư thế nằm) ===
        x1, y1, x2, y2 = box[:4]
        width = x2 - x1
        height = y2 - y1
        is_prone = width > height * self.config['aspect_ratio_factor']

        # === 4. Head vs Hip ===
        head_low = False
        try:
            if keypoints[0][2] > kp_conf and avg_hip_y is not None:
                head_y = keypoints[0][1]
                if head_y > avg_hip_y * self.config['head_hip_ratio']:
                    head_low = True
        except (IndexError, TypeError):
            pass

        # === 5. Prone counter ===
        if is_prone or head_low:
            self.prone_counter += 1
        else:
            self.prone_counter = max(0, self.prone_counter - 1)

        # === 6. Kết luận ===
        prone_threshold = self.config['prone_confirmation_frames']
        vel_threshold = self.config['velocity_threshold']

        is_fall = (
            # Ngã đột ngột: tốc độ cao + tư thế bất thướlng
            (is_sudden_drop and (is_prone or head_low)) or
            # Nằm lâu: đủ frame xác nhận nằm ngang hoặc đầu thấp
            (self.prone_counter >= prone_threshold and (is_prone or head_low)) or
            # Chế độ video: phát hiện linh hoạt hơn
            (self.config.get('video_mode', False) and is_prone and velocity > 0.1)
        )

        details = {
            'velocity': round(velocity, 4),
            'is_prone': is_prone,
            'head_low': head_low,
            'is_sudden_drop': is_sudden_drop,
            'prone_counter': self.prone_counter,
            'aspect_ratio': round(width / max(height, 1), 3),
        }

        return is_fall, details

    def _draw_debug_overlay(self, frame, details, confidence):
        """Vẽ thông tin debug lên frame (được hiển thị luôn)."""
        h, w = frame.shape[:2]
        font = cv2.FONT_HERSHEY_SIMPLEX

        # Nền mờ cho debug panel
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, h - 120), (300, h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)

        y = h - 100
        color_ok = (0, 220, 100)
        color_warn = (0, 165, 255)
        color_fall = (0, 0, 255)

        vel = details.get('velocity', 0)
        prone = details.get('is_prone', False)
        head_low = details.get('head_low', False)
        prone_cnt = details.get('prone_counter', 0)
        persons = details.get('persons_detected', 0)
        in_cooldown = details.get('in_cooldown', False)

        vel_color = color_warn if vel > 0.2 else color_ok
        pose_color = color_warn if (prone or head_low) else color_ok
        cd_color = color_warn if in_cooldown else color_ok

        lines = [
            (f"Persons: {persons}  Conf: {confidence:.2f}", color_ok),
            (f"Velocity: {vel:.3f}  Prone: {'YES' if prone else 'no'}  HeadLow: {'YES' if head_low else 'no'}",
             pose_color if (prone or head_low) else color_ok),
            (f"Prone Counter: {prone_cnt}  Cooldown: {'YES' if in_cooldown else 'no'}",
             cd_color),
        ]

        for text, color in lines:
            cv2.putText(frame, text, (8, y), font, 0.5, color, 1, cv2.LINE_AA)
            y += 22

    def _draw_fall_overlay(self, frame):
        """Vẽ cảnh báo trực quan lên frame."""
        h, w = frame.shape[:2]

        # Viền đỏ
        cv2.rectangle(frame, (0, 0), (w - 1, h - 1), (0, 0, 255), 8)

        # Nền text
        overlay = frame.copy()
        cv2.rectangle(overlay, (w // 4, 10), (3 * w // 4, 80), (0, 0, 180), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        # Text cảnh báo
        text = "FALL DETECTED!"
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(text, font, 1.4, 3)[0]
        text_x = (w - text_size[0]) // 2
        cv2.putText(frame, text, (text_x, 55), font, 1.4, (255, 255, 255), 3)

        # Dòng phụ: TE NGA
        sub = "TE NGA - CANH BAO KHAN CAP!"
        sub_size = cv2.getTextSize(sub, font, 0.55, 1)[0]
        sub_x = (w - sub_size[0]) // 2
        cv2.putText(frame, sub, (sub_x, 75), font, 0.55, (255, 200, 0), 1)

    def set_video_mode(self, enabled: bool):
        """Bật/tắt chế độ video file (nhạy hơn, ngưỡng thấp hơn)."""
        self.config['video_mode'] = enabled
        if enabled:
            self.config['velocity_threshold'] = 0.15
            self.config['prone_confirmation_frames'] = 2
            self.config['keypoint_confidence'] = 0.25
        else:
            self.config['velocity_threshold'] = 0.3
            self.config['prone_confirmation_frames'] = 2
            self.config['keypoint_confidence'] = 0.3
        logger.info(f"Video mode {'enabled' if enabled else 'disabled'}: config updated")

    def _draw_skeletons(self, frame, keypoints_tensor):
        """Vẽ khung xương trực tiếp từ keypoints tensor/numpy.

        Supports tensors or numpy arrays of shape (N, K, 3) where K is keypoints count.
        """
        if keypoints_tensor is None:
            return

        # Convert to numpy if it's a tensor-like object
        try:
            kpts = keypoints_tensor.data.cpu().numpy()
        except Exception:
            try:
                kpts = np.array(keypoints_tensor)
            except Exception:
                return

        # COCO-style skeleton connections (17-keypoint ordering)
        skeleton = [
            (5, 6), (5, 7), (7, 9), (6, 8), (8, 10),
            (11, 12), (5, 11), (6, 12), (11, 13), (13, 15), (12, 14), (14, 16)
        ]

        h, w = frame.shape[:2]

        for person_kpts in kpts:
            # person_kpts shape: (K, 3)
            for a, b in skeleton:
                try:
                    xa, ya, ca = person_kpts[a]
                    xb, yb, cb = person_kpts[b]
                except Exception:
                    continue

                if ca > self.config.get('keypoint_confidence', 0.3) and cb > self.config.get('keypoint_confidence', 0.3):
                    pt1 = (int(xa), int(ya))
                    pt2 = (int(xb), int(yb))
                    cv2.line(frame, pt1, pt2, (0, 200, 255), 2, cv2.LINE_AA)

            # Draw keypoints
            for (x, y, c) in person_kpts:
                try:
                    if c > self.config.get('keypoint_confidence', 0.3):
                        cv2.circle(frame, (int(x), int(y)), 3, (0, 255, 0), -1)
                except Exception:
                    continue

    def get_stats(self) -> dict:
        """Trả về thống kê hiện tại."""
        return {
            'total_frames': self.total_frames,
            'total_falls': self.total_falls,
            'total_detections': self.total_detections,
            'fall_rate': self.total_falls / max(self.total_frames, 1),
            'config': self.config.copy(),
        }

    def reset(self):
        """Reset trạng thái detector."""
        self.prev_hip_y = None
        self.prev_time = None
        self.velocity_y = 0
        self.prone_counter = 0
        self.last_fall_time = 0
        self.total_frames = 0
        self.total_falls = 0
        self.total_detections = 0


if __name__ == '__main__':
    detector = FallDetector('../yolo11n-pose.pt')
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        is_fall, annotated, conf, details = detector.detect(frame)

        # Hiển thị stats
        stats = detector.get_stats()
        info = f"Frames: {stats['total_frames']} | Falls: {stats['total_falls']}"
        cv2.putText(annotated, info, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow("FallGuard AI", annotated)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
