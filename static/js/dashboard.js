// Dashboard-specific functionality
class Dashboard {
    constructor() {
        this.stats = {};
    }

    async init() {
        await this.loadStats();
        this.updateKBDocCount();
    }

    async loadStats() {
        try {
            await Promise.all([
                this.loadRAGStatus(),
                this.loadAnalytics(),
                this.loadEvents(),
                this.loadQuizHistory(),
                this.loadDashboardAnalytics()
            ]);
        } catch (error) {
            console.error('Error loading dashboard stats:', error);
            if (error.message === 'Unauthorized') {
                showAuthModal();
            }
        }
    }

    async loadRAGStatus() {
        try {
            const response = await fetch('/api/rag/status');
            const data = await response.json();
            
            if (data.document_count !== undefined) {
                this.updateElement('kbCount', data.document_count);
                this.updateElement('kbStatus', data.status || 'Ready');
            }

            const ragStatus = document.getElementById('ragStatus');
            if (data.ready && ragStatus) {
                ragStatus.style.display = 'inline';
                if (data.document_count !== undefined) {
                    ragStatus.textContent = `Knowledge Base (${data.document_count} docs)`;
                }
            }
        } catch (error) {
            console.error('Error loading RAG status:', error);
        }
    }

    async loadAnalytics() {
        try {
            const response = await window.authManager.apiCall('/api/chat/analytics');
            if (!response.ok) {
                if (response.status === 401) throw new Error('Unauthorized');
                return;
            }
            const data = await response.json();
            
            if (data.total_queries !== undefined) {
                this.updateElement('queriesCount', data.total_queries);
                this.updateElement('queriesToday', `${data.today_queries} today`);
            }

            if (data.last_activity) {
                const activityText = this.formatLastActivity(data.last_activity);
                this.updateElement('chatLastActivity', `Last activity: ${activityText}`);
            }
        } catch (error) {
            console.error('Error loading analytics:', error);
        }
    }

    async loadEvents() {
        try {
            const response = await window.authManager.apiCall('/api/calendar/upcoming');
            if (!response.ok) {
                if (response.status === 401) throw new Error('Unauthorized');
                return;
            }
            const data = await response.json();
            
            if (data.count !== undefined) {
                this.updateElement('eventsCount', data.count);
                const nextEventText = data.next_event ? data.next_event.title : 'No events scheduled';
                this.updateElement('nextEvent', nextEventText);
            }
        } catch (error) {
            console.error('Error loading events:', error);
        }
    }

    async loadQuizHistory() {
        try {
            const response = await window.authManager.apiCall('/api/quiz/history');
            if (!response.ok) {
                if (response.status === 401) throw new Error('Unauthorized');
                return;
            }
            const data = await response.json();
            
            if (data.total_attempts !== undefined) {
                this.updateElement('quizCount', data.total_attempts);
                this.updateElement('quizTotal', `/ ${data.total_quizzes || 0}`);
                this.updateElement('totalQuizzesMetric', data.total_attempts || 0);
                this.updateElement('avgScoreMetric', `${data.average_score || 0}%`);
                
                const avgScoreBar = document.getElementById('avgScoreBar');
                if (avgScoreBar) {
                    avgScoreBar.style.width = `${data.average_score || 0}%`;
                }
            }
        } catch (error) {
            console.error('Error loading quiz history:', error);
        }
    }

    async loadDashboardAnalytics() {
        try {
            const response = await window.authManager.apiCall('/api/analytics/dashboard');
            if (!response.ok) {
                if (response.status === 401) throw new Error('Unauthorized');
                return;
            }
            const data = await response.json();
            
            if (data.trends?.daily) {
                this.renderQuizTrendChart(data.trends.daily);
            }
            
            if (data.activity?.recent) {
                this.updateUpcomingEvents(data.activity.recent);
            }
        } catch (error) {
            console.error('Error loading analytics:', error);
        }
    }

    async updateKBDocCount() {
        try {
            const response = await fetch('/api/rag/status');
            const data = await response.json();
            const kbDocCountEl = document.getElementById('kbDocCount');
            if (kbDocCountEl && data.document_count !== undefined) {
                kbDocCountEl.textContent = `(${data.document_count})`;
            }
        } catch (error) {
            console.error('Error loading KB status:', error);
        }
    }

    renderQuizTrendChart(dailyData) {
        const container = document.getElementById('quizTrendChart');
        if (!container) return;

        if (!dailyData || dailyData.length === 0) {
            container.innerHTML = '<div style="text-align: center; color: var(--text-secondary); padding: 40px;">No trend data available yet. Complete some quizzes to see your performance!</div>';
            return;
        }

        // Chart rendering logic here (simplified for brevity)
        container.innerHTML = '<div style="text-align: center; color: var(--text-secondary); padding: 40px;">Chart rendering...</div>';
    }

    async updateUpcomingEvents(recentActivity) {
        const container = document.getElementById('upcomingEventsList');
        if (!container) return;

        try {
            const response = await window.authManager.apiCall('/api/calendar/upcoming');
            if (!response.ok) return;
            const data = await response.json();
            
            if (data.events && data.events.length > 0) {
                let html = '';
                data.events.slice(0, 2).forEach(event => {
                    html += `
                        <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid var(--border);">
                            <div>
                                <div style="font-size: 14px; font-weight: 500; color: var(--text); margin-bottom: 4px;">
                                    • ${this.escapeHtml(event.title)}
                                </div>
                                <div style="font-size: 12px; color: var(--text-secondary);">${event.time || 'All day'}</div>
                            </div>
                        </div>
                    `;
                });
                container.innerHTML = html;
            } else {
                container.innerHTML = '<div style="text-align: center; color: var(--text-secondary); padding: 20px;">No upcoming events</div>';
            }
        } catch (error) {
            console.error('Error loading events:', error);
        }
    }

    // Utility methods
    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) element.textContent = value;
    }

    formatLastActivity(timestamp) {
        const lastActivity = new Date(timestamp * 1000);
        const minutesAgo = Math.floor((Date.now() - lastActivity) / 60000);
        if (minutesAgo < 1) return 'Just now';
        if (minutesAgo < 60) return `${minutesAgo}m ago`;
        return `${Math.floor(minutesAgo / 60)}h ago`;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Global dashboard instance
window.dashboardInstance = new Dashboard();
