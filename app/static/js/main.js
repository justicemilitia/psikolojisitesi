// PsikologSitesi - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Flash message auto-dismiss
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Date picker default value (today)
    var dateInputs = document.querySelectorAll('input[type="date"]:not([min])');
    var today = new Date().toISOString().split('T')[0];
    dateInputs.forEach(function(input) {
        input.min = today;
        if (!input.value) {
            input.value = today;
        }
    });
    
    // Psychologist specialty filter
    var specialtyFilter = document.getElementById('specialty-filter');
    if (specialtyFilter) {
        specialtyFilter.addEventListener('change', function() {
            var specialty = this.value;
            if (specialty) {
                window.location.href = '/psychologists?specialty=' + encodeURIComponent(specialty);
            } else {
                window.location.href = '/psychologists';
            }
        });
    }
    
    // Appointment booking form validation
    var appointmentForm = document.getElementById('appointment-form');
    if (appointmentForm) {
        appointmentForm.addEventListener('submit', function(event) {
            var psychologistId = document.getElementById('psychologist_id').value;
            var date = document.getElementById('date').value;
            var time = document.getElementById('time').value;
            
            if (!psychologistId || !date || !time) {
                event.preventDefault();
                alert('Please fill in all fields');
                return false;
            }
            
            // Validate date is in the future
            var selectedDate = new Date(date);
            var today = new Date();
            today.setHours(0, 0, 0, 0);
            
            if (selectedDate < today) {
                event.preventDefault();
                alert('Please select a future date');
                return false;
            }
            
            return true;
        });
    }
    
    // Time slot selection
    var timeSlots = document.querySelectorAll('.time-slot');
    if (timeSlots.length > 0) {
        timeSlots.forEach(function(slot) {
            slot.addEventListener('click', function() {
                // Remove selected class from all slots
                timeSlots.forEach(function(s) {
                    s.classList.remove('selected');
                });
                
                // Add selected class to clicked slot
                this.classList.add('selected');
                
                // Update hidden input with selected time
                var timeInput = document.getElementById('selected-time');
                if (timeInput) {
                    timeInput.value = this.dataset.time;
                }
                
                // Show booking button
                var bookingButton = document.getElementById('booking-button');
                if (bookingButton) {
                    bookingButton.style.display = 'block';
                }
            });
        });
    }
    
    // Profile form password validation
    var profileForm = document.getElementById('profile-form');
    if (profileForm) {
        var newPassword = document.getElementById('new_password');
        var confirmPassword = document.getElementById('confirm_new_password');
        
        profileForm.addEventListener('submit', function(event) {
            if (newPassword.value && newPassword.value !== confirmPassword.value) {
                event.preventDefault();
                alert('New password and confirmation do not match');
                return false;
            }
            
            return true;
        });
    }
    
    // Search form validation
    var searchForm = document.querySelector('form[action*="search"]');
    if (searchForm) {
        searchForm.addEventListener('submit', function(event) {
            var searchInput = this.querySelector('input[name="q"]');
            if (!searchInput.value.trim()) {
                event.preventDefault();
                return false;
            }
            
            return true;
        });
    }
});

// Function to confirm appointment cancellation
function confirmCancel(event, appointmentId) {
    if (!confirm('Are you sure you want to cancel this appointment?')) {
        event.preventDefault();
        return false;
    }
    
    return true;
}

// Function to format date in locale format
function formatDate(dateString) {
    var date = new Date(dateString);
    return date.toLocaleDateString();
}

// Function to format time in locale format
function formatTime(timeString) {
    var timeParts = timeString.split(':');
    var date = new Date();
    date.setHours(parseInt(timeParts[0]), parseInt(timeParts[1]));
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}