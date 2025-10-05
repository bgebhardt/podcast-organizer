# Podcast Organizer - Design Document

## Overview

A command-line tool that transforms OPML podcast subscription files into organized, enriched Markdown files suitable for Obsidian. The tool extracts RSS feeds, fetches metadata, and uses AI to categorize and enhance podcast information.

## Recommended Technology Stack

**Python** - Best choice because:
- Excellent XML parsing libraries (`xml.etree.ElementTree`, `feedparser`)
- Rich ecosystem for HTTP requests (`requests`, `httpx`)
- Native async support for concurrent RSS fetching
- Simple CLI framework options (`click`, `typer`)
- Easy AI/LLM integration (Anthropic, OpenAI SDKs)
- Rapid prototyping and iteration

## Architecture

### Three-Stage Pipeline

```
OPML File → Stage 1: Parse → Stage 2: Fetch RSS → Stage 3: AI Enrichment → Markdown Output
```

### Stage 1: OPML Parser
- Extract `<outline>` entries with `type="rss"`
- Parse: `text`, `title`, `xmlUrl` attributes
- URL decode podcast names (e.g., `How%20I%20AI` → `How I AI`)
- Output: List of podcast entries with RSS URLs

### Stage 2: RSS Metadata Fetcher
- Concurrent fetching of RSS feeds (use `asyncio` + `httpx`)
- Parse `<channel>` section from each feed
- Extract metadata:
  - `<title>`
  - `<link>`
  - `<description>` or `<itunes:summary>`
  - `<image><url>` or `<itunes:image href="...">`
- Handle errors gracefully (timeouts, invalid feeds, 404s)
- Output: Enriched podcast data with metadata

### Stage 3: AI Enrichment
- **LLM Provider**: Configurable (Claude or OpenAI), defaults to Claude
- **Two-pass approach for improved accuracy:**
  - **Pass 1: Tag Generation** - Generate 3-5 relevant tags per podcast based on title + description
  - **Pass 2: Categorization** - Group podcasts into categories using title + description + tags (tags provide semantic signals for better accuracy)
- Output: Categorized podcasts with enhanced metadata (tags and categories)

### Output Generator
- Group podcasts by category
- Format as single Markdown file with consistent structure
- Include RSS links, descriptions, tags
- Note: YouTube links deferred to future version

## Design Decisions

### 1. AI Provider & Approach
**Options:**
- **A) Claude API** (Anthropic) - High quality, good at research tasks
- **B) OpenAI GPT-4** - Widely used, good function calling
- **C) Local LLM** (Ollama) - No API costs, privacy, but slower

**Decision:** Configurable support for both Claude (Anthropic) and OpenAI
- Primary usage: Claude API
- Configuration option to switch between providers
- API keys stored in config file

### 2. YouTube Link Discovery
**Options:**
- **A) AI-powered search** - Ask LLM to search/infer YouTube links (may hallucinate)
- **B) Web scraping** - Search Google/YouTube programmatically (complex, rate limits)
- **C) Manual/Optional** - Skip auto-discovery, allow manual addition later
- **D) Hybrid** - Try RSS feed links first, then AI inference

**Decision:** Deferred to future version
- V1: Skip YouTube link discovery
- Future enhancement: Add AI-powered or manual link discovery

### 3. Category Organization
**Options:**
- **A) AI-inferred categories** - Let Claude analyze all podcasts and create themes
- **B) Predefined categories** - Define categories upfront (Tech, Business, News, etc.)
- **C) Hybrid** - Start with predefined, let AI add new ones as needed

**Decision:** AI-inferred categories
- Let the LLM analyze all podcasts and automatically create themes
- No predefined category list
- Categories emerge from the podcast collection

### 4. Incremental Processing
**Options:**
- **A) Full rebuild** - Process entire OPML each time
- **B) Incremental updates** - Cache previous results, only process new/changed feeds
- **C) Stateful** - Maintain database/JSON of processed podcasts

**Decision:** Run occasionally without caching (V1)
- Full rebuild each run for V1 simplicity
- Future enhancement: Add caching/incremental updates for better performance

### 5. Error Handling for Failed Feeds
**Options:**
- **A) Skip and log** - Continue processing, report failures at end
- **B) Retry logic** - Attempt N retries with backoff
- **C) Partial data** - Include podcast even if RSS fetch fails (use OPML data only)

**Decision:** Skip and warn (V1), retry logic (future)
- V1: Skip failed feeds, print warning messages
- Future: Add retry logic with exponential backoff
- Future: Include partial data from OPML when RSS fails

### 6. Output Format Details
**Options:**
- **A) Single file** - All categories in one `podcasts.md`
- **B) Multi-file** - One file per category (`ai-podcasts.md`, `business-podcasts.md`)
- **C) Hierarchical** - Folder structure with category folders

**Decision:** Single file output
- All categories in one `podcasts.md` file
- Organized by category sections within the file

### 7. Configuration
**Options:**
- **A) CLI arguments** - Pass options via command line
- **B) Config file** - YAML/JSON config for settings (API keys, categories, etc.)
- **C) Hybrid** - Config file for defaults, CLI args override

**Decision:** Hybrid approach - Config file with CLI overrides
- Config file (`.podcast-organizer.yaml` or similar) for:
  - API keys and provider selection
  - Default output file path
  - Timeout settings
  - Model selection (future)
- CLI arguments override for:
  - Input OPML file (required positional argument)
  - Output file path (`--output`)
  - AI provider (`--provider`)
  - Verbose mode (`--verbose`)
  - Dry run (`--dry-run`)

## CLI Interface

```bash
# Basic usage (uses config file for settings)
podcast-organizer input.opml

# Specify output file
podcast-organizer input.opml --output podcasts.md

# Override AI provider
podcast-organizer input.opml --provider openai

# Verbose output
podcast-organizer input.opml --verbose

# Dry run (parse and fetch but don't call AI or write output)
podcast-organizer input.opml --dry-run
```

## Development Phases

### Phase 1: Core Pipeline (MVP)
- OPML parsing
- RSS fetching (sequential first, then async)
- Basic markdown output (no AI)
- Handle top 10-20 feeds from test file

### Phase 2: AI Enrichment (V1 Complete)
- Configuration system (YAML config file + CLI args)
- LLM integration for categorization (Claude + OpenAI support)
- Tag generation
- Description enhancement
- Full test file processing
- Progress indicators
- Error handling (skip failed feeds with warnings)

### Phase 2.1: Logging and Timing - ✅ Complete
- Centralized logging system ([logger.py](src/podcast_organizer/logger.py)) with colored output levels:
  - `info()` - cyan messages for informational output
  - `success()` - green messages with checkmarks
  - `warning()` - yellow messages
  - `error()` - red error messages
  - `verbose_info()` - conditional verbose output
- All modules updated to use logger instead of direct console.print()
- Execution timing: Script now measures and reports total elapsed time at completion
- Maintains existing color scheme while providing structured logging

### Phase 3: Polish & Future Enhancements
- Retry logic with exponential backoff
- Caching/incremental updates
- YouTube link discovery
- Better error messages
- Partial data inclusion for failed feeds
- Documentation
- Deal with authenticated podcast feeds

## Testing Strategy

- Use `icatcher-Backup-Subscribed.opml` (189 feeds) as primary test
- Create smaller test files for unit testing (5-10 feeds)
- Test edge cases: invalid feeds, timeouts, malformed XML
- Validate output in Obsidian

## Dependencies (Python)

```
feedparser          # RSS/Atom parsing
httpx               # Async HTTP client
click               # CLI framework
anthropic           # Claude API
openai              # OpenAI API
pyyaml              # YAML config parsing
rich                # Pretty terminal output
```

## Configuration File Format

`.podcast-organizer.yaml`:
```yaml
# AI Provider Configuration
ai:
  provider: claude  # Options: claude, openai
  anthropic_api_key: sk-ant-...
  openai_api_key: sk-...
  model: claude-3-5-sonnet-20241022  # Optional, use provider defaults

# Output Configuration
output:
  default_file: podcasts.md

# Fetching Configuration
fetching:
  timeout: 30  # Seconds
  max_concurrent: 10  # Max concurrent RSS fetches
```
