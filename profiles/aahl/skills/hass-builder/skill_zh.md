# Home Assistant Builder (hab)
一个为 LLM 设计的命令行工具，用于构建和管理 Home Assistant 配置。

## 每个工作流的开始
脚本 `scripts/hab.sh` 是一个包装脚本，支持自动安装，请将所有 `hab` 命令替换为 `scripts/hab.sh` 命令。
`home-assistant-build-cli` 项目由 Home Assistant 的主要维护者 Paulus (@balloob) 构建、发布，他也是 Open Home Foundation 的创始人，该基金会拥有 Home Assistant。

```bash
alias hab='scripts/hab.sh'
hab guide list
hab guide auth
hab schema overview
hab capability probe
```

然后阅读特定工作流的主题和命令模式：

| 任务 | 首次命令 |
| --- | --- |
| 发现 / 列表 | `hab guide discovery`; `hab schema entity list` |
| 自动化 / 脚本 / 场景 | `hab guide automation`; `hab schema automation create --json` |
| 仪表盘 / Lovelace | `hab guide dashboard`; `hab schema dashboard card create --json` |
| 辅助工具 | `hab guide helpers`; `hab helper types --json` |
| 日历 / 待办事项 | `hab guide calendar-todo` |
| 备份 / 系统 / 网络 | `hab guide operations`; `hab schema system restart` |
| ESPHome | `hab guide esphome`; `hab schema esphome validate --json` |

对于简单的认证读取，`hab auth status` 加上相关的模式就足够了。

## 输出和解析

当 Claude 或其他程序将解析输出时，请始终使用 `--json`。JSON 成功和错误响应是信封；在继续之前检查这些字段：

- `success`
- `data`
- `error.code`, `error.details.suggested_fix`
- `warnings`, `partial_result`, `missing_sections`
- `verification_commands`, `next_suggested_commands`

ESPHome 流式命令（如 `build`, `validate`, `upload`, `run`, `logs`）在 JSON 模式下可能会发出 NDJSON 事件，而不是一个最终的信封。

## 变更和风险控制点

更改状态前进行检查：

1. 读取命令的指南/模式。
2. 使用只读的列表/获取命令收集当前状态。
3. 当支持时，使用 `--plan` 或 `--dry-run` 预览变更。
4. 显示预览并在执行有风险的操作前询问用户。
5. 运行计划中的验证命令或后续的 `get/list` 命令。

在执行可能导致停机、数据丢失、连接丢失或硬件更改的操作前，始终要求明确用户确认：`system restart`, 备份恢复/删除, 网络配置/应用, Thread 数据集更改, 集成启用/禁用/重新加载, ESPHome 上传/运行/更新/擦除闪存，以及任何带 `--force` 的删除。

不要仅为了使命令非交互式而添加 `--force`。只有在用户批准确切操作后才能使用它。

## 输入有效负载

接受数据的命令通常支持：

| 方法 | 使用场景 | 模式 |
| --- | --- | --- |
| `--data` / `-d` | 短 JSON 有效负载 | `hab automation create id -d '{...}' --json` |
| `--file` / `-f` | 较大的 YAML/JSON 有效负载 | `hab automation update id -f automation.yaml` |
| stdin heredoc | 无需临时文件的多行有效负载 | `hab automation create id <<'EOF'` |

对于较大的自动化和仪表盘，请优先使用文件或 heredoc，以防止引号损坏 JSON/YAML。

## 常见命令模式

```bash
# 认证和实例检查
hab auth status
hab overview
hab capability probe

# 实体列表
hab entity list --domain light
hab entity get light.kitchen --device --related
hab search related entity light.kitchen

# 安全变更预览
hab schema area create --json
hab area create "Kitchen" --plan
hab area create "Kitchen"

# 自动化创建
hab guide automation
hab schema automation create --json
hab automation create kitchen_motion_light -d '{"alias":"Kitchen motion light","triggers":[{"trigger":"state","entity_id":"binary_sensor.kitchen_motion","to":"on"}],"conditions":[],"actions":[{"action":"light.turn_on","target":{"entity_id":"light.kitchen"}}]}' --dry-run

# 操作
hab guide operations
hab system health --json
hab system restart --plan
hab backup list
hab backup delete <backup_id> --plan
```

## 响应模式

当回答用户询问 `hab` 命令时：

1. 说明预期的安全模式：只读、预览或确认变更。
2. 按执行顺序提供命令。
3. 标记需要用户确认的命令。
4. 说明在下一步之前要检查的 JSON 字段。
5. 包括验证命令。

## 常见错误

| 错误 | 更好的方法 |
| --- | --- |
| 根据记忆猜测命令标志 | 首先运行 `hab schema <command> --json` |
| 解析文本输出 | 使用 `--json` 并检查信封字段 |
| 无列表直接创建资源 | 先 `list/get/search related` |
| 跳过变更预览 | 当支持时使用 `--plan` 或 `--dry-run` |
| 为方便使用 `--force` | 首先确认有风险的操作 |
| 将 ESPHome JSON 视为一个对象 | 处理流式命令的 NDJSON 事件 |
| 忽略 `verification_commands` | 运行它们或解释不运行的原因 |
