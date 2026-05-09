"""配置管理"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """转换配置"""

    # 引擎设置
    engine: str = "auto"  # auto | docling | mineru | pymupdf
    force_engine: Optional[str] = None

    # Docling 设置
    docling_use_vlm: bool = False

    # MinerU 设置
    mineru_backend: str = "pipeline"  # pipeline | vlm

    # 输出设置
    output_format: str = "md"  # md | docx

    # 行为设置
    verify_quality: bool = False
    batch_size: int = 10
    log_level: str = "INFO"

    # 降级设置
    max_fallbacks: int = 2
