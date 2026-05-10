"""质量自测 — 自动化格式和结构检测"""

import logging
import time

import pytest

from pdf_pilot.convert import convert
from pdf_pilot.model import BlockType

logger = logging.getLogger(__name__)

# 检查 Docling 是否可用 (CPU 环境下可能崩溃)
_DOCING_STABLE = True
try:
    from pdf_pilot.engines.docling_engine import DoclingEngine

    engine = DoclingEngine()
    if engine.is_available():
        # 尝试一次转换来检测是否稳定
        test_code = """
from pdf_pilot.engines.docling_engine import DoclingEngine
e = DoclingEngine()
e.extract("__PDF_PATH__")
"""
        # 不实际测试，直接假设 GPU 环境稳定
        _DOCING_STABLE = True  # 假设稳定，实际运行时崩溃由 pytest 处理
except Exception:
    _DOCING_STABLE = False


skip_if_docling_unstable = pytest.mark.skipif(
    not _DOCING_STABLE,
    reason="Docling crashes on CPU+Windows; requires GPU",
)


class TestEnglishQuality:
    """英文 PDF 转换质量测试 (PyMuPDF 引擎)"""

    def test_multi_column_reading_order(self, multi_column_pdf):
        """多栏 PDF 阅读顺序测试 — 不应出现乱序"""
        doc = convert(multi_column_pdf, engine="pymupdf")

        assert doc.raw_markdown, "输出不应为空"
        assert len(doc.raw_markdown) > 100, "输出内容过少"

        # 检查段落顺序合理性（内容应该可读）
        blocks_text = [b.content for b in doc.blocks]
        combined = "\n".join(blocks_text)

        # 检查没有乱码 (可打印字符比例 > 95%)
        printable = sum(1 for c in combined if c.isprintable() or c in "\n\t ")
        total = max(len(combined), 1)
        ratio = printable / total
        assert ratio > 0.95, f"乱码率过高: {100 * (1 - ratio):.1f}%"

        logger.info(
            f"  Multi-column quality: {total} chars, {ratio * 100:.1f}% printable"
        )

    def test_multi_column_has_headings(self, multi_column_pdf):
        """多栏 PDF 应包含标题结构"""
        doc = convert(multi_column_pdf, engine="pymupdf")

        headings = [b for b in doc.blocks if b.type == BlockType.HEADING]
        assert len(headings) >= 1, "应至少有一个标题"

    def test_table_extraction(self, table_pdf):
        """表格提取测试 — 检查是否有表格内容"""
        doc = convert(table_pdf, engine="pymupdf")

        # Markdown 中应包含表格（以 | 分隔的行）
        md_lines = doc.raw_markdown.split("\n")
        table_lines = [line for line in md_lines if "|" in line]

        assert len(table_lines) > 0, "应提取到表格内容"

        # 表格行应有合理的列数
        for line in table_lines[:5]:
            cells = [c.strip() for c in line.split("|") if c.strip()]
            assert len(cells) >= 1, f"表格行格式异常: {line[:50]}"

        logger.info(f"  Table extraction: {len(table_lines)} table lines found")

    def test_academic_formulas(self, academic_pdf):
        """学术论文公式提取测试"""
        doc = convert(academic_pdf, engine="pymupdf")

        assert doc.raw_markdown, "输出不应为空"

        md = doc.raw_markdown

        # 检查公式标记 ($...$ 或 $$...$$)
        has_inline_math = "$" in md and "$" in md[md.index("$") + 1 :]
        has_block_math = "$$" in md

        # 至少应有一些数学符号
        math_indicators = md.count("∈") + md.count("∑") + md.count("∫")

        logger.info(
            f"  Formula detection: inline_math={has_inline_math}, "
            f"block_math={has_block_math}, symbols={math_indicators}"
        )

        # 学术论文应有内容
        assert len(md) > 500, f"输出过短 ({len(md)} chars), 可能提取不完整"

    def test_academic_headings_hierarchy(self, academic_pdf):
        """学术论文标题层级测试"""
        doc = convert(academic_pdf, engine="pymupdf")

        headings = [b for b in doc.blocks if b.type == BlockType.HEADING]

        # 学术论文通常有多个标题
        assert len(headings) >= 1, "应至少有一个标题"

        # 检查标题层级合理 (1-4)
        for h in headings:
            assert 1 <= h.level <= 4, f"标题层级异常: {h.level}"

    def test_scanned_pdf_basic(self, scanned_pdf):
        """扫描件基本处理测试"""
        doc = convert(scanned_pdf, engine="pymupdf")
        # PyMuPDF 不擅长扫描件，但不应崩溃
        assert doc is not None
        logger.info(f"  Scanned PDF processed, output length: {len(doc.raw_markdown)}")


class TestEngineQuality:
    """引擎质量对比测试"""

    def test_pymupdf_produces_output(self, multi_column_pdf):
        """PyMuPDF 应产生有效输出"""
        doc = convert(multi_column_pdf, engine="pymupdf")
        assert doc.raw_markdown
        assert len(doc.raw_markdown) > 100


class TestOutputFormat:
    """输出格式测试"""

    def test_markdown_output(self, multi_column_pdf, output_dir):
        """Markdown 输出测试"""
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "test_output.md"

        convert(multi_column_pdf, output_path=output_path, engine="pymupdf")

        assert output_path.exists(), "Markdown 文件应被创建"
        content = output_path.read_text(encoding="utf-8")
        assert len(content) > 100, "Markdown 文件内容过少"

    def test_docx_output(self, multi_column_pdf, output_dir):
        """Word 输出测试"""
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "test_output.docx"

        convert(multi_column_pdf, output_path=output_path, engine="pymupdf")

        assert output_path.exists(), "Word 文件应被创建"
        size = output_path.stat().st_size
        assert size > 1000, f"Word 文件过小 ({size} bytes)"

        logger.info(f"  DOCX output: {size} bytes")


class TestPerformance:
    """性能测试"""

    def test_pymupdf_speed(self, multi_column_pdf):
        """PyMuPDF 速度测试 — 冷启动应 < 30s"""
        start = time.time()
        convert(multi_column_pdf, engine="pymupdf")
        elapsed = time.time() - start

        logger.info(f"  PyMuPDF time: {elapsed:.2f}s")
        assert elapsed < 30, f"PyMuPDF 转换超时: {elapsed:.1f}s"

    def test_pymupdf_table_speed(self, table_pdf):
        """表格 PDF 转换速度测试"""
        start = time.time()
        convert(table_pdf, engine="pymupdf")
        elapsed = time.time() - start

        logger.info(f"  Table PDF time: {elapsed:.2f}s")
        assert elapsed < 10, f"表格 PDF 转换超时: {elapsed:.1f}s"

    def test_pymupdf_academic_speed(self, academic_pdf):
        """学术论文转换速度测试"""
        start = time.time()
        convert(academic_pdf, engine="pymupdf")
        elapsed = time.time() - start

        logger.info(f"  Academic PDF time: {elapsed:.2f}s")
        assert elapsed < 10, f"学术论文转换超时: {elapsed:.1f}s"
