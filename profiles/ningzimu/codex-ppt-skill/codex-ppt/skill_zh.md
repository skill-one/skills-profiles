# Codex PPT

## 概述

该技能能够根据源材料创建基于图像的 PowerPoint 幻灯片。每张幻灯片都是一个完整的 16:9 生成的图像。最终图像通过 `scripts/assemble_ppt.py` 组装成 `.pptx` 文件。

在用户需要视觉统一的演示且接受全屏图像页面时使用此技能。当每个文本框、图表或形状都必须保持单独可编辑时，不要使用它。

优先使用内置的图像生成/编辑工具。仅在内置后端不可用、缺少所需功能或用户明确要求 API/CLI 模式时使用 `scripts/image_gen.py`。

## 严格约束

- 在每个阶段之前，阅读相关的 `Reference Map` 文件。该文件是编排合同；详细规则位于 `docs/` 和工作提示位于 `prompts/`。
- 尊重审批关卡。在 `docs/workflow-gates-and-progress.md` 中的审批之前，不要创建最终的 `deck_spec.json`、`speech.md`、提示工作、幻灯片图像或 `.pptx`。
- 在用户批准样本幻灯片并授权全套幻灯片生成后，每当有子代理可用时，必须将每个剩余的幻灯片图像工作分派给幻灯片子代理。
- 主代理拥有编排、提示工作、状态记录、QA、演讲笔记和组装。不要在可用幻灯片子代理的情况下，用顺序生产来无声地替换它们。
- 每个最终的 `origin_image/slide_XX.png` 必须由选定的图像后端生成：内置图像生成/编辑工具或 `scripts/image_gen.py`。
- 本地绘图、Pillow、SVG、HTML/CSS/canvas 截图、python-pptx/PptxGenJS 布局和手动叠加是故障模式，不是后备方案。
- 选定的图像后端必须在后端确认后保持固定。不要让子代理为了方便而切换后端。
- 在样本批准后，记录已批准样本的生成方式，并将该确切方法传递给每个幻灯片子代理。
- 幻灯片分派和结果状态必须使用捆绑的脚本记录。仅靠聊天消息不能使幻灯片分派或完成。
- 如果必需的子代理、图像后端或必需图像路径不可用，请停止并报告一个阻塞器，并提供幻灯片 ID 和证据。不要创建质量较低的替代品。

## 可见进度

对于非平凡的幻灯片，请保留一个用户可见的检查清单，其中包含一个活动步骤。规范完成证据位于 `docs/workflow-gates-and-progress.md`。

默认可见步骤：

1. 准备源材料、大纲、样式和后端决策。
2. 生成并批准一个样本幻灯片。
3. 准备幻灯片工作和幻灯片状态。
4. 分派幻灯片子代理。
5. 记录生成的幻灯片结果。
6. QA、修复、笔记和 PPT 组装。

不要仅从聊天中标记步骤完成；使用实际文件或脚本记录的状态。

## 默认工作流程

1. 理解源内容。
   - 确定主题、受众、目标、页面数量、样式/品牌约束以及要包含或排除的部分。
   - 如果未指定页面数量，请选择一个实用的数量。典型的演示文稿有 8-12 张幻灯片。

2. 规划演示文稿大纲。
   - 在编写或更新 `outline.md` 之前，阅读 `docs/workflow-gates-and-progress.md` 和 `docs/outline-style-and-sample.md`。
   - 起草幻灯片角色和必需的源图像。请求确认，然后在样式、后端、样本或下游工件获得批准之前停止。

3. 确认统一的视觉风格。
   - 在提供样式选项或使用 `references/` 中的文件之前，阅读 `docs/outline-style-and-sample.md`。
   - 提供 2-3 个具体的样式方向，推荐一个，等待确认，然后保持一个视觉身份，同时根据页面角色变化布局。

4. 确认图像后端。
   - 在生成任何幻灯片图像之前，阅读 `docs/backend-selection.md`。
   - 检查内置图像工具是否可调用，说明你检查了什么，命名后端，解释后备状态，并等待确认。
   - 如果选择 CLI/API 后备，请阅读 `docs/cli-api-fallback.md`。仅在配置错误或明确 API 设置请求后，才阅读 `docs/image-model-configuration.md`。

5. 生成一个样本幻灯片以供批准。
   - 在生成或批准样本幻灯片之前，阅读 `docs/outline-style-and-sample.md`。
   - 在大纲、样式和后端确认后，生成一个代表性的样本。在批准之前不要生成整个演示文稿。
   - 批准后，在 `deck_spec.json` 中记录 `sample_generation_method`，以便工作和子代理继承相同的路径。

6. 创建项目目录。
   - 在初始化文件夹或组装文件之前，阅读 `docs/project-assembly-and-reporting.md`。
   - 如果未指定目标，请使用当前工作目录或源文件目录。

7. 准备用户提供的资产。
   - 在使用纸制图形、图表、截图、标志或其他必需资产之前，阅读 `docs/user-supplied-assets.md`。
   - 将必需的资产视为严格的输入，并在生成之前确认幻灯片到资产的映射。

8. 生成所有幻灯片图像。
   - 在全套幻灯片图像生成之前，阅读 `docs/slide-generation-and-subagents.md`。
   - 使用 `scripts/prepare_slide_prompts.py` 或保存的 `prompts/slide_XX.json` 文件创建每张幻灯片的工作。
   - 每个最终图像必须来自选定的后端，并通过捆绑的状态脚本记录。

9. 分派幻灯片子代理。
   - 在分派或替换幻灯片工作之前，阅读 `docs/slide-generation-and-subagents.md` 和 `prompts/slide-worker.md`。
   - 尽可能为每个剩余的幻灯片工作使用一个子代理。如果无法生成必需的子代理，请停止并报告一个阻塞器，除非用户更改工作流程。

10. 质量检查和修复。
    - 在 QA 或组装之前，阅读 `docs/project-assembly-and-reporting.md`。
    - 在组装之前检查每张幻灯片：文本、大纲匹配、截断、样式、不想要的页码、重叠和必需资产。
    - 使用更严格的提示重新生成严重故障。在可用的情况下，使用后端编辑局部问题。
    - 对于 CLI/API 后备编辑命令，请阅读 `docs/cli-api-fallback.md`。仅在验证编辑后的输出后，才替换最终幻灯片。

11. 编写演讲笔记并组装 PPT。
    - 在编写 `speech.md` 或运行组装之前，阅读 `docs/project-assembly-and-reporting.md`。
    - 确保 `outline.md` 反映了最终确认的演示文稿大纲。使用 `speech.md` 标题映射到 `Slide N`。
    - 在组装之前，确保 `slide_jobs.json` 显示生成的幻灯片为 `recorded`，批准的样本为 `accepted`。如果任何幻灯片为 `pending`、`dispatched` 或 `blocked`，请停止。

12. 报告结果。
    - 使用 `docs/project-assembly-and-reporting.md` 中的最终报告检查清单。
    - 包括路径、幻灯片数量、使用的后端、记录结果状态以及任何限制或阻塞器。

13. 保存可重用的样式。
    - 如果被要求保存当前演示文稿样式或提供的图像/PDF/PPT/PPTX 样式，请阅读 `docs/style-library.md`。
    - 如果最终演示文稿使用了自定义或调整的样式，请在最终报告中主动提供保存它，根据 `docs/project-assembly-and-reporting.md`。用户自定义样式存储在 `${CODEX_PPT_HOME:-~/.codex-ppt-skill}/references/`，优先于同名的内置样式。

## 子代理分派

样本批准后，在运行时可以生成子代理时，幻灯片子代理是必需的。主代理准备工作并记录状态；每个工作处理 exactly 一个 `prompts/slide_XX.json` 工作并仅返回选定的图像路径、后端和 QA 笔记。

使用 `docs/slide-generation-and-subagents.md` 进行分派、命令、结果记录、阻塞器和后端来源。使用 `prompts/slide-worker.md` 作为交接模板。

子代理不得编辑 `outline.md`、`deck_spec.json`、其他幻灯片工作、`origin_image/`、`speech.md` 或最终的 `.pptx`。父代理记录输出并组装。

## 接受标准

- 输出是一个有效的 `.pptx`。
- 每个预期的最终幻灯片图像都存在于 `origin_image/slide_XX.png` 下。
- 每个最终幻灯片图像都是由确认的后端生成的，并通过 `record_slide_result.py` 记录，除非一个批准的样本被运行状态标记为接受。
- `outline.md` 反映了批准的演示文稿大纲。
- 当预期演讲笔记时，`speech.md` 存在，并且组装将那些笔记写入 PPT。
- `slide_jobs.json` 和 `slide_run_state.json` 反映了最终状态。
- 必需的源图像是明显表示的，或者报告了阻塞器。
- 如果受阻，最终响应将识别阶段、幻灯片 ID、证据路径和未完成的原因；不要将演示文稿标记为完成。

## Reference Map

- `docs/workflow-gates-and-progress.md`：审批关卡、进度、完成证据。
- `docs/backend-selection.md`：后端决策规则和确认文本。
- `docs/outline-style-and-sample.md`：大纲、样式、样本规则、提示示例。
- `docs/user-supplied-assets.md`：严格处理必需的源资产。
- `docs/slide-generation-and-subagents.md`：工作、分派、结果记录、阻塞器、来源。
- `docs/cli-api-fallback.md`：后备运行时、生成/编辑命令、图像限制、故障排除。
- `docs/image-model-configuration.md`：API 密钥、基本 URL、模型、`.env`；仅在需要配置时阅读。
- `docs/project-assembly-and-reporting.md`：项目目录、笔记、组装、最终报告、提示原则。
- `prompts/slide-worker.md`：幻灯片子代理交接模板。
- `references/*.md`：内置视觉样式参考。用户自定义样式存储在 `${CODEX_PPT_HOME:-~/.codex-ppt-skill}/references/`，并优先于同名的内置样式。

## 文档和更新

有关源代码、文档、安装、配置和示例，请参阅 [ningzimu/codex-ppt-skill](https://github.com/ningzimu/codex-ppt-skill)。
