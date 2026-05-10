# Contributing to pdf_pilot

Thank you for your interest in contributing! pdf_pilot is a multi-engine PDF converter that automatically routes documents to the optimal extraction engine.

## Development Setup

```bash
# Clone the repository
git clone https://github.com/Electricitysheep/pdf-pilot.git
cd pdf-pilot

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies (creates .venv automatically)
uv sync --dev

# Activate the virtual environment
source .venv/bin/activate  # Linux/macOS
# or: .venv\Scripts\activate  # Windows

# Run tests
uv run pytest tests/ -v

# Run self-test (downloads real PDFs)
uv run python self_test.py
```

## Project Structure

```
pdf_pilot/
├── cli.py              # Command-line interface
├── config.py           # Configuration
├── convert.py          # Main conversion entry point
├── model.py            # Data models
├── router.py           # Engine routing logic
├── detectors/          # Document analysis (scan, complexity, language)
├── engines/            # PDF extraction engines (pymupdf, docling, mineru)
└── output/             # Output formatters (markdown, docx)
```

## How to Contribute

1. **Find an issue** — Check [open issues](https://github.com/Electricitysheep/pdf-pilot/issues) or create a new one to discuss your idea
2. **Fork & branch** — Create a feature branch from `main`
3. **Make changes** — Follow existing code style, add tests for new features
4. **Run tests** — Ensure `pytest tests/ -v` and `python self_test.py` pass
5. **Submit PR** — Describe what changed and why

## Code Style

- Follow PEP 8 with 88-character line length
- Run `uv run ruff check .` before submitting
- Run `uv run ruff format .` to format code
- Add type hints to function signatures
- Docstrings: one-line for obvious functions, multi-line for complex logic

## Testing

- **Unit tests**: `uv run pytest tests/ -v` (30 tests)
- **End-to-end**: `uv run python self_test.py` (41 tests, downloads real PDFs)
- **Quality tests**: `uv run pytest tests/test_quality.py -v`

## Pull Request Guidelines

- One feature or fix per PR
- Include tests for new functionality
- Update README if changing behavior
- Keep PRs focused — avoid unrelated refactoring

## Reporting Issues

- Use the [issue templates](.github/ISSUE_TEMPLATE/) if available
- Include: Python version, pdf_pilot version, PDF sample (if possible)
- For conversion issues, attach the problematic PDF and expected output

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
