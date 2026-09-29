---
name: nature-shared
description: 内部共享引用支持包，用于已安装的《自然技能》，包括自然写作、自然润色、自然响应、自然阅读和自然纸转PPT。不要将其作为独立用户工作流程调用。仅加载其他《自然技能》请求的特定核心文件或期刊格式文件。
---

# Nature 共享引用

仅将此包用作已安装 Nature 技能的依赖项。

- 加载精确引用的文件；不要预加载整个包。
- 将 `core/` 和 `journal-formats/` 视为共享定义，而非独立工作流。
- 仅将 `journal-formats/nature.md` 用于旗舰期刊 Nature，并将 `core/research-compliance.md` 仅在其专业适用性门禁被触发时使用。
- 将 `journal-formats/nature-machine-intelligence.md` 用于精确 NMI 文章类型、限制、初始提交文件、数据/代码责任和生产要求；不要导入旗舰 Nature 或 Nature Communications 的限制。
- 将 `core/main-text-discipline.md` 用于结果放置、主文本压缩、修订累积、图注/SI 分配和重复声明检查。
- 将 `core/nature-results-discussion.md` 用于语料库衍生的 Nature 风格结果声明升级、证据约束的本地解释和讨论综合；不要将其呈现为官方期刊政策。
- 将 `core/discussion-argument-language.md` 用于期刊通用讨论功能排序、反向漏斗控制、证据校准的模态、声明特定限制和不确定性驱动的未来工作。
- 将 `core/nature-introduction.md` 用于语料库衍生的 Nature 风格问题漏斗、精确知识空白、文献张力、问题优先的新颖性和引言-结果对齐；不要将其呈现为官方期刊政策。
- 将 `core/nature-abstract.md` 用于语料库衍生的 Nature 风格以发现为中心的摘要压缩、声明层级、选择性数值支持和领域级回报；不要将其呈现为官方期刊政策。
- 返回请求技能以获取任务逻辑、输出格式和最终 QA。
