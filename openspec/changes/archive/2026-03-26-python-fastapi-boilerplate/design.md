## Context

This change introduces a minimal, runnable FastAPI boilerplate intended for local development. There is no existing project — this is a greenfield setup. The app is launched from the console using a Python entry point and runs locally via `uvicorn`.

## Goals / Non-Goals

**Goals:**
- Provide a clean project layout separating concerns (routes, config, main entry point)
- Support local launch via `python main.py` or `uvicorn app.main:app --reload`
- Load configuration from environment variables with `.env` fallback via `python-dotenv`
- Include a `/health` endpoint to verify the app is running

**Non-Goals:**
- Deployment configuration (Docker, CI/CD, cloud)
- Authentication or database integration
- Testing scaffolding (out of scope for initial boilerplate)
- Production hardening (HTTPS, rate limiting, etc.)

## Decisions

### Project layout: flat `app/` package
Use a single `app/` package with `main.py` at root as the entry point. Routers live in `app/routers/`, configuration in `app/config.py`.

**Alternatives considered:**
- `src/` layout: adds indirection without benefit for small apps
- Single-file: doesn't scale; not useful as a boilerplate pattern

### ASGI server: uvicorn with `[standard]` extras
`uvicorn[standard]` includes `uvloop` and `httptools` for better performance and supports `--reload` for development.

**Alternatives considered:**
- `hypercorn`: less common, fewer FastAPI integrations documented
- `gunicorn + uvicorn workers`: appropriate for production, unnecessary here

### Configuration: `pydantic-settings` + `.env` file
Use `pydantic-settings` (`BaseSettings`) to declare typed config fields. Values are read from environment variables, with a `.env` file as fallback.

**Alternatives considered:**
- Raw `os.getenv`: no validation, no type coercion
- `dynaconf`: heavier dependency, more complexity than needed

### Entry point: `main.py` calling `uvicorn.run()`
A `main.py` at project root calls `uvicorn.run("app.main:app", ...)` so the app can be started with `python main.py`. This is beginner-friendly and IDE-compatible.

## Risks / Trade-offs

- **Pydantic v1 vs v2 compatibility** → Use `pydantic-settings` which works with both; pin versions in requirements
- **`uvicorn.run()` in main.py blocks hot reload in some editors** → Document that `uvicorn app.main:app --reload` is the preferred dev command; `python main.py` is for simplicity
