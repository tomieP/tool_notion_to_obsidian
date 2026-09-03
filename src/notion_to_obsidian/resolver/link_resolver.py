import re
from urllib.parse import unquote

from ..index.page_index import PageIndex


NOTION_PAGE_ID_PATTERN = re.compile(
    r"(?P<title>.+?)\s(?P<id>[0-9a-f]{32})\.md$",
    re.IGNORECASE,
)


def _iter_markdown_links(content: str):
    """Yield Markdown links from content.

    Supports parentheses inside link targets.

    Example:

        [Public](Post/API%20(Public)%203c3178....md)

    Yields:

        (start, end, label, target)
    """

    i = 0

    while i < len(content):
        if content[i] != "[":
            i += 1
            continue

        label_end = content.find("]", i + 1)

        if label_end == -1:
            i += 1
            continue

        if label_end + 1 >= len(content):
            i += 1
            continue

        if content[label_end + 1] != "(":
            i += 1
            continue

        target_start = label_end + 2
        j = target_start
        depth = 0

        while j < len(content):
            char = content[j]

            if char == "(":
                depth += 1

            elif char == ")":
                if depth == 0:
                    break

                depth -= 1

            j += 1

        if j >= len(content):
            i += 1
            continue

        label = content[i + 1:label_end]
        target = content[target_start:j]

        yield i, j + 1, label, target

        i = j + 1


class LinkResolver:
    """Resolve Notion internal Markdown links into Obsidian wikilinks."""

    def __init__(self, page_index: PageIndex):
        self.page_index = page_index

    def resolve(self, content: str) -> str:
        """Resolve all known internal page links in Markdown content."""

        replacements = []

        for start, end, _label, target in _iter_markdown_links(content):
            parsed = self._parse_internal_link(target)

            if parsed is None:
                continue

            page_id, anchor = parsed

            page = self.page_index.get_by_id(page_id)

            if page is None:
                continue

            replacement = f"[[{page.title}"

            if anchor:
                replacement += f"#{anchor}"

            replacement += "]]"

            replacements.append(
                (start, end, replacement)
            )

        # Replace from right to left so that the original
        # positions remain valid.
        for start, end, replacement in reversed(replacements):
            content = (
                content[:start]
                + replacement
                + content[end:]
            )

        return content

    def _parse_internal_link(
        self,
        target: str,
    ) -> tuple[str, str | None] | None:
        """Parse a Notion internal page link.

        Returns:
            (page_id, anchor)

        Returns None for:
            - external URLs
            - non-page links
            - invalid targets
        """

        # External URLs must never be treated as internal
        # Notion page links, even if they contain a 32-character
        # hexadecimal string.
        if re.match(
            r"^[a-z][a-z0-9+.-]*://",
            target,
            re.IGNORECASE,
        ):
            return None

        # Decode URL-encoded filenames.
        decoded_target = unquote(target)

        # Extract anchor before matching the .md filename.
        anchor = None

        if "#" in decoded_target:
            decoded_target, anchor = decoded_target.split(
                "#",
                1,
            )

        match = NOTION_PAGE_ID_PATTERN.search(decoded_target)

        if match is None:
            return None

        page_id = match.group("id")

        return page_id, anchor