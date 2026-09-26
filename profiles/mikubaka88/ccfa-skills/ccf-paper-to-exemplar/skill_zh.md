# 从论文到范例

## 家庭文件合约

在撰写前，确定每个任务/成果的规范输出和一个稳定的 working directory。复用明确的或已建立的任务路径；否则使用项目根目录下的 `ccfa-workfiles/<用途>/<成果ID>/`，仅在需要时使用 `source/`、`assets/`、`cache/` 和 `build/`。就地更新当前文件；不要分散中间文件或创建迭代副本。保留输入和所需证据；仅清理此任务创建的已验证的可丢弃文件。使用 UTF-8 文本 I/O，并在保存或渲染后检查中文文本。对于文件工作，应用 [artifact-contracts.md](../ccf-common/references/artifact-contracts.md) 并在技能转换时复用相同的路径。

## 协作合约

在专家执行前，先阅读并应用 [ccf-humanization](../ccf-humanization/SKILL.md)，然后应用 [ccf-common](../ccf-common/SKILL.md)。在每次交接时，复用其适用的活跃规则或刷新缺失/变更的规则。即使没有文本，这两个预检也是必需的；详细的编辑、实验和维护模式仅在相关时运行。

保留一个集成的负责人，并积极使用其他技能来解决问题缺失的前提条件或检查材料发现。复用适用的证据；不要跳过必要的准备工作以节省 tokens。在最终确定前，集成贡献并验证受影响的成果。遵循条件性的 [合作路线](../ccf-common/references/routing.md)；避免无关的阶段和重复报告。

## 范围和共享控制

将提供的论文 PDF 提炼为可复用的写作模式，保留源归属和科学意义。此技能拥有范例卡片；手稿起草属于 `ccf-paper-writer`，视觉重建属于 `ccf-visual-composer`，科学审查属于 `ccf-paper-reviewer`。

遵循 `../ccf-common/references/handoff-modes.md`、`../ccf-common/references/task-modes.md` 和 `../ccf-common/references/artifact-contracts.md`。在撰写前解决现有的卡片/库和缓存路径。通过编辑命名的现有卡片或以上下文形式返回分析来保留“不创建新文件”请求。仅转换不授权全局库/默认变更。

## 工作流程

1. 确定论文路径、源版本、期望的写作模式、可选的会议和授权的输出目的地。当复用的卡片和提取匹配相同的源和请求范围时，复用它们；新的源版本需要检查受影响的分析。
2. 如果需要提取，运行 `scripts/convert.py` 并使用明确的 `--output-dir`、`--full-text` 和 `--full-text-dir` 指向选择的 working cache。对于新项目，共享默认值是 `ccfa-workfiles/exemplars/<source-id>/`，提取在 `cache/` 中；保留已建立的路径。转换器保留现有卡片并仅创建缺失的骨架。`--full-text-dir` 是可选的；省略它将保留传统的输出布局。提取需要 Python 和 `pymupdf`，而复用有效现有卡片不需要。
3. 检查提取成功和页面标记。在连贯的段落中分析相关的完整源；使用搜索和目标范围进行本地卡片更新。当方程式、图形或阅读顺序影响解释时，检查实际 PDF 页面。不要用仅包含摘要的分析代替完整论文范例，或把空提取视为完成。
4. 恢复源的叙事、摘要/引言/方法/证据的移动、引用模式和可复用技术。不要强制添加限制性结尾。使用 `../ccf-paper-writer/references/prose-quality-guardrails.md` 排除防御性习惯、人工标签、公式倾倒、不受支持的热潮和机械性文本。
5. 使用 `scripts/convert.py` 生成的段落标题和已建立的卡片就地填充或修订现有卡片：故事模式、摘要移动、引言移动、方法移动、证据移动、引用模式、可复用技术、不复制边界。记录标题、会议/年份（经验证时）、源身份/版本和相关的页/段落锚点。仅当源提供实质性示例时才添加排除的反模式。将写作移动与源主张和独特措辞分开。
6. 当请求库注册时，使用 `../ccf-paper-writer/references/exemplars/cards/` 或用户的现有库，并更新 `../ccf-paper-writer/references/exemplars/index.md` 而不重复条目。保留无关卡片；仅匹配的文件名不能证明相同的源。将原始提取保留在工作缓存中，在可复用卡片库之外。
7. 仅在请求默认选择时更新 `../ccf-paper-writer/references/custom-format/default-user-format.md`。仅请求会议的可以通过索引选择现有相关卡片，而不是提取另一个 PDF。仅当会议家族分类不明确时才加载 `../ccf-paper-writer/references/venue-guides/index.md`。
8. 验证完成的卡片没有 `[ANALYZE]` 或 `[MANUAL]` 占位符，源引用准确，输出/缓存路径有序。返回规范卡片路径和有用的写作模式；仅在执行时报告实际的注册/默认变更。不要重复完整的 PDF 提取或添加通用的下一步操作菜单。

## 作者交接

传递选定的卡片路径、源身份和相关的写作移动。作者决定是否需要其任务的风格参考；段落编辑不会自动加载默认或会议卡片包。对于完整手稿或明确的风格适应，从 `../ccf-paper-writer/references/exemplars/index.md` 选择并仅加载匹配的段落/卡片。保留现有的用户默认值，不要将它们视为每个写作请求的强制阅读材料。
