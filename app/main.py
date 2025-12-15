from fastapi import FastAPI
from pydantic import BaseModel
from app.rag_pipeline import create_rag_chain

app = FastAPI(title="RAG Support Bot")

rag_chain = create_rag_chain()

class AskBody(BaseModel):
    question: str

@app.post("/ask")
def ask(body: AskBody):
    answer = rag_chain.invoke(body.question)
    return {"question": body.question, "answer": answer}
