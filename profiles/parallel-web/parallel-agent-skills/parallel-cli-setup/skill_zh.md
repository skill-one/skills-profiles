# 并行CLI设置

以最小的摩擦设置或维护 `parallel-cli`。如果你正在运行这个提示，你的目标是按照以下说明设置 `parallel-cli`，以便用户可以执行搜索、运行提取、深度研究等。

## 第1步：安装或升级CLI

检查CLI是否存在：

```bash
command -v parallel-cli
```

如果缺失，可以使用以下任一方法安装：

1. 仅限macOS：`brew install parallel-web/tap/parallel-cli`
2. Linux/macOS/Windows (uv)：`uv tool install "parallel-web-tools[cli]"`
3. Linux/macOS/Windows (npm)：`npm install -g parallel-web-cli`
4. Linux/macOS/Windows (pipx)：`pipx install "parallel-web-tools[cli]" && pipx ensurepath`

当 `parallel-cli` 存在时，需要版本 `>=0.9.2`。如果较旧，请先确定安装方法，然后再建议更新。使用 `command -v parallel-cli`，如果它是符号链接，则检查 `readlink "$(command -v parallel-cli)"`。`~/.local/share/uv/tools/` 下的路径表示 `uv tool install`；`~/.local/share/parallel-cli/` 下的路径表示独立安装程序。

升级命令（根据安装方式选择）：

- 独立安装：`parallel-cli update`
- uv：`uv tool upgrade parallel-web-tools[cli]`
- pipx：`pipx upgrade parallel-web-tools[cli]`
- npm：`npm update -g parallel-web-cli`
- homebrew：`brew update && brew upgrade parallel-web/tap/parallel-cli`

## 第2步：认证

检查认证状态：

```bash
parallel-cli auth --json
```

你会得到类似以下的响应：

```json
{
  "authenticated": true,
  "method": "oauth",
  "env_var_set": false,
  "has_stored_credentials": true,
  "stored_overridden_by_env": false,
  "token_file": "xxx",
  "version": 1,
  "selected_org_id": "legacy",
  "selected_org_name": null,
  "has_control_api_tokens": false
}
```

如果 `authenticated` 为 `false` 或 `selected_org_id` 为 `legacy`，提示用户登录：

```bash
parallel-cli login --json
```

如果是无头会话，请追加 `--no-browser`。

这会触发设备OAuth。用户将被提示打开网页浏览器并输入CLI输出的代码。

从代理封装中调用时，优先通过Monitor风格的工具流式传输stdout，而不是在完成时阻塞。

输出将如下所示：

```json
{"event": "auth_start"}
{"event": "device_code", "verification_uri": "http://localhost:3000/getServiceKeys/device", "verification_uri_complete": "http://localhost:3000/getServiceKeys/device?user_code=CHQX-NQKP&onboard_variant=agent", "user_code": "CHQX-NQKP", "expires_in": 600, "browser_open_attempted": true, "browser_opened": true}
{"event": "auth_waiting"}
{"event": "auth_success"}
```

`{"event": "auth_success"}` 仅在用户成功授权CLI后才会发出。否则，它会在 `{"event": "auth_waiting"}` 处阻塞。

## 第3步：检查余额

认证后，检查当前余额：

```bash
parallel-cli balance get
```

如果为零，提示用户添加余额：

```bash
parallel-cli balance add <AMOUNT_IN_CENTS>
```

明确说明组织应该已经添加了支付方式。如果没有，用户可以前往 <https://platform.parallel.ai/settings> 添加一个。

## 第4步：安装Parallel技能

为用户安装技能：

```bash
parallel-cli skills install
```

如果代理不支持热重载，用户可能需要重启代理。

## 第5步：建议首次运行

提示用户使用新安装的技能立即运行搜索或提取。建议以下之一（对于Codex，使用 `$` 而不是 `/”）：

- `/parallel-web-search <query>` — 快速网页搜索
- `/parallel-web-extract <url>` — 从URL提取内容
- `/parallel-deep-research <topic>` — 全面研究
- `/parallel-data-enrichment <list>` — 丰富实体列表
