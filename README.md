# TABLE OF CONTENT

1. [ROADMAP](#roadmap)
2. [ARCHITECTURE](#architecture)
3. [WORK FLOW](#work-flow)

# 1. ROADMAP
```
STEP 1
↓
Export Notion
↓
STEP 2
↓
Phân tích cấu trúc export
↓
STEP 3
↓
Xây page mapping
↓
STEP 4
↓
Convert → Markdown
↓
STEP 5
↓
Convert tables
↓
STEP 6
↓
Resolve Notion links → [[wikilinks]]
↓
STEP 7
↓
Normalize filenames
↓
STEP 8
↓
Generate migration report
↓
STEP 9
↓
Import vào Obsidian
↓
STEP 10
↓
Kiểm tra broken links
↓
STEP 11
↓
Gắn hình ảnh thủ công
↓
STEP 12
↓
Thiết kế Second Brain
```
# 2. ARCHITECTURE
```
notion-to-obsidian/
│
├── src/
│   └── notion_to_obsidian/
│       ├── __init__.py
│       ├── cli.py
│       ├── parser/
│       ├── converter/
│       ├── resolver/
│       ├── validator/
│       └── report/
│
├── tests/
├── examples/
├── README.md
├── pyproject.toml
└── .gitignore
```

# 3. WORK FLOW

```
                    NOTION
                       │
                       │ Export ZIP
                       ▼
              ┌──────────────────┐
              │ Migration Engine │
              └────────┬─────────┘
                       │
          ┌────────────┼────────────┐
          ↓            ↓            ↓
      Content       Tables        Links
          │            │            │
          │            │            ↓
          │            │       [[Wikilinks]]
          │            │
          └────────────┴────────────┐
                                    ↓
                              Clean Markdown
                                    │
                                    ↓
                              OBSIDIAN VAULT
                                    │
                         ┌──────────┼──────────┐
                         ↓          ↓          ↓
                     Backlinks     MOC       Graph
                         │          │          │
                         └──────────┼──────────┘
                                    ↓
                              SECOND BRAIN
```