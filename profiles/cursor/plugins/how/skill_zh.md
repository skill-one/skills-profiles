# 如何

探索代码库以回答“X是如何工作的？”这类问题。产出面向子系统新加入的高级工程师级别的架构说明，足够构建一个工作的心智模型，而不是像注释过的源代码那样过多细节。

下面的每个spawn命名了`pstack-models.mdc`规则中的一行角色定义和默认值。将`model`设置为该行值，如果规则或该行缺失，则设置为默认值。当值为`auto`或`inherit-parent`时，不设置`model`。如果任务工具拒绝一个slug，使用默认值并说明。如果它拒绝默认值，则根据错误信息使用同一系列的最近有效slug。

## 第1步。评估复杂度

如果范围不明确，请说明你的理解并探索。用户可以重新定向。

- **简单**（单个模块、小型工具、狭窄的问题，例如“函数X是如何工作的”）：不需要探索者。一个解释者一次性探索并解释。转到第2b步。
- **复杂**（跨越多个文件或服务的子系统、横切功能、完整的架构概述）：首先并行生成探索者，然后交给解释者。转到第2a步。

如有疑问，选择简单路径。

## 第2a步。探索（仅限复杂问题）

将问题分解为2到4个探索角度，每个角度是子系统的一个独立切片。在单个消息中生成所有探索者：

- `subagent_type`: `generalPurpose`
- `model`: `how explorer`行，默认`grok-4.7-xhigh-fast`
- `readonly`: `true`

每个探索者获得`references/explorer-prompt.md`中的提示，并用其角度填充。然后转到第3步。

## 第2b步。直接解释（简单问题）

生成一个Task子代理，一次性探索并解释：

- `subagent_type`: `generalPurpose`
- `model`: `how explainer`行，默认`claude-opus-5-5-max`
- `readonly`: `true`

从`references/explainer-prompt.md`构建其提示，不包括探索者发现部分。转到第4步。

## 第3步。综合（仅限复杂问题）

所有探索者返回后，生成一个Task子代理将他们的发现综合为一个解释：

- `subagent_type`: `generalPurpose`
- `model`: `how explainer`行，默认`claude-opus-5-5-max`
- `readonly`: `true`

从`references/explainer-prompt.md`构建其提示，用每个探索者的发现填充。

## 第4步。呈现

将解释者的输出呈现给用户。从对话中进行的轻微编辑以增强清晰度或上下文是可以的。不要大幅重写它。

## 输出格式

解释使用`references/explainer-prompt.md`中定义的章节，删除不相关的章节：概述、关键概念、工作原理、存放位置、注意事项。
