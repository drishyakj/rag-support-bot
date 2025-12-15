# RAG Support Bot

This project implements a **Retrieval-Augmented Generation (RAG)** support bot using the **LangChain** framework and **OpenAI** models.  
It crawls a website, cleans the text, generates embeddings, stores them in a **Chroma** vector database, and exposes a **FastAPI** endpoint that answers questions based only on the crawled content.

---

## 1. Project Overview

The workflow consists of the following steps:

1. **Crawling:** The bot crawls a specified website and saves text content locally.  
2. **Cleaning:** The raw text is cleaned and stored in the `data/clean` directory.  
3. **Indexing:** Clean text is chunked, embedded using `text-embedding-3-small`, and stored in Chroma.  
4. **RAG Chain:** A retriever and LLM (`gpt-4o-mini`) are combined using LangChain.  
5. **API:** A `/ask` endpoint accepts a question and returns an answer based only on retrieved context.

---

## 2. Folder Structure

```

rag-support-bot/
├── .env
├── requirements.txt
├── app/
│   ├── crawl.py
│   ├── rag_pipeline.py
│   └── main.py
└── scripts/
└── run_api.sh

````

---

## 3. Environment Setup

### Create and activate virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
````

### Install dependencies

```bash
pip install -r requirements.txt
```

### Environment variables

Create a `.env` file in the project root:

```
OPENAI_API_KEY=sk-your-key-here
SEED_URL=https://en.wikipedia.org/wiki/Artificial_intelligence
MAX_PAGES=30
```

---

## 4. Running the Application

Use the provided script to handle everything — crawl, index, and start the API.

### Clean build and run

```bash
./scripts/run_api.sh clean
```

This will:

* Remove old data
* Crawl the website specified in `.env`
* Generate embeddings and build the Chroma index
* Start the FastAPI server on port **8000**

### Reuse existing data

```bash
./scripts/run_api.sh
```

If the cleaned data and Chroma index already exist, they will be reused.

---

## 5. Testing the API

Once the server is running:

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Who coined the term artificial intelligence?"}'
```

Example response:

```json
{
  "question": "Who coined the term artificial intelligence?",
  "answer": "John McCarthy coined the term 'artificial intelligence' in 1956."
}
```

---

## 6. Components

| File              | Description                                       |
| ----------------- | ------------------------------------------------- |
| `crawl.py`        | Crawls and stores website text.                   |
| `rag_pipeline.py` | Splits, embeds, and creates the RAG chain.        |
| `main.py`         | Exposes FastAPI `/ask` endpoint.                  |
| `run_api.sh`      | Orchestrates crawling, indexing, and API startup. |

---

## 7. Notes

* The first run may take longer due to model downloads and embeddings generation.
* Embeddings are stored locally in `data/chroma/`.
* You can adjust the number of chunks or retriever results (`k`) in `rag_pipeline.py`.
* To change the source site, update the `SEED_URL` in `.env`.

---

## 8. Example Queries

* “What is artificial intelligence?”
* “Who founded the field of AI?”
* “When was AI first introduced?”
* “What are the main applications of AI?”

---

This project demonstrates the complete RAG pipeline — from data ingestion to retrieval and response generation — using **LangChain**, **OpenAI**, and **Chroma**.

```

