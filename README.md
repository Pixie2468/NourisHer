# 🌸 NourisHer — PCOS Wellness App

A full-stack mobile-first wellness application designed specifically for women with PCOS.

<<<<<<< HEAD
## Tech Stack
- **Frontend**: React 18 + TypeScript + Tailwind CSS + Vite
- **Backend**: Python + FastAPI + SQLAlchemy (async)
- **Database**: PostgreSQL 16
- **AI Chatbot**: Anthropic Claude (claude-sonnet-4-20250514)
- **Auth**: JWT (access + refresh tokens) + bcrypt
=======
What I added

- FastAPI app (src/main.py) with a streaming endpoint at `/stream` that accepts `application/x-ndjson` and stores results in Postgres.
- SQLAlchemy models and Alembic migration to create tables and the `vector` extension.
- Docker Compose file to run Postgres with pgvector.
- QLoRA/LoRA training script: `scripts/finetune_qlora.py` (suitable for small experiments on low VRAM; tune params carefully).
- Examples under `examples/` and a unit test `tests/test_stream.py` that patches DB and model for local testing.
>>>>>>> main

---

## Project Structure

```
nourisHer/
├── backend/                  # FastAPI Python backend
│   ├── core/
│   │   ├── config.py         # Settings & env vars
│   │   ├── database.py       # Async SQLAlchemy engine
│   │   └── security.py       # JWT + password utils
│   ├── models/               # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── profile.py
│   │   ├── diet.py
│   │   └── other.py          # Chat, community, content, cycle, streak
│   ├── routers/              # FastAPI route handlers
│   │   ├── auth.py           # /api/auth/*
│   │   ├── profile.py        # /api/profile/*
│   │   ├── chat.py           # /api/chat/*
│   │   ├── diet.py           # /api/diet/*
│   │   ├── community.py      # /api/community/*
│   │   └── content_cycle.py  # /api/content/* & /api/cycle/*
│   ├── schemas/
│   │   ├── auth.py           # Pydantic auth schemas
│   │   └── main.py           # All other Pydantic schemas
│   ├── services/
│   │   ├── chatbot.py        # Anthropic Claude integration + PCOS system prompt
│   │   └── diet_generator.py # AI-powered diet plan generation
│   ├── main.py               # FastAPI app entry point
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/                 # React + TypeScript frontend
│   ├── src/
│   │   ├── components/
│   │   │   └── layout/
│   │   │       └── AppLayout.tsx   # Bottom nav shell
│   │   ├── pages/
│   │   │   ├── AuthPage.tsx        # Login / Register
│   │   │   ├── OnboardPage.tsx     # 3-step profile setup
│   │   │   ├── HomePage.tsx        # Dashboard + routine
│   │   │   ├── DietPage.tsx        # AI diet plans
│   │   │   ├── ChatPage.tsx        # Nour AI chatbot
│   │   │   ├── CommunityPage.tsx   # Groups + posts
│   │   │   ├── LearnPage.tsx       # Videos + articles
│   │   │   └── ProfilePage.tsx     # User profile + settings
│   │   ├── hooks/
│   │   │   └── useAuthStore.ts     # Zustand auth state
│   │   ├── services/
│   │   │   └── api.ts              # Axios client + interceptors
│   │   ├── styles/
│   │   │   └── globals.css         # Tailwind + custom classes
│   │   └── main.tsx                # React Router + QueryClient
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── Dockerfile
│   └── nginx.conf
├── database/
│   └── schema.sql            # Full PostgreSQL schema
├── docker-compose.yml        # One-command full-stack launch
└── README.md
```

---

## Quick Start

### Option A — Docker (Recommended)

```bash
# 1. Clone / unzip project
cd nourisHer

# 2. Create backend env file
cp backend/.env.example backend/.env
# Edit backend/.env and add your ANTHROPIC_API_KEY

# 3. Launch everything
docker compose up --build

# App runs at:
#   Frontend  → http://localhost:3000
#   Backend   → http://localhost:8000
#   API Docs  → http://localhost:8000/api/docs
```

### Option B — Local Development

#### Backend
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env — set DATABASE_URL and ANTHROPIC_API_KEY

# Run database migrations (ensure PostgreSQL is running)
# Create database first:
#   psql -U postgres -c "CREATE DATABASE nourisher_db;"
#   psql -U postgres -c "CREATE USER nourisher WITH PASSWORD 'password';"
#   psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE nourisher_db TO nourisher;"
# Apply schema:
#   psql -U nourisher -d nourisher_db -f ../database/schema.sql

# Start backend
uvicorn main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend

# Install dependencies
npm install

# Start dev server (proxies /api to localhost:8000)
npm run dev

# App runs at http://localhost:3000
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Sign in |
| POST | `/api/auth/refresh` | Refresh JWT |
| GET  | `/api/auth/me` | Current user |
| GET/POST/PUT | `/api/profile/` | PCOS profile CRUD |
| POST | `/api/diet/generate` | AI diet plan generation |
| GET  | `/api/diet/today` | Today's meal plan |
| GET  | `/api/diet/history` | Past 7 plans |
| POST | `/api/chat/` | Chat with Nour AI |
| GET  | `/api/chat/sessions` | Chat history |
| GET  | `/api/community/groups` | List groups |
| POST | `/api/community/groups/{id}/join` | Join group |
| GET/POST | `/api/community/groups/{id}/posts` | Group posts |
| POST | `/api/community/posts/{id}/like` | Like post |
| POST | `/api/community/posts/{id}/comments` | Add comment |
| GET  | `/api/content/` | Educational content |
| GET/POST | `/api/cycle/` | Cycle tracking |
| GET  | `/api/cycle/today` | Today's cycle entry |

---

## Environment Variables

```env
# Required
DATABASE_URL=postgresql+asyncpg://nourisher:password@localhost:5432/nourisher_db
JWT_SECRET_KEY=your-secret-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional
FRONTEND_URL=http://localhost:3000
SMTP_HOST=smtp.gmail.com
SMTP_USER=you@gmail.com
SMTP_PASSWORD=your_app_password
```

---

## Features

- ✅ **Auth** — Register/Login with JWT, refresh tokens, bcrypt passwords
- ✅ **Onboarding** — 3-step profile wizard (age, weight, symptoms, allergies, goals)
- ✅ **AI Diet Plans** — Claude generates personalized PCOS-friendly meal plans
- ✅ **Nour AI Chatbot** — Full conversation history, Claude-powered PCOS guidance
- ✅ **Community** — Groups, posts, comments, likes
- ✅ **Educational Content** — Videos, articles, guides
- ✅ **Cycle Tracking** — Daily logging with phase detection
- ✅ **Daily Routine** — Checklist with progress tracking
- ✅ **Streaks & Points** — Gamification system

---

<<<<<<< HEAD
## License
MIT — built with 🌸 for women with PCOS
=======
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
>>>>>>> main
