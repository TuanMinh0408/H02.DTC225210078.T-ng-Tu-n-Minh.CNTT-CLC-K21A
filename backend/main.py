"""
FallGuard AI — Main Server
=====================================================
Backend FastAPI với WebSocket real-time detection,
REST API cho thống kê, lịch sử, cài đặt, và export.

Endpoints:
  GET  /api/health       — Kiểm tra trạng thái server
  GET  /api/stats        — Thống kê tổng hợp
  GET  /api/history      — Danh sách lịch sử sự cố
  GET  /api/settings     — Lấy cài đặt hiện tại
  POST /api/settings     — Cập nhật cài đặt
  DELETE /api/history/{id} — Xóa 1 sự cố
  GET  /api/export       — Export CSV
  WS   /ws/detect        — WebSocket detection stream
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
import cv2
import numpy as np
import base64
import json
import asyncio
from detector import FallDetector
from model_comparison import load_comparison_data
import os
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
import io
import csv
import logging
import numpy as np

# ─── Logging ──────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger('FallGuard')

# ─── Paths ────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CAPTURES_DIR = DATA_DIR / "captures"
DB_PATH = DATA_DIR / "fall_detection.db"

CAPTURES_DIR.mkdir(parents=True, exist_ok=True)

# ─── App ──────────────────────────────────────────────────────────
app = FastAPI(
    title="FallGuard AI",
    description="Hệ thống phát hiện té ngã thông minh sử dụng Deep Learning",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Database ─────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            confidence REAL,
            image_path TEXT,
            is_fall BOOLEAN,
            velocity REAL DEFAULT 0,
            aspect_ratio REAL DEFAULT 0,
            notes TEXT DEFAULT ''
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')

    # Default settings
    defaults = {
        'confidence_threshold': '0.5',
        'velocity_threshold': '0.5',
        'cooldown_seconds': '10',
        'prone_confirmation_frames': '3',
        'notification_sound': 'true',
        'notification_browser': 'true',
        'notification_email': 'false',
        'email_recipient': '',
        'email_smtp_host': '',
        'email_smtp_port': '587',
        'email_smtp_user': '',
        'email_smtp_pass': '',
    }
    for key, val in defaults.items():
        cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', (key, val))

    conn.commit()
    conn.close()


init_db()


def _sanitize_for_json(obj):
    """Recursively convert numpy types and other non-JSON-native objects to Python builtins."""
    # dict
    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}
    # list/tuple
    if isinstance(obj, (list, tuple)):
        return [_sanitize_for_json(v) for v in obj]
    # numpy scalar
    if isinstance(obj, np.generic):
        try:
            return obj.item()
        except Exception:
            return obj.tolist() if hasattr(obj, 'tolist') else obj
    # numpy array
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    # datetime
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj

# ─── Detector ─────────────────────────────────────────────────────
DETECTOR_MODEL_PATH = Path(os.environ.get('FALL_MODEL_PATH', str(BASE_DIR / 'yolo11n-pose.pt')))
if not DETECTOR_MODEL_PATH.is_absolute():
    DETECTOR_MODEL_PATH = BASE_DIR / DETECTOR_MODEL_PATH
DETECTOR_MODEL_PATH = DETECTOR_MODEL_PATH.resolve()

if not DETECTOR_MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Fall detection model not found: {DETECTOR_MODEL_PATH}. "
        "Set FALL_MODEL_PATH to a valid model file or place yolo11n-pose.pt in the project root."
    )

logger.info(f"Loading detector model from {DETECTOR_MODEL_PATH}")
detector = FallDetector(model_path=str(DETECTOR_MODEL_PATH))
server_start_time = datetime.now()


# ─── REST API ─────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    uptime = str(datetime.now() - server_start_time).split('.')[0]
    stats = detector.get_stats()
    return {
        "status": "ok",
        "message": "FallGuard AI is running",
        "version": "2.0.0",
        "uptime": uptime,
        "total_frames_processed": stats['total_frames'],
    }


@app.get("/api/stats")
async def get_stats():
    """Thống kê tổng hợp cho dashboard."""
    conn = get_db()
    cursor = conn.cursor()

    # Total incidents
    cursor.execute('SELECT COUNT(*) as total FROM incidents WHERE is_fall = 1')
    total = cursor.fetchone()['total']

    # Today
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('SELECT COUNT(*) as today FROM incidents WHERE is_fall = 1 AND date(timestamp) = ?', (today,))
    today_count = cursor.fetchone()['today']

    # This week
    week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    cursor.execute('SELECT COUNT(*) as week FROM incidents WHERE is_fall = 1 AND date(timestamp) >= ?', (week_ago,))
    week_count = cursor.fetchone()['week']

    # Average confidence
    cursor.execute('SELECT AVG(confidence) as avg_conf FROM incidents WHERE is_fall = 1')
    row = cursor.fetchone()
    avg_conf = row['avg_conf'] if row['avg_conf'] else 0

    # Daily breakdown (last 7 days)
    cursor.execute('''
        SELECT date(timestamp) as day, COUNT(*) as count
        FROM incidents WHERE is_fall = 1
        AND date(timestamp) >= ?
        GROUP BY date(timestamp)
        ORDER BY day
    ''', (week_ago,))
    daily = [{'day': r['day'], 'count': r['count']} for r in cursor.fetchall()]

    # Hourly distribution
    cursor.execute('''
        SELECT strftime('%H', timestamp) as hour, COUNT(*) as count
        FROM incidents WHERE is_fall = 1
        GROUP BY hour ORDER BY hour
    ''')
    hourly = [{'hour': r['hour'], 'count': r['count']} for r in cursor.fetchall()]

    # Uptime
    uptime = str(datetime.now() - server_start_time).split('.')[0]

    conn.close()

    return {
        'total_incidents': total,
        'today_incidents': today_count,
        'week_incidents': week_count,
        'avg_confidence': round(avg_conf, 4),
        'daily_breakdown': daily,
        'hourly_distribution': hourly,
        'uptime': uptime,
        'detector_stats': detector.get_stats(),
    }


@app.get("/api/history")
async def get_history(limit: int = 50, offset: int = 0):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM incidents ORDER BY timestamp DESC LIMIT ? OFFSET ?',
        (limit, offset)
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


@app.delete("/api/history/{incident_id}")
async def delete_incident(incident_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT image_path FROM incidents WHERE id = ?', (incident_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Incident not found")

    # Xóa file ảnh
    if row['image_path']:
        img_path = BASE_DIR / row['image_path'].lstrip('/')
        if img_path.exists():
            img_path.unlink()

    cursor.execute('DELETE FROM incidents WHERE id = ?', (incident_id,))
    conn.commit()
    conn.close()
    return {"message": "Deleted successfully"}


@app.delete("/api/history")
async def clear_history():
    """Xóa toàn bộ lịch sử."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM incidents')
    conn.commit()
    conn.close()

    # Xóa tất cả captures
    for f in CAPTURES_DIR.glob('*.jpg'):
        f.unlink()

    return {"message": "All history cleared"}


@app.get("/api/export")
async def export_csv():
    """Export lịch sử sự cố ra CSV."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM incidents ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Timestamp', 'Confidence', 'Image Path', 'Is Fall', 'Velocity', 'Aspect Ratio', 'Notes'])
    for row in rows:
        writer.writerow([row['id'], row['timestamp'], row['confidence'],
                        row['image_path'], row['is_fall'],
                        row['velocity'], row['aspect_ratio'], row['notes']])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename=fallguard_history_{datetime.now().strftime("%Y%m%d")}.csv'}
    )


@app.get("/api/model-comparison")
async def get_model_comparison():
    """Lấy dữ liệu so sánh các mô hình AI."""
    try:
        data = load_comparison_data()
        return data
    except Exception as e:
        logger.error(f"Model comparison error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/detector/reset")
async def reset_detector():
    """Reset trạng thái detector (dùng khi chuyển từ video sang camera hoặc ngược lại)."""
    detector.reset()
    logger.info("Detector state reset")
    return {"message": "Detector reset successfully"}


@app.post("/api/detector/video-mode")
async def set_video_mode(body: dict):
    """Bật/tắt chế độ video file (nhạy hơn, phù hợp với video ngã upload)."""
    enabled = bool(body.get("enabled", True))
    detector.set_video_mode(enabled)
    detector.reset()  # Reset state khi chuyển mode
    return {"message": f"Video mode {'enabled' if enabled else 'disabled'}", "video_mode": enabled}


@app.post("/api/detect-frame")
async def detect_single_frame(file: UploadFile = File(...)):
    """
    Phát hiện té ngã từ 1 frame ảnh upload (dùng cho video offline).
    Returns: JSON với kết quả detection.
    """
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image")

        is_fall, annotated_frame, confidence, details = detector.detect(frame)

        # Lưu nếu phát hiện ngã
        image_path = None
        if is_fall:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"fall_{timestamp}.jpg"
            save_path = CAPTURES_DIR / filename
            cv2.imwrite(str(save_path), annotated_frame)
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO incidents (confidence, image_path, is_fall, velocity, aspect_ratio)
                   VALUES (?, ?, ?, ?, ?)''',
                (float(confidence), f"/captures/{filename}", True,
                 float(details.get('velocity', 0)), float(details.get('aspect_ratio', 0)))
            )
            conn.commit()
            conn.close()
            image_path = f"/captures/{filename}"
            logger.info(f"Fall recorded from frame upload: {filename}")

        # Encode annotated frame
        res, buffer = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        encoded_image = base64.b64encode(buffer.tobytes()).decode('utf-8')

        return {
            "fall_detected": bool(is_fall),
            "confidence": round(float(confidence), 4),
            "annotated_image": f"data:image/jpeg;base64,{encoded_image}",
            "image_path": image_path,
            "details": {
                "velocity": float(details.get('velocity', 0)),
                "is_prone": bool(details.get('is_prone', False)),
                "head_low": bool(details.get('head_low', False)),
                "prone_counter": int(details.get('prone_counter', 0)),
                "persons_detected": int(details.get('persons_detected', 0)),
                "aspect_ratio": float(details.get('aspect_ratio', 0)),
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Frame detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/settings")
async def get_settings():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT key, value FROM settings')
    settings = {r['key']: r['value'] for r in cursor.fetchall()}
    conn.close()
    return settings


@app.post("/api/settings")
async def update_settings(new_settings: dict):
    conn = get_db()
    cursor = conn.cursor()

    for key, value in new_settings.items():
        cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
                       (key, str(value)))

    conn.commit()
    conn.close()

    # Cập nhật detector config
    detector_keys = ['confidence_threshold', 'velocity_threshold', 'cooldown_seconds', 'prone_confirmation_frames']
    detector_update = {}
    for k in detector_keys:
        if k in new_settings:
            try:
                detector_update[k] = float(new_settings[k])
            except (ValueError, TypeError):
                pass

    if detector_update:
        detector.update_config(detector_update)

    return {"message": "Settings updated", "updated_keys": list(new_settings.keys())}


# ─── WebSocket ────────────────────────────────────────────────────

@app.websocket("/ws/detect")
async def detect_fall_websocket(websocket: WebSocket):
    await websocket.accept()
    logger.info("Client connected via WebSocket")
    # Disable server-side debug overlay for live websocket streaming
    try:
        detector.update_config({'draw_debug_overlay': False})
        logger.info('Debug overlay disabled for WebSocket client')
    except Exception:
        logger.exception('Failed to update detector config for websocket client')

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            image_data = payload.get("image")

            if not image_data:
                continue

            try:
                header, encoded = image_data.split(",", 1)
                logger.info(f"Received base64 encoded length: {len(encoded)}")
                nparr = np.frombuffer(base64.b64decode(encoded), np.uint8)
                logger.info(f"Decoded nparr length: {len(nparr)}")
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if frame is not None:
                    logger.info(f"Decoded frame shape: {frame.shape}")
                else:
                    logger.error("cv2.imdecode returned None!")
            except Exception as e:
                logger.error(f"Decode error: {e}")
                continue

            if frame is None:
                continue

            # Detect
            is_fall, annotated_frame, confidence, details = detector.detect(frame)

            # Lưu sự cố
            if is_fall:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                filename = f"fall_{timestamp}.jpg"
                save_path = CAPTURES_DIR / filename

                cv2.imwrite(str(save_path), annotated_frame)

                conn = get_db()
                cursor = conn.cursor()
                cursor.execute(
                    '''INSERT INTO incidents (confidence, image_path, is_fall, velocity, aspect_ratio)
                       VALUES (?, ?, ?, ?, ?)''',
                    (float(confidence), f"/captures/{filename}", True,
                     details.get('velocity', 0), details.get('aspect_ratio', 0))
                )
                conn.commit()
                conn.close()
                logger.info(f"Fall recorded: {filename}")

            # Encode response
            res, buffer = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
            if not res:
                logger.error("cv2.imencode failed!")
                continue
            encoded_image = base64.b64encode(buffer.tobytes()).decode('utf-8')
            logger.info(f"Sending response base64 length: {len(encoded_image)}")

            response = {
                "fall_detected": bool(is_fall),
                "confidence": round(float(confidence), 4),
                "annotated_image": f"data:image/jpeg;base64,{encoded_image}",
                "details": {
                    "velocity": details.get('velocity', 0),
                    "is_prone": details.get('is_prone', False),
                    "head_low": details.get('head_low', False),
                    "prone_counter": details.get('prone_counter', 0),
                    "persons_detected": details.get('persons_detected', 0),
                }
            }

            # Sanitize response to ensure all types are JSON-serializable (numpy types -> native)
            safe_resp = _sanitize_for_json(response)
            await websocket.send_text(json.dumps(safe_resp))

    except WebSocketDisconnect:
        logger.info("Client disconnected")
        # Restore debug overlay default when client disconnects
        try:
            detector.update_config({'draw_debug_overlay': True})
            logger.info('Debug overlay restored after WebSocket disconnect')
        except Exception:
            logger.exception('Failed to restore detector config after disconnect')
    except Exception as e:
        logger.error(f"WebSocket error: {e}")


# ─── Static files ────────────────────────────────────────────────
app.mount("/captures", StaticFiles(directory=str(CAPTURES_DIR)), name="captures")
app.mount("/", StaticFiles(directory=str(BASE_DIR / "frontend"), html=True), name="frontend")


if __name__ == "__main__":
    import socket
    import uvicorn

    server_host = os.environ.get('FALL_SERVER_HOST', '0.0.0.0')
    preferred_port = int(os.environ.get('FALL_SERVER_PORT', 8000))

    def find_free_port(start_port: int = 8000, host: str = '0.0.0.0') -> int:
        port = start_port
        while port < 9000:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                try:
                    sock.bind((host, port))
                    return port
                except OSError:
                    port += 1
        raise RuntimeError('No available port found between 8000 and 8999')

    server_port = preferred_port
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((server_host, server_port))
    except OSError:
        logger.warning(f"Port {server_port} unavailable. Finding free port...")
        server_port = find_free_port(preferred_port, server_host)

    logger.info(f"Starting FallGuard AI Server on {server_host}:{server_port}...")
    # Attempt to open the dashboard in Google Chrome (fallback to default browser)
    try:
        import threading
        import time
        import subprocess
        import shutil
        import webbrowser

        def _open_in_chrome(url: str):
            # Prefer explicit CHROME_PATH env var
            chrome_path = os.environ.get('CHROME_PATH')
            candidates = [chrome_path,
                          r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                          r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"]
            exe = None
            for p in candidates:
                if p and os.path.isfile(p):
                    exe = p
                    break

            if not exe:
                exe = shutil.which('chrome') or shutil.which('google-chrome') or shutil.which('chrome.exe')

            try:
                if exe:
                    subprocess.Popen([exe, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    webbrowser.open(url)
            except Exception as e:
                logger.warning(f"Failed to open browser automatically: {e}")

        def _delayed_open():
            # If server_host is 0.0.0.0, use localhost for browser
            open_host = 'localhost' if server_host in ('0.0.0.0', '::', '') else server_host
            url = f"http://{open_host}:{server_port}"
            # small delay to allow uvicorn to bind the port
            time.sleep(1.0)
            _open_in_chrome(url)

        threading.Thread(target=_delayed_open, daemon=True).start()
    except Exception:
        logger.debug('Auto-open browser thread failed to start')

    uvicorn.run(app, host=server_host, port=server_port)
