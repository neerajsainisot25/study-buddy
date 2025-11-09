// Dashboard-specific functionality
class Dashboard {
    constructor() {
        this.stats = {};
        this.dashboardData = null;
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
                this.loadDashboardAnalytics(),
                this.loadUserProfile()
            ]);
        } catch (error) {
            console.error('Error loading dashboard stats:', error);
        }
    }

    async loadUserProfile() {
        try {
            const response = await fetch('/api/profile');
            if (!response.ok) return;
            const data = await response.json();
            
            // Update welcome message with user name
            const welcomeBanner = document.querySelector('.welcome-banner h2');
            if (welcomeBanner && data.name) {
                welcomeBanner.textContent = `Welcome back, ${data.name}! 👋`;
            }
            
            // Update study hours from profile
            if (data.study_hours) {
                this.updateElement('studyHours', data.study_hours);
                const studyHoursBar = document.getElementById('studyHoursBar');
                if (studyHoursBar) {
                    const weeklyGoal = data.weekly_goal || 20;
                    const percentage = Math.min((data.study_hours / weeklyGoal) * 100, 100);
                    studyHoursBar.style.width = `${percentage}%`;
                }
            }
        } catch (error) {
            console.error('Error loading user profile:', error);
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
            const response = await fetch('/api/chat/analytics');
            if (!response.ok) return;
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
            const response = await fetch('/api/calendar/upcoming');
            if (!response.ok) return;
            const data = await response.json();
            
            if (data.count !== undefined) {
                this.updateElement('eventsCount', data.count);
                const nextEventText = data.next_event ? data.next_event.title : 'No events scheduled';
                this.updateElement('nextEvent', nextEventText);
            }
            
            // Update upcoming events list
            await this.updateUpcomingEvents(data);
        } catch (error) {
            console.error('Error loading events:', error);
        }
    }

    async loadQuizHistory() {
        try {
            const response = await fetch('/api/quiz/history');
            if (!response.ok) return;
            const data = await response.json();
            
            if (data.total_attempts !== undefined) {
                this.updateElement('quizCount', data.total_attempts);
                this.updateElement('quizTotal', `/ ${data.total_quizzes || 0}`);
                this.updateElement('totalQuizzesMetric', data.total_attempts || 0);
                this.updateElement('avgScoreMetric', `${data.average_score || 0}%`);
                this.updateElement('currentStreak', data.total_attempts || 0);
                
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
            const response = await fetch('/api/analytics/dashboard');
            if (!response.ok) return;
            const data = await response.json();
            
            this.dashboardData = data;
            
            // Update streak and metrics
            if (data.quiz) {
                this.updateElement('studyStreak', data.quiz.total_attempts || 0);
                this.updateElement('personalBest', data.quiz.total_quizzes || 0);
                this.updateElement('studyStreakDays', `${data.quiz.total_attempts || 0} quizzes`);
            }
            
            // Update quiz performance by topic
            if (data.quiz && data.quiz.by_topic) {
                this.updateQuizPerformanceByTopic(data.quiz.by_topic);
            }
            
            // Update recent chat sessions
            if (data.activity && data.activity.recent_chats) {
                this.updateRecentChats(data.activity.recent_chats);
            }
            
            // Update trends
            if (data.trends && data.trends.daily) {
                this.renderQuizTrendChart(data.trends.daily);
            }
        } catch (error) {
            console.error('Error loading dashboard analytics:', error);
        }
    }

    updateQuizPerformanceByTopic(topicPerformance) {
        const container = document.getElementById('quizPerformanceList');
        if (!container) return;
        
        if (!topicPerformance || Object.keys(topicPerformance).length === 0) {
            container.innerHTML = '<div style="text-align: center; color: var(--text-secondary); padding: 40px;">No quiz data yet. Take your first quiz to see performance metrics!</div>';
            return;
        }
        
        // Convert to array and sort by count
        const topics = Object.entries(topicPerformance)
            .map(([topic, data]) => ({topic, ...data}))
            .sort((a, b) => b.count - a.count)
            .slice(0, 5);
        
        let html = '';
        const colors = ['var(--primary)', 'var(--accent)', 'var(--success)', 'var(--primary-light)', 'var(--accent-light)'];
        
        topics.forEach((item, index) => {
            const borderBottom = index < topics.length - 1 ? 'border-bottom: 1px solid var(--border);' : '';
            const color = colors[index % colors.length];
            html += `
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 0; ${borderBottom}">
                    <div style="font-size: 14px; font-weight: 500; color: var(--text);">${this.escapeHtml(item.topic)}</div>
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <div style="flex: 1; height: 8px; background: var(--bg-secondary); border-radius: 4px; width: 120px; overflow: hidden;">
                            <div style="height: 100%; background: ${color}; width: ${item.avg_score}%; transition: width 0.5s ease;"></div>
                        </div>
                        <span style="font-size: 14px; font-weight: 600; color: var(--text); min-width: 40px; text-align: right;">${Math.round(item.avg_score)}%</span>
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
    }

    updateRecentChats(recentChats) {
        const container = document.getElementById('recentChatsList');
        if (!container) return;
        
        if (!recentChats || recentChats.length === 0) {
            container.innerHTML = '<div style="text-align: center; color: var(--text-secondary); padding: 20px;">No recent chats. Start a conversation!</div>';
            return;
        }
        
        let html = '';
        recentChats.slice(0, 2).forEach((chat, index) => {
            const borderBottom = index < recentChats.length - 1 && index < 1 ? 'border-bottom: 1px solid var(--border);' : '';
            html += `
                <div style="padding: 12px 0; ${borderBottom}">
                    <div style="font-size: 14px; font-weight: 500; color: var(--text); margin-bottom: 4px;">${this.escapeHtml(chat.question)}</div>
                    <div style="font-size: 11px; color: var(--text-light); margin-top: 4px;">${chat.time_ago || 'Recently'}</div>
                </div>
            `;
        });
        
        container.innerHTML = html;
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
            return;
        }

        // Chart rendering logic here (simplified for brevity)
        container.innerHTML = '<div style="text-align: center; color: var(--text-secondary); padding: 40px;">Chart rendering...</div>';
    }

    async updateUpcomingEvents(data) {
        const container = document.getElementById('upcomingEventsList');
        if (!container) return;

        if (data.events && data.events.length > 0) {
            let html = '';
            data.events.slice(0, 2).forEach((event, index) => {
                const borderBottom = index < 1 && data.events.length > 1 ? 'border-bottom: 1px solid var(--border);' : '';
                html += `
                    <div style="padding: 12px 0; ${borderBottom}">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <div style="font-size: 14px; font-weight: 500; color: var(--text); margin-bottom: 4px;">
                                    ${this.escapeHtml(event.title)}
                                </div>
                                <div style="font-size: 12px; color: var(--text-secondary);">${event.time || 'All day'} • ${event.date}</div>
                            </div>
                        </div>
                    </div>
                `;
            });
            container.innerHTML = html;
        } else {
            container.innerHTML = '<div style="text-align: center; color: var(--text-secondary); padding: 20px;">No upcoming events. Add one in the Calendar!</div>';
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
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Global dashboard instance
window.dashboardInstance = new Dashboard();
