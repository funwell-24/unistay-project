// static/js/main.js
// Main JavaScript File for UniStay Platform

// Global Variables
let currentUser = null;
let apiBaseUrl = '/api';

// Document Ready
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    loadUserData();
});

// Initialize Application
function initializeApp() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Initialize Select2
    if (typeof $.fn.select2 !== 'undefined') {
        $('.select2').select2({
            theme: 'bootstrap-5'
        });
    }
    
    // Hide loader after page load
    hideLoader();
}

// Setup Event Listeners
function setupEventListeners() {
    // Back to top button
    window.addEventListener('scroll', function() {
        const backToTop = document.getElementById('backToTop');
        if (backToTop) {
            if (window.pageYOffset > 300) {
                backToTop.style.display = 'block';
            } else {
                backToTop.style.display = 'none';
            }
        }
    });
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
    
    // Auto-hide alerts
    setTimeout(function() {
        document.querySelectorAll('.alert').forEach(alert => {
            const bsAlert = new bootstrap.Alert(alert);
            setTimeout(() => bsAlert.close(), 5000);
        });
    }, 1000);
}

// Load User Data
function loadUserData() {
    fetch('/api/current-user')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                currentUser = data.user;
                updateUIForUser();
            }
        })
        .catch(error => console.error('Error loading user data:', error));
}

// Update UI Based on User
function updateUIForUser() {
    if (currentUser) {
        // Update user avatar
        const userAvatar = document.querySelector('.user-avatar');
        if (userAvatar && currentUser.profile_photo) {
            userAvatar.src = currentUser.profile_photo;
        }
        
        // Update user name
        const userNameElements = document.querySelectorAll('.user-name');
        userNameElements.forEach(el => {
            el.textContent = currentUser.full_name;
        });
    }
}

// Show Loader
function showLoader() {
    const loader = document.getElementById('loader');
    if (loader) {
        loader.style.display = 'flex';
    }
}

// Hide Loader
function hideLoader() {
    const loader = document.getElementById('loader');
    if (loader) {
        loader.style.display = 'none';
    }
}

// Show Toast Notification
function showToast(message, type = 'info') {
    const toastEl = document.getElementById('liveToast');
    if (toastEl) {
        const toastBody = document.getElementById('toastMessage');
        const toastHeader = toastEl.querySelector('.toast-header');
        
        let icon = 'fas fa-bell';
        if (type === 'success') icon = 'fas fa-check-circle';
        if (type === 'error') icon = 'fas fa-exclamation-circle';
        if (type === 'warning') icon = 'fas fa-exclamation-triangle';
        
        if (toastHeader) {
            toastHeader.querySelector('i').className = `${icon} me-2 text-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'primary'}`;
        }
        
        if (toastBody) {
            toastBody.textContent = message;
        }
        
        const toast = new bootstrap.Toast(toastEl);
        toast.show();
    }
}

// Format Currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-KE', {
        style: 'currency',
        currency: 'KES',
        minimumFractionDigits: 0
    }).format(amount);
}

// Format Date
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-KE', options);
}

// Format Relative Time
function formatRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000);
    
    if (diff < 60) return 'just now';
    if (diff < 3600) return `${Math.floor(diff / 60)} minutes ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)} hours ago`;
    if (diff < 604800) return `${Math.floor(diff / 86400)} days ago`;
    
    return formatDate(dateString);
}

// Debounce Function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Validate Email
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Validate Phone (Kenyan format)
function validatePhone(phone) {
    const re = /^(\+254|0)[17]\d{8}$/;
    return re.test(phone);
}

// Get URL Parameters
function getUrlParams() {
    const params = {};
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    
    for (const [key, value] of urlParams) {
        params[key] = value;
    }
    
    return params;
}

// Set URL Parameters
function setUrlParams(params) {
    const url = new URL(window.location.href);
    for (const [key, value] of Object.entries(params)) {
        if (value) {
            url.searchParams.set(key, value);
        } else {
            url.searchParams.delete(key);
        }
    }
    window.history.pushState({}, '', url);
}

// Copy to Clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success');
    }).catch(() => {
        showToast('Failed to copy', 'error');
    });
}

// Lazy Load Images
function lazyLoadImages() {
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// Infinite Scroll
function setupInfiniteScroll(callback) {
    let loading = false;
    
    window.addEventListener('scroll', debounce(() => {
        if (loading) return;
        
        const scrollPosition = window.innerHeight + window.scrollY;
        const threshold = document.body.scrollHeight - 500;
        
        if (scrollPosition >= threshold) {
            loading = true;
            callback().finally(() => {
                loading = false;
            });
        }
    }, 200));
}

// Export Functions
window.utils = {
    showLoader,
    hideLoader,
    showToast,
    formatCurrency,
    formatDate,
    formatRelativeTime,
    validateEmail,
    validatePhone,
    getUrlParams,
    setUrlParams,
    copyToClipboard,
    lazyLoadImages
};