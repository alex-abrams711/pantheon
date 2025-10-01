"""CLI for Pantheon agents library."""

import click


@click.group()
@click.version_option(version="0.1.0", prog_name="pantheon")
def main():
    """Pantheon: Quality-focused agents library for Claude Code."""
    pass


if __name__ == "__main__":
    main()
