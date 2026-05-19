# Voice Notes — Month 1 Implementation Plan

## TL;DR

> **Quick Summary**: Add voice note send/receive capability to 1ai-reach WhatsApp CS bot using ChatterBox Multilingual TTS (500M, language_id="ms") and faster-whisper STT (medium). Customers send voice → transcribe → generate response → synthesize voice → send back.
> 
> **Deliverables**:
> - Voice note transcription (STT) working for Indonesian
> - Voice note generation (TTS) with natural-sounding Malay/Indonesian voice
> - End-to-end pipeline: voice in → text → LLM reply → voice out
> - Graceful fallback to text if voice processing fails
> - Configuration for voice features per WA number
> 
> **Estimated Effort**: Medium (8-12 focused tasks)
> **Parallel Execution**: YES — 3 waves
> **Critical Path**: Task 1 → Task 3 → Task 5 → Task 6 → Task 7 → Task 8

---

## Context

### Original Request
User wants voice note support for WhatsApp CS bot. Explicitly chose **ChatterBox TTS** from `resemble-ai/chatterbox` (referenced via `vndee/local-talking-llm`) because it produces natural-sounding voice with emotion control and voice cloning capabilities.

### Interview Summary
**Key Discussions**:
- Voice tech preference: Local/Offline only (no cloud APIs)
- TTS engine: ChatterBox Multilingual (500M params, 23+ languages including Malay "ms")
- STT engine: faster-whisper (medium model, already installed)
- Hardware: NVIDIA GTX 1660 SUPER 6GB VRAM
- Default voice reply mode: auto (text for text, voice for voice)
- User wants natural CS agent voice, not robotic

**Research Findings**:
- ChatterBox Multilingual supports Malay ("ms") — closest to Indonesian, no "id" code
- ChatterBox API: `model.generate(text, audio_prompt_path=ref, language_id="ms")`
- ChatterBox Turbo (350M) is English-only — NOT suitable
- Sample rate output: `model.sr` (S3GEN_SR)
- WAHA sendVoice: POST `/api/sendVoice` with base64-encoded OGG/OPUS audio
- WAHA voice detection: `payload.type == "ptt"` or `"audio"`, `payload._data.message.pttMessage`
- Python 3.14 in venv; torch 2.11.0 + torchaudio 2.11.0 compatible
- VRAM concern: faster-whisper medium (~1.5GB) + ChatterBox 500M (~2GB) = ~3.5GB total (fits in 6GB)

### Metis Review
**Identified Gaps** (addressed):
- VRAM contention: Models fit simultaneously (~3.5GB of 6GB). Add CPU fallback for safety.
- Malay vs Indonesian: Acceptable quality for CS use case. Test in Task 4.
- Voice cloning: Deferred to later (Phase 2). Use default voice for now.
- Gradio bloat: chatterbox-tts depends on gradio — install anyway but don't import.
- Long responses: Use nltk.sent_tokenize for sentence splitting + concatenation with silence gaps.
- Concurrent requests: Models cached in memory, process sequentially with queue.

---

## Work Objectives

### Core Objective
Enable voice note send/receive on 1ai-reach's WhatsApp CS bot with natural-sounding Indonesian responses using local GPU inference.

### Concrete Deliverables
- `scripts/voice_config.py` — Voice configuration constants
- `scripts/audio_utils.py` — Audio format conversion utilities
- `scripts/stt_engine.py` — Speech-to-text engine (faster-whisper)
- `scripts/tts_engine.py` — Text-to-speech engine (ChatterBox Multilingual)
- `scripts/voice_pipeline.py` — Orchestration between STT/LLM/TTS
- Modified `scripts/senders.py` — `send_voice_note()` function
- Modified `webhook_server.py` — Voice note detection and routing
- Modified `scripts/cs_engine.py` — Voice reply mode integration
- Modified `scripts/config.py` — Voice configuration constants

### Definition of Done
- [ ] Customer sends voice note → bot transcribes and understands correctly
- [ ] Bot generates text response → converts to natural voice → sends as voice note
- [ ] Voice notes play correctly in WhatsApp (Android + iOS)
- [ ] If voice processing fails, text response sent as fallback
- [ ] All voice config in config.py (no hardcoded values)
- [ ] Models load successfully on GPU within VRAM budget
- [ ] End-to-end latency < 30 seconds for typical messages

### Must Have
- STT with Indonesian language support (faster-whisper medium)
- TTS with ChatterBox Multilingual (language_id="ms")
- WAHA integration for voice send/receive
- Graceful text fallback on any failure
- Voice feature toggle per WA number (config)
- Model caching (load once, reuse)

### Must NOT Have (Guardrails)
- ❌ No voice cloning in this build (Phase 2)
- ❌ No emotion/exaggeration tuning UI (use defaults: exaggeration=0.5, cfg_weight=0.5)
- ❌ No streaming TTS (generate full, then send)
- ❌ No audio transcription logging to DB (privacy)
- ❌ No cloud API calls (local GPU only)
- ❌ No Flosia/laundry content in generic voice engine
- ❌ No gradio UI (just API usage)
- ❌ Never crash the webhook — always return 200 OK

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: NO (no test framework configured)
- **Automated tests**: None (use agent-executed QA scenarios)
- **Framework**: N/A
- **Agent-Executed QA**: ALWAYS (mandatory for all tasks)

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Audio processing**: Use Bash (python script) — generate test audio, verify format conversion
- **STT/TTS**: Use Bash (python script) — run inference, verify output quality
- **API integration**: Use Bash (curl) — test WAHA endpoints
- **End-to-end**: Use Bash (python script) — simulate full voice pipeline

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — foundation):
├── Task 1: Install dependencies (torch, chatterbox-tts, nltk) [quick]
├── Task 2: Create voice_config.py [quick]
├── Task 3: Create audio_utils.py [quick]
└── Task 4: Validate ChatterBox + VRAM profiling [deep]

Wave 2 (After Wave 1 — core engines):
├── Task 5: Create stt_engine.py (depends: 2, 3) [unspecified-high]
├── Task 6: Create tts_engine.py (depends: 2, 3, 4) [deep]
└── Task 7: Create voice_pipeline.py (depends: 5, 6) [unspecified-high]

Wave 3 (After Wave 2 — integration):
├── Task 8: Add send_voice_note to senders.py (depends: 2, 3) [quick]
├── Task 9: Update webhook_server.py for voice detection (depends: 5, 7) [unspecified-high]
├── Task 10: Update cs_engine.py for voice reply mode (depends: 6, 7, 8) [unspecified-high]

Wave 4 (After Wave 3 — testing + deployment):
├── Task 11: End-to-end integration test (depends: 9, 10) [deep]
└── Task 12: Deploy + restart services (depends: 11) [quick]

Wave FINAL (After ALL tasks — independent review):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
└── Task F3: Real manual QA (unspecified-high)

Critical Path: Task 1 → Task 4 → Task 6 → Task 7 → Task 10 → Task 11 → Task 12
Parallel Speedup: ~40% faster than sequential
Max Concurrent: 4 (Wave 1)
```

### Dependency Matrix

| Task | Depends On | Blocks | Wave |
|------|-----------|--------|------|
| 1 | — | 4, 5, 6 | 1 |
| 2 | — | 3, 5, 6, 8 | 1 |
| 3 | 2 | 5, 6, 8 | 1 |
| 4 | 1 | 6 | 1 |
| 5 | 2, 3 | 7, 9 | 2 |
| 6 | 2, 3, 4 | 7, 10 | 2 |
| 7 | 5, 6 | 9, 10 | 2 |
| 8 | 2, 3 | 10 | 3 |
| 9 | 5, 7 | 11 | 3 |
| 10 | 6, 7, 8 | 11 | 3 |
| 11 | 9, 10 | 12 | 4 |
| 12 | 11 | — | 4 |

### Agent Dispatch Summary

- **Wave 1**: **4** — T1 `quick`, T2 `quick`, T3 `quick`, T4 `deep`
- **Wave 2**: **3** — T5 `unspecified-high`, T6 `deep`, T7 `unspecified-high`
- **Wave 3**: **3** — T8 `quick`, T9 `unspecified-high`, T10 `unspecified-high`
- **Wave 4**: **2** — T11 `deep`, T12 `quick`
- **FINAL**: **3** — F1 `oracle`, F2 `unspecified-high`, F3 `unspecified-high`

---

## TODOs

- [ ] 1. Install voice pipeline dependencies

  **What to do**:
  - Activate `.venv` and install: `pip install chatterbox-tts nltk`
  - This pulls in torch 2.11.0, torchaudio 2.11.0, transformers, diffusers, librosa, conformer, safetensors, etc.
  - After install, download nltk sentence tokenizer: `python3 -c "import nltk; nltk.download('punkt_tab')"`
  - Verify torch sees GPU: `python3 -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"`
  - Verify chatterbox imports: `python3 -c "from chatterbox.tts import ChatterboxTTS; print('OK')"`
  - Record exact package versions installed

  **Must NOT do**:
  - Do NOT install system-wide (install into .venv only)
  - Do NOT install gradio extras
  - Do NOT modify any existing source files

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Single command installation + verification
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `playwright`: Not a browser task

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 2, 3 — they're just file creation)
  - **Parallel Group**: Wave 1 (with Tasks 2, 3, 4)
  - **Blocks**: Tasks 4, 5, 6
  - **Blocked By**: None (can start immediately)

  **References**:
  **External References**:
  - ChatterBox pyproject.toml: `https://github.com/resemble-ai/chatterbox/blob/master/pyproject.toml` — Dependencies list, confirms torch>=2.9.0 for Python 3.14
  - ChatterBox example: `https://github.com/resemble-ai/chatterbox/blob/master/example_tts.py` — API usage pattern

  **WHY Each Reference Matters**:
  - pyproject.toml shows exact dependency versions to expect; confirms Python 3.14 compatibility with torch>=2.9.0

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Dependencies installed correctly
    Tool: Bash (python)
    Preconditions: .venv activated
    Steps:
      1. Run: `. .venv/bin/activate && python3 -c "import torch; print(f'torch {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}')"`
      2. Assert output contains "torch 2.1" and "CUDA: True"
      3. Run: `. .venv/bin/activate && python3 -c "from chatterbox.tts import ChatterboxTTS; print('chatterbox OK')"`
      4. Assert output contains "chatterbox OK"
      5. Run: `. .venv/bin/activate && python3 -c "import nltk; print('nltk OK')"`
      6. Assert output contains "nltk OK"
    Expected Result: All imports succeed, CUDA available
    Failure Indicators: ImportError, ModuleNotFoundError, CUDA: False
    Evidence: .sisyphus/evidence/task-1-deps-installed.txt

  Scenario: NLTK punkt tokenizer downloaded
    Tool: Bash (python)
    Preconditions: nltk installed
    Steps:
      1. Run: `. .venv/bin/activate && python3 -c "import nltk; print(nltk.sent_tokenize('Halo. Apa kabar?'))"`
      2. Assert output is a list with 2 sentences: ['Halo.', 'Apa kabar?']
    Expected Result: Sentence tokenization works for Indonesian text
    Failure Indicators: LookupError, empty list
    Evidence: .sisyphus/evidence/task-1-nltk-punkt.txt
  ```

  **Commit**: YES
  - Message: `feat(deps): install voice pipeline dependencies (torch, chatterbox-tts, nltk)`
  - Files: `.venv/` (no source changes to commit)
  - Pre-commit: `python3 -c "import torch; from chatterbox.tts import ChatterboxTTS; import nltk"`

- [ ] 2. Create voice_config.py

  **What to do**:
  - Create `scripts/voice_config.py` with all voice-related configuration constants
  - Import base config values from `config.py`
  - Define: VOICE_ENABLED, VOICE_STT_MODEL_SIZE, VOICE_STT_DEVICE, VOICE_STT_LANGUAGE, VOICE_TTS_ENGINE, VOICE_TTS_LANGUAGE_ID, VOICE_TTS_EXAGGERATION, VOICE_TTS_CFG_WEIGHT, VOICE_TTS_DEVICE, VOICE_MAX_AUDIO_DURATION, VOICE_MAX_RESPONSE_LENGTH, VOICE_TIMEOUT_SECONDS, VOICE_REPLY_MODE, VOICE_FORMAT, VOICE_CODEC, VOICE_BITRATE, VOICE_SAMPLE_RATE
  - Define WAHA voice endpoints: WAHA_SEND_VOICE_ENDPOINT, WAHA_MEDIA_DOWNLOAD_BASE
  - Add per-session voice config lookup helper: `get_voice_config(session_name) -> dict`

  **Must NOT do**:
  - Do NOT hardcode API keys or URLs (import from config.py)
  - Do NOT add Flosia/laundry specific configuration
  - Do NOT import torch or heavy ML libraries at module level

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Single file creation with constants
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `playwright`: Not a browser task

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 1, 3)
  - **Parallel Group**: Wave 1 (with Tasks 1, 3, 4)
  - **Blocks**: Tasks 3, 5, 6, 8
  - **Blocked By**: None (can start immediately)

  **References**:
  **Pattern References**:
  - `scripts/config.py:1-50` — How constants are organized: `WAHA_URL`, `WAHA_API_KEY`, `WAHA_SESSION` patterns. All paths use `Path` objects via `_ROOT`. Config values imported, never hardcoded.
  - `scripts/config.py:WAHA_URL, WAHA_API_KEY, WAHA_DIRECT_URL, WAHA_DIRECT_API_KEY` — WAHA connection details to import

  **WHY Each Reference Matters**:
  - config.py shows the pattern: all constants at module level, imports from env vars, Path objects for paths. voice_config.py must follow this exact pattern.

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: voice_config imports cleanly
    Tool: Bash (python)
    Preconditions: .venv activated, scripts/ in sys.path
    Steps:
      1. Run: `. .venv/bin/activate && cd /home/openclaw/.openclaw/workspace/1ai-reach && PYTHONPATH=scripts python3 -c "from voice_config import VOICE_ENABLED, VOICE_TTS_LANGUAGE_ID, VOICE_REPLY_MODE; print(f'enabled={VOICE_ENABLED}, lang={VOICE_TTS_LANGUAGE_ID}, mode={VOICE_REPLY_MODE}')"`
      2. Assert output contains "enabled=True", "lang=ms", "mode=auto"
    Expected Result: All config constants import and have expected default values
    Failure Indicators: ImportError, NameError, wrong values
    Evidence: .sisyphus/evidence/task-2-voice-config.txt

  Scenario: No heavy ML imports at module level
    Tool: Bash (python)
    Preconditions: voice_config.py exists
    Steps:
      1. Run: `grep -n "import torch\|import torchaudio\|from chatterbox" scripts/voice_config.py`
      2. Assert exit code 1 (no matches found)
    Expected Result: No ML library imports — config is lightweight
    Failure Indicators: Matches found (would slow down webhook server import)
    Evidence: .sisyphus/evidence/task-2-no-ml-imports.txt
  ```

  **Commit**: YES (groups with Task 3)
  - Message: `feat(voice): add voice config and audio utilities`
  - Files: `scripts/voice_config.py`

- [ ] 3. Create audio_utils.py

  **What to do**:
  - Create `scripts/audio_utils.py` with audio format conversion utilities
  - Function `download_media(url: str, timeout: int = 30) -> bytes` — Download audio from WAHA media URL with API key auth
  - Function `convert_to_wav(input_bytes: bytes, input_format: str = "ogg") -> tuple[int, bytes]` — Convert any audio to WAV (for STT input). Returns (sample_rate, wav_bytes). Uses ffmpeg subprocess.
  - Function `convert_to_ogg(wav_bytes: bytes, sample_rate: int = 24000, bitrate: str = "32k") -> bytes` — Convert WAV to OGG/OPUS (for WhatsApp). Uses ffmpeg subprocess.
  - Function `wav_to_base64(wav_bytes: bytes) -> str` — Base64 encode for WAHA API
  - Function `ogg_to_base64(ogg_bytes: bytes) -> str` — Base64 encode for WAHA API
  - Function `get_audio_duration(audio_bytes: bytes, format: str = "ogg") -> float` — Get duration in seconds using ffprobe
  - Function `concatenate_wav_chunks(chunks: list[tuple[int, bytes]], silence_ms: int = 250) -> tuple[int, bytes]` — Concatenate WAV audio pieces with silence gaps (for long-form TTS)
  - All functions use ffmpeg subprocess (already installed v8.0.1)
  - Import WAHA credentials from config.py for authenticated media download

  **Must NOT do**:
  - Do NOT import pydub (use ffmpeg subprocess directly — lighter)
  - Do NOT import torch or ML libraries
  - Do NOT hardcode ffmpeg path

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Utility file creation with ffmpeg wrappers
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `playwright`: Not a browser task

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 1, 2 — but needs voice_config constants for WAHA_URL)
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 4) — Task 3 technically depends on Task 2 for config import, but can be written independently
  - **Blocks**: Tasks 5, 6, 8
  - **Blocked By**: Task 2 (for voice_config constants)

  **References**:
  **Pattern References**:
  - `scripts/senders.py:283-307` — `send_typing_indicator()` pattern for WAHA API calls with auth headers. Shows how to construct WAHA requests with `X-Api-Key` header.
  - `scripts/config.py:WAHA_URL, WAHA_API_KEY, WAHA_DIRECT_URL, WAHA_DIRECT_API_KEY` — WAHA connection for media downloads

  **API/Type References**:
  - WAHA media download: `GET {WAHA_URL}/api/files/{filename}` with `X-Api-Key` header — from webhook payload `payload.media.url`
  - ffmpeg subprocess pattern: `subprocess.run(["ffmpeg", "-i", "pipe:0", "-f", "wav", "pipe:1"], input=bytes, capture_output=True)`

  **External References**:
  - ffmpeg OGG/OPUS encoding: `ffmpeg -i input.wav -c:a libopus -b:a 32k -ar 48000 output.ogg`
  - ffmpeg WAV output: `ffmpeg -i input.ogg -f wav -ar 16000 -ac 1 output.wav`

  **WHY Each Reference Matters**:
  - senders.py shows the exact WAHA auth pattern — audio_utils must use same header format for media downloads
  - ffmpeg commands are the exact incantations needed for WhatsApp-compatible audio

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Audio conversion OGG → WAV → OGG roundtrip
    Tool: Bash (python)
    Preconditions: ffmpeg installed, audio_utils.py exists
    Steps:
      1. Create a test WAV sine wave: `python3 -c "import struct, wave; w=wave.open('/tmp/test.wav','w'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000); w.writeframes(struct.pack('<'+str(16000)+'h',*[int(32767*__import__('math').sin(2*3.14159*440*i/16000)) for i in range(16000)])); w.close()"`
      2. Run: `PYTHONPATH=scripts python3 -c "from audio_utils import convert_to_ogg, convert_to_wav; import wave; wav=open('/tmp/test.wav','rb').read(); ogg=convert_to_ogg(wav,16000); sr,wav2=convert_to_wav(ogg); print(f'OGG size={len(ogg)}, WAV sr={sr}, size={len(wav2)}')"`
      3. Assert OGG size > 0 and WAV sample_rate > 0
    Expected Result: Audio converts both ways without errors
    Failure Indicators: ffmpeg errors, zero-length output, subprocess errors
    Evidence: .sisyphus/evidence/task-3-audio-conversion.txt

  Scenario: Base64 encoding works
    Tool: Bash (python)
    Preconditions: audio_utils.py exists
    Steps:
      1. Run: `PYTHONPATH=scripts python3 -c "from audio_utils import ogg_to_base64; b=ogg_to_base64(b'test_audio_data'); print(type(b).__name__, len(b))"`
      2. Assert output is "str" and length > 0
    Expected Result: Returns base64 string
    Failure Indicators: TypeError, AttributeError
    Evidence: .sisyphus/evidence/task-3-base64.txt

  Scenario: Duration detection works
    Tool: Bash (python)
    Preconditions: ffmpeg installed, test WAV exists
    Steps:
      1. Run: `PYTHONPATH=scripts python3 -c "from audio_utils import get_audio_duration; import wave; data=open('/tmp/test.wav','rb').read(); dur=get_audio_duration(data,'wav'); print(f'duration={dur:.2f}s')"`
      2. Assert duration is approximately 1.0 seconds (±0.1)
    Expected Result: Duration detected correctly
    Failure Indicators: ffprobe error, wrong duration
    Evidence: .sisyphus/evidence/task-3-duration.txt
  ```

  **Commit**: YES (groups with Task 2)
  - Message: `feat(voice): add voice config and audio utilities`
  - Files: `scripts/audio_utils.py`

- [ ] 4. Validate ChatterBox + VRAM profiling

  **What to do**:
  - Create a test script `scripts/test_voice_models.py` that:
    1. Loads ChatterBox Multilingual model on GPU: `ChatterboxMultilingualTTS.from_pretrained(device="cuda")`
    2. Generates sample Indonesian text with `language_id="ms"`: "Halo Kak, terima kasih sudah menghubungi kami. Ada yang bisa saya bantu hari ini?"
    3. Saves output to `/tmp/chatterbox_test.wav`
    4. Records VRAM usage before and after model load
    5. Then loads faster-whisper medium model on same GPU
    6. Transcribes the generated WAV file
    7. Records total VRAM usage with both models loaded
    8. Tests CPU fallback: `ChatterboxMultilingualTTS.from_pretrained(device="cpu")` — verify it works but note timing
  - Print clear report: model sizes, VRAM usage, inference time, transcription quality
  - If VRAM > 5GB with both models: recommend using CPU for one of them

  **Must NOT do**:
  - Do NOT modify any production files
  - Do NOT leave models loaded (release after test)

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Requires GPU profiling, model validation, and analysis
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `playwright`: Not a browser task

  **Parallelization**:
  - **Can Run In Parallel**: NO (needs Task 1 complete — torch + chatterbox installed)
  - **Parallel Group**: Wave 1 (after Task 1)
  - **Blocks**: Task 6
  - **Blocked By**: Task 1

  **References**:
  **External References**:
  - ChatterBox Multilingual API: `https://github.com/resemble-ai/chatterbox/blob/master/example_tts.py` — Shows `ChatterboxMultilingualTTS.from_pretrained(device=device)` and `model.generate(text, language_id="fr")` pattern
  - faster-whisper API: `https://github.com/SYSTRAN/faster-whisper` — Shows `WhisperModel("medium", device="cuda")` and `model.transcribe(audio, language="id")` pattern

  **WHY Each Reference Matters**:
  - These are the exact API patterns to use. ChatterBox Multilingual uses `language_id` param, NOT `exaggeration` (that's the English-only model).

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: ChatterBox Multilingual generates Indonesian audio
    Tool: Bash (python)
    Preconditions: torch + chatterbox-tts installed, GPU available
    Steps:
      1. Run: `. .venv/bin/activate && PYTHONPATH=scripts python3 scripts/test_voice_models.py`
      2. Check output for "TTS inference time" line — assert < 30 seconds
      3. Check output for "VRAM" line — assert < 5.5 GB
      4. Check `/tmp/chatterbox_test.wav` exists and size > 10000 bytes
      5. Run: `ffprobe /tmp/chatterbox_test.wav 2>&1 | grep Duration` — assert duration > 1s
    Expected Result: Audio generated, plays correctly, VRAM within budget
    Failure Indicators: OOM error, CUDA error, empty file, ImportError
    Evidence: .sisyphus/evidence/task-4-chatterbox-validation.txt

  Scenario: faster-whisper transcribes generated audio
    Tool: Bash (python)
    Preconditions: test_voice_models.py ran successfully
    Steps:
      1. Check test output for "STT transcription" line
      2. Assert transcription contains at least some recognizable Indonesian words (e.g., "halo", "terima", "bantu")
    Expected Result: Transcription matches original text reasonably (>50% word overlap)
    Failure Indicators: Empty transcription, wrong language, garbled text
    Evidence: .sisyphus/evidence/task-4-stt-validation.txt

  Scenario: Both models fit in VRAM simultaneously
    Tool: Bash (python)
    Preconditions: Both models loaded in test
    Steps:
      1. Check test output for "Total VRAM" line
      2. Assert value < 5.5 GB (leaving 0.5GB headroom on 6GB card)
    Expected Result: Both models coexist in VRAM without OOM
    Failure Indicators: > 5.5GB, CUDA OOM, model load failure
    Evidence: .sisyphus/evidence/task-4-vram-profile.txt
  ```

  **Commit**: YES
  - Message: `test(voice): validate ChatterBox multilingual + VRAM profiling`
  - Files: `scripts/test_voice_models.py`

- [ ] 5. Create stt_engine.py

  **What to do**:
  - Create `scripts/stt_engine.py` with Speech-to-Text engine class
  - Class `STTEngine`:
    - `__init__(model_size="medium", device="cuda", language="id")` — Load faster-whisper model
    - `transcribe(audio_bytes: bytes, audio_format: str = "wav") -> dict` — Transcribe audio to text
      - Converts audio to WAV if needed (using audio_utils)
      - Runs faster-whisper inference
      - Returns: `{"text": str, "language": str, "confidence": float, "duration": float}`
    - `transcribe_file(file_path: str) -> dict` — Convenience wrapper for file input
    - `_warm_up()` — Run dummy inference on first load to cache model
  - Singleton pattern: module-level `_instance = None` with `get_stt_engine()` factory
  - Lazy model loading: don't load model until first call
  - Handle errors gracefully: return `{"text": "", "error": "..."}` on failure
  - Import from audio_utils for format conversion

  **Must NOT do**:
  - Do NOT load model at import time (lazy load on first use)
  - Do NOT log transcribed text to database
  - Do NOT crash on invalid audio — return empty text with error

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Requires careful ML integration, error handling, and singleton pattern
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 6 after both depend on Wave 1)
  - **Parallel Group**: Wave 2 (with Task 6)
  - **Blocks**: Tasks 7, 9
  - **Blocked By**: Tasks 2, 3

  **References**:
  **Pattern References**:
  - `scripts/cs_engine.py:1-60` — Import pattern, module-level initialization, lazy imports from same directory
  - `scripts/conversation_tracker.py` — Singleton-like patterns, module-level state

  **API/Type References**:
  - faster-whisper API: `WhisperModel(size, device="cuda", compute_type="int8_float16")` for GPU, `transcribe(audio_path, language="id", beam_size=5)` returns `(segments, info)`

  **External References**:
  - faster-whisper docs: `https://github.com/SYSTRAN/faster-whisper` — Model sizes: tiny, base, small, medium, large-v3. Medium is best balance for Indonesian.

  **WHY Each Reference Matters**:
  - cs_engine.py shows the lazy import pattern used throughout the codebase — follow same style
  - faster-whisper API needs specific compute_type for GPU efficiency

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: STT engine transcribes WAV file
    Tool: Bash (python)
    Preconditions: faster-whisper installed, test WAV exists from Task 4
    Steps:
      1. Run: `. .venv/bin/activate && PYTHONPATH=scripts python3 -c "
from stt_engine import get_stt_engine
engine = get_stt_engine()
with open('/tmp/chatterbox_test.wav', 'rb') as f:
    result = engine.transcribe(f.read(), 'wav')
print(f'text={result.get(\"text\",\"\")[:100]}')
print(f'language={result.get(\"language\",\"\")}')
print(f'duration={result.get(\"duration\",0):.2f}')
"`
      2. Assert text is non-empty
      3. Assert language is "id" or "ms" or "en"
      4. Assert duration > 0
    Expected Result: Transcription returns non-empty text with metadata
    Failure Indicators: Empty text, exception, model load failure
    Evidence: .sisyphus/evidence/task-5-stt-engine.txt

  Scenario: STT handles invalid audio gracefully
    Tool: Bash (python)
    Preconditions: stt_engine.py exists
    Steps:
      1. Run: `. .venv/bin/activate && PYTHONPATH=scripts python3 -c "
from stt_engine import get_stt_engine
engine = get_stt_engine()
result = engine.transcribe(b'not_audio_data', 'wav')
print(f'text={result.get(\"text\",\"\")}')
print(f'error={result.get(\"error\",\"\")}')
"`
      2. Assert text is empty or error is non-empty
      3. Assert NO exception raised (graceful handling)
    Expected Result: Returns dict with error message, no crash
    Failure Indicators: Uncaught exception, crash
    Evidence: .sisyphus/evidence/task-5-stt-error.txt
  ```

  **Commit**: YES
  - Message: `feat(voice): add STT engine with faster-whisper`
  - Files: `scripts/stt_engine.py`

- [ ] 6. Create tts_engine.py

  **What to do**:
  - Create `scripts/tts_engine.py` with Text-to-Speech engine class
  - Class `TTSEngine`:
    - `__init__(device="cuda", language_id="ms")` — Load ChatterBox Multilingual model
    - `synthesize(text: str, audio_prompt_path: str = None, exaggeration: float = 0.5, cfg_weight: float = 0.5) -> tuple[int, bytes]` — Generate audio from text
      - Uses `ChatterboxMultilingualTTS.from_pretrained(device=device)`
      - Calls `model.generate(text, language_id=self.language_id, audio_prompt_path=audio_prompt_path)`
      - Returns (sample_rate, wav_bytes)
    - `synthesize_long_form(text: str, ...) -> tuple[int, bytes]` — Split long text into sentences (nltk.sent_tokenize), synthesize each, concatenate with 250ms silence gaps
    - `_split_into_sentences(text: str) -> list[str]` — Use nltk.sent_tokenize, fall back to simple regex if nltk fails
    - `_concatenate_wav(chunks: list[tuple[int, bytes]]) -> tuple[int, bytes]` — Use audio_utils.concatenate_wav_chunks
  - Singleton pattern: module-level `_instance = None` with `get_tts_engine()` factory
  - Lazy model loading: don't load model until first synthesize call
  - CPU fallback: if CUDA OOM, retry with device="cpu"
  - Import from audio_utils for concatenation

  **Must NOT do**:
  - Do NOT load model at import time
  - Do NOT use ChatterBox English-only model (use Multilingual)
  - Do NOT hardcode device to "cuda" (allow CPU fallback)
  - Do NOT use language_id="id" (not supported, use "ms")

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Complex ML integration with fallback logic, singleton pattern, long-form synthesis
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 5)
  - **Parallel Group**: Wave 2 (with Task 5)
  - **Blocks**: Tasks 7, 10
  - **Blocked By**: Tasks 2, 3, 4 (needs VRAM profiling results)

  **References**:
  **Pattern References**:
  - `scripts/stt_engine.py` — (created in Task 5) Same singleton pattern, lazy loading, error handling

  **API/Type References**:
  - ChatterBox Multilingual API from `example_tts.py`:
    ```python
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    model = ChatterboxMultilingualTTS.from_pretrained(device="cuda")
    wav = model.generate(text, language_id="ms")
    # wav is torch tensor, model.sr is sample rate
    ```
  - From `src/chatterbox/tts.py:generate()` — Returns torch tensor (1, samples), needs `.squeeze().cpu().numpy()` conversion to get raw audio bytes
  - From `vndee/local-talking-llm` reference — Long form: `nltk.sent_tokenize()` + concatenate with silence

  **External References**:
  - ChatterBox repo: `https://github.com/resemble-ai/chatterbox` — Multilingual model usage, supported languages list (includes "ms" Malay)
  - ChatterBox Multilingual tips: Default settings (exaggeration=0.5, cfg_weight=0.5) work well. Lower cfg_weight for fast speakers.

  **WHY Each Reference Matters**:
  - ChatterBox Multilingual is different from English-only model — uses `ChatterboxMultilingualTTS` class and `language_id` parameter
  - Long-form synthesis pattern from vndee reference is essential for CS responses (typically 2-4 sentences)

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: TTS generates Indonesian audio
    Tool: Bash (python)
    Preconditions: chatterbox-tts installed, torch+CUDA working
    Steps:
      1. Run: `. .venv/bin/activate && PYTHONPATH=scripts python3 -c "
from tts_engine import get_tts_engine
engine = get_tts_engine()
sr, wav = engine.synthesize('Halo Kak, terima kasih sudah menghubungi kami.')
import wave
w = wave.open('/tmp/tts_test.wav', 'w')
w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
w.writeframes(wav); w.close()
print(f'sr={sr}, size={len(wav)}, duration={len(wav)/sr:.2f}s')
"
      2. Assert sr > 0 and len(wav) > 0
      3. Assert duration > 1 second
      4. Verify `/tmp/tts_test.wav` plays: `ffprobe /tmp/tts_test.wav 2>&1 | grep Duration`
    Expected Result: Audio file generated with correct sample rate, plays correctly
    Failure Indicators: OOM, ImportError, zero-length output
    Evidence: .sisyphus/evidence/task-6-tts-engine.txt

  Scenario: Long-form synthesis works for multi-sentence text
    Tool: Bash (python)
    Preconditions: TTS engine working
    Steps:
      1. Run: `. .venv/bin/activate && PYTHONPATH=scripts python3 -c "
from tts_engine import get_tts_engine
engine = get_tts_engine()
sr, wav = engine.synthesize_long_form('Halo Kak. Terima kasih sudah menghubungi kami. Ada yang bisa saya bantu hari ini?')
print(f'sr={sr}, duration={len(wav)/sr:.2f}s')
"
      2. Assert duration > 3 seconds (3 sentences should take ~3-6 seconds)
      3. Assert no errors
    Expected Result: Longer audio generated from multiple sentences
    Failure Indicators: Error, duration too short (sentences not concatenated)
    Evidence: .sisyphus/evidence/task-6-tts-longform.txt

  Scenario: CPU fallback works
    Tool: Bash (python)
    Preconditions: TTS engine working
    Steps:
      1. Run: `. .venv/bin/activate && PYTHONPATH=scripts python3 -c "
from tts_engine import TTSEngine
engine = TTSEngine(device='cpu', language_id='ms')
sr, wav = engine.synthesize('Test CPU fallback.')
print(f'cpu_sr={sr}, size={len(wav)}')
"
      2. Assert output is non-empty (CPU mode works, even if slower)
    Expected Result: Audio generated on CPU (slower but functional)
    Failure Indicators: Error, empty output
    Evidence: .sisyphus/evidence/task-6-tts-cpu.txt
  ```

  **Commit**: YES
  - Message: `feat(voice): add TTS engine with ChatterBox multilingual`
  - Files: `scripts/tts_engine.py`

- [ ] 7. Create voice_pipeline.py

  **What to do**:
  - Create `scripts/voice_pipeline.py` — the orchestration glue
  - Function `process_inbound_voice(media_url: str, wa_number_id: str, contact_phone: str, session_name: str, msg_type: str = "ptt") -> dict`:
    1. Download audio from WAHA media URL (audio_utils.download_media)
    2. Check duration (audio_utils.get_audio_duration) — skip if > 60s
    3. Convert to WAV (audio_utils.convert_to_wav)
    4. Transcribe with STT (stt_engine.transcribe)
    5. If STT text is empty → return fallback text "Maaf, saya tidak bisa mendengar pesan suara Anda. Bisa ditulis dalam teks?"
    6. Pass transcribed text to `cs_engine.handle_inbound_message(wa_number_id, contact_phone, text, session_name)`
    7. Get response text from cs_engine result
    8. Determine reply mode: check voice_config for session's VOICE_REPLY_MODE
       - "auto": if inbound was voice → reply with voice; if text → reply with text
       - "always": always reply with voice
       - "never": always reply with text (cs_engine already sent text)
    9. If voice reply: synthesize response (tts_engine.synthesize_long_form) → convert to OGG (audio_utils.convert_to_ogg) → base64 encode → call senders.send_voice_note
    10. Return result dict: `{"action": "voice_replied"|"text_replied"|"error", "transcription": str, "response": str, "voice_sent": bool}`
  - Function `generate_voice_reply(text: str, session_name: str) -> bool` — Standalone voice synthesis + send (for cs_engine to call)
  - Add timeout wrapper: if any step takes > VOICE_TIMEOUT_SECONDS, abort and send text fallback
  - Add VRAM check before synthesis: if nvidia-smi shows < 1GB free, use CPU fallback

  **Must NOT do**:
  - Do NOT call cs_engine twice (it already sends text — need to intercept)
  - Do NOT block the webhook for > 30 seconds
  - Do NOT crash on any error — always return valid dict

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Complex orchestration with multiple external dependencies and error handling
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Tasks 5, 6)
  - **Parallel Group**: Wave 2 (after Tasks 5, 6)
  - **Blocks**: Tasks 9, 10
  - **Blocked By**: Tasks 5, 6

  **References**:
  **Pattern References**:
  - `scripts/cs_engine.py:394-547` — `handle_inbound_message()` flow: rate limit → conversation → KB search → generate → send. Voice pipeline must integrate into this flow.
  - `webhook_server.py:88-134` — Current message handling: detects type, calls handle_inbound_message. Voice pipeline intercepts BEFORE this call.
  - `scripts/senders.py:186-201` — `send_whatsapp()` pattern: try primary method, fall back on failure.

  **API/Type References**:
  - `cs_engine.handle_inbound_message()` returns `{"action": str, "response": str, "conversation_id": int, "reason": str}`
  - `stt_engine.transcribe()` returns `{"text": str, "language": str, "confidence": float, "duration": float}`
  - `tts_engine.synthesize_long_form()` returns `(sample_rate: int, wav_bytes: bytes)`

  **WHY Each Reference Matters**:
  - cs_engine flow is critical — voice pipeline needs to either intercept BEFORE text send or wrap the entire flow
  - webhook shows where voice detection happens (line 88-99) and where to route to voice_pipeline

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Voice pipeline processes a voice note end-to-end
    Tool: Bash (python)
    Preconditions: All voice modules working, test WAV from Task 4
    Steps:
      1. Run: `. .venv/bin/activate && PYTHONPATH=scripts python3 -c "
from voice_pipeline import process_inbound_voice
# Use a local file path instead of URL for testing
result = process_inbound_voice(
    media_url='file:///tmp/chatterbox_test.wav',
    wa_number_id='default',
    contact_phone='628999888777@c.us',
    session_name='default',
)
print(f'action={result.get(\"action\")}')
print(f'transcription={result.get(\"transcription\",\"\")[:100]}')
print(f'voice_sent={result.get(\"voice_sent\",False)}')
"
      2. Assert action is "voice_replied" or "text_replied" (not "error")
      3. Assert transcription is non-empty
    Expected Result: Pipeline processes voice, generates response, attempts voice reply
    Failure Indicators: action="error", empty transcription, exception
    Evidence: .sisyphus/evidence/task-7-voice-pipeline.txt

  Scenario: Fallback on invalid audio
    Tool: Bash (python)
    Preconditions: Voice pipeline exists
    Steps:
      1. Run: `. .venv/bin/activate && PYTHONPATH=scripts python3 -c "
from voice_pipeline import process_inbound_voice
result = process_inbound_voice(
    media_url='file:///tmp/nonexistent.wav',
    wa_number_id='default',
    contact_phone='628999888777@c.us',
    session_name='default',
)
print(f'action={result.get(\"action\")}')
"
      2. Assert action is NOT "error" (should gracefully degrade)
    Expected Result: Returns valid result with error indication but no crash
    Failure Indicators: Uncaught exception, 500 error
    Evidence: .sisyphus/evidence/task-7-fallback.txt
  ```

  **Commit**: YES
  - Message: `feat(voice): add voice pipeline orchestration`
  - Files: `scripts/voice_pipeline.py`

- [ ] 8. Add send_voice_note to senders.py

  **What to do**:
  - Add `send_voice_note(phone: str, audio_bytes: bytes, session_name: str, audio_format: str = "ogg") -> bool` to `scripts/senders.py`
  - Follows same pattern as `send_whatsapp_session()`:
    1. Convert phone to chat_id (handle @lid format too)
    2. Base64 encode audio bytes
    3. POST to WAHA `/api/sendVoice` with `{"session": session_name, "chatId": chat_id, "file": {"mimetype": "audio/ogg; codecs=opus", "data": base64_data}}`
    4. Try WAHA_URL first, then WAHA_DIRECT
    5. Log success/failure
  - Also add `send_audio(phone: str, audio_bytes: bytes, session_name: str, filename: str = "voice.ogg") -> bool` for non-voice-note audio (uses `/api/sendFile`)
  - Import from audio_utils for base64 encoding

  **Must NOT do**:
  - Do NOT modify existing send_whatsapp_session() or send_whatsapp() functions
  - Do NOT add voice-related imports at module level (lazy import inside function)
  - Do NOT break existing text sending functionality

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Single function addition following existing patterns
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 9, 10 — independent of engine code)
  - **Parallel Group**: Wave 3 (with Tasks 9, 10)
  - **Blocks**: Task 10
  - **Blocked By**: Tasks 2, 3

  **References**:
  **Pattern References**:
  - `scripts/senders.py:204-223` — `send_whatsapp_session()` — THE pattern to follow. Handles @lid vs @c.us, tries multiple WAHA targets.
  - `scripts/senders.py:226-280` — `_send_wa_waha_raw()` — Core WAHA sending with fallback targets. Voice sending uses same structure but different endpoint.
  - `scripts/senders.py:96-162` — `_send_wa_waha()` — Session iteration and target fallback pattern.

  **API/Type References**:
  - WAHA sendVoice endpoint: `POST {url}/api/sendVoice` with JSON body `{"session": "name", "chatId": "628xxx@c.us", "file": {"mimetype": "audio/ogg; codecs=opus", "data": "base64..."}}`
  - Headers: `{"X-Api-Key": key, "Content-Type": "application/json"}`

  **External References**:
  - WAHA API docs for voice sending

  **WHY Each Reference Matters**:
  - senders.py has battle-tested WAHA communication patterns with auth, fallback, error handling. New function MUST match this exactly.

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: send_voice_note function exists and accepts correct parameters
    Tool: Bash (python)
    Preconditions: senders.py modified
    Steps:
      1. Run: `. .venv/bin/activate && PYTHONPATH=scripts python3 -c "
import inspect
from senders import send_voice_note
sig = inspect.signature(send_voice_note)
params = list(sig.parameters.keys())
print(f'params={params}')
assert 'phone' in params
assert 'audio_bytes' in params
assert 'session_name' in params
print('OK')
"
      2. Assert function signature has phone, audio_bytes, session_name parameters
    Expected Result: Function exists with correct signature
    Failure Indicators: ImportError, missing parameters
    Evidence: .sisyphus/evidence/task-8-send-voice-sig.txt

  Scenario: send_voice_note makes WAHA API call (mock test)
    Tool: Bash (python)
    Preconditions: senders.py modified
    Steps:
      1. Run: `. .venv/bin/activate && PYTHONPATH=scripts python3 -c "
from unittest.mock import patch, MagicMock
from senders import send_voice_note
with patch('senders._req') as mock_req:
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_req.post.return_value = mock_resp
    result = send_voice_note('62881080269682', b'fake_audio_data', 'warung_kecantikan')
    print(f'result={result}')
    assert result == True
    # Verify correct endpoint was called
    call_args = mock_req.post.call_args
    print(f'endpoint={call_args[0][0]}')
    assert '/api/sendVoice' in call_args[0][0]
"
      2. Assert WAHA /api/sendVoice endpoint called
    Expected Result: Function calls correct WAHA endpoint with correct payload
    Failure Indicators: Wrong endpoint, wrong payload format
    Evidence: .sisyphus/evidence/task-8-send-voice-mock.txt
  ```

  **Commit**: YES
  - Message: `feat(voice): add send_voice_note to senders`
  - Files: `scripts/senders.py`

- [ ] 9. Update webhook_server.py for voice detection

  **What to do**:
  - Modify `webhook_server.py` to detect and route voice notes
  - At line 88-99 (message type detection), change voice handling:
    - Instead of replacing body_text with `[Customer mengirim voice note]`, route to voice_pipeline
    - When `msg_type in ("audio", "ptt")` AND `VOICE_ENABLED` is True:
      1. Extract media URL from `payload.get("media", {}).get("url", "")`
      2. Import voice_pipeline (lazy import at function level)
      3. Call `voice_pipeline.process_inbound_voice(media_url, wa_number_id, sender, session, msg_type)`
      4. Return the voice pipeline result
    - If VOICE_ENABLED is False OR media_url is empty → fall back to current text placeholder behavior
  - Add import guard: try importing voice_pipeline, catch ImportError gracefully
  - Keep existing behavior for text, image, video, document types unchanged

  **Must NOT do**:
  - Do NOT break existing text message handling
  - Do NOT add heavy ML imports at module level
  - Do NOT change the webhook response format
  - Do NOT remove the dedup logic (lines 74-79)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Careful modification of production webhook handler with graceful fallback
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 8, 10)
  - **Parallel Group**: Wave 3 (with Tasks 8, 10)
  - **Blocks**: Task 11
  - **Blocked By**: Tasks 5, 7

  **References**:
  **Pattern References**:
  - `webhook_server.py:57-139` — THE webhook handler function. Shows: event extraction, dedup, from_me check, group skip, type filter, media handling, handle_inbound_message call.
  - `webhook_server.py:88-99` — Current media type handling (the section being modified). Voice/PTT currently just gets a text label.

  **API/Type References**:
  - WAHA webhook payload for voice:
    ```json
    {
      "event": "message",
      "session": "warung_kecantikan",
      "payload": {
        "from": "628xxx@c.us",
        "type": "ptt",
        "body": "",
        "fromMe": false,
        "id": "msg_xxx",
        "hasMedia": true,
        "media": {
          "mimetype": "audio/ogg; codecs=opus",
          "url": "http://WAHA_HOST/api/files/xxx.opus"
        }
      }
    }
    ```

  **WHY Each Reference Matters**:
  - webhook handler is the entry point — must not break it. Current code at lines 88-99 is the exact section to modify. Need to preserve all existing logic and just add voice routing.

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Voice note detected and routed to voice pipeline
    Tool: Bash (curl)
    Preconditions: Flask server running on port 8766
    Steps:
      1. Run: `curl -s -X POST http://localhost:8766/webhook/waha -H "Content-Type: application/json" -d '{"event":"message","session":"default","payload":{"from":"628999888777@c.us","type":"ptt","body":"","fromMe":false,"id":"test_voice_001","hasMedia":true,"media":{"mimetype":"audio/ogg; codecs=opus","url":"http://example.com/test.opus"}}}'`
      2. Assert response status 200
      3. Assert response JSON contains "status": "ok"
    Expected Result: Webhook processes voice note without error
    Failure Indicators: 500 error, "error" in response, crash
    Evidence: .sisyphus/evidence/task-9-webhook-voice.txt

  Scenario: Text messages still work unchanged
    Tool: Bash (curl)
    Preconditions: Flask server running on port 8766
    Steps:
      1. Run: `curl -s -X POST http://localhost:8766/webhook/waha -H "Content-Type: application/json" -d '{"event":"message","session":"default","payload":{"from":"628999888777@c.us","type":"chat","body":"Halo, saya tertarik dengan produk Anda","fromMe":false,"id":"test_text_001"}}'`
      2. Assert response status 200
      3. Assert response JSON contains "status": "ok"
      4. Assert action is "replied" or "skipped" (not "error")
    Expected Result: Text messages processed exactly as before
    Failure Indicators: Different behavior than before voice changes
    Evidence: .sisyphus/evidence/task-9-webhook-text.txt

  Scenario: Voice with missing media URL falls back gracefully
    Tool: Bash (curl)
    Preconditions: Flask server running
    Steps:
      1. Run: `curl -s -X POST http://localhost:8766/webhook/waha -H "Content-Type: application/json" -d '{"event":"message","session":"default","payload":{"from":"628999888777@c.us","type":"ptt","body":"","fromMe":false,"id":"test_voice_no_media_001"}}'`
      2. Assert response status 200 (no crash)
    Expected Result: Falls back to text placeholder, no crash
    Failure Indicators: 500 error, exception
    Evidence: .sisyphus/evidence/task-9-webhook-fallback.txt
  ```

  **Commit**: YES
  - Message: `feat(voice): add voice note detection to webhook`
  - Files: `webhook_server.py`

- [ ] 10. Update cs_engine.py for voice reply mode

  **What to do**:
  - Modify `scripts/cs_engine.py` to support voice reply mode
  - Add optional parameter `voice_reply: bool = False` to `handle_inbound_message()`
  - When `voice_reply=True`:
    - Skip the text send at lines 531-534 (send_typing_indicator + send_whatsapp_session)
    - Instead, import and call `voice_pipeline.generate_voice_reply(response_text, session_name, contact_phone)`
    - If voice generation fails, fall back to sending text
  - Add a new function `reply_with_voice(contact_phone: str, response_text: str, session_name: str) -> bool` that:
    1. Gets TTS engine (lazy load)
    2. Synthesizes response_text to audio
    3. Converts to OGG
    4. Calls send_voice_note
    5. Returns True if voice sent, False if fallback to text
  - Keep all existing text reply logic intact when voice_reply=False

  **Must NOT do**:
  - Do NOT change default behavior (voice_reply defaults to False)
  - Do NOT remove text sending entirely (always need fallback)
  - Do NOT break existing CLI test mode (--test flag)
  - Do NOT import ML libraries at module level

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Careful modification of core CS logic with backward compatibility
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 8, 9)
  - **Parallel Group**: Wave 3 (with Tasks 8, 9)
  - **Blocks**: Task 11
  - **Blocked By**: Tasks 6, 7, 8

  **References**:
  **Pattern References**:
  - `scripts/cs_engine.py:530-534` — THE text reply section to modify. Currently: send_typing → sleep → send_whatsapp_session → stop_typing. Need to add voice branch here.
  - `scripts/cs_engine.py:482-486` — Escalation message sending (similar pattern). Shows how senders are called.
  - `scripts/cs_engine.py:582-618` — CLI test mode. Must continue working with new voice_reply parameter.

  **API/Type References**:
  - `senders.send_voice_note(phone, audio_bytes, session_name)` — New function from Task 8
  - `voice_pipeline.generate_voice_reply(text, session_name)` — New function from Task 7

  **WHY Each Reference Matters**:
  - Line 530-534 is the exact insertion point. Must preserve the typing indicator and add voice path BEFORE the text send.
  - CLI test mode must not break — it monkey-patches senders.

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Voice reply mode sends voice instead of text
    Tool: Bash (python)
    Preconditions: All modules working, GPU available
    Steps:
      1. Run: `. .venv/bin/activate && PYTHONPATH=scripts python3 -c "
from unittest.mock import patch, MagicMock
import cs_engine as _ce

# Mock the voice sending
with patch('cs_engine.send_voice_note', return_value=True) as mock_vn:
    with patch('cs_engine.send_whatsapp_session', return_value=True) as mock_txt:
        with patch('cs_engine.send_typing_indicator', return_value=True):
            _ce.init_db()
            result = _ce.handle_inbound_message(
                wa_number_id='default',
                contact_phone='628999888777@c.us',
                message_text='Halo',
                session_name='default',
                voice_reply=True,
            )
            print(f'action={result.get(\"action\")}')
            # Voice should have been attempted
            print(f'voice_called={mock_vn.called}')
            print(f'text_called={mock_txt.called}')
"
      2. Assert voice_reply parameter is accepted (no TypeError)
      3. Assert action is "replied" (or "voice_replied")
    Expected Result: Voice reply attempted instead of text when voice_reply=True
    Failure Indicators: TypeError (missing parameter), voice not attempted
    Evidence: .sisyphus/evidence/task-10-cs-voice-mode.txt

  Scenario: Default behavior unchanged (text reply)
    Tool: Bash (python)
    Preconditions: cs_engine.py modified
    Steps:
      1. Run: `. .venv/bin/activate && PYTHONPATH=scripts python3 -c "
from unittest.mock import patch
import cs_engine as _ce

with patch('cs_engine.send_whatsapp_session', return_value=True) as mock_txt:
    with patch('cs_engine.send_typing_indicator', return_value=True):
        _ce.init_db()
        result = _ce.handle_inbound_message(
            wa_number_id='default',
            contact_phone='628999888777@c.us',
            message_text='Halo',
            session_name='default',
        )
        print(f'action={result.get(\"action\")}')
        print(f'text_called={mock_txt.called}')
"
      2. Assert text sending still called (default behavior preserved)
    Expected Result: Text reply sent exactly as before when no voice_reply parameter
    Failure Indicators: Text not sent, different behavior
    Evidence: .sisyphus/evidence/task-10-cs-text-default.txt
  ```

  **Commit**: YES
  - Message: `feat(voice): add voice reply mode to CS engine`
  - Files: `scripts/cs_engine.py`

- [ ] 11. End-to-end integration test

  **What to do**:
  - Create comprehensive integration test `scripts/test_voice_integration.py`
  - Test 1: STT → LLM → TTS pipeline (offline, no WAHA)
    - Generate test audio with TTS: "Berapa harga serum wajah?"
    - Transcribe with STT
    - Pass to cs_engine (mock mode) → get response text
    - Synthesize response with TTS
    - Save all intermediate results to evidence files
  - Test 2: Webhook voice note processing (with mock WAHA)
    - Simulate WAHA webhook payload with voice note
    - Verify webhook routes to voice pipeline
    - Verify response sent (mock the send function)
  - Test 3: Error scenarios
    - Invalid audio → text fallback
    - VRAM OOM → CPU fallback
    - Missing media URL → text fallback
    - Very long audio (>60s) → rejection with message
  - Test 4: Concurrent voice notes
    - Send 2 voice notes simultaneously
    - Verify both processed (sequentially, no crash)
  - Record all timings and save report

  **Must NOT do**:
  - Do NOT send real WhatsApp messages (mock all senders)
  - Do NOT require internet access (use local files only)
  - Do NOT modify production code

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Comprehensive testing with mocking, timing analysis, edge cases
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on all prior tasks)
  - **Parallel Group**: Wave 4 (after Wave 3)
  - **Blocks**: Task 12
  - **Blocked By**: Tasks 9, 10

  **References**:
  **Pattern References**:
  - `scripts/cs_engine.py:554-618` — CLI test mode pattern for mocking senders
  - `scripts/test_voice_models.py` — (Task 4) VRAM profiling test to build upon

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Full pipeline test passes
    Tool: Bash (python)
    Preconditions: All voice modules installed and working
    Steps:
      1. Run: `. .venv/bin/activate && PYTHONPATH=scripts python3 scripts/test_voice_integration.py 2>&1`
      2. Assert exit code 0
      3. Check output for "ALL TESTS PASSED" or similar
      4. Check output for timing report (each test < 30s)
    Expected Result: All integration tests pass within time limits
    Failure Indicators: Non-zero exit code, test failures, timeouts
    Evidence: .sisyphus/evidence/task-11-integration-test.txt

  Scenario: Error scenarios handled gracefully
    Tool: Bash (python)
    Preconditions: Integration test script exists
    Steps:
      1. Check integration test output for "Error scenarios" section
      2. Assert all error scenarios report "PASS" (graceful handling)
    Expected Result: All error cases handled without crashes
    Failure Indicators: Uncaught exceptions in error scenarios
    Evidence: .sisyphus/evidence/task-11-error-scenarios.txt
  ```

  **Commit**: YES
  - Message: `test(voice): end-to-end integration test`
  - Files: `scripts/test_voice_integration.py`

- [ ] 12. Deploy + restart services

  **What to do**:
  - Restart 1ai-reach-mcp systemd service: `sudo systemctl restart 1ai-reach-mcp`
  - Verify health endpoint: `curl http://localhost:8766/health`
  - Check logs for errors: `journalctl -u 1ai-reach-mcp -n 50 --no-pager`
  - Verify GPU usage: `nvidia-smi`
  - Test webhook with test voice note (curl to webhook)
  - Test webhook with text message (ensure backward compatibility)
  - If any service fails to start: check logs, fix, restart again
  - Once verified: git push to origin

  **Must NOT do**:
  - Do NOT restart dashboard unless needed (it's static Next.js)
  - Do NOT force-push to remote

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Standard deployment commands
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on all prior tasks)
  - **Parallel Group**: Wave 4 (after Task 11)
  - **Blocks**: Final verification
  - **Blocked By**: Task 11

  **References**:
  **Pattern References**:
  - `systemd/` — systemd unit files for 1ai-reach-mcp

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Service restarts successfully
    Tool: Bash
    Preconditions: All code committed
    Steps:
      1. Run: `sudo systemctl restart 1ai-reach-mcp`
      2. Run: `sleep 3 && systemctl is-active 1ai-reach-mcp`
      3. Assert output is "active"
      4. Run: `curl -s http://localhost:8766/health`
      5. Assert JSON response with "status": "ok"
    Expected Result: Service running and healthy
    Failure Indicators: "failed", "inactive", connection refused
    Evidence: .sisyphus/evidence/task-12-service-health.txt

  Scenario: Voice webhook works in production
    Tool: Bash (curl)
    Preconditions: Service running
    Steps:
      1. Run: `curl -s -X POST http://localhost:8766/webhook/waha -H "Content-Type: application/json" -d '{"event":"message","session":"default","payload":{"from":"628999888777@c.us","type":"ptt","body":"","fromMe":false,"id":"prod_test_voice_001","hasMedia":true,"media":{"mimetype":"audio/ogg","url":"http://example.com/test.opus"}}}'`
      2. Assert response status 200
    Expected Result: Webhook processes voice without crash
    Failure Indicators: 500 error, service crash
    Evidence: .sisyphus/evidence/task-12-prod-voice.txt

  Scenario: Text messages still work
    Tool: Bash (curl)
    Preconditions: Service running
    Steps:
      1. Run: `curl -s -X POST http://localhost:8766/webhook/waha -H "Content-Type: application/json" -d '{"event":"message","session":"default","payload":{"from":"628999888777@c.us","type":"chat","body":"Halo kak","fromMe":false,"id":"prod_test_text_001"}}'`
      2. Assert response status 200 and action is "replied" or "skipped"
    Expected Result: Text messages work exactly as before
    Failure Indicators: Different behavior than pre-voice deployment
    Evidence: .sisyphus/evidence/task-12-prod-text.txt
  ```

  **Commit**: YES
  - Message: `chore(voice): deploy and restart services`
  - Files: N/A (deployment only, git push)

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 3 review agents run in PARALLEL. ALL must APPROVE. Rejection → fix → re-run.

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, run command). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Review all changed files for: `as any` type ignores, empty catches, console.log in prod, commented-out code, unused imports. Check AI slop: excessive comments, over-abstraction, generic names. Verify no Flosia/laundry content in voice modules. Check all config values come from config.py.
  Output: `Files [N clean/N issues] | VERDICT: APPROVE/REJECT`

- [ ] F3. **Real Manual QA** — `unspecified-high`
  Start from clean state. Execute EVERY QA scenario from EVERY task. Test end-to-end: send test voice note via WAHA API → verify webhook processes → verify STT transcribes → verify TTS generates → verify voice sent. Test error cases: missing audio, OOM fallback, text fallback. Save evidence to `.sisyphus/evidence/final-qa/`.
  Output: `Scenarios [N/N pass] | Integration [N/N] | Edge Cases [N tested] | VERDICT: APPROVE/REJECT`

---

## Commit Strategy

- **Task 1**: `feat(deps): install voice pipeline dependencies (torch, chatterbox-tts, nltk)` — requirements.txt or venv
- **Task 2-3**: `feat(voice): add voice config and audio utilities` — scripts/voice_config.py, scripts/audio_utils.py
- **Task 4**: `test(voice): validate ChatterBox multilingual + VRAM profiling` — scripts/test_voice_models.py
- **Task 5**: `feat(voice): add STT engine with faster-whisper` — scripts/stt_engine.py
- **Task 6**: `feat(voice): add TTS engine with ChatterBox multilingual` — scripts/tts_engine.py
- **Task 7**: `feat(voice): add voice pipeline orchestration` — scripts/voice_pipeline.py
- **Task 8**: `feat(voice): add send_voice_note to senders` — scripts/senders.py
- **Task 9**: `feat(voice): add voice note detection to webhook` — webhook_server.py
- **Task 10**: `feat(voice): add voice reply mode to CS engine` — scripts/cs_engine.py
- **Task 11**: `test(voice): end-to-end integration test` — tests/
- **Task 12**: `chore(voice): deploy and restart services` — systemd/

---

## Success Criteria

### Verification Commands
```bash
# All modules import cleanly
cd /home/openclaw/.openclaw/workspace/1ai-reach
. .venv/bin/activate
python3 -c "from voice_config import *; print('voice_config OK')"
python3 -c "from audio_utils import *; print('audio_utils OK')"
python3 -c "from stt_engine import STTEngine; print('stt_engine OK')"
python3 -c "from tts_engine import TTSEngine; print('tts_engine OK')"
python3 -c "from voice_pipeline import VoicePipeline; print('voice_pipeline OK')"

# VRAM usage within budget
nvidia-smi --query-gpu=memory.used --format=csv,noheader  # Should be < 5GB

# Services running
systemctl is-active 1ai-reach-mcp  # Should be "active"
curl -s http://localhost:8766/health | python3 -m json.tool  # Should return {"status": "ok"}
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] Voice notes work end-to-end (voice in → voice out)
- [ ] Text fallback works when voice fails
- [ ] VRAM usage under 5GB
- [ ] End-to-end latency < 30 seconds
- [ ] All services running and healthy
