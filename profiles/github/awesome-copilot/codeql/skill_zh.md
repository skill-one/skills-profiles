# CodeQL 代码扫描

本技能提供配置和运行 CodeQL 代码扫描的流程指导，包括通过 GitHub Actions 工作流和独立的 CodeQL CLI。

## 使用此技能的场景

当请求涉及以下情况时，请使用此技能：

- 创建或自定义 `codeql.yml` GitHub Actions 工作流
- 在默认设置和高级设置之间选择代码扫描方案
- 配置 CodeQL 语言矩阵、构建模式或查询套件
- 本地运行 CodeQL CLI (`codeql database create`, `database analyze`, `github upload-results`)
- 理解或解释 CodeQL 生成的 SARIF 输出
- 排错 CodeQL 分析失败（构建模式、编译语言、运行器要求）
- 为单体仓库配置 CodeQL 并进行组件级扫描
- 配置依赖缓存、自定义查询包或模型包

## 支持的语言

CodeQL 支持以下语言标识符：

| 语言 | 标识符 | 替代方案 |
|---|---|---|
| C/C++ | `c-cpp` | `c`, `cpp` |
| C# | `csharp` | — |
| Go | `go` | — |
| Java/Kotlin | `java-kotlin` | `java`, `kotlin` |
| JavaScript/TypeScript | `javascript-typescript` | `javascript`, `typescript` |
| Python | `python` | — |
| Ruby | `ruby` | — |
| Rust | `rust` | — |
| Swift | `swift` | — |
| GitHub Actions | `actions` | — |

> 替代标识符与标准标识符等效（例如，`javascript` 不排除 TypeScript 分析）。

## 核心工作流 — GitHub Actions

### 第 1 步：选择设置类型

- **默认设置** — 从仓库设置 → 高级安全 → 代码分析启用。快速入门的最佳选择。大多数语言使用 `none` 构建模式。
- **高级设置** — 创建 `.github/workflows/codeql.yml` 文件，完全控制触发器、构建模式、查询套件和矩阵策略。

要从默认切换到高级：首先禁用默认设置，然后提交工作流文件。

### 第 2 步：配置工作流触发器

定义扫描运行时机：

```yaml
on:
  push:
    branches: [main, protected]
  pull_request:
    branches: [main]
  schedule:
    - cron: '30 6 * * 1'  # 每周一 6:30 UTC 周期性扫描
```

- `push` — 每次推送到指定分支时扫描；结果显示在安全选项卡中
- `pull_request` — 扫描 PR 合并提交；结果作为 PR 检查注释显示
- `schedule` — 默认分支的周期性扫描（cron 必须存在于默认分支上）
- `merge_group` — 如果仓库使用合并队列，则添加

要跳过仅文档 PR 的扫描：

```yaml
on:
  pull_request:
    paths-ignore:
      - '**/*.md'
      - '**/*.txt'
```

> `paths-ignore` 控制工作流是否运行，而不是控制分析哪些文件。

### 第 3 步：配置权限

设置最小权限：

```yaml
permissions:
  security-events: write   # 上传 SARIF 结果所需
  contents: read            # 检出代码所需
  actions: read             # 私有仓库使用 codeql-action 所需
```

### 第 4 步：配置语言矩阵

使用矩阵策略并行分析每种语言：

```yaml
jobs:
  analyze:
    name: 分析 (${{ matrix.language }})
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        include:
          - language: javascript-typescript
            build-mode: none
          - language: python
            build-mode: none
```

对于编译语言，设置适当的 `build-mode`：
- `none` — 无需构建（支持 C/C++、C#、Java、Rust）
- `autobuild` — 自动构建检测
- `manual` — 自定义构建命令（仅高级设置可用）

> 搜索 `references/compiled-languages.md` 获取详细的每语言 autobuild 行为和运行器要求。

### 第 5 步：配置 CodeQL 初始化和分析

```yaml
steps:
  - name: 检出仓库
    uses: actions/checkout@v4

  - name: 初始化 CodeQL
    uses: github/codeql-action/init@v4
    with:
      languages: ${{ matrix.language }}
      build-mode: ${{ matrix.build-mode }}
      queries: security-extended
      dependency-caching: true

  - name: 执行 CodeQL 分析
    uses: github/codeql-action/analyze@v4
    with:
      category: "/language:${{ matrix.language }}"
```

**查询套件选项：**
- `security-extended` — 默认安全查询加额外覆盖
- `security-and-quality` — 安全查询加代码质量查询
- 通过 `packs:` 输入自定义查询包（例如，`codeql/javascript-queries:AlertSuppression.ql`）

**依赖缓存：** 在 `init` 操作中设置 `dependency-caching: true` 以跨运行缓存恢复的依赖。

**分析类别：** 使用 `category` 区分单体仓库中的 SARIF 结果（例如，按语言、按组件）。

### 第 6 步：单体仓库配置

对于包含多个组件的单体仓库，使用 `category` 参数分离 SARIF 结果：

```yaml
category: "/language:${{ matrix.language }}/component:frontend"
```

要限制分析到特定目录，使用 CodeQL 配置文件（`.github/codeql/codeql-config.yml`）：

```yaml
paths:
  - apps/
  - services/
paths-ignore:
  - node_modules/
  - '**/test/**'
```

在工作流中引用它：

```yaml
- uses: github/codeql-action/init@v4
  with:
    config-file: .github/codeql/codeql-config.yml
```

### 第 7 步：手动构建步骤（编译语言）

如果 `autobuild` 失败或需要自定义构建命令：

```yaml
- language: c-cpp
  build-mode: manual
```

然后添加显式构建步骤在 `init` 和 `analyze` 之间：

```yaml
- if: matrix.build-mode == 'manual'
  name: 构建
  run: |
    make bootstrap
    make release
```

## 核心工作流 — CodeQL CLI

### 第 1 步：安装 CodeQL CLI

下载 CodeQL 套件（包含 CLI 和预编译查询）：

```bash
# 从 https://github.com/github/codeql-action/releases 下载
# 解压并添加到 PATH
export PATH="$HOME/codeql:$PATH"

# 验证安装
codeql resolve packs
codeql resolve languages
```

> 始终使用 CodeQL 套件，而不是单独的 CLI 下载。套件确保查询兼容性并提供预编译查询以获得更好的性能。

### 第 2 步：创建 CodeQL 数据库

```bash
# 单语言
codeql database create codeql-db \
  --language=javascript-typescript \
  --source-root=src

# 多语言（集群模式）
codeql database create codeql-dbs \
  --db-cluster \
  --language=java,python \
  --command=./build.sh \
  --source-root=src
```

对于编译语言，通过 `--command` 提供构建命令。

### 第 3 步：分析数据库

```bash
codeql database analyze codeql-db \
  javascript-code-scanning.qls \
  --format=sarif-latest \
  --sarif-category=javascript \
  --output=results.sarif
```

常见查询套件：`<language>-code-scanning.qls`, `<language>-security-extended.qls`, `<language>-security-and-quality.qls`。

### 第 4 步：上传结果到 GitHub

```bash
codeql github upload-results \
  --repository=owner/repo \
  --ref=refs/heads/main \
  --commit=<commit-sha> \
  --sarif=results.sarif
```

需要 `GITHUB_TOKEN` 环境变量具有 `security-events: write` 权限。

### CLI 服务器模式

为避免多次 JVM 初始化，运行多个命令时：

```bash
codeql execute cli-server
```

> 搜索 `references/cli-commands.md` 获取详细的 CLI 命令参考。

## 告警管理

### 严重性级别

告警有两个严重性维度：
- **标准严重性：** `Error`, `Warning`, `Note`
- **安全严重性：** `Critical`, `High`, `Medium`, `Low`（基于 CVSS 分数；显示优先级更高）

### Copilot 自动修复

GitHub Copilot 自动修复会自动为 PR 中的 CodeQL 告警生成修复建议 — 无需 Copilot 订阅。提交前仔细审查建议。

### PR 中的告警分派

- 告警显示为更改行的检查注释
- 默认情况下，`error`/`critical`/`high` 严重性告警会导致检查失败
- 配置合并保护规则集以自定义阈值
- 带有文档理由地忽略误报以保留审计记录

> 搜索 `references/alert-management.md` 获取详细的告警管理指导。

## 自定义查询和包

### 使用自定义查询包

```yaml
- uses: github/codeql-action/init@v4
  with:
    packs: |
      my-org/my-security-queries@1.0.0
      codeql/javascript-queries:AlertSuppression.ql
```

### 创建自定义查询包

使用 CodeQL CLI 创建和发布包：

```bash
# 初始化新包
codeql pack init my-org/my-queries

# 安装依赖
codeql pack install

# 发布到 GitHub Container Registry
codeql pack publish
```

### CodeQL 配置文件

为高级查询和路径配置，创建 `.github/codeql/codeql-config.yml`：

```yaml
paths:
  - apps/
  - services/
paths-ignore:
  - '**/test/**'
  - node_modules/
queries:
  - uses: security-extended
packs:
  javascript-typescript:
    - my-org/my-custom-queries
```

## 代码扫描日志

### 摘要指标

工作流日志包含关键指标：
- **代码库代码行数** — 提取前的基线
- **提取代码行数** — 包括外部库和自动生成文件
- **提取错误/警告** — 提取期间失败或产生警告的文件

### 调试日志

为启用详细诊断：
- **GitHub Actions：** 重新运行工作流并勾选“启用调试日志”
- **CodeQL CLI：** 使用 `--verbosity=progress++` 和 `--logdir=codeql-logs`

## 排错

### 常见问题

| 问题 | 解决方案 |
|---|---|
| 工作流未触发 | 验证 `on:` 触发器与事件匹配；检查 `paths`/`branches` 过滤器；确保目标分支存在工作流 |
| `Resource not accessible` 错误 | 添加 `security-events: write` 和 `contents: read` 权限 |
| Autobuild 失败 | 切换到 `build-mode: manual` 并添加显式构建命令 |
| 未看到源代码 | 验证 `--source-root`、构建命令和语言标识符 |
| C# 编译器失败 | 检查 `/p:EmitCompilerGeneratedFiles=true` 与 `.sqlproj` 或遗留项目冲突 |
| 扫描代码行数少于预期 | 从 `none` 切换到 `autobuild`/`manual`；验证构建是否编译所有源 |
| 无构建模式下的 Kotlin | 禁用并重新启用默认设置以切换到 `autobuild` |
| 每次运行缓存未命中 | 验证 `init` 操作中的 `dependency-caching: true` |
| 磁盘/内存不足 | 使用更大的运行器；通过 `paths` 配置减少分析范围；使用 `build-mode: none` |
| SARIF 上传失败 | 确保令牌具有 `security-events: write`；检查 10 MB 文件大小限制 |
| SARIF 结果超出限制 | 分批上传不同 `--sarif-category`；减少查询范围 |
| 两个 CodeQL 工作流 | 如果使用高级设置，禁用默认设置；或删除旧工作流文件 |
| 分析缓慢 | 启用依赖缓存；使用 `--threads=0`；减少查询套件范围 |

> 搜索 `references/troubleshooting.md` 获取详细的排错解决方案。

### 硬件要求（自托管运行器）

| 代码库大小 | RAM | CPU |
|---|---|---|
| 小 (<100K LOC) | 8 GB+ | 2 核心 |
| 中等 (100K–1M LOC) | 16 GB+ | 4–8 核心 |
| 大 (>1M LOC) | 64 GB+ | 8 核心 |

所有大小：SSD 需 ≥14 GB 可用磁盘空间。

### Action 版本控制

将 CodeQL actions 固定到特定主版本：

```yaml
uses: github/codeql-action/init@v4      # 推荐
uses: github/codeql-action/autobuild@v4
uses: github/codeql-action/analyze@v4
```

为最大安全性，固定到完整提交 SHA 而不是版本标签。

## 参考文件

按需加载以下参考文件获取详细文档：

- `references/workflow-configuration.md` — 完整工作流触发器、运行器和配置选项
  - 搜索模式：`trigger`, `schedule`, `paths-ignore`, `db-location`, `model packs`, `alert severity`, `merge protection`, `concurrency`, `config file`
- `references/cli-commands.md` — 完整 CodeQL CLI 命令参考
  - 搜索模式：`database create`, `database analyze`, `upload-results`, `resolve packs`, `cli-server`, `installation`, `CI integration`
- `references/sarif-output.md` — SARIF v2.1.0 对象模型、上传限制和第三方支持
  - 搜索模式：`sarifLog`, `result`, `location`, `region`, `codeFlow`, `fingerprint`, `suppression`, `upload limits`, `third-party`, `precision`, `security-severity`
- `references/compiled-languages.md` — 每种语言的构建模式和 autobuild 行为
  - 搜索模式：`C/C++`, `C#`, `Java`, `Go`, `Rust`, `Swift`, `autobuild`, `build-mode`, `hardware`, `dependency caching`
- `references/troubleshooting.md` — 全面错误诊断和解决方案
  - 搜索模式：`no source code`, `out of disk`, `out of memory`, `403`, `C# compiler`, `analysis too long`, `fewer lines`, `Kotlin`, `extraction errors`, `debug logging`, `SARIF upload`, `SARIF limits`
- `references/alert-management.md` — 告警严重性、分派、Copilot Autofix 和忽略
  - 搜索模式：`severity`, `security severity`, `CVSS`, `Copilot Autofix`, `dismiss`, `triage`, `PR alerts`, `data flow`, `merge protection`, `REST API`
