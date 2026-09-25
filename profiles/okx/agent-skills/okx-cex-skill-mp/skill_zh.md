# OKX 技能市场

在 OKX 技能市场中浏览、搜索、安装和管理 AI 交易技能。技能是模块化的 AI 提示包，可扩展您的交易助手的功能——涵盖市场分析、交易执行、风险管理和投资组合优化。

> **⚠️ 第三方内容声明**
> OKX 技能市场中的技能由 **独立第三方开发者** 创建和发布，而非 OKX。OKX 不负责审核、认可或对任何第三方技能的内容、准确性或行为负责。使用技能前，请务必查看其 SKILL.md 文件，并仅从您信任的开发者处安装技能。
> 通过 `okx skill add` 安装技能时，它会从市场下载并保存到您代理的技能目录（例如 `~/.agents/skills/<skill-name>/`）中。技能完全在您的本地计算机上运行，并使用代理的全部权限——请像安装任何第三方软件一样谨慎对待。

**技能路由**
- 技能市场 → `okx-cex-skill-mp`（此技能）
- 市场数据 / 指标 → `okx-cex-market`
- 账户余额 / 持仓 → `okx-cex-portfolio`
- 下单 / 取消订单 → `okx-cex-trade`
- 网格 / DCA 机器人 → `okx-cex-bot`

## 前置条件

1. 安装 `okx` CLI：
   ```bash
   npm install -g @okx_ai/okx-trade-cli
   ```
2. 配置 API 凭证（访问市场所需）：
   ```bash
   okx config init
   ```

---

## 安装策略

当用户想要安装技能时，请严格按以下顺序操作：

1. **始终首先尝试 `okx skill add <name>`** — 这一步会一次性下载并安装技能到所有检测到的代理（Claude Code、OpenClaw、Cursor、Windsurf 等）。
2. **只有当 `add` 失败时**，才回退到手动下载：
   - 告知用户 `add` 失败的原因（网络错误、npx 不可用、权限问题等）
   - 提供 `okx skill download <name> --dir <path>` 作为替代方案
   - 指导用户手动解压并将文件放置到其代理的技能目录中

除非 `add` 已经失败，否则不要跳过 `add` 直接使用 `download`。

---

## 命令参考

| # | 命令 | 描述 |
|---|---------|-------|
| 1 | `okx skill search <keyword>` | 通过关键词搜索市场 |
| 2 | `okx skill search --categories <id>` | 按类别筛选技能 |
| 3 | `okx skill categories` | 列出所有可用类别 |
| 4 | `okx skill add <name>` | 下载并安装到所有检测到的代理 |
| 5 | `okx skill download <name> [--dir <path>] [--format zip\|skill]` | 下载包（默认格式：zip） |
| 6 | `okx skill list` | 列出本地已安装的技能 |
| 7 | `okx skill check <name>` | 检查是否有新版本可用 |
| 8 | `okx skill remove <name>` | 卸载技能 |
| 9 | `okx skill verify <name>` | 按需重新验证已安装技能的签名 |

为任何命令添加 `--json` 以获取原始 JSON 输出。添加 `--env` 将输出包装为 `{"env", "profile", "data"}` 格式。

---

## 命令详解

### 1. 搜索技能

```bash
okx skill search grid
```

输出：
```
  NAME              VERSION   DESCRIPTION
  grid-premium      1.2.0     带技术分析的增强型网格交易
  grid-dca          1.0.0     网格策略与 DCA 结合

2 技能找到（第 1/1 页）。使用 `okx skill add <name>` 安装。
```

带类别筛选的搜索：
```bash
okx skill search --categories trading-strategy
```

分页（响应包含 `totalPage` 表示总页数）：
```bash
okx skill search grid --page 2 --limit 5
# 输出："3 技能找到（第 2/4 页）。使用 `okx skill add <name>` 安装。"
```

### 2. 浏览类别

```bash
okx skill categories
```

输出：
```
  ID                  NAME
  trading-strategy    交易策略
  risk-management     风险管理
  analysis            市场分析
```

### 3. 安装技能

```bash
okx skill add grid-premium
```

输出：
```
正在下载 grid-premium...
正在验证签名...
  签名验证通过（密钥：okx-skill-signing-key-2026，文件：3）
正在安装到检测到的代理...
✓ 技能 "grid-premium" v1.2.0 已安装
  注意：此技能由第三方开发者创建，非 OKX。使用前请查看 SKILL.md。
```

底层操作：
1. 从 OKX 市场API下载技能 zip 文件
2. 解压并验证包（检查是否存在 SKILL.md，读取元数据）
3. **验证 Ed25519 签名和 SHA-256 文件完整性**——验证失败时阻止安装
4. 运行 `npx skills add` 以安装到所有本地检测到的代理
5. 在 `~/.okx/skills/registry.json` 中记录安装信息（包括验证状态）

**强制安装（绕过验证）**：
```bash
okx skill add grid-premium --force
```
> ⚠️ **安全警告**：`--force` 绕过签名验证，即使验证失败也会安装技能。仅当您信任源并了解风险时使用此选项。绕过验证会记录在注册表中，状态为 `bypassed`。

### 4. 仅下载（不安装）

当 `add` 失败或用户希望获取原始包时：

```bash
okx skill download grid-premium --dir ~/Downloads/
```

输出：
```
✓ 已下载 grid-premium.zip
  路径：/Users/me/Downloads/grid-premium.zip
```

下载为 `.skill` 格式（代理支持该扩展名）：
```bash
okx skill download grid-premium --dir ~/Downloads/ --format skill
```

zip 文件包含：
- `SKILL.md` — 技能的主要指令文件
- `_meta.json` — 元数据（名称、版本、标题、描述）
- `reference/` — 可选的辅助文档

### 5. 列出已安装技能

```bash
okx skill list
```

输出：
```
  NAME              VERSION   安装时间
  grid-premium      1.2.0     2026-03-25 10:30:00
  dca-smart         2.1.0     2026-03-20 14:00:00

已安装 2 个技能。
```

### 6. 检查更新

```bash
okx skill check grid-premium
```

输出：
```
grid-premium: 已安装 v1.0.0 → 最新 v1.2.0（有更新）
  使用 `okx skill add grid-premium` 更新。
```

要更新，只需再次运行 `okx skill add <name>`——它会覆盖旧版本。

### 7. 卸载技能

```bash
okx skill remove grid-premium
```

输出：
```
✓ 已卸载技能 "grid-premium"
```

### 8. 验证技能的签名

对已安装的技能重新运行签名验证，而无需重新安装：

```bash
okx skill verify grid-premium
```

输出（成功）：
```
✓ grid-premium: 签名验证通过（密钥：okx-skill-signing-key-2026，文件：3）
```

输出（失败）：
```
✗ grid-premium: 验证失败 — 无效签名
```

- 失败时退出码为 `1`。
- 结果会持久化回 `~/.okx/skills/registry.json`。
- 使用 `--json` 获取机器可读输出。

---

## MCP 工具（替代方案）

当 CLI 不可用时（例如没有终端访问权限的 Claude Desktop），相同的技能市场功能可通过 MCP 工具实现：

| MCP 工具 | 对应 CLI | 描述 |
|----------|---------|-------|
| `skills_search` | `okx skill search` | 通过关键词/类别搜索。响应包含 `totalPage` 用于分页。 |
| `skills_get_categories` | `okx skill categories` | 列出类别 |
| `skills_download` | `okx skill download` | 下载包到目录（默认格式：`.skill`；传递 `format: "zip"` 获取 zip） |

注意：MCP 工具仅支持搜索和下载。完整的安装流程（`add`）需要 CLI 访问权限。

---

## 错误处理

| 错误 | 含义 | 操作 |
|------|-------|-------|
| `70002 SKILL_DELETED` | 技能已从市场删除 | 选择其他技能 |
| `70003 NO_APPROVED_VERSION` | 没有可用的已批准版本 | 技能正在审核中，稍后再试 |
| `70030 VERSION_NOT_APPROVED` | 版本尚未批准下载 | 等待审核或使用旧版本 |
| `50111/50112/50113` | 身份验证错误 | 运行 `okx config init` 设置凭证 |
| `npx skills add` 失败 | npx 不可用或网络问题 | 使用 `okx skill download` 代替，然后手动安装 |
