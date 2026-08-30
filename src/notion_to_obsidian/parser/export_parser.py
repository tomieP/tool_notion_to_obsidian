from pathlib import Path

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