# Task 1 — Voting system

This FastAPI project follows the classroom reference structure: `main.py`, `utils/`, `src/admin/` and `src/user/`.

The current phase implements user registration with the same initial idea shown in the professor's code: a temporary in-memory `FakeDB`. Data is lost whenever the API is restarted. PostgreSQL will replace this storage in a later phase.

## Run the project

1. Copy `.env.example` to `.env` and replace `USER_JWT_SECRET` with a long, local secret. The `.env` file is ignored by Git.

2. Open a Bash terminal in the `task_1` directory.

3. Activate the course Conda environment:

   ```bash
   conda activate MC26
   ```

4. Refresh the Poetry lock and install dependencies:

   ```bash
   poetry lock
   poetry install
   ```

5. Start the FastAPI development server:

   ```bash
   poetry run uvicorn main:voting_app --reload
   ```
