"""Stupid Student Agent for asking questions"""
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from typing import List, Optional
from schemas import StudentQuestion
import os

class StudentAgent:
    
    PERSONA_PROMPT = """You are a curious but naive student.
Your job is to learn by asking simple but probing questions.
Rules:
- Ask exactly ONE question at a time
- Ask exactly 3 questions total per session
- Base questions ONLY on the provided context
- Escalate difficulty gradually (start simple, get more detailed)
- Do not explain, only ask
- Questions should help reveal understanding gaps
- Be conversational and friendly
"""
    
    def __init__(self, model_name: str = "gpt-4o", temperature: float = 0.7, max_questions: int = 3):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        self.question_chain = self.llm.with_structured_output(StudentQuestion)
        self.max_questions = max_questions
    
    def generate_question(
        self, 
        context_chunks: List[Document], 
        previous_questions: List[str],
        question_index: int
    ) -> Optional[str]:
        if question_index >= self.max_questions:
            return None
        
        context = "\n\n".join([
            f"Context {i+1}:\n{chunk.page_content}"
            for i, chunk in enumerate(context_chunks)
        ])
        
        prev_q_text = "\n".join([
            f"{i+1}. {q}"
            for i, q in enumerate(previous_questions)
        ]) if previous_questions else "None yet"
        
        if question_index == 0:
            difficulty_hint = "Start with a basic, foundational question."
        elif question_index == 1:
            difficulty_hint = "Ask a more detailed question that builds on the first."
        else:
            difficulty_hint = "Ask a challenging question that tests deeper understanding."
        
        prompt = f"""{self.PERSONA_PROMPT}
Context:
{context}
Questions already asked:
{prev_q_text}
This is question {question_index + 1} of {self.max_questions}.
{difficulty_hint}
Ask the next question."""
        
        try:
            result = self.question_chain.invoke(prompt)
            return result.question
        except Exception as e:
            print(f"Error generating question: {e}")
            return f"Can you explain the main concept from the material?"
    
    def should_continue(self, question_index: int) -> bool:
        return question_index < self.max_questions
