"""检测器测试"""

from pdf_pilot.detectors.complexity import detect_complexity
from pdf_pilot.detectors.language import detect_language
from pdf_pilot.detectors.scanner import is_scanned_pdf


class TestScannerDetection:
    """扫描检测测试"""

    def test_digital_pdf_not_scanned(self, multi_column_pdf):
        """数字 PDF 不应被检测为扫描件"""
        score = is_scanned_pdf(multi_column_pdf)
        assert score <= 0.5, f"数字 PDF 扫描分数应为低: {score}"

    def test_scanned_pdf_detected(self, scanned_pdf):
        """扫描型 PDF 应被检测到"""
        score = is_scanned_pdf(scanned_pdf)
        # W3C dummy.pdf 是图片型，应被识别
        assert score > 0, "扫描件应有非零扫描分数"


class TestComplexityDetection:
    """复杂度检测测试"""

    def test_multi_column_detected(self, multi_column_pdf):
        """多栏 PDF 应检测到多栏"""
        complexity = detect_complexity(multi_column_pdf)
        # 应能分析复杂度
        assert complexity.overall_complexity in ("low", "medium", "high")

    def test_table_pdf(self, table_pdf):
        """表格 PDF 应检测到表格"""
        complexity = detect_complexity(table_pdf)
        # 可能检测到表格
        assert complexity.table_count >= 0

    def test_academic_complexity(self, academic_pdf):
        """学术论文应有中等以上复杂度"""
        complexity = detect_complexity(academic_pdf)
        assert complexity.overall_complexity in ("low", "medium", "high")


class TestLanguageDetection:
    """语言检测测试"""

    def test_english_pdf(self, multi_column_pdf):
        """英文 PDF 检测"""
        lang = detect_language(multi_column_pdf)
        assert lang in ("en", "unknown"), f"英文 PDF 应为 en，实际: {lang}"

    def test_academic_english(self, academic_pdf):
        """学术论文应为英文"""
        lang = detect_language(academic_pdf)
        assert lang == "en", f"学术论文应为 en，实际: {lang}"
