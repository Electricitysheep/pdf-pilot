"""引擎抽象基类 — 所有 PDF 引擎必须实现此接口"""

from abc import ABC, abstractmethod

from pdf2doc.model import ExtractedDocument


class EngineBase(ABC):
    """所有 PDF 转换引擎的统一接口"""

    @abstractmethod
    def extract(self, pdf_path: str) -> ExtractedDocument:
        """从 PDF 提取结构化文档

        Args:
            pdf_path: PDF 文件路径

        Returns:
            ExtractedDocument: 统一的文档结构
        """
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """检查引擎依赖是否已安装且可用"""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """引擎名称标识"""
        ...

    @property
    def priority(self) -> int:
        """引擎优先级（数字越小优先级越高），用于降级"""
        return 99

    def extract_batch(self, pdf_paths: list[str]) -> list[ExtractedDocument]:
        """批量提取（默认逐页处理，子类可覆盖以优化）"""
        return [self.extract(p) for p in pdf_paths]
