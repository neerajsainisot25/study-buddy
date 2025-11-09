class Profile {
    constructor() {
        this.userData = {
            name: 'Student',
            email: 'student@studymate.app',
            grade: 'Not Set',
            goal: 20,
            bio: 'No bio yet',
            daysActive: 0,
            totalQuizzes: 0,
            studyHours: 0
        };
    }

    init() {
        this.updateUI();
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

    saveProfile() {
        const name = document.getElementById('profileName')?.value;
        const grade = document.getElementById('profileGrade')?.value;
        const goal = document.getElementById('profileGoal')?.value;
        const bio = document.getElementById('profileBio')?.value;

        this.userData = {
            ...this.userData,
            name: name || this.userData.name,
            grade: grade || this.userData.grade,
            goal: parseInt(goal) || this.userData.goal,
            bio: bio || this.userData.bio
        };

        alert('Profile saved locally!');
        this.updateUI();
    }

    toggleDarkMode(enabled) {
        if (enabled) {
            document.body.classList.add('dark-mode');
        } else {
            document.body.classList.remove('dark-mode');
        }
    }

    deleteAccount() {
        alert('This is a demo version. Account deletion is not available.');
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
