# indexion readme — README 构建指南

使用模板、文档注释、手写文本和每个包的 README 构建 项目 README。这项技能涵盖**构建方面**：脚手架、生成、规划、组装和验证。评估现有文档请参考 `indexion-documentation`。

## 文件存放位置

项目规范各不相同；编辑前请先检查实际存在的内容：

| 资产 | 已见到的存放模式 |
|------|------------------|
| 配置 | `doc.json` (仓库根目录) **或** `.indexion/readme/doc.json` |
| 每个包的模板 | `docs/templates/readme.md` (无 SoT 常量；通过 `--template` 声明) |
| 静态文本 | `docs/intro.md`, `docs/installation.md`, `docs/license.md`, … |
| 每个包的 README | `cmd/<name>/README.md`, `src/<name>/README.md` |
| 组装后的根 README | 通常为 `README.md`。某些项目使用 `.mbt.md` 后缀，使文件同时成为 MoonBit doctest 模块 — 在这种情况下，`README.md` 是指向 `README.mbt.md` 的软链接。 |
| `.indexion.toml` | `[doc] config_path` / `per_package` 自动加载 doc.json |

**首先要检查的是** `git diff` / `ls -la`：`README.md` 上的软链接、根目录或 `.indexion/readme/` 下的 `doc.json`，以及 `.indexion.toml`。这些文件的存在表明 README 是手动维护、构建组装还是混合模式。

## 工作流程概述

```
doc init                      → .indexion/readme/template.md + doc.json (全新项目)
编辑 doc.json + docs/*.md     → 声明事实来源
doc readme --per-package      → cmd/<pkg>/README.md (API 骨架；非覆盖写入)
手写每个每个包的 README 的概述 / 使用方法 / 选项 / 示例
doc readme --config           → 组装的根 README
plan drift <prev> <new>       → 验证组装输出（或手动编辑）是否纯粹是增量
```

## 第 1 步：初始化（仅限全新项目）

```bash
indexion doc init <project-dir>
```

创建 `.indexion/readme/template.md` + `.indexion/readme/doc.json`。对于已存在 `doc.json` 或 `.indexion.toml` 指向其中一个的项目，可跳过此步骤。

## 第 2 步：配置 doc.json

```json
{
  "$schema": "./schemas/doc-config.schema.json",
  "version": "1.0",
  "spec": "moonbit",
  "output": { "format": "markdown", "filename": "README.md" },
  "packages": [
    {
      "path": "cmd/<name>",
      "title": "<命令名称>",
      "include_in_root": true,
      "sections": ["overview", "usage"]
    }
    // …每个应出现在组装根 README 中的包都有一项条目
  ],
  "root": {
    "output": "README.md",
    "sections": [
      { "type": "static",   "file": "docs/intro.md" },
      { "type": "toc",      "title": "命令" },
      { "type": "packages", "filter": "cmd/**" },
      { "type": "static",   "file": "docs/installation.md" },
      { "type": "static",   "file": "docs/license.md" }
    ]
  }
}
```

**根部分类型：**
- `static` — 原封不动地包含一个 markdown 文件
- `toc` — 插入目录标题
- `packages` — 从 `packages` 数组中提取条目，通过 glob 过滤

**包字段：**
- `include_in_root` — 是否包含在组装的根 README 中
- `sections` — 要提取的 README 标题；由每个包提取流程尊重
  注意：根目录中的 `{ "type": "packages" }` 目前输出一个**包链接表**，而不是每个包的 `sections` 所暗示的丰富概述/使用方法扩展。见下文“已知限制”。

## 第 3 步：生成每个包的 README

```bash
indexion doc readme --per-package src/ cmd/
```

在每个包目录中生成 `README.md`（如果尚不存在）。**非覆盖写入** — 现有的每个包的 README 将保持不变。

骨架仅包含 API（通过 KGF 从 `///` 文档注释中提取）。将其视为起点，之后手动编写文本部分（概述、使用方法、选项、示例）。

```bash
# 单个包输出到标准输出
indexion doc readme src/kgf/lexer/

# 单个包输出到文件
indexion doc readme -o=README.md src/kgf/lexer/
```

**关于副作用**：`doc readme --template=<t> <paths...>`（下文基于模板的模式）遍历给定路径，并**自动创建**每个缺少的包的 README — 即使没有 `--per-package`。如果你在宽路径（`cmd/`, `src/`）上运行它，预期无关包中会出现新文件。使用窄路径或运行后 `grep git status` 进行清理，以避免意外创建。

## 第 4 步：编写静态内容

创建 `docs/intro.md`, `docs/installation.md`, 等 — 任何你的 `root.sections` 引用的内容。这些是手写文本；组装器将它们原封不动地拉入。

## 第 5 步：生成写作计划（可选）

```bash
indexion plan readme --template=docs/templates/readme.md --plans-dir=.indexion/plans src/
```

为手动或 LLM 辅助的编写发出每个部分的写作任务。

## 第 6 步：组装 README

```bash
# 配置驱动（推荐；doc.json 控制布局和包列表）
indexion doc readme --config=doc.json

# 模板驱动（替代方案；{{include:…}} 和 {{packages}} 占位符）
indexion doc readme --template=docs/templates/readme.md -o=README.md cmd/
```

配置路径可以位于仓库根目录或 `.indexion/readme/` 下。通过 `.indexion.toml` 的 `[doc] config_path = "…"`，`--config=` 标志变为可选。

## 第 7 步：使用 `plan drift` 验证

在重新生成**或**任何手动编辑根 README 后，验证更改是否纯粹是增量（无静默删除，无无关部分的重新格式化）：

```bash
# 快照旧版本
git show HEAD:README.md > /tmp/README.before.md

# 与新版本比较
indexion plan drift --top=20 /tmp/README.before.md README.md
```

输出中要查找的内容：
- `Drift terms in /tmp/README.before.md (missing on the other side): (none)` — 未删除任何内容
- `Drift terms in README.md (missing on the other side): …` — 精确地是你打算添加的新词汇（命令名称、新标志、新概念）
- `Cosine similarity` 接近 1.0 对于小的增量更改；如果重新格式化部分，则显著降低

用于 CI 集成：

```bash
indexion plan drift --vocab-threshold=0.05 /tmp/README.before.md README.md
# 如果 cosine_distance > 0.05 则退出 1 — 可用作防止意外大重写的保护
```

此工作流程同样适用于翻译的 README 对（`README.md` ↔ `README-ja.md`）：跨语言漂移检测原生支持，因为词汇子分词委托给 `kgfs/natural/` 中的自然语言 KGF。

## 模板语法

模板文件支持 `{{placeholder}}` 替换：

| 占位符 | 扩展 |
|--------|------|
| `{{include:path}}` | 相对于项目根目录的文件内容 |
| `{{packages}}` | 所有发现的包（通过 CLI `--include` / `--exclude` 过滤） |
| `{{module_doc}}` | 仅模块级文档 |

## .indexion.toml 集成

```toml
[doc]
config_path = "doc.json"   # 无需 --config 自动加载 doc.json
per_package = true         # 使 `doc readme <path>` 默认为 --per-package
```

显式 `--config=…` 始终优先。

## 已知限制：`packages` 根部分生成表而非丰富扩展

`doc-config.schema.json` 允许每个 `packageEntry` 的 `sections: ["overview", "usage", …]`，但当前的 `doc readme --config` 实现在根中发出 `{ "type": "packages" }` 时，不会内联展开这些部分。输出是一个包含空描述的包链接表。

两个实际后果：

1. 如果项目的提交根 README 包含丰富的每个命令概述 / 使用方法段落，它们并非由 `doc readme --config` 生成。它们是手动维护的。将 `doc readme --config -o=/tmp/regen.md` 与提交的 README 对比，以查看有多少是手动编写的；较大的差异意味着 README 主要由手动维护。
2. 对于新命令，你目前需要**此外**手动编辑丰富部分到组装的 README 中，除了将包条目添加到 `doc.json` 和编写每个包的 README。使用上述 `plan drift` 验证来确认手动编辑仅添加，从未删除。

如果你修复此限制（使 `{ "type": "packages" }` 尊重每个条目的 `sections`），请更新此技能以删除本节。

## 常见陷阱

**"doc readme --per-package 未生成任何内容"**
- 所有包都已有 README。该命令仅创建新文件，从不覆盖。先删除现有 README 再重新生成。

**"在 `cmd/` 上运行 `doc readme --template …` 在我未触碰的包中创建了 README"**
- 模板模式作为副作用自动生成缺少的每个包的 README。要么传递窄路径，要么从 `git status` 撤销意外创建。

**"自动生成的每个包的 README 仅是 API 列表"**
- 按设计。手写概述、使用方法、选项、示例。对于 CLI 命令，权威行为来自 `indexion <command> --help`。

**"我对 README.md 的手动编辑将被 `doc readme --config` 擦除"**
- 如果组装器最终生成丰富形状（见“已知限制”），则会擦除。在此之前，组装器生成严格子集（表），你的丰富部分的手动编辑会保留。始终运行 `plan drift` 跨检查以确保。

**"编辑 README.md 摧毁了无关部分"**
- 运行 `plan drift HEAD:README.md README.md` 并查看前一个版本的“在另一侧缺失”输出。如果列出了除 `(none)` 之外的内容，你删除了内容。
