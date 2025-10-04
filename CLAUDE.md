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
