# FRAGMENT — AI News-to-Video Automation Engine

> **ET Gen AI Hackathon 2025** | Built for the Economic Times GenAI Challenge

**FRAGMENT** is an end-to-end AI system that monitors Economic Times RSS feeds, detects trending business news, and automatically converts articles into viral short-form videos — then publishes them directly to YouTube Shorts. Zero human intervention. One click. Full video. Live on YouTube.

---

## The Problem We're Solving

India's business news ecosystem produces thousands of articles daily. Economic Times alone publishes hundreds of stories — on AI startups, market movements, funding rounds, and policy shifts. These stories reach readers who scroll past them in seconds.

Meanwhile, YouTube Shorts gets **70 billion views per day.** Instagram Reels. TikTok. Short-form video is the most powerful distribution channel ever built.

**The gap:** World-class business journalism is trapped in text format while the world has moved to video.

**The cost of bridging that gap manually:** 4 people × 4 hours × ₹400 per video = unsustainable at scale.

**FRAGMENT closes that gap with AI — in under 4 minutes per video.**

---

## Live Demo Result

```
Article  →  "India's economic ties with Azerbaijan improve despite political drift"
Video ID →  isuGi9gZM5c
URL      →  https://youtube.com/shorts/isuGi9gZM5c
Time     →  6 seconds to upload after assembly
```

---

## How It Works — Full Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                    FRAGMENT PIPELINE                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. FETCH      Economic Times RSS (3 feeds, 100+ articles)  │
│       ↓                                                     │
│  2. RANK       AI Trend Scoring (100-point algorithm)       │
│       ↓                                                     │
│  3. SELECT     Top 3 trending articles only                 │
│       ↓                                                     │
│  4. SCRIPT     GPT-4 viral script generation                │
│                HOOK → NEWS → WHY → FACT → ENDING            │
│       ↓                                                     │
│  5. VISUALS    Article images + DALL-E 3 fallback           │
│       ↓                                                     │
│  6. VOICE      Kokoro TTS (local, zero API cost)            │
│       ↓                                                     │
│  7. ASSEMBLE   MoviePy → 1080×1920 MP4, burned subtitles    │
│       ↓                                                     │
│  8. THUMBNAIL  PIL → Bold text overlay, 1280×720            │
│       ↓                                                     │
│  9. METADATA   GPT-4 → Title, description, hashtags         │
│       ↓                                                     │
│ 10. PUBLISH    YouTube Data API v3 → Live on Shorts         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Judging Criteria Alignment

### Innovation & Creativity ✅

**What makes FRAGMENT novel:**

- **Trend Intelligence** — Not just "latest articles." A 100-point scoring algorithm weighs recency, keyword virality, category relevance, and headline psychology. Only the top 3 articles per run are processed.

- **Viral Script Architecture** — GPT-4 doesn't summarize. It writes using a proven viral structure:
  ```
  HOOK        (0–3s)   Stop the scroll
  THE NEWS    (3–13s)  What happened
  WHY MATTERS (13–23s) Why you should care
  KEY FACT    (23–31s) The number that changes everything
  ENDING      (31–36s) Follow for more
  ```

- **Hybrid Visual Sourcing** — Uses real article images first (authentic, contextual), falls back to DALL-E 3 only when needed (cost-efficient).

- **Local TTS** — Kokoro TTS runs entirely on-device. No per-character API cost. No latency. Professional news anchor voice.

---

### Technical Implementation ✅

**Multi-Agent Architecture** — 7 specialized AI agents, each with a single responsibility:

| Agent | Responsibility |
|-------|---------------|
| `ViralScriptAgent` | GPT-4 script generation with viral structure |
| `ImageGeneratorAgent` | Hybrid sourcing: article images → DALL-E 3 |
| `AudioGeneratorAgent` | Kokoro TTS narration |
| `VideoAssemblyAgent` | MoviePy assembly, subtitles, effects |
| `ThumbnailAgent` | PIL thumbnail with text overlay |
| `MetadataAgent` | Platform-optimized titles, descriptions, hashtags |
| `PublishingAgent` | YouTube resumable upload API |

**Content Intelligence:**

```python
# Trend scoring — every article scored out of 100
trend_score = (
    recency_score      # 0–30: < 1hr = 30pts, < 6hr = 25pts
  + keyword_score      # 0–40: AI=10, Startup=8, IPO=9, Funding=8
  + category_score     # 0–20: Tech×1.5, Startup×1.4, AI×1.5
  + virality_score     # 0–10: numbers, shocking, breaking, exclusive
)
```

**Tech Stack:**

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10, FastAPI, Uvicorn |
| AI / LLM | OpenAI GPT-4, DALL-E 3 |
| TTS | Kokoro (local, offline) |
| Video | MoviePy, PIL/Pillow, pysrt |
| Content | feedparser, BeautifulSoup4 |
| Publishing | YouTube Data API v3 |
| Frontend | React 18, Vite, TailwindCSS |

**RSS Feeds Monitored:**
```
https://economictimes.indiatimes.com/rssfeedsdefault.cms
https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms
https://economictimes.indiatimes.com/news/rssfeeds/1715249553.cms
```

---

### Feasibility & Scalability ✅

**It works today.** We have live YouTube videos generated and published by this system.

**Cost per video:**
- GPT-4 script: ~₹2
- DALL-E 3 images (5): ~₹30
- TTS: ₹0 (local)
- Assembly: ₹0 (local)
- YouTube upload: ₹0
- **Total: ~₹32 per video**

**Time per video:** 3–5 minutes end-to-end

**Scaling path:**
- Run every 6 hours → 4 videos/day → 120 videos/month → ₹3,840/month
- Add APScheduler for fully automated scheduled runs
- Extend to Instagram Reels, TikTok, LinkedIn (API integrations already built)
- Multi-language support via GPT-4 translation layer
- White-label for any news publication (Mint, Business Standard, NDTV Profit)

**Caching:** RSS feeds cached for 5 minutes. Article content fetched lazily — only for top-ranked articles, not all 100+.

---

### Relevance to Problem Statement ✅

This project is built **specifically for Economic Times** and the GenAI challenge:

- Uses Economic Times RSS feeds as the **only content source**
- Generates content optimized for **ET's audience** (business, finance, tech)
- Demonstrates how ET can **extend its reach** from text readers to video viewers
- Directly addresses the **content distribution gap** in Indian business media
- Built with **Indian market context** — India tech, startup ecosystem, Sensex, Nifty keywords weighted in trend scoring

**The irony:** We built a system that turns Economic Times articles into viral videos — for an Economic Times hackathon.

---

### Documentation & Presentation Quality ✅

See `FRAGMENT_SPEECH.md` for the full 3-minute demo presentation script.

---

## Project Structure

```
FRAGMENT/
├── app/
│   ├── agents/                  # 7 specialized AI agents
│   │   ├── viral_script_agent.py
│   │   ├── image_agent.py
│   │   ├── audio_agent.py
│   │   ├── assembly_agent.py
│   │   ├── thumbnail_agent.py
│   │   ├── metadata_agent.py
│   │   └── publishing_agent.py
│   ├── api/v1/
│   │   ├── automation.py        # POST /automation/run
│   │   └── videos.py            # GET /videos/list
│   ├── services/
│   │   └── news_automation_service.py  # Pipeline orchestration
│   └── core/config.py           # Pydantic settings
│
├── content_sources/
│   ├── economic_times_fetcher.py  # RSS + BeautifulSoup scraping
│   └── trend_analyzer.py          # 100-point scoring algorithm
│
├── new-frontend/                # React 18 dashboard
│   └── src/
│       ├── features/dashboard/
│       │   └── components/
│       │       ├── AutomationPanel.jsx   # One-click automation
│       │       └── VideoLibrarySection.jsx
│       └── services/
│           └── automationApi.js
│
├── resources/                   # Runtime output (gitignored)
│   ├── scripts/    # Generated JSON scripts
│   ├── images/     # Sourced/generated images
│   ├── audio/      # TTS segments
│   ├── video/      # Assembled videos + thumbnails
│   └── subtitles/  # SRT files
│
├── static/videos/               # Served to frontend
├── tts/                         # Kokoro TTS integration
├── assembly/                    # MoviePy pipeline
└── imagegen/                    # DALL-E integration
```

---

## Setup & Run

### 1. Clone and install

```bash
git clone <repo-url>
cd FRAGMENT
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Add your API keys to .env
```

Required keys:
```env
OPENAI_API_KEY=sk-proj-...
YOUTUBE_API_KEY=AIza...
YOUTUBE_ACCESS_TOKEN=ya29...
```

### 3. Install frontend

```bash
cd new-frontend
npm install
```

### 4. Run

**Terminal 1 — Backend:**
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd new-frontend && npm run dev
```

**Open:** http://localhost:5173

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/automation/run` | Run full pipeline |
| `GET` | `/api/v1/automation/status` | Live progress |
| `GET` | `/api/v1/automation/trending` | Top articles with scores |
| `GET` | `/api/v1/videos/list` | Generated video library |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Swagger UI |

```bash
# Run automation via curl
curl -X POST http://localhost:8000/api/v1/automation/run \
  -H "Content-Type: application/json" \
  -d '{"top_n": 3, "auto_publish": true}'
```

---

## Verification

```bash
python verify_setup.py      # Check all imports, keys, directories
python test_end_to_end.py   # Run 10 integration tests
```

Expected:
```
TOTAL: 10/10 tests passed (100%)
🎉 ALL TESTS PASSED! APPLICATION IS READY!
```

---


## Built For

**ET Gen AI Hackathon 2025**
In partnership with Unstop
Organized by The Economic Times

> *"This is the platform where students turn ideas into impactful solutions and establish themselves as the next generation of AI leaders."*

---

*FRAGMENT — Because every great story deserves to be seen.*
