"""Quiz routes with Supabase integration"""
from flask import Blueprint, request, jsonify
from app.services.llm_service import LLMService
from app.services.supabase_service import supabase_service
from app.middleware.auth import require_auth, optional_auth
import time

quiz_supabase_bp = Blueprint('quiz_supabase', __name__)

@quiz_supabase_bp.route('/generate', methods=['POST'])
def generate_quiz():
    """Generate quiz questions using LLM"""
    data = request.json or {}
    topic = data.get('topic', '').strip()
    num_questions = int(data.get('num_questions', 5))
    quiz_type = data.get('quiz_type', 'multiple_choice')
    difficulty = data.get('difficulty', 'intermediate')
    source_material = data.get('source_material', 'general')
    
    user_id = None  # No auth required
    
    if not topic:
        return jsonify({"error": "Topic is required"}), 400
    
    if num_questions < 1 or num_questions > 20:
        return jsonify({"error": "Number of questions must be between 1 and 20"}), 400
    
    try:
        # Build prompt
        question_type_instructions = {
            'multiple_choice': 'multiple choice questions with 4 options (A, B, C, D)',
            'true_false': 'true/false questions',
            'fill_blank': 'fill-in-the-blank questions with 4 multiple choice options',
            'short_answer': 'short answer questions (provide expected answer key points)'
        }
        
        difficulty_instructions = {
            'beginner': 'Use simple language and basic concepts suitable for beginners.',
            'intermediate': 'Use moderate complexity suitable for intermediate learners.',
            'advanced': 'Use advanced concepts and terminology suitable for experts.'
        }
        
        prompt = f"""Generate {num_questions} {question_type_instructions.get(quiz_type, 'multiple choice')} about: {topic}

Difficulty Level: {difficulty_instructions.get(difficulty, 'intermediate')}

Format each question as JSON with this structure:
{{
    "question": "Question text here",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct": 0,
    "explanation": "Brief explanation of why this answer is correct"
}}
where "correct" is the index (0-3) of the correct answer.

Return ONLY a JSON array of questions, no other text."""
        
        content = LLMService.call_llm([{"role": "user", "content": prompt}])
        questions = LLMService.extract_json(content, json_type='array')
        
        # Validate questions structure
        if not isinstance(questions, list):
            raise Exception("Invalid response format: expected array")
        
        # Add metadata to each question
        for q in questions:
            q['type'] = quiz_type
            q['difficulty'] = difficulty
            if 'explanation' not in q:
                q['explanation'] = "Correct answer explanation"
        
        # Store quiz in Supabase
        if supabase_service.is_available():
            quiz_data = {
                "user_id": user_id,
                "topic": topic,
                "difficulty": difficulty,
                "quiz_type": quiz_type,
                "num_questions": num_questions,
                "source_material": source_material,
                "questions": questions
            }
            
            response = supabase_service.client.table('quizzes').insert(quiz_data).execute()
            quiz_id = response.data[0]['id'] if response.data else None
        else:
            quiz_id = f"quiz_{int(time.time())}"
        
        return jsonify({
            "questions": questions,
            "quiz_id": quiz_id,
            "metadata": {
                "topic": topic,
                "num_questions": num_questions,
                "quiz_type": quiz_type,
                "difficulty": difficulty
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@quiz_supabase_bp.route('/submit', methods=['POST'])
def submit_quiz_answers():
    """Evaluate quiz answers (no auth required)"""
    data = request.json or {}
    answers = data.get('answers', [])
    questions = data.get('questions', [])
    quiz_id = data.get('quiz_id', '')
    time_taken = data.get('time_taken', 0)
    
    if not answers or not questions:
        return jsonify({"error": "Answers and questions are required"}), 400
    
    try:
        correct = 0
        total = len(questions)
        results = []
        
        for i, question in enumerate(questions):
            user_answer = answers[i] if i < len(answers) else None
            correct_answer = question.get('correct', -1)
            is_correct = user_answer == correct_answer
            
            if is_correct:
                correct += 1
            
            results.append({
                "question": question.get('question', ''),
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "options": question.get('options', []),
                "explanation": question.get('explanation', '')
            })
        
        score = (correct / total * 100) if total > 0 else 0
        
        # Get topic from quiz
        quiz_topic = data.get('topic', '')
        if not quiz_topic and quiz_id and supabase_service.is_available():
            try:
                quiz_response = supabase_service.client.table('quizzes').select('topic').eq('id', quiz_id).single().execute()
                if quiz_response.data:
                    quiz_topic = quiz_response.data.get('topic', '')
            except:
                pass
        
        # Store quiz attempt in Supabase (no user_id since no auth)
        if supabase_service.is_available():
            attempt_data = {
                "quiz_id": quiz_id if quiz_id else None,
                "topic": quiz_topic,
                "score": score,
                "correct": correct,
                "total": total,
                "time_taken": time_taken,
                "answers": results
            }
            
            # Skip saving without user_id - would violate database constraints
            # supabase_service.client.table('quiz_attempts').insert(attempt_data).execute()
        
        return jsonify({
            "score": score,
            "correct": correct,
            "total": total,
            "time_taken": time_taken,
            "results": results
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@quiz_supabase_bp.route('/history', methods=['GET'])
def get_quiz_history():
    """Get quiz history (no auth required - returns empty)"""
    try:
        if not supabase_service.is_available():
            return jsonify({"total_quizzes": 0, "total_attempts": 0, "average_score": 0, "recent_attempts": []})
        
        # No auth - return empty history
        quizzes = []
        attempts = []
        
        total_quizzes = 0
        total_attempts = 0
        attempts_data = []
        avg_score = 0
        
        return jsonify({
            "total_quizzes": total_quizzes,
            "total_attempts": total_attempts,
            "average_score": round(avg_score, 1),
            "recent_attempts": attempts_data[:10]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@quiz_supabase_bp.route('/list', methods=['GET'])
def get_quiz_list():
    """Get list of all quizzes (no auth required - returns empty)"""
    try:
        if not supabase_service.is_available():
            return jsonify({"quizzes": [], "count": 0})
        
        # No auth - return empty list
        quizzes = {"data": []}
        
        return jsonify({
            "quizzes": quizzes.data if quizzes.data else [],
            "count": len(quizzes.data) if quizzes.data else 0
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
