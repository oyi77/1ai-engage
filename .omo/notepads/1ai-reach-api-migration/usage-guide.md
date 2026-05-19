## API Authentication Usage Guide

### For Developers

#### 1. Development Mode (No Authentication)

If `API_API_KEYS` is empty or not set, the API runs in dev mode and accepts all requests:

```bash
# .env file (or leave API_API_KEYS unset)
API_API_KEYS=
```

#### 2. Production Mode (With Authentication)

Set one or more API keys in your `.env` file:

```bash
# Single key
API_API_KEYS=your_secret_key_here

# Multiple keys (comma-separated)
API_API_KEYS=key1,key2,key3
```

#### 3. Making Authenticated Requests

Include the `X-API-Key` header in your requests:

```bash
# Using curl
curl -H "X-API-Key: your_secret_key_here" http://localhost:8888/api/v1/agents/config

# Using Python requests
import requests
headers = {"X-API-Key": "your_secret_key_here"}
response = requests.get("http://localhost:8888/api/v1/agents/config", headers=headers)

# Using JavaScript fetch
fetch("http://localhost:8888/api/v1/agents/config", {
  headers: {
    "X-API-Key": "your_secret_key_here"
  }
})
```

#### 4. Endpoints That Don't Require Authentication

- `/health` - Health check
- `/api/v1/health` - Health check (v1)
- `/api/v1/webhooks/*` - All webhook endpoints

#### 5. Rate Limiting Configuration

Configure rate limiting in `.env`:

```bash
# Max requests per minute per IP (default: 100)
API_RATE_LIMIT_PER_MINUTE=100

# Enable/disable rate limiting (default: true)
API_RATE_LIMIT_ENABLED=true
```

#### 6. Error Responses

**401 Unauthorized** - Missing or invalid API key:
```json
{
  "detail": "Missing API key. Provide X-API-Key header."
}
```

**429 Too Many Requests** - Rate limit exceeded:
```json
{
  "error_code": "RATE_LIMIT_EXCEEDED",
  "message": "Rate limit exceeded. Maximum 100 requests per minute.",
  "retry_after": 60
}
```

### For Dashboard Integration

The Next.js dashboard should include the API key in all requests to secured endpoints:

```typescript
// In your API client
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    'X-API-Key': process.env.NEXT_PUBLIC_API_KEY
  }
});
```

### Security Best Practices

1. **Never commit API keys to git** - Use environment variables
2. **Use HTTPS in production** - API keys are transmitted in headers
3. **Rotate keys regularly** - Add new key, update clients, remove old key
4. **Use different keys per environment** - Dev, staging, production
5. **Monitor rate limit hits** - Adjust limits based on legitimate usage patterns
