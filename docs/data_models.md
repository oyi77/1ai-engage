# Data Models Reference

## Overview

1ai-reach uses **Pydantic models** for all domain entities, providing type safety, validation, and serialization.

## Core Models

### Lead

**Location**: `src/oneai_reach/domain/models/lead.py`

Represents a business lead in the outreach pipeline.

**Fields**:
- `id`: Unique identifier
- `displayName`: Business name
- `email`: Contact email (validated)
- `phone`: Phone number (normalized to +62 format)
- `websiteUri`: Website URL (auto-adds https://)
- `linkedin`: LinkedIn profile URL
- `status`: Current funnel stage (LeadStatus enum)
- `contacted_at`: When first contacted
- `replied_at`: When lead replied
- `research`: Research notes
- `review_score`: Proposal quality score (0-10)

**Status Enum** (13 stages):
- `NEW` → `ENRICHED` → `DRAFT_READY` → `NEEDS_REVISION` → `REVIEWED`
- `CONTACTED` → `FOLLOWED_UP` → `REPLIED` → `MEETING_BOOKED`
- `WON` / `LOST` / `COLD` / `UNSUBSCRIBED`

**Computed Properties**:
- `is_warm`: True if REPLIED or MEETING_BOOKED
- `is_cold`: True if COLD, LOST, or UNSUBSCRIBED
- `days_since_contact`: Days since contacted_at
- `needs_followup`: True if >3 days without reply

**Validation**:
- Email format validated
- Phone normalized: `081234567890` → `+6281234567890`
- URL normalized: `example.com` → `https://example.com`

### Conversation

**Location**: `src/oneai_reach/domain/models/conversation.py`

Represents a WhatsApp conversation with a customer.

**Fields**:
- `id`: Unique identifier
- `wa_number_id`: WhatsApp session ID
- `contact_phone`: Customer phone number
- `contact_name`: Customer name
- `lead_id`: Associated lead (optional)
- `engine_mode`: CS mode (cs/cold/manual)
- `status`: Conversation state (active/resolved/escalated/cold)
- `message_count`: Total messages
- `last_message_at`: Last activity timestamp

**Status Enum**:
- `ACTIVE`: Ongoing conversation
- `RESOLVED`: Successfully resolved
- `ESCALATED`: Needs human intervention
- `COLD`: No response for >48 hours

**Engine Mode Enum**:
- `CS`: Customer service mode
- `COLD`: Cold outreach mode
- `MANUAL`: Manual control (no auto-reply)

**Computed Properties**:
- `is_active`: True if status is ACTIVE
- `is_escalated`: True if status is ESCALATED
- `hours_since_last_message`: Hours since last activity
- `is_stale`: True if >48 hours inactive

### Message

**Location**: `src/oneai_reach/domain/models/message.py`

Represents a single message in a conversation.

**Fields**:
- `id`: Unique identifier
- `conversation_id`: Parent conversation
- `waha_message_id`: WAHA message ID
- `direction`: in/out
- `message_text`: Message content
- `message_type`: text/voice/image/document/etc.
- `timestamp`: When message was sent/received

**Direction Enum**:
- `IN`: Incoming (from customer)
- `OUT`: Outgoing (from system)

**Message Type Enum**:
- `TEXT`, `VOICE`, `IMAGE`, `DOCUMENT`, `VIDEO`, `AUDIO`, `STICKER`, `LOCATION`, `CONTACT`

**Computed Properties**:
- `is_incoming`: True if direction is IN
- `is_outgoing`: True if direction is OUT
- `is_voice`: True if type is VOICE
- `is_media`: True if type is IMAGE/VIDEO/DOCUMENT/AUDIO
- `age_minutes`: Minutes since timestamp

### Proposal

**Location**: `src/oneai_reach/domain/models/proposal.py`

Represents a generated proposal for a lead.

**Fields**:
- `id`: Unique identifier
- `lead_id`: Associated lead
- `content`: Proposal text
- `score`: Quality score (0.0-10.0)
- `reviewed`: Whether reviewed by AI
- `reviewed_at`: Review timestamp
- `review_notes`: Reviewer feedback

**Validation**:
- Score must be 0.0-10.0
- Score rounded to 2 decimals

**Computed Properties**:
- `is_high_quality`: True if score ≥ 7.0
- `is_reviewed`: True if reviewed flag set
- `needs_revision`: True if score < 5.0
- `word_count`: Number of words in content
- `char_count`: Number of characters

### KnowledgeEntry

**Location**: `src/oneai_reach/domain/models/knowledge.py`

Represents a knowledge base entry for customer service.

**Fields**:
- `id`: Unique identifier
- `wa_number_id`: WhatsApp session (scoped KB)
- `category`: Entry type (faq/doc/snippet)
- `question`: Question text (for FAQs)
- `answer`: Answer text
- `content`: Full content
- `tags`: Comma-separated tags
- `priority`: Priority level (0-10)

**Category Enum**:
- `FAQ`: Frequently asked question
- `DOC`: Documentation
- `SNIPPET`: Code/text snippet

**Validation**:
- Priority must be 0-10
- Tags normalized to lowercase

**Computed Properties**:
- `is_faq`: True if category is FAQ
- `is_snippet`: True if category is SNIPPET
- `is_high_priority`: True if priority ≥ 7
- `tag_list`: Tags split into list
- `searchable_text`: Combined question + answer + content

## Model Configuration

All models use:
```python
model_config = {"from_attributes": True}
```

This enables:
- SQLAlchemy ORM compatibility
- sqlite3.Row compatibility
- Dict-to-model conversion

## Validation Examples

### Email Validation
```python
Lead(email="test@example.com")  # ✓ Valid
Lead(email="not-an-email")      # ✗ ValidationError
```

### Phone Normalization
```python
Lead(phone="081234567890")      # → +6281234567890
Lead(phone="+6281234567890")    # → +6281234567890
Lead(phone="6281234567890")     # → +6281234567890
```

### Score Validation
```python
Proposal(score=8.5)   # ✓ Valid
Proposal(score=11.0)  # ✗ ValidationError (max 10)
Proposal(score=-1.0)  # ✗ ValidationError (min 0)
```

## Usage Patterns

### Creating Models
```python
lead = Lead(
    id="lead_123",
    displayName="Test Company",
    email="contact@test.com",
    phone="081234567890",
    status=LeadStatus.NEW
)
```

### Accessing Computed Properties
```python
if lead.is_warm:
    print(f"Lead replied {lead.days_since_reply} days ago")

if lead.needs_followup:
    print("Time to follow up!")
```

### Model Serialization
```python
# To dict
lead_dict = lead.model_dump()

# To JSON
lead_json = lead.model_dump_json()

# From dict
lead = Lead(**lead_dict)
```

## Repository Interfaces

Models are persisted via repository interfaces:

- `LeadRepository`: CRUD operations for leads
- `ConversationRepository`: CRUD operations for conversations
- `KnowledgeRepository`: CRUD operations with full-text search

See `src/oneai_reach/domain/repositories/` for interface definitions.

## Testing

All models have comprehensive unit tests:
- 94 tests in `tests/unit/domain/test_models.py`
- 100% coverage of validation logic
- All computed properties tested
- Edge cases covered

## Migration from Old Format

Old CSV/dict format automatically converts to Pydantic models via `from_attributes=True` configuration.
