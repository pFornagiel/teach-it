"""Routes for document ingestion"""
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import uuid
from models import UploadedFile, db
from services.document_processor import DocumentProcessor
from config import Config

ingestion_bp = Blueprint('ingestion', __name__, url_prefix='/api/ingestion')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@ingestion_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    user_id = request.form.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    try:
        user_id = uuid.UUID(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user_id format'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    filename = secure_filename(file.filename)
    file_id = uuid.uuid4()
    
    upload_dir = Config.UPLOAD_FOLDER
    os.makedirs(upload_dir, exist_ok=True)
    
    file_ext = filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{file_id}.{file_ext}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    file.save(file_path)
    
    uploaded_file = UploadedFile(
        id=file_id,
        user_id=user_id,
        filename=filename,
        file_path=file_path,
        file_type=file_ext,
        file_size=os.path.getsize(file_path),
        processing_status='pending'
    )
    
    db.session.add(uploaded_file)
    db.session.commit()
    
    processor = DocumentProcessor(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP
    )
    
    result = processor.process_file(file_path, str(file_id), str(user_id))
    
    if result['success']:
        return jsonify({
            'file_id': str(file_id),
            'filename': filename,
            'status': 'completed',
            'message': f'File processed successfully. Created {result["chunks_created"]} chunks.',
            'chunks_created': result['chunks_created']
        }), 201
    else:
        return jsonify({
            'file_id': str(file_id),
            'filename': filename,
            'status': 'failed',
            'error': result['error']
        }), 500

@ingestion_bp.route('/status/<file_id>', methods=['GET'])
def get_file_status(file_id):
    try:
        file_uuid = uuid.UUID(file_id)
    except ValueError:
        return jsonify({'error': 'Invalid file_id format'}), 400
    
    uploaded_file = UploadedFile.query.get(file_uuid)
    
    if not uploaded_file:
        return jsonify({'error': 'File not found'}), 404
    
    return jsonify(uploaded_file.to_dict()), 200

@ingestion_bp.route('/files/<user_id>', methods=['GET'])
def get_user_files(user_id):
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user_id format'}), 400
    
    files = UploadedFile.query.filter_by(user_id=user_uuid).all()
    
    return jsonify({
        'files': [f.to_dict() for f in files]
    }), 200
