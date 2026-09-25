# Obsidian 设置 — 库初始化

你正在设置一个新的 Obsidian 知识库（或修复一个现有的知识库）。

## 第 1 步：创建 .env

如果 `.env` 不存在，从 `.env.example` 创建它。询问用户以下内容：

1. **知识库应该存放在哪里？** → `OBSIDIAN_VAULT_PATH`
   - 默认：`~/Documents/obsidian-wiki-vault`
   - 必须是绝对路径（展开后）

2. **你的源文档在哪里？** → `OBSIDIAN_SOURCES_DIR`
   - 可以是多个路径，用逗号分隔
   - 默认：`~/Documents`
   - 本地 git 仓库克隆（公共或私有，任何主机）也可以列在这里——先在本地克隆仓库，然后添加其路径。有关仓库源如何处理的说明，请参阅 `wiki-ingest/SKILL.md` 中的“导入 Git 仓库”。

3. **要导入 Claude 历史记录吗？** → `CLAUDE_HISTORY_PATH`
   - 默认：自动从 `~/.claude` 发现
   - 如果 Claude 数据在其他地方，请显式设置

4. **安装了 QMD 吗？** → `QMD_WIKI_COLLECTION` / `QMD_PAPERS_COLLECTION` / `QMD_TRANSPORT`
   - 可选。启用 `wiki-query` 中的语义搜索和 `wiki-ingest` 中的源发现。
   - 默认为 `QMD_TRANSPORT=mcp`，除非用户希望代理直接调用本地 `qmd` CLI。
   - 如果使用 CLI 模式，默认设置 `QMD_CLI_SEARCH_MODE=quality`；如果重新排序太慢，建议 `balanced`。
   - 如果不确定，暂时跳过——这两种技能都会自动回退到 `Grep`。
   - 安装说明：请参阅 `.env.example`（QMD 部分）。
   - **如果 `QMD_WIKI_COLLECTION` 被设置，请验证该集合排除了 `_raw/`。** 知识库集合和论文集合必须保持分离——`wiki-query` 将它们作为不同的层引用（编译的知识与原始暂存），而 `OBSIDIAN_VAULT_PATH` 包含 `_raw/`，所以一个简单的 `qmd collection add <vault>` 会默默地合并这两个。
     读取 `~/.config/qmd/index.yml`，找到 `$QMD_WIKI_COLLECTION` 的条目，并检查其 `ignore` 列表是否包含 `_raw/**`（理想情况下还应包含 `log.md`，它没有语义价值）。如果集合还不存在，请创建它（`qmd collection add "$OBSIDIAN_VAULT_PATH" --name <collection-name>`），然后手动将 `ignore` 块添加到 `index.yml` 中——`qmd` 没有 `--ignore` 标志，并且拒绝在一个已经有一个集合的路径上执行第二次 `collection add`，所以编辑 YAML 是唯一的方法。编辑后运行 `qmd update`。
     如果集合已经存在但没有 `ignore` 块，请告诉用户他们的知识库集合正在索引 `_raw/`（包括 `wiki-ingest` 留下的 `_raw/_archived/` 草稿），并建议添加 `ignore` 块并重新运行 `qmd update`。

5. **令牌预算警告阈值是多少？** → `WIKI_TOKEN_WARN_THRESHOLD`
   - 默认：`100000`（当全知识库读取成本超过 100K 令牌时发出警告）
   - 设置为 `0` 以禁用警告
   - `wiki-status` 显示令牌足迹表并自动发出此警告

6. **启用暂存写入吗？** → `WIKI_STAGED_WRITES`
   - 默认：未设置 / `false`（页面直接写入其最终位置）
   - 设置为 `true` 用于团队知识库、高风险领域或任何知识库，其中人类希望对每个 LLM 编写的页面拥有最终决定权
   - 启用时：所有新/更新的页面首先进入 `_staging/`；运行 `/wiki-stage-commit` 进行审查并推广它们
   - `wiki-status` 在文件等待时显示“暂存写入待处理”计数

在解决配置后，使用 Config Resolution Protocol 中 `.skills/llm-wiki/SKILL.md` 中的确切 `obsidian_wiki_config_dir` 算法分配全局配置目录。仅在它不存在时创建共享写入配置文件。保留现有的 `$GLOBAL_CONFIG_DIR/WRITING.md`；永远不要覆盖它，也不要询问额外的写作风格问题。

当它从配置加载时使用 `OBSIDIAN_WIKI_REPO`。当它不存在时，从加载的技能的绝对路径派生绝对仓库/数据根，区分打包的 `<root>/skills/wiki-setup/SKILL.md` 布局和源 `<root>/.skills/wiki-setup/SKILL.md` 布局。然后检查两个规范模板布局：

- 打包安装：`<root>/skills/llm-wiki/references/WRITING.md`
- 源检出：`<root>/.skills/llm-wiki/references/WRITING.md`

```bash
GLOBAL_CONFIG_DIR="$(obsidian_wiki_config_dir)"
mkdir -p "$GLOBAL_CONFIG_DIR"

SKILL_FILE="<绝对路径的 wiki-setup/SKILL.md>"
SKILL_DIR="$(cd "$(dirname "$SKILL_FILE")" && pwd)"
if [ -n "${OBSIDIAN_WIKI_REPO:-}" ]; then
  WIKI_ROOT="${OBSIDIAN_WIKI_REPO%/}"
else
  case "$SKILL_DIR" in
    */.skills/wiki-setup) WIKI_ROOT="${SKILL_DIR%/.skills/wiki-setup}" ;;
    */skills/wiki-setup) WIKI_ROOT="${SKILL_DIR%/skills/wiki-setup}" ;;
    *) echo "Cannot derive writing-profile template root from $SKILL_DIR" >&2; exit 1 ;;
  esac
fi

WRITING_TEMPLATE=""
for candidate in \
  "$WIKI_ROOT/skills/llm-wiki/references/WRITING.md" \
  "$WIKI_ROOT/.skills/llm-wiki/references/WRITING.md"
do
  if [ -f "$candidate" ]; then
    WRITING_TEMPLATE="$candidate"
    break
  fi
done
[ -n "$WRITING_TEMPLATE" ] || { echo "Writing profile template not found under $WIKI_ROOT" >&2; exit 1; }

WRITING_PROFILE="$GLOBAL_CONFIG_DIR/WRITING.md"
if [ ! -e "$WRITING_PROFILE" ]; then
  cp "$WRITING_TEMPLATE" "$WRITING_PROFILE"
fi
```

## 第 2 步：创建库目录结构

```bash
mkdir -p "$OBSIDIAN_VAULT_PATH"/{concepts,entities,skills,references,synthesis,journal,projects,_archives,_raw,_staging,.obsidian}
```

- `.obsidian/` — Obsidian 自己的配置。创建库识别。
- `projects/` — 每个项目的知识（在摄取过程中填充）。
- `_archives/` — 存储知识库快照以用于重建/恢复操作。
- `_raw/` — 未处理的草稿的暂存区域。将草稿笔记放在这里；`wiki-ingest` 将将其提升为正确的知识库页面，并将原始文件移动到 `_raw/_archived/`（在第一次使用时创建）。
- `_staging/` — 当 `WIKI_STAGED_WRITES=true` 时 LLM 编写的页面的审查队列。这里的页面在通过 `/wiki-stage-commit` 推广之前在 Obsidian 的图中不可见。

## 第 3 步：创建特殊文件

### index.md

```markdown
---
title: 知识库索引
---

# 知识库索引

*此索引自动维护。最后更新：TIMESTAMP*

## 概念

*还没有页面。使用 `wiki-ingest` 添加你的第一个源。*

## 实体

## 技能

## 参考文献

## 综合

## 日志
```

### log.md

```markdown
---
title: 知识库日志
---

# 知识库日志

- [TIMESTAMP] INIT vault_path="OBSIDIAN_VAULT_PATH" categories=concepts,entities,skills,references,synthesis,journal
```

### hot.md

```markdown
---
title: 热缓存
updated: TIMESTAMP
---

# 热缓存

*一个约 500 字的语义快照，显示最近的活跃情况。每次主要写入操作后更新。*

## 最近活动

- [TIMESTAMP] INIT — 在 OBSIDIAN_VAULT_PATH 创建知识库

## 活跃线程

*还没有——开始摄取源以填充。*

## 关键要点

*还没有。*

## 标记的矛盾

*还没有。*
```

### .manifest.json

创建一个空清单，以便摄取技能有一个跟踪文件可以追加，并且 `obsidian-wiki doctor` 报告知识库已完成（它将 `.manifest.json` 视为必需的核心文件）：

```bash
printf '{}\n' > "$OBSIDIAN_VAULT_PATH/.manifest.json"
```

## 第 4 步：创建 .obsidian 配置

为良好的开箱即用体验创建最小的 Obsidian 配置：

### .obsidian/app.json
```json
{
  "strictLineBreaks": false,
  "showFrontmatter": false,
  "defaultViewMode": "preview",
  "livePreview": true
}
```

### .obsidian/appearance.json
```json
{
  "baseFontSize": 16
}
```

## 第 5 步：推荐 Obsidian 插件

告诉用户这些推荐的社区插件（它们需要手动安装）：

1. **Dataview** — 查询页面元数据，创建动态表格。知识库的必备插件。
2. **Graph Analysis** — 增强图视图以探索连接。
3. **Templater** — 如果他们想使用模板手动创建页面。
4. **Obsidian Git** — 自动将知识库备份到 git 仓库。

## 第 6 步：验证设置

运行快速合理性检查：
- [ ] 知识库目录存在，包含：`concepts/`、`entities/`、`skills/`、`references/`、`synthesis/`、`journal/`、`projects/`、`_archives/`、`_raw/`
- [ ] `index.md` 存在于知识库根目录
- [ ] `log.md` 存在于知识库根目录
- [ ] `hot.md` 存在于知识库根目录
- [ ] `.manifest.json` 存在于知识库根目录（空的 `{}` 可以）
- [ ] `.env` 设置了 `OBSIDIAN_VAULT_PATH`
- [ ] `.obsidian/` 目录存在
- [ ] `_staging/` 目录存在（即使 `WIKI_STAGED_WRITES` 未设置也需要——在设置时创建以供将来使用）
- [ ] `WRITING_PROFILE` 存在于解析的全局配置目录
- [ ] 源目录（如果配置）存在且可读

报告结果，包括解析的绝对 `WRITING_PROFILE` 路径，并告诉用户他们现在可以：
1. 在 Obsidian 中打开知识库（文件 → 打开知识库 → 选择目录）
2. 运行 `wiki-status` 查看可摄取的内容
3. 运行 `wiki-ingest` 添加他们的第一个源
4. 运行 `claude-history-ingest` 挖掘他们的 Claude 对话
5. 运行 `codex-history-ingest` 挖掘他们的 Codex 会话（如果他们使用 Codex）
6. 任何时候运行 `wiki-status` 检查差异

## 可选：安装停止钩子（自动捕获）

询问用户：**“要在会话结束时自动捕获发现吗？”**

如果同意，将停止钩子安装到他们的全局 Claude Code 设置中，以便每个有意义的会话在关闭之前自动提示 `/wiki-capture --quick`。

**钩子做什么：** 读取停止时的会话记录，计算文件编辑和 shell 调用次数，如果有显著工作，则提示 Claude 运行 `/wiki-capture --quick` 一次。`wiki-capture` 快速模式的 KEEP/SKIP 阈值防止噪音——常规或不确定的会话会自动跳过。

**安装步骤：**

1. 找到 obsidian-wiki 仓库路径。如果 `OBSIDIAN_WIKI_REPO` 在配置中设置，请使用它。
   否则，检查常见位置：`~/Documents/projects/obsidian-wiki`、`~/obsidian-wiki`，或询问用户。

2. 定位 `wiki-stop-capture.sh` 脚本。它的路径在 pip/uv 安装和源检出之间不同，因此检查 `<REPO_PATH>` 下的两种布局，并使用第一个存在的：

   - `<REPO_PATH>/hooks/wiki-stop-capture.sh` — 打包安装（`OBSIDIAN_WIKI_REPO` 指向捆绑的 `_data/` 目录，该目录在 `hooks/` 下提供钩子）。
   - `<REPO_PATH>/.claude/hooks/wiki-stop-capture.sh` — 源检出。

   如果都不存在（例如，一个早于捆绑钩子的轮），请从稳定位置获取规范副本并指向那里。使用 `llm-wiki/SKILL.md` 中 Config Resolution Protocol 的全局配置目录（默认为 XDG 风格 `~/.config/obsidian-wiki`，如果该路径已存在则使用遗留的 `~/.obsidian-wiki`）：

   ```bash
   CONFIG_DIR="$( [[ -d "$HOME/.obsidian-wiki" && ! -e "${XDG_CONFIG_HOME:-$HOME/.config}/obsidian-wiki" ]] && echo "$HOME/.obsidian-wiki" || echo "${XDG_CONFIG_HOME:-$HOME/.config}/obsidian-wiki" )"
   mkdir -p "$CONFIG_DIR/hooks"
   curl -fsSL https://raw.githubusercontent.com/Ar9av/obsidian-wiki/main/.claude/hooks/wiki-stop-capture.sh \
     -o "$CONFIG_DIR/hooks/wiki-stop-capture.sh"
   chmod +x "$CONFIG_DIR/hooks/wiki-stop-capture.sh"
   ```

   使用解析的绝对路径作为 `<HOOK_PATH>` 下方的内容。

3. 将钩子条目合并到 `~/.claude/settings.json`：

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "bash <HOOK_PATH>"
          }
        ]
      }
    ]
  }
}
```

   如果 `~/.claude/settings.json` 已存在并且有 `hooks.Stop` 数组，**追加**新条目而不是替换——不要覆盖现有的钩子。

   > **注意——此仓库内可能存在重复提示。** obsidian-wiki 仓库提供其自己的 git 跟踪的 `.claude/settings.json`，在相对路径上注册相同的停止钩子。Claude Code *合并* 项目级和用户级钩子配置而不是让其中一个覆盖另一个，因此仓库内的会话结束会触发两个注册。这是预期的且无害的——钩子声明每个会话的原子哨兵，因此只发出一次提示。保留两者：删除项目条目会弄脏一个跟踪框架文件并禁用克隆该仓库的任何人的捕获。

4. 确认：**“停止钩子已安装。Claude Code 将在您写入文件或运行 ≥ 4 个 shell 命令的任何会话结束时提示 `/wiki-capture --quick`。”**

**稍后卸载：** 从 `~/.claude/settings.json` 中删除钩子条目或将 `WIKI_STOP_CAPTURE=false` 设置在您的 shell 中以跳过单个会话的捕获（`HIVEMIND_CAPTURE=false` 仍然受尊重）。

## 可选：配置 GitHub 同步

询问用户：**“要同步您的知识库到私有 GitHub 仓库吗？”**

知识库是纯 markdown，因此推送到 git 可以免费获得版本历史记录、备份和跨设备同步。这是可选的——如果用户拒绝或没有现成的仓库，请跳过。

如果同意：

1. 询问仓库 URL（例如 `https://github.com/you/my-wiki.git`）。如果知识库包含个人笔记，建议它是**私有的**。
2. 运行 CLI，它处理 `git init`、默认的 `.gitignore` 和 `origin` 远程的连接——这是 `obsidian-wiki setup` 的交互式提示和 `setup.sh` 使用的相同代码路径，因此有一个实现需要保持正确（有关原因，请参阅问题 #153）：
   ```bash
   obsidian-wiki sync-setup "<repo-url>" --vault "$OBSIDIAN_VAULT_PATH"
   ```
   如果 `obsidian-wiki` 二进制文件不在 PATH 上（源检出而没有安装），请从仓库中运行它：`PYTHONPATH="$OBSIDIAN_WIKI_REPO" python3 -m obsidian_wiki.cli sync-setup ...`，使用可用的 `OBSIDIAN_WIKI_REPO` 或本地检出路径。
3. 告诉用户他们可以随时运行 `obsidian-wiki sync` 来提交和推送待处理的库更改（全部暂存，带时间戳提交，推送）。没有要检查的同步状态配置文件——库自己的 `git remote` 是真相来源。

## 可选：设置后刷新 QMD

如果配置了 `QMD_WIKI_COLLECTION` 并且本地 QMD CLI 可用，在初始库文件存在后运行 `qmd update`，以便新鲜库立即可查询。通常在设置时不需要嵌入过程，因为库开始时为空，所以一个简单的更新就足够了，除非你已经填充了页面。在运行它之前，确认 Step 1.4 中描述的 `_raw/` 排除是否到位——否则此更新会将（当前为空的）暂存目录索引到知识库集合中，并且未来放在那里的每个草稿都会默默地加入其中。
