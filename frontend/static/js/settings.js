/**
 * settings.js - Settings page interactions.
 */
(function () {
  'use strict';

  function el(id) { return document.getElementById(id); }

  function showToast(msg, type) {
    type = type || 'success';
    var c = el('toast-container');
    if (!c) return;
    var t = document.createElement('div');
    t.className = 'toast ' + (type === 'success' ? 'toast-success' : 'toast-error');
    t.textContent = msg;
    c.appendChild(t);
    setTimeout(function () {
      t.style.animation = 'fade-out .3s ease forwards';
      setTimeout(function () { if (t.parentNode) t.parentNode.removeChild(t); }, 300);
    }, 3500);
  }

  var sensitivitySlider = el('detection_sensitivity');
  var sensitivityVal = el('sensitivity-val');
  if (sensitivitySlider && sensitivityVal) {
    sensitivitySlider.addEventListener('input', function () {
      sensitivityVal.textContent = 'Current: ' + sensitivitySlider.value + '%';
    });
  }

  var eyeClosureSlider = el('eye_closure_threshold');
  var eyeClosureHint = el('eye-closure-hint');
  if (eyeClosureSlider && eyeClosureHint) {
    eyeClosureSlider.addEventListener('input', function () {
      var v = parseInt(eyeClosureSlider.value, 10);
      eyeClosureHint.textContent = 'Alert when eyes are closed for ' + v + ' second' + (v === 1 ? '' : 's');
    });
  }

  var volumeSlider = el('alert_volume');
  var volumeVal = el('volume-val');
  if (volumeSlider && volumeVal) {
    volumeSlider.addEventListener('input', function () {
      volumeVal.textContent = volumeSlider.value + '%';
    });
  }

  var alertDelaySlider = el('alert_delay');
  var alertDelayHint = el('alert-delay-hint');
  if (alertDelaySlider && alertDelayHint) {
    alertDelaySlider.addEventListener('input', function () {
      var v = parseInt(alertDelaySlider.value, 10);
      alertDelayHint.textContent = v === 0
        ? 'No delay - alert immediately after detection'
        : 'Delay alerts by ' + v + ' second' + (v === 1 ? '' : 's') + ' after detection';
    });
  }

  function collectSettings() {
    var form = el('settings-form');
    if (!form) return null;
    var data = {};

    ['detection_sensitivity', 'eye_closure_threshold', 'alert_volume', 'alert_delay'].forEach(function (name) {
      var input = form.querySelector('[name="' + name + '"]');
      if (input) data[name] = parseInt(input.value, 10);
    });

    [
      'blink_rate_monitoring', 'head_pose_tracking', 'yawn_detection',
      'audio_alerts', 'voice_warnings', 'visual_alerts', 'vibration_alerts',
      'night_vision', 'auto_exposure',
      'emergency_contacts', 'data_logging', 'privacy_mode', 'share_anonymous_data'
    ].forEach(function (name) {
      var input = form.querySelector('[name="' + name + '"]');
      if (input) data[name] = input.checked;
    });

    ['camera_resolution', 'frame_rate', 'face_detection_mode', 'emergency_contact_phone', 'alert_email_recipient'].forEach(function (name) {
      var input = form.querySelector('[name="' + name + '"]');
      if (input) data[name] = input.value.trim();
    });

    return data;
  }

  var saveBtn = el('save-settings-btn');
  if (saveBtn) {
    saveBtn.addEventListener('click', function () {
      var data = collectSettings();
      if (!data) {
        showToast('Could not read settings form.', 'error');
        return;
      }
      if (data.alert_email_recipient && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.alert_email_recipient)) {
        showToast('Enter a valid alert email address.', 'error');
        return;
      }

      saveBtn.disabled = true;
      saveBtn.textContent = 'Saving...';

      fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify(data)
      })
        .then(function (res) {
          if (res.ok) {
            showToast('Settings saved successfully!', 'success');
          } else if (res.status === 401) {
            showToast('Session expired - please log in again.', 'error');
            setTimeout(function () { window.location.href = '/login'; }, 1500);
          } else {
            showToast('Server error - settings not saved.', 'error');
          }
        })
        .catch(function () {
          showToast('Network error - settings not saved.', 'error');
        })
        .finally(function () {
          saveBtn.disabled = false;
          saveBtn.textContent = 'Save Settings';
        });
    });
  }

  var DEFAULTS = {
    detection_sensitivity: 75,
    eye_closure_threshold: 3,
    blink_rate_monitoring: true,
    head_pose_tracking: true,
    yawn_detection: true,
    audio_alerts: true,
    voice_warnings: true,
    visual_alerts: true,
    vibration_alerts: false,
    alert_volume: 70,
    alert_delay: 2,
    camera_resolution: '1920x1080',
    frame_rate: '30',
    face_detection_mode: 'High Performance',
    night_vision: true,
    auto_exposure: true,
    emergency_contacts: true,
    data_logging: true,
    privacy_mode: false,
    share_anonymous_data: true,
    emergency_contact_phone: '',
    alert_email_recipient: ''
  };

  var resetBtn = el('reset-defaults-btn');
  if (resetBtn) {
    resetBtn.addEventListener('click', function () {
      var form = el('settings-form');
      if (!form) return;

      Object.keys(DEFAULTS).forEach(function (name) {
        var val = DEFAULTS[name];
        var input = form.querySelector('[name="' + name + '"]');
        if (!input) return;
        if (typeof val === 'boolean') {
          input.checked = val;
        } else {
          input.value = String(val);
          input.dispatchEvent(new Event('input'));
        }
      });

      showToast('Settings reset to defaults.', 'success');
    });
  }
})();
