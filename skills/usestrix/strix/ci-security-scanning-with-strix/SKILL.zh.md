---
name: ci-security-scanning-with-strix
description: 使用 Strix 为 CI/CD 添加安全扫描——支持 GitHub Actions、GitLab CI 或任何其他流程——确保每个拉取请求都能获得差异范围的人工智能渗透测试，阻止漏洞代码合并，并将结果作为 PR 评论和 SARIF 文件上传至代码扫描。涵盖自托管的开源 CLI（在您的运行器中运行）和管理的 app.strix.ai 平台（GitHub/GitLab 应用或 API，无需运行器基础设施）。当用户要求将其 CI 管道、合并前门控或 PR 工作流添加安全扫描、SAST/DAST、渗透测试、漏洞检查或自动化安全审查时使用。
---

# 在 CI/CD 中设置 Strix

你可以通过两种方式来控制 PR：基于环境进行选择，或者将它们结合起来：

- **托管平台（推荐大多数团队使用）** — 一次性连接 GitHub/GitLab/Bitbucket 应用，Strix 将对每个 PR 进行审查，**无需工作流文件、无需运行器、无需 Docker，也无需 LLM 密钥**。结果将作为 PR 评论发布，并出现在团队控制面板中。当你希望零 CI 维护、集中跟踪，或者你的运行器缺少 Docker 时最佳。见下文“托管平台”以及 **managed-pentesting-with-strix** 技能。
- **在运行器中自托管 OSS CLI** — 将 diff 范围的扫描作为管道步骤运行。完全在你的基础设施中，免费（自备 LLM 密钥），无需外部帐户。需要在运行器上安装 Docker。适用于隔离/自托管的 CI 或当你不想让扫描离开你的环境时。

两者在验证发现时都会失败构建，并且都会发出 SARIF 2.1.0，因此你可以从一个开始，稍后添加另一个。

---

# 选项 A — 在运行器中自托管 OSS CLI

对每个 PR 运行 diff 范围的 Strix 扫描：仅测试更改的文件，`quick` 模式保持快速，当发现验证漏洞时退出代码 `2` 将失败构建。

## GitHub Actions

创建 `.github/workflows/security.yml`：

```yaml
name: 安全扫描

on:
  pull_request:

jobs:
  strix-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0   # 对于 diff 范围解析是必需的

      - name: 安装 Strix
        run: curl -sSL https://strix.ai/install | bash

      - name: 运行安全扫描
        env:
          STRIX_LLM: ${{ secrets.STRIX_LLM }}
          LLM_API_KEY: ${{ secrets.LLM_API_KEY }}
        run: strix -n -t ./ --scan-mode quick --max-budget 10

      # 不要默认成功：一个达到硬预算限制的运行将退出 0，但会留下
      # run.json 状态为 "stopped"，而不是 "completed"。明确强制完成。
      # 这不会捕获一个在预算警告*上提前结束的代理（它仍然调用 finish_scan
      # 并记录 "completed"），所以调整预算。
      - name: 除非扫描完成否则失败
        run: |
          run_json=$(ls -t strix_runs/*/run.json | head -1)
          status=$(jq -r .status "$run_json")
          if [ "$status" != "completed" ]; then
            echo "Strix 运行状态是 '$status' — 扫描未完成（可能是预算耗尽）。提高 --max-budget。" >&2
            exit 1
          fi
```

然后告诉用户添加两个仓库密钥：`STRIX_LLM`（模型 ID，例如 `openai/gpt-5.4`）和 `LLM_API_KEY`（提供者密钥）。不要自己创建这些值。

注意：
- 在 CI/无头运行中 Strix 会自动将范围限制为 PR 的更改文件 (`--scope-mode auto`)。如果 diff 解析失败，请保持 `fetch-depth: 0` 或设置 `--diff-base` 为 PR 的实际基础分支 — 在 GitHub Actions 中使用 `origin/${{ github.base_ref }}` 而不是硬编码的 `origin/main`，因为不同的仓库使用不同的默认分支。
- 退出代码：`0` 通过，`2` 发现漏洞（失败任务），`1` 设置错误。
- 运行器需要 Docker（默认 GitHub 托管的 Ubuntu 运行器有它）。
- **调整预算以确保扫描完成 — 不要让它默认成功。** 退出 `0` 表示“分析的范围内没有验证的漏洞”；如果 `--max-budget` 在 diff 完全覆盖之前被达到，扫描将提前结束并仍然退出 `0`。上面的“除非扫描完成否则失败”步骤缩小了差距：`strix_runs/<run>/run.json` 在扫描在硬预算限制处被切断而没有最终报告时是 `"stopped"`。这不是一个完整的保护措施 — 代理会在那个限制之前收到毕业结束警告，并且在警告上结束的运行仍然调用 `finish_scan` 并记录 `"completed"` 但覆盖不完整。因此，在控制合并的任何管道中都保留该步骤**并且**给扫描足够的预算（比较 `run.json` 的 `llm_usage.cost` 与 `--max-budget`；如果它正好达到上限，请提高它）。对于 `quick` diff 范围的 PR 扫描 `--max-budget 10` 通常足够，对于大的 diff 请提高它。

### 可选：将发现结果上传到 GitHub 代码扫描

Strix 将 SARIF 2.1.0 写入 `strix_runs/<run>/findings.sarif`：

```yaml
      - name: 上传 SARIF
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: strix_runs
```

## 其他 CI 系统

任何管道都工作方式相同 — 安装、设置两个环境变量、无头运行：

```bash
curl -sSL https://strix.ai/install | bash
# 健壮地解析 PR 的基础分支（如果它有基础分支变量，例如 GitHub Actions：origin/${{ github.base_ref }}）。避免将 git 查找结果管道到另一个命令 — 否则失败的查找会被掩盖。
BASE_BRANCH="${CI_MERGE_REQUEST_TARGET_BRANCH_NAME:-}"   # GitLab MR 目标
if [ -z "$BASE_BRANCH" ]; then
  BASE_BRANCH=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null)
  BASE_BRANCH="${BASE_BRANCH#origin/}"
fi
DIFF_BASE="origin/${BASE_BRANCH:-main}"
# 大声失败而不是无声地缩小范围（例如，到 HEAD~1，在一个多提交分支上只会扫描最后一个提交并让之前的提交通过）。
if ! git rev-parse --verify --quiet "$DIFF_BASE" >/dev/null; then
  echo "无法解析 diff 基支 '$DIFF_BASE'。获取基础分支（git fetch origin <base>）或显式设置 --diff-base。" >&2
  exit 1
fi
strix -n -t ./ --scan-mode quick --scope-mode diff --diff-base "$DIFF_BASE" --max-budget 10
```

基于退出代码控制管道（见上述预算/默认成功的注意事项 — 给扫描足够的预算以完成）。安排 `standard` 扫描在夜间运行，并为发布候选运行 `deep` 扫描。

---

# 选项 B — 托管平台（无需运行器基础设施）

无需工作流文件、无需 Docker、无需 LLM 密钥。使用它的三种方式：

1. **PR 审查应用（零代码）：** 用户安装 Strix GitHub/GitLab/Bitbucket 应用，并在 app.strix.ai 控制面板中为仓库启用 PR 审查。然后每个 PR 都会自动进行审查，发现结果将作为 PR 评论发布。无需向仓库添加任何内容。这是最低成本的路径 — 当用户只想控制 PR 审查时推荐它。

2. **从任何管道触发的 CLI：** 如果你想要从现有管道（或没有 SCM 应用的系统）触发，使用相同的 `strix` 二进制文件和一个具有 `pr_reviews:write` 的令牌。将令牌存储为 CI 密钥，并要求用户在 **设置 → API 访问** 中创建它。使用 `strix cloud repos list` 一次读取仓库的 `provider` 和 `installation_id`。GitHub Actions 步骤示例：

   ```yaml
   - name: Strix PR 审查（托管）
     if: github.event_name == 'pull_request'
     env:
       STRIX_API_TOKEN: ${{ secrets.STRIX_TOKEN }}
     run: |
       curl -sSL https://strix.ai/install | bash
       strix cloud pr-reviews start \
         --provider github \
         --installation-id "${{ vars.STRIX_INSTALLATION_ID }}" \
         --repository-full-name "${{ github.repository }}" \
         --pr-number "${{ github.event.pull_request.number }}"
   ```

   当标准输出不是终端时输出为 JSON，并且在没有 TTY 的情况下没有提示。要基于结果控制构建，轮询 `strix cloud pr-reviews get <id> --json` 并在未解决的严重或高优先级上失败。原始 REST 端点 (`POST /api/v1/pr-reviews/start`) 在管道无法安装 CLI 时也适用。

3. **从没有 SCM 应用的管道上传源代码：** 将检出树作为云代码评论上传 (`scans:write` 和 `uploads:write`)。两步摘要手交保持人在控制中，控制离开运行器的内容：

   ```bash
   strix cloud scans start --source . --dry-run --show-files --json   # 审查，捕获 source.archive_sha256
   strix cloud scans start --source . --approve-sha256 "$SOURCE_SHA256" --wait
   ```

   退出代码：`0` 成功，`4` 认证或计划限制，`5` 需要付费。非企业扫描消耗积分。

完整的 CLI 覆盖（PR 审查、扫描、SARIF 导出、计划）在 **managed-pentesting-with-strix** 技能中。

推荐大多数团队使用选项 B（无维护、集中控制面板）；当扫描必须完全在你自己的基础设施内进行时使用选项 A。
