"""AI enrichment for podcast categorization and tagging."""

import json
from typing import List, Dict, Optional
from abc import ABC, abstractmethod

from anthropic import Anthropic
from openai import OpenAI
from rich.console import Console

from .rss_fetcher import PodcastMetadata
from .config import AIConfig
from .tag_generator import generate_tags_for_podcast


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
        """Build categorization prompt for Claude (simplified for large collections)."""
        podcasts_json = json.dumps(podcast_list, indent=2)

        return f"""You are helping organize a podcast collection. I have {len(podcast_list)} podcasts that need to be categorized.

Here are the podcasts:

{podcasts_json}

Please analyze these podcasts and:
1. Create logical category groupings (e.g., "Technology & AI", "Business & Entrepreneurship", "News & Politics", "Health & Wellness", etc.)
2. Assign each podcast to ONE category based on its title and description
3. Use clear, descriptive category names

Return your response as a JSON object with this structure:

{{
  "categories": {{
    "Technology & AI": [0, 1, 5, 8, 12],
    "Business & Entrepreneurship": [2, 3, 4],
    "News & Politics": [6, 7, 9]
  }}
}}

IMPORTANT:
- Include ALL podcast IDs (0 through {len(podcast_list)-1}) in the categories
- Each podcast must be assigned to exactly ONE category
- Only return valid JSON, no other text or explanations

Use the podcast IDs (0, 1, 2, etc.) to reference podcasts."""

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
        """Build categorization prompt for OpenAI (simplified for large collections)."""
        podcasts_json = json.dumps(podcast_list, indent=2)

        return f"""You are helping organize a podcast collection. I have {len(podcast_list)} podcasts that need to be categorized.

Here are the podcasts:

{podcasts_json}

Please analyze these podcasts and:
1. Create logical category groupings (e.g., "Technology & AI", "Business & Entrepreneurship", "News & Politics", "Health & Wellness", etc.)
2. Assign each podcast to ONE category based on its title and description
3. Use clear, descriptive category names

Return your response as a JSON object with this structure:

{{
  "categories": {{
    "Technology & AI": [0, 1, 5, 8, 12],
    "Business & Entrepreneurship": [2, 3, 4],
    "News & Politics": [6, 7, 9]
  }}
}}

IMPORTANT:
- Include ALL podcast IDs (0 through {len(podcast_list)-1}) in the categories
- Each podcast must be assigned to exactly ONE category

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
    output_file: str = "podcasts.md",
    verbose: bool = False
) -> List[PodcastMetadata]:
    """
    Enrich podcasts with AI-generated categories and tags.

    Args:
        podcasts: List of PodcastMetadata objects
        config: AI configuration
        output_file: Output markdown filename (used to derive JSON filename)
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

    # Save JSON response to file
    json_file = f"{output_file}.json"
    try:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(enrichment_data, f, indent=2, ensure_ascii=False)
        if verbose:
            console.print(f"  ✓ Saved AI response to: {json_file}")
    except Exception as e:
        console.print(f"[yellow]Warning: Could not save JSON response:[/yellow] {e}")

    # Apply enrichment to podcasts
    podcast_enrichments = enrichment_data.get("podcasts", {})
    categories = enrichment_data.get("categories", {})

    # Apply categories from category mapping
    for category, podcast_ids in categories.items():
        for podcast_id in podcast_ids:
            if podcast_id < len(valid_podcasts):
                valid_podcasts[podcast_id].category = category

    # Generate tags for all podcasts based on category + title
    for podcast in valid_podcasts:
        if podcast.category:
            # Auto-generate tags from category and title
            auto_tags = generate_tags_for_podcast(
                category=podcast.category,
                title=podcast.display_title,
                max_total_tags=5
            )
            podcast.tags = auto_tags

    # Apply detailed enrichment from AI if available (overrides auto-tags)
    num_enriched = len(podcast_enrichments)
    for i, podcast in enumerate(valid_podcasts):
        enrichment = podcast_enrichments.get(str(i), {})

        if enrichment:
            # Override with AI-generated tags if provided
            ai_tags = enrichment.get("tags", [])
            if ai_tags:
                podcast.tags = ai_tags

            # Use enhanced description if provided
            enhanced_desc = enrichment.get("enhanced_description")
            if enhanced_desc:
                podcast.enhanced_description = enhanced_desc

    if verbose:
        console.print(f"  ✓ Created {len(categories)} categories")
        console.print(f"  ✓ Auto-generated tags for all {len(valid_podcasts)} podcasts")
        if num_enriched > 0:
            console.print(f"  ✓ AI-enhanced tags for {num_enriched} podcasts")
        for cat, podcast_ids in categories.items():
            console.print(f"    - {cat}: {len(podcast_ids)} podcasts")

    # Combine valid and failed podcasts
    return valid_podcasts + failed_podcasts
