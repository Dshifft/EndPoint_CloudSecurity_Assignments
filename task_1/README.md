# Task 1 — Voting system authentication

FastAPI REST API for user and administrator authentication in a voting system. Voting functionality is not part of this task.

Implemented features:

- User registration, login, token validation and account deletion.
- Administrator registration, email MFA request, MFA login, token validation and account deletion.
- JWT tokens for users and administrators.
- Ethereal SMTP for administrator MFA emails.

## Run the project

1. Open a Bash terminal in the `task_1` directory.

2. Activate the course Conda environment:

   ```bash
   conda activate MC26
   ```

3. Install the Poetry dependencies:

   ```bash
   poetry install
   ```

4. Start the FastAPI development server:

   ```bash
   poetry run uvicorn main:voting_app --reload
   ```

5. Open the FastAPI documentation:

   ```text
   http://127.0.0.1:8000/docs
   ```

## Temporary storage

The API currently uses `FakeDB`
