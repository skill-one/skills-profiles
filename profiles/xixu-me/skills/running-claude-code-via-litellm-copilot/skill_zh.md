## 概述

使用此技能针对特定的解决方案，其中 Claude Code 保留其 Anthropic 形式的客户端行为，但实际的后端流量被发送到本地 LiteLLM 代理，然后转发到 GitHub Copilot。

将其视为一个高级解决方案，而不是官方保证的 GitHub 工作流程。在技术上帮助用户成功，但不要承诺 GitHub 支持、政策批准或长期兼容性。

此技能以指导为先，但执行意识：

- 如果用户只需要解释，请提供最小的正确文件集、命令和检查。
- 如果用户需要在当前机器上进行实际设置工作，请先检查并调整命令以适应活动的 shell 和操作系统。
- 在进行持久性编辑（如 `~/.claude/settings.json` 或 shell 配置文件）之前暂停。

在需要证明哪些部分来自文章，哪些部分是根据当前的 LiteLLM 文档收紧的之前，请阅读 [`references/doc-verified-notes.md`](./references/doc-verified-notes.md)。

## 何时使用

当用户需要以下任何一项时，使用此技能：

- 通过 LiteLLM 在 GitHub Copilot 上运行 Claude Code
- 在保留 Claude Code 工作流程的同时降低直接的 Anthropic API 花费
- LiteLLM 的 GitHub Copilot 提供者的本地 `config.yaml`
- `ANTHROPIC_BASE_URL`、`ANTHROPIC_MODEL` 或 `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` 设置
- 帮助理解 LiteLLM 启动期间的 GitHub 设备授权
- 帮助解决模型不匹配、404 类似错误、没有请求到达 LiteLLM 或 GitHub 401/403 失败

不要使用此技能用于：

- 判断解决方案是否被 GitHub 条款允许
- 与 Claude Code 加 Copilot 无关的通用 LiteLLM 架构
- 没有 Copilot 或 LiteLLM 组件的直接 Anthropic API 设置

## 核心规则

1. 先简短说明合规性。
   解释这是一个基于本地代理路径的解决方案，不是 GitHub 推广的工作流程，用户必须自行评估最新的 Copilot 条款和限制。
2. 优先选择最小可行路径。
   除非用户明确要求持久性设置，否则从临时环境变量和本地 `config.yaml` 开始。
3. 保持 `ANTHROPIC_MODEL` 和 LiteLLM `model_name` 相同。
   精确的字符串匹配比巧妙的解释更重要。
4. 将 `ANTHROPIC_AUTH_TOKEN` 视为本地占位符。
   Claude Code 在本地期望非空值，但它不是 GitHub Copilot 凭证，也不应被视为可重用的密钥。
5. 不要整体覆盖 `~/.claude/settings.json`。
   仅合并需要的 `env` 键并保留无关设置。

## 工作流程

### 1. 预检查

当用户需要实际设置工作时要首先检查这些：

- `claude --help` 成功
- `uv --version` 或 `pip --version` 成功
- 用户有 GitHub Copilot 访问权限
- 预期的 LiteLLM 端口可用，通常是 `4000`

如果用户只需要说明，请说明先决条件而不是运行它们。

### 2. 选择临时与持久设置

使用此规则：

- 临时设置：首次设置、调试和低风险试验的首选默认设置
- 持久设置：只有当用户明确希望代理路径每次 Claude Code 启动时都生效

对于持久设置，确认目标文件，然后将键合并到 `~/.claude/settings.json`。不要替换文件内容。

### 3. 创建 LiteLLM `config.yaml`

从文章的流程开始，但保持提供者命名与 LiteLLM 文档一致：

```yaml
model_list:
  - model_name: claude-opus-4.5
    litellm_params:
      model: github_copilot/claude-opus-4.5
      drop_params: true
```

解释字段：

- `model_name`：Claude Code 将请求的逻辑名称
- `model`：LiteLLM 提供者路径，使用 `github_copilot/<model>`
- `drop_params: true`：在转发到 Copilot 之前删除不支持的 Anthropic 特定字段

如果用户想要其他 Copilot 支持的模型，保持相同的模式：

```yaml
model_list:
  - model_name: <logical-name>
    litellm_params:
      model: github_copilot/<copilot-model>
      drop_params: true
```

除非用户已经遇到拒绝，表明需要标头覆盖，否则不要在默认路径中硬编码额外的标头。

### 4. 安装和启动 LiteLLM

首选安装：

```bash
uv tool install "litellm[proxy]"
```

备用：

```bash
pip install "litellm[proxy]"
```

从包含 `config.yaml` 的目录启动代理：

```bash
litellm --config config.yaml --port 4000
```

告诉用户保持该终端打开，因为日志是在验证期间最快的真相来源。

### 5. 解释 GitHub 设备授权

在首次成功请求 GitHub Copilot 提供者时，LiteLLM 可能会打开设备授权流程：

1. LiteLLM 打印验证 URL 和设备代码
2. 用户打开 URL 并批准请求
3. LiteLLM 将生成的凭证本地存储以供将来使用

存在可选的令牌位置覆盖：

- `GITHUB_COPILOT_TOKEN_DIR`
- `GITHUB_COPILOT_ACCESS_TOKEN_FILE`

仅在用户需要自定义令牌存储、共享环境或围绕过期或丢失凭证的故障排除时提及这些。

### 6. 配置 Claude Code

对于临时的 PowerShell 会话：

```powershell
$env:ANTHROPIC_AUTH_TOKEN = "sk-any-string"
$env:ANTHROPIC_BASE_URL = "http://localhost:4000"
$env:ANTHROPIC_MODEL = "claude-opus-4.5"
$env:CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC = "1"
claude
```

对于临时的 Bash 或 Zsh 会话：

```bash
export ANTHROPIC_AUTH_TOKEN="sk-any-string"
export ANTHROPIC_BASE_URL="http://localhost:4000"
export ANTHROPIC_MODEL="claude-opus-4.5"
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
claude
```

对于持久配置，将这些键合并到 `~/.claude/settings.json`：

```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "sk-any-string",
    "ANTHROPIC_BASE_URL": "http://localhost:4000",
    "ANTHROPIC_MODEL": "claude-opus-4.5",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
  }
}
```

合并安全行为：

- 如果文件不存在，则创建它
- 如果存在，则保留所有无关的顶级键
- 保留与此工作流程无关的现有 `env` 条目
- 仅更新上述四个键
- 如果 JSON 格式错误，则停止并报告解析问题，而不是覆盖文件

### 7. 验证请求链

尽可能使用两个终端：

- 终端 A 运行 LiteLLM
- 终端 B 运行 `claude`

请求一个小的提示，例如一个简短的脚本或代码审查请求，然后验证：

- Claude Code 正常启动
- LiteLLM 日志显示传入请求
- LiteLLM 日志指示 GitHub Copilot 模型路径，通常是 `github_copilot/<model>`

健康路径是：

```text
Claude Code -> LiteLLM -> GitHub Copilot -> LiteLLM -> Claude Code
```

### 8. 故障排除

如果 Claude Code 报告模型未找到、404 类似失败或 LiteLLM 说模型不存在：

- 精确比较 `ANTHROPIC_MODEL` 和 `model_name`
- 检查大小写、标点符号和连字符

如果 LiteLLM 从未收到请求：

- 确认 `ANTHROPIC_BASE_URL` 指向 <http://localhost:4000>
- 确认 LiteLLM 仍在该端口上运行
- 确认环境变量是在启动 `claude` 的同一 shell 会话中设置的
- 如果 URL 正确但仍然沉默，请检查本地防火墙或端口冲突

如果 LiteLLM 到达 GitHub Copilot 但收到 401 或 403 响应：

- 通过重新启动 LiteLLM 并重试重复设备授权流程
- 确认 GitHub 账户仍然有 Copilot 访问权限
- 如果设置了自定义令牌目录变量，请验证它们指向预期的文件

## 高级回退：标头覆盖

文章使用显式的 Copilot 风格标头。当前的 LiteLLM 文档将 GitHub Copilot 作为提供者公开，并记录了标头覆盖支持。

仅在以下情况下才考虑显式的 `extra_headers`：

- 基本提供者流程到达 Copilot 但仍然需要客户端形状覆盖
- 用户已经有一些证据表明特定的环境在使用编辑器风格标头时表现更好

示例回退：

```yaml
model_list:
  - model_name: claude-opus-4.5
    litellm_params:
      model: github_copilot/claude-opus-4.5
      drop_params: true
      extra_headers:
        editor-version: "vscode/1.85.1"
        editor-plugin-version: "copilot/1.155.0"
        Copilot-Integration-Id: "vscode-chat"
        user-agent: "GithubCopilot/1.155.0"
```

将其作为高级回退呈现，而不是通用默认值。

## 输出检查清单

使用此技能回答真实用户请求时，包括：

- 简短的合规性说明
- 精确的 `config.yaml` 或要应用的差异
- 适合 shell 的命令
- 设置是临时的还是持久的
- 验证路径
- 如果失败，最小的相关故障排除部分

## 安全提醒

- 不要声称 GitHub 官方支持此解决方案。
- 不要暗示虚拟的 `ANTHROPIC_AUTH_TOKEN` 是一个真实的 Copilot 凭证。
- 不要建议整体覆盖 `~/.claude/settings.json`。
- 不要将过时的模型名称作为保证当前可用性呈现；如果用户要求特定模型，请保持 `github_copilot/<model>` 模式，并注意 Copilot 暴露的模型可用性可能会变化。
