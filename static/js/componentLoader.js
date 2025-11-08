// Component loader for dynamic HTML injection
class ComponentLoader {
    static async loadComponent(url, containerId) {
        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error(`Failed to load ${url}`);
            
            const html = await response.text();
            const container = document.getElementById(containerId);
            
            if (container) {
                container.innerHTML = html;
                return true;
            }
            return false;
        } catch (error) {
            console.error(`Error loading component from ${url}:`, error);
            return false;
        }
    }

    static async loadAll() {
        const components = [
            { url: '/templates/components/sidebar.html', container: 'sidebarContainer' },
            { url: '/templates/pages/dashboard.html', container: 'dashboardContainer' },
            { url: '/templates/components/modals.html', container: 'modalsContainer' },
            { url: '/templates/pages/quiz.html', container: 'quizContainer' },
            { url: '/templates/pages/calendar.html', container: 'calendarContainer' },
            { url: '/templates/pages/analytics.html', container: 'analyticsContainer' },
            { url: '/templates/pages/profile.html', container: 'profileContainer' }
        ];

        const promises = components.map(comp => 
            this.loadComponent(comp.url, comp.container)
        );

        await Promise.all(promises);
    }
}

window.ComponentLoader = ComponentLoader;
