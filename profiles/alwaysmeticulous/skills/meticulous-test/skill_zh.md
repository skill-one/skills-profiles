要使用 Meticulous 测试前端变更，请按照以下步骤逐步操作，使用 CLI 或 MCP 命令（如文中所述）。

> 开始之前，请运行 `meticulous-cli-update` 命令以确保 Meticulous CLI 和技能已更新——除非在本对话中之前已经运行过，则可跳过此步骤。

如果您已经获得测试运行 ID，请跳至步骤 4。

## 步骤 1 -- 构建前端

1. 通过检查相应步骤的 CI 配置来确定 Meticulous 期望的构建工件：
   - GitHub：`.github/workflows/*.yml` 用于 `uses: alwaysmeticulous/report-diffs-action/upload-assets@v1`（构建资源）或 `upload-container@v1`（Docker 镜像）
   - GitLab：`.gitlab-ci.yml`（或包含的 `.gitlab/ci/*.yml`）用于 `npx @alwaysmeticulous/cli ci upload-assets`（构建资源）或 `ci upload-container`（Docker 镜像）
   - Bitbucket：`bitbucket-pipelines.yml` 用于相同的 `npx @alwaysmeticulous/cli ci upload-assets` / `ci upload-container` 步骤
2. 按照该 CI 配置中使用的相同说明构建前端。

## 步骤 2 -- 上传构建

使用 `agent upload-build` 将构建注册为可重复使用的部署。这会上传工件并在标准输出中打印 `deploymentId`——它**不会**触发运行。

```bash
# CLI
meticulous agent upload-build --appDirectory <构建路径>     # 资源
meticulous agent upload-build --localImageTag <镜像标签>        # 容器

# MCP（非 1:1 映射 — 请求上传 URL，自行上传工件，然后注册）
request_asset_upload(size=<zipByteSize>)      # 或 request_container_upload() — 无必需参数
# ... 自行将 zip/镜像上传到返回的 URL/注册表 ...
register_asset_build(uploadId="<id>", commitSha="<sha>")      # 或 register_container_build(uploadId="<id>", commitSha="<sha>")
```

- `--appDirectory` 指向构建输出目录（例如 `dist/` 子目录）；`--localImageTag` 是本地 Docker 镜像标签。构建模式自动检测。
- 构建的提交默认为本地 git HEAD。如果工作区有未提交的变更，则捕获为**临时提交**（显示为 `commitSha (local, 临时由于工作区脏): …`）——见未提交变更的注释。
- 未跟踪的文件会被拒绝（无法捕获）——先用 `git add` 添加它们。
- 从标准输出捕获 `deploymentId`（使用 `--verbose` 也会在标准错误中显示进度）。

## 步骤 3 -- 触发测试运行

为部署触发运行，并与基准进行比较。从仓库目录运行以自动推断基准（与 origin 默认分支的合并基）和 git 差异：

```bash
# CLI
meticulous agent trigger-test-run --deploymentId <deploymentId>

# MCP（从不推断 `baseSha`/`gitDiffOutput` — 显式传递它们 — 并始终立即返回，无需等待运行完成）
trigger_test_run(deploymentId="<deploymentId>", baseSha="<sha>")
```

- 基准**必需**。它从当前目录自动推断，或传递 `--baseSha <sha>`（可选 `--gitDiffOutput`）显式设置。
- 省略 `--deploymentId` 以使用本地 HEAD 提交最近上传的部署——这要求工作区干净（无未提交变更）。
- 命令默认**阻塞直到运行完成**并打印 `testRunId` 到标准输出；检测到视觉差异时最终状态为 `Failure`（正常完成，非错误）。传递 `--dontWaitForTestRunToComplete` 以在运行触发后立即返回。
- **一个构建，多个基准**：相同的 `deploymentId` 可以针对不同的基准重新触发——只需再次运行 `agent trigger-test-run` 并使用不同的 `--baseSha`。无需重新构建或重新上传。

记下输出中的 `testRunId`。

## 步骤 4 -- 审查视觉变更

使用 `meticulous-review` 命令，并传递步骤 3 的 `testRunId`。它会获取差异摘要，检查代表性截图 / DOM 差异 / 时间线，并生成最终报告，将每个视觉变更分类为预期或非预期。

> **未提交的变更**：如果您在脏工作区构建/测试，运行记录在非 HEAD 的临时提交上（且未推送）。从本地检出解析运行的命令——`meticulous-review` / `agent test-run-diffs` 无 `--testRunId`——无法按提交查找，因此在这种情况下**必须**在审查步骤中传递显式的 `--testRunId`。
