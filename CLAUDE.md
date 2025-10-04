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

### Phase 2 - In Progress
- Configuration system (YAML + CLI overrides)
- AI integration (Claude/OpenAI)
- Category generation
- Tag generation
- Description enhancement

### Phase 3 - Future
- Retry logic
- Caching/incremental updates
- YouTube link discovery

## Project Structure

```
podcast-organizer/
├── src/podcast_organizer/
│   ├── __init__.py
│   ├── opml_parser.py       # Parse OPML, extract RSS URLs
│   ├── rss_fetcher.py        # Async RSS metadata fetching
│   ├── markdown_generator.py # Generate markdown output
│   └── cli.py                # Click-based CLI
├── podcast-organizer         # Main executable script
├── requirements.txt          # Python dependencies
├── DESIGN.md                 # Full design document
├── USAGE.md                  # Usage guide
└── test-sample.opml          # Test file with 11 feeds
```

## Common Development Commands

### Running the Tool

```bash
# Basic usage
./podcast-organizer input.opml

# With options
./podcast-organizer input.opml --output podcasts.md --verbose

# Limit for testing
./podcast-organizer icatcher-Backup-Subscribed.opml --limit 20

# Dry run
./podcast-organizer input.opml --dry-run
```

### Testing

```bash
# Small test (11 feeds)
./podcast-organizer test-sample.opml --verbose

# Medium test (15 feeds from full OPML)
./podcast-organizer icatcher-Backup-Subscribed.opml --limit 15

# Full OPML (189 feeds)
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
- Phase 1: Basic output without AI categorization
- Separates successful vs failed fetches
- Phase 2 will add AI-generated categories and tags

### CLI ([src/podcast_organizer/cli.py](src/podcast_organizer/cli.py))
- Click-based command-line interface
- Options: --output, --limit, --timeout, --max-concurrent, --verbose, --dry-run
- Rich console output with colored text and progress indicators
