"""Quiz routes blueprint"""
from flask import Blueprint, request, jsonify, session as flask_session
from app.services.llm_service import LLMService
from app.services.storage import storage
from app.services.langgraph_service import rag_service
from app.services.web_search import WebSearchService
from app.services.database import db_service, Quiz, QuizAttempt
from sqlalchemy.exc import SQLAlchemyError
import time
import json
import uuid
import logging

logger = logging.getLogger(__name__)

quiz_bp = Blueprint('quiz', __name__)

def get_session_id():
    """Get or create session ID"""
    if 'session_id' not in flask_session:
        flask_session['session_id'] = str(uuid.uuid4())
    return flask_session['session_id']

@quiz_bp.route('/generate', methods=['POST'])
def generate_quiz():
    """Generate quiz questions using LLM with enhanced options"""
    data = request.json or {}
    topic = data.get('topic', '').strip()
    topics = data.get('topics', [])  # Multi-topic support
    num_questions = int(data.get('num_questions', 5))
    quiz_type = data.get('quiz_type', 'multiple_choice')  # multiple_choice, true_false, fill_blank, short_answer
    difficulty = data.get('difficulty', 'intermediate')  # beginner, intermediate, advanced
    source_material = data.get('source_material', 'general')  # general, knowledge_base, web_search

    # Combine topic and topics
    if topics and isinstance(topics, list):
        topic_str = ', '.join([topic] + topics) if topic else ', '.join(topics)
    else:
        topic_str = topic

    if not topic_str:
        return jsonify({"error": "Topic is required"}), 400

    if num_questions < 1 or num_questions > 20:
        return jsonify({"error": "Number of questions must be between 1 and 20"}), 400

    try:
        # Build context based on source material
        context = ""
        if source_material == 'knowledge_base' and rag_service and rag_service.is_ready():
            # Search knowledge base for relevant content
            kb_docs = rag_service.search(topic_str, k=3)
            if kb_docs:
                context = "Use the following information from the knowledge base:\n"
                for i, doc in enumerate(kb_docs, 1):
                    context += f"{i}. {doc['content'][:300]}...\n\n"
        elif source_material == 'web_search':
            # Perform web search
            search_results = WebSearchService.search(topic_str, max_results=3)
            if search_results:
                context = "Use the following information from web search:\n"
                for i, result in enumerate(search_results, 1):
                    context += f"{i}. {result['title']}: {result['snippet']}\n\n"

        # Build prompt based on quiz type
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

        prompt = f"""Generate {num_questions} {question_type_instructions.get(quiz_type, 'multiple choice')} about: {topic_str}

Difficulty Level: {difficulty_instructions.get(difficulty, 'intermediate')}

{context if context else ''}

Format each question as JSON with this structure:
{{
    "question": "Question text here",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct": 0,
    "explanation": "Brief explanation of why this answer is correct"
}}
where "correct" is the index (0-3) of the correct answer.

For true/false questions, use options: ["True", "False"]
For fill-in-the-blank, provide 4 multiple choice options.
For short answer, provide 4 key points that should be in the answer.

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
        
        # Store quiz metadata
        session_id = get_session_id()
        quiz_id = f"quiz_{int(time.time())}"
        
        # Store in database if available
        if db_service.is_available():
            db_session = None
            try:
                db_session = db_service.get_session()
                new_quiz = Quiz(
                    quiz_id=quiz_id,
                    session_id=session_id,
                    topic=topic_str,
                    num_questions=num_questions,
                    quiz_type=quiz_type,
                    difficulty=difficulty,
                    source_material=source_material,
                    questions=questions
                )
                db_session.add(new_quiz)
                db_session.commit()
            except SQLAlchemyError as e:
                logger.error(f"Database error storing quiz: {e}")
                if db_session:
                    db_session.rollback()
            finally:
                if db_session:
                    db_service.close_session(db_session)
        else:
            # Fallback to memory storage
            if not hasattr(storage, '_quiz_storage'):
                storage._quiz_storage = []
            quiz_data = {
                "id": quiz_id,
                "topic": topic_str,
                "num_questions": num_questions,
                "quiz_type": quiz_type,
                "difficulty": difficulty,
                "source_material": source_material,
                "questions": questions,
                "created": time.time()
            }
            storage._quiz_storage.append(quiz_data)
        
        return jsonify({
            "questions": questions,
            "quiz_id": quiz_id,
            "metadata": {
                "topic": topic_str,
                "num_questions": num_questions,
                "quiz_type": quiz_type,
                "difficulty": difficulty
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@quiz_bp.route('/submit', methods=['POST'])
def submit_quiz_answers():
    """Evaluate quiz answers with enhanced feedback"""
    data = request.json or {}
    answers = data.get('answers', [])
    questions = data.get('questions', [])
    quiz_id = data.get('quiz_id', '')
    time_taken = data.get('time_taken', 0)

    if not answers or not questions:
        return jsonify({"error": "Answers and questions are required"}), 400

    if len(answers) != len(questions):
        return jsonify({"error": "Number of answers must match number of questions"}), 400

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
        session_id = get_session_id()

        # Get topic from quiz metadata
        quiz_topic = ''
        if db_service.is_available():
            db_session = None
            try:
                db_session = db_service.get_session()
                quiz = db_session.query(Quiz).filter_by(quiz_id=quiz_id).first()
                if quiz:
                    quiz_topic = quiz.topic
            except SQLAlchemyError as e:
                logger.error(f"Database error getting quiz: {e}")
            finally:
                if db_session:
                    db_service.close_session(db_session)
        elif hasattr(storage, '_quiz_storage'):
            for quiz in storage._quiz_storage:
                if quiz.get('id') == quiz_id:
                    quiz_topic = quiz.get('topic', '')
                    break
        
        # Store quiz attempt in database
        if db_service.is_available():
            db_session = None
            try:
                db_session = db_service.get_session()
                attempt = QuizAttempt(
                    quiz_id=quiz_id,
                    session_id=session_id,
                    score=score,
                    correct=correct,
                    total=total,
                    time_taken=time_taken,
                    topic=quiz_topic
                )
                db_session.add(attempt)
                db_session.commit()
            except SQLAlchemyError as e:
                logger.error(f"Database error storing attempt: {e}")
                if db_session:
                    db_session.rollback()
            finally:
                if db_session:
                    db_service.close_session(db_session)
        else:
            # Fallback to memory storage
            attempt_data = {
                "quiz_id": quiz_id,
                "score": score,
                "correct": correct,
                "total": total,
                "time_taken": time_taken,
                "timestamp": time.time(),
                "topic": quiz_topic
            }
            
            if not hasattr(storage, '_quiz_attempts'):
                storage._quiz_attempts = []
            storage._quiz_attempts.append(attempt_data)

        return jsonify({
            "score": score,
            "correct": correct,
            "total": total,
            "time_taken": time_taken,
            "results": results
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@quiz_bp.route('/history', methods=['GET'])
def get_quiz_history():
    """Get quiz history and statistics"""
    try:
        session_id = get_session_id()
        
        if db_service.is_available():
            db_session = None
            try:
                db_session = db_service.get_session()
                
                # Get quizzes and attempts from database
                quizzes = db_session.query(Quiz).filter_by(session_id=session_id).all()
                attempts = db_session.query(QuizAttempt).filter_by(session_id=session_id).order_by(QuizAttempt.created_at.desc()).limit(10).all()
                
                total_quizzes = len(quizzes)
                total_attempts = db_session.query(QuizAttempt).filter_by(session_id=session_id).count()
                
                # Calculate average score
                from sqlalchemy import func as sql_func
                avg_score_result = db_session.query(sql_func.avg(QuizAttempt.score)).filter_by(session_id=session_id).scalar()
                avg_score = round(avg_score_result, 1) if avg_score_result else 0
                
                # Format recent attempts
                recent_attempts = [{
                    "quiz_id": a.quiz_id,
                    "score": a.score,
                    "correct": a.correct,
                    "total": a.total,
                    "time_taken": a.time_taken,
                    "topic": a.topic,
                    "timestamp": a.created_at.timestamp()
                } for a in attempts]
                
                return jsonify({
                    "total_quizzes": total_quizzes,
                    "total_attempts": total_attempts,
                    "average_score": avg_score,
                    "recent_attempts": recent_attempts
                })
            except SQLAlchemyError as e:
                logger.error(f"Database error in get_quiz_history: {e}")
            finally:
                if db_session:
                    db_service.close_session(db_session)
        
        # Fallback to memory storage
        attempts = getattr(storage, '_quiz_attempts', [])
        quizzes = getattr(storage, '_quiz_storage', [])
        
        total_quizzes = len(quizzes)
        total_attempts = len(attempts)
        avg_score = sum(a['score'] for a in attempts) / len(attempts) if attempts else 0
        
        recent_attempts = sorted(attempts, key=lambda x: x.get('timestamp', 0), reverse=True)[:10]
        
        return jsonify({
            "total_quizzes": total_quizzes,
            "total_attempts": total_attempts,
            "average_score": round(avg_score, 1),
            "recent_attempts": recent_attempts
        })
    except Exception as e:
        logger.error(f"Error in get_quiz_history: {e}")
        return jsonify({"error": str(e)}), 500

