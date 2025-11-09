/**
 * Analytics Module
 * Handles real-time analytics display and updates
 */

class Analytics {
    constructor() {
        this.updateInterval = null;
        this.updateFrequency = 5000; // 5 seconds
        this.isActive = false;
    }

    init() {
        this.isActive = true;
        this.loadAnalytics();
        this.startAutoUpdate();
    }

    stop() {
        this.isActive = false;
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    startAutoUpdate() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        
        this.updateInterval = setInterval(() => {
            if (this.isActive) {
                this.loadAnalytics();
            }
        }, this.updateFrequency);
    }

    async loadAnalytics() {
        try {
            const response = await fetch('/api/analytics/dashboard');
            if (!response.ok) {
                return;
            }
            const data = await response.json();

            this.updateOverview(data);
            this.updateCharts(data);
            this.updateRecentActivity(data);
            this.updateLastUpdated();
        } catch (error) {
            console.error('Error loading analytics:', error);
        }
    }

    updateOverview(data) {
        // Total Tasks
        const totalTasks = data.tasks?.total || 0;
        const tasksBreakdown = data.tasks?.completed || {};
        const tasksText = `${tasksBreakdown.quizzes || 0} quizzes, ${tasksBreakdown.chats || 0} chats, ${tasksBreakdown.events || 0} events`;
        
        this.updateElement('totalTasks', totalTasks);
        this.updateElement('tasksBreakdown', tasksText);

        // Quiz Attempts
        const totalQuizAttempts = data.quiz?.total_attempts || 0;
        const todayQuizAttempts = data.quiz?.today_attempts || 0;
        const avgScore = data.quiz?.average_score || 0;
        
        this.updateElement('totalQuizAttempts', totalQuizAttempts);
        this.updateElement('todayQuizAttempts', `${todayQuizAttempts} today`);
        this.updateElement('avgQuizScore', `${avgScore}%`);

        // Chat Queries
        const totalQueries = data.chat?.total_queries || 0;
        const todayQueries = data.chat?.today_queries || 0;
        const activeSessions = data.chat?.active_sessions || 0;
        
        this.updateElement('totalQueries', totalQueries);
        this.updateElement('todayQueries', `${todayQueries} today`);
        this.updateElement('activeSessions', activeSessions);

        // Week Stats
        const weekQuizAttempts = data.quiz?.week_attempts || 0;
        this.updateElement('weekQuizAttempts', weekQuizAttempts);
    }

    updateCharts(data) {
        // Score Distribution
        this.renderScoreDistribution(data.quiz?.recent_attempts || []);
        
        // Quiz Types
        this.renderQuizTypes(data.quiz?.by_type || {});
        
        // Performance Trend
        this.renderPerformanceTrend(data.trends?.daily || []);
    }

    renderScoreDistribution(attempts) {
        const container = document.getElementById('scoreDistribution');
        if (!container) return;

        if (attempts.length === 0) {
            container.innerHTML = '<div style="text-align: center; color: var(--text-secondary); padding: 40px;">No quiz attempts yet</div>';
            return;
        }

        const ranges = {
            '0-50': 0,
            '51-70': 0,
            '71-85': 0,
            '86-100': 0
        };

        attempts.forEach(attempt => {
            const score = attempt.score || 0;
            if (score <= 50) ranges['0-50']++;
            else if (score <= 70) ranges['51-70']++;
            else if (score <= 85) ranges['71-85']++;
            else ranges['86-100']++;
        });

        const max = Math.max(...Object.values(ranges));
        const colors = {
            '0-50': '#ef4444',
            '51-70': '#f59e0b',
            '71-85': '#3b82f6',
            '86-100': '#10b981'
        };

        let html = '<div style="display: flex; flex-direction: column; gap: 12px;">';
        Object.entries(ranges).forEach(([range, count]) => {
            const percentage = max > 0 ? (count / max) * 100 : 0;
            html += `
                <div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 12px;">
                        <span style="color: var(--text); font-weight: 500;">${range}%</span>
                        <span style="color: var(--text-secondary);">${count}</span>
                    </div>
                    <div style="width: 100%; height: 24px; background: var(--bg-secondary); border-radius: 4px; overflow: hidden;">
                        <div style="width: ${percentage}%; height: 100%; background: ${colors[range]}; transition: width 0.3s ease;"></div>
                    </div>
                </div>
            `;
        });
        html += '</div>';

        container.innerHTML = html;
    }

    renderQuizTypes(types) {
        const container = document.getElementById('quizTypesChart');
        if (!container) return;

        if (Object.keys(types).length === 0) {
            container.innerHTML = '<div style="text-align: center; color: var(--text-secondary); padding: 40px;">No quiz types data</div>';
            return;
        }

        const total = Object.values(types).reduce((sum, val) => sum + val, 0);
        const colors = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'];
        let colorIndex = 0;

        let html = '<div style="display: flex; flex-direction: column; gap: 16px;">';
        Object.entries(types).forEach(([type, count]) => {
            const percentage = total > 0 ? (count / total) * 100 : 0;
            const color = colors[colorIndex % colors.length];
            colorIndex++;

            const typeName = type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
            
            html += `
                <div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <div style="width: 12px; height: 12px; border-radius: 2px; background: ${color};"></div>
                            <span style="font-size: 13px; font-weight: 500; color: var(--text);">${typeName}</span>
                        </div>
                        <div style="font-size: 12px; color: var(--text-secondary);">
                            <strong style="color: var(--text);">${count}</strong> (${percentage.toFixed(1)}%)
                        </div>
                    </div>
                    <div style="width: 100%; height: 8px; background: var(--bg-secondary); border-radius: 4px; overflow: hidden;">
                        <div style="width: ${percentage}%; height: 100%; background: ${color}; transition: width 0.3s ease;"></div>
                    </div>
                </div>
            `;
        });
        html += '</div>';

        container.innerHTML = html;
    }

    renderPerformanceTrend(dailyData) {
        const container = document.getElementById('performanceTrend');
        if (!container) return;

        if (dailyData.length === 0) {
            container.innerHTML = '<div style="text-align: center; color: var(--text-secondary); padding: 40px;">No trend data available</div>';
            return;
        }

        // Sort by date
        const sorted = dailyData.sort((a, b) => new Date(a.date) - new Date(b.date));
        const maxQuizzes = Math.max(...sorted.map(d => d.quizzes || 0), 1);
        const maxScore = Math.max(...sorted.map(d => d.avg_score || 0), 1);

        let html = '<div style="display: flex; align-items: flex-end; gap: 12px; height: 200px; padding: 20px 0;">';
        
        sorted.forEach(day => {
            const date = new Date(day.date);
            const dayName = date.toLocaleDateString('en-US', { weekday: 'short' });
            const dayNum = date.getDate();
            
            const quizHeight = maxQuizzes > 0 ? (day.quizzes / maxQuizzes) * 100 : 0;
            const scoreHeight = maxScore > 0 ? (day.avg_score / maxScore) * 100 : 0;
            
            html += `
                <div style="flex: 1; display: flex; flex-direction: column; align-items: center; gap: 8px;">
                    <div style="flex: 1; display: flex; align-items: flex-end; gap: 4px; width: 100%;">
                        <div style="flex: 1; background: var(--primary); border-radius: 4px 4px 0 0; min-height: 20px; height: ${quizHeight}%; opacity: 0.8;" title="${day.quizzes} quizzes"></div>
                        <div style="flex: 1; background: var(--success); border-radius: 4px 4px 0 0; min-height: 20px; height: ${scoreHeight}%; opacity: 0.8;" title="Avg: ${day.avg_score.toFixed(1)}%"></div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 11px; font-weight: 600; color: var(--text);">${dayNum}</div>
                        <div style="font-size: 10px; color: var(--text-secondary);">${dayName}</div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        html += '<div style="display: flex; gap: 16px; justify-content: center; margin-top: 12px; font-size: 11px; color: var(--text-secondary);">';
        html += '<div style="display: flex; align-items: center; gap: 6px;"><div style="width: 12px; height: 12px; background: var(--primary); border-radius: 2px;"></div>Quizzes</div>';
        html += '<div style="display: flex; align-items: center; gap: 6px;"><div style="width: 12px; height: 12px; background: var(--success); border-radius: 2px;"></div>Avg Score</div>';
        html += '</div>';

        container.innerHTML = html;
    }

    updateRecentActivity(data) {
        const container = document.getElementById('recentActivity');
        if (!container) return;

        const activities = data.activity?.recent || [];

        if (activities.length === 0) {
            container.innerHTML = '<div style="text-align: center; color: var(--text-secondary); padding: 40px;">No recent activity</div>';
            return;
        }

        let html = '<div style="display: flex; flex-direction: column; gap: 12px;">';
        activities.forEach(activity => {
            const icon = activity.type === 'quiz' ? '🎯' : '💬';
            const color = activity.type === 'quiz' ? 'var(--success)' : 'var(--primary)';
            
            html += `
                <div style="display: flex; align-items: center; gap: 12px; padding: 12px; background: var(--bg-secondary); border-radius: 6px; border-left: 3px solid ${color};">
                    <div style="font-size: 20px;">${icon}</div>
                    <div style="flex: 1;">
                        <div style="font-size: 13px; font-weight: 500; color: var(--text); margin-bottom: 2px;">
                            ${this.escapeHtml(activity.title || 'Activity')}
                        </div>
                        <div style="font-size: 11px; color: var(--text-secondary);">
                            ${activity.time_ago || 'Just now'}
                            ${activity.type === 'quiz' && activity.score ? ` • Score: ${activity.score}%` : ''}
                        </div>
                    </div>
                </div>
            `;
        });
        html += '</div>';

        container.innerHTML = html;
    }

    updateLastUpdated() {
        const now = new Date();
        const timeStr = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        this.updateElement('lastUpdated', `Last updated: ${timeStr}`);
    }

    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Export for use in other modules
window.Analytics = Analytics;

