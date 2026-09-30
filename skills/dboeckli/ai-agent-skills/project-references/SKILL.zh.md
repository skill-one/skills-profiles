---
name: project-references
description: 从你本地在 `~/projects/referenzen/` 下检出的 GitHub 仓库中查找约定、模式以及具体实现。当你在代码库家族中不确定如何实现某项功能时，随时使用这项技能——例如 Helm 图结构、Kubernetes 配置清单、框架配置模式、Docker Compose 约定、CI/CD 管道设置，或任何其他重复出现的架构决策。在猜测约定之前，应主动调用此功能；在采用模式时，务必引用源项目及路径。此外，当用户要求检出、更新或搜索参考仓库，或跨仓库生成 GitHub Actions 触发器（push、pull_request、schedule/cron）的概览/报告时，也请使用此功能。
---

---

# 项目参考

此技能管理您自己的 GitHub 仓库的本地镜像，位于 `~/projects/referenzen/` 下，并允许您在不猜测或盲目查看所有仓库的情况下查找约定和实现模式。

对参考项目本身的操作都是**只读**的。只有 `git clone` 和 `git pull` 会写入该目录——从不进行编辑。

---

## 使用说明

### 第 1 步：检查相关仓库是否已克隆

```bash
ls ~/projects/referenzen/
```

如果所需的仓库缺失，请先运行 `scripts/clone-or-update.sh owner/repo` 来克隆它。

### 第 2 步：询问用户哪个参考项目最相关

不要盲目扫描所有仓库——这会填充上下文。询问：“您的哪些兄弟项目使用了这种模式？”或者列出可用仓库并让用户选择。

### 第 3 步：有针对性地搜索——先文件，再 grep

使用 `find` 通过名称定位文件，然后使用 `cat` 或 `grep` 仅读取相关部分。对于搜索命令和模式，请参考 `references/search-patterns.md`。

### 第 4 步：采用模式时引用来源

应用模式前，始终说明该模式来自哪个项目和文件路径：

> 模式来自 `your-service` → `helm-charts/Chart.yaml` 第 4 行

### 第 5 步：仅在明确要求时同步

仅在用户说“同步所有”或“更新所有参考”时运行 `scripts/sync-all.sh`。对于单个仓库，优先使用 `scripts/clone-or-update.sh`。

---

## 示例

### 示例 1：查找 Helm 图表约定

用户说：“这个项目的 Helm 图表应该如何结构化？”

操作：

1. 运行 `ls ~/projects/referenzen/` 查看可用仓库
2. 询问：“我应该使用哪个兄弟项目作为参考？”——用户说 `your-service`
3. 运行 `find ~/projects/referenzen/your-service -name "Chart.yaml"` 定位它
4. 读取文件，记下结构（apiVersion、dependencies、版本模式）
5. 应用相同结构；引用：“来自 `your-service/helm-charts/Chart.yaml`”

结果：与兄弟项目一致的 Helm 图表，并注明了可追溯的来源。

### 示例 2：检出新的参考仓库

用户说：“将我的 other-service 项目作为参考进行克隆”

操作：

1. 运行 `bash scripts/clone-or-update.sh owner/other-service`
2. 输出流，以便用户看到 CLONE/PULL/SKIP 进度
3. 使用 `ls ~/projects/referenzen/other-service/` 确认

结果：本地可用仓库用于模式查找；未进行编辑。

### 示例 3：查找配置模式

用户说：“如何像其他项目一样配置数据库池？”

操作：

1. `ls ~/projects/referenzen/` — 选择一个相关的兄弟项目
2. `grep -rn "database.pool" ~/projects/referenzen/your-service/src/main/resources/`
3. 读取相关配置部分
4. 引用：“来自 `your-service/src/main/resources/application.yaml` 第 42 行”

结果：从可信的兄弟项目中获取确切的配置，而不是猜测。

### 示例 4：GitHub Actions 触发的概述

用户说：“我的项目何时运行 GitHub Actions——推送、PR 或计划？”

操作：

1. 运行 `bash scripts/list-workflow-triggers.sh`（添加 `--glob` 以缩小到单个
   管道，`--root` 用于不同的检出目录）
2. 展示排序后的概述（星期/时间、人类可读格式加上原始 cron）以及事件
   仅工作流
3. 指引用户查看生成的报告 `target/workflow-triggers.md`

结果：跨所有参考仓库的触发器概述（按时间排序）加上 Markdown 报告，而无需打开每个工作流文件。

---

## 仓库来源

支持两种来源——当存在时优先使用手动列表：

1. **手动列表** (`~/claude-shared/projekte.txt`)：每行一个 GitHub 仓库 URL 或
   `owner/name` 缩写，忽略空行和 `#` 注释。
2. **自动发现**：当文件不存在或用户明确要求完整同步时，运行
   `gh repo list --limit 200 --json nameWithOwner`

---

## 脚本

两个现成的脚本位于 `scripts/` 中——用它们代替编写内联 Bash。两者都接受 `REFERENZEN_DIR` 作为环境变量覆盖（默认：
`~/projects/referenzen`）。

### `scripts/clone-or-update.sh <owner/repo>`

克隆单个仓库或本地存在时拉取。当本地有更改时拒绝拉取（退出码 2）——从不暂存或重置。

```bash
bash scripts/clone-or-update.sh owner/your-repo
```

退出码：`0` = 成功，`2` = 跳过（本地更改），`3` = 克隆/拉取失败。

### `scripts/sync-all.sh [--list <file>] [--limit <n>]`

迭代所有仓库并调用每个仓库的克隆或更新逻辑。优先使用 `~/claude-shared/projekte.txt`
作为来源；当文件不存在时回退到 `gh repo list`。在末尾打印摘要行。

```bash
# 同步所有（自动检测来源）
bash scripts/sync-all.sh

# 使用特定列表文件
bash scripts/sync-all.sh --list ~/claude-shared/projekte.txt

# 限制 gh repo list 到 50 个仓库
bash scripts/sync-all.sh --limit 50
```

**不要**盲目运行 sync-all——仅在用户明确说“同步所有”或“更新所有参考”时使用。
对于单个仓库，优先使用 `clone-or-update.sh`。

### `scripts/list-workflow-triggers.sh [--root <dir>] [--glob <pattern>] [--out <file>] [--no-report]`

扫描每个仓库检出目录中的 `.github/workflows/*.yml` 和 `*.yaml`，从 `on:` 块中提取
触发器（`push`、`pull_request`、`schedule`、`workflow_dispatch`、`release`、…）以及
任何 `cron:` 表达式，打印概述并写入 Markdown 报告。计划工作流按**星期/时间**排序并显示
**人类可读的运行时间**（例如 `Monday 02:05`），旁边是**原始 cron 表达式**；
没有计划的工作流将列在单独的事件部分。只读，无需网络访问。

- `--root <dir>` — 包含仓库检出目录的目录。默认：
  `$REFERENZEN_DIR` 或 `~/projects/referenzen`。
- `--glob <pattern>` — 可选文件名过滤器，例如 `maven-build.yml`。
  默认：所有工作流。
- `--out <file>` — Markdown 报告路径。默认：
  `target/workflow-triggers.md`（相对于当前项目目录，如果缺失则创建）。
- `--no-report` — 仅输出到 stdout，跳过报告文件。

```bash
# 概述 + 报告所有参考仓库
bash scripts/list-workflow-triggers.sh

# 仅 maven-build.yml，自定义报告位置
bash scripts/list-workflow-triggers.sh --glob 'maven-build.yml' --out target/maven-triggers.md

# 不同的检出根（例如 Windows 挂载）
bash scripts/list-workflow-triggers.sh --root /mnt/c/Development/projects/all-git-repos
```

---

## 工作流

### 1. 检出或更新仓库

运行适当的脚本并流式输出，以便用户看到每个 CLONE / PULL / SKIP 操作。

### 2. 在参考项目中搜索

将搜索范围限定为用户实际需要的部分。优先使用有针对性的查找而不是广泛的递归 grep。
对于现成的搜索命令和引用模式，请参考 `references/search-patterns.md`。

### 3. 发现可用的参考项目

```bash
ls ~/projects/referenzen/
```

如果 `~/claude-shared/projekte.txt` 存在，请显示其内容以解释哪些仓库被跟踪，哪些是本地存在的。

### 4. GitHub Actions 触发的概述

运行 `scripts/list-workflow-triggers.sh` 获取跨仓库的每个工作流的 `on:` 触发器和 `cron:` 条目概述。
它还将报告写入 `target/workflow-triggers.md`。使用 `--glob` 聚焦于单个管道（例如 `maven-build.yml`），
并使用 `--root` 指定不同的检出目录。

---

## 何时主动建议此技能

在以下情况下建议查找参考项目：

- 用户询问如何结构化某事物，且答案可能因项目约定而异（Helm 图表布局、Flyway 迁移命名、Dockerfile 模式、Maven 插件排序等）
- 存在多种合理方法，且与兄弟项目的一致性很重要
- 用户说“像其他项目一样”或“和之前一样”但未指定项目

询问用户哪个参考项目最相关，而不是扫描所有项目——扫描在上下文中成本很高。

---

## 安全规则

- 不要编辑、暂存、提交或删除 `~/projects/referenzen/` 中的文件。
- 如果 `git pull` 因本地更改而失败，请明确报告冲突并停止——不要暂存、重置或强制。
- 不要在响应中暴露包含密钥的仓库内容（`.env`、凭证文件），仅读取和引用结构。
