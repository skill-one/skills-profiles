---
name: tesseract-motion
description: 在 Tesseract 中本地创建可编辑的运动图形，包括全帧动画场景、字体设计、图表、底部字幕和覆盖在提供的素材上的叠加层。用于专注的运动设计工作；使用 tesseract-video 来组装或修订完整的素材剪辑。
---

# 使用 Tesseract 设计动画

CLI 可能会为某些命令发送基本的使用遥测数据。您可以通过 `TESSERACT_SKILL=tesseract-motion` 和 [其他归因变量](references/telemetry.md) 提供可选的归因信息。尊重 CLI 的遥测数据禁用设置；切勿代表用户启用遥测数据。

创建一个具有清晰视觉构思的动态合成。明确动画传达的内容、其节奏、目标画布，以及这是完整场景还是必须保留视频可见性的叠加层。

在设计广告片头时，请阅读 [广告钩子](references/ad-hooks.md)：开发与实际产品/信息相关的清晰视觉构思，在可用时将其关键出现时间与确认的片头音乐提示对齐，并与下一场景一起预览。声音和转场可以强化构思；它们不是必需的效果堆栈。

1. 从包含此 `SKILL.md` 的目录中解析该技能的根路径。阅读 [CLI 安装](references/installation.md) 并在每次会话中检查所需的 Tesseract 版本。在整个任务中使用解析的可执行路径。阅读 [本地操作](references/local-operation.md) 和 [原生创作](references/native-authoring.md)。
2. 阅读 [动画设计](references/motion-design.md)。使用提供的品牌/风格参考。对于叠加层，检查实际视频在预期位置和时间；围绕主体、文本和动作进行设计。
3. 选择一个有用的机制——字体排印、路径、蒙版、预合成、图表或媒体处理。使用原生图层和协调的 AnimationGraph。欢迎使用现有视频片段和图形资源；设计的一个预渲染图像会破坏可编辑动画。
4. 从 `tsrct project schema` 或 `tsrct project schema --document` 中检索所需的特定定义。[效果创作](references/fx-authoring.md) 和 [动画](references/motion.md) 显示工作线形形状和本地渲染，不是强制设计。对于主体遮挡，在支持时使用实际人物遮罩，而不是近似的手绘轮廓。
5. 当提供的或先前生成的音乐设定节奏时，请阅读 [波形编辑](references/waveform-editing.md)：打开音乐波形，听取确认重音和短语变化，并在创作时间前将动画出现/揭示映射到选定的音乐事件。保留所选曲目；不要将每个峰值都误认为节拍或机械同步每个动作。当图形是可听视频的一部分时，请阅读 [声音设计](references/sound-design.md)。当本地强调或转场声音强化动作时添加，当语音或现有混音已经承载时刻时保持安静。将声音保存在单独的音频图层中，并使用 [音频和时间](references/audio-and-timing.md) 进行导入文件、位置和包络。静音叠加层请求保持静音。
6. 使用 [胶片条预览](references/filmstrip-review.md) 在构建过程中检查和修正保存的动画。最后使用 [审查和交付](references/review-and-delivery.md)，包括在上下文中播放。

输出可编辑合成为便携式 `.tsrct` 文档和渲染预览。将叠加层作为原生图层合成到提供的视频片段上。对于透明叠加层，使用 `export --format prores --fx-solo compositionId:layerId --output overlay.mov` 并验证 alpha 通道。单独导出覆盖目标活动窗口而不带音频；完整项目 MOV 导出保留项目混音。

优先使用支持的效果和原生文本/形状动画。对于不寻常的视觉效果处理，仅在阅读 [自定义着色器合同](references/custom-shader.md) 后使用自定义 WGSL。切勿发明 API 字段、关键帧格式或此运行时不提供的功能，例如任意 3D 网格导入。
