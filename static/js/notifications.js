/**
 * Modern Notification System
 * Toast notifications with animations and auto-dismiss
 */

class NotificationSystem {
    constructor() {
        this.container = null;
        this.init();
    }

    init() {
        // Create notification container
        this.container = document.createElement('div');
        this.container.id = 'notification-container';
        this.container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 12px;
            max-width: 400px;
        `;
        document.body.appendChild(this.container);
    }

    show(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        
        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };

        const colors = {
            success: { bg: '#10b981', border: '#059669' },
            error: { bg: '#ef4444', border: '#dc2626' },
            warning: { bg: '#f59e0b', border: '#d97706' },
            info: { bg: '#3b82f6', border: '#2563eb' }
        };

        const color = colors[type] || colors.info;

        notification.style.cssText = `
            background: ${color.bg};
            color: white;
            padding: 16px 20px;
            border-radius: 12px;
            border-left: 4px solid ${color.border};
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 14px;
            font-weight: 500;
            animation: slideInRight 0.3s ease, fadeOut 0.3s ease ${duration - 300}ms;
            cursor: pointer;
            transition: transform 0.2s ease;
        `;

        notification.innerHTML = `
            <div style="
                width: 24px;
                height: 24px;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.2);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 16px;
                font-weight: bold;
            ">${icons[type]}</div>
            <div style="flex: 1;">${message}</div>
            <button style="
                background: none;
                border: none;
                color: white;
                font-size: 18px;
                cursor: pointer;
                opacity: 0.7;
                transition: opacity 0.2s;
                padding: 0;
                width: 20px;
                height: 20px;
            " onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0.7'">×</button>
        `;

        // Hover effect
        notification.addEventListener('mouseenter', () => {
            notification.style.transform = 'translateX(-5px)';
        });

        notification.addEventListener('mouseleave', () => {
            notification.style.transform = 'translateX(0)';
        });

        // Close button
        const closeBtn = notification.querySelector('button');
        closeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.remove(notification);
        });

        // Click to dismiss
        notification.addEventListener('click', () => {
            this.remove(notification);
        });

        this.container.appendChild(notification);

        // Auto remove
        if (duration > 0) {
            setTimeout(() => {
                this.remove(notification);
            }, duration);
        }

        return notification;
    }

    remove(notification) {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }

    success(message, duration) {
        return this.show(message, 'success', duration);
    }

    error(message, duration) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration) {
        return this.show(message, 'info', duration);
    }
}

// Add animations to document
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(100px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    @keyframes slideOutRight {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100px);
        }
    }

    @keyframes fadeOut {
        from { opacity: 1; }
        to { opacity: 0.7; }
    }
`;
document.head.appendChild(style);

// Global instance
window.notify = new NotificationSystem();

// Export for modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NotificationSystem;
}
