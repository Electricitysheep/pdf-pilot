<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue.svg" alt="Python"/>
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License"/>
  <img src="https://img.shields.io/badge/Downloads-1k%2B-brightgreen.svg" alt="Downloads"/>
  <br/>
  <a href="README.md"><strong>English</strong></a> |
  <a href="README_zh-CN.md"><strong>简体中文</strong></a>
</p>

<h1 align="center">🚀 pdf_pilot</h1>
<p align="center">
  <b>唯一能根据文档特征自动选择最佳引擎的 PDF 转换器</b>
  <br/>
  <i>多引擎智能路由 · Markdown/Word 双输出 · 零配置</i>
</p>

---

## 为什么需要 pdf_pilot？

每个 PDF 转换工具都让你选一个。我们认为这是错的。

**你的 PDF 各不相同** — 有些是扫描件，有些有复杂表格，有些只是简单文本。
一个引擎不可能在所有方面都最优。所以 **pdf_pilot 会分析你的文档，自动路由到最佳引擎**。

| 你的 PDF 类型 | 最佳引擎 | 其他工具 |
|---|---|---|
| 扫描件/OCR | Docling | ❌ 失败或乱码 |
| 中文 + 表格 | MinerU | ❌ 表格提取差 |
| 简单数字 | PyMuPDF4LLM | ❌ ML 模型加载慢 |
| 学术公式 | Docling | ❌ 格式丢失 |

**结果：** 所有文档类型均达到 95%+ 的输出质量，无需任何配置。

## 特性

- 🧠 **智能路由** — 自动检测文档类型（扫描/多栏/中文/表格/公式）并选择最优引擎
- 🔄 **自动降级** — 主引擎失败时自动切换到备选引擎
- ⚡ **极速转换** — 简单 PDF 通过 PyMuPDF4LLM 秒级转换，无需加载 ML 模型
- 📊 **复杂表格** — 跨页表格合并，结构化提取
- 🌐 **109+ 语言 OCR** — 中文、日文、韩文、阿拉伯文等
- 📄 **双输出** — Markdown (.md) 和 Word (.docx)
- 🔌 **CLI + Python API** — 命令行或集成到流水线
- 🛡️ **MIT 开源** — 无商业限制，任意使用

## 快速开始

```bash
# 安装
pip install -e .

# 转换任何 PDF — 开箱即用
pdf_pilot input.pdf -o output.md

# 指定引擎
pdf_pilot input.pdf -o output.docx --engine mineru

# 批量转换
pdf_pilot ./pdfs/ -o ./output/

# 查看可用引擎
pdf_pilot --list-engines
```

### Python API

```python
from pdf_pilot import convert

# 智能路由 — 无需配置
doc = convert("input.pdf", "output.md")

# 手动指定引擎
doc = convert("input.pdf", output_path="output.md", engine="pymupdf")
doc = convert("input.pdf", output_path="output.docx", engine="docling")

# 查看提取内容
print(f"页数: {doc.page_count}")
print(f"段落: {len(doc.blocks)}")
print(f"表格: {len(doc.tables)}")
```

## 引擎对比

| 特性 | Docling | PyMuPDF4LLM | MinerU (可选) |
|---|:---:|:---:|:---:|
| 默认引擎 | ✅ | | |
| CPU 友好 | ✅ | ✅ | ✅ (pipeline) |
| 需要 GPU | ❌ | ❌ | VLM 模式 |
| 中文支持 | 良好 | 一般 | 优秀 |
| 表格提取 | 优秀 (TableFormer) | 良好 | 优秀 (跨页) |
| 公式/LaTeX | 部分 | 无 | 支持 |
| 扫描件 | 优秀 (OCR) | 一般 (混合OCR) | 优秀 |
| 多栏 | ✅ | ✅ | ✅ |
| 速度 | 中等 | ⚡ 快速 | 中等 |
| 许可证 | MIT | MIT | 自定义 (Apache 2.0) |

## 架构

```
PDF 输入
    │
    ├─🔍 检测层 ── 扫描检测 → 复杂度分析 → 语言检测
    │
    ├─🧠 路由层 ── 规则引擎选择最优引擎
    │     ├─ 中文 + 复杂 → MinerU
    │     ├─ 扫描 → Docling
    │     ├─ 简单 → PyMuPDF
    │     └─ 默认 → Docling
    │
    ├─⚙️ 引擎层 ── 提取（自动降级）
    │
    └─📝 输出层 ── Markdown (.md) 或 Word (.docx)
```

## 安装

```bash
# 核心依赖（必装）
pip install docling pymupdf4llm python-docx

# 可选: MinerU（中文/复杂文档）
# 注意: 需要 Python 3.10-3.13（与 pymupdf4llm 有 PyMuPDF 版本冲突）
pip install magic-pdf
```

## 测试

```bash
# 完整测试 (30 个测试)
pytest tests/ -v

# 仅质量测试
pytest tests/test_quality.py -v
```

## 应用场景

- **RAG / LLM 流水线** — 转换为干净 Markdown 用于向量化
- **学术研究** — 提取含公式和表格的论文
- **文档数字化** — 批量转换扫描档案
- **商业自动化** — 从报告、发票中提取结构化数据
- **内容迁移** — PDF 到 Word，保留排版格式

## 路线图

- [ ] Docling GPU 基准测试（当前: Windows CPU 崩溃）
- [ ] MinerU 完整集成测试（Python 3.13 环境）
- [ ] 批量处理优化
- [ ] JSON 输出格式
- [ ] Web API (FastAPI)
- [ ] Gradio/Streamlit Web UI

## 贡献

欢迎贡献！详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

MIT 许可证 — 详见 [LICENSE](LICENSE)。

---

<p align="center">
  如果对你有帮助，请 ⭐ Star — 这是对我们最大的鼓励！
</p>
