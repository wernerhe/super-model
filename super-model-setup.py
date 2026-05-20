#!/usr/bin/env python3
"""super-model-setup - install Super-Model into a target project.

Usage:

    python super-model-setup.py [target-project-dir]

If no target is given, the parent of this script's directory is used.
The script refuses to run if that parent resolves to a filesystem root.

The 8 install modules run in order; each is idempotent so re-running
produces no diffs when nothing has changed.
"""

# Python version guard MUST use only Python 3.6-compatible syntax
# (no f-strings, no walrus operator, no PEP 604 unions). The guard
# itself must run cleanly under any Python 3 the user happens to have
# so they get an actionable error instead of a SyntaxError.
import sys

_MIN_PYTHON = (3, 11)
if sys.version_info < _MIN_PYTHON:
    sys.stderr.write(
        f"ERROR: super-model-setup requires Python {_MIN_PYTHON[0]}.{_MIN_PYTHON[1]}+ (you have {sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}).\n"
    )
    sys.stderr.write("Install a recent Python and re-run super-model-setup.\n")
    sys.exit(1)

# Imports below the guard. Annotations stay simple (plain types only,
# no PEP 585 generics, no PEP 604 unions) so the WHOLE file parses on
# Python 3.6 - otherwise the guard never gets a chance to print the
# friendly error and the user just sees a SyntaxError.
import json
import re
import shutil
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

USER_INVOKABLE_SKILLS = (
    "super-brainstorm",
    "super-code-review",
    "super-delete-branch",
    "super-mcp-builder",
    "super-model-setup",
    "super-prepare-branch",
    "super-visual-debug",
)

GITIGNORE_ENTRIES = (".super/cache/", ".worktrees/")

_MAX_DESCRIPTION_LEN = 256

CLAUDE_MD_TEMPLATE = """# Project guidance for Claude

This project uses **Super-Model** for AI-assisted development orchestration. Super-Model source lives at `{super_model_root}`.

## Available slash commands

- `/super-brainstorm` - design + spec + plan workflow before coding
- `/super-code-review` - comprehensive review at significant milestones
- `/super-prepare-branch` - verify branch is ready to merge / open a PR
- `/super-delete-branch` - safety-checked branch deletion
- `/super-model-setup` - re-run setup (e.g., to refresh slash commands)
- `/super-visual-debug` - visual fix/improve loop (3D, CAD, UI)
- `/super-mcp-builder` - install / inspect / configure MCP servers

## Configuration

- Per-project config: `.super/config.json` (created by `super-model-setup`)

Super-Model is per-project: there is no user-level / "global" config.
See `{super_model_root}/docs/architecture/config-cascade.md` for the
resolution model.

## Notes for Claude

- If a Super-Model skill says it requires an MCP, check whether the MCP is wired in `.mcp.json`. If not, point the user at `/super-mcp-builder` to discover and install one rather than trying to proceed without it.
- The SessionStart hook injects the `using-super-model` skill content automatically - no need to re-read it manually.

## Installation Policy

Do not install software, system packages, or language libraries
(pip, uv, pipx, poetry, conda, npm, yarn, pnpm, brew, winget, choco,
apt, dnf, etc.) without explicit approval. If an install is needed,
state what you want to install and why, and wait for confirmation.
"""

CANONICAL_INSTALL_RULES = [
    "Bash(pip install *)",
    "Bash(pip3 install *)",
    "Bash(uv pip install *)",
    "Bash(uv add *)",
    "Bash(pipx install *)",
    "Bash(poetry add *)",
    "Bash(conda install *)",
    "Bash(mamba install *)",
    "Bash(npm install *)",
    "Bash(npm i *)",
    "Bash(yarn add *)",
    "Bash(pnpm add *)",
    "Bash(brew install *)",
    "Bash(winget install *)",
    "Bash(choco install *)",
    "Bash(scoop install *)",
    "Bash(apt install *)",
    "Bash(apt-get install *)",
    "Bash(dnf install *)",
    "Bash(yum install *)",
]

_INSTALL_POLICY_HEADING = "## Installation Policy"
_INSTALL_POLICY_CLAUDE_MD_SECTION = """
## Installation Policy

Do not install software, system packages, or language libraries
(pip, uv, pipx, poetry, conda, npm, yarn, pnpm, brew, winget, choco,
apt, dnf, etc.) without explicit approval. If an install is needed,
state what you want to install and why, and wait for confirmation.
"""


# ---------------------------------------------------------------------------
# Path-resolution helpers
# ---------------------------------------------------------------------------


def _resolve_target_project(argv, super_source):
    """Determine the install target. Either argv[1] (if given) or the
    parent of super_source. Always returns an absolute Path."""
    if len(argv) > 1:
        return Path(argv[1]).expanduser().resolve()
    return super_source.parent.resolve()


def _refuse_drive_root(target):
    """Fail fast if target is a filesystem root.

    On Windows, target.anchor is like 'C:\\' and target.root is '\\\\'.
    On POSIX, target.anchor is '/' and target.root is also '/'.
    """
    target_str = str(target).rstrip("\\/")
    anchor = target.anchor.rstrip("\\/")
    if not target_str or target_str == anchor:
        raise SystemExit(
            f"ERROR: install target resolved to a filesystem root: {target}\n"
            "  Super-Model is installed per-project. Drop the Super-Model folder INSIDE\n"
            "  a project directory (e.g., C:\\my-project\\Super-Model\\) and re-run."
        )


# ---------------------------------------------------------------------------
# Per-module functions
# ---------------------------------------------------------------------------


def _init_claude_md(target, super_source):
    """Module 1: claude-md-init. Seed <target>/CLAUDE.md on first install."""
    claude_md = target / "CLAUDE.md"
    if claude_md.exists():
        existing = claude_md.read_text(encoding="utf-8")
        if _INSTALL_POLICY_HEADING.lower() in existing.lower():
            return "CLAUDE.md present; install-policy section already there"
        # Append install-policy section without touching other content.
        new_text = existing.rstrip() + "\n" + _INSTALL_POLICY_CLAUDE_MD_SECTION
        claude_md.write_text(new_text, encoding="utf-8")
        return "CLAUDE.md present; appended Installation Policy section"
    claude_md.write_text(
        CLAUDE_MD_TEMPLATE.format(super_model_root=str(super_source).replace("\\", "/")),
        encoding="utf-8",
    )
    return "created CLAUDE.md"


def _init_super_config(target):
    """Module 2: super-config-init. Create <target>/.super/config.json."""
    super_dir = target / ".super"
    super_dir.mkdir(parents=True, exist_ok=True)
    config = super_dir / "config.json"
    if config.exists():
        return ".super/config.json already present"
    config.write_text("{}\n", encoding="utf-8")
    return "created .super/config.json"


def _update_gitignore(target):
    """Module 3: gitignore-update. Append canonical entries with dedup."""
    gitignore = target / ".gitignore"
    existing = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
    lines = existing.splitlines()
    added = []
    for entry in GITIGNORE_ENTRIES:
        if entry not in lines:
            lines.append(entry)
            added.append(entry)
    if not added:
        return ".gitignore already has canonical entries"
    new_text = "\n".join(lines).rstrip() + "\n"
    gitignore.write_text(new_text, encoding="utf-8")
    return "appended {} entries to .gitignore: {}".format(len(added), ", ".join(added))


def _detect_project_type(target):
    """Module 4: project-type-detection. Read-only manifest inspection."""
    markers = [
        ("pyproject.toml", "Python (modern)"),
        ("setup.py", "Python (legacy)"),
        ("package.json", "Node / TypeScript"),
        ("Cargo.toml", "Rust"),
        ("go.mod", "Go"),
        ("pom.xml", "Java (Maven)"),
        ("build.gradle", "JVM (Gradle)"),
    ]
    detected = [name for (fname, name) in markers if (target / fname).exists()]
    if not detected:
        return "project type: unknown (no manifest detected)"
    return "project type: " + ", ".join(detected)


def _wire_mcp(target):
    """Module 5: mcp-wiring. Initialize <target>/.mcp.json (no source vendoring)."""
    project_mcp = target / ".mcp.json"
    if not project_mcp.exists():
        project_mcp.write_text(json.dumps({"mcpServers": {}}, indent=2) + "\n", encoding="utf-8")
        return "created .mcp.json (empty)"
    return ".mcp.json already present (not modified)"


def _install_hooks(target, super_source):
    """Module 6: hooks-install. Merge SessionStart entry into .claude/settings.json."""
    settings = _load_or_init_settings(target)
    settings.setdefault("hooks", {})
    if not isinstance(settings["hooks"], dict):
        settings["hooks"] = {}
    settings["hooks"].setdefault("SessionStart", [])
    if not isinstance(settings["hooks"]["SessionStart"], list):
        settings["hooks"]["SessionStart"] = []
    hook_command = '"{}" session-start'.format((super_source / "hooks" / "run-hook.cmd").as_posix())
    entry = {
        "matcher": "startup|clear|compact",
        "hooks": [{"type": "command", "command": hook_command, "async": False}],
    }
    # Dedup by command string within nested hooks.
    for existing in settings["hooks"]["SessionStart"]:
        for h in existing.get("hooks", []):
            if h.get("command") == hook_command:
                return "SessionStart hook already installed"
    settings["hooks"]["SessionStart"].append(entry)
    _save_settings(target, settings)
    return "added SessionStart hook to .claude/settings.json"


def _install_permissions(target):
    """Module 7: permissions-install. Merge canonical install-approval rules."""
    settings = _load_or_init_settings(target)
    settings.setdefault("permissions", {})
    if not isinstance(settings["permissions"], dict):
        settings["permissions"] = {}
    settings["permissions"].setdefault("ask", [])
    if not isinstance(settings["permissions"]["ask"], list):
        settings["permissions"]["ask"] = []
    ask = settings["permissions"]["ask"]
    # Ensure $defaults at position 0.
    if "$defaults" not in ask:
        ask.insert(0, "$defaults")
    added = 0
    for rule in CANONICAL_INSTALL_RULES:
        if rule not in ask:
            ask.append(rule)
            added += 1
    _save_settings(target, settings)
    if added == 0:
        return "install-approval rules already present"
    return f"added {added} install-approval rules to permissions.ask"


def _install_slash_commands(target, super_source):
    """Module 8: slash-commands-install. Write 7 super-* shim files to all 3 IDEs."""
    # Claude Code
    claude_cmds = target / ".claude" / "commands"
    claude_cmds.mkdir(parents=True, exist_ok=True)
    # Windsurf
    windsurf_workflows = target / ".windsurf" / "workflows"
    windsurf_workflows.mkdir(parents=True, exist_ok=True)
    windsurf_rules = target / ".windsurf" / "rules"
    windsurf_rules.mkdir(parents=True, exist_ok=True)
    # Cline
    cline_workflows = target / ".clinerules" / "workflows"
    cline_workflows.mkdir(parents=True, exist_ok=True)
    cline_root = target / ".clinerules"
    cline_root.mkdir(parents=True, exist_ok=True)

    drift_count = 0
    written_count = 0
    for skill in USER_INVOKABLE_SKILLS:
        source_shim = super_source / "commands" / f"{skill}.md"
        if not source_shim.exists():
            continue
        expected = source_shim.read_text(encoding="utf-8")
        for dest in (
            claude_cmds / f"{skill}.md",
            windsurf_workflows / f"{skill}.md",
            cline_workflows / f"{skill}.md",
        ):
            action = _write_shim_with_drift_check(dest, expected)
            if action == "wrote":
                written_count += 1
            elif action == "drift":
                drift_count += 1

    # Always-on rule body shared by Windsurf and Cline.
    rule_body = _super_model_rule_body(super_source)
    _write_shim_with_drift_check(windsurf_rules / "super-model.md", rule_body)
    _write_shim_with_drift_check(cline_root / "super-model.md", rule_body)

    if drift_count:
        return (
            f"wrote {written_count} slash-command files; {drift_count} user-edited files preserved"
        )
    return f"wrote {written_count} slash-command files across Claude / Windsurf / Cline"


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _load_or_init_settings(target):
    settings_path = target / ".claude" / "settings.json"
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    if settings_path.exists():
        try:
            return json.loads(settings_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            # Corrupt file - back it up and start fresh rather than crash.
            backup = settings_path.with_suffix(".json.bak")
            shutil.copy2(settings_path, backup)
            return {}
    return {}


def _save_settings(target, settings):
    settings_path = target / ".claude" / "settings.json"
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")


def _super_model_rule_body(super_source):
    """Body shared by .windsurf/rules/super-model.md and .clinerules/super-model.md.

    History: previously named _windsurf_rules_per_project_content; renamed
    when Cline support was added because the body is identical between
    the two IDEs (both serve as the always-on rule for their IDE).
    """
    lines = [
        "# Super-Model always-on rule",
        "",
        "This project uses Super-Model for AI-assisted development orchestration.",
        f"Super-Model source: `{super_source.as_posix()}`",
        "",
        "## Available slash commands",
        "",
    ]
    for skill in USER_INVOKABLE_SKILLS:
        lines.append(f"- `/{skill}`")
    lines.append("")
    lines.append("## Installation Policy")
    lines.append("")
    lines.append("Do not install software, system packages, or language libraries")
    lines.append("(pip, uv, pipx, poetry, conda, npm, yarn, pnpm, brew, winget, choco,")
    lines.append("apt, dnf, etc.) without explicit approval. If an install is needed,")
    lines.append("state what you want to install and why, and wait for confirmation.")
    lines.append("")
    lines.append("## User instructions still win")
    lines.append("")
    lines.append("The user's explicit instructions in this conversation override Super-Model's")
    lines.append("skill bodies. The 1% rule applies to skill DISCOVERY, not skill APPLICATION.")
    lines.append("")
    return "\n".join(lines)


def _load_skill_metadata(super_source, skill_name):
    """Read skills/<name>/SKILL.md frontmatter; return as dict.

    Used by slash-commands-install to mirror the description: from the
    source SKILL.md into the slash-command shim if drift is detected.
    """
    skill_md = super_source / "skills" / skill_name / "SKILL.md"
    if not skill_md.exists():
        return {}
    text = skill_md.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    fm = {}
    for line in parts[1].splitlines():
        m = re.match(r"^(\w+):\s*(.+)$", line.strip())
        if m:
            fm[m.group(1)] = m.group(2)
    return fm


def _detect_user_edits(existing_content, expected_content):
    """Drift heuristic: compare body past frontmatter against expected.

    Frontmatter description differences are NOT user edits (setup may
    ship updated descriptions). Body differences ARE user edits and
    must be preserved.
    """

    def _split_body(text):
        parts = text.split("---", 2)
        if len(parts) < 3:
            return text
        return parts[2].strip()

    return _split_body(existing_content) != _split_body(expected_content)


def _write_shim_with_drift_check(dest, expected_content):
    """Write expected_content to dest unless user edits are detected.

    Returns 'wrote' if file was created or updated, 'noop' if identical,
    'drift' if the existing file shows user edits to the body (preserve).
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        dest.write_text(expected_content, encoding="utf-8")
        return "wrote"
    existing = dest.read_text(encoding="utf-8")
    if existing == expected_content:
        return "noop"
    if _detect_user_edits(existing, expected_content):
        return "drift"
    # Body matches; only frontmatter differs - safe to rewrite.
    dest.write_text(expected_content, encoding="utf-8")
    return "wrote"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(argv=None):
    argv = argv if argv is not None else sys.argv
    super_source = Path(__file__).resolve().parent
    target = _resolve_target_project(argv, super_source)
    _refuse_drive_root(target)

    print("super-model-setup:")
    print(f"  source: {super_source}")
    print(f"  target: {target}")
    print()

    print("[Project root]")
    print("  " + _init_claude_md(target, super_source))
    print("  " + _init_super_config(target))
    print("  " + _update_gitignore(target))
    print("  " + _detect_project_type(target))
    print("  " + _wire_mcp(target))

    print()
    print("[Claude Code]")
    print("  " + _install_hooks(target, super_source))
    print("  " + _install_permissions(target))

    print()
    print("[Slash commands]")
    print("  " + _install_slash_commands(target, super_source))

    print()
    print("super-model-setup: done.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
