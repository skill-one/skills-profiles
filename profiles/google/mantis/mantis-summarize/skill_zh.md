# 总结器 (/mantis-summarize)

## 系统目标

仓库映射器。自动化生成以安全为中心的确定性目录内容摘要，以减少下游规划和研究阶段的令牌开销。

## 命令定义

- **命令:** `/mantis-summarize`
- **描述:** 通过为每个目录生成以安全为中心的摘要（`mantis-summary.md`）来预处理仓库，以提高规划和研究的效率。
- **参数（可选；由协调器提供，由区块A消费）:**
  `--snapshot_root`/`--snapshot_id`/`--state_root`。在PINNED模式下，源代码在CODE_ROOT下读取，但摘要将被跳过（见输出位置）。全部缺失 → 模式关闭（树内摘要，如今天所见）。

## 输入/输出契约

- **读取**:
  - `workspace/.mantis_state.json`（用于跟踪当前循环遍历）。
  - 代码库目录和源文件（排除`node_modules`、`vendor`、`.git`、构建输出和`tests/`）。
  - 子目录摘要（来自子目录的`mantis-summary.md`文件）。
  - `workspace/historical_learnings.jsonl`（可选，用于丰富摘要）。
- **写入**:
  - 遍历脚本到工作区。
  - 模式关闭：每个源目录中的`mantis-summary.md`（如今天所见）。PINNED：跳过（见输出位置）。
- **前提条件**:
  - 源文件和目录结构必须存在。
- **幂等性保证**:
  - 确定性地就地覆盖现有的`mantis-summary.md`文件，并更新汇总。

## 说明

### 第0步：定位器解析 + 输出位置（首先运行）

```
定位器解析（在读取任何目标代码或工件之前）：
0. 角色：如果此技能永远不会读取目标源代码（报告、校准、反映），则您是一个仅查找结果的阶段：跳过步骤2-6；仍然从状态中读取active_snapshot以进行溯源/注释；仅因代码根未设置而永远不会停止。
1. 确定CODE_ROOT，按此优先级顺序：
   a. 如果在本次调用中传递了`--target_root`，CODE_ROOT = `--target_root`。它是权威的，并覆盖SNAPSHOT_ROOT和状态回退（用于调用者传递准备好的树，例如一个补丁阴影）。
   b. 否则，如果传递了`--snapshot_root`（或SNAPSHOT_ROOT），使用它。
   c. 否则读取`state_root/workspace/.mantis_state.json`（如果传递了`--state_root`，则使用`--state_root`，否则相对于当前目录的`./workspace/...`）-> active_snapshot.root / .snapshot_id / .snapshot_pinned。
   d. 否则（无参数且无可读的active_snapshot）：CODE_ROOT = 当前目录，将snapshot_pinned = false（模式关闭）。不要停止。
2. 信号检查（仅当snapshot_pinned为true且您未采取路径1a时）：
   验证CODE_ROOT/.mantis_snapshot_id存在且等于SNAPSHOT_ID。如果缺失或不同 -> 停止“snapshot信号不匹配”。（一个`--target_root`树（1a）是故意被修改的，并且是信号豁免的。）
3. 路径字段：
   - SNAPSHOT-相对（在CODE_ROOT下读取）：code_paths条目；计划目标文件，这些是文件路径。仅删除尾部的":<数字>"。包含"://"的code_paths条目是URL/端点，不是文件读取。不是以<现有路径>:<整数>形式的code_paths条目是非源定位器（符号/偏移/端点）：仅检查工件/符号是否存在；跳过所有行范围和行存在逻辑。
   - STATE-相对（在state_root/workspace下读取/写入，永远不会以CODE_ROOT为前缀）：
     kb_references、repro_file_path、reattack_file_path、辅助脚本、报告文件以及所有状态/查找JSON。
4. 当snapshot_pinned为true时，永远不要在CODE_ROOT下写入。任何编译、生成或写入工件的命令都必须在从CODE_ROOT创建的私有阴影副本中运行（使用`mktemp -d`从CODE_ROOT），永远不要以cwd=CODE_ROOT运行。只读检查可以cd到CODE_ROOT。
5. VCS-METADATA切割：历史记录日志提取和任何VCS diff/blame命令在LIVE仓库根目录（仍然有`.git`/.hg/.repo）下运行，而不是CODE_ROOT（快照副本会删除VCS元数据）。不要因为CODE_ROOT缺少`.git`/.hg/.repo而停止。
6. 每个shell命令使用绝对路径，并在该调用上设置自己的工作目录。不要假设工作目录在调用之间持久存在。
```

输出位置（强制）：

- PINNED模式（snapshot_pinned为true）：本次遍历中摘要将被**跳过**。在PINNED模式下，CODE_ROOT是只读的（区块A步骤4），消费者（计划、历史、研究人员）从代码树中的源目录读取`mantis-summary.md`——而不是从状态相对镜像中读取。写入一个消费者不读取的镜像将默默地浪费工作。在PINNED模式下不要写入任何`mantis-summary.md`文件。（如果未来更改将消费者连接到镜像并通过溯源标记重新映射，可以重新考虑；目前，PINNED模式的摘要是无活力的。）
- HALT模式（active_snapshot存在 + snapshot_pinned=false）：行为如MODE-OFF（将`mantis-summary.md`写入每个源目录）。快照不是只读的（没有不可变的副本被固定），因此写入树是安全的。
- 模式关闭（没有`active_snapshot`——今天的默认值）：行为与今天完全相同——将`mantis-summary.md`写入每个源目录。
- 在所有非PINNED模式下，`mantis-summary.md`文件必须对每个VCS脏检查都不可见，并且在任何同步之前从目标树中删除（元代理在区块C步骤0中强制执行此操作）。永远不要让摘要使树看起来脏。

您的任务是编写并执行一个脚本，该脚本将遍历仓库目录树，并在每个包含源代码的目录中创建一个`mantis-summary.md`文件。

这是一个**可选的预处理阶段**，旨在大幅减少策略师（`/mantis-plan`）所需的上下文窗口大小，并为研究人员（`/mantis-researcher`）提供快速参考地图。

按以下方式执行总结阶段：

1. **编写遍历脚本（自下而上分层）**：在工作区中编写一个脚本（例如Python或bash），使用**自下而上（后序）遍历**遍历仓库目录树。

   - 脚本必须忽略非源代码目录，例如`node_modules`、`vendor`、`.git`、构建输出和`tests/`。
   - 通过自下而上的遍历，脚本确保子目录在父目录之前被总结。
   - 当分析一个目录时，脚本应将LLM传递给该目录中的本地源文件**加上**其直接子目录的`mantis-summary.md`文件。不要将子目录的原始源文件传递给父目录。
   - 当分析非常大的目录时，上下文窗口大小可能会成为问题。不要一次性传递文件和目录摘要，而是生成每个文件的摘要或以更高效的方式操作，以避免传递过多令牌给LLM处理。

2. **生成安全摘要（映射-归约）**：脚本应读取`workspace/historical_learnings.jsonl`（如果存在），以检查当前目录中文件的历史漏洞和安全修复，并将它们作为上下文传递。脚本应指示LLM或代理工具生成目录的简洁、以安全为中心的摘要。为了在目录树的较高层级保持合理的令牌长度，LLM应抽象掉较低级别的细节，专注于汇总的架构。您的脚本使用的提示应要求：

   - **核心组件**：主要文件和子目录是什么，它们做什么？
   - **API端点 & 导出**：哪些函数或类被暴露给其他模块？
   - **信任边界 & 外部输入**：此目录是否处理不受信任的数据、网络请求或用户输入？
   - **敏感操作**：是否有解析器、加密函数或内存管理操作？
   - **历史漏洞 & 修复**：此目录中的哪些文件或组件在`workspace/historical_learnings.jsonl`中记录了历史漏洞或与安全相关的修复？总结过去的修复、受影响的组件和漏洞类别，以突出过去的回归或反复出现的弱点。

   摘要必须足够合理，可以纳入较大问题的处理中，因此目标应为一两万字或更少。

3. **输出到`mantis-summary.md`**：在模式关闭（或HALT）中，将`mantis-summary.md`写入相应的源目录（如果存在则覆盖）。在PINNED模式下，不要写入——摘要本次遍历中将被跳过（见上述输出位置）。永远不要写入只读快照。

4. **执行脚本**：运行您刚刚编写的脚本以生成整个仓库的所有摘要。等待它成功完成。

5. **完成**：摘要现在已生成。通知用户。

当完成时，通知用户。
