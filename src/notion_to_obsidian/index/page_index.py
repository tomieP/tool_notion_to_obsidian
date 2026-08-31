from pathlib import Path

from ..parser.page import Page


class PageIndex:
    """Index Notion pages and their Obsidian destination paths."""

    def __init__(self, output_dir: str | Path = "."):
        self.output_dir = Path(output_dir)

        self._pages_by_id: dict[str, Page] = {}
        self._pages_by_title: dict[str, list[Page]] = {}

    def add(self, page: Page) -> None:
        """Add a page to the index.

        Raises:
            ValueError: If the Notion page ID already exists.
        """
        if page.id in self._pages_by_id:
            raise ValueError(
                f"Duplicate Notion page ID: {page.id}"
            )

        self._pages_by_id[page.id] = page
        self._pages_by_title.setdefault(page.title, []).append(page)

    def get_by_id(self, page_id: str) -> Page | None:
        """Return a page by its Notion ID."""
        return self._pages_by_id.get(page_id)

    def get_by_title(self, title: str) -> list[Page]:
        """Return all pages matching a title."""
        return self._pages_by_title.get(title, [])

    def obsidian_path(self, page_id: str) -> Path:
        """Return the destination path of a page in the Obsidian vault.

        The original directory structure is preserved while the
        Notion page ID is removed from the filename.
        """
        page = self.get_by_id(page_id)

        if page is None:
            raise KeyError(
                f"Unknown Notion page ID: {page_id}"
            )

        relative_path = page.source_path.with_name(
            f"{page.title}.md"
        )

        return self.output_dir / relative_path


    def get_all(self) -> list[Page]:
        """Return all indexed pages."""
        return list(self._pages_by_id.values())


    def __len__(self) -> int:
        """Return the number of indexed pages."""
        return len(self._pages_by_id)