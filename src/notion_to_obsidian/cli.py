import argparse
from pathlib import Path

from .converter.content_converter import ContentConverter
from .converter.table_converter import TableConverter
from .index.page_index import PageIndex
from .parser.export import NotionExport
from .parser.export_parser import ExportParser
from .resolver.link_resolver import LinkResolver
from .validator.validator import Validator


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="notion-to-obsidian",
        description="Convert a Notion export ZIP into an Obsidian vault.",
    )

    parser.add_argument(
        "input",
        help="Path to the Notion export ZIP file.",
    )

    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Path to the output Obsidian vault.",
    )

    return parser


def migrate(
    input_path: str | Path,
    output_path: str | Path,
):
    """Convert a Notion export into an Obsidian vault."""
    export = NotionExport(input_path)
    parser = ExportParser(export)

    pages = parser.parse_pages()

    page_index = PageIndex(output_path)

    for page in pages:
        page_index.add(page)

    content_converter = ContentConverter()
    table_converter = TableConverter()
    link_resolver = LinkResolver(page_index)

    for page in pages:
        content = export.read(
            str(page.source_path)
        )

        content = content_converter.convert(
            content
        )

        content = table_converter.convert(
            content
        )

        content = link_resolver.resolve(
            content
        )

        destination = page_index.obsidian_path(
            page.id
        )

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination.write_text(
            content,
            encoding="utf-8",
        )

    validator = Validator()

    validation_result = validator.validate(
        output_path,
        page_index,
    )

    return page_index, validation_result


def format_validation_report(
    page_count: int,
    output_path: str | Path,
    validation_result,
) -> str:
    """Format migration and validation results for the CLI."""
    lines = [
        "Migration completed.",
        f"Pages: {page_count}",
        f"Output: {output_path}",
    ]

    if validation_result.is_valid:
        lines.append("Validation: PASSED")
        return "\n".join(lines)

    lines.append("Validation: FAILED")

    error_groups = [
        ("Missing pages:", validation_result.missing_pages),
        ("Broken links:", validation_result.broken_links),
        (
            "Malformed tables:",
            validation_result.malformed_tables,
        ),
        (
            "Duplicate filenames:",
            validation_result.duplicate_filenames,
        ),
    ]

    for heading, errors in error_groups:
        if not errors:
            continue

        lines.append("")
        lines.append(heading)

        for error in errors:
            lines.append(f"  {error}")

    return "\n".join(lines)


def main() -> int:
    """Run the command-line interface."""
    parser = build_parser()
    args = parser.parse_args()

    page_index, validation_result = migrate(
        args.input,
        args.output,
    )

    print(
        format_validation_report(
            page_count=len(page_index),
            output_path=args.output,
            validation_result=validation_result,
        )
    )

    return 0 if validation_result.is_valid else 1