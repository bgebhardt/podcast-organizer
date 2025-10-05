"""Markdown output generator for podcast metadata."""

from typing import List, Dict, Tuple
from collections import defaultdict
from .rss_fetcher import PodcastMetadata


def is_feed_no_longer_exists(error_msg: str) -> bool:
    """
    Determine if an error indicates the feed no longer exists.

    Args:
        error_msg: Error message from fetch_error

    Returns:
        True if feed no longer exists (404, DNS failure, etc.)
    """
    if not error_msg:
        return False

    error_lower = error_msg.lower()

    # HTTP 404
    if "404" in error_msg:
        return True

    # DNS resolution failures
    if "nodename nor servname" in error_lower:
        return True
    if "name or service not known" in error_lower:
        return True
    if "failed to resolve" in error_lower:
        return True

    # Connection refused / host unreachable
    if "connection refused" in error_lower:
        return True

    return False


def categorize_failed_feeds(failed: List[PodcastMetadata]) -> Tuple[List[PodcastMetadata], List[PodcastMetadata]]:
    """
    Categorize failed feeds into two groups.

    Args:
        failed: List of failed PodcastMetadata objects

    Returns:
        Tuple of (no_longer_exists, parsing_errors)
    """
    no_longer_exists = []
    parsing_errors = []

    for podcast in failed:
        if is_feed_no_longer_exists(podcast.fetch_error or ""):
            no_longer_exists.append(podcast)
        else:
            parsing_errors.append(podcast)

    return no_longer_exists, parsing_errors


def generate_basic_markdown(podcasts: List[PodcastMetadata]) -> str:
    """
    Generate a basic markdown file from podcast metadata (Phase 1 - no AI).

    Args:
        podcasts: List of PodcastMetadata objects

    Returns:
        Formatted markdown string
    """
    lines = []

    # Header
    lines.append("# My Podcasts\n")
    lines.append(f"Total podcasts: {len(podcasts)}\n")
    lines.append(f"Successfully fetched: {sum(1 for p in podcasts if p.has_metadata)}\n")
    lines.append(f"Failed: {sum(1 for p in podcasts if not p.has_metadata)}\n")
    lines.append("")

    # Group podcasts: successful first, then failed
    successful = [p for p in podcasts if p.has_metadata]
    failed = [p for p in podcasts if not p.has_metadata]

    # Successful podcasts
    if successful:
        lines.append("## Podcasts\n")

        for podcast in successful:
            lines.append(f"### {podcast.display_title}\n")

            if podcast.link:
                lines.append(f"**Link:** {podcast.link}")

            lines.append(f"**RSS Feed:** {podcast.xml_url}")

            if podcast.description:
                lines.append(f"**Description:** {podcast.description}")

            if podcast.image_url:
                lines.append(f"<img src=\"{podcast.image_url}\" width=\"200\">")

            lines.append("")  # Blank line between podcasts

    # Failed podcasts - categorized
    if failed:
        no_longer_exists, parsing_errors = categorize_failed_feeds(failed)

        # Feeds that no longer exist (404, DNS failures)
        if no_longer_exists:
            lines.append("## Feeds No Longer Exist\n")
            lines.append("These feeds returned 404 errors or have DNS resolution failures:\n")

            for podcast in no_longer_exists:
                error_msg = podcast.fetch_error or "Unknown error"
                lines.append(f"- **{podcast.title}**")
                lines.append(f"  - URL: {podcast.xml_url}")
                lines.append(f"  - Error: {error_msg}\n")

        # Feed parsing errors
        if parsing_errors:
            lines.append("## Feed Parsing Errors\n")
            lines.append("These feeds exist but have XML/parsing errors:\n")

            for podcast in parsing_errors:
                error_msg = podcast.fetch_error or "Unknown error"
                lines.append(f"- **{podcast.title}**")
                lines.append(f"  - URL: {podcast.xml_url}")
                lines.append(f"  - Error: {error_msg}\n")

    return "\n".join(lines)


def generate_enriched_markdown(podcasts: List[PodcastMetadata]) -> str:
    """
    Generate an AI-enriched markdown file organized by categories (Phase 2).

    Args:
        podcasts: List of PodcastMetadata objects with AI enrichment

    Returns:
        Formatted markdown string
    """
    lines = []

    # Header
    lines.append("# My Podcasts\n")
    lines.append(f"Total podcasts: {len(podcasts)}\n")
    lines.append(f"Successfully fetched: {sum(1 for p in podcasts if p.has_metadata)}\n")
    lines.append(f"Failed: {sum(1 for p in podcasts if not p.has_metadata)}\n")
    lines.append("")

    # Group podcasts by category
    successful = [p for p in podcasts if p.has_metadata]
    failed = [p for p in podcasts if not p.has_metadata]

    # Organize successful podcasts by category
    categorized: Dict[str, List[PodcastMetadata]] = defaultdict(list)
    uncategorized = []

    for podcast in successful:
        if podcast.category:
            categorized[podcast.category].append(podcast)
        else:
            uncategorized.append(podcast)

    # Sort categories alphabetically
    sorted_categories = sorted(categorized.keys())

    # Output each category
    for category in sorted_categories:
        lines.append(f"## {category}\n")

        for podcast in categorized[category]:
            lines.append(f"### {podcast.display_title}\n")

            if podcast.link:
                lines.append(f"**Link:** {podcast.link}")

            lines.append(f"**RSS Feed:** {podcast.xml_url}")

            # Use enhanced description if available
            description = podcast.final_description
            if description:
                lines.append(f"**Description:** {description}")

            # Add tags
            if podcast.tags:
                tags_str = " ".join(f"#{tag}" for tag in podcast.tags)
                lines.append(f"**Tags:** {tags_str}")

            if podcast.image_url:
                lines.append(f"<img src=\"{podcast.image_url}\" width=\"200\">")

            lines.append("")  # Blank line between podcasts

    # Uncategorized podcasts (shouldn't happen with AI, but just in case)
    if uncategorized:
        lines.append("## Uncategorized\n")

        for podcast in uncategorized:
            lines.append(f"### {podcast.display_title}\n")

            if podcast.link:
                lines.append(f"**Link:** {podcast.link}")

            lines.append(f"**RSS Feed:** {podcast.xml_url}")

            if podcast.description:
                lines.append(f"**Description:** {podcast.description}")

            if podcast.image_url:
                lines.append(f"<img src=\"{podcast.image_url}\" width=\"200\">")

            lines.append("")

    # Failed podcasts - categorized
    if failed:
        no_longer_exists, parsing_errors = categorize_failed_feeds(failed)

        # Feeds that no longer exist (404, DNS failures)
        if no_longer_exists:
            lines.append("## Feeds No Longer Exist\n")
            lines.append("These feeds returned 404 errors or have DNS resolution failures:\n")

            for podcast in no_longer_exists:
                error_msg = podcast.fetch_error or "Unknown error"
                lines.append(f"- **{podcast.title}**")
                lines.append(f"  - URL: {podcast.xml_url}")
                lines.append(f"  - Error: {error_msg}\n")

        # Feed parsing errors
        if parsing_errors:
            lines.append("## Feed Parsing Errors\n")
            lines.append("These feeds exist but have XML/parsing errors:\n")

            for podcast in parsing_errors:
                error_msg = podcast.fetch_error or "Unknown error"
                lines.append(f"- **{podcast.title}**")
                lines.append(f"  - URL: {podcast.xml_url}")
                lines.append(f"  - Error: {error_msg}\n")

    return "\n".join(lines)


def write_markdown(content: str, output_path: str) -> None:
    """
    Write markdown content to a file.

    Args:
        content: Markdown content string
        output_path: Path to output file
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
