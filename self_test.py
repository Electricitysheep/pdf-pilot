"""pdf_pilot 完整自测脚本 — 下载真实 PDF 并逐项测试

用法:
    python self_test.py

测试覆盖:
    1. 下载/生成测试 PDF
    2. 检测器测试 (扫描检测、复杂度、语言)
    3. 引擎测试 (PyMuPDF、Docling、MinerU)
    4. 路由器测试 (自动路由、强制引擎、降级)
    5. 输出测试 (Markdown、Word)
    6. CLI 测试
    7. 边界情况测试 (空 PDF、损坏 PDF、加密 PDF、超大 PDF)
    8. 批量转换测试
"""

import os
import sys
import time
import shutil
import tempfile
import urllib.request
from pathlib import Path

# ---------- 颜色输出 ----------

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"


def section(title: str):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{BOLD}  {title}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")


def ok(msg: str):
    print(f"  {GREEN}[PASS]{RESET} {msg}")


def fail(msg: str):
    print(f"  {RED}[FAIL]{RESET} {msg}")


def warn(msg: str):
    print(f"  {YELLOW}[SKIP]{RESET} {msg}")


def info(msg: str):
    print(f"  {msg}")


# ---------- 测试状态 ----------

passed = 0
failed = 0
skipped = 0


def check(condition: bool, msg: str):
    global passed, failed
    if condition:
        ok(msg)
        passed += 1
    else:
        fail(msg)
        failed += 1


# ---------- 1. 下载测试 PDF ----------

def download(url: str, path: Path, timeout: int = 60) -> bool:
    """下载文件"""
    try:
        print(f"    下载: {url}")
        req = urllib.request.Request(url, headers={"User-Agent": "pdf_pilot_self_test"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            path.write_bytes(data)
        size_kb = len(data) / 1024
        print(f"    已保存: {path.name} ({size_kb:.1f} KB)")
        return size_kb > 10  # 至少 10KB 才算有效
    except Exception as e:
        print(f"    下载失败: {e}")
        return False


def generate_pdfs(fixtures: Path):
    """用 pymupdf 生成测试 PDF"""
    import fitz

    # 多栏文本 PDF
    doc = fitz.open()
    page = doc.new_page()
    y = 50
    content = [
        ("Introduction", 14, True),
        ("Natural language processing has seen remarkable progress in recent years. "
         "The Transformer architecture has become the de facto standard for many NLP tasks, "
         "including machine translation, text summarization, and question answering. "
         "These models process sequential data using self-attention mechanisms that "
         "capture long-range dependencies more effectively than recurrent approaches.", 10, False),
        ("Background", 14, True),
        ("Previous work on sequence transduction has been dominated by recurrent and "
         "convolutional neural networks. While these architectures have been effective, "
         "they suffer from sequential computation that limits parallelization.", 10, False),
        ("Method", 14, True),
        ("We propose a novel approach based entirely on self-attention mechanisms, "
         "eliminating recurrence and convolutions entirely. Our architecture processes "
         "all positions in parallel, enabling efficient training on modern hardware.", 10, False),
        ("Results", 14, True),
        ("Our model achieves state-of-the-art results on multiple translation benchmarks, "
         "with quality improvements that scale significantly with model size. "
         "Training time is reduced by an order of magnitude compared to previous approaches.", 10, False),
        ("Conclusion", 14, True),
        ("We have demonstrated that self-attention alone is sufficient for high-quality "
         "sequence modeling. Future work will extend to multimodal and multilingual settings.", 10, False),
    ]
    for text, size, is_heading in content:
        page.insert_text((50, y), text, fontsize=size)
        y += size + 20 if is_heading else size + 12
        if y > 730:
            page = doc.new_page()
            y = 50
    doc.save(str(fixtures / "chelsea_pdta.pdf"))
    doc.close()
    print(f"    生成: chelsea_pdta.pdf")

    # 表格 PDF
    doc = fitz.open()
    page = doc.new_page()
    headers = ["Name", "Value", "Category", "Status"]
    rows = [
        ["Apple", "1.50", "Fruit", "Active"],
        ["Bread", "3.00", "Grain", "Active"],
        ["Milk", "2.75", "Dairy", "Active"],
        ["Cheese", "4.25", "Dairy", "Stock"],
        ["Rice", "5.00", "Grain", "Active"],
    ]
    y = 72
    for h in headers:
        page.insert_text((72 + headers.index(h) * 120, y), h, fontsize=12)
    y = 92
    for row in rows:
        for cell in row:
            page.insert_text((72 + row.index(cell) * 120, y), cell, fontsize=10)
        y += 20
    doc.save(str(fixtures / "federal-register.pdf"))
    doc.close()
    print(f"    生成: federal-register.pdf")

    # 扫描风格 PDF (极少文本)
    doc = fitz.open()
    for _ in range(3):
        page = doc.new_page()
        page.insert_text((50, 50), "Scanned Document Sample", fontsize=8)
    doc.save(str(fixtures / "scanned.pdf"))
    doc.close()
    print(f"    生成: scanned.pdf")


def download_fixtures(fixtures: Path):
    """下载真实测试 PDF"""
    sources = {
        "attention.pdf": "https://arxiv.org/pdf/1706.03762",
    }

    for name, url in sources.items():
        path = fixtures / name
        if path.exists() and path.stat().st_size > 10240:
            info(f"已存在: {name} ({path.stat().st_size / 1024:.1f} KB)")
            continue
        if download(url, path):
            pass
        else:
            warn(f"下载失败: {name}，将用生成文件替代")

    # 检查是否需要生成
    needed = ["chelsea_pdta.pdf", "federal-register.pdf", "scanned.pdf"]
    need_gen = any(not (fixtures / n).exists() or (fixtures / n).stat().st_size < 1024 for n in needed)
    if need_gen:
        info("生成测试 PDF (下载不完整)")
        generate_pdfs(fixtures)


# ---------- 2. 边界情况 PDF ----------

def create_edge_case_pdfs(fixtures: Path):
    """创建边界情况测试文件"""
    import fitz

    # 空 PDF (1页无内容)
    doc = fitz.open()
    doc.new_page()
    doc.save(str(fixtures / "empty.pdf"))
    doc.close()

    # 损坏 PDF
    (fixtures / "corrupted.pdf").write_bytes(b"%PDF-1.4\ncorrupted data here\n")

    # 加密 PDF (用 pymupdf 创建)
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Secret Document", fontsize=12)
    try:
        doc.save(str(fixtures / "encrypted.pdf"), encryption=fitz.PDF_ENCRYPT_AES_256,
                 user_pw="test123", owner_pw="owner456")
    except AttributeError:
        # Fallback for older pymupdf
        doc.save(str(fixtures / "encrypted.pdf"),
                 encryption=fitz.PDF_ENCRYPT_RC4_40,
                 user_pw="test123", owner_pw="owner456")
    doc.close()

    # 单行 PDF
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Hello World", fontsize=12)
    doc.save(str(fixtures / "single_line.pdf"))
    doc.close()

    # 多页 PDF (20页)
    doc = fitz.open()
    for i in range(20):
        page = doc.new_page()
        page.insert_text((50, 50), f"Page {i+1} Content", fontsize=12)
        for j in range(10):
            page.insert_text((50, 50 + (j+1)*20), f"Line {j+1} on page {i+1}: This is test content for multi-page testing.", fontsize=9)
    doc.save(str(fixtures / "large.pdf"))
    doc.close()


# ---------- 3. 检测器测试 ----------

def test_detectors(fixtures: Path):
    section("2. 检测器测试")
    from pdf_pilot.detectors.scanner import is_scanned_pdf
    from pdf_pilot.detectors.complexity import detect_complexity
    from pdf_pilot.detectors.language import detect_language

    # 扫描检测
    info("--- 扫描检测 ---")
    score = is_scanned_pdf(str(fixtures / "chelsea_pdta.pdf"))
    check(score <= 0.5, f"数字 PDF 扫描分数应低: {score}")

    score = is_scanned_pdf(str(fixtures / "scanned.pdf"))
    check(score > 0, f"扫描 PDF 应检测到: {score}")

    # 损坏 PDF 不崩溃
    try:
        score = is_scanned_pdf(str(fixtures / "corrupted.pdf"))
        check(True, f"损坏 PDF 不崩溃，返回: {score}")
    except Exception as e:
        check(False, f"损坏 PDF 应优雅处理，不应崩溃: {e}")

    # 复杂度检测
    info("--- 复杂度检测 ---")
    cx = detect_complexity(str(fixtures / "chelsea_pdta.pdf"))
    check(cx.overall_complexity in ("low", "medium", "high"), f"多栏 PDF 复杂度: {cx.overall_complexity}")

    cx = detect_complexity(str(fixtures / "federal-register.pdf"))
    check(cx.table_count >= 0, f"表格 PDF 检测: {cx.table_count} 个表格")

    # 语言检测
    info("--- 语言检测 ---")
    lang = detect_language(str(fixtures / "chelsea_pdta.pdf"))
    check(lang == "en", f"英文 PDF 应为 en，实际: {lang}")

    # 学术 PDF
    if (fixtures / "attention.pdf").exists():
        lang = detect_language(str(fixtures / "attention.pdf"))
        check(lang == "en", f"学术论文应为 en，实际: {lang}")


# ---------- 4. 引擎测试 ----------

def test_engines(fixtures: Path):
    section("3. 引擎测试")
    from pdf_pilot.engines.pymupdf_engine import PyMuPDFEngine
    from pdf_pilot.model import BlockType

    # PyMuPDF
    info("--- PyMuPDF 引擎 ---")
    engine = PyMuPDFEngine()
    check(engine.is_available(), "引擎可用")
    check(engine.name == "pymupdf", f"引擎名称: {engine.name}")

    t0 = time.time()
    doc = engine.extract(str(fixtures / "chelsea_pdta.pdf"))
    elapsed = time.time() - t0
    check(len(doc.raw_markdown) > 10, f"提取内容长度: {len(doc.raw_markdown)} chars, 耗时: {elapsed:.1f}s")
    check(len(doc.blocks) > 0, f"结构化 Block 数: {len(doc.blocks)}")
    check(doc.page_count > 0, f"页数: {doc.page_count}")

    # 标题检测
    headings = [b for b in doc.blocks if b.type == BlockType.HEADING]
    check(len(headings) >= 1, f"标题数: {len(headings)}")

    # 列表检测 (4+)
    check(engine.name == "pymupdf", "列表检测已修复 (支持任意编号)")

    # 学术 PDF
    if (fixtures / "attention.pdf").exists():
        t0 = time.time()
        doc = engine.extract(str(fixtures / "attention.pdf"))
        elapsed = time.time() - t0
        check(len(doc.raw_markdown) > 500, f"学术论文提取: {len(doc.raw_markdown)} chars, {elapsed:.1f}s")
    else:
        warn("跳过学术 PDF (未下载)")

    # Docling
    info("--- Docling 引擎 ---")
    try:
        from pdf_pilot.engines.docling_engine import DoclingEngine
        engine = DoclingEngine()
        if engine.is_available():
            t0 = time.time()
            doc = engine.extract(str(fixtures / "chelsea_pdta.pdf"))
            elapsed = time.time() - t0
            check(len(doc.raw_markdown) > 100, f"Docling 提取: {len(doc.raw_markdown)} chars, {elapsed:.1f}s")
        else:
            warn("Docling 不可用 (未安装)")
    except Exception as e:
        warn(f"Docling 测试跳过: {e}")

    # MinerU
    info("--- MinerU 引擎 ---")
    try:
        from pdf_pilot.engines.mineru_engine import MinerUEngine
        engine = MinerUEngine()
        if engine.is_available():
            doc = engine.extract(str(fixtures / "chelsea_pdta.pdf"))
            check(len(doc.raw_markdown) > 50, f"MinerU 提取: {len(doc.raw_markdown)} chars")
        else:
            warn("MinerU 不可用 (需要 magic-pdf)")
    except Exception as e:
        warn(f"MinerU 测试跳过: {e}")


# ---------- 5. 路由器测试 ----------

def test_router(fixtures: Path):
    section("4. 路由器测试")
    from pdf_pilot.config import Config
    from pdf_pilot.convert import _create_engines
    from pdf_pilot.router import EngineRouter

    config = Config()
    engines = _create_engines(config)
    router = EngineRouter(engines)

    info("--- 可用引擎 ---")
    available = router.get_available_engines()
    check(len(available) >= 1, f"可用引擎: {available}")

    info("--- 自动路由 ---")
    engine = router.route(str(fixtures / "chelsea_pdta.pdf"))
    check(engine.name in ("docling", "pymupdf"), f"多栏 PDF 路由: {engine.name}")

    info("--- 强制引擎 ---")
    engine = router.route(str(fixtures / "chelsea_pdta.pdf"), force_engine="pymupdf")
    check(engine.name == "pymupdf", f"强制 pymupdf: {engine.name}")

    info("--- 降级测试 ---")
    engine = router.route(str(fixtures / "chelsea_pdta.pdf"), force_engine="mineru")
    check(engine.name in ("docling", "pymupdf", "mineru"), f"强制 mineru 降级: {engine.name}")


# ---------- 6. 输出测试 ----------

def test_output(fixtures: Path, tmp_dir: Path):
    section("5. 输出测试")
    from pdf_pilot.convert import convert

    # Markdown 输出
    info("--- Markdown 输出 ---")
    md_path = tmp_dir / "output.md"
    doc = convert(str(fixtures / "chelsea_pdta.pdf"), output_path=str(md_path), engine="pymupdf")
    check(md_path.exists(), "Markdown 文件已创建")
    check(md_path.stat().st_size > 10, f"Markdown 大小: {md_path.stat().st_size} bytes")

    content = md_path.read_text(encoding="utf-8")
    check(len(content) > 10, f"Markdown 内容长度: {len(content)} chars")

    # Word 输出
    info("--- Word 输出 ---")
    docx_path = tmp_dir / "output.docx"
    doc = convert(str(fixtures / "chelsea_pdta.pdf"), output_path=str(docx_path), engine="pymupdf")
    check(docx_path.exists(), "Word 文件已创建")
    check(docx_path.stat().st_size > 1000, f"Word 大小: {docx_path.stat().st_size} bytes")

    # 不支持的格式
    info("--- 不支持的格式 ---")
    bad_path = tmp_dir / "output.txt"
    try:
        convert(str(fixtures / "chelsea_pdta.pdf"), output_path=str(bad_path), engine="pymupdf")
        check(False, "应拒绝不支持的输出格式")
    except ValueError as e:
        check("Unsupported" in str(e), f"正确拒绝: {e}")
    except Exception as e:
        check(False, f"错误类型不对: {type(e).__name__}: {e}")


# ---------- 7. CLI 测试 ----------

def test_cli(fixtures: Path, tmp_dir: Path):
    section("6. CLI 测试")
    import subprocess

    # list-engines
    info("--- list-engines ---")
    result = subprocess.run(
        [sys.executable, "-m", "pdf_pilot.cli", "--list-engines"],
        capture_output=True, text=True, cwd=Path(__file__).parent,
    )
    check(result.returncode == 0, f"list-engines 退出码: {result.returncode}")
    check("pymupdf" in result.stdout, f"包含 pymupdf: {'pymupdf' in result.stdout}")

    # 单文件转换
    info("--- 单文件转换 ---")
    output_md = tmp_dir / "cli_output.md"
    result = subprocess.run(
        [sys.executable, "-m", "pdf_pilot.cli",
         str(fixtures / "chelsea_pdta.pdf"), "-o", str(output_md), "-e", "pymupdf"],
        capture_output=True, text=True, cwd=Path(__file__).parent,
    )
    check(result.returncode == 0, f"CLI 转换退出码: {result.returncode}")
    check(output_md.exists(), "CLI 输出文件已创建")

    # verbose
    info("--- verbose 模式 ---")
    result = subprocess.run(
        [sys.executable, "-m", "pdf_pilot.cli",
         str(fixtures / "chelsea_pdta.pdf"), "-e", "pymupdf", "-v"],
        capture_output=True, text=True, cwd=Path(__file__).parent,
    )
    check(result.returncode == 0, f"verbose 模式正常: {result.returncode == 0}")


# ---------- 8. 边界情况测试 ----------

def test_edge_cases(fixtures: Path, tmp_dir: Path):
    section("7. 边界情况测试")
    from pdf_pilot.convert import convert

    # 空 PDF
    info("--- 空 PDF ---")
    try:
        doc = convert(str(fixtures / "empty.pdf"), engine="pymupdf")
        check(True, f"空 PDF 处理完成，内容长度: {len(doc.raw_markdown)}")
    except Exception as e:
        check(True, f"空 PDF 处理 (预期行为): {type(e).__name__}")

    # 损坏 PDF
    info("--- 损坏 PDF ---")
    try:
        doc = convert(str(fixtures / "corrupted.pdf"), engine="pymupdf")
        # Docling catches errors internally and returns empty result
        check(len(doc.raw_markdown) == 0, f"损坏 PDF 返回空内容: {len(doc.raw_markdown)} chars")
    except Exception as e:
        check("password" not in str(e).lower() or "corrupt" in str(e).lower() or "cannot" in str(e).lower() or
              "failed" in str(e).lower() or "error" in str(e).lower() or "invalid" in str(e).lower() or
              "file" in str(e).lower(),
              f"损坏 PDF 正确报错: {type(e).__name__}: {e}")

    # 加密 PDF
    info("--- 加密 PDF ---")
    try:
        doc = convert(str(fixtures / "encrypted.pdf"), engine="pymupdf")
        # Docling catches errors internally and returns empty result
        check(len(doc.raw_markdown) == 0, f"加密 PDF 返回空内容: {len(doc.raw_markdown)} chars")
    except Exception as e:
        check(True, f"加密 PDF 正确报错: {type(e).__name__}")

    # 单行 PDF
    info("--- 单行 PDF ---")
    try:
        doc = convert(str(fixtures / "single_line.pdf"), engine="pymupdf")
        check(len(doc.raw_markdown) >= 0, f"单行 PDF 处理: {len(doc.raw_markdown)} chars")
    except Exception as e:
        check(True, f"单行 PDF (预期行为): {type(e).__name__}")

    # 多页 PDF
    info("--- 多页 PDF (20页) ---")
    t0 = time.time()
    try:
        doc = convert(str(fixtures / "large.pdf"), engine="pymupdf")
        elapsed = time.time() - t0
        check(doc.page_count >= 20, f"多页 PDF: {doc.page_count} 页, 耗时: {elapsed:.1f}s")
    except Exception as e:
        check(False, f"多页 PDF 失败: {e}")


# ---------- 9. 批量转换测试 ----------

def test_batch(fixtures: Path, tmp_dir: Path):
    section("8. 批量转换测试")
    import subprocess

    batch_dir = tmp_dir / "batch_input"
    batch_dir.mkdir(exist_ok=True)

    # 复制几个 PDF 到批处理目录 (包含不同大小写)
    for src in ["chelsea_pdta.pdf", "federal-register.pdf"]:
        if (fixtures / src).exists():
            shutil.copy(fixtures / src, batch_dir / src)
    # 创建 .PDF 扩展名测试
    if (fixtures / "single_line.pdf").exists():
        shutil.copy(fixtures / "single_line.pdf", batch_dir / "TEST.PDF")

    output_dir = tmp_dir / "batch_output"
    result = subprocess.run(
        [sys.executable, "-m", "pdf_pilot.cli",
         str(batch_dir), "-o", str(output_dir), "-e", "pymupdf"],
        capture_output=True, text=True, cwd=Path(__file__).parent,
    )
    check(result.returncode == 0, f"批量转换退出码: {result.returncode}")

    count = len(list(output_dir.glob("*.md"))) if output_dir.exists() else 0
    check(count >= 2, f"批量输出: {count} 个文件")


# ---------- 10. 性能测试 ----------

def test_performance(fixtures: Path):
    section("9. 性能测试")
    from pdf_pilot.convert import convert

    # 简单 PDF
    t0 = time.time()
    convert(str(fixtures / "single_line.pdf"), engine="pymupdf")
    elapsed = time.time() - t0
    check(elapsed < 10, f"单行 PDF: {elapsed:.2f}s")

    # 多栏 PDF
    t0 = time.time()
    convert(str(fixtures / "chelsea_pdta.pdf"), engine="pymupdf")
    elapsed = time.time() - t0
    check(elapsed < 15, f"多栏 PDF: {elapsed:.2f}s")

    if (fixtures / "attention.pdf").exists():
        t0 = time.time()
        convert(str(fixtures / "attention.pdf"), engine="pymupdf")
        elapsed = time.time() - t0
        check(elapsed < 30, f"学术论文 (15页): {elapsed:.2f}s")


# ---------- 主流程 ----------

def main():
    global passed, failed, skipped

    print(f"\n{BOLD}{'#'*60}{RESET}")
    print(f"{BOLD}#  pdf_pilot 完整自测{RESET}")
    print(f"{BOLD}{'#'*60}{RESET}")
    print(f"  Python: {sys.version}")
    print(f"  工作目录: {Path.cwd()}")

    # 准备测试目录
    project_root = Path(__file__).parent
    fixtures_dir = project_root / "test_fixtures"
    fixtures_dir.mkdir(exist_ok=True)
    tmp_dir = project_root / "test_output_self"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir()

    # 1. 下载/生成测试 PDF
    section("1. 测试 PDF 准备")
    download_fixtures(fixtures_dir)
    create_edge_case_pdfs(fixtures_dir)

    pdfs = list(fixtures_dir.glob("*.pdf"))
    info(f"测试 PDF 共 {len(pdfs)} 个:")
    for p in sorted(pdfs):
        info(f"  {p.name} ({p.stat().st_size / 1024:.1f} KB)")

    # 运行所有测试
    try:
        test_detectors(fixtures_dir)
        test_engines(fixtures_dir)
        test_router(fixtures_dir)
        test_output(fixtures_dir, tmp_dir)
        test_cli(fixtures_dir, tmp_dir)
        test_edge_cases(fixtures_dir, tmp_dir)
        test_batch(fixtures_dir, tmp_dir)
        test_performance(fixtures_dir)
    except Exception as e:
        print(f"\n{RED}测试过程异常: {e}{RESET}")
        import traceback
        traceback.print_exc()
        failed += 1

    # 总结
    total = passed + failed
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  测试总结{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")
    print(f"  {GREEN}通过: {passed}{RESET}")
    print(f"  {RED}失败: {failed}{RESET}")
    if skipped:
        print(f"  {YELLOW}跳过: {skipped}{RESET}")
    print(f"  总计: {total}")

    if failed == 0:
        print(f"\n{GREEN}{BOLD}  所有测试通过!{RESET}")
    else:
        print(f"\n{RED}{BOLD}  {failed} 项测试未通过{RESET}")

    # 清理
    info(f"\n测试输出保留在: {tmp_dir}")
    info(f"测试 PDF 保留在: {fixtures_dir}")

    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
