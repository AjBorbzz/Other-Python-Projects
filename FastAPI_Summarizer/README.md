# FastAPI SIEM Log Summarizer for Private LLM

## Quick Start (Dev)
```bash
cp .env.example .env
# pull a model once (terminal 1)
docker compose up -d ollama
sleep 4 && docker compose exec ollama ollama pull llama3:8b-instruct
# run api (terminal 2)
docker compose up api