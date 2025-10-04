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
- **LLM Provider**: Use Claude/Anthropic API
- Batch process podcasts for categorization
- For each podcast:
  - Infer category/theme based on title + description
  - Search for YouTube channel (may require web search or heuristics)
  - Generate/refine description if needed
  - Generate relevant tags
- Output: Categorized podcasts with enhanced metadata

### Output Generator
- Group podcasts by category
- Format as Markdown with consistent structure
- Include RSS links, YouTube links, descriptions, tags

## Key Design Decisions (Requiring Input)

### 1. AI Provider & Approach
**Options:**
- **A) Claude API** (Anthropic) - High quality, good at research tasks
- **B) OpenAI GPT-4** - Widely used, good function calling
- **C) Local LLM** (Ollama) - No API costs, privacy, but slower

**Question:** Which AI provider do you prefer? Do you have API keys for Claude or OpenAI? Budget considerations?

### 2. YouTube Link Discovery
**Options:**
- **A) AI-powered search** - Ask LLM to search/infer YouTube links (may hallucinate)
- **B) Web scraping** - Search Google/YouTube programmatically (complex, rate limits)
- **C) Manual/Optional** - Skip auto-discovery, allow manual addition later
- **D) Hybrid** - Try RSS feed links first, then AI inference

**Question:** How important is YouTube link accuracy? Acceptable to have some missing/incorrect links?

### 3. Category Organization
**Options:**
- **A) AI-inferred categories** - Let Claude analyze all podcasts and create themes
- **B) Predefined categories** - Define categories upfront (Tech, Business, News, etc.)
- **C) Hybrid** - Start with predefined, let AI add new ones as needed

**Question:** Do you have preferred category names/structure, or should the tool auto-generate based on your subscriptions?

### 4. Incremental Processing
**Options:**
- **A) Full rebuild** - Process entire OPML each time
- **B) Incremental updates** - Cache previous results, only process new/changed feeds
- **C) Stateful** - Maintain database/JSON of processed podcasts

**Question:** Will you run this once, occasionally, or regularly? Should it remember previous runs?

### 5. Error Handling for Failed Feeds
**Options:**
- **A) Skip and log** - Continue processing, report failures at end
- **B) Retry logic** - Attempt N retries with backoff
- **C) Partial data** - Include podcast even if RSS fetch fails (use OPML data only)

**Question:** How should the tool handle feeds that fail to fetch (timeouts, 404s, invalid XML)?

### 6. Output Format Details
**Options:**
- **A) Single file** - All categories in one `podcasts.md`
- **B) Multi-file** - One file per category (`ai-podcasts.md`, `business-podcasts.md`)
- **C) Hierarchical** - Folder structure with category folders

**Question:** Preferred output structure for Obsidian? Single file or split by category?

### 7. Configuration
**Options:**
- **A) CLI arguments** - Pass options via command line
- **B) Config file** - YAML/JSON config for settings (API keys, categories, etc.)
- **C) Hybrid** - Config file for defaults, CLI args override

**Question:** Preferred way to configure the tool (API keys, output preferences, etc.)?

## Proposed CLI Interface

```bash
# Basic usage
podcast-organizer input.opml -o output.md

# With options
podcast-organizer input.opml \
  --output podcasts.md \
  --api-key $ANTHROPIC_KEY \
  --categories "AI,Business,News,Entertainment" \
  --skip-youtube \
  --verbose
```

## Development Phases

### Phase 1: Core Pipeline (MVP)
- OPML parsing
- RSS fetching (sequential)
- Basic markdown output (no AI)
- Handle top 10-20 feeds from test file

### Phase 2: Concurrency & Robustness
- Async RSS fetching
- Error handling & retries
- Progress indicators
- Full test file processing

### Phase 3: AI Enrichment
- LLM integration for categorization
- Tag generation
- YouTube link discovery
- Description enhancement

### Phase 4: Polish
- Configuration system
- Better error messages
- Output formatting options
- Documentation

## Testing Strategy

- Use `icatcher-Backup-Subscribed.opml` (189 feeds) as primary test
- Create smaller test files for unit testing (5-10 feeds)
- Test edge cases: invalid feeds, timeouts, malformed XML
- Validate output in Obsidian

## Dependencies (Python)

```
feedparser          # RSS/Atom parsing
httpx               # Async HTTP client
click/typer         # CLI framework
anthropic           # Claude API (or openai for GPT)
python-dotenv       # Environment variables
rich                # Pretty terminal output
```

## Next Steps

Please answer the key questions above so I can:
1. Finalize the technical approach
2. Create the project structure
3. Begin implementation with Phase 1
