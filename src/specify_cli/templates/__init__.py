"""Template management for Specify CLI."""

from .discovery import get_installation_templates_dir, find_local_template
from .download import download_template_from_github, download_and_extract_template

__all__ = [
    "get_installation_templates_dir",
    "find_local_template",
    "download_template_from_github",
    "download_and_extract_template",
]
