# CI/CD 安全扫描器

这项技能将模型转换为工作流-YAML扫描器。读取文件，遍历检测规则，以严重程度和具体重写建议的形式报告发现。无需安装工具，无需运行命令——分析就是模型读取YAML文件。

规则编码了来自Astral、OpenSSF、GitHub Security Lab、Chainguard以及zizmor审计集的当前共识。目标是标记出与这些工具会标记的相同模式，而无需实际运行它们。

## 心智模型

每个工作流都位于一个2x2的矩阵上：**特权 vs 非特权**交叉**可信 vs 不可信代码**。妥协只发生在**特权工作流运行不可信代码**这一格。以下规则是检测工作流何时进入该格的方法。

- **特权** = 拥有密钥、写入权限，或生成敏感工件（发布、部署、评论、标签）。
- **不可信代码** = 任何fork PR作者可以影响的任何内容：PR源代码、PR标题、PR正文、提交信息、分支名称、工作流读取的文件、缓存的文件、由另一个不可信工作流生成的工件。

当不确定某个值是否可信时，将其视为不可信。误报的成本是代码审查评论；漏报的成本是供应链妥协。

## 扫描流程

对于用户提供的每个工作流文件，按顺序执行以下步骤。每个步骤对应一类攻击。

### 第1步：危险触发器

查看`on:`块。立即标记：

- **`pull_request_target`** — P0，除非有明确理由。使用密钥和写入权限运行，可被fork PR触发。标准的pwn-request向量。即使没有检出head，攻击者输入也会出现在PR标题、分支名称、提交信息中，并会被插值。
- **`workflow_run`** — P0。与`pull_request_target`的问题相同，但间接，通过一个链式`pull_request`工作流的工件或元数据。
- **`issue_comment`, `issues`, `pull_request_review`, `pull_request_review_comment`** — P1。使用密钥，任何人都可以评论触发。只有当工作流不将用户控制的字段模板插值到shell中时才是安全的。
- **带广泛通配符的`push`**（`branches: ['*']`或无分支过滤器）— P2。攻击者如果成功创建PR，可以通过推送后续分支来触发特权工作流。

对于每个发现：命名触发器，解释为什么在此特定工作流的上下文中它是危险的，并提出重写建议（通常替换为`pull_request`，有时拆分为两个工作流，有时需要使用GitHub App而不是Actions）。

### 第2步：权限

在工作流和作业级别查找`permissions:`块。

- **没有顶层`permissions:`块** — P1。默认的`GITHUB_TOKEN`权限取决于仓库和组织的设置；在较旧的仓库中可能是`write-all`。标记为：在顶部添加`permissions: {}`，按作业授权。
- **任何地方的`permissions: write-all`** — P1。
- **作业级别的`permissions:`授予了作业明显不需要的更多权限** — P2。例如，在只运行测试的作业上使用`contents: write`。建议最小权限。
- **与第1步的危险触发器结合** — 严重程度提升一级。

### 第3步：操作符固定

查看每一行`uses:`。

- **固定到标签**（`uses: actions/checkout@v4`，`@v4.1.1`）— P1。标签是可变的；如果攻击者攻破了操作符仓库，可以强制推送标签。
- **固定到分支**（`uses: actions/checkout@main`）— P0。比标签固定更糟；该分支的任何提交都会立即流入。
- **固定到SHA但没有版本注释** — P3级别的发现。建议使用格式`uses: owner/action@<sha> # v4.1.1`，以便在更新固定时保持审查的可读性。
- **固定到看起来不寻常的SHA**（第三方操作符、可疑所有者、最近创建的仓库）— 标记为手动验证；无法确认冒充者提交状态，但值得注意。

标签/分支固定的重写总是：替换为它们打算使用的完整40字符提交SHA，加上`# vX.Y.Z`注释。

### 第4步：shell注入（模板注入）

对于每个`run:`块，扫描`${{ ... }}`替换。

常量或非攻击者控制值是安全的（例如`${{ matrix.os }}`，`${{ secrets.MY_TOKEN }}`，尽管在某些上下文中这也存在风险）。危险的字段是：

- `github.event.pull_request.title`, `body`, `head.ref`, `head.sha`, `head.label`
- `github.event.issue.title`, `body`
- `github.event.comment.body`, `user.login`
- `github.event.review.body`
- `github.head_ref`
- `github.event.workflow_run.head_branch`, `head_commit.message`
- `github.event.commits.*.message`, `author.name`, `author.email`
- 如果工作流在特权上下文中运行，来自`workflow_dispatch`的任何`inputs.*`
- 任何来自`actions/github-script`、下载的工件或外部API响应的字段

**检测规则**：如果`run:`块在脚本正文中直接包含`${{ github.event.* }}`或`${{ github.head_ref }}`，那就是P0模板注入。修复方法总是：

```yaml
# 易受攻击
- run: echo "分支是 ${{ github.head_ref }}"

# 安全
- env:
    BRANCH: ${{ github.head_ref }}
  run: echo "分支是 $BRANCH"
```

还标记（P1）：

- `echo "VAR=${{ untrusted }}" >> $GITHUB_ENV` — 环境文件注入。攻击者可以通过包含换行符来跳出变量。
- `echo "::set-env name=VAR::${{ untrusted }}"` — 已弃用的工作流命令，问题相同。
- 将不可信文件`cat`到`$GITHUB_ENV`或`$GITHUB_OUTPUT`中的内联脚本。

### 第5步：不可信检出

对于每个`actions/checkout`步骤：

- **`ref: ${{ github.event.pull_request.head.sha }}`**（或`head.ref`）在工作流由`pull_request_target`或`workflow_run`触发时 — P0。这是标准的pwn-request：特权上下文运行fork作者代码。
- **`persist-credentials: true`**（默认）在工作流不需要推送回时 — P2。建议`persist-credentials: false`，除非工作流明确需要嵌入的令牌。

### 第6步：特权上下文中的缓存

对于每个使用`cache:`输入的步骤（最常见的是在`actions/setup-node`、`setup-python`、`setup-go`、`setup-java`或直接`actions/cache`上）：

- **在发布或发布工作流中缓存** — P0。来自默认分支上的任何其他工作流的缓存中毒可以将恶意构建输入流到发布中。Trivy和TeamPCP攻击都通过这一途径。
- **在处理密钥的工作流中缓存** — P1。
- **缓存键未限定，导致不可信PR工作流与默认分支构建写入相同的键** — P2。

发布工作流的修复方法：完全移除`cache:`，并添加一条评论解释原因（例如`# 不缓存：见 https://github.com/actions/setup-node/issues/1445`）。

### 第7步：工件传播注入

如果工作流从另一个工作流下载工件（`actions/download-artifact`、`dawidd6/action-download-artifact`等）：

- **工件内容未经验证就在`run:`或`$GITHUB_ENV`中使用** — 如果生成工作流在不可信代码上运行（例如来自fork的`pull_request`），P0。攻击者可以将任意内容放入工件中。
- **建议严格验证**：如果工件应该是PR编号，则拒绝任何非数字的内容。如果是结构化文件，则解析并验证模式。

### 第8步：发布特定加固

如果工作流看起来像发布/发布工作流（发布到npm、PyPI、crates.io、Docker注册表；创建GitHub发布；推送标签）：

- **发布作业未声明`environment:`** — P1。发布凭证应限定于部署环境，而不是仓库/组织密钥。
- **使用长生命周期的注册表令牌**（`secrets.NPM_TOKEN`、`secrets.PYPI_TOKEN`）而不是OIDC/可信发布 — P2。建议使用相关注册表的OIDC路径。
- **未生成证明**（`actions/attest-build-provenance`、npm的`--provenance`、PyPI的PEP 740）— P3加固建议，不是漏洞。
- **发布路径中的缓存** — P0，见第6步。

### 第9步：自托管运行器

如果工作流使用`runs-on:`，并且不是GitHub托管的运行器（`ubuntu-*`、`windows-*`、`macos-*`）：

- **可被fork PR触发的自托管运行器** — P0。自托管运行器跨作业共享状态，并已导致关键妥协（PyTorch）。标记为手动审查运行器作用域。
- 这超出了默认威胁模型——标记发现并建议用户在GitHub设置中验证运行器限制。

## 发现格式

按严重程度报告每个发现，P0优先。格式如下。按严重程度分组。

```
[P0] 模板注入在 .github/workflows/ci.yml:23
  运行块直接将 github.event.pull_request.title 插值到shell。
  攻击者控制PR标题，可以在工作流上下文中执行任意代码，该上下文可以访问 GITHUB_TOKEN。

  易受攻击：
    - run: echo "标题: ${{ github.event.pull_request.title }}"

  修复：
    - env:
        TITLE: ${{ github.event.pull_request.title }}
      run: echo "标题: $TITLE"
```

如果用户粘贴了原始YAML而没有文件名，则将其称为“工作流”，并在代码片段内使用行号。

## 严重程度等级

- **P0** — 现在可利用，无需链。Fork PR作者或任意GitHub用户可以妥协密钥、仓库内容或发布。阻止合并。
- **P1** — 需要一个额外步骤即可利用（例如，需要与其他发现结合，或需要维护者错误）。如果在发布路径上发现，则阻止合并。
- **P2** — 加固差距。直接不可利用，但如果与其他未来漏洞结合，会减少影响范围。在正常审查周期中修复。
- **P3** — 样式或一致性发现。值得修复以提高可读性，没有安全影响。

## 工作流看起来正常时

遍历所有九个步骤后，如果没有任何发现：

1. 明确说明。 "未发现标准规则集中的问题。"
2. 注明未检查的内容：组织级设置（默认令牌权限、规则集强制执行、2FA）、仓库级设置（分支保护、标签保护、不可变发布）、操作符源代码（固定操作符本身在运行时是否安装可变二进制文件）以及依赖项的运行时行为。
3. 建议用户检查`references/checklist.md`下的“每个仓库”和“每个组织”项——这些需要GitHub设置访问权限，而不是工作流YAML。

干净的工作流扫描并不意味着安全的状态。

## 参考文件

- `references/triggers.md` — 每个GitHub Actions触发器的详细表格，每个触发器危险或安全的因素，以及人们使用危险触发器进行常见操作的 безопас 模式。当工作流使用用户特别询问的触发器，或当您想解释触发器为何危险时超出简短摘要之外时，请阅读此文件。
- `references/checklist.md` — 每个工作流/每个仓库/每个组织的平面清单。在用户请求完整审计、扫描多个仓库或按规模分派时很有用。包括分派优先级顺序。
- `references/patterns.md` — 常见的“我想安全地做X”模式。当用户询问如何替换被标记的危险模式，而不仅仅是识别它时，请阅读此文件。

## 这项技能不会做什么

- 它不会安装zizmor、pinact或任何其他东西。扫描就是模型读取YAML并应用这些规则。
- 它不会建议安装工具，除非用户明确询问“我应该运行什么工具”。即使这样，也要直接指出模式——这项技能中的规则就是这些工具编码的审核。
- 它不会用缓解措施掩盖`pull_request_target`发现。如果工作流使用该触发器并且没有被GitHub App保护，就是一个开放的发现。
- 它不会告诉用户一切都很好，而不会命名检查了什么和什么没有检查。默认回答“这是安全的”是“以下是扫描覆盖的内容和发现的内容”。
