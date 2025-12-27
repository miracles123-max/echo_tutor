# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Echo Tutor is an AI-powered language learning assistant built on a **multi-agent architecture**. It supports document/image OCR, text-to-speech pronunciation guidance, and intelligent interactive Q&A for language learning.

### Tech Stack
- **Backend**: FastAPI + LangGraph (multi-agent workflow) + DashScope (Alibaba Cloud AI services)
- **Frontend**: Vue 3 + Vite + Element Plus
- **AI Services**: Qwen-VL (OCR), Qwen3-TTS-Flash (TTS), Qwen-Turbo (LLM)

## Common Commands

### Backend Development
```bash
# Sync dependencies and start dev server
uv sync
uv run uvicorn echo_tutor.main:app --reload

# Run with custom host/port
uv run python echo_tutor/main.py

# Run tests
uv run pytest

# Run specific test
uv run pytest tests/test_config.py -v

# Code formatting and linting
uv run black echo_tutor/
uv run ruff check echo_tutor/
uv run mypy echo_tutor/

# API diagnostics (troubleshoot API key issues)
uv run python scripts/diagnose_api.py
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev    # Start dev server at http://localhost:5173
npm run build  # Build for production
```

## Architecture

### Backend Structure (`echo_tutor/`)

```
├── main.py              # FastAPI app entry point
├── config.py            # Settings management (Pydantic BaseSettings)
├── api/
│   └── routes.py        # REST API endpoints
├── models/
│   └── schemas.py       # Pydantic data models
├── agents/              # LangGraph multi-agent system
│   ├── graph.py         # Workflow orchestration
│   ├── reader_agent.py  # Document/image OCR processing
│   └── tutor_agent.py   # TTS generation & Q&A
└── services/
    └── modelscope_client.py  # DashScope API client
```

### Multi-Agent Workflow (LangGraph)

The system uses **LangGraph** to orchestrate a two-agent workflow:

1. **DocumentReaderAgent** (`agents/reader_agent.py:15-63`)
   - Processes uploaded files (images or text documents)
   - Performs OCR on images using `qwen-vl-ocr` API
   - Reads text files directly
   - Splits content into manageable sections

2. **PronunciationTutorAgent** (`agents/tutor_agent.py:11-68`)
   - Generates TTS audio using `qwen3-tts-flash` API
   - Creates comprehension questions via Qwen LLM
   - Evaluates user answers
   - Saves audio files to `/audio` static mount

The workflow graph is defined in `agents/graph.py:5-26`:
```
Entry → read_document → provide_tutoring → END
```

### API Endpoints (`api/routes.py:17-143`)

- **POST /api/v1/upload** - Upload document/image, initialize LangGraph session
- **GET /api/v1/session/{file_id}/current** - Get current learning section (text + audio + questions)
- **POST /api/v1/session/{file_id}/answer** - Submit answer for evaluation
- **POST /api/v1/session/{file_id}/next** - Move to next section

### Service Layer

**ModelScopeClient** (`services/modelscope_client.py:8-175`) handles all DashScope API interactions:
- `ocr_image()` - Qwen-VL-OCR for image text extraction
- `text_to_speech()` - Qwen3-TTS-Flash for audio generation
- `chat_with_qwen()` - Qwen-Turbo for text generation/evaluation

## Configuration

### Environment Variables (`.env`)
```env
MODELSCOPE_API_KEY=sk-xxxx...        # Required: DashScope API key (must start with sk-)
QWEN_MODEL=qwen-turbo                 # LLM model name
HOST=0.0.0.0                         # Server host
PORT=8000                            # Server port
DEBUG=True                           # Debug mode
MAX_FILE_SIZE=10485760               # Max upload size (10MB)
UPLOAD_DIR=./data/uploads            # File storage directory
```

**Important**: The API key must start with `sk-` (new DashScope format), NOT `ms-` (old ModelScope format). Use `scripts/diagnose_api.py` to verify.

### Settings (`config.py:4-23`)
Centralized configuration using Pydantic BaseSettings with environment variable support.

## File Storage

- **Upload Directory**: `./data/uploads/` (configured via `UPLOAD_DIR`)
- **Audio Files**: Saved as `audio_{section}.wav`, accessible via `/audio` static mount
- **Session Management**: In-memory (use Redis in production - see `routes.py:14`)

## Development Notes

### Testing
- Tests use `pytest` with `pytest-asyncio` for async support
- Test configuration in `pyproject.toml:55-60`
- Single test: `uv run pytest tests/test_config.py -v`

### Dependencies
- Managed via `uv` (Python package manager)
- See `pyproject.toml:12-24` for core dependencies
- Dev dependencies: `pyproject.toml:26-33`

### Frontend Integration
- Vue dev server runs on `http://localhost:5173`
- CORS configured for localhost in `main.py:16-22`
- API calls to `http://localhost:8000/api/v1/*`

### Static Files
- Audio files mounted at `/audio` endpoint (`main.py:31-33`)
- Uploaded files saved to `UPLOAD_DIR` directory

## Key Implementation Details

1. **Async Throughout**: All API handlers use `async/await`
2. **State Management**: LangGraph uses `AgentState` TypedDict (`reader_agent.py:6-13`)
3. **Message Passing**: LangChain messages (HumanMessage/AIMessage) for agent communication
4. **Error Handling**: Graceful fallbacks for API failures (see `modelscope_client.py:64-70`, `tutor_agent.py:114-130`)
5. **JSON Responses**: Tutor agent returns JSON-encoded content in messages (`tutor_agent.py:58-66`)

## Troubleshooting

### API Issues
Run diagnostic script: `uv run python scripts/diagnose_api.py`
- Verifies API key format
- Tests connectivity to all three DashScope services
- Checks permissions for Qwen-VL-OCR, Qwen3-TTS, and Qwen-Turbo

### Common Errors
- **401 Unauthorized**: Invalid or expired API key
- **File too large**: Check `MAX_FILE_SIZE` setting
- **Session not found**: Session stored in memory, lost on restart

## Production Considerations

- Replace in-memory sessions with Redis/database
- Add authentication/authorization
- Implement rate limiting
- Use persistent storage for uploaded files
- Add proper logging and monitoring
- Configure CORS for production domains
