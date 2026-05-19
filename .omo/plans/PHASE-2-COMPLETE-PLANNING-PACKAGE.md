# 1ai-Engage Phase 2 — Complete Planning Package

**Document Status**: ✅ COMPLETE & READY FOR IMPLEMENTATION  
**Created**: 2026-04-15  
**Timeline**: 6+ months (April 2026 - October 2026)  
**Team**: Solo developer  
**Approach**: Local/Offline processing, incremental delivery

---

## 📋 Planning Summary

This document consolidates all Phase 2 planning artifacts:
1. ✅ Comprehensive 6-month roadmap
2. ✅ Voice note architecture design (STT/TTS)
3. ✅ Dashboard UI designs (Quick Replies, Analytics, A/B Testing)
4. ✅ Feature prioritization and dependencies
5. ✅ Resource requirements and risk mitigation

---

## 🎯 Phase 2 Vision

Transform 1ai-reach from **text-only CS automation** into a **multi-modal, intelligent customer engagement platform** with:
- 🎙️ Voice note send/receive (STT + TTS)
- 🔘 Quick reply buttons for faster interaction
- 📊 Advanced analytics and A/B testing
- 🧠 Conversation intelligence (sentiment, intent, memory)
- 🌐 Multi-channel foundation (Instagram, Telegram)

**Expected Impact**:
- 30-50% increase in customer engagement
- 15-25% improvement in conversion rates
- 40-60% reduction in manual work
- Foundation for 2-3x lead volume

---

## 📅 Month-by-Month Breakdown

### Month 1 (April 2026): Voice Foundation
**Deliverable**: Voice note send/receive working end-to-end

**Components to Build**:
- `stt_engine.py` — faster-whisper-medium-id (STT)
- `tts_engine.py` — MeloTTS or Coqui XTTS-v2 (TTS)
- `voice_pipeline.py` — orchestration
- `audio_utils.py` — ffmpeg conversion
- `voice_config.py` — model management

**Effort**: 25-32 days

**Key Milestones**:
- Week 1-2: STT engine setup and testing
- Week 3-4: TTS engine setup and testing
- Week 5: Integration with webhook_server.py
- Week 6: Polish, error handling, documentation

---

### Month 2 (May 2026): Quick Replies + Sentiment
**Deliverable**: Quick replies + sentiment detection live

**Components to Build**:
- Quick reply button builder (dashboard UI)
- Sentiment detection engine (IndoBERT)
- Auto-escalation rules
- Sentiment visualization dashboard

**Effort**: 18-22 days

**Key Milestones**:
- Week 1-2: Quick reply buttons implementation
- Week 3: Sentiment detection engine
- Week 4: Dashboard integration and testing

---

### Month 3 (June 2026): Analytics Foundation
**Deliverable**: Analytics dashboard + A/B testing framework

**Components to Build**:
- Conversation analytics dashboard
- Funnel visualization
- A/B testing framework
- Results dashboard

**Effort**: 22-27 days

**Key Milestones**:
- Week 1-2: Analytics dashboard
- Week 3-4: A/B testing framework

---

### Month 4 (July 2026): Optimization Features
**Deliverable**: Smart follow-ups + auto-KB live

**Components to Build**:
- Smart follow-up timing engine
- Auto-KB generation
- Deduplication logic
- KB suggestion review dashboard

**Effort**: 18-22 days

**Key Milestones**:
- Week 1-2: Smart follow-up timing
- Week 3-4: Auto-KB generation

---

### Month 5 (August 2026): Advanced Features
**Deliverable**: Conversation intelligence features

**Components to Build**:
- Conversation summarization
- Intent classification (NLP)
- Intent-based routing
- Intent visualization dashboard

**Effort**: 13-17 days

**Key Milestones**:
- Week 1-2: Conversation summarization
- Week 3-4: Intent classification

---

### Month 6 (September-October 2026): Multi-Channel Prep
**Deliverable**: Multi-channel foundation ready

**Components to Build**:
- Long-term customer memory (vector DB)
- Instagram DM integration
- Telegram Bot integration
- Unified pipeline and dashboard

**Effort**: 30-37 days

**Key Milestones**:
- Week 1-2: Long-term memory system
- Week 3-4: Multi-channel integration

---

## 🏗️ Voice Note Architecture

### Component Diagram
```
[WAHA Webhook] → [webhook_server.py] 
                        ↓
                [voice_pipeline.py] 
                        ↓
    [stt_engine.py] → [cs_engine.py] → [tts_engine.py]
                        ↓
                   [audio_utils.py]
                        ↓
                   [senders.py]
```

### File Structure
```
scripts/
├── voice_pipeline.py      # Glue logic for voice processing
├── stt_engine.py          # Speech-to-text (faster-whisper)
├── tts_engine.py          # Text-to-speech (MeloTTS/Coqui)
├── audio_utils.py         # Audio conversion (ffmpeg)
├── voice_config.py        # Configuration and model paths
├── cs_engine.py           # Updated for voice replies
├── webhook_server.py      # Updated for voice detection
└── senders.py             # Updated with send_voice_note
```

### Key Integration Points

**webhook_server.py** (modifications):
```python
# Detect voice note webhooks
if msg_type in ("audio", "ptt"):
    from voice_pipeline import process_voice_note
    process_voice_note(data)
```

**cs_engine.py** (new function):
```python
def handle_voice_reply(contact_phone, response_text, session_name):
    """Generate voice response for the given text reply."""
    pass
```

**senders.py** (new function):
```python
def send_voice_note(chat_id, audio_file_path, session_name):
    """Send voice note via WAHA API."""
    pass
```

### Implementation Effort by Component

| Component | Complexity | Time |
|-----------|-----------|------|
| voice_config.py | Low | 1-2 days |
| audio_utils.py | Medium | 3-4 days |
| stt_engine.py | High | 4-5 days |
| tts_engine.py | High | 4-5 days |
| voice_pipeline.py | Medium | 3-4 days |
| Integration & Testing | Medium | 5-7 days |
| **Total** | | **25-32 days** |

---

## 🎨 Dashboard UI Designs

### 1. Quick Reply Buttons Configuration

**Page**: `/quick-replies`

**Key Components**:
- QuickReplyGroupList — Container for all groups
- QuickReplyGroupCard — Individual group with buttons
- QuickReplyButtonRow — Individual button with text/response
- QuickReplyGroupForm — Create/edit groups
- QuickReplyButtonForm — Create/edit buttons

**API Endpoints**:
- `GET /api/quick-replies` — Fetch all groups
- `POST /api/quick-replies` — Create group
- `PATCH /api/quick-replies/:id` — Update group
- `DELETE /api/quick-replies/:id` — Delete group
- `POST /api/quick-replies/:groupId/buttons` — Add button
- `PATCH /api/quick-replies/buttons/:id` — Update button
- `DELETE /api/quick-replies/buttons/:id` — Delete button

**Effort**: 6-9 days

---

### 2. Conversation Analytics Dashboard

**Page**: `/analytics`

**Key Components**:
- MetricCard — KPI display (conversations, response rate, etc.)
- FunnelChart — Custom funnel visualization
- TopPerformersTable — Top quick replies
- DateRangeFilter — Time period selection
- ChannelFilter — Channel filtering

**API Endpoints**:
- `GET /api/analytics/overview` — High-level metrics
- `GET /api/analytics/funnel` — Funnel data
- `GET /api/analytics/quick-replies/performance` — Quick reply stats
- `GET /api/analytics/response-times` — Response time stats
- `GET /api/analytics/engagement-patterns` — Engagement heatmap

**Effort**: 11-15 days

---

### 3. A/B Testing Results Display

**Page**: `/ab-tests`

**Key Components**:
- TestList — List of all tests
- TestCard — Individual test results
- MetricComparisonChart — Variant comparison
- StatisticalSignificanceIndicator — Confidence level
- WinnerBadge — Winning variant indicator

**API Endpoints**:
- `GET /api/ab-tests` — List all tests
- `GET /api/ab-tests/:id` — Get test details
- `POST /api/ab-tests` — Create test
- `PATCH /api/ab-tests/:id` — Update test
- `POST /api/ab-tests/:id/start` — Start test
- `POST /api/ab-tests/:id/stop` — Stop test

**Effort**: 8-13 days

---

## 📊 Feature Prioritization Matrix

### TIER 1: Must Have (Months 1-2)
| Feature | Why | Effort | Impact |
|---------|-----|--------|--------|
| Voice Notes | 40-60% prefer voice | 25-32d | High |
| Quick Replies | 3x faster interaction | 6-9d | High |
| Sentiment Detection | Prevent churn | 5-7d | Medium |

### TIER 2: Should Have (Months 2-4)
| Feature | Why | Effort | Impact |
|---------|-----|--------|--------|
| Analytics Dashboard | Identify bottlenecks | 11-15d | High |
| A/B Testing | Optimize conversion | 12-15d | High |
| Smart Follow-ups | 15-25% better conversion | 10-12d | Medium |
| Auto-KB | Reduce manual work | 8-10d | Medium |

### TIER 3: Could Have (Months 4-6)
| Feature | Why | Effort | Impact |
|---------|-----|--------|--------|
| Summarization | Faster handoff | 3-4d | Low |
| Intent Classification | Better routing | 8-10d | Medium |
| Long-term Memory | Personalization | 10-12d | Medium |
| Multi-Channel | 2-3x more leads | 20-25d | High |

---

## 🛠️ Resource Requirements

### Hardware
- **GPU**: NVIDIA RTX 3060+ (12GB VRAM) for local STT/TTS
- **Storage**: 50-100GB for models + audio cache
- **RAM**: 16GB minimum (32GB recommended)

### Software Dependencies
```
# STT
faster-whisper>=0.10.0
torch>=2.0.0
torchaudio>=2.0.0

# TTS
TTS>=0.22.0  # Coqui TTS
melo-tts>=0.1.0  # MeloTTS

# Sentiment
transformers>=4.30.0

# Audio
librosa>=0.10.0
soundfile>=0.12.0
pydub>=0.25.1

# Analytics
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0

# Vector DB (optional)
chromadb>=0.4.0  # Local alternative
```

### Development Time Allocation
- **Implementation**: 60% (120 days)
- **Testing & QA**: 20% (40 days)
- **Documentation**: 10% (20 days)
- **Buffer & Optimization**: 10% (20 days)

---

## ⚠️ Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| STT/TTS latency too high | Medium | High | Pre-optimize models, use quantization, GPU acceleration |
| Voice quality issues | Medium | Medium | Test with real customers early, fallback to text |
| Multi-channel complexity | High | High | Build modular pipeline, test each channel separately |
| Model memory constraints | Medium | Medium | Use smaller models, implement model caching |
| Customer adoption of voice | Low | Medium | A/B test voice vs text, gather feedback |

---

## ✅ Success Metrics

### Month 1-2
- ✅ Voice note latency <5s (STT) + <3s (TTS)
- ✅ Voice note accuracy >90% (Indonesian)
- ✅ Quick reply button adoption >30%
- ✅ Sentiment detection accuracy >85%

### Month 3-4
- ✅ Analytics dashboard used daily
- ✅ A/B test conversion improvement >5%
- ✅ Smart follow-up conversion +15%
- ✅ Auto-KB suggestions >50% accuracy

### Month 5-6
- ✅ Multi-channel foundation ready
- ✅ Overall engagement +30-50%
- ✅ Conversion rate +15-25%
- ✅ Manual work reduced by 40%

---

## 🔄 Rollback Plan

Each feature has a kill switch:
- Voice notes: Toggle `VOICE_ENABLED` in config
- Quick replies: Disable button rendering
- Sentiment: Disable auto-escalation
- Analytics: Read-only mode
- A/B testing: Disable variant assignment

---

## 📝 Next Steps

1. **Approve this roadmap** — Confirm priorities and timeline
2. **Set up development environment** — GPU, models, dependencies
3. **Start Month 1** — Voice note implementation
4. **Weekly check-ins** — Track progress, adjust as needed
5. **Monthly reviews** — Assess impact, gather feedback

---

## 📚 Related Documents

- **Voice Architecture Design**: See section "🏗️ Voice Note Architecture"
- **Dashboard UI Designs**: See section "🎨 Dashboard UI Designs"
- **Feature Details**: See section "📊 Feature Prioritization Matrix"

---

**Document Version**: 1.0  
**Status**: ✅ READY FOR IMPLEMENTATION  
**Last Updated**: 2026-04-15T19:47:35Z
