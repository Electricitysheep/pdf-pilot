"""PyMuPDF4LLM 引擎适配 — 快速模式"""

import logging
import re
from pathlib import Path

from pdf_pilot.engines.base import EngineBase
from pdf_pilot.model import (
    Block,
    BlockType,
    ExtractedDocument,
)

logger = logging.getLogger(__name__)


class PyMuPDFEngine(EngineBase):
    """通过 PyMuPDF4LLM 快速提取 PDF 内容

    特点:
    - 纯 C 引擎，速度极快
    - 无 ML 模型依赖，启动快
    - 适合排版简单的数字 PDF
    - 混合 OCR（仅对需要区域 OCR）
    - 版面感知阅读顺序重建
    """

    @property
    def name(self) -> str:
        return "pymupdf"

    @property
    def priority(self) -> int:
        return 3  # 快速模式，较低优先级（默认不选）

    def is_available(self) -> bool:
        try:
            import pymupdf4llm  # noqa: F401

            return True
        except ImportError:
            return False

    def extract(self, pdf_path: str) -> ExtractedDocument:
        """使用 PyMuPDF4LLM 提取 PDF 内容"""
        import pymupdf4llm

        pdf = Path(pdf_path)
        if not pdf.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        # 提取 Markdown
        md_text = pymupdf4llm.to_markdown(str(pdf))

        # 获取页数
        page_count = 0
        try:
            import pymupdf

            with pymupdf.open(str(pdf)) as doc:
                page_count = len(doc)
        except Exception:
            page_count = 0

        # 解析 Markdown 为结构化 Block
        blocks = self._parse_markdown_to_blocks(md_text)

        return ExtractedDocument(
            title=blocks[0].content
            if blocks and blocks[0].type == BlockType.HEADING
            else "",
            blocks=blocks,
            raw_markdown=md_text,
            metadata={
                "page_count": page_count,
                "engine": "pymupdf",
            },
        )

    def _parse_markdown_to_blocks(self, md_text: str) -> list[Block]:
        """将 Markdown 文本解析为结构化 Block"""
        blocks = []
        if not md_text:
            return blocks

        lines = md_text.split("\n")
        i = 0
        in_code_block = False
        code_lines = []

        while i < len(lines):
            line = lines[i]

            # 代码块检测
            if line.strip().startswith("```"):
                if in_code_block:
                    # 结束代码块
                    blocks.append(
                        Block(
                            type=BlockType.CODE,
                            content="\n".join(code_lines),
                        )
                    )
                    code_lines = []
                    in_code_block = False
                else:
                    # 开始代码块
                    in_code_block = True
                i += 1
                continue

            if in_code_block:
                code_lines.append(line)
                i += 1
                continue

            # 空行跳过
            if not line.strip():
                i += 1
                continue

            # 标题检测
            if line.startswith("#"):
                level = 0
                for ch in line:
                    if ch == "#":
                        level += 1
                    else:
                        break
                content = line[level:].strip()
                if content.startswith(" "):
                    content = content[1:]
                blocks.append(
                    Block(
                        type=BlockType.HEADING,
                        content=content,
                        level=min(level, 6),
                    )
                )

            # 列表项检测（支持任意编号）
            elif re.match(r"^(\d+\.\s|[-*]\s)", line.strip()):
                blocks.append(
                    Block(
                        type=BlockType.LIST_ITEM,
                        content=line.strip(),
                    )
                )

            # 表格行检测
            elif "|" in line and ("---" in line or line.strip().startswith("|")):
                blocks.append(
                    Block(
                        type=BlockType.TABLE,
                        content=line.strip(),
                    )
                )

            # 普通段落
            else:
                # 合并连续行
                paragraph_lines = [line.strip()]
                i += 1
                while i < len(lines):
                    next_line = lines[i].strip()
                    if (
                        not next_line
                        or next_line.startswith("#")
                        or re.match(r"^(\d+\.\s|[-*]\s)", next_line)
                        or next_line.startswith("```")
                    ):
                        break
                    paragraph_lines.append(next_line)
                    i += 1
                blocks.append(
                    Block(
                        type=BlockType.PARAGRAPH,
                        content=" ".join(paragraph_lines),
                    )
                )
                continue

            i += 1

        return blocks
