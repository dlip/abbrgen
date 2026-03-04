import logging
from abbrgen.abbreviation import load_abbreviation_file, validate_combos
import typer
from pathlib import Path

from abbrgen.config import DEFAULT_CONFIG, Config, load_or_create_config

from .abbreviate import abbreviate as abbr


app = typer.Typer()


class State:
    config: Config


@app.callback()
def callback(
    ctx: typer.Context,
    config: Path = typer.Option(
        DEFAULT_CONFIG, "-c", "--config", help="Path to config file"
    ),
):
    logging.basicConfig(level="INFO")
    if ctx.invoked_subcommand != "setup":
        if not config.exists():
            print(
                f"Error: config {config} does not exist, run 'abbrgen setup' to create it"
            )
            raise typer.Abort()

    loaded_config = load_or_create_config(config)
    if ctx.invoked_subcommand != "setup":
        if not loaded_config.abbreviation_file.exists():
            print(
                f"Error: abrreviation file {loaded_config.abbreviation_file} does not exist, run 'abbrgen setup' to create it"
            )
            raise typer.Abort()

    State.config = loaded_config


@app.command()
def setup():
    print("Setup Complete")


@app.command()
def abbreviate():
    abbr(State.config)


@app.command()
def output():
    abbrs = load_abbreviation_file(State.config.abbreviation_file)
    validate_combos(abbrs)

    for output in State.config.outputs:
        print(f"Running generator '{output}'")
        output = getattr(State.config.output_options, output)
        output.generate(abbrs)


if __name__ == "__main__":
    app()
