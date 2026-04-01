## ADDED Requirements

### Requirement: Upload router is registered
The application SHALL register the upload router in `app/routers/__init__.py` so that `POST /upload` is accessible without modifying `app/main.py`.

#### Scenario: Upload endpoint accessible after router registration
- **WHEN** the upload router is included in `app/routers/__init__.py`
- **THEN** `POST /upload` is reachable and returns a non-404 response
