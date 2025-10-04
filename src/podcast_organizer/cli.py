"""Command-line interface for podcast organizer."""

import click
from pathlib import Path
from rich.console import Console

from .opml_parser import parse_opml_limit
from .rss_fetcher import fetch_all_rss_metadata_sync
from .markdown_generator import generate_basic_markdown, write_markdown


console = Console()


@click.command()
@click.argument('input_file', type=click.Path(exists=True, dir_okay=False))
@click.option(
    '--output', '-o',
    default='podcasts.md',
    help='Output markdown file path',
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
    default=30,
    help='RSS fetch timeout in seconds'
)
@click.option(
    '--max-concurrent',
    type=int,
    default=10,
    help='Maximum concurrent RSS fetches'
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
    verbose: bool,
    dry_run: bool
):
    """
    Podcast Organizer - Transform OPML podcast subscriptions into organized Markdown.

    Phase 1 (MVP): Parse OPML, fetch RSS metadata, output basic markdown.
    """
    console.print(f"[bold blue]Podcast Organizer[/bold blue] - Phase 1 (MVP)\n")

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
    console.print(f"  Settings: timeout={timeout}s, max_concurrent={max_concurrent}")

    try:
        podcasts = fetch_all_rss_metadata_sync(
            entries,
            max_concurrent=max_concurrent,
            timeout=timeout,
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

    # Step 3: Generate markdown
    console.print(f"[cyan]Step 3:[/cyan] Generating markdown output")

    try:
        markdown_content = generate_basic_markdown(podcasts)

        if dry_run:
            console.print("  [yellow]Dry run - skipping file write[/yellow]")
            console.print(f"  Would write to: {output}")
        else:
            write_markdown(markdown_content, output)
            output_path = Path(output).resolve()
            console.print(f"  ✓ Written to: {output_path}\n")

        console.print("[bold green]✓ Complete![/bold green]")

    except Exception as e:
        console.print(f"[red]Error generating markdown:[/red] {e}")
        raise click.Abort()


if __name__ == '__main__':
    main()
