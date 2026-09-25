# 发布技能

支持任何项目类型的多语言变更日志的通用发布工作流。

## 用户输入工具

当此技能提示用户时，请遵循以下工具选择规则（优先级顺序）：

1. **优先使用**当前代理运行时暴露的**内置用户输入工具** — 例如，`AskUserQuestion`、`request_user_input`、`clarify`、`ask_user` 或任何等效工具。
2. **降级处理**：如果没有此类工具，则发出编号的纯文本消息，并要求用户对每个问题回复选择的编号/答案。
3. **批量处理**：如果工具支持每调用处理多个问题，则将所有适用问题合并为单个调用；如果仅支持单个问题，则按优先级顺序逐个询问。

下方的具体 `AskUserQuestion` 引用仅为示例 — 在其他运行时中应替换为本地等效工具。

## 快速入门

只需运行 `/release-skills` — 自动检测您的项目配置。

## 支持的项目

| 项目类型 | 版本文件 | 自动检测 |
|----------|----------|----------|
| Node.js | package.json | ✓ |
| Python | pyproject.toml | ✓ |
| Rust | Cargo.toml | ✓ |
| Claude 插件 | marketplace.json | ✓ |
| 通用 | VERSION / version.txt | ✓ |

## 选项

| 标志 | 描述 |
|------|------|
| `--dry-run` | 预览变更而不执行 |
| `--major` | 强制主版本号递增 |
| `--minor` | 强制次版本号递增 |
| `--patch` | 强制修订号递增 |
| `--backfill-releases` | 为变更日志部分创建现有的标签缺失的 GitHub Releases |

## 工作流

### 第 1 步：检测项目配置

1. 检查是否存在 `.releaserc.yml`（可选的配置覆盖）
   - 如果存在，则检查它是否定义了发布钩子
2. 通过扫描自动检测版本文件（优先级顺序）：
   - `package.json`（Node.js）
   - `pyproject.toml`（Python）
   - `Cargo.toml`（Rust）
   - `marketplace.json` 或 `.claude-plugin/marketplace.json`（Claude 插件）
   - `VERSION` 或 `version.txt`（通用）
3. 使用 glob 模式扫描查找变更日志文件：
   - `CHANGELOG*.md`
   - `HISTORY*.md`
   - `CHANGES*.md`
4. 通过文件名后缀识别每个变更日志的语言
5. 检测 GitHub 发布支持：
   - 检查 `origin` 是否指向 GitHub
   - 检查 `gh` 是否已安装并认证
   - 在可用时使用 `gh release list --limit 5` 检查现有发布
6. 显示检测到的配置

**项目钩子契约**：

如果 `.releaserc.yml` 定义了 `release.hooks`，则保持发布工作流通用，并将特定于项目的打包/发布委托给这些钩子。

支持的钩子：

| 钩子 | 目的 | 预期责任 |
|------|------|----------|
| `prepare_artifact` | 使目标可发布 | 验证目标是否自包含，同步/嵌入本地依赖项，可选地暂存额外文件 |
| `publish_artifact` | 发布可发布的目标 | 上传准备好的目标（如果项目使用暂存目录，则为暂存目录），附加版本/变更日志/标签 |

支持的占位符：

| 占位符 | 含义 |
|------|------|
| `{project_root}` | 仓库根目录的绝对路径 |
| `{target}` | 正在发布的模块/技能的绝对路径 |
| `{artifact_dir}` | 当项目使用时，此目标用于临时暂存目录的绝对路径 |
| `{version}` | 发布工作流选择的版本 |
| `{dry_run}` | `true` 或 `false` |
| `{release_notes_file}` | 包含发布笔记/变更日志文本的 UTF-8 文件的绝对路径 |

执行规则：
- 保持技能通用：不要将注册表/包管理器/项目布局细节硬编码到此 SKILL 中。
- 如果存在 `prepare_artifact`，则在需要最终可发布目标状态的发布相关检查之前，针对每个目标运行一次。
- 将发布笔记写入临时文件，并将该文件路径传递给 `publish_artifact`；不要将多行变更日志文本内联到 shell 命令中。
- 如果没有钩子，则回退到默认的、与项目无关的发布工作流。

**语言检测规则**：

变更日志文件遵循模式 `CHANGELOG_{LANG}.md` 或 `CHANGELOG.{lang}.md`，其中 `{lang}` / `{LANG}` 是语言或区域代码。

| 模式 | 示例 | 语言 |
|------|------|------|
| 无后缀 | `CHANGELOG.md` | en（默认） |
| `_{LANG}`（大写） | `CHANGELOG_CN.md`、`CHANGELOG_JP.md` | 对应语言 |
| `.{lang}`（小写） | `CHANGELOG.zh.md`、`CHANGELOG.ja.md` | 对应语言 |
| `.{lang-region}` | `CHANGELOG.zh-CN.md` | 对应区域变体 |

常见语言代码：`zh`（中文）、`ja`（日语）、`ko`（韩语）、`de`（德语）、`fr`（法语）、`es`（西班牙语）。

**输出示例**：
```
检测到项目：
  版本文件：package.json (1.2.3)
  变更日志：
    - CHANGELOG.md (en)
    - CHANGELOG.zh.md (zh)
    - CHANGELOG.ja.md (ja)
```

### 第 2 步：分析自上次标签以来的变更

```bash
LAST_TAG=$(git tag --sort=-v:refname | head -1)
git log ${LAST_TAG}..HEAD --oneline
git diff ${LAST_TAG}..HEAD --stat
```

按常规提交类型分类：

| 类型 | 描述 |
|------|------|
| feat | 新功能 |
| fix | 修复 |
| docs | 文档 |
| refactor | 代码重构 |
| perf | 性能改进 |
| test | 测试变更 |
| style | 格式化、样式 |
| chore | 维护（在变更日志中跳过） |

**破坏性变更检测**：
- 提交信息以 `BREAKING CHANGE` 开头
- 提交正文/结尾包含 `BREAKING CHANGE:`
- 移除公共 API、重命名导出、更改接口

如果检测到破坏性变更，则警告用户： "检测到破坏性变更。考虑主版本号递增（使用 `--major` 标志）。"

### 第 3 步：确定版本号递增

规则（优先级顺序）：
1. 用户标志 `--major/--minor/--patch` → 使用指定值
2. 检测到破坏性变更 → 主版本号递增（1.x.x → 2.0.0）
3. 存在 `feat:` 提交 → 次版本号递增（1.2.x → 1.3.0）
4. 其他情况 → 修订号递增（1.2.3 → 1.2.4）

显示版本变更：`1.2.3 → 1.3.0`

### 第 4 步：生成多语言变更日志

针对每个检测到的变更日志文件：

1. **从文件名后缀识别语言**
2. **检测第三方贡献者**：
   - 检查合并提交：`git log ${LAST_TAG}..HEAD --merges --pretty=format:"%H %s"`
   - 对于每个合并的 PR，通过 `gh pr view <number> --json author --jq '.author.login'` 识别 PR 作者
   - 与仓库所有者（通过 `gh repo view --json owner --jq '.owner.login'`）比较
   - 如果 PR 作者 ≠ 仓库所有者 → 第三方贡献者
3. **生成该语言的内容**：
   - 目标语言的节标题
   - 用目标语言自然书写的变更描述（不要翻译）
   - 日期格式：YYYY-MM-DD（通用）
   - **第三方贡献**：将贡献者署名 `(by @username)` 添加到变更日志条目
4. **插入到文件头部**（保留现有内容）

**节标题翻译**（内置）：

| 类型 | en | zh | ja | ko | de | fr | es |
|------|----|----|----|----|----|----|-----|
| feat | Features | 新功能 | 新機能 | 새로운 기능 | Funktionen | Fonctionnalités | Características |
| fix | Fixes | 修复 | 修正 | 수정 | Fehlerbehebungen | Corrections | Correcciones |
| docs | Documentation | 文档 | ドキュメント | 문서 | Dokumentation | Documentation | Documentación |
| refactor | Refactor | 重构 | リファクタリング | 리팩토링 | Refactoring | Refactorisation | Refactorización |
| perf | Performance | 性能优化 | パフォーマンス | 성능 | Leistung | Performance | Rendimiento |
| breaking | Breaking Changes | 破坏性变更 | 破壊的変更 | 주요 변경사항 | Breaking Changes | Changements majeurs | Cambios importantes |

**变更日志格式**：

```markdown
## {VERSION} - {YYYY-MM-DD}

### 新功能
- 新功能描述
- 第三方贡献（by @username）

### 修复
- 修复描述

### 文档
- 文档变更描述
```

仅包含有变更的节。省略空节。

**第三方署名规则**：
- 仅对不是仓库所有者的贡献者添加 `(by @username)`
- 使用带 `@` 前缀的 GitHub 用户名
- 放在变更日志条目行的末尾
- 在所有语言中一致使用（始终使用 `(by @username)` 格式，不要翻译）

**多语言示例**：

英语（CHANGELOG.md）：
```markdown
## 1.3.0 - 2026-01-22

### 新功能
- 添加用户认证模块 (by @contributor1)
- 支持 OAuth2 登录

### 修复
- 修复连接池内存泄漏
```

中文（CHANGELOG.zh.md）：
```markdown
## 1.3.0 - 2026-01-22

### 新功能
- 新增用户认证模块 (by @contributor1)
- 支持 OAuth2 登录

### 修复
- 修复连接池内存泄漏问题
```

日语（CHANGELOG.ja.md）：
```markdown
## 1.3.0 - 2026-01-22

### 新機能
- ユーザー認証モジュールを追加 (by @contributor1)
- OAuth2 ログインをサポート

### 修正
- コネクションプールのメモリリークを修正
```

### 第 5 步：按技能/模块分组变更

分析自上次标签以来的提交并按受影响的技能/模块分组：

1. **每个提交识别变更文件**
2. **按技能/模块分组**：
   - `skills/<skill-name>/*` → 在该技能下分组
   - 根文件（CLAUDE.md 等）→ 分组为 "项目"
   - 一个提交中包含多个技能 → 分成多个组
3. **针对每个组**，识别需要的 README 更新

**示例分组**：
```
baoyu-cover-image:
  - feat: 添加新样式选项
  - fix: 处理透明背景
  → README 更新：选项表

baoyu-comic:
  - refactor: 改进面板布局算法
  → 无需 README 更新

项目:
  - docs: 更新 CLAUDE.md 架构部分
```

### 第 6 步：分别提交每个技能/模块

针对每个技能/模块组（按变更顺序）：

1. **检查是否需要 README 更新**：
   - 扫描 `README*.md` 以查找提及此技能/模块
   - 验证选项/标志是否正确记录
   - 如果语法变更，更新使用示例
   - 如果行为变更，更新功能描述

2. **暂存并提交**：
   ```bash
   git add skills/<skill-name>/*
   git add README.md README.zh.md  # 如果为此技能更新
   git commit -m "<type>(<skill-name>): <有意义的描述>"
   ```

3. **提交信息格式**：
   - 使用常规提交格式：`<type>(<范围>): <描述>`
   - `<type>`：feat、fix、refactor、docs、perf 等
   - `<范围>`：技能名称或 "项目"
   - `<描述>`：变更的清晰、有意义的描述

**示例提交**：
```bash
git commit -m "feat(baoyu-cover-image): 添加水彩和极简风格"
git commit -m "fix(baoyu-comic): 改进长对话的面板布局"
git commit -m "docs(project): 更新架构文档"
```

**常见的 README 更新需求**：
| 变更类型 | 要检查的 README 部分 |
|----------|----------------------|
| 新选项/标志 | 选项表、使用示例 |
| 重命名的选项 | 选项表、使用示例 |
| 新功能 | 功能描述、示例 |
| 破坏性变更 | 迁移说明、弃用警告 |
| 内部结构重构 | 架构部分（如果暴露给用户） |

### 第 7 步：生成变更日志并更新版本

1. **生成多语言变更日志**（如第 4 步所述）
2. **更新版本文件**：
   - 读取版本文件（JSON/TOML/文本）
   - 更新版本号
   - 回写（保留格式）
3. **创建发布笔记文件**：
   - 优先使用 `CHANGELOG.md` 中的新版本部分
   - 如果没有英语/默认变更日志，则使用第一个检测到的变更日志
   - 仅提取确切的 `## {VERSION} - {YYYY-MM-DD}` 部分，直到下一个 `##`
   - 当需要时，匹配纯文本版本和带标签的标题，例如 `1.2.3` 和 `v1.2.3`
   - 将破坏性变更保持在顶部；如果需要，在其余部分之前添加简短的高亮
   - 将笔记写入 UTF-8 临时文件，并重用于注释标签消息、GitHub Releases 和 `publish_artifact`
   - 在正常模式下，如果找不到笔记，则停止而不是创建空的标签或 GitHub Releases

**不同文件类型的版本路径**：

| 文件 | 路径 |
|------|------|
| package.json | `$.version` |
| pyproject.toml | `project.version` |
| Cargo.toml | `package.version` |
| marketplace.json | `$.metadata.version` |
| VERSION / version.txt | 直接内容 |

### 第 8 步：用户确认

在创建发布提交之前，询问用户确认：

**使用 `AskUserQuestion` 提问三个问题**：

1. **版本号递增**（单选）：
   - 显示基于第 3 步分析的推荐版本
   - 选项：推荐（带标签）、其他 semver 选项
   - 示例：`1.2.3 → 1.3.0 (推荐)`，`1.2.3 → 1.2.4`，`1.2.3 → 2.0.0`

2. **推送到远程**（单选）：
   - 选项："是，提交后推送"，"否，仅本地保留"

3. **发布 GitHub Release**（单选）：
   - 仅在 GitHub 发布支持可用时提供
   - 当用户也选择了推送时，默认为 "是，推送后创建"
   - 如果用户保留本地发布，则不要创建或编辑 GitHub Release

**确认前的输出示例**：
```
已创建提交：
  1. feat(baoyu-cover-image): 添加水彩和极简风格
  2. fix(baoyu-comic): 改进长对话的面板布局
  3. docs(project): 更新架构文档

变更日志预览（en）：
  ## 1.3.0 - 2026-01-22
  ### 新功能
  - 为 cover-image 添加水彩和极简风格
  ### 修复
  - 改进 comic 长对话的面板布局

发布笔记来源：CHANGELOG.md#1.3.0
准备创建发布提交、注释标签和 GitHub Release。
```

### 第 9 步：创建发布提交和注释标签

用户确认后：

1. **暂存版本和变更日志文件**：
   ```bash
   git add <version-file>
   git add CHANGELOG*.md
   ```

2. **创建发布提交**：
   ```bash
   git commit -m "chore: 发布 v{VERSION}"
   ```

3. **创建注释标签**：
   ```bash
   git tag -a v{VERSION} -F <release-notes-file>
   ```
   如果 `.releaserc.yml` 设置 `tag.sign: true`，则使用 `git tag -s` 和相同的笔记文件。

4. **如果用户确认**（第 8 步）：
   ```bash
   git push origin main
   git push origin v{VERSION}
   ```

**注意**：不要添加 Co-Authored-By 行。这是一个发布提交，不是代码贡献。

### 第 10 步：发布发布工件和 GitHub Release

项目工件发布和 GitHub Releases 是独立的输出：

1. **项目工件**：
   - 如果 `release.hooks.publish_artifact` 存在，则针对每个准备好的目标运行一次
   - 传递与标签和 GitHub Release 使用的相同 `{release_notes_file}`
   - 在干运行模式下，传递 `{dry_run}=true` 并报告将要发布的内容

2. **GitHub Release**：
   - 仅在用户确认远程发布且 GitHub 支持可用时运行
   - 确保标签在远程存在后再创建发布
   - 使用提取的笔记创建或更新：
     ```bash
     if gh release view v{VERSION} >/dev/null 2>&1; then
       gh release edit v{VERSION} --title "v{VERSION}" --notes-file <release-notes-file>
     else
       gh release create v{VERSION} --title "v{VERSION}" --notes-file <release-notes-file> --verify-tag
     fi
     ```
   - 永远不要将多行发布笔记内联到 shell 命令中

**发布后输出**：
```
已创建发布 v1.3.0。

提交：
  1. feat(baoyu-cover-image): 添加水彩和极简风格
  2. fix(baoyu-comic): 改进长对话的面板布局
  3. docs(project): 更新架构文档
  4. chore: 发布 v1.3.0

标签：v1.3.0
标签类型：注释
GitHub Release：已发布  # 或 "跳过/本地仅"
状态：已推送到 origin  # 或 "本地仅 - 准备好运行 git push"
```

## 回填现有 GitHub Releases

在用户要求回填历史发布或传递 `--backfill-releases` 时使用此模式。

1. 不要递增版本、编辑变更日志或创建发布提交。
2. 列出按版本顺序存在的标签并检测缺失的发布：
   ```bash
   git tag --sort=v:refname
   gh release view <tag>
   ```
3. 对于没有 GitHub Release 的每个标签：
   - 通过剥离配置的标签前缀来规范化变更日志查找，例如 `v1.2.3` -> `1.2.3`
   - 从 `CHANGELOG.md` 提取匹配的部分；如果没有匹配的变更日志文件，则回退
   - 如果没有匹配的变更日志部分，则跳过或询问是否发布
   - 使用以下命令创建发布：
     ```bash
     gh release create <tag> --title "<tag>" --notes-file <release-notes-file> --verify-tag
     ```
4. 使用 `git cat-file -t <tag>` 检测轻量级标签（`commit` 表示轻量级，`tag` 表示注释）。
5. 默认情况下不要重写公共轻量级标签。将现有远程标签转换为注释标签需要显式用户确认，因为它会重写已发布的引用。

## 配置 (.releaserc.yml)

项目根目录中的可选配置文件以覆盖默认值：

```yaml
# .releaserc.yml - 可选配置

# 版本文件（如果未指定，则自动检测）
version:
  file: package.json
  path: $.version  # JSONPath 用于 JSON，点路径用于 TOML

# 变更日志文件（如果未指定，则自动检测）
changelog:
  files:
    - path: CHANGELOG.md
      lang: en
    - path: CHANGELOG.zh.md
      lang: zh
    - path: CHANGELOG.ja.md
      lang: ja

  # 节点映射（常规提交类型 → 变更日志节）
  # 使用 null 跳过变更日志中的类型
  sections:
    feat: Features
    fix: Fixes
    docs: Documentation
    refactor: Refactor
    perf: Performance
    test: Tests
    chore: null

# 提交信息格式
commit:
  message: "chore: release v{version}"

# 标签格式
tag:
  prefix: v  # 结果为 v1.0.0
  sign: false

# 额外文件包含在发布提交中
include:
  - README.md
  - package.json
```

## 干运行模式

当指定 `--dry-run` 时：

```
=== 干运行模式 ===

检测到项目：
  版本文件：package.json (1.2.3)
  变更日志：CHANGELOG.md (en), CHANGELOG.zh.md (zh)

上次标签：v1.2.3
建议版本：v1.3.0

按技能/模块分组的变更：
  baoyu-cover-image:
    - feat: 添加水彩风格
    - feat: 添加极简风格
    → 提交：feat(baoyu-cover-image): 添加水彩和极简风格
    → README 更新：选项表

  baoyu-comic:
    - fix: 长对话的面板布局
    → 提交：fix(baoyu-comic): 改进长对话的面板布局
    → 无需 README 更新

变更日志预览（en）：
  ## 1.3.0 - 2026-01-22
  ### 新功能
  - 为 cover-image 添加水彩和极简风格
  ### 修复
  - 改进 comic 长对话的面板布局

变更日志预览（zh）：
  ## 1.3.0 - 2026-01-22
  ### 新功能
  - 为 cover-image 添加水彩和极简风格
  ### 修复
  - 改进 comic 长对话的面板布局

要创建的提交：
  1. feat(baoyu-cover-image): 添加水彩和极简风格
  2. fix(baoyu-comic): 改进长对话的面板布局
  3. chore: 发布 v1.3.0

未进行任何更改。运行时不要指定 --dry-run 以执行。
```

## 示例用法

```
/release-skills              # 自动检测版本号递增
/release-skills --dry-run    # 仅预览
/release-skills --minor      # 强制次版本号递增
/release-skills --patch      # 强制修订号递增
/release-skills --major      # 强制主版本号递增（需确认）
/release-skills --backfill-releases  # 为现有标签创建缺失的 GitHub Releases
```

## 使用场景

在用户请求以下内容时触发此技能：
- "发布", "发布", "创建发布", "新版本", "新版本"
- "递增版本", "更新版本", "更新版本"
- "准备发布"
- "发布笔记", "GitHub Release", "回填 Release"
- "推送到远程"（如有未提交的变更）

**重要**：如果用户说 "直接 push" 或 "直接 push" 且有未提交的变更，仍然首先执行上述所有步骤。
