"""Master Evaluation Agent for grading user responses"""
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from typing import List, Dict
from schemas import EvaluationResult
import os

class EvaluationAgent:
    
    EVALUATION_PROMPT = """You are a subject matter expert and educator.
Your task is to evaluate a student's understanding based on:
1. The original source material they studied
2. The questions they were asked
3. Their answers to those questions
Provide a comprehensive evaluation that includes:
- An overall grade (A, B, C, D, or F)
- Concepts they understood correctly
- Any misconceptions or errors
- Specific tips for improvement
Be constructive and encouraging while being honest about gaps in understanding."""
    
    def __init__(self, model_name: str = "gpt-4o", temperature: float = 0.8):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        self.evaluation_chain = self.llm.with_structured_output(EvaluationResult)
    
    def evaluate_session(
        self,
        source_material: List[Document],
        qa_pairs: List[Dict[str, str]]
    ) -> EvaluationResult:
        source_text = "\n\n".join([
            f"Source {i+1}:\n{chunk.page_content}"
            for i, chunk in enumerate(source_material)
        ])
        
        qa_text = "\n\n".join([
            f"Q{i+1}: {pair['question']}\nA{i+1}: {pair['answer']}"
            for i, pair in enumerate(qa_pairs)
        ])
        
        prompt = f"""{self.EVALUATION_PROMPT}
Original Source Material:
{source_text}
Student's Q&A Session:
{qa_text}
Provide your evaluation."""
        
        try:
            result = self.evaluation_chain.invoke(prompt)
            return result
        except Exception as e:
            print(f"Error evaluating session: {e}")
            return EvaluationResult(
                score="C",
                correct_concepts=["Attempted to engage with the material"],
                misconceptions=["Unable to fully evaluate due to technical error"],
                improvement_tips=["Please try again or contact support"]
            )
    
    def quick_evaluate_answer(
        self,
        question: str,
        answer: str,
        context: List[Document]
    ) -> Dict[str, any]:
        context_text = "\n\n".join([chunk.page_content for chunk in context])
        
        prompt = f"""Based on this context:
{context_text}
Question: {question}
Answer: {answer}
Is this answer correct? Provide brief feedback (2-3 sentences)."""
        
        try:
            response = self.llm.invoke(prompt)
            return {
                'feedback': response.content,
                'is_correct': 'correct' in response.content.lower() or 'yes' in response.content.lower()
            }
        except Exception as e:
            print(f"Error in quick evaluation: {e}")
            return {
                'feedback': "Unable to evaluate at this time.",
                'is_correct': None
            }
