# 技能：GitHub 流量

获取并分析 GitHub 仓库流量数据——页面浏览量、Git 克隆数、推荐来源、热门页面和星标增长。可选择生成 PNG 图片的趋势图。

> **前提条件：**
> - 必须安装并认证 `gh` 命令行工具
> - 需要**推送（写入）权限**到目标仓库——GitHub 的流量 API 在仅读访问下无法工作
> - `matplotlib` 是可选的（用于 PNG 图表生成；若不可用则回退到 ASCII 格式）

---

## 使用场景

- 用户询问关于仓库流量、页面浏览量、克隆次数或访客来源
- 用户想查看流量随时间的变化趋势（每周、每月、每季度）
- 用户想生成流量报告图表用于分享或文档
- 用户想定期快照流量数据以建立长期历史记录

---

## 重要提示：GitHub 流量 API 限制

GitHub 仅提供**最近 14 天**的流量数据。要追踪更长时间段（30 天、90 天等）的趋势，脚本会将每次获取的数据存储在本地历史文件（`~/.github-traffic/<repo>_traffic.json`）中。**需要定期快照以积累历史数据。**

推荐：设置 cron 任务或 CI 定时任务定期运行快照命令：

```bash
# 每日快照（无输出，仅存储数据）
0 9 * * * python /path/to/scripts/github_traffic.py owner/repo --snapshot
```

---

## 默认工作流程

```bash
python /path/to/skills/github-traffic/scripts/github_traffic.py <owner/repo>
```

这将：
1. 通过 `gh api` 获取当前流量数据
2. 保存快照到 `~/.github-traffic/` 用于历史追踪
3. 显示格式化的摘要（浏览量、克隆数、推荐来源、热门页面）

---

## 生成图表

```bash
# 生成 PNG 趋势图（最近 30 天，默认）
python .../github_traffic.py owner/repo --chart

# 最后 7 天
python .../github_traffic.py owner/repo --chart --days 7

# 最后 90 天（需要积累的历史）
python .../github_traffic.py owner/repo --chart --days 90

# ASCII 图表（无需 matplotlib）
python .../github_traffic.py owner/repo --ascii
```

PNG 图表包含最多 3 个面板：
1. **页面浏览量**——总浏览量和独立访客（面积图）
2. **Git 克隆数**——总克隆数和独立克隆者（柱状图+折线图）
3. **星标增长**——随时间的星标数（折线图，当存在多个快照时显示）

---

## 脚本选项

| 标志 | 默认值 | 描述 |
|------|---------|-------------|
| `repo` (位置参数) | 必须提供 | 仓库格式为 `owner/name` |
| `--chart` | 关闭 | 生成 PNG 趋势图 |
| `--ascii` | 关闭 | 强制 ASCII 柱状图输出 |
| `--days` | `30` | 图表中包含的天数 |
| `--history-dir` | `~/.github-traffic/` | 历史数据存储目录 |
| `--output` | `<repo>_traffic.png` | 图表图片的输出路径 |
| `--snapshot` | 关闭 | 仅获取和存储数据（不显示） |

---

## 示例

```bash
# 快速流量摘要
python .../github_traffic.py zilliztech/memsearch

# 每周趋势图
python .../github_traffic.py zilliztech/memsearch --chart --days 7

# 每月趋势图，自定义输出路径
python .../github_traffic.py zilliztech/memsearch --chart --days 30 --output ./reports/traffic.png

# 仅存储快照（用于 cron 任务）
python .../github_traffic.py zilliztech/memsearch --snapshot

# matplotlib 不可用时使用 ASCII 图表
python .../github_traffic.py zilliztech/memsearch --ascii --days 14
```

---

## 历史记录与长期追踪

每次运行都会将当前 14 天的数据合并到持久化 JSON 文件 `~/.github-traffic/<owner>_<repo>_traffic.json` 中。文件包含：

- **每日浏览量**：日期 → {浏览量, 独立访客}
- **每日克隆数**：日期 → {克隆数, 独立克隆者}
- **星标快照**：日期 → 星标数
- **获取元数据**：时间戳, 14 天总计, 星标, 分叉数

要生成有意义的 30/90 天图表，至少每 14 天运行一次脚本（理想情况是每天）。超过 14 天的空白将显示为图表中的缺失数据。

---

## 权限

GitHub 流量 API 需要**推送权限**到仓库。这意味着：
- 仓库所有者和管理员：完全访问权限
- 具有写入/维护角色的协作者：完全访问权限
- 仅读用户和分叉者：**无访问权限**（API 返回 403）

如果遇到权限错误，请检查 `gh auth status` 并确保您的 token 具有写入权限。

---

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| "必须具有推送权限" 错误 | 您需要仓库写入权限。检查 `gh auth status`。 |
| 图表仅显示 14 天 | GitHub 仅提供 14 天窗口。定期运行 `--snapshot` 积累历史数据。 |
| matplotlib 未找到 | 使用 `pip install matplotlib` 安装。或使用 `--ascii` 生成文本图表。 |
| 某些日期无数据 | GitHub 可能不会报告零流量的日期。这些空白是正常的。 |
