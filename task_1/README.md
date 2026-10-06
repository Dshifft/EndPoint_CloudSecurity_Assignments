# Task 1 — Voting system

This FastAPI project follows the classroom reference structure: `main.py`, `utils/`, `src/admin/` and `src/user/`.

The current phase implements user registration with the same initial idea shown in the professor's code: a temporary in-memory `FakeDB`. Data is lost whenever the API is restarted. PostgreSQL will replace this storage in a later phase.

## Run the project

1. Open a Bash terminal in the `task_1` directory.

2. Activate the course Conda environment:

   ```bash
   conda activate MC26
   ```

3. Refresh the Poetry lock and install dependencies:

   ```bash
   poetry lock
   poetry install
   ```

4. Start the FastAPI development server:

   ```bash
   poetry run uvicorn main:voting_app --reload
   ```
