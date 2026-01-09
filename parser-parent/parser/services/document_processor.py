"""Document processing service that orchestrates the ingestion pipeline"""
from typing import List
import uuid
from datetime import datetime
from models import KnowledgeChunk, UploadedFile, db
from services.document_loader import DocumentLoaderService
from services.chunking_service import ChunkingService
from services.metadata_service import MetadataExtractionService
from services.embedding_service import EmbeddingService

class DocumentProcessor:
    def __init__(self, chunk_size: int = 750, chunk_overlap: int = 150):
        self.loader = DocumentLoaderService()
        self.chunker = ChunkingService(chunk_size, chunk_overlap)
        self.metadata_extractor = MetadataExtractionService()
        self.embedding_service = EmbeddingService()
    
    def process_file(self, file_path: str, file_id: str, user_id: str) -> dict:
        try:
            uploaded_file = UploadedFile.query.get(file_id)
            if uploaded_file:
                uploaded_file.processing_status = 'processing'
                db.session.commit()
            
            documents = self.loader.load_file(file_path)
            documents = self.loader.add_file_metadata(documents, file_path, file_id, user_id)
            
            chunks = self.chunker.split_documents(documents)
            
            chunk_records = []
            for chunk in chunks:
                metadata = self.metadata_extractor.extract_metadata(chunk)
                
                embedding = self.embedding_service.embed_text(chunk.page_content)
                
                chunk_record = KnowledgeChunk(
                    id=uuid.uuid4(),
                    user_id=user_id,
                    file_id=file_id,
                    content_blob=chunk.page_content,
                    embedding=embedding,
                    topic=metadata.topic,
                    keywords=metadata.keywords,
                    difficulty_level=metadata.difficulty_level,
                    summary=metadata.summary
                )
                chunk_records.append(chunk_record)
            
            db.session.bulk_save_objects(chunk_records)
            
            if uploaded_file:
                uploaded_file.processing_status = 'completed'
                uploaded_file.processed_at = datetime.utcnow()
                
            db.session.commit()
            
            return {
                'success': True,
                'chunks_created': len(chunk_records),
                'file_id': file_id
            }
            
        except Exception as e:
            if uploaded_file:
                uploaded_file.processing_status = 'failed'
                uploaded_file.error_message = str(e)
                db.session.commit()
            
            return {
                'success': False,
                'error': str(e),
                'file_id': file_id
            }
