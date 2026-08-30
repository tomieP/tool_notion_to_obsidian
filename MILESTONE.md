Milestone 1 — Hiểu dữ liệu Notion
ZIP
 ↓
extract
 ↓
scan files
 ↓
identify pages
 ↓
extract page metadata
Milestone 2 — Page Index
Notion files
      ↓
PageIndex
      ↓
{
    notion_file → obsidian_file
}
Milestone 3 — Content Converter
Notion Markdown
      ↓
Clean Markdown
Milestone 4 — Internal Link Resolver
[Post](DOCS/Post xxx.md)
            ↓
       [[Post]]
Milestone 5 — Table
Notion exported table
          ↓
Obsidian Markdown table
Milestone 6 — Validator
converted vault
      ↓
check
 ├── missing pages
 ├── broken links
 ├── malformed tables
 └── duplicate filenames
Milestone 7 — CLI

Cuối cùng mới có:

notion-to-obsidian input.zip -o vault/