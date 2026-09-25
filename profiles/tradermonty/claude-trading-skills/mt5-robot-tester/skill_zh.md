# MT5 机器人测试器

## 概述

通过命令行驱动策略测试器，从 *候选* 文件夹中筛选出最佳的 MetaTrader 5 机器人（专家顾问），通过 **3 轮管道**，随着每个机器人的进展在文件夹之间移动，并在每次循环中 **跨运行学习** 以改进选择。整个运行过程会被检查点保存，并且可以恢复。

- **第 1 轮 — 筛选（所有货币对）**：在配置的 `common.symbols` 列表中的每个符号上回测 EA（每个符号一个 `Optimization=0` 的回测 — MT5 构建 6061 将 `Optimization=3` 的 XML 留空，因此使用按符号回测）。门槛：**≥5 个盈利的符号 AND 最佳符号 ≥3× 存款**。
- **第 2 轮 — 最佳货币对回测**：在最佳符号上进行单次回测；分析净利润 %、最差回撤 %、正月份 %、所有年份正、LR 相关性、到新高的月份。
- **第 3 轮 — 顺序参数优化**：在 `MagicNumber` 之后优化 5–6 个输入，一次一个，范围 ±50% 步长 5%；然后进行最终回测。
- **最终候选者**：优化结果 **优于** 第 2 轮 **且** 利润 **≥4× 存款** **且** 最差回撤 **≤12%**。

测试过的机器人会移动到 *测试中*；最终候选者也会连同其优化的 `.set` 复制到 *最终候选者* 文件夹。

## 使用场景

- "在 MetaTrader 5 中测试机器人 / 机器人 / EAs。"
- 筛选 MT5 专家顾问文件夹并跨所有货币对选择最佳。
- 优化 EA 参数并通过利润/回撤/一致性决定最终候选者。
- 恢复中断的测试运行。

## 前置条件

- **Windows + MetaTrader 5** 安装（测试器运行 `terminal64.exe`）。
- 交易商 **tick 数据** 下载（默认建模是真实 tick，`Model=4`）。
- `MQL5\Experts` 下面的三个文件夹：*候选*、*测试中*、*最终候选者*。
- **`common.symbols`** 在配置中设置 — 第 1 轮回测的货币对（你的 Market Watch 符号）。
- 可选的每个机器人的 `.set` 文件（配置 `sets_dir`）用于第 2 轮基线和第 3 轮参数优化。优化期间，除了当前正在搜索的参数外，所有输入都是固定的；如果没有 `.set`，第 3 轮将被跳过，结果来自第 2 轮。
- **运行前关闭 MetaTrader 5** — 测试器需要独占使用数据文件夹。
- Python 3.9+（仅使用标准库）。没有付费 API。

## 工作流程

### 第 1 步 — 配置

复制 `assets/pipeline_config.template.json`，填写三个文件夹路径和（可选的）`terminal_path`。永远不要提交真实的个人路径 — 在运行时传递配置。默认值已经编码了约定的设置（2020.01.01→2026.06.30，H1，Model=4，10000 美元，1:100，门槛和阈值）。

### 第 2 步 — 干运行（可选）

在不启动 MT5 的情况下验证生成的第 1 轮 INI 文件：

```bash
python3 skills/mt5-robot-tester/scripts/mt5_batch_tester.py \
  --config my_config.json --output-dir reports/mt5_pipeline --dry-run
```

### 第 3 步 — 运行管道

```bash
python3 skills/mt5-robot-tester/scripts/mt5_batch_tester.py \
  --config my_config.json --output-dir reports/mt5_pipeline
```

每个机器人流经 R1 → R2 → R3 → 最终候选者决策。每一步后都会将进度写入 `state.json` 和 `run.log`。

### 第 4 步 — 如果中断则恢复

```bash
python3 skills/mt5-robot-tester/scripts/mt5_batch_tester.py \
  --config my_config.json --output-dir reports/mt5_pipeline --resume
```

`--resume` 跳过已完成的机器人，并仅重用完成的轮次，同时执行配置、EA 二进制文件和输入 `.set` 指纹仍然匹配。如果周期、符号列表、二进制文件或 `.set` 发生变化，则安全地重新启动该机器人。

### 可选 — HTML 控制面板

启动本地仪表板，查看每个文件夹中的机器人、每个机器人的阶段和裁决，以及一个 **启动** 按钮 — 启动后无需 CLI：

```bash
python3 skills/mt5-robot-tester/scripts/dashboard.py \
  --config my_config.json --output-dir reports/mt5_pipeline
```

它提供 `http://127.0.0.1:8765/`（自动打开，仅限本地）。页面每 3 秒自动刷新：文件夹内容、每个机器人的阶段（R1/R2/R3/完成）、通过/失败裁决、摘要计数和实时 `run.log`。启动/停止请求仅限于精确的本地原点，并需要每个服务器的 CSRF 令牌。

### 第 5 步 — 阅读结果

- `leaderboard_<ts>.md` / `.json` — 排名，包括裁决和关键指标。
- `learnings.json` / `learnings.md` — 本轮技能学到的内容（参数影响和符号优先级）在配置的输出目录下。
- `mt5_reports/` 和 `mt5_ini/` — 每个机器人/轮次的原始 MT5 报告和配置。

## 轮次详情

### 第 1 轮门槛（两者都必需）
1. `count_positive_profit(passes) ≥ round1_min_positive`（默认 5）。
2. `best_symbol_profit ≥ round1_min_profit_multiple × deposit`（默认 3×）。

失败 → 机器人被拒绝（移动到 *测试中*）。

### 第 2 轮质量指标（参考阈值）
净利润 ≥300%，最差 DD <15%（较大的平衡/权益 %），正月份 >70%，所有年份正，**LR 相关性 ≥0.80**，到新高的月份 ≤3。
按机器人报告；硬性最终候选者门槛是第 3 轮。

### 第 3 轮顺序优化
对于 `MagicNumber` 之后的所有 5–6 个输入（首先学习顺序），优化单个参数，范围 `[V×0.5, V×1.5]` 步长 `V×0.05` (`Optimization=1`)，同时固定其他 `.set` 输入，固定其最佳值，然后继续。使用精确的完整输入集运行最终回测，以保存最终候选者的输入。

### 最终候选者
`evaluate_finalist`：优于第 2 轮 **且** 利润 ≥4× 存款 **且** 最差 DD ≤12%。 → 复制到 *最终候选者* 并附带 `<bot>.set`。

## 跨轮次自我学习

`learnings.json` 累积，每个运行：参数平均利润改进（重新排序第 3 轮优化，以便最影响的参数首先尝试），符号优先级（每个作为最佳货币对出现的频率），以及每个机器人的裁决。这使得选择在每个循环中更快地收敛。确定性 — 纯粹的聚合统计数据。

## 输出格式

- `leaderboard_<ts>.json` — 按利润从高到低排序的最终候选者列表 `{name, verdict, best_symbol, r2_profit, final_profit, final_dd_pct, lr, reason}`。
- `leaderboard_<ts>.md` — 相同于表格。
- `state.json` — 可恢复的每个机器人/每个轮次的检查点。

## 资源

- `scripts/mt5_batch_tester.py` — 管道协调器 + INI 构建器（CLI）。
- `scripts/parse_mt5_optimization.py` — 优化报告（XML/HTML）解析器 + 第 1 轮门槛。
- `scripts/parse_mt5_report.py` — 回测报告解析器 + 平衡系列指标。
- `scripts/mt5_learnings.py` — 跨运行学习存储。
- `scripts/mt5_common.py` — 共享解析辅助函数（EN/ES 标头，数字）。
- `references/mt5-cli-reference.md` — MT5 `[Tester]`/`[TesterInputs]` 键、枚举、报告格式和注意事项。
- `assets/pipeline_config.template.json` — 带有占位符的配置模板。

## 关键原则

1. **永远不要提交个人路径** — 文件夹/终端来自配置/ENV/参数。
2. **相对 `Report=` 名称**，因为构建 6061 忽略绝对报告路径；从终端数据目录收集完成的报告。
3. **真实 tick (`Model=4`)** 需要交易商 tick 数据；它很慢 — 预期运行时间很长。
4. **可恢复**：每轮都会检查点；`--resume` 仅重用匹配指纹的工作并重试执行错误。
5. **失败关闭**：不完整、超时、陈旧或无法解析的报告永远不会拒绝、提升或移动候选者。每个唯一的第 1 轮符号必须完成。
6. **单一 MT5 所有者**：为每个共享的 MT5 数据文件夹在整个进程生命周期中保留一个操作系统锁。如果无法确认子进程终止，整个运行将停止并写入 `.blocked` 标记；手动删除该标记之前，请验证记录的 PID/进程树已退出。
7. **完整周期指标**：在开始、结束或跨完整一年没有交易的月份仍然是配置测试周期的一部分。
8. **每个循环学习**：参数/符号统计数据使未来的运行更倾向于胜利。
9. **验证你的构建**：报告布局（尤其是交易表格）和 32 ms 延迟映射可能不同 — 请参阅参考中的 *(verify)* 注释。
