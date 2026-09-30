---
name: indexion-readme
description: README构建 — 初始化模板结构，从文档注释生成每个包的README，规划写作任务，通过doc.json配置从docs/和包README组装根README，并使用`plan drift`验证修改。
---

# indexion readme — README 构建

从模板、文档注释、手写文本和每个包的 README 构建 project README。这项技能涵盖**构建方面**：脚手架、生成、规划、组装和验证。评估现有文档，请参阅 `indexion-documentation`。

## 内容存放位置

规范因项目而异；编辑前请检查实际存在的内容：

| 资产 | 见过的存放位置模式 |
|------|--------------------|
| 配置 | `doc.json`（仓库根目录）**或** `.indexion/readme/doc.json` |
| 每个包的模板 | `docs/templates/readme.md`（没有 SoT 常量；通过 `--template` 声明） |
| 静态文本 | `docs/intro.md`，`docs/installation.md`，`docs/license.md`，… |
| 每个包的 README | `cmd/<name>/README.md`，`src/<name>/README.md` |
| 组装的根 README | 通常为 `README.md`。一些项目使用 `.mbt.md` 后缀，因此文件也是一个 MoonBit doctest 模块——在这种情况下，`README.md` 是指向 `README.mbt.md` 的软链接。 |
| `.indexion.toml` | `[doc] config_path` / `per_package` 自动加载 doc.json |

**首先要检查的是** `git diff` / `ls -la`：`README.md` 上的软链接、`doc.json`（在根目录或 `.indexion/readme/` 下）、`.indexion.toml`。这些存在表明 README 是手动维护的、构建组装的，还是混合的。

## 工作流概述

```
doc init                      → .indexion/readme/template.md + doc.json（空白项目）
编辑 doc.json + docs/*.md     → 声明事实来源
doc readme --per-package      → cmd/<pkg>/README.md（API 骨架；非覆盖）
手写每个每个包的 README 的概述 / 使用 / 选项 / 示例
doc readme --config           → 组装的根 README
plan drift <prev> <new>       → 验证组装输出（或手动编辑）是否纯粹是附加的
```

## 第 1 步：初始化（仅限空白项目）

```bash
indexion doc init <project-dir>
```

创建 `.indexion/readme/template.md` + `.indexion/readme/doc.json`。在已经存在 `doc.json` 或 `.indexion.toml` 指向一个的项目的项目上跳过此步骤。

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
    // …每个应出现在组装的根 README 中的包都有一个条目
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
- `packages` — 从 `packages` 数组中拉取条目，通过 glob 过滤

**包字段：**
- `include_in_root` — 是否包含在组装的根 README 中
- `sections` — 要提取的 README 标题；由每个包提取流程尊重
  注意：根目录中的 `{ "type": "packages" }` 目前发出一个**表格**，而不是每个包的 `sections` 暗示的丰富概述/使用扩展。见“已知限制”下方。

## 第 3 步：生成每个包的 README

```bash
indexion doc readme --per-package src/ cmd/
```

在每个包目录中生成 `README.md`（如果尚未存在）。**非覆盖**——现有的每个包的 README 保持不变。

骨架仅 API（通过 KGF 从 `///` 文档注释中提取）。将其视为起点，之后手动编写文本部分（概述、使用、选项、示例）。

```bash
# 单个包到标准输出
indexion doc readme src/kgf/lexer/

# 单个包到一个文件
indexion doc readme -o=README.md src/kgf/lexer/
```

**关于副作用**：`doc readme --template=<t> <paths...>`（下面的基于模板的模式）遍历给定路径，并**自动创建**缺少的每个包的 README——即使没有 `--per-package`。如果你在宽路径（`cmd/`，`src/`）上运行它，预期在无关的包中创建新文件。使用窄路径或在之后运行 `grep git status` 以清理意外的创建。

## 第 4 步：编写静态内容

创建 `docs/intro.md`，`docs/installation.md`，等等——任何你的 `root.sections` 引用的内容。这些是手写文本；组装器按原样拉取它们。

## 第 5 步：生成写作计划（可选）

```bash
indexion plan readme --template=docs/templates/readme.md --plans-dir=.indexion/plans src/
```

为手动或 LLM 辅助创作发出每个部分的写作任务。

## 第 6 步：组装 README

```bash
# 配置驱动（首选；doc.json 控制布局和包列表）
indexion doc readme --config=doc.json

# 模板驱动（替代方案；{{include:…}} 和 {{packages}} 占位符）
indexion doc readme --template=docs/templates/readme.md -o=README.md cmd/
```

配置路径可以位于仓库根目录或 `.indexion/readme/` 下。使用 `.indexion.toml` 的 `[doc] config_path = "…"`，`--config=` 标志变为可选。

## 第 7 步：使用 `plan drift` 验证

重新生成后**或**对根 README 的任何手动编辑，验证更改是否纯粹是附加的（没有静默删除，没有无关部分的重新格式化）：

```bash
# 快照上一个版本
git show HEAD:README.md > /tmp/README.before.md

# 与新版本比较
indexion plan drift --top=20 /tmp/README.before.md README.md
```

在输出中查找：
- `Drift terms in /tmp/README.before.md (missing on the other side): (none)` — 没有被删除
- `Drift terms in README.md (missing on the other side): …` — 你打算添加的确切词汇（命令名称、新标志、新概念）
- `Cosine similarity` 接近 1.0 对于小的附加更改；如果重新格式化部分，则显著降低

对于 CI 集成：

```bash
indexion plan drift --vocab-threshold=0.05 /tmp/README.before.md README.md
# 如果 cosine_distance > 0.05 则退出 1——作为防止意外大重写的保护
```

此相同工作流适用于翻译的 README 对（`README.md` ↔ `README-ja.md`）：跨语言漂移检测原生工作，因为词汇子标记化委托给 `kgfs/natural/` 中的自然语言 KGF。

## 模板语法

模板文件支持 `{{placeholder}}` 替换：

| 占位符 | 展开 |
|-------|------|
| `{{include:path}}` | 文件内容（相对于项目根目录） |
| `{{packages}}` | 所有发现的包（通过 CLI `--include` / `--exclude` 过滤） |
| `{{module_doc}}` | 仅模块级文档 |

## .indexion.toml 集成

```toml
[doc]
config_path = "doc.json"   # 无需 --config 自动加载 doc.json
per_package = true         # 使 `doc readme <path>` 默认为 --per-package
```

显式的 `--config=…` 总是优先。

## 已知限制：`packages` 根部分产生表格，而不是丰富扩展

`doc-config.schema.json` 允许 `sections: ["overview", "usage", …]` 在每个 `packageEntry` 上，但当前的 `doc readme --config` 实现在发出根中的 `{ "type": "packages" }` 时不会内联扩展这些部分。输出是一个带有空描述的包链接 markdown 表格。

两个实际后果：

1. 如果项目的提交的根 README 包含丰富的每个命令概述 / 使用段落，它们不是由 `doc readme --config` 生成的，因为目前它不支持。它们是手动维护的。将 `doc readme --config -o=/tmp/regen.md` 与提交的 README 进行比较，以查看有多少是手动编写的；很大的差异意味着 README 主要由手动维护。
2. 对于新命令，您目前需要**还**手动编辑丰富的部分到组装的 README 中，除了将包条目添加到 `doc.json` 和编写每个包的 README。使用上述 `plan drift` 验证来确认手动编辑仅添加，从未删除。

如果您修复此限制（使 `{ "type": "packages" }` 尊重每个条目的 `sections`），请更新此技能以删除本节。

## 常见陷阱

**"doc readme --per-package 什么都没生成"**
- 所有包都已经有 README。该命令仅创建新文件，从不覆盖。首先删除现有的 README 以重新生成。

**"doc readme --template … 在 `cmd/` 上创建了我在未触及的包中的 README"**
- 模板模式作为副作用自动生成缺少的每个包的 README。要么传递窄路径，要么从 `git status` 恢复意外的创建。

**"自动生成的每个包的 README 只是 API 列表"**
- 按设计。手写概述、使用、选项、示例。对于 CLI 命令，权威行为来自 `indexion <command> --help`。

**"我对 README.md 的手动编辑将被 `doc readme --config` 擦除"**
- 如果组装器最终产生丰富的形状（见“已知限制”），则会。直到那时，组装器产生严格子集（表格），而您对丰富部分的编辑会保留。始终运行 `plan drift` 跨检查以确保。

**"编辑 README.md 摧毁了无关部分"**
- 运行 `plan drift HEAD:README.md README.md` 并查看先前版本的“在另一边缺失”输出。如果它列出了任何不同于 `(none)` 的内容，则您删除了内容。
