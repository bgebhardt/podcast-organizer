"""Command-line interface for podcast organizer."""

import click
from pathlib import Path
from rich.console import Console

from .opml_parser import parse_opml_limit
from .rss_fetcher import fetch_all_rss_metadata_sync
from .markdown_generator import generate_basic_markdown, generate_enriched_markdown, write_markdown
from .config import load_config, validate_config
from .ai_enricher import enrich_podcasts_with_ai


console = Console()


@click.command()
@click.argument('input_file', type=click.Path(exists=True, dir_okay=False))
@click.option(
    '--output', '-o',
    default=None,
    help='Output markdown file path (overrides config)',
    type=click.Path()
)
@click.option(
    '--limit',
    type=int,
    default=None,
    help='Limit number of podcasts to process (for testing)'
)
@click.option(
    '--timeout',
    type=int,
    default=None,
    help='RSS fetch timeout in seconds (overrides config)'
)
@click.option(
    '--max-concurrent',
    type=int,
    default=None,
    help='Maximum concurrent RSS fetches (overrides config)'
)
@click.option(
    '--provider',
    type=click.Choice(['claude', 'openai'], case_sensitive=False),
    default=None,
    help='AI provider to use (overrides config)'
)
@click.option(
    '--no-ai',
    is_flag=True,
    help='Skip AI enrichment (Phase 1 output only)'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Verbose output'
)
@click.option(
    '--dry-run',
    is_flag=True,
    help='Parse and fetch but do not write output'
)
def main(
    input_file: str,
    output: str,
    limit: int,
    timeout: int,
    max_concurrent: int,
    provider: str,
    no_ai: bool,
    verbose: bool,
    dry_run: bool
):
    """
    Podcast Organizer - Transform OPML podcast subscriptions into organized Markdown.

    Phase 1: Parse OPML, fetch RSS metadata
    Phase 2: AI enrichment with categorization and tags
    """
    # Load configuration
    config = load_config()

    # Apply CLI overrides
    if output:
        config.output.default_file = output
    if timeout is not None:
        config.fetching.timeout = timeout
    if max_concurrent is not None:
        config.fetching.max_concurrent = max_concurrent
    if provider:
        config.ai.provider = provider.lower()

    # Validate config (only if using AI)
    if not no_ai:
        errors = validate_config(config, require_ai=True)
        if errors:
            console.print("[red]Configuration errors:[/red]")
            for error in errors:
                console.print(f"  - {error}")
            console.print("\n[yellow]Tip:[/yellow] Copy .podcast-organizer.yaml.example to .podcast-organizer.yaml and add your API keys")
            raise click.Abort()

    # Determine phase
    phase = "Phase 1 (No AI)" if no_ai else f"Phase 2 (AI: {config.ai.provider})"
    console.print(f"[bold blue]Podcast Organizer[/bold blue] - {phase}\n")

    # Step 1: Parse OPML
    console.print(f"[cyan]Step 1:[/cyan] Parsing OPML file: {input_file}")
    try:
        entries = parse_opml_limit(input_file, limit)
        console.print(f"  ✓ Found {len(entries)} podcast(s)\n")
    except Exception as e:
        console.print(f"[red]Error parsing OPML:[/red] {e}")
        raise click.Abort()

    if not entries:
        console.print("[yellow]No podcast entries found in OPML file[/yellow]")
        return

    # Step 2: Fetch RSS metadata
    console.print(f"[cyan]Step 2:[/cyan] Fetching RSS metadata")
    console.print(f"  Settings: timeout={config.fetching.timeout}s, max_concurrent={config.fetching.max_concurrent}")

    try:
        podcasts = fetch_all_rss_metadata_sync(
            entries,
            max_concurrent=config.fetching.max_concurrent,
            timeout=config.fetching.timeout,
            verbose=verbose
        )

        successful = sum(1 for p in podcasts if p.has_metadata)
        failed = len(podcasts) - successful

        console.print(f"  ✓ Fetched: {successful} successful, {failed} failed\n")

        if failed > 0 and verbose:
            console.print("[yellow]Failed feeds:[/yellow]")
            for p in podcasts:
                if not p.has_metadata:
                    console.print(f"  - {p.title}: {p.fetch_error}")
            console.print()

    except Exception as e:
        console.print(f"[red]Error fetching RSS feeds:[/red] {e}")
        raise click.Abort()

    # Step 3: AI Enrichment (if enabled)
    if not no_ai:
        console.print(f"[cyan]Step 3:[/cyan] AI enrichment")

        try:
            podcasts = enrich_podcasts_with_ai(
                podcasts,
                config.ai,
                verbose=verbose
            )
            console.print()

        except Exception as e:
            console.print(f"[red]Error during AI enrichment:[/red] {e}")
            raise click.Abort()

    # Step 4 (or 3 if no AI): Generate markdown
    step_num = 4 if not no_ai else 3
    console.print(f"[cyan]Step {step_num}:[/cyan] Generating markdown output")

    try:
        if no_ai:
            markdown_content = generate_basic_markdown(podcasts)
        else:
            markdown_content = generate_enriched_markdown(podcasts)

        if dry_run:
            console.print("  [yellow]Dry run - skipping file write[/yellow]")
            console.print(f"  Would write to: {config.output.default_file}")
        else:
            write_markdown(markdown_content, config.output.default_file)
            output_path = Path(config.output.default_file).resolve()
            console.print(f"  ✓ Written to: {output_path}\n")

        console.print("[bold green]✓ Complete![/bold green]")

    except Exception as e:
        console.print(f"[red]Error generating markdown:[/red] {e}")
        raise click.Abort()


if __name__ == '__main__':
    main()
