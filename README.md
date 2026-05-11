# NourisHer — FastAPI + LLaMA fine-tuning + Postgres (pgvector)

This repository contains a minimal FastAPI service that accepts NDJSON input, runs generation with a LLaMA-family model, and stores inputs/outputs in a Postgres database with pgvector support for embeddings. It also includes a QLoRA/LoRA fine-tuning script tuned for low-VRAM environments, tests and examples.

What I added

- FastAPI app (src/main.py) with a streaming endpoint at `/stream` that accepts `application/x-ndjson` and stores results in Postgres.
- SQLAlchemy models and Alembic migration to create tables and the `vector` extension.
- Docker Compose file to run Postgres with pgvector.
- QLoRA/LoRA training script: `scripts/finetune_qlora.py` (suitable for small experiments on low VRAM; tune params carefully).
- Examples under `examples/` and a unit test `tests/test_stream.py` that patches DB and model for local testing.

Quick start (local)

1) Prerequisites

- Python 3.11+
- Docker (for Postgres with pgvector)

2) Start Postgres with pgvector

```bash
docker compose up -d postgres
```

3) Create a virtual environment and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
# optional ML dependencies for training and inference
pip install transformers accelerate datasets peft bitsandbytes safetensors huggingface_hub
```

4) Configure environment variables (optional)

```bash
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/nourisher"
export MODEL_PATH="ml/models/finetuned-llama"
export LOAD_IN_4BIT="true"
export SYSTEM_PROMPT_PATH="configs/system_prompt.txt"
```

Or copy the template and edit:

```bash
cp .env.example .env
```

5) Apply Alembic migrations (optional if you rely on auto-create)

```bash
alembic upgrade head
```

6) Run the FastAPI app

```bash
uvicorn nourisher.main:app --reload --host 0.0.0.0 --port 8000
```

7) Verify health

```bash
curl http://localhost:8000/health
```

8) Stream output to frontend via SSE

```bash
curl -N -H "Content-Type: application/json" \
  -d '{"prompt":"Age 28, weight 44.6, height 152.0, ..."}' \
  http://localhost:8000/stream/sse
```

9) Stream NDJSON data to the API (batch ingest)

```bash
curl -X POST -H "Content-Type: application/x-ndjson" \
  --data-binary @examples/data.ndjson \
  http://localhost:8000/stream
```

Docker Compose (API + Postgres)

```bash
docker compose up -d
```

The API will be available at `http://localhost:8000`.

API documentation (OpenAPI)

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

API overview

- `GET /health` -> health check
- `POST /stream` -> ingest NDJSON, run model inference, store records
- `POST /stream/sse` -> stream model output via Server-Sent Events

Request/response examples

1) Health check

```bash
curl http://localhost:8000/health
```

Response:

```json
{"status":"ok"}
```

2) NDJSON ingestion (batch)

```bash
curl -X POST -H "Content-Type: application/x-ndjson" \
  --data-binary @examples/data.ndjson \
  http://localhost:8000/stream
```

Response:

```json
{"status":"ok"}
```

1) SSE streaming (frontend friendly)

```bash
curl -N -H "Content-Type: application/json" \
  -d '{"prompt":"Age 28, weight 44.6, height 152.0, ..."}' \
  http://localhost:8000/stream/sse
```

Each SSE event is a JSON object:

```json
{"text":"pcos"}
```

Browser example:

```js
const source = new EventSource("http://localhost:8000/stream/sse");
source.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.text);
};
```

Fine-tuning with QLoRA / LoRA (low-VRAM)

- The script `scripts/finetune_qlora.py` is a minimal example that uses PEFT/LoRA and supports 4-bit quantization (QLoRA) via bitsandbytes. On a 4GB VRAM GPU you must use very small batch sizes and aggressive gradient accumulation. Example command:

```bash
# example using accelerate
accelerate launch --num_processes 1 scripts/finetune_qlora.py \
  --base_model <BASE_MODEL> \
  --dataset examples/finetune_example.jsonl \
  --output_dir ml/models/finetuned-llama \
  --use_4bit
```

PCOS LoRA training (labels 0/1)

```bash
accelerate launch --num_processes 1 scripts/finetune_pcos_lora.py \
  --base_model <BASE_MODEL> \
  --dataset data/pcos_final.jsonl \
  --output_dir ml/models/pcos-lora \
  --system_prompt configs/system_prompt.txt \
  --use_4bit
```

Use the trained adapter in the API

```bash
export MODEL_PATH="ml/models/pcos-lora"
uvicorn nourisher.main:app --host 0.0.0.0 --port 8000
```

Notes and tips

- If you hit OOM on 4GB VRAM:
  - reduce `--max_seq_length` (default 512)
  - increase `--gradient_accumulation_steps`
  - use `device_map="auto"` and accelerate offloading to CPU if available
- For production inference with large models, consider a separate inference worker process or queue so the FastAPI app doesn't block on model generation.
- The Alembic migration creates the `vector` extension and an `embeddings` table with `vector(1536)`. Adjust the dimension if you use a different embedding model.

Testing

Run the test suite:

```bash
pip install pytest pytest-asyncio httpx
pytest -q
```

Troubleshooting

- If Postgres is not reachable, verify `DATABASE_URL` and that the container is running.
- If model loading fails, confirm `MODEL_PATH` points to a valid model or adapter directory.
- For SSE in the browser, use `EventSource` and ensure CORS is configured if needed.
- If Alembic fails, verify the DB is running and `alembic.ini` matches your driver.

If you want me to tune the finetune script further for your exact GPU profile (4GB VRAM), I can add an `accelerate` config and a tuned set of parameters — say whether you prefer slightly slower training with more accumulation or attempting CPU offload.
