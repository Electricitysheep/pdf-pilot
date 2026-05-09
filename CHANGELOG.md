# Changelog

## [0.2.0] - 2026-05-09

### Added
- Comprehensive Usage Guide with CLI and Python API examples
- Competitor comparison table (vs pdfplumber, marker, pymupdf, unstructured)
- Colab demo notebook for zero-install testing
- AI Agent platform integration guide (Claude Code, OpenClaw, OpenCode, Hermes)
- LangChain integration module (`pdf_pilot.integrations.langchain`)
- LlamaIndex integration module (`pdf_pilot.integrations.llamaindex`)
- CODE_OF_CONDUCT.md
- Enhanced CONTRIBUTING.md with project structure and testing guidelines
- Improved bug report template with more fields
- scripts/demo.py and scripts/record_demo.sh for terminal demo recording

### Fixed
- Config bug where `config.engine` was not set for non-Config callers
- Engine fallback tracking with `tried` set to prevent same-engine retry loops
- Resource leaks in all 3 detectors (pymupdf.open without try/finally)
- Scanner detection for OCR-overlay scanned PDFs
- CJK language detection expanded to 5 Unicode ranges
- Case-insensitive PDF globbing for batch conversion
- ValueError for unsupported output formats
- List item detection with regex for arbitrary numbering
- Version upper bounds on dependencies

### Changed
- PyPI workflow made non-blocking for releases
- README badge and Colab link added

## [0.1.0] - 2026-05-08

### Added
- Initial release
- Intelligent engine routing (Docling / PyMuPDF4LLM / MinerU)
- PDF auto-detection: scan, complexity, language
- Markdown and Word output
- CLI and Python API
- Automatic engine fallback
- 30 automated tests
