import os
from dotenv import load_dotenv
load_dotenv()
class Config:
    
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/upside_db')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'csv', 'png', 'jpg', 'jpeg'}
    
    CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '750'))
    CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '150'))
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'text-embedding-ada-002')
    LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-4o')
    LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', '0.7'))
    
    RETRIEVAL_TOP_K = int(os.getenv('RETRIEVAL_TOP_K', '6'))
    
    MAX_QUESTIONS_PER_SESSION = int(os.getenv('MAX_QUESTIONS_PER_SESSION', '3'))
