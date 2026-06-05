// static/js/admin.js
// Admin Dashboard Scripts

// Admin Dashboard Initialization
document.addEventListener('DOMContentLoaded', function() {
    initAdminDashboard();
    setupUserManagement();
    setupVerificationSystem();
    initReportsSystem();
});

// Initialize Admin Dashboard
function initAdminDashboard() {
    // Load platform stats
    loadPlatformStats();
    
    // Load recent activities
    loadRecentActivities();
    
    // Initialize admin charts
    if (document.getElementById('platformGrowthChart')) {
        initPlatformGrowthChart();
    }
}

// Load Platform Statistics
async function loadPlatformStats() {
    try {
        const response = await fetch('/api/admin/platform-stats');
        const data = await response.json();
        
        if (data.success) {
            updatePlatformStats(data.stats);
        }
    } catch (error) {
        console.error('Error loading platform stats:', error);
    }
}

// Update Platform Stats UI
function updatePlatformStats(stats) {
    const elements = {
        totalUsers: document.getElementById('totalUsers'),
        totalProperties: document.getElementById('totalProperties'),
        totalBookings: document.getElementById('totalBookings'),
        totalRevenue: document.getElementById('totalRevenue'),
        pendingVerifications: document.getElementById('pendingVerifications'),
        pendingReports: document.getElementById('pendingReports')
    };
    
    for (const [key, element] of Object.entries(elements)) {
        if (element && stats[key] !== undefined) {
            if (key === 'totalRevenue') {
                element.textContent = formatCurrency(stats[key]);
            } else {
                element.textContent = stats[key].toLocaleString();
            }
        }
    }
}

// Load Recent Activities
async function loadRecentActivities() {
    const container = document.getElementById('recentActivities');
    if (!container) return;
    
    try {
        const response = await fetch('/api/admin/recent-activities');
        const data = await response.json();
        
        if (data.success && data.activities.length > 0) {
            updateActivitiesUI(data.activities);
        } else {
            container.innerHTML = '<div class="text-center py-3">No recent activities</div>';
        }
    } catch (error) {
        console.error('Error loading activities:', error);
    }
}

// Update Activities UI
function updateActivitiesUI(activities) {
    const container = document.getElementById('recentActivities');
    if (!container) return;
    
    let html = '<div class="list-group">';
    activities.forEach(activity => {
        const icon = getActivityIcon(activity.type);
        html += `
            <div class="list-group-item">
                <div class="d-flex">
                    <div class="me-3">
                        <i class="${icon} fa-2x"></i>
                    </div>
                    <div class="flex-grow-1">
                        <p class="mb-1">${escapeHtml(activity.description)}</p>
                        <small class="text-muted">${formatRelativeTime(activity.created_at)}</small>
                    </div>
                </div>
            </div>
        `;
    });
    html += '</div>';
    
    container.innerHTML = html;
}

// Get Activity Icon
function getActivityIcon(type) {
    const icons = {
        'user': 'fas fa-user-circle text-primary',
        'property': 'fas fa-home text-success',
        'booking': 'fas fa-calendar-check text-warning',
        'verification': 'fas fa-check-double text-info',
        'report': 'fas fa-flag text-danger'
    };
    return icons[type] || 'fas fa-bell text-secondary';
}

// Initialize Platform Growth Chart
function initPlatformGrowthChart() {
    const ctx = document.getElementById('platformGrowthChart').getContext('2d');
    window.platformChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Users',
                    data: [],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Properties',
                    data: [],
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Revenue (KES)',
                    data: [],
                    borderColor: '#ffc107',
                    backgroundColor: 'rgba(255, 193, 7, 0.1)',
                    tension: 0.4,
                    fill: true,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Count'
                    }
                },
                y1: {
                    position: 'right',
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Revenue (KES)'
                    },
                    ticks: {
                        callback: function(value) {
                            return 'KES ' + value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
    
    loadPlatformGrowthData();
}

// Load Platform Growth Data
async function loadPlatformGrowthData() {
    try {
        const response = await fetch('/api/admin/growth-data');
        const data = await response.json();
        
        if (data.success && window.platformChart) {
            window.platformChart.data.labels = data.labels;
            window.platformChart.data.datasets[0].data = data.users;
            window.platformChart.data.datasets[1].data = data.properties;
            window.platformChart.data.datasets[2].data = data.revenue;
            window.platformChart.update();
        }
    } catch (error) {
        console.error('Error loading growth data:', error);
    }
}

// Setup User Management
function setupUserManagement() {
    // User search
    const userSearch = document.getElementById('userSearch');
    if (userSearch) {
        userSearch.addEventListener('input', debounce(searchUsers, 500));
    }
    
    // Role filter
    const roleFilter = document.getElementById('roleFilter');
    if (roleFilter) {
        roleFilter.addEventListener('change', filterUsers);
    }
    
    // Status filter
    const statusFilter = document.getElementById('statusFilter');
    if (statusFilter) {
        statusFilter.addEventListener('change', filterUsers);
    }
}

// Search Users
async function searchUsers() {
    const query = document.getElementById('userSearch').value;
    if (query.length < 2) return;
    
    showLoader();
    
    try {
        const response = await fetch(`/api/admin/users/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        if (data.success) {
            updateUsersTable(data.users);
        }
    } catch (error) {
        console.error('Error searching users:', error);
    } finally {
        hideLoader();
    }
}

// Filter Users
function filterUsers() {
    const role = document.getElementById('roleFilter').value;
    const status = document.getElementById('statusFilter').value;
    
    const rows = document.querySelectorAll('#usersTable tbody tr');
    rows.forEach(row => {
        const userRole = row.dataset.role;
        const userStatus = row.dataset.status;
        
        let show = true;
        if (role && role !== 'all' && userRole !== role) show = false;
        if (status && status !== 'all' && userStatus !== status) show = false;
        
        row.style.display = show ? '' : 'none';
    });
}

// Update Users Table
function updateUsersTable(users) {
    const tbody = document.querySelector('#usersTable tbody');
    if (!tbody) return;
    
    let html = '';
    users.forEach(user => {
        html += `
            <tr data-role="${user.user_type}" data-status="${user.is_active ? 'active' : 'inactive'}">
                <td>${user.id}</td>
                <td>
                    <div class="d-flex align-items-center">
                        <img src="${user.profile_photo || '/static/images/default-avatar.png'}" 
                             class="user-avatar me-2" width="30" height="30">
                        ${escapeHtml(user.full_name)}
                    </div>
                </td>
                <td>${escapeHtml(user.email)}</td>
                <td>${user.phone}</td>
                <td><span class="badge bg-${getUserTypeColor(user.user_type)}">${user.user_type}</span></td>
                <td>
                    <span class="user-status ${user.is_active ? 'active' : 'inactive'}"></span>
                    ${user.is_active ? 'Active' : 'Inactive'}
                </td>
                <td>${formatDate(user.created_at)}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-info" onclick="viewUser(${user.id})">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-warning" onclick="editUser(${user.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-danger" onclick="toggleUserStatus(${user.id})">
                            <i class="fas fa-${user.is_active ? 'ban' : 'check'}"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    });
    
    tbody.innerHTML = html;
}

// Get User Type Color
function getUserTypeColor(type) {
    const colors = {
        'admin': 'danger',
        'landlord': 'success',
        'student': 'info'
    };
    return colors[type] || 'secondary';
}

// Setup Verification System
function setupVerificationSystem() {
    // Auto-refresh verification list
    if (document.getElementById('verificationList')) {
        setInterval(loadPendingVerifications, 30000);
    }
}

// Load Pending Verifications
async function loadPendingVerifications() {
    const container = document.getElementById('verificationList');
    if (!container) return;
    
    try {
        const response = await fetch('/api/admin/pending-verifications');
        const data = await response.json();
        
        if (data.success && data.verifications.length > 0) {
            updateVerificationList(data.verifications);
        }
    } catch (error) {
        console.error('Error loading verifications:', error);
    }
}

// Update Verification List
function updateVerificationList(verifications) {
    const container = document.getElementById('verificationList');
    if (!container) return;
    
    let html = '<div class="row">';
    verifications.forEach(verification => {
        html += `
            <div class="col-md-6 mb-3">
                <div class="card verification-card">
                    <div class="card-body">
                        <h6>${escapeHtml(verification.full_name)}</h6>
                        <p class="small text-muted mb-2">
                            <i class="fas fa-envelope"></i> ${verification.email}<br>
                            <i class="fas fa-phone"></i> ${verification.phone}
                        </p>
                        <hr>
                        <div class="d-flex gap-2">
                            <button class="btn btn-sm btn-success" onclick="verifyLandlord(${verification.id})">
                                <i class="fas fa-check"></i> Verify
                            </button>
                            <button class="btn btn-sm btn-danger" onclick="rejectLandlord(${verification.id})">
                                <i class="fas fa-times"></i> Reject
                            </button>
                            <button class="btn btn-sm btn-info" onclick="viewDocuments(${verification.id})">
                                <i class="fas fa-file-alt"></i> Documents
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    html += '</div>';
    
    container.innerHTML = html;
}

// Verify Landlord
async function verifyLandlord(landlordId) {
    const result = await showConfirm('Verify Landlord', 'Are you sure you want to verify this landlord?');
    if (!result.isConfirmed) return;
    
    showLoader();
    
    try {
        const response = await fetch(`/api/admin/verify-landlord/${landlordId}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Landlord verified successfully', 'success');
            loadPendingVerifications();
            loadPlatformStats();
        } else {
            showToast(data.message || 'Error verifying landlord', 'error');
        }
    } catch (error) {
        console.error('Error verifying landlord:', error);
        showToast('An error occurred', 'error');
    } finally {
        hideLoader();
    }
}

// Reject Landlord
async function rejectLandlord(landlordId) {
    const result = await showConfirm('Reject Landlord', 'Are you sure you want to reject this landlord?');
    if (!result.isConfirmed) return;
    
    showLoader();
    
    try {
        const response = await fetch(`/api/admin/reject-landlord/${landlordId}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Landlord rejected', 'info');
            loadPendingVerifications();
        } else {
            showToast(data.message || 'Error rejecting landlord', 'error');
        }
    } catch (error) {
        console.error('Error rejecting landlord:', error);
        showToast('An error occurred', 'error');
    } finally {
        hideLoader();
    }
}

// Initialize Reports System
function initReportsSystem() {
    if (document.getElementById('reportsTable')) {
        loadReports();
    }
}

// Load Reports
async function loadReports() {
    try {
        const response = await fetch('/api/admin/reports');
        const data = await response.json();
        
        if (data.success) {
            updateReportsTable(data.reports);
        }
    } catch (error) {
        console.error('Error loading reports:', error);
    }
}

// Update Reports Table
function updateReportsTable(reports) {
    const tbody = document.querySelector('#reportsTable tbody');
    if (!tbody) return;
    
    let html = '';
    reports.forEach(report => {
        html += `
            <tr>
                <td>#${report.id}</td>
                <td>${escapeHtml(report.reporter_name)}</td>
                <td><span class="badge bg-danger">${report.report_type}</span></td>
                <td>${report.target_type}: #${report.target_id}</td>
                <td>${report.description.substring(0, 100)}...</td>
                <td>
                    <span class="badge bg-${getReportStatusColor(report.status)}">
                        ${report.status}
                    </span>
                </td>
                <td>${formatDate(report.created_at)}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-info" onclick="viewReport(${report.id})">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-success" onclick="resolveReport(${report.id})">
                            <i class="fas fa-check"></i>
                        </button>
                        <button class="btn btn-danger" onclick="deleteReport(${report.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    });
    
    tbody.innerHTML = html;
}

// Get Report Status Color
function getReportStatusColor(status) {
    const colors = {
        'pending': 'warning',
        'investigating': 'info',
        'resolved': 'success',
        'dismissed': 'secondary'
    };
    return colors[status] || 'secondary';
}

// Resolve Report
async function resolveReport(reportId) {
    const result = await showConfirm('Resolve Report', 'Mark this report as resolved?');
    if (!result.isConfirmed) return;
    
    showLoader();
    
    try {
        const response = await fetch(`/api/admin/report/${reportId}/resolve`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Report marked as resolved', 'success');
            loadReports();
        } else {
            showToast('Error resolving report', 'error');
        }
    } catch (error) {
        console.error('Error resolving report:', error);
        showToast('An error occurred', 'error');
    } finally {
        hideLoader();
    }
}

// Export admin functions
window.admin = {
    verifyLandlord,
    rejectLandlord,
    viewUser,
    editUser,
    toggleUserStatus,
    viewReport,
    resolveReport,
    loadPlatformStats,
    loadReports
};