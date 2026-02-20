# Swapneel Prompts

## Prompt 1 — 2026-02-19
relevant instructions for claude.md

1. Never make assumptions, always ask questions to clarify decisions
2. Document all the raw prompts I input in a file called swapneel_prompts.md where you store the instructions (except any sensitive details).
3. Ensure you always git commit after every single change you make (and check changes are committed before you make any file changes just to be sure).
4. Always write local tests in a folder called tests in order to ensure you document tests and run them to verify every single function and module you develop works as intended.
5. As you decompose an instruction into steps of actions to take, can you ensure you write these down so that it is easy to pick up where you leave off. Always write these files into a folder called `scratchpad` so that it is accessible, individually possible to run and test functionality.
6. For all code, always write docstrings, document it accurately and with a clean explanation of the use for the code as relevant. Add the code structure and any instructions needed for data or to run it in the README.md file that must always be up to date with the project goals, project data, and instructions to run it.

## Prompt 2 — 2026-02-19
Implement the full Social Media Analysis Dashboard plan:
- Build Python scripts to collect 25 posts each from Twitter/X (twitterapi.io), Facebook/Meta (BrightData), and TikTok (BrightData)
- Extract factual claims using GPT-4o via OpenRouter
- Present results in a React (Vite) dashboard with human verification
- Architecture: No backend server, Python scripts write static JSON, React reads them
- Key constraints: atomic file saves, exponential backoff on API calls, API keys never committed
- 16-step implementation sequence from Phase 0 (setup) through Phase 4 (React dashboard)
- Each step includes scratchpad decomposition, tests, docstrings, and git commit

## Prompt 3 — 2026-02-19
Research how BrightData's API works for collecting social media data from Facebook and TikTok. Specifically:
1. Can you collect data from Facebook pages/groups and TikTok accounts using just the page/account URL + the BrightData API key? Or do you necessarily need a "dataset ID"?
2. How does the BrightData dataset API work — do you create/purchase a dataset first in the control panel, then trigger collection via API?
3. Does BrightData offer any free tier, demo data, or trial access for testing?
4. What are the minimum steps to collect Facebook posts from a public page URL and TikTok posts from a public account URL via BrightData?
Search the BrightData documentation and API reference to find accurate answers.

User chose: Use live BrightData API (~$0.08) with hardcoded public dataset IDs, find real Facebook/TikTok page URLs.

## Prompt 4 — 2026-02-20
Search for real Facebook page and TikTok account URLs related to "India AI Impact Summit" topic. Find functional URLs that can be used with the BrightData API for data collection. Add them to the README as clickable links for documentation.

## Prompt 5 — 2026-02-20
Run the full pipeline locally: collect data from Twitter, Facebook, and TikTok using the sample URLs, extract claims with GPT-4o, and start the React dashboard to view results.

## Prompt 6 — 2026-02-20
User called out that tests for Meta and TikTok were mocked and did not verify real API integration. Demanded honest assessment of what's working and what isn't. Asked for:
1. Fix TikTok collection (profiles dataset returns metadata not posts, need video URLs)
2. Verify data is relevant to keywords not random
3. Detailed methodology explanation in explanations_for_slides.md for Gamma.app slides
4. Clear walkthrough of: Twitter keyword search, Google URL search for Facebook/TikTok, BrightData collection process

## Prompt 7 — 2026-02-20
Find 5-10 specific TikTok VIDEO URLs (format: tiktok.com/@username/video/NUMBERS) related to India AI, artificial intelligence India, AI Impact Summit India, or Indian tech. These are needed for the BrightData TikTok Posts dataset (gd_lu702nij2f790tmv9h) which requires individual video URLs, not profile URLs.
