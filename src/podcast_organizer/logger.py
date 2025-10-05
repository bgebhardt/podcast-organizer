"""Centralized logging with colored output for podcast organizer."""

from rich.console import Console
from typing import Optional


class PodcastLogger:
    """
    Centralized logger with colored output levels.

    Maintains existing color scheme while providing structured logging:
    - INFO: cyan/blue messages (default informational output)
    - SUCCESS: green messages with checkmarks
    - WARNING: yellow messages
    - ERROR: red messages
    """

    def __init__(self, verbose: bool = False):
        """
        Initialize logger.

        Args:
            verbose: Enable verbose output
        """
        self.console = Console()
        self.verbose = verbose

    def info(self, message: str, style: str = "cyan"):
        """
        Log informational message.

        Args:
            message: Message to log
            style: Rich color/style (cyan, blue, white, etc.)
        """
        self.console.print(f"[{style}]{message}[/{style}]")

    def success(self, message: str, prefix: str = "✓"):
        """
        Log success message in green.

        Args:
            message: Message to log
            prefix: Prefix symbol (default: checkmark)
        """
        if prefix:
            self.console.print(f"[green]{prefix} {message}[/green]")
        else:
            self.console.print(f"[green]{message}[/green]")

    def warning(self, message: str):
        """
        Log warning message in yellow.

        Args:
            message: Warning message
        """
        self.console.print(f"[yellow]{message}[/yellow]")

    def error(self, message: str):
        """
        Log error message in red.

        Args:
            message: Error message
        """
        self.console.print(f"[red]{message}[/red]")

    def verbose_info(self, message: str, style: str = "cyan"):
        """
        Log verbose informational message (only shown if verbose=True).

        Args:
            message: Message to log
            style: Rich color/style
        """
        if self.verbose:
            self.info(message, style)

    def header(self, message: str, style: str = "bold cyan"):
        """
        Log header message.

        Args:
            message: Header message
            style: Rich color/style
        """
        self.console.print(f"[{style}]{message}[/{style}]")

    def step(self, message: str, style: str = ""):
        """
        Log step message (no color by default).

        Args:
            message: Step message
            style: Optional Rich color/style
        """
        if style:
            self.console.print(f"[{style}]{message}[/{style}]")
        else:
            self.console.print(message)

    def print(self, message: str, style: Optional[str] = None):
        """
        Print plain message with optional styling.

        Args:
            message: Message to print
            style: Optional Rich color/style
        """
        if style:
            self.console.print(f"[{style}]{message}[/{style}]")
        else:
            self.console.print(message)


# Global logger instance (initialized in cli.py)
_logger: Optional[PodcastLogger] = None


def init_logger(verbose: bool = False) -> PodcastLogger:
    """
    Initialize global logger instance.

    Args:
        verbose: Enable verbose output

    Returns:
        PodcastLogger instance
    """
    global _logger
    _logger = PodcastLogger(verbose=verbose)
    return _logger


def get_logger() -> PodcastLogger:
    """
    Get global logger instance.

    Returns:
        PodcastLogger instance

    Raises:
        RuntimeError: If logger not initialized
    """
    if _logger is None:
        raise RuntimeError("Logger not initialized. Call init_logger() first.")
    return _logger
