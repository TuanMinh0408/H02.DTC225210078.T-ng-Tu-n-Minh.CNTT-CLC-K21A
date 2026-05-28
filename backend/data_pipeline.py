import cv2
import numpy as np
import os
from ultralytics import YOLO
from pathlib import Path

def extract_keypoints_from_video(video_path, model, output_path):
    """
    Trích xuất tọa độ 17 keypoints từ video và lưu thành file .npy (Tuần 4).
    Format output: (N_frames, 17, 3) -> [x, y, conf]
    """
    cap = cv2.VideoCapture(str(video_path))
    all_keypoints = []
    
    print(f"Processing: {video_path.name}...")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        # Inference
        results = model(frame, verbose=False)
        
        # Lấy keypoints của người đầu tiên
        if results[0].keypoints is not None and len(results[0].keypoints.data) > 0:
            # results[0].keypoints.data[0] shape: [17, 3]
            kp = results[0].keypoints.data[0].cpu().numpy()
            if kp.shape == (17, 3):
                all_keypoints.append(kp)
            else:
                # Trường hợp đặc biệt (ví dụ model trả về shape khác)
                all_keypoints.append(np.zeros((17, 3)))
        else:
            # Nếu không thấy người, điền zero
            all_keypoints.append(np.zeros((17, 3)))
            
    cap.release()
    
    if all_keypoints:
        # Chuyển đổi list sang array một cách an toàn
        kp_array = np.stack(all_keypoints)
        np.save(output_path, kp_array)
        print(f"Saved {len(all_keypoints)} frames to {output_path}")
        return kp_array
    return None

if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent.parent
    VIDEO_DIR = BASE_DIR / "archive"
    OUTPUT_DIR = BASE_DIR / "data" / "processed"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load model
    model = YOLO(str(BASE_DIR / 'yolo11n-pose.pt'))
    
    # Processing videos
    video_files = list(VIDEO_DIR.glob("*.mp4"))
    
    for v_file in video_files:
        out_file = OUTPUT_DIR / f"{v_file.stem}_kp.npy"
        extract_keypoints_from_video(v_file, model, out_file)
