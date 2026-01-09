"""Metadata extraction service using LLM structured output"""
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from typing import List
from schemas import TopicMetadata
import os

class MetadataExtractionService:    
    def __init__(self, model_name: str = "gpt-4.1", temperature: float = 0.7):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        self.metadata_chain = self.llm.with_structured_output(TopicMetadata)
    
    def extract_metadata(self, chunk: Document) -> TopicMetadata:
        prompt = f"""Extract learning metadata from the following text.
Text:
{chunk.page_content}
Identify:
- The main topic or concept
- Key terms and keywords (as a list)
- Difficulty level (beginner, intermediate, or advanced)
- A brief summary (1-2 sentences)
"""
        
        try:
            metadata = self.metadata_chain.invoke(prompt)
            return metadata
        except Exception as e:
            print(f"Error extracting metadata: {e}")
            return TopicMetadata(
                topic="Unknown",
                keywords=[],
                difficulty_level="intermediate",
                summary=chunk.page_content[:200]
            )
    
    def extract_metadata_batch(self, chunks: List[Document]) -> List[TopicMetadata]:
        metadata_list = []
        for chunk in chunks:
            metadata = self.extract_metadata(chunk)
            metadata_list.append(metadata)
        
        return metadata_list
    
    def update_chunk_metadata(self, chunk: Document, metadata: TopicMetadata) -> Document:
        chunk.metadata.update({
            'topic': metadata.topic,
            'keywords': metadata.keywords,
            'difficulty_level': metadata.difficulty_level,
            'summary': metadata.summary
        })
        return chunk
