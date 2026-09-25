# 致癌性

结合突变测试和necessist（测试语句移除）与代码图分析，将发现结果分类为可操作的类别：误报、缺失单元测试和模糊测试目标。

## 使用场景

- 突变测试揭示需要分类的幸存突变体后
- 确定单元测试应具有最高影响的区域
- 查找需要模糊测试框架而不是单元测试的函数
- 使用数据流上下文优先考虑测试改进
- 从可操作结果中过滤出无害突变体
- 查找不必要的测试语句，表明断言较弱（necessist）

## 不应使用场景

- 代码库没有现有的测试套件（先编写测试）
- 纯粹的文档或配置更改
- 单文件脚本具有简单逻辑

## 前置条件

- **trailmark**已安装 — 如果`uv run trailmark`失败，请运行：
  ```bash
  uv tool install trailmark
# Python代码片段：uv run --with trailmark python - （工具环境不可导入）
  ```
  **不要**将"手动验证"或"手动分析"作为运行trailmark的替代方案。先安装它。如果安装失败，请报告错误而不是切换到手动分析。
- 目标语言的**突变测试框架** — 如果框架命令失败（找不到、未安装），请使用[references/mutation-frameworks.md](references/mutation-frameworks.md)中的说明安装它。
  **不要**切换到"手动突变分析"或跳过突变测试。先安装框架。如果安装失败，请报告错误而不是切换到手动突变分析。
- **necessist**（可选，推荐） — 如果目标语言受支持（Go、Rust、Solidity/Foundry、TypeScript/Hardhat、TypeScript/Vitest、Rust/Anchor），请使用`cargo install necessist`安装。
  请参阅[references/mutation-frameworks.md](references/mutation-frameworks.md)了解详细信息。
- 现有的通过测试套件
- **macOS环境**：在任何`mull-runner`调用之前运行`ulimit -n 1024`。macOS Tahoe（26+）默认设置无限文件描述符，这会导致Mull的子进程创建崩溃。请参阅[references/mutation-frameworks.md](references/mutation-frameworks.md)了解详细信息。

---

## 拒绝理由

| 拒绝理由 | 为什么错误 | 必要操作 |
|----------|----------|----------|
| "所有幸存的突变体都需要测试" | 许多是无害的或等效的 | 分类后再编写测试 |
| "突变测试太嘈杂" | 噪声意味着你没有进行分类 | 使用图形数据过滤 |
| "单元测试涵盖所有内容" | 复杂的数据流需要模糊测试 | 检查入口点可达性 |
| "死代码突变体不重要" | 死代码应该被移除 | 标记为清理 |
| "低复杂度=低风险" | 边界错误隐藏在简单代码中 | 检查突变体位置 |
| "工具未安装，我会手动操作" | 手动分析遗漏了工具捕获的内容 | 先安装工具 |
| "Necessist不是突变测试，跳过它" | Necessist发现突变测试遗漏的内容：弱测试 | 当语言支持时同时运行 |

---

## 快速入门

```bash
# 1. 构建代码图
uv run trailmark analyze --language auto --summary {targetDir}

# 2. 运行突变测试（语言相关）
# Python:
uv run mutmut run --paths-to-mutate {targetDir}/src
uv run mutmut results

# 2b. 运行necessist（如果语言支持）
necessist

# 3. 使用此技能的工作流分析结果（第3阶段）
```

---

## 工作流概述

```
第1阶段：图构建      → 使用trailmark解析代码库
      ↓
第2阶段：突变运行     → 执行突变测试框架
第2b阶段：Necessist运行   → 移除测试语句（可选，并行）
      ↓
第3阶段：分类         → 使用图形数据分类发现结果
      ↓
输出：分类报告
  ├── 已证实         （两个工具标记相同函数 — 最高价值）
  ├── 误报          （无害的，跳过）
  ├── 缺失测试        （编写单元测试）
  └── 模糊测试目标      （设置模糊测试框架）
```

---

## 决策树

```
├─ 需要为语言设置突变测试？
│  └─ 阅读：references/mutation-frameworks.md
│
├─ 需要设置necessist或查找弱测试语句？
│  └─ 阅读：references/mutation-frameworks.md（Necessist部分）
│
├─ 需要深入了解分类标准？
│  └─ 阅读：references/triage-methodology.md
│
├─ 需要了解图形数据如何指导分类？
│  └─ 阅读：references/graph-analysis.md
│
└─ 已有结果+图形？使用下方的第3阶段。
```

---

## 第1阶段：构建代码图和运行预分析

使用trailmark解析目标代码库并在突变测试之前运行预分析。预分析计算爆炸半径、入口点、权限边界和污染传播，第3阶段将使用这些数据分类。

```bash
uv run trailmark analyze --language auto --summary {targetDir}
```

使用`QueryEngine` API构建图形并运行预分析：
1. `QueryEngine.from_directory("{targetDir}", language="auto")`
2. 调用`engine.preanalysis()` — **必须**在分类之前
3. 导出`engine.to_json()`以与突变结果进行交叉引用

如果目标语言的自动检测错误，请使用显式语言或逗号分隔列表（如`python,rust`）重新运行。

请参阅[references/graph-analysis.md](references/graph-analysis.md)了解完整的API：节点映射、可达性查询、爆炸半径和预分析子图查找。

---

## 第2阶段：运行突变测试

选择并运行适当的框架。请参阅[references/mutation-frameworks.md](references/mutation-frameworks.md)了解语言特定的设置。

**捕获幸存的突变体。** 每个框架报告方式不同，但按每个突变体提取以下字段：

| 字段 | 描述 |
|------|------|
| 文件路径 | 包含突变体的源文件 |
| 行号 | 应用突变体的行 |
| 突变类型 | 修改了什么（运算符、值等） |
| 状态 | 幸存、杀死、超时、错误 |

仅过滤**幸存**的突变体用于第3阶段。

---

## 第2b阶段：运行Necessist（可选）

如果目标语言受支持（Go、Rust、Solidity/Foundry、TypeScript/Hardhat、TypeScript/Vitest、Rust/Anchor），请运行necessist以查找不必要的测试语句。这独立于第2阶段运行，可以并行执行。

```bash
# 自动检测框架
necessist

# 或目标特定测试文件
necessist tests/test_parser.rs

# 导出结果
necessist --dump
```

过滤到测试**移除后通过**的结果。请参阅[references/mutation-frameworks.md](references/mutation-frameworks.md)了解框架特定的配置和标准化记录格式。

使用[references/graph-analysis.md](references/graph-analysis.md)中描述的算法将每个移除映射到生产函数。

---

## 第3阶段：分类发现结果

对于每个幸存的突变体和每个necessist移除，使用图形数据确定其分类桶。Necessist移除必须首先映射到生产函数（请参阅[references/graph-analysis.md](references/graph-analysis.md)）。

### 快速分类（突变测试）

| 信号 | 桶 | 理由 |
|------|------|------|
| 图中没有调用者 | **误报** | 死代码，突变体不可达 |
| 仅测试调用者 | **误报** | 测试基础设施，不是生产 |
| 日志/显示字符串 | **误报** | 修饰性的，没有行为影响 |
| 等效突变体 | **误报** | 尽管突变，行为未改变 |
| 简单函数，低CC，没有入口点路径 | **缺失测试** | 单元测试很简单 |
| 错误处理路径 | **缺失测试** | 应该有负面测试用例 |
| 边界条件（off-by-one） | **缺失测试** | 属性基础测试候选 |
| 纯函数，确定性 | **缺失测试** | 容易测试，高价值 |
| 高CC（>10），入口点可达 | **模糊测试目标** | 复杂+暴露=模糊它 |
| 解析器/验证器/反序列化器 | **模糊测试目标** | 结构化输入处理 |
| 调用者数量（>10）+中等CC | **模糊测试目标** | 高爆炸半径 |
| 二进制/线路协议处理 | **模糊测试目标** | 模糊器擅长格式测试 |

### 快速分类（Necessist）

| 信号 | 桶 | 理由 |
|------|------|------|
| 重复设置或调试调用 | **误报** | 语句确实不必要 |
| 无法映射到生产函数 | **误报** | 没有图形上下文进行分类 |
| 调用移除，没有断言检查其效果 | **缺失测试** | 测试具有弱断言 |
| 断言移除，测试仍然通过 | **缺失测试** | 重复或覆盖不足 |
| 映射到高CC入口点可达函数 | **模糊测试目标** | 复杂+暴露+弱测试 |

当突变测试和necessist标记相同的生产行为时，标记为**已证实** — 最高置信度发现。

有关详细标准，请参阅[references/triage-methodology.md](references/triage-methodology.md)。

### 分类图形查询

对于每个突变体，将其映射到其包含的图形节点，并使用第1阶段的预分析子图（污染、高_blast_radius、权限边界）进行分类。分类逻辑检查：没有调用者→误报，权限边界→模糊测试，高CC+污染→模糊测试，高爆炸半径→模糊测试，否则→缺失测试。

请参阅[references/graph-analysis.md](references/graph-analysis.md)了解`batch_triage`实现和节点映射函数。

---

## 输出格式

生成markdown报告：

```markdown
# Genotoxic分类报告

## 摘要
- 总幸存突变体：N
- 总necessist移除：N
- 已证实发现：N
- 误报：N (N%)
- 缺失测试覆盖：N (N%)
- 模糊测试目标：N (N%)

## 已证实发现
| 文件 | 行 | 函数 | 突变信号 | Necessist信号 | 操作 |
|------|------|------|----------|----------------|------|

## 误报
| 文件 | 行 | 突变 | 理由 | 来源 |
|------|------|------|------|------|

## 缺失测试覆盖
| 文件 | 行 | 函数 | CC | 调用者 | 建议测试 | 来源 |
|------|------|------|----|---------|----------------|------|

## 模糊测试目标
| 文件 | 行 | 函数 | CC | 入口点路径 | 爆炸半径 | 来源 |
|------|------|------|----|-----------------|--------------|------|
```

`来源`列是`mutation`、`necessist`或`已证实`。

将报告写入工作目录中的`GENOTOXIC_REPORT.md`。

---

## 质量检查清单

交付前：

- [ ] 为目标语言构建了trailmark图形
- [ ] 突变框架运行完成
- [ ] 运行了necessist（如果语言支持）或注明不适用
- [ ] 所有幸存的突变体已分类（无未分类项）
- [ ] 所有necessist移除已分类（如适用）
- [ ] 已识别已证实发现（如果两个工具都运行）
- [ ] 误报具有明确理由
- [ ] 缺失测试项包括建议的测试类型
- [ ] 模糊测试目标包括入口点路径和爆炸半径
- [ ] 报告文件写入`GENOTOXIC_REPORT.md`
- [ ] 通知用户总结统计数据

---

## 集成

**trailmark技能：**
- 第1阶段：构建代码图，查询复杂性和入口点
- 第3阶段：调用者分析，可达性，爆炸半径

**property-based-testing技能：**
- 涉及边界条件的缺失测试覆盖项
- 序列化突变体的往返/幂等属性

**testing-handbook-skills（模糊测试）：**
- 模糊测试目标项：使用`harness-writing`、`cargo-fuzz`、`atheris`

---

## 支持文档

- **[references/mutation-frameworks.md](references/mutation-frameworks.md)** -
  语言特定框架设置、输出解析和necessist配置
- **[references/triage-methodology.md](references/triage-methodology.md)** -
  详细的分类标准、边缘情况和突变测试及necessist的示例
- **[references/graph-analysis.md](references/graph-analysis.md)** -
  图形查询模式、测试到生产映射和结果合并

---

**首次用户：** 从第1阶段（图形构建）开始，然后运行突变，然后使用第3阶段中的快速分类表。

**有经验的用户：** 跳到第3阶段并使用决策树加载特定参考材料。
