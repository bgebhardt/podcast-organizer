# Testing Phase 2

## Setup

1. Copy the example config file:
   ```bash
   cp .podcast-organizer.yaml.example .podcast-organizer.yaml
   ```

2. Edit `.podcast-organizer.yaml` and add your API key:
   ```yaml
   ai:
     provider: claude
     anthropic_api_key: your-actual-key-here
   ```

   Or set environment variable:
   ```bash
   export ANTHROPIC_API_KEY=your-actual-key-here
   ```

## Test Commands

### Phase 1 (No AI) - Should still work
```bash
./podcast-organizer test-sample.opml --no-ai --output test-phase1.md
```

### Phase 2 (AI Enrichment) - Small test
```bash
# Test with 5 podcasts
./podcast-organizer test-mini.opml --verbose --output test-phase2-mini.md

# Test with 10 podcasts
./podcast-organizer test-sample.opml --limit 10 --verbose --output test-phase2.md
```

### Provider Override
```bash
# Use OpenAI instead of Claude (requires OPENAI_API_KEY)
./podcast-organizer test-mini.opml --provider openai --output test-openai.md
```

## Expected Output

Phase 2 output should have:
- Podcasts organized into AI-generated categories
- Tags for each podcast
- Enhanced descriptions (if improved by AI)
- Categories like "Technology & Business", "News & Politics", "Gaming & Entertainment", etc.

## Troubleshooting

### Error: "anthropic_api_key not configured"
- Make sure `.podcast-organizer.yaml` exists with your API key
- Or set `ANTHROPIC_API_KEY` environment variable

### Error: "Unknown AI provider"
- Check that `provider` in config is either `claude` or `openai`

### JSON parsing errors
- The AI prompt might need adjustment
- Try running with `--verbose` to see the response
