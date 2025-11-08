"""Quiz routes with Supabase persistence"""
from flask import Blueprint, request, jsonify, render_template
from app.services.supabase_service import supabase_service
from app.services.llm_service import LLMService
from app.services.langgraph_service import rag_service
from app.services.web_search import WebSearchService
from app.extensions import supabase
import json

quiz_v2_bp = Blueprint('quiz_v2', __name__)

def get_user_id():
    """Get user ID from X-User-Id header"""
    user_id = request.headers.get('X-User-Id')
    if not user_id:
        # For development, allow a default user
        user_id = '00000000-0000-0000-0000-000000000000'
    return user_id

@quiz_v2_bp.route('/generate', methods=['POST'])
def generate_quiz():
    """Generate quiz and store in Supabase"""
    user_id = get_user_id()
    
    if not supabase_service.is_available():
        return jsonify({"error": "Supabase not configured"}), 503
    
    try:
        data = request.json or {}
        topic = data.get('topic', '').strip()
        topics = data.get('topics', [])
        num_questions = int(data.get('num_questions', 5))
        quiz_type = data.get('quiz_type', 'multiple_choice')
        difficulty = data.get('difficulty', 'intermediate')
        source_material = data.get('source_material', 'general')
        
        # Combine topic and topics
        if topics and isinstance(topics, list):
            topic_str = ', '.join([topic] + topics) if topic else ', '.join(topics)
        else:
            topic_str = topic
        
        if not topic_str:
            return jsonify({"error": "Topic is required"}), 400
        
        if num_questions < 1 or num_questions > 20:
            return jsonify({"error": "Number of questions must be between 1 and 20"}), 400
        
        # Build context based on source material
        context = ""
        if source_material == 'knowledge_base' and rag_service and rag_service.is_ready():
            kb_docs = rag_service.search(topic_str, k=3)
            if kb_docs:
                context = "Use the following information from the knowledge base:\n"
                for i, doc in enumerate(kb_docs, 1):
                    context += f"{i}. {doc['content'][:300]}...\n\n"
        elif source_material == 'web_search':
            search_results = WebSearchService.search(topic_str, max_results=3)
            if search_results:
                context = "Use the following information from web search:\n"
                for i, result in enumerate(search_results, 1):
                    context += f"{i}. {result['title']}: {result['snippet']}\n\n"
        
        # Build prompt for LLM - expect items array format
        prompt = f"""Generate {num_questions} multiple choice questions about: {topic_str}

Difficulty Level: {difficulty}

{context if context else ''}

Return a JSON object with this exact structure:
{{
    "items": [
        {{
            "question": "Question text here",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "answer": "B",
            "explanation": "Brief explanation of why this answer is correct"
        }}
    ]
}}

The "answer" field should be the letter (A, B, C, or D) corresponding to the correct option.
Return ONLY the JSON object, no other text."""
        
        # Call LLM
        content = LLMService.call_llm([{"role": "user", "content": prompt}])
        
        # Extract JSON - expect object with items array
        quiz_data = LLMService.extract_json(content, json_type='object')
        
        if not quiz_data or 'items' not in quiz_data:
            # Try to extract items array directly
            items = LLMService.extract_json(content, json_type='array')
            if items:
                quiz_data = {"items": items}
            else:
                raise Exception("Invalid response format: expected object with 'items' array")
        
        items = quiz_data.get('items', [])
        if not items:
            raise Exception("No quiz items generated")
        
        # Convert answer letters to indices for storage
        letter_to_index = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
        for item in items:
            answer_letter = str(item.get('answer', '')).upper().strip()
            options = item.get('options', [])
            
            # Find index of answer
            answer_index = letter_to_index.get(answer_letter)
            if answer_index is None or answer_index >= len(options):
                # Fallback: try to find by first character
                if answer_letter and len(answer_letter) > 0:
                    answer_index = letter_to_index.get(answer_letter[0])
                if answer_index is None:
                    answer_index = 0  # Default to first option
            
            # Store both answer letter and index
            item['correct_index'] = answer_index
            item['answer_letter'] = answer_letter
            if 'explanation' not in item:
                item['explanation'] = "Correct answer explanation"
        
        # Store quiz in Supabase
        if supabase.is_available() and supabase.client:
            quiz_record = {
                'user_id': user_id,
                'topic': topic_str,
                'topics': topics if topics else None,
                'quiz_type': quiz_type,
                'difficulty': difficulty,
                'source_material': source_material,
                'num_questions': num_questions,
                'questions': items  # JSONB accepts dict/list directly
            }
            
            response = supabase.client.table('quizzes').insert(quiz_record).execute()
            quiz_id = response.data[0]['id'] if response.data else None
            
            return jsonify({
                "id": quiz_id,
                "items": items,
                "metadata": {
                    "topic": topic_str,
                    "num_questions": num_questions,
                    "quiz_type": quiz_type,
                    "difficulty": difficulty
                }
            }), 201
        else:
            return jsonify({"error": "Supabase not available"}), 503
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@quiz_v2_bp.route('', methods=['GET'])
def list_quizzes():
    """List all quizzes for the user"""
    user_id = get_user_id()
    
    if not supabase_service.is_available():
        return jsonify({"error": "Supabase not configured"}), 503
    
    try:
        if supabase.is_available() and supabase.client:
            response = supabase.client.table('quizzes').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
            quizzes = [dict(row) for row in response.data] if response.data else []
            
            # Check if request wants HTML (HTMX)
            if request.headers.get('HX-Request'):
                # Return HTML fragment
                html = ''
                for quiz in quizzes:
                    date_str = ''
                    if quiz.get('created_at'):
                        try:
                            from datetime import datetime
                            date = datetime.fromisoformat(str(quiz['created_at']).replace('Z', '+00:00'))
                            date_str = date.strftime('%m/%d/%Y')
                        except:
                            date_str = ''
                    
                    # Parse questions to get count
                    questions_data = quiz.get('questions', [])
                    if isinstance(questions_data, str):
                        try:
                            questions_data = json.loads(questions_data)
                        except:
                            questions_data = []
                    num_items = len(questions_data) if isinstance(questions_data, list) else quiz.get('num_questions', 0)
                    
                    html += f'''
                    <div class="quiz-item p-4 border border-gray-200 rounded-lg mb-3 hover:bg-gray-50">
                        <div class="flex justify-between items-start">
                            <div class="flex-1 cursor-pointer" onclick="loadQuiz('{quiz['id']}')">
                                <div class="font-medium text-gray-900">{quiz.get('topic', 'Untitled Quiz')}</div>
                                <div class="text-sm text-gray-500 mt-1">
                                    {num_items} questions • {quiz.get('difficulty', 'intermediate')} • {date_str}
                                </div>
                            </div>
                            <button 
                                onclick="deleteQuiz('{quiz['id']}', event)"
                                class="ml-4 text-red-600 hover:text-red-700 px-2 py-1 text-sm">
                                Delete
                            </button>
                        </div>
                    </div>
                    '''
                return html, 200
            
            return jsonify({
                "quizzes": quizzes,
                "count": len(quizzes)
            }), 200
        else:
            return jsonify({"error": "Supabase not available"}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@quiz_v2_bp.route('/<quiz_id>', methods=['GET'])
def get_quiz(quiz_id):
    """Get quiz items"""
    user_id = get_user_id()
    
    if not supabase_service.is_available():
        return jsonify({"error": "Supabase not configured"}), 503
    
    try:
        if supabase.is_available() and supabase.client:
            response = supabase.client.table('quizzes').select('*').eq('id', quiz_id).eq('user_id', user_id).limit(1).execute()
            
            if not response.data:
                return jsonify({"error": "Quiz not found"}), 404
            
            quiz = dict(response.data[0])
            
            # Parse questions JSONB (may be dict/list or string)
            questions_data = quiz.get('questions', [])
            if isinstance(questions_data, str):
                try:
                    questions_data = json.loads(questions_data)
                except:
                    questions_data = []
            if not isinstance(questions_data, list):
                questions_data = []
            
            # Check if request wants HTML (HTMX) - redirect to play page
            if request.headers.get('HX-Request'):
                # Return redirect or HTML fragment
                from flask import redirect
                return redirect(f'/quiz/{quiz_id}/play'), 302
            
            return jsonify({
                "id": quiz['id'],
                "topic": quiz.get('topic'),
                "items": questions_data,
                "metadata": {
                    "quiz_type": quiz.get('quiz_type'),
                    "difficulty": quiz.get('difficulty'),
                    "num_questions": quiz.get('num_questions')
                }
            }), 200
        else:
            return jsonify({"error": "Supabase not available"}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@quiz_v2_bp.route('/<quiz_id>/submit', methods=['POST'])
def submit_quiz(quiz_id):
    """Submit quiz answers and create analysis"""
    user_id = get_user_id()
    
    if not supabase_service.is_available():
        return jsonify({"error": "Supabase not configured"}), 503
    
    try:
        data = request.json or {}
        answers = data.get('answers', [])  # Array of answer indices or letters
        time_taken = data.get('time_taken', 0)
        
        if not supabase.is_available() or not supabase.client:
            return jsonify({"error": "Supabase not available"}), 503
        
        # Get quiz
        quiz_response = supabase.client.table('quizzes').select('*').eq('id', quiz_id).eq('user_id', user_id).limit(1).execute()
        if not quiz_response.data:
            return jsonify({"error": "Quiz not found"}), 404
        
        quiz = dict(quiz_response.data[0])
        questions_data = quiz.get('questions', [])
        if isinstance(questions_data, str):
            try:
                questions_data = json.loads(questions_data)
            except:
                questions_data = []
        if not isinstance(questions_data, list):
            questions_data = []
        
        # Evaluate answers
        correct = 0
        total = len(questions_data)
        results = []
        
        for i, item in enumerate(questions_data):
            user_answer = answers[i] if i < len(answers) else None
            
            # Handle both index and letter answers
            correct_answer_index = item.get('correct_index')
            if correct_answer_index is None:
                # Fallback: try to get from answer_letter
                answer_letter = item.get('answer_letter', item.get('answer', ''))
                letter_to_index = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
                correct_answer_index = letter_to_index.get(str(answer_letter).upper().strip()[0] if answer_letter else '', 0)
            
            # Convert user answer to index if it's a letter
            user_answer_index = user_answer
            if isinstance(user_answer, str) and user_answer.upper() in ['A', 'B', 'C', 'D']:
                letter_to_index = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
                user_answer_index = letter_to_index.get(user_answer.upper())
            
            # Handle null answers
            if user_answer_index is None:
                is_correct = False
            else:
                is_correct = user_answer_index == correct_answer_index
            
            if is_correct:
                correct += 1
            
            results.append({
                "question": item.get('question', ''),
                "user_answer": user_answer_index,
                "correct_answer": correct_answer_index,
                "is_correct": is_correct,
                "options": item.get('options', []),
                "explanation": item.get('explanation', '')
            })
        
        score = (correct / total * 100) if total > 0 else 0
        
        # Create quiz attempt record
        attempt_data = {
            'user_id': user_id,
            'quiz_id': quiz_id,
            'score': round(score, 2),
            'correct': correct,
            'total': total,
            'time_taken': time_taken,
            'answers': results  # JSONB accepts dict/list directly
        }
        
        attempt_response = supabase.client.table('quiz_attempts').insert(attempt_data).execute()
        attempt_id = attempt_response.data[0]['id'] if attempt_response.data else None
        
        return jsonify({
            "attempt_id": attempt_id,
            "score": round(score, 2),
            "correct": correct,
            "total": total,
            "time_taken": time_taken,
            "results": results
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@quiz_v2_bp.route('/<quiz_id>', methods=['DELETE'])
def delete_quiz(quiz_id):
    """Delete a quiz"""
    user_id = get_user_id()
    
    if not supabase_service.is_available():
        return jsonify({"error": "Supabase not configured"}), 503
    
    try:
        if supabase.is_available() and supabase.client:
            # Delete quiz (attempts will be cascade deleted)
            response = supabase.client.table('quizzes').delete().eq('id', quiz_id).eq('user_id', user_id).execute()
            
            return jsonify({"success": True, "message": "Quiz deleted"}), 200
        else:
            return jsonify({"error": "Supabase not available"}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@quiz_v2_bp.route('/history', methods=['GET'])
def get_quiz_history():
    """Get quiz history with attempts and analysis"""
    user_id = get_user_id()
    
    if not supabase_service.is_available():
        return jsonify({"error": "Supabase not configured"}), 503
    
    try:
        if supabase.is_available() and supabase.client:
            # Get all quiz attempts for the user
            attempts_response = supabase.client.table('quiz_attempts').select('*').eq('user_id', user_id).order('completed_at', desc=True).limit(50).execute()
            attempts = [dict(row) for row in attempts_response.data] if attempts_response.data else []
            
            # Get quiz details for each attempt
            quiz_ids = [attempt['quiz_id'] for attempt in attempts]
            if quiz_ids:
                quizzes_response = supabase.client.table('quizzes').select('id, topic').in_('id', quiz_ids).execute()
                quizzes_dict = {q['id']: q for q in quizzes_response.data} if quizzes_response.data else {}
                
                # Attach quiz info to attempts
                for attempt in attempts:
                    quiz_id = attempt.get('quiz_id')
                    if quiz_id in quizzes_dict:
                        attempt['quiz_info'] = quizzes_dict[quiz_id]
                    else:
                        attempt['quiz_info'] = {'topic': 'Unknown Quiz'}
            
            # Check if request wants HTML (HTMX)
            if request.headers.get('HX-Request'):
                # Return HTML fragment
                html = ''
                if not attempts:
                    html = '<p class="text-gray-500 text-center py-8">No quiz attempts yet. Complete a quiz to see your history here.</p>'
                else:
                    for attempt in attempts:
                        quiz_info = attempt.get('quiz_info', {})
                        if isinstance(quiz_info, dict):
                            quiz_topic = quiz_info.get('topic', 'Unknown Quiz')
                        else:
                            quiz_topic = 'Unknown Quiz'
                        
                        date_str = ''
                        if attempt.get('completed_at'):
                            try:
                                from datetime import datetime
                                date = datetime.fromisoformat(str(attempt['completed_at']).replace('Z', '+00:00'))
                                date_str = date.strftime('%m/%d/%Y %H:%M')
                            except:
                                date_str = ''
                        
                        score = attempt.get('score', 0)
                        correct = attempt.get('correct', 0)
                        total = attempt.get('total', 0)
                        time_taken = attempt.get('time_taken', 0)
                        
                        # Format time
                        time_str = ''
                        if time_taken:
                            minutes = time_taken // 60
                            seconds = time_taken % 60
                            if minutes > 0:
                                time_str = f'{minutes}m {seconds}s'
                            else:
                                time_str = f'{seconds}s'
                        
                        # Get score color
                        score_color = 'text-green-600' if score >= 70 else 'text-yellow-600' if score >= 50 else 'text-red-600'
                        
                        html += f'''
                        <div class="bg-white p-4 border border-gray-200 rounded-lg mb-3 hover:bg-gray-50">
                            <div class="flex justify-between items-start">
                                <div class="flex-1">
                                    <div class="font-medium text-gray-900">{quiz_topic}</div>
                                    <div class="text-sm text-gray-500 mt-1">
                                        Score: <span class="{score_color} font-semibold">{score:.1f}%</span> 
                                        ({correct}/{total} correct)
                                        {f' • Time: {time_str}' if time_str else ''}
                                        {f' • {date_str}' if date_str else ''}
                                    </div>
                                </div>
                                <button 
                                    onclick="viewAttemptAnalysis('{attempt['id']}')"
                                    class="ml-4 text-blue-600 hover:text-blue-700 px-3 py-1 text-sm border border-blue-200 rounded">
                                    View Analysis
                                </button>
                            </div>
                        </div>
                        '''
                return html, 200
            
            return jsonify({
                "attempts": attempts,
                "count": len(attempts)
            }), 200
        else:
            return jsonify({"error": "Supabase not available"}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@quiz_v2_bp.route('/attempt/<attempt_id>', methods=['GET'])
def get_attempt_analysis(attempt_id):
    """Get detailed analysis for a quiz attempt"""
    user_id = get_user_id()
    
    if not supabase_service.is_available():
        return jsonify({"error": "Supabase not configured"}), 503
    
    try:
        if supabase.is_available() and supabase.client:
            response = supabase.client.table('quiz_attempts').select('*').eq('id', attempt_id).eq('user_id', user_id).limit(1).execute()
            
            if not response.data:
                return jsonify({"error": "Attempt not found"}), 404
            
            attempt = dict(response.data[0])
            
            # Get quiz details
            quiz_id = attempt.get('quiz_id')
            quiz_topic = 'Unknown Quiz'
            if quiz_id:
                quiz_response = supabase.client.table('quizzes').select('topic').eq('id', quiz_id).limit(1).execute()
                if quiz_response.data:
                    quiz_topic = quiz_response.data[0].get('topic', 'Unknown Quiz')
            
            # Parse answers (results)
            answers_data = attempt.get('answers', [])
            if isinstance(answers_data, str):
                try:
                    answers_data = json.loads(answers_data)
                except:
                    answers_data = []
            if not isinstance(answers_data, list):
                answers_data = []
            
            # Always render template for analysis page
            return render_template('quiz_analysis.html', 
                attempt=attempt, 
                results=answers_data,
                quiz_topic=quiz_topic), 200
        else:
            return jsonify({"error": "Supabase not available"}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@quiz_v2_bp.route('/<quiz_id>/play', methods=['GET'])
def quiz_play_page(quiz_id):
    """Quiz play page"""
    user_id = get_user_id()
    
    if not supabase_service.is_available():
        return jsonify({"error": "Supabase not configured"}), 503
    
    try:
        if supabase.is_available() and supabase.client:
            response = supabase.client.table('quizzes').select('*').eq('id', quiz_id).eq('user_id', user_id).limit(1).execute()
            
            if not response.data:
                return jsonify({"error": "Quiz not found"}), 404
            
            quiz = dict(response.data[0])
            questions_data = quiz.get('questions', [])
            if isinstance(questions_data, str):
                try:
                    questions_data = json.loads(questions_data)
                except:
                    questions_data = []
            if not isinstance(questions_data, list):
                questions_data = []
            
            return render_template('quiz_play.html', quiz=quiz, items=questions_data), 200
        else:
            return jsonify({"error": "Supabase not available"}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500

