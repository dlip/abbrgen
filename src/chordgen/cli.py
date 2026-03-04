import logging
from chordgen.chord import load_chords_file, validate_chords
import typer
from pathlib import Path

from chordgen.config import DEFAULT_CONFIG, Config, load_or_create_config
from chordgen.gen import gen as run_gen


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
                f"Error: config {config} does not exist, run 'chordgen setup' to create it"
            )
            raise typer.Abort()

    loaded_config = load_or_create_config(config)
    if ctx.invoked_subcommand != "setup":
        if not loaded_config.chords_file.exists():
            print(
                f"Error: abrreviation file {loaded_config.chords_file} does not exist, run 'chordgen setup' to create it"
            )
            raise typer.Abort()

    State.config = loaded_config


@app.command()
def setup():
    print("Setup Complete")


@app.command()
def gen():
    run_gen(State.config)


@app.command()
def output():
    chords = load_chords_file(State.config.chords_file)
    validate_chords(chords)

    for output in State.config.outputs:
        print(f"Running output '{output}'")
        output = getattr(State.config.output_options, output)
        output.generate(chords)


if __name__ == "__main__":
    app(i)
