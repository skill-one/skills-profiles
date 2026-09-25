# 验证：Salesforce 开发环境

验证所有必需的先决条件，并呈现清晰、可操作的 status 报告。这项技能是按需触发——它不会在会话启动时自动运行。显式运行它以检查或修复您的本地设置。

## 第一阶段：先决条件扫描

运行工具检查：

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/sf-context check-tools
```

输出是一个包含 `tools` 数组的 JSON 对象（在出现任何关键错误时，还会包含一个 `diagnostic` 块）。

**横幅由插件自动绘制——请勿自行重绘。** 当 `check-tools` 运行时，插件会在可见通道上确定性地绘制带边框的 **"Ready to build on Salesforce?"** 横幅——每个工具一行状态，页脚结论，以及导航页脚——与 SessionStart 横幅完全相同。这是一个 **Tier-1 表面**：您可以阅读 JSON 以便理解，但**绝对不要**重绘、重新渲染横幅。仅添加简短的说明，说明结果对用户意味着什么，然后进入**第二阶段**。

绘制的横幅如下所示（示意图——每行中的版本/消息文本直接来自 JSON：`version` 对应 🟢，`message` + 修复提示 对应 🟡/🔴，注释 对应 ℹ️；下方的值显示样式，而非固定字符串）：

```
──────────────────────────────────────────────────────────────
 Ready to build on Salesforce?   checking your toolchain…
──────────────────────────────────────────────────────────────
 🟢 Salesforce CLI             v2.144.6
 🟢 Code Analyzer              v5.14.0 · JIT, auto-installs on first use
 🟢 Node.js                    v22.11.0 LTS
 🟢 NPM                        v10.9.0
 🟢 Git                        v2.50.1
 🟢 Salesforce MCP (config)    .mcp.json + proxy present
 🟢 Salesforce MCP (endpoint)  org instance reachable
 ℹ️  Salesforce MCP (process)   confirm with /mcp or /doctor
 🟢 Source Tracking            enabled
──────────────────────────────────────────────────────────────
 ✓ toolchain ready                                (skill: platform-environment-validate)
```

每行的状态点表示状态——🔴 `critical`（缺失或低于最低版本——无法进行 Salesforce 开发），🟡 `warn`（已安装但已过时、非 LTS 或配置错误），🟢 `ok`，ℹ️ `info`（一个无法自动验证的上下文注释，例如 MCP 进程健康状况）——并且带边框的页脚给出结论以及最相关的 `Next:` 步骤。每个工具的 JSON `status` 字段是事实来源；在您编写简短说明时，请使用这些状态。

**如果横幅未绘制**（较旧的 Claude Code 构建，或绘制回退），请**不要**从 JSON 手动绘制它。使用确定性渲染器打印它：

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/sf-context readiness-banner
```

这读取 `check-tools` 刚记录的相同扫描结果，并打印相同的带边框横幅——行按固定顺序排列，页脚结论，以及导航页脚（带有其 `Next:` 步骤）——因此顺序、填充、计数和下一步选择在脚本中一次性确定，永远不会手动重新推导。`check-tools` JSON 是权威的、机器可读的结果。

**确定性结果——**绝对不要覆盖失败：JSON 报告是权威的、机器可读的结果。如果某个工具报告 🔴/🟡，请按原样报告。**不要**以不同的方式重新运行工具（PowerShell、原始 shell 探测、不同命令）然后报告 🟢——一个偶然发现工具的回退**不代表**确定性检查通过。一个失败的检查必须保持失败状态，直到**相同**的 `check-tools` 检查通过。当报告包含 `diagnostic` 块（在出现任何关键错误时附加）时，请显示它：它包含平台、活动 shell、工作目录、插件根目录，以及**解析的可执行路径**——这是查看工具未解析原因的最快方式（例如 Windows `sf.cmd` 未在 `PATH` 中）。诊断设计为无密钥；**切勿**向其中添加令牌或 org 身份验证。

**MCP 以三个不同的行报告——**切勿相互推断：`Salesforce MCP (config)`（`.mcp.json` + `sf-mcp-proxy.bundled.js` 是否存在？），`Salesforce MCP (endpoint)`（平台端点是否可达？），以及 `Salesforce MCP (process)`（MCP 进程是否实际健康？）。进程行报告为 ℹ️ **信息性**（不是警告）——此脚本无法看到 Claude Code 拥有的 MCP 子进程，因此绿色配置/端点**必须**不能显示为工作的 MCP。使用 `/mcp` 或 `/doctor` 确认进程健康状况。端点行作为连接代理探测 org **实例 URL**，而不是平台-MCP 端点本身。

## 检查的工具

| 工具 | 最低要求 | 验证 |
|---|---|---|
| Salesforce CLI | 存在，并且是最新版本 | `sf --version` (🟡 当有更新可用时) |
| Code Analyzer 插件 | 安装**或** JIT 注册 | `sf plugins inspect @salesforce/plugin-code-analyzer`，回退到 CLI 的 `oclif.jitPlugins` 注册表 |
| Node.js | >= 18 (even/LTS) | `node --version` |
| NPM | >= 3.10 | `npm --version` |
| Git | 必须存在 | `git --version` |
| Salesforce MCP (config) | `.mcp.json` 配置 + 代理包存在 | 插件根目录 `.mcp.json` 检查 + `sf-mcp-proxy.bundled.js` 存在 |
| Salesforce MCP (endpoint) | Org 实例 URL 可达（连接代理） | 对 org 实例 URL 进行 HTTP 探测 |
| Salesforce MCP (process) | ℹ️ 信息性——此处无法验证 | 使用 `/mcp` 或 `/doctor` 确认 |
| Source Tracking | 连接的 org 启用 | `sf project deploy preview` |

所有外部工具（`sf`、`npm`、`node`、`git`）都通过单个跨平台解析器启动：`shutil.which`（PATHEXT-aware）找到工具，并通过 COMSPEC 包装的 argv 数组调用 Windows 的 `.cmd`/`.bat` 衬垫（`sf.cmd`、`npm.cmd`）——永远不会是 shell 字符串——因此此扫描和 `/salesforce-development:org` 在 Windows、macOS 和 Linux 上正确检测 `sf`/`npm`/默认 org。

**Code Analyzer 是 JIT 插件——注册 ≠ 安装。** Salesforce CLI 声明 `@salesforce/plugin-code-analyzer` 为“即时”（JIT）插件：它仅在第一次运行 `sf code-analyzer` 命令时物理安装。在此之前，即使它对用户完全可用，`sf plugins inspect` 对它**也会失败**。因此，检查将 JIT 注册视为成功——如果 `inspect` 返回没有版本，它会回退到 CLI 自己的 `oclif.jitPlugins` 注册表（从 `sf plugins --json` 的根条目读取），并报告 🟢，附带固定版本和注释，说明它在首次使用时自动安装。只有既未安装也未 JIT 注册的插件才是 🔴 严重。

## 第二阶段：安装 / 更新

**如果所有状态为绿色：** 确认设置完成。用户可以开始开发。

**如果存在警告或严重项：** 向用户显示选项：

```
Some tools need attention. What would you like to do?

  [1] Fix all items
  [2] Choose which items to fix
  [3] Skip for now
```

对于用户想要修复的每个工具，提供适用于其操作系统的正确安装/更新命令。**不要**自动运行安装命令——显示命令并要求用户确认后再运行它。

### 按 工具 分类的安装 / 更新命令

**Salesforce CLI —— 未安装：**
```bash
# macOS/Linux (npm)
npm install --global @salesforce/cli

# macOS (Homebrew)
brew install sf
```

**Salesforce CLI —— 更新：**
```bash
sf update
```

**Code Analyzer 插件 —— 未安装：**
```bash
sf plugins install @salesforce/plugin-code-analyzer
```

**Code Analyzer 插件 —— 更新：**
```bash
sf plugins update @salesforce/plugin-code-analyzer
```

**Node.js —— 未安装或低于最低版本：**
```bash
# macOS (nvm — 推荐，安装 LTS)
nvm install --lts && nvm use --lts

# macOS (Homebrew)
brew install node

# Windows — 从 https://nodejs.org 下载（LTS 版本）
```

**NPM —— 更新：**
```bash
npm install --global npm@latest
```

**Git —— 未安装：**
```bash
# macOS (Xcode CLT)
xcode-select --install

# macOS (Homebrew)
brew install git

# Windows — 从 https://git-scm.com 下载
```

**Source Tracking —— 未启用：**
```bash
sf org enable tracking --target-org <alias>
```

**Salesforce MCP —— 配置错误：** 如果 `.mcp.json` 缺失或为空，重新加载插件：
```
/reload-plugins
```

## 重要说明

- 安装修改 PATH 的工具（Node.js、SF CLI）后，用户可能需要退出并重新启动 Claude Code 才能使更改生效。
- Source Tracking 需要一个连接的 org——如果没有配置 org，请先运行 `/salesforce-development:login`。
- 对于 org 身份验证问题（过期会话、错误的 org、INVALID_SESSION_ID），请运行 `/salesforce-development:login` 而不是此技能。
- **SF CLI 过时 → 🟡 在就绪扫描中：** 就绪意味着 *最新*。当 CLI 的缓存更新检查报告有更新的版本时，`check-tools` 将 Salesforce CLI 报告为 🟡（已安装但已过时）并附带正确的更新命令，而不是 🟢。与会话启动通知不同，此警告忽略了每个版本的无需提示门——显式就绪扫描始终报告事实状态——但它仍然尊重硬性禁用的 `SFDX_SKIP_CLI_UPDATE_CHECK=1`。
- **会话启动时 SF CLI 更新通知：** 当 CLI 报告有可用更新时，`sf-context detect` SessionStart 钩子会显示一次并要求代理提供更新（`sf update`，或 `npm install --global @salesforce/cli@latest` 用于 npm-global 安装）。拒绝或失败的更新会记录一个**每个版本**的无需提示门（`.sf/sf-cli-update-state.json`），因此相同版本不会再提示，但新版本会重新提示。设置 `SFDX_SKIP_CLI_UPDATE_CHECK=1` 以禁用检查。
