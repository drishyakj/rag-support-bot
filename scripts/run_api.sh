#!/usr/bin/env bash
set -e
export $(grep -v '^#' .env | xargs)

if [ "$1" = "clean" ]; then
  rm -rf data/raw data/clean data/chroma
  mkdir -p data/raw data/clean
fi

if [ -z "$(ls -A data/clean 2>/dev/null)" ]; then
  python app/crawl.py
fi

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
