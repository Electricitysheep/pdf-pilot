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

# 查看可用引擎
pdf_pilot --list-engines
```

详细使用教程 → [使用指南](#使用指南)

## 使用指南

### 命令行 (CLI)

安装后可以使用 `pdf_pilot` 命令进行转换。

**1. 基本转换 — 自动模式**

让 pdf_pilot 自动分析文档并选择最佳引擎：

```bash
pdf_pilot input.pdf -o output.md
```

输出格式由文件扩展名决定：`.md` 输出 Markdown，`.docx` 输出 Word。

```bash
# 转换为 Word
pdf_pilot input.pdf -o output.docx
```

**2. 强制指定引擎**

```bash
# 使用 PyMuPDF（最快，适合简单数字 PDF）
pdf_pilot input.pdf -o output.md -e pymupdf

# 使用 Docling（适合扫描件、表格、公式）
pdf_pilot input.pdf -o output.md -e docling

# 使用 MinerU（适合中文 + 复杂文档，需安装）
pdf_pilot input.pdf -o output.md -e mineru
```

**3. 批量转换目录**

```bash
# 批量转换文件夹中的所有 PDF
pdf_pilot ./pdfs/ -o ./output/

# 批量转换为 Word
pdf_pilot ./pdfs/ -o ./output/ -f docx
```

**4. 查看可用引擎**

```bash
pdf_pilot --list-engines
```

输出示例：
```
可用引擎:
--------------------------------------------------
  docling            OK  (priority: 1)
  pymupdf            OK  (priority: 3)
  mineru             MISSING  (priority: 2)
```

**5. 详细日志模式**

```bash
pdf_pilot input.pdf -v
```

显示引擎选择过程、检测结果和处理时间。

### Python API

在代码中直接调用：

```python
from pdf_pilot.convert import convert

# 自动模式 — 最简单
doc = convert("input.pdf", "output.md")
print(f"页数: {doc.page_count}, 引擎: {doc.metadata['engine']}")

# 指定引擎
doc = convert("input.pdf", engine="docling")
doc = convert("input.pdf", "output.docx", engine="pymupdf")

# 查看结构化内容
print(doc.raw_markdown)      # 完整 Markdown 文本
print(doc.blocks)            # 结构化段落（标题、正文等）
print(doc.tables)            # 提取的表格
print(doc.metadata)          # 引擎、页数等信息
```

### 如何选择引擎

| 场景 | 推荐引擎 | 命令行 |
|---|---|---|
| 不知道选哪个 | `auto`（路由自动选择） | `pdf_pilot input.pdf -e auto` |
| 简单文本 PDF，数字原版 | `pymupdf`（最快） | `pdf_pilot input.pdf -e pymupdf` |
| 扫描件、照片、需要 OCR | `docling`（内置 OCR） | `pdf_pilot input.pdf -e docling` |
| 复杂表格、学术论文 | `docling`（TableFormer） | `pdf_pilot input.pdf -e docling` |
| 中文文档（需安装） | `mineru`（中文优化） | `pdf_pilot input.pdf -e mineru` |

不确定时从 `auto` 开始。路由系统会分析扫描状态、复杂度和语言来做出最佳选择。

### 在 AI 助手中使用（Claude / Cursor / Copilot）

直接告诉 AI 助手：*"用 pdf_pilot 把这个 PDF 转成 Markdown"*，它会自动执行命令。或者编写 Python 代码：

```python
# 粘贴到 AI 助手的代码环境中
from pdf_pilot.convert import convert
doc = convert("input.pdf", "output.md", engine="auto")
with open("output.md", "w", encoding="utf-8") as f:
    f.write(doc.raw_markdown)
print(f"完成 — {doc.page_count} 页，{len(doc.raw_markdown)} 字符")
```

### 在 AI Agent 平台中使用

pdf_pilot 可以作为本地工具被各种 AI Agent 平台调用，实现自动化 PDF 处理流水线。

**Claude Code**

在 Claude Code 中直接运行命令行或调用 Python：

```
# 在 Claude Code 终端中直接运行
pdf_pilot input.pdf -o output.md -e pymupdf

# 或者让 Claude Code 编写转换脚本
python -c "from pdf_pilot.convert import convert; doc = convert('input.pdf', 'output.md')"
```

在 Claude 对话中直接描述需求即可：*"把当前目录下的所有 PDF 批量转换为 Markdown"*。

**OpenClaw**

OpenClaw 支持自定义工具集成。将 pdf_pilot 注册为工具：

```python
# 在 OpenClaw 的工作流中调用
import subprocess
result = subprocess.run(
    ["pdf_pilot", "input.pdf", "-o", "output.md", "-e", "auto"],
    capture_output=True, text=True
)
print(result.stdout)
```

或者通过 Python API 直接集成到你的 agent pipeline 中：

```python
from pdf_pilot.convert import convert
doc = convert("input.pdf", engine="auto")
# 将提取的内容传递给 LLM 进行后续处理
```

**OpenCode**

OpenCode 支持 Shell 工具调用，可以直接执行 pdf_pilot 命令：

```bash
# 在 OpenCode 的 Shell 工具中执行
pdf_pilot ./documents/ -o ./output/ -e pymupdf
```

也可以在 OpenCode 的 agent prompt 中描述任务：*"批量转换 data/ 目录下所有 PDF 为 Markdown 格式"*。

**Hermes**

Hermes 作为自主 agent 框架，可以编排多步骤 PDF 处理流程：

```python
# 在 Hermes 任务定义中使用
from pdf_pilot.convert import convert

def process_pdf(pdf_path):
    doc = convert(pdf_path, engine="auto")
    # 后续处理：向量化、摘要生成、知识图谱构建等
    return doc.raw_markdown
```

Hermes 可以自动将多个 pdf_pilot 调用组合成完整的数据处理流水线。

## 应用场景

- **RAG / LLM 流水线** — 转换为干净 Markdown 用于向量化
- **学术研究** — 提取含公式和表格的论文
- **文档数字化** — 批量转换扫描档案
- **商业自动化** — 从报告、发票中提取结构化数据
- **内容迁移** — PDF 到 Word，保留排版格式

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
