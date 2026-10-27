# PhoneixAI — AI Automation Portfolio

A small portfolio and runnable prototypes for an AI automation / developer internship application.

> **Honest scope note:** these are demonstration prototypes, not claims of completed paid client deployments. Prices in the Telegram bot are illustrative. RequestPilot's local mode is heuristic, not a language model. LLM mode is optional and only activates when a server-side API key is configured.

## Included

- `index.html` — responsive portfolio page with a working lead-triage demo. It works from a local file using a browser-side demo heuristic; if opened at the FastAPI server URL, it calls the API.
- `app.py` — FastAPI backend for RequestPilot. It uses a local fallback by default and can call an OpenAI-compatible chat-completions API (for example, OpenRouter) when configured.
- `telegram_bot.py` — aiogram 3 Telegram bot prototype with a multi-step quote flow, input validation, simple calculation, and SQLite persistence.
- `csv_cleaner.py` — CSV normalization, deduplication, and JSON report generator.

## Run the portfolio + RequestPilot API

Python 3.11+ recommended.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app:app --reload
```

Open `http://127.0.0.1:8000`. The API is available at `http://127.0.0.1:8000/docs`; health check: `/health`.

### Optional LLM mode

Set environment variables on the server, never inside `index.html`:

```bash
export LLM_API_KEY="your_key_here"
export LLM_BASE_URL="https://openrouter.ai/api/v1"
export LLM_MODEL="your-provider/model-id"
uvicorn app:app --reload
```

Model IDs and provider support can change, so use a model currently available to your account. Without `LLM_API_KEY`, `/api/analyze` uses local deterministic rules and does not call an external service.

## Run the Telegram bot prototype

1. Create a bot with Telegram's official BotFather and obtain a token.
2. Set the token in your shell; don't commit it.

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
python telegram_bot.py
```

In Telegram, send `/start` and `/quote`. The demo collects dimensions and material, calculates an illustrative estimate, and stores the record in SQLite. The formula is not suitable for real pricing without business rules and validation.

## Run the CSV cleaner

Create an input CSV with a header row, optionally including an `email` column, then run:

```bash
python csv_cleaner.py input.csv cleaned.csv
```

The script trims values, lowercases email addresses, removes duplicates by email (or full row when email is empty), and creates `cleaned.csv.report.json`. Use anonymized test data in demos.

## AI coding workflow used to prepare this portfolio

The intended workflow is OpenCode as the AI coding harness, with an LLM reached through OpenRouter. Work is decomposed into small changes; project instructions/skills supply context; changes are reviewed and manually exercised. This repository does not claim that every line was handwritten. The developer should be ready to explain the design, run the demos, and discuss limitations.

## Project status

- Public repository: https://github.com/PhoneixAI/ai-automation-portfolio
- `index.html` contains an interactive lead-triage demo.
- `app.py` provides a FastAPI backend with optional LLM integration.
- `telegram_bot.py` contains a Telegram bot prototype.
- `csv_cleaner.py` provides CSV cleaning and JSON report generation.

These are demonstration prototypes, not production deployments.
The LLM mode requires API configuration, and the Telegram bot
requires a bot token. Review the setup instructions before running.

