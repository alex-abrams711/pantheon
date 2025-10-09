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
@click.pass_context
def init(ctx: click.Context, auto_integrate: bool) -> None:
    """Initialize Pantheon agents in your project.

    This command:
    - Creates .claude/agents/ directory
    - Copies DEV and QA agents to your project
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

    # Step 3: Copy agents (DEV + QA)
    package_agents_dir = Path(__file__).parent / "agents"
    agents_to_copy = ["dev.md", "qa.md"]

    for agent_file in agents_to_copy:
        agent_source = package_agents_dir / agent_file
        agent_dest = agents_dir / agent_file

        if agent_dest.exists():
            click.echo(f"⚠ {agent_dest.relative_to(cwd)} already exists (skipping)")
        else:
            shutil.copy2(agent_source, agent_dest)
            agent_name = agent_file.replace(".md", "").upper()
            click.echo(f"✓ Copied {agent_name} agent to {agent_dest.relative_to(cwd)}")

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
                "Would you like to integrate DEV agent with Spec Kit?", default=True
            )

        if should_integrate:
            click.echo("")
            ctx.invoke(integrate, dry_run=False)

    click.echo("\n✅ Initialization complete!")


@main.command()
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview changes without applying them",
)
def integrate(dry_run: bool) -> None:
    """Integrate DEV agent with Spec Kit commands and install quality infrastructure.

    This command:
    - Adds minimal integration directives to /implement, /plan, and /tasks commands
    - Updates CLAUDE.md with multi-agent workflow orchestration instructions
    - Installs quality gate hooks (SubagentStop, PreCommit, PhaseGate,
      OrchestratorCodeGate)

    NOTE: Quality config (.pantheon/quality-config.json) should be generated using the
    /pantheon:contextualize slash command in Claude Code for intelligent discovery.
    """
    from pantheon.integrations.claude import install_hooks, validate_hook_installation
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
            "validation": {"valid": False, "errors": [], "files_checked": []},
        }
    )

    if dry_run:
        # Show what would be done
        click.echo("Would create backup directory")
        click.echo("Would modify:")
        click.echo("  - .claude/commands/implement.md")
        click.echo("  - .claude/commands/plan.md")
        click.echo("  - .claude/commands/tasks.md")
        click.echo("  - CLAUDE.md")
        click.echo("\nWould install hooks:")
        click.echo("  - .pantheon/hooks/subagent-validation.sh (SubagentStop)")
        click.echo("  - .pantheon/hooks/pre-commit-gate.sh (PreCommit)")
        click.echo("  - .pantheon/hooks/phase-transition-gate.sh (PhaseGate)")
        click.echo("  - Update .claude/settings.json")
        click.echo(
            "\n💡 Use /pantheon:contextualize in Claude Code to "
            "generate quality-config.json"
        )
        return

    # Report Spec Kit integration results
    if result["success"]:
        click.echo("✅ Spec Kit integration successful!\n")
        if result["backup_dir"]:
            backup_path = result["backup_dir"].relative_to(cwd)
            click.echo(f"📦 Backup created: {backup_path}/\n")
        click.echo("Modified files:")
        for filename in result["files_modified"]:
            click.echo(f"  ✓ {filename}")
    else:
        click.echo("❌ Spec Kit integration failed!\n")
        for error in result["errors"]:
            click.echo(f"  • {error}")

        if result["backup_dir"]:
            backup_path = result["backup_dir"].relative_to(cwd)
            click.echo(f"\n📦 Backup available at: {backup_path}/")
            click.echo("   Run 'pantheon rollback' to restore")
        return

    # Integrate orchestration instructions into CLAUDE.md
    click.echo("\nIntegrating orchestration instructions...\n")
    from pantheon.integrations.spec_kit import integrate_claude_md

    try:
        if integrate_claude_md(cwd):
            click.echo("✓ CLAUDE.md updated with multi-agent workflow orchestration")
        else:
            click.echo("⚠️  Could not update CLAUDE.md")
    except Exception as e:
        click.echo(f"⚠️  CLAUDE.md integration warning: {e}")

    # Install quality hooks
    click.echo("\nInstalling quality gate hooks...\n")
    try:
        hook_results = install_hooks(cwd)

        # Validate installation
        validation = validate_hook_installation(cwd)

        # Report hook installation
        all_hooks_ok = all(status == "OK" for status in validation.values())

        if all_hooks_ok:
            click.echo("✅ Quality hooks installed successfully!\n")
            click.echo("Installed hooks:")
            for hook_name in hook_results.keys():
                click.echo(f"  ✓ {hook_name}")

            click.echo("\n💡 DEV agent is now integrated with Spec Kit")
            click.echo("   Quality hooks will validate work automatically")
            click.echo("   Run /implement to use DEV for task execution")
            click.echo(
                "\n💡 Next step: Generate quality config using "
                "/pantheon:contextualize in Claude Code"
            )
            click.echo(
                "   This will intelligently discover quality commands for your project"
            )
        else:
            click.echo("⚠️  Quality hooks installed with warnings:\n")
            for hook_name, status in validation.items():
                if status == "OK":
                    click.echo(f"  ✓ {hook_name}: {status}")
                else:
                    click.echo(f"  ⚠ {hook_name}: {status}")

    except FileNotFoundError as e:
        click.echo(f"❌ Hook installation failed: {e}")
        click.echo(
            "\n💡 Spec Kit integration completed, but hooks could not be installed"
        )
    except PermissionError as e:
        click.echo(f"❌ Hook installation failed: {e}")
        click.echo(
            "\n💡 Spec Kit integration completed, but hooks could not be installed"
        )


@main.command()
@click.option(
    "--force",
    is_flag=True,
    help="Skip confirmation prompt",
)
def rollback(force: bool) -> None:
    """Rollback to the most recent backup and uninstall quality hooks.

    Restores Spec Kit command files from the most recent integration backup
    and removes quality gate hooks.
    """
    from pantheon.integrations.claude import uninstall_hooks
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

    click.echo("\nHooks to remove:")
    click.echo("  • SubagentStop")
    click.echo("  • PreCommit")
    click.echo("  • PhaseGate")

    # Confirm unless --force
    if not force:
        click.echo()
        if not click.confirm("Restore files and remove hooks?"):
            click.echo("Rollback cancelled.")
            return

    # Perform rollback
    click.echo("\nRolling back...\n")
    result = rollback_integration(cwd)

    if result["success"]:
        click.echo("✅ Spec Kit rollback successful!\n")
        click.echo("Restored files:")
        for filename in result["files_restored"]:
            click.echo(f"  ✓ {filename}")
        if result["backup_dir"]:
            backup_path = result["backup_dir"].relative_to(cwd)
            click.echo(f"\n📦 Backup used: {backup_path}/")
    else:
        click.echo("❌ Spec Kit rollback failed!\n")
        for error in result["errors"]:
            click.echo(f"  • {error}")
        return

    # Uninstall hooks
    click.echo("\nRemoving quality hooks...\n")
    try:
        if uninstall_hooks(cwd):
            click.echo("✅ Quality hooks removed successfully!")
        else:
            click.echo("⚠️  Some hooks could not be removed")
    except FileNotFoundError:
        click.echo("⚠️  No .claude/ directory found - hooks already removed?")


if __name__ == "__main__":
    main()
