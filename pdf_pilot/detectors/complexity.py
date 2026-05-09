"""PDF 复杂度检测器 — 表格、公式、多栏"""

import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ComplexityScore:
    """复杂度评分"""
    has_tables: bool = False
    table_count: int = 0
    has_formulas: bool = False
    formula_count: int = 0
    has_multi_column: bool = False
    column_count: int = 1
    overall_complexity: str = "low"  # low / medium / high

    @property
    def is_complex(self) -> bool:
        return self.overall_complexity in ("medium", "high")


def detect_complexity(pdf_path: str) -> ComplexityScore:
    """检测 PDF 文档的排版复杂度"""
    try:
        import pymupdf
    except ImportError:
        logger.warning("PyMuPDF not available, cannot detect complexity")
        return ComplexityScore()

    pdf = Path(pdf_path)
    if not pdf.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    try:
        doc = pymupdf.open(str(pdf))
    except Exception as e:
        logger.warning(f"Cannot open PDF for complexity detection: {e}")
        return ComplexityScore()

    try:
        page_count = len(doc)

        total_tables = 0
        total_formulas = 0
        multi_column_pages = 0
        check_pages = min(page_count, 5)

        for page_num in range(check_pages):
            page = doc[page_num]

            # 检测表格
            tabs = page.find_tables()
            if tabs:
                table_count = len(tabs.tables) if hasattr(tabs, 'tables') else 0
                total_tables += table_count

            # 检测多栏
            blocks = page.get_text("dict", flags=pymupdf.TEXTFLAGS_TEXT)["blocks"]
            if _is_multi_column(blocks):
                multi_column_pages += 1

            # 检测公式（通过文本内容匹配）
            text = page.get_text()
            formula_count = _count_formulas(text)
            total_formulas += formula_count

        has_tables = total_tables > 0
        has_formulas = total_formulas > 0
        has_multi_col = multi_column_pages > check_pages * 0.3

        complexity = "low"
        score = sum([has_tables, has_formulas, has_multi_col])
        if score >= 2:
            complexity = "high"
        elif score >= 1:
            complexity = "medium"

        return ComplexityScore(
            has_tables=has_tables,
            table_count=total_tables,
            has_formulas=has_formulas,
            formula_count=total_formulas,
            has_multi_column=has_multi_col,
            column_count=2 if has_multi_col else 1,
            overall_complexity=complexity,
        )
    finally:
        doc.close()


def _is_multi_column(blocks: list) -> bool:
    """判断页面是否为多栏布局"""
    if len(blocks) < 3:
        return False

    # 获取每个文本块的 bbox
    col_blocks = []
    for block in blocks:
        if block.get("type") == 0:  # text block
            bbox = block.get("bbox", (0, 0, 0, 0))
            col_blocks.append(bbox)

    if len(col_blocks) < 2:
        return False

    # 按 Y 坐标分组，检查同一行是否有多个文本块
    y_groups = {}
    for bbox in col_blocks:
        y_key = round(bbox[1] / 20)  # 20px 容差
        if y_key not in y_groups:
            y_groups[y_key] = []
        y_groups[y_key].append(bbox)

    for y_key, bboxes in y_groups.items():
        if len(bboxes) >= 2:
            # 检查是否有水平分离（不同列）
            x_positions = sorted([b[0] for b in bboxes])
            if len(x_positions) >= 2:
                gap = x_positions[1] - x_positions[0]
                if gap > 50:  # 水平间距 > 50px 视为不同列
                    return True

    return False


def _count_formulas(text: str) -> int:
    """粗略检测公式数量"""
    import re
    # 检测 LaTeX 风格的公式标记
    patterns = [
        r'\$\$.*?\$\$',  # 块级公式 $$...$$
        r'\$[^$]+\$$',  # 行内公式 $...$
        r'\\\[.*?\\\]',  # \[...\] 块级
        r'\\\(.+?\\\)',  # \(...\) 行内
    ]
    count = 0
    for pattern in patterns:
        count += len(re.findall(pattern, text, re.DOTALL))
    return count
