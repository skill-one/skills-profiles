---
name: h3-prompt-writing
description: 为T2VA、I2VA、FL2VA、L2VA和Ref2VA编写MiniMax H3视频生成提示。在将多模态请求重写为H3提示结构时使用，包括组合integrated_multimodal_description、overall_soundscape和non_diegetic_music，对齐关键帧，或为图像、视频和音频定义参考标签。
---

# H3 提示词编写

## 工作流程

1. 确定输入模式：T2VA、I2VA、FL2VA、L2VA 或全参考 Ref2VA。
2. 对于基础文本/关键帧模式，读取 `references/base-en.txt` 并遵循其最终提示词结构。
3. 对于全参考模式，读取 `references/ref-en.txt` 并遵循其六部分重写格式。
4. 保留所选指南中的确切字段名、部分顺序、标签和时间记号。

## 基础模式

- T2VA：从文本构建完整的音视频时间线。
- I2VA：从第一帧开始并从此帧向前发展。
- FL2VA：描述第一帧和最后一帧之间的连续路径。
- L2VA：推断一个合理的开场并汇聚到提供的最后一帧。

按 `references/base-en.txt` 中所示顺序使用 `integrated_multimodal_description`、`overall_soundscape` 和 `non_diegetic_music`。

## 全参考模式

Ref2VA 重写使用 `subject_definitions`、`summary`、`retention_analysis`、`detailed_description`、`overall_soundscape` 和 `non_diegetic_music` 的顺序。参考标签在所有部分中保持一致。

阅读 `references/ref-en.txt` 了解标签规则、保留分析以及完整示例。

## 输出规则

- 以英文编写重写部分；保留对话、歌词和可见场景文本在其原始语言中。
- 通过构图、主体、环境、动作、摄像机、声音以及参考内容出现的确切时间点来描述每个镜头。
- 避免情节总结、未解决的参考标签以及与请求时长不符的时间记号。
