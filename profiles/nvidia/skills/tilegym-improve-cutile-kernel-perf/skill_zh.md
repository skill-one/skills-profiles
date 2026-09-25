# 迭代 cuTile 内核性能优化
在 TileGym 存储库中，系统性地分析、诊断瓶颈，并迭代调优 cuTile 内核的性能。

## 指南

按顺序遵循三个阶段：**设置**环境与基线，运行**实验**循环并记录日志，然后迭代**实验循环**直至性能目标达成或进一步提升趋于平稳。

## 设置
与用户合作准备优化环境：
1. 创建一个干净的 git 分支：建议分支名称，例如 `cutile-perf-<内核名称>-<日期>` 从当前分支创建。执行 `git checkout -b <分支名称>`
2. 定位目标内核：
   - cuTile 内核位于 `src/tilegym/suites/<套件>/cutile/` 或 `src/tilegym/ops/cutile/`
   - 阅读内核文件并识别：`@ct.kernel` 装饰的函数、启动包装器 (`ct.launch()` 或 `ct_experimental.autotune_launch()`)、`@register_impl` 注册以及当前的自动调优配置（如有）
3. 分类内核：
   - 算术强度 < 10 -> 内存受限
   - 算术强度 10-50 -> 平衡
   - 算术强度 > 50 -> 计算受限

   注意：分类仅用于实验循环中优化优先级的选择。**核心指标**始终是 `延迟 (ms)`。
4. 检查 GPU 环境：
   - 确保可用的 GPU 节点（Blackwell 或 Ampere GPU）
   - 所有后续基准测试命令应在 GPU 节点上运行
5. 研究相关参考：
   - `references/optimization-playbook.md`：每个优化的分步食谱（A 至 J），附带前后代码示例
   - `references/perf-knobs-catalog.md`：所有可调参数的完整目录（TMA、持久调度、占用率、瓦片大小、延迟提示等）
   - `references/cutile-api-reference.md`：cuTile API 参考和 18 条关键规则
   - `references/performance-model.md`：屋顶线/性能模型、瓶颈诊断、自动调优
   - `references/ir-dump-guide.md`：IR 倾倒、分析及错误诊断
   - `references/cutile-patterns-reference.md`：常见 cuTile 模式和转换快速参考
6. 创建 @sandbox/perf_results.md 以跟踪进度。首次运行将写入基线
7. 确认并开始：一旦获得确认，即可启动实验

## 实验
每次实验迭代对目标内核应用一项优化，验证正确性，重新基准测试并记录结果。每次迭代应强制在 10 分钟内完成。

### 目标
- 提升**核心指标**：降低 `延迟 (ms)`
- 遵循**核心约束**：正确性不得倒退 — 每项优化必须保持数值正确性。与基线相比，`延迟 (ms)` 不得倒退 > 2%

### 可更改项
- `src/tilegym/suites/<套件>/cutile/` 或 `src/tilegym/ops/cutile/` 下的目标内核文件：内核主体、瓦片大小、占用率、num_ctas、TMA 使用、延迟提示、flush_to_zero、自动调优配置、持久调度以及其他 cuTile 特定参数
- 内核的启动包装器：网格计算、自动调优配置空间
- @sandbox/：可自由添加新文件或修改您创建的文件，但无需提交到 git

### 不可更改项
- 内核功能语义（输入、输出和容差内的数值行为）
- 测试基础设施和基准测试框架
- 以上未列出的任何内容

### 实验输出预期

#### 正确性测试：
```bash
python -m pytest tests/suites/.../test_<内核名称>.py -k "test_ and cutile and not test_perf" -v
```

#### 性能基准测试：
每次迭代：
1. 运行 pytest 基准测试：`python -m pytest ... --print-record` → 提取延迟 (ms)
2. 在 perf_results.md 中记录延迟

基准测试命令：
```bash
python -m pytest tests/suites/.../test_<内核名称>.py -k "test_perf and cutile" --print-record -v
```

延迟示例：
```
Cutile: {'forward': {'mean': 3.7903138461538455, 'std': 0.0016941310873207053, 'rel_std': 0.044696327430505396, 'median': 3.789880999999999, 'min': 3.7883389999999992, 'max': 3.7941230000000004, 'nrep': 13, 'peak_mem_mb': 913}} ms
```

### 跟踪实验进度
使用 @sandbox/perf_results.md 记录每次迭代的結果。它应仅包含一个 5 列的 Markdown 表格：
- `iteration`：迭代编号，从 0（基线）开始
- `optimization`：应用的内容（例如，"基线"、"TMA 替换 gather"、"持久调度")
- `latency_ms`：内核延迟（毫秒），六位小数
- `correctness`：PASS 或 FAIL
- `status`：迭代是否为 `keep`、`revert` 或 `crash`

示例内容：

```markdown
| iteration | optimization       | latency_ms | correctness | status |
|----------:|:-------------------|-----------:|:------------|-------:|
| 0         | baseline           |   0.820000 | PASS        | keep   |
| 1         | TMA replace gather |   0.390000 | PASS        | keep   |
```

如果文件为空，则创建表格标题。为每次迭代追加一行。

### 基线
第一次迭代（迭代 0）将不会更改任何代码，仅运行正确性测试和性能基准测试。结果将列在第一行作为基线。

## 实验循环
核心方法是为每次迭代从食谱中应用一项优化，验证正确性，基准测试，并决定是否保留或回滚。一次尝试一项优化，并保持干净的实验记录。

循环：
1. 检查 git 状态：当前所在的 git 分支/提交
2. 从 `references/optimization-playbook.md` 选择并应用一项优化：
3. 验证正确性 — 如果失败，**立即回滚**。常见原因：`flush_to_zero`/`rounding_mode=APPROX` 改变了结果、瓦片大小越界、`allow_tma=False` 语义、持久循环边界错误
4. 重新基准测试并与当前基线比较
5. git 提交
6. 在 @sandbox/perf_results.md 中记录结果
7. 决策规则：

   | 结果       | 动作       |
   |-----------|-----------|
   | 提升(`延迟 (ms)`) >= 5% | 接受为新基线，继续 |
   | 提升 2-5%  | 接受，下一迭代优先级降低 |
   | 提升 < 2%  | 接受但停止，除非用户要求更多 |
   | 任何配置上的倒退 | 立即回滚，尝试下一项优化 |
   | 连续两次迭代无改进 | 停止 |
   | 根本原因是 `调度` 或 `未知` | 升级至用户 |

9. 如果保留，更新基线编号并继续循环
10. 如果回滚，git reset 回到开始位置，并按优先级顺序尝试下一项优化
UNTIL：所有尝试完成，或超过 25 次迭代，或用户中断

*保持自主性*：在设置阶段询问用户澄清。一旦进入实验循环，不要暂停以请求用户反馈：使用最佳判断进行决策，及时参考优化食谱和性能参数目录，如果卡住则深入思考。
