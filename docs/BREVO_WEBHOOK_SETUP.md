# Brevo Webhook Configuration Guide

## Overview

This guide explains how to configure Brevo webhooks to enable email tracking (delivery, opens, clicks, bounces) for the 1ai-reach system.

## Prerequisites

- Brevo account with API access
- Access to Brevo dashboard (https://app.brevo.com)
- Webhook endpoint deployed and accessible: `https://reach.aitradepulse.com/api/v1/webhooks/brevo/events`

## Configuration Steps

### 1. Access Brevo Webhook Settings

1. Log in to Brevo dashboard: https://app.brevo.com
2. Navigate to **Settings** → **Webhooks**
3. Click **Add a new webhook**

### 2. Configure Webhook URL

**Webhook URL**: `https://reach.aitradepulse.com/api/v1/webhooks/brevo/events`

**HTTP Method**: POST

### 3. Select Events to Track

Enable the following events:

#### Email Events (Required)
- ✅ **delivered** - Email successfully delivered to recipient's inbox
- ✅ **opened** - Recipient opened the email (tracked via pixel)
- ✅ **click** - Recipient clicked a link in the email
- ✅ **hard_bounce** - Email bounced permanently (invalid address)
- ✅ **soft_bounce** - Email bounced temporarily (mailbox full, etc.)
- ✅ **spam** - Email marked as spam by recipient
- ✅ **blocked** - Email blocked by recipient's server
- ✅ **invalid_email** - Invalid email address format
- ✅ **unsubscribed** - Recipient unsubscribed

#### Optional Events
- ⬜ **request** - Email send request received
- ⬜ **deferred** - Email delivery deferred
- ⬜ **error** - Email sending error

### 4. Configure Webhook Security (Optional but Recommended)

1. Generate a webhook secret key (random string, 32+ characters)
2. Add to Brevo webhook configuration
3. Update 1ai-reach environment variable:
   ```bash
   export SMTP_BREVO_WEBHOOK_SECRET="your-secret-key-here"
   ```
4. Restart FastAPI service:
   ```bash
   systemctl --user restart 1ai-reach-api
   ```

### 5. Test Webhook

1. Click **Test webhook** in Brevo dashboard
2. Check webhook endpoint logs:
   ```bash
   tail -f /home/openclaw/projects/1ai-reach/logs/fastapi.log
   ```
3. Verify test event is received and processed

### 6. Activate Webhook

1. Click **Save** to activate the webhook
2. Brevo will now send real-time events to your endpoint

## Webhook Payload Examples

### Delivered Event
```json
{
  "event": "delivered",
  "email": "recipient@example.com",
  "id": 123456,
  "date": "2026-04-21 07:00:00",
  "ts": 1713682800,
  "message_id": "<abc123@smtp-relay.brevo.com>",
  "ts_event": 1713682800,
  "subject": "Collaboration Proposal from BerkahKarya",
  "tag": "lead:ChIJsdI5wTT2aS4R6iQY_MMuFrs",
  "sending_ip": "1.2.3.4",
  "ts_epoch": 1713682800
}
```

### Opened Event
```json
{
  "event": "opened",
  "email": "recipient@example.com",
  "id": 123456,
  "date": "2026-04-21 07:05:00",
  "ts": 1713683100,
  "message_id": "<abc123@smtp-relay.brevo.com>",
  "ts_event": 1713683100,
  "subject": "Collaboration Proposal from BerkahKarya",
  "tag": "lead:ChIJsdI5wTT2aS4R6iQY_MMuFrs"
}
```

### Click Event
```json
{
  "event": "click",
  "email": "recipient@example.com",
  "id": 123456,
  "date": "2026-04-21 07:06:00",
  "ts": 1713683160,
  "message_id": "<abc123@smtp-relay.brevo.com>",
  "ts_event": 1713683160,
  "subject": "Collaboration Proposal from BerkahKarya",
  "tag": "lead:ChIJsdI5wTT2aS4R6iQY_MMuFrs",
  "link": "https://berkahkarya.org"
}
```

### Hard Bounce Event
```json
{
  "event": "hard_bounce",
  "email": "invalid@example.com",
  "id": 123456,
  "date": "2026-04-21 07:01:00",
  "ts": 1713682860,
  "message_id": "<abc123@smtp-relay.brevo.com>",
  "ts_event": 1713682860,
  "subject": "Collaboration Proposal from BerkahKarya",
  "tag": "lead:ChIJsdI5wTT2aS4R6iQY_MMuFrs",
  "reason": "550 5.1.1 User unknown"
}
```

## What Happens When Events Are Received

### 1. Webhook Receives Event
- FastAPI endpoint `/api/v1/webhooks/brevo/events` receives POST request
- Validates webhook signature (if configured)
- Parses event payload

### 2. Lead Lookup
- Finds lead by email address in database
- If lead not found, event is ignored with status "lead_not_found"

### 3. Event Logging
- Logs event to `event_log` table with full details
- Event type: `email_delivered`, `email_opened`, `email_click`, etc.

### 4. Lead Update
Based on event type:

| Event | Lead Update |
|-------|-------------|
| `delivered` | Set `email_delivered_at` = timestamp |
| `opened` | Set `email_opened_at` = timestamp, increment `email_open_count` |
| `click` | Set `email_clicked_at` = timestamp, increment `email_click_count` |
| `hard_bounce` | Set `status` = "bounced", `email_bounce_reason` = reason |
| `soft_bounce` | Set `status` = "bounced", `email_bounce_reason` = reason |
| `spam` | Set `status` = "unsubscribed", `email_bounce_reason` = "marked_as_spam" |
| `unsubscribed` | Set `status` = "unsubscribed" |

### 5. Response
- Returns JSON: `{"status": "success", "event": "delivered", "email": "..."}`

## Monitoring Webhook Activity

### Check Recent Events
```bash
sqlite3 /home/openclaw/projects/1ai-reach/data/leads.db \
  "SELECT event_type, timestamp, details FROM event_log 
   WHERE event_type LIKE 'email_%' 
   ORDER BY timestamp DESC LIMIT 20;"
```

### Check Email Tracking Stats
```bash
sqlite3 /home/openclaw/projects/1ai-reach/data/leads.db \
  "SELECT 
     COUNT(*) as total_sent,
     COUNT(email_delivered_at) as delivered,
     COUNT(email_opened_at) as opened,
     COUNT(email_clicked_at) as clicked,
     COUNT(CASE WHEN status='bounced' THEN 1 END) as bounced
   FROM leads 
   WHERE contacted_at IS NOT NULL;"
```

### View Lead Email Journey
```bash
sqlite3 /home/openclaw/projects/1ai-reach/data/leads.db \
  "SELECT 
     displayName,
     email,
     contacted_at,
     email_delivered_at,
     email_opened_at,
     email_open_count,
     email_clicked_at,
     email_click_count,
     status
   FROM leads 
   WHERE email = 'recipient@example.com';"
```

## Troubleshooting

### Webhook Not Receiving Events

1. **Check webhook is active in Brevo dashboard**
   - Settings → Webhooks → Verify status is "Active"

2. **Test webhook endpoint manually**
   ```bash
   curl -X POST https://reach.aitradepulse.com/api/v1/webhooks/brevo/events \
     -H "Content-Type: application/json" \
     -d '{"event":"delivered","email":"test@example.com","message_id":"test-123","ts":1713682800}'
   ```

3. **Check FastAPI logs**
   ```bash
   tail -f /tmp/1ai-reach-api.log
   ```

4. **Verify nginx is routing correctly**
   ```bash
   curl -s http://localhost:8000/api/v1/webhooks/brevo/events
   ```

### Signature Validation Failing

1. **Verify secret is configured correctly**
   ```bash
   echo $SMTP_BREVO_WEBHOOK_SECRET
   ```

2. **Check Brevo dashboard secret matches environment variable**

3. **Temporarily disable signature validation for testing**
   - Comment out signature validation in `webhooks.py`
   - Restart FastAPI
   - Test webhook
   - Re-enable validation

### Events Not Updating Leads

1. **Check lead exists with matching email**
   ```bash
   sqlite3 /home/openclaw/projects/1ai-reach/data/leads.db \
     "SELECT id, displayName, email FROM leads WHERE email = 'recipient@example.com';"
   ```

2. **Check event_log for received events**
   ```bash
   sqlite3 /home/openclaw/projects/1ai-reach/data/leads.db \
     "SELECT * FROM event_log WHERE event_type LIKE 'email_%' ORDER BY timestamp DESC LIMIT 10;"
   ```

3. **Check database permissions**
   ```bash
   ls -la /home/openclaw/projects/1ai-reach/data/leads.db
   ```

## Additional Tracking Features

### Tracking Pixel (Automatic)
- Automatically embedded in all HTML emails
- 1x1 transparent GIF: `https://reach.aitradepulse.com/api/v1/webhooks/track/open/{lead_id}/{message_id}`
- Tracks opens even if Brevo webhook fails

### Link Click Tracking (Manual)
To track specific links, wrap them with tracking URL:
```
Original: https://berkahkarya.org
Tracked: https://reach.aitradepulse.com/api/v1/webhooks/track/click/{lead_id}/{message_id}?url=https%3A%2F%2Fberkahkarya.org
```

## Security Considerations

1. **Always use HTTPS** for webhook endpoint
2. **Enable webhook signature validation** in production
3. **Rate limit webhook endpoint** to prevent abuse
4. **Validate email addresses** before processing events
5. **Sanitize event data** before storing in database

## Support

For issues or questions:
- Check logs: `/tmp/1ai-reach-api.log`
- Review event_log table for debugging
- Contact: oyi77.coder@gmail.com
