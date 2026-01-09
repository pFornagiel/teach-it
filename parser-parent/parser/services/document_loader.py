"""Document loading service using LangChain loaders"""
from langchain_community.document_loaders import (
    UnstructuredPDFLoader,
    UnstructuredWordDocumentLoader,
    TextLoader,
    CSVLoader,
    UnstructuredImageLoader
)
from langchain_core.documents import Document
from typing import List
import os

class DocumentLoaderService:
    
    @staticmethod
    def load_file(file_path: str) -> List[Document]:
        try:
            if file_path.endswith(".pdf"):
                return UnstructuredPDFLoader(file_path, mode="elements").load()
            
            elif file_path.endswith(".docx"):
                return UnstructuredWordDocumentLoader(file_path).load()
            
            elif file_path.endswith(".txt"):
                return TextLoader(file_path, encoding='utf-8').load()
            
            elif file_path.endswith(".csv"):
                return CSVLoader(file_path).load()
            
            elif file_path.endswith((".png", ".jpg", ".jpeg")):
                return UnstructuredImageLoader(file_path).load()
            
            else:
                raise ValueError(f"Unsupported file type: {file_path}")
                
        except Exception as e:
            raise Exception(f"Error loading file {file_path}: {str(e)}")
    
    @staticmethod
    def add_file_metadata(documents: List[Document], file_path: str, file_id: str, user_id: str) -> List[Document]:
        file_ext = os.path.splitext(file_path)[1]
        
        for doc in documents:
            doc.metadata.update({
                'source_file': file_path,
                'file_type': file_ext,
                'file_id': file_id,
                'user_id': user_id
            })
        
        return documents
