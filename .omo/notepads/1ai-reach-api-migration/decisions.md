## Architectural Decisions

### Authentication Strategy

**Decision**: Use simple API key authentication via X-API-Key header

**Rationale**:
- Simpler than OAuth/JWT for internal API usage
- Easy to configure and rotate keys
- Sufficient security for backend-to-backend communication
- FastAPI Depends() pattern makes it easy to apply

**Alternatives Considered**:
- JWT tokens: Too complex for this use case
- OAuth2: Overkill for internal API
- Basic Auth: Less secure, harder to rotate credentials

### Rate Limiting Strategy

**Decision**: Sliding window rate limiting per IP address

**Rationale**:
- More accurate than fixed window (prevents burst attacks)
- Per-IP limiting prevents single client from overwhelming server
- Configurable limit allows tuning based on load
- Middleware approach applies to all endpoints uniformly

**Implementation Details**:
- Uses in-memory storage (simple, fast)
- Cleans up old entries automatically
- Exempts health checks (monitoring shouldn't be rate limited)
- Returns standard 429 status with Retry-After header

### Webhook Security

**Decision**: Webhooks remain open (no API key required)

**Rationale**:
- External services (WAHA, CAPI) need to call webhooks
- Webhook signature verification is the proper security mechanism
- API keys would complicate webhook configuration

**Future Enhancement**:
- Add HMAC signature verification for webhooks
- Use WAHA_WEBHOOK_SECRET for signature validation
