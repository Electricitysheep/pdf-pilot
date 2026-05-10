"""CLI 入口"""

import argparse
import logging
import sys
from pathlib import Path


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        prog="pdf_pilot",
        description="智能路由 PDF 转换工具 — 多引擎自动选择",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  pdf_pilot input.pdf                    # 智能模式 → Markdown
  pdf_pilot input.pdf -o output.md       # 指定输出
  pdf_pilot input.pdf -o output.docx     # Word 输出
  pdf_pilot input.pdf --engine docling   # 强制指定引擎
  pdf_pilot input.pdf --engine pymupdf   # 快速模式
  pdf_pilot input.pdf --engine mineru    # MinerU 模式
  pdf_pilot input.pdf --list-engines     # 查看可用引擎
  pdf_pilot ./pdfs/ -o ./output/         # 批量转换
        """,
    )

    parser.add_argument(
        "input",
        nargs="?",
        help="PDF 输入路径（文件或目录）",
        default=None,
    )
    parser.add_argument(
        "-o",
        "--output",
        help="输出路径（文件或目录）",
        default=None,
    )
    parser.add_argument(
        "-e",
        "--engine",
        choices=["auto", "docling", "mineru", "pymupdf"],
        default="auto",
        help="选择引擎（默认: auto 自动选择）",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["md", "docx"],
        default=None,
        help="输出格式（默认: md）",
    )
    parser.add_argument(
        "--list-engines",
        action="store_true",
        help="列出所有引擎及其可用状态",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="转换后运行质量验证",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="详细日志输出",
    )

    args = parser.parse_args()

    # 配置日志
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # 列出引擎
    if args.list_engines:
        _list_engines()
        return

    # 检查 input 参数
    if not args.input:
        parser.error("the following arguments are required: input")

    # 批量转换
    input_path = Path(args.input)
    if input_path.is_dir():
        _batch_convert(input_path, args)
        return

    # 单文件转换
    _convert_file(input_path, args)


def _list_engines():
    """列出可用引擎"""
    from pdf_pilot.config import Config
    from pdf_pilot.convert import _create_engines

    config = Config()
    engines = _create_engines(config)

    print("\n可用引擎:")
    print("-" * 50)
    for engine in engines:
        status = "OK" if engine.is_available() else "MISSING"
        print(f"  {engine.name:15s}  {status}  (priority: {engine.priority})")
    print()

    unavailable = [e for e in engines if not e.is_available()]
    if unavailable:
        print("不可用引擎的修复方法:")
        for engine in unavailable:
            if engine.name == "mineru":
                print("  mineru: pip install magic-pdf")
                print(
                    "    (注意: 需要 Python 3.10-3.13，与 pymupdf4llm 有 PyMuPDF 版本冲突)"
                )
        print()


def _convert_file(input_path: Path, args):
    """转换单个文件"""
    from pdf_pilot.config import Config
    from pdf_pilot.convert import convert

    # 确定输出路径
    output = args.output
    if not output:
        output = input_path.with_suffix(".md")
    output = Path(output)

    # 确定格式
    if args.format:
        fmt = args.format
    elif output.suffix.lower() == ".docx":
        fmt = "docx"
    else:
        fmt = "md"

    # 配置
    config = Config()
    config.engine = args.engine
    config.output_format = fmt

    print(f"输入: {input_path}")
    print(f"输出: {output}")
    print(f"引擎: {args.engine}")

    try:
        doc = convert(
            str(input_path),
            output_path=str(output),
            engine=args.engine,
            config=config,
        )

        print("\n转换完成!")
        print(f"  页面数: {doc.page_count}")
        print(f"  引擎:   {doc.metadata.get('engine', 'unknown')}")
        print(f"  输出:   {output}")

        if doc.blocks:
            print(f"  段落数: {len(doc.blocks)}")
        if doc.tables:
            print(f"  表格数: {len(doc.tables)}")

    except Exception as e:
        print(f"\n转换失败: {e}", file=sys.stderr)
        sys.exit(1)


def _batch_convert(input_dir: Path, args):
    """批量转换目录下的所有 PDF"""
    from pdf_pilot.config import Config
    from pdf_pilot.convert import convert

    pdfs = sorted([p for p in input_dir.iterdir() if p.suffix.lower() == ".pdf"])
    if not pdfs:
        print(f"在 {input_dir} 中未找到 PDF 文件")
        return

    output_dir = Path(args.output) if args.output else input_dir / "output"

    config = Config()
    config.engine = args.engine
    config.output_format = args.format or "md"

    print(f"批量转换: {len(pdfs)} 个 PDF")
    print(f"输出目录: {output_dir}")
    print()

    success_count = 0
    fail_count = 0

    for pdf in pdfs:
        ext = "docx" if config.output_format == "docx" else "md"
        output_path = output_dir / f"{pdf.stem}.{ext}"

        try:
            convert(
                str(pdf),
                output_path=str(output_path),
                engine=args.engine,
                config=config,
            )
            print(f"  OK {pdf.name}")
            success_count += 1
        except Exception as e:
            print(f"  FAIL {pdf.name}: {e}")
            fail_count += 1

    print(f"\n完成: {success_count} 成功, {fail_count} 失败")


if __name__ == "__main__":
    main()
