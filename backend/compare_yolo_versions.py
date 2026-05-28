"""
YOLO Version Comparison — FallGuard AI
=====================================================
So sánh tốc độ và hiệu suất trích xuất pose giữa:
  - YOLOv11-Pose (local weight yolo11n-pose.pt)
  - YOLOv8n-Pose (Ultralytics pretrained weight yolov8n-pose.pt)

Script này tạo báo cáo JSON chứa:
  - total_frames
  - avg_inference_ms
  - frames_with_pose
  - pose_detection_rate
  - avg_confidence
  - total_falls (heuristic fall detection)

Chạy:
  python backend/compare_yolo_versions.py
"""

import argparse
import json
import time
from pathlib import Path
import cv2
from ultralytics import YOLO
from detector import FallDetector

BASE_DIR = Path(__file__).resolve().parent.parent
ARCHIVE_DIR = BASE_DIR / 'archive'
BENCHMARK_DIR = BASE_DIR / 'data' / 'benchmark'
BENCHMARK_DIR.mkdir(parents=True, exist_ok=True)

MODEL_SPECS = [
    {
        'name': 'YOLOv11-Pose',
        'path': str(BASE_DIR / 'yolo11n-pose.pt'),
        'tag': 'yolo11',
    },
    {
        'name': 'YOLOv8n-Pose',
        'path': 'yolov8n-pose.pt',
        'tag': 'yolov8n',
    },
]


class YoloPoseEvaluator:
    def __init__(self, model_path: str, model_name: str):
        self.model_name = model_name
        self.model_path = model_path
        self.detector = FallDetector(model_path=model_path)
        self.model = self.detector.model

    def evaluate_video(self, video_path: Path) -> dict:
        cap = cv2.VideoCapture(str(video_path))
        frame_count = 0
        pose_frames = 0
        total_confidence = 0.0
        total_confidence_count = 0
        total_falls = 0
        total_inference_time = 0.0

        print(f"Evaluating {self.model_name} on {video_path.name}...")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            start = time.perf_counter()
            results = self.model(frame, verbose=False)
            elapsed = (time.perf_counter() - start) * 1000.0
            total_inference_time += elapsed

            keypoints = None
            boxes = None
            if results[0].keypoints is not None and len(results[0].keypoints.data) > 0 and results[0].boxes is not None:
                try:
                    keypoints = results[0].keypoints.data[0].cpu().numpy()
                    boxes = results[0].boxes.data[0].cpu().numpy()
                except Exception:
                    keypoints = None
                    boxes = None

            if keypoints is not None and boxes is not None:
                pose_frames += 1
                total_confidence += float(boxes[4])
                total_confidence_count += 1

                # Phân tích fall detection bằng cùng heuristics như detector
                raw_fall, _ = self.detector._analyze_fall(keypoints, boxes)
                now = time.time()
                in_cooldown = (now - self.detector.last_fall_time) < self.detector.config['cooldown_seconds']
                if raw_fall and not in_cooldown:
                    total_falls += 1
                    self.detector.last_fall_time = now

                if float(boxes[4]) > self.detector.config['confidence_threshold']:
                    self.detector.total_detections += 1

        cap.release()

        avg_confidence = total_confidence / max(total_confidence_count, 1)
        pose_rate = pose_frames / max(frame_count, 1)
        avg_inference_ms = total_inference_time / max(frame_count, 1)

        return {
            'model_name': self.model_name,
            'model_path': self.model_path,
            'video': video_path.name,
            'total_frames': frame_count,
            'pose_frames': pose_frames,
            'pose_detection_rate': round(pose_rate, 4),
            'avg_confidence': round(avg_confidence, 4),
            'avg_inference_ms': round(avg_inference_ms, 4),
            'total_falls': total_falls,
            'total_detections': self.detector.total_detections,
        }


def find_video_files(source_dir: Path) -> list[Path]:
    videos = [p for p in source_dir.glob('*.mp4') if p.is_file()]
    return sorted(videos)


def main() -> None:
    parser = argparse.ArgumentParser(description='Compare YOLOv11-Pose and YOLOv8n-Pose performance.')
    parser.add_argument('--videos', nargs='+', default=None, help='Video file(s) to evaluate')
    parser.add_argument('--output', default=str(BENCHMARK_DIR / 'yolo_pose_comparison.json'), help='Output JSON path')
    args = parser.parse_args()

    videos = []
    if args.videos:
        videos = [Path(v) for v in args.videos]
    else:
        videos = find_video_files(ARCHIVE_DIR)

    if not videos:
        raise FileNotFoundError(f'No video files found in {ARCHIVE_DIR}. Add sample MP4 files or pass --videos.')

    comparison = {
        'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'videos': [v.name for v in videos],
        'models': [],
    }

    for spec in MODEL_SPECS:
        evaluator = YoloPoseEvaluator(spec['path'], spec['name'])
        for video_path in videos:
            result = evaluator.evaluate_video(video_path)
            comparison['models'].append(result)
            print(json.dumps(result, indent=2, ensure_ascii=False))

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)

    print(f"\nComparison report saved to {args.output}")


if __name__ == '__main__':
    main()
