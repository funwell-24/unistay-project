// static/js/filters.js
// Search and Filter Functionality

// Property Filter State
let filterState = {
    location: '',
    propertyType: '',
    minPrice: '',
    maxPrice: '',
    distance: '',
    amenities: {
        wifi: false,
        security: false,
        parking: false,
        water: false,
        electricity: false
    },
    sortBy: 'newest',
    page: 1
};

// Initialize Filters
document.addEventListener('DOMContentLoaded', function() {
    initializeFilters();
    loadFilterValues();
    setupFilterListeners();
});

// Initialize Filters UI
function initializeFilters() {
    // Load saved filters from URL or localStorage
    const urlParams = getUrlParams();
    if (Object.keys(urlParams).length > 0) {
        applyFiltersFromUrl(urlParams);
    } else {
        loadSavedFilters();
    }
    
    updateFilterUI();
}

// Load filter values from localStorage
function loadSavedFilters() {
    const saved = localStorage.getItem('propertyFilters');
    if (saved) {
        try {
            filterState = JSON.parse(saved);
        } catch(e) {
            console.error('Error loading saved filters:', e);
        }
    }
}

// Save filters to localStorage
function saveFilters() {
    localStorage.setItem('propertyFilters', JSON.stringify(filterState));
}

// Setup Filter Event Listeners
function setupFilterListeners() {
    // Location filter
    const locationInput = document.getElementById('filterLocation');
    if (locationInput) {
        locationInput.addEventListener('change', function() {
            filterState.location = this.value;
            applyFilters();
        });
    }
    
    // Property type filter
    const typeSelect = document.getElementById('filterType');
    if (typeSelect) {
        typeSelect.addEventListener('change', function() {
            filterState.propertyType = this.value;
            applyFilters();
        });
    }
    
    // Price range filters
    const minPrice = document.getElementById('filterMinPrice');
    const maxPrice = document.getElementById('filterMaxPrice');
    
    if (minPrice) {
        minPrice.addEventListener('input', debounce(function() {
            filterState.minPrice = this.value;
            applyFilters();
        }, 500));
    }
    
    if (maxPrice) {
        maxPrice.addEventListener('input', debounce(function() {
            filterState.maxPrice = this.value;
            applyFilters();
        }, 500));
    }
    
    // Distance filter
    const distanceSelect = document.getElementById('filterDistance');
    if (distanceSelect) {
        distanceSelect.addEventListener('change', function() {
            filterState.distance = this.value;
            applyFilters();
        });
    }
    
    // Amenity checkboxes
    const amenities = ['wifi', 'security', 'parking', 'water', 'electricity'];
    amenities.forEach(amenity => {
        const checkbox = document.getElementById(`filter${amenity.charAt(0).toUpperCase() + amenity.slice(1)}`);
        if (checkbox) {
            checkbox.addEventListener('change', function() {
                filterState.amenities[amenity] = this.checked;
                applyFilters();
            });
        }
    });
    
    // Sort by filter
    const sortSelect = document.getElementById('filterSort');
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            filterState.sortBy = this.value;
            applyFilters();
        });
    }
    
    // Reset filters button
    const resetBtn = document.getElementById('resetFilters');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetFilters);
    }
}

// Apply Filters
async function applyFilters() {
    showLoader();
    saveFilters();
    updateUrlParams();
    
    try {
        const response = await fetch('/api/search-properties', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(filterState)
        });
        
        const data = await response.json();
        
        if (data.success) {
            updatePropertyResults(data.properties);
            updatePagination(data.pagination);
        } else {
            showToast('Error loading properties', 'error');
        }
    } catch (error) {
        console.error('Filter error:', error);
        showToast('An error occurred', 'error');
    } finally {
        hideLoader();
    }
}

// Update Property Results
function updatePropertyResults(properties) {
    const container = document.getElementById('propertiesContainer');
    if (!container) return;
    
    if (properties.length === 0) {
        container.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-home fa-4x text-muted mb-3"></i>
                <h4>No properties found</h4>
                <p>Try adjusting your filters or search criteria.</p>
                <button class="btn btn-primary" onclick="resetFilters()">Reset Filters</button>
            </div>
        `;
        return;
    }
    
    let html = '<div class="row">';
    properties.forEach(property => {
        html += `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="card property-card h-100">
                    <img src="${property.image_url || '/static/images/placeholder.jpg'}" 
                         class="property-image" alt="${property.title}">
                    <div class="card-body">
                        <h5 class="card-title">${escapeHtml(property.title)}</h5>
                        <p class="property-location">
                            <i class="fas fa-map-marker-alt"></i> ${escapeHtml(property.location)}
                        </p>
                        <p class="property-price">${formatCurrency(property.price)}/month</p>
                        <div class="property-amenities mb-2">
                            ${property.amenities.map(a => `<span class="amenity-badge">${a}</span>`).join('')}
                        </div>
                        <a href="/property/${property.id}" class="btn btn-primary w-100">View Details</a>
                    </div>
                </div>
            </div>
        `;
    });
    html += '</div>';
    
    container.innerHTML = html;
}

// Update Pagination
function updatePagination(pagination) {
    const container = document.getElementById('paginationContainer');
    if (!container) return;
    
    if (!pagination || pagination.total_pages <= 1) {
        container.innerHTML = '';
        return;
    }
    
    let html = '<nav><ul class="pagination justify-content-center">';
    
    // Previous button
    if (pagination.has_prev) {
        html += `<li class="page-item"><a class="page-link" href="#" onclick="changePage(${pagination.prev_page})">Previous</a></li>`;
    } else {
        html += `<li class="page-item disabled"><span class="page-link">Previous</span></li>`;
    }
    
    // Page numbers
    for (let i = 1; i <= pagination.total_pages; i++) {
        if (i === pagination.current_page) {
            html += `<li class="page-item active"><span class="page-link">${i}</span></li>`;
        } else if (Math.abs(i - pagination.current_page) <= 2) {
            html += `<li class="page-item"><a class="page-link" href="#" onclick="changePage(${i})">${i}</a></li>`;
        } else if (i === pagination.current_page - 3 || i === pagination.current_page + 3) {
            html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
        }
    }
    
    // Next button
    if (pagination.has_next) {
        html += `<li class="page-item"><a class="page-link" href="#" onclick="changePage(${pagination.next_page})">Next</a></li>`;
    } else {
        html += `<li class="page-item disabled"><span class="page-link">Next</span></li>`;
    }
    
    html += '</ul></nav>';
    container.innerHTML = html;
}

// Change Page
function changePage(page) {
    filterState.page = page;
    applyFilters();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Reset All Filters
function resetFilters() {
    filterState = {
        location: '',
        propertyType: '',
        minPrice: '',
        maxPrice: '',
        distance: '',
        amenities: {
            wifi: false,
            security: false,
            parking: false,
            water: false,
            electricity: false
        },
        sortBy: 'newest',
        page: 1
    };
    
    updateFilterUI();
    applyFilters();
    showToast('Filters reset', 'info');
}

// Update Filter UI
function updateFilterUI() {
    // Update form inputs with current filter state
    const locationInput = document.getElementById('filterLocation');
    if (locationInput) locationInput.value = filterState.location;
    
    const typeSelect = document.getElementById('filterType');
    if (typeSelect) typeSelect.value = filterState.propertyType;
    
    const minPrice = document.getElementById('filterMinPrice');
    if (minPrice) minPrice.value = filterState.minPrice;
    
    const maxPrice = document.getElementById('filterMaxPrice');
    if (maxPrice) maxPrice.value = filterState.maxPrice;
    
    const distanceSelect = document.getElementById('filterDistance');
    if (distanceSelect) distanceSelect.value = filterState.distance;
    
    // Update checkboxes
    for (const [amenity, checked] of Object.entries(filterState.amenities)) {
        const checkbox = document.getElementById(`filter${amenity.charAt(0).toUpperCase() + amenity.slice(1)}`);
        if (checkbox) checkbox.checked = checked;
    }
    
    const sortSelect = document.getElementById('filterSort');
    if (sortSelect) sortSelect.value = filterState.sortBy;
}

// Apply filters from URL parameters
function applyFiltersFromUrl(params) {
    if (params.location) filterState.location = params.location;
    if (params.type) filterState.propertyType = params.type;
    if (params.min_price) filterState.minPrice = params.min_price;
    if (params.max_price) filterState.maxPrice = params.max_price;
    if (params.distance) filterState.distance = params.distance;
    if (params.sort) filterState.sortBy = params.sort;
    
    applyFilters();
}

// Update URL with current filters
function updateUrlParams() {
    const params = {
        location: filterState.location || undefined,
        type: filterState.propertyType || undefined,
        min_price: filterState.minPrice || undefined,
        max_price: filterState.maxPrice || undefined,
        distance: filterState.distance || undefined,
        sort: filterState.sortBy || undefined,
        page: filterState.page > 1 ? filterState.page : undefined
    };
    
    setUrlParams(params);
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Export filter functions
window.filters = {
    applyFilters,
    resetFilters,
    changePage,
    getFilterState: () => filterState
};