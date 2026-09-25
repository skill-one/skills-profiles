# 安全所有权映射

## 概述

从 git 历史中构建人员与文件的二分图，然后计算所有权风险并导出 Neo4j/Gephi 的图工件。同时构建文件共同变更图（基于共享提交的 Jaccard 相似度）以通过它们共同移动的方式对文件进行聚类，同时忽略大型、嘈杂的提交。

## 要求

- Python 3
- `networkx`（必需；社区检测默认启用）

使用以下命令安装：

```bash
pip install networkx
```

## 工作流程

1. 限定仓库和时间窗口（可选 `--since/--until`）。
2. 确定敏感度规则（使用默认值或提供 CSV 配置文件）。
3. 使用 `scripts/run_ownership_map.py` 构建所有权映射（共同变更图默认启用；使用 `--cochange-max-files` 忽略超节点提交）。
4. 社区默认计算；图 ML 输出可选 (`--graphml`)。
5. 使用 `scripts/query_ownership.py` 查询输出，以获取有界的 JSON 切片。
6. 持久化和可视化（参见 `references/neo4j-import.md`）。

默认情况下，共同变更图会忽略常见的“粘合”文件（锁文件、`.github/*`、编辑器配置），因此集群反映实际代码移动，而不是共享的基础设施编辑。使用 `--cochange-exclude` 或 `--no-default-cochange-excludes` 覆盖。默认情况下排除 Dependabot 提交；使用 `--no-default-author-excludes` 或通过 `--author-exclude-regex` 添加模式。

如果您想从共同变更聚类中排除 Linux 构建粘合文件（如 `Kbuild`），请传递：

```bash
python skills/skills/security-ownership-map/scripts/run_ownership_map.py \
  --repo /path/to/linux \
  --out ownership-map-out \
  --cochange-exclude "**/Kbuild"
```

## 快速入门

从仓库根目录运行：

```bash
python skills/skills/security-ownership-map/scripts/run_ownership_map.py \
  --repo . \
  --out ownership-map-out \
  --since "12 个月前" \
  --emit-commits
```

默认值：作者身份、作者日期和合并提交被排除。如果需要，使用 `--identity committer`、`--date-field committer` 或 `--include-merges`。

示例（覆盖共同变更排除项）：

```bash
python skills/skills/security-ownership-map/scripts/run_ownership_map.py \
  --repo . \
  --out ownership-map-out \
  --cochange-exclude "**/Cargo.lock" \
  --cochange-exclude "**/.github/**" \
  --no-default-cochange-excludes
```

默认情况下计算社区。要禁用：

```bash
python skills/skills/security-ownership-map/scripts/run_ownership_map.py \
  --repo . \
  --out ownership-map-out \
  --no-communities
```

## 敏感度规则

默认情况下，脚本会标记常见的身份/加密/秘密路径。通过提供 CSV 文件覆盖：

```
# pattern,tag,weight
**/auth/**,auth,1.0
**/crypto/**,crypto,1.0
**/*.pem,secrets,1.0
```

使用 `--sensitive-config path/to/sensitive.csv` 使用它。

## 输出工件

`ownership-map-out/` 包含：

- `people.csv`（节点：人员）
- `files.csv`（节点：文件）
- `edges.csv`（边：接触）
- `cochange_edges.csv`（文件到文件的共同变更边，具有 Jaccard 权重；使用 `--no-cochange` 时省略）
- `summary.json`（安全所有权发现）
- `commits.jsonl`（可选，如果 `--emit-commits`）
- `communities.json`（默认情况下从共同变更边计算，包括每个社区的维护者；使用 `--no-communities` 禁用）
- `cochange.graph.json`（NetworkX 节点-链接 JSON，具有 `community_id` + `community_maintainers`；如果没有共同变更边，则回退到 `ownership.graph.json`）
- `ownership.graphml` / `cochange.graphml`（可选，如果 `--graphml`）

`people.csv` 包括基于作者提交偏移的时区检测：`primary_tz_offset`、`primary_tz_minutes` 和 `timezone_offsets`。

## LLM 查询辅助工具

使用 `scripts/query_ownership.py` 返回小型的、JSON 有界切片，而无需将整个图加载到上下文中。

示例：

```bash
python skills/skills/security-ownership-map/scripts/query_ownership.py --data-dir ownership-map-out people --limit 10
python skills/skills/security-ownership-map/scripts/query_ownership.py --data-dir ownership-map-out files --tag auth --bus-factor-max 1
python skills/skills/security-ownership-map/scripts/query_ownership.py --data-dir ownership-map-out person --person alice@corp --limit 10
python skills/skills/security-ownership-map/scripts/query_ownership.py --data-dir ownership-map-out file --file crypto/tls
python skills/skills/security-ownership-map/scripts/query_ownership.py --data-dir ownership-map-out cochange --file crypto/tls --limit 10
python skills/skills/security-ownership-map/scripts/query_ownership.py --data-dir ownership-map-out summary --section orphaned_sensitive_code
python skills/skills/security-ownership-map/scripts/query_ownership.py --data-dir ownership-map-out community --id 3
```

使用 `--community-top-owners 5`（默认）控制每个社区存储的维护者数量。

## 基本安全查询

运行以下命令以使用有界输出回答常见的安全所有权问题：

```bash
# Orphaned sensitive code (stale + low bus factor)
python skills/skills/security-ownership-map/scripts/query_ownership.py --data-dir ownership-map-out summary --section orphaned_sensitive_code

# Hidden owners for sensitive tags
python skills/skills/security-ownership-map/scripts/query_ownership.py --data-dir ownership-map-out summary --section hidden_owners

# Sensitive hotspots with low bus factor
python skills/skills/security-ownership-map/scripts/query_ownership.py --data-dir ownership-map-out summary --section bus_factor_hotspots

# Auth/crypto files with bus factor <= 1
python skills/skills/security-ownership-map/scripts/query_ownership.py --data-dir ownership-map-out files --tag auth --bus-factor-max 1
python skills/skills/security-ownership-map/scripts/query_ownership.py --data-dir ownership-map-out files --tag crypto --bus-factor-max 1

# Who is touching sensitive code the most
python skills/skills/security-ownership-map/scripts/query_ownership.py --data-dir ownership-map-out people --sort sensitive_touches --limit 10

# Co-change neighbors (cluster hints for ownership drift)
python skills/skills/security-ownership-map/scripts/query_ownership.py --data-dir ownership-map-out cochange --file path/to/file --min-jaccard 0.05 --limit 20

# Community maintainers (for a cluster)
python skills/skills/security-ownership-map/scripts/query_ownership.py --data-dir ownership-map-out community --id 3

# Monthly maintainers for the community containing a file
python skills/skills/security-ownership-map/scripts/community_maintainers.py \
  --data-dir ownership-map-out \
  --file network/card.c \
  --since 2025-01-01 \
  --top 5

# Quarterly buckets instead of monthly
python skills/skills/security-ownership-map/scripts/community_maintainers.py \
  --data-dir ownership-map-out \
  --file network/card.c \
  --since 2025-01-01 \
  --bucket quarter \
  --top 5
```

注意：
- 接触默认为一次作者提交（不是每个文件）。使用 `--touch-mode file` 按文件计数接触。
- 使用 `--window-days 90` 或 `--weight recency --half-life-days 180` 平滑变更。
- 使用 `--ignore-author-regex '(bot|dependabot)'` 过滤机器人。
- 使用 `--min-share 0.1` 仅显示稳定的维护者。
- 使用 `--bucket quarter` 进行日历季度分组。
- 使用 `--identity committer` 或 `--date-field committer` 切换到提交者归因。
- 使用 `--include-merges` 包括合并提交（默认排除）。

### 摘要格式（默认）

使用此结构，如有需要可添加字段：

```json
{
  "orphaned_sensitive_code": [
    {
      "path": "crypto/tls/handshake.rs",
      "last_security_touch": "2023-03-12T18:10:04+00:00",
      "bus_factor": 1
    }
  ],
  "hidden_owners": [
    {
      "person": "alice@corp",
      "controls": "63% of auth code"
    }
  ]
}
```

## 图持久化

当您需要将 CSV 文件加载到 Neo4j 中时，使用 `references/neo4j-import.md`。它包括约束、导入 Cypher 和可视化提示。

## 注意事项

- `bus_factor_hotspots` 在 `summary.json` 中列出了具有低 bus factor 的敏感文件；`orphaned_sensitive_code` 是陈旧的子集。
- 如果 `git log` 太大，使用 `--since` 或 `--until` 缩小范围。
- 将 `summary.json` 与 CODEOWNERS 进行比较，以突出所有权漂移。
