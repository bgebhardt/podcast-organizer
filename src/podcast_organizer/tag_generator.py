"""Tag generation utilities for podcasts."""

import re
from typing import List, Set


# Common podcast-related stop words to exclude from tags
STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'with', 'from', 'to', 'of', 'in', 'on',
    'for', 'is', 'at', 'by', 'as', 'podcast', 'podcasts', 'show', 'episode', 'episodes'
}


def generate_tags_from_category(category: str, max_tags: int = 3) -> List[str]:
    """
    Generate tags from a category name.

    Args:
        category: Category name (e.g., "Technology & AI")
        max_tags: Maximum number of tags to generate

    Returns:
        List of tags (e.g., ["technology", "ai"])
    """
    if not category:
        return []

    # Split on common separators
    words = re.split(r'[&/,\s]+', category.lower())

    # Filter out stop words, but keep short words if they're uppercase (acronyms like AI)
    tags = []
    for word in words:
        word = word.strip()
        if not word:
            continue

        # Keep if:
        # - Length > 2 and not a stop word
        # - OR length == 2 and all uppercase in original (AI, ML, etc.)
        if (len(word) > 2 and word not in STOP_WORDS) or (len(word) == 2):
            tags.append(word)

    # Remove duplicates while preserving order
    seen = set()
    unique_tags = []
    for tag in tags:
        if tag not in seen:
            seen.add(tag)
            unique_tags.append(tag)

    return unique_tags[:max_tags]


def extract_keywords_from_title(title: str, max_keywords: int = 2) -> List[str]:
    """
    Extract potential keywords from a podcast title.

    Args:
        title: Podcast title
        max_keywords: Maximum number of keywords to extract

    Returns:
        List of keyword tags
    """
    if not title:
        return []

    # Remove common patterns
    title = re.sub(r'\bpodcast\b', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\bthe\b', '', title, flags=re.IGNORECASE)

    # Split into words
    words = re.findall(r'\b[a-zA-Z]{3,}\b', title.lower())

    # Filter stop words
    keywords = [
        word
        for word in words
        if word not in STOP_WORDS
    ]

    # Remove duplicates while preserving order
    seen = set()
    unique_keywords = []
    for keyword in keywords:
        if keyword not in seen:
            seen.add(keyword)
            unique_keywords.append(keyword)

    return unique_keywords[:max_keywords]


def generate_tags_for_podcast(
    category: str,
    title: str,
    max_total_tags: int = 5
) -> List[str]:
    """
    Generate tags for a podcast using category and title.

    Args:
        category: Podcast category
        title: Podcast title
        max_total_tags: Maximum total tags to generate

    Returns:
        List of tags combining category-based and title-based tags
    """
    all_tags = []

    # Start with category tags (priority)
    category_tags = generate_tags_from_category(category)
    all_tags.extend(category_tags)

    # Add title keywords if we have room
    remaining = max_total_tags - len(all_tags)
    if remaining > 0:
        title_keywords = extract_keywords_from_title(title, max_keywords=remaining)

        # Only add keywords that aren't already covered by category tags
        for keyword in title_keywords:
            if keyword not in all_tags:
                all_tags.append(keyword)
                if len(all_tags) >= max_total_tags:
                    break

    return all_tags


def normalize_tag(tag: str) -> str:
    """
    Normalize a tag by replacing spaces with dashes.

    Args:
        tag: Raw tag string (may contain spaces)

    Returns:
        Normalized tag with dashes instead of spaces
    """
    return tag.lower().strip().replace(' ', '-')


def deduplicate_tags(tags: List[str]) -> List[str]:
    """
    Remove duplicate tags while preserving order, and normalize them.

    Args:
        tags: List of tags (may contain duplicates or spaces)

    Returns:
        List of unique, normalized tags (with dashes instead of spaces)
    """
    seen = set()
    unique = []
    for tag in tags:
        tag_normalized = normalize_tag(tag)
        if tag_normalized and tag_normalized not in seen:
            seen.add(tag_normalized)
            unique.append(tag_normalized)
    return unique
