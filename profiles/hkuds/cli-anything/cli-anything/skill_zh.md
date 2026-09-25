# CLI-Anything for Codex

当用户希望 Codex 像一个 `CLI-Anything` 构建器一样工作时，请使用此技能。

## 首先阅读完整的方法论

在实施之前，请使用完整的方法论源：

1. 读取相对于此技能目录的 `references/HARNESS.md`。
2. 读取 `references/commands/` 下匹配的模式规范。
3. 仅在它们适用于目标时，读取 `references/guides/` 下引用的文件。
4. 如果安装的资源不可用，并且此技能是从一个 `CLI-Anything` 仓库签出使用的，请读取 `../cli-anything-plugin/HARNESS.md` 以及周围的资源。
5. 如果本地源不可用，请克隆或下载 `https://github.com/HKUDS/CLI-Anything` 并使用 `cli-anything-plugin/HARNESS.md`。
6. 只有当所有完整方法论源都不可用时，才遵循以下简化的规则。

安装程序将 `cli-anything-plugin/` 中的规范资源打包到此技能中，因此一个正常的 Codex 安装是自包含的。

## 资源映射

| 路径 | 目的 |
|------|---------|
| `references/HARNESS.md` | 完整的方法论和质量规则 |
| `references/commands/cli-anything.md` | 构建模式规范 |
| `references/commands/refine.md` | 精炼模式规范 |
| `references/commands/test.md` | 测试模式规范 |
| `references/commands/validate.md` | 验证清单 |
| `references/commands/list.md` | 已安装/生成的 harness 发现 |
| `references/guides/` | 按需实施指导 |
| `scripts/repl_skin.py` | 复制到生成的 harness 中作为 `utils/repl_skin.py` |
| `scripts/preview_bundle.py` | 复制到支持预览的 harness 中作为 `utils/preview_bundle.py` |
| `scripts/skill_generator.py` | 生成规范和打包的 CLI 技能 |
| `scripts/templates/SKILL.md.template` | `skill_generator.py` 使用的技能生成模板 |
| `references/docs/PREVIEW_PROTOCOL.md` | 共享预览包协议 |

在读取打包的文档时，请使用这些路径重映射，而不是将插件路径相对于当前工作目录解析：

| 文档引用 | 已安装技能路径 |
|--------------------|----------------------|
| `guides/...` | `references/guides/...` |
| `cli-anything-plugin/repl_skin.py` | `scripts/repl_skin.py` |
| `cli-anything-plugin/preview_bundle.py` | `scripts/preview_bundle.py` |
| `cli-anything-plugin/skill_generator.py` | `scripts/skill_generator.py` |
| `templates/SKILL.md.template` | `scripts/templates/SKILL.md.template` |
| `docs/PREVIEW_PROTOCOL.md` | `references/docs/PREVIEW_PROTOCOL.md` |

## 输入

接受以下之一：

- 本地源路径，例如 `./gimp` 或 `/path/to/software`
- GitHub 仓库 URL

如果需要，从克隆后的本地目录名中派生软件名称。

## 模式

### 构建

读取 `references/commands/cli-anything.md`。通过源分析、架构设计、实施、测试规划、测试实施、测试文档、CLI 特定的 `SKILL.md` 生成以及本地安装来构建完整的 harness。

### 精炼

读取 `references/commands/refine.md`。清点当前命令和测试，将它们与目标软件进行比较，然后逐步添加高影响力的功能，除非用户要求破坏性更改，否则不删除现有命令。

### 测试

读取 `references/commands/test.md`。运行 harness 测试以针对真实后端，验证已安装命令的子进程覆盖率，并且仅用通过的结果更新 `TEST.md`。

### 验证

读取 `references/commands/validate.md`。验证 harness 是否符合完整目录、实施、测试、文档、打包和代码质量清单。

### 列出

读取 `references/commands/list.md`。发现已安装和生成的 CLI-Anything 工具，并根据请求以人类可读或 JSON 格式输出。

## 简化回退规则

仅在无法检索完整方法论时使用。

### Harness 结构

生成：

```text
<software>/
└── agent-harness/
    ├── <SOFTWARE>.md
    ├── setup.py
    └── cli_anything/
        └── <software>/
            ├── README.md
            ├── __init__.py
            ├── __main__.py
            ├── <software>_cli.py
            ├── core/
            ├── utils/
            └── tests/
```

### 必要行为

- 优先使用真实软件后端而不是重新实现。
- 提供一次性 Click 子命令和默认 REPL 模式。
- 支持 `--json` 机器可读输出。
- 在目标支持的情况下添加会话状态，包括撤销/重做。
- 自动保存一次性会话突变并支持 `--dry-run`。
- 使用锁定会话文件写入以避免并发 JSON 损坏。
- 复制并使用统一的 `ReplSkin`。
- 为具有有意义视觉或检查状态的软件添加诚实的预览命令。
- 生成规范和打包的 CLI 特定的 `SKILL.md` 文件。

### 测试

- 在测试代码之前编写 `TEST.md`。
- 保留 `test_core.py` 以进行单元覆盖率。
- 保留 `test_full_e2e.py` 以进行真实文件工作流和真实后端验证。
- 通过程序方式验证渲染/导出输出，而不仅仅是进程退出代码。
- 通过 `_resolve_cli()` 测试安装的 `cli-anything-<software>` 命令。
- 使用 `CLI_ANYTHING_FORCE_INSTALLED=1` 运行发布验证。

### 打包

- 使用 `find_namespace_packages(include=["cli_anything.*"])`。
- 将 `cli_anything/` 保留为命名空间包，不包含顶层 `__init__.py`。
- 通过 `console_scripts` 暴露 `cli-anything-<software>`。
- 包括打包的 CLI 特定的 `skills/SKILL.md`。

## 输出预期

在报告进度或最终结果时，包括：

- 目标软件和源路径
- 添加或更改的文件
- 运行的验证命令
- 开放的风险或后端限制
