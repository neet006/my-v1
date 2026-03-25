/**
 * statistics.js — Chart.js charts for A.M.A.T.S. Statistics page.
 */
(function () {
  'use strict';

  const DARK_BG   = '#13151c';
  const GRID_CLR  = 'rgba(255,255,255,.06)';
  const TEXT_CLR  = '#8b90a8';
  const DAYS      = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];

  Chart.defaults.color       = TEXT_CLR;
  Chart.defaults.borderColor = GRID_CLR;
  Chart.defaults.font.family = "'Inter', sans-serif";
  Chart.defaults.font.size   = 11;

  function ctx(id) {
    return document.getElementById(id);
  }

  // 1 ── Weekly Alert Summary (Bar)
  new Chart(ctx('weeklyAlertsChart'), {
    type: 'bar',
    data: {
      labels: DAYS,
      datasets: [{
        data: [2, 1, 4, 0, 3, 1, 2],
        backgroundColor: '#e8394b',
        borderRadius: 4,
        borderSkipped: false,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false } },
        y: { beginAtZero: true, ticks: { stepSize: 1 } }
      }
    }
  });

  // 2 ── Drowsiness by Time of Day (Line)
  new Chart(ctx('drowsinessByTimeChart'), {
    type: 'line',
    data: {
      labels: ['6AM','8AM','10AM','12PM','2PM','4PM','6PM','8PM','10PM'],
      datasets: [{
        data: [45, 15, 22, 32, 18, 28, 35, 40, 55],
        borderColor: '#ff9500',
        backgroundColor: 'rgba(255,149,0,.08)',
        tension: 0.4,
        fill: true,
        pointBackgroundColor: '#ff9500',
        pointRadius: 4,
        borderWidth: 2,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false } },
        y: { beginAtZero: true, max: 70 }
      }
    }
  });

  // 3 ── Alert Types Distribution (Pie)
  new Chart(ctx('alertTypesChart'), {
    type: 'pie',
    data: {
      labels: ['Eyes Closed 45%', 'Slow Blinks 30%', 'Head Nod 15%', 'Micro Sleep 10%'],
      datasets: [{
        data: [45, 30, 15, 10],
        backgroundColor: ['#e8394b','#ff9500','#7c5cfc','#4d7cfe'],
        borderColor: DARK_BG,
        borderWidth: 2,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right',
          labels: { boxWidth: 12, padding: 12, font: { size: 11 } }
        }
      }
    }
  });

  // 4 ── Weekly Driving Time vs Avg Drowsiness (Dual Bar)
  new Chart(ctx('drivingVsDrowsinessChart'), {
    type: 'bar',
    data: {
      labels: DAYS,
      datasets: [
        {
          label: 'Driving (hrs)',
          data: [6, 8, 12, 4, 3, 9, 7],
          backgroundColor: '#4d7cfe',
          borderRadius: 3,
          yAxisID: 'y',
        },
        {
          label: 'Avg Drowsiness (%)',
          data: [18, 24, 32, 12, 9, 27, 19],
          backgroundColor: '#00d68f',
          borderRadius: 3,
          yAxisID: 'y1',
        }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top', labels: { boxWidth: 10, padding: 10 } }
      },
      scales: {
        x: { grid: { display: false } },
        y:  { beginAtZero: true, position: 'left',  ticks: { stepSize: 3 }, max: 14 },
        y1: { beginAtZero: true, position: 'right', grid: { drawOnChartArea: false }, max: 40, ticks: { stepSize: 9 } }
      }
    }
  });
})();
