import os
import glob
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough

load_dotenv()

CLEAN_DIR = "data/clean"
CHROMA_DIR = "data/chroma"


def load_docs():
    docs = []
    for path in sorted(glob.glob(os.path.join(CLEAN_DIR, "*.txt"))):
        with open(path, "r", encoding="utf-8") as f:
            text = f.read().strip()
            if text:
                docs.append(text)
    return docs


def prepare_vectorstore():
    docs = load_docs()
    if not docs:
        print("No documents found in data/clean/. Run crawl first.")
        return None

    splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)
    chunks = []
    for doc in docs:
        chunks.extend(splitter.split_text(doc))

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    os.makedirs(CHROMA_DIR, exist_ok=True)
    db = Chroma.from_texts(chunks, embedding=embeddings, persist_directory=CHROMA_DIR)
    db.persist()
    return db


def load_vectorstore():
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    return Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)


def create_rag_chain():
    if not os.path.exists(CHROMA_DIR) or not os.listdir(CHROMA_DIR):
        db = prepare_vectorstore()
    else:
        db = load_vectorstore()

    retriever = db.as_retriever(search_kwargs={"k": 3})
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    prompt = ChatPromptTemplate.from_template("""
    Answer the question based only on the following context.
    If you cannot answer from the context, say "I don't have information about that."

    Context:
    {context}

    Question: {question}

    Answer:
    """)

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | model
        | StrOutputParser()
    )

    return chain
