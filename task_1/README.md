# Task 1 — Voting system

This is the initial structure for the voting-system API. It follows the organisation of the classroom reference project: `main.py`, `utils/`, `src/admin/`, `src/user/` and `test/`.

At this stage the API only has its root route. Authentication, database, users, administrators and MFA will be added one at a time in later approved steps.

## Run the project

1. Open a Bash terminal in the `task_1` directory.

2. Activate the course Conda environment:

   ```bash
   conda activate MC26
   ```

3. Install the dependencies managed by Poetry:

   ```bash
   poetry install
   ```

4. Start the FastAPI development server:

   ```bash
   poetry run uvicorn main:voting_app --reload
   ```

5. Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/). The API must return:

   ```json
   {"message": "Welcome to the voting app!"}
   ```

6. Optional: open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to see the FastAPI documentation.
