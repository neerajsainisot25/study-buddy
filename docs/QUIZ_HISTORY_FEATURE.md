# Quiz History Feature

## Overview
Added a quiz history sidebar to the quiz page that displays past quiz attempts with statistics and details.

## Features Added

### 1. Two-Column Layout
- **Left Column**: Quiz creation form (existing functionality)
- **Right Column**: Quiz history sidebar (new)

### 2. Quiz History Sidebar
The sidebar includes:

#### Statistics Summary
- **Total Quizzes**: Count of all quiz attempts
- **Average Score**: Average score across all attempts

#### Recent Quiz List
Each quiz attempt shows:
- Quiz topic/title
- Date and time taken
- Score percentage (color-coded)
- Number of correct answers
- Time taken to complete
- Color-coded border (green for high scores, yellow for medium, red for low)

### 3. Backend API
New endpoint: `GET /api/quiz/history`
- Returns quiz statistics and recent attempts
- Includes total quizzes, average score, and last 10 attempts

### 4. Responsive Design
- Desktop (>1200px): Full two-column layout with 400px history sidebar
- Tablet (968px-1200px): Narrower 350px history sidebar
- Mobile (<968px): Stacked layout with history below quiz form

## Technical Implementation

### Files Modified
1. **templates/pages/quiz.html**
   - Added grid layout wrapper
   - Added quiz history sidebar HTML

2. **static/js/quiz.js**
   - Added `loadHistory()` method to fetch history data
   - Added `displayHistory()` method to render history items
   - Integrated history refresh after quiz submission

3. **app/routes/quiz.py**
   - Added `/history` endpoint
   - Enhanced quiz attempt storage with topic information

4. **static/css/style.css**
   - Added responsive styles for history column
   - Added custom scrollbar styling

## Usage
1. Navigate to the Quiz page
2. Create and complete quizzes as usual
3. View your quiz history in the right sidebar
4. History updates automatically after each quiz completion
5. Click on history items to see details (hover effect)

## Color Coding
- **Green** (≥80%): Excellent performance
- **Yellow** (60-79%): Good performance
- **Red** (<60%): Needs improvement
