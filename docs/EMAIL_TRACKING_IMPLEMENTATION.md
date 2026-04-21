# Email Tracking Implementation Guide
## 1ai-reach Cold Outreach System

**Date:** 2026-04-21
**Status:** Implementation Roadmap

---

## PHASE 1: EMAIL OPEN TRACKING

### 1.1 Database Schema Update

Add tracking fields to leads table:

```sql
ALTER TABLE leads ADD COLUMN email_opened_at TEXT;
ALTER TABLE leads ADD COLUMN email_open_count INTEGER DEFAULT 0;
ALTER TABLE leads ADD COLUMN email_first_opened_at TEXT;
```

Create email tracking events table:

```sql
CREATE TABLE IF NOT EXISTS email_tracking_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id TEXT NOT NULL,
    event_type TEXT NOT NULL,  -- 'open', 'click', 'bounce'
    event_timestamp TEXT DEFAULT (datetime('now')),
    user_agent TEXT,
    ip_address TEXT,
    metadata TEXT,  -- JSON: {url, referer, etc}
    FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE
);

CREATE INDEX idx_email_tracking_lead_id ON email_tracking_events(lead_id);
CREATE INDEX idx_email_tracking_event_type ON email_tracking_events(event_type);
```

### 1.2 Tracking Pixel Implementation

**File:** `src/oneai_reach/infrastructure/messaging/email_sender.py`

Modify `_make_html_body()` method:

```python
def _make_html_body(self, body: str, lead_id: str, message_id: str) -> str:
    """Generate branded HTML email with tracking pixel.
    
    Args:
        body: Plain text email body
        lead_id: Lead ID for tracking
        message_id: Unique message ID for tracking
    
    Returns:
        HTML email body with tracking pixel
    """
    # Escape body text for HTML
    body_html = body.replace('\n', '<br>')
    
    # Generate tracking pixel URL
    tracking_url = f"{self.settings.api.base_url}/api/v1/webhooks/email/open"
    pixel_url = f"{tracking_url}?lead_id={lead_id}&msg_id={message_id}"
    
    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #1a7a4a; color: white; padding: 20px; text-align: center; }}
            .logo {{ max-width: 150px; height: auto; }}
            .content {{ padding: 20px; background-color: #f9f9f9; }}
            .footer {{ text-align: center; font-size: 12px; color: #999; padding: 20px; }}
            a {{ color: #1a7a4a; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="{self.LOGO_URL}" alt="BerkahKarya" class="logo">
            </div>
            <div class="content">
                {body_html}
            </div>
            <div class="footer">
                <p>© 2026 BerkahKarya. All rights reserved.</p>
                <p>Jika Anda tidak ingin menerima email ini, balas dengan kata 'berhenti'</p>
            </div>
        </div>
        <!-- Tracking pixel (1x1 transparent GIF) -->
        <img src="{pixel_url}" width="1" height="1" alt="" style="display:none;" />
    </body>
    </html>
    """
    return html
```

### 1.3 Open Tracking Webhook

**File:** `src/oneai_reach/api/webhooks/email.py` (NEW)

```python
"""Email tracking webhooks for opens, clicks, and bounces."""

from fastapi import APIRouter, Request
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional

router = APIRouter(prefix="/api/v1/webhooks/email", tags=["webhooks"])


class EmailOpenPayload(BaseModel):
    lead_id: str
    msg_id: str


@router.get("/open")
async def track_email_open(
    lead_id: str,
    msg_id: str,
    request: Request
) -> dict:
    """Track email open event via pixel.
    
    Args:
        lead_id: Lead ID
        msg_id: Message ID
        request: FastAPI request object
    
    Returns:
        1x1 transparent GIF (pixel)
    """
    try:
        # Extract metadata
        user_agent = request.headers.get("user-agent", "")
        ip_address = request.client.host if request.client else ""
        
        # Store tracking event
        from oneai_reach.infrastructure.database import get_db
        db = get_db()
        
        db.execute("""
            INSERT INTO email_tracking_events 
            (lead_id, event_type, user_agent, ip_address, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (
            lead_id,
            "open",
            user_agent,
            ip_address,
            f'{{"msg_id": "{msg_id}"}}'
        ))
        
        # Update lead
        db.execute("""
            UPDATE leads 
            SET email_opened_at = ?,
                email_open_count = email_open_count + 1,
                email_first_opened_at = COALESCE(email_first_opened_at, ?)
            WHERE id = ?
        """, (
            datetime.now(timezone.utc).isoformat(),
            datetime.now(timezone.utc).isoformat(),
            lead_id
        ))
        db.commit()
        
    except Exception as e:
        logger.error(f"Error tracking email open: {e}")
    
    # Return 1x1 transparent GIF
    gif_data = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4d\x01\x00\x3b'
    
    return Response(
        content=gif_data,
        media_type="image/gif",
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )
```

### 1.4 Update Lead Model

**File:** `src/oneai_reach/domain/models/lead.py`

```python
class Lead(BaseModel):
    # ... existing fields ...
    
    # Email tracking
    email_opened_at: Optional[datetime] = None
    email_open_count: int = 0
    email_first_opened_at: Optional[datetime] = None
    email_clicked_at: Optional[datetime] = None
    email_click_count: int = 0
    bounce_status: Optional[str] = None  # hard|soft|none
```

---

## PHASE 2: EMAIL CLICK TRACKING

### 2.1 Link Rewriter Service

**File:** `src/oneai_reach/infrastructure/messaging/link_rewriter.py` (NEW)

```python
"""Link rewriting for email click tracking."""

import re
from urllib.parse import urlencode, quote
from typing import Dict, Optional


class LinkRewriter:
    """Rewrite links in email body for click tracking."""
    
    def __init__(self, base_url: str):
        """Initialize link rewriter.
        
        Args:
            base_url: Base URL for tracking service
        """
        self.base_url = base_url
        self.link_pattern = re.compile(r'href=["\']([^"\']+)["\']')
    
    def rewrite_links(
        self,
        html_body: str,
        lead_id: str,
        message_id: str
    ) -> str:
        """Rewrite all links in HTML body for tracking.
        
        Args:
            html_body: HTML email body
            lead_id: Lead ID
            message_id: Message ID
        
        Returns:
            HTML body with rewritten links
        """
        def replace_link(match):
            original_url = match.group(1)
            
            # Skip tracking pixel and unsubscribe links
            if 'webhooks/email/open' in original_url or 'berhenti' in original_url:
                return match.group(0)
            
            # Create tracking URL
            tracking_url = f"{self.base_url}/api/v1/webhooks/email/click"
            params = {
                'lead_id': lead_id,
                'msg_id': message_id,
                'url': original_url
            }
            tracked_url = f"{tracking_url}?{urlencode(params)}"
            
            return f'href="{tracked_url}"'
        
        return self.link_pattern.sub(replace_link, html_body)
```

### 2.2 Click Tracking Webhook

**File:** `src/oneai_reach/api/webhooks/email.py` (ADD TO EXISTING)

```python
@router.get("/click")
async def track_email_click(
    lead_id: str,
    msg_id: str,
    url: str,
    request: Request
) -> RedirectResponse:
    """Track email click and redirect to original URL.
    
    Args:
        lead_id: Lead ID
        msg_id: Message ID
        url: Original URL to redirect to
        request: FastAPI request object
    
    Returns:
        Redirect to original URL
    """
    try:
        # Extract metadata
        user_agent = request.headers.get("user-agent", "")
        ip_address = request.client.host if request.client else ""
        referer = request.headers.get("referer", "")
        
        # Store tracking event
        from oneai_reach.infrastructure.database import get_db
        db = get_db()
        
        db.execute("""
            INSERT INTO email_tracking_events 
            (lead_id, event_type, user_agent, ip_address, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (
            lead_id,
            "click",
            user_agent,
            ip_address,
            f'{{"msg_id": "{msg_id}", "url": "{url}", "referer": "{referer}"}}'
        ))
        
        # Update lead
        db.execute("""
            UPDATE leads 
            SET email_clicked_at = ?,
                email_click_count = email_click_count + 1
            WHERE id = ?
        """, (
            datetime.now(timezone.utc).isoformat(),
            lead_id
        ))
        db.commit()
        
    except Exception as e:
        logger.error(f"Error tracking email click: {e}")
    
    # Redirect to original URL
    return RedirectResponse(url=url, status_code=302)
```

### 2.3 Update Email Sender

**File:** `src/oneai_reach/infrastructure/messaging/email_sender.py`

```python
def send(self, email: str, subject: str, body: str, lead_id: str = None) -> bool:
    """Send email with fallback chain and tracking.
    
    Args:
        email: Recipient email address
        subject: Email subject
        body: Email body (plain text)
        lead_id: Lead ID for tracking (optional)
    
    Returns:
        True if sent successfully, False otherwise
    """
    # Generate message ID
    message_id = f"{lead_id}_{int(time.time())}" if lead_id else str(uuid.uuid4())
    
    # Convert to HTML with tracking
    html_body = self._make_html_body(body, lead_id, message_id)
    
    # Rewrite links for click tracking
    if lead_id:
        from oneai_reach.infrastructure.messaging.link_rewriter import LinkRewriter
        rewriter = LinkRewriter(self.settings.api.base_url)
        html_body = rewriter.rewrite_links(html_body, lead_id, message_id)
    
    # Try fallback chain
    return (
        self._send_via_brevo(email, subject, html_body)
        or self._send_via_stalwart(email, subject, html_body)
        or self._send_via_gog(email, subject, html_body)
        or self._send_via_himalaya(email, subject, html_body)
        or self._send_via_queue(email, subject, html_body)
    )
```

---

## PHASE 3: BOUNCE HANDLING

### 3.1 Bounce Webhook

**File:** `src/oneai_reach/api/webhooks/email.py` (ADD TO EXISTING)

```python
class BouncePayload(BaseModel):
    email: str
    bounce_type: str  # hard|soft
    bounce_subtype: str  # permanent|transient|undetermined
    timestamp: str


@router.post("/bounce")
async def handle_email_bounce(payload: BouncePayload) -> dict:
    """Handle email bounce webhook from Brevo.
    
    Args:
        payload: Bounce event payload
    
    Returns:
        Webhook response
    """
    try:
        from oneai_reach.infrastructure.database import get_db
        db = get_db()
        
        # Find lead by email
        lead = db.execute(
            "SELECT id FROM leads WHERE email = ?",
            (payload.email,)
        ).fetchone()
        
        if not lead:
            return {"status": "ok", "message": "lead_not_found"}
        
        lead_id = lead[0]
        
        # Store bounce event
        db.execute("""
            INSERT INTO email_tracking_events 
            (lead_id, event_type, metadata)
            VALUES (?, ?, ?)
        """, (
            lead_id,
            "bounce",
            f'{{"bounce_type": "{payload.bounce_type}", "subtype": "{payload.bounce_subtype}"}}'
        ))
        
        # Update lead
        if payload.bounce_type == "hard":
            # Hard bounce: mark as unsubscribed
            db.execute("""
                UPDATE leads 
                SET status = ?, bounce_status = ?
                WHERE id = ?
            """, ("unsubscribed", "hard", lead_id))
        else:
            # Soft bounce: just track
            db.execute("""
                UPDATE leads 
                SET bounce_status = ?
                WHERE id = ?
            """, ("soft", lead_id))
        
        db.commit()
        
        return {"status": "ok", "bounce_type": payload.bounce_type}
        
    except Exception as e:
        logger.error(f"Error handling bounce: {e}")
        return {"status": "error", "message": str(e)}
```

### 3.2 Configure Brevo Webhook

In Brevo dashboard:
1. Go to Settings → Webhooks
2. Add webhook URL: `https://your-domain.com/api/v1/webhooks/email/bounce`
3. Select events: `bounce`
4. Save

---

## PHASE 4: ENGAGEMENT SCORING

### 4.1 Engagement Service

**File:** `src/oneai_reach/application/analytics/engagement_service.py` (NEW)

```python
"""Email engagement scoring and analytics."""

from datetime import datetime, timedelta
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class EngagementMetrics:
    """Email engagement metrics."""
    opens: int = 0
    clicks: int = 0
    replies: int = 0
    bounces: int = 0
    score: float = 0.0
    level: str = "cold"  # cold|warm|hot


class EngagementService:
    """Calculate engagement scores for leads."""
    
    # Scoring weights
    WEIGHTS = {
        "open": 1.0,
        "click": 3.0,
        "reply": 10.0,
        "bounce": -5.0,
    }
    
    # Engagement levels
    LEVELS = {
        "cold": (0, 5),
        "warm": (5, 15),
        "hot": (15, 100),
    }
    
    def __init__(self, db_connection):
        """Initialize engagement service.
        
        Args:
            db_connection: Database connection
        """
        self.db = db_connection
    
    def calculate_engagement(self, lead_id: str) -> EngagementMetrics:
        """Calculate engagement metrics for a lead.
        
        Args:
            lead_id: Lead ID
        
        Returns:
            EngagementMetrics object
        """
        # Get tracking events
        events = self.db.execute("""
            SELECT event_type, COUNT(*) as count
            FROM email_tracking_events
            WHERE lead_id = ?
            GROUP BY event_type
        """, (lead_id,)).fetchall()
        
        metrics = EngagementMetrics()
        
        for event_type, count in events:
            if event_type == "open":
                metrics.opens = count
            elif event_type == "click":
                metrics.clicks = count
            elif event_type == "bounce":
                metrics.bounces = count
        
        # Check for reply
        lead = self.db.execute(
            "SELECT replied_at FROM leads WHERE id = ?",
            (lead_id,)
        ).fetchone()
        
        if lead and lead[0]:
            metrics.replies = 1
        
        # Calculate score
        metrics.score = (
            metrics.opens * self.WEIGHTS["open"] +
            metrics.clicks * self.WEIGHTS["click"] +
            metrics.replies * self.WEIGHTS["reply"] +
            metrics.bounces * self.WEIGHTS["bounce"]
        )
        
        # Determine level
        for level, (min_score, max_score) in self.LEVELS.items():
            if min_score <= metrics.score < max_score:
                metrics.level = level
                break
        
        return metrics
    
    def get_engagement_report(self) -> Dict:
        """Get engagement report for all leads.
        
        Returns:
            Engagement report with metrics and segments
        """
        leads = self.db.execute(
            "SELECT id FROM leads WHERE status IN ('contacted', 'followed_up', 'replied')"
        ).fetchall()
        
        report = {
            "total_leads": len(leads),
            "segments": {
                "cold": 0,
                "warm": 0,
                "hot": 0,
            },
            "metrics": {
                "avg_opens": 0,
                "avg_clicks": 0,
                "avg_score": 0,
                "open_rate": 0,
                "click_rate": 0,
                "reply_rate": 0,
            }
        }
        
        total_opens = 0
        total_clicks = 0
        total_score = 0
        total_replies = 0
        
        for (lead_id,) in leads:
            metrics = self.calculate_engagement(lead_id)
            report["segments"][metrics.level] += 1
            total_opens += metrics.opens
            total_clicks += metrics.clicks
            total_score += metrics.score
            total_replies += metrics.replies
        
        if leads:
            report["metrics"]["avg_opens"] = total_opens / len(leads)
            report["metrics"]["avg_clicks"] = total_clicks / len(leads)
            report["metrics"]["avg_score"] = total_score / len(leads)
            report["metrics"]["open_rate"] = (total_opens / len(leads)) * 100
            report["metrics"]["click_rate"] = (total_clicks / len(leads)) * 100
            report["metrics"]["reply_rate"] = (total_replies / len(leads)) * 100
        
        return report
```

### 4.2 Analytics API Endpoint

**File:** `src/oneai_reach/api/analytics.py` (NEW)

```python
"""Analytics API endpoints."""

from fastapi import APIRouter, Depends
from oneai_reach.application.analytics.engagement_service import EngagementService

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/engagement")
async def get_engagement_report(db = Depends(get_db)) -> dict:
    """Get email engagement report.
    
    Returns:
        Engagement metrics and segments
    """
    service = EngagementService(db)
    return service.get_engagement_report()


@router.get("/engagement/{lead_id}")
async def get_lead_engagement(lead_id: str, db = Depends(get_db)) -> dict:
    """Get engagement metrics for a specific lead.
    
    Args:
        lead_id: Lead ID
    
    Returns:
        Engagement metrics
    """
    service = EngagementService(db)
    metrics = service.calculate_engagement(lead_id)
    return {
        "lead_id": lead_id,
        "opens": metrics.opens,
        "clicks": metrics.clicks,
        "replies": metrics.replies,
        "bounces": metrics.bounces,
        "score": metrics.score,
        "level": metrics.level,
    }
```

---

## IMPLEMENTATION CHECKLIST

### Phase 1: Email Open Tracking
- [ ] Add `email_opened_at`, `email_open_count`, `email_first_opened_at` to leads table
- [ ] Create `email_tracking_events` table
- [ ] Implement tracking pixel in `_make_html_body()`
- [ ] Create `/api/v1/webhooks/email/open` endpoint
- [ ] Update Lead model with tracking fields
- [ ] Test pixel tracking with test email

### Phase 2: Email Click Tracking
- [ ] Create `LinkRewriter` service
- [ ] Implement link rewriting in email sender
- [ ] Create `/api/v1/webhooks/email/click` endpoint
- [ ] Add `email_clicked_at`, `email_click_count` to leads table
- [ ] Test click tracking with test email

### Phase 3: Bounce Handling
- [ ] Add `bounce_status` field to leads table
- [ ] Create `/api/v1/webhooks/email/bounce` endpoint
- [ ] Configure Brevo webhook
- [ ] Auto-unsubscribe on hard bounce
- [ ] Test bounce handling

### Phase 4: Engagement Scoring
- [ ] Create `EngagementService`
- [ ] Implement engagement scoring algorithm
- [ ] Create `/api/v1/analytics/engagement` endpoint
- [ ] Create `/api/v1/analytics/engagement/{lead_id}` endpoint
- [ ] Build analytics dashboard UI

---

## TESTING STRATEGY

### Unit Tests
```python
# Test link rewriter
def test_link_rewriter():
    rewriter = LinkRewriter("http://localhost:8000")
    html = '<a href="https://example.com">Click here</a>'
    result = rewriter.rewrite_links(html, "lead_123", "msg_456")
    assert "webhooks/email/click" in result
    assert "lead_id=lead_123" in result

# Test engagement scoring
def test_engagement_scoring():
    service = EngagementService(db)
    metrics = service.calculate_engagement("lead_123")
    assert metrics.score >= 0
    assert metrics.level in ["cold", "warm", "hot"]
```

### Integration Tests
```python
# Test open tracking
def test_email_open_tracking():
    # Send test email
    sender.send("test@example.com", "Test", "Body", lead_id="lead_123")
    
    # Simulate pixel load
    response = client.get("/api/v1/webhooks/email/open?lead_id=lead_123&msg_id=msg_456")
    assert response.status_code == 200
    
    # Verify tracking event
    events = db.execute("SELECT * FROM email_tracking_events WHERE lead_id = ?", ("lead_123",)).fetchall()
    assert len(events) > 0
    assert events[0]["event_type"] == "open"

# Test click tracking
def test_email_click_tracking():
    # Simulate click
    response = client.get("/api/v1/webhooks/email/click?lead_id=lead_123&msg_id=msg_456&url=https://example.com")
    assert response.status_code == 302
    assert response.headers["location"] == "https://example.com"
    
    # Verify tracking event
    events = db.execute("SELECT * FROM email_tracking_events WHERE lead_id = ?", ("lead_123",)).fetchall()
    assert any(e["event_type"] == "click" for e in events)
```

---

## DEPLOYMENT NOTES

1. **Database Migration:** Run migrations before deploying
2. **API Configuration:** Update `settings.api.base_url` for tracking URLs
3. **Brevo Webhook:** Configure webhook in Brevo dashboard
4. **Testing:** Test with staging environment first
5. **Monitoring:** Monitor webhook error rates
6. **Privacy:** Ensure GDPR compliance for tracking

---

## PERFORMANCE CONSIDERATIONS

1. **Tracking Events Table:** Add indexes on `lead_id` and `event_type`
2. **Webhook Rate Limiting:** Implement rate limiting on tracking endpoints
3. **Async Processing:** Consider async event processing for high volume
4. **Cache:** Cache engagement scores (5-minute TTL)
5. **Cleanup:** Archive old tracking events (>90 days)

