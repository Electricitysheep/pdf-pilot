"""MinerU (Magic-PDF) 引擎适配 — 中文/复杂文档最佳"""

import logging
from pathlib import Path

from pdf_pilot.engines.base import EngineBase
from pdf_pilot.model import (
    Block,
    BlockType,
    ExtractedDocument,
    Table,
)

logger = logging.getLogger(__name__)


class MinerUEngine(EngineBase):
    """通过 MinerU (Magic-PDF) 提取 PDF 内容

    MinerU (上海 AI Lab) 特点:
    - 中文原生支持
    - 跨页表格合并
    - 公式 LaTeX 转换
    - VLM 后端 (95+ OmniDocBench 分数)
    - Pipeline 后端 (CPU 友好)

    注意: MinerU 依赖 PyMuPDF<1.25.0，可能与 pymupdf4llm 冲突。
         需独立安装: pip install magic-pdf
    """

    def __init__(self, backend: str = "pipeline"):
        """初始化 MinerU 引擎

        Args:
            backend: 'pipeline' (CPU, 85+ 分) 或 'vlm' (GPU, 95+ 分)
        """
        self.backend = backend
        self._model = None

    @property
    def name(self) -> str:
        return "mineru"

    @property
    def priority(self) -> int:
        return 2  # 中文/复杂文档首选

    def is_available(self) -> bool:
        try:
            import magic_pdf  # noqa: F401
            return True
        except ImportError:
            return False

    def extract(self, pdf_path: str) -> ExtractedDocument:
        """使用 MinerU 提取 PDF 内容"""
        try:
            from magic_pdf.data.data_reader_writer import DataWriter, DataReader
            from magic_pdf.pipe.OC_Pipe import OC_Pipe
            from magic_pdf.pipe.UNI_Pipe import UNI_Pipe
        except ImportError:
            raise ImportError(
                "MinerU (magic-pdf) is not installed. "
                "Install with: pip install magic-pdf\n"
                "Note: MinerU requires PyMuPDF<1.25.0, which may conflict "
                "with pymupdf4llm. Use a separate environment."
            )

        pdf = Path(pdf_path)
        if not pdf.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        # 读取 PDF 内容
        pdf_content = pdf.read_bytes()

        # MinerU 处理
        jf = {
            "version": "1.0",
            "pdf_info": [],
        }

        try:
            pipe = UNI_Pipe(pdf_content, jf, model=None)
            md_content = pipe.pipe_predict()

            # 提取 Markdown
            raw_md = str(md_content) if md_content else ""

            blocks = []
            if raw_md:
                blocks = self._parse_markdown_to_blocks(raw_md)

            return ExtractedDocument(
                title=blocks[0].content if blocks and blocks[0].type == BlockType.HEADING else "",
                blocks=blocks,
                raw_markdown=raw_md,
                metadata={
                    "page_count": 0,
                    "engine": "mineru",
                    "backend": self.backend,
                },
            )
        except Exception as e:
            logger.error(f"MinerU extraction failed: {e}")
            raise

    def _parse_markdown_to_blocks(self, md_text: str) -> list[Block]:
        """将 Markdown 文本解析为结构化 Block"""
        blocks = []
        if not md_text:
            return blocks

        lines = md_text.split("\n")
        in_code_block = False
        code_lines = []

        for line in lines:
            if line.strip().startswith("```"):
                if in_code_block:
                    blocks.append(Block(
                        type=BlockType.CODE,
                        content="\n".join(code_lines),
                    ))
                    code_lines = []
                    in_code_block = False
                else:
                    in_code_block = True
                continue

            if in_code_block:
                code_lines.append(line)
                continue

            if not line.strip():
                continue

            if line.startswith("#"):
                level = 0
                for ch in line:
                    if ch == "#":
                        level += 1
                    else:
                        break
                content = line[level:].strip()
                if content and content[0] == " ":
                    content = content[1:]
                blocks.append(Block(
                    type=BlockType.HEADING,
                    content=content,
                    level=min(level, 6),
                ))
            elif line.strip().startswith(("- ", "* ", "1. ")):
                blocks.append(Block(
                    type=BlockType.LIST_ITEM,
                    content=line.strip(),
                ))
            elif "|" in line or "---" in line:
                blocks.append(Block(
                    type=BlockType.TABLE,
                    content=line.strip(),
                ))
            else:
                blocks.append(Block(
                    type=BlockType.PARAGRAPH,
                    content=line.strip(),
                ))

        return blocks
