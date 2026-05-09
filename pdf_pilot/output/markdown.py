"""Markdown 输出格式化"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def write_markdown(
    md_text: str,
    output_path: str | Path,
) -> Path:
    """将 Markdown 内容写入文件

    Args:
        md_text: Markdown 内容
        output_path: 输出文件路径

    Returns:
        Path: 输出文件路径
    """
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(md_text, encoding="utf-8")
    logger.info(f"Markdown written to {output}")
    return output
