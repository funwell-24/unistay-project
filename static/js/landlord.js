// static/js/landlord.js
// Landlord Dashboard Scripts

// Landlord Dashboard Initialization
document.addEventListener('DOMContentLoaded', function() {
    initLandlordDashboard();
    setupPropertyForm();
    setupImageUpload();
    initAnalytics();
});

// Initialize Landlord Dashboard
function initLandlordDashboard() {
    // Load property stats
    loadPropertyStats();
    
    // Load recent bookings
    loadRecentBookings();
    
    // Load earnings data
    loadEarningsData();
}

// Load Property Statistics
async function loadPropertyStats() {
    try {
        const response = await fetch('/api/landlord/property-stats');
        const data = await response.json();
        
        if (data.success) {
            updatePropertyStatsUI(data.stats);
        }
    } catch (error) {
        console.error('Error loading property stats:', error);
    }
}

// Update Property Stats UI
function updatePropertyStatsUI(stats) {
    const elements = {
        totalProperties: document.getElementById('totalProperties'),
        availableUnits: document.getElementById('availableUnits'),
        pendingBookings: document.getElementById('pendingBookings'),
        monthlyViews: document.getElementById('monthlyViews'),
        totalEarnings: document.getElementById('totalEarnings'),
        conversionRate: document.getElementById('conversionRate')
    };
    
    for (const [key, element] of Object.entries(elements)) {
        if (element && stats[key] !== undefined) {
            if (key === 'totalEarnings') {
                element.textContent = formatCurrency(stats[key]);
            } else if (key === 'conversionRate') {
                element.textContent = `${stats[key]}%`;
            } else {
                element.textContent = stats[key].toLocaleString();
            }
        }
    }
}

// Load Recent Bookings
async function loadRecentBookings() {
    const container = document.getElementById('recentBookings');
    if (!container) return;
    
    try {
        const response = await fetch('/api/landlord/recent-bookings');
        const data = await response.json();
        
        if (data.success && data.bookings.length > 0) {
            updateBookingsUI(data.bookings);
        } else {
            container.innerHTML = '<div class="text-center py-3">No recent bookings</div>';
        }
    } catch (error) {
        console.error('Error loading bookings:', error);
    }
}

// Update Bookings UI
function updateBookingsUI(bookings) {
    const container = document.getElementById('recentBookings');
    if (!container) return;
    
    let html = '<div class="list-group">';
    bookings.forEach(booking => {
        html += `
            <div class="list-group-item">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="mb-1">${escapeHtml(booking.student_name)}</h6>
                        <p class="mb-1 small">${escapeHtml(booking.property_title)}</p>
                        <small>Move in: ${formatDate(booking.move_in_date)}</small>
                    </div>
                    <div>
                        <span class="badge bg-${getStatusColor(booking.status)}">${booking.status}</span>
                        <div class="btn-group btn-group-sm mt-2">
                            <button class="btn btn-success" onclick="approveBooking(${booking.id})">
                                <i class="fas fa-check"></i>
                            </button>
                            <button class="btn btn-danger" onclick="rejectBooking(${booking.id})">
                                <i class="fas fa-times"></i>
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

// Get Status Color
function getStatusColor(status) {
    const colors = {
        'pending': 'warning',
        'approved': 'success',
        'rejected': 'danger',
        'completed': 'info'
    };
    return colors[status] || 'secondary';
}

// Approve Booking
async function approveBooking(bookingId) {
    const result = await showConfirm('Approve Booking', 'Are you sure you want to approve this booking?');
    if (!result.isConfirmed) return;
    
    showLoader();
    
    try {
        const response = await fetch(`/api/landlord/booking/${bookingId}/approve`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Booking approved successfully!', 'success');
            loadRecentBookings();
            loadPropertyStats();
        } else {
            showToast(data.message || 'Error approving booking', 'error');
        }
    } catch (error) {
        console.error('Error approving booking:', error);
        showToast('An error occurred', 'error');
    } finally {
        hideLoader();
    }
}

// Reject Booking
async function rejectBooking(bookingId) {
    const result = await showConfirm('Reject Booking', 'Are you sure you want to reject this booking?');
    if (!result.isConfirmed) return;
    
    showLoader();
    
    try {
        const response = await fetch(`/api/landlord/booking/${bookingId}/reject`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Booking rejected', 'info');
            loadRecentBookings();
            loadPropertyStats();
        } else {
            showToast(data.message || 'Error rejecting booking', 'error');
        }
    } catch (error) {
        console.error('Error rejecting booking:', error);
        showToast('An error occurred', 'error');
    } finally {
        hideLoader();
    }
}

// Setup Property Form
function setupPropertyForm() {
    const form = document.getElementById('propertyForm');
    if (!form) return;
    
    form.addEventListener('submit', submitProperty);
    
    // Auto-calculate price display
    const priceInput = document.getElementById('monthlyRent');
    if (priceInput) {
        priceInput.addEventListener('input', function() {
            const display = document.getElementById('priceDisplay');
            if (display) {
                display.textContent = formatCurrency(this.value);
            }
        });
    }
}

// Submit Property
async function submitProperty(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    
    // Validate required fields
    const requiredFields = ['title', 'property_type', 'monthly_rent', 'location_area', 'distance'];
    for (const field of requiredFields) {
        if (!formData.get(field)) {
            showToast(`Please fill in the ${field.replace('_', ' ')} field`, 'error');
            return;
        }
    }
    
    showLoader();
    
    try {
        const response = await fetch('/api/landlord/property', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Property listed successfully! It will be visible after admin approval.', 'success');
            setTimeout(() => {
                window.location.href = '/landlord/properties';
            }, 2000);
        } else {
            showToast(data.message || 'Error listing property', 'error');
        }
    } catch (error) {
        console.error('Error submitting property:', error);
        showToast('An error occurred', 'error');
    } finally {
        hideLoader();
    }
}

// Setup Image Upload
function setupImageUpload() {
    const dropZone = document.getElementById('imageDropZone');
    if (!dropZone) return;
    
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('border-primary');
    });
    
    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.classList.remove('border-primary');
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('border-primary');
        
        const files = Array.from(e.dataTransfer.files);
        handleImageFiles(files);
    });
    
    const fileInput = document.getElementById('propertyImages');
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            handleImageFiles(Array.from(e.target.files));
        });
    }
}

// Handle Image Files
function handleImageFiles(files) {
    const imageFiles = files.filter(file => file.type.startsWith('image/'));
    
    if (imageFiles.length === 0) {
        showToast('Please select image files only', 'error');
        return;
    }
    
    const container = document.getElementById('imagePreviewContainer');
    if (!container) return;
    
    imageFiles.forEach(file => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const preview = document.createElement('div');
            preview.className = 'preview-image';
            preview.innerHTML = `
                <img src="${e.target.result}" alt="Preview">
                <button type="button" class="remove-image" onclick="this.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            `;
            container.appendChild(preview);
        };
        reader.readAsDataURL(file);
    });
}

// Initialize Analytics
function initAnalytics() {
    if (document.getElementById('analyticsChart')) {
        loadAnalyticsData();
    }
}

// Load Analytics Data
async function loadAnalyticsData() {
    try {
        const response = await fetch('/api/landlord/analytics');
        const data = await response.json();
        
        if (data.success) {
            updateAnalyticsCharts(data);
        }
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

// Update Analytics Charts
function updateAnalyticsCharts(data) {
    // Views chart
    if (window.viewsChart && data.views) {
        window.viewsChart.data.labels = data.views.labels;
        window.viewsChart.data.datasets[0].data = data.views.values;
        window.viewsChart.update();
    }
    
    // Bookings chart
    if (window.bookingsChart && data.bookings) {
        window.bookingsChart.data.labels = data.bookings.labels;
        window.bookingsChart.data.datasets[0].data = data.bookings.values;
        window.bookingsChart.update();
    }
}

// Load Earnings Data
async function loadEarningsData() {
    try {
        const response = await fetch('/api/landlord/earnings');
        const data = await response.json();
        
        if (data.success && window.earningsChart) {
            window.earningsChart.data.labels = data.labels;
            window.earningsChart.data.datasets[0].data = data.earnings;
            window.earningsChart.update();
        }
    } catch (error) {
        console.error('Error loading earnings:', error);
    }
}

// Delete Property
async function deleteProperty(propertyId) {
    const result = await showConfirm('Delete Property', 'Are you sure you want to delete this property? This action cannot be undone.');
    if (!result.isConfirmed) return;
    
    showLoader();
    
    try {
        const response = await fetch(`/api/landlord/property/${propertyId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Property deleted successfully', 'success');
            location.reload();
        } else {
            showToast(data.message || 'Error deleting property', 'error');
        }
    } catch (error) {
        console.error('Error deleting property:', error);
        showToast('An error occurred', 'error');
    } finally {
        hideLoader();
    }
}

// Export landlord functions
window.landlord = {
    approveBooking,
    rejectBooking,
    deleteProperty,
    loadPropertyStats,
    loadRecentBookings
};