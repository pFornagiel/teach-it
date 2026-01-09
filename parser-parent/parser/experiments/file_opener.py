from langchain_community.document_loaders import (
    UnstructuredPDFLoader,
    UnstructuredWordDocumentLoader,
    TextLoader,
    CSVLoader,
    UnstructuredImageLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
import os
import glob
from typing import List, Dict, Any
import json

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
        print(f"Error loading file {file_path}: {str(e)}")
        return []

def load_files_from_directory(directory_path: str) -> List[Document]:
    documents = []
    supported_extensions = [".pdf", ".docx", ".txt", ".csv", ".png", ".jpg", ".jpeg", ".dat", ".text", ".md"]
    
    if not os.path.exists(directory_path):
        print(f"Directory {directory_path} does not exist")
        return documents
    
    for ext in supported_extensions:
        pattern = os.path.join(directory_path, f"*{ext}")
        files = glob.glob(pattern)
        
        for file_path in files:
            print(f"Loading file: {file_path}")
            docs = load_file(file_path)
            
            for doc in docs:
                doc.metadata.update({
                    'source_file': file_path,
                    'file_type': ext,
                    'directory': directory_path
                })
            
            documents.extend(docs)
    
    return documents

def create_text_splitter(chunk_size: int = 1000, chunk_overlap: int = 200) -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )

def create_vector_store(documents: List[Document], embeddings_model=None) -> FAISS:
    if not documents:
        raise ValueError("No documents provided for vector store creation")
    
    if embeddings_model is None:
        try:
            embeddings_model = OpenAIEmbeddings()
        except Exception as e:
            print(f"OpenAI embeddings not available: {e}")
            print("Using HuggingFace embeddings as fallback")
            from langchain.embeddings import HuggingFaceEmbeddings
            embeddings_model = HuggingFaceEmbeddings()
    
    text_splitter = create_text_splitter()
    split_docs = text_splitter.split_documents(documents)
    
    vector_store = FAISS.from_documents(split_docs, embeddings_model)
    return vector_store

def save_documents_to_json(documents: List[Document], output_path: str):
    doc_data = []
    for doc in documents:
        doc_data.append({
            'content': doc.page_content,
            'metadata': doc.metadata
        })
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(doc_data, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(documents)} documents to {output_path}")

def load_documents_from_json(input_path: str) -> List[Document]:
    with open(input_path, 'r', encoding='utf-8') as f:
        doc_data = json.load(f)
    
    documents = []
    for item in doc_data:
        doc = Document(
            page_content=item['content'],
            metadata=item['metadata']
        )
        documents.append(doc)
    
    return documents

def main():
    print("=== LangChain File Processing and Storage Test ===\n")
    
    base_path = "../../../hackathon_source_materials"
    lecture_dirs = [
        os.path.join(base_path, "lecture_1"),
        os.path.join(base_path, "lecture_2"), 
        os.path.join(base_path, "lecture_3"),
        os.path.join(base_path, "lecture_4")
    ]
    
    all_documents = []
    
    for lecture_dir in lecture_dirs:
        print(f"\n--- Processing {lecture_dir} ---")
        docs = load_files_from_directory(lecture_dir)
        all_documents.extend(docs)
        print(f"Loaded {len(docs)} documents from {lecture_dir}")
    
    print(f"\n=== Total Documents Loaded: {len(all_documents)} ===")
    
    for i, doc in enumerate(all_documents):
        print(f"\nDocument {i+1}:")
        print(f"  Source: {doc.metadata.get('source_file', 'Unknown')}")
        print(f"  Type: {doc.metadata.get('file_type', 'Unknown')}")
        print(f"  Content preview: {doc.page_content[:200]}...")
    
    json_output_path = "processed_documents.json"
    save_documents_to_json(all_documents, json_output_path)
    
    print(f"\n=== Testing JSON Storage Reliability ===")
    loaded_docs = load_documents_from_json(json_output_path)
    print(f"Successfully loaded {len(loaded_docs)} documents from JSON storage")
    
    try:
        print(f"\n=== Creating Vector Store and Retriever ===")
        vector_store = create_vector_store(all_documents)
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})
        
        test_queries = [
            "korylator lumiczny",
            "agarwia meryno", 
            "neurokorelacje roślin",
            "predykcyjne sieci"
        ]
        
        print(f"\n=== Testing Retrieval ===")
        for query in test_queries:
            print(f"\nQuery: '{query}'")
            results = retriever.get_relevant_documents(query)
            print(f"Found {len(results)} relevant documents:")
            for j, result in enumerate(results):
                print(f"  Result {j+1}: {result.metadata.get('source_file', 'Unknown')}")
                print(f"    Content: {result.page_content[:150]}...")
        
        vector_store.save_local("faiss_index")
        print(f"\nVector store saved to 'faiss_index' directory")
        
    except Exception as e:
        print(f"Error creating vector store: {e}")
        print("This might be due to missing OpenAI API key or network issues")
    
    print(f"\n=== LangChain Test Complete ===")
    print(f"Successfully processed {len(all_documents)} documents")
    print(f"Documents saved to: {json_output_path}")
    print("Vector store created and saved (if embeddings were available)")

if __name__ == "__main__":
    main()
