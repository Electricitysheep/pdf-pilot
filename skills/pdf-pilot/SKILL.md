---
name: pdf-pilot
description: PDF conversion and extraction tool (Docling, MinerU, PyMuPDF). Automatically routes to the best engine for scanned pages, Chinese text, or complex tables. Outputs Markdown or Word (.docx).
---

# pdf_pilot

A multi-engine PDF converter that **automatically routes each document to the optimal engine**. No manual selection required.

- **3 Engines:** Docling (OCR/Math), MinerU (Chinese/Tables), PyMuPDF4LLM (Fast/Simple).
- **2 Outputs:** Markdown (`.md`) and Word (`.docx`).
- **Logic:** Detects scanned pages, language, and complexity to choose the best engine.

## Installation

```bash
pip install pdf-pilot
# Engines are optional:
pip install "pdf-pilot[docling]"  # OCR, formulas
pip install "pdf-pilot[mineru]"   # Chinese, complex tables
```

## CLI Usage

```bash
# Auto engine (recommended)
pdf_pilot input.pdf -o output.md

# Specific engine/format
pdf_pilot input.pdf -e [docling|mineru|pymupdf] -f [md|docx]

# Batch processing
pdf_pilot ./input_dir/ -o ./output_dir/

# List status
pdf_pilot --list-engines
```

## Python API

```python
from pdf_pilot import convert, Config

# Simple conversion
doc = convert("input.pdf", "output.md")

# Accessing content
print(doc.raw_markdown)
for block in doc.blocks:  # types: heading, paragraph, table, image, formula
    print(block.type, block.content)

# Tables & Images
for table in doc.tables: print(table.rows)
for img in doc.images: print(img.path)

# Advanced Config
config = Config(engine="docling", output_format="docx", verify_quality=True)
doc = convert("input.pdf", config=config)
```

## Engine Selection Strategy

| PDF Type | Default Engine | Reason |
|----------|----------------|--------|
| Scanned / OCR | `docling` | High-quality OCR & layout recovery |
| Chinese + Tables | `mineru` | Specialized in Chinese document structure |
| Simple / Digital | `pymupdf` | Fast, lightweight, no ML models |
| Academic / Math | `docling` | Built-in LaTeX formula recognition |

**Fallback:** If the preferred engine fails, pdf_pilot automatically retries with others in order.
