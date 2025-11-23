# API DOCUMENTATION

**AGI Studio REST API v2.0**  
**Base URL:** `http://localhost:8000/api/v1`  
**Protocol:** REST with WebSocket support

---

## TABLE OF CONTENTS

1. [Authentication](#authentication)
2. [Rate Limiting](#rate-limiting)
3. [Error Handling](#error-handling)
4. [Endpoints](#endpoints)
5. [WebSocket API](#websocket-api)
6. [SDKs & Examples](#sdks--examples)

---

## AUTHENTICATION

### Bearer Token Authentication

All API requests require a valid JWT token in the Authorization header:

```http
Authorization: Bearer <your-jwt-token>
```

### Obtaining a Token

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "your-username",
  "password": "your-password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

## RATE LIMITING

| Tier | Requests per Minute | Requests per Hour |
|------|---------------------|-------------------|
| Free | 10 | 100 |
| Pro | 60 | 1000 |
| Enterprise | Unlimited | Unlimited |

Rate limit headers are included in all responses:

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1700000000
```

---

## ERROR HANDLING

### Error Response Format

```json
{
  "error": "Validation Error",
  "detail": "Prompt cannot be empty",
  "code": "VALIDATION_ERROR",
  "timestamp": "2025-11-23T12:00:00Z"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Temporary unavailability |

### Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Input validation failed |
| `AUTHENTICATION_ERROR` | Authentication failed |
| `AUTHORIZATION_ERROR` | Insufficient permissions |
| `RATE_LIMIT_ERROR` | Rate limit exceeded |
| `INTERNAL_ERROR` | Server error |
| `MODEL_ERROR` | Model inference error |
| `NOT_FOUND` | Resource not found |

---

## ENDPOINTS

### Health Check

**GET** `/health`

Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": "2025-11-23T12:00:00Z"
}
```

---

### Text Generation

**POST** `/api/v1/generate`

Generate text using Victor model.

**Request:**
```json
{
  "prompt": "Explain quantum computing in simple terms",
  "max_tokens": 150,
  "temperature": 0.7,
  "top_p": 0.9,
  "frequency_penalty": 0.0,
  "presence_penalty": 0.0,
  "stop": ["\n\n"]
}
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | Yes | - | Input prompt (1-10000 chars) |
| `max_tokens` | integer | No | 150 | Maximum tokens to generate (1-2048) |
| `temperature` | float | No | 0.7 | Sampling temperature (0.0-2.0) |
| `top_p` | float | No | 1.0 | Nucleus sampling (0.0-1.0) |
| `frequency_penalty` | float | No | 0.0 | Frequency penalty (-2.0 to 2.0) |
| `presence_penalty` | float | No | 0.0 | Presence penalty (-2.0 to 2.0) |
| `stop` | array | No | null | Stop sequences |

**Response:**
```json
{
  "id": "gen-abc123",
  "object": "text_completion",
  "created": 1700000000,
  "model": "victor-gpt5",
  "choices": [
    {
      "text": "Quantum computing uses quantum bits...",
      "index": 0,
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 7,
    "completion_tokens": 143,
    "total_tokens": 150
  }
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Hello, world!",
    "max_tokens": 50
  }'
```

---

### Conversations

#### Create Conversation

**POST** `/api/v1/conversations`

Create a new conversation.

**Request:**
```json
{
  "title": "My First Chat",
  "system_prompt": "You are a helpful assistant."
}
```

**Response:**
```json
{
  "id": "conv-123",
  "title": "My First Chat",
  "created_at": "2025-11-23T12:00:00Z",
  "updated_at": "2025-11-23T12:00:00Z"
}
```

#### List Conversations

**GET** `/api/v1/conversations`

List all conversations for the authenticated user.

**Query Parameters:**
- `page` (integer): Page number (default: 1)
- `per_page` (integer): Items per page (default: 20, max: 100)
- `sort` (string): Sort field (default: "updated_at")
- `order` (string): Sort order ("asc" or "desc", default: "desc")

**Response:**
```json
{
  "conversations": [
    {
      "id": "conv-123",
      "title": "My First Chat",
      "message_count": 10,
      "created_at": "2025-11-23T12:00:00Z",
      "updated_at": "2025-11-23T12:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 1,
    "pages": 1
  }
}
```

#### Get Conversation

**GET** `/api/v1/conversations/{conversation_id}`

Get a specific conversation with messages.

**Response:**
```json
{
  "id": "conv-123",
  "title": "My First Chat",
  "messages": [
    {
      "id": "msg-1",
      "role": "user",
      "content": "Hello!",
      "created_at": "2025-11-23T12:00:00Z"
    },
    {
      "id": "msg-2",
      "role": "assistant",
      "content": "Hi! How can I help you?",
      "created_at": "2025-11-23T12:00:05Z"
    }
  ],
  "created_at": "2025-11-23T12:00:00Z",
  "updated_at": "2025-11-23T12:00:05Z"
}
```

#### Add Message

**POST** `/api/v1/conversations/{conversation_id}/messages`

Add a message to a conversation and get AI response.

**Request:**
```json
{
  "content": "What is quantum computing?",
  "stream": false
}
```

**Response:**
```json
{
  "user_message": {
    "id": "msg-3",
    "role": "user",
    "content": "What is quantum computing?",
    "created_at": "2025-11-23T12:05:00Z"
  },
  "assistant_message": {
    "id": "msg-4",
    "role": "assistant",
    "content": "Quantum computing is...",
    "created_at": "2025-11-23T12:05:03Z"
  }
}
```

#### Delete Conversation

**DELETE** `/api/v1/conversations/{conversation_id}`

Delete a conversation.

**Response:**
```json
{
  "status": "deleted",
  "id": "conv-123"
}
```

---

### Memory Management

#### Store Memory

**POST** `/api/v1/memory`

Store a memory for retrieval.

**Request:**
```json
{
  "content": "User prefers technical explanations",
  "type": "preference",
  "metadata": {
    "category": "communication_style"
  }
}
```

**Response:**
```json
{
  "id": "mem-abc123",
  "created_at": "2025-11-23T12:00:00Z"
}
```

#### Search Memories

**GET** `/api/v1/memory/search`

Search memories by semantic similarity.

**Query Parameters:**
- `query` (string): Search query
- `limit` (integer): Max results (default: 10, max: 50)
- `type` (string): Filter by memory type

**Response:**
```json
{
  "memories": [
    {
      "id": "mem-abc123",
      "content": "User prefers technical explanations",
      "type": "preference",
      "relevance_score": 0.95,
      "created_at": "2025-11-23T12:00:00Z"
    }
  ]
}
```

---

### Model Management

#### List Models

**GET** `/api/v1/models`

List available models.

**Response:**
```json
{
  "models": [
    {
      "id": "victor-gpt5",
      "name": "Victor GPT-5",
      "version": "1.0.0-GODCORE",
      "description": "Post-singularity grade AGI",
      "capabilities": ["text", "code", "reasoning"],
      "context_length": 8192
    }
  ]
}
```

#### Get Model Info

**GET** `/api/v1/models/{model_id}`

Get detailed model information.

**Response:**
```json
{
  "id": "victor-gpt5",
  "name": "Victor GPT-5",
  "version": "1.0.0-GODCORE",
  "architecture": "Hybrid Fractal Transformer",
  "parameters": "7B",
  "context_length": 8192,
  "capabilities": ["text", "code", "reasoning"],
  "performance": {
    "avg_latency_ms": 250,
    "throughput_tokens_per_sec": 50
  }
}
```

---

## WEBSOCKET API

### Connect

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/generate?token=YOUR_TOKEN')
```

### Send Message

```javascript
ws.send(JSON.stringify({
  type: 'generate',
  data: {
    prompt: 'Hello, world!',
    max_tokens: 50,
    stream: true
  }
}))
```

### Receive Streaming Response

```javascript
ws.onmessage = (event) => {
  const message = JSON.parse(event.data)
  
  switch (message.type) {
    case 'token':
      console.log('Token:', message.data.token)
      break
    case 'done':
      console.log('Generation complete')
      break
    case 'error':
      console.error('Error:', message.data.error)
      break
  }
}
```

---

## SDKS & EXAMPLES

### Python SDK

```python
from agi_studio import Client

client = Client(api_key="YOUR_API_KEY")

# Generate text
response = client.generate(
    prompt="Explain quantum computing",
    max_tokens=150
)
print(response.text)

# Create conversation
conversation = client.conversations.create(
    title="My Chat"
)

# Add message
response = conversation.add_message(
    "Hello, how are you?"
)
print(response.assistant_message.content)
```

### JavaScript/TypeScript SDK

```typescript
import { AgiStudioClient } from '@agi-studio/client'

const client = new AgiStudioClient({
  apiKey: 'YOUR_API_KEY'
})

// Generate text
const response = await client.generate({
  prompt: 'Explain quantum computing',
  maxTokens: 150
})
console.log(response.text)

// Stream generation
const stream = await client.generateStream({
  prompt: 'Write a story',
  maxTokens: 500
})

for await (const token of stream) {
  process.stdout.write(token)
}
```

### cURL Examples

**Generate text:**
```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Hello, world!",
    "max_tokens": 50,
    "temperature": 0.7
  }'
```

**Create conversation:**
```bash
curl -X POST http://localhost:8000/api/v1/conversations \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Chat"
  }'
```

**List conversations:**
```bash
curl -X GET "http://localhost:8000/api/v1/conversations?page=1&per_page=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## VERSIONING

API versions are specified in the URL path:

- Current: `/api/v1/...`
- Legacy: `/api/v0/...` (deprecated)

We maintain backward compatibility for at least 6 months after deprecation.

---

## SUPPORT

- **Documentation:** https://docs.agi-studio.dev
- **API Status:** https://status.agi-studio.dev
- **Issues:** https://github.com/MASSIVEMAGNETICS/agi-studio-release/issues
- **Community:** https://discord.gg/agi-studio

---

**Document Version:** 2.0.0  
**Last Updated:** November 23, 2025  
**Status:** PRODUCTION
