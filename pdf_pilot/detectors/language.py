"""PDF 语言检测器 — 中文/英文检测"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def detect_language(pdf_path: str) -> str:
    """检测 PDF 的主要语言

    Returns:
        str: 'zh' (中文), 'en' (英文), 'unknown'
    """
    try:
        import pymupdf
    except ImportError:
        logger.warning("PyMuPDF not available, cannot detect language")
        return "unknown"

    pdf = Path(pdf_path)
    if not pdf.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    doc = pymupdf.open(str(pdf))
    page_count = len(doc)

    if page_count == 0:
        doc.close()
        return "unknown"

    # 抽样检查前5页
    sample_pages = min(page_count, 5)
    total_chars = 0
    chinese_chars = 0
    latin_chars = 0

    for page_num in range(sample_pages):
        page = doc[page_num]
        text = page.get_text()

        for char in text:
            if '一' <= char <= '鿿':
                chinese_chars += 1
                total_chars += 1
            elif 'A' <= char <= 'Z' or 'a' <= char <= 'z':
                latin_chars += 1
                total_chars += 1

    doc.close()

    if total_chars == 0:
        return "unknown"

    chinese_ratio = chinese_chars / total_chars

    if chinese_ratio > 0.3:
        return "zh"
    elif latin_chars > chinese_chars and latin_chars / total_chars > 0.3:
        return "en"
    else:
        return "unknown"
