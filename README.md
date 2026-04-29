# NourisHer — FastAPI + LLaMA fine-tuning + Postgres (pgvector)

This repository contains a minimal FastAPI service that accepts NDJSON input, runs generation with a LLaMA-family model, and stores inputs/outputs in a Postgres database with pgvector support for embeddings. It also includes a QLoRA/LoRA fine-tuning script tuned for low-VRAM environments, tests and examples.

What I added
- FastAPI app (src/main.py) with a streaming endpoint at `/stream` that accepts `application/x-ndjson` and stores results in Postgres.
- SQLAlchemy models and Alembic migration to create tables and the `vector` extension.
- Docker Compose file to run Postgres with pgvector.
- QLoRA/LoRA training script: `scripts/finetune_qlora.py` (suitable for small experiments on low VRAM; tune params carefully).
- Examples under `examples/` and a unit test `tests/test_stream.py` that patches DB and model for local testing.

Quick start (local)

1) Start Postgres with pgvector

```bash
docker compose up -d
```

2) Create a virtual environment and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
# core
pip install fastapi uvicorn sqlalchemy alembic asyncpg pgvector httpx
# optional ML dependencies for training and inference
pip install transformers accelerate datasets peft bitsandbytes safetensors huggingface_hub
```

3) Configure DATABASE_URL (optional; defaults to postgres://postgres:postgres@localhost:5432/nourisher)

```bash
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/nourisher"
```

4) Apply Alembic migrations

```bash
alembic upgrade head
```

5) Run the FastAPI app

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

6) Stream data to the API (example)

```bash
curl -X POST -H "Content-Type: application/x-ndjson" --data-binary @examples/data.ndjson http://localhost:8000/stream
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

Notes and tips
- If you hit OOM on 4GB VRAM:
  - reduce `--max_seq_length` (default 512)
  - increase `--gradient_accumulation_steps`
  - use `device_map="auto"` and accelerate offloading to CPU if available
- For production inference with large models, consider a separate inference worker process or queue so the FastAPI app doesn't block on model generation.
- The Alembic migration creates the `vector` extension and an `embeddings` table with `vector(1536)`. Adjust the dimension if you use a different embedding model.

Testing

Run the unit test (requires pytest and httpx):

```bash
pip install pytest pytest-asyncio httpx
pytest -q
```

If you want me to tune the finetune script further for your exact GPU profile (4GB VRAM), I can add an `accelerate` config and a tuned set of parameters — say whether you prefer slightly slower training with more accumulation or attempting CPU offload.
