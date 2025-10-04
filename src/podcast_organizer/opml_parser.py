"""OPML parser for extracting podcast RSS feed URLs."""

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List
from urllib.parse import unquote


@dataclass
class PodcastEntry:
    """Represents a podcast entry from OPML."""
    text: str
    title: str
    xml_url: str

    def __post_init__(self):
        """Decode URL-encoded strings."""
        self.text = unquote(self.text)
        self.title = unquote(self.title)


def parse_opml(file_path: str) -> List[PodcastEntry]:
    """
    Parse an OPML file and extract podcast RSS feed information.

    Args:
        file_path: Path to the OPML file

    Returns:
        List of PodcastEntry objects containing podcast metadata

    Raises:
        FileNotFoundError: If the OPML file doesn't exist
        ET.ParseError: If the OPML file is malformed
    """
    tree = ET.parse(file_path)
    root = tree.getroot()

    podcasts = []

    # Find all outline elements with type="rss"
    for outline in root.findall(".//outline[@type='rss']"):
        text = outline.get('text', '')
        title = outline.get('title', '')
        xml_url = outline.get('xmlUrl', '')

        # Skip entries without required fields
        if not xml_url:
            continue

        # Use title if text is empty, or vice versa
        if not text:
            text = title
        if not title:
            title = text

        podcasts.append(PodcastEntry(
            text=text,
            title=title,
            xml_url=xml_url
        ))

    return podcasts


def parse_opml_limit(file_path: str, limit: int = None) -> List[PodcastEntry]:
    """
    Parse an OPML file with an optional limit on number of entries.

    Args:
        file_path: Path to the OPML file
        limit: Maximum number of entries to return (None for all)

    Returns:
        List of PodcastEntry objects
    """
    podcasts = parse_opml(file_path)

    if limit is not None and limit > 0:
        return podcasts[:limit]

    return podcasts
