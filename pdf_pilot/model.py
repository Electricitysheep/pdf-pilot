"""统一文档数据模型 — 所有引擎的统一输出格式"""

from dataclasses import dataclass, field
from enum import Enum


class BlockType(Enum):
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST_ITEM = "list_item"
    CODE = "code"
    TABLE = "table"
    IMAGE = "image"
    FORMULA = "formula"
    CAPTION = "caption"
    FOOTNOTE = "footnote"


@dataclass
class Block:
    """文档中的一个内容块"""

    type: BlockType
    content: str
    level: int = 0  # 标题层级 (1-6)
    metadata: dict = field(default_factory=dict)


@dataclass
class TableCell:
    """表格单元格"""

    text: str
    row_span: int = 1
    col_span: int = 1


@dataclass
class Table:
    """结构化表格"""

    caption: str = ""
    headers: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)
    num_rows: int = 0
    num_cols: int = 0
    raw_html: str = ""  # 保留原始 HTML 表格


@dataclass
class Image:
    """图片引用"""

    path: str = ""
    description: str = ""
    caption: str = ""
    width: int = 0
    height: int = 0


@dataclass
class Formula:
    """数学公式"""

    latex: str  # LaTeX 表达式
    inline: bool = False  # 行内公式 vs 独立公式
    page: int = 0


@dataclass
class ExtractedDocument:
    """所有引擎统一输出的文档结构"""

    title: str = ""
    blocks: list[Block] = field(default_factory=list)
    tables: list[Table] = field(default_factory=list)
    images: list[Image] = field(default_factory=list)
    formulas: list[Formula] = field(default_factory=list)
    raw_markdown: str = ""  # 原始 Markdown（引擎直接输出）
    metadata: dict = field(default_factory=dict)

    @property
    def page_count(self) -> int:
        return int(self.metadata.get("page_count", 0))

    @property
    def detected_language(self) -> str:
        return self.metadata.get("language", "unknown")
