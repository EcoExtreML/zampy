"""Implements CLI interface for Zampy."""
import click
from zampy.recipe import RecipeManager


@click.command()
@click.option(
    "--filename",
    prompt="Path to the recipe filename",
    help="Path to the recipe filename.",
)
def run_recipe(filename: str) -> None:
    """Run the recipe using the CLI."""
    click.echo(f"Executing recipe: {filename}")
    rm = RecipeManager(filename)
    rm.run()


if __name__ == "__main__":
    run_recipe()
