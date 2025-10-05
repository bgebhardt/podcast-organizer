"""AI enrichment for podcast categorization and tagging."""

import json
from typing import List, Dict, Optional
from abc import ABC, abstractmethod

from anthropic import Anthropic
from openai import OpenAI
from rich.console import Console

from .rss_fetcher import PodcastMetadata
from .config import AIConfig


console = Console()


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    def enrich_podcasts(self, podcasts: List[PodcastMetadata]) -> Dict:
        """
        Enrich podcasts with categories and tags.

        Args:
            podcasts: List of PodcastMetadata objects

        Returns:
            Dict with categorization and enrichment data
        """
        pass


class ClaudeProvider(AIProvider):
    """Claude (Anthropic) AI provider."""

    def __init__(self, api_key: str, model: Optional[str] = None):
        self.client = Anthropic(api_key=api_key)
        self.model = model or "claude-3-5-sonnet-20241022"

    def enrich_podcasts(self, podcasts: List[PodcastMetadata]) -> Dict:
        """Enrich podcasts using Claude."""
        # Build podcast list for prompt
        podcast_list = []
        for i, p in enumerate(podcasts):
            podcast_list.append({
                "id": i,
                "title": p.display_title,
                "description": p.description or "No description available"
            })

        prompt = self._build_prompt(podcast_list)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=8000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Parse JSON response
            content = response.content[0].text
            return self._parse_response(content, podcasts)

        except Exception as e:
            console.print(f"[red]Error calling Claude API:[/red] {e}")
            raise

    def _build_prompt(self, podcast_list: List[Dict]) -> str:
        """Build enrichment prompt for Claude."""
        podcasts_json = json.dumps(podcast_list, indent=2)

        return f"""You are helping organize a podcast collection. I have {len(podcast_list)} podcasts that need to be categorized and tagged.

Here are the podcasts:

{podcasts_json}

Please analyze these podcasts and:
1. Create logical category groupings (e.g., "Technology & AI", "Business & Entrepreneurship", "News & Politics", etc.)
2. Assign each podcast to ONE category
3. Generate 3-5 relevant tags for each podcast (as hashtags, e.g., #technology #ai #innovation)
4. Optionally improve/summarize descriptions if they're too verbose or unclear

Return your response as a JSON object with this structure:

{{
  "categories": {{
    "Category Name 1": [0, 1, 5],
    "Category Name 2": [2, 3, 4]
  }},
  "podcasts": {{
    "0": {{
      "category": "Category Name 1",
      "tags": ["technology", "ai", "innovation"],
      "enhanced_description": "Optional improved description or null"
    }},
    "1": {{ ... }}
  }}
}}

Use the podcast IDs (0, 1, 2, etc.) to reference podcasts. Only return valid JSON, no other text."""

    def _parse_response(self, content: str, podcasts: List[PodcastMetadata]) -> Dict:
        """Parse Claude's JSON response."""
        try:
            # Try to extract JSON from response
            # Sometimes Claude wraps JSON in markdown code blocks
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                content = content[start:end].strip()
            elif "```" in content:
                start = content.find("```") + 3
                end = content.find("```", start)
                content = content[start:end].strip()

            data = json.loads(content)
            return data

        except json.JSONDecodeError as e:
            console.print(f"[red]Failed to parse JSON response:[/red] {e}")
            console.print(f"[yellow]Response:[/yellow] {content}")
            raise


class OpenAIProvider(AIProvider):
    """OpenAI (GPT) AI provider."""

    def __init__(self, api_key: str, model: Optional[str] = None):
        self.client = OpenAI(api_key=api_key)
        self.model = model or "gpt-4-turbo-preview"

    def enrich_podcasts(self, podcasts: List[PodcastMetadata]) -> Dict:
        """Enrich podcasts using OpenAI."""
        # Build podcast list for prompt
        podcast_list = []
        for i, p in enumerate(podcasts):
            podcast_list.append({
                "id": i,
                "title": p.display_title,
                "description": p.description or "No description available"
            })

        prompt = self._build_prompt(podcast_list)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that organizes podcast collections. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )

            # Parse JSON response
            content = response.choices[0].message.content
            return self._parse_response(content, podcasts)

        except Exception as e:
            console.print(f"[red]Error calling OpenAI API:[/red] {e}")
            raise

    def _build_prompt(self, podcast_list: List[Dict]) -> str:
        """Build enrichment prompt for OpenAI."""
        podcasts_json = json.dumps(podcast_list, indent=2)

        return f"""You are helping organize a podcast collection. I have {len(podcast_list)} podcasts that need to be categorized and tagged.

Here are the podcasts:

{podcasts_json}

Please analyze these podcasts and:
1. Create logical category groupings (e.g., "Technology & AI", "Business & Entrepreneurship", "News & Politics", etc.)
2. Assign each podcast to ONE category
3. Generate 3-5 relevant tags for each podcast (as hashtags, e.g., #technology #ai #innovation)
4. Optionally improve/summarize descriptions if they're too verbose or unclear

Return your response as a JSON object with this structure:

{{
  "categories": {{
    "Category Name 1": [0, 1, 5],
    "Category Name 2": [2, 3, 4]
  }},
  "podcasts": {{
    "0": {{
      "category": "Category Name 1",
      "tags": ["technology", "ai", "innovation"],
      "enhanced_description": "Optional improved description or null"
    }},
    "1": {{ ... }}
  }}
}}

Use the podcast IDs (0, 1, 2, etc.) to reference podcasts."""

    def _parse_response(self, content: str, podcasts: List[PodcastMetadata]) -> Dict:
        """Parse OpenAI's JSON response."""
        try:
            data = json.loads(content)
            return data
        except json.JSONDecodeError as e:
            console.print(f"[red]Failed to parse JSON response:[/red] {e}")
            console.print(f"[yellow]Response:[/yellow] {content}")
            raise


def create_ai_provider(config: AIConfig) -> AIProvider:
    """
    Factory function to create appropriate AI provider.

    Args:
        config: AI configuration

    Returns:
        AIProvider instance

    Raises:
        ValueError: If provider is invalid or API key is missing
    """
    provider = config.provider.lower()

    if provider == "claude":
        if not config.anthropic_api_key:
            raise ValueError("Anthropic API key not configured")
        return ClaudeProvider(config.anthropic_api_key, config.model)

    elif provider == "openai":
        if not config.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        return OpenAIProvider(config.openai_api_key, config.model)

    else:
        raise ValueError(f"Unknown AI provider: {provider}")


def enrich_podcasts_with_ai(
    podcasts: List[PodcastMetadata],
    config: AIConfig,
    verbose: bool = False
) -> List[PodcastMetadata]:
    """
    Enrich podcasts with AI-generated categories and tags.

    Args:
        podcasts: List of PodcastMetadata objects
        config: AI configuration
        verbose: Show verbose output

    Returns:
        List of enriched PodcastMetadata objects
    """
    if not podcasts:
        return podcasts

    # Filter out podcasts without metadata
    valid_podcasts = [p for p in podcasts if p.has_metadata]
    failed_podcasts = [p for p in podcasts if not p.has_metadata]

    if not valid_podcasts:
        console.print("[yellow]No valid podcasts to enrich[/yellow]")
        return podcasts

    if verbose:
        console.print(f"[cyan]Enriching {len(valid_podcasts)} podcasts with {config.provider}...[/cyan]")

    # Create AI provider
    provider = create_ai_provider(config)

    # Get enrichment data
    enrichment_data = provider.enrich_podcasts(valid_podcasts)

    # Apply enrichment to podcasts
    podcast_enrichments = enrichment_data.get("podcasts", {})

    for i, podcast in enumerate(valid_podcasts):
        enrichment = podcast_enrichments.get(str(i), {})

        podcast.category = enrichment.get("category")
        podcast.tags = enrichment.get("tags", [])

        # Use enhanced description if provided and better than original
        enhanced_desc = enrichment.get("enhanced_description")
        if enhanced_desc:
            podcast.enhanced_description = enhanced_desc

    if verbose:
        categories = enrichment_data.get("categories", {})
        console.print(f"  ✓ Created {len(categories)} categories")
        for cat, podcast_ids in categories.items():
            console.print(f"    - {cat}: {len(podcast_ids)} podcasts")

    # Combine valid and failed podcasts
    return valid_podcasts + failed_podcasts
