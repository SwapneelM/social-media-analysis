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
tests/          # All local tests
scratchpad/     # Task decomposition notes and runnable scratch files
swapneel_prompts.md  # Log of raw user prompts
README.md       # Always up-to-date project docs
```
