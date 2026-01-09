import os
import glob
import json
from typing import List, Dict, Any

class MockDocument:
    def __init__(self, page_content: str, metadata: Dict[str, Any] = None):
        self.page_content = page_content
        self.metadata = metadata or {}

def load_file_mock(file_path: str) -> List[MockDocument]:
    try:
        if file_path.endswith(".txt"):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return [MockDocument(content, {"source": file_path, "type": "text"})]
        
        elif file_path.endswith(".csv"):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return [MockDocument(content, {"source": file_path, "type": "csv"})]
        
        elif file_path.endswith((".pdf", ".docx")):
            return [MockDocument(
                f"[Simulated content from {os.path.basename(file_path)}]\n"
                f"This would contain the extracted text from the {file_path.split('.')[-1].upper()} file.",
                {"source": file_path, "type": file_path.split('.')[-1]}
            )]
        
        elif file_path.endswith((".png", ".jpg", ".jpeg")):
            return [MockDocument(
                f"[Simulated OCR/image analysis from {os.path.basename(file_path)}]\n"
                f"This would contain extracted text or image descriptions.",
                {"source": file_path, "type": "image"}
            )]
        
        else:
            raise ValueError(f"Unsupported file type: {file_path}")
    
    except Exception as e:
        print(f"Error loading file {file_path}: {str(e)}")
        return []

def load_files_from_directory_mock(directory_path: str) -> List[MockDocument]:
    documents = []
    supported_extensions = [".pdf", ".docx", ".txt", ".csv", ".png", ".jpg", ".jpeg"]
    
    if not os.path.exists(directory_path):
        print(f"Directory {directory_path} does not exist")
        return documents
    
    for ext in supported_extensions:
        pattern = os.path.join(directory_path, f"*{ext}")
        files = glob.glob(pattern)
        
        for file_path in files:
            print(f"Loading file: {file_path}")
            docs = load_file_mock(file_path)
            
            for doc in docs:
                doc.metadata.update({
                    'source_file': file_path,
                    'file_type': ext,
                    'directory': directory_path
                })
            
            documents.extend(docs)
    
    return documents

def save_documents_to_json_mock(documents: List[MockDocument], output_path: str):
    doc_data = []
    for doc in documents:
        doc_data.append({
            'content': doc.page_content,
            'metadata': doc.metadata
        })
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(doc_data, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(documents)} documents to {output_path}")

def load_documents_from_json_mock(input_path: str) -> List[MockDocument]:
    with open(input_path, 'r', encoding='utf-8') as f:
        doc_data = json.load(f)
    
    documents = []
    for item in doc_data:
        doc = MockDocument(
            page_content=item['content'],
            metadata=item['metadata']
        )
        documents.append(doc)
    
    return documents

def simulate_text_splitting(documents: List[MockDocument], chunk_size: int = 1000) -> List[MockDocument]:
    split_docs = []
    
    for doc in documents:
        content = doc.page_content
        
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i + chunk_size]
            if chunk.strip():
                chunk_metadata = doc.metadata.copy()
                chunk_metadata['chunk_index'] = len(split_docs)
                chunk_metadata['chunk_size'] = len(chunk)
                
                split_docs.append(MockDocument(chunk, chunk_metadata))
    
    return split_docs

def simulate_vector_search(documents: List[MockDocument], query: str, k: int = 3) -> List[MockDocument]:
    query_lower = query.lower()
    scored_docs = []
    
    for doc in documents:
        content_lower = doc.page_content.lower()
        score = content_lower.count(query_lower)
        if score > 0:
            scored_docs.append((score, doc))
    
    scored_docs.sort(key=lambda x: x[0], reverse=True)
    return [doc for score, doc in scored_docs[:k]]

def main():
    print("=== LangChain File Processing and Storage Demo ===\n")
    print("This demo simulates LangChain functionality without requiring installation.\n")
    
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
        docs = load_files_from_directory_mock(lecture_dir)
        all_documents.extend(docs)
        print(f"Loaded {len(docs)} documents from {lecture_dir}")
    
    print(f"\n=== Total Documents Loaded: {len(all_documents)} ===")
    
    for i, doc in enumerate(all_documents):
        print(f"\nDocument {i+1}:")
        print(f"  Source: {doc.metadata.get('source_file', 'Unknown')}")
        print(f"  Type: {doc.metadata.get('file_type', 'Unknown')}")
        print(f"  Content preview: {doc.page_content[:200]}...")
    
    json_output_path = "processed_documents_demo.json"
    save_documents_to_json_mock(all_documents, json_output_path)
    
    print(f"\n=== Testing JSON Storage Reliability ===")
    loaded_docs = load_documents_from_json_mock(json_output_path)
    print(f"Successfully loaded {len(loaded_docs)} documents from JSON storage")
    
    print(f"\n=== Simulating Text Splitting ===")
    split_docs = simulate_text_splitting(all_documents, chunk_size=500)
    print(f"Split {len(all_documents)} documents into {len(split_docs)} chunks")
    
    print(f"\n=== Simulating Vector Search and Retrieval ===")
    test_queries = [
        "korylator lumiczny",
        "agarwia meryno", 
        "neurokorelacje roślin",
        "predykcyjne sieci"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = simulate_vector_search(split_docs, query, k=3)
        print(f"Found {len(results)} relevant documents:")
        for j, result in enumerate(results):
            print(f"  Result {j+1}: {result.metadata.get('source_file', 'Unknown')}")
            print(f"    Content: {result.page_content[:150]}...")
    
    print(f"\n=== Demo Complete ===")
    print(f"Successfully processed {len(all_documents)} documents")
    print(f"Documents saved to: {json_output_path}")
    print("Demonstrated LangChain capabilities:")
    print("  ✓ Multi-format file loading (PDF, DOCX, TXT, CSV, Images)")
    print("  ✓ Document metadata management")
    print("  ✓ Reliable JSON storage and retrieval")
    print("  ✓ Text chunking for better processing")
    print("  ✓ Vector similarity search simulation")
    print("  ✓ Retriever pattern implementation")
    
    print(f"\nTo use with actual LangChain:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Set OpenAI API key (optional, HuggingFace fallback available)")
    print("3. Run the full file_opener.py script")

if __name__ == "__main__":
    main()