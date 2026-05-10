"""扫描型 PDF 检测器 — 判断 PDF 是否为扫描/图片型（需要 OCR）"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def is_scanned_pdf(pdf_path: str) -> float:
    """检测 PDF 是否为扫描型

    Returns:
        float: 扫描概率 (0.0-1.0)，越高越可能是扫描件
    """
    try:
        import pymupdf
    except ImportError:
        logger.warning("PyMuPDF not available, cannot detect scanned PDF")
        return 0.0

    pdf = Path(pdf_path)
    if not pdf.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    try:
        doc = pymupdf.open(str(pdf))
    except Exception as e:
        logger.warning(f"Cannot open PDF for scan detection: {e}")
        return 0.0

    try:
        page_count = len(doc)

        if page_count == 0:
            return 0.0

        scanned_page_count = 0

        check_pages = min(page_count, 5)
        for page_num in range(check_pages):
            page = doc[page_num]

            text = page.get_text()
            text_len = len(text.strip())

            if text_len < 200:
                vector_count = (
                    len(page.get_drawings()) if hasattr(page, "get_drawings") else 0
                )
                image_count = (
                    len(page.get_images()) if hasattr(page, "get_images") else 0
                )
                # 扫描件：无矢量对象且文本极少，或有图片但文本很少（OCR-overlay 扫描件）
                if (vector_count == 0 and text_len < 50) or (
                    image_count > 0 and text_len < 100
                ):
                    scanned_page_count += 1

        sampled_ratio = scanned_page_count / max(check_pages, 1)

        if sampled_ratio > 0.8:
            return 0.95
        elif sampled_ratio > 0.5:
            return 0.8
        elif sampled_ratio > 0.2:
            return 0.5
        elif sampled_ratio > 0:
            return 0.3
        else:
            return 0.1
    finally:
        doc.close()
