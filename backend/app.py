import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import time
import json

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# In-memory storage for session data (mock persistence)
sessions = {}

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Mocking "processing" time
        time.sleep(1)
        
        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200

@app.route('/api/topics', methods=['POST'])
def get_topics():
    # Mock topics generation based on file
    data = request.json
    # filename = data.get('filename') # unused in mock
    
    time.sleep(1.5) # Mock processing
    
    mock_topics = [
        "Create a simple HTTP server",
        "Understanding React Hooks",
        "Basics of Quantum Physics"
    ]
    return jsonify({'topics': mock_topics}), 200

@app.route('/api/start_session', methods=['POST'])
def start_session():
    data = request.json
    topic = data.get('topic')
    filename = data.get('filename') # Kept for interface consistency
    session_id = f"session_{int(time.time())}"
    
    sessions[session_id] = {
        'topic': topic,
        'filename': filename,
        'questions_asked': 0,
        'target_questions': 3,
        'history': [],
        'scores': []
    }
    
    return jsonify({'session_id': session_id}), 200

@app.route('/api/continue_session', methods=['POST'])
def continue_session():
    data = request.json
    session_id = data.get('session_id')
    
    if session_id not in sessions:
        return jsonify({'error': 'Session not found'}), 404
        
    sessions[session_id]['target_questions'] += 3
    return jsonify({'message': 'Session extended'}), 200

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    session_id = data.get('session_id')
    user_answer = data.get('answer')
    
    if session_id not in sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session = sessions[session_id]
    
    # If user provided an answer (not the initial fetch)
    if user_answer:
        session['history'].append({'role': 'user', 'content': user_answer})
        session['questions_asked'] += 1
        # Mock scoring logic
        session['scores'].append("A" if len(user_answer) > 10 else "C")
    
    # Check if we should end or continue
    if session['questions_asked'] >= session.get('target_questions', 3):
        return jsonify({
            'finished': True,
            'message': 'Good job! Ready for evaluation?'
        }), 200
    
    # Generate next question (Mock)
    topic = session['topic']
    base_questions = [
        f"Explain the first concept of {topic}.",
        f"How does {topic} relate to everyday life?",
        f"What is the most critical part of {topic}?",
        f"Can you give an example of {topic} in action?",
        f"What are common misconceptions about {topic}?",
        f"How would you explain {topic} to a 5 year old?"
    ]
    
    # Cyclic question selection
    idx = session['questions_asked'] % len(base_questions)
    next_question = base_questions[idx]
    
    session['history'].append({'role': 'assistant', 'content': next_question})
    
    return jsonify({
        'finished': False,
        'question': next_question
    }), 200

@app.route('/api/evaluate', methods=['POST'])
def evaluate():
    data = request.json
    session_id = data.get('session_id')
    
    if session_id not in sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    # Mock evaluation
    time.sleep(2)
    
    return jsonify({
        'grade': 'B+',
        'comments': 'You explained the basics well, but missed some details on the advanced concepts.',
        'details': [
            {'point': 'Clarity', 'status': 'correct'},
            {'point': 'Depth', 'status': 'partial'},
            {'point': 'Examples', 'status': 'correct'}
        ]
    }), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
