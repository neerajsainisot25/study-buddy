/**
 * Main Application Controller
 * Handles tab navigation and app initialization
 */

class App {
    constructor() {
        this.currentTab = 'chat';
        this.init();
    }

    init() {
        this.setupTabNavigation();
        this.initializeModules();
    }

    setupTabNavigation() {
        const tabs = document.querySelectorAll('.nav-tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                const tabName = e.target.textContent.includes('Chat') ? 'chat' :
                               e.target.textContent.includes('Quiz') ? 'quiz' : 'calendar';
                this.switchTab(tabName, e.target);
            });
        });
    }

    switchTab(tab, element) {
        // Update active tab
        document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
        
        element.classList.add('active');
        document.getElementById(tab + 'Tab').classList.add('active');
        
        this.currentTab = tab;

        // Initialize tab-specific functionality
        if (tab === 'calendar' && typeof Calendar !== 'undefined') {
            Calendar.init();
        }
    }

    initializeModules() {
        // Initialize chat if module exists
        if (typeof Chat !== 'undefined') {
            Chat.init();
        }

        // Initialize quiz if module exists
        if (typeof Quiz !== 'undefined') {
            Quiz.init();
        }

        // Initialize calendar if module exists
        if (typeof Calendar !== 'undefined') {
            Calendar.init();
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
});

