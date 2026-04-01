## ADDED Requirements

### Requirement: App launches from console
The project SHALL provide a `main.py` at the project root that starts the FastAPI application using `uvicorn.run()` when executed directly (`python main.py`).

#### Scenario: Launch app with python main.py
- **WHEN** the user runs `python main.py` from the project root
- **THEN** the uvicorn server starts on `http://127.0.0.1:8000` and the app accepts HTTP requests

#### Scenario: App is also launchable via uvicorn CLI
- **WHEN** the user runs `uvicorn app.main:app --reload`
- **THEN** the server starts with hot reload enabled and serves the same application

### Requirement: Host and port are configurable
The `main.py` entry point SHALL read host and port from the application configuration so they can be overridden via environment variables.

#### Scenario: Default host and port
- **WHEN** no environment variables are set
- **THEN** the app binds to `127.0.0.1` on port `8000`

#### Scenario: Override port via environment variable
- **WHEN** the `APP_PORT` environment variable is set to `9000`
- **THEN** the app binds to port `9000`
