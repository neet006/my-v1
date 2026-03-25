/**
 * dashboard.js — Live Monitor simulation for A.M.A.T.S.
 * Simulates real-time drowsiness, blink rate, eye status, and session timer.
 * All element lookups are guarded so this file never throws if an element is missing.
 */
(function () {
  'use strict';

  // ── Safe element getter ────────────────────────────────────────
  function el(id) { return document.getElementById(id); }

  const drowsinessPctEl  = el('drowsiness-pct');
  const drowsinessBarEl  = el('drowsiness-fill');
  const eyeStatusEl      = el('eye-status-val');
  const blinkRateEl      = el('blink-rate-val');
  const sessionTimeEl    = el('session-time-val');
  const statusBadgeEl    = el('current-status-badge');
  const alertsListEl     = el('alerts-list');
  const eyeTrackTextEl   = el('eye-tracking-text');
  const toastContainer   = el('toast-container');

  // ── State ─────────────────────────────────────────────────────
  const sessionStart = Date.now();
  let drowsiness     = 5;      // 0-100
  let blinkRate      = 17;
  let alertCount     = 0;
  const recentAlerts = [];

  // ── Toast ─────────────────────────────────────────────────────
  function showToast(msg, type) {
    type = type || 'warning';
    if (!toastContainer) return;
    const t = document.createElement('div');
    t.className = 'toast toast-' + (type === 'success' ? 'success' : 'error');
    t.textContent = (type === 'success' ? '✅ ' : '⚠️ ') + msg;
    toastContainer.appendChild(t);
    setTimeout(function () {
      t.style.animation = 'fade-out .3s ease forwards';
      setTimeout(function () { if (t.parentNode) t.parentNode.removeChild(t); }, 300);
    }, 4000);
  }

  // ── Timer ─────────────────────────────────────────────────────
  function formatTime(ms) {
    var totalSec = Math.floor(ms / 1000);
    var h   = Math.floor(totalSec / 3600);
    var m   = Math.floor((totalSec % 3600) / 60);
    var s   = totalSec % 60;
    return (h < 10 ? '0' : '') + h + ':' +
           (m < 10 ? '0' : '') + m + ':' +
           (s < 10 ? '0' : '') + s;
  }

  function updateTimer() {
    if (sessionTimeEl) {
      sessionTimeEl.textContent = '🕐 ' + formatTime(Date.now() - sessionStart);
    }
  }

  // ── Status classification ─────────────────────────────────────
  function classifyStatus(pct) {
    if (pct < 30) return { label: 'ALERT',    badgeClass: 'badge-ok' };
    if (pct < 60) return { label: 'DROWSY',   badgeClass: 'badge-warning' };
    return             { label: 'CRITICAL', badgeClass: 'badge-alert' };
  }

  // ── Alert panel update ────────────────────────────────────────
  function pushAlert(msg) {
    var now = new Date();
    var t   = now.getHours() + ':' + String(now.getMinutes()).padStart(2, '0');
    recentAlerts.unshift(t + ' — ' + msg);
    if (recentAlerts.length > 5) recentAlerts.pop();

    if (alertsListEl) {
      alertsListEl.innerHTML = '';          // clear old content safely
      recentAlerts.forEach(function (a) {
        var div = document.createElement('div');
        div.style.cssText = 'font-size:12px;padding:5px 0;border-bottom:1px solid var(--border);color:var(--text-secondary)';
        div.textContent = a;
        alertsListEl.appendChild(div);
      });
    }
    showToast(msg, 'warning');
  }

  // ── Main simulation tick ───────────────────────────────────────
  function tick() {
    // Natural drift
    drowsiness += (Math.random() - 0.47) * 4;
    drowsiness  = Math.max(2, Math.min(98, drowsiness));
    blinkRate  += (Math.random() - 0.5) * 2;
    blinkRate   = Math.round(Math.max(10, Math.min(28, blinkRate)));

    var pct    = Math.round(drowsiness);
    var eyeOpen = drowsiness < 65 || Math.random() > 0.25;
    var status  = classifyStatus(pct);

    // Update drowsiness %
    if (drowsinessPctEl)  drowsinessPctEl.textContent = pct + '%';
    if (drowsinessBarEl)  drowsinessBarEl.style.width = pct + '%';

    // Update blink rate
    if (blinkRateEl) blinkRateEl.textContent = blinkRate + ' bpm';

    // Update eye status
    if (eyeStatusEl) {
      eyeStatusEl.textContent = eyeOpen ? '👁️ Open' : '😴 Closed';
      eyeStatusEl.style.color = eyeOpen ? 'var(--accent-green)' : 'var(--accent-red)';
    }
    if (eyeTrackTextEl) {
      eyeTrackTextEl.textContent = 'Eye Tracking: ' + (eyeOpen ? 'Open' : 'Closed');
    }

    // Update status badge
    if (statusBadgeEl) {
      statusBadgeEl.textContent = status.label;
      statusBadgeEl.className   = 'badge ' + status.badgeClass;
    }

    // Trigger alert at high drowsiness (random so it's not every tick)
    if (pct >= 60 && Math.random() > 0.92) {
      alertCount++;
      pushAlert('Drowsiness alert #' + alertCount + ' — Level: ' + pct + '%');
    } else if (!eyeOpen && Math.random() > 0.94) {
      pushAlert('Eyes closed detected — stay alert!');
    }
  }

  // ── Kick off ──────────────────────────────────────────────────
  updateTimer();
  tick();
  setInterval(updateTimer, 1000);
  setInterval(tick, 1800);

})();
