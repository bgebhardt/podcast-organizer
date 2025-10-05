"""AI enrichment for podcast categorization and tagging."""

import json
from typing import List, Dict, Optional
from abc import ABC, abstractmethod

from anthropic import Anthropic
from openai import OpenAI
from rich.console import Console

from .rss_fetcher import PodcastMetadata
from .config import AIConfig
from .tag_generator import generate_tags_for_podcast, deduplicate_tags


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

    @abstractmethod
    def generate_tags_batch(self, podcasts: List[PodcastMetadata], batch_size: int = 25) -> Dict:
        """
        Generate tags for podcasts in batches.

        Args:
            podcasts: List of PodcastMetadata objects
            batch_size: Number of podcasts per batch

        Returns:
            Dict mapping podcast index to list of tags
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

    def generate_tags_batch(self, podcasts: List[PodcastMetadata], batch_size: int = 25) -> Dict:
        """Generate tags for podcasts in batches using Claude."""
        all_tags = {}

        # Process in batches
        for i in range(0, len(podcasts), batch_size):
            batch = podcasts[i:i + batch_size]
            batch_data = [
                {
                    "id": i + j,
                    "title": p.display_title,
                    "category": p.category or "Uncategorized",
                    "description": (p.description or "")[:200]  # Truncate long descriptions
                }
                for j, p in enumerate(batch)
            ]

            prompt = self._build_tag_prompt(batch_data)

            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4000,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )

                content = response.content[0].text
                batch_tags = self._parse_response(content, batch)

                # Merge batch results
                if "tags" in batch_tags:
                    all_tags.update(batch_tags["tags"])

            except Exception as e:
                console.print(f"[yellow]Warning: Failed to generate tags for batch {i//batch_size + 1}:[/yellow] {e}")
                continue

        return {"tags": all_tags}

    def _build_tag_prompt(self, podcast_list: List[Dict]) -> str:
        """Build tag generation prompt for Claude."""
        podcasts_json = json.dumps(podcast_list, indent=2)

        return f"""Generate 3-5 relevant tags for each of these {len(podcast_list)} podcasts.

Podcasts:
{podcasts_json}

For each podcast, create tags that:
1. Reflect the podcast's category and topic
2. Include relevant keywords from the title
3. Are concise (1-2 words each)
4. Are lowercase without # symbol
5. Use dashes to join multi-word tags (e.g., "venture-capital" not "venture capital")

Return JSON in this format:
{{
  "tags": {{
    "0": ["technology", "business", "venture-capital"],
    "1": ["news", "politics", "world-affairs"]
  }}
}}

Include ALL podcast IDs (0 through {len(podcast_list)-1}). Return only valid JSON."""


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

    def generate_tags_batch(self, podcasts: List[PodcastMetadata], batch_size: int = 25) -> Dict:
        """Generate tags for podcasts in batches using OpenAI."""
        all_tags = {}

        # Process in batches
        for i in range(0, len(podcasts), batch_size):
            batch = podcasts[i:i + batch_size]
            batch_data = [
                {
                    "id": i + j,
                    "title": p.display_title,
                    "category": p.category or "Uncategorized",
                    "description": (p.description or "")[:200]
                }
                for j, p in enumerate(batch)
            ]

            prompt = self._build_tag_prompt(batch_data)

            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that generates relevant tags for podcasts. Always respond with valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )

                content = response.choices[0].message.content
                batch_tags = self._parse_response(content, batch)

                # Merge batch results
                if "tags" in batch_tags:
                    all_tags.update(batch_tags["tags"])

            except Exception as e:
                console.print(f"[yellow]Warning: Failed to generate tags for batch {i//batch_size + 1}:[/yellow] {e}")
                continue

        return {"tags": all_tags}

    def _build_tag_prompt(self, podcast_list: List[Dict]) -> str:
        """Build tag generation prompt for OpenAI."""
        podcasts_json = json.dumps(podcast_list, indent=2)

        return f"""Generate 3-5 relevant tags for each of these {len(podcast_list)} podcasts.

Podcasts:
{podcasts_json}

For each podcast, create tags that:
1. Reflect the podcast's category and topic
2. Include relevant keywords from the title
3. Are concise (1-2 words each)
4. Are lowercase without # symbol
5. Use dashes to join multi-word tags (e.g., "venture-capital" not "venture capital")

Return JSON in this format:
{{
  "tags": {{
    "0": ["technology", "business", "venture-capital"],
    "1": ["news", "politics", "world-affairs"]
  }}
}}

Include ALL podcast IDs (0 through {len(podcast_list)-1})."""


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

    # Create AI provider
    provider = create_ai_provider(config)

    # PASS 1: Categorization (works well for large collections)
    if verbose:
        console.print(f"[cyan]Pass 1: Categorizing {len(valid_podcasts)} podcasts with {config.provider}...[/cyan]")

    enrichment_data = provider.enrich_podcasts(valid_podcasts)
    categories = enrichment_data.get("categories", {})

    # Apply categories from category mapping
    for category, podcast_ids in categories.items():
        for podcast_id in podcast_ids:
            if podcast_id < len(valid_podcasts):
                valid_podcasts[podcast_id].category = category

    if verbose:
        console.print(f"  ✓ Created {len(categories)} categories")
        for cat, podcast_ids in categories.items():
            console.print(f"    - {cat}: {len(podcast_ids)} podcasts")

    # PASS 2: AI Tag Generation (in batches for reliability)
    if verbose:
        console.print(f"[cyan]Pass 2: Generating AI tags in batches...[/cyan]")

    tag_data = provider.generate_tags_batch(valid_podcasts, batch_size=25)
    ai_tags_generated = tag_data.get("tags", {})

    # Apply AI-generated tags (normalize to use dashes)
    num_ai_tagged = 0
    for i, podcast in enumerate(valid_podcasts):
        ai_tags = ai_tags_generated.get(str(i), [])
        if ai_tags:
            # Normalize AI tags to ensure dashes instead of spaces
            podcast.tags = deduplicate_tags(ai_tags)
            num_ai_tagged += 1
        else:
            # Fallback to auto-generated tags if AI didn't provide
            if podcast.category:
                auto_tags = generate_tags_for_podcast(
                    category=podcast.category,
                    title=podcast.display_title,
                    max_total_tags=5
                )
                # Auto-generated tags are already normalized via deduplicate_tags
                podcast.tags = deduplicate_tags(auto_tags)

    if verbose:
        console.print(f"  ✓ AI-generated tags for {num_ai_tagged}/{len(valid_podcasts)} podcasts")
        if num_ai_tagged < len(valid_podcasts):
            console.print(f"  ✓ Auto-generated tags for remaining {len(valid_podcasts) - num_ai_tagged} podcasts")

    # Save combined enrichment data to JSON
    enrichment_data["ai_tags"] = ai_tags_generated
    enrichment_data["stats"] = {
        "total_podcasts": len(valid_podcasts),
        "categories": len(categories),
        "ai_tagged": num_ai_tagged,
        "auto_tagged": len(valid_podcasts) - num_ai_tagged
    }

    json_file = f"{output_file}.json"
    try:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(enrichment_data, f, indent=2, ensure_ascii=False)
        if verbose:
            console.print(f"  ✓ Saved enrichment data to: {json_file}")
    except Exception as e:
        console.print(f"[yellow]Warning: Could not save JSON response:[/yellow] {e}")

    # Combine valid and failed podcasts
    return valid_podcasts + failed_podcasts
