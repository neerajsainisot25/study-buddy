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
            const data = await response.json();
            
            if (data.total_queries !== undefined) {
                this.updateElement('queriesCount', data.total_queries);
                this.updateElement('queriesToday', `${data.today_queries} today`);
                this.updateElement('chatQueriesMetric', data.total_queries);
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
            const response = await fetch('/api/quiz/history');
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
            const response = await fetch('/api/analytics/dashboard');
            const data = await response.json();
            
            if (data.trends?.daily) {
                this.renderQuizTrendChart(data.trends.daily);
            }
            
            if (data.activity?.recent) {
                this.updateUpcomingEvents(data.activity.recent);
            }
            
            this.updateQuizPerformance(data.quiz);
            this.updateRecentChats(data.chat);
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

    updateUpcomingEvents(recentActivity) {
        const container = document.getElementById('upcomingEventsList');
        if (!container) return;

        fetch('/api/calendar/upcoming')
            .then(response => response.json())
            .then(data => {
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
            })
            .catch(error => console.error('Error loading events:', error));
    }

    updateQuizPerformance(quizData) {
        const container = document.getElementById('quizPerformanceList');
        if (!container) return;

        fetch('/api/analytics/quiz')
            .then(response => response.json())
            .then(data => {
                const topicPerf = data.topic_performance || {};
                const topics = Object.keys(topicPerf);
                
                if (topics.length > 0) {
                    let html = '';
                    topics.slice(0, 3).forEach((topic, index) => {
                        const perf = topicPerf[topic];
                        const score = perf.avg_score || 0;
                        const borderStyle = index < topics.length - 1 ? 'border-bottom: 1px solid var(--border);' : '';
                        
                        html += `
                            <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 0; ${borderStyle}">
                                <div style="font-size: 14px; font-weight: 500; color: var(--text);">${this.escapeHtml(topic)}</div>
                                <div style="display: flex; align-items: center; gap: 12px;">
                                    <div style="flex: 1; height: 8px; background: var(--bg-secondary); border-radius: 4px; width: 120px; overflow: hidden;">
                                        <div style="height: 100%; background: var(--gradient-primary); width: ${score}%; transition: width 0.5s ease;"></div>
                                    </div>
                                    <span style="font-size: 14px; font-weight: 600; color: var(--text); min-width: 40px; text-align: right;">${Math.round(score)}%</span>
                                </div>
                            </div>
                        `;
                    });
                    container.innerHTML = html;
                } else {
                    container.innerHTML = '<div style="text-align: center; color: var(--text-secondary); padding: 20px;">Complete quizzes to see performance data</div>';
                }
            })
            .catch(error => {
                console.error('Error loading quiz performance:', error);
                container.innerHTML = '<div style="text-align: center; color: var(--text-secondary); padding: 20px;">Complete quizzes to see performance data</div>';
            });
    }

    updateRecentChats(chatData) {
        const container = document.getElementById('recentChatsList');
        if (!container) return;

        fetch('/api/chat/history')
            .then(response => response.json())
            .then(data => {
                if (data.sessions && data.sessions.length > 0) {
                    let html = '';
                    data.sessions.slice(0, 2).forEach((session, index) => {
                        const borderStyle = index < 1 ? 'border-bottom: 1px solid var(--border);' : '';
                        const preview = session.last_message || 'No messages';
                        
                        html += `
                            <div style="padding: 12px 0; ${borderStyle}">
                                <div style="font-size: 14px; font-weight: 500; color: var(--text); margin-bottom: 4px;">
                                    Chat Session (${session.message_count} messages)
                                </div>
                                <div style="font-size: 12px; color: var(--text-secondary);">${this.escapeHtml(preview)}</div>
                            </div>
                        `;
                    });
                    container.innerHTML = html;
                } else {
                    container.innerHTML = '<div style="text-align: center; color: var(--text-secondary); padding: 20px;">Start chatting to see recent conversations</div>';
                }
            })
            .catch(error => {
                console.error('Error loading chat sessions:', error);
                container.innerHTML = '<div style="text-align: center; color: var(--text-secondary); padding: 20px;">Start chatting to see recent conversations</div>';
            });
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
