# 模型使用

## 概述

从 CodexBar 的本地成本日志中获取每个模型的成本。支持 Codex 或 Claude 的 "当前模型"（最新每日条目）或 "所有模型" 汇总。

CodexBar 为 macOS 和 Linux 提供 CLI 构建版本。当 `codexbar` 在 `PATH` 中时，该技能直接读取本地使用情况；捆绑的 Python 汇总器也接受通过 `--input` 任何 Python 可用位置的导出 CodexBar JSON。

## 快速入门

1. 通过 CodexBar CLI 获取成本 JSON 或传递 JSON 文件。
2. 使用捆绑的脚本按模型进行汇总。

```bash
python {baseDir}/scripts/model_usage.py --provider codex --mode current
python {baseDir}/scripts/model_usage.py --provider codex --mode all
python {baseDir}/scripts/model_usage.py --provider claude --mode all --format json --pretty
```

## 当前模型逻辑

- 使用带有 `modelBreakdowns` 的最新每日行。
- 选择该行中成本最高的模型。
- 当缺少细分时，回退到 `modelsUsed` 中的最后一条记录。
- 当需要特定模型时，使用 `--model <name>` 覆盖。

## 输入

- 默认：运行 `codexbar cost --format json --provider <codex|claude>`。
- macOS 和 Linux：使用上述捆绑的 Homebrew 公式安装程序进行实时本地使用情况读取。Linux 用户还可以使用 CodexBar 的 [AUR 软件包](https://aur.archlinux.org/packages/codexbar-cli) 或 [官方发布 tarball](https://github.com/steipete/CodexBar/releases)。
- 其他平台：使用 `--input` 与导出的 CodexBar JSON。
- 文件或标准输入：

```bash
codexbar cost --provider codex --format json > /tmp/cost.json
python {baseDir}/scripts/model_usage.py --input /tmp/cost.json --mode all
cat /tmp/cost.json | python {baseDir}/scripts/model_usage.py --input - --mode current
```

## 输出

- 文本（默认）或 JSON (`--format json --pretty`)。
- 值是每个模型的成本；CodexBar 输出中不会按模型分割 token。

## 参考

- 阅读 `references/codexbar-cli.md` 了解 CLI 标志和成本 JSON 字段。
