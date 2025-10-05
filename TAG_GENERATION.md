# Tag Generation Strategy

## Problem

When processing large podcast collections (100+ podcasts), AI models have output limitations and may only generate detailed tags for a subset of podcasts, even though categorization works well for all podcasts.

## Solution: True Two-Pass AI Approach

### Pass 1: AI Categorization (Works Great at Scale)
- AI analyzes all podcasts and assigns them to logical categories
- Simplified prompt focuses only on categorization
- Reliable for 100+ podcasts
- Example categories: "Technology & AI", "Business & Entrepreneurship", "News & Politics"

### Pass 2: AI Tag Generation in Batches (With Fallback)
- **Primary**: AI generates 3-5 contextual tags per podcast
- Processes in batches of 25 podcasts for reliability
- Each batch gets category context + podcast title + description excerpt
- **Fallback**: Auto-generated tags from category + title if AI batch fails
  1. **Category names**: "Technology & AI" → `#technology #ai`
  2. **Podcast titles**: "Acquired" → `#acquired`
- Filters common stop words (the, a, and, podcast, etc.)
- Handles acronyms (AI, ML, D&D, etc.)

## Benefits

✅ **AI-Powered**: Real AI-generated tags for most podcasts (not just inferred)
✅ **Reliable**: Batching ensures high success rate for large collections
✅ **Fallback Safety**: Auto-tags ensure 100% coverage if AI fails
✅ **Contextual**: AI considers category, title, and description for better tags
✅ **Scalable**: Batches of 25 handle collections of any size

## Examples

### Example 1: Technology Podcast
- **Category**: "Technology & AI"
- **Title**: "Acquired"
- **Generated Tags**: `#technology #ai #acquired`

### Example 2: Business Podcast
- **Category**: "Business & Entrepreneurship"
- **Title**: "All-In with Chamath, Jason, Sacks & Friedberg"
- **Generated Tags**: `#business #entrepreneurship #all #chamath #jason`

### Example 3: Gaming Podcast
- **Category**: "Gaming & Entertainment"
- **Title**: "3 Wise DMs"
- **Generated Tags**: `#gaming #entertainment #wise #dms`

## Technical Implementation

### New Module: `tag_generator.py`

```python
generate_tags_for_podcast(category, title, max_total_tags=5)
```

**Process:**
1. Extract words from category (split on &, /, commas, spaces)
2. Filter stop words but keep 2-letter acronyms
3. Extract keywords from title
4. Combine category tags (priority) + title keywords
5. Deduplicate and limit to max_total_tags

### Updated AI Prompts

**Before (Complex):**
```
Generate categories, tags, and descriptions for each podcast...
[Often incomplete for large collections]
```

**After (Simplified):**
```
Categorize all podcasts into logical groups.
Return only: { "categories": { "Category Name": [podcast_ids] } }
[Reliable for 100+ podcasts]
```

## Configuration

No configuration needed! The hybrid approach is automatic:
- AI handles categorization
- System auto-generates tags

## Testing

```bash
# Test with 5 podcasts
./podcast-organizer test-mini.opml --verbose

# Test with 182 podcasts
./podcast-organizer icatcher-Backup-Subscribed.opml --verbose
```

You should see:
```
✓ Created 15 categories
✓ Auto-generated tags for all 182 podcasts
```

## Future Enhancements

Potential improvements for future versions:

1. **AI-enhanced tags**: Optionally enhance tags with AI for specific podcasts
2. **Custom tag rules**: User-defined tag generation patterns
3. **Tag synonyms**: Map similar concepts (tech → technology)
4. **Multi-word tags**: Support tags like "artificial-intelligence"
