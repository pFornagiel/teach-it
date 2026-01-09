from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class TopicMetadata(BaseModel):
    topic: str = Field(description="Main topic or concept covered in this chunk")
    keywords: List[str] = Field(description="Key terms and concepts")
    difficulty_level: DifficultyLevel = Field(description="Difficulty level of the content")
    summary: str = Field(description="Brief summary of the content")

class KeywordExpansion(BaseModel):
    keywords: List[str] = Field(description="Expanded list of related keywords, synonyms, and prerequisite topics")

class StudentQuestion(BaseModel):
    question: str = Field(description="A simple, probing question based on the context")

class EvaluationResult(BaseModel):
    score: str = Field(description="Grade from A to F")
    correct_concepts: List[str] = Field(description="Concepts the user understood correctly")
    misconceptions: List[str] = Field(description="Misconceptions or errors in understanding")
    improvement_tips: List[str] = Field(description="Specific tips for improvement")

# Request/Response schemas for API endpoints
class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    status: str
    message: str

class ChunkResponse(BaseModel):
    id: str
    content: str
    topic: Optional[str]
    keywords: Optional[List[str]]
    difficulty_level: Optional[str]
    summary: Optional[str]

class RetrievalRequest(BaseModel):
    query: str = Field(description="Learning topic or question")
    user_id: str = Field(description="User ID for filtering")
    top_k: int = Field(default=6, description="Number of chunks to retrieve")

class RetrievalResponse(BaseModel):
    chunks: List[ChunkResponse]
    expanded_keywords: List[str]

class StartSessionRequest(BaseModel):
    user_id: str
    topic: str = Field(description="Topic to learn about")

class StartSessionResponse(BaseModel):
    session_id: str
    topic: str
    first_question: str

class AnswerQuestionRequest(BaseModel):
    session_id: str
    answer: str

class AnswerQuestionResponse(BaseModel):
    session_id: str
    next_question: Optional[str]
    session_completed: bool

class EvaluateSessionRequest(BaseModel):
    session_id: str

class EvaluateSessionResponse(BaseModel):
    session_id: str
    evaluation: EvaluationResult
    all_qa_pairs: List[dict]
