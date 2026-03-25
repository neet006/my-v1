/**
 * dashboard.js - Real webcam monitor controls for the Flask dashboard.
 */
(function () {
  'use strict';

  function el(id) { return document.getElementById(id); }

  var drowsinessPctEl = el('drowsiness-pct');
  var drowsinessBarEl = el('drowsiness-fill');
  var eyeStatusEl = el('eye-status-val');
  var blinkRateEl = el('blink-rate-val');
  var sessionTimeEl = el('session-time-val');
  var statusBadgeEl = el('current-status-badge');
  var alertsListEl = el('alerts-list');
  var eyeTrackTextEl = el('eye-tracking-text');
  var faceStatusTextEl = el('face-status-text');
  var liveIndicatorEl = el('live-indicator');
  var startDriveBtn = el('start-drive-btn');
  var stopDriveBtn = el('stop-drive-btn');
  var cameraStreamEl = el('camera-stream');
  var toastContainer = el('toast-container');
  var pollHandle = null;
  var lastErrorMessage = '';

  function showToast(msg, type) {
    var tone = type === 'success' ? 'success' : 'error';
    if (!toastContainer) return;
    var t = document.createElement('div');
    t.className = 'toast toast-' + tone;
    t.textContent = msg;
    toastContainer.appendChild(t);
    setTimeout(function () {
      t.style.animation = 'fade-out .3s ease forwards';
      setTimeout(function () {
        if (t.parentNode) t.parentNode.removeChild(t);
      }, 300);
    }, 3200);
  }

  function updateBadge(status) {
    var label = status || 'IDLE';
    var badgeClass = 'badge-dark';
    if (label === 'SAFE' || label === 'ALERT') badgeClass = 'badge-ok';
    if (label === 'WARNING' || label === 'DROWSY') badgeClass = 'badge-warning';
    if (label === 'HIGH RISK' || label === 'CRITICAL') badgeClass = 'badge-alert';
    if (statusBadgeEl) {
      statusBadgeEl.textContent = label;
      statusBadgeEl.className = 'badge ' + badgeClass;
    }
  }

  function renderAlerts(alerts) {
    if (!alertsListEl) return;
    alertsListEl.innerHTML = '';
    if (!alerts || !alerts.length) {
      alertsListEl.textContent = 'No alerts in this drive';
      return;
    }
    alerts.forEach(function (item) {
      var div = document.createElement('div');
      div.style.cssText = 'font-size:12px;padding:5px 0;border-bottom:1px solid var(--border);color:var(--text-secondary)';
      div.textContent = item;
      alertsListEl.appendChild(div);
    });
  }

  function renderStatus(data) {
    if (drowsinessPctEl) drowsinessPctEl.textContent = (data.drowsiness || 0) + '%';
    if (drowsinessBarEl) drowsinessBarEl.style.width = (data.drowsiness || 0) + '%';
    if (eyeStatusEl) {
      eyeStatusEl.textContent = data.eye_status || 'Waiting';
      eyeStatusEl.style.color = data.eye_status === 'Closed' ? 'var(--accent-red)' : (data.eye_status === 'Open' ? 'var(--accent-green)' : 'var(--text-secondary)');
    }
    if (blinkRateEl) blinkRateEl.textContent = (data.blink_rate || 0) + ' bpm';
    if (sessionTimeEl) sessionTimeEl.textContent = data.session_time || '00:00:00';
    if (eyeTrackTextEl) eyeTrackTextEl.textContent = 'Eye Tracking: ' + (data.eye_status || 'Waiting');
    if (faceStatusTextEl) faceStatusTextEl.textContent = data.face_detected ? 'Face Detection: Active' : 'Face Detection: No face';
    if (liveIndicatorEl) liveIndicatorEl.textContent = data.running ? 'LIVE' : 'IDLE';
    if (startDriveBtn) startDriveBtn.disabled = !!data.running;
    if (stopDriveBtn) stopDriveBtn.disabled = !data.running;
    updateBadge(data.running ? data.status : 'IDLE');
    renderAlerts(data.recent_alerts || []);

    if (cameraStreamEl) {
      cameraStreamEl.style.opacity = data.running ? '1' : '0.25';
    }
    if (data.error && data.error !== lastErrorMessage) {
      lastErrorMessage = data.error;
      showToast(data.error, 'error');
    }
    if (!data.error) {
      lastErrorMessage = '';
    }
  }

  function pollStatus() {
    fetch('/api/monitor/status', {
      credentials: 'same-origin'
    })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        renderStatus(data);
      })
      .catch(function () {
        showToast('Could not read monitor status.', 'error');
        stopPolling();
      });
  }

  function startPolling() {
    stopPolling();
    pollStatus();
    pollHandle = setInterval(pollStatus, 1000);
  }

  function stopPolling() {
    if (pollHandle) {
      clearInterval(pollHandle);
      pollHandle = null;
    }
  }

  function startDrive() {
    if (startDriveBtn) startDriveBtn.disabled = true;
    fetch('/api/monitor/start', {
      method: 'POST',
      credentials: 'same-origin'
    })
      .then(function (res) { return res.json().then(function (data) { return { ok: res.ok, data: data }; }); })
      .then(function (result) {
        if (!result.ok || !result.data.ok) {
          throw new Error(result.data.error || 'Could not start camera monitor.');
        }
        startPolling();
        showToast('Camera monitoring started.', 'success');
      })
      .catch(function (err) {
        if (startDriveBtn) startDriveBtn.disabled = false;
        showToast(err.message || 'Could not start drive.', 'error');
      });
  }

  function stopDrive() {
    if (stopDriveBtn) stopDriveBtn.disabled = true;
    fetch('/api/monitor/stop', {
      method: 'POST',
      credentials: 'same-origin'
    })
      .then(function (res) { return res.json().then(function (data) { return { ok: res.ok, data: data }; }); })
      .then(function (result) {
        if (!result.ok || !result.data.ok) {
          throw new Error('Could not stop camera monitor.');
        }
        renderStatus({
          running: false,
          drowsiness: 0,
          eye_status: 'Waiting',
          blink_rate: 0,
          session_time: '00:00:00',
          status: 'IDLE',
          face_detected: false,
          recent_alerts: [],
        });
        startPolling();
        showToast('Drive stopped and statistics saved.', 'success');
      })
      .catch(function () {
        showToast('Could not stop drive.', 'error');
      });
  }

  if (startDriveBtn) startDriveBtn.addEventListener('click', startDrive);
  if (stopDriveBtn) stopDriveBtn.addEventListener('click', stopDrive);

  startPolling();
})();
