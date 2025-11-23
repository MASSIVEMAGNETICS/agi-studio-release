# SECURITY BEST PRACTICES & GUIDELINES

**AGI Studio Security Framework**  
**Version:** 2.0.0-SECURE  
**Classification:** CRITICAL INFRASTRUCTURE

---

## TABLE OF CONTENTS

1. [Security Philosophy](#security-philosophy)
2. [Threat Model](#threat-model)
3. [Input Validation](#input-validation)
4. [Authentication & Authorization](#authentication--authorization)
5. [Data Protection](#data-protection)
6. [API Security](#api-security)
7. [Secrets Management](#secrets-management)
8. [Dependency Security](#dependency-security)
9. [Incident Response](#incident-response)
10. [Compliance & Auditing](#compliance--auditing)

---

## SECURITY PHILOSOPHY

AGI Studio follows a **defense-in-depth** security model with these core principles:

1. **Zero Trust:** Never trust, always verify
2. **Least Privilege:** Minimal access rights by default
3. **Privacy First:** User data is sacred (Bloodline Law #2)
4. **Security by Design:** Built-in, not bolted-on
5. **Transparency:** Clear security practices and audit trails
6. **Fail Secure:** Systems default to secure state on failure

---

## THREAT MODEL

### Asset Classification

| Asset | Sensitivity | Threat Level | Protection Required |
|-------|------------|--------------|---------------------|
| User data & conversations | CRITICAL | High | Encryption, access control, audit |
| Model weights | HIGH | Medium | Integrity checks, version control |
| API keys & secrets | CRITICAL | High | Vault, rotation, monitoring |
| Source code | MEDIUM | Medium | Access control, code review |
| Bloodline directives | CRITICAL | High | Immutability, integrity verification |

### Attack Vectors

1. **Injection Attacks** (SQL, NoSQL, Command, Prompt)
2. **Authentication Bypass**
3. **Authorization Failures**
4. **Data Exfiltration**
5. **Model Poisoning**
6. **Denial of Service**
7. **Supply Chain Attacks**
8. **Insider Threats**

---

## INPUT VALIDATION

### Principle: "Never Trust User Input"

#### Text Input Sanitization

```python
import re
from typing import Optional
from pydantic import BaseModel, validator

class SafeTextInput(BaseModel):
    text: str
    
    @validator('text')
    def sanitize_text(cls, v: str) -> str:
        # Remove null bytes
        v = v.replace('\x00', '')
        
        # Limit length
        if len(v) > 100000:
            raise ValueError("Input too long")
        
        # Remove control characters except newline and tab
        v = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', v)
        
        return v.strip()

def sanitize_html(text: str) -> str:
    """Remove HTML tags to prevent XSS"""
    return re.sub(r'<[^>]+>', '', text)

def sanitize_sql(text: str) -> str:
    """Escape SQL special characters"""
    # Use parameterized queries instead!
    return text.replace("'", "''").replace(";", "")

def sanitize_path(path: str) -> str:
    """Prevent path traversal attacks"""
    import os
    # Remove .. and leading /
    path = path.replace('..', '').lstrip('/')
    # Ensure it's within allowed directory
    base_dir = '/app/data'
    full_path = os.path.join(base_dir, path)
    if not full_path.startswith(base_dir):
        raise ValueError("Invalid path")
    return full_path
```

#### Prompt Injection Prevention

```python
class PromptGuard:
    """Protect against prompt injection attacks"""
    
    DANGEROUS_PATTERNS = [
        r'ignore\s+previous\s+instructions',
        r'system\s*:\s*you\s+are',
        r'developer\s+mode',
        r'jailbreak',
        r'<\|im_start\|>',
        r'<\|im_end\|>',
    ]
    
    @staticmethod
    def scan(prompt: str) -> tuple[bool, Optional[str]]:
        """Returns (is_safe, reason)"""
        prompt_lower = prompt.lower()
        
        for pattern in PromptGuard.DANGEROUS_PATTERNS:
            if re.search(pattern, prompt_lower):
                return False, f"Potential injection detected: {pattern}"
        
        # Check for unusual encoding
        if any(ord(c) > 127 for c in prompt):
            # Allow unicode but log it
            pass
        
        return True, None
    
    @staticmethod
    def sanitize(prompt: str) -> str:
        """Remove potentially dangerous content"""
        # Implement sanitization logic
        return prompt
```

### File Upload Validation

```python
from typing import BinaryIO
import magic

ALLOWED_MIME_TYPES = {
    'image/png',
    'image/jpeg',
    'image/webp',
    'audio/wav',
    'audio/mp3',
    'text/plain',
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

def validate_file_upload(file: BinaryIO, filename: str) -> None:
    """Validate uploaded file"""
    # Check file size
    file.seek(0, 2)  # Seek to end
    size = file.tell()
    file.seek(0)  # Reset
    
    if size > MAX_FILE_SIZE:
        raise ValueError("File too large")
    
    # Check MIME type
    mime = magic.from_buffer(file.read(2048), mime=True)
    file.seek(0)
    
    if mime not in ALLOWED_MIME_TYPES:
        raise ValueError(f"Invalid file type: {mime}")
    
    # Check filename
    if '..' in filename or filename.startswith('/'):
        raise ValueError("Invalid filename")
```

---

## AUTHENTICATION & AUTHORIZATION

### JWT-Based Authentication

```python
from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext

SECRET_KEY = "your-secret-key-from-env"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
```

### Role-Based Access Control (RBAC)

```python
from enum import Enum
from typing import List

class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"

class Permission(str, Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"

ROLE_PERMISSIONS = {
    Role.ADMIN: [Permission.READ, Permission.WRITE, Permission.DELETE, Permission.ADMIN],
    Role.USER: [Permission.READ, Permission.WRITE],
    Role.READONLY: [Permission.READ],
}

def check_permission(user_role: Role, required_permission: Permission) -> bool:
    return required_permission in ROLE_PERMISSIONS.get(user_role, [])

# FastAPI dependency
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    token = credentials.credentials
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return payload

def require_permission(permission: Permission):
    async def permission_checker(user: dict = Depends(get_current_user)):
        user_role = Role(user.get("role", "readonly"))
        if not check_permission(user_role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return user
    return permission_checker
```

---

## DATA PROTECTION

### Encryption at Rest

```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import os
import base64

class EncryptionManager:
    """Manage encryption for sensitive data"""
    
    def __init__(self, master_key: str):
        # Derive key from master key
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'static-salt',  # Use unique salt per deployment
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt string data"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def encrypt_file(self, filepath: str) -> None:
        """Encrypt file in place"""
        with open(filepath, 'rb') as f:
            data = f.read()
        encrypted = self.cipher.encrypt(data)
        with open(filepath, 'wb') as f:
            f.write(encrypted)
    
    def decrypt_file(self, filepath: str) -> None:
        """Decrypt file in place"""
        with open(filepath, 'rb') as f:
            encrypted = f.read()
        data = self.cipher.decrypt(encrypted)
        with open(filepath, 'wb') as f:
            f.write(data)

# Usage
encryption = EncryptionManager(os.environ['ENCRYPTION_KEY'])
encrypted_memory = encryption.encrypt("sensitive user memory")
```

### Secure Memory Storage

```python
class SecureMemoryStore:
    """Store memories with encryption"""
    
    def __init__(self, encryption_manager: EncryptionManager):
        self.encryption = encryption_manager
    
    def store_memory(self, user_id: str, memory: dict) -> str:
        """Store encrypted memory"""
        import json
        memory_json = json.dumps(memory)
        encrypted = self.encryption.encrypt(memory_json)
        
        # Store in database with user_id
        # ... database logic
        
        return encrypted
    
    def retrieve_memory(self, memory_id: str, user_id: str) -> dict:
        """Retrieve and decrypt memory"""
        import json
        # Retrieve from database, verify user_id
        encrypted = "..."  # from database
        
        decrypted = self.encryption.decrypt(encrypted)
        return json.loads(decrypted)
```

---

## API SECURITY

### Rate Limiting Strategy

```python
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Tuple

class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, requests_per_minute: int = 60):
        self.rpm = requests_per_minute
        self.buckets: Dict[str, Tuple[int, datetime]] = defaultdict(
            lambda: (self.rpm, datetime.utcnow())
        )
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed"""
        tokens, last_update = self.buckets[client_id]
        now = datetime.utcnow()
        
        # Refill tokens
        time_passed = (now - last_update).total_seconds()
        tokens_to_add = int(time_passed * self.rpm / 60)
        tokens = min(self.rpm, tokens + tokens_to_add)
        
        if tokens > 0:
            self.buckets[client_id] = (tokens - 1, now)
            return True
        else:
            self.buckets[client_id] = (tokens, last_update)
            return False

# FastAPI middleware
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, rpm: int = 60):
        super().__init__(app)
        self.limiter = RateLimiter(rpm)
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        
        if not self.limiter.is_allowed(client_ip):
            raise HTTPException(status_code=429, detail="Too many requests")
        
        response = await call_next(request)
        return response
```

### CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

# Secure CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://app.yourdomain.com",
    ],  # Never use ["*"] in production!
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=3600,
)
```

### Request Signing

```python
import hmac
import hashlib

def sign_request(data: str, secret: str) -> str:
    """Sign request with HMAC"""
    return hmac.new(
        secret.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()

def verify_signature(data: str, signature: str, secret: str) -> bool:
    """Verify request signature"""
    expected = sign_request(data, secret)
    return hmac.compare_digest(expected, signature)
```

---

## SECRETS MANAGEMENT

### Environment Variables

```python
import os
from typing import Optional

class SecretManager:
    """Manage secrets from environment"""
    
    @staticmethod
    def get_secret(key: str, required: bool = True) -> Optional[str]:
        value = os.environ.get(key)
        if required and value is None:
            raise ValueError(f"Required secret {key} not found")
        return value
    
    @staticmethod
    def validate_secrets() -> None:
        """Validate all required secrets are present"""
        required = [
            'SECRET_KEY',
            'DATABASE_URL',
            'ENCRYPTION_KEY',
        ]
        missing = [k for k in required if not os.environ.get(k)]
        if missing:
            raise ValueError(f"Missing required secrets: {missing}")
```

### Secrets Rotation

```python
from datetime import datetime, timedelta

class SecretRotationManager:
    """Manage secret rotation"""
    
    def __init__(self):
        self.rotation_period = timedelta(days=90)
        self.warning_period = timedelta(days=7)
    
    def check_rotation_needed(self, secret_created_at: datetime) -> tuple[bool, str]:
        """Check if secret needs rotation"""
        age = datetime.utcnow() - secret_created_at
        
        if age > self.rotation_period:
            return True, "SECRET_EXPIRED"
        elif age > (self.rotation_period - self.warning_period):
            return False, "SECRET_EXPIRING_SOON"
        else:
            return False, "SECRET_OK"
```

---

## DEPENDENCY SECURITY

### Dependency Scanning

```yaml
# .github/workflows/security-scan.yml
name: Security Scan

on:
  schedule:
    - cron: '0 0 * * *'  # Daily
  pull_request:
  push:
    branches: [main]

jobs:
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Snyk
        uses: snyk/actions/python@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high
      
      - name: Run Safety
        run: |
          pip install safety
          safety check --json
```

### Requirements Pinning

```
# requirements.txt - Pin exact versions
flask==3.0.0
pydantic==2.5.0
sqlalchemy==2.0.23

# requirements-dev.txt
-r requirements.txt
pytest==7.4.3
black==23.12.0
ruff==0.1.6
```

---

## INCIDENT RESPONSE

### Incident Classification

| Severity | Description | Response Time | Escalation |
|----------|-------------|---------------|------------|
| P0 - Critical | Data breach, system down | Immediate | CEO, CTO |
| P1 - High | Security vulnerability | <1 hour | Security Lead |
| P2 - Medium | Degraded service | <4 hours | On-call Engineer |
| P3 - Low | Minor issue | <24 hours | Team |

### Incident Response Playbook

1. **Detection**
   - Alert triggered
   - Manual report
   - Automated scan

2. **Assessment**
   - Classify severity
   - Identify affected systems
   - Determine scope

3. **Containment**
   - Isolate affected systems
   - Block malicious actors
   - Preserve evidence

4. **Eradication**
   - Remove threat
   - Patch vulnerabilities
   - Update configurations

5. **Recovery**
   - Restore services
   - Verify integrity
   - Monitor for recurrence

6. **Lessons Learned**
   - Post-mortem analysis
   - Update procedures
   - Implement preventions

### Security Audit Logging

```python
import logging
from datetime import datetime
from typing import Optional

class SecurityAuditLogger:
    """Log security-relevant events"""
    
    def __init__(self):
        self.logger = logging.getLogger('security.audit')
    
    def log_authentication(
        self,
        user_id: str,
        success: bool,
        ip_address: str,
        user_agent: str
    ):
        self.logger.info(
            "Authentication attempt",
            extra={
                "event": "auth",
                "user_id": user_id,
                "success": success,
                "ip": ip_address,
                "user_agent": user_agent,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def log_authorization(
        self,
        user_id: str,
        resource: str,
        action: str,
        allowed: bool
    ):
        self.logger.info(
            "Authorization check",
            extra={
                "event": "authz",
                "user_id": user_id,
                "resource": resource,
                "action": action,
                "allowed": allowed,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def log_data_access(
        self,
        user_id: str,
        data_type: str,
        data_id: str,
        operation: str
    ):
        self.logger.info(
            "Data access",
            extra={
                "event": "data_access",
                "user_id": user_id,
                "data_type": data_type,
                "data_id": data_id,
                "operation": operation,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
```

---

## COMPLIANCE & AUDITING

### GDPR Compliance

```python
class GDPRCompliance:
    """GDPR compliance utilities"""
    
    def export_user_data(self, user_id: str) -> dict:
        """Export all user data (Right to Access)"""
        return {
            "user_profile": {},  # from database
            "conversations": [],  # from database
            "memories": [],      # from vector store
            "metadata": {}       # timestamps, etc.
        }
    
    def delete_user_data(self, user_id: str) -> None:
        """Delete all user data (Right to Erasure)"""
        # Delete from all systems
        # - Database
        # - Vector store
        # - Cache
        # - Logs (anonymize)
        # - Backups (mark for deletion)
        pass
    
    def get_consent_status(self, user_id: str) -> dict:
        """Get user consent status"""
        return {
            "data_processing": True,
            "analytics": False,
            "marketing": False,
            "updated_at": "2025-11-23T00:00:00Z"
        }
```

### Security Checklist

- [ ] All user inputs validated and sanitized
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (output encoding)
- [ ] CSRF protection enabled
- [ ] Secure password hashing (bcrypt, argon2)
- [ ] HTTPS enforced
- [ ] Security headers configured
- [ ] Rate limiting implemented
- [ ] Secrets not in source code
- [ ] Dependencies regularly updated
- [ ] Vulnerability scanning automated
- [ ] Audit logging comprehensive
- [ ] Backup and recovery tested
- [ ] Incident response plan documented
- [ ] Access control implemented
- [ ] Data encryption at rest and in transit
- [ ] Regular security training for team
- [ ] Penetration testing conducted

---

**Document Version:** 1.0  
**Last Updated:** November 23, 2025  
**Classification:** INTERNAL USE ONLY
