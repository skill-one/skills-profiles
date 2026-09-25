# 华为云代理集成（OpenViking 长期记忆）

## 概述

将 OpenViking 长期记忆与编码代理集成和解绑。代理在 `/root/job-envs/sandboxes/` 下的 bwrap 沙箱中运行，并使用其**原生机制**——MCP（`mcp__openviking__*` 工具）或 HTTP 内存提供者——因此集成在代理升级后仍然有效。

集成写入是**模板级别的持久化**：配置被注入到代理的 `start.sh` / 配置模板下 `/root/template/<agent>/`，因此沙箱 `stop + start` 保留集成。

## 支持的代理

| 代理 | 机制 | 持久化 |
|------|------|--------|
| CodeArts CLI | `@openviking/opencode-plugin` → `.codeartsdoer/node_modules/` | 模板 + 实时 |
| OpenCode | `@openviking/opencode-plugin` (npm 镜像 → GitHub 备用) | 模板 start.sh |
| OpenClaw | `clawhub:@openviking/openclaw-plugin` + `contextEngine` 插槽 | 模板 start.sh |
| | ↳ **优化**：禁用 `session-memory` 钩子 + 拒绝 `memory_search` 工具（OpenViking 处理召回；本地内存降低质量） |
| Hermes | 内置 `memory.provider: openviking`（HTTP REST，无 MCP） | 模板 + 实时 |
| WorkSwarm | 双通道：原生提供者 + MCP（13 个工具）+ 代码模式补丁 | 模板 + 实时 + 运行时补丁 |
| KimiCode | 通过 `mcp.json` 的 MCP | 模板 + 实时 |
| DeepSeek Harness | `@openviking/dsh-memory-plugin` 包（从 GitHub 按需获取） | 模板 start.sh |
| Prime Agent | `@openviking/pi-coding-agent-extension`（从 GitHub 按需获取） | 模板 start.sh |

每个代理的配置详情：[参考资料/agent-configs.md](references/agent-configs.md)。

## 前置条件

- OpenViking 服务器运行在 `http://127.0.0.1:1933` (`curl -s http://127.0.0.1:1933/health`)。
- 代理沙箱存在于 `/root/job-envs/sandboxes/`（由 job-env-manager 管理）。
- 主机工具：`curl`、`python3`、`bash`。OpenCode/OpenClaw 需要额外的 `npm`。
- 无需华为云 IAM 策略——此技能仅对本地 bwrap 沙箱操作。

## 参数确认（必需输入）

| 参数 | 必需 | 描述 | 示例 |
|------|------|------|------|
| `--agent <name>` | 是（除非 `--all`） | 目标代理（见上表） | `--agent opencode` |
| `--all` | 是（除非 `--agent`） | 对所有 8 个代理操作 | `--all` |
| `--endpoint <url>` | 否 | OpenViking 服务器 URL（默认 `http://127.0.0.1:1933`） | `--endpoint http://192.168.1.100:1933` |
| `--api-key <key>` | 否 | OpenViking API 密钥（开发模式无需）。聊天中永不回显 | `--api-key sk-xxx` |
| `--dry-run` | 否 | 显示更改但不应用 | `--dry-run` |
| `--yes` / `-y` | 否 | 跳过授权提示（仅自动化） | `--yes` |
| `--json` | 否 | `status.sh`：机器可读输出 | `--json` |

## 核心命令

| 功能 | 命令 |
|------|------|
| 查看集成状态 | `scripts/status.sh`（`--json` 机器可读，`--agent <name>` 指定） |
| 验证 MCP 端点 | `scripts/verify_mcp.sh` |
| 集成单个代理 | `scripts/integrate.sh --agent <name> [--endpoint URL] [--api-key KEY] [--dry-run] [--yes]` |
| 集成全部代理 | `scripts/integrate.sh --all` |
| 解绑单个代理 | `scripts/unbind.sh --agent <name> [--dry-run] [--yes]` |
| 解绑全部代理 | `scripts/unbind.sh --all` |

## 工作流程

```bash
SKILL_DIR=/root/.agents/skills/huawei-cloud-openviking-agent-integration
```

1. **检查状态**：`$SKILL_DIR/scripts/status.sh` — 每个代理状态：`template + live`（激活）、`template only`（重启时激活）、`live only`（重启时丢失）。
2. **验证 MCP**：`$SKILL_DIR/scripts/verify_mcp.sh` — 完整 MCP 握手（初始化 → 工具列表 → 健康）。
3. **集成**：`$SKILL_DIR/scripts/integrate.sh --agent <name>`（或 `--all`）。
4. **解绑**：`$SKILL_DIR/scripts/unbind.sh --agent <name>`（或 `--all`）。
5. **重建 OpenClaw**：通过 job-env-manager API 的 `stop + start` 重新运行 `start.sh`。脚本：[参考资料/related-commands.md](references/related-commands.md)。

## 授权与安全

- **授权是必需的**——`integrate.sh` 和 `unbind.sh` 需要明确的 `confirm`（或 `--yes` 用于自动化）。`--dry-run` 预览而不授权。
- **不要伪造集成状态**——始终运行 `status.sh` 以验证后再报告。
- **直接编辑代理配置**——所有更改都通过技能脚本进行。
- **日志中无 API 密钥**——`--api-key` 值绝不能出现在输出中。
- 每次配置修改都会创建 `.bak.<timestamp>` 备份以回滚。

完整规则：[参考资料/guardrails.md](references/guardrails.md)。故障排除：[参考资料/troubleshooting.md](references/troubleshooting.md)。

## 插件来源

技能**不自带插件代码**——插件在集成时按需安装，通过国内优先镜像（华为云 npm → npmmirror → npmjs；GitHub 原始镜像用于非 npm 插件）。所有下载都通过 GitHub blob SHA 进行字节验证。如果上游不可达，`/root/runtime/` 下的已安装副本会被复用（三层缓存：沙箱 `node_modules` → 运行时缓存 → 在线）。

## 参考资料

| 文档 | 描述 |
|------|------|
| [agent-configs.md](references/agent-configs.md) | 每个代理配置详情、MCP 工具、服务器信息 |
| [guardrails.md](references/guardrails.md) | 安全性、授权、访问权限 |
| [troubleshooting.md](references/troubleshooting.md) | 失败场景和修复 |
| [verification.md](references/verification.md) | 验证方法和验收标准 |
| [related-commands.md](references/related-commands.md) | 重启/重建脚本、环境变量 |

## 脚本（OO 架构）

基础类（`lib/base.sh`）+ 注册器（`lib/registry.sh`）+ 每个代理的子类（`agents/*.sh`）。入口点（`integrate/unbind/status.sh`）是薄的 CLI 解析器。所有脚本都是幂等的，带 `.bak.<timestamp>` 备份。添加新代理 = `agents/` 中的一个文件。
