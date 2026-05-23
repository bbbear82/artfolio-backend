# Artfolio Backend

FastAPI proxy service that handles OpenAI API calls server-side for the Artfolio iOS app.

## Requirements

- Python 3.12+
- PostgreSQL 16+ (or SQLite for testing)

## Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env
# Edit .env with your actual OpenAI key and JWT secret

# Run with Docker Compose (includes PostgreSQL)
docker-compose up --build

# Or run directly (requires local PostgreSQL)
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

## Running Tests

```bash
pip install aiosqlite  # needed for SQLite async test backend
pytest tests/ -v
```

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | No | Health check |
| POST | `/auth/apple` | No | Exchange Apple identity token for session JWT |
| POST | `/api/augment` | Bearer JWT | Generate artwork description, term definitions, and/or portfolio statement |
| POST | `/api/translate` | Bearer JWT | Translate previously generated AI content |

## Deployment

### Docker (ECS Fargate)

```bash
docker build -t artfolio-backend .
docker run -p 8000:8000 --env-file .env artfolio-backend
```

### AWS Lambda

The `app/lambda_handler.py` file provides a Mangum adapter. Deploy with your preferred Lambda packaging tool (SAM, CDK, Serverless Framework) using `app.lambda_handler.handler` as the entry point.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | (required) |
| `JWT_SECRET` | Secret for signing session JWTs | (required) |
| `APPLE_BUNDLE_ID` | iOS app bundle ID for Apple token verification | `com.yourcompany.artfolio` |
| `DATABASE_URL` | PostgreSQL async connection string | `postgresql+asyncpg://...` |
| `DAILY_AUGMENT_LIMIT` | Max augmentations per user per day | `10` |
| `DAILY_TRANSLATE_LIMIT` | Max translations per user per day | `10` |
