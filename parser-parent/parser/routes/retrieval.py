"""Routes for knowledge retrieval"""
from flask import Blueprint, request, jsonify
import uuid
from services.retrieval_service import RetrievalService
from config import Config

retrieval_bp = Blueprint('retrieval', __name__, url_prefix='/api/retrieval')

@retrieval_bp.route('/search', methods=['POST'])
def search_knowledge():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    query = data.get('query')
    user_id = data.get('user_id')
    top_k = data.get('top_k', Config.RETRIEVAL_TOP_K)
    
    if not query:
        return jsonify({'error': 'query is required'}), 400
    
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user_id format'}), 400
    
    retrieval_service = RetrievalService()
    documents, expanded_keywords = retrieval_service.retrieve_chunks(
        query=query,
        user_id=str(user_uuid),
        top_k=top_k
    )
    
    chunks = []
    for doc in documents:
        chunks.append({
            'id': doc.metadata.get('id'),
            'content': doc.page_content,
            'topic': doc.metadata.get('topic'),
            'keywords': doc.metadata.get('keywords'),
            'difficulty_level': doc.metadata.get('difficulty_level'),
            'summary': doc.metadata.get('summary')
        })
    
    return jsonify({
        'chunks': chunks,
        'expanded_keywords': expanded_keywords
    }), 200

@retrieval_bp.route('/by-topic', methods=['POST'])
def search_by_topic():
    """
    Search for chunks by topic
    
    Request:
        {
            "topic": "Photosynthesis",
            "user_id": "uuid",
            "top_k": 6
        }
        
    Response:
        {
            "chunks": [...]
        }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    topic = data.get('topic')
    user_id = data.get('user_id')
    top_k = data.get('top_k', Config.RETRIEVAL_TOP_K)
    
    if not topic:
        return jsonify({'error': 'topic is required'}), 400
    
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user_id format'}), 400
    
    retrieval_service = RetrievalService()
    documents = retrieval_service.retrieve_by_topic(
        topic=topic,
        user_id=str(user_uuid),
        top_k=top_k
    )
    
    chunks = []
    for doc in documents:
        chunks.append({
            'id': doc.metadata.get('id'),
            'content': doc.page_content,
            'topic': doc.metadata.get('topic'),
            'keywords': doc.metadata.get('keywords'),
            'difficulty_level': doc.metadata.get('difficulty_level'),
            'summary': doc.metadata.get('summary')
        })
    
    return jsonify({
        'chunks': chunks
    }), 200
