"""Embedding service for generating vector embeddings"""
from langchain_openai import OpenAIEmbeddings
from typing import List
import os

class EmbeddingService:
    
    def __init__(self, model: str = "text-embedding-ada-002"):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.embeddings = OpenAIEmbeddings(model=model)
    
    def embed_text(self, text: str) -> List[float]:
        return self.embeddings.embed_query(text)
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return self.embeddings.embed_documents(texts)
