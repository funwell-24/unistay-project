// static/js/student.js
// Student Dashboard Scripts

// Student Dashboard Initialization
document.addEventListener('DOMContentLoaded', function() {
    initStudentDashboard();
    setupSavePropertyButtons();
    setupReviewSystem();
    initPropertyComparison();
});

// Initialize Student Dashboard
function initStudentDashboard() {
    // Load saved properties count
    loadSavedPropertiesCount();
    
    // Load booking history
    loadBookingHistory();
    
    // Initialize property search
    if (document.getElementById('quickSearch')) {
        setupQuickSearch();
    }
}

// Load Saved Properties Count
async function loadSavedPropertiesCount() {
    try {
        const response = await fetch('/api/student/saved-count');
        const data = await response.json();
        
        if (data.success) {
            const badge = document.getElementById('savedCount');
            if (badge) {
                badge.textContent = data.count;
            }
        }
    } catch (error) {
        console.error('Error loading saved count:', error);
    }
}

// Load Booking History
async function loadBookingHistory() {
    const container = document.getElementById('bookingHistory');
    if (!container) return;
    
    try {
        const response = await fetch('/api/student/bookings');
        const data = await response.json();
        
        if (data.success && data.bookings.length > 0) {
            updateBookingHistoryUI(data.bookings);
        } else {
            container.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-calendar fa-3x text-muted mb-3"></i>
                    <p>No bookings yet</p>
                    <a href="/search" class="btn btn-primary">Browse Properties</a>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading bookings:', error);
    }
}

// Update Booking History UI
function updateBookingHistoryUI(bookings) {
    const container = document.getElementById('bookingHistory');
    if (!container) return;
    
    let html = '<div class="table-responsive"><table class="table table-hover"><thead><tr>';
    html += '<th>Property</th><th>Booking Date</th><th>Move In Date</th><th>Status</th><th>Action</th>';
    html += '</tr></thead><tbody>';
    
    bookings.forEach(booking => {
        let statusBadge = '';
        switch(booking.status) {
            case 'pending':
                statusBadge = '<span class="badge bg-warning">Pending</span>';
                break;
            case 'approved':
                statusBadge = '<span class="badge bg-success">Approved</span>';
                break;
            case 'rejected':
                statusBadge = '<span class="badge bg-danger">Rejected</span>';
                break;
            default:
                statusBadge = `<span class="badge bg-secondary">${booking.status}</span>`;
        }
        
        html += `<tr>
            <td><strong>${escapeHtml(booking.property_title)}</strong><br><small class="text-muted">${escapeHtml(booking.location)}</small></td>
            <td>${formatDate(booking.booking_date)}</td>
            <td>${booking.move_in_date ? formatDate(booking.move_in_date) : 'Not set'}</td>
            <td>${statusBadge}</td>
            <td><a href="/property/${booking.property_id}" class="btn btn-sm btn-primary">View Property</a></td>
        </tr>`;
    });
    
    html += '</tbody></table></div>';
    container.innerHTML = html;
}

// Setup Save Property Buttons
function setupSavePropertyButtons() {
    document.querySelectorAll('.save-property-btn').forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.preventDefault();
            const propertyId = this.dataset.propertyId;
            
            if (!propertyId) return;
            
            try {
                const response = await fetch(`/api/student/save-property/${propertyId}`, {
                    method: 'POST'
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showToast('Property saved to favorites!', 'success');
                    this.innerHTML = '<i class="fas fa-check"></i> Saved';
                    this.disabled = true;
                } else {
                    showToast(data.message || 'Error saving property', 'error');
                }
            } catch (error) {
                console.error('Error saving property:', error);
                showToast('An error occurred', 'error');
            }
        });
    });
}

// Setup Review System
function setupReviewSystem() {
    const reviewForm = document.getElementById('reviewForm');
    if (reviewForm) {
        reviewForm.addEventListener('submit', submitReview);
    }
    
    // Star rating selector
    const stars = document.querySelectorAll('.rating-star');
    stars.forEach(star => {
        star.addEventListener('click', function() {
            const rating = this.dataset.rating;
            updateStarRating(rating);
        });
    });
}

// Submit Review
async function submitReview(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const propertyId = formData.get('property_id');
    const rating = formData.get('rating');
    const comment = formData.get('comment');
    
    if (!rating || rating < 1 || rating > 5) {
        showToast('Please select a rating', 'error');
        return;
    }
    
    if (!comment || comment.trim().length < 10) {
        showToast('Please provide a detailed review (minimum 10 characters)', 'error');
        return;
    }
    
    showLoader();
    
    try {
        const response = await fetch(`/api/student/review/${propertyId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ rating: parseInt(rating), comment })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Review submitted! It will be visible after approval.', 'success');
            event.target.reset();
            resetStarRating();
            
            // Close modal if open
            const modal = bootstrap.Modal.getInstance(document.getElementById('reviewModal'));
            if (modal) modal.hide();
        } else {
            showToast(data.message || 'Error submitting review', 'error');
        }
    } catch (error) {
        console.error('Error submitting review:', error);
        showToast('An error occurred', 'error');
    } finally {
        hideLoader();
    }
}

// Update Star Rating UI
function updateStarRating(rating) {
    const stars = document.querySelectorAll('.rating-star');
    stars.forEach((star, index) => {
        if (index < rating) {
            star.classList.add('fas');
            star.classList.remove('far');
            star.style.color = '#ffc107';
        } else {
            star.classList.add('far');
            star.classList.remove('fas');
            star.style.color = '#adb5bd';
        }
    });
    
    document.getElementById('ratingValue').value = rating;
}

// Reset Star Rating
function resetStarRating() {
    updateStarRating(0);
}

// Setup Quick Search
function setupQuickSearch() {
    const searchInput = document.getElementById('quickSearch');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', debounce(async function() {
        const query = this.value;
        
        if (query.length < 2) return;
        
        try {
            const response = await fetch(`/api/search-suggestions?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            if (data.success) {
                showSearchSuggestions(data.suggestions);
            }
        } catch (error) {
            console.error('Error getting suggestions:', error);
        }
    }, 300));
}

// Show Search Suggestions
function showSearchSuggestions(suggestions) {
    let suggestionsHtml = '<div class="list-group">';
    suggestions.forEach(suggestion => {
        suggestionsHtml += `
            <a href="/search?location=${encodeURIComponent(suggestion)}" class="list-group-item list-group-item-action">
                <i class="fas fa-map-marker-alt me-2"></i> ${escapeHtml(suggestion)}
            </a>
        `;
    });
    suggestionsHtml += '</div>';
    
    const container = document.getElementById('searchSuggestions');
    if (container) {
        container.innerHTML = suggestionsHtml;
        container.style.display = 'block';
        
        // Hide after 3 seconds
        setTimeout(() => {
            container.style.display = 'none';
        }, 3000);
    }
}

// Initialize Property Comparison
function initPropertyComparison() {
    const compareCheckboxes = document.querySelectorAll('.compare-checkbox');
    compareCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateCompareList(this.value, this.checked);
        });
    });
    
    loadCompareList();
}

// Update Compare List
function updateCompareList(propertyId, add) {
    let compareList = JSON.parse(localStorage.getItem('compareList') || '[]');
    
    if (add) {
        if (compareList.length >= 4) {
            showToast('You can compare up to 4 properties at once', 'warning');
            this.checked = false;
            return;
        }
        if (!compareList.includes(propertyId)) {
            compareList.push(propertyId);
        }
    } else {
        compareList = compareList.filter(id => id != propertyId);
    }
    
    localStorage.setItem('compareList', JSON.stringify(compareList));
    updateCompareBadge(compareList.length);
}

// Load Compare List
function loadCompareList() {
    const compareList = JSON.parse(localStorage.getItem('compareList') || '[]');
    updateCompareBadge(compareList.length);
    
    // Check checkboxes for properties in compare list
    document.querySelectorAll('.compare-checkbox').forEach(checkbox => {
        checkbox.checked = compareList.includes(checkbox.value);
    });
}

// Update Compare Badge
function updateCompareBadge(count) {
    const badge = document.getElementById('compareCount');
    if (badge) {
        if (count > 0) {
            badge.textContent = count;
            badge.style.display = 'inline';
        } else {
            badge.style.display = 'none';
        }
    }
}

// View Compare Page
function viewCompare() {
    const compareList = JSON.parse(localStorage.getItem('compareList') || '[]');
    if (compareList.length < 2) {
        showToast('Please select at least 2 properties to compare', 'warning');
        return;
    }
    
    window.location.href = `/compare?ids=${compareList.join(',')}`;
}

// Export student functions
window.student = {
    loadSavedPropertiesCount,
    loadBookingHistory,
    submitReview,
    viewCompare
};