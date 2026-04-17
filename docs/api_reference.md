# 1ai-reach API Reference

## Overview

The 1ai-reach API is built with **FastAPI** and provides a unified interface for:
- **Webhooks**: Receive events from WAHA (WhatsApp) and CAPI (lead forms)
- **Agent Control**: Manage pipeline execution, leads, and integrations
- **MCP (Model Control Protocol)**: Expose system state and operations to AI agents
- **Admin**: System-level controls and monitoring

All endpoints return **JSON** responses. Errors include error codes and descriptive messages.

## Base URL

```
http://localhost:8000
```

## Authentication

### API Key Authentication

Secured endpoints require an `X-API-Key` header:

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/v1/agents/config
```

**Endpoints requiring authentication:**
- All `/api/v1/agents/*` endpoints
- All `/api/v1/admin/*` endpoints
- All `/api/v1/mcp` endpoints

**Endpoints NOT requiring authentication:**
- `/health` - Health check
- `/api/v1/health` - Health check (v1)
- `/api/v1/webhooks/waha/*` - WAHA webhooks (may use IP whitelisting)
- `/api/v1/webhooks/capi/*` - CAPI webhooks (may use signature verification)

### Rate Limiting

The API implements rate limiting to prevent abuse:
- **Limit**: 100 requests per minute per IP
- **Response**: `429 Too Many Requests` when limit exceeded
- **Header**: `Retry-After` indicates seconds to wait

```bash
HTTP/1.1 429 Too Many Requests
Retry-After: 60
```

## Health Check

### GET /health

Basic health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

**Status Codes:**
- `200 OK` - Service is healthy

---

### GET /api/v1/health

Health check endpoint (v1 API).

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

**Status Codes:**
- `200 OK` - Service is healthy

---

## Webhooks

### WAHA Webhooks

WAHA (WhatsApp HTTP API) webhooks for receiving messages and status updates.

#### POST /api/v1/webhooks/waha/message

Receive incoming WhatsApp messages.

**Request Body:**
```json
{
  "session": "default",
  "from": "+62812345678",
  "body": "Hello, I'm interested in your services",
  "timestamp": 1234567890,
  "messageId": "msg_123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Message received and processed"
}
```

**Status Codes:**
- `200 OK` - Message processed successfully
- `400 Bad Request` - Invalid request format
- `422 Unprocessable Entity` - Validation error

---

#### POST /api/v1/webhooks/waha/status

Receive WhatsApp message delivery status updates.

**Request Body:**
```json
{
  "session": "default",
  "messageId": "msg_123",
  "status": "delivered",
  "timestamp": 1234567890
}
```

**Response:**
```json
{
  "success": true,
  "message": "Status updated"
}
```

**Status Codes:**
- `200 OK` - Status updated successfully
- `400 Bad Request` - Invalid request format
- `422 Unprocessable Entity` - Validation error

---

### CAPI Webhooks

CAPI (Customer API) webhooks for receiving lead form submissions.

#### POST /api/v1/webhooks/capi/lead

Receive new lead submissions from web forms.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+62812345678",
  "company": "Acme Corp",
  "message": "Interested in your services"
}
```

**Response:**
```json
{
  "success": true,
  "leadId": "lead_123",
  "message": "Lead created successfully"
}
```

**Status Codes:**
- `200 OK` - Lead created successfully
- `400 Bad Request` - Invalid request format
- `422 Unprocessable Entity` - Validation error

---

## Agent Control API

### Configuration & Status

#### GET /api/v1/agents/config

Get agent configuration and settings.

**Headers:**
```
X-API-Key: your-api-key
```

**Response:**
```json
{
  "success": true,
  "data": {
    "pipeline_enabled": true,
    "auto_learn_enabled": true,
    "voice_enabled": true,
    "rate_limit": 100
  }
}
```

**Status Codes:**
- `200 OK` - Configuration retrieved
- `401 Unauthorized` - Missing or invalid API key
- `403 Forbidden` - Insufficient permissions

---

#### GET /api/v1/agents/status

Get current system status.

**Headers:**
```
X-API-Key: your-api-key
```

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "running",
    "uptime_seconds": 3600,
    "active_jobs": 2,
    "last_update": "2024-04-18T10:30:00Z"
  }
}
```

**Status Codes:**
- `200 OK` - Status retrieved
- `401 Unauthorized` - Missing or invalid API key

---

### Funnel Management

#### GET /api/v1/agents/funnel

Get lead funnel statistics.

**Headers:**
```
X-API-Key: your-api-key
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_leads": 150,
    "new": 20,
    "enriched": 80,
    "contacted": 60,
    "replied": 15,
    "meeting_booked": 5,
    "won": 2
  }
}
```

**Status Codes:**
- `200 OK` - Funnel data retrieved
- `401 Unauthorized` - Missing or invalid API key

---

### Job Management

#### GET /api/v1/agents/jobs

List all background jobs.

**Headers:**
```
X-API-Key: your-api-key
```

**Query Parameters:**
- `status` (optional): Filter by status (running, completed, failed)
- `limit` (optional): Maximum results (default: 50)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "job_id": "job_123",
      "stage": "scraper",
      "status": "running",
      "progress": 45,
      "started_at": "2024-04-18T10:00:00Z"
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Jobs retrieved
- `401 Unauthorized` - Missing or invalid API key

---

#### GET /api/v1/agents/jobs/{job_id}

Get details of a specific job.

**Headers:**
```
X-API-Key: your-api-key
```

**Path Parameters:**
- `job_id` (required): Job identifier

**Response:**
```json
{
  "success": true,
  "data": {
    "job_id": "job_123",
    "stage": "scraper",
    "status": "running",
    "progress": 45,
    "started_at": "2024-04-18T10:00:00Z",
    "logs": ["Starting scraper...", "Found 10 leads..."]
  }
}
```

**Status Codes:**
- `200 OK` - Job details retrieved
- `401 Unauthorized` - Missing or invalid API key
- `404 Not Found` - Job not found

---

#### POST /api/v1/agents/jobs/{job_id}/stop

Stop a running job.

**Headers:**
```
X-API-Key: your-api-key
```

**Path Parameters:**
- `job_id` (required): Job identifier

**Response:**
```json
{
  "success": true,
  "message": "Job stopped successfully"
}
```

**Status Codes:**
- `200 OK` - Job stopped
- `401 Unauthorized` - Missing or invalid API key
- `404 Not Found` - Job not found
- `409 Conflict` - Job already completed

---

### Pipeline Stages

#### POST /api/v1/agents/stages/{stage}/start

Start a specific pipeline stage.

**Headers:**
```
X-API-Key: your-api-key
```

**Path Parameters:**
- `stage` (required): Stage name (scraper, enricher, researcher, generator, reviewer, blaster, followup)

**Request Body:**
```json
{
  "query": "Digital Agency in Jakarta",
  "limit": 50
}
```

**Response:**
```json
{
  "success": true,
  "job_id": "job_123",
  "message": "Stage started"
}
```

**Status Codes:**
- `200 OK` - Stage started
- `401 Unauthorized` - Missing or invalid API key
- `400 Bad Request` - Invalid stage or parameters
- `409 Conflict` - Another job already running

---

#### POST /api/v1/agents/stages/{stage}/run

Run a specific pipeline stage (synchronous).

**Headers:**
```
X-API-Key: your-api-key
```

**Path Parameters:**
- `stage` (required): Stage name

**Request Body:**
```json
{
  "query": "Digital Agency in Jakarta",
  "limit": 50
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "leads_processed": 50,
    "duration_seconds": 120
  }
}
```

**Status Codes:**
- `200 OK` - Stage completed
- `401 Unauthorized` - Missing or invalid API key
- `400 Bad Request` - Invalid stage or parameters
- `504 Gateway Timeout` - Stage took too long

---

### Lead Management

#### GET /api/v1/agents/leads

List all leads.

**Headers:**
```
X-API-Key: your-api-key
```

**Query Parameters:**
- `status` (optional): Filter by status (new, enriched, contacted, replied, etc.)
- `limit` (optional): Maximum results (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "lead_123",
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+62812345678",
      "company": "Acme Corp",
      "status": "contacted",
      "score": 75
    }
  ],
  "total": 150
}
```

**Status Codes:**
- `200 OK` - Leads retrieved
- `401 Unauthorized` - Missing or invalid API key

---

#### GET /api/v1/agents/leads/{lead_id}

Get details of a specific lead.

**Headers:**
```
X-API-Key: your-api-key
```

**Path Parameters:**
- `lead_id` (required): Lead identifier

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "lead_123",
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+62812345678",
    "company": "Acme Corp",
    "status": "contacted",
    "score": 75,
    "created_at": "2024-04-18T10:00:00Z",
    "last_contacted": "2024-04-18T11:00:00Z"
  }
}
```

**Status Codes:**
- `200 OK` - Lead retrieved
- `401 Unauthorized` - Missing or invalid API key
- `404 Not Found` - Lead not found

---

#### PATCH /api/v1/agents/leads/{lead_id}/status

Update lead status.

**Headers:**
```
X-API-Key: your-api-key
```

**Path Parameters:**
- `lead_id` (required): Lead identifier

**Request Body:**
```json
{
  "status": "replied"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Lead status updated"
}
```

**Status Codes:**
- `200 OK` - Status updated
- `401 Unauthorized` - Missing or invalid API key
- `404 Not Found` - Lead not found
- `400 Bad Request` - Invalid status

---

#### PATCH /api/v1/agents/leads/{lead_id}/fields

Update lead fields.

**Headers:**
```
X-API-Key: your-api-key
```

**Path Parameters:**
- `lead_id` (required): Lead identifier

**Request Body:**
```json
{
  "email": "newemail@example.com",
  "phone": "+62812345679",
  "notes": "Updated contact info"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Lead fields updated"
}
```

**Status Codes:**
- `200 OK` - Fields updated
- `401 Unauthorized` - Missing or invalid API key
- `404 Not Found` - Lead not found
- `400 Bad Request` - Invalid fields

---

### Testing

#### POST /api/v1/agents/test/email

Send a test email.

**Headers:**
```
X-API-Key: your-api-key
```

**Request Body:**
```json
{
  "to": "test@example.com",
  "subject": "Test Email",
  "body": "This is a test email"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Test email sent"
}
```

**Status Codes:**
- `200 OK` - Email sent
- `401 Unauthorized` - Missing or invalid API key
- `400 Bad Request` - Invalid email address

---

#### POST /api/v1/agents/test/whatsapp

Send a test WhatsApp message.

**Headers:**
```
X-API-Key: your-api-key
```

**Request Body:**
```json
{
  "phone": "+62812345678",
  "message": "This is a test message"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Test message sent"
}
```

**Status Codes:**
- `200 OK` - Message sent
- `401 Unauthorized` - Missing or invalid API key
- `400 Bad Request` - Invalid phone number

---

### WhatsApp Sessions

#### GET /api/v1/agents/wa/sessions

List all WhatsApp sessions.

**Headers:**
```
X-API-Key: your-api-key
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "name": "default",
      "phone": "+62812345678",
      "status": "connected",
      "last_activity": "2024-04-18T11:00:00Z"
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Sessions retrieved
- `401 Unauthorized` - Missing or invalid API key

---

#### POST /api/v1/agents/wa/sessions

Create a new WhatsApp session.

**Headers:**
```
X-API-Key: your-api-key
```

**Request Body:**
```json
{
  "name": "session_name",
  "phone": "+62812345678"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Session created"
}
```

**Status Codes:**
- `200 OK` - Session created
- `401 Unauthorized` - Missing or invalid API key
- `400 Bad Request` - Invalid parameters

---

#### GET /api/v1/agents/wa/sessions/{session_name}

Get WhatsApp session details.

**Headers:**
```
X-API-Key: your-api-key
```

**Path Parameters:**
- `session_name` (required): Session name

**Response:**
```json
{
  "success": true,
  "data": {
    "name": "default",
    "phone": "+62812345678",
    "status": "connected",
    "last_activity": "2024-04-18T11:00:00Z"
  }
}
```

**Status Codes:**
- `200 OK` - Session retrieved
- `401 Unauthorized` - Missing or invalid API key
- `404 Not Found` - Session not found

---

#### DELETE /api/v1/agents/wa/sessions/{session_name}

Delete a WhatsApp session.

**Headers:**
```
X-API-Key: your-api-key
```

**Path Parameters:**
- `session_name` (required): Session name

**Response:**
```json
{
  "success": true,
  "message": "Session deleted"
}
```

**Status Codes:**
- `200 OK` - Session deleted
- `401 Unauthorized` - Missing or invalid API key
- `404 Not Found` - Session not found

---

#### GET /api/v1/agents/wa/sessions/{session_name}/qr

Get WhatsApp session QR code for authentication.

**Headers:**
```
X-API-Key: your-api-key
```

**Path Parameters:**
- `session_name` (required): Session name

**Response:**
```json
{
  "success": true,
  "data": {
    "qr_code": "data:image/png;base64,...",
    "expires_at": "2024-04-18T11:05:00Z"
  }
}
```

**Status Codes:**
- `200 OK` - QR code retrieved
- `401 Unauthorized` - Missing or invalid API key
- `404 Not Found` - Session not found

---

### Knowledge Base

#### GET /api/v1/agents/kb

Get knowledge base entries.

**Headers:**
```
X-API-Key: your-api-key
```

**Query Parameters:**
- `category` (optional): Filter by category
- `limit` (optional): Maximum results (default: 50)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "kb_123",
      "category": "services",
      "content": "We offer digital marketing services...",
      "created_at": "2024-04-18T10:00:00Z"
    }
  ]
}
```

**Status Codes:**
- `200 OK` - KB entries retrieved
- `401 Unauthorized` - Missing or invalid API key

---

#### POST /api/v1/agents/kb

Add a knowledge base entry.

**Headers:**
```
X-API-Key: your-api-key
```

**Request Body:**
```json
{
  "category": "services",
  "content": "We offer digital marketing services..."
}
```

**Response:**
```json
{
  "success": true,
  "id": "kb_123",
  "message": "KB entry created"
}
```

**Status Codes:**
- `200 OK` - KB entry created
- `401 Unauthorized` - Missing or invalid API key
- `400 Bad Request` - Invalid parameters

---

### Monitoring & Analytics

#### GET /api/v1/agents/events

Get system events and audit log.

**Headers:**
```
X-API-Key: your-api-key
```

**Query Parameters:**
- `type` (optional): Filter by event type
- `limit` (optional): Maximum results (default: 50)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "timestamp": "2024-04-18T11:00:00Z",
      "type": "lead_created",
      "details": {"lead_id": "lead_123"}
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Events retrieved
- `401 Unauthorized` - Missing or invalid API key

---

#### GET /api/v1/agents/integrations

Get integration status.

**Headers:**
```
X-API-Key: your-api-key
```

**Response:**
```json
{
  "success": true,
  "data": {
    "brain": {"status": "connected", "last_sync": "2024-04-18T11:00:00Z"},
    "waha": {"status": "connected", "sessions": 1},
    "n8n": {"status": "connected", "workflows": 5}
  }
}
```

**Status Codes:**
- `200 OK` - Integration status retrieved
- `401 Unauthorized` - Missing or invalid API key

---

## MCP (Model Control Protocol)

### POST /api/v1/mcp

Execute MCP method calls.

**Headers:**
```
X-API-Key: your-api-key
Content-Type: application/json
```

**Request Body (JSON-RPC 2.0):**
```json
{
  "jsonrpc": "2.0",
  "method": "get_funnel_state",
  "params": {},
  "id": 1
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "total_leads": 150,
    "funnel_stages": {...}
  },
  "id": 1
}
```

**Status Codes:**
- `200 OK` - Method executed
- `401 Unauthorized` - Missing or invalid API key
- `400 Bad Request` - Invalid JSON-RPC request
- `500 Internal Server Error` - Method execution failed

---

### GET /api/v1/mcp/methods

List available MCP methods.

**Headers:**
```
X-API-Key: your-api-key
```

**Response:**
```json
{
  "success": true,
  "methods": [
    {
      "name": "get_funnel_state",
      "description": "Get current funnel state",
      "params": []
    },
    {
      "name": "run_stage",
      "description": "Run a pipeline stage",
      "params": ["stage", "options"]
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Methods retrieved
- `401 Unauthorized` - Missing or invalid API key

---

## Admin API

### System Control

#### POST /api/v1/admin/pause

Pause the autonomous pipeline.

**Headers:**
```
X-API-Key: your-api-key
```

**Response:**
```json
{
  "success": true,
  "message": "Pipeline paused"
}
```

**Status Codes:**
- `200 OK` - Pipeline paused
- `401 Unauthorized` - Missing or invalid API key

---

#### POST /api/v1/admin/resume

Resume the autonomous pipeline.

**Headers:**
```
X-API-Key: your-api-key
```

**Response:**
```json
{
  "success": true,
  "message": "Pipeline resumed"
}
```

**Status Codes:**
- `200 OK` - Pipeline resumed
- `401 Unauthorized` - Missing or invalid API key

---

#### GET /api/v1/admin/status

Get admin status.

**Headers:**
```
X-API-Key: your-api-key
```

**Response:**
```json
{
  "success": true,
  "data": {
    "pipeline_status": "running",
    "uptime_seconds": 3600,
    "last_action": "resume"
  }
}
```

**Status Codes:**
- `200 OK` - Status retrieved
- `401 Unauthorized` - Missing or invalid API key

---

#### GET /api/v1/admin/conversations

List all conversations.

**Headers:**
```
X-API-Key: your-api-key
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "conv_123",
      "lead_id": "lead_123",
      "channel": "whatsapp",
      "status": "active",
      "message_count": 5
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Conversations retrieved
- `401 Unauthorized` - Missing or invalid API key

---

#### POST /api/v1/admin/conversations/{conv_id}/stop

Stop a conversation.

**Headers:**
```
X-API-Key: your-api-key
```

**Path Parameters:**
- `conv_id` (required): Conversation identifier

**Response:**
```json
{
  "success": true,
  "message": "Conversation stopped"
}
```

**Status Codes:**
- `200 OK` - Conversation stopped
- `401 Unauthorized` - Missing or invalid API key
- `404 Not Found` - Conversation not found

---

## Error Responses

All error responses follow this format:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Invalid request format",
    "details": {}
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_REQUEST` | 400 | Invalid request format or parameters |
| `UNAUTHORIZED` | 401 | Missing or invalid API key |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 422 | Request validation failed |
| `CONFLICT` | 409 | Request conflicts with current state |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Internal server error |

---

## Examples

### Example 1: Get Funnel Status

```bash
curl -X GET http://localhost:8000/api/v1/agents/funnel \
  -H "X-API-Key: your-api-key"
```

### Example 2: Start Scraper Stage

```bash
curl -X POST http://localhost:8000/api/v1/agents/stages/scraper/start \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Digital Agency in Jakarta",
    "limit": 50
  }'
```

### Example 3: Update Lead Status

```bash
curl -X PATCH http://localhost:8000/api/v1/agents/leads/lead_123/status \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "replied"
  }'
```

### Example 4: Receive WAHA Webhook

```bash
curl -X POST http://localhost:8000/api/v1/webhooks/waha/message \
  -H "Content-Type: application/json" \
  -d '{
    "session": "default",
    "from": "+62812345678",
    "body": "Hello, I am interested",
    "timestamp": 1234567890,
    "messageId": "msg_123"
  }'
```

---

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Limit**: 100 requests per minute per IP address
- **Response**: `429 Too Many Requests` when limit exceeded
- **Retry-After**: Header indicates seconds to wait before retrying

Example rate-limited response:

```
HTTP/1.1 429 Too Many Requests
Retry-After: 60

{
  "success": false,
  "error": {
    "code": "RATE_LIMITED",
    "message": "Too many requests. Please try again later."
  }
}
```

---

## Pagination

Endpoints that return lists support pagination:

**Query Parameters:**
- `limit` (optional): Maximum results per page (default: 50, max: 500)
- `offset` (optional): Number of results to skip (default: 0)

**Response:**
```json
{
  "success": true,
  "data": [...],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

---

## Versioning

The API uses URL-based versioning:

- **Current Version**: `/api/v1/`
- **Legacy**: `/` (deprecated, use v1)

All new code should use `/api/v1/` endpoints.

---

## Support

For API issues or questions:
1. Check the [Architecture Overview](docs/architecture.md)
2. Review [Data Models](docs/data_models.md)
3. Check [Migration Guide](docs/migration_guide.md) for legacy integration
