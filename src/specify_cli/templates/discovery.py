"""Template discovery utilities for local and remote templates."""

import re
from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()


def get_installation_templates_dir() -> Path:
    """Get the path to the spec-kit-templates directory within the installation.

    Returns:
        Path to the spec-kit-templates directory (may not exist yet)
    """
    # Get the directory where this module is located
    # Works for both regular install and editable install (pip install -e .)
    package_dir = Path(__file__).parent.parent
    templates_dir = package_dir / "spec-kit-templates"
    return templates_dir


def find_local_template(
    ai_assistant: str,
    script_type: str,
    search_dir: Optional[Path] = None,
    verbose: bool = False
) -> Optional[Path]:
    """Find local template zip file matching pattern spec-kit-template-{agent}-{script}-v{version}.zip

    Searches in the following order:
    1. Installation templates directory (src/specify_cli/spec-kit-templates/)
    2. Optional search_dir if provided (for backward compatibility)

    Args:
        ai_assistant: AI assistant name (e.g., 'claude', 'copilot')
        script_type: Script type ('sh' or 'ps')
        search_dir: Optional additional directory to search (deprecated, for backward compatibility)
        verbose: Whether to print search information

    Returns:
        Path to the latest matching template file, or None if not found
    """
    pattern = f"spec-kit-template-{ai_assistant}-{script_type}-v"
    version_pattern = re.compile(
        rf"^spec-kit-template-{re.escape(ai_assistant)}-{re.escape(script_type)}-v(\d+\.\d+\.\d+)\.zip$"
    )

    # Determine search directories (installation dir first)
    installation_dir = get_installation_templates_dir()
    search_dirs = [installation_dir]
    if search_dir and search_dir != installation_dir:
        search_dirs.append(search_dir)

    if verbose:
        for dir_path in search_dirs:
            if dir_path.exists():
                console.print(
                    f"[cyan]Searching for local template:[/cyan] {pattern}*.zip in {dir_path}"
                )

    all_matching_files = []

    for dir_path in search_dirs:
        if not dir_path.exists():
            continue

        for file in dir_path.glob(f"{pattern}*.zip"):
            match = version_pattern.match(file.name)
            if match:
                version_str = match.group(1)
                # Parse semantic version (major.minor.patch)
                try:
                    version_parts = tuple(map(int, version_str.split('.')))
                    all_matching_files.append((file, version_parts, version_str))
                except ValueError:
                    continue

    if not all_matching_files:
        if verbose:
            console.print(
                f"[yellow]No local template found matching pattern:[/yellow] {pattern}*.zip"
            )
            console.print(
                f"[dim]Searched in: {', '.join(str(d) for d in search_dirs if d.exists())}[/dim]"
            )
        return None

    # Sort by version (descending) and get the latest
    all_matching_files.sort(key=lambda x: x[1], reverse=True)
    latest_file, _, version_str = all_matching_files[0]

    if verbose:
        console.print(
            f"[green]Found local template:[/green] {latest_file.name} (v{version_str})"
        )
        console.print(f"[dim]Location: {latest_file.parent}[/dim]")
        if len(all_matching_files) > 1:
            console.print(
                f"[dim]Other versions available: {', '.join(f.name for f, _, _ in all_matching_files[1:])}"
            )

    return latest_file
