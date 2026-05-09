"""LlamaIndex Document integration for pdf_pilot"""

from typing import TYPE_CHECKING, Optional

from pdf_pilot.convert import convert

if TYPE_CHECKING:
    from llama_index.core.schema import Document as LliDoc


def to_llamaindex_document(
    input_path: str,
    output_path: Optional[str] = None,
    engine: str = "auto",
) -> "LliDoc":
    """将 pdf_pilot 提取的文档转换为 LlamaIndex Document 对象。

    可直接用于 LlamaIndex RAG 索引（VectorStoreIndex, SummaryIndex 等）。

    Args:
        input_path: PDF 文件路径
        output_path: 输出文件路径（可选）
        engine: 引擎选择 ("auto"/"docling"/"pymupdf"/"mineru")

    Returns:
        LlamaIndex Document 对象

    Examples:
        >>> from pdf_pilot.integrations.llamaindex import to_llamaindex_document
        >>> doc = to_llamaindex_document("report.pdf")
        >>> from llama_index.core import VectorStoreIndex
        >>> index = VectorStoreIndex.from_documents([doc])
    """
    extracted = convert(input_path, output_path=output_path, engine=engine)

    meta = {
        "source": input_path,
        "engine": extracted.metadata.get("engine", "unknown"),
        "page_count": extracted.page_count,
        "language": extracted.detected_language,
        "block_count": len(extracted.blocks),
    }

    try:
        from llama_index.core.schema import Document as LliDoc

        return LliDoc(text=extracted.raw_markdown, metadata=meta)
    except ImportError:
        raise ImportError(
            "llama-index is required for LlamaIndex integration. "
            "Install it with: pip install llama-index"
        )


def to_llamaindex_documents(
    input_paths: list[str],
    engine: str = "auto",
) -> list["LliDoc"]:
    """批量转换多个 PDF 为 LlamaIndex Document 列表。

    Args:
        input_paths: PDF 文件路径列表
        engine: 引擎选择

    Returns:
        LlamaIndex Document 列表
    """
    docs = []
    for path in input_paths:
        doc = to_llamaindex_document(path, engine=engine)
        docs.append(doc)
    return docs
