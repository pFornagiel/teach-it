-- Database initialization script for Upside Learning API
-- Run this script to set up the PostgreSQL database with pgvector extension
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
-- Create knowledge_chunks table
CREATE TABLE IF NOT EXISTS knowledge_chunks (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    file_id UUID NOT NULL,
    
    content_blob TEXT NOT NULL,
    embedding VECTOR(1536),
    
    topic TEXT,
    keywords JSONB,
    difficulty_level VARCHAR(50),
    summary TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);
-- Create indexes for knowledge_chunks
CREATE INDEX IF NOT EXISTS idx_chunks_user_id ON knowledge_chunks(user_id);
CREATE INDEX IF NOT EXISTS idx_chunks_file_id ON knowledge_chunks(file_id);
CREATE INDEX IF NOT EXISTS idx_chunks_topic ON knowledge_chunks(topic);
CREATE INDEX IF NOT EXISTS idx_chunks_keywords ON knowledge_chunks USING GIN (keywords);
CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON knowledge_chunks USING ivfflat (embedding vector_cosine_ops);
-- Create teaching_sessions table
CREATE TABLE IF NOT EXISTS teaching_sessions (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    current_topic TEXT,
    question_index INTEGER DEFAULT 0,
    completed BOOLEAN DEFAULT FALSE,
    retrieved_chunks JSONB,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
-- Create index for teaching_sessions
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON teaching_sessions(user_id);
-- Create answers table
CREATE TABLE IF NOT EXISTS answers (
    id UUID PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES teaching_sessions(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    
    created_at TIMESTAMP DEFAULT NOW()
);
-- Create index for answers
CREATE INDEX IF NOT EXISTS idx_answers_session_id ON answers(session_id);
-- Create uploaded_files table
CREATE TABLE IF NOT EXISTS uploaded_files (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(512) NOT NULL,
    file_type VARCHAR(50),
    file_size INTEGER,
    processing_status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP
);
-- Create index for uploaded_files
CREATE INDEX IF NOT EXISTS idx_files_user_id ON uploaded_files(user_id);
CREATE INDEX IF NOT EXISTS idx_files_status ON uploaded_files(processing_status);
