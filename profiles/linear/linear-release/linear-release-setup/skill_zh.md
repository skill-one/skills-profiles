# 线性发布设置

[linear-release README](https://github.com/linear/linear-release/blob/main/README.md) 是命令、标志、安装、环境变量、路径过滤和故障排除的权威来源。在生成任何配置之前，请先获取它——这项技能专注于交互式设置工作流和 README 无法为用户做出的管道建模决策。

## 交互式工作流

### 第 1 步：预检查

在生成配置之前，请确认：

1. **在 Linear 中存在发布管道** — 用户必须在 Linear 中首先创建一个发布管道（设置 → 发布）。每个管道都有自己的访问密钥。
2. **检测 CI 平台** — 查找 `.github/workflows/*.yml`（GitHub Actions）、`.gitlab-ci.yml`（GitLab CI）、`.circleci/config.yml`（CircleCI）或其他 CI 配置。
3. **检测默认分支** — 检查 `git symbolic-ref refs/remotes/origin/HEAD` 或 CI 配置。不要假设是 `main`。

### 第 2 步：映射管道，然后询问

首先列出用户独立发布的每个构建——每个构建都将成为自己的 Linear 管道。管道与阶段混淆是最常见的设置错误，因此，每当拆分不明确时，请应用“阶段与管道”部分中的测试。

按顺序询问：

1. **CI 平台** — 如果未自动检测。

2. **你发布什么，以及发布给谁？** 明确提示常见的拆分候选方案：生产与 Beta 或 TestFlight、夜间或狗粮构建、预发布环境、按平台构建（iOS、Android、Web）、单仓库中的按服务构建。对于每个候选方案，应用测试：_这些可以同时持有不同的提交吗？_ 是 → 分离的管道。否（相同的不可变构建通过关卡）→ 一个管道带阶段。

3. **对于每个管道：持续还是计划？**
   - **持续** — 每次部署都完成一个发布。典型用于夜间构建、狗粮和合并时发布 Web 应用。
   - **计划** — 发布会随时间收集更改并通过阶段后再发布。典型用于版本化的移动应用和本地部署。

   **测试：** 团队是否需要在发布前跟踪发布——命名它、查看其中排队的内容或将其通过阶段（代码冻结、QA 等）？
   - 是 → **计划**（发布在发布之前作为进行中的事物存在）。
   - 否 → **持续**（发布在发布时刻创建）。

4. **对于每个计划管道，明确询问：**
   - **分支模型** — 仅 `main`，还是 `main` + 发布分支（`release/*`）？
   - **版本来源** — 日历（`2026.05`）、语义版本（`1.2.0`）或提交 SHA？源自分支名称、CI 变量、文件或 git 标签？
   - **阶段** — 发布在完成前会经过哪些阶段（例如，“代码冻结”、“在 QA”）？阶段是单个构建的关卡，而不是分离的管道。
   - **自动化** — 所有手动通过 `workflow_dispatch`，还是自动化的（例如，切割发布分支自动提升它）？

5. **单仓库路径** — 如果多个管道共享一个仓库，请记录哪些路径属于每个管道，并在 Linear 管道设置中或通过 `--include-paths` 连接路径过滤器。

### 第 3 步：生成 CI 配置

首先获取当前命令、标志、安装片段和命令目标规则的 [README](https://github.com/linear/linear-release/blob/main/README.md)。对于 GitHub Actions，优先使用官方动作（`linear/linear-release-action@v0`）；对于其他平台，根据 README 的安装部分使用 CLI 二进制文件。

#### 基于 Docker 的 CI 运行时要求

运行 linear-release 作业的镜像必须提供：

- **glibc。** 预构建的二进制文件是动态链接到 glibc 的，并且不会在 Alpine/musl 镜像上运行。选择 Debian/Ubuntu 基础（`debian:bookworm-slim`、`ubuntu:24.04`、`buildpack-deps:bookworm`）。避免 `alpine`、任何 `*-alpine` 标签和 `curlimages/curl`——在 musl 上，二进制文件会因为缺少 glibc 动态加载器而出现不明确的“未找到”错误。
- **`git`。** 轻量级镜像不包含它。显式安装它：`apt-get update && apt-get install -y git`。
- **`curl`**（或 `wget`）。需要下载 CLI 二进制文件。

#### GitLab CI：检查现有变量

如果 `.gitlab-ci.yml` 已存在，请检查任何默认的 `variables:` 块。linear-release 作业需要完整克隆，因此当项目默认值会阻止这一点时，在作业级别覆盖：

- `GIT_STRATEGY: clone` — 如果项目默认是 `none` 或 `empty`（两者都完全跳过克隆），则需要此设置。
- `GIT_DEPTH: 0` — 在 linear-release 作业上设置此值。新 GitLab 项目默认为深度 20 的浅克隆，并且项目通常会进一步降低深度。

选择匹配的示例模板，调整（分支模式、阶段名称、路径、版本格式），并将其添加到现有工作流或创建新工作流。多个管道意味着多个工作流或作业，每个作业使用自己的访问密钥调用 CLI——每个管道一个密钥（例如 `LINEAR_ACCESS_KEY_IOS`、`LINEAR_ACCESS_KEY_WEB`）。

| 平台       | 管道类型 | 示例                                                                                                               |
| ---------- | -------- | ------------------------------------------------------------------------------------------------------------------ |
| GitHub Actions | 持续    | [`github-actions-continuous/`](https://github.com/linear/linear-release/blob/main/examples/github-actions-continuous) |
| GitHub Actions | 计划     | [`github-actions-scheduled/`](https://github.com/linear/linear-release/blob/main/examples/github-actions-scheduled)   |
| GitLab CI      | 持续    | [`gitlab-ci-continuous/`](https://github.com/linear/linear-release/blob/main/examples/gitlab-ci-continuous)           |
| GitLab CI      | 计划     | [`gitlab-ci-scheduled/`](https://github.com/linear/linear-release/blob/main/examples/gitlab-ci-scheduled)             |
| CircleCI       | 持续    | [`circleci-continuous/`](https://github.com/linear/linear-release/blob/main/examples/circleci-continuous)             |
| CircleCI       | 计划     | [`circleci-scheduled/`](https://github.com/linear/linear-release/blob/main/examples/circleci-scheduled)               |

每个计划示例在标题中都包含一个**单仓库**注释，解释如何按平台拆分工作流以进行路径过滤。

### 第 4 步：提醒关于密钥

告诉用户将 `LINEAR_ACCESS_KEY` 密钥添加到他们的 CI 环境中：

- **GitHub Actions**：仓库设置 → 密钥和变量 → 动作 → 新建仓库密钥
- **GitLab CI**：设置 → CI/CD → 变量
- **CircleCI**：项目设置 → 环境变量

访问密钥是在 Linear 中从管道的设置页面创建的。每个管道都有自己的访问密钥。

## 关键概念

Linear 的**发布管道**是一个独立的发布流，具有自己的版本历史、当前发布和访问密钥。这不是一个 CI 管道；它是 Linear 用于跟踪发布的单元，并且你的 CI 配置调用 CLI 来更新它。独立发布的产品、环境或分发渠道是不同的管道。

管道分为两种类型——**持续**和**计划**。有关每种类型的权威描述，请参阅 README 的 [管道类型](https://github.com/linear/linear-release#pipeline-types) 部分。

### 阶段与管道

一个**管道**是一个发布流。一个**阶段**是该管道上发布的一个阶段。混淆两者是最常见的设置错误——在编写任何配置之前，请通过以下测试。

**测试：** 两个事物是否可以同时处于进行中状态，持有不同的提交？

- 是 → 分离的管道。TestFlight 在 `HEAD` 上运行，同时生产从发布分支发布 1.2。Web 预发布自动部署从 `main`，而 prod 落后。一个热修复在一个流中，但在另一个流中未发生。
- 否，它是通过关卡移动的相同构建 → 一个管道带阶段。发布在 1.2 切割，通过代码冻结、QA 和 RC 沉浸，然后发布。构建永远不会改变；只有阶段会改变。

阶段是流程关卡：“代码冻结”、“在 QA”、“在评审”、“RC 沉浸”。它们仅在计划管道上存在。

**模糊案例——应用测试：**

- **Beta / TestFlight。** TestFlight 在同一构建上的 GA 沉浸前 → 生产管道上的阶段。一个分离的夜间或狗粮频道发布**不同构建** → 自己的管道。
- **预发布环境。** 从 `main` 自动部署的预发布环境（或运行 prod 没有的热修复）→ 分离的管道。与 prod 持有完全相同构建、只是提前在提升路径上的预发布环境 → 阶段。
- **单仓库按服务。** 每个独立发布的按服务 → 自己的管道，通过路径过滤器作用域。明确；服务永远不会是阶段。

阶段也可以在 Linear 中**冻结**。冻结的阶段会使 `sync`（不带 `--release-version`）跳过该发布并在下一个发布上着陆提交——这是一个代码冻结的安全网。这是一个流程工具，而不是将两个管道压缩到一个中的方法。

## 参考

关于命令、标志、环境变量、命令目标、路径过滤、JSON 输出和故障排除的一切都存在于 [linear-release README](https://github.com/linear/linear-release#readme)。有关 GitHub Action 输入及其如何映射到 CLI 标志，请参阅 [action README](https://github.com/linear/linear-release-action#inputs)。始终获取这些，而不是依赖记忆——它们会领先于这项技能。

### 检查清单

- [ ] 完整克隆 / `fetch-depth: 0`（GitLab: `GIT_DEPTH: 0`，且 `GIT_STRATEGY` 不是 `none`）
- [ ] `LINEAR_ACCESS_KEY` 设置为密钥（每个管道一个）
- [ ] 正确的二进制平台（`linux-x64`、`darwin-arm64` 或 `darwin-x64`）
- [ ] 基于 Docker 的 CI：glibc 基础镜像（无 Alpine/musl）且 `git` 和 `curl` 可用
- [ ] 在正确的分支上触发（`main` 用于持续；`main` + `release/*` 用于计划）
- [ ] 单仓库：路径过滤器设置（在 Linear 配置或通过 `--include-paths`），如果使用发布分支，则使用分离的工作流
