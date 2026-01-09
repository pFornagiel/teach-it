"""Routes for teaching sessions (Stupid Student Agent)"""
from flask import Blueprint, request, jsonify
import uuid
from models import TeachingSession, Answer, db
from services.retrieval_service import RetrievalService
from services.student_agent import StudentAgent
from services.evaluation_agent import EvaluationAgent
from config import Config

teaching_bp = Blueprint('teaching', __name__, url_prefix='/api/teaching')

@teaching_bp.route('/start-session', methods=['POST'])
def start_session():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    user_id = data.get('user_id')
    topic = data.get('topic')
    
    if not user_id or not topic:
        return jsonify({'error': 'user_id and topic are required'}), 400
    
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user_id format'}), 400
    
    retrieval_service = RetrievalService()
    documents, _ = retrieval_service.retrieve_chunks(
        query=topic,
        user_id=str(user_uuid),
        top_k=Config.RETRIEVAL_TOP_K
    )
    
    if not documents:
        return jsonify({'error': 'No knowledge found for this topic. Please upload relevant documents first.'}), 404
    
    session = TeachingSession(
        id=uuid.uuid4(),
        user_id=user_uuid,
        current_topic=topic,
        question_index=0,
        completed=False,
        retrieved_chunks=[doc.metadata for doc in documents]
    )
    
    db.session.add(session)
    db.session.commit()
    
    student_agent = StudentAgent(max_questions=Config.MAX_QUESTIONS_PER_SESSION)
    first_question = student_agent.generate_question(
        context_chunks=documents,
        previous_questions=[],
        question_index=0
    )
    
    return jsonify({
        'session_id': str(session.id),
        'topic': topic,
        'first_question': first_question
    }), 201

@teaching_bp.route('/answer', methods=['POST'])
def answer_question():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    session_id = data.get('session_id')
    answer = data.get('answer')
    
    if not session_id or not answer:
        return jsonify({'error': 'session_id and answer are required'}), 400
    
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        return jsonify({'error': 'Invalid session_id format'}), 400
    
    session = TeachingSession.query.get(session_uuid)
    
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    if session.completed:
        return jsonify({'error': 'Session already completed'}), 400
    
    previous_answers = Answer.query.filter_by(session_id=session_uuid).order_by(Answer.created_at).all()
    
    current_question = f"Question {session.question_index + 1}"
    
    answer_record = Answer(
        id=uuid.uuid4(),
        session_id=session_uuid,
        question=current_question,
        answer=answer
    )
    
    db.session.add(answer_record)
    
    session.question_index += 1
    
    student_agent = StudentAgent(max_questions=Config.MAX_QUESTIONS_PER_SESSION)
    
    if not student_agent.should_continue(session.question_index):
        session.completed = True
        db.session.commit()
        
        return jsonify({
            'session_id': str(session.id),
            'next_question': None,
            'session_completed': True,
            'message': 'Session completed! You can now request an evaluation.'
        }), 200
    
    from langchain_core.documents import Document
    documents = [
        Document(page_content="", metadata=chunk)
        for chunk in session.retrieved_chunks
    ]
    
    previous_questions = [a.question for a in previous_answers]
    
    next_question = student_agent.generate_question(
        context_chunks=documents,
        previous_questions=previous_questions,
        question_index=session.question_index
    )
    
    db.session.commit()
    
    return jsonify({
        'session_id': str(session.id),
        'next_question': next_question,
        'session_completed': False
    }), 200

@teaching_bp.route('/evaluate/<session_id>', methods=['GET'])
def evaluate_session(session_id):
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        return jsonify({'error': 'Invalid session_id format'}), 400
    session = TeachingSession.query.get(session_uuid)
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    if not session.completed:
        return jsonify({'error': 'Session not yet completed'}), 400
    answers = Answer.query.filter_by(session_id=session_uuid).order_by(Answer.created_at).all()
    if not answers:
        return jsonify({'error': 'No answers found for this session'}), 404
    from langchain_core.documents import Document
    source_material = [
        Document(page_content="", metadata=chunk)
        for chunk in session.retrieved_chunks
    ]
    qa_pairs = [
        {'question': a.question, 'answer': a.answer}
        for a in answers
    ]
    evaluation_agent = EvaluationAgent()
    evaluation = evaluation_agent.evaluate_session(
        source_material=source_material,
        qa_pairs=qa_pairs
    )
    return jsonify({
        'session_id': str(session.id),
        'evaluation': {
            'score': evaluation.score,
            'correct_concepts': evaluation.correct_concepts,
            'misconceptions': evaluation.misconceptions,
            'improvement_tips': evaluation.improvement_tips
        },
        'all_qa_pairs': qa_pairs
    }), 200

@teaching_bp.route('/session/<session_id>', methods=['GET'])
def get_session(session_id):
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        return jsonify({'error': 'Invalid session_id format'}), 400
    session = TeachingSession.query.get(session_uuid)
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    answers = Answer.query.filter_by(session_id=session_uuid).order_by(Answer.created_at).all()
    return jsonify({
        'session': session.to_dict(),
        'answers': [a.to_dict() for a in answers]
    }), 200
