# 1ai-Engage Phase 2 — Comprehensive 6-Month Roadmap

**Status**: Planning Phase  
**Timeline**: 6+ months (April 2026 - October 2026)  
**Team**: Solo developer  
**Tech Stack**: Python (backend), Next.js (frontend), WAHA (WhatsApp API), Local ML models (STT/TTS)  
**Approach**: Local/Offline processing, incremental feature delivery

---

## Executive Summary

Phase 2 transforms 1ai-reach from a text-only CS automation system into a **multi-modal, intelligent customer engagement platform** with voice capabilities, advanced analytics, and sales optimization features.

**Key Goals**:
- ✅ Add voice note send/receive (STT + TTS)
- ✅ Improve customer experience (quick replies, sentiment detection)
- ✅ Enable data-driven optimization (A/B testing, analytics)
- ✅ Reduce manual work (auto-KB, smart follow-ups)
- ✅ Prepare for multi-channel expansion (Instagram, Telegram)

**Expected Impact**:
- 30-50% increase in customer engagement (voice + quick replies)
- 15-25% improvement in conversion rates (A/B testing + smart timing)
- 40-60% reduction in manual KB maintenance (auto-generation)
- Foundation for 2-3x lead volume (multi-channel ready)

---

## Phase 2 Feature Breakdown

### TIER 1: Must Have (Months 1-2)
These features directly improve customer experience and are prerequisites for later features.

#### 1.1 Voice Note Support (Send + Receive)
**What**: Customers send voice notes → AI transcribes → replies with voice note  
**Why**: 40-60% of Indonesian customers prefer voice over text  
**Effort**: 25-32 days  
**Dependencies**: None (standalone feature)

**Components**:
- `stt_engine.py` — faster-whisper-medium-id (STT)
- `tts_engine.py` — MeloTTS or Coqui XTTS-v2 (TTS)
- `voice_pipeline.py` — orchestration
- `audio_utils.py` — ffmpeg conversion
- `voice_config.py` — model management

**Deliverables**:
- [ ] STT engine with Indonesian language support
- [ ] TTS engine with natural voice output
- [ ] WAHA integration for voice note send/receive
- [ ] Fallback to text if voice processing fails
- [ ] Voice note toggle per WA number (config)

**Acceptance Criteria**:
- Customer sends voice note → AI transcribes within 5 seconds
- AI generates text reply → converts to voice within 3 seconds
- Voice note plays correctly in WhatsApp
- Handles various audio formats (OGG, MP3, WAV)

---

#### 1.2 Quick Reply Buttons
**What**: Customers tap buttons instead of typing ("Track Order", "Speak to Agent", etc.)  
**Why**: 3x faster interaction, better intent capture, higher engagement  
**Effort**: 8-10 days  
**Dependencies**: None (standalone feature)

**Components**:
- Dashboard UI: Quick reply button builder
- `webhook_server.py` — button click handling
- `cs_engine.py` — button-triggered responses
- API endpoints for CRUD operations

**Deliverables**:
- [ ] Dashboard page for quick reply configuration
- [ ] Button template library (pre-built for common intents)
- [ ] Per-WA-number button customization
- [ ] Button click tracking and analytics
- [ ] Dynamic button generation based on conversation stage

**Acceptance Criteria**:
- Admin can create/edit/delete quick reply buttons
- Buttons appear in WhatsApp conversations
- Button clicks are logged and tracked
- Buttons can trigger different responses per product line

---

#### 1.3 Sentiment Detection + Auto-Escalation
**What**: Detect angry/frustrated customers → auto-escalate to human  
**Why**: Prevent churn, improve CSAT, reduce negative reviews  
**Effort**: 5-7 days  
**Dependencies**: None (uses existing KB/LLM)

**Components**:
- `sentiment_engine.py` — IndoBERT-based sentiment analysis
- `webhook_server.py` — escalation trigger
- `state_manager.py` — escalation tracking
- Dashboard: Sentiment trends visualization

**Deliverables**:
- [ ] Real-time sentiment scoring (positive/negative/neutral)
- [ ] Emotion classification (happy, frustrated, confused, angry)
- [ ] Auto-escalation rules (configurable thresholds)
- [ ] Sentiment history per customer
- [ ] Dashboard showing sentiment trends

**Acceptance Criteria**:
- Sentiment score calculated for each message
- Frustrated customers escalated within 1 message
- Escalation reason logged
- Sentiment trends visible in dashboard

---

### TIER 2: Should Have (Months 2-4)
These features enable data-driven optimization and reduce manual work.

#### 2.1 Conversation Analytics Dashboard
**What**: Real-time funnel metrics, response times, bot containment rate  
**Why**: Identify bottlenecks, measure performance, benchmark against industry  
**Effort**: 10-12 days  
**Dependencies**: Sentiment detection (for CSAT proxy)

**Components**:
- Dashboard page: `/analytics`
- API endpoints: `/api/analytics/*`
- Charts: Funnel, time-series, heatmaps
- Filters: Date range, product line, channel

**Deliverables**:
- [ ] Funnel visualization (new → enriched → contacted → replied → meeting)
- [ ] Key metrics: avg response time, bot containment %, escalation rate
- [ ] Time-series charts: daily/weekly trends
- [ ] Filters: date range, product line, WA number
- [ ] Export to CSV/PDF

**Acceptance Criteria**:
- Dashboard loads in <2 seconds
- Metrics update in real-time
- Filters work correctly
- Charts are mobile-responsive

---

#### 2.2 A/B Testing Framework
**What**: Test two response variants, measure conversion impact  
**Why**: Identify best-performing CS tone, optimize conversion by 5-10%  
**Effort**: 12-15 days  
**Dependencies**: Analytics dashboard (for results display)

**Components**:
- `ab_testing.py` — variant assignment and tracking
- `webhook_server.py` — variant routing
- Dashboard: A/B test results page
- API endpoints: `/api/ab-tests/*`

**Deliverables**:
- [ ] Create A/B tests via dashboard
- [ ] Auto-assign variants (50/50 split)
- [ ] Track conversions per variant
- [ ] Statistical significance calculator
- [ ] Results dashboard with confidence intervals

**Acceptance Criteria**:
- Can create A/B test with two response variants
- Variants assigned randomly to customers
- Conversion tracked per variant
- Results show statistical significance
- Can pause/stop tests

---

#### 2.3 Smart Follow-Up Timing
**What**: Analyze customer engagement patterns → send follow-ups at optimal time  
**Why**: 15-25% higher follow-up conversion rate  
**Effort**: 10-12 days  
**Dependencies**: Conversation analytics

**Components**:
- `engagement_analyzer.py` — response time analysis
- `follow_up_scheduler.py` — optimal timing prediction
- `autonomous_loop.py` — integration with existing scheduler

**Deliverables**:
- [ ] Track response time per customer
- [ ] Calculate engagement velocity
- [ ] Predict optimal follow-up window
- [ ] Schedule follow-ups dynamically
- [ ] Track follow-up conversion rates

**Acceptance Criteria**:
- Follow-up timing varies per customer
- Conversion rate improves by 15%+
- Can override timing manually
- Timing logic is explainable

---

#### 2.4 Auto-KB Generation
**What**: Extract FAQ entries from high-volume questions in conversations  
**Why**: KB stays current, reduce manual maintenance, identify knowledge gaps  
**Effort**: 8-10 days  
**Dependencies**: None (uses existing LLM)

**Components**:
- `kb_extractor.py` — question/answer extraction
- `kb_deduplicator.py` — similarity-based deduplication
- Dashboard: KB suggestion review page
- API endpoints: `/api/kb/suggestions/*`

**Deliverables**:
- [ ] Extract Q&A from conversations
- [ ] Deduplicate similar questions
- [ ] Flag for human review
- [ ] One-click publish to KB
- [ ] Track KB entry usage

**Acceptance Criteria**:
- Suggestions appear within 1 hour of conversation
- Deduplication accuracy >90%
- Admin can approve/reject suggestions
- Published entries appear in KB immediately

---

### TIER 3: Could Have (Months 4-6)
These features enable future expansion and advanced capabilities.

#### 3.1 Conversation Summarization
**What**: Auto-generate 2-3 sentence summary of long conversations  
**Why**: Agents see context instantly, reduce handoff friction  
**Effort**: 3-4 days  
**Dependencies**: None (uses existing LLM)

**Components**:
- `conversation_summarizer.py` — Claude API integration
- Dashboard: Summary display in conversation view

**Deliverables**:
- [ ] Summary generated on escalation
- [ ] Summary cached for performance
- [ ] Editable by agent
- [ ] Logged for CRM

---

#### 3.2 Intent Classification (NLP)
**What**: Move from keyword matching to NLP-based intent detection  
**Why**: Catch complaints phrased as questions, better routing  
**Effort**: 8-10 days  
**Dependencies**: None (standalone)

**Components**:
- `intent_classifier.py` — RASA NLU or fine-tuned BERT
- `webhook_server.py` — intent-based routing

**Deliverables**:
- [ ] Intent classification with confidence scores
- [ ] Low-confidence escalation
- [ ] Intent-based KB recommendations
- [ ] Intent trends dashboard

---

#### 3.3 Long-Term Customer Memory
**What**: Store customer preferences, past issues → remember across conversations  
**Why**: Customers don't repeat themselves, faster resolution  
**Effort**: 10-12 days  
**Dependencies**: None (uses vector DB)

**Components**:
- `customer_memory.py` — fact extraction and storage
- Vector DB: Pinecone or Weaviate (or local Chroma)
- `cs_engine.py` — memory retrieval in prompts

**Deliverables**:
- [ ] Extract key facts from conversations
- [ ] Store in vector DB per customer
- [ ] Retrieve on new conversation
- [ ] Add to LLM context
- [ ] Manual memory editing

---

#### 3.4 Multi-Channel Foundation (Instagram + Telegram)
**What**: Extend to Instagram DMs and Telegram Bot  
**Why**: Capture leads where they are, 2-3x more volume  
**Effort**: 20-25 days  
**Dependencies**: All Tier 1 & 2 features (for unified pipeline)

**Components**:
- `instagram_handler.py` — Meta Graph API integration
- `telegram_handler.py` — Telegram Bot API
- Unified message normalization
- Channel-agnostic KB + LLM pipeline

**Deliverables**:
- [ ] Instagram DM integration
- [ ] Telegram Bot integration
- [ ] Unified inbox in dashboard
- [ ] Cross-channel conversation history
- [ ] Per-channel customization

---

## Month-by-Month Timeline

### Month 1 (April 2026): Voice Foundation
**Goal**: Get voice note send/receive working end-to-end

**Week 1-2: STT Engine**
- [ ] Set up faster-whisper-medium-id locally
- [ ] Create `stt_engine.py` with transcription function
- [ ] Test with sample Indonesian audio files
- [ ] Benchmark latency (target: <5s per message)

**Week 3-4: TTS Engine**
- [ ] Set up MeloTTS or Coqui XTTS-v2 locally
- [ ] Create `tts_engine.py` with synthesis function
- [ ] Test voice quality in Indonesian
- [ ] Benchmark latency (target: <3s per message)

**Week 5: Integration**
- [ ] Create `voice_pipeline.py` orchestration
- [ ] Create `audio_utils.py` for format conversion
- [ ] Integrate with `webhook_server.py` for voice note detection
- [ ] Test end-to-end: voice in → transcribe → reply → voice out

**Week 6: Polish & Testing**
- [ ] Error handling and fallbacks
- [ ] Performance optimization
- [ ] Test with real WhatsApp voice notes
- [ ] Documentation

**Deliverable**: Voice note send/receive working in production

---

### Month 2 (May 2026): Quick Replies + Sentiment
**Goal**: Improve customer experience with quick replies and sentiment detection

**Week 1-2: Quick Reply Buttons**
- [ ] Design dashboard UI for button builder
- [ ] Create API endpoints for CRUD
- [ ] Implement button rendering in WhatsApp
- [ ] Test button click tracking

**Week 3: Sentiment Detection**
- [ ] Set up IndoBERT sentiment model
- [ ] Create `sentiment_engine.py`
- [ ] Integrate with `webhook_server.py`
- [ ] Create escalation rules

**Week 4: Dashboard Integration**
- [ ] Add sentiment visualization to dashboard
- [ ] Add quick reply management page
- [ ] Test end-to-end

**Deliverable**: Quick replies + sentiment detection live

---

### Month 3 (June 2026): Analytics Foundation
**Goal**: Build analytics dashboard and A/B testing framework

**Week 1-2: Analytics Dashboard**
- [ ] Design dashboard layout
- [ ] Create API endpoints for metrics
- [ ] Implement funnel chart
- [ ] Add filters and date range

**Week 3-4: A/B Testing**
- [ ] Create `ab_testing.py` framework
- [ ] Implement variant assignment
- [ ] Create results dashboard
- [ ] Statistical significance calculator

**Deliverable**: Analytics dashboard + A/B testing framework

---

### Month 4 (July 2026): Optimization Features
**Goal**: Enable data-driven optimization

**Week 1-2: Smart Follow-Up Timing**
- [ ] Analyze engagement patterns
- [ ] Build timing prediction model
- [ ] Integrate with scheduler
- [ ] Test and validate

**Week 3-4: Auto-KB Generation**
- [ ] Extract Q&A from conversations
- [ ] Deduplication logic
- [ ] Review dashboard
- [ ] One-click publish

**Deliverable**: Smart follow-ups + auto-KB live

---

### Month 5 (August 2026): Advanced Features
**Goal**: Add conversation intelligence

**Week 1-2: Conversation Summarization**
- [ ] Implement summarization
- [ ] Cache for performance
- [ ] Dashboard integration

**Week 3-4: Intent Classification**
- [ ] Set up RASA or fine-tuned BERT
- [ ] Intent-based routing
- [ ] Dashboard visualization

**Deliverable**: Conversation intelligence features

---

### Month 6 (September-October 2026): Multi-Channel Prep
**Goal**: Foundation for multi-channel expansion

**Week 1-2: Long-Term Memory**
- [ ] Fact extraction
- [ ] Vector DB setup
- [ ] Memory retrieval in prompts

**Week 3-4: Multi-Channel Foundation**
- [ ] Instagram integration
- [ ] Telegram integration
- [ ] Unified pipeline
- [ ] Cross-channel dashboard

**Deliverable**: Multi-channel foundation ready

---

## Resource Requirements

### Hardware
- **GPU**: NVIDIA RTX 3060+ (12GB VRAM) for local STT/TTS
  - Alternative: RTX 4060 (8GB) with model quantization
  - Fallback: CPU-only mode (slower, but works)
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
torch>=2.0.0

# Audio
librosa>=0.10.0
soundfile>=0.12.0
pydub>=0.25.1

# Analytics
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0

# Vector DB (optional)
pinecone-client>=3.0.0  # or
chromadb>=0.4.0  # local alternative
```

### Development Time Allocation
- **Implementation**: 60% (120 days)
- **Testing & QA**: 20% (40 days)
- **Documentation**: 10% (20 days)
- **Buffer & Optimization**: 10% (20 days)

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| STT/TTS latency too high | Medium | High | Pre-optimize models, use quantization, GPU acceleration |
| Voice quality issues | Medium | Medium | Test with real customers early, fallback to text |
| Multi-channel complexity | High | High | Build modular pipeline, test each channel separately |
| Model memory constraints | Medium | Medium | Use smaller models, implement model caching |
| Customer adoption of voice | Low | Medium | A/B test voice vs text, gather feedback |

---

## Success Metrics

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

## Rollback Plan

Each feature has a kill switch:
- Voice notes: Toggle `VOICE_ENABLED` in config
- Quick replies: Disable button rendering
- Sentiment: Disable auto-escalation
- Analytics: Read-only mode
- A/B testing: Disable variant assignment

---

## Next Steps

1. **Approve this roadmap** — Confirm priorities and timeline
2. **Set up development environment** — GPU, models, dependencies
3. **Start Month 1** — Voice note implementation
4. **Weekly check-ins** — Track progress, adjust as needed
5. **Monthly reviews** — Assess impact, gather feedback

---

**Document Version**: 1.0  
**Last Updated**: 2026-04-15  
**Status**: Ready for Implementation
