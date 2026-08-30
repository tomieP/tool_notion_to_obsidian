from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Page:
    """Represent a Notion page discovered in an export."""

    id: str
    title: str
    source_path: Path

    @property
    def parent_path(self) -> Path:
        """Return the directory containing the page."""
        return self.source_path.parent