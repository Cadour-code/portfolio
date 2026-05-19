const PALETTE = {
  primary:  '#1d504c',
  primaryLight: '#2a6b65',
  yellow:   '#f0b800',
  cream:    '#e8dcc0',
  red:      '#c94a3e',
  success:  '#4a9d5f',
  border:   '#e0ddd5',
};

function makeRadarChart(canvasId, labels, data, label) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  return new Chart(ctx, {
    type: 'radar',
    data: {
      labels: labels,
      datasets: [{
        label: label || 'Úroveň',
        data: data,
        backgroundColor: 'rgba(29,80,76,0.15)',
        borderColor: PALETTE.primary,
        borderWidth: 2,
        pointBackgroundColor: PALETTE.yellow,
        pointBorderColor: PALETTE.primary,
        pointRadius: 5,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      scales: {
        r: {
          beginAtZero: true,
          max: 100,
          ticks: { stepSize: 20, font: { size: 11 }, color: '#6b6b6b' },
          grid:  { color: PALETTE.border },
          angleLines: { color: PALETTE.border },
          pointLabels: { font: { size: 12, weight: '500' }, color: '#1a1a1a' },
        }
      },
      plugins: {
        legend: { display: false },
      }
    }
  });
}

function makeLineChart(canvasId, labels, data, skillName) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  return new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: skillName || 'Úroveň',
        data: data,
        borderColor: PALETTE.yellow,
        backgroundColor: 'rgba(240,184,0,0.12)',
        borderWidth: 2.5,
        tension: 0.4,
        fill: true,
        pointBackgroundColor: PALETTE.primary,
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 5,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          ticks: { stepSize: 20, color: '#6b6b6b' },
          grid:  { color: PALETTE.border },
        },
        x: {
          ticks: { color: '#6b6b6b', maxRotation: 45 },
          grid:  { display: false },
        }
      },
      plugins: {
        legend: {
          labels: { color: '#1a1a1a', font: { size: 12 } }
        }
      }
    }
  });
}
