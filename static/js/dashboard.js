// static/js/dashboard.js
// Dashboard Common Functions

// Dashboard Initialization
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    loadDashboardStats();
    setupDashboardEvents();
});

// Initialize Dashboard
function initializeDashboard() {
    // Set active nav item based on current URL
    const currentPath = window.location.pathname;
    document.querySelectorAll('.list-group-item').forEach(item => {
        const href = item.getAttribute('href');
        if (href && currentPath.includes(href)) {
            item.classList.add('active');
        }
    });
    
    // Initialize charts if they exist
    if (document.getElementById('viewsChart')) {
        initViewsChart();
    }
    
    if (document.getElementById('earningsChart')) {
        initEarningsChart();
    }
}

// Load Dashboard Statistics
async function loadDashboardStats() {
    const statsContainer = document.getElementById('dashboardStats');
    if (!statsContainer) return;
    
    try {
        const response = await fetch('/api/dashboard/stats');
        const data = await response.json();
        
        if (data.success) {
            updateStatsUI(data.stats);
        }
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
    }
}

// Update Statistics UI
function updateStatsUI(stats) {
    for (const [key, value] of Object.entries(stats)) {
        const element = document.getElementById(`stat-${key}`);
        if (element) {
            element.textContent = value;
        }
    }
}

// Setup Dashboard Events
function setupDashboardEvents() {
    // Refresh button
    const refreshBtn = document.getElementById('refreshStats');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            loadDashboardStats();
            showToast('Statistics refreshed', 'success');
        });
    }
    
    // Date range picker
    const dateRange = document.getElementById('dateRange');
    if (dateRange) {
        dateRange.addEventListener('change', function() {
            loadChartData(this.value);
        });
    }
}

// Initialize Views Chart
function initViewsChart() {
    const ctx = document.getElementById('viewsChart').getContext('2d');
    window.viewsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Property Views',
                data: [],
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Views: ${context.raw.toLocaleString()}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

// Initialize Earnings Chart
function initEarningsChart() {
    const ctx = document.getElementById('earningsChart').getContext('2d');
    window.earningsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Earnings (KES)',
                data: [],
                backgroundColor: '#28a745',
                borderColor: '#1e7e34',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `KES ${context.raw.toLocaleString()}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return 'KES ' + value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

// Load Chart Data
async function loadChartData(range = 'month') {
    showLoader();
    
    try {
        const response = await fetch(`/api/chart-data?range=${range}`);
        const data = await response.json();
        
        if (data.success) {
            if (window.viewsChart) {
                window.viewsChart.data.labels = data.labels;
                window.viewsChart.data.datasets[0].data = data.views;
                window.viewsChart.update();
            }
            
            if (window.earningsChart) {
                window.earningsChart.data.labels = data.labels;
                window.earningsChart.data.datasets[0].data = data.earnings;
                window.earningsChart.update();
            }
        }
    } catch (error) {
        console.error('Error loading chart data:', error);
        showToast('Error loading chart data', 'error');
    } finally {
        hideLoader();
    }
}

// Export Data
async function exportData(format = 'csv') {
    showLoader();
    
    try {
        const response = await fetch(`/api/export-data?format=${format}`);
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `dashboard-data.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        showToast('Data exported successfully', 'success');
    } catch (error) {
        console.error('Error exporting data:', error);
        showToast('Error exporting data', 'error');
    } finally {
        hideLoader();
    }
}

// Print Dashboard
function printDashboard() {
    window.print();
}

// Auto-refresh Dashboard (every 30 seconds)
let autoRefreshInterval = null;

function startAutoRefresh(interval = 30000) {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
    
    autoRefreshInterval = setInterval(() => {
        if (!document.hidden) {
            loadDashboardStats();
        }
    }, interval);
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}

// Initialize auto-refresh if on dashboard
if (window.location.pathname.includes('/dashboard')) {
    startAutoRefresh();
    
    // Stop auto-refresh when page is hidden
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            stopAutoRefresh();
        } else {
            startAutoRefresh();
            loadDashboardStats();
        }
    });
}

// Export dashboard functions
window.dashboard = {
    loadDashboardStats,
    exportData,
    printDashboard,
    startAutoRefresh,
    stopAutoRefresh
};