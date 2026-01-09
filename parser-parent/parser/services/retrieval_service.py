"""Retrieval service with keyword expansion"""
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from typing import List
from sqlalchemy import text
from models import KnowledgeChunk, db
from schemas import KeywordExpansion
from services.embedding_service import EmbeddingService
import os

class RetrievalService:
    def __init__(self, model_name: str = "gpt-4o", temperature: float = 0.7):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        self.expansion_chain = self.llm.with_structured_output(KeywordExpansion)
        self.embedding_service = EmbeddingService()
    
    def expand_keywords(self, query: str) -> List[str]:
        prompt = f"""User wants to learn: "{query}"
Expand this into a comprehensive list of related concepts, synonyms, and prerequisite topics.
Include:
- The main concept
- Related concepts
- Synonyms and alternative terms
- Prerequisite topics needed to understand this
- Common applications or examples
Return only the keywords as a list."""
        
        try:
            result = self.expansion_chain.invoke(prompt)
            return result.keywords
        except Exception as e:
            print(f"Error expanding keywords: {e}")
            return [query]
    
    def retrieve_chunks(
        self, 
        query: str, 
        user_id: str, 
        top_k: int = 6
    ) -> tuple[List[Document], List[str]]:
        expanded_keywords = self.expand_keywords(query)
        
        query_embedding = self.embedding_service.embed_text(query)
        
        sql_query = text("""
            SELECT *
            FROM knowledge_chunks
            WHERE user_id = :user_id
            AND (
                keywords ?| :keywords
                OR topic ILIKE ANY(:topic_patterns)
            )
            ORDER BY embedding <=> :query_embedding
            LIMIT :limit
        """)
        
        topic_patterns = [f"%{kw}%" for kw in expanded_keywords]
        
        try:
            result = db.session.execute(
                sql_query,
                {
                    'user_id': user_id,
                    'keywords': expanded_keywords,
                    'topic_patterns': topic_patterns,
                    'query_embedding': str(query_embedding),
                    'limit': top_k
                }
            )
            
            chunks = result.fetchall()
            
            documents = []
            for chunk in chunks:
                doc = Document(
                    page_content=chunk.content_blob,
                    metadata={
                        'id': str(chunk.id),
                        'topic': chunk.topic,
                        'keywords': chunk.keywords,
                        'difficulty_level': chunk.difficulty_level,
                        'summary': chunk.summary
                    }
                )
                documents.append(doc)
            
            return documents, expanded_keywords
            
        except Exception as e:
            print(f"Error retrieving chunks: {e}")
            chunks = KnowledgeChunk.query.filter_by(user_id=user_id).limit(top_k).all()
            documents = [chunk.to_langchain_document() for chunk in chunks]
            return documents, expanded_keywords
    
    def retrieve_by_topic(self, topic: str, user_id: str, top_k: int = 6) -> List[Document]:
        chunks = KnowledgeChunk.query.filter(
            KnowledgeChunk.user_id == user_id,
            KnowledgeChunk.topic.ilike(f"%{topic}%")
        ).limit(top_k).all()
        
        return [chunk.to_langchain_document() for chunk in chunks]
