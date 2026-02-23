import typer
from pathlib import Path

from .abbrgen import abbrgen

app = typer.Typer()
DEFAULT_CONFIG = Path.home() / ".abbrgen" / "config.yaml"


@app.command()
def run(
    config: Path = typer.Option(
        DEFAULT_CONFIG, "-c", "--config", help="Path to config file"
    ),
):
    if config != DEFAULT_CONFIG and not config.exists():
        raise typer.BadParameter(f"Config file does not exist: {config}")

    abbrgen(config)


if __name__ == "__main__":
    app()
