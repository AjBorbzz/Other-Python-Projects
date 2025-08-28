# FastAPI SIEM Log Summarizer for Private LLM

## Quick Start (Dev)
```bash
cp .env.example .env
# pull a model once (terminal 1)
docker compose up -d ollama
sleep 4 && docker compose exec ollama ollama pull llama3:8b-instruct
# run api (terminal 2)
docker compose up api


```bash
# llama3 (default or explicit)
curl -X POST http://localhost:8000/summarize -H 'Content-Type: application/json' \
  -d '{"incident_id":"INC-123","provider":"llama3","logs":["..."]}'

# openai (requires OPENAI_API_KEY)
curl -X POST http://localhost:8000/summarize -H 'Content-Type: application/json' \
  -d '{"incident_id":"INC-124","provider":"openai","logs":["..."]}'

```