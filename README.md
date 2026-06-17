# Email OSINT Tool

Open-source intelligence tool for comprehensive email analysis. Aggregates data from multiple sources to build an exposure profile and risk score.

## Features

- **Email Validation** — RFC-compliant validation with normalization
- **Domain Intelligence** — MX records, A records, WHOIS data
- **Breach Detection** — XposedOrNot API + local breach database
- **Gravatar Lookup** — Profile picture and account discovery
- **Username Enumeration** — Sherlock-powered social profile discovery
- **Social Profile Checks** — Direct checks on GitHub, Twitter, LinkedIn, Instagram, Reddit
- **Web Mentions** — Google search for public email references
- **Risk Scoring** — Composite 0-100 risk score with radar visualization
- **Export** — JSON and CSV report export

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, FastAPI, aiosqlite |
| Frontend | React 18, TypeScript, Tailwind CSS, Recharts |
| Infrastructure | Docker, Nginx, Docker Compose |

## Quick Start

### Local Development

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env
uvicorn app:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

### Docker

```bash
docker compose up --build
```

The app will be available at `http://localhost:80`.

## Configuration

All settings are configurable via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `SHERLOCK_PATH` | `sherlock` | Path to Sherlock binary |
| `DB_PATH` | `reports.db` | SQLite database file path |
| `ALLOWED_ORIGINS` | `localhost:5173,localhost:80` | CORS allowed origins |
| `RATE_LIMIT_REQUESTS` | `10` | Max requests per window |
| `RATE_LIMIT_WINDOW_SECONDS` | `60` | Rate limit window |
| `HTTP_TIMEOUT` | `10` | External HTTP request timeout |
| `SHERLOCK_TIMEOUT` | `30` | Sherlock process timeout |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/analyze` | Analyze an email address |
| `GET` | `/api/report/{id}` | Retrieve a saved report |
| `GET` | `/health` | Health check |

## License

For authorized security research only.
