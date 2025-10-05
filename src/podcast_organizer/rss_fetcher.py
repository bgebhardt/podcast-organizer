"""RSS feed fetcher for extracting podcast metadata."""

import asyncio
from dataclasses import dataclass, field
from typing import List, Optional
import feedparser
import httpx
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .opml_parser import PodcastEntry


console = Console()


@dataclass
class PodcastMetadata:
    """Represents enriched podcast metadata from RSS feed."""
    # Original OPML data
    title: str
    xml_url: str

    # Fetched RSS metadata
    rss_title: Optional[str] = None
    link: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

    # AI enrichment data (Phase 2)
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    enhanced_description: Optional[str] = None

    # Error tracking
    fetch_error: Optional[str] = None

    @property
    def display_title(self) -> str:
        """Get the best available title."""
        return self.rss_title or self.title

    @property
    def has_metadata(self) -> bool:
        """Check if RSS metadata was successfully fetched."""
        return self.rss_title is not None

    @property
    def final_description(self) -> Optional[str]:
        """Get the best available description (enhanced or original)."""
        return self.enhanced_description or self.description


async def fetch_rss_metadata(
    entry: PodcastEntry,
    timeout: int = 30
) -> PodcastMetadata:
    """
    Fetch RSS metadata for a single podcast.

    Args:
        entry: PodcastEntry with RSS URL
        timeout: Request timeout in seconds

    Returns:
        PodcastMetadata with fetched information
    """
    metadata = PodcastMetadata(
        title=entry.title,
        xml_url=entry.xml_url
    )

    # User-Agent header is required by some feed hosts (e.g., Buzzsprout)
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; Podcast Organizer/1.0; +https://github.com)'
    }

    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, headers=headers) as client:
            response = await client.get(entry.xml_url)
            response.raise_for_status()

            # Parse RSS feed
            feed = feedparser.parse(response.text)

            if feed.bozo:
                # Feed has parsing errors
                metadata.fetch_error = f"Feed parsing error: {feed.get('bozo_exception', 'Unknown error')}"
                return metadata

            # Extract channel metadata
            channel = feed.get('feed', {})

            metadata.rss_title = channel.get('title', '').strip()
            metadata.link = channel.get('link', '').strip()

            # Try multiple description fields
            metadata.description = (
                channel.get('summary', '').strip() or
                channel.get('subtitle', '').strip() or
                channel.get('description', '').strip()
            )

            # Try to get image URL
            if 'image' in channel and 'href' in channel['image']:
                metadata.image_url = channel['image']['href']
            elif 'image' in channel and 'url' in channel['image']:
                metadata.image_url = channel['image']['url']

    except httpx.TimeoutException:
        metadata.fetch_error = f"Timeout after {timeout}s"
    except httpx.HTTPStatusError as e:
        metadata.fetch_error = f"HTTP {e.response.status_code}"
    except Exception as e:
        metadata.fetch_error = f"Error: {str(e)}"

    return metadata


async def fetch_all_rss_metadata(
    entries: List[PodcastEntry],
    max_concurrent: int = 10,
    timeout: int = 30,
    verbose: bool = False
) -> List[PodcastMetadata]:
    """
    Fetch RSS metadata for multiple podcasts concurrently.

    Args:
        entries: List of PodcastEntry objects
        max_concurrent: Maximum concurrent requests
        timeout: Request timeout in seconds
        verbose: Show progress information

    Returns:
        List of PodcastMetadata objects
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_with_semaphore(entry: PodcastEntry) -> PodcastMetadata:
        async with semaphore:
            return await fetch_rss_metadata(entry, timeout)

    if verbose:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(
                f"Fetching RSS feeds for {len(entries)} podcasts...",
                total=None
            )

            results = await asyncio.gather(
                *[fetch_with_semaphore(entry) for entry in entries]
            )

            progress.update(task, completed=True)
    else:
        results = await asyncio.gather(
            *[fetch_with_semaphore(entry) for entry in entries]
        )

    return results


def fetch_all_rss_metadata_sync(
    entries: List[PodcastEntry],
    max_concurrent: int = 10,
    timeout: int = 30,
    verbose: bool = False
) -> List[PodcastMetadata]:
    """
    Synchronous wrapper for fetch_all_rss_metadata.

    Args:
        entries: List of PodcastEntry objects
        max_concurrent: Maximum concurrent requests
        timeout: Request timeout in seconds
        verbose: Show progress information

    Returns:
        List of PodcastMetadata objects
    """
    return asyncio.run(
        fetch_all_rss_metadata(entries, max_concurrent, timeout, verbose)
    )
