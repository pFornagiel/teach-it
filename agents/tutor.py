from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

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

    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # Nowoczesny łańcuch LCEL zastępujący RetrievalQA
    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain
