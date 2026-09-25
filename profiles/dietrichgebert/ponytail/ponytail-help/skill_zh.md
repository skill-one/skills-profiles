# Ponytail 帮助

调用时显示此参考卡片。一次性使用，不要更改模式、写入标志文件或持久化任何内容。

## 级别

| 级别 | 触发方式 | 变化内容 |
|------|----------|----------|
| **Lite** | `/ponytail lite` | 按要求构建，用一行代码命名更懒的选择方案。 |
| **Full** | `/ponytail` | 默认级别：YAGNI → 标准库 → 本地 → 一行代码 → 最小化。默认。 |
| **Ultra** | `/ponytail ultra` | YAGNI 极端主义者。先删除后添加。在构建前挑战需求。 |

级别持续到更改或会话结束。

## 技能

| 技能 | 触发方式 | 功能 |
|------|----------|------|
| **ponytail** | `/ponytail` | 懒惰模式本身。最简单的可行方案。 |
| **ponytail-review** | `/ponytail-review` | 过度设计审查：`L42: yagni: 工厂，一个产品。内联。` |
| **ponytail-audit** | `/ponytail-audit` | 整个仓库的过度设计审查：待删除内容的排名列表。 |
| **ponytail-debt** | `/ponytail-debt` | 收集 `ponytail:` 快捷注释到一个跟踪账本。 |
| **ponytail-gain** | `/ponytail-gain` | 测量影响得分板：代码更少，成本更低，速度更快。 |
| **ponytail-help** | `/ponytail-help` | 此卡片。 |

Codex 使用 `@ponytail`、`@ponytail-review` 和 `@ponytail-help`；Claude Code 和 OpenCode 使用上述的斜杠命令形式（OpenCode 将全部六个作为斜杠命令打包）。

## 停用

说“停止 ponytail”或“正常模式”。随时用 `/ponytail` 恢复。
`/ponytail off` 也有效。

## 设置默认模式

默认模式 = `full`，会话自动激活。更改它：

**环境变量**（最高优先级）：
```bash
export PONYTAIL_DEFAULT_MODE=ultra
```

**配置文件** (`~/.config/ponytail/config.json`，Windows: `%APPDATA%\ponytail\config.json`)：
```json
{ "defaultMode": "lite" }
```

设置 `"off"` 以禁用会话启动时的自动激活，需要时用 `/ponytail` 手动激活。

解析顺序：环境变量 > 配置文件 > `full`。

## 更新

一次性启用自动更新：打开 `/plugin`，进入 Marketplaces，选择 ponytail，启用自动更新。Claude Code 启动时会拉取新版本（当提示时运行 `/reload-plugins`）。手动刷新：`/plugin marketplace update ponytail` 然后 `/reload-plugins`。

如果 `/plugin` 不可识别，你的 Claude Code 已过时。更新它 (`npm install -g @anthropic-ai/claude-code@latest`，或 `brew upgrade claude-code`) 并重启。其他主机使用自己的更新流程。

## 更多

完整文档 + 示例：https://github.com/DietrichGebert/ponytail
