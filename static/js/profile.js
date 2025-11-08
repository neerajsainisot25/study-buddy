// Profile functionality
class Profile {
    constructor() {
        this.userData = {};
    }

    init() {
        this.loadProfile();
        this.setupEventListeners();
    }

    setupEventListeners() {
        const darkModeToggle = document.getElementById('darkModeToggle');
        if (darkModeToggle) {
            darkModeToggle.addEventListener('change', (e) => {
                this.toggleDarkMode(e.target.checked);
            });
        }
    }

    async loadProfile() {
        try {
            const response = await fetch('/api/auth/profile');
            if (!response.ok) {
                return;
            }
            const data = await response.json();
            
            this.userData = {
                name: data.full_name || data.email,
                email: data.email,
                grade: data.grade || 'Not Set',
                goal: data.weekly_goal || 20,
                bio: data.bio || 'No bio yet',
                daysActive: data.days_active || 0,
                totalQuizzes: data.total_quizzes || 0,
                studyHours: data.study_hours || 0
            };
            
            this.updateUI();
        } catch (error) {
            console.error('Error loading profile:', error);
        }
    }

    updateUI() {
        const fields = {
            'profileName': this.userData.name,
            'profileEmail': this.userData.email,
            'profileGoal': this.userData.goal,
            'profileBio': this.userData.bio,
            'profileDaysActive': this.userData.daysActive,
            'profileTotalQuizzes': this.userData.totalQuizzes,
            'profileStudyHours': this.userData.studyHours
        };

        Object.entries(fields).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                    element.value = value;
                } else {
                    element.textContent = value;
                }
            }
        });
    }

    async saveProfile() {
        const name = document.getElementById('profileName')?.value;
        const grade = document.getElementById('profileGrade')?.value;
        const goal = document.getElementById('profileGoal')?.value;
        const bio = document.getElementById('profileBio')?.value;

        try {
            const response = await fetch('/api/auth/profile', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    full_name: name,
                    grade: grade,
                    weekly_goal: parseInt(goal),
                    bio: bio
                })
            });

            if (response.ok) {
                alert('Profile saved successfully!');
                this.loadProfile();
            } else {
                alert('Error saving profile');
            }
        } catch (error) {
            console.error('Error saving profile:', error);
            alert('Error saving profile');
        }
    }

    toggleDarkMode(enabled) {
        if (enabled) {
            document.body.classList.add('dark-mode');
        } else {
            document.body.classList.remove('dark-mode');
        }
    }

    async deleteAccount() {
        if (!confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
            return;
        }

        if (!confirm('This will permanently delete all your data. Are you absolutely sure?')) {
            return;
        }

        try {
            const response = await fetch('/api/auth/profile', {
                method: 'DELETE'
            });

            if (response.ok) {
                alert('Account deleted successfully. You will be logged out.');
                window.authManager.logout();
            } else {
                alert('Error deleting account');
            }
        } catch (error) {
            console.error('Error deleting account:', error);
            alert('Error deleting account');
        }
    }
}

// Global functions for onclick handlers
function saveProfile() {
    if (window.profileInstance) {
        window.profileInstance.saveProfile();
    }
}

function deleteAccount() {
    if (window.profileInstance) {
        window.profileInstance.deleteAccount();
    }
}

// Global profile instance
window.profileInstance = new Profile();
