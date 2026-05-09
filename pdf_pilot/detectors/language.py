"""PDF 语言检测器 — 中文/英文检测"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def _is_cjk(char: str) -> bool:
    """判断字符是否为 CJK 文字（含扩展区、假名、谚文）"""
    cp = ord(char)
    return (
        0x4E00 <= cp <= 0x9FFF or    # CJK Unified Ideographs
        0x3400 <= cp <= 0x4DBF or    # CJK Extension A
        0x3040 <= cp <= 0x30FF or    # Hiragana + Katakana
        0xAC00 <= cp <= 0xD7AF or    # Hangul
        0xF900 <= cp <= 0xFAFF       # CJK Compatibility
    )


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

    try:
        doc = pymupdf.open(str(pdf))
    except Exception as e:
        logger.warning(f"Cannot open PDF for language detection: {e}")
        return "unknown"

    try:
        page_count = len(doc)

        if page_count == 0:
            return "unknown"

        sample_pages = min(page_count, 5)
        total_chars = 0
        chinese_chars = 0
        latin_chars = 0

        for page_num in range(sample_pages):
            page = doc[page_num]
            text = page.get_text()

            for char in text:
                if char.isspace():
                    continue
                total_chars += 1
                if _is_cjk(char):
                    chinese_chars += 1
                elif char.isalpha():
                    latin_chars += 1
    finally:
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
