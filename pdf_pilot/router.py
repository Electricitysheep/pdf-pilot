"""智能路由 — 基于 PDF 特征选择最佳引擎"""

import logging
from typing import Optional

from pdf_pilot.detectors.complexity import detect_complexity
from pdf_pilot.detectors.language import detect_language
from pdf_pilot.detectors.scanner import is_scanned_pdf
from pdf_pilot.engines.base import EngineBase

logger = logging.getLogger(__name__)


class EngineRouter:
    """智能引擎路由器

    路由规则:
    - 中文 + 复杂(表格/公式) → MinerU
    - 扫描型 PDF → Docling (OCR)
    - 简单数字 PDF → PyMuPDF4LLM (最快)
    - 英文学术 → Docling
    - 默认 → Docling
    """

    def __init__(self, engines: list[EngineBase]):
        """初始化路由器

        Args:
            engines: 可用引擎列表
        """
        self.engines = {e.name: e for e in engines}
        self._engine_list = [e for e in engines if e.is_available()]

    def route(
        self,
        pdf_path: str,
        force_engine: Optional[str] = None,
    ) -> EngineBase:
        """根据 PDF 特征选择最佳引擎

        Args:
            pdf_path: PDF 文件路径
            force_engine: 强制指定引擎名称，None 表示自动选择

        Returns:
            EngineBase: 选中的引擎
        """
        # 手动指定优先
        if force_engine:
            engine = self._get_available_engine(force_engine)
            if engine:
                logger.info(f"Using forced engine: {force_engine}")
                return engine
            logger.warning(
                f"Forced engine '{force_engine}' not available, "
                f"falling back to auto-detection"
            )

        # 自动路由
        engine = self._auto_route(pdf_path)
        logger.info(f"Auto-selected engine: {engine.name}")
        return engine

    def _auto_route(self, pdf_path: str) -> EngineBase:
        """自动选择最佳引擎"""
        # 检测 PDF 特征
        scan_score = 0.0
        complexity = None
        language = "unknown"

        try:
            scan_score = is_scanned_pdf(pdf_path)
        except Exception as e:
            logger.warning(f"Scanner detection failed: {e}")

        try:
            complexity = detect_complexity(pdf_path)
        except Exception as e:
            logger.warning(f"Complexity detection failed: {e}")

        try:
            language = detect_language(pdf_path)
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")

        logger.debug(
            f"PDF analysis: scan={scan_score:.2f}, "
            f"complexity={complexity.overall_complexity if complexity else 'unknown'}, "
            f"lang={language}"
        )

        # 路由决策
        engine = None

        # 规则1: 扫描型 → Docling (OCR 能力强)
        if scan_score > 0.7:
            engine = self._get_available_engine("docling")

        # 规则2: 中文 + 复杂 → MinerU (如果有) 否则 Docling
        elif language == "zh" and complexity and complexity.is_complex:
            engine = self._get_available_engine("mineru")
            if not engine:
                engine = self._get_available_engine("docling")

        # 规则3: 纯简单数字 PDF → PyMuPDF (最快)
        elif (
            scan_score < 0.2 and
            complexity and
            complexity.overall_complexity == "low"
        ):
            engine = self._get_available_engine("pymupdf")

        # 规则4: 英文学术 → Docling
        elif language == "en" and complexity and complexity.is_complex:
            engine = self._get_available_engine("docling")

        # 默认: Docling (最稳妥)
        if not engine:
            engine = self._get_available_engine("docling")

        # 最终回退
        if not engine and self._engine_list:
            engine = self._engine_list[0]

        if not engine:
            raise RuntimeError("No PDF engine is available")

        return engine

    def _get_available_engine(self, name: str) -> Optional[EngineBase]:
        """获取指定名称的可用引擎"""
        engine = self.engines.get(name)
        if engine and engine.is_available():
            return engine
        return None

    def get_available_engines(self) -> list[str]:
        """列出所有可用引擎"""
        return [e.name for e in self._engine_list]

    def list_engines(self) -> list[dict]:
        """列出所有引擎信息"""
        return [
            {
                "name": e.name,
                "available": e.is_available(),
                "priority": e.priority,
            }
            for e in self.engines.values()
        ]
