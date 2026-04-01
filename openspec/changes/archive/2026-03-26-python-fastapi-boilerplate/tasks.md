## 1. Project Structure

- [x] 1.1 Create project root directory layout (`app/`, `app/routers/`)
- [x] 1.2 Create `pyproject.toml` (or `requirements.txt`) with `fastapi`, `uvicorn[standard]`, and `pydantic-settings` dependencies
- [x] 1.3 Create `.env.example` with all supported config keys and example values
- [x] 1.4 Create `.gitignore` excluding `.env`, `__pycache__`, `.venv`, etc.

## 2. Configuration

- [x] 2.1 Create `app/config.py` with a `Settings` class extending `pydantic_settings.BaseSettings`
- [x] 2.2 Add fields: `app_title`, `app_version`, `app_description`, `host`, `port` with defaults
- [x] 2.3 Configure `model_config` to load from `.env` file
- [x] 2.4 Export a singleton `settings = Settings()` instance

## 3. Application Factory

- [x] 3.1 Create `app/main.py` that instantiates `FastAPI` with title/version/description from `settings`
- [x] 3.2 Register the base router from `app/routers/`

## 4. Routers

- [x] 4.1 Create `app/routers/__init__.py` that defines a base `APIRouter` and includes sub-routers
- [x] 4.2 Create `app/routers/health.py` with `GET /health` returning `{"status": "ok"}`
- [x] 4.3 Register `health` router in `app/routers/__init__.py`

## 5. Entry Point

- [x] 5.1 Create `main.py` at project root that calls `uvicorn.run("app.main:app", host=..., port=..., reload=True)`
- [x] 5.2 Verify `python main.py` starts the server on the configured host/port
- [x] 5.3 Verify `GET /health` returns `{"status": "ok"}` and `GET /docs` shows Swagger UI
