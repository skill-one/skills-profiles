# 变异测试 (mewt/muton)

引导至正确的变异测试工作流程并加载该工作流程所需的参考。

> **注意**: muton 和 mewt 具有完全相同的接口。示例使用 `mewt`；对于 muton 项目，请替换为 `muton` 及其文件名 (`muton.toml`, `muton.sqlite`)。

`mewt --help` 和 `mewt <子命令> --help` 是命令行行为的权威来源。以下示例反映 mewt 4.x API；当某个标志看起来不熟悉或命令失败时，请运行 `--help`。

## 使用场景

当用户：
- 提及 "mewt"、"muton" 或 "变异测试"
- 希望配置、范围界定或加速变异测试活动
- 希望分析变异结果——存活/未捕获变异体、等价变异体、杀伤率
- 希望使用变异结果在源代码中查找错误

时，使用此技能。

## 不适用场景

当用户在不涉及变异测试上下文的情况下询问测试或行覆盖率时，不要使用此技能。

---

## 工作流程选择

选择工作流程，然后加载为其列出的参考。工作流程和参考不会相互加载——该决策在此处做出。

**设置、范围界定或加速活动**
→ [workflows/configuration.md](workflows/configuration.md)
→ 当活动估算时间足够长需要裁剪，或用户要求使其更快时，也加载 [references/optimization-strategies.md](references/optimization-strategies.md)。

**活动完成，在未测试代码中查找错误**
→ [workflows/bug-hunter.md](workflows/bug-hunter.md)

**将结果转换为正式分析报告**
→ [workflows/analyzing-results.md](workflows/analyzing-results.md)，此外：
- [references/equivalent-mutants.md](references/equivalent-mutants.md) — 等价目录和验证程序
- [references/severity-classification.md](references/severity-classification.md) — 严重性等级标准
- [references/report-template.md](references/report-template.md) — 报告结构
- [references/blockchain-patterns.md](references/blockchain-patterns.md) — **仅**适用于 Solidity、Move、FunC/Tolk、Cairo 或 Solana Rust 目标
- [references/input-formats.md](references/input-formats.md) — 除非结果来自 mewt 或 muton。外国工具输出可能无法自我描述；这涵盖了 slither-mutate、mull 和 dextool-mutate 的解析锚点

**其他情况** → 运行 `mewt --help` 或 `mewt <子命令> --help`，然后直接协助。

---

## 基本命令

```bash
# 设置和运行
mewt init                    # 创建配置和数据库
mewt mutate [paths]          # 生成变异体但不测试它们
mewt run [paths]             # 生成变异体并运行活动

# 读取结果
mewt status                  # 按文件分解的概览
mewt results                 # 未捕获变异体（默认视图）
mewt results --all           # 每种结果，而不仅仅是未捕获的
mewt results --format json   # json | sarif | ids | table

# 窄化范围（这些过滤器适用于 `results` 和 `print mutants`）
mewt results --target 'src/auth/**'   # 引号包围 glob 以防止 shell 展开
mewt results --severity high,medium
mewt results --mutation-types ER,CR
mewt results --status Uncaught        # Uncaught | TestFail | Skipped | Timeout
mewt results --line 42

# 调查和重新测试
mewt print mutant --id [id]              # 查看已变异的代码
mewt test --ids [ids]                    # 重新测试特定变异体
mewt test --ids-file uncaught_ids.txt    # 从文件中重新测试 IDs，或 '-' 表示 stdin

# 检查配置
mewt print config                        # 生效配置
mewt print targets                       # 实际被变异的文件
mewt print mutations --language [lang]   # 某种语言的变异和严重性
```

语言标签是 mewt 4.x 中的规范 `family` 或 `family/dialect` 值——例如 `rust`、`javascript/ts`、`move/sui`、`move/iota`。

---

## 结果含义

- **Caught/TestFail**: 测试检测到变异（良好）
- **Uncaught**: 测试未检测到变更。检查代码以区分测试差距与等价变异
- **Timeout**: 测试耗时过长——非结论性，不作为覆盖率证据
- **Skipped**: 由于同一行上存在更严重的变异体而跳过较不严重的变异体

---

## 解读变异类型

`mewt print mutations --language [lang]` 列出某种语言的每个变异 slug、描述和严重性，是权威的——操作集随每个版本增长。该输出并未说明存活变异体 *意味着什么*，这正是优先级排序的来源：

| 严重性 | 代表性 slugs | 未捕获变异体告诉你的信息 |
|----------|---------------------|-----------------------------------|
| 高 | `ER` (错误替换) | 测试容忍注入的错误。调查路径是否执行、错误处理是否掩盖了变更，以及断言是否检查了结果。 |
| 中 | `CR` (注释替换) | 删除语句不会导致测试失败。检查其效果是否重要以及断言是否观察到这些效果。 |
| 中 | `IF`/`IT` (如果假/真)、`NR` (否定移除) | 测试无法区分更改的条件。两种常量替换存活都可能指示未执行的路径或分支结果的弱断言。 |
| 低 | 运算符重排 (`AOS`、`COS`、`LOS`、`BOS`、移位/赋值变体)、`BL`、`AS`、`LC`、`WF` | 检查边界输入、算术断言和语义等价性。仅凭变异结果无法确定代码是否执行。 |

严重性排序的是 *变异*，不是风险。一个低严重性存活变异体在费用计算中比一个高严重性存活变异体在日志行中更重要——权衡变异代码的作用。使用 `--severity` 过滤以按优先级顺序处理结果。
