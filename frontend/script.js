/* FallGuard AI — Dashboard JavaScript */

// ═══ DOM Elements ═══
const video = document.getElementById('input-video');
const canvas = document.getElementById('output-canvas');
const ctx = canvas.getContext('2d');
const startBtn = document.getElementById('start-btn');
const systemStatus = document.getElementById('system-status');
const recentAlertsList = document.getElementById('recent-alerts-list');
const historyGrid = document.getElementById('history-grid');
const fallOverlay = document.getElementById('fall-overlay');
const fpsCounter = document.getElementById('fps-counter');
const overlayMetricsPanel = document.getElementById('overlay-metrics-panel');
const overlayConf = document.getElementById('overlay-conf');
const overlayVel = document.getElementById('overlay-vel');
const overlayPose = document.getElementById('overlay-pose');
const overlayPersons = document.getElementById('overlay-persons');
const overlayAspect = document.getElementById('overlay-aspect');
const overlayProne = document.getElementById('overlay-prone');
const fallOverlayConf = document.getElementById('fall-overlay-conf');
const fallOverlayVel = document.getElementById('fall-overlay-vel');
const fallOverlayPose = document.getElementById('fall-overlay-pose');
const alertSound = document.getElementById('alert-sound');
const alertCount = document.getElementById('alert-count');
const noFeed = document.getElementById('no-feed');
const cameraSelect = document.getElementById('camera-select');

// Tab elements
const tabBtns = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

// Settings elements
const setConfidence = document.getElementById('set-confidence');
const setVelocity = document.getElementById('set-velocity');
const setCooldown = document.getElementById('set-cooldown');
const setProne = document.getElementById('set-prone');
const setSound = document.getElementById('set-sound');
const setBrowserNotif = document.getElementById('set-browser-notif');
const setEmailNotif = document.getElementById('set-email-notif');

// State
let ws = null;
let isMonitoring = false;
let lastFrameTime = performance.now();
let sessionAlertCount = 0;
let weeklyChart = null;
let hourlyChart = null;
let statsInterval = null;

// Config
const API_URL = window.location.origin;
const WS_URL = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/detect`;

// ═══ TAB SWITCHING ═══
tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const tabId = btn.getAttribute('data-tab');
        tabBtns.forEach(b => b.classList.remove('active'));
        tabContents.forEach(c => c.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById(`${tabId}-tab`).classList.add('active');
        
        if (tabId === 'history') fetchHistory();
        if (tabId === 'stats') {
            fetchStats();
            fetchModelComparison();
        }
        if (tabId === 'settings') loadSettings();
    });
});

// ═══ TOAST NOTIFICATION ═══
function showToast(message, type = 'info', duration = 3000) {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    const icons = { success: 'check-circle', error: 'times-circle', info: 'info-circle', warning: 'exclamation-triangle' };
    toast.innerHTML = `<i class="fas fa-${icons[type] || 'info-circle'}"></i> ${message}`;
    container.appendChild(toast);
    setTimeout(() => { toast.classList.add('toast-exit'); setTimeout(() => toast.remove(), 300); }, duration);
}

// ═══ CAMERA SETUP ═══
async function enumerateCameras() {
    try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoDevices = devices.filter(d => d.kind === 'videoinput');
        if (videoDevices.length === 0) return;

        const currentVal = cameraSelect.value;
        cameraSelect.innerHTML = '';

        const defaultOpt = document.createElement('option');
        defaultOpt.value = '';
        defaultOpt.textContent = 'Default Camera';
        cameraSelect.appendChild(defaultOpt);

        videoDevices.forEach((device, i) => {
            const option = document.createElement('option');
            option.value = device.deviceId;
            option.textContent = device.label || `Camera ${i + 1}`;
            cameraSelect.appendChild(option);
        });

        if (currentVal) {
            const exists = Array.from(cameraSelect.options).some(o => o.value === currentVal);
            if (exists) cameraSelect.value = currentVal;
        }
    } catch (e) { console.error('Camera enumeration failed:', e); }
}

async function setupWebcam() {
    try {
        if (video.srcObject) {
            video.srcObject.getTracks().forEach(t => t.stop());
            video.srcObject = null;
        }

        const deviceId = cameraSelect.value;
        let constraints;

        if (deviceId && deviceId !== '0' && deviceId.length > 5) {
            constraints = { video: { deviceId: { exact: deviceId }, width: { ideal: 320 }, height: { ideal: 240 } } };
        } else {
            constraints = { video: { width: { ideal: 320 }, height: { ideal: 240 }, facingMode: 'user' } };
        }

        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        video.srcObject = stream;

        await new Promise((resolve, reject) => {
            const timeout = setTimeout(() => reject(new Error('Camera timeout')), 10000);
            video.onloadedmetadata = () => {
                video.play().then(() => { clearTimeout(timeout); resolve(); }).catch(e => { clearTimeout(timeout); resolve(); });
            };
            video.onerror = () => { clearTimeout(timeout); reject(new Error('Video error')); };
        });

        await enumerateCameras();
        return true;
    } catch (err) {
        showToast('Camera setup failed: ' + err.message, 'error');
        throw err;
    }
}

// ═══ WEBSOCKET ═══
function connectWebSocket() {
    ws = new WebSocket(WS_URL);

    ws.onopen = () => {
        systemStatus.innerHTML = '<span class="status-dot"></span> Online';
        systemStatus.className = 'status-badge status-online';
        noFeed.classList.add('hidden');
        
        // Ensure detector is in normal mode
        fetch(`${API_URL}/api/detector/video-mode`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ enabled: false })
        }).catch(e => console.error(e));
    };

    ws.onclose = () => {
        systemStatus.innerHTML = '<span class="status-dot"></span> Offline';
        systemStatus.className = 'status-badge status-offline';
        if (isMonitoring) setTimeout(connectWebSocket, 2000);
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            if (data.annotated_image) {
                window.lastAnnotatedTime = performance.now();
                const img = new Image();
                img.onload = () => { canvas.width = img.width; canvas.height = img.height; ctx.drawImage(img, 0, 0); };
                img.src = data.annotated_image;
            }
            // If server provided raw keypoints, draw skeletons client-side for clarity
            if (data.details && data.details.keypoints && Array.isArray(data.details.keypoints) && data.details.keypoints.length > 0) {
                // Draw after image render
                const drawAfter = () => {
                    try {
                        drawClientSkeletons(ctx, data.details.keypoints);
                    } catch (e) { console.error('Client skeleton draw error', e); }
                };
                // If annotated_image is present, wait a tick to ensure image drawn
                if (data.annotated_image) setTimeout(drawAfter, 20);
                else drawAfter();
            }
            if (data.details) {
                document.getElementById('det-persons').textContent = data.details.persons_detected || 0;
                document.getElementById('det-velocity').textContent = (data.details.velocity || 0).toFixed(3);
                document.getElementById('det-conf').textContent = `${((data.confidence || 0) * 100).toFixed(1)}%`;
                const pose = data.details.is_prone ? 'Prone' : (data.details.head_low ? 'Head Low' : 'Normal');
                const poseEl = document.getElementById('det-pose');
                poseEl.textContent = pose;
                poseEl.style.color = pose === 'Normal' ? 'var(--success)' : 'var(--danger)';

                updateOverlayMetrics(data);
            }
            if (data.fall_detected) triggerAlarm(data);
            else fallOverlay.classList.remove('active');

            const now = performance.now();
            fpsCounter.textContent = `${Math.round(1000 / (now - lastFrameTime))} FPS`;
            lastFrameTime = now;
        } catch (err) { console.error(err); }
    };
}

// Client-side skeleton drawing using COCO-like keypoint ordering
function drawClientSkeletons(ctx, keypointsList) {
    if (!ctx || !keypointsList) return;
    const skeleton = [
        [5,6],[5,7],[7,9],[6,8],[8,10],[11,12],[5,11],[6,12],[11,13],[13,15],[12,14],[14,16]
    ];

    ctx.save();
    ctx.lineWidth = 2;
    keypointsList.forEach(person => {
        // person: array of [x,y,c]
        ctx.strokeStyle = 'rgba(0,200,255,0.9)';
        ctx.fillStyle = 'rgba(0,255,0,0.9)';
        skeleton.forEach(seg => {
            const a = person[seg[0]]; const b = person[seg[1]];
            if (!a || !b) return;
            const [xa, ya, ca] = a; const [xb, yb, cb] = b;
            if (ca > 0.25 && cb > 0.25) {
                ctx.beginPath(); ctx.moveTo(xa, ya); ctx.lineTo(xb, yb); ctx.stroke();
            }
        });
        // keypoints
        person.forEach(kp => {
            if (!kp) return;
            const [x, y, c] = kp;
            if (c > 0.25) {
                ctx.beginPath(); ctx.arc(x, y, 3, 0, Math.PI*2); ctx.fill();
            }
        });
    });
    ctx.restore();
}

// ═══ ALARM ═══
function triggerAlarm(data, isVideoMode = false) {
    if (isVideoMode) {
        document.getElementById('video-fall-badge').classList.remove('hidden');
        
        if (setSound.checked) {
            alertSound.currentTime = 0;
            alertSound.play().catch(() => {});
        }
        
        const timeStr = new Date().toLocaleTimeString('vi-VN');
        const alertHtml = `
            <div class="alert-item">
                <div class="alert-time">${timeStr}</div>
                <div class="alert-msg">⚠️ Phát hiện té ngã (Video)!</div>
                <div class="alert-detail">Conf: ${((data.confidence || 0) * 100).toFixed(1)}% | Vel: ${(data.details?.velocity || 0).toFixed(3)}</div>
            </div>`;
        const list = document.getElementById('video-alerts-list');
        if (list.querySelector('.empty-state')) list.innerHTML = '';
        list.insertAdjacentHTML('afterbegin', alertHtml);
        
        const countEl = document.getElementById('vid-alert-count');
        countEl.textContent = parseInt(countEl.textContent) + 1;
        document.getElementById('vid-falls').textContent = countEl.textContent;
        return;
    }

    if (fallOverlay.classList.contains('active')) return;

    fallOverlay.classList.add('active');
    sessionAlertCount++;
    alertCount.textContent = sessionAlertCount;
    if (fallOverlayConf) fallOverlayConf.textContent = `${((data.confidence || 0) * 100).toFixed(1)}%`;
    if (fallOverlayVel) fallOverlayVel.textContent = (data.details?.velocity || 0).toFixed(3);
    if (fallOverlayPose) fallOverlayPose.textContent = data.details?.is_prone ? 'Prone' : data.details?.head_low ? 'Head Low' : 'Normal';
    if (fallOverlayPose) fallOverlayPose.style.color = data.details?.is_prone || data.details?.head_low ? 'var(--danger)' : 'var(--success)';

    if (setSound.checked) {
        alertSound.currentTime = 0;
        alertSound.play().catch(() => {});
    }

    if (setBrowserNotif.checked && Notification.permission === 'granted') {
        new Notification('⚠️ FallGuard AI Alert', { body: `Fall detected! Confidence: ${((data.confidence || 0) * 100).toFixed(1)}%`, icon: '🛡️' });
    }

    const time = new Date().toLocaleTimeString('vi-VN');
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert-item';
    alertDiv.innerHTML = `
        <div class="alert-time">${time}</div>
        <div class="alert-msg">⚠️ Phát hiện té ngã!</div>
        <div class="alert-detail">Conf: ${((data.confidence || 0) * 100).toFixed(1)}% | Vel: ${(data.details?.velocity || 0).toFixed(3)}</div>
    `;

    if (recentAlertsList.querySelector('.empty-state')) recentAlertsList.innerHTML = '';
    recentAlertsList.insertBefore(alertDiv, recentAlertsList.firstChild);

    setTimeout(() => fallOverlay.classList.remove('active'), 5000);
}

function updateOverlayMetrics(data) {
    if (!data || !data.details) return;
    if (overlayMetricsPanel) overlayMetricsPanel.classList.remove('hidden');
    if (overlayConf) overlayConf.textContent = `${((data.confidence || 0) * 100).toFixed(1)}%`;
    if (overlayVel) overlayVel.textContent = (data.details.velocity || 0).toFixed(3);
    const poseState = data.details.is_prone ? 'Prone' : (data.details.head_low ? 'Head Low' : 'Normal');
    if (overlayPose) {
        overlayPose.textContent = poseState;
        overlayPose.style.color = poseState === 'Normal' ? 'var(--success)' : 'var(--danger)';
    }
    if (overlayPersons) overlayPersons.textContent = data.details.persons_detected || 0;
    if (overlayAspect) overlayAspect.textContent = (data.details.aspect_ratio || 0).toFixed(2);
    if (overlayProne) overlayProne.textContent = data.details.prone_counter || 0;
}

// ═══ SEND FRAME ═══
function sendFrame() {
    if (!isMonitoring) return;
    if (ws?.readyState === WebSocket.OPEN && video.readyState >= 2 && video.videoWidth > 0 && video.videoHeight > 0) {
        if (!window.lastAnnotatedTime || performance.now() - window.lastAnnotatedTime > 1000) {
            canvas.width = video.videoWidth; canvas.height = video.videoHeight;
            ctx.drawImage(video, 0, 0);
            ctx.fillStyle = "red"; ctx.font = "20px Arial"; ctx.fillText("Đang chờ phản hồi từ AI... (Raw Camera)", 10, 30);
        }
        const temp = document.createElement('canvas');
        // Lower capture resolution for faster network + encoding
        temp.width = 160; temp.height = 120;
        temp.getContext('2d').drawImage(video, 0, 0, 160, 120);
        // Reduce JPEG quality to lower payload size
        const dataUrl = temp.toDataURL('image/jpeg', 0.45);
        try { ws.send(JSON.stringify({ image: dataUrl })); } catch (e) { console.warn('WS send failed', e); }
    }
    // Throttle sending to ~10 FPS to reduce latency and CPU usage
    if (isMonitoring) setTimeout(() => requestAnimationFrame(sendFrame), 100);
}

// ═══ START/STOP ═══
startBtn.addEventListener('click', async () => {
    if (!isMonitoring) {
        try {
            await setupWebcam();
            connectWebSocket();
            isMonitoring = true;
            startBtn.innerHTML = '<i class="fas fa-stop"></i> Stop Monitoring';
            startBtn.className = 'btn btn-stop';
            sendFrame();
            statsInterval = setInterval(fetchStatsQuiet, 30000);
            showToast('Monitoring started', 'success');
        } catch (e) { }
    } else {
        isMonitoring = false;
        if (ws) ws.close();
        if (video.srcObject) video.srcObject.getTracks().forEach(t => t.stop());
        startBtn.innerHTML = '<i class="fas fa-play"></i> Start Monitoring';
        startBtn.className = 'btn btn-primary';
        noFeed.classList.remove('hidden');
        if (overlayMetricsPanel) overlayMetricsPanel.classList.add('hidden');
        fallOverlay.classList.remove('active');
        if (statsInterval) clearInterval(statsInterval);
        showToast('Monitoring stopped', 'info');
    }
});

// ═══ VIDEO UPLOAD TEST LOGIC ═══
const videoInput = document.getElementById('video-file-input');
const browseVideoBtn = document.getElementById('browse-video-btn');
const uploadZone = document.getElementById('upload-zone');
const videoPlayer = document.getElementById('upload-video-player');
const videoInfoBar = document.getElementById('video-info-bar');
const videoFilename = document.getElementById('video-filename');
const videoDuration = document.getElementById('video-duration');
const clearVideoBtn = document.getElementById('clear-video-btn');
const analyzeVideoBtn = document.getElementById('analyze-video-btn');
const stopVideoBtn = document.getElementById('stop-video-btn');
const videoProgressBar = document.getElementById('video-progress-bar');
const videoProgressText = document.getElementById('video-progress-text');
const videoProgressWrap = document.getElementById('video-progress-wrap');
const videoOutputCanvas = document.getElementById('video-output-canvas');
const videoCtx = videoOutputCanvas.getContext('2d');

let isAnalyzingVideo = false;

browseVideoBtn.addEventListener('click', () => videoInput.click());
uploadZone.addEventListener('dragover', e => { e.preventDefault(); uploadZone.classList.add('dragover'); });
uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('dragover'));
uploadZone.addEventListener('drop', e => {
    e.preventDefault(); uploadZone.classList.remove('dragover');
    if (e.dataTransfer.files.length) handleVideoFile(e.dataTransfer.files[0]);
});
videoInput.addEventListener('change', e => {
    if (e.target.files.length) handleVideoFile(e.target.files[0]);
});

function handleVideoFile(file) {
    if (!file.type.startsWith('video/')) {
        showToast('Vui lòng chọn file video', 'error');
        return;
    }
    
    const url = URL.createObjectURL(file);
    videoPlayer.src = url;
    videoFilename.textContent = file.name;
    
    videoPlayer.onloadedmetadata = () => {
        const mins = Math.floor(videoPlayer.duration / 60);
        const secs = Math.floor(videoPlayer.duration % 60).toString().padStart(2, '0');
        videoDuration.textContent = `${mins}:${secs}`;
        
        uploadZone.classList.add('hidden');
        videoInfoBar.classList.remove('hidden');
        analyzeVideoBtn.disabled = false;
        
        document.getElementById('video-no-result').classList.add('hidden');
        
        // Setup canvas
        videoOutputCanvas.width = videoPlayer.videoWidth;
        videoOutputCanvas.height = videoPlayer.videoHeight;
        videoCtx.drawImage(videoPlayer, 0, 0, videoOutputCanvas.width, videoOutputCanvas.height);
    };
}

clearVideoBtn.addEventListener('click', () => {
    videoPlayer.src = '';
    uploadZone.classList.remove('hidden');
    videoInfoBar.classList.add('hidden');
    analyzeVideoBtn.disabled = true;
    document.getElementById('video-no-result').classList.remove('hidden');
    videoCtx.clearRect(0, 0, videoOutputCanvas.width, videoOutputCanvas.height);
    resetVideoStats();
});

function resetVideoStats() {
    document.getElementById('vid-frame').textContent = '0';
    document.getElementById('vid-falls').textContent = '0';
    document.getElementById('vid-conf').textContent = '0%';
    document.getElementById('vid-pose').textContent = 'Normal';
    document.getElementById('vid-alert-count').textContent = '0';
    document.getElementById('video-alerts-list').innerHTML = '<div class="empty-state"><i class="fas fa-film empty-icon"></i><p>Chưa có sự kiện</p></div>';
    document.getElementById('video-fall-badge').classList.add('hidden');
}

analyzeVideoBtn.addEventListener('click', async () => {
    if (isAnalyzingVideo) return;
    
    // Stop live monitoring if running
    if (isMonitoring) startBtn.click();
    
    try {
        // Set detector to video mode
        await fetch(`${API_URL}/api/detector/video-mode`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ enabled: true })
        });
        
        isAnalyzingVideo = true;
        analyzeVideoBtn.classList.add('hidden');
        stopVideoBtn.classList.remove('hidden');
        videoProgressWrap.classList.remove('hidden');
        
        resetVideoStats();
        videoPlayer.currentTime = 0;
        
        processNextFrame();
    } catch (e) {
        showToast('Lỗi khi cấu hình AI', 'error');
        stopVideoAnalysis();
    }
});

stopVideoBtn.addEventListener('click', stopVideoAnalysis);

function stopVideoAnalysis() {
    isAnalyzingVideo = false;
    analyzeVideoBtn.classList.remove('hidden');
    stopVideoBtn.classList.add('hidden');
    videoProgressWrap.classList.add('hidden');
    showToast('Đã dừng phân tích', 'info');
}

async function processNextFrame() {
    if (!isAnalyzingVideo) return;
    
    if (videoPlayer.currentTime >= videoPlayer.duration || videoPlayer.ended) {
        isAnalyzingVideo = false;
        analyzeVideoBtn.classList.remove('hidden');
        stopVideoBtn.classList.add('hidden');
        videoProgressWrap.classList.add('hidden');
        showToast('Phân tích hoàn tất', 'success');
        return;
    }
    
    // Update progress
    const progress = (videoPlayer.currentTime / videoPlayer.duration) * 100;
    videoProgressBar.style.width = `${progress}%`;
    videoProgressText.textContent = `${Math.round(progress)}%`;
    
    // Create blob from frame
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = 640; 
    tempCanvas.height = 480;
    const tCtx = tempCanvas.getContext('2d');
    tCtx.drawImage(videoPlayer, 0, 0, tempCanvas.width, tempCanvas.height);
    
    tempCanvas.toBlob(async (blob) => {
        if (!blob) return;
        
        const formData = new FormData();
        formData.append('file', blob, 'frame.jpg');
        
        try {
            const res = await fetch(`${API_URL}/api/detect-frame`, {
                method: 'POST',
                body: formData
            });
            const data = await res.json();
            
            if (data.annotated_image) {
                const img = new Image();
                img.onload = () => {
                    videoCtx.clearRect(0, 0, videoOutputCanvas.width, videoOutputCanvas.height);
                    videoCtx.drawImage(img, 0, 0, videoOutputCanvas.width, videoOutputCanvas.height);
                };
                img.src = data.annotated_image;
            }
            
            // Update stats
            document.getElementById('vid-frame').textContent = Math.round(videoPlayer.currentTime * 30);
            document.getElementById('vid-conf').textContent = `${((data.confidence || 0) * 100).toFixed(1)}%`;
            
            if (data.details) {
                const pose = data.details.is_prone ? 'Prone' : (data.details.head_low ? 'Head Low' : 'Normal');
                document.getElementById('vid-pose').textContent = pose;
            }
            
            if (data.fall_detected) {
                triggerAlarm(data, true);
            }
            
        } catch (e) {
            console.error('Frame error', e);
        }
        
        // Advance video by ~0.1s (10 FPS for analysis is usually enough and faster)
        videoPlayer.currentTime += 0.1;
        
        // Allow UI to breathe
        requestAnimationFrame(processNextFrame);
        
    }, 'image/jpeg', 0.8);
}


// ═══ FETCH STATS ═══
async function fetchStats() {
    try {
        const res = await fetch(`${API_URL}/api/stats`);
        const data = await res.json();
        updateStatCards(data);
        updateCharts(data);
    } catch (e) { console.error('Stats fetch error:', e); }
}

async function fetchStatsQuiet() {
    try {
        const res = await fetch(`${API_URL}/api/stats`);
        const data = await res.json();
        updateStatCards(data);
    } catch (e) { }
}

function updateStatCards(data) {
    animateValue('stat-total-val', parseInt(document.getElementById('stat-total-val').textContent) || 0, data.total_incidents || 0);
    animateValue('stat-today-val', parseInt(document.getElementById('stat-today-val').textContent) || 0, data.today_incidents || 0);
    document.getElementById('stat-conf-val').textContent = `${((data.avg_confidence || 0) * 100).toFixed(1)}%`;
    document.getElementById('stat-uptime-val').textContent = data.uptime || '00:00:00';
}

function animateValue(elemId, start, end) {
    if (start === end) return;
    const el = document.getElementById(elemId);
    const duration = 600;
    const startTime = performance.now();
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.round(start + (end - start) * eased);
        if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
}

// ═══ FETCH MODEL COMPARISON ═══
async function fetchModelComparison() {
    try {
        const res = await fetch(`${API_URL}/api/model-comparison`);
        const data = await res.json();
        renderModelComparison(data);
    } catch (e) {
        console.error('Model comparison fetch error:', e);
        document.getElementById('model-comparison-content').innerHTML = `
            <div class="empty-state">
                <i class="fas fa-exclamation-triangle empty-icon"></i>
                <p>Không thể tải dữ liệu so sánh mô hình</p>
            </div>
        `;
    }
}

function renderModelComparison(data) {
    const container = document.getElementById('model-comparison-content');
    document.getElementById('comparison-source').textContent = `Source: ${data.source === 'benchmark_actual' ? 'Actual Benchmark' : 'Theoretical Data'}`;
    
    let html = `
        <div class="table-responsive">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Mô hình</th>
                        <th>Accuracy</th>
                        <th>Precision</th>
                        <th>Recall</th>
                        <th>F1-Score</th>
                        <th>AUC</th>
                        <th>Parameters</th>
                        <th>Time (s)</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    const models = Object.values(data.results).sort((a, b) => b.test_metrics.f1_score - a.test_metrics.f1_score);
    
    models.forEach(m => {
        const isMain = m.is_main;
        const metrics = m.test_metrics;
        
        html += `
            <tr class="${isMain ? 'highlight-row' : ''}">
                <td>
                    <div class="model-name">
                        ${m.architecture}
                        ${isMain ? '<span class="badge badge-success">Mô hình chính</span>' : ''}
                    </div>
                </td>
                <td>${(metrics.accuracy * 100).toFixed(2)}%</td>
                <td>${(metrics.precision * 100).toFixed(2)}%</td>
                <td>${(metrics.recall * 100).toFixed(2)}%</td>
                <td class="fw-bold text-primary">${(metrics.f1_score * 100).toFixed(2)}%</td>
                <td>${(metrics.auc * 100).toFixed(2)}%</td>
                <td>${m.num_params.toLocaleString()}</td>
                <td>${m.training_time_seconds.toFixed(1)}</td>
            </tr>
        `;
    });
    
    html += `
                </tbody>
            </table>
        </div>
        <div class="model-summary-box mt-3">
            <strong>Kết luận:</strong> Mô hình tốt nhất là <span class="badge badge-blue">${data.best_model}</span> với F1-Score <strong>${(data.best_f1_score * 100).toFixed(2)}%</strong>.
            Hệ thống hiện tại đang triển khai <strong>Bi-LSTM + Attention</strong> do cân bằng tốt giữa tốc độ phát hiện thời gian thực và độ chính xác cao.
        </div>
    `;
    
    container.innerHTML = html;
}

// ═══ CHARTS ═══
function updateCharts(data) {
    const weeklyCtx = document.getElementById('weekly-chart');
    if (weeklyChart) weeklyChart.destroy();

    const days = (data.daily_breakdown || []).map(d => d.day);
    const counts = (data.daily_breakdown || []).map(d => d.count);
    const last7 = [];
    for (let i = 6; i >= 0; i--) {
        const d = new Date(); d.setDate(d.getDate() - i);
        last7.push({ day: d.toISOString().split('T')[0].slice(5), count: 0 });
    }
    days.forEach((day, i) => {
        const match = last7.find(d => day.endsWith(d.day));
        if (match) match.count = counts[i];
    });

    weeklyChart = new Chart(weeklyCtx, {
        type: 'bar',
        data: {
            labels: last7.map(d => d.day),
            datasets: [{ label: 'Falls', data: last7.map(d => d.count), backgroundColor: 'rgba(99,102,241,0.5)', borderColor: '#6366f1', borderWidth: 2, borderRadius: 8, maxBarThickness: 40 }]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { stepSize: 1, color: '#64748b' } }, x: { ticks: { color: '#64748b' }, grid: { display: false } } } }
    });

    const hourlyCtx = document.getElementById('hourly-chart');
    if (hourlyChart) hourlyChart.destroy();

    const hours24 = Array.from({ length: 24 }, (_, i) => ({ hour: String(i).padStart(2, '0'), count: 0 }));
    (data.hourly_distribution || []).forEach(h => {
        const match = hours24.find(x => x.hour === h.hour);
        if (match) match.count = h.count;
    });

    hourlyChart = new Chart(hourlyCtx, {
        type: 'line',
        data: {
            labels: hours24.map(h => `${h.hour}:00`),
            datasets: [{ label: 'Falls', data: hours24.map(h => h.count), borderColor: '#ef4444', backgroundColor: 'rgba(239,68,68,0.1)', fill: true, tension: 0.4, pointRadius: 3, pointBackgroundColor: '#ef4444', borderWidth: 2 }]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { stepSize: 1, color: '#64748b' } }, x: { ticks: { color: '#64748b', maxTicksLimit: 12 }, grid: { display: false } } } }
    });
}

// ═══ HISTORY ═══
async function fetchHistory() {
    try {
        const res = await fetch(`${API_URL}/api/history`);
        const data = await res.json();
        historyGrid.innerHTML = '';
        if (!data.length) {
            historyGrid.innerHTML = '<div class="empty-state"><i class="fas fa-inbox empty-icon"></i><p>No history records found</p></div>';
            return;
        }
        data.forEach(item => {
            const date = item.timestamp ? new Date(item.timestamp).toLocaleString('vi-VN') : 'N/A';
            const div = document.createElement('div');
            div.className = 'history-item';
            div.innerHTML = `
                <button class="history-delete" data-id="${item.id}" title="Delete"><i class="fas fa-times"></i></button>
                <div class="history-img-wrap"><img src="${item.image_path}" class="history-img" alt="Fall capture"></div>
                <div class="history-info">
                    <div class="history-date">${date}</div>
                    <div class="history-conf">Confidence: ${((item.confidence || 0) * 100).toFixed(1)}%</div>
                </div>
            `;
            historyGrid.appendChild(div);
        });

        document.querySelectorAll('.history-delete').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                if (!confirm('Xóa sự cố này?')) return;
                try {
                    await fetch(`${API_URL}/api/history/${btn.dataset.id}`, { method: 'DELETE' });
                    showToast('Deleted', 'success');
                    fetchHistory();
                } catch (e) { showToast('Delete failed', 'error'); }
            });
        });
    } catch (e) { console.error('History error:', e); }
}

document.getElementById('export-csv-btn').addEventListener('click', () => { window.open(`${API_URL}/api/export`, '_blank'); });
document.getElementById('clear-history-btn').addEventListener('click', async () => {
    if (!confirm('Xóa toàn bộ lịch sử?')) return;
    try { await fetch(`${API_URL}/api/history`, { method: 'DELETE' }); showToast('History cleared', 'success'); fetchHistory(); } catch (e) { }
});
document.getElementById('refresh-history').addEventListener('click', () => { fetchHistory(); showToast('Refreshed', 'info'); });

// ═══ SETTINGS ═══
[[setConfidence, 'set-confidence-val', v => v], [setVelocity, 'set-velocity-val', v => v], [setCooldown, 'set-cooldown-val', v => v + 's'], [setProne, 'set-prone-val', v => v]].forEach(([input, labelId, fmt]) => {
    input.addEventListener('input', () => { document.getElementById(labelId).textContent = fmt(parseFloat(input.value).toFixed(2).replace(/\.?0+$/, '') || input.value); });
});
setEmailNotif.addEventListener('change', () => document.getElementById('email-settings').classList.toggle('hidden', !setEmailNotif.checked));

async function loadSettings() {
    try {
        const res = await fetch(`${API_URL}/api/settings`);
        const s = await res.json();
        if (s.confidence_threshold) { setConfidence.value = s.confidence_threshold; setConfidence.dispatchEvent(new Event('input')); }
        if (s.velocity_threshold) { setVelocity.value = s.velocity_threshold; setVelocity.dispatchEvent(new Event('input')); }
        if (s.cooldown_seconds) { setCooldown.value = s.cooldown_seconds; setCooldown.dispatchEvent(new Event('input')); }
        if (s.prone_confirmation_frames) { setProne.value = s.prone_confirmation_frames; setProne.dispatchEvent(new Event('input')); }
        setSound.checked = s.notification_sound === 'true';
        setBrowserNotif.checked = s.notification_browser === 'true';
        setEmailNotif.checked = s.notification_email === 'true';
        if (s.email_recipient) document.getElementById('set-email').value = s.email_recipient;
        if (s.email_smtp_host) document.getElementById('set-smtp-host').value = s.email_smtp_host;
        document.getElementById('email-settings').classList.toggle('hidden', !setEmailNotif.checked);
    } catch (e) { }
}

document.getElementById('save-settings-btn').addEventListener('click', async () => {
    try {
        await fetch(`${API_URL}/api/settings`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                confidence_threshold: setConfidence.value, velocity_threshold: setVelocity.value, cooldown_seconds: setCooldown.value,
                prone_confirmation_frames: setProne.value, notification_sound: setSound.checked.toString(),
                notification_browser: setBrowserNotif.checked.toString(), notification_email: setEmailNotif.checked.toString(),
                email_recipient: document.getElementById('set-email').value, email_smtp_host: document.getElementById('set-smtp-host').value,
            })
        });
        showToast('Settings saved successfully', 'success');
    } catch (e) { showToast('Failed to save settings', 'error'); }
});

setBrowserNotif.addEventListener('change', () => {
    if (setBrowserNotif.checked && Notification.permission !== 'granted') {
        Notification.requestPermission().then(perm => { if (perm !== 'granted') { setBrowserNotif.checked = false; showToast('Permission denied', 'warning'); } });
    }
});

// ═══ INIT ═══
(async function init() {
    await enumerateCameras();
    fetchStatsQuiet();
    loadSettings();
})();
