import typer
from pathlib import Path

from abbrgen.config import DEFAULT_CONFIG

from .abbreviate import abbreviate as abbr


app = typer.Typer()
state = {"config": DEFAULT_CONFIG}


@app.callback()
def run(
    config: Path = typer.Option(
        DEFAULT_CONFIG, "-c", "--config", help="Path to config file"
    ),
):
    state["config"] = config


@app.command()
def abbreviate():
    abbr(state["config"])


if __name__ == "__main__":
    app()
