import json
import logging
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
# from backend.app import app  # Removed to avoid circular import
# Actually, I don't need app here. I need to be careful with imports.

import sys
import os

# Helper to ensure we can import from agents folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.loaders import load_file
from agents.vectorstore import build_vectorstore
from agents.tutor import build_tutor

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StudentAgent:
    def __init__(self):
        self.vectorstore = None
        self.tutor_chain = None
        self.current_topic = None
        self.history = []
        self.questions_asked = 0
        self.target_questions = 3
        self.evaluator_llm = ChatOpenAI(model="gpt-4.1", temperature=0.3)
        self.topic_generator_llm = ChatOpenAI(model="gpt-4.1", temperature=0.5)

    def _invoke_with_retry(self, llm, prompt, retries=10):
        """Helper to invoke LLM with retries."""
        for attempt in range(retries):
            try:
                response = llm.invoke(prompt)
                return response
            except Exception as e:
                logger.warning(f"LLM invoke failed (attempt {attempt+1}/{retries}): {e}")
                if attempt == retries - 1:
                    raise e
        return None

    def process_files(self, file_paths: list[str]):
        """Load files and build vectorstore."""
        logger.info(f"Processing files: {file_paths}")
        try:
            self.vectorstore = build_vectorstore(file_paths)
            logger.info("Vectorstore built successfully.")
        except Exception as e:
            logger.error(f"Error building vectorstore: {e}")
            raise e

    def generate_topics(self) -> list[str]:
        """Generate topics based on loaded documents."""
        if not self.vectorstore:
            return ["No files loaded. Please upload content first."]

        # We can retrieve some general context or just use a generic prompt if we had the full text. 
        # Vectorstore doesn't easily give "all text". 
        # For simplicity, we might assume the files are small enough or we just sample.
        # Let's try to query the vectorstore for "Summary of main topics".
        
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5})
        docs = retriever.invoke("What are the main topics covered in this material?")
        context = "\n".join([d.page_content for d in docs])

        prompt = f"""
        Analyze the following text and extract 5 key learnable topics suitable for a student.
        Return ONLY a JSON array of strings, e.g. ["Topic 1", "Topic 2"].
        
        Text:
        {context[:4000]}
        """

        response = self._invoke_with_retry(self.topic_generator_llm, prompt)
        try:
            content = response.content.strip()
            # Handle markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:-3]
            topics = json.loads(content)
            if isinstance(topics, dict) and 'topics' in topics:
                 return topics['topics']
            return topics
        except Exception as e:
            logger.error(f"Error parsing topics: {e}")
            return ["Error generating topics. Try again."]

    def start_learning(self, topic: str):
        """Initialize learning session for a topic."""
        self.current_topic = topic
        self.questions_asked = 0
        self.history = []
        if self.vectorstore:
            self.tutor_chain = build_tutor(self.vectorstore)
        else:
            raise ValueError("Vectorstore not initialized. Upload files first.")

    def chat(self, user_answer: str = None) -> dict:
        """
        Handle a chat turn.
        If user_answer is None, it means we are starting or just want the next question.
        """
        finished = False
        
        if user_answer:
            self.history.append({"role": "user", "content": user_answer})
            self.questions_asked += 1
        
        if self.questions_asked >= self.target_questions:
            return {"finished": True, "message": "Great work! You've completed the session for this topic. Ready for evaluation?"}

        # Generate next question
        # We use the tutor chain which is a RetrievalQA. 
        # We need to craft the prompt carefully. The tutor.py prompt expects {context} and {question}.
        # Here "question" is actually the "instruction to the tutor" to generate a question for the student.
        
        # NOTE: The existing tutor.py returns a direct answer to a user's question. 
        # But here we want the AGENT to ask the questions (Socratic method).
        # We might need to adjust how we use the tutor chain or just call the LLM directly with context.
        # Let's use the vectorstore retrieval manually + custom prompt for Socratic behavior.

        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
        # Determine what to ask about.
        query_for_context = f"Concepts related to {self.current_topic}"
        if self.history:
              query_for_context += f" related to previous answer: {self.history[-1]['content']}"
        
        docs = retriever.invoke(query_for_context)
        context = "\n".join([d.page_content for d in docs])
        
        history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.history])

        socratic_prompt = f"""
        You are a Socratic tutor teaching the topic: {self.current_topic}.
        Your goal is to verify the student's understanding by asking insightful questions one by one.
        Do NOT lecture. Ask a question that requires the student to explain the concept.
        
        Context from materials:
        {context}
        
        Conversation History:
        {history_text}
        
        Task:
        - If the student just answered, evaluate it briefly (internally) and ask the follow-up question. 
        - If this is the start, ask the first fundamental question about {self.current_topic}.
        - Ensure the question is answered by the materials provided.
        - Return ONLY the question text.
        """
        
        response = self._invoke_with_retry(self.evaluator_llm, socratic_prompt)
        next_question = response.content.strip()
        
        self.history.append({"role": "assistant", "content": next_question})
        
        return {
            "finished": False,
            "question": next_question
        }

    def evaluate(self) -> dict:
        """Evaluate the entire session."""
        history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.history])
        
        prompt = f"""
        Review the following tutoring session transcript for the topic: {self.current_topic}.
        Evaluate the student's understanding.
        
        Transcript:
        {history_text}
        
        Return a JSON object with:
        - grade (A-F)
        - comments (General feedback)
        - details (Array of objects with "point" (what was good/bad) and "status" (correct/partial/wrong))
        """
        
        response = self._invoke_with_retry(self.evaluator_llm, prompt)
        try:
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            return json.loads(content)
        except Exception as e:
            logger.error(f"Error parsing evaluation: {e}")
            return {
                "grade": "N/A",
                "comments": "Error generating evaluation.",
                "details": []
            }
