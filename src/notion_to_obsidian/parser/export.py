from pathlib import Path
from zipfile import ZipFile


class NotionExport:
    """Represent a Notion ZIP export."""

    def __init__(self, zip_path: str | Path):
        self.zip_path = Path(zip_path)

        if not self.zip_path.exists():
            raise FileNotFoundError(
                f"Export file not found: {self.zip_path}"
            )

        if self.zip_path.suffix.lower() != ".zip":
            raise ValueError(
                f"Expected a ZIP file, got: {self.zip_path}"
            )

    def files(self) -> list[str]:
        """Return all file paths stored in the ZIP."""
        with ZipFile(self.zip_path, "r") as archive:
            return [
                name
                for name in archive.namelist()
                if not name.endswith("/")
            ]

    def pages(self) -> list[str]:
        """Return Markdown files representing Notion pages."""
        return [
            file
            for file in self.files()
            if Path(file).suffix.lower() == ".md"
        ]

    def assets(self) -> list[str]:
        """Return non-Markdown files stored in the export."""
        return [
            file
            for file in self.files()
            if Path(file).suffix.lower() != ".md"
        ]