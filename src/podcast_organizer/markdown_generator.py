"""Markdown output generator for podcast metadata."""

from typing import List, Dict
from collections import defaultdict
from .rss_fetcher import PodcastMetadata


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
                lines.append(f"**Link:** {podcast.link}\n")

            lines.append(f"**RSS Feed:** {podcast.xml_url}\n")

            if podcast.description:
                lines.append(f"**Description:** {podcast.description}\n")

            if podcast.image_url:
                lines.append(f"**Image:** {podcast.image_url}\n")

            lines.append("")  # Blank line between podcasts

    # Failed podcasts
    if failed:
        lines.append("## Failed to Fetch\n")
        lines.append("The following podcasts could not be fetched:\n")

        for podcast in failed:
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
                lines.append(f"**Link:** {podcast.link}\n")

            lines.append(f"**RSS Feed:** {podcast.xml_url}\n")

            # Use enhanced description if available
            description = podcast.final_description
            if description:
                lines.append(f"**Description:** {description}\n")

            # Add tags
            if podcast.tags:
                tags_str = " ".join(f"#{tag}" for tag in podcast.tags)
                lines.append(f"**Tags:** {tags_str}\n")

            if podcast.image_url:
                lines.append(f"**Image:** {podcast.image_url}\n")

            lines.append("")  # Blank line between podcasts

    # Uncategorized podcasts (shouldn't happen with AI, but just in case)
    if uncategorized:
        lines.append("## Uncategorized\n")

        for podcast in uncategorized:
            lines.append(f"### {podcast.display_title}\n")

            if podcast.link:
                lines.append(f"**Link:** {podcast.link}\n")

            lines.append(f"**RSS Feed:** {podcast.xml_url}\n")

            if podcast.description:
                lines.append(f"**Description:** {podcast.description}\n")

            if podcast.image_url:
                lines.append(f"**Image:** {podcast.image_url}\n")

            lines.append("")

    # Failed podcasts
    if failed:
        lines.append("## Failed to Fetch\n")
        lines.append("The following podcasts could not be fetched:\n")

        for podcast in failed:
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
