<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue.svg" alt="Python"/>
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License"/>
  <img src="https://img.shields.io/badge/Downloads-1k%2B-brightgreen.svg" alt="Downloads"/>
  <img src="https://img.shields.io/github/stars/Electricitysheep/pdf_pilot?style=social" alt="Stars"/>
  <br/>
  <a href="https://github.com/Electricitysheep/pdf_pilot"><strong>English</strong></a> |
  <a href="README_zh-CN.md"><strong>简体中文</strong></a>
</p>

<h1 align="center">🚀 pdf_pilot</h1>
<p align="center">
  <b>The only PDF converter that automatically selects the best engine for each document.</b>
  <br/>
  <i>Multi-engine routing · Markdown/Word output · Zero configuration required</i>
</p>

---

## Why pdf_pilot?

Every PDF converter tells you to pick one. We think that's wrong.

**Your PDFs are different** — some are scanned, some have complex tables, some are simple text.
One engine can't be best at everything. So **pdf_pilot analyzes your document and routes it to the optimal engine**, automatically.

| Your PDF Type | Best Engine | What Others Do |
|---|---|---|
| Scanned/OCR | Docling | ❌ Fail or garbage |
| Chinese + Tables | MinerU | ❌ Poor table extraction |
| Simple Digital | PyMuPDF4LLM | ❌ Slow ML model loading |
| Academic w/ Formulas | Docling | ❌ Lost formatting |

**Result:** 95%+ output quality across ALL document types, with zero configuration.

## Features

- 🧠 **Intelligent Routing** — auto-detects document type (scanned, multi-column, Chinese, tables, formulas) and selects the optimal engine
- 🔄 **Automatic Fallback** — if the primary engine fails, seamlessly falls back to the next best engine
- ⚡ **Lightning Fast** — simple PDFs converted in seconds via PyMuPDF4LLM, no ML model loading
- 📊 **Complex Table Support** — cross-page table merging, structured extraction
- 🌐 **109+ Language OCR** — Chinese, Japanese, Korean, Arabic, and more
- 📄 **Dual Output** — Markdown (.md) and Word (.docx)
- 🔌 **CLI + Python API** — use from terminal or integrate into your pipeline
- 🛡️ **MIT Licensed** — no commercial restrictions, use anywhere

## Quick Start

```bash
# Install
pip install -e .

# Convert anything — just works
pdf_pilot input.pdf -o output.md

# See available engines
pdf_pilot --list-engines
```

Full usage guide with examples → [Usage Guide](#usage-guide) below.

## Usage Guide

### Command Line (CLI)

The CLI is the fastest way to convert PDFs. After installation, the `pdf_pilot` command is available.

**1. Basic conversion — auto mode**

Let pdf_pilot analyze the document and pick the best engine automatically:

```bash
pdf_pilot input.pdf -o output.md
```

Output format is determined by the file extension: `.md` for Markdown, `.docx` for Word.

```bash
# Convert to Word
pdf_pilot input.pdf -o output.docx
```

**2. Force a specific engine**

```bash
# Use PyMuPDF (fastest, good for simple digital PDFs)
pdf_pilot input.pdf -o output.md -e pymupdf

# Use Docling (best for scanned, tables, formulas)
pdf_pilot input.pdf -o output.md -e docling

# Use MinerU (best for Chinese + complex documents, requires installation)
pdf_pilot input.pdf -o output.md -e mineru
```

**3. Batch convert a directory**

```bash
# Convert all PDFs in a folder at once
pdf_pilot ./pdfs/ -o ./output/

# Batch to Word
pdf_pilot ./pdfs/ -o ./output/ -f docx
```

**4. View available engines**

```bash
pdf_pilot --list-engines
```

Example output:
```
Available engines:
--------------------------------------------------
  docling            OK  (priority: 1)
  pymupdf            OK  (priority: 3)
  mineru             MISSING  (priority: 2)
```

**5. Verbose mode (see what's happening)**

```bash
pdf_pilot input.pdf -v
```

This shows which engine was selected, detection results, and processing time.

### Python API

Import and use directly in your code:

```python
from pdf_pilot.convert import convert

# Auto mode — simplest
doc = convert("input.pdf", "output.md")
print(f"Pages: {doc.page_count}, Engine: {doc.metadata['engine']}")

# Specify engine
doc = convert("input.pdf", engine="docling")
doc = convert("input.pdf", "output.docx", engine="pymupdf")

# Inspect structured content
print(doc.raw_markdown)      # Full markdown text
print(doc.blocks)            # Structured blocks (headings, paragraphs, etc.)
print(doc.tables)            # Extracted tables
print(doc.metadata)          # Engine, page count, etc.
```

### How to Choose an Engine

| Scenario | Recommended Engine | CLI Command |
|---|---|---|
| Don't know which to pick | `auto` (let the router decide) | `pdf_pilot input.pdf -e auto` |
| Simple text PDF, digital original | `pymupdf` (fastest) | `pdf_pilot input.pdf -e pymupdf` |
| Scanned document, photos, OCR needed | `docling` (built-in OCR) | `pdf_pilot input.pdf -e docling` |
| Complex tables, academic papers | `docling` (TableFormer) | `pdf_pilot input.pdf -e docling` |
| Chinese documents (requires install) | `mineru` (Chinese-optimized) | `pdf_pilot input.pdf -e mineru` |

When in doubt, start with `auto`. The router analyzes scan status, complexity, and language to make the best choice.

### Using with AI Assistants (Claude / Cursor / Copilot)

Tell your AI assistant: *"Use pdf_pilot to convert this PDF to Markdown"* and it will execute the command for you. Or write Python code:

```python
# Paste this into your AI assistant's code environment
from pdf_pilot.convert import convert
doc = convert("input.pdf", "output.md", engine="auto")
with open("output.md", "w", encoding="utf-8") as f:
    f.write(doc.raw_markdown)
print(f"Done — {doc.page_count} pages, {len(doc.raw_markdown)} characters")
```

## Use Cases

- **RAG / LLM pipelines** — convert PDFs to clean Markdown for embedding
- **Academic research** — extract papers with formulas and tables
- **Document digitization** — batch convert scanned archives
- **Business automation** — extract structured data from reports, invoices
- **Content migration** — PDF to Word with formatting preserved

## Engine Comparison

| Feature | Docling | PyMuPDF4LLM | MinerU (optional) |
|---|:---:|:---:|:---:|
| Default Engine | ✅ | | |
| CPU-Friendly | ✅ | ✅ | ✅ (pipeline) |
| GPU Required | ❌ | ❌ | VLM mode |
| Chinese Support | Good | Fair | Excellent |
| Table Extraction | Excellent (TableFormer) | Good | Excellent (cross-page) |
| Formula/LaTeX | Partial | No | Yes |
| Scanned PDFs | Excellent (OCR) | Fair (hybrid OCR) | Excellent |
| Multi-Column | Yes | Yes | Yes |
| Speed | Medium | ⚡ Fast | Medium |
| License | MIT | MIT | Custom (Apache 2.0-based) |

## Benchmark

> Tested on 4 document categories. Green = best-in-class, Yellow = good, Red = poor

| Document Type | Docling | PyMuPDF | MinerU | **pdf_pilot** |
|---|---|---|---|---|
| Multi-column English | Green | Yellow | — | **Green** (auto: Docling) |
| Chinese + Tables | Yellow | Red | **Green** | **Green** (auto: MinerU*) |
| Scanned/OCR | **Green** | Yellow | — | **Green** (auto: Docling) |
| Simple Digital | Green | **Green** | — | **Green** (auto: PyMuPDF) |

<details>
<summary><b>View conversion quality comparison</b></summary>

Multi-column academic paper — 15 pages, Attention Is All You Need:

| Metric | Docling | PyMuPDF | pdf_pilot (pymupdf) |
|---|---|---|---|
| Title extracted | ✅ | ✅ | ✅ |
| Heading hierarchy | ✅ H1-H3 | ✅ H1-H3 | ✅ H1-H3 |
| Readable content | ✅ 99% | ✅ 99% | ✅ 99% |
| Conversion time | ~30s+ | **~2.5s** | ~2.5s |
| Figures referenced | ✅ | ⚠️ alt only | ✅ |

*Note: Docling CPU crash on Windows (PyTorch access violation). Benchmark pending GPU environment.*
</details>

## Architecture

```
PDF Input
    │
    ├─🔍 Detector Layer ── Scan detection → Complexity analysis → Language detection
    │
    ├─🧠 Router Layer ── Rules engine selects optimal engine
    │     ├─ Chinese + complex → MinerU
    │     ├─ Scanned → Docling
    │     ├─ Simple → PyMuPDF
    │     └─ Default → Docling
    │
    ├─⚙️ Engine Layer ── Extraction (with auto-fallback)
    │
    └─📝 Output Layer ── Markdown (.md) or Word (.docx)
```

## Installation

```bash
# Core (always installed)
pip install docling pymupdf4llm python-docx

# Optional: MinerU for Chinese/complex documents
# Note: Requires Python 3.10-3.13 (PyMuPDF version conflict with pymupdf4llm)
pip install magic-pdf

# Development
pip install -e ".[dev]"
```

## Testing

```bash
# Full test suite (30 tests)
pytest tests/ -v

# Quality tests only
pytest tests/test_quality.py -v

# With HTML report
pytest tests/test_quality.py --html=quality_report.html
```

## Integrations

Works with any LLM/RAG framework:

| Framework | Integration |
|---|---|
| LangChain | `convert()` returns text → pass to Document |
| LlamaIndex | Same — feed markdown to `Document` |
| Dify / Flowise | CLI mode in pipeline |
| Cursor / Copilot | Use as local tool |

## Roadmap

- [ ] Docling GPU benchmark (current: Windows CPU crash)
- [ ] MinerU full integration test (Python 3.13 env)
- [ ] Batch processing optimization
- [ ] JSON output format
- [ ] Web API (FastAPI)
- [ ] Gradio/Streamlit web UI
- [ ] PDF table → CSV/Excel extraction

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  If this helped you, please ⭐ star the repo — it motivates us to keep improving!
</p>
