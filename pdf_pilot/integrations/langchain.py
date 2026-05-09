"""LangChain Document integration for pdf_pilot"""

from typing import TYPE_CHECKING, Any, Optional

from pdf_pilot.convert import convert

if TYPE_CHECKING:
    from langchain.docstore.document import Document


def to_langchain_document(
    input_path: str,
    output_path: Optional[str] = None,
    engine: str = "auto",
    extra_meta: Optional[dict] = None,
) -> "Document":
    """将 pdf_pilot 提取的文档转换为 LangChain Document 对象。

    可直接用于 LangChain RAG 流水线（VectorStoreIndex, RetrievalQA 等）。

    Args:
        input_path: PDF 文件路径
        output_path: 输出文件路径（可选）
        engine: 引擎选择 ("auto"/"docling"/"pymupdf"/"mineru")
        extra_meta: 额外元数据（可选）

    Returns:
        LangChain Document 对象

    Examples:
        >>> from pdf_pilot.integrations.langchain import to_langchain_document
        >>> doc = to_langchain_document("report.pdf")
        >>> from langchain.vectorstores import FAISS
        >>> from langchain.embeddings import OpenAIEmbeddings
        >>> db = FAISS.from_documents([doc], OpenAIEmbeddings())
    """
    extracted = convert(input_path, output_path=output_path, engine=engine)

    meta: dict[str, Any] = {
        "source": input_path,
        "engine": extracted.metadata.get("engine", "unknown"),
        "page_count": extracted.page_count,
        "language": extracted.detected_language,
        "block_count": len(extracted.blocks),
    }
    if extra_meta:
        meta.update(extra_meta)

    try:
        from langchain.docstore.document import Document as LCDoc

        return LCDoc(page_content=extracted.raw_markdown, metadata=meta)
    except ImportError:
        raise ImportError(
            "langchain is required for LangChain integration. "
            "Install it with: pip install langchain langchain-core"
        )


def to_langchain_documents(
    input_paths: list[str],
    engine: str = "auto",
    split_by_page: bool = False,
) -> list["Document"]:
    """批量转换多个 PDF 为 LangChain Document 列表。

    Args:
        input_paths: PDF 文件路径列表
        engine: 引擎选择
        split_by_page: 是否按页面分割（每页一个 Document）

    Returns:
        LangChain Document 列表
    """
    docs = []
    for path in input_paths:
        if split_by_page:
            extracted = convert(path, engine=engine)
            for block in extracted.blocks:
                meta = {
                    "source": path,
                    "engine": extracted.metadata.get("engine", "unknown"),
                    "page": block.metadata.get("page", 0),
                }
                try:
                    from langchain.docstore.document import Document as LCDoc

                    docs.append(LCDoc(page_content=block.content, metadata=meta))
                except ImportError:
                    raise ImportError(
                        "langchain is required. pip install langchain"
                    )
        else:
            doc = to_langchain_document(path, engine=engine)
            docs.append(doc)
    return docs
