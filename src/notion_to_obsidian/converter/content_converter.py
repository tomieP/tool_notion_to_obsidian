import re


class ContentConverter:
    """Convert Notion-exported Markdown into clean Markdown."""

    def convert(self, content: str) -> str:
        """Convert raw Notion Markdown into clean Markdown."""
        content = self._normalize_line_endings(content)
        content = self._normalize_trailing_whitespace(content)
        content = self._remove_redundant_blank_lines(content)
        content = self._remove_trailing_blank_lines(content)

        return content

    def _normalize_line_endings(self, content: str) -> str:
        """Normalize all line endings to LF."""
        return content.replace("\r\n", "\n").replace("\r", "\n")

    def _normalize_trailing_whitespace(self, content: str) -> str:
        """Remove trailing spaces from each line."""
        return "\n".join(
            line.rstrip()
            for line in content.split("\n")
        )

    def _remove_redundant_blank_lines(self, content: str) -> str:
        """Collapse excessive consecutive blank lines."""
        return re.sub(r"\n{3,}", "\n\n", content)

    def _remove_trailing_blank_lines(self, content: str) -> str:
        """Ensure content ends with exactly one newline."""
        return content.rstrip() + "\n"