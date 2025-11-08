/**
 * Calendar Module
 * Handles calendar display and event management
 */

class Calendar {
    constructor() {
        this.currentDate = new Date();
        this.eventsList = null;
    }

    init() {
        this.eventsList = document.getElementById('eventsList');
        const calendarDateInput = document.getElementById('calendarDate');
        const eventDateInput = document.getElementById('eventDate');
        
        const today = new Date().toISOString().split('T')[0];
        if (calendarDateInput) calendarDateInput.value = today;
        if (eventDateInput) eventDateInput.value = today;
        
        this.loadCalendar();
    }

    async loadCalendar() {
        const dateInput = document.getElementById('calendarDate');
        if (!dateInput || !dateInput.value) return;
        
        this.currentDate = new Date(dateInput.value + 'T00:00:00');
        await this.renderCalendar();
        this.loadEvents(dateInput.value);
    }

    async renderCalendar() {
        const container = document.getElementById('calendarContainer');
        if (!container) return;

        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const daysInMonth = lastDay.getDate();
        const startingDayOfWeek = firstDay.getDay();

        const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 
                          'July', 'August', 'September', 'October', 'November', 'December'];
        const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

        // Get all events for the month to mark days
        const eventsMap = {};
        for (let day = 1; day <= daysInMonth; day++) {
            const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
            try {
                const response = await fetch(`/api/calendar/events?date=${dateStr}`);
                const data = await response.json();
                if (response.ok && data.events && data.events.length > 0) {
                    eventsMap[dateStr] = true;
                }
            } catch (e) {
                // Silently fail for individual day checks
            }
        }

        let html = `<h3 style="margin-bottom: 15px;">${monthNames[month]} ${year}</h3>`;
        html += '<div class="calendar-grid">';
        
        dayNames.forEach(day => {
            html += `<div class="calendar-day-header">${day}</div>`;
        });

        for (let i = 0; i < startingDayOfWeek; i++) {
            html += '<div class="calendar-day other-month"></div>';
        }

        const today = new Date();
        for (let day = 1; day <= daysInMonth; day++) {
            const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
            const isToday = year === today.getFullYear() && month === today.getMonth() && day === today.getDate();
            const hasEvents = eventsMap[dateStr] ? 'has-events' : '';
            html += `<div class="calendar-day ${isToday ? 'today' : ''} ${hasEvents}" onclick="Calendar.selectDate('${dateStr}')" style="position: relative;">${day}</div>`;
        }

        html += '</div>';
        container.innerHTML = html;
    }

    selectDate(dateStr) {
        const eventDateInput = document.getElementById('eventDate');
        if (eventDateInput) eventDateInput.value = dateStr;
        this.loadEvents(dateStr);
    }

    async loadEvents(date) {
        if (!this.eventsList) return;

        try {
            const response = await fetch(`/api/calendar/events?date=${date}`);
            const data = await response.json();
            if (response.ok) {
                this.displayEvents(data.events || []);
            }
        } catch (error) {
            console.error('Error loading events:', error);
            this.eventsList.innerHTML = '<p style="color: #666; text-align: center; padding: 20px;">Error loading events</p>';
        }
    }

    displayEvents(events) {
        if (!this.eventsList) return;

        if (events.length === 0) {
            this.eventsList.innerHTML = '<p style="color: #666; text-align: center; padding: 20px;">No events for this date</p>';
            return;
        }

        this.eventsList.innerHTML = '<h3 style="margin-bottom: 15px;">Events</h3>';
        events.forEach((event, index) => {
            const eventDiv = document.createElement('div');
            eventDiv.className = 'event-item';
            const date = document.getElementById('eventDate')?.value || '';
            eventDiv.innerHTML = `
                <div class="event-info">
                    <h4>${event.title}</h4>
                    <p>${event.description || 'No description'}</p>
                    ${event.time ? `<p style="color: #667eea; font-size: 12px;">⏰ ${event.time}</p>` : ''}
                </div>
                <div class="event-actions">
                    <button class="btn btn-danger btn-small" onclick="Calendar.deleteEvent('${date}', ${index})">Delete</button>
                </div>
            `;
            this.eventsList.appendChild(eventDiv);
        });
    }

    async addEvent() {
        const titleInput = document.getElementById('eventTitle');
        const descriptionInput = document.getElementById('eventDescription');
        const dateInput = document.getElementById('eventDate');
        const timeInput = document.getElementById('eventTime');

        if (!titleInput || !dateInput) return;

        const title = titleInput.value.trim();
        const description = descriptionInput?.value.trim() || '';
        const date = dateInput.value;
        const time = timeInput?.value || '';

        if (!title || !date) {
            alert('Title and date are required');
            return;
        }

        try {
            const response = await fetch('/api/calendar/events', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, description, date, time })
            });

            const data = await response.json();
            if (response.ok) {
                if (titleInput) titleInput.value = '';
                if (descriptionInput) descriptionInput.value = '';
                if (timeInput) timeInput.value = '';
                this.loadEvents(date);
                await this.renderCalendar(); // Refresh calendar to show event indicator
            } else {
                alert('Error: ' + (data.error || 'Failed to add event'));
            }
        } catch (error) {
            alert('Error: ' + error.message);
        }
    }

    async deleteEvent(date, eventId) {
        if (!confirm('Delete this event?')) return;

        try {
            const response = await fetch(`/api/calendar/events/${date}/${eventId}`, {
                method: 'DELETE'
            });
            if (response.ok) {
                this.loadEvents(date);
                await this.renderCalendar(); // Refresh calendar
            }
        } catch (error) {
            alert('Error deleting event');
        }
    }

    async suggestEvent() {
        const descriptionInput = document.getElementById('eventDescription');
        if (!descriptionInput) return;

        const description = descriptionInput.value.trim();
        if (!description) {
            alert('Please enter a description first');
            return;
        }

        try {
            const response = await fetch('/api/calendar/suggest', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ description })
            });

            const data = await response.json();
            if (response.ok && data.suggestion) {
                const titleInput = document.getElementById('eventTitle');
                const timeInput = document.getElementById('eventTime');
                
                if (titleInput) titleInput.value = data.suggestion.title || '';
                if (descriptionInput) descriptionInput.value = data.suggestion.description || description;
                if (timeInput) timeInput.value = data.suggestion.time || '';
            }
        } catch (error) {
            alert('Error getting suggestion');
        }
    }
}

// Export for use in other modules
window.Calendar = Calendar;

// Global functions for onclick handlers
window.loadCalendar = () => Calendar.loadCalendar();
window.addEvent = () => Calendar.addEvent();
window.suggestEvent = () => Calendar.suggestEvent();

