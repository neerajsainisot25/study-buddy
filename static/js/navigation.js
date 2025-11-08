// Navigation and page switching logic
class Navigation {
    constructor() {
        this.currentPage = 'dashboard';
    }

    switchPage(page, element) {
        // Update nav items
        document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
        if (element) element.classList.add('active');

        // Update page content
        document.querySelectorAll('.page-content').forEach(content => content.classList.remove('active'));
        const pageElement = document.getElementById(page + 'Page');
        if (pageElement) pageElement.classList.add('active');

        // Page-specific initialization
        this.initializePage(page);
        this.currentPage = page;
    }

    initializePage(page) {
        switch(page) {
            case 'analytics':
                if (typeof Analytics !== 'undefined' && window.analyticsInstance) {
                    window.analyticsInstance.init();
                }
                break;
            case 'calendar':
                if (typeof Calendar !== 'undefined' && window.calendarInstance) {
                    window.calendarInstance.loadCalendar();
                }
                break;
            case 'profile':
                if (typeof Profile !== 'undefined' && window.profileInstance) {
                    window.profileInstance.loadProfile();
                }
                break;
            case 'quiz':
                if (typeof Quiz !== 'undefined' && window.quizInstance) {
                    window.quizInstance.init();
                }
                break;
            default:
                // Stop analytics updates when navigating away
                if (typeof Analytics !== 'undefined' && window.analyticsInstance) {
                    window.analyticsInstance.stop();
                }
        }
    }
}

// Global navigation instance
window.navigationInstance = new Navigation();

// Global function for onclick handlers
function switchPage(page, element) {
    window.navigationInstance.switchPage(page, element);
    
    // Close mobile sidebar after navigation
    if (window.innerWidth <= 768) {
        toggleMobileSidebar();
    }
}

// Mobile sidebar toggle functionality (for mobile menu only)
function toggleSidebar() {
    toggleMobileSidebar();
}

function toggleMobileSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    
    if (window.innerWidth <= 768) {
        sidebar.classList.toggle('mobile-open');
        overlay.classList.toggle('active');
    }
}
