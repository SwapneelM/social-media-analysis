# Social Media Claims Analysis — Methodology

> A step-by-step walkthrough of how we collect social media data from Twitter, Facebook, and TikTok, extract factual claims using AI, and present them for human verification.

---

## Slide 1: Overview — What We Built

A three-stage pipeline for social media fact-checking:

1. **Collect** — Pull posts from Twitter, Facebook, and TikTok using their respective APIs
2. **Extract** — Use GPT-4o to identify factual claims in each post
3. **Verify** — Human reviewers accept or reject AI-classified claims in a dashboard

**Key principle**: Every claim needs both AI confidence scoring AND human judgment.

---

## Slide 2: Architecture at a Glance

```
┌─────────────────┐     ┌──────────────┐     ┌──────────────────┐
│  Data Collection │ --> │  Claims      │ --> │  React Dashboard │
│  (Python)        │     │  Extraction  │     │  (Human Review)  │
│                  │     │  (GPT-4o)    │     │                  │
│  Twitter API     │     │              │     │  Accept / Reject │
│  BrightData API  │     │  Confidence  │     │  Reviewer Notes  │
│  (Meta + TikTok) │     │  Scoring     │     │  JSON Export     │
└─────────────────┘     └──────────────┘     └──────────────────┘
```

- No backend server — Python writes JSON files, React reads them
- Crash-safe: atomic file writes ensure data is never corrupted
- All API calls use exponential backoff for reliability

---

## Slide 3: Twitter Collection — Keyword Search

### How It Works

We search Twitter for posts matching specific keywords using the **twitterapi.io** Advanced Search API.

### Method

1. **Define keywords**: e.g., `"India AI Impact Summit"`, `"#AIImpactSummit"`
2. **Send search query**: Keywords are combined with `OR` logic
3. **Paginate**: Follow `next_cursor` tokens until we have 25 posts
4. **Save incrementally**: Each page of results is saved to disk immediately (crash safety)

### Technical Details

- **Endpoint**: `GET https://api.twitterapi.io/twitter/tweet/advanced_search`
- **Authentication**: API key in `x-api-key` header
- **Query type**: `"Latest"` (most recent posts first)
- **Rate limit handling**: Exponential backoff on HTTP 429 responses

### Example Query

```
query: "India AI Impact Summit" OR "#AIImpactSummit"
queryType: Latest
```

### What We Get

Each tweet is normalized to a unified schema:
- Post ID, author, full text, URL
- Engagement metrics (likes, retweets, replies)
- Timestamp and collection timestamp

### Our Results

- Searched for: `"India AI Impact Summit" OR "#AIImpactSummit"`
- Collected: **25 tweets** across 2 pages
- Time taken: ~3 seconds

---

## Slide 4: Facebook Collection — URL-Based via BrightData

### The Challenge

Facebook doesn't offer a public keyword search API. You can't just search "India AI" and get posts.

### Our Solution: BrightData Web Scraper API

BrightData is a web data platform that provides structured data extraction from social media sites. We use their **Facebook Posts** dataset to scrape public page posts.

### Method

1. **Find Facebook pages via Google Search**: Search for organizations related to our topic
   - e.g., Google: `"India AI" Facebook page NASSCOM NITI Aayog`
   - Found: [IndiaAI](https://www.facebook.com/INDIAai), [NITI Aayog](https://www.facebook.com/NITIAayog/), [NASSCOM](https://www.facebook.com/nasscomOfficial/)
2. **Verify URLs manually**: Visit each page to confirm it's public and relevant
3. **Submit URLs to BrightData**: Send page URLs with `num_of_posts: 25`
4. **Poll for completion**: Check status every 10 seconds until data is ready
5. **Download and normalize**: Parse the response and map fields to our schema

### Technical Details — 3-Step Async Workflow

**Step 1 — Trigger:**
```
POST https://api.brightdata.com/datasets/v3/trigger
  ?dataset_id=gd_lkaxegm826bjpoo9m5&format=json

Body: [{"url": "https://www.facebook.com/INDIAai", "num_of_posts": 25}]

Response: {"snapshot_id": "sd_mluk9mub116fho53g3"}
```

**Step 2 — Poll (every 10s):**
```
GET https://api.brightdata.com/datasets/v3/progress/sd_mluk9mub116fho53g3

Response: {"status": "running"}  →  {"status": "ready"}
```

**Step 3 — Download:**
```
GET https://api.brightdata.com/datasets/v3/snapshot/sd_mluk9mub116fho53g3

Response: [{"post_text": "...", "likes": 200, ...}, ...]
```

### Important Detail: NDJSON Format

BrightData returns **newline-delimited JSON** (one JSON object per line), NOT a standard JSON array. Our code handles both formats.

### Our Results

- Page collected: [IndiaAI Facebook](https://www.facebook.com/INDIAai)
- Collected: **25 Facebook posts**
- Time taken: ~5 minutes (BrightData scraping is asynchronous)

---

## Slide 5: TikTok Collection — Video-Level via BrightData

### The Challenge

TikTok's API is even more restricted than Facebook's. There's no public search API at all.

### Our Solution: BrightData + Google Search for Video URLs

BrightData's **TikTok Posts** dataset scrapes individual videos by URL. It does NOT support profile-level scraping or keyword search — you must provide specific video URLs.

### Method

1. **Search Google for TikTok videos** about our topic:
   - Google: `site:tiktok.com "India AI" OR "artificial intelligence India"`
   - Google: `tiktok.com video India AI technology`
   - Also tried: `tiktok.com/@username/video India AI`
2. **Collect video URLs**: Each must match format `tiktok.com/@user/video/DIGITS`
3. **Submit all video URLs to BrightData** in a single batch
4. **Poll and download** (same async workflow as Facebook)

### Why Video URLs, Not Profile URLs?

BrightData offers two TikTok datasets:
- **Profiles** (`gd_l1villgoiiidt09ci`) — returns account metadata (follower count, bio) — NOT posts
- **Posts** (`gd_lu702nij2f790tmv9h`) — returns full video data (text, likes, shares) — THIS is what we use

We learned this the hard way: the Profiles dataset only returns a single dict of account info, not a list of posts.

### Video URLs We Collected

Found via Google search for India + AI TikTok content:
- `@nala.india` — "AI is actually... Indian?!"
- `@uptin` — "AI Changing Indian Accents"
- `@lexfridman` — Sundar Pichai on growing up in India
- `@nate.b.jones` — Amazon's Checkout AI in India
- `@varun_rana_` — "AI = Amazon India"
- And 5 more videos about AI and India

### Technical Details

```
POST https://api.brightdata.com/datasets/v3/trigger
  ?dataset_id=gd_lu702nij2f790tmv9h&format=json

Body: [
  {"url": "https://www.tiktok.com/@nala.india/video/7509540960238341381"},
  {"url": "https://www.tiktok.com/@uptin/video/7482022226741447958"},
  ...
]
```

**Key constraint**: No `num_of_posts` field allowed. Each URL = one video scraped.

### Our Results

- Videos submitted: **10 video URLs**
- Collected: **10 TikTok posts** with full text, engagement, and metadata
- Time taken: ~90 seconds

---

## Slide 6: Claims Extraction — GPT-4o via OpenRouter

### What Is a "Factual Claim"?

A statement that asserts something is true about the world and can be verified. NOT opinions, questions, or subjective statements.

**Example claim**: "India's AI market is expected to reach $17 billion by 2027"
**NOT a claim**: "I think AI is amazing for everyone!"

### Method

1. **Process posts one at a time** (not batched — more reliable)
2. **Send each post to GPT-4o** with a carefully designed prompt:
   - System prompt defining what a factual claim is
   - 4 few-shot examples showing correct extraction
   - The actual post text to analyze
3. **Parse the structured JSON response** for each claim:
   - `claim_text`: The extracted claim, clearly stated
   - `confidence`: 0.0 to 1.0 — how confident the AI is this IS a factual claim
   - `category`: science, politics, economics, health, technology, society, etc.
   - `reasoning`: Why the AI classified this as a factual claim
   - `source_quote`: The exact text from the post
4. **Classify by confidence threshold**:
   - **≥ 0.85** → `auto_accepted` (high confidence it's a real claim)
   - **0.60 – 0.85** → `needs_review` (human must verify)
   - **< 0.60** → `auto_rejected` (likely not a factual claim)

### Technical Details

```
POST https://openrouter.ai/api/v1/chat/completions

Model: openai/gpt-4o
Temperature: 0.1 (low = more consistent)

Messages: [system_prompt, few_shot_examples..., user_post]
```

### Safety Features

- **Incremental saving**: Claims file is written to disk after EVERY post (crash-safe)
- **Error resilience**: If one post fails, the pipeline continues with the next
- **Exponential backoff**: Retries on rate limits or server errors

### Our Results

- Posts processed: **60** (25 Twitter + 25 Facebook + 10 TikTok)
- Claims extracted: **~70 total**
- Breakdown: ~63 auto-accepted, ~7 needs review, ~0 auto-rejected
- Time taken: ~2 minutes

---

## Slide 7: Human Verification Dashboard

### Why Human Review?

AI confidence scores are a starting point, not the final answer. Claims with 0.60–0.85 confidence need human judgment to determine if they're genuine factual claims or ambiguous statements.

### Dashboard Features

Built with React (Vite) — reads JSON files directly, no backend server needed.

**Three tabs:**
1. **Collect Data** — Generate CLI commands for data collection
2. **Posts** — Browse all collected posts, filter by platform, sort by engagement
3. **Claims Review** — The core verification workflow

**Claims Review tab:**
- Three sub-tabs: "Needs Review" (highlighted), "Auto-Accepted", "Auto-Rejected"
- Each claim shows: text, confidence bar (color-coded), reasoning, source quote
- **Accept/Reject buttons** for claims needing review
- **Reviewer notes** text field for documenting decisions
- **localStorage persistence** — decisions survive page refreshes
- **Export button** — download verified claims as JSON

### Data Flow

```
Python scripts → data/posts.json, data/claims.json
                          ↓
React dashboard reads via fetch()
                          ↓
Human Accept/Reject → localStorage
                          ↓
Export → verified_claims.json
```

---

## Slide 8: What We Learned

### API Realities
- **Twitter**: Best developer experience. Keyword search works out of the box.
- **Facebook**: No public search API. Must know specific page URLs upfront, then use BrightData.
- **TikTok**: Most restrictive. No search, no profile scraping for posts. Must find individual video URLs via Google.

### BrightData Gotchas
- Returns **NDJSON** (newline-delimited JSON), not standard JSON arrays
- TikTok has TWO datasets (Profiles vs Posts) that do very different things
- Asynchronous polling: Facebook took ~5 minutes, TikTok took ~90 seconds

### GPT-4o Claims Extraction
- Very good at distinguishing facts from opinions
- Few-shot examples dramatically improve output quality
- Low temperature (0.1) ensures consistent formatting

### Cost
- Twitter API: included in API key subscription
- BrightData: ~$0.08 for 35 records (25 Facebook + 10 TikTok)
- OpenRouter (GPT-4o): ~$0.15 for 60 posts
- **Total: under $0.25 for the full demo**

---

## Slide 9: Reproducibility — Run It Yourself

### Prerequisites
- Python 3.9+, Node.js 18+
- API keys: twitterapi.io, BrightData, OpenRouter

### Commands

```bash
# 1. Install
pip install -r requirements.txt
cd dashboard && npm install

# 2. Collect (example with India AI Summit topic)
python -m collectors.run_collection \
  --twitter-keywords "India AI Impact Summit" "#AIImpactSummit" \
  --meta-urls "https://www.facebook.com/INDIAai" \
  --tiktok-urls "https://www.tiktok.com/@nala.india/video/7509540960238341381"

# 3. Extract claims
python -m claims.run_extraction

# 4. View dashboard
cd dashboard && npm run dev
```

### Tests
```bash
python -m pytest tests/ -v  # 69 unit tests, all passing
```
