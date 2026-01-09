from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

def build_tutor(vectorstore):
    llm = ChatOpenAI(
        model="gpt-4.1",
        temperature=0.2
    )

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""
Jesteś inteligentnym nauczycielem.
Uczysz użytkownika WYŁĄCZNIE na podstawie poniższych materiałów.

Materiały:
{context}

Zadanie:
1. Wytłumacz zagadnienie jasno i krok po kroku.
2. Podaj przykład jeżeli ma sens.

Pytanie użytkownika:
{question}
"""
    )

    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True
    )
