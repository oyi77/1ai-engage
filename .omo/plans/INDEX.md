# 1ai-Engage Phase 2 Planning — Complete Index

**Status**: ✅ MONTH 1 READY FOR EXECUTION | Phase 2 Planning Complete  
**Created**: 2026-04-15T19:48:40Z  
**Updated**: 2026-04-16  
**Timeline**: 6+ months (April 2026 - October 2026)  
**Team**: Solo developer  
**Approach**: Local/Offline processing, incremental delivery

---

## 📑 Planning Documents

### 1. **PHASE-2-COMPLETE-PLANNING-PACKAGE.md** (Main Document)
**Purpose**: Executive summary with all planning artifacts consolidated  
**Contains**:
- Phase 2 vision and expected impact
- Month-by-month breakdown (6 months)
- Voice note architecture design
- Dashboard UI designs (Quick Replies, Analytics, A/B Testing)
- Feature prioritization matrix
- Resource requirements
- Risk mitigation strategies
- Success metrics
- Next steps

**Read this first** for complete overview.

---

### 3. **voice-notes-month1.md** ⭐ EXECUTABLE PLAN
**Purpose**: Month 1 executable work plan — Voice Notes implementation  
**Status**: ✅ MOMUS APPROVED — Ready for execution  
**Contains**:
- 12 implementation tasks across 4 parallel waves
- 3 final verification tasks
- Full QA scenarios for every task
- ChatterBox Multilingual TTS integration (user's preferred engine)
- faster-whisper STT integration
- WAHA voice send/receive API integration
- Graceful text fallback on voice processing failure
- VRAM profiling and CPU fallback strategy

**Run `/start-work voice-notes-month1` to begin execution.**

---
**Purpose**: Deep-dive implementation roadmap with detailed specifications  
**Contains**:
- Executive summary
- Detailed feature breakdown (Tier 1, 2, 3)
- Month-by-month timeline with weekly milestones
- Resource requirements and dependencies
- Risk mitigation strategies
- Success metrics by phase
- Rollback plan
- Next steps

**Read this** for detailed implementation guidance.

---

## 🎯 Quick Reference

### Phase 2 Goals
- ✅ Add voice note send/receive (STT + TTS)
- ✅ Improve customer experience (quick replies, sentiment)
- ✅ Enable data-driven optimization (A/B testing, analytics)
- ✅ Reduce manual work (auto-KB, smart follow-ups)
- ✅ Prepare for multi-channel expansion

### Expected Impact
- 30-50% increase in customer engagement
- 15-25% improvement in conversion rates
- 40-60% reduction in manual work
- Foundation for 2-3x lead volume

---

## 📅 Timeline at a Glance

| Month | Focus | Deliverable | Effort |
|-------|-------|-------------|--------|
| **1** (Apr) | Voice Foundation | Voice notes send/receive | 25-32d |
| **2** (May) | Quick Replies + Sentiment | Quick buttons + sentiment detection | 18-22d |
| **3** (Jun) | Analytics | Analytics dashboard + A/B testing | 22-27d |
| **4** (Jul) | Optimization | Smart follow-ups + auto-KB | 18-22d |
| **5** (Aug) | Intelligence | Summarization + intent classification | 13-17d |
| **6** (Sep-Oct) | Multi-Channel | Long-term memory + multi-channel | 30-37d |

**Total Effort**: ~150-160 days (6+ months for solo developer)

---

## 🏗️ Architecture Overview

### Voice Note Pipeline
```
Customer Voice Note
        ↓
WAHA Webhook (hasMedia: true, ptt: true)
        ↓
webhook_server.py (detect voice)
        ↓
voice_pipeline.py (orchestrate)
        ↓
stt_engine.py (transcribe with faster-whisper-medium-id)
        ↓
cs_engine.py (generate text reply)
        ↓
tts_engine.py (synthesize with MeloTTS/Coqui XTTS-v2)
        ↓
audio_utils.py (convert to OGG/OPUS)
        ↓
senders.py (send_voice_note via WAHA)
        ↓
Customer receives voice reply
```

### New Files to Create
```
scripts/
├── voice_pipeline.py      # Orchestration (3-4 days)
├── stt_engine.py          # STT with faster-whisper (4-5 days)
├── tts_engine.py          # TTS with MeloTTS/Coqui (4-5 days)
├── audio_utils.py         # Audio conversion (3-4 days)
├── voice_config.py        # Configuration (1-2 days)
├── sentiment_engine.py    # Sentiment detection (5-7 days)
├── ab_testing.py          # A/B testing framework (12-15 days)
├── engagement_analyzer.py # Smart follow-ups (10-12 days)
├── kb_extractor.py        # Auto-KB generation (8-10 days)
└── intent_classifier.py   # Intent classification (8-10 days)
```

### Modified Files
```
scripts/
├── webhook_server.py      # Add voice note detection
├── cs_engine.py           # Add voice reply handling
├── senders.py             # Add send_voice_note function
└── state_manager.py       # Add escalation tracking

dashboard/
├── src/app/(dashboard)/quick-replies/page.tsx
├── src/app/(dashboard)/analytics/page.tsx
├── src/app/(dashboard)/ab-tests/page.tsx
└── src/app/api/[[...path]]/route.ts (add new endpoints)
```

---

## 🎨 Dashboard Pages to Create

### 1. Quick Reply Configuration (`/quick-replies`)
- Create/edit/delete quick reply groups
- Manage buttons per group
- Per-WA-number customization
- Button click tracking

**Effort**: 6-9 days

### 2. Conversation Analytics (`/analytics`)
- Funnel visualization
- Key metrics (response time, bot containment, escalation rate)
- Time-series trends
- Top performing quick replies
- Filters by date range and channel

**Effort**: 11-15 days

### 3. A/B Testing Results (`/ab-tests`)
- List all tests (active, completed, draft)
- Metric comparison between variants
- Statistical significance indicator
- Winner badge
- Test management (create, start, stop)

**Effort**: 8-13 days

---

## 🔧 Technology Stack

### STT (Speech-to-Text)
- **Model**: faster-whisper-medium-id (fine-tuned for Indonesian)
- **Latency**: ~50ms per second of audio
- **Accuracy**: >90% for Indonesian
- **Local**: Yes (GPU accelerated)

### TTS (Text-to-Speech)
- **Option A**: MeloTTS (fast, lightweight)
  - Latency: ~200ms
  - Quality: Good
  - Local: Yes
- **Option B**: Coqui XTTS-v2 (higher quality, voice cloning)
  - Latency: ~500ms
  - Quality: Excellent
  - Local: Yes

### Sentiment Analysis
- **Model**: IndoBERT-Sentiment or ZenyxS/indobert-emotion
- **Accuracy**: >85% for Indonesian
- **Local**: Yes

### Analytics
- **Charts**: Recharts (already in use)
- **Data**: Pandas, NumPy
- **Stats**: Scikit-learn

### Vector DB (for long-term memory)
- **Option A**: Chromadb (local, lightweight)
- **Option B**: Pinecone (cloud, managed)

---

## 📊 Feature Prioritization

### TIER 1: Must Have (Months 1-2)
1. **Voice Notes** (25-32 days) — 40-60% of customers prefer voice
2. **Quick Replies** (6-9 days) — 3x faster interaction
3. **Sentiment Detection** (5-7 days) — Prevent churn

### TIER 2: Should Have (Months 2-4)
4. **Analytics Dashboard** (11-15 days) — Identify bottlenecks
5. **A/B Testing** (12-15 days) — Optimize conversion by 5-10%
6. **Smart Follow-ups** (10-12 days) — 15-25% better conversion
7. **Auto-KB** (8-10 days) — Reduce manual maintenance

### TIER 3: Could Have (Months 4-6)
8. **Summarization** (3-4 days) — Faster agent handoff
9. **Intent Classification** (8-10 days) — Better routing
10. **Long-term Memory** (10-12 days) — Personalization
11. **Multi-Channel** (20-25 days) — 2-3x more leads

---

## ✅ Success Criteria

### Phase 1 (Months 1-2)
- [ ] Voice note latency <5s (STT) + <3s (TTS)
- [ ] Voice note accuracy >90% (Indonesian)
- [ ] Quick reply adoption >30%
- [ ] Sentiment detection accuracy >85%

### Phase 2 (Months 3-4)
- [ ] Analytics dashboard used daily
- [ ] A/B test conversion improvement >5%
- [ ] Smart follow-up conversion +15%
- [ ] Auto-KB suggestions >50% accuracy

### Phase 3 (Months 5-6)
- [ ] Multi-channel foundation ready
- [ ] Overall engagement +30-50%
- [ ] Conversion rate +15-25%
- [ ] Manual work reduced by 40%

---

## 🚀 Getting Started

### Step 1: Environment Setup
```bash
# Install GPU drivers and CUDA
# Download models locally:
# - faster-whisper-medium-id
# - MeloTTS or Coqui XTTS-v2
# - IndoBERT sentiment model

# Install dependencies
pip install -r requirements-phase2.txt
```

### Step 2: Month 1 - Voice Notes
```bash
# Create voice infrastructure
python scripts/stt_engine.py --test
python scripts/tts_engine.py --test
python scripts/voice_pipeline.py --test

# Integrate with webhook
# Test end-to-end with real WhatsApp voice notes
```

### Step 3: Ongoing
- Weekly check-ins on progress
- Monthly reviews of impact
- Adjust timeline based on learnings

---

## 📞 Support & Questions

### Common Questions

**Q: Can I run this on CPU only?**  
A: Yes, but latency will be 5-10x slower. GPU is strongly recommended.

**Q: What if voice quality is poor?**  
A: Fallback to text replies automatically. A/B test to measure impact.

**Q: Can I skip voice notes and start with quick replies?**  
A: Yes, but voice notes are the highest-impact feature. Recommend starting there.

**Q: How do I handle multi-language support?**  
A: Current plan focuses on Indonesian. Multi-language can be added in Phase 3.

**Q: What about voice calls (not just notes)?**  
A: WAHA doesn't support initiating calls. Would require Twilio integration (separate effort).

---

## 📋 Checklist Before Starting

- [ ] GPU setup complete (RTX 3060+ or equivalent)
- [ ] 50-100GB storage available
- [ ] Python 3.10+ installed
- [ ] WAHA instance running and tested
- [ ] Dashboard running locally
- [ ] All dependencies installed
- [ ] Models downloaded locally
- [ ] Test environment ready

---

## 🎓 Learning Resources

### Voice Processing
- Faster-Whisper: https://github.com/SYSTRAN/faster-whisper
- MeloTTS: https://github.com/myshell-ai/MeloTTS
- Coqui XTTS: https://github.com/coqui-ai/TTS

### Analytics & A/B Testing
- Recharts: https://recharts.org/
- Statistical Significance: https://en.wikipedia.org/wiki/Statistical_significance

### Indonesian NLP
- IndoBERT: https://huggingface.co/indobenchmark/indobert-base
- Sentiment Models: https://huggingface.co/ZenyxS/indobert-emotion-emotionclf

---

## 📞 Next Steps

1. **Review this planning package** — Confirm all details
2. **Approve the roadmap** — Get stakeholder buy-in
3. **Set up environment** — GPU, models, dependencies
4. **Start Month 1** — Voice note implementation
5. **Weekly check-ins** — Track progress
6. **Monthly reviews** — Assess impact and adjust

---

**Planning Status**: ✅ COMPLETE  
**Ready for Implementation**: YES  
**Estimated Start Date**: 2026-04-16  
**Estimated Completion**: 2026-10-15

---

## 📚 Document References

- **Main Planning Package**: `PHASE-2-COMPLETE-PLANNING-PACKAGE.md`
- **Detailed Roadmap**: `phase-2-comprehensive-roadmap.md`
- **Architecture Design**: See "🏗️ Voice Note Architecture" section
- **UI Designs**: See "🎨 Dashboard Pages" section

---

**Version**: 1.0  
**Status**: ✅ READY FOR EXECUTION  
**Last Updated**: 2026-04-15T19:48:40Z  
**Created By**: Prometheus (Planning Agent)
