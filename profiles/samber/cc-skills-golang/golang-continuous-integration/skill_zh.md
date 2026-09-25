**角色设定：** 你是一名 Go DevOps 工程师。你将 CI 视为质量门禁——每个流水线决策都会根据构建速度、信号可靠性和安全态势进行权衡。

**模式：**

- **设置**——首次为项目添加 CI：从快速参考表开始，然后按以下顺序生成工作流：测试 → 代码风格检查 → 安全扫描 → 发布。优先为每个 GitHub Action 使用最新的稳定主版本。
- **改进**——审计或扩展现有流水线：首先阅读当前的工作流文件，对照快速参考表识别差距，然后提出有针对性的补充建议，避免重复现有步骤。

**依赖项：**

- goreleaser: `go install github.com/goreleaser/goreleaser/v2@latest`
- gh: `brew install gh`

# Go 持续集成

使用 GitHub Actions 为 Go 项目设置生产级 CI/CD 流水线。

## Action 版本

以下示例中的版本是参考版本，可能已经过时。GitHub Actions 经常发布新版本——每个 Action 的当前主版本（`actions/checkout`、`actions/setup-go`、`golangci/golangci-lint-action`、`codecov/codecov-action`、`goreleaser/goreleaser-action` 等）可能与此处显示的版本不同。

## 快速参考

| 阶段         | 工具                        | 目的                       |
| ------------ | --------------------------- | ----------------------------- |
| **测试**      | `go test -race`             | 单元测试 + 竞态检测         |
| **覆盖率**  | `codecov/codecov-action`    | 覆盖率报告            |
| **代码风格检查** | `golangci-lint`             | 全面代码风格检查         |
| **静态分析** | `go vet`                    | 内置静态分析      |
| **SAST**      | `gosec`、`CodeQL`、`Bearer` | 安全静态分析      |
| **漏洞扫描** | `govulncheck`               | 已知漏洞检测            |
| **Docker**    | `docker/build-push-action`  | 多平台镜像构建   |
| **依赖项**    | Dependabot / Renovate       | 自动化依赖项更新  |
| **发布**   | GoReleaser                  | 自动化二进制发布     |
| **AI 代码审查** | Claude Code / Copilot       | AI 驱动的 PR 代码审查          |

---

## 测试

`.github/workflows/test.yml` — 查看 [test.yml](./assets/test.yml)

根据 `go.mod` 调整 Go 版本矩阵：

```
go 1.23   → matrix: ["1.23", "1.24", "1.25", "1.26", "1.27", "stable"]
go 1.24   → matrix: ["1.24", "1.25", "1.26", "1.27", "stable"]
go 1.25   → matrix: ["1.25", "1.26", "1.27", "stable"]
go 1.26   → matrix: ["1.26", "1.27", "stable"]
go 1.27   → matrix: ["1.27", "stable"]
```

使用 `fail-fast: false`，以便一个 Go 版本失败不会取消其他版本。

Go 1.27 将 Darwin 的最低要求提高到 macOS 13（Ventura）。`macos-latest`/`macos-14`+ 运行器不受影响；如果项目仍然需要，则仅固定较旧的 `macos-12` 运行器，并注意它现在无法使用 Go 1.27 工具链构建。

测试标志：

- `-race`: CI 必须使用 `-race` 标志运行测试（捕获数据竞争——Go 中的未定义行为）
- `-shuffle=on`: 随机化测试顺序以捕获测试之间的依赖关系
- `-coverprofile`: 生成覆盖率数据
- `git diff --exit-code`: 如果 `go mod tidy` 改变了任何内容，则失败

### 覆盖率配置

CI 应强制执行代码覆盖率阈值。在仓库根目录的 `codecov.yml` 中配置阈值——查看 [codecov.yml](./assets/codecov.yml)

---

## 集成测试

`.github/workflows/integration.yml` — 查看 [integration.yml](./assets/integration.yml)

使用 `-count=1` 禁用测试缓存——缓存的测试结果可能会隐藏不稳定的服务的交互。

---

## 代码风格检查

`golangci-lint` 必须在 CI 中对每个 PR 运行。`.github/workflows/lint.yml` — 查看 [lint.yml](./assets/lint.yml)

### golangci-lint 配置

在项目根目录创建 `.golangci.yml`。查看 `samber/cc-skills-golang@golang-lint` 技能以获取推荐的配置。

---

## 安全 & SAST

`.github/workflows/security.yml` — 查看 [security.yml](./assets/security.yml)

CI 必须运行 `govulncheck`——它仅报告您的项目实际调用的代码路径中的漏洞，而不是通用的 CVE 扫描器。

- CodeQL 结果显示在仓库的“安全”选项卡中。
- Bearer 在检测敏感数据流问题方面表现良好。

### CodeQL 配置

创建 `.github/codeql/codeql-config.yml` 以使用扩展的安全查询套件——查看 [codeql-config.yml](./assets/codeql-config.yml)

可用的查询套件：

- **default**: 标准安全查询
- **security-extended**: 精度略低的额外安全查询
- **security-and-quality**: 安全查询加上可维护性和可靠性检查

### 容器镜像扫描

如果项目生成 Docker 镜像，Docker 工作流中包含 Trivy 容器扫描——查看 [docker.yml](./assets/docker.yml)

---

## 依赖项管理

### Dependabot

`.github/dependabot.yml` — 查看 [dependabot.yml](./assets/dependabot.yml)

次要/补丁更新被分组到一个 PR 中。主要更新会获得单独的 PR，因为它们可能有破坏性变更。

#### Dependabot 自动合并

`.github/workflows/dependabot-auto-merge.yml` — 查看 [dependabot-auto-merge.yml](./assets/dependabot-auto-merge.yml)

> **安全警告：** 此工作流需要 `contents: write` 和 `pull-requests: write`——这些是提升权限，允许合并 PR 并修改仓库内容。`if: github.actor == 'dependabot[bot]'` 防护措施仅限制执行为 Dependabot。不要移除此防护措施。请注意，`github.actor` 检查并非完全防欺骗——**分支保护规则才是真正的安全网**。确保配置了分支保护（查看 [仓库安全设置](#repository-security-settings)），要求状态检查和必需的批准，以便自动合并只有在所有检查通过后才能成功，无论谁触发了工作流。

### Renovate（替代方案）

Renovate 是一个更成熟且可配置的 Dependabot 替代方案。它原生支持自动合并、分组、计划、正则表达式管理器和多模块仓库感知更新。如果 Dependabot 感觉过于受限，Renovate 是首选方案。

安装 [Renovate GitHub 应用](https://github.com/apps/renovate)，然后在仓库根目录创建 `renovate.json`——查看 [renovate.json](./assets/renovate.json)

与 Dependabot 相比的关键优势：

- **`gomodTidy`**: 更新后自动运行 `go mod tidy`
- **原生自动合并**: 无需单独的工作流
- **更好的分组**: 更灵活的 PR 分组规则
- **正则表达式管理器**: 可以更新 Dockerfile、Makefile 等中的版本
- **多模块仓库支持**: 处理 Go 工作空间和多模块仓库

---

## 发布自动化

GoReleaser 自动化二进制构建、校验和和 GitHub 发布。配置因项目类型而异。

### 发布工作流

`.github/workflows/release.yml` — 查看 [release.yml](./assets/release.yml)

> **安全警告：** 此工作流需要 `contents: write` 以创建 GitHub 发布。它仅限于标签推送（`tags: ["v*"]`），因此不能由 PR 或分支推送触发。只有具有推送权限的用户才能创建标签。

### GoReleaser 用于 CLI/程序

程序需要跨平台二进制文件、存档，以及可选的 Docker 镜像。

`.goreleaser.yml` — 查看 [goreleaser-cli.yml](./assets/goreleaser-cli.yml)

### GoReleaser 用于库

库不会生成二进制文件——它们只需要一个带有变更日志的 GitHub 发布。使用跳过构建的最小配置。

`.goreleaser.yml` — 查看 [goreleaser-lib.yml](./assets/goreleaser-lib.yml)

对于库，您甚至可能不需要 GoReleaser——通过 UI 或 `gh release create` 创建的简单 GitHub 发布通常就足够了。

### GoReleaser 用于多模块仓库 / 多二进制文件

当仓库包含多个命令（例如，`cmd/api/`、`cmd/worker/`）。

`.goreleaser.yml` — 查看 [goreleaser-monorepo.yml](./assets/goreleaser-monorepo.yml)

### Docker 构建 & 推送

对于生成 Docker 镜像的项目。此工作流构建多平台镜像，生成 SBOM 和来源证明，推送到 GitHub 容器注册表 (GHCR) 和 Docker Hub，并包含 Trivy 容器扫描。

`.github/workflows/docker.yml` — 查看 [docker.yml](./assets/docker.yml)

> **安全警告：** 权限按工作流范围划分：`container-scan` 工作流仅获得 `contents: read` + `security-events: write`，而 `docker` 工作流获得 `packages: write`（用于推送到 GHCR）和 `attestations: write` + `id-token: write`（用于来源/SBOM 签名）。这确保扫描工作流即使被攻破也无法推送镜像。在 PR 上将 `push` 标志设置为 `false`，以便未经信任的代码无法发布镜像。`DOCKERHUB_USERNAME` 和 `DOCKERHUB_TOKEN` 密钥必须在仓库密钥设置中配置——切勿硬编码凭证。

关键细节：

- **QEMU + Buildx**: 对于多平台构建 (`linux/amd64,linux/arm64`) 所需。移除不需要的平台。
- **`push: false` 在 PR 上**: 构建镜像但从未在 PR 上推送——这验证 Dockerfile 而不会发布未经信任的代码。
- **元数据操作**: 自动生成 semver 标签 (`v1.2.3` → `1.2.3`、`1.2`、`1`)、分支标签 (`main`) 和 SHA 标签。
- **来源 + SBOM**: `provenance: mode=max` 和 `sbom: true` 生成供应链证明。这些需要 `attestations: write` 和 `id-token: write` 权限。
- **双注册表**: 推送到 GHCR（使用 `GITHUB_TOKEN`，无需额外密钥）和 Docker Hub（需要 `DOCKERHUB_USERNAME` + `DOCKERHUB_TOKEN` 密钥）。如果不需要，请移除 Docker Hub 登录和镜像行。
- **Trivy**: 扫描构建的镜像中的 CRITICAL 和 HIGH 漏洞，并将结果上传到“安全”选项卡。
- 调整镜像名称和注册表以匹配您的项目。对于仅 GHCR，请移除 Docker Hub 登录步骤，并从 `images:` 中移除 `docker.io/` 行。

---

## 仓库安全设置

仓库安全设置（分支保护、工作流权限、密钥、环境）构成了 CI 流水线的安全基础——这些在 [repo-security.md](./references/repo-security.md) 中有记录。

---

## AI 驱动的代码审查

将 AI 代理作为 PR 审查者添加到传统静态分析中。当加载此技能插件时，代理会根据审查区域应用相关的 Go 技能——捕获架构漂移、逻辑错误、缺失的错误上下文和并发风险，这些是代码风格检查器无法检测到的。

> **成本说明：** AI 审查代理按 PR 并行运行。为控制成本，请移除不需要的工作，或将 PR 触发过滤器设置为仅特定分支。

以下每个子部分都是一个针对特定审查者的生成工件——链接的资产文件在 CI 运行器上运行，而不是开发人员的本地工具，因此其工具名称和权限标志是故意字面的，而不是能力描述。

### Claude Code

`.github/workflows/ai-review.yml` — 查看 [claude-code-review.yml](./assets/claude-code-review.yml)

工作流运行并行作业，每个作业针对一组审查区域和优先级级别：

| 工作流 | 区域 | 优先级 |
| --- | --- | --- |
| `quality` | 代码风格、命名、文档、设计模式 | 建议优先 |
| `correctness` | 错误处理、代码安全、并发 | 阻塞优先 |
| `security` | 安全、依赖项 | 阻塞优先 |
| `quality-depth` | 测试、性能、可观察性、现代化 | 混合 |

根据项目可能相关的附加技能：`golang-cli`、`golang-context`、`golang-data-structures`、`golang-database`、`golang-dependency-injection` 或任何库特定技能。

Claude Code GitHub 应用集成通过 `/install-github-app` 命令配置，该命令设置所需的 API 密钥。

### GitHub Copilot

将技能复制到您的仓库，然后将 [copilot-review-instructions.md](./assets/copilot-review-instructions.md) 追加到 `.github/copilot-instructions.md`：

```bash
npx skills add https://github.com/samber/cc-skills-golang --agent github-copilot --skill '*' -y --copy
ln -s .agents .copilot
```

---

## 常见错误

| 错误 | 修复 |
| --- | --- |
| CI 测试中缺少 `-race` | 始终使用 `go test -race` |
| 没有 `-shuffle=on` | 随机化测试顺序以捕获测试之间的依赖关系 |
| 缓存集成测试结果 | 使用 `-count=1` 禁用缓存 |
| `go mod tidy` 未检查 | 添加 `go mod tidy && git diff --exit-code` 步骤 |
| 缺少 `fail-fast: false` | 一个 Go 版本失败不应取消其他作业 |
| 未固定 Action 版本 | GitHub Actions 必须使用固定主版本（例如 `@vN`，而不是 `@master`） |
| 没有 `permissions` 块 | 按工作流遵循最小权限 |
| 忽略 govulncheck 查找结果 | 修复或提供理由抑制 |
| CI 中没有 AI 审查 | 添加 Claude Code 或 Copilot 审查——捕获静态分析遗漏的逻辑、安全和架构问题 |

## 相关技能

查看 `samber/cc-skills-golang@golang-lint`、`samber/cc-skills-golang@golang-security`、`samber/cc-skills-golang@golang-testing`、`samber/cc-skills-golang@golang-dependency-management`、`samber/cc-skills-golang@golang-modernize` 技能。
