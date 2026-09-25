# 开放知识格式 (OKF)

[OKF v0.2](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md) 是一种用于智能体可读知识的便携格式：Markdown 文件、YAML 前置文本和标准链接。`/open-knowledge` 技能管理工具使用；该技能涵盖 OKF 语义。

## 核心规则

- 包是一个 `.md` 文件组成的目录树。每个非保留文件是一个概念；其不包含 `.md` 的路径是其 ID。
- 每个概念都需要可解析的前置文本，其中包含非空字符串 `type`。其他字段不是必需的。
- 类型是一个开放词汇表。消费者必须接受未知类型和元数据。
- 使用标准 Markdown 链接表示便携关系。允许断链和索引缺失。
- `index.md` 和 `log.md` 在所有层级都是保留的。使用小写文件名。
- `index.md` 通常没有前置文本；只有根索引可以声明 `okf_version: "0.2"`。
- `log.md` 按最新优先排序；条目标题以 ISO 日期开头 —— `## YYYY-MM-DD: 摘要`（日期后的摘要是可选的；裸的 `## YYYY-MM-DD` 也是符合规范的）。
- OKF 消费者读取 `.md`，而不是 `.mdx`。

## 作者判断

- 使每个概念成为最小的有用链接或引文目标。选择稳定、描述性的类型；`Document` 只是一个通用的后备选项。
- 不要编造事实、关系、资源、来源、验证或历史。缺失知识比错误结构更好。
- 只有在添加真实信息时才使用 `title`、`description`、`resource` 和 `tags`。
- 在 `sources` 中记录来源。使用匹配的 `sources[].id` 将声明级别的引文与 Markdown 脚注连接起来。
- 将作者身份和验证分开：`generated` 指示谁生成了内容；`verified` 指示谁确认了它。在适用时使用精确的小写 `human:` 和 `process:` 前缀。
- 将每个来源时间戳写为 ISO 8601 datetime 并带有明确的 UTC 偏移 (`stale_after: 2026-12-31T00:00:00Z`)，绝不使用裸日期或无偏移的时间。这涵盖 `generated.at`、`verified[].at`、`stale_after`、`sources[].last_modified` 和 `usage_window` 的两个边界。`log.md` 条目标题是不同的：它保持为纯 `YYYY-MM-DD` 日期。
- 将 `status: deprecated` 和过期的 `stale_after` 值视为可信信号，而不是验证错误。
- 对于 `type: Attested Computation`，遵循声明的运行时和参数。不要重写受认可的运算。

## 读取和维护包

- 从最近的 `index.md` 开始，检查前置文本，然后只跟随相关链接。
- 优先使用当前、已验证的来源，但容忍未知类型和不完整的链接。
- 如果包与假设冲突，信任包；如果缺失或不一致，请说明。
- 将持久发现写回相关概念和编写的枚举。
- 当包使用日志时，在持久更改后添加真实的带日期的 `log.md` 条目。
- 在更新概念时读取遗留的 `timestamp` 和正文引文，但优先使用 v0.2 的 `generated.at` 和 `sources`。迁移时绝不编造来源。

## OpenKnowledge 的 `okf` 插件

可选的项目插件在不阻塞写入的情况下提供持续的便携性反馈：

- 写入时警告和项目审计检查结构、前置文本、保留文件、链接和 `.mdx` 使用情况。
- `.ok/okf/*.schema.json` 包含精确的字段契约。读取这些生成的文件而不是猜测；不要编辑它们。
- 确定性的 lint 检查结果建立符合性。智能体判断仍然建立元数据是否真实有用。
- 可选的索引生成维护 `index.md` 文件。生成的索引是机器拥有的：绝不编辑它们，因为 OpenKnowledge 会替换它们的内容。
- `log.md` 保持为编写的，而不是生成的。

插件默认关闭，每条规则都可以禁用。其价值在于当 OpenKnowledge 原生内容会被其他 OKF 消费者误读时提供早期警告。
