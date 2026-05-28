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
        if (tabId === 'stats') fetchStats();
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

        // Add a "Default Camera" option first
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

        // Restore previous selection if valid
        if (currentVal) {
            const exists = Array.from(cameraSelect.options).some(o => o.value === currentVal);
            if (exists) cameraSelect.value = currentVal;
        }
    } catch (e) { console.error('Camera enumeration failed:', e); }
}

async function setupWebcam() {
    try {
        // Stop any existing stream first
        if (video.srcObject) {
            video.srcObject.getTracks().forEach(t => t.stop());
            video.srcObject = null;
        }

        const deviceId = cameraSelect.value;
        let constraints;

        // Only use exact deviceId if we have a real device ID (not empty or "0")
        if (deviceId && deviceId !== '0' && deviceId.length > 5) {
            constraints = {
                video: {
                    deviceId: { exact: deviceId },
                    width: { ideal: 640 },
                    height: { ideal: 480 }
                }
            };
        } else {
            // Use default camera — no deviceId constraint
            constraints = {
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: 'user'
                }
            };
        }

        console.log('Requesting camera with constraints:', JSON.stringify(constraints));
        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        video.srcObject = stream;

        // Wait for video to be ready and playing
        await new Promise((resolve, reject) => {
            const timeout = setTimeout(() => reject(new Error('Camera timeout')), 10000);

            video.onloadedmetadata = () => {
                video.play()
                    .then(() => {
                        clearTimeout(timeout);
                        resolve();
                    })
                    .catch(playErr => {
                        clearTimeout(timeout);
                        // Autoplay may be blocked, but video is still ready
                        console.warn('Video autoplay blocked:', playErr);
                        resolve();
                    });
            };

            video.onerror = () => {
                clearTimeout(timeout);
                reject(new Error('Video element error'));
            };
        });

        // Re-enumerate cameras now that we have permission (labels become available)
        await enumerateCameras();

        console.log(`Camera ready: ${video.videoWidth}x${video.videoHeight}`);
        return true;

    } catch (err) {
        console.error('Camera setup failed:', err);

        let message = 'Cannot access webcam. ';
        if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
            message += 'Permission denied. Please allow camera access in browser settings.';
        } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
            message += 'No camera found. Please connect a camera.';
        } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
            message += 'Camera is in use by another application.';
        } else if (err.name === 'OverconstrainedError') {
            message += 'Selected camera not available. Trying default...';
            // Fallback: try without any deviceId constraint
            try {
                const fallbackStream = await navigator.mediaDevices.getUserMedia({
                    video: { width: { ideal: 640 }, height: { ideal: 480 } }
                });
                video.srcObject = fallbackStream;
                await new Promise(resolve => {
                    video.onloadedmetadata = () => { video.play().then(resolve).catch(resolve); };
                });
                await enumerateCameras();
                showToast('Using default camera (fallback)', 'warning');
                return true;
            } catch (fallbackErr) {
                message = 'No camera available. Check connection and permissions.';
            }
        } else {
            message += err.message || 'Unknown error.';
        }

        showToast(message, 'error', 5000);
        throw err;
    }
}

// ═══ WEBSOCKET ═══
function connectWebSocket() {
    ws = new WebSocket(WS_URL);

    ws.onopen = () => {
        console.log('Connected to Backend');
        systemStatus.innerHTML = '<span class="status-dot"></span> Online';
        systemStatus.className = 'status-badge status-online';
        noFeed.classList.add('hidden');
        showToast('Connected to FallGuard AI server', 'success');
    };

    ws.onclose = () => {
        systemStatus.innerHTML = '<span class="status-dot"></span> Offline';
        systemStatus.className = 'status-badge status-offline';
        if (isMonitoring) setTimeout(connectWebSocket, 2000);
    };

    ws.onerror = () => showToast('Connection error', 'error');

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);

            // Draw annotated frame
            if (data.annotated_image) {
                window.lastAnnotatedTime = performance.now();
                const img = new Image();
                img.onload = () => { canvas.width = img.width; canvas.height = img.height; ctx.drawImage(img, 0, 0); };
                img.src = data.annotated_image;
            }

            // Update detection details
            if (data.details) {
                document.getElementById('det-persons').textContent = data.details.persons_detected || 0;
                document.getElementById('det-velocity').textContent = (data.details.velocity || 0).toFixed(3);
                document.getElementById('det-conf').textContent = `${((data.confidence || 0) * 100).toFixed(1)}%`;
                const pose = data.details.is_prone ? 'Prone' : (data.details.head_low ? 'Head Low' : 'Normal');
                const poseEl = document.getElementById('det-pose');
                poseEl.textContent = pose;
                poseEl.style.color = pose === 'Normal' ? 'var(--success)' : 'var(--danger)';
            }

            // Fall detected
            if (data.fall_detected) {
                triggerAlarm(data);
            } else {
                fallOverlay.classList.remove('active');
            }

            // FPS
            const now = performance.now();
            const fps = Math.round(1000 / (now - lastFrameTime));
            fpsCounter.textContent = `${fps} FPS`;
            lastFrameTime = now;
        } catch (err) {
            console.error("WS Message Error:", err);
            fpsCounter.textContent = "JS ERROR";
            fpsCounter.style.color = "red";
        }
    };
}

// ═══ ALARM ═══
function triggerAlarm(data) {
    if (fallOverlay.classList.contains('active')) return;

    fallOverlay.classList.add('active');
    sessionAlertCount++;
    alertCount.textContent = sessionAlertCount;

    // Sound
    if (setSound.checked) {
        alertSound.currentTime = 0;
        alertSound.play().catch(() => {});
    }

    // Browser notification
    if (setBrowserNotif.checked && Notification.permission === 'granted') {
        new Notification('⚠️ FallGuard AI Alert', {
            body: `Fall detected! Confidence: ${((data.confidence || 0) * 100).toFixed(1)}%`,
            icon: '🛡️', requireInteraction: true,
        });
    }

    // Add to session alerts
    const time = new Date().toLocaleTimeString('vi-VN');
    const conf = ((data.confidence || 0) * 100).toFixed(1);
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert-item';
    alertDiv.innerHTML = `
        <div class="alert-time">${time}</div>
        <div class="alert-msg">⚠️ Phát hiện té ngã!</div>
        <div class="alert-detail">Confidence: ${conf}% | Velocity: ${(data.details?.velocity || 0).toFixed(3)}</div>
    `;

    if (recentAlertsList.querySelector('.empty-state')) recentAlertsList.innerHTML = '';
    recentAlertsList.insertBefore(alertDiv, recentAlertsList.firstChild);

    // Auto-hide overlay after 5s
    setTimeout(() => fallOverlay.classList.remove('active'), 5000);
}

// ═══ SEND FRAME ═══
function sendFrame() {
    if (!isMonitoring) return;

    // Only send if websocket is open and video is ready
    if (ws?.readyState === WebSocket.OPEN && video.readyState >= 2 && video.videoWidth > 0 && video.videoHeight > 0) {
        // ONLY draw raw camera feed if we haven't received AI frames recently
        if (!window.lastAnnotatedTime || performance.now() - window.lastAnnotatedTime > 1000) {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            ctx.drawImage(video, 0, 0);
            
            // Draw debug text
            ctx.fillStyle = "red";
            ctx.font = "20px Arial";
            ctx.fillText("Đang chờ phản hồi từ AI... (Raw Camera)", 10, 30);
        }

        const temp = document.createElement('canvas');
        const tCtx = temp.getContext('2d');
        temp.width = 320; temp.height = 240;
        tCtx.drawImage(video, 0, 0, 320, 240);

        const base64 = temp.toDataURL('image/jpeg', 0.6);
        ws.send(JSON.stringify({ image: base64 }));
    }

    // Schedule next frame (~15-20 FPS target)
    if (isMonitoring) {
        setTimeout(() => requestAnimationFrame(sendFrame), 50);
    }
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
        } catch (e) { /* webcam error already shown */ }
    } else {
        isMonitoring = false;
        if (ws) ws.close();
        if (video.srcObject) video.srcObject.getTracks().forEach(t => t.stop());
        startBtn.innerHTML = '<i class="fas fa-play"></i> Start Monitoring';
        startBtn.className = 'btn btn-primary';
        noFeed.classList.remove('hidden');
        if (statsInterval) clearInterval(statsInterval);
        showToast('Monitoring stopped', 'info');
    }
});

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
    } catch (e) { /* silent */ }
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

// ═══ CHARTS ═══
function updateCharts(data) {
    // Weekly chart
    const weeklyCtx = document.getElementById('weekly-chart');
    if (weeklyChart) weeklyChart.destroy();

    const days = (data.daily_breakdown || []).map(d => d.day);
    const counts = (data.daily_breakdown || []).map(d => d.count);

    // Fill missing days
    const last7 = [];
    for (let i = 6; i >= 0; i--) {
        const d = new Date(); d.setDate(d.getDate() - i);
        const ds = d.toISOString().split('T')[0];
        last7.push({ day: ds.slice(5), count: 0 });
    }
    days.forEach((day, i) => {
        const match = last7.find(d => day.endsWith(d.day));
        if (match) match.count = counts[i];
    });

    weeklyChart = new Chart(weeklyCtx, {
        type: 'bar',
        data: {
            labels: last7.map(d => d.day),
            datasets: [{ label: 'Falls', data: last7.map(d => d.count),
                backgroundColor: 'rgba(99,102,241,0.5)', borderColor: '#6366f1',
                borderWidth: 2, borderRadius: 8, maxBarThickness: 40 }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, ticks: { stepSize: 1, color: '#64748b' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                x: { ticks: { color: '#64748b' }, grid: { display: false } }
            }
        }
    });

    // Hourly chart
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
            datasets: [{ label: 'Falls', data: hours24.map(h => h.count),
                borderColor: '#ef4444', backgroundColor: 'rgba(239,68,68,0.1)',
                fill: true, tension: 0.4, pointRadius: 3, pointBackgroundColor: '#ef4444', borderWidth: 2 }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, ticks: { stepSize: 1, color: '#64748b' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                x: { ticks: { color: '#64748b', maxTicksLimit: 12 }, grid: { display: false } }
            }
        }
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
                <div class="history-img-wrap"><img src="${item.image_path}" class="history-img" alt="Fall capture" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 1 1%22><rect fill=%22%23111%22 width=%221%22 height=%221%22/></svg>';"></div>
                <div class="history-info">
                    <div class="history-date">${date}</div>
                    <div class="history-conf">Confidence: ${((item.confidence || 0) * 100).toFixed(1)}%</div>
                </div>
            `;
            historyGrid.appendChild(div);
        });

        // Delete handlers
        document.querySelectorAll('.history-delete').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const id = btn.dataset.id;
                if (!confirm('Xóa sự cố này?')) return;
                try {
                    await fetch(`${API_URL}/api/history/${id}`, { method: 'DELETE' });
                    showToast('Deleted', 'success');
                    fetchHistory();
                } catch (e) { showToast('Delete failed', 'error'); }
            });
        });
    } catch (e) { console.error('History error:', e); }
}

// ═══ EXPORT CSV ═══
document.getElementById('export-csv-btn').addEventListener('click', async () => {
    try {
        window.open(`${API_URL}/api/export`, '_blank');
        showToast('CSV export started', 'success');
    } catch (e) { showToast('Export failed', 'error'); }
});

// ═══ CLEAR HISTORY ═══
document.getElementById('clear-history-btn').addEventListener('click', async () => {
    if (!confirm('Xóa toàn bộ lịch sử? Hành động này không thể hoàn tác.')) return;
    try {
        await fetch(`${API_URL}/api/history`, { method: 'DELETE' });
        showToast('History cleared', 'success');
        fetchHistory();
    } catch (e) { showToast('Failed to clear', 'error'); }
});

document.getElementById('refresh-history').addEventListener('click', () => { fetchHistory(); showToast('Refreshed', 'info'); });

// ═══ SETTINGS ═══
// Range sliders live update
[
    [setConfidence, 'set-confidence-val', v => v],
    [setVelocity, 'set-velocity-val', v => v],
    [setCooldown, 'set-cooldown-val', v => v + 's'],
    [setProne, 'set-prone-val', v => v],
].forEach(([input, labelId, fmt]) => {
    input.addEventListener('input', () => {
        document.getElementById(labelId).textContent = fmt(parseFloat(input.value).toFixed(2).replace(/\.?0+$/, '') || input.value);
    });
});

// Email toggle
setEmailNotif.addEventListener('change', () => {
    document.getElementById('email-settings').classList.toggle('hidden', !setEmailNotif.checked);
});

// Load settings from server
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
    } catch (e) { /* settings not available yet */ }
}

// Save settings
document.getElementById('save-settings-btn').addEventListener('click', async () => {
    const settings = {
        confidence_threshold: setConfidence.value,
        velocity_threshold: setVelocity.value,
        cooldown_seconds: setCooldown.value,
        prone_confirmation_frames: setProne.value,
        notification_sound: setSound.checked.toString(),
        notification_browser: setBrowserNotif.checked.toString(),
        notification_email: setEmailNotif.checked.toString(),
        email_recipient: document.getElementById('set-email').value,
        email_smtp_host: document.getElementById('set-smtp-host').value,
    };
    try {
        await fetch(`${API_URL}/api/settings`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });
        showToast('Settings saved successfully', 'success');
    } catch (e) { showToast('Failed to save settings', 'error'); }
});

// ═══ BROWSER NOTIFICATION PERMISSION ═══
setBrowserNotif.addEventListener('change', () => {
    if (setBrowserNotif.checked && Notification.permission !== 'granted') {
        Notification.requestPermission().then(perm => {
            if (perm !== 'granted') {
                setBrowserNotif.checked = false;
                showToast('Browser notification permission denied', 'warning');
            }
        });
    }
});

// ═══ KEYBOARD SHORTCUTS ═══
document.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    if (e.key === 'm' || e.key === 'M') startBtn.click();
    if (e.key === '1') document.getElementById('tab-live').click();
    if (e.key === '2') document.getElementById('tab-stats').click();
    if (e.key === '3') document.getElementById('tab-history').click();
    if (e.key === '4') document.getElementById('tab-settings').click();
});

// ═══ INIT ═══
(async function init() {
    await enumerateCameras();
    fetchStatsQuiet();
    loadSettings();
})();
