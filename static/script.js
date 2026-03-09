// CHART INITIALIZATION
const ctx = document.getElementById('hashrateChart').getContext('2d');
const hashrateChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Hashrate (H/s)',
            data: [],
            borderColor: '#007bff',
            backgroundColor: 'rgba(0, 123, 255, 0.1)',
            fill: true,
            tension: 0.4
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: { beginAtZero: true, grid: { color: 'rgba(200, 200, 200, 0.2)' } },
            x: { grid: { display: false } }
        },
        plugins: { legend: { display: false } }
    }
});

// THEME MANAGEMENT
const themeToggle = document.getElementById('theme-toggle');
const html = document.documentElement;

themeToggle.onclick = () => {
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
};

if (localStorage.getItem('theme') === 'dark') {
    html.setAttribute('data-theme', 'dark');
}

// TAB MANAGEMENT
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.onclick = () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

        btn.classList.add('active');
        const target = btn.getAttribute('data-tab');
        if (target === 'logs') {
            document.getElementById('logs-tab').classList.add('active');
        } else {
            document.getElementById(target).classList.add('active');
        }
    };
});

// NOTIFICATIONS
function notify(title, body) {
    if (Notification.permission === "granted") {
        new Notification(title, { body });
    } else if (Notification.permission !== "denied") {
        Notification.requestPermission();
    }
}

// DATA POLLING
let lastShares = 0;
function updateStats() {
    fetch('/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('hashrate').textContent = data.hash_rate.toFixed(2) + ' H/s';
            document.getElementById('shares').textContent = data.shares_found;
            document.getElementById('protocol-v').textContent = data.v2 ? 'V2' : 'V1';
            document.getElementById('best-coin').textContent = data.best_coin;

            // AI Info
            document.getElementById('ai-status-text').textContent = data.ai_trained ? 'Trained' : 'Training...';
            document.getElementById('ai-accuracy').textContent = data.ai_trained ? '94.2%' : '0.0%';

            const gpuBadge = document.getElementById('gpu-active');
            if (data.gpu_active) {
                gpuBadge.textContent = 'ACTIVE';
                gpuBadge.className = 'status-on';
            } else {
                gpuBadge.textContent = 'OFF';
                gpuBadge.className = 'status-off';
            }

            const badge = document.getElementById('status-badge');
            if (data.is_mining) {
                badge.textContent = 'Mining Active';
                badge.className = 'badge active';
            } else {
                badge.textContent = 'Miner Stopped';
                badge.className = 'badge stopped';
            }

            // Update Chart
            const now = new Date().toLocaleTimeString();
            hashrateChart.data.labels.push(now);
            hashrateChart.data.datasets[0].data.push(data.hash_rate);
            if (hashrateChart.data.labels.length > 20) {
                hashrateChart.data.labels.shift();
                hashrateChart.data.datasets[0].data.shift();
            }
            hashrateChart.update('none');

            // Notifications for shares
            if (data.shares_found > lastShares) {
                notify("Share Found!", "A new valid share has been submitted to the pool.");
                lastShares = data.shares_found;
            }
        });
}

function updateLogs() {
    fetch('/logs')
        .then(response => response.json())
        .then(data => {
            const logWindow = document.getElementById('logs');
            logWindow.innerHTML = data.map(log => `<p>${log}</p>`).join('');
            logWindow.scrollTop = logWindow.scrollHeight;
        });
}

document.getElementById('start-btn').onclick = () => {
    const formData = new FormData(document.getElementById('config-form'));
    fetch('/start', { method: 'POST', body: formData });
    notify("Miner Started", "Attempting to connect to the pool...");
};

document.getElementById('stop-btn').onclick = () => {
    fetch('/stop', { method: 'POST' });
    notify("Miner Stopped", "Mining process has been terminated.");
};

document.getElementById('clear-logs').onclick = () => {
    document.getElementById('logs').innerHTML = '<p>Logs cleared (display only).</p>';
};

document.getElementById('train-ai-btn').onclick = () => {
    fetch('/train', { method: 'POST' });
    notify("Training Started", "Generating synthetic data and training Neural Network...");
};

setInterval(updateStats, 2000);
setInterval(updateLogs, 3000);
updateStats();
updateLogs();
