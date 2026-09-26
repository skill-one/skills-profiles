# 状态行生成器

生成自定义的 Claude Code 状态行脚本，可选择列和配色主题。直接安装到 `~/.claude/settings.json`。

## 工作原理

Claude Code 支持通过配置在 `~/.claude/settings.json` 中的 shell 脚本来自定义状态行。该脚本接收会话 JSON 数据（模型、上下文窗口、工作区、Vim、工作树等）作为标准输入，并将格式化文本输出到标准输出。

此技能会根据您的偏好生成定制的 bash 脚本并自动安装。

## 脚本目录

**重要提示**：所有脚本都位于此技能的 `scripts/` 子目录中。

**代理执行说明**：
1. 确定此 SKILL.md 文件的目录路径为 `SKILL_DIR`
2. 脚本路径 = `${SKILL_DIR}/scripts/<脚本名>.mjs`
3. 将此文档中的所有 `${SKILL_DIR}` 替换为实际路径

**脚本参考**：
| 脚本 | 目的 |
|------|---------|
| `scripts/generate.mjs` | 根据选择选项生成并安装状态行脚本 |

## 前置条件

- **jq** — 生成的状态行脚本需要使用 jq 解析来自 Claude Code 的 JSON 输入。在 Windows 上，脚本会自动检测通过 WinGet 或 scoop 安装的 jq；如果仍然找不到 jq，请手动将其目录添加到 PATH 中。
- **Bun** — 需要运行生成器。如果未全局安装，请使用 `npx -y bun`。

## 使用方法

```bash
# 预览生成的脚本
npx -y bun ${SKILL_DIR}/scripts/generate.mjs --elements model,context,effort,git,dir --theme gruvbox

# 生成并安装
npx -y bun ${SKILL_DIR}/scripts/generate.mjs --elements model,context,effort,git,dir --theme dracula --install
```

### 选项

| 标志 | 默认值 | 描述 |
|------|---------|-------------|
| `--elements <列表>` | `model,context,cost,effort,style,git,dir` | 要显示的逗号分隔列 |
| `--theme <名称>` | `gruvbox` | 配色主题 — 下方表格中有说明 |
| `--effort-icon <预设>` | `arrow` (`↯`) 用于图标主题，其他情况无 | 覆盖努力前缀图标。预设：`arrow`, `bolt`, `flash`, `reason`, `dot`, `none`。也可以接受原始字符。 |
| `--install` | off | 将脚本写入 `~/.claude/scripts/statusline.sh` 并更新 `settings.json` |

### 列

| 列 | 描述 | 数据源 |
|------|-------------|-------------|
| `model` | 活动模型名称（例如 "Opus 4.7"） | `model.display_name` |
| `context` | 进度条 + 百分比 — **颜色随剩余容量变化** | `context_window.remaining_percentage` |
| `cost` | 会话 API 花费格式化为 `$X.XX`（以金为单位） — 当四舍五入到 `$0.00` 时隐藏 | `cost.total_cost_usd` 来自输入 JSON |
| `effort` | 推理努力级别 — **颜色随级别变化** | `effortLevel` 在 `~/.claude/settings.local.json` → `~/.claude/settings.json` |
| `style` | 输出样式名称（例如 Explanatory, Learning） — 当为 "default" 时隐藏 | `output_style.name` 来自输入 JSON |
| `git` | Git 分支名称（脏时为黄色） | `worktree.branch` → git CLI |
| `dir` | 仓库基本名称（在 worktree 中为原始仓库） | `worktree.original_repo_dir` → `workspace.current_dir` |
| `worktree` | 粗体 `worktree:<id>` 标签（在工作树外隐藏） | `worktree.name` → 通过 git CLI 获取父目录基本名称 |
| `vim` | Vim 模式指示器（不活动时隐藏） | `vim.mode` |

### 颜色变化元素

**`context`** — 条形填充 + 百分比颜色随剩余容量变化：

| 剩余 | 颜色 | 含义 |
|------|-------|---------|
| > 50% | 绿色 | 上下文充足 |
| 20–50% | 黄色 | 注意 |
| < 20% | 红色 | 接近满 — 即将紧凑 |

**`effort`** — 值 + 可选前缀图标随级别变化颜色：

| 级别 | 颜色 |
|------|-------|
| `max`, `xhigh`, `high` | **粗体红色** |
| `medium` | 黄色 |
| `low`, `xlow`, `minimal` | 绿色 |
| 其他 / 未设置 | 暗淡（或完全未设置时隐藏） |

### 主题

| 主题 | 氛围 | 条形图中的图标 |
|------|------|------------------------|
| `gruvbox` | 温暖复古、柔和 | `✦` 模型 · `↯` 努力 · `❋` 样式 · `⌂` 目录 · `⊕` 工作树 · `⎇` git · `⌨` vim |
| `dracula` | 现代暗黑、高饱和度 | `◈` 模型 · `↯` 努力 · `❋` 样式 · `⌂` 目录 · `⊕` 工作树 · `⎇` git · `⌨` vim |
| `robbyrussell` | 经典 oh-my-zsh | 无前缀图标 — 仅显示颜色和标签 |
| `minimal` | 默认终端颜色 | 无前缀图标 — 纯文本 |

`context` 列特意跳过了前缀图标 — 颜色变化的进度条已经足够直观。`effort` 前缀 (`↯`) 已包含在图标主题中，可以通过 `--effort-icon` 覆盖。

### 努力图标

通过 `--effort-icon <预设>` 交换努力值前面的符号。预设：

| 预设 | 符号 | 备注 |
|------|-------|-------|
| `arrow` | `↯` | 闪电箭头 — **默认**，细 |
| `bolt`  | `ϟ` | 希腊 koppa — 细闪电 |
| `flash` | `⚡` | 经典闪电 — 在 emoji-presentation 字体中为宽 |
| `reason`| `∴` | 因此 |
| `dot`   | `◉` | 填充圆圈 |
| `none`  | (隐藏) | 完全移除图标 |

也可以通过 `--effort-icon <char>` 传递任何原始字符。

**工作树行为**：当位于 git 工作树中（通过输入 JSON 的 `worktree.*` 字段或通过 `git rev-parse --git-common-dir` 回退检测）时，`worktree` 列显示粗体 `worktree:<id>` 标签，使用父目录名称（例如 `~/.codex/worktrees/46a6/clawmaster` → `worktree:46a6`）。`git` 列优先使用输入 JSON 中的 `worktree.branch`；`dir` 列优先使用 `worktree.original_repo_dir`，以便跨工作树保持仓库身份稳定。

## 调用方式

此技能可以带或不带参数调用：

- **无参数** (`/webup-statusline`)：通过 `AskUserQuestion` 进行交互式提示，选择列和主题。
- **带参数** (`/webup-statusline dracula`)：NLP 解析主题和列偏好。

### 参数解析（自然语言）

参数字符串为自由文本。使用 NLP 提取：

1. **主题** — 匹配：`gruvbox`, `robbyrussell`, `minimal`, `dracula`。识别别名（暗黑=dracula, 极简=minimal, 复古=gruvbox, レトロ=gruvbox）。
2. **元素** — 查找提及：`model`, `context/进度/コンテキスト`, `effort/推理强度/努力度`, `git/分支/ブランチ`, `dir/目录/ディレクトリ`, `worktree/工作树/ワークツリー`, `vim`。

未指定字段使用默认值：`model,context,effort,git,dir` 列，`gruvbox` 主题。

## 工作流程

1. **如果未提供参数**：使用 `AskUserQuestion` 在单个提示中询问两个问题。`AskUserQuestion` 每个问题最多 4 个选项，因此 **提供列的精选预设** 而不是详尽的切换列表。如果用户选择 "其他"，则将他们的自由文本解释为逗号分隔的列列表（或映射到列的自然语言描述）。

   **Q1 — 列预设**（单选）：要显示哪些列？提供这 3 个精选预设 — `AskUserQuestion` 将自动添加一个 "其他" 选项，允许用户输入自由文本列列表或描述。

   - "全部（推荐）" — `model,context,cost,effort,style,git,dir,worktree`（所有当前有用的列；`vim` 因大多数用户不使用 vim 快捷键而排除）
   - "默认" — `model,context,effort,style,git,dir`（平衡 — 排除 cost 和 worktree；匹配技能的默认标志值）
   - "核心" — `model,context,git,dir`（精简；无努力、无样式、无 cost）

   如果用户选择自动添加的 "其他"，则将他们的自由文本视为逗号分隔的列列表，或视为映射到列的自然语言描述。如果解析不明确，则回退到 `默认`。

   **Q2 — 主题**（单选）：配色主题？
   - "Dracula" — 现代暗黑，紫色/粉色/青色（推荐）
   - "Gruvbox Dark" — 温暖复古调色板，24 位真彩色
   - "Robbyrussell" — 经典 oh-my-zsh 风格，无图标
   - "Minimal" — 无装饰，仅暗淡分隔符

   **如果提供参数**：从参数中解析主题和列。跳过提示。

2. 将用户选择映射到脚本标志：
   - 列预设 → 扩展为预设的 `--elements` 列表：
     - `Everything` → `model,context,cost,effort,style,git,dir,worktree`
     - `Default`    → `model,context,effort,style,git,dir`
     - `Essentials` → `model,context,git,dir`
     - `Other`（由 `AskUserQuestion` 自动添加）→ 解析用户的自由文本；仅保留已识别的列名 (`model,context,cost,effort,style,dir,worktree,git,vim`)。如果解析不明确，则回退到 `Default`。
   - 主题 → `--theme` 值（`gruvbox`, `dracula`, `robbyrussell`, `minimal` 之一）

3. 使用 `--install` 运行生成器：
   ```bash
   npx -y bun ${SKILL_DIR}/scripts/generate.mjs --elements <列表> --theme <主题> --install
   ```

4. 告知用户重启 Claude Code 以查看新的状态行。

## 输出示例

**Dracula**（所有列），剩余=49%，cost=$0.42，effort=high，输出样式=Explanatory，位于工作树中：
```
◈ Opus 4.7 | [■■■■■■■■■■□□□□□□□□□□] 51% | $0.42 | ↯ high | ❋ Explanatory | ⌂ clawmaster | ⊕ worktree:46a6 | ⎇ feat/xyz
```
（条形黄色 — 剩余 49%；`$0.42` 金币会话花费紧邻条形；努力 "high" 粗体红色；紫色 `❋ Explanatory` 位于努力和目录之间；上下文不带前缀图标 — 条形已足够直观）

**Gruvbox Dark**（模型 + 上下文 + 努力 + 目录 + git），剩余=88%，努力=medium：
```
✦ Opus 4.7 | [■■□□□□□□□□□□□□□□□□□□] 12% | ↯ medium | ⌂ skills-cc | ⎇ main
```
（条形绿色 — 剩余 88%；努力 "medium" 黄色）

**Minimal**（模型 + 努力 + 目录 + git），努力=low：
```
Claude Opus 4.7 · low · skills-cc · main
```
（极简无前缀图标；努力 "low" 绿色）

## 注意事项

- 生成的脚本保存到 `~/.claude/scripts/statusline.sh`
- 再次运行技能会覆盖现有脚本 — 直接重新运行即可更改主题或列
- 脚本使用 `jq` 解析 JSON 输入 — 确保已安装。在 Windows 上，脚本会自动检测 WinGet 和 scoop jq 路径；如果仍然找不到 jq，请手动将其添加到 PATH 中
- Git 脏检测使用 `--no-optional-locks` 以避免干扰其他 git 操作
