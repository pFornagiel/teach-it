from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector
import uuid
from datetime import datetime
db = SQLAlchemy()
class KnowledgeChunk(db.Model):
    __tablename__ = 'knowledge_chunks'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), nullable=False, index=True)
    file_id = db.Column(UUID(as_uuid=True), nullable=False, index=True)
    
    content_blob = db.Column(db.Text, nullable=False)
    embedding = db.Column(Vector(1536))

    
    topic = db.Column(db.Text)
    keywords = db.Column(JSONB)
    difficulty_level = db.Column(db.String(50))

    summary = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'file_id': str(self.file_id),
            'content_blob': self.content_blob,
            'topic': self.topic,
            'keywords': self.keywords,
            'difficulty_level': self.difficulty_level,
            'summary': self.summary,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def to_langchain_document(self):
        from langchain_core.documents import Document
        return Document(
            page_content=self.content_blob,
            metadata={
                'id': str(self.id),
                'topic': self.topic,
                'keywords': self.keywords or [],
                'difficulty_level': self.difficulty_level,
                'summary': self.summary
            }
        )

class TeachingSession(db.Model):
    __tablename__ = 'teaching_sessions'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), nullable=False, index=True)
    current_topic = db.Column(db.Text)
    question_index = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)
    
    retrieved_chunks = db.Column(JSONB)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    answers = db.relationship('Answer', backref='session', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'current_topic': self.current_topic,
            'question_index': self.question_index,
            'completed': self.completed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Answer(db.Model):
    __tablename__ = 'answers'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = db.Column(UUID(as_uuid=True), db.ForeignKey('teaching_sessions.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'session_id': str(self.session_id),
            'question': self.question,
            'answer': self.answer,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class UploadedFile(db.Model):
    __tablename__ = 'uploaded_files'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    file_type = db.Column(db.String(50))
    file_size = db.Column(db.Integer)
    processing_status = db.Column(db.String(50), default='pending')

    error_message = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'filename': self.filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'processing_status': self.processing_status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }
