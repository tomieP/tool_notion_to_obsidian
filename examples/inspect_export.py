from src.notion_to_obsidian.parser.export import NotionExport
from src.notion_to_obsidian.parser.export_parser import ExportParser


export = NotionExport(
    r".\ExportBlock-5cc2a77c-12fd-4a88-892a-152531173594-Part-1.zip"
)

parser = ExportParser(export)

pages = parser.parse_pages()

print(f"TOTAL PAGES: {len(pages)}")

for page in pages:
    print(
        f"- title={page.title!r} "
        f"id={page.id} "
        f"path={page.source_path}"
    )