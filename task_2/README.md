# Task 2 — Logging and Docker for the voting API

FastAPI REST API for user and administrator authentication in a voting system.

Implemented features:

- User registration, login, token validation and account deletion.
- Administrator registration, email MFA request, MFA login, token validation
  and account deletion.
- JWT tokens for users and administrators.
- File logging at `logs/logs.log` with a minimum level of `INFO`.
- Docker and Docker Compose configuration.

## Configuration

Copy `.env.example` to `.env` and replace its placeholder values before
starting the application. The `.env` file is intentionally excluded from Git.

## How to run the app

Run these commands from the `task_2` directory.

Build the image:

```bash
docker compose build
```

Start the app:

```bash
docker compose up
```

Stop the app:

```bash
docker compose down
```

### Optional Makefile shortcuts

If `make` is available in your Bash environment, the same actions can be run
with `make build`, `make up`, and `make down`. Use `make logs` to follow the
container logs or `make restart` to recreate the service.

The API is available at `http://127.0.0.1:8000` and its interactive
documentation is available at `http://127.0.0.1:8000/docs`. Application events
are written to `logs/logs.log` on the host machine.
