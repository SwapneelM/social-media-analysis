# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sample social data collection project — part of the `simppl/dw` workspace. Intended for collecting and processing social media data.

## Development Rules

### Decision Making
- Never make assumptions. Always ask clarifying questions before making decisions.

### Prompt Logging
- Log every raw user prompt to `swapneel_prompts.md` (exclude sensitive details like API keys or passwords).

### Git Discipline
- Git commit after **every single change**.
- Before making any file changes, verify all prior changes are committed.

### Testing
- Write local tests in the `tests/` folder for every function and module.
- Run tests to verify correctness before considering work complete.

### Scratchpad / Task Decomposition
- When decomposing instructions into steps, write them into the `scratchpad/` folder.
- Each scratchpad file should be individually runnable and testable.
- This ensures work can be resumed if interrupted.

### Documentation
- All code must have docstrings with clear explanations of purpose and usage.
- `README.md` must always be kept up to date with: project goals, project data descriptions, code structure, and instructions to run.

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
  src/components/        # React components (InputForm, PostsTable, ClaimsReview, etc.)
data/                    # Output JSON files (posts.json, claims.json)
  raw/                   # Raw API responses (gitignored)
tests/                   # All unit tests (69 tests)
scratchpad/              # Task decomposition notes
swapneel_prompts.md      # Log of raw user prompts
README.md                # Always up-to-date project docs
```

## Key Commands

```bash
# Run all tests
python -m pytest tests/ -v

# Collect data
python -m collectors.run_collection --twitter-keywords "AI" --meta-urls "..." --tiktok-urls "..."

# Extract claims
python -m claims.run_extraction

# Run dashboard
cd dashboard && npm run dev
```
