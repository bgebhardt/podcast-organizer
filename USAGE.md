# Podcast Organizer - Usage Guide

## Current Implementation Status

- ✅ **Phase 1 (MVP)**: OPML parsing, RSS fetching, basic markdown output
- ✅ **Phase 2 (AI)**: Configuration system, AI-powered categorization, tag generation
- 🔄 **Phase 3 (Future)**: Retry logic, caching, YouTube link discovery

## Installation

### 1. Set Up Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Important:** Activate the virtual environment each time you use the tool:
```bash
source venv/bin/activate
```

### 2. Alternative: System-wide Install (Not Recommended)

If you prefer not to use a virtual environment:
```bash
pip3 install --user -r requirements.txt
```

## Configuration

### Option 1: Config File (Recommended)

```bash
# Copy example config
cp .podcast-organizer.yaml.example .podcast-organizer.yaml

# Edit and add your API key
vi .podcast-organizer.yaml
```

Example `.podcast-organizer.yaml`:
```yaml
ai:
  provider: claude  # or openai
  anthropic_api_key: sk-ant-your-key-here

output:
  default_file: podcasts.md

fetching:
  timeout: 30
  max_concurrent: 10
```

### Option 2: Environment Variables

```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here
# or
export OPENAI_API_KEY=sk-your-key-here
```

## Basic Usage

### Phase 2: AI-Enriched Output (Default)

```bash
# Process with AI categorization and tags
./podcast-organizer input.opml

# Specify output file
./podcast-organizer input.opml --output my-podcasts.md

# Verbose output
./podcast-organizer input.opml --verbose

# Limit for testing
./podcast-organizer input.opml --limit 10 --verbose
```

### Phase 1: Basic Output (No AI)

```bash
# Skip AI enrichment
./podcast-organizer input.opml --no-ai

# Useful when you don't have API keys or want quick output
./podcast-organizer input.opml --no-ai --output basic.md
```

## Advanced Options

```bash
# Override AI provider
./podcast-organizer input.opml --provider openai

# Custom timeout (overrides config)
./podcast-organizer input.opml --timeout 60

# Max concurrent fetches (overrides config)
./podcast-organizer input.opml --max-concurrent 20

# Dry run (parse and fetch, but don't write output or call AI)
./podcast-organizer input.opml --dry-run

# Combine options
./podcast-organizer icatcher-Backup-Subscribed.opml \
  --output podcasts.md \
  --timeout 45 \
  --max-concurrent 15 \
  --verbose
```

## Test Files

Three test files are provided:

1. **test-mini.opml** - Tiny test (5 feeds) for quick AI testing
   ```bash
   ./podcast-organizer test-mini.opml --verbose
   ```

2. **test-sample.opml** - Small test (11 feeds, 1 invalid)
   ```bash
   ./podcast-organizer test-sample.opml --verbose
   ```

3. **icatcher-Backup-Subscribed.opml** - Full OPML (189 feeds)
   ```bash
   # Test with subset
   ./podcast-organizer icatcher-Backup-Subscribed.opml --limit 20 --verbose

   # Process all feeds (costs more API tokens)
   ./podcast-organizer icatcher-Backup-Subscribed.opml --output all-podcasts.md
   ```

## Output Formats

### Phase 2 (AI-Enriched) Output

Organized by AI-generated categories:

```markdown
# My Podcasts

Total podcasts: 10
Successfully fetched: 10
Failed: 0

## Technology & Business

### Acquired
**Link:** https://acquired.fm
**RSS Feed:** https://feeds.transistor.fm/acquired
**Description:** Every company has a story. Learn the playbooks...
**Tags:** #technology #business #podcasts
**Image:** https://...

### All-In with Chamath, Jason, Sacks & Friedberg
...

## News & Politics

### Code Switch
...

## Gaming & Entertainment

### 3 Wise DMs
...
```

### Phase 1 (Basic) Output

Simple list without categories:

```markdown
# My Podcasts

Total podcasts: 10
Successfully fetched: 10
Failed: 0

## Podcasts

### Acquired
**Link:** https://acquired.fm
**RSS Feed:** https://feeds.transistor.fm/acquired
**Description:** Every company has a story...
**Image:** https://...

### 3 Wise DMs
...
```

## What's Next

**Phase 3** will add:
- Retry logic with exponential backoff
- Caching/incremental updates
- YouTube link discovery
- Better error reporting
- Partial data inclusion for failed feeds

## Troubleshooting

### "anthropic_api_key not configured"
Create `.podcast-organizer.yaml` or set `ANTHROPIC_API_KEY` environment variable.

### "Unknown AI provider"
Check that `provider` in config is `claude` or `openai`.

### Want to skip AI temporarily?
Use `--no-ai` flag for Phase 1 output.
