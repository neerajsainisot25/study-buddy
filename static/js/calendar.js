// Calendar functionality
class Calendar {
    constructor() {
        this.events = {};
        this.currentDate = new Date();
        this.selectedDate = null;
    }

    init() {
        this.renderCalendar();
        this.loadEvents();
        this.setDefaultDate();
        this.updateTodayDate();
        this.loadTodayEvents();
    }

    loadCalendar() {
        this.init();
    }

    showLoginPrompt() {
        const calendarContainer = document.getElementById('calendarContainer');
        if (calendarContainer) {
            calendarContainer.innerHTML = `
                <div class="section-card" style="text-align: center; padding: 60px 20px;">
                    <h2 style="color: var(--text); margin-bottom: 20px;">Calendar</h2>
                    <p style="color: var(--text-secondary); margin-bottom: 30px;">Please sign in to view and manage your events</p>
                    <button onclick="showAuthModal()" class="btn btn-primary">Sign In</button>
                </div>
            `;
        }
    }

    updateTodayDate() {
        const todayEl = document.getElementById('todayDate');
        if (todayEl) {
            const today = new Date();
            todayEl.textContent = today.toLocaleDateString('en-US', { 
                month: 'short', 
                day: 'numeric' 
            });
        }
    }

    async loadTodayEvents() {
        const container = document.getElementById('todayEventsList');
        if (!container) return;

        try {
            const today = new Date().toISOString().split('T')[0];
            const response = await fetch(`/api/calendar/events?date=${today}`);
            
            if (response.ok) {
                const data = await response.json();
                const events = data.events || [];
                
                if (events.length === 0) {
                    container.innerHTML = '<div class="text-center text-gray-500 py-8 text-sm">No events today</div>';
                    return;
                }
                
                let html = '';
                events.forEach((event, index) => {
                    html += `
                        <div class="p-3 rounded-lg border transition-all hover:shadow-md" style="background: var(--bg-secondary); border-color: var(--border);">
                            <div class="flex items-start justify-between gap-2">
                                <div class="flex-1">
                                    <div class="flex items-center gap-2 mb-1">
                                        ${event.time ? `<span class="text-xs font-semibold px-2 py-1 rounded" style="background: var(--accent); color: white;">${event.time}</span>` : ''}
                                        <span class="text-xs font-medium" style="color: var(--text-secondary);">#${index + 1}</span>
                                    </div>
                                    <h4 class="font-semibold text-sm mb-1" style="color: var(--text);">${this.escapeHtml(event.title)}</h4>
                                    ${event.description ? `<p class="text-xs" style="color: var(--text-secondary);">${this.escapeHtml(event.description)}</p>` : ''}
                                </div>
                                <button onclick="deleteEventFromList('${today}', '${event.id || 0}')" 
                                    class="text-red-600 hover:text-red-800 text-sm p-1">
                                    🗑️
                                </button>
                            </div>
                        </div>
                    `;
                });
                
                container.innerHTML = html;
        } catch (error) {
            console.error('Error loading today events:', error);
        }
    }

    setDefaultDate() {
        const dateInput = document.getElementById('eventDate');
        if (dateInput) {
            dateInput.value = new Date().toISOString().split('T')[0];
        }
    }

    renderCalendar() {
        const grid = document.getElementById('calendarGrid');
        const monthYear = document.getElementById('currentMonthYear');
        if (!grid || !monthYear) return;

        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        
        monthYear.textContent = this.currentDate.toLocaleDateString('en-US', { 
            month: 'long', 
            year: 'numeric' 
        });

        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        const today = new Date();
        
        let html = '';
        
        // Empty cells for days before month starts
        for (let i = 0; i < firstDay; i++) {
            html += '<div class="border min-h-[100px]" style="border-color: var(--border); background: var(--bg-tertiary);"></div>';
        }
        
        // Days of the month
        for (let day = 1; day <= daysInMonth; day++) {
            const date = new Date(year, month, day);
            const dateStr = date.toISOString().split('T')[0];
            const isToday = date.toDateString() === today.toDateString();
            const dayEvents = this.events[dateStr] || [];
            
            const todayStyle = isToday ? 
                'background: var(--primary); color: var(--dark); font-weight: 700;' : 
                'color: var(--text);';
            
            html += `
                <div class="border min-h-[100px] p-2 hover:shadow-md transition-all cursor-pointer"
                     style="border-color: var(--border); background: var(--bg-secondary);"
                     onclick="selectDate('${dateStr}')">
                    <div class="text-right mb-1">
                        <span class="inline-block w-7 h-7 rounded-full text-sm font-semibold flex items-center justify-center"
                              style="${todayStyle}">
                            ${day}
                        </span>
                    </div>
                    <div class="space-y-1">
                        ${dayEvents.slice(0, 2).map(event => `
                            <div class="text-xs px-2 py-1 rounded truncate" 
                                 style="background: var(--accent); color: white;"
                                 title="${this.escapeHtml(event.title)}">
                                ${event.time ? '⏰ ' + event.time + ' ' : ''}${this.escapeHtml(event.title)}
                            </div>
                        `).join('')}
                        ${dayEvents.length > 2 ? `
                            <div class="text-xs px-2" style="color: var(--text-secondary);">+${dayEvents.length - 2} more</div>
                        ` : ''}
                    </div>
                </div>
            `;
        }
        
        grid.innerHTML = html;
    }

    async loadEvents() {
        try {
            const year = this.currentDate.getFullYear();
            const month = this.currentDate.getMonth();
            const daysInMonth = new Date(year, month + 1, 0).getDate();
            
            this.events = {};
            
            for (let day = 1; day <= daysInMonth; day++) {
                const date = new Date(year, month, day);
                const dateStr = date.toISOString().split('T')[0];
                
                const response = await fetch(`/api/calendar/events?date=${dateStr}`);
                if (response.ok) {
                    const data = await response.json();
                    if (data.events && data.events.length > 0) {
                        this.events[dateStr] = data.events;
                    }
                }
            }
            
            this.renderCalendar();
            this.loadEventsList();
        } catch (error) {
            console.error('Error loading events:', error);
        }
    }

    async loadEventsList() {
        const container = document.getElementById('eventsList');
        const countBadge = document.getElementById('upcomingCount');
        if (!container) return;

        try {
            const response = await fetch('/api/calendar/upcoming');
            if (response.ok) {
                const data = await response.json();
                const events = data.events || [];
                
                const today = new Date().toISOString().split('T')[0];
                const upcomingEvents = events.filter(e => e.date !== today);
                
                if (countBadge) {
                    countBadge.textContent = upcomingEvents.length;
                }
                
                if (upcomingEvents.length === 0) {
                    container.innerHTML = '<div class="text-center text-gray-500 py-8 text-sm">No upcoming events</div>';
                    return;
                }
                
                let html = '';
                upcomingEvents.forEach(event => {
                    const date = new Date(event.date);
                    const dateStr = date.toLocaleDateString('en-US', { 
                        month: 'short', 
                        day: 'numeric' 
                    });
                    
                    html += `
                        <div class="p-3 rounded-lg border transition-all hover:shadow-md" style="background: var(--bg-secondary); border-color: var(--border);">
                            <div class="flex items-start gap-3">
                                <div class="flex-shrink-0 text-center px-2 py-1 rounded" style="background: var(--primary); color: var(--dark);">
                                    <div class="text-lg font-bold">${date.getDate()}</div>
                                    <div class="text-xs">${date.toLocaleDateString('en-US', { month: 'short' }).toUpperCase()}</div>
                                </div>
                                <div class="flex-1 min-w-0">
                                    <h4 class="font-semibold text-sm mb-1 truncate" style="color: var(--text);">${this.escapeHtml(event.title)}</h4>
                                    ${event.description ? `<p class="text-xs truncate" style="color: var(--text-secondary);">${this.escapeHtml(event.description)}</p>` : ''}
                                    ${event.time ? `<div class="text-xs mt-1" style="color: var(--accent);">⏰ ${event.time}</div>` : ''}
                                </div>
                                <button onclick="deleteEventFromList('${event.date}', '${event.id || 0}')" 
                                    class="text-red-600 hover:text-red-800 text-sm p-1">
                                    🗑️
                                </button>
                            </div>
                        </div>
                    `;
                });
                
                container.innerHTML = html;
            }
        } catch (error) {
            console.error('Error loading events list:', error);
        }
    }

    async addEvent() {
        const title = document.getElementById('eventTitle')?.value;
        const description = document.getElementById('eventDescription')?.value;
        const date = document.getElementById('eventDate')?.value;
        const time = document.getElementById('eventTime')?.value;

        if (!title || !date) {
            alert('Please fill in title and date');
            return;
        }

        try {
            const response = await fetch('/api/calendar/events', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, description, date, time })
            });

            if (response.ok) {
                await this.loadEvents();
                await this.loadTodayEvents();
                this.clearForm();
                if (window.notify) {
                    window.notify.success('Event added successfully!');
                } else {
                    alert('Event added successfully!');
                }
            } else {
                const data = await response.json();
                if (window.notify) {
                    window.notify.error('Error: ' + (data.error || 'Failed to add event'));
                } else {
                    alert('Error: ' + (data.error || 'Failed to add event'));
                }
            }
        } catch (error) {
            console.error('Error adding event:', error);
            if (window.notify) {
                window.notify.error('Error adding event');
            } else {
                alert('Error adding event');
            }
        }
    }

    async suggestEvent() {
        const description = prompt('Describe the event you want to create:');
        if (!description) return;

        try {
            const response = await fetch('/api/calendar/suggest', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ description })
            });

            if (response.ok) {
                const data = await response.json();
                const suggestion = data.suggestion;
                
                document.getElementById('eventTitle').value = suggestion.title || '';
                document.getElementById('eventDescription').value = suggestion.description || '';
                document.getElementById('eventTime').value = suggestion.time || '';
                
                if (window.notify) {
                    window.notify.success('AI suggestion applied! Review and submit to save.');
                } else {
                    alert('AI suggestion applied! Review and click "Add Event" to save.');
                }
            } else {
                if (window.notify) {
                    window.notify.error('Failed to get AI suggestion');
                } else {
                    alert('Failed to get AI suggestion');
                }
            }
        } catch (error) {
            console.error('Error getting suggestion:', error);
            if (window.notify) {
                window.notify.error('Error getting AI suggestion');
            } else {
                alert('Error getting AI suggestion');
            }
        }
    }

    clearForm() {
        const fields = ['eventTitle', 'eventDescription', 'eventTime'];
        fields.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.value = '';
        });
    }

    previousMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() - 1);
        this.loadEvents();
    }

    nextMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() + 1);
        this.loadEvents();
    }

    goToToday() {
        this.currentDate = new Date();
        this.loadEvents();
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Global functions for onclick handlers
function addEvent() {
    if (window.calendarInstance) {
        window.calendarInstance.addEvent();
    }
}

function suggestEvent() {
    if (window.calendarInstance) {
        window.calendarInstance.suggestEvent();
    }
}

function previousMonth() {
    if (window.calendarInstance) {
        window.calendarInstance.previousMonth();
    }
}

function nextMonth() {
    if (window.calendarInstance) {
        window.calendarInstance.nextMonth();
    }
}

function goToToday() {
    if (window.calendarInstance) {
        window.calendarInstance.goToToday();
    }
}

function selectDate(dateStr) {
    if (window.calendarInstance) {
        document.getElementById('eventDate').value = dateStr;
        // Scroll to add event form
        document.getElementById('eventTitle')?.focus();
    }
}

async function deleteEventFromList(date, eventId) {
    if (!confirm('Are you sure you want to delete this event?')) return;
    
    try {
        const response = await fetch(`/api/calendar/events/${date}/${eventId}`, {
            method: 'DELETE'
        });
        
        if (response.ok && window.calendarInstance) {
            await window.calendarInstance.loadEvents();
        }
    } catch (error) {
        console.error('Error deleting event:', error);
    }
}

// Create global calendar instance
window.calendarInstance = new Calendar();
