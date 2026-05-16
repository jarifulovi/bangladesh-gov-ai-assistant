# Bangladesh Government Services Chatbot Backend

FastAPI backend for a lightweight, fine-tuned assistant that answers Bangladesh government service queries.

## Quickstart

Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the API:

```bash
uvicorn main:app --reload
```

Test the mock mode (skips model load):

```bash
BG_ASSISTANT_USE_MOCK=true uvicorn main:app --reload
```

## Configuration

Environment variables are prefixed with `BG_ASSISTANT_`:

- `BG_ASSISTANT_MODEL_NAME` (default: `Qwen/Qwen2.5-1.5B-Instruct`)
- `BG_ASSISTANT_LORA_ADAPTER_PATH` (optional)
- `BG_ASSISTANT_MAX_NEW_TOKENS` (default: `256`)
- `BG_ASSISTANT_TEMPERATURE` (default: `0.7`)
- `BG_ASSISTANT_TOP_P` (default: `0.9`)
- `BG_ASSISTANT_SYSTEM_PROMPT`
- `BG_ASSISTANT_USE_MOCK` (default: `false`)
