import logging

from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme

theme = Theme(
    {
        "info": "cyan",
        "success": "bold green",
        "warning": "yellow",
        "error": "bold red",
        "request": "magenta",
        "dim": "grey50",
    }
)

console = Console(theme=theme, force_terminal=True, color_system="truecolor")

handler = RichHandler(
    console=console,
    rich_tracebacks=True,
    tracebacks_show_locals=False,
    show_path=False,
    show_time=True,
    markup=True,
    omit_repeated_times=False,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[handler],
)

logger = logging.getLogger("movie-api")

# Route uvicorn logs through rich too → single consistent colored stream
for name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
    lg = logging.getLogger(name)
    lg.handlers = [handler]
    lg.propagate = False
