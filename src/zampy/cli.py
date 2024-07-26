"""Implements CLI interface for Zampy."""

from pathlib import Path
import click
import dask.distributed
from zampy.recipe import RecipeManager


@click.command()
@click.argument("recipe", type=click.Path(exists=True, path_type=Path))
@click.option("--skip-download", is_flag=True)
def run_recipe(recipe: Path, skip_download: bool) -> None:
    """Run the recipe using the CLI."""
    click.echo(f"Executing recipe: {recipe}")
    rm = RecipeManager(recipe, skip_download)
    rm.run()


if __name__ == "__main__":
    dask.distributed.Client()
    run_recipe()
