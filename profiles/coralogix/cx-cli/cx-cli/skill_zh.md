# cx-cli

所有 cx CLI 命令的通用横切行为。

---

## 更新通知

运行任何 cx 命令后，使用以下渠道（按优先级顺序）检查更新通知。如果存在更新版本，请先完成对用户请求的响应，然后在最后提及一次更新。

更新通知始终包含**两部分**——二进制升级和技能刷新。提供两个命令；不要仅提及版本号或仅提及二进制升级。

### 1. 主要渠道——卡通模式 (`-o toon`)

带有 `--output toon` 的命令会在标准输出追加一个**独立的 JSON 行**：

```json
{"_meta":{"update":{"binary":{"current":"0.1.7","latest":"0.2.0","command":"brew upgrade cx"},"skills":{"command":"npx skills add coralogix/cx-cli/skills","docs":"https://github.com/coralogix/cx-cli#install"}}}}
```

扫描标准输出的**最后一行**查找 `_meta.update`。当存在时：

- 二进制升级：`_meta.update.binary.command`（当前版本：`.binary.current`，最新版本：`.binary.latest`）
- 技能刷新：`_meta.update.skills.command`

### 2. 模式启动检查

`cx schema` 在模式 JSON 的**顶层**嵌入相同的 `_meta.update` 对象（不是追加行）。以相同方式检查 `_meta.update.binary` 和 `_meta.update.skills`。

### 3. 备用渠道——人类可读文本

同时扫描标准错误和标准输出查找纯文本通知。二进制和技能显示在同一行，用 `|` 分隔：

```
[cx update] v0.2.0 可用（你拥有 0.1.9） | 升级：brew upgrade cx | 技能：npx skills add coralogix/cx-cli/skills
```

TTY 文本模式使用两行，具有相同的 `upgrade: ... | skills: ...` 模式：

```
cx 0.2.0 可用（你拥有 0.1.9）。
升级：brew upgrade cx | 技能：npx skills add coralogix/cx-cli/skills
```

这些在文本/JSON 模式下的标准错误中显示，在正常命令之后。

### 响应模板

> [在此处总结命令结果]
>
> ---
> 可用更新的 cx 版本（X.Y.Z）——你拥有 A.B.C。是否需要我运行 `<二进制升级命令>` 和 `npx skills add coralogix/cx-cli/skills` 进行更新？

保持一条简短的结束语。不要在会话中的后续命令中重复。

---

## 一般 cx CLI 指南

- 处理结果时始终使用 `--output toon` 获取机器可读输出
- 使用 `cx schema` 发现可用命令及其标志
- 命令支持 `-p profile1 -p profile2` 的多配置分叉
- 对于查询或管理 Coralogix 数据的命令，使用 `--http-timeout <SECONDS>` 或 `CX_HTTP_TIMEOUT=<SECONDS>` 设置 API 请求截止时间
- 使用 `--yes` 在脚本中跳过确认提示
- 使用 `--read-only` 进行安全探索，无需担心修改风险
