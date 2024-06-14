"""Implements CLI interface for Zampy."""
from pathlib import Path
import click
import dask.distributed
from zampy.recipe import RecipeManager


@click.command()
@click.argument("recipe", type=click.Path(exists=True, path_type=Path))
def run_recipe(recipe: Path) -> None:
    """Run the recipe using the CLI."""
    click.echo(f"Executing recipe: {recipe}")
    rm = RecipeManager(recipe)
    rm.run()


if __name__ == "__main__":
    dask.distributed.Client()
    run_recipe()
