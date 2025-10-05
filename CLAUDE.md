# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A tool to parse OPML files from podcast apps (like iCatcher) and generate organized markdown files with enriched podcast metadata. The output is designed for Obsidian and includes categorization, descriptions, YouTube links, and tags.

## Project Goals

The tool processes podcasts in three steps:

1. **Parse OPML file** - Extract RSS feed URLs from `<outline>` entries with `type="rss"`, `text`, `title`, and `xmlUrl` attributes
2. **Fetch RSS metadata** - Retrieve each RSS feed and parse the `<channel>` section to extract:
   - `<title>`
   - `<link>`
   - `<description>` (or `<itunes:summary>`)
   - `<image><url>` (or `<itunes:image href>`)
3. **AI enrichment** - Use AI to:
   - Categorize podcasts by major themes
   - Find YouTube channel links for each podcast
   - Generate/refine descriptions
   - Add relevant tags

## Expected Output Format

Markdown file organized by category with entries like:

```markdown
# AI Podcasts

Title: How I AI
Link: [rss](https://anchor.fm/s/1035b1568/podcast/rss)
YouTube Link: [How I AI - YouTube](https://www.youtube.com/@howiaipodcast)
Description: How I AI, hosted by Claire Vo, is for anyone wondering how to actually use these magical new tools...

Tags: #ai #productmanagement

# Retirement Podcasts

...
```

## Input Format

OPML entries look like:
```xml
<outline type="rss" text="How%20I%20AI" title="How%20I%20AI" xmlUrl="https://anchor.fm/s/1035b1568/podcast/rss" />
```

RSS feeds contain a `<channel>` section with podcast metadata using both standard RSS and iTunes namespace tags (`itunes:*`).

## Current Implementation Status

### Phase 1 (MVP) - ✅ Complete
- OPML parsing with URL decoding
- Async RSS metadata fetching
- Basic markdown output (no AI)
- Error handling for failed feeds
- CLI with verbose and dry-run modes

### Phase 2 (AI Enrichment) - ✅ Complete
- Configuration system (YAML + CLI overrides)
- AI integration (Claude/OpenAI)
- AI-generated category organization
- Tag generation (3-5 tags per podcast)
- Description enhancement
- `--no-ai` flag to use Phase 1 mode
- `--provider` flag to switch between Claude/OpenAI

### Phase 3 - Future
- Retry logic with exponential backoff
- Caching/incremental updates
- YouTube link discovery
- Partial data inclusion for failed feeds

## Project Structure

```
podcast-organizer/
├── src/podcast_organizer/
│   ├── __init__.py
│   ├── opml_parser.py         # Parse OPML, extract RSS URLs
│   ├── rss_fetcher.py          # Async RSS metadata fetching (with AI fields)
│   ├── markdown_generator.py   # Generate markdown (basic + enriched)
│   ├── config.py               # Configuration loading (YAML + env vars)
│   ├── ai_enricher.py          # AI providers (Claude/OpenAI)
│   └── cli.py                  # Click-based CLI
├── podcast-organizer           # Main executable script
├── requirements.txt            # Python dependencies
├── .podcast-organizer.yaml.example  # Config template
├── DESIGN.md                   # Full design document
├── USAGE.md                    # Usage guide
├── TESTING.md                  # Phase 2 testing guide
├── test-mini.opml              # Tiny test (5 feeds)
├── test-sample.opml            # Small test (11 feeds)
└── icatcher-Backup-Subscribed.opml  # Full OPML (189 feeds)
```

## Common Development Commands

### Setup

```bash
# Quick setup (creates venv, installs deps)
./setup.sh

# Then activate venv (needed each session)
source venv/bin/activate

# Configure API key
cp .podcast-organizer.yaml.example .podcast-organizer.yaml
# Edit to add API key

# Or use environment variable
export ANTHROPIC_API_KEY=sk-ant-your-key
```

### Running the Tool

```bash
# Phase 2 (AI-enriched, default)
./podcast-organizer input.opml
./podcast-organizer input.opml --verbose
./podcast-organizer input.opml --provider openai

# Phase 1 (basic, no AI)
./podcast-organizer input.opml --no-ai

# With options
./podcast-organizer input.opml --output podcasts.md --limit 20 --verbose

# Dry run (no output, no AI calls)
./podcast-organizer input.opml --dry-run
```

### Testing

```bash
# Tiny test for AI (5 feeds)
./podcast-organizer test-mini.opml --verbose

# Small test (11 feeds)
./podcast-organizer test-sample.opml --verbose

# Without AI (Phase 1)
./podcast-organizer test-sample.opml --no-ai --output test-basic.md

# Medium test (20 feeds from full OPML)
./podcast-organizer icatcher-Backup-Subscribed.opml --limit 20 --verbose

# Full OPML (189 feeds - uses more API tokens)
./podcast-organizer icatcher-Backup-Subscribed.opml --output all-podcasts.md
```

## Key Design Decisions

- **Language**: Python (feedparser, httpx, click, anthropic/openai)
- **AI Provider**: Configurable (Claude default, OpenAI option)
- **Categories**: AI-inferred (no predefined list)
- **Output**: Single markdown file
- **Config**: YAML file + CLI overrides
- **Concurrency**: Async RSS fetching (default: 10 concurrent)

## Implementation Notes

### OPML Parser ([src/podcast_organizer/opml_parser.py](src/podcast_organizer/opml_parser.py))
- Uses `xml.etree.ElementTree` for parsing
- Finds `<outline type="rss">` elements
- URL-decodes podcast names (e.g., `How%20I%20AI` → `How I AI`)
- Returns `PodcastEntry` dataclass with text, title, xml_url

### RSS Fetcher ([src/podcast_organizer/rss_fetcher.py](src/podcast_organizer/rss_fetcher.py))
- Async fetching with `httpx` and `asyncio`
- Uses `feedparser` to parse RSS/Atom feeds
- Extracts: title, link, description, image URL
- Handles errors gracefully (timeout, HTTP errors, parse errors)
- Returns `PodcastMetadata` dataclass with fetch status

### Markdown Generator ([src/podcast_organizer/markdown_generator.py](src/podcast_organizer/markdown_generator.py))
- `generate_basic_markdown()`: Phase 1 output without categories
- `generate_enriched_markdown()`: Phase 2 output with AI-generated categories, tags
- Organizes podcasts by category, includes tags and enhanced descriptions
- Separates successful vs failed fetches

### Configuration ([src/podcast_organizer/config.py](src/podcast_organizer/config.py))
- Loads `.podcast-organizer.yaml` from current dir or home dir
- Environment variable support for API keys
- CLI arguments override config values
- Validates AI provider and API key availability

### AI Enricher ([src/podcast_organizer/ai_enricher.py](src/podcast_organizer/ai_enricher.py))
- Abstract `AIProvider` interface with Claude and OpenAI implementations
- Sends all podcasts to AI in single request for categorization
- Parses structured JSON response with categories, tags, enhanced descriptions
- `ClaudeProvider`: Uses Anthropic SDK with claude-3-5-sonnet-20241022
- `OpenAIProvider`: Uses OpenAI SDK with gpt-4-turbo-preview

### CLI ([src/podcast_organizer/cli.py](src/podcast_organizer/cli.py))
- Click-based command-line interface
- Loads config, applies CLI overrides, validates before AI calls
- Options: --output, --limit, --timeout, --max-concurrent, --provider, --no-ai, --verbose, --dry-run
- Rich console output with colored text and progress indicators
- Shows phase (Phase 1 vs Phase 2) and AI provider in header
