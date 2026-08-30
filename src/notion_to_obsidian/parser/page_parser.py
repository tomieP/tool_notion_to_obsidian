import re
from pathlib import Path

from .page import Page


NOTION_ID_PATTERN = re.compile(
    r"^(?P<title>.+)\s(?P<id>[0-9a-f]{32})$",
    re.IGNORECASE,
)


class PageParser:
    """Parse Notion page metadata from an exported Markdown path."""

    def parse(self, source_path: str | Path) -> Page:
        source_path = Path(source_path)

        if source_path.suffix.lower() != ".md":
            raise ValueError(
                f"Expected a Markdown page, got: {source_path}"
            )

        match = NOTION_ID_PATTERN.match(source_path.stem)

        if match is None:
            raise ValueError(
                f"Could not parse Notion page ID from: {source_path.name}"
            )

        return Page(
            id=match.group("id"),
            title=match.group("title"),
            source_path=source_path,
        )