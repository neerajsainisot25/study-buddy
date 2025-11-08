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
        // Load profile data from API
        try {
            // For now, use default data
            this.userData = {
                name: 'Alex Johnson',
                email: 'alex.johnson@example.com',
                grade: '11th Grade',
                goal: 20,
                bio: 'Passionate about learning and achieving academic excellence.',
                daysActive: 45,
                totalQuizzes: 24,
                studyHours: 42
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
        const email = document.getElementById('profileEmail')?.value;
        const grade = document.getElementById('profileGrade')?.value;
        const goal = document.getElementById('profileGoal')?.value;
        const bio = document.getElementById('profileBio')?.value;

        try {
            // Save to API
            console.log('Saving profile:', { name, email, grade, goal, bio });
            alert('Profile saved successfully!');
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
            // Call delete API
            console.log('Deleting account...');
            alert('Account deletion requested. You will be logged out.');
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
