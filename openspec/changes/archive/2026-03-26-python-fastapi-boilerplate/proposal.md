## Why

Setting up a new Python project with FastAPI from scratch requires repetitive boilerplate configuration. A standard, opinionated boilerplate eliminates this friction and enforces project structure consistency.

## What Changes

- New Python project structure with FastAPI as the web framework
- Console-launchable application using `uvicorn` as the ASGI server
- Local development configuration (environment variables, hot reload)
- Structured project layout with routers, models, and configuration modules
- Dependency management via `pyproject.toml` or `requirements.txt`
- Basic health-check endpoint as a starting point

## Capabilities

### New Capabilities

- `app-entrypoint`: Console entry point to launch the FastAPI app locally with uvicorn
- `api-router`: Base router structure with a health-check endpoint
- `app-config`: Configuration management using environment variables and `.env` support

### Modified Capabilities

## Impact

- New standalone project directory (no existing code affected)
- Dependencies: `fastapi`, `uvicorn[standard]`, `python-dotenv`
- Local development only — no deployment or containerization scope
