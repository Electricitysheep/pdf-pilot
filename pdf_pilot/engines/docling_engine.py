"""Docling 引擎适配 — 默认通用引擎"""

import logging
from pathlib import Path
from typing import Optional

from pdf2doc.engines.base import EngineBase
from pdf2doc.model import (
    Block,
    BlockType,
    ExtractedDocument,
    Formula,
    Image,
    Table,
)

logger = logging.getLogger(__name__)


class DoclingEngine(EngineBase):
    """通过 Docling 引擎提取 PDF 内容

    Docling (IBM) 特点:
    - MIT 许可证，CPU 友好
    - TableFormer 表格识别
    - 多格式支持 (PDF/DOCX/PPTX/HTML/图片等)
    - 中文 OCR 支持
    - 版面分析和阅读顺序重建
    """

    def __init__(self, use_vlm: bool = False):
        """初始化 Docling 引擎

        Args:
            use_vlm: 是否使用 VLM 模式 (需要 GPU)
        """
        self._converter = None
        self.use_vlm = use_vlm

    @property
    def name(self) -> str:
        return "docling"

    @property
    def priority(self) -> int:
        return 1  # 默认引擎，最高优先级

    def is_available(self) -> bool:
        try:
            import docling  # noqa: F401
            from docling.document_converter import DocumentConverter  # noqa: F401
            return True
        except ImportError:
            return False

    def _get_converter(self):
        if self._converter is None:
            from docling.document_converter import DocumentConverter
            self._converter = DocumentConverter()
        return self._converter

    def extract(self, pdf_path: str) -> ExtractedDocument:
        """使用 Docling 提取 PDF 内容"""
        pdf = Path(pdf_path)
        if not pdf.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        converter = self._get_converter()
        result = converter.convert(str(pdf), raises_on_error=False)

        if result.status.value != "success":
            logger.warning(
                f"Docling conversion status: {result.status.value} "
                f"for {pdf_path}"
            )

        doc = result.document

        # 提取 Markdown
        raw_md = doc.export_to_markdown()

        # 提取结构化信息
        blocks, tables, images, formulas = self._extract_structure(doc)

        return ExtractedDocument(
            title=self._extract_title(doc),
            blocks=blocks,
            tables=tables,
            images=images,
            formulas=formulas,
            raw_markdown=raw_md,
            metadata={
                "page_count": doc.num_pages,
                "engine": "docling",
                "status": result.status.value,
            },
        )

    def _extract_title(self, doc) -> str:
        """提取文档标题"""
        try:
            if doc.title:
                return doc.title
        except Exception:
            pass

        # 尝试从第一个标题块提取
        for item in doc.iterate_items():
            if hasattr(item, "label") and str(item.label) in (
                "GroupLabel.SECTION_HEADER",
                "section_header",
                "heading",
            ):
                try:
                    text = self._get_item_text(item, doc)
                    if text:
                        return text
                except Exception:
                    continue
        return ""

    def _extract_structure(self, doc):
        """从 DoclingDocument 提取结构化内容"""
        blocks = []
        tables = []
        images = []
        formulas = []

        try:
            for item, level in doc.iterate_items():
                label = str(getattr(item, "label", ""))

                # 标题
                if "section_header" in label.lower() or "heading" in label.lower():
                    text = self._get_item_text(item, doc) or ""
                    lvl = getattr(item, "level", 0)
                    blocks.append(Block(
                        type=BlockType.HEADING,
                        content=text,
                        level=int(lvl) if lvl else 1,
                    ))

                # 段落文本
                elif "text" in label.lower() or "paragraph" in label.lower():
                    text = self._get_item_text(item, doc) or ""
                    if text.strip():
                        blocks.append(Block(
                            type=BlockType.PARAGRAPH,
                            content=text,
                        ))

                # 列表项
                elif "list_item" in label.lower():
                    text = self._get_item_text(item, doc) or ""
                    if text.strip():
                        blocks.append(Block(
                            type=BlockType.LIST_ITEM,
                            content=text,
                        ))

                # 代码块
                elif "code" in label.lower():
                    text = self._get_item_text(item, doc) or ""
                    blocks.append(Block(
                        type=BlockType.CODE,
                        content=text,
                    ))

                # 表格
                elif "table" in label.lower():
                    table = self._extract_table(item, doc)
                    if table:
                        tables.append(table)

                # 图片
                elif "picture" in label.lower() or "figure" in label.lower():
                    img = self._extract_image(item, doc)
                    if img:
                        images.append(img)

                # 公式
                elif "formula" in label.lower():
                    text = self._get_item_text(item, doc) or ""
                    if text.strip():
                        formulas.append(Formula(
                            latex=text.strip(),
                            inline=False,
                        ))

        except Exception as e:
            logger.warning(f"Error extracting structure: {e}")

        return blocks, tables, images, formulas

    def _get_item_text(self, item, doc) -> Optional[str]:
        """从文档项提取文本"""
        try:
            text, _ = doc.get_text(item)
            if isinstance(text, str):
                return text.strip()
        except Exception:
            pass
        return None

    def _extract_table(self, item, doc) -> Optional[Table]:
        """提取表格结构"""
        try:
            if hasattr(item, "data"):
                # 尝试获取 HTML 表格
                html = doc.export_to_html()
                return Table(
                    raw_html=html,
                    num_rows=0,
                    num_cols=0,
                )

            # 通过 iterate_items 提取
            table_data = []
            num_cols = 0
            for cell_text, _ in doc.get_text(item):
                if isinstance(cell_text, str):
                    cells = [c.strip() for c in cell_text.split("\t")]
                    table_data.append(cells)
                    num_cols = max(num_cols, len(cells))

            headers = table_data[0] if table_data else []
            rows = table_data[1:] if len(table_data) > 1 else []

            return Table(
                headers=headers,
                rows=rows,
                num_rows=len(rows),
                num_cols=num_cols,
            )
        except Exception as e:
            logger.warning(f"Error extracting table: {e}")
            return None

    def _extract_image(self, item, doc) -> Optional[Image]:
        """提取图片引用"""
        try:
            desc = ""
            if hasattr(item, "text"):
                desc = item.text if isinstance(item.text, str) else ""
            return Image(
                description=desc.strip(),
            )
        except Exception:
            return None
