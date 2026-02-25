# GitHub Actions CI/CD

This directory contains GitHub Actions workflows for continuous integration and deployment.

## Workflows

### 1. CI Pipeline (`ci.yml`)

Main CI pipeline that runs on every push and pull request to `main` and `develop` branches.

**Jobs:**

- **Backend CI**: Runs Python tests with pytest
- **Frontend CI**: Runs TypeScript type checking, linting, and builds
- **Integration Tests**: Placeholder for integration tests (runs after backend and frontend)

**Triggers:**

- Push to `main` or `develop`
- Pull requests to `main` or `develop`

### 2. Backend Tests (`backend-tests.yml`)

Comprehensive backend testing with multiple Python versions.

**Features:**

- Tests on Python 3.9, 3.10, and 3.11
- Runs pytest with coverage
- Linting with flake8
- Uploads coverage to Codecov

**Triggers:**

- Push to `main` or `develop` (only when backend files change)
- Pull requests to `main` or `develop` (only when backend files change)

### 3. Frontend Tests (`frontend-tests.yml`)

Comprehensive frontend testing with multiple Node versions.

**Features:**

- Tests on Node 18.x and 20.x
- TypeScript type checking
- ESLint linting
- Vitest unit tests with coverage
- Production build verification
- Uploads coverage to Codecov

**Triggers:**

- Push to `main` or `develop` (only when frontend files change)
- Pull requests to `main` or `develop` (only when frontend files change)

## Running Tests Locally

### Backend Tests

```bash
cd backend
pip install -r requirements.txt
pip install pytest pytest-cov
pytest
```

### Frontend Tests

```bash
cd frontend
npm install
npm test
npm run lint
npm run type-check
npm run build
```

## Coverage Reports

Coverage reports are automatically uploaded to Codecov on every push. You can view them at:

- Backend: `codecov.io/gh/YOUR_USERNAME/YOUR_REPO/flags/backend`
- Frontend: `codecov.io/gh/YOUR_USERNAME/YOUR_REPO/flags/frontend`

## Adding New Tests

### Backend

Add test files in `backend/tests/`:

- Unit tests: `backend/tests/unit/test_*.py`
- Integration tests: `backend/tests/integration/test_*.py`

### Frontend

Add test files in `frontend/src/`:

- Component tests: `frontend/src/components/**/__tests__/*.test.tsx`
- Utility tests: `frontend/src/utils/__tests__/*.test.ts`
- Store tests: `frontend/src/stores/__tests__/*.test.ts`

## Continuous Deployment

To add continuous deployment:

1. Add deployment jobs to `ci.yml`
2. Configure deployment secrets in GitHub repository settings
3. Add environment-specific workflows (staging, production)

## Badges

Add these badges to your main README.md:

```markdown
![CI Pipeline](https://github.com/YOUR_USERNAME/YOUR_REPO/workflows/CI%20Pipeline/badge.svg)
![Backend Tests](https://github.com/YOUR_USERNAME/YOUR_REPO/workflows/Backend%20Tests/badge.svg)
![Frontend Tests](https://github.com/YOUR_USERNAME/YOUR_REPO/workflows/Frontend%20Tests/badge.svg)
[![codecov](https://codecov.io/gh/YOUR_USERNAME/YOUR_REPO/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/YOUR_REPO)
```
