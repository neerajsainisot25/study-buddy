/**
 * Quiz Module
 * Handles quiz generation and submission
 */

class Quiz {
    constructor() {
        this.currentQuestions = [];
        this.userAnswers = [];
        this.setupSection = null;
        this.loadingSection = null;
        this.quizSection = null;
        this.resultsSection = null;
    }

    init() {
        this.setupSection = document.getElementById('quizSetup');
        this.loadingSection = document.getElementById('quizLoading');
        this.quizSection = document.getElementById('quizSection');
        this.resultsSection = document.getElementById('quizResults');
        
        // Show setup section initially
        this.showSetup();
    }

    async generate() {
        const topicInput = document.getElementById('topicInput');
        const numQuestionsInput = document.getElementById('numQuestions');
        
        if (!topicInput || !numQuestionsInput) return;

        const topic = topicInput.value.trim();
        const numQuestions = parseInt(numQuestionsInput.value) || 5;

        if (!topic) {
            alert('Please enter a topic for the quiz');
            return;
        }

        this.showLoading();

        try {
            const response = await fetch('/api/quiz/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    topic: topic,
                    num_questions: numQuestions
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.currentQuestions = data.questions;
                this.userAnswers = new Array(this.currentQuestions.length).fill(null);
                this.displayQuiz();
            } else {
                alert('Error: ' + (data.error || 'Failed to generate quiz'));
                this.showSetup();
            }
        } catch (error) {
            alert('Error generating quiz: ' + error.message);
            this.showSetup();
        }
    }

    showSetup() {
        this.hideAll();
        if (this.setupSection) {
            this.setupSection.classList.remove('hidden');
            this.setupSection.style.display = 'block';
        }
    }

    showLoading() {
        this.hideAll();
        if (this.loadingSection) {
            this.loadingSection.classList.remove('hidden');
            this.loadingSection.style.display = 'block';
        }
    }

    showQuiz() {
        this.hideAll();
        if (this.quizSection) {
            this.quizSection.classList.remove('hidden');
            this.quizSection.style.display = 'block';
        }
    }

    showResults() {
        this.hideAll();
        if (this.resultsSection) {
            this.resultsSection.classList.remove('hidden');
            this.resultsSection.style.display = 'block';
        }
    }

    hideAll() {
        if (this.setupSection) {
            this.setupSection.classList.add('hidden');
            this.setupSection.style.display = 'none';
        }
        if (this.loadingSection) {
            this.loadingSection.classList.add('hidden');
            this.loadingSection.style.display = 'none';
        }
        if (this.quizSection) {
            this.quizSection.classList.add('hidden');
            this.quizSection.style.display = 'none';
        }
        if (this.resultsSection) {
            this.resultsSection.classList.add('hidden');
            this.resultsSection.style.display = 'none';
        }
    }

    displayQuiz() {
        const container = document.getElementById('questionsContainer');
        if (!container) return;

        container.innerHTML = '';

        this.currentQuestions.forEach((question, index) => {
            const questionDiv = document.createElement('div');
            questionDiv.className = 'question-card';
            questionDiv.innerHTML = `
                <div class="question-number">Question ${index + 1} of ${this.currentQuestions.length}</div>
                <div class="question-text">${question.question}</div>
                <div class="options">
                    ${question.options.map((option, optIndex) => `
                        <label class="option ${this.userAnswers[index] === optIndex ? 'selected' : ''}">
                            <input type="radio" name="question${index}" value="${optIndex}" 
                                ${this.userAnswers[index] === optIndex ? 'checked' : ''}
                                onchange="selectQuizAnswer(${index}, ${optIndex})" />
                            <span>${option}</span>
                        </label>
                    `).join('')}
                </div>
            `;
            container.appendChild(questionDiv);
        });

        this.showQuiz();
    }

    selectAnswer(questionIndex, answerIndex) {
        this.userAnswers[questionIndex] = answerIndex;
        this.displayQuiz();
    }

    async submit() {
        const unanswered = this.userAnswers.filter(a => a === null).length;
        if (unanswered > 0 && !confirm(`You have ${unanswered} unanswered question(s). Submit anyway?`)) {
            return;
        }

        try {
            const response = await fetch('/api/quiz/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    questions: this.currentQuestions,
                    answers: this.userAnswers
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.displayResults(data);
            } else {
                alert('Error: ' + (data.error || 'Failed to submit'));
            }
        } catch (error) {
            alert('Error: ' + error.message);
        }
    }

    displayResults(data) {
        this.showResults();
        
        const score = Math.round(data.score);
        const scoreValue = document.getElementById('scoreValue');
        const scoreText = document.getElementById('scoreText');
        
        if (scoreValue) scoreValue.textContent = score + '%';
        if (scoreText) scoreText.textContent = `You got ${data.correct} out of ${data.total} questions correct!`;

        const container = document.getElementById('resultsContainer');
        if (!container) return;

        container.innerHTML = '';

        data.results.forEach((result, index) => {
            const resultDiv = document.createElement('div');
            resultDiv.className = `result-item ${result.is_correct ? 'correct' : 'incorrect'}`;
            
            const userAnswerText = result.user_answer !== null 
                ? result.options[result.user_answer] 
                : 'Not answered';
            const correctAnswerText = result.options[result.correct_answer];

            resultDiv.innerHTML = `
                <div class="result-question">Question ${index + 1}: ${result.question}</div>
                <div style="margin-top: 8px; font-size: 14px;">
                    <div style="color: ${result.is_correct ? '#4caf50' : '#f5576c'}; font-weight: 600;">
                        Your answer: ${userAnswerText} ${result.is_correct ? '✓' : '✗'}
                    </div>
                    ${!result.is_correct ? `<div style="color: #4caf50; font-weight: 600; margin-top: 5px;">Correct answer: ${correctAnswerText}</div>` : ''}
                </div>
            `;
            container.appendChild(resultDiv);
        });
    }

    reset() {
        this.currentQuestions = [];
        this.userAnswers = [];
        
        const topicInput = document.getElementById('topicInput');
        const numQuestionsInput = document.getElementById('numQuestions');
        
        if (topicInput) topicInput.value = '';
        if (numQuestionsInput) numQuestionsInput.value = '5';
        
        this.showSetup();
    }
}

// Export for use in other modules
window.Quiz = Quiz;

// Global functions for onclick handlers - use instance
window.generateQuiz = () => {
    if (window.quizInstance) {
        window.quizInstance.generate();
    }
};

window.submitQuiz = () => {
    if (window.quizInstance) {
        window.quizInstance.submit();
    }
};

window.resetQuiz = () => {
    if (window.quizInstance) {
        window.quizInstance.reset();
    }
};

window.selectQuizAnswer = (questionIndex, answerIndex) => {
    if (window.quizInstance) {
        window.quizInstance.selectAnswer(questionIndex, answerIndex);
    }
};

