---
name: cli-for-agents
description: 设计或审查命令行界面（CLI），以便编码代理能够可靠地运行它们：非交互式标志、分层 --help 带示例、标准输入/管道、快速可操作的错误、幂等性、干运行以及可预测的结构。在构建 CLI、添加命令、编写 --help 或当用户提及代理、终端或自动化友好的 CLI 时使用。
---

# 为代理提供的命令行界面

面向人类的命令行界面常常会阻碍代理的使用：交互式提示、庞大的前置文档以及没有可复制示例的帮助文本。应优先选择能够在无头环境下工作且可在管道中组合的模式。

## 优先非交互式操作

- 每个输入都应该能够以标志或标志值的形式表达。不要要求使用方向键、菜单或定时提示。
- 如果缺少标志，**那么**才回退到交互模式——而不是反过来。

**错误示例：** `mycli deploy` → `? 哪个环境？(使用方向键)`  
**正确示例：** `mycli deploy --env staging`

## 无需堆砌上下文即可发现命令

- 代理逐步发现子命令：`mycli`，然后 `mycli deploy --help`。不要在每次运行时打印整个手册。
- 让每个子命令拥有自己的文档，这样未使用的命令就不会出现在上下文中。

## 可用的 `--help`

- 每个子命令都有 `--help`。
- 每个 `--help` 都包含**示例**，并展示实际调用方式。示例比纯文本说明更适合模式匹配。

```text
选项：
  --env     目标环境 (staging, production)
  --tag     图像标签 (默认: latest)
  --force   跳过确认

示例：
  mycli deploy --env staging
  mycli deploy --env production --tag v1.2.3
  mycli deploy --env staging --force
```

## 标准输入、标志和管道

- 在合理的情况下接受标准输入（例如 `cat config.json | mycli config import --stdin`）。
- 避免奇特的 positional 参数顺序，并避免因缺少值而回退到交互式提示。
- 支持链式调用：`mycli deploy --env staging --tag $(mycli build --output tag-only)`。

## 快速失败并提供可操作的错误信息

- 当缺少必需标志时：立即退出并显示清晰的错误信息及**正确的示例调用**，而不是卡住。

```text
错误：未指定图像标签。
  mycli deploy --env staging --tag <image-tag>
  可用标签：mycli build list --output tags
```

## 不可变性

- 代理会频繁重试。同一个成功命令运行两次应该是安全的（无操作或明确的"已完成"），而不是重复副作用。

## 具有破坏性的操作

- 添加 `--dry-run`（或等效选项），以便代理在提交前可以预览计划。
- 提供 `--yes` / `--force` 以跳过确认，同时为人类保留安全默认值。

## 可预测的结构

- 在所有地方使用一致的模式，例如 `资源` + `动词`：如果存在 `mycli service list`，那么 `mycli deploy list` 和 `mycli config list` 应该遵循相同的结构。

## 成功输出

- 成功时，返回机器可用的数据：ID、URL、持续时间。纯文本可以，避免仅依赖装饰性输出。

```text
已部署 v1.2.3 到 staging
url: https://staging.myapp.com
deploy_id: dep_abc123
duration: 34s
```

## 审查现有命令行界面时

- 检查：非交互式路径、分层帮助、`--help` 中的示例、标准输入/管道故事、带调用的错误信息、不可变性、干运行、确认跳过标志、一致的命令结构、结构化的成功输出。
