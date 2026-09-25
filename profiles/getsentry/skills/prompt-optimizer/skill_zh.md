# 提示优化器

使用 evals 优化提示。保留所有指令、示例和外部上下文引用的因果关系。

## 只加载所需内容

| 需求 | 读取 |
|------|------|
| 新提示 | `references/core-patterns.md`、`references/model-family-notes.md`、`references/transformed-examples.md` |
| 现有提示 | `references/meta-optimization-loop.md`、`references/core-patterns.md`、`references/model-family-notes.md` |
| 模型族端口 | `references/model-family-notes.md`、`references/core-patterns.md` |
| 重复失败 | `references/meta-optimization-loop.md`、`references/core-patterns.md` |
| 弱或模糊的草稿 | `references/transformed-examples.md` |
| 起源 | `SOURCES.md` |

## 第 1 步：捕获合约

编辑前记录：

- 任务类型：新建、优化、端口或调试
- 目标模型族和快照（如果已知）
- 提示表面：`system`、`developer`、`user`、工具描述、示例、模式
- 层级所有者：平台、部署者/角色、检索的上下文、用户有效负载
- 目标和非目标
- 输入、工具和可用外部文件
- 所需输出形状
- 成功标准和失败案例
- 硬性约束：延迟、冗长性、安全性、预算、工具使用、风格

如果成功标准或示例缺失，请先创建一个小型 eval 集合。
如果瓶颈是模型选择、检索、工具模式或缺失 evals，请在重写前说明。

## 第 2 步：盘点外部上下文

对于仓库或代理提示，按确切路径列出稳定上下文：

| 上下文类型 | 示例 |
|--------------|----------|
| 代理规则 | `AGENTS.md`、`CLAUDE.md` |
| 规格 | `specs/*.md`、`docs/api.md` |
| 政策 | `SECURITY.md`、`docs/releasing.md` |
| 示例 | `examples/`、`tests/fixtures/` |

规则：

- 通过仓库相对路径引用稳定文件，而不是复制它们。
- 仅粘贴提示或 eval 案例所需的片段。
- 标记文件是否为 `loaded`、`referenced` 或 `超出范围`。
- 避免模糊的上下文指针，例如“阅读文档”。

## 第 3 步：选择模型策略

阅读 `references/model-family-notes.md`。

- 已知族：针对该族进行优化。
- 未知族：编写可移植的基座并附上简短的适配器说明。
- 快照变更：重新运行 evals。
- 跨族差异：仅针对失败的层级进行专门化。

## 第 4 步：塑形提示

阅读 `references/core-patterns.md`。

- 将稳定政策放在 `system` 或 `developer` 中。
- 将任务本地事实、检索的上下文和变量放在用户界面部分。
- 每个行为规则保留一个所有者。
- 仅使用标题或标签来分隔内容类型。
- 将工具政策放在提示文本中；将模式保留在提供者原生工具中。
- 除非改变行为，否则保持角色轻量。
- 使用最短的措辞来保留约束。
- 删除填充、重复提醒、无效示例和不影响 evals 的推理。

## 第 5 步：优化

阅读 `references/meta-optimization-loop.md` 以进行改进。

1. 在相同的 eval 切片上对当前提示进行基线。
2. 按根本原因对失败进行聚类。
3. 写出具体的编辑批评。
4. 生成两个到四个候选者：
   - 最小差异修复
   - 结构优先重写
   - 示例优先或工具规则变体
   - 当需要时提供者适配器
5. 在相同案例上比较候选者。
6. 保持简短的优化日志。
7. 在保留案例上验证获胜者。
8. 在平台期、振荡、过拟合、过度成本或非提示瓶颈时停止。

## 第 6 步：返回包

返回：

1. `目标`
2. `成功标准`
3. `外部上下文`
4. `优化提示`
5. `适配器说明`
6. `Eval 集合`
7. `优化日志`
8. `残余风险`

对于现有提示，包括主要行为变更的简洁差异式说明。

## 失败模式

- 在定义 eval 目标前进行编辑
- 无边界地混合政策、示例和原始上下文
- 在各层级间重复规则
- 将持久政策放在用户有效负载中
- 要求思维链
- 保留矛盾的遗留指令
- 过拟合一个或两个示例
- 保留不再提高 evals 的示例
- 仅在提示文本中修复工具使用失败，而工具描述或模式薄弱
- 添加不减少歧义的标记
- 将角色作为行为规则的替代品
