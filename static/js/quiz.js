/**
 * Quiz Module
 * Handles quiz generation, preview, taking, and results
 */

class Quiz {
    constructor() {
        this.currentQuestions = [];
        this.userAnswers = [];
        this.currentQuestionIndex = 0;
        this.quizId = null;
        this.quizMetadata = null;
        this.startTime = null;
        this.timerInterval = null;
        this.topicTags = [];
        this.setupSection = null;
        this.loadingSection = null;
        this.previewSection = null;
        this.quizSection = null;
        this.resultsSection = null;
    }

    init() {
        this.setupSection = document.getElementById('quizSetup');
        this.loadingSection = document.getElementById('quizLoading');
        this.previewSection = document.getElementById('quizPreview');
        this.quizSection = document.getElementById('quizSection');
        this.resultsSection = document.getElementById('quizResults');
        
        this.showSetup();
        this.loadHistory();
    }

    async generate() {
        const topicInput = document.getElementById('topicInput');
        const numQuestionsInput = document.getElementById('numQuestions');
        const quizType = document.getElementById('quizType');
        const difficulty = document.getElementById('difficulty');
        const sourceMaterial = document.getElementById('sourceMaterial');
        const timeLimit = document.getElementById('timeLimit');
        
        if (!topicInput || !numQuestionsInput) return;

        const topic = topicInput.value.trim();
        const numQuestions = parseInt(numQuestionsInput.value) || 5;
        const quizTypeValue = quizType ? quizType.value : 'multiple_choice';
        const difficultyValue = difficulty ? difficulty.value : 'intermediate';
        const sourceMaterialValue = sourceMaterial ? sourceMaterial.value : 'general';
        const timeLimitValue = timeLimit ? parseInt(timeLimit.value) : null;

        // Combine topic and tags
        const allTopics = [topic, ...this.topicTags].filter(t => t && t.trim());

        if (allTopics.length === 0) {
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
                    topics: this.topicTags,
                    num_questions: numQuestions,
                    quiz_type: quizTypeValue,
                    difficulty: difficultyValue,
                    source_material: sourceMaterialValue,
                    time_limit: timeLimitValue
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.currentQuestions = data.questions;
                this.quizId = data.quiz_id;
                this.quizMetadata = data.metadata;
                this.userAnswers = new Array(this.currentQuestions.length).fill(null);
                this.currentQuestionIndex = 0;
                this.showPreview();
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

    showPreview() {
        this.hideAll();
        if (this.previewSection) {
            this.previewSection.classList.remove('hidden');
            this.previewSection.style.display = 'block';
            this.displayPreview();
        }
    }

    showQuiz() {
        this.hideAll();
        if (this.quizSection) {
            this.quizSection.classList.remove('hidden');
            this.quizSection.style.display = 'block';
        }
        this.startTimer();
        this.updateNavigation();
    }

    showResults() {
        this.hideAll();
        if (this.resultsSection) {
            this.resultsSection.classList.remove('hidden');
            this.resultsSection.style.display = 'block';
        }
        this.stopTimer();
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
        if (this.previewSection) {
            this.previewSection.classList.add('hidden');
            this.previewSection.style.display = 'none';
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

    displayPreview() {
        const container = document.getElementById('previewContainer');
        if (!container) return;

        container.innerHTML = '';

        this.currentQuestions.forEach((question, index) => {
            const previewDiv = document.createElement('div');
            previewDiv.className = 'preview-question';
            previewDiv.innerHTML = `
                <div class="preview-question-number">Question ${index + 1}</div>
                <div class="preview-question-text">${this.escapeHtml(question.question)}</div>
                <div class="preview-options">
                    ${question.options.map((opt, i) => 
                        `<div>${String.fromCharCode(65 + i)}. ${this.escapeHtml(opt)}</div>`
                    ).join('')}
                </div>
            `;
            container.appendChild(previewDiv);
        });
    }

    displayQuiz() {
        const container = document.getElementById('questionsContainer');
        if (!container) return;

        container.innerHTML = '';

        // Show only current question
        const question = this.currentQuestions[this.currentQuestionIndex];
        if (!question) return;

        const questionDiv = document.createElement('div');
        questionDiv.className = 'question-card';
        
        const quizType = question.type || 'multiple_choice';
        
        questionDiv.innerHTML = `
            <div class="question-number">Question ${this.currentQuestionIndex + 1} of ${this.currentQuestions.length}</div>
            <div class="question-text">${this.escapeHtml(question.question)}</div>
            <div class="options">
                ${this.renderOptions(question, quizType)}
            </div>
        `;
        
        container.innerHTML = '';
        container.appendChild(questionDiv);
        
        this.updateProgress();
        this.updateNavigation();
    }

    renderOptions(question, quizType) {
        if (quizType === 'true_false') {
            return `
                <label class="option ${this.userAnswers[this.currentQuestionIndex] === 0 ? 'selected' : ''}">
                    <input type="radio" name="question${this.currentQuestionIndex}" value="0" 
                        ${this.userAnswers[this.currentQuestionIndex] === 0 ? 'checked' : ''}
                        onchange="selectQuizAnswer(${this.currentQuestionIndex}, 0)" />
                    <span>True</span>
                </label>
                <label class="option ${this.userAnswers[this.currentQuestionIndex] === 1 ? 'selected' : ''}">
                    <input type="radio" name="question${this.currentQuestionIndex}" value="1" 
                        ${this.userAnswers[this.currentQuestionIndex] === 1 ? 'checked' : ''}
                        onchange="selectQuizAnswer(${this.currentQuestionIndex}, 1)" />
                    <span>False</span>
                </label>
            `;
        }
        
        return question.options.map((option, optIndex) => `
            <label class="option ${this.userAnswers[this.currentQuestionIndex] === optIndex ? 'selected' : ''}">
                <input type="radio" name="question${this.currentQuestionIndex}" value="${optIndex}" 
                    ${this.userAnswers[this.currentQuestionIndex] === optIndex ? 'checked' : ''}
                    onchange="selectQuizAnswer(${this.currentQuestionIndex}, ${optIndex})" />
                <span>${this.escapeHtml(option)}</span>
            </label>
        `).join('');
    }

    selectAnswer(questionIndex, answerIndex) {
        this.userAnswers[questionIndex] = answerIndex;
        this.updateProgress();
        this.updateNavigation();
    }

    navigateQuestion(direction) {
        const newIndex = this.currentQuestionIndex + direction;
        if (newIndex >= 0 && newIndex < this.currentQuestions.length) {
            this.currentQuestionIndex = newIndex;
            this.displayQuiz();
        }
    }

    updateProgress() {
        const progressEl = document.getElementById('quizProgress');
        const progressBar = document.getElementById('progressBar');
        const answeredCount = document.getElementById('answeredCount');
        
        if (progressEl) {
            progressEl.textContent = `Question ${this.currentQuestionIndex + 1} of ${this.currentQuestions.length}`;
        }
        
        if (progressBar) {
            const progress = ((this.currentQuestionIndex + 1) / this.currentQuestions.length) * 100;
            progressBar.style.width = progress + '%';
        }
        
        if (answeredCount) {
            const answered = this.userAnswers.filter(a => a !== null).length;
            answeredCount.textContent = `${answered} of ${this.currentQuestions.length} answered`;
        }
    }

    updateNavigation() {
        const prevBtn = document.getElementById('prevQuestion');
        const nextBtn = document.getElementById('nextQuestion');
        const submitBtn = document.getElementById('submitQuizBtn');
        
        if (prevBtn) {
            prevBtn.disabled = this.currentQuestionIndex === 0;
        }
        
        if (nextBtn) {
            nextBtn.disabled = this.currentQuestionIndex === this.currentQuestions.length - 1;
        }
        
        if (submitBtn) {
            submitBtn.style.display = this.currentQuestionIndex === this.currentQuestions.length - 1 ? 'inline-block' : 'none';
        }
    }

    startTimer() {
        this.startTime = Date.now();
        this.timerInterval = setInterval(() => {
            const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;
            const timerEl = document.getElementById('quizTimer');
            if (timerEl) {
                timerEl.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
            }
        }, 1000);
    }

    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    }

    getTimeTaken() {
        if (this.startTime) {
            return Math.floor((Date.now() - this.startTime) / 1000);
        }
        return 0;
    }

    async submit() {
        const unanswered = this.userAnswers.filter(a => a === null).length;
        if (unanswered > 0 && !confirm(`You have ${unanswered} unanswered question(s). Submit anyway?`)) {
            return;
        }

        const timeTaken = this.getTimeTaken();

        try {
            const response = await fetch('/api/quiz/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    questions: this.currentQuestions,
                    answers: this.userAnswers,
                    quiz_id: this.quizId,
                    time_taken: timeTaken
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.displayResults(data);
                // Refresh quiz history
                this.loadHistory();
                // Refresh dashboard stats
                if (typeof loadDashboardStats === 'function') {
                    loadDashboardStats();
                }
                // Refresh analytics if active
                if (typeof Analytics !== 'undefined' && window.analyticsInstance && window.analyticsInstance.isActive) {
                    window.analyticsInstance.loadAnalytics();
                }
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
        const timeTaken = document.getElementById('quizTimeTaken');
        
        if (scoreValue) scoreValue.textContent = score + '%';
        if (scoreText) scoreText.textContent = `You got ${data.correct} out of ${data.total} questions correct!`;
        
        const minutes = Math.floor(data.time_taken / 60);
        const seconds = data.time_taken % 60;
        if (timeTaken) {
            timeTaken.textContent = `Time taken: ${minutes}m ${seconds}s`;
        }

        const container = document.getElementById('resultsContainer');
        if (!container) return;

        container.innerHTML = '';

        data.results.forEach((result, index) => {
            const resultDiv = document.createElement('div');
            resultDiv.className = `result-item ${result.is_correct ? 'correct' : 'incorrect'}`;
            resultDiv.style.cssText = 'padding: 16px; margin-bottom: 16px; border-radius: 8px; border-left: 4px solid;';
            resultDiv.style.borderLeftColor = result.is_correct ? 'var(--success)' : 'var(--error)';
            resultDiv.style.background = result.is_correct ? 'rgba(16, 185, 129, 0.05)' : 'rgba(239, 68, 68, 0.05)';
            
            const userAnswerText = result.user_answer !== null 
                ? result.options[result.user_answer] 
                : 'Not answered';
            const correctAnswerText = result.options[result.correct_answer];

            resultDiv.innerHTML = `
                <div style="font-weight: 600; margin-bottom: 8px; color: var(--text);">
                    Question ${index + 1}: ${this.escapeHtml(result.question)}
                </div>
                <div style="margin-top: 12px; font-size: 14px;">
                    <div style="color: ${result.is_correct ? 'var(--success)' : 'var(--error)'}; font-weight: 600; margin-bottom: 6px;">
                        Your answer: ${this.escapeHtml(userAnswerText)} ${result.is_correct ? '✓' : '✗'}
                    </div>
                    ${!result.is_correct ? `
                        <div style="color: var(--success); font-weight: 600; margin-bottom: 8px;">
                            Correct answer: ${this.escapeHtml(correctAnswerText)}
                        </div>
                    ` : ''}
                    ${result.explanation ? `
                        <div style="color: var(--text-secondary); font-size: 13px; margin-top: 8px; padding: 12px; background: var(--bg-secondary); border-radius: 6px; border-left: 3px solid var(--primary);">
                            <strong>Explanation:</strong> ${this.escapeHtml(result.explanation)}
                        </div>
                    ` : ''}
                </div>
            `;
            container.appendChild(resultDiv);
        });
    }

    reset() {
        this.currentQuestions = [];
        this.userAnswers = [];
        this.currentQuestionIndex = 0;
        this.quizId = null;
        this.quizMetadata = null;
        this.topicTags = [];
        this.stopTimer();
        
        const topicInput = document.getElementById('topicInput');
        const numQuestionsInput = document.getElementById('numQuestions');
        const topicTagsContainer = document.getElementById('topicTags');
        
        if (topicInput) topicInput.value = '';
        if (numQuestionsInput) numQuestionsInput.value = '5';
        if (topicTagsContainer) topicTagsContainer.innerHTML = '';
        
        this.showSetup();
    }

    retake() {
        this.userAnswers = new Array(this.currentQuestions.length).fill(null);
        this.currentQuestionIndex = 0;
        this.showQuiz();
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    async loadHistory() {
        try {
            const response = await fetch('/api/quiz/history');
            if (!response.ok) {
                return;
            }
            const data = await response.json();
            this.displayHistory(data);
        } catch (error) {
            console.error('Error loading quiz history:', error);
        }
    }

    displayHistory(data) {
        // Update stats
        const totalQuizzesEl = document.getElementById('totalQuizzes');
        const avgScoreEl = document.getElementById('avgScore');
        
        if (totalQuizzesEl) {
            totalQuizzesEl.textContent = data.total_attempts || 0;
        }
        if (avgScoreEl) {
            avgScoreEl.textContent = (data.average_score || 0).toFixed(1) + '%';
        }

        // Display history list
        const historyList = document.getElementById('historyList');
        if (!historyList) return;

        if (!data.recent_attempts || data.recent_attempts.length === 0) {
            historyList.innerHTML = `
                <div style="text-align: center; padding: 40px 20px; color: var(--text-secondary); font-size: 14px;">
                    <svg style="width: 48px; height: 48px; margin: 0 auto 12px; opacity: 0.3;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                    <div>No quiz history yet</div>
                    <div style="font-size: 12px; margin-top: 4px;">Complete a quiz to see it here</div>
                </div>
            `;
            return;
        }

        historyList.innerHTML = '';

        data.recent_attempts.forEach(attempt => {
            const date = new Date(attempt.timestamp * 1000);
            const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            const timeStr = date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
            
            const score = Math.round(attempt.score);
            const scoreColor = score >= 80 ? 'var(--success)' : score >= 60 ? 'var(--warning)' : 'var(--error)';
            
            const minutes = Math.floor(attempt.time_taken / 60);
            const seconds = attempt.time_taken % 60;
            const timeDisplay = minutes > 0 ? `${minutes}m ${seconds}s` : `${seconds}s`;

            const historyItem = document.createElement('div');
            historyItem.style.cssText = 'padding: 12px; background: var(--bg-secondary); border-radius: 8px; border-left: 3px solid ' + scoreColor + '; cursor: pointer; transition: all 0.2s;';
            historyItem.onmouseenter = function() { this.style.background = 'var(--bg-hover)'; };
            historyItem.onmouseleave = function() { this.style.background = 'var(--bg-secondary)'; };
            
            historyItem.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                    <div style="flex: 1;">
                        <div style="font-weight: 600; font-size: 14px; color: var(--text); margin-bottom: 4px;">
                            ${this.escapeHtml(attempt.topic || 'Quiz')}
                        </div>
                        <div style="font-size: 11px; color: var(--text-secondary);">
                            ${dateStr} at ${timeStr}
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 20px; font-weight: 700; color: ${scoreColor};">
                            ${score}%
                        </div>
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 12px; color: var(--text-secondary);">
                    <span>${attempt.correct}/${attempt.total} correct</span>
                    <span>⏱️ ${timeDisplay}</span>
                </div>
            `;
            
            historyList.appendChild(historyItem);
        });
    }
}

// Export for use in other modules
window.Quiz = Quiz;

// Global functions for onclick handlers
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

window.retakeQuiz = () => {
    if (window.quizInstance) {
        window.quizInstance.retake();
    }
};

window.selectQuizAnswer = (questionIndex, answerIndex) => {
    if (window.quizInstance) {
        window.quizInstance.selectAnswer(questionIndex, answerIndex);
    }
};

window.navigateQuestion = (direction) => {
    if (window.quizInstance) {
        window.quizInstance.navigateQuestion(direction);
    }
};

window.startQuiz = () => {
    if (window.quizInstance) {
        window.quizInstance.showQuiz();
        window.quizInstance.displayQuiz();
    }
};

window.regenerateQuiz = () => {
    if (window.quizInstance) {
        window.quizInstance.generate();
    }
};

window.addTopicTag = () => {
    const topicInput = document.getElementById('topicInput');
    const topicTagsContainer = document.getElementById('topicTags');
    
    if (!topicInput || !topicTagsContainer) return;
    
    const topic = topicInput.value.trim();
    if (!topic) return;
    
    if (window.quizInstance && !window.quizInstance.topicTags.includes(topic)) {
        window.quizInstance.topicTags.push(topic);
        
        const tagDiv = document.createElement('div');
        tagDiv.className = 'topic-tag';
        tagDiv.innerHTML = `
            <span>${escapeHtml(topic)}</span>
            <span class="topic-tag-remove" onclick="removeTopicTag('${escapeHtml(topic)}')">×</span>
        `;
        topicTagsContainer.appendChild(tagDiv);
        
        topicInput.value = '';
    }
};

window.removeTopicTag = (tag) => {
    if (window.quizInstance) {
        window.quizInstance.topicTags = window.quizInstance.topicTags.filter(t => t !== tag);
        const topicTagsContainer = document.getElementById('topicTags');
        if (topicTagsContainer) {
            topicTagsContainer.innerHTML = '';
            window.quizInstance.topicTags.forEach(t => {
                const tagDiv = document.createElement('div');
                tagDiv.className = 'topic-tag';
                tagDiv.innerHTML = `
                    <span>${escapeHtml(t)}</span>
                    <span class="topic-tag-remove" onclick="removeTopicTag('${escapeHtml(t)}')">×</span>
                `;
                topicTagsContainer.appendChild(tagDiv);
            });
        }
    }
};

window.incrementQuestions = () => {
    const numQuestionsInput = document.getElementById('numQuestions');
    if (numQuestionsInput) {
        const current = parseInt(numQuestionsInput.value) || 5;
        if (current < 20) {
            numQuestionsInput.value = current + 1;
        }
    }
};

window.decrementQuestions = () => {
    const numQuestionsInput = document.getElementById('numQuestions');
    if (numQuestionsInput) {
        const current = parseInt(numQuestionsInput.value) || 5;
        if (current > 1) {
            numQuestionsInput.value = current - 1;
        }
    }
};

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Global selection functions for quiz options
window.selectQuizType = (type, element) => {
    // Remove active class from all options
    document.querySelectorAll('.quiz-type-option').forEach(opt => {
        opt.classList.remove('active');
    });
    
    // Add active class to selected option
    if (element) {
        element.classList.add('active');
    }
    
    // Store selection (you can use a hidden input or data attribute)
    const quizTypeInput = document.getElementById('quizType');
    if (quizTypeInput) {
        quizTypeInput.value = type;
    } else {
        // Create hidden input if it doesn't exist
        const input = document.createElement('input');
        input.type = 'hidden';
        input.id = 'quizType';
        input.value = type;
        document.getElementById('quizSetup').appendChild(input);
    }
};

window.selectDifficulty = (difficulty, element) => {
    // Remove active class from all options
    document.querySelectorAll('.difficulty-option').forEach(opt => {
        opt.classList.remove('active');
    });
    
    // Add active class to selected option
    if (element) {
        element.classList.add('active');
    }
    
    // Store selection
    const difficultyInput = document.getElementById('difficulty');
    if (difficultyInput) {
        difficultyInput.value = difficulty;
    } else {
        // Create hidden input if it doesn't exist
        const input = document.createElement('input');
        input.type = 'hidden';
        input.id = 'difficulty';
        input.value = difficulty;
        document.getElementById('quizSetup').appendChild(input);
    }
};

window.selectSource = (source, element) => {
    // Remove active class from all options
    document.querySelectorAll('.source-tag').forEach(opt => {
        opt.classList.remove('active');
    });
    
    // Add active class to selected option
    if (element) {
        element.classList.add('active');
    }
    
    // Store selection
    const sourceInput = document.getElementById('sourceMaterial');
    if (sourceInput) {
        sourceInput.value = source;
    } else {
        // Create hidden input if it doesn't exist
        const input = document.createElement('input');
        input.type = 'hidden';
        input.id = 'sourceMaterial';
        input.value = source;
        document.getElementById('quizSetup').appendChild(input);
    }
};

window.addTopicTag = () => {
    const topicInput = document.getElementById('topicInput');
    const topicTagsContainer = document.getElementById('topicTags');
    
    if (!topicInput || !topicTagsContainer) return;
    
    const topic = topicInput.value.trim();
    if (!topic) return;
    
    // Add to quiz instance if available
    if (window.quizInstance && window.quizInstance.topicTags) {
        if (!window.quizInstance.topicTags.includes(topic)) {
            window.quizInstance.topicTags.push(topic);
        }
    }
    
    // Create tag element
    const tag = document.createElement('div');
    tag.className = 'topic-tag';
    tag.innerHTML = `
        ${escapeHtml(topic)}
        <span class="topic-tag-remove" onclick="removeTopicTag('${escapeHtml(topic)}', this.parentElement)">×</span>
    `;
    
    topicTagsContainer.appendChild(tag);
    topicInput.value = '';
};

window.removeTopicTag = (topic, element) => {
    // Remove from quiz instance
    if (window.quizInstance && window.quizInstance.topicTags) {
        const index = window.quizInstance.topicTags.indexOf(topic);
        if (index > -1) {
            window.quizInstance.topicTags.splice(index, 1);
        }
    }
    
    // Remove element
    if (element && element.parentElement) {
        element.parentElement.removeChild(element);
    }
};

// Initialize default selections on page load
document.addEventListener('DOMContentLoaded', () => {
    // Set default quiz type
    const defaultQuizType = document.querySelector('.quiz-type-option.active');
    if (defaultQuizType) {
        const type = defaultQuizType.getAttribute('data-type');
        if (type) {
            selectQuizType(type, defaultQuizType);
        }
    }
    
    // Set default difficulty
    const defaultDifficulty = document.querySelector('.difficulty-option.active');
    if (defaultDifficulty) {
        const difficulty = defaultDifficulty.getAttribute('data-difficulty');
        if (difficulty) {
            selectDifficulty(difficulty, defaultDifficulty);
        }
    }
    
    // Set default source
    const defaultSource = document.querySelector('.source-tag.active');
    if (defaultSource) {
        const source = defaultSource.getAttribute('data-source');
        if (source) {
            selectSource(source, defaultSource);
        }
    }
});
