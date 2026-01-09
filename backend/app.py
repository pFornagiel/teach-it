import os
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import time
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = Flask(__name__)
CORS(app)

# Use the main project uploads folder (one level up from backend)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    UPLOAD_FOLDER = 'uploads'  # Fallback to local folder
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# In-memory storage for session data (mock persistence)
sessions = {}

# Image extensions
IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'}

@app.route('/api/notes', methods=['POST'])
def get_notes():
    """Get the content of uploaded notes file"""
    data = request.json
    filename = data.get('filename')
    
    if not filename:
        return jsonify({'error': 'No filename provided'}), 400
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    # Determine file format
    file_ext = os.path.splitext(filename)[1].lower().lstrip('.')
    
    try:
        content = ''
        
        # Handle image files
        if file_ext in IMAGE_EXTENSIONS:
            with open(filepath, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            mime_type = f'image/{file_ext}'
            if file_ext == 'jpg':
                mime_type = 'image/jpeg'
            content = f'data:{mime_type};base64,{image_data}'
            return jsonify({
                'filename': filename,
                'content': content,
                'format': 'image'
            }), 200
        
        elif file_ext == 'txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        
        elif file_ext == 'csv':
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        
        elif file_ext == 'docx':
            try:
                from docx import Document
                doc = Document(filepath)
                content = '\n'.join([para.text for para in doc.paragraphs])
            except ImportError:
                return jsonify({'error': 'python-docx not installed'}), 500
        
        elif file_ext == 'pdf':
            try:
                from PyPDF2 import PdfReader
                reader = PdfReader(filepath)
                text_parts = []
                for page in reader.pages:
                    text_parts.append(page.extract_text() or '')
                content = '\n'.join(text_parts)
            except ImportError:
                return jsonify({'error': 'PyPDF2 not installed'}), 500
        
        else:
            # Try to read as text for unknown formats
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except:
                return jsonify({'error': 'Unsupported file format'}), 400
        
        return jsonify({
            'filename': filename,
            'content': content,
            'format': file_ext or 'txt'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notes/analyze', methods=['POST'])
def analyze_notes():
    """Analyze notes and return highlighted content with summary"""
    data = request.json
    filename = data.get('filename')
    
    if not filename:
        return jsonify({'error': 'No filename provided'}), 400
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    file_ext = os.path.splitext(filename)[1].lower().lstrip('.')
    
    # Get the text content
    try:
        content = ''
        if file_ext == 'txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        elif file_ext == 'docx':
            from docx import Document
            doc = Document(filepath)
            content = '\n'.join([para.text for para in doc.paragraphs])
        elif file_ext == 'pdf':
             return jsonify({'error': 'PDF files are not supported. Please convert to DOCX or TXT.'}), 400

        else:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
    except Exception as e:
        return jsonify({'error': f'Failed to read file: {str(e)}'}), 500
    
    if not content.strip():
        return jsonify({'error': 'File is empty'}), 400
    
    # Call OpenAI to analyze and highlight
    try:
        # Truncate content if too long to avoid token limits
        max_content_length = 15000
        truncated_content = content[:max_content_length] if len(content) > max_content_length else content
        
        prompt = f"""Analyze the following study notes. Return a JSON object with:
1. "summary": A concise summary (3-5 sentences) of the key points.
2. "highlighted_html": The text with HTML spans for highlighting:
   - <span class="highlight-definition">text</span> for definitions
   - <span class="highlight-concept">text</span> for key concepts
   - <span class="highlight-important">text</span> for important notes
   - <span class="highlight-example">text</span> for examples

IMPORTANT: Return ONLY valid JSON, no markdown, no code blocks. Escape all quotes and special characters properly.

Notes to analyze:

{truncated_content}"""

        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are a study assistant. Return ONLY valid JSON with 'summary' and 'highlighted_html' keys. No markdown code blocks. Properly escape all special characters in JSON strings."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=16000
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if result_text.startswith('```'):
            lines = result_text.split('\n')
            # Remove first line (```json) and last line (```)
            lines = [l for l in lines if not l.strip().startswith('```')]
            result_text = '\n'.join(lines)
        
        # Try to find JSON object in response
        start_idx = result_text.find('{')
        end_idx = result_text.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            result_text = result_text[start_idx:end_idx + 1]
        
        try:
            result = json.loads(result_text)
        except json.JSONDecodeError:
            # Fallback: try to fix common issues
            import re
            # Replace unescaped newlines in strings
            result_text = re.sub(r'(?<!\\)\n', '\\n', result_text)
            try:
                result = json.loads(result_text)
            except:
                # Last resort: return original content with basic highlighting
                return jsonify({
                    'filename': filename,
                    'summary': 'Summary generation failed - displaying original content.',
                    'highlighted_html': f'<p>{content}</p>',
                    'format': file_ext
                }), 200
        
        return jsonify({
            'filename': filename,
            'summary': result.get('summary', ''),
            'highlighted_html': result.get('highlighted_html', content),
            'format': file_ext
        }), 200
        
    except json.JSONDecodeError as e:
        return jsonify({'error': f'Failed to parse AI response: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'AI analysis failed: {str(e)}'}), 500

@app.route('/api/notes/list', methods=['GET'])
def list_notes():
    """List all uploaded files in the uploads folder"""
    try:
        files = []
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            # Skip PDF files
            if filename.lower().endswith('.pdf'):
                continue
                
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(filepath):
                files.append({
                    'filename': filename,
                    'format': os.path.splitext(filename)[1].lower().lstrip('.'),
                    'size': os.path.getsize(filepath)
                })
        return jsonify({'files': files}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    files = request.files.getlist('file')
    if not files or files[0].filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    saved_filenames = []
    for file in files:
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            saved_filenames.append(filename)
    
    # Mocking "processing" time
    time.sleep(1)
    
    return jsonify({'message': 'Files uploaded successfully', 'filenames': saved_filenames}), 200

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
    filenames = data.get('filenames') # List of filenames
    session_id = f"session_{int(time.time())}"
    
    sessions[session_id] = {
        'topic': topic,
        'filenames': filenames,
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
