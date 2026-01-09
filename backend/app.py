import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import logging

from dotenv import load_dotenv

load_dotenv()

# Ensure agents module is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.student import StudentAgent

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# In-memory storage for session data
# Map session_id -> StudentAgent instance
active_agents = {}

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    files = request.files.getlist('file')
    if not files or files[0].filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    saved_filenames = []
    filepaths = []
    
    for file in files:
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            saved_filenames.append(filename)
            filepaths.append(filepath)
            
    # For Hackathon simplicity, we might just have one global "user" context or temporary sessions.
    # But let's assume we initialize an agent per session later.
    # For /api/topics, since it's stateless in the old mock, we might need to assume a "default" session 
    # OR we return a session_id right here. 
    # However, the frontend flow seems to be Upload -> Topics -> Start Session.
    # So we'll store these filepaths temporarily or create an agent here and return an ID?
    # The current frontend might expect just filenames. 
    # Let's create a temporary agent just for topics generation or manage it better.
    # Better yet: The frontend sends 'filenames' to /api/start_session.
    # So for /api/topics, the frontend expects us to know what files were uploaded?
    # Actually, the mock /api/topics endpoint just waited.
    # Let's implementation:
    # 1. Upload saves files.
    # 2. /api/topics needs to know WHICH files. 
    # IF the frontend doesn't send filenames to /api/topics, we might have to assume "all recent files" or similar.
    # Let's look at the integration guide again: "Backend reads uploaded file".
    # We will assume for this MVP that we process the files sent in the request or just the latest ones.
    # But wait, /api/topics is a POST. Does it send data?
    # The mock used `request.json` but commented out `filename = data.get('filename')`.
    # Let's assume the frontend sends the list of filenames it just uploaded.
    
    return jsonify({'message': 'Files uploaded successfully', 'filenames': saved_filenames}), 200

@app.route('/api/topics', methods=['POST'])
def get_topics():
    data = request.json
    # We expect filenames to be passed here, or we use all files in upload folder?
    # Let's try to get filenames from request, if not, scan upload folder (hacky but works for demo).
    filenames = data.get('filenames', [])
    
    if not filenames:
        # Fallback: list all in uploads
        filenames = os.listdir(app.config['UPLOAD_FOLDER'])
    
    file_paths = [os.path.join(app.config['UPLOAD_FOLDER'], f) for f in filenames if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], f))]
    
    if not file_paths:
        return jsonify({'error': 'No files found'}), 400

    # Create a temporary agent to generate topics
    # Note: This is expensive to rebuild vectorstore just for topics, but safe.
    try:
        temp_agent = StudentAgent()
        temp_agent.process_files(file_paths)
        topics = temp_agent.generate_topics()
        return jsonify({'topics': topics}), 200
    except Exception as e:
        logger.error(f"Error in get_topics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/start_session', methods=['POST'])
def start_session():
    data = request.json
    topic = data.get('topic')
    filenames = data.get('filenames', []) # List of filenames
    
    if not filenames:
         filenames = os.listdir(app.config['UPLOAD_FOLDER'])
         
    file_paths = [os.path.join(app.config['UPLOAD_FOLDER'], f) for f in filenames]
    
    session_id = f"session_{os.urandom(4).hex()}"
    
    agent = StudentAgent()
    try:
        agent.process_files(file_paths)
        agent.start_learning(topic)
        active_agents[session_id] = agent
        return jsonify({'session_id': session_id}), 200
    except Exception as e:
         logger.error(f"Error starting session: {e}")
         return jsonify({'error': str(e)}), 500

@app.route('/api/continue_session', methods=['POST'])
def continue_session():
    data = request.json
    session_id = data.get('session_id')
    
    if session_id not in active_agents:
        return jsonify({'error': 'Session not found'}), 404
        
    agent = active_agents[session_id]
    agent.target_questions += 3
    return jsonify({'message': 'Session extended'}), 200

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    session_id = data.get('session_id')
    user_answer = data.get('answer') # Can be None if it's the start
    
    if session_id not in active_agents:
        return jsonify({'error': 'Session not found'}), 404
    
    agent = active_agents[session_id]
    
    try:
        response = agent.chat(user_answer)
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/evaluate', methods=['POST'])
def evaluate():
    data = request.json
    session_id = data.get('session_id')
    
    if session_id not in active_agents:
        return jsonify({'error': 'Session not found'}), 404
    
    agent = active_agents[session_id]
    
    try:
        evaluation = agent.evaluate()
        return jsonify(evaluation), 200
    except Exception as e:
        logger.error(f"Error in evaluation: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
