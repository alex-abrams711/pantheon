"""CLI for Pantheon agents library."""

from pathlib import Path

import click

from pantheon import __version__
from pantheon.agents import install_agents
from pantheon.commands import install_commands
from pantheon.hooks import install_hooks, validate_hook_installation


@click.group()
@click.version_option(version=__version__, prog_name="pantheon")
@click.pass_context
def main(ctx: click.Context) -> None:
    """Pantheon: Quality-focused agents library for Claude Code.

    Pantheon provides production-ready DEV and QA agents with quality-focused
    workflows for building features with guaranteed quality.
    """
    ctx.ensure_object(dict)


@main.command()
def init() -> None:
    """Initialize Pantheon agents in your project.

    This command:
    - Creates .claude/agents/ directory
    - Copies DEV and QA agents to your project
    - Installs /pantheon:contextualize slash command
    - Installs quality gate hooks
    """
    cwd = Path.cwd()
    claude_dir = cwd / ".claude"

    # Step 1: Ensure .claude/ directory exists
    if not claude_dir.exists():
        claude_dir.mkdir()
        click.echo(f"✓ Created {claude_dir.relative_to(cwd)}/")
    else:
        click.echo(f"✓ Found {claude_dir.relative_to(cwd)}/")

    # Step 2: Install agents
    click.echo("\nInstalling agents...")
    try:
        agent_results = install_agents(cwd)

        # Report agent installation
        for agent_name, status in agent_results.items():
            if status == "copied":
                click.echo(f"✓ Copied {agent_name.upper()} agent")
            elif status == "skipped":
                click.echo(
                    f"⚠ {agent_name}.md already exists (skipping)"
                )
            else:  # failed
                click.echo(f"⚠️  Failed to copy {agent_name.upper()} agent")

    except FileNotFoundError as e:
        click.echo(f"⚠️  Could not install agents: {e}")
    except PermissionError as e:
        click.echo(f"⚠️  Permission error installing agents: {e}")
    except Exception as e:
        click.echo(f"⚠️  Unexpected error installing agents: {e}")

    # Step 3: Install commands
    click.echo("\nInstalling commands...")
    try:
        command_results = install_commands(cwd)

        # Report command installation
        for command_name, success in command_results.items():
            if success:
                click.echo(f"✓ Installed /pantheon:{command_name} command")
            else:
                click.echo(f"⚠️  Failed to install /pantheon:{command_name} command")

    except FileNotFoundError as e:
        click.echo(f"⚠️  Could not install commands: {e}")
    except PermissionError as e:
        click.echo(f"⚠️  Permission error installing commands: {e}")
    except Exception as e:
        click.echo(f"⚠️  Unexpected error installing commands: {e}")

    # Step 4: Install quality gate hooks
    click.echo("\nInstalling quality gate hooks...")
    try:
        install_hooks(cwd)

        # Validate installation
        validation = validate_hook_installation(cwd)

        # Report hook installation
        all_hooks_ok = all(status == "OK" for status in validation.values())

        if all_hooks_ok:
            click.echo("✓ Quality hooks installed successfully")
        else:
            click.echo("⚠️  Quality hooks installed with warnings:")
            for hook_name, status in validation.items():
                if status != "OK":
                    click.echo(f"  • {hook_name}: {status}")

    except FileNotFoundError as e:
        click.echo(f"⚠️  Could not install hooks: {e}")
    except PermissionError as e:
        click.echo(f"⚠️  Permission error installing hooks: {e}")
    except Exception as e:
        click.echo(f"⚠️  Unexpected error installing hooks: {e}")

    click.echo("\n✅ Initialization complete!")
    click.echo("\n💡 Next steps:")
    click.echo("  1. Run: /pantheon:contextualize")
    click.echo("     (Generates .pantheon/quality-config.json and quality-report.sh)")
    click.echo("  2. Use DEV agent to implement features")
    click.echo("  3. Use QA agent to validate work")


if __name__ == "__main__":
    main()
