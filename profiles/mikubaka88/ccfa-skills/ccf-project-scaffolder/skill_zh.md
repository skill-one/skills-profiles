# CCF 项目脚手架

## 家族文件契约

在编写前，确定每个任务/产物的规范输出和一个稳定的 working directory。复用显式或已建立的任务路径；否则使用项目根目录 `ccfa-workfiles/<用途>/<产物ID>/`，仅在需要时包含 `source/`、`assets/`、`cache/` 和 `build/`。就地更新当前文件；不要分散中间产物或创建迭代副本。保留输入和所需证据；仅清理此任务创建的已验证可丢弃文件。使用 UTF-8 文本 I/O，并在保存或渲染后检查中文文本。对于文件工作，应用 [artifact-contracts.md](../ccf-common/references/artifact-contracts.md) 并在技能转换中复用相同路径。

## 协作契约

在专家执行前，先阅读并应用 [ccf-humanization](../ccf-humanization/SKILL.md)，然后应用 [ccf-common](../ccf-common/SKILL.md)。在每次交接时，复用其适用的活跃规则或刷新缺失/变更的规则。即使没有文本，这两个预检也是必需的；详细的编辑、实验和维护模式仅在相关时运行。

保留一个集成负责人，并积极使用其他技能来解决问题或检查材料发现。复用适用证据；不要跳过必要的准备工作以节省 token。在最终确定前，集成贡献并验证受影响的成果。遵循条件性 [合作路线](../ccf-common/references/routing.md)；避免无关阶段和重复报告。

## 调用控制

**CCFA 交接模式：PARTIAL（推荐）**。遵循 `metadata.ccf_skill_controls.handoff_question_mode`、`../ccf-common/references/handoff-modes.md` 和 `../ccf-common/references/task-modes.md`。一个脚手架请求授权必要的本地结构；一个 dry-run 或 no-new-files 请求会相应限制变更。

## 核心规则

创建请求的项目结构、模板和状态，不要编造研究内容。保留现有用户文件并补全兼容的缺失部分，而不是替换一个已建立的项目。

## 工作流

1. 从对话和文件系统中确定项目位置、场所、请求的文件夹和现有产物。推断常规目录名称；仅询问一个未解决的最终位置或覆盖选择。
2. 通过 `../ccf-paper-writer/references/venue-guides/index.md` 选择匹配的模板。验证模板及其支持的风格/资源是否可用。在请求时使用提供的模板；精确识别不可用的依赖项，而不是复制一个不完整的模板。
3. 通过 `../ccf-common/references/artifact-contracts.md` 确定最终产物和工作根。仅创建需要的目录和模板，按需包含 source/assets/cache/build 子目录。保留现有布局；不要迁移用户文件或覆盖手稿、参考文献或配置以刷新脚手架。
4. 如果 `ccfa.yaml` 缺失且请求初始化，则复制 `assets/ccfa.yaml`，在 `../ccf-common/references/ccfa-yaml-contract.md` 中保留必需字段，并仅填充提供的项目元数据。仅在请求范围内读取和更新现有状态；未知的研究字段保持显式占位符。
5. 检查创建的路径、模板引用和 YAML。当请求可运行模板且引擎可用时，构建是有用的；不要为目录设置运行研究实验或最终提交检查。
6. 报告实际创建/更新的路径和任何具体的缺失依赖项。对于 dry run，返回建议的树和操作，而无需写入文件。

## 边界

使用 `../ccf-common/references/artifact-contracts.md` 处理文件所有权。项目工作流规划属于 `ccf-pipeline-orchestrator`，手稿文本属于 `ccf-paper-writer`，最终包检查属于 `ccf-submission-checker`。不要编造标题、摘要、主张、实验或引用。
