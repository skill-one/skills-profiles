# od-contribute — OpenDesign 的首次贡献流程

锁定到 `nexu-io/open-design`。分支按**贡献类型**划分，而非按问题划分。用类型特定的无代码验证器替换了 dev-loop。设计目标为让没有任何编程背景的产品用户也能提交真实的 PR。

## 语言

在所有面向用户的消息中镜像用户的语言——`AskUserQuestion` 标签和描述、状态更新、错误说明。从他们的第一条消息中检测；不确定时默认为英文。

**生成的工件（PR 标题、提交信息、PR/问题正文文件、分支名称）必须为英文**，无论用户的聊天语言是什么。GitHub 规范、维护者审查和搜索都假设为英文。`templates/` 下的模板已经是英文——渲染时保持原样。

脚本位于 `scripts/` 下。从任何脚本中源共享的辅助工具：

```bash
source "$(dirname "$0")/config.sh"
```

下方的 `SKILL_DIR` = 包含此 `SKILL.md` 的目录。

---

## 第 1 步 — 前置条件检查（始终为第一步）

```bash
bash "$SKILL_DIR/scripts/check-prereqs.sh"
```

- 退出码 0：从标准输出捕获 `GH_USER=<login>`。默认 `TARGET_FORK="${GH_USER}/open-design"`。
- 退出码 2：原封不动地显示打印的安装/认证提示并停止。不要尝试令牌工作绕过。

如果 `gh repo view "$TARGET_FORK"` 失败，询问用户（一个 `AskUserQuestion`）是否现在通过 `gh repo fork nexu-io/open-design --clone=false` 分叉。默认为是。

## 第 2 步 — 选择贡献类型

单个 `AskUserQuestion`（标题："贡献"，多选：否），四个选项。将选项标签/描述翻译成用户的聊天语言；分支路由保持不变。

1. **🎨 提交我用 OD 制作的内容**——_我要贡献到上游的技能、设计系统、HyperFrame 或模板_ → 分支 `3a`
2. **🌍 翻译 OD 文档**——_README / QUICKSTART / CONTRIBUTING 翻译成新的语言_ → 分支 `3b`
3. **📝 修复文档 / 撰写博客 / 修正错别字**——_错别字修正、死链接、用例说明_ → 分支 `3c`
4. **🐛 报告 Bug**——_某功能出问题了；我会帮助将其转化为高质量的问题_ → 分支 `3d`（问题路径，无 PR）

每个分支都是自包含的。步骤 7–8（预览 + 推送）在分支 `3a`/`3b`/`3c` 中共享。分支 `3d` 完全跳过它们。

---

### 第 3a 步 — OD 产品提交（技能 / 设计系统）

**3a.1** 询问用户："你想提交的工件的本地路径是什么？"（单个自由文本，翻译成用户的聊天语言）。常见：一个文件夹路径（技能）或一个 `DESIGN.md` 文件（设计系统）。

**3a.2** 探测类型：

```bash
# 技能：包含带 frontmatter 的 SKILL.md 的文件夹。
# 设计系统：匹配 DESIGN.md 结构的文件。
```

如果模糊，询问用户确认。

**3a.3** 运行设置：

```bash
bash "$SKILL_DIR/scripts/setup-workspace.sh" skill <slug>
# 或
bash "$SKILL_DIR/scripts/setup-workspace.sh" design-system <slug>
```

`<slug>` 是技能 `name` frontmatter 字段的 `od::slugify` 或品牌名称。从标准输出捕获 `WORKDIR`。

**3a.4** 将工件复制到工作区的正确目标目录：
- 技能 → `$WORKDIR/skills/<slug>/`
- 设计系统 → `$WORKDIR/design-systems/<brand-slug>/DESIGN.md`（以及同一文件夹中的任何同级资源）

**3a.5** 验证：

```bash
bash "$SKILL_DIR/scripts/validate-skill-submission.sh" "$WORKDIR/skills/<slug>"
# 或，传递 1-2 个参考 DESIGN.md 文件：
bash "$SKILL_DIR/scripts/validate-design-system.sh" \
  "$WORKDIR/design-systems/<slug>/DESIGN.md" \
  --reference "$WORKDIR/design-systems/airbnb/DESIGN.md" \
  --reference "$WORKDIR/design-systems/apple/DESIGN.md"
```

如果验证失败，原封不动地显示错误行，询问用户修复，重试。**永远不要推送失败的工件。**

**3a.6** 通过 `AskUserQuestion`（将标签翻译成用户的聊天语言）询问 3 个简短问题：
- "我们应该在 PR 中以什么名字署名？" — 自由文本
- "这个技能 / 设计系统的简短介绍？" — 自由文本
- "截图路径（可选）？" — 自由文本

**3a.7** 使用替换渲染 `templates/PR-BODY-skill.md`（或 `PR-BODY-design-system.md`）：
- `{{SKILL_NAME}}`, `{{SKILL_SLUG}}`（或 `{{BRAND_NAME}}`, `{{BRAND_SLUG}}`）
- `{{PITCH}}`（单行）
- `{{MOTIVATION}}`（自由文本——代理可以基于技能正文起草此内容，但用户确认）
- `{{TRY_PROMPT}}`（用户推荐的提示——代理建议默认值，用户确认）
- `{{SCREENSHOT_BLOCK}}`（如果提供了截图路径，则为 Markdown 图片块，否则为空）
- `{{DISCORD_INVITE}}` 来自 `$OD_DISCORD_INVITE`

写入 `$WORKDIR/.od-contrib/PR-BODY.md`。

→ 跳转到 **第 7 步**。

---

### 第 3b 步 — 国际化翻译

**3b.1** 设置工作区（slug = `translate-<doc>-<lang>` 如果已知，否则 `translate`）：

```bash
bash "$SKILL_DIR/scripts/setup-workspace.sh" i18n translate
# 捕获 WORKDIR
```

**3b.2** 发现差距：

```bash
bash "$SKILL_DIR/scripts/discover-i18n-gaps.sh" "$WORKDIR" > /tmp/od-i18n-gaps.json
```

每行是 JSON。按以下顺序排序：
- `status: "missing"` 优先（缺失语言是最高杠杆）
- 然后 `status: "stale"` 按 `english_commits_since_translation` 降序排列
- README 家族优先于 QUICKSTART 优先于 CONTRIBUTING

**3b.3** 取前 3-4 个差距，通过 `AskUserQuestion`（标题："翻译目标"）呈现。每个选项标签如：`README → 한국어 (韩语)` / `QUICKSTART (zh-CN) 刷新 — 12 次提交落后`。将标题文本翻译成用户的聊天语言，但保持选项标签描述性（语言名称属于其脚本）。

**3b.4** 一旦用户选择，**重命名分支** 为具体：
```bash
git -C "$WORKDIR" branch -m "od-contrib/i18n/<doc>-<lang>-<date>"
```
（或者如果用户之前确认，可以在第 3b.1 步预设 slug。）

**3b.5** 翻译。阅读英文源。结构化保留地翻译：
- 代码块：保持未翻译
- 品牌 / 产品名称：保持未翻译
- 行内代码中的文件名：保持未翻译
- 图片 / 链接目标：保持未翻译；如果存在链接文档的本地化版本，将链接切换到本地化文件
- 标题：翻译，保持标题深度相同
- 表格：仅翻译单元格文本，保持对齐/管道

将结果写入 `$WORKDIR/<TRANSLATED_PATH>`（例如 `QUICKSTART.es.md`）。向用户显示与英文源的比较统一差异，以进行视觉检查（行数差异在 ±15% 以内是一个健康的信号）。

**3b.6** 将翻译文件与英文源进行验证。`--reference` 标志告诉验证器忽略源中已经损坏的相对引用——OD 文档经常链接到网站路由 slug（例如 `skills/blog-post/`），这些不是磁盘上的文件；我们不想因为预先存在的死引用而导致结构化保留的翻译失败。

```bash
bash "$SKILL_DIR/scripts/validate-markdown.sh" \
  "$WORKDIR/<TRANSLATED_PATH>" \
  --reference "$WORKDIR/<ENGLISH_PATH>"
```

如果失败 → 原封不动地显示，修复，重试。

**3b.7** 渲染 `templates/PR-BODY-i18n.md` 并使用 `{{DOC_NAME}}`, `{{LANG_DISPLAY_NAME}}`, `{{LANG_CODE}}`, `{{TRANSLATED_PATH}}`, `{{ENGLISH_PATH}}`, `{{STATUS}}`, `{{TRANSLATION_NOTES}}`（代理的一段话：任何棘手之处、保留的未翻译术语等），`{{DISCORD_INVITE}}`。

→ **第 7 步**。

---

### 第 3c 步 — 文档 / 博客 / 错别字

**3c.1** 设置工作区（slug `docs`）：

```bash
bash "$SKILL_DIR/scripts/setup-workspace.sh" docs <slug>
```

**3c.2** 询问用户（一个 `AskUserQuestion`）：
1. **自动发现小修复**（运行 `discover-doc-gaps`，选择一些）
2. **我有特定的修复想法**（自由文本）
3. **我想撰写博客 / 案例研究**（自由文本——用例是什么？）

**3c.3 (自动发现分支)** 运行：

```bash
bash "$SKILL_DIR/scripts/discover-doc-gaps.sh" "$WORKDIR" > /tmp/od-doc-gaps.json
```

按 `kind`（错别字 / 死链接 / todo）分组。向用户显示最多 6 个候选者通过 `AskUserQuestion`。一旦选择，在代码中应用修复（错别字：替换单词；死链接：询问用户新的 URL；todo：这是一个真正的任务，询问用户撰写缺失的文本）。

**3c.4 (特定修复分支)** 阅读文件，应用用户描述的更改。通过差异确认。

**3c.5 (博客分支)** 首先检查 OD 是否有博客目录：

```bash
ls "$WORKDIR/docs" 2>/dev/null
```

如果存在 `docs/blog/` 或类似的，将新帖子放在那里。如果不存在，询问用户它应该放在哪里，默认为 `docs/<slug>.md`。生成大纲 → 用户填写特定部分（他们的用例、截图、使用的提示、渲染输出）→ 代理拼接成最终 Markdown。

**3c.6** 验证所有更改/添加的文件。对于已存在于仓库中的文件（错别字修复、死链接修复、文档编辑），传递 `--reference` 指向 HEAD 版本，以便我们仅在用户引入的相对引用上失败，而不是预先存在的路由 slug：

```bash
# 对于修改现有文件：
git -C "$WORKDIR" show "HEAD:<path>" > "/tmp/od-contrib-orig-<basename>" 2>/dev/null
bash "$SKILL_DIR/scripts/validate-markdown.sh" \
  "$WORKDIR/<changed-path>" \
  --reference "/tmp/od-contrib-orig-<basename>"

# 对于用户从零开始创建的新文件（例如一个博客帖子），
# 省略 --reference。验证器将完全跳过相对引用检查（因为它无法在孤立状态下区分路由 slug 和真实路径）。
```

**3c.7** 渲染 `templates/PR-BODY-docs.md` 并使用 `{{ONE_LINE_SUMMARY}}`, `{{DETAILS}}`, `{{FILES_LIST}}`, `{{DISCORD_INVITE}}`。

→ **第 7 步**。

---

### 第 3d 步 — Bug 报告（问题路径，无 PR）

**3d.1** 运行时读取 OD 的实际模式以确保镜像：

```bash
gh api "repos/${TARGET_REPO}/contents/.github/ISSUE_TEMPLATE/bug-report.yml" --jq .content | base64 -d > /tmp/od-bug-report.yml
```

如果模式与模板（`templates/ISSUE-BODY-bug.md`）有偏差，重新生成正文以匹配。

**3d.2** 通过 `AskUserQuestion`，每个关键字段一个结构化提示。使用**平实语言**，而不是 YAML 字段名：

| Bug-report 字段 | 向用户提问的提示 |
|---|---|
| `description` | "出什么问题了？一句话即可。" |
| `steps` | "如何复现？逐步向我说明。" |
| `expected` | "你期望发生什么？" |
| `version` | "你运行的是哪个 OD 版本？（关于菜单，或 `od --version`）" |
| `platform` | 下拉菜单：macOS (Apple Silicon) / macOS (Intel) / Windows / Linux / 其他 |
| `logs` | "你能粘贴任何错误日志吗？如果没有，跳过。" |
| `screenshots` | "截图路径？如果没有，跳过。" |

将上述每个提示在运行时翻译成用户的聊天语言。

**3d.3** 自动收集我们能收集的（这些不需要询问用户）：
- 从 `uname` 获取 OS 家族
- 如果相关，从 `node -v` 获取 Node 版本

**3d.4** 去重：从描述中提取 3-5 个关键词，运行：

```bash
gh search issues "<keywords>" --repo "$TARGET_REPO" --state open --limit 5 --json number,title,url
```

如果存在匹配项，通过 `AskUserQuestion`（翻译成用户的语言）呈现给用户："这些现有问题看起来相关。你想：(a) 评论一个现有问题，(b) 还是无论如何打开新问题，(c) 取消？"

**3d.5** 如果继续开新问题，渲染 `templates/ISSUE-BODY-bug.md` 并提交：

```bash
bash "$SKILL_DIR/scripts/create-issue.sh" \
  --title "$TITLE" \
  --body-file "$WORKDIR_OR_TMP/.od-contrib/ISSUE-BODY.md" \
  --dedupe-keywords "<keywords>"
```

**3d.6** 在单独的一行打印问题 URL。**不要**从此分支推送分支或打开 PR。

---

## 第 7 步 — 预览 + 确认（仅 PR 分支共享）

向用户显示一个干净的摘要：

```text
即将提交：
  分支：  od-contrib/<type>/<slug>-<date>
  文件：
    + skills/foo/SKILL.md            (1.2 KB)
    + skills/foo/preview.png         (54 KB)
  推送到：  <fork 或上游>
  打开 PR：  nexu-io/open-design:main ← <fork>:<branch>
```

然后 `git -C "$WORKDIR" diff --stat` 和渲染的 PR 正文的前 40 行，以进行视觉检查。

必须 `AskUserQuestion` 确认（翻译成用户的语言）："推送这个 PR？" 提供三个选项：
- **发布它** — 继续到第 8 步
- **让我修改** — 返回到相关的第 3 子步骤
- **取消** — 将工作区留在磁盘上，告诉用户路径以便他们稍后返回，退出

没有明确的 "发布它" 不要推送。

## 第 8 步 — 推送 & 打开 PR

```bash
bash "$SKILL_DIR/scripts/create-pr.sh" \
  --workdir "$WORKDIR" \
  --type "<skill|design-system|i18n|docs>" \
  --title "<PR 标题来自 references/newcomer-tone.md>" \
  --body-file "$WORKDIR/.od-contrib/PR-BODY.md"
```

在单独的一行打印 PR URL。完成。

---

## 安全护栏（强制）

- 永远不要推送到 `main` / `master` / `develop`。推送脚本会拒绝。
- 永远不要 `--force` 推送。只是不要。
- 所有工作区活动都保持在 `$OD_WORK_ROOT`（默认 `$HOME/od-contrib-work`）。`od::assert_in_workroot` 强制执行此规则。
- Bug 报告路径**始终**在 `gh issue create` 之前运行去重搜索。
- 尊重用户记忆：跳过 GitHub 用户 `xxiaoxiong` 的任何贡献者查找（[[feedback_no_outreach_xxiaoxiong]]）。

## 不应使用此技能的情况

- 用户想修复守护进程 / 网络Bug或添加带代码更改的功能 → 使用 `auto-github-contributor`（它有 TDD 循环）。此技能故意不运行 lint/typecheck/测试，因为内容路径不需要它们。
- 用户想从零**生成**技能 / 设计系统 → 那是 OpenDesign 本身。先运行 OD，获取工件，然后回来这里提交它。
