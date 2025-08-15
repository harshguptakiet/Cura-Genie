# CuraGenie Testing Guide

This guide provides comprehensive information about the testing infrastructure implemented for the CuraGenie platform, including backend, frontend, and end-to-end testing.

## Table of Contents

1. [Overview](#overview)
2. [Backend Testing](#backend-testing)
3. [Frontend Testing](#frontend-testing)
4. [End-to-End Testing](#end-to-end-testing)
5. [CI/CD Pipeline](#cicd-pipeline)
6. [Test Data Management](#test-data-management)
7. [Writing Tests](#writing-tests)
8. [Running Tests](#running-tests)
9. [Coverage Reports](#coverage-reports)
10. [Troubleshooting](#troubleshooting)

## Overview

The CuraGenie platform implements a comprehensive testing strategy with the following components:

- **Backend Testing**: Unit and integration tests using pytest
- **Frontend Testing**: Component tests using Jest and React Testing Library
- **End-to-End Testing**: Complete workflow tests using Playwright
- **Visual Testing**: Component development using Storybook
- **CI/CD Pipeline**: Automated testing and deployment using GitHub Actions

## Backend Testing

### Test Structure

```
backend/
├── tests/
│   ├── conftest.py          # Test configuration and fixtures
│   ├── factories.py         # Test data factories
│   ├── unit/                # Unit tests
│   │   ├── test_models.py   # Database model tests
│   │   ├── test_auth.py     # Authentication tests
│   │   └── test_services.py # Service layer tests
│   ├── integration/         # Integration tests
│   │   └── test_api_endpoints.py
│   └── fixtures/            # Test data fixtures
├── pytest.ini              # Pytest configuration
└── requirements-test.txt    # Testing dependencies
```

### Key Features

- **SQLite Test Database**: Uses in-memory SQLite for fast, isolated tests
- **Factory Pattern**: Generates realistic test data using factory-boy
- **Mocking**: Comprehensive mocking of external services (OpenAI, S3, etc.)
- **Coverage**: Enforces 80%+ code coverage with detailed reports

### Running Backend Tests

```bash
# Run all tests
cd backend
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m auth

# Run tests in parallel
pytest -n auto

# Run tests with verbose output
pytest -v
```

## Frontend Testing

### Test Structure

```
frontend/
├── src/
│   ├── components/
│   │   └── auth/
│   │       ├── __tests__/
│   │       │   └── auth-form.test.tsx
│   │       └── auth-form.tsx
│   └── mocks/
│       ├── server.ts        # MSW server setup
│       └── handlers.ts      # API mock handlers
├── jest.config.js           # Jest configuration
├── jest.setup.js            # Jest setup and mocks
└── package.json             # Testing dependencies
```

### Key Features

- **Jest + React Testing Library**: Modern testing stack for React components
- **MSW (Mock Service Worker)**: API mocking for isolated component testing
- **Accessibility Testing**: Built-in accessibility checks
- **Visual Testing**: Storybook integration for component development

### Running Frontend Tests

```bash
# Run all tests
cd frontend
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run tests for CI
npm run test:ci

# Run specific test file
npm test -- auth-form.test.tsx
```

## End-to-End Testing

### Test Structure

```
frontend/
├── e2e/
│   ├── genomic-upload.spec.ts    # Genomic workflow tests
│   ├── global-setup.ts           # Test environment setup
│   └── global-teardown.ts        # Test environment cleanup
├── playwright.config.ts           # Playwright configuration
└── fixtures/                      # Test data files
    └── sample.vcf
```

### Key Features

- **Cross-Browser Testing**: Tests run on Chrome, Firefox, Safari, and mobile
- **Real User Workflows**: Complete end-to-end user journeys
- **Visual Regression**: Screenshots and videos on test failures
- **Parallel Execution**: Tests run in parallel for faster execution

### Running E2E Tests

```bash
# Run all E2E tests
cd frontend
npm run test:e2e

# Run tests with UI
npm run test:e2e:ui

# Run specific test file
npx playwright test genomic-upload.spec.ts

# Run tests in specific browser
npx playwright test --project=chromium
```

## CI/CD Pipeline

### GitHub Actions Workflow

The CI/CD pipeline runs automatically on:
- Push to `main` and `develop` branches
- Pull requests to `main` and `develop` branches

### Pipeline Stages

1. **Backend Tests**: Python tests with PostgreSQL database
2. **Frontend Tests**: JavaScript/TypeScript tests and build
3. **Security Scan**: Vulnerability scanning with Trivy
4. **Performance Tests**: Load testing and benchmarks
5. **Quality Gates**: Coverage and performance thresholds
6. **Deployment**: Staging (develop) and production (main)

### Quality Gates

- **Code Coverage**: Backend ≥80%, Frontend ≥80%
- **Security**: No critical vulnerabilities
- **Performance**: Response times within thresholds
- **Tests**: All tests must pass

## Test Data Management

### Test Factories

Backend tests use factory-boy to generate realistic test data:

```python
from tests.factories import UserFactory, GenomicDataFactory

# Create a user with genomic data
user = UserFactory()
genomic_data = GenomicDataFactory(user=user)
```

### Mock Services

External services are mocked to ensure test isolation:

```python
@pytest.fixture
def mock_openai():
    with patch('core.llm_service.openai') as mock:
        mock.ChatCompletion.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Mocked response"))]
        )
        yield mock
```

### Test Fixtures

Common test scenarios are available as fixtures:

```python
def test_user_profile(client, db_session, create_complete_user_profile):
    profile = create_complete_user_profile
    # Test with complete user data
```

## Writing Tests

### Backend Test Guidelines

1. **Use Descriptive Names**: Test names should clearly describe what is being tested
2. **Follow AAA Pattern**: Arrange, Act, Assert
3. **Test Edge Cases**: Include error conditions and boundary cases
4. **Use Factories**: Generate test data using factories, not hardcoded values
5. **Mock External Dependencies**: Don't rely on external services

Example:
```python
def test_user_registration_duplicate_email(client, db_session):
    """Test registration with duplicate email fails"""
    # Arrange
    user = UserFactory(email="duplicate@example.com")
    db_session.add(user)
    db_session.commit()
    
    # Act
    response = client.post("/api/auth/register", json={
        "email": "duplicate@example.com",
        "username": "differentuser",
        "password": "SecurePass123!",
        "role": "patient"
    })
    
    # Assert
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]
```

### Frontend Test Guidelines

1. **Test User Behavior**: Focus on how users interact with components
2. **Use Semantic Queries**: Prefer `getByRole`, `getByLabelText` over `getByTestId`
3. **Test Accessibility**: Ensure components are accessible
4. **Mock API Calls**: Use MSW to mock API responses
5. **Test Error States**: Include loading, error, and success states

Example:
```typescript
it('validates required fields', async () => {
  render(<AuthForm mode="login" />)
  
  const submitButton = screen.getByRole('button', { name: /sign in/i })
  fireEvent.click(submitButton)
  
  await waitFor(() => {
    expect(screen.getByText(/email is required/i)).toBeInTheDocument()
    expect(screen.getByText(/password is required/i)).toBeInTheDocument()
  })
})
```

### E2E Test Guidelines

1. **Test Complete Workflows**: Focus on user journeys, not individual components
2. **Use Realistic Data**: Use actual file uploads and realistic user interactions
3. **Handle Async Operations**: Wait for operations to complete
4. **Test Cross-Browser**: Ensure compatibility across different browsers
5. **Include Visual Verification**: Check that UI elements are visible and correct

Example:
```typescript
test('complete genomic file upload workflow', async ({ page }) => {
  // Navigate and login
  await page.goto('/auth/login')
  await page.fill('[name="email"]', 'demo@curagenie.com')
  await page.fill('[name="password"]', 'demo123')
  await page.click('button[type="submit"]')
  
  // Upload file
  await page.goto('/dashboard/genomic-upload')
  await page.locator('input[type="file"]').setInputFiles('fixtures/sample.vcf')
  await page.click('button:has-text("Upload")')
  
  // Verify success
  await expect(page.locator('.upload-success')).toBeVisible()
})
```

## Running Tests

### Local Development

```bash
# Backend tests
cd backend
pytest --cov=. --cov-report=html

# Frontend tests
cd frontend
npm run test:coverage

# E2E tests
cd frontend
npm run test:e2e

# Storybook
cd frontend
npm run storybook
```

### CI/CD Environment

Tests run automatically in GitHub Actions with:
- PostgreSQL database service
- Node.js and Python environments
- Parallel job execution
- Artifact collection and reporting

### Test Commands

| Command | Description |
|---------|-------------|
| `pytest` | Run all backend tests |
| `pytest -m unit` | Run only unit tests |
| `pytest -m integration` | Run only integration tests |
| `npm test` | Run all frontend tests |
| `npm run test:coverage` | Run tests with coverage |
| `npm run test:e2e` | Run end-to-end tests |
| `npm run storybook` | Start Storybook development server |

## Coverage Reports

### Backend Coverage

- **HTML Report**: `backend/htmlcov/index.html`
- **XML Report**: `backend/coverage.xml` (for CI/CD)
- **Terminal Report**: Shows missing lines and branches

### Frontend Coverage

- **HTML Report**: `frontend/coverage/lcov-report/index.html`
- **LCOV Report**: `frontend/coverage/lcov.info` (for CI/CD)
- **Terminal Report**: Shows coverage percentages by file

### Coverage Thresholds

- **Backend**: 80% line coverage, 75% branch coverage
- **Frontend**: 80% line coverage, 75% branch coverage
- **Critical Paths**: 95% coverage (authentication, file processing)

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Ensure test database is properly configured
   - Check database service health in CI/CD

2. **Test Data Issues**
   - Verify factories are properly configured
   - Check database migrations are up to date

3. **Mock Service Issues**
   - Ensure MSW handlers are properly configured
   - Check that API endpoints match mock handlers

4. **Coverage Issues**
   - Verify source files are included in coverage
   - Check for excluded patterns in configuration

### Debug Commands

```bash
# Backend tests with debug output
pytest -v -s --tb=long

# Frontend tests with debug output
npm test -- --verbose

# E2E tests with debug mode
npx playwright test --debug

# Run specific failing test
pytest tests/unit/test_auth.py::TestAuthService::test_user_registration_success
```

### Performance Testing

```bash
# Run performance benchmarks
cd backend
pytest tests/unit/test_performance.py --benchmark-only

# Run load tests
cd backend
locust -f tests/performance/locustfile.py --headless
```

## Best Practices

1. **Test Isolation**: Each test should be independent and not affect others
2. **Fast Execution**: Tests should run quickly (under 5 seconds each)
3. **Realistic Data**: Use factories to generate realistic test data
4. **Clear Assertions**: Test assertions should be clear and specific
5. **Error Handling**: Test both success and failure scenarios
6. **Accessibility**: Include accessibility testing in frontend tests
7. **Documentation**: Document complex test scenarios and setup

## Contributing

When adding new features or components:

1. **Write Tests First**: Follow TDD principles
2. **Update Test Data**: Add new factories and fixtures as needed
3. **Maintain Coverage**: Ensure new code meets coverage thresholds
4. **Update Documentation**: Keep this guide current with new testing patterns

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Playwright Documentation](https://playwright.dev/)
- [Storybook Documentation](https://storybook.js.org/)
- [MSW Documentation](https://mswjs.io/)
- [Factory Boy Documentation](https://factoryboy.readthedocs.io/)
