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
    from pathlib import Path

from ..index.page_index import PageIndex
from .export import NotionExport
from .page import Page
from .page_parser import PageParser


class ExportParser:
    """Parse pages from a Notion export."""

    def __init__(
        self,
        export: NotionExport,
        page_parser: PageParser | None = None,
    ):
        self.export = export
        self.page_parser = page_parser or PageParser()

    def parse_pages(self) -> list[Page]:
        """Parse all Markdown pages in the export."""
        return [
            self.page_parser.parse(Path(path))
            for path in self.export.pages()
        ]

    def build_index(
        self,
        output_dir: str | Path = ".",
    ) -> PageIndex:
        """Build a page index from the export."""
        index = PageIndex(output_dir)

        for page in self.parse_pages():
            index.add(page)

        return index