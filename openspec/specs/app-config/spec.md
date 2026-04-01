## ADDED Requirements

### Requirement: Configuration is loaded from environment variables
The application SHALL use `pydantic-settings` (`BaseSettings`) to declare all configuration fields so they are read from environment variables at startup.

#### Scenario: Config loaded from environment
- **WHEN** the `APP_PORT` environment variable is set to `9000` before starting the app
- **THEN** the application binds to port `9000`

### Requirement: .env file is supported as fallback
The configuration system SHALL load a `.env` file from the project root as a fallback when environment variables are not set, using `python-dotenv` integration built into `pydantic-settings`.

#### Scenario: .env file overrides defaults
- **WHEN** a `.env` file contains `APP_PORT=8080` and no `APP_PORT` environment variable is set
- **THEN** the application binds to port `8080`

#### Scenario: Environment variable takes precedence over .env
- **WHEN** both `APP_PORT=9000` (env var) and `APP_PORT=8080` (.env file) are set
- **THEN** the application uses port `9000`

### Requirement: A .env.example file is provided
The project SHALL include a `.env.example` file listing all supported configuration keys with example or default values.

#### Scenario: Developer sets up local config
- **WHEN** a developer copies `.env.example` to `.env`
- **THEN** the application starts with sensible defaults without any additional setup
