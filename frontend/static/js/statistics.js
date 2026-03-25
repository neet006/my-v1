/**
 * statistics.js - Build charts from saved session data.
 */
(function () {
  'use strict';

  function parseSessions() {
    var node = document.getElementById('sessions-data');
    if (!node) return [];
    try {
      return JSON.parse(node.textContent || '[]');
    } catch (_err) {
      return [];
    }
  }

  function parseDurationHours(duration) {
    var text = String(duration || '');
    var hourMatch = text.match(/(\d+)\s*h/i);
    var minuteMatch = text.match(/(\d+)\s*m/i);
    var hours = hourMatch ? parseInt(hourMatch[1], 10) : 0;
    var minutes = minuteMatch ? parseInt(minuteMatch[1], 10) : 0;
    return hours + (minutes / 60);
  }

  function parsePercent(value) {
    var match = String(value || '').match(/(\d+)/);
    return match ? parseInt(match[1], 10) : 0;
  }

  function chartCtx(id) {
    return document.getElementById(id);
  }

  var sessions = parseSessions();
  var normalized = sessions.map(function (session, index) {
    var maxDrowsiness = parsePercent(session.max_drowsiness);
    var alerts = Number(session.alerts || 0);
    var drowsyEvents = Number(session.drowsy_events != null ? session.drowsy_events : alerts);
    var sleepEvents = Number(session.sleep_events != null ? session.sleep_events : (maxDrowsiness >= 80 ? 1 : 0));

    return {
      label: 'S' + (sessions.length - index),
      date: session.date || '',
      durationHours: parseDurationHours(session.duration),
      alerts: alerts,
      drowsyEvents: drowsyEvents,
      sleepEvents: sleepEvents,
      maxDrowsiness: maxDrowsiness
    };
  }).reverse();

  var totalHours = normalized.reduce(function (sum, session) { return sum + session.durationHours; }, 0);
  var totalAlerts = normalized.reduce(function (sum, session) { return sum + session.drowsyEvents; }, 0);
  var totalSleepEvents = normalized.reduce(function (sum, session) { return sum + session.sleepEvents; }, 0);
  var avgDrowsiness = normalized.length
    ? normalized.reduce(function (sum, session) { return sum + session.maxDrowsiness; }, 0) / normalized.length
    : 0;

  var totalTimeEl = document.getElementById('stat-total-time');
  var totalAlertsEl = document.getElementById('stat-total-alerts');
  var sleepEventsEl = document.getElementById('stat-sleep-events');
  var avgDrowsinessEl = document.getElementById('stat-avg-drowsiness');

  if (totalTimeEl) totalTimeEl.textContent = totalHours.toFixed(1);
  if (totalAlertsEl) totalAlertsEl.textContent = String(totalAlerts);
  if (sleepEventsEl) sleepEventsEl.textContent = String(totalSleepEvents);
  if (avgDrowsinessEl) avgDrowsinessEl.textContent = Math.round(avgDrowsiness) + '%';

  if (!window.Chart) return;

  Chart.defaults.color = '#8b90a8';
  Chart.defaults.borderColor = 'rgba(255,255,255,.06)';
  Chart.defaults.font.family = "'Inter', sans-serif";
  Chart.defaults.font.size = 11;

  var labels = normalized.map(function (session) { return session.label; });

  new Chart(chartCtx('weeklyAlertsChart'), {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Dizzy Alerts',
        data: normalized.map(function (session) { return session.drowsyEvents; }),
        backgroundColor: '#e8394b',
        borderRadius: 4,
        borderSkipped: false
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false } },
        y: { beginAtZero: true, ticks: { stepSize: 1 } }
      }
    }
  });

  new Chart(chartCtx('drowsinessByTimeChart'), {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Max Drowsiness (%)',
        data: normalized.map(function (session) { return session.maxDrowsiness; }),
        borderColor: '#ff9500',
        backgroundColor: 'rgba(255,149,0,.08)',
        tension: 0.35,
        fill: true,
        pointBackgroundColor: '#ff9500',
        pointRadius: 4,
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false } },
        y: { beginAtZero: true, max: 100 }
      }
    }
  });

  new Chart(chartCtx('alertTypesChart'), {
    type: 'pie',
    data: {
      labels: ['Drowsy Alerts', 'Sleep Risk Events'],
      datasets: [{
        data: [totalAlerts, totalSleepEvents],
        backgroundColor: ['#4d7cfe', '#e8394b'],
        borderColor: '#13151c',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right',
          labels: { boxWidth: 12, padding: 12, font: { size: 11 } }
        }
      }
    }
  });

  new Chart(chartCtx('drivingVsDrowsinessChart'), {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Driving (hrs)',
          data: normalized.map(function (session) { return Number(session.durationHours.toFixed(2)); }),
          backgroundColor: '#4d7cfe',
          borderRadius: 3,
          yAxisID: 'y'
        },
        {
          label: 'Max Drowsiness (%)',
          data: normalized.map(function (session) { return session.maxDrowsiness; }),
          backgroundColor: '#00d68f',
          borderRadius: 3,
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top', labels: { boxWidth: 10, padding: 10 } }
      },
      scales: {
        x: { grid: { display: false } },
        y: { beginAtZero: true, position: 'left' },
        y1: { beginAtZero: true, position: 'right', grid: { drawOnChartArea: false }, max: 100 }
      }
    }
  });
})();
