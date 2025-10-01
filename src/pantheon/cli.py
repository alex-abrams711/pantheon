"""CLI for Pantheon agents library."""

import click
import shutil
from pathlib import Path

from pantheon import __version__


@click.group()
@click.version_option(version=__version__, prog_name="pantheon")
@click.pass_context
def main(ctx):
    """Pantheon: Quality-focused agents library for Claude Code.

    Pantheon provides production-ready agents with quality-focused workflows
    and seamless integration with frameworks like Spec Kit.
    """
    ctx.ensure_object(dict)


@main.command()
@click.option(
    "--auto-integrate",
    is_flag=True,
    help="Automatically integrate with Spec Kit if detected (skip prompt)",
)
def init(auto_integrate):
    """Initialize Pantheon agents in your project.

    This command:
    - Creates .claude/agents/ directory
    - Copies DEV agent to your project
    - Detects Spec Kit and offers integration
    """
    cwd = Path.cwd()
    claude_dir = cwd / ".claude"
    agents_dir = claude_dir / "agents"

    # Step 1: Ensure .claude/ directory exists
    if not claude_dir.exists():
        claude_dir.mkdir()
        click.echo(f"✓ Created {claude_dir.relative_to(cwd)}/")
    else:
        click.echo(f"✓ Found {claude_dir.relative_to(cwd)}/")

    # Step 2: Ensure .claude/agents/ directory exists
    if not agents_dir.exists():
        agents_dir.mkdir()
        click.echo(f"✓ Created {agents_dir.relative_to(cwd)}/")
    else:
        click.echo(f"✓ Found {agents_dir.relative_to(cwd)}/")

    # Step 3: Copy DEV agent
    package_agents_dir = Path(__file__).parent / "agents"
    dev_agent_source = package_agents_dir / "dev.md"
    dev_agent_dest = agents_dir / "dev.md"

    if dev_agent_dest.exists():
        click.echo(f"⚠ {dev_agent_dest.relative_to(cwd)} already exists (skipping)")
    else:
        shutil.copy2(dev_agent_source, dev_agent_dest)
        click.echo(f"✓ Copied DEV agent to {dev_agent_dest.relative_to(cwd)}")

    # Step 4: Detect Spec Kit
    specify_dir = cwd / ".specify"
    commands_dir = claude_dir / "commands"
    spec_kit_detected = specify_dir.exists() and commands_dir.exists()

    if spec_kit_detected:
        click.echo("\n🔍 Spec Kit detected!")

        if auto_integrate:
            should_integrate = True
        else:
            should_integrate = click.confirm(
                "Would you like to integrate DEV agent with Spec Kit?",
                default=True
            )

        if should_integrate:
            click.echo("\n💡 Run 'pantheon integrate' to add DEV agent integration to Spec Kit commands.")

    click.echo("\n✅ Initialization complete!")


@main.command()
def list():
    """List available agents and their installation status.

    Shows agents available in the Pantheon library and indicates
    which ones are installed locally in .claude/agents/
    """
    cwd = Path.cwd()
    agents_dir = cwd / ".claude" / "agents"

    # Get agents from package
    package_agents_dir = Path(__file__).parent / "agents"
    available_agents = []

    if package_agents_dir.exists():
        for agent_file in package_agents_dir.glob("*.md"):
            agent_name = agent_file.stem.upper()
            local_path = agents_dir / agent_file.name
            is_installed = local_path.exists()

            available_agents.append({
                "name": agent_name,
                "file": agent_file.name,
                "installed": is_installed
            })

    if not available_agents:
        click.echo("No agents available in Pantheon library.")
        return

    click.echo("Available Agents:\n")

    for agent in available_agents:
        status = "✓ installed" if agent["installed"] else "  not installed"
        click.echo(f"  {agent['name']:<10} ({agent['file']:<15}) [{status}]")

    if not agents_dir.exists():
        click.echo(f"\n💡 Run 'pantheon init' to install agents to {agents_dir.relative_to(cwd)}/")
    elif not any(a["installed"] for a in available_agents):
        click.echo(f"\n💡 Run 'pantheon init' to install agents")


if __name__ == "__main__":
    main()
