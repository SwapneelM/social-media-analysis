# Social Media Analysis Dashboard

A case-study dashboard that collects posts from Twitter/X, Facebook/Meta, and TikTok, extracts factual claims using GPT-4o, and presents them in a React dashboard with human verification.

## Project Goals

1. Collect 25 posts each from Twitter, Facebook, and TikTok on a given topic
2. Extract factual claims from posts using GPT-4o (via OpenRouter)
3. Auto-classify claims by confidence: auto-accepted (≥0.85), needs-review (0.60–0.85), auto-rejected (<0.60)
4. Present results in a React dashboard for human review and verification
5. Export verified claims as JSON

## Architecture

```
[React Dashboard (Vite)]  ──reads──>  data/*.json  <──writes──  [Python Scripts]
                                                                      │
                               ┌──────────────────────────────────────┤
                               │                  │                   │
                        twitterapi.io       BrightData API      OpenRouter API
                        (keyword search)    (Meta + TikTok)     (GPT-4o claims)
```

- **Python scripts** collect social media data and extract claims, writing results to `data/` as JSON
- **React app** reads those JSON files and displays them in a dashboard
- **Human verification** uses localStorage + JSON export (no backend server)

## Project Structure

```
collectors/              # Python data collection modules
  config.py              # Environment config and constants
  retry_utils.py         # Exponential backoff decorator
  file_utils.py          # Atomic JSON save utility
  twitter_collector.py   # Twitter/X via twitterapi.io
  brightdata_utils.py    # Shared BrightData trigger/poll/download
  meta_collector.py      # Facebook via BrightData
  tiktok_collector.py    # TikTok via BrightData
  run_collection.py      # CLI entry point for data collection
claims/                  # Claims extraction modules
  prompts.py             # GPT-4o prompts and few-shot examples
  extractor.py           # OpenRouter API calls + confidence classification
  run_extraction.py      # CLI entry point for claims extraction
dashboard/               # React (Vite) dashboard app
data/                    # Output JSON files (posts.json, claims.json)
  raw/                   # Raw API responses (gitignored)
tests/                   # All unit tests
scratchpad/              # Task decomposition notes
```

## Data

- `data/posts.json` — Unified post schema from all platforms
- `data/claims.json` — Extracted claims with confidence scores and status
- `data/raw/` — Raw API responses (gitignored, for debugging)

## Setup

### Prerequisites

- Python 3.9+
- Node.js 18+

### Installation

```bash
# Python dependencies
pip install -r requirements.txt

# React dashboard
cd dashboard && npm install
```

### Environment Variables

1. Copy the dummy env file:
   ```bash
   cp .env.dummy .env
   ```
2. Open `.env` and fill in your API keys:
   - `TWITTERAPI_KEY` — from [twitterapi.io](https://twitterapi.io)
   - `BRIGHTDATA_API_KEY` — from [BrightData](https://brightdata.com) (Account Settings > API tokens)
   - `OPENROUTER_API_KEY` — from [OpenRouter](https://openrouter.ai/keys)
3. Never commit `.env` (it's already in `.gitignore`)

## Sample URLs for Data Collection

The demo topic is **India AI Impact Summit 2026**. Below are verified, public URLs you can use with each platform.

### Twitter Keywords

Use these keywords to search for tweets about the summit:

- `"India AI Impact Summit"`
- `"AI Impact Summit" India`
- `#AIImpactSummit`

### Facebook Pages (for BrightData collection)

These are verified public Facebook pages of organizations involved in India's AI ecosystem:

- [IndiaAI (Official)](https://www.facebook.com/INDIAai) — Government of India's AI portal
- [NITI Aayog](https://www.facebook.com/NITIAayog/) — India's policy think tank, key organizer
- [NASSCOM](https://www.facebook.com/nasscomOfficial/) — India's IT industry association
- [Digital India](https://www.facebook.com/OfficialDigitalIndia/) — Government digital transformation initiative

### TikTok Videos (for BrightData collection)

**Important**: BrightData's TikTok Posts dataset requires individual **video URLs** (not profile URLs). Find videos via Google search: `site:tiktok.com "India AI"`.

India + AI related TikTok videos:

- [@nala.india — "AI is actually... Indian?!"](https://www.tiktok.com/@nala.india/video/7509540960238341381)
- [@uptin — "AI Changing Indian Accents"](https://www.tiktok.com/@uptin/video/7482022226741447958)
- [@lexfridman — Sundar Pichai on India](https://www.tiktok.com/@lexfridman/video/7513527554477772062)
- [@nate.b.jones — Amazon's AI in India](https://www.tiktok.com/@nate.b.jones/video/7353448604138278174)
- [@varun_rana_ — "AI = Amazon India"](https://www.tiktok.com/@varun_rana_/video/7353652876734041390)

### Example Collection Command

```bash
python -m collectors.run_collection \
  --twitter-keywords "India AI Impact Summit" "#AIImpactSummit" \
  --meta-urls "https://www.facebook.com/INDIAai" \
  --tiktok-urls \
    "https://www.tiktok.com/@nala.india/video/7509540960238341381" \
    "https://www.tiktok.com/@uptin/video/7482022226741447958" \
    "https://www.tiktok.com/@lexfridman/video/7513527554477772062"
```

## Usage

### 1. Collect Data

```bash
python -m collectors.run_collection \
  --twitter-keywords "keyword1" "keyword2" \
  --meta-urls "https://facebook.com/page" \
  --tiktok-urls "https://tiktok.com/@user"
```

### 2. Extract Claims

```bash
python -m claims.run_extraction
```

### 3. Run Dashboard

```bash
cd dashboard && npm run dev
```

### 4. Run Tests

```bash
python -m pytest tests/ -v
```
