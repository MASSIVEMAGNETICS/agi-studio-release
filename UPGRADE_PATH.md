# AGI STUDIO - DETAILED UPGRADE IMPLEMENTATION PATH

**Version:** 2.0.0-NEXTGEN  
**Implementation Guide**  
**Status:** READY FOR EXECUTION

---

## OVERVIEW

This document provides detailed, actionable steps to implement the upgrades outlined in ASSESSMENT.md. Each section includes specific code examples, configurations, and validation steps.

---

## PHASE 1: FOUNDATION (WEEKS 1-4)

### 1.1 Testing Infrastructure Setup

#### Backend Testing (pytest)

**Step 1: Install dependencies**

```bash
cd backend
pip install pytest pytest-cov pytest-asyncio pytest-mock httpx
```

**Step 2: Create test configuration**

`backend/pytest.ini`:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --cov=.
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=80
```

**Step 3: Create test directory structure**

```bash
mkdir -p backend/tests/{unit,integration,e2e}
mkdir -p backend/tests/unit/{api,core,nodes,memory}
```

**Step 4: Example unit test**

`backend/tests/unit/core/test_node_base.py`:
```python
import pytest
from core.node_base import NodeBase

class TestNodeBase:
    def test_node_initialization(self):
        node = NodeBase(node_id="test", config={})
        assert node.node_id == "test"
        assert node.state == "IDLE"
        assert node.log == []
    
    def test_log_event(self, capsys):
        node = NodeBase(node_id="test", config={})
        node.log_event("Test message")
        assert "Test message" in node.log
        captured = capsys.readouterr()
        assert "[test] Test message" in captured.out
    
    def test_run_not_implemented(self):
        node = NodeBase(node_id="test", config={})
        with pytest.raises(NotImplementedError):
            node.run()
```

**Step 5: Example integration test**

`backend/tests/integration/test_api.py`:
```python
import pytest
from flask import Flask
from api.agi_api import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_load_graph(client):
    response = client.post('/load_graph', json={"nodes": [], "edges": []})
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'loaded'

def test_victor_generate(client):
    response = client.post('/victor/generate', json={'prompt': 'Hello'})
    assert response.status_code == 200
    data = response.get_json()
    assert 'text' in data
```

#### Frontend Testing (Vitest + React Testing Library)

**Step 1: Install dependencies**

```bash
cd frontend
npm install -D vitest @vitest/ui jsdom @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

**Step 2: Configure Vitest**

`frontend/vitest.config.ts`:
```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './tests/setup.ts',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      exclude: ['node_modules/', 'tests/']
    }
  }
})
```

**Step 3: Test setup**

`frontend/tests/setup.ts`:
```typescript
import '@testing-library/jest-dom'
import { expect, afterEach } from 'vitest'
import { cleanup } from '@testing-library/react'

afterEach(() => {
  cleanup()
})
```

**Step 4: Example component test**

`frontend/tests/components/Header.test.tsx`:
```typescript
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import Header from '../../components/Header'
import { TabId } from '../../types'

describe('Header', () => {
  it('renders all tabs', () => {
    const setActiveTab = vi.fn()
    render(<Header activeTab={TabId.AGI_BUILDER} setActiveTab={setActiveTab} />)
    
    expect(screen.getByText(/AGI Builder/i)).toBeInTheDocument()
    expect(screen.getByText(/AGI Trainer/i)).toBeInTheDocument()
  })

  it('calls setActiveTab when tab is clicked', () => {
    const setActiveTab = vi.fn()
    render(<Header activeTab={TabId.AGI_BUILDER} setActiveTab={setActiveTab} />)
    
    const trainerTab = screen.getByText(/AGI Trainer/i)
    fireEvent.click(trainerTab)
    
    expect(setActiveTab).toHaveBeenCalledWith(TabId.AGI_TRAINER)
  })
})
```

**Step 5: Add test scripts**

`frontend/package.json`:
```json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage"
  }
}
```

### 1.2 Code Quality Tools

#### Backend (Python)

**Step 1: Install tools**

```bash
cd backend
pip install ruff black mypy
```

**Step 2: Configure Ruff**

`backend/pyproject.toml`:
```toml
[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
    "ARG", # flake8-unused-arguments
    "SIM", # flake8-simplify
]
ignore = ["E501"]  # line too long (handled by black)

[tool.ruff.lint.isort]
known-first-party = ["core", "api", "nodes", "memory"]

[tool.black]
line-length = 100
target-version = ['py310']
```

**Step 3: Configure mypy**

`backend/mypy.ini`:
```ini
[mypy]
python_version = 3.10
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
strict_equality = True
```

#### Frontend (TypeScript)

**Step 1: Install tools**

```bash
cd frontend
npm install -D eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin prettier eslint-config-prettier
```

**Step 2: Configure ESLint**

`frontend/.eslintrc.json`:
```json
{
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended",
    "prettier"
  ],
  "parser": "@typescript-eslint/parser",
  "parserOptions": {
    "ecmaVersion": 2023,
    "sourceType": "module",
    "ecmaFeatures": {
      "jsx": true
    }
  },
  "rules": {
    "react/react-in-jsx-scope": "off",
    "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
    "@typescript-eslint/explicit-function-return-type": "warn"
  }
}
```

**Step 3: Configure Prettier**

`frontend/.prettierrc`:
```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false
}
```

**Step 4: Strict TypeScript**

`frontend/tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2023", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "noImplicitReturns": true,
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "react-jsx"
  }
}
```

### 1.3 Pre-commit Hooks

**Step 1: Install pre-commit**

```bash
pip install pre-commit
```

**Step 2: Configuration**

`.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: check-merge-conflict
      
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
        
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        
  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.1.0
    hooks:
      - id: prettier
        types_or: [javascript, jsx, ts, tsx, json, css]
```

**Step 3: Install hooks**

```bash
pre-commit install
```

### 1.4 CI/CD Pipeline

**GitHub Actions Workflow**

`.github/workflows/ci.yml`:
```yaml
name: CI/CD Pipeline

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main, develop]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
          cache: 'pip'
          
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov ruff mypy
          
      - name: Lint with Ruff
        run: |
          cd backend
          ruff check .
          
      - name: Type check with mypy
        run: |
          cd backend
          mypy . --ignore-missing-imports
          
      - name: Run tests
        run: |
          cd backend
          pytest --cov=. --cov-report=xml
          
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml
          
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
          
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
          
      - name: Lint
        run: |
          cd frontend
          npm run lint
          
      - name: Type check
        run: |
          cd frontend
          npx tsc --noEmit
          
      - name: Run tests
        run: |
          cd frontend
          npm run test:coverage
          
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
          
      - name: Upload results
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'
```

---

## PHASE 2: SECURITY HARDENING (WEEKS 5-8)

### 2.1 Input Validation with Pydantic

**Step 1: Install Pydantic**

```bash
pip install pydantic pydantic-settings
```

**Step 2: Create validation models**

`backend/api/models.py`:
```python
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator, constr
import re

class PromptRequest(BaseModel):
    """Validated request for text generation"""
    prompt: constr(min_length=1, max_length=10000) = Field(
        ..., 
        description="User prompt for generation"
    )
    max_tokens: Optional[int] = Field(
        default=150, 
        ge=1, 
        le=2048,
        description="Maximum tokens to generate"
    )
    temperature: Optional[float] = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature"
    )
    
    @validator('prompt')
    def validate_prompt(cls, v):
        # Remove potentially dangerous characters
        if re.search(r'[<>\"\'{}]', v):
            raise ValueError("Prompt contains potentially unsafe characters")
        return v.strip()

class GraphConfig(BaseModel):
    """Validated graph configuration"""
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    edges: List[Dict[str, Any]] = Field(default_factory=list)
    
    @validator('nodes')
    def validate_nodes(cls, v):
        for node in v:
            if 'id' not in node or 'type' not in node:
                raise ValueError("Each node must have 'id' and 'type'")
        return v

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None
    code: str

class SuccessResponse(BaseModel):
    """Standard success response"""
    status: str
    data: Optional[Dict[str, Any]] = None
```

**Step 3: Update API with validation**

`backend/api/agi_api.py`:
```python
from flask import Flask, request, jsonify
from pydantic import ValidationError
from core.pipeline_runner import PipelineRunner
from nodes.VictorModel import VictorModel
from api.models import PromptRequest, GraphConfig, ErrorResponse

app = Flask(__name__)
runner = None

@app.errorhandler(ValidationError)
def handle_validation_error(e):
    return jsonify(ErrorResponse(
        error="Validation Error",
        detail=str(e),
        code="VALIDATION_ERROR"
    ).dict()), 400

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Unhandled exception: {e}", exc_info=True)
    return jsonify(ErrorResponse(
        error="Internal Server Error",
        detail="An unexpected error occurred",
        code="INTERNAL_ERROR"
    ).dict()), 500

@app.route("/load_graph", methods=["POST"])
def load_graph():
    global runner
    try:
        config = GraphConfig(**request.json)
        runner = PipelineRunner(config.dict())
        return jsonify({"status": "loaded"})
    except ValidationError as e:
        raise

@app.route('/victor/generate', methods=['POST'])
def victor_generate():
    try:
        req = PromptRequest(**request.json)
        output = VictorModel(node_id="victor", config={}).run({'prompt': req.prompt})
        return jsonify(output)
    except ValidationError as e:
        raise

if __name__ == "__main__":
    app.run(port=8000)
```

### 2.2 Structured Logging

**Step 1: Install logging library**

```bash
pip install python-json-logger
```

**Step 2: Configure logging**

`backend/core/logging_config.py`:
```python
import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging(level=logging.INFO):
    """Configure structured JSON logging"""
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Console handler with JSON formatting
    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger
```

**Step 3: Use structured logging**

`backend/api/agi_api.py`:
```python
import logging
from core.logging_config import setup_logging

logger = setup_logging(logging.INFO)

@app.route('/victor/generate', methods=['POST'])
def victor_generate():
    logger.info("Received generation request", extra={
        "endpoint": "/victor/generate",
        "user_agent": request.headers.get('User-Agent')
    })
    
    try:
        req = PromptRequest(**request.json)
        logger.debug("Request validated", extra={"prompt_length": len(req.prompt)})
        
        output = VictorModel(node_id="victor", config={}).run({'prompt': req.prompt})
        
        logger.info("Generation completed", extra={
            "output_length": len(output.get('text', ''))
        })
        
        return jsonify(output)
    except Exception as e:
        logger.error("Generation failed", extra={
            "error": str(e),
            "error_type": type(e).__name__
        }, exc_info=True)
        raise
```

### 2.3 Rate Limiting

**Step 1: Install Flask-Limiter**

```bash
pip install Flask-Limiter
```

**Step 2: Configure rate limiting**

`backend/api/agi_api.py`:
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour", "20 per minute"],
    storage_uri="memory://"
)

@app.route('/victor/generate', methods=['POST'])
@limiter.limit("10 per minute")
def victor_generate():
    # ... existing code
```

### 2.4 Security Headers

`backend/api/agi_api.py`:
```python
from flask import Flask
from flask_talisman import Talisman

app = Flask(__name__)

# Configure security headers
Talisman(app, 
    force_https=False,  # Set to True in production
    strict_transport_security=True,
    content_security_policy={
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline'",
        'style-src': "'self' 'unsafe-inline'"
    }
)

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

### 2.5 Environment Configuration

**Step 1: Create .env template**

`.env.example`:
```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/agi_studio

# Redis
REDIS_URL=redis://localhost:6379/0

# Victor GPT5
VICTOR_MODEL_PATH=./victor_gpt5/data/victor_gpt5_godcore.weights
VICTOR_BLOODLINE_PATH=./victor_gpt5/bloodline.txt

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Security
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
RATE_LIMIT_ENABLED=True

# Feature Flags
ENABLE_ANALYTICS=False
ENABLE_TELEMETRY=False
```

**Step 2: Load environment variables**

`backend/core/config.py`:
```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Flask
    flask_env: str = "development"
    flask_debug: bool = False
    secret_key: str
    
    # Database
    database_url: str
    redis_url: str
    
    # Victor
    victor_model_path: str
    victor_bloodline_path: str
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Security
    allowed_origins: List[str] = []
    rate_limit_enabled: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

---

## PHASE 3: PERFORMANCE & SCALABILITY (WEEKS 9-12)

### 3.1 Database Layer

**Step 1: Install dependencies**

```bash
pip install sqlalchemy alembic psycopg2-binary
```

**Step 2: Database models**

`backend/db/models.py`:
```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Conversation(Base):
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    title = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, nullable=False)
    role = Column(String(50))  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class ModelVersion(Base):
    __tablename__ = 'model_versions'
    
    id = Column(Integer, primary_key=True)
    version = Column(String(50), unique=True, nullable=False)
    path = Column(String(500), nullable=False)
    metrics = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Integer, default=0)
```

**Step 3: Alembic setup**

```bash
cd backend
alembic init migrations
```

### 3.2 Caching with Redis

`backend/core/cache.py`:
```python
import redis
import json
from typing import Optional, Any
from core.config import settings

class CacheManager:
    def __init__(self):
        self.redis_client = redis.from_url(settings.redis_url)
    
    def get(self, key: str) -> Optional[Any]:
        value = self.redis_client.get(key)
        return json.loads(value) if value else None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        self.redis_client.setex(key, ttl, json.dumps(value))
    
    def delete(self, key: str):
        self.redis_client.delete(key)
    
    def exists(self, key: str) -> bool:
        return self.redis_client.exists(key)

cache = CacheManager()
```

### 3.3 Docker Configuration

**Backend Dockerfile**

`backend/Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "api.agi_api:app"]
```

**Frontend Dockerfile**

`frontend/Dockerfile`:
```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

**Docker Compose**

`docker-compose.yml`:
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://postgres:password@db:5432/agi_studio
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./victor_gpt5:/app/victor_gpt5:ro
    restart: unless-stopped
    
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
    
  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=agi_studio
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    
volumes:
  postgres_data:
```

---

## PHASE 4: ADVANCED FEATURES (WEEKS 13-16)

### 4.1 FastAPI Migration

**New FastAPI application**

`backend/api/main.py`:
```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from api.models import PromptRequest, GraphConfig, ErrorResponse
from core.config import settings
from core.logging_config import setup_logging
from nodes.VictorModel import VictorModel

logger = setup_logging()
app = FastAPI(
    title="AGI Studio API",
    description="Next-generation AGI platform API",
    version="2.0.0"
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/v1/generate")
@limiter.limit("10/minute")
async def generate(request: PromptRequest):
    """Generate text using Victor model"""
    try:
        logger.info("Generation request", extra={"prompt_length": len(request.prompt)})
        
        victor = VictorModel(node_id="victor", config={})
        result = victor.run({'prompt': request.prompt})
        
        return result
    except Exception as e:
        logger.error("Generation failed", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "2.0.0"}

@app.get("/")
async def root():
    """API root"""
    return {
        "message": "AGI Studio API v2.0",
        "docs": "/docs",
        "health": "/health"
    }
```

### 4.2 WebSocket Support

`backend/api/websocket.py`:
```python
from fastapi import WebSocket, WebSocketDisconnect
from typing import List
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/generate")
async def websocket_generate(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            request = json.loads(data)
            
            # Stream generation
            victor = VictorModel(node_id="victor", config={})
            # Implement streaming logic here
            
            await manager.send_personal_message(
                json.dumps({"status": "complete"}),
                websocket
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

---

## VALIDATION CHECKLIST

After implementing each phase, validate with:

### Phase 1 Validation
- [ ] All tests pass (`pytest` and `npm test`)
- [ ] Code coverage >80%
- [ ] Linting passes with zero errors
- [ ] Type checking passes
- [ ] Pre-commit hooks work
- [ ] CI pipeline runs successfully

### Phase 2 Validation
- [ ] All inputs are validated
- [ ] Structured logging works
- [ ] Rate limiting prevents abuse
- [ ] Security headers present
- [ ] Environment variables load correctly
- [ ] Error responses are consistent

### Phase 3 Validation
- [ ] Database migrations work
- [ ] Caching reduces response times
- [ ] Docker containers build and run
- [ ] Docker Compose orchestrates all services
- [ ] Health checks pass

### Phase 4 Validation
- [ ] FastAPI documentation available at `/docs`
- [ ] API performance improved
- [ ] WebSocket connections stable
- [ ] Load testing shows improvements

---

## ROLLBACK PROCEDURES

If issues occur:

1. **Code Issues:** Revert to previous Git commit
2. **Database Issues:** Use Alembic to downgrade migrations
3. **Deployment Issues:** Roll back to previous Docker image
4. **Configuration Issues:** Restore from backup `.env` file

---

## MONITORING & METRICS

### Key Metrics to Track

1. **Performance**
   - API response time (p50, p95, p99)
   - Database query time
   - Cache hit ratio
   - Model inference time

2. **Reliability**
   - Error rate
   - Uptime percentage
   - Request success rate
   - Recovery time

3. **Security**
   - Failed authentication attempts
   - Rate limit hits
   - Suspicious requests
   - Security scan results

4. **Usage**
   - Requests per second
   - Active users
   - Token consumption
   - Feature adoption

---

**Document Version:** 1.0  
**Last Updated:** November 23, 2025  
**Status:** READY FOR IMPLEMENTATION
