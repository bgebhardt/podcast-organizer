# Podcast Organizer - Quick Start Guide

## 1. Set Up Python Virtual Environment

### Quick Setup (Recommended)

```bash
# Run the setup script
./setup.sh
```

### Manual Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Note:** You need to activate the virtual environment each time you use the tool:
```bash
source venv/bin/activate
```

## 2. Configure API Key

### Option A: Config File
```bash
cp .podcast-organizer.yaml.example .podcast-organizer.yaml
# Edit .podcast-organizer.yaml and add your Anthropic API key
```

### Option B: Environment Variable
```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Get your API key at: https://console.anthropic.com/

## 3. Run Your First Test

```bash
# Test with 5 podcasts (quick)
./podcast-organizer test-mini.opml --verbose
```

This will:
1. Parse the OPML file
2. Fetch RSS metadata for 5 podcasts
3. Use Claude AI to categorize and tag them
4. Generate `podcasts.md` with organized output

## 4. Process Your Own OPML

```bash
# Your podcast subscription file
./podcast-organizer your-podcasts.opml --output my-organized-podcasts.md
```

## Examples

### Start Small
```bash
# 10 podcasts for testing
./podcast-organizer icatcher-Backup-Subscribed.opml --limit 10 --verbose
```

### Without AI (faster, no API cost)
```bash
./podcast-organizer test-sample.opml --no-ai --output basic.md
```

### Full Processing
```bash
# Process all podcasts (costs API tokens)
./podcast-organizer icatcher-Backup-Subscribed.opml --output all-podcasts.md
```

## What You Get

**Input (OPML):**
```xml
<outline type="rss" text="Acquired" xmlUrl="https://feeds.transistor.fm/acquired" />
```

**Output (Markdown):**
```markdown
## Technology & Business

### Acquired
**Link:** https://acquired.fm
**RSS Feed:** https://feeds.transistor.fm/acquired
**Description:** Every company has a story. Learn the playbooks...
**Tags:** #technology #business #podcasts
```

## Troubleshooting

**Error: "externally-managed-environment"**
→ You need to use a virtual environment (see step 1 above)

**Error: "anthropic_api_key not configured"**
→ Create `.podcast-organizer.yaml` or set `ANTHROPIC_API_KEY`

**Forgot to activate venv?**
→ Run `source venv/bin/activate` first

**Want basic output without AI?**
→ Use `--no-ai` flag

**See what's happening?**
→ Use `--verbose` flag

## Next Steps

- Read [USAGE.md](USAGE.md) for all options
- Read [DESIGN.md](DESIGN.md) for architecture details
- Read [TESTING.md](TESTING.md) for testing guide
