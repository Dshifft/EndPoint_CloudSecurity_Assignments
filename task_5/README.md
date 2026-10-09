# Task 5 — Testing, Nginx and CI/CD

FastAPI voting API with automated tests, Nginx and Azure deployment.

Implemented features:

- Separate Docker Compose configuration for tests.
- Nginx with HTTPS, two API replicas and a 10 requests per second limit.
- GitHub Actions workflow that tests and deploys to Azure.

## Tests

```bash
make test
```

## Deployment

The workflow in `.github/workflows/task_5_production.yml` runs on each push to
`main` and can also be started manually from GitHub Actions.

It first executes `make test`. If the tests fail, the deployment job does not
run. If they pass, the workflow:

- creates the production `.env` file from GitHub Secrets;
- connects to the Azure VM through SSH;
- copies the application without the certificate and private key;
- runs `docker compose -f docker-compose.production.yml up --build -d`.

The certificate and private key remain only on the Azure VM. The workflow
deploys two API replicas behind Nginx.

The required GitHub Secrets contain the Azure SSH connection and the
application environment variables.

Production documentation is available at:

```text
https://135.116.202.172/docs
```

HTTP requests are redirected to HTTPS.
