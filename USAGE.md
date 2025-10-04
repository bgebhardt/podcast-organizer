# Podcast Organizer - Usage Guide

## Phase 1 (MVP) - Current Implementation

Phase 1 provides OPML parsing, RSS metadata fetching, and basic markdown output (without AI enrichment).

### Installation

```bash
# Install dependencies
pip3 install -r requirements.txt
```

### Basic Usage

```bash
# Process an OPML file
./podcast-organizer input.opml

# Specify output file
./podcast-organizer input.opml --output my-podcasts.md

# Limit number of podcasts (for testing)
./podcast-organizer input.opml --limit 20

# Verbose output with progress
./podcast-organizer input.opml --verbose

# Dry run (parse and fetch, but don't write output)
./podcast-organizer input.opml --dry-run
```

### Advanced Options

```bash
# Custom timeout (default: 30 seconds)
./podcast-organizer input.opml --timeout 60

# Max concurrent fetches (default: 10)
./podcast-organizer input.opml --max-concurrent 20

# Combine options
./podcast-organizer icatcher-Backup-Subscribed.opml \
  --output podcasts.md \
  --timeout 45 \
  --max-concurrent 15 \
  --verbose
```

### Testing

Two test files are provided:

1. **test-sample.opml** - Small test file with 11 feeds (10 valid, 1 invalid)
   ```bash
   ./podcast-organizer test-sample.opml --output test-output.md --verbose
   ```

2. **icatcher-Backup-Subscribed.opml** - Full OPML with 189 feeds
   ```bash
   # Test with subset
   ./podcast-organizer icatcher-Backup-Subscribed.opml --limit 20

   # Process all feeds
   ./podcast-organizer icatcher-Backup-Subscribed.opml --output all-podcasts.md
   ```

### Current Output Format

Phase 1 generates a markdown file with:
- Summary statistics (total, successful, failed)
- Successfully fetched podcasts with:
  - Title
  - Website link
  - RSS feed URL
  - Description
  - Image URL
- Failed podcasts section with error messages

### What's Next

**Phase 2** will add:
- Configuration file support (`.podcast-organizer.yaml`)
- AI-powered categorization (Claude/OpenAI)
- Tag generation
- Description enhancement
- Full error handling

**Phase 3** will add:
- Retry logic
- Caching/incremental updates
- YouTube link discovery
- Better error reporting
