# 发现问题

你在仓库中发现了安全问题。这项技能计划要扫描哪些漏洞向量，然后针对每个项目执行这些扫描。

## 输入

- **depth**: `quick`（默认）、`balanced` 或 `full` — 通过 `$ARGUMENTS` 覆盖

$ARGUMENTS

> **注意**：传递的参数可用于自定义扫描工作流，如果提供。例如，如果用户指定了一组特定的向量、向量数量、特定的候选文件、关注的区域、候选文件数量等，请确保将相关细节传递给技能中的相关步骤。

## 支持文件

- 循环脚本：[scripts/loop.sh](scripts/loop.sh)
- 扫描标准：[criteria/index.yaml](criteria/index.yaml)

---

## 第 1 步：设置

计算特定于仓库的输出目录：
```bash
repo_name=$(basename "$(pwd)") && remote_url=$(git remote get-url origin 2>/dev/null || pwd) && short_hash=$(printf '%s' "$remote_url" | git hash-object --stdin | cut -c1-8) && repo_id="${repo_name}-${short_hash}" && short_sha=$(git rev-parse --short HEAD 2>/dev/null || date +%Y%m%d) && ghost_repo_dir="$HOME/.ghost/repos/${repo_id}" && scan_dir="${ghost_repo_dir}/scans/${short_sha}/code" && cache_dir="${ghost_repo_dir}/cache" && mkdir -p "$scan_dir" && echo "scan_dir=$scan_dir cache_dir=$cache_dir"
```

1. 读取 `$cache_dir/repo.md` — 如果缺失，请先运行仓库上下文技能，然后继续。
2. 读取 [criteria/index.yaml](criteria/index.yaml) 以获取每个项目类型的有效代理→向量映射。
3. 如果未提供，将 `depth` 设置为 `quick`。
4. 如果 `depth` 是 `full`，则警告用户完整扫描会使用大量令牌，并在继续之前要求用户确认。如果他们拒绝，则回退到 `balanced`。

---

## 第 2 步：计划扫描

如果 `$scan_dir/plan.md` 已存在，则跳到下一步。

否则，使用 [scripts/loop.sh](scripts/loop.sh) 运行计划器：

```bash
bash <path-to-loop.sh> $scan_dir planner.md "- depth: <depth>
- arguments: <relevant argument overrides if any, otherwise omit>" 1 $cache_dir
```

使用 10 分钟的超时。如果命令超时，请重新运行它 — 脚本会从上次停止的地方继续。如果连续 3 次以相同的错误失败，请停止并报告失败。

**验证**：在继续之前，`$scan_dir/plan.md` 存在且包含至少一个 `## Project:` 部分。

---

## 第 3 步：提名文件

如果 `$scan_dir/nominations.md` 不存在，则通过读取 `$scan_dir/plan.md` 并针对每个项目部分（`## Project: <base_path> (<type>)`），解析推荐扫描表。对于每一行，提取代理和向量列。写入 `$scan_dir/nominations.md` — 每个项目、代理、向量组合占一行。跳过扫描表为空的项目的项目。

```markdown
# Nominations

- [ ] <base_path> (<type>) | <agent> | <vector>
- [ ] <base_path> (<type>) | <agent> | <vector>
...
```

如果 `$scan_dir/nominations.md` 已存在，则将每个顶级任务 `- [x]` 更改为 `- [ ]`。保持每个项目下的所有缩进行/子任务不变。

### 运行提名脚本

使用 [scripts/loop.sh](scripts/loop.sh)：

```bash
bash <path-to-loop.sh> $scan_dir nominator.md "- depth: <depth>
- arguments: <relevant argument overrides if any, otherwise omit>" 5 $cache_dir
```

使用 10 分钟的超时。如果命令超时，请重新运行它 — 脚本会从上次停止的地方继续。如果连续 3 次以相同的错误失败，请停止并报告失败。

**验证**：在继续之前，`$scan_dir/nominations.md` 包含至少一条 `- [x]` 行。

---

## 第 4 步：分析提名的文件

读取 `$scan_dir/nominations.md`。对于在带检查的 `- [x]` 行下的每个候选文件，追加到 `$scan_dir/analyses.md`（跳过已在 `analyses.md` 中列出的候选文件）。

```
- [ ] <base_path> (<type>) | <agent> | <vector> | <candidate_file>
```

创建结果目录：
```bash
mkdir -p $scan_dir/findings
```

### 运行分析脚本

使用 [scripts/loop.sh](scripts/loop.sh)：

```bash
bash <path-to-loop.sh> $scan_dir analyzer.md "" 5 $cache_dir
```

使用 10 分钟的超时。如果命令超时，请重新运行它 — 脚本会从上次停止的地方继续。如果连续 3 次以相同的错误失败，请停止并报告失败。

**验证**：在继续之前，`$scan_dir/analyses.md` 包含至少一条 `- [x]` 行。

---

## 第 5 步：验证结果

列出 `$scan_dir/findings/` 中的所有 `.md` 文件。如果不存在，则写入 `no-findings.md` 摘要并停止。

使用 [scripts/loop.sh](scripts/loop.sh)：

```bash
bash <path-to-loop.sh> $scan_dir verifier.md "" 5 $cache_dir
```

使用 10 分钟的超时。如果命令超时，请重新运行它 — 脚本会从上次停止的地方继续。如果连续 3 次以相同的错误失败，请停止并报告失败。

---

## 完成

所有步骤完成后，报告扫描结果：

1. 列出 `$scan_dir/findings/` 中的所有结果文件。
2. 统计已验证与被拒绝的结果数量。
3. 向用户展示摘要。
