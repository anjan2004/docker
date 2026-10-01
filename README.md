# Simple Python CI/CD with GitHub Actions & Docker

A complete reference project demonstrating how to separate:
1. **Pull Request (PR) Validation**: Runs tests and validates Docker image creation and execution on PRs.
2. **Main Push Workflow**: Runs tests, builds production Docker images, validates the container, and automatically publishes images to GitHub Container Registry (GHCR).

---

## Project Structure

```text
simple-python-ci-cd/
├── .github/
│   └── workflows/
│       ├── pr.yml          # Pull Request validation workflow
│       └── main.yml        # Main push build, test & publish workflow
├── app.py                  # Core application logic
├── test_app.py             # Pytest unit tests
├── Dockerfile              # Container definition
├── .dockerignore           # Files ignored during docker build
├── requirements.txt        # Python dependencies (pytest)
└── README.md               # Practical instructions
```

---

## Step-by-Step Practical Guide

### Step 1: Initialize Git and Push to GitHub

```bash
git init
git add .
git commit -m "feat: initial python project with CI/CD workflows"
git branch -M main
git remote add origin https://github.com/<YOUR_USERNAME>/simple-python-ci-cd.git
git push -u origin main
```

### Step 2: Test the Pull Request Workflow

1. Create and switch to a feature branch:
   ```bash
   git checkout -b feature/add-divide-function
   ```

2. Make a change in `app.py`:
   ```python
   def divide(a, b):
       if b == 0:
           raise ValueError("Cannot divide by zero")
       return a / b
   ```

3. Add a corresponding test in `test_app.py`:
   ```python
   from app import divide

   def test_divide():
       assert divide(10, 2) == 5
   ```

4. Commit and push the branch:
   ```bash
   git add app.py test_app.py
   git commit -m "feat: add divide operation"
   git push -u origin feature/add-divide-function
   ```

5. Open a **Pull Request** to `main` on GitHub:
   - GitHub Actions will trigger [`.github/workflows/pr.yml`](.github/workflows/pr.yml).
   - It will run `pytest`.
   - It will build the Docker image and perform container smoke tests.
   - **Notice**: It does NOT push any Docker images to the registry.

### Step 3: Test the Main Push Workflow (Merge PR)

1. Merge your Pull Request into `main` on GitHub.
2. GitHub Actions will trigger [`.github/workflows/main.yml`](.github/workflows/main.yml):
   - It executes Python tests.
   - It builds the production Docker image.
   - It tests the built image before pushing.
   - It publishes the image to **GitHub Container Registry (GHCR)** tagged with `latest` and short commit SHA.

---

## Pulling and Running the Published Docker Image

```bash
# Pull the latest image
docker pull ghcr.io/<YOUR_USERNAME>/simple-python-ci-cd:latest

# Run the container
docker run --rm ghcr.io/<YOUR_USERNAME>/simple-python-ci-cd:latest
```
