"""CLI for Pantheon agents library."""

import shutil
from pathlib import Path

import click

from pantheon import __version__


@click.group()
@click.version_option(version=__version__, prog_name="pantheon")
@click.pass_context
def main(ctx: click.Context) -> None:
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
def init(auto_integrate: bool) -> None:
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
            click.echo(
                "\n💡 Run 'pantheon integrate' to add DEV agent "
                "integration to Spec Kit commands."
            )

    click.echo("\n✅ Initialization complete!")


@main.command()
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview changes without applying them",
)
def integrate(dry_run: bool) -> None:
    """Integrate DEV agent with Spec Kit commands.

    Adds minimal integration directives to /implement, /plan, and /tasks
    commands to enable DEV agent delegation.
    """
    from pantheon.integrations.spec_kit import integrate_spec_kit

    cwd = Path.cwd()

    if dry_run:
        click.echo("🔍 Dry run mode - no changes will be made\n")

    # Run integration
    click.echo("Integrating DEV agent with Spec Kit...\n")

    from pantheon.integrations.spec_kit import IntegrationResult

    result: IntegrationResult = (
        integrate_spec_kit(cwd)
        if not dry_run
        else {
            "success": False,
            "backup_dir": None,
            "files_modified": [],
            "errors": ["Dry run mode"],
            "validation": {"valid": False, "errors": [], "files_checked": []}
        }
    )

    if dry_run:
        # Show what would be done
        click.echo("Would create backup directory")
        click.echo("Would modify:")
        click.echo("  - .claude/commands/implement.md")
        click.echo("  - .claude/commands/plan.md")
        click.echo("  - .claude/commands/tasks.md")
        return

    # Report results
    if result["success"]:
        click.echo("✅ Integration successful!\n")
        if result["backup_dir"]:
            backup_path = result["backup_dir"].relative_to(cwd)
            click.echo(f"📦 Backup created: {backup_path}/\n")
        click.echo("Modified files:")
        for filename in result["files_modified"]:
            click.echo(f"  ✓ {filename}")

        click.echo("\n💡 DEV agent is now integrated with Spec Kit")
        click.echo("   Run /implement to use DEV for task execution")
    else:
        click.echo("❌ Integration failed!\n")
        for error in result["errors"]:
            click.echo(f"  • {error}")

        if result["backup_dir"]:
            backup_path = result["backup_dir"].relative_to(cwd)
            click.echo(f"\n📦 Backup available at: {backup_path}/")
            click.echo("   Run 'pantheon rollback' to restore")


@main.command()
@click.option(
    "--force",
    is_flag=True,
    help="Skip confirmation prompt",
)
def rollback(force: bool) -> None:
    """Rollback to the most recent backup.

    Restores Spec Kit command files from the most recent integration backup.
    """
    from pantheon.integrations.spec_kit import find_latest_backup, rollback_integration

    cwd = Path.cwd()

    # Find backup first to show user what will be restored
    backup_dir = find_latest_backup(cwd)

    if not backup_dir:
        click.echo("❌ No backup found. Nothing to rollback.")
        return

    # Show what will be restored
    click.echo(f"📦 Found backup: {backup_dir.relative_to(cwd)}/\n")
    click.echo("Files to restore:")
    for backup_file in backup_dir.glob("*.md"):
        click.echo(f"  • {backup_file.name}")

    # Confirm unless --force
    if not force:
        click.echo()
        if not click.confirm("Restore these files from backup?"):
            click.echo("Rollback cancelled.")
            return

    # Perform rollback
    click.echo("\nRolling back...\n")
    result = rollback_integration(cwd)

    if result["success"]:
        click.echo("✅ Rollback successful!\n")
        click.echo("Restored files:")
        for filename in result["files_restored"]:
            click.echo(f"  ✓ {filename}")
        if result["backup_dir"]:
            backup_path = result["backup_dir"].relative_to(cwd)
            click.echo(f"\n📦 Backup used: {backup_path}/")
    else:
        click.echo("❌ Rollback failed!\n")
        for error in result["errors"]:
            click.echo(f"  • {error}")


@main.command()
def list() -> None:
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
        agents_path = agents_dir.relative_to(cwd)
        click.echo(f"\n💡 Run 'pantheon init' to install agents to {agents_path}/")
    elif not any(a["installed"] for a in available_agents):
        click.echo("\n💡 Run 'pantheon init' to install agents")


if __name__ == "__main__":
    main()
