from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from app.rag_pipeline import create_rag_chain

load_dotenv()

app = FastAPI(title="RAG Support Bot")

rag_chain = create_rag_chain()


class CrawlRequest(BaseModel):
    baseUrl: str


class AskRequest(BaseModel):
    question: str


# @app.post("/crawl")
# def crawl_site(request: CrawlRequest):
#     return {"message": f"Received crawl request for {request.baseUrl}. Crawling is managed separately."}


@app.post("/ask")
def ask_question(request: AskRequest):
    answer = rag_chain.invoke(request.question)
    return {"question": request.question, "answer": answer}

