"""主转换函数 — 统一入口"""

import logging
from pathlib import Path
from typing import Optional

from pdf_pilot.config import Config
from pdf_pilot.engines.base import EngineBase
from pdf_pilot.engines.docling_engine import DoclingEngine
from pdf_pilot.engines.mineru_engine import MinerUEngine
from pdf_pilot.engines.pymupdf_engine import PyMuPDFEngine
from pdf_pilot.model import ExtractedDocument
from pdf_pilot.output.docx import write_docx
from pdf_pilot.output.markdown import write_markdown
from pdf_pilot.router import EngineRouter

logger = logging.getLogger(__name__)


def _create_engines(config: Config) -> list[EngineBase]:
    """根据配置创建引擎列表"""
    engines = [
        DoclingEngine(use_vlm=config.docling_use_vlm),
        PyMuPDFEngine(),
    ]

    # MinerU 作为可选引擎
    mineru = MinerUEngine(backend=config.mineru_backend)
    if mineru.is_available():
        engines.append(mineru)
    else:
        logger.debug(
            "MinerU not available (requires: pip install magic-pdf). "
            "Falling back to Docling for Chinese/complex documents."
        )

    return engines


def convert(
    input_path: str | Path,
    output_path: Optional[str | Path] = None,
    engine: str = "auto",
    config: Optional[Config] = None,
) -> ExtractedDocument:
    """智能 PDF 转换主入口

    根据 PDF 特征自动选择最佳引擎，提取内容并输出为 Markdown 或 Word。

    Args:
        input_path: PDF 输入路径
        output_path: 输出文件路径 (可选，.md 或 .docx)
        engine: 引擎选择 ("auto" 或 "docling"/"mineru"/"pymupdf")
        config: 转换配置 (可选)

    Returns:
        ExtractedDocument: 提取的文档结构

    Examples:
        >>> from pdf_pilot import convert
        >>> doc = convert("input.pdf", "output.md")
        >>> doc = convert("input.pdf", engine="docling")
        >>> doc = convert("input.pdf", "output.docx", engine="mineru")
    """
    if config is None:
        config = Config()
    config.engine = engine

    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"PDF not found: {input_path}")

    # 创建引擎列表和路由器
    engines = _create_engines(config)
    router = EngineRouter(engines)

    force_engine = None if engine == "auto" else engine

    # 路由选择引擎
    selected_engine = router.route(str(input_path), force_engine=force_engine)

    # 执行提取（带降级）
    doc = _extract_with_fallback(selected_engine, str(input_path), router, config)

    # 输出
    if output_path:
        output_path = Path(output_path)
        suffix = output_path.suffix.lower()

        if suffix == ".docx":
            write_docx(doc.raw_markdown, output_path)
        elif suffix in (".md", ".markdown", ""):
            write_markdown(doc.raw_markdown, output_path)
        else:
            raise ValueError(f"Unsupported output format: {suffix}. Use .md or .docx")

    return doc


def _extract_with_fallback(
    engine: EngineBase,
    pdf_path: str,
    router: EngineRouter,
    config: Config,
) -> ExtractedDocument:
    """执行提取，失败时自动降级到其他引擎"""
    tried: set[str] = set()
    last_error = None
    current_engine = engine

    while len(tried) < len(router._engine_list):
        if current_engine.name in tried:
            break
        tried.add(current_engine.name)
        try:
            logger.info(
                f"Extracting with engine: {current_engine.name}"
            )
            return current_engine.extract(pdf_path)
        except Exception as e:
            last_error = e
            logger.warning(
                f"Engine {current_engine.name} failed: {e}"
            )

            # 选择下一个未尝试过的最佳引擎
            available = [
                e for e in router._engine_list
                if e.name not in tried
            ]
            if available:
                current_engine = min(available, key=lambda e: e.priority)
                logger.info(f"Falling back to: {current_engine.name}")
            else:
                break

    raise RuntimeError(
        f"All extraction attempts failed. Last error: {last_error}"
    ) from last_error
