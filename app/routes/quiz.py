"""Quiz routes blueprint"""
from flask import Blueprint, request, jsonify
from app.services.llm_service import LLMService

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/generate', methods=['POST'])
def generate_quiz():
    """Generate quiz questions using LLM"""
    data = request.json or {}
    topic = data.get('topic', '').strip()
    num_questions = int(data.get('num_questions', 5))

    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    if num_questions < 1 or num_questions > 20:
        return jsonify({"error": "Number of questions must be between 1 and 20"}), 400

    try:
        prompt = f"""Generate {num_questions} multiple choice quiz questions about {topic}. 
Format each question as JSON with this structure:
{{
    "question": "Question text here",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct": 0
}}
where "correct" is the index (0-3) of the correct answer.

Return ONLY a JSON array of questions, no other text. Example:
[
    {{"question": "What is...?", "options": ["A", "B", "C", "D"], "correct": 0}},
    {{"question": "Which...?", "options": ["A", "B", "C", "D"], "correct": 1}}
]"""

        content = LLMService.call_llm([{"role": "user", "content": prompt}])
        questions = LLMService.extract_json(content, json_type='array')
        
        # Validate questions structure
        if not isinstance(questions, list):
            raise Exception("Invalid response format: expected array")
        
        return jsonify({"questions": questions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@quiz_bp.route('/submit', methods=['POST'])
def submit_quiz_answers():
    """Evaluate quiz answers"""
    data = request.json or {}
    answers = data.get('answers', [])
    questions = data.get('questions', [])

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
                "options": question.get('options', [])
            })

        score = (correct / total * 100) if total > 0 else 0

        return jsonify({
            "score": score,
            "correct": correct,
            "total": total,
            "results": results
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

