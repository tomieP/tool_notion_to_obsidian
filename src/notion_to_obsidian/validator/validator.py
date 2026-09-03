from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import re

from ..index.page_index import PageIndex


WIKILINK_PATTERN = re.compile(
    r"\[\[([^\[\]]+)\]\]"
)

TABLE_SEPARATOR_PATTERN = re.compile(
    r"^\s*\|?\s*:?-+:?\s*(?:\|\s*:?-+:?\s*)+\|?\s*$"
)


@dataclass(frozen=True)
class ValidationResult:
    """Represent the result of validating a converted vault."""

    missing_pages: list[str]
    broken_links: list[str]
    malformed_tables: list[str]
    duplicate_filenames: list[str]

    @property
    def is_valid(self) -> bool:
        """Return True if no validation errors were found."""
        return not any(
            [
                self.missing_pages,
                self.broken_links,
                self.malformed_tables,
                self.duplicate_filenames,
            ]
        )


class Validator:
    """Validate a converted Obsidian vault."""

    def validate(
        self,
        vault_path: str | Path,
        page_index: PageIndex,
    ) -> ValidationResult:
        """Validate the converted vault."""
        vault_path = Path(vault_path)

        missing_pages = self._find_missing_pages(
            page_index
        )

        broken_links = self._find_broken_links(
            vault_path
        )

        malformed_tables = self._find_malformed_tables(
            vault_path
        )

        duplicate_filenames = (
            self._find_duplicate_filenames(
                page_index
            )
        )

        return ValidationResult(
            missing_pages=missing_pages,
            broken_links=broken_links,
            malformed_tables=malformed_tables,
            duplicate_filenames=duplicate_filenames,
        )

    def _find_missing_pages(
        self,
        page_index: PageIndex,
    ) -> list[str]:
        """Find pages expected by the index but missing from the vault."""
        missing_pages = []

        for page in page_index.get_all():
            destination = page_index.obsidian_path(
                page.id
            )

            if not destination.exists():
                missing_pages.append(
                    str(destination)
                )

        return sorted(missing_pages)

    def _find_duplicate_filenames(
        self,
        page_index: PageIndex,
    ) -> list[str]:
        """Find destination paths shared by multiple pages."""
        destinations = [
            page_index.obsidian_path(page.id)
            for page in page_index.get_all()
        ]

        counts = Counter(destinations)

        return sorted(
            str(path)
            for path, count in counts.items()
            if count > 1
        )

    def _find_broken_links(
        self,
        vault_path: str | Path,
    ) -> list[str]:
        """Find wikilinks whose target page does not exist."""
        vault_path = Path(vault_path)

        broken_links = []

        for markdown_path in vault_path.rglob("*.md"):
            content = markdown_path.read_text(
                encoding="utf-8"
            )

            relative_path = markdown_path.relative_to(
                vault_path
            )

            for match in self._iter_valid_wikilinks(
                content
            ):
                raw_target = match.group(1)

                target = (
                    self._normalize_wikilink_target(
                        raw_target
                    )
                )

                if not target:
                    continue

                target_path = (
                    vault_path / f"{target}.md"
                )

                if not target_path.exists():
                    broken_links.append(
                        f"{relative_path}: [[{raw_target}]]"
                    )

        return sorted(broken_links)

    def _iter_valid_wikilinks(
        self,
        content: str,
    ):
        """Yield wikilink matches outside code blocks and inline code."""
        in_code_block = False
        fence_marker = None

        for line in content.splitlines():
            stripped = line.lstrip()

            if (
                stripped.startswith("```")
                or stripped.startswith("~~~")
            ):
                marker = stripped[:3]

                if not in_code_block:
                    in_code_block = True
                    fence_marker = marker

                elif marker == fence_marker:
                    in_code_block = False
                    fence_marker = None

                continue

            if in_code_block:
                continue

            for match in WIKILINK_PATTERN.finditer(
                line
            ):
                if self._is_inside_inline_code(
                    line,
                    match.start(),
                ):
                    continue

                yield match

    def _is_inside_inline_code(
        self,
        line: str,
        position: int,
    ) -> bool:
        """Return True when a position is inside inline code."""
        prefix = line[:position]

        return prefix.count("`") % 2 == 1

    def _normalize_wikilink_target(
        self,
        target: str,
    ) -> str:
        """Normalize a wikilink target into a vault-relative path."""
        target = target.split("|", 1)[0]
        target = target.split("#", 1)[0]
        target = target.strip()

        return target

    def _find_malformed_tables(
        self,
        vault_path: str | Path,
    ) -> list[str]:
        """Find malformed Markdown tables in the vault."""
        vault_path = Path(vault_path)

        malformed_tables = []

        for markdown_path in vault_path.rglob("*.md"):
            lines = markdown_path.read_text(
                encoding="utf-8"
            ).splitlines()

            relative_path = markdown_path.relative_to(
                vault_path
            )

            index = 0

            while index < len(lines) - 1:
                header = lines[index]
                separator = lines[index + 1]

                if not self._looks_like_table_row(
                    header
                ):
                    index += 1
                    continue

                if not self._looks_like_table_row(
                    separator
                ):
                    index += 1
                    continue

                if not self._is_table_separator(
                    separator
                ):
                    malformed_tables.append(
                        f"{relative_path}:{index + 2}"
                    )

                    index += 2
                    continue

                header_columns = (
                    self._count_table_columns(
                        header
                    )
                )

                if header_columns == 0:
                    index += 2
                    continue

                row_index = index + 2

                while (
                    row_index < len(lines)
                    and self._looks_like_table_row(
                        lines[row_index]
                    )
                ):
                    row_columns = (
                        self._count_table_columns(
                            lines[row_index]
                        )
                    )

                    if row_columns != header_columns:
                        malformed_tables.append(
                            f"{relative_path}:{row_index + 1}"
                        )

                    row_index += 1

                index = row_index

        return sorted(
            set(malformed_tables)
        )

    def _looks_like_table_row(
        self,
        line: str,
    ) -> bool:
        """Return True if a line looks like a Markdown table row."""
        stripped = line.strip()

        return (
            stripped.startswith("|")
            and stripped.endswith("|")
            and stripped.count("|") >= 2
        )

    def _is_table_separator(
        self,
        line: str,
    ) -> bool:
        """Return True if a line is a valid Markdown table separator."""
        return bool(
            TABLE_SEPARATOR_PATTERN.fullmatch(
                line
            )
        )

    def _count_table_columns(
        self,
        line: str,
    ) -> int:
        """Count columns in a Markdown table row."""
        stripped = line.strip()

        if stripped.startswith("|"):
            stripped = stripped[1:]

        if stripped.endswith("|"):
            stripped = stripped[:-1]

        if not stripped:
            return 0

        return len(
            stripped.split("|")
        )