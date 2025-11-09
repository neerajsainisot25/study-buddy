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
            const response = await fetch('/api/profile');
            if (!response.ok) {
                console.error('Failed to load profile');
                return;
            }
            const data = await response.json();
            
            this.userData = {
                name: data.name || 'Student',
                email: data.email || '',
                grade: data.grade || 'Not Set',
                bio: data.bio || 'Welcome to StudyMate!',
                weekly_goal: data.weekly_goal || 20,
                days_active: data.days_active || 0,
                total_quizzes: data.total_quizzes || 0,
                study_hours: data.study_hours || 0,
                avg_score: data.avg_score || 0
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
            'profileGoal': this.userData.weekly_goal,
            'profileBio': this.userData.bio,
            'profileDaysActive': this.userData.days_active,
            'profileTotalQuizzes': this.userData.total_quizzes,
            'profileStudyHours': this.userData.study_hours
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
            const response = await fetch('/api/profile', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: name,
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

    deleteAccount() {
        alert('Account data is stored in session. Clear your browser data to reset.');
    }
}

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

window.profileInstance = new Profile();
