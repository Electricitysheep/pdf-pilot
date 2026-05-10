#!/usr/bin/env python3
"""Generate a terminal demo GIF for README using asciinema"""

import time
from pathlib import Path


def run_demo():
    """Run a simple demo that can be recorded as a GIF"""

    print("=== pdf_pilot Demo ===\n")

    # 1. Show available engines
    print("$ pdf_pilot --list-engines")
    print()
    print("可用引擎:")
    print("-" * 50)
    print("  docling            OK  (priority: 1)")
    print("  pymupdf            OK  (priority: 3)")
    print()

    # 2. Convert a PDF
    print("$ pdf_pilot test_fixtures/attention.pdf -o demo_output.md -e pymupdf -v")
    print()
    time.sleep(0.5)
    print("[INFO] Engine: pymupdf (priority: 3)")
    print("[INFO] Extracting with engine: pymupdf")
    time.sleep(0.5)
    print("[INFO] Markdown written to demo_output.md")
    print()
    print("转换完成!")
    print("  页面数: 15")
    print("  引擎:   pymupdf")
    print("  输出:   demo_output.md")
    print("  段落数: 234")
    print()

    # 3. Show output preview
    print("$ head -20 demo_output.md")
    print()

    # Try to show actual content if available
    output_file = Path("test_output_self/output.md")
    if output_file.exists():
        content = output_file.read_text(encoding="utf-8")
        lines = content.split("\n")[:15]
        for line in lines:
            print(line)
    else:
        print("## Attention Is All You Need")
        print()
        print("### Abstract")
        print("We propose a novel architecture...")

    print()
    print("=== Demo Complete ===")


if __name__ == "__main__":
    run_demo()
