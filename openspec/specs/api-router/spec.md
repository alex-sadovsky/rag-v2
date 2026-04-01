## ADDED Requirements

### Requirement: Health-check endpoint
The application SHALL expose a `GET /health` endpoint that returns a JSON response indicating the service is running.

#### Scenario: Health check returns 200
- **WHEN** a client sends `GET /health`
- **THEN** the server responds with HTTP 200 and body `{"status": "ok"}`

### Requirement: Routers are registered via a base router
The application SHALL use an `APIRouter` in `app/routers/` and include it in the main `FastAPI` app instance, so new routers can be added without modifying `app/main.py`.

#### Scenario: New router added without changing main.py
- **WHEN** a new router module is created in `app/routers/` and registered in the router package
- **THEN** its endpoints are accessible without modifying `app/main.py`

### Requirement: App metadata is set
The `FastAPI` app instance SHALL include a `title`, `version`, and `description` sourced from configuration.

#### Scenario: App metadata visible in docs
- **WHEN** a client opens `http://127.0.0.1:8000/docs`
- **THEN** the Swagger UI displays the configured app title and version

### Requirement: Upload router is registered
The application SHALL register the upload router in `app/routers/__init__.py` so that `POST /upload` is accessible without modifying `app/main.py`.

#### Scenario: Upload endpoint accessible after router registration
- **WHEN** the upload router is included in `app/routers/__init__.py`
- **THEN** `POST /upload` is reachable and returns a non-404 response
