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

    doc = pymupdf.open(str(pdf))
    page_count = len(doc)

    if page_count == 0:
        doc.close()
        return 0.0

    scanned_page_count = 0

    check_pages = min(page_count, 5)  # 抽样检查前5页
    for page_num in range(check_pages):
        page = doc[page_num]

        # 检查页面文本量
        text = page.get_text()
        text_len = len(text.strip())

        # 核心判断：纯扫描件几乎没有可提取文本
        # 每页文本量 < 200 chars 且没有矢量对象 → 疑似扫描件特征
        # （有矢量对象的低文本页面是封面/图表页，不是扫描件）
        if text_len < 200:
            # 检查是否有矢量图形/文本对象（有说明是矢量生成的，非扫描）
            vector_count = len(page.get_drawings()) if hasattr(page, 'get_drawings') else 0
            if vector_count == 0 and text_len == 0:
                scanned_page_count += 1

    doc.close()

    # 计算扫描概率
    sampled_ratio = scanned_page_count / max(check_pages, 1)

    # 综合评分
    if sampled_ratio > 0.8:
        return 0.95  # 几乎确定是扫描件
    elif sampled_ratio > 0.5:
        return 0.8
    elif sampled_ratio > 0.2:
        return 0.5
    elif sampled_ratio > 0:
        return 0.3
    else:
        return 0.1  # 无扫描特征
