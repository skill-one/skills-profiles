# 代理的命令行界面

面向人类的命令行界面往往会阻塞代理：交互式提示、巨大的前置文档以及没有可复制示例的帮助文本。优先选择能够在无头环境下工作且可在管道中组合的模式。

## 首先采用非交互式

- 每个输入都应该可以表示为标志或标志值。不要要求箭头键、菜单或定时提示。
- 如果缺少标志，**那么**才回退到交互模式——而不是反过来。

**糟糕的示例：** `mycli deploy` → `? 哪个环境？(使用箭头键)`  
**良好的示例：** `mycli deploy --env staging`

## 无需抛出上下文即可发现

- 代理逐步发现子命令：`mycli`，然后 `mycli deploy --help`。不要在每次运行时打印整个手册。
- 让每个子命令拥有自己的文档，这样未使用的命令就不会出现在上下文中。

## 可用的 `--help`

- 每个子命令都有 `--help`。
- 每个 `--help` 都包含**示例**，其中包含实际调用示例。示例比说明性文字更适合模式匹配。

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

- 在有意义的地方接受标准输入（例如 `cat config.json | mycli config import --stdin`）。
- 避免奇特的顺序排列，并避免因缺少值而回退到交互式提示。
- 支持链式操作：`mycli deploy --env staging --tag $(mycli build --output tag-only)`。

## 快速失败并提供可操作的错误

- 在缺少必需标志时：立即退出并显示清晰的错误消息和**正确的示例调用**，而不是挂起。

```text
错误：未指定图像标签。
  mycli deploy --env staging --tag <image-tag>
  可用的标签：mycli build list --output tags
```

## 不可变性

- 代理经常重试。同一个成功的命令运行两次应该是安全的（无操作或明确的“已完成”），而不是重复副作用。

## 具有破坏性的操作

- 添加 `--dry-run`（或等效选项），以便代理在提交前可以预览计划。
- 提供 `--yes` / `--force` 以跳过确认，同时为人类保留安全默认值。

## 可预测的结构

- 在所有地方使用一致的模式，例如 `资源` + `动词`：如果存在 `mycli service list`，那么 `mycli deploy list` 和 `mycli config list` 应该遵循相同的结构。

## 成功输出

- 成功时，返回机器可用的数据：ID、URL、持续时间。纯文本可以；避免仅依赖装饰性输出。

```text
已部署 v1.2.3 到 staging
url: https://staging.myapp.com
deploy_id: dep_abc123
duration: 34s
```

## 审查现有命令行界面时

- 检查：非交互路径、分层帮助、`--help` 上的示例、标准输入/管道故事、包含调用的错误消息、不可变性、干运行、确认跳过标志、一致的命令结构、结构化的成功输出。
