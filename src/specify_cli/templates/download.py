"""Template download and extraction utilities."""

import json
import os
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Optional, Tuple

import httpx
import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .discovery import find_local_template

console = Console()


def _github_auth_headers(cli_token: Optional[str] = None) -> dict:
    """Return Authorization header dict only when a non-empty token exists."""
    token = (
        (cli_token or os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN") or "").strip()
    ) or None
    return {"Authorization": f"Bearer {token}"} if token else {}


def handle_vscode_settings(
    sub_item: Path,
    dest_file: Path,
    rel_path: Path,
    verbose: bool = False,
    tracker=None,
    merge_json_files=None
) -> None:
    """Handle merging or copying of .vscode/settings.json files.

    Args:
        sub_item: Source file path
        dest_file: Destination file path
        rel_path: Relative path for logging
        verbose: Whether to print verbose output
        tracker: Optional StepTracker instance
        merge_json_files: Function to merge JSON files (injected dependency)
    """
    def log(message, color="green"):
        if verbose and not tracker:
            console.print(f"[{color}]{message}[/] {rel_path}")

    try:
        with open(sub_item, 'r', encoding='utf-8') as f:
            new_settings = json.load(f)

        if dest_file.exists():
            if merge_json_files:
                merged = merge_json_files(dest_file, new_settings, verbose=verbose and not tracker)
                with open(dest_file, 'w', encoding='utf-8') as f:
                    json.dump(merged, f, indent=4)
                    f.write('\n')
                log("Merged:", "green")
            else:
                shutil.copy2(sub_item, dest_file)
                log("Copied (merge_json_files not available):", "yellow")
        else:
            shutil.copy2(sub_item, dest_file)
            log("Copied (no existing settings.json):", "blue")

    except Exception as e:
        log(f"Warning: Could not merge, copying instead: {e}", "yellow")
        shutil.copy2(sub_item, dest_file)


def download_template_from_github(
    ai_assistant: str,
    download_dir: Path,
    *,
    script_type: str = "sh",
    verbose: bool = True,
    show_progress: bool = True,
    client: Optional[httpx.Client] = None,
    debug: bool = False,
    github_token: Optional[str] = None,
) -> Tuple[Path, dict]:
    """Download template from GitHub releases.

    Args:
        ai_assistant: AI assistant name (e.g., 'claude', 'copilot')
        download_dir: Directory to download template to
        script_type: Script type ('sh' or 'ps')
        verbose: Whether to print verbose output
        show_progress: Whether to show download progress
        client: Optional httpx.Client instance
        debug: Whether to print debug information
        github_token: Optional GitHub token for authentication

    Returns:
        Tuple of (zip_path, metadata_dict)
    """
    repo_owner = "github"
    repo_name = "spec-kit"

    # Import ssl_context from parent module if client not provided
    if client is None:
        import ssl
        import truststore
        ssl_context = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        client = httpx.Client(verify=ssl_context)

    if verbose:
        console.print("[cyan]Fetching latest release information...[/cyan]")
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"

    try:
        response = client.get(
            api_url,
            timeout=30,
            follow_redirects=True,
            headers=_github_auth_headers(github_token),
        )
        status = response.status_code
        if status != 200:
            msg = f"GitHub API returned {status} for {api_url}"
            if debug:
                msg += f"\nResponse headers: {response.headers}\nBody (truncated 500): {response.text[:500]}"
            raise RuntimeError(msg)
        try:
            release_data = response.json()
        except ValueError as je:
            raise RuntimeError(
                f"Failed to parse release JSON: {je}\nRaw (truncated 400): {response.text[:400]}"
            )
    except Exception as e:
        console.print(f"[red]Error fetching release information[/red]")
        console.print(Panel(str(e), title="Fetch Error", border_style="red"))
        raise typer.Exit(1)

    assets = release_data.get("assets", [])
    pattern = f"spec-kit-template-{ai_assistant}-{script_type}"
    matching_assets = [
        asset
        for asset in assets
        if pattern in asset["name"] and asset["name"].endswith(".zip")
    ]

    asset = matching_assets[0] if matching_assets else None

    if asset is None:
        console.print(
            f"[red]No matching release asset found[/red] for [bold]{ai_assistant}[/bold] "
            f"(expected pattern: [bold]{pattern}[/bold])"
        )
        asset_names = [a.get('name', '?') for a in assets]
        console.print(
            Panel("\n".join(asset_names) or "(no assets)", title="Available Assets", border_style="yellow")
        )
        raise typer.Exit(1)

    download_url = asset["browser_download_url"]
    filename = asset["name"]
    file_size = asset["size"]

    if verbose:
        console.print(f"[cyan]Found template:[/cyan] {filename}")
        console.print(f"[cyan]Size:[/cyan] {file_size:,} bytes")
        console.print(f"[cyan]Release:[/cyan] {release_data['tag_name']}")

    zip_path = download_dir / filename
    if verbose:
        console.print(f"[cyan]Downloading template...[/cyan]")

    try:
        with client.stream(
            "GET",
            download_url,
            timeout=60,
            follow_redirects=True,
            headers=_github_auth_headers(github_token),
        ) as response:
            if response.status_code != 200:
                body_sample = response.text[:400]
                raise RuntimeError(
                    f"Download failed with {response.status_code}\n"
                    f"Headers: {response.headers}\nBody (truncated): {body_sample}"
                )
            total_size = int(response.headers.get('content-length', 0))
            with open(zip_path, 'wb') as f:
                if total_size == 0:
                    for chunk in response.iter_bytes(chunk_size=8192):
                        f.write(chunk)
                else:
                    if show_progress:
                        with Progress(
                            SpinnerColumn(),
                            TextColumn("[progress.description]{task.description}"),
                            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                            console=console,
                        ) as progress:
                            task = progress.add_task("Downloading...", total=total_size)
                            downloaded = 0
                            for chunk in response.iter_bytes(chunk_size=8192):
                                f.write(chunk)
                                downloaded += len(chunk)
                                progress.update(task, completed=downloaded)
                    else:
                        for chunk in response.iter_bytes(chunk_size=8192):
                            f.write(chunk)
    except Exception as e:
        console.print(f"[red]Error downloading template[/red]")
        detail = str(e)
        if zip_path.exists():
            zip_path.unlink()
        console.print(Panel(detail, title="Download Error", border_style="red"))
        raise typer.Exit(1)

    if verbose:
        console.print(f"Downloaded: {filename}")

    metadata = {
        "filename": filename,
        "size": file_size,
        "release": release_data["tag_name"],
        "asset_url": download_url
    }
    return zip_path, metadata


def download_and_extract_template(
    project_path: Path,
    ai_assistant: str,
    script_type: str,
    is_current_dir: bool = False,
    *,
    verbose: bool = True,
    tracker=None,
    client: Optional[httpx.Client] = None,
    debug: bool = False,
    github_token: Optional[str] = None,
    merge_json_files=None,
) -> Path:
    """Download the latest release and extract it to create a new project.

    First attempts to use local template file from installation directory,
    then falls back to GitHub download.

    Args:
        project_path: Path to extract template to
        ai_assistant: AI assistant name (e.g., 'claude', 'copilot')
        script_type: Script type ('sh' or 'ps')
        is_current_dir: Whether extracting to current directory
        verbose: Whether to print verbose output
        tracker: Optional StepTracker instance (with keys: fetch, download, extract, cleanup)
        client: Optional httpx.Client instance
        debug: Whether to print debug information
        github_token: Optional GitHub token for authentication
        merge_json_files: Function to merge JSON files (injected dependency)

    Returns:
        Path to the extracted project
    """
    # Try to find local template first (searches installation directory)
    local_template = find_local_template(ai_assistant, script_type, verbose=verbose and tracker is None)

    if local_template:
        # Use local template
        zip_path = local_template
        if tracker:
            tracker.add("fetch", "Check for local template")
            tracker.complete("fetch", f"found {local_template.name}")
            tracker.add("download", "Download template")
            tracker.skip("download", "using local template")
        elif verbose:
            console.print(f"[green]Using local template:[/green] {local_template.name}")

        # Extract metadata from filename (e.g., spec-kit-template-claude-sh-v1.2.3.zip)
        version_match = re.search(r'-v(\d+\.\d+\.\d+)\.zip$', local_template.name)
        version = version_match.group(1) if version_match else "unknown"

        meta = {
            "filename": local_template.name,
            "size": local_template.stat().st_size,
            "release": f"v{version}",
            "asset_url": f"file://{local_template}",
            "source": "local"
        }
    else:
        # Fall back to GitHub download
        if tracker:
            tracker.add("fetch", "Check for local template")
            tracker.complete("fetch", "not found, downloading from GitHub")
        elif verbose:
            console.print("[cyan]No local template found, downloading from GitHub...[/cyan]")

        # Get current directory for download
        current_dir = Path.cwd()

        if tracker:
            tracker.start("fetch", "contacting GitHub API")
        try:
            zip_path, meta = download_template_from_github(
                ai_assistant,
                current_dir,
                script_type=script_type,
                verbose=verbose and tracker is None,
                show_progress=(tracker is None),
                client=client,
                debug=debug,
                github_token=github_token
            )
            meta["source"] = "github"
            if tracker:
                tracker.complete("fetch", f"release {meta['release']} ({meta['size']:,} bytes)")
                tracker.add("download", "Download template")
                tracker.complete("download", meta['filename'])
        except Exception as e:
            if tracker:
                tracker.error("fetch", str(e))
            else:
                if verbose:
                    console.print(f"[red]Error downloading template:[/red] {e}")
            raise

    if tracker:
        tracker.add("extract", "Extract template")
        tracker.start("extract")
    elif verbose:
        console.print("Extracting template...")

    try:
        if not is_current_dir:
            project_path.mkdir(parents=True)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_contents = zip_ref.namelist()
            if tracker:
                tracker.start("zip-list")
                tracker.complete("zip-list", f"{len(zip_contents)} entries")
            elif verbose:
                console.print(f"[cyan]ZIP contains {len(zip_contents)} items[/cyan]")

            if is_current_dir:
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)
                    zip_ref.extractall(temp_path)

                    extracted_items = list(temp_path.iterdir())
                    if tracker:
                        tracker.start("extracted-summary")
                        tracker.complete("extracted-summary", f"temp {len(extracted_items)} items")
                    elif verbose:
                        console.print(f"[cyan]Extracted {len(extracted_items)} items to temp location[/cyan]")

                    source_dir = temp_path
                    if len(extracted_items) == 1 and extracted_items[0].is_dir():
                        source_dir = extracted_items[0]
                        if tracker:
                            tracker.add("flatten", "Flatten nested directory")
                            tracker.complete("flatten")
                        elif verbose:
                            console.print(f"[cyan]Found nested directory structure[/cyan]")

                    for item in source_dir.iterdir():
                        dest_path = project_path / item.name
                        if item.is_dir():
                            if dest_path.exists():
                                if verbose and not tracker:
                                    console.print(f"[yellow]Merging directory:[/yellow] {item.name}")
                                for sub_item in item.rglob('*'):
                                    if sub_item.is_file():
                                        rel_path = sub_item.relative_to(item)
                                        dest_file = dest_path / rel_path
                                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                                        # Special handling for .vscode/settings.json - merge instead of overwrite
                                        if dest_file.name == "settings.json" and dest_file.parent.name == ".vscode":
                                            handle_vscode_settings(
                                                sub_item, dest_file, rel_path, verbose, tracker, merge_json_files
                                            )
                                        else:
                                            shutil.copy2(sub_item, dest_file)
                            else:
                                shutil.copytree(item, dest_path)
                        else:
                            if dest_path.exists() and verbose and not tracker:
                                console.print(f"[yellow]Overwriting file:[/yellow] {item.name}")
                            shutil.copy2(item, dest_path)
                    if verbose and not tracker:
                        console.print(f"[cyan]Template files merged into current directory[/cyan]")
            else:
                zip_ref.extractall(project_path)

                extracted_items = list(project_path.iterdir())
                if tracker:
                    tracker.start("extracted-summary")
                    tracker.complete("extracted-summary", f"{len(extracted_items)} top-level items")
                elif verbose:
                    console.print(f"[cyan]Extracted {len(extracted_items)} items to {project_path}:[/cyan]")
                    for item in extracted_items:
                        console.print(f"  - {item.name} ({'dir' if item.is_dir() else 'file'})")

                if len(extracted_items) == 1 and extracted_items[0].is_dir():
                    nested_dir = extracted_items[0]
                    temp_move_dir = project_path.parent / f"{project_path.name}_temp"

                    shutil.move(str(nested_dir), str(temp_move_dir))

                    project_path.rmdir()

                    shutil.move(str(temp_move_dir), str(project_path))
                    if tracker:
                        tracker.add("flatten", "Flatten nested directory")
                        tracker.complete("flatten")
                    elif verbose:
                        console.print(f"[cyan]Flattened nested directory structure[/cyan]")

    except Exception as e:
        if tracker:
            tracker.error("extract", str(e))
        else:
            if verbose:
                console.print(f"[red]Error extracting template:[/red] {e}")
                if debug:
                    console.print(Panel(str(e), title="Extraction Error", border_style="red"))

        if not is_current_dir and project_path.exists():
            shutil.rmtree(project_path)
        raise typer.Exit(1)
    else:
        if tracker:
            tracker.complete("extract")
    finally:
        if tracker:
            tracker.add("cleanup", "Remove temporary archive")

        # Only delete the zip if it was downloaded from GitHub (not a local template)
        should_delete = meta.get("source") == "github"

        if should_delete and zip_path.exists():
            zip_path.unlink()
            if tracker:
                tracker.complete("cleanup")
            elif verbose:
                console.print(f"Cleaned up: {zip_path.name}")
        else:
            if tracker:
                tracker.skip("cleanup", "local template preserved")
            elif verbose:
                console.print(f"[dim]Preserved local template: {zip_path.name}")

    return project_path
