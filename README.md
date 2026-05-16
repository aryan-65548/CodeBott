# CodeBott

A 30-day project building an AI-powered code review agent that reviews GitHub Pull Requests, Issues, and Commits using **Groq API** as the LLM backbone.

## Project Overview

This agent automatically analyzes:
- **Pull Requests** — diffs, file changes, coding patterns
- **Issues** — bug reports, feature requests, context
- **Commits** — change history, commit message quality
- **Code Quality** — best practices, security, performance

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Groq API (llama3-70b-8192) |
| Backend | FastAPI + Python 3.11 |
| GitHub Integration | PyGithub |
| Frontend | React + Vite |
| Config | Pydantic Settings |

---

## Project Structure
code-review-agent/
│
├── backend/
│   ├── agent/
│   │   ├── reviewer.py          # Core LLM review logic (Groq)
│   │   ├── prompts.py           # All system/user prompts
│   │   └── tools.py             # Agent tools
│   │
│   ├── github/
│   │   ├── client.py            # GitHub API wrapper
│   │   ├── pr_fetcher.py        # Fetch PR diffs, files, metadata
│   │   ├── issue_fetcher.py     # Fetch issues and comments
│   │   ├── commit_fetcher.py    # Fetch commit diffs
│   │   └── webhook_handler.py   # Handle GitHub webhooks
│   │
│   ├── api/
│   │   ├── routes.py            # FastAPI routes
│   │   └── schemas.py           # Pydantic models
│   │
│   ├── config/
│   │   └── settings.py          # Env vars, config loader
│   │
│   ├── utils/
│   │   ├── diff_parser.py       # Parse git diffs
│   │   ├── code_formatter.py    # Format code snippets
│   │   └── logger.py            # Logging setup
│   │
│   └── main.py                  # FastAPI entrypoint
│
├── frontend/
│   └── src/
│       ├── components/          # ReviewCard, DiffViewer, etc.
│       └── pages/               # Home, PRReview, Dashboard
│
├── tests/
│   ├── test_reviewer.py
│   ├── test_github_client.py
│   └── test_diff_parser.py
│
├── .env.example
├── docker-compose.yml
└── README.md

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/code-review-agent.git
cd code-review-agent
```

### 2. Create virtual environment

```bash
python3.11 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` with your keys:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama3-70b-8192
GITHUB_TOKEN=your_github_token
GITHUB_WEBHOOK_SECRET=your_webhook_secret
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=true
```

### 5. Get your API keys

| Key | Where |
|---|---|
| `GROQ_API_KEY` | console.groq.com → API Keys |
| `GITHUB_TOKEN` | github.com → Settings → Developer Settings → Fine-grained tokens |
| `GITHUB_WEBHOOK_SECRET` | Run `python3 -c "import secrets; print(secrets.token_hex(32))"` |

**GitHub Token permissions needed:**
- Contents: Read-only
- Issues: Read-only
- Metadata: Read-only
- Pull requests: Read-only
- Commit statuses: Read-only

---


---

## Security

- Never commit your `.env` file — it's in `.gitignore`
- Use fine-grained GitHub tokens with minimum required permissions
- Rotate API keys regularly

---

## Author

Will be built by **Aryan Patel** as a 30-day challenge.

> ⭐ this repo if you find it useful!
