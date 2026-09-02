import re


TABLE_SEPARATOR_PATTERN = re.compile(
    r"^\s*\|?\s*:?-+:?\s*(?:\|\s*:?-+:?\s*)*\|?\s*$"
)


class TableConverter:
    """Convert Notion-exported Markdown tables into normalized Markdown tables."""

    def convert(self, content: str) -> str:
        """Convert all Markdown tables found in the content."""
        lines = content.splitlines()

        result: list[str] = []
        index = 0

        while index < len(lines):
            if self._is_table_start(lines, index):
                table_lines, next_index = self._collect_table(
                    lines,
                    index,
                )

                result.extend(
                    self._convert_table(table_lines)
                )

                index = next_index
                continue

            result.append(lines[index])
            index += 1

        return "\n".join(result) + "\n"

    def _is_table_start(
        self,
        lines: list[str],
        index: int,
    ) -> bool:
        """Return whether the current position starts a Markdown table."""
        if index + 1 >= len(lines):
            return False

        return (
            self._is_table_candidate(lines[index])
            and self._is_separator_row(lines[index + 1])
        )

    def _is_table_candidate(self, line: str) -> bool:
        """Return whether a line can start a Markdown table."""
        stripped = line.strip()

        return (
            stripped.startswith("|")
            and stripped.count("|") >= 2
        )

    def _is_table_row(self, line: str) -> bool:
        """Return whether a complete Markdown table row is present."""
        stripped = line.strip()

        return (
            stripped.startswith("|")
            and stripped.endswith("|")
            and stripped.count("|") >= 2
        )

    def _is_separator_row(self, line: str) -> bool:
        """Return whether a line is a Markdown table separator."""
        return bool(TABLE_SEPARATOR_PATTERN.match(line))

    def _collect_table(
        self,
        lines: list[str],
        start: int,
    ) -> tuple[list[str], int]:
        """Collect physical lines belonging to one table."""
        table_lines = [
            lines[start],
            lines[start + 1],
        ]

        index = start + 2
        row_is_open = False

        while index < len(lines):
            line = lines[index]

            if not line.strip():
                break

            stripped = line.strip()

            # A new table row starts with "|".
            if stripped.startswith("|"):
                table_lines.append(line)

                # A row is complete only when it also ends with "|".
                row_is_open = not stripped.endswith("|")

                index += 1
                continue

            # Continuation of an unfinished table row.
            if row_is_open:
                table_lines.append(line)

                if stripped.endswith("|"):
                    row_is_open = False

                index += 1
                continue

            # Indented content is also considered continuation content.
            if line.startswith((" ", "\t")):
                table_lines.append(line)
                index += 1
                continue

            break

        return table_lines, index

    def _convert_table(self, lines: list[str]) -> list[str]:
        """Convert physical table lines into normalized logical rows."""
        header = self._parse_row(lines[0])
        column_count = len(header)

        rows: list[list[str]] = [header]
        current_row: list[str] | None = None

        for line in lines[2:]:
            stripped = line.strip()

            # A line beginning with "|" starts a new logical row.
            if stripped.startswith("|"):
                current_row = self._parse_row(
                    line,
                    column_count=column_count,
                )
                rows.append(current_row)
                continue

            # Any non-empty line after a row starts is continuation
            # content for the final cell.
            if current_row is not None and stripped:
                self._append_multiline_content(
                    current_row,
                    line,
                )

        normalized_rows = [
            self._normalize_row(
                row,
                column_count,
            )
            for row in rows
        ]

        separator = ["---"] * column_count

        return [
            self._render_row(normalized_rows[0]),
            self._render_row(separator),
            *[
                self._render_row(row)
                for row in normalized_rows[1:]
            ],
        ]

    def _parse_row(
        self,
        line: str,
        column_count: int | None = None,
    ) -> list[str]:
        """Parse a physical table row into cells."""
        stripped = line.strip()

        if stripped.startswith("|"):
            stripped = stripped[1:]

        if stripped.endswith("|"):
            stripped = stripped[:-1]

        # A one-column table may legitimately contain "|" inside
        # the cell content.
        if column_count == 1:
            return [stripped.strip()]

        return [
            cell.strip()
            for cell in stripped.split("|")
        ]

    def _append_multiline_content(
        self,
        row: list[str],
        line: str,
    ) -> None:
        """Append continuation content to the final cell."""
        content = line.strip()

        if not content or not row:
            return

        # The closing "|" belongs to the table syntax, not the cell.
        if content.endswith("|"):
            content = content[:-1].rstrip()

        row[-1] = self._join_multiline_cell(
            row[-1],
            content,
        )

    def _join_multiline_cell(
        self,
        existing: str,
        continuation: str,
    ) -> str:
        """Join multiline content with a Markdown line break."""
        if not existing:
            return continuation

        return f"{existing}<br>{continuation}"

    def _normalize_row(
        self,
        row: list[str],
        column_count: int,
    ) -> list[str]:
        """Normalize row width and escape cell content."""
        if len(row) < column_count:
            row = row + [""] * (
                column_count - len(row)
            )

        if len(row) > column_count:
            row = row[:column_count]

        return [
            self._escape_cell(cell)
            for cell in row
        ]

    def _escape_cell(self, cell: str) -> str:
        """Escape pipe characters inside a table cell."""
        return cell.replace("|", r"\|")

    def _render_row(self, cells: list[str]) -> str:
        """Render cells as a Markdown table row."""
        return "| " + " | ".join(cells) + " |"