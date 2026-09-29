---
name: hatch-pet
description: 创建、修复、验证、可视化质量保证（QA）和打包与Codex兼容的动画宠物及宠物精灵图集，可从角色艺术、生成图像、公司或潜在品牌提示或视觉参考中获取。当用户需要轻量级工作流程的Codex宠物、非像素自定义宠物风格、潜在公司吉祥物宠物，或包含透明未使用单元格、QA接触图和宠物.json打包的完整8x9动画宠物图集时使用。此技能组合了安装的$imagegen系统技能用于视觉生成，并使用捆绑脚本进行确定性精灵图集组装。
---

# Hatch Pet

## 概述

根据概念、品牌提示、公司/潜在客户名称、一个或多个参考图像，或这些输入的组合来创建一个与Codex兼容的动画宠物。此工作流程保留了用于图谱几何、验证、视觉质量保证和打包的确定性hatch-pet管道，同时使用简洁的状态特定提示，并允许任何宠物安全的视觉风格。

面向用户的输入是可选的。如果用户省略宠物名称，则从概念、品牌、公司或参考文件名中推断一个名称；如果无法做到这一点，则选择一个简短友好的名称。如果用户省略描述，则从概念或参考中推断一个描述。如果用户省略参考图像，则首先从文本生成基础宠物，然后使用该基础作为每个动画行的规范参考。

## 生成委托

对所有正常视觉生成使用`$imagegen`。

在生成基础艺术、行条或修复行之前，加载并遵循安装的图像生成技能：

```text
${CODEX_HOME:-$HOME/.codex}/skills/.system/imagegen/SKILL.md
```

不要直接调用图像API、图像CLI或任何其他图像生成路径。让`$imagegen`选择其自己的内置优先路径和回退规则。如果`$imagegen`表示回退需要确认，则在继续之前询问用户。

调用`$imagegen`时，将生成的宠物提示作为权威的视觉规范传递。宠物提示应保持简洁、状态特定、面向精灵生成，并基于列出的输入图像。将更长的策略和QA规则保留在此技能和确定性审查脚本中，而不是将它们扩展到每个图像提示中。不要将提示包装在通用的`$imagegen`共享提示模式中。

仅为此技能的脚本用于确定性图像工作：准备布局指南和提示、镜像批准的`running-left`、提取帧、验证行、组合最终图谱、创建接触表和运动预览QA媒体。父拥有的shell/`jq`步骤处理清单更新、打包和清理。

## 存储控制

内置的`$imagegen`路径将生成的PNG字节存储在调用它的回滚中，即使它还在`${CODEX_HOME:-$HOME/.codex}/generated_images`下写入文件。稍后删除文件可以减少文件系统使用，但它不会缩小已写入的回滚。保持图像生成隔离和边界：

- 每个视觉工作使用一个轻量级生成工作进程。不要将多个基础/行工作批量到同一个工作进程。
- 工作进程必须仅返回`selected_source=...`和`qa_note=...`；它们在其最终响应中不得包含Markdown图像预览、base64或额外的视觉附件。
- 父进程不得视觉上打开每个生成的PNG。使用工作进程QA来检查每个工作，并仅检查最终接触表。
- 将选定的生成输出复制到`decoded/`后，当它存在于`${CODEX_HOME:-$HOME/.codex}/generated_images`中时，删除选定的原始文件，然后如果可能的话，删除其现在空的生成目录。
- 对于存储敏感的完整运行，当可用时，询问用户是否要使用`$imagegen` CLI回退。该路径需要本地API凭证和明确用户确认，但它可以避免内置图像有效负载嵌入到回滚事件中。

## 品牌发现

如果用户提供一个品牌、公司、产品或潜在客户名称，而不是具体的头像描述或参考图像，则在准备宠物运行之前运行一个轻量级的发现子代理。发现工作进程必须使用网络搜索，并优先考虑官方来源，例如品牌网站、产品页面、文档、关于页面、新闻页面或品牌页面。只有在官方页面过于单薄时才使用信誉良好的二级来源。保持搜索范围狭窄：足够提取视觉和个性提示，而不是市场研究摘要。

当用户已经提供具体的吉祥物/头像描述或参考图像时，除非用户明确要求品牌研究，否则跳过发现。

发现工作进程的责任：

- 在网上搜索2-4个相关来源，优先考虑官方页面
- 编写自适应的Markdown简报，而不是僵化的字段转储
- 涵盖身份/类别、受众/使用上下文、视觉系统、个性/语气、产品/领域主题、吉祥物翻译提示、避免事项和证据/信心
- 将从来源中推断的吉祥物指导标记为推断
- 避免复制标志、可读标记、UI截图、口号或文本
- 以包含仅`brand_name`、`brand_brief`、`avatar_seed`、`avoid`和`brand_sources`的紧凑`Generation handoff`部分结束
- 不要生成图像、准备运行文件夹或编辑不相关的文件

使用此发现工作进程提示：

```text
Research a brand for hatch-pet mascot creation.

Brand/product/prospect: <brand name>
User context: <short user request>
Output file: <absolute path to brand-discovery.md>

使用网络搜索。优先考虑官方品牌、产品、文档、关于、新闻或品牌页面。如果官方来源过于单薄，则使用信誉良好的二级来源。编写自适应的Markdown简报到输出文件。标题可以灵活地按品牌变化，但简报必须涵盖：
- identity/category: 规范名称、产品类型、它做什么
- audience/use context: 它服务谁以及它出现在哪里
- visual system: 调色板、形状、线条质量、材料、排版感觉、图标、模式
- personality/tone: 情感特征、能量、正式性、俏皮性
- product/domain motifs: 物体、工作流程、动词、隐喻、环境
- mascot translation cues: 候选形式、标志性特征、道具、宠物尺寸下必须阅读的内容
- avoidances: 标志/文本、商标敏感元素、误导性提示、竞争对手混淆、不良吉祥物匹配
- evidence/confidence: 来源URL加上证据薄弱或推断的笔记

不要复制标志、可读标记、UI截图、口号或文本。清楚地标记从非直接来源推断的吉祥物指导。

在简报的末尾以包含以下内容的`Generation handoff`部分结束：
- brand_name=<规范品牌/产品名称>
- brand_brief=<一句话，最多45个字，涵盖调色板/语气/领域主题/个性>
- avatar_seed=<简短的吉祥物安全视觉想法，不复制标志>
- avoid=<简短的逗号分隔列表>
- brand_sources=<逗号分隔的来源URL>

返回：
brand_discovery_file=<绝对输出文件路径>
brand_name=<规范品牌/产品名称>
brand_brief=<来自Generation handoff的相同紧凑句子>
avatar_seed=<来自Generation handoff的相同简短种子>
avoid=<来自Generation handoff的相同简短避免列表>
brand_sources=<相同的逗号分隔URL>
```

父进程应在准备运行之前保存Markdown简报，然后将它作为`--brand-discovery-file`与`--brand-name`、`--brand-brief`一起传递，并在用户没有提供更好的头像描述时，根据`avatar_seed`重复`--brand-source`和基于`avatar_seed`的简洁`--pet-notes`值。保留完整简报以供审查；只有紧凑的回退字段应塑造提示。如果网络搜索不可用，并且用户只给出了一个简单的品牌名称，则在生成之前请求品牌提示。

对于正常的宠物运行，预期最多10个视觉生成工作：1个基础宠物加上9个行条工作。Codex应用程序合同目前使用所有9个状态：`idle`、`running-right`、`running-left`、`waving`、`jumping`、`failed`、`waiting`、`running`和`review`。唯一确定性视觉派生是`running-left`，它可能是在生成、视觉检查并明确批准可以镜像`running-right`之后由镜像`running-right`产生的。如果镜像不合适，则作为正常的基于`$imagegen`的行生成`running-left`。

选择视觉输出后，父代理将该确切图像复制到作业的`decoded/`路径中，并在`imagegen-jobs.json`中标记作业完成。不要编写填充行输出的辅助脚本。确定性Python脚本只能处理已生成的视觉输出。

只有基础工作可以是提示唯一的。通过`$imagegen`生成的每个行条工作都必须使用`imagegen-jobs.json`中列出的输入图像，包括在选定基础输出复制后创建的规范基础参考。将任何没有附加接地图像的行生成视为无效。

## 宠物安全风格

默认风格是`auto`：从用户的提示和参考中推断宠物的风格，然后在每一行中保留该风格。如果用户指定了风格，则尊重它。支持的风格预设包括`pixel`、`plush`、`clay`、`sticker`、`flat-vector`、`3d-toy`、`painterly`、`brand-inspired`和`auto`。

任何风格都是可接受的，只要它保持宠物安全：

- 整体身体轮廓在`192x208`单元格内可读
- 在所有行中保持一致的面部、比例、材料、调色板和道具
- 清洁的可移除色键背景
- 足够大，宠物尺寸下可以阅读的细节
- 除非用户明确提供批准的参考艺术并要求它们，否则不允许文本、标签、UI或可读标志

非像素风格是一流的第一类。Plush、clay、sticker、vector、3D toy、painterly吉祥物、墨水、brand-inspired外观应在满足图谱和可读性约束时被接受。

## 透明度和效果

宠物行被处理为透明的`192x208`单元格，因此每个生成的像素必须要么属于宠物精灵，要么是清洁的可移除色键背景。优先考虑姿势、表情和轮廓变化，而不是装饰性效果。

确定性光栅管道拥有透明度不变量：变为完全透明的像素被标准化，以便它们不会保留隐藏的RGB残留，如果导出的文件违反该不变量，则图谱验证应失败。不要通过接受视觉不一致的输出来掩盖彩色光晕或透明像素残留。

允许的效果必须满足所有这些条件：

- 效果与状态相关，并有助于解释动画。
- 效果与宠物轮廓物理连接、接触或重叠，而不是悬浮在附近。
- 效果与宠物位于同一帧槽中，并且不会创建单独的精灵组件。
- 效果是不透明的，边缘足够硬，以便清洁提取，并使用非色键颜色。
- 效果足够小，在`192x208`下保持可读性，不会杂乱。

默认情况下避免这些，因为它们通常会破坏透明背景清理或组件提取：

- 波浪标记、运动弧、速度线、动作条纹、残留像、模糊或涂抹
- 分离的星星、松散的闪光、悬浮的标点符号、悬浮的图标、下落的泪滴、分离的烟雾云或松散的灰尘
- 投影阴影、接触阴影、阴影、椭圆地板阴影、地板补丁、着陆标记、冲击爆发、发光、光晕、光环或软透明效果
- 文本、标签、帧编号、可见网格、指南标记、对话气泡、思想气泡、UI面板、代码片段、棋盘透明度、白色背景、黑色背景或场景
- 宠物、道具、效果、高光或阴影中的色键相邻颜色
- 迷失像素、断开的轮廓碎片、斑点/噪声、裁剪的身体部分、重叠的姿势或任何跨越相邻帧槽的姿势

状态特定指导：

- `idle`：保持这种平静且低干扰。仅使用微妙的呼吸、微小的眨眼、轻微的头部或身体摆动、非常小的材料摇摆或另一个保持人格的运动。循环必须仍然包含可见的微观变化；不要接受六个实际上相同的副本。不要显示挥手、行走、奔跑、跳跃、说话、工作、审查、情绪反应、大型手势、项目交互或新道具。
- `waving`：仅通过爪子、手、翅膀或肢体姿势显示挥手。不要绘制波浪标记、运动弧、线条、闪光、符号或悬浮效果围绕手势。
- `jumping`：仅通过身体位置显示垂直运动。不要绘制阴影、灰尘、着陆标记、冲击爆发、弹跳垫或地板提示。
- `failed`：如果它们遵守允许效果规则，则允许眼泪、连接的烟雾泡或连接的星星；不要使用红色X标记、悬浮符号、分离的烟雾、分离的星星或分离的泪滴。
- `waiting`：通过期待提问姿势显示Codex需要批准、帮助或用户输入。将其与普通空闲和审查区分开来。
- `running`：显示主动任务工作、处理、思考、扫描、打字或专注努力。不要显示字面的脚跑步、慢跑、冲刺、跑步机运动、抬起的膝盖、长步、挥动手臂、方向性旅行、速度线、灰尘云、地板阴影、运动轨迹或分离的运动效果。
- `review`：通过倾斜、眨眼、眼睛、头部倾斜或爪子/手位置显示专注。不要添加放大镜、纸张、代码、UI、标点符号、符号或除非它们已经存在于基础宠物身份中，否则添加其他新道具。
- `running-right`和`running-left`：仅通过身体、肢体和道具运动显示方向拖动运动。`running-right`必须面向并向右移动；`running-left`必须面向并向左移动。它们的节奏必须在循环中明显交替，而不是重复几乎静态的步伐。不要绘制速度线、灰尘云、地板阴影、运动轨迹或分离的运动效果。

## 可见进度计划

对于每个宠物运行，保留一个可见清单，以便用户可以看到工作进展到哪里。在开始之前创建清单，一次保持一个步骤活跃，并在每个步骤完成后更新它。

使用此清单进行正常宠物运行，将`<Pet>`替换为宠物的名称或`your pet`：

1. Getting `<Pet>` ready.
2. Imagining `<Pet>`'s main look.
3. Picturing `<Pet>`'s poses.
4. Hatching `<Pet>`.

每个步骤的含义：

- `Getting <Pet> ready.` 选择或确认宠物名称、描述、源图像、风格预设、风格注释和工作文件夹。对于裸品牌/产品/公司请求，首先运行品牌发现工作进程并捕获紧凑的品牌简报、来源URL和头像种子。
- `Imagining <Pet>'s main look.` 生成宠物的主要参考图像。这成为视觉真实来源。
- `Picturing <Pet>'s poses.` 通过轻量级工作进程生成姿势行，从`idle`和`running-right`开始以确认身份和步态。仅在`running-right`在翻转时明显有效时才镜像`running-left`。
- `Hatching <Pet>.` 将批准的姿势转换为最终宠物文件，审查接触表、预览和验证结果，修复任何损坏的部分，保存`pet.json`和`spritesheet.webp`，然后报告输出路径。

仅在真实文件、图像或决策存在时才标记步骤完成。如果这是修复运行，则从第一个相关步骤开始，而不是重新启动整个清单。

## 默认工作流程

1. 准备宠物运行文件夹和imagegen工作清单：

```bash
SKILL_DIR="${CODEX_HOME:-$HOME/.codex}/skills/hatch-pet"
python "$SKILL_DIR/scripts/prepare_pet_run.py" \
  --pet-name "<Name>" \
  --description "<one sentence>" \
  --reference /absolute/path/to/reference.png \
  --output-dir /absolute/path/to/run \
  --pet-notes "<stable pet description>" \
  --brand-discovery-file /absolute/path/to/brand-discovery.md \
  --brand-name "<optional researched brand name>" \
  --brand-brief "<optional compact researched brand cue sentence>" \
  --brand-source "https://example.com/source" \
  --style-preset auto \
  --style-notes "<optional freeform style notes>" \
  --force
```

以上所有参数均为可选，除了需要表达用户约束的任何标志。对于纯文本请求，通过 `--pet-notes` 传递概念，省略 `--reference`；`prepare_pet_run.py` 将根据需要推断名称、描述、色度键和输出目录。
对于纯品牌请求，首先运行发现工作器，保存 Markdown 简报，然后通过 `--brand-discovery-file` 传递简报路径，通过 `--pet-notes` 传递 `avatar_seed`，通过 `--brand-name` 传递 `brand_name`，通过 `--brand-brief` 传递 `brand_brief`，并通过重复 `--brand-source` 传递每个源 URL。

2. 查看 `imagegen-jobs.json` 以查找下一个准备好的 `$imagegen` 工作。当工作的 `status` 不是 `complete` 且 `depends_on` 中的每个 ID 都已完成时，工作就准备好了。最好直接使用 `jq` 或编辑器读取清单，而不是添加辅助脚本以显示状态：

```bash
jq '.jobs[] | {id, kind, status, depends_on, prompt_file, retry_prompt_file, input_images, output_path, derivation_policy}' /absolute/path/to/run/imagegen-jobs.json
```

3. 默认使用轻量级工作器生成视觉工作：

- 首先使用轻量级基础工作器生成和复制 `base`。
- 接下来生成和复制 `idle` 和 `running-right` 作为身份和步态检查，每行使用一个轻量级工作器。
- 查看 `running-right`；只有当视觉身份、道具位置、标记、照明和方向语义仍然正确时，才镜像 `running-left`。
- 当镜像会改变含义或身份时，使用轻量级工作器正常生成 `running-left`。
- 使用轻量级工作器生成其余行，使用每个工作列出的每个输入图像。

对于每个准备好的视觉工作，使用 `imagegen-jobs.json` 中列出的提示文件调用 `$imagegen`，使用其角色标签的每个列出的输入图像，除非 `$imagegen` 本身路由否则使用默认内置 `image_gen` 路径。父代理必须将其自己的图像处理保持最小：不要在父级展开中打开每个生成的 `base` 或行。工作器只返回选定的源路径和一个单句 QA 备注；父级在清单中记录选定的源路径。

`prepare_pet_run.py` 在 `references/layout-guides/` 下创建 9 个行特定布局指南图像，每个动画状态一个。行工作将匹配的指南作为仅布局输入附加，以便模型可以遵循正确的帧数、间距、居中和安全填充。将这些指南视为不可见的施工参考：生成的行条不得包含可见的框、边框、居中标记、标签、指南颜色或指南背景。

生成行条时，在行提示中保持身份锁定为权威。保留相同的风格、面部、标记、调色板、材料、道具设计、身体比例和轮廓，从规范基础开始。行工作默认附加布局指南和规范基础；解码的基础保存在运行文件夹中以进行确定性处理，而不是作为冗余生成输入发送。

如果 `$imagegen` 返回传输级别的 `Bad Request` 对于一行，使用其生成的 `retry_prompt_file` 重新尝试该行一次。重试提示保留了行 ID、帧数、色度键、规范基础身份和状态动作。保留规范基础。如果重试仍然失败，请停止并报告失败的行和提示路径，而不是切换到任何其他生成路径。

4. 选择生成的工作输出后，将其复制到解码输出路径并标记工作完成。对于 `base`，还创建规范身份参考：

```bash
RUN_DIR=/absolute/path/to/run
JOB_ID=<job-id>
SOURCE=/absolute/path/to/generated-output.png
OUTPUT_REL=$(jq -r --arg id "$JOB_ID" '.jobs[] | select(.id == $id) | .output_path' "$RUN_DIR/imagegen-jobs.json")
mkdir -p "$(dirname "$RUN_DIR/$OUTPUT_REL")"
cp "$SOURCE" "$RUN_DIR/$OUTPUT_REL"
```

```bash
if [ "$JOB_ID" = "base" ]; then mkdir -p "$RUN_DIR/references"; cp "$RUN_DIR/$OUTPUT_REL" "$RUN_DIR/references/canonical-base.png"; fi
```

```bash
UPDATED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)
TMP_MANIFEST=$(mktemp)
jq --arg id "$JOB_ID" --arg source "$SOURCE" --arg at "$UPDATED_AT" '(.jobs[] | select(.id == $id)) += {status: "complete", source_path: $source, completed_at: $at}' "$RUN_DIR/imagegen-jobs.json" > "$TMP_MANIFEST"
mv "$TMP_MANIFEST" "$RUN_DIR/imagegen-jobs.json"
```

如果复制的源位于 `${CODEX_HOME:-$HOME/.codex}/generated_images`，解码复制存在后删除原始生成文件：

```bash
GENERATED_ROOT="${CODEX_HOME:-$HOME/.codex}/generated_images"
case "$SOURCE" in
  "$GENERATED_ROOT"/*)
    rm -f "$SOURCE"
    rmdir "$(dirname "$SOURCE")" 2>/dev/null || true
    ;;
esac
```

5. 只有当视觉上安全时才派生 `running-left`：

```bash
python "$SKILL_DIR/scripts/derive_running_left_from_running_right.py" \
  --run-dir /absolute/path/to/run \
  --confirm-appropriate-mirror \
  --decision-note "<why mirroring preserves this pet's identity>"
```

该脚本将每个生成的帧槽就地镜像，以便左向行保留右向行的时序顺序。不要用整个条镜像来反转动画时序。

6. 当所有工作都完成后，直接运行图像处理脚本：

```bash
RUN_DIR=/absolute/path/to/run
mkdir -p "$RUN_DIR/final" "$RUN_DIR/qa"
```

```bash
python "$SKILL_DIR/scripts/extract_strip_frames.py" \
  --decoded-dir "$RUN_DIR/decoded" \
  --output-dir "$RUN_DIR/frames" \
  --states all \
  --method auto
```

```bash
python "$SKILL_DIR/scripts/inspect_frames.py" \
  --frames-root "$RUN_DIR/frames" \
  --json-out "$RUN_DIR/qa/review.json" \
  --require-components
```

```bash
python "$SKILL_DIR/scripts/compose_atlas.py" \
  --frames-root "$RUN_DIR/frames" \
  --output "$RUN_DIR/final/spritesheet.png" \
  --webp-output "$RUN_DIR/final/spritesheet.webp"
```

```bash
python "$SKILL_DIR/scripts/validate_atlas.py" \
  "$RUN_DIR/final/spritesheet.webp" \
  --json-out "$RUN_DIR/final/validation.json"
```

```bash
python "$SKILL_DIR/scripts/make_contact_sheet.py" \
  "$RUN_DIR/final/spritesheet.webp" \
  --output "$RUN_DIR/qa/contact-sheet.png"
```

```bash
python "$SKILL_DIR/scripts/render_animation_previews.py" \
  --frames-root "$RUN_DIR/frames" \
  --output-dir "$RUN_DIR/qa/previews"
```

如果预览 GIF 显示大小弹出或基线跳跃是由每帧拟合到单元提取引起的，并且原始行条本身具有稳定的比例和位置，请使用显式行稳定性模式重新运行帧提取，然后重新运行检查、图表合成、验证、联系表生成和预览：

```bash
python "$SKILL_DIR/scripts/extract_strip_frames.py" \
  --decoded-dir "$RUN_DIR/decoded" \
  --output-dir "$RUN_DIR/frames" \
  --states all \
  --method stable-slots
```

```bash
python "$SKILL_DIR/scripts/inspect_frames.py" \
  --frames-root "$RUN_DIR/frames" \
  --json-out "$RUN_DIR/qa/review.json" \
  --require-components \
  --allow-stable-slots
```

将 `stable-slots` 作为有意的 QA 驱动的更正，而不是默认值。它应该减少提取引起的运动弹出，同时不会隐藏剪辑的宽姿势或坏源条。

清理前的预期输出：

```text
run/
  pet_request.json
  imagegen-jobs.json
  prompts/
  decoded/
  frames/frames-manifest.json
  final/spritesheet.webp
  final/validation.json
  qa/contact-sheet.png
  qa/previews/*.gif
  qa/review.json
  qa/run-summary.json
```

默认情况下，输出包写在运行目录外。如果设置了 `CODEX_HOME`，则使用它；否则使用 `$HOME/.codex`。

```text
${CODEX_HOME:-$HOME/.codex}/pets/<pet-name>/
  pet.json
  spritesheet.webp
```

使用 shell 和 `jq` 打包：

```bash
RUN_DIR=/absolute/path/to/run
PET_ID=$(jq -r '.pet_id' "$RUN_DIR/pet_request.json")
DISPLAY_NAME=$(jq -r '.display_name' "$RUN_DIR/pet_request.json")
DESCRIPTION=$(jq -r '.description' "$RUN_DIR/pet_request.json")
PET_DIR="${CODEX_HOME:-$HOME/.codex}/pets/$PET_ID"
mkdir -p "$PET_DIR"
cp "$RUN_DIR/final/spritesheet.webp" "$PET_DIR/spritesheet.webp"
jq -n --arg id "$PET_ID" --arg displayName "$DISPLAY_NAME" --arg description "$DESCRIPTION" '{id: $id, displayName: $displayName, description: $description, spritesheetPath: "spritesheet.webp"}' > "$PET_DIR/pet.json"
```

打包后写入 `qa/run-summary.json`：

```bash
jq -n --arg run_dir "$RUN_DIR" --arg spritesheet "$RUN_DIR/final/spritesheet.webp" --arg validation "$RUN_DIR/final/validation.json" --arg contact_sheet "$RUN_DIR/qa/contact-sheet.png" --arg review "$RUN_DIR/qa/review.json" --arg package "$PET_DIR" '{ok: true, run_dir: $run_dir, spritesheet: $spritesheet, validation: $validation, contact_sheet: $contact_sheet, review: $review, package: $package}' > "$RUN_DIR/qa/run-summary.json"
```

在确定性图像处理后，使用轻量级视觉 QA 工作器检查 `qa/contact-sheet.png` 和 `qa/previews/*.gif` 之前接受宠物。确定性验证是必要的但不充分。如果任何行意外改变物种/身体类型、面部、标记、调色板、材料、道具设计、风格、道具侧或整体轮廓，则阻止接受。运动预览也必须拒绝意外的尺寸弹出、反向或停滞的方向节奏、错误的朝向方向和技术上不同但视觉上惰性的空闲循环。

在模型视觉 QA 接受联系表后，删除中间运行工件：

保留 `pet_request.json`、`final/spritesheet.webp`、`final/validation.json`、`qa/contact-sheet.png`、`qa/previews/`、`qa/review.json` 和 `qa/run-summary.json`。删除生成的提示文件、布局指南、解码行条、提取的帧、`final/spritesheet.png` 和 imagegen 工作清单。当用户想要调试工件或运行仍然需要修复时，跳过清理。

## 轻量级视觉工作器

默认情况下，使用轻量级子代理进行图像密集型工作。这限制了每个 `$imagegen` 展开到选定的一个图像，将联系表视觉有效载荷保持在父线程之外，并在保留完整 9 状态应用程序合同的同时降低成本。

## 子代理委托

除非用户明确禁止，否则使用子代理为此运行。如果用户未允许使用子代理，或者子代理使用的意图模糊，则询问用户是否允许为并行工作路径生成子代理。

父级责任：

- 当用户提供纯品牌/产品/公司/潜在客户名称时，在准备之前运行品牌发现工作器
- 准备运行并检查 `imagegen-jobs.json`
- 将基础工作、行工作和最终联系表 QA 分配给轻量级工作器
- 将选定的工作器输出复制到其解码路径，并在 `imagegen-jobs.json` 中标记工作完成
- 从选定的基础输出创建 `references/canonical-base.png`
- 在适当的时候运行批准的 `running-left` 镜像派生
- 运行确定性图像处理、打包、修复再生和清理

基础工作器责任：

- 仅处理 `base` 工作
- 读取 `prompts/base-pet.md` 并使用任何列出的参考图像
- 仅使用 `$imagegen`
- 尊重提示中任何紧凑的品牌灵感行作为广泛的视觉/个性指导，而不复制标志、可读标记、UI 截图、口号或文本
- 仅返回 `selected_source=/absolute/path/to/selected-output.png` 和 `qa_note=<one sentence>`

行工作器责任：

- 精确处理一个行工作
- 读取行提示并使用所有列出的输入图像
- 仅使用 `$imagegen`；不要在本地绘制、编辑、平铺或合成精灵
- 执行快速视觉检查：帧数、身份、色度背景、间距、剪辑和分离效果
- 执行行提示的透明度和效果规则，包括没有分离效果、没有 `waving` 的波浪标记、没有方向运行行的速度线或灰尘、没有非方向 `running` 行的字面脚步运行，以及仅当状态提示允许时才允许附加的不透明精灵状眼泪/烟雾/星星
- 仅返回 `selected_source=/absolute/path/to/selected-output.png` 和 `qa_note=<one sentence>`

最终视觉 QA 工作器责任：

- 检查 `qa/contact-sheet.png` 以及 `qa/previews/` 下的行 GIF，以及 `qa/review.json` 和 `final/validation.json` 作为有用的文本上下文
- 验证所有 9 行都符合 Codex 应用程序状态合同和相同的宠物身份
- 返回紧凑的结果：`visual_qa=pass` 或 `visual_qa=fail`，以及当失败时行特定的修复备注
- 不要编辑文件、排队修复、打包或清理

工作器模型选择：

- 对于品牌发现，优先选择较小的有能力的模型，因为它返回紧凑的研究简报，而不是进行编排。
- 当模型覆盖可用时，优先选择较小的有能力的模型用于视觉工作器，例如 `gpt-5.4-mini` 带有中等推理。
- 仅在编排或较小的工人模型不可用时使用父级/默认模型。
- 最多同时保持两个生成工作器活动，除非用户明确要求更高的并行性。在确定性图像处理后作为单个工作器运行最终视觉 QA。在工作器结果被消耗后关闭工作器。

使用此基础工作器提示：

```text
生成 hatch-pet 基础图像。

运行目录： <绝对运行目录>
工作 ID： base
提示文件： <绝对基础提示文件>
输入图像：
- <绝对路径> — <角色>

仅使用 $imagegen。读取基础提示并附加每个列出的输入图像。如果提示包含品牌灵感，仅将其用作广泛的吉祥物安全指导；不要复制标志、可读标记、UI 截图、口号或文本。返回之前，视觉检查结果是否为居中全身宠物，在平坦色度背景上，没有文本、场景、阴影或分离效果。

不要编辑清单、复制到解码、标记工作完成、生成行、运行图像处理脚本、修复、打包或打开无关文件。
不要在最终响应中包含 Markdown 图像预览、base64 或额外附件。

返回：
selected_source=/absolute/path/to/selected-output.png
qa_note=<one sentence>
```

使用此行工作器提示：

```text
生成一个 hatch-pet 行。

运行目录： <绝对运行目录>
行 ID： <row-id>
提示文件： <绝对提示文件>
重试提示文件： <绝对重试提示文件>
输入图像：
- <绝对路径> — <角色>
- <绝对路径> — <角色>

仅使用 $imagegen。读取行提示并附加每个列出的输入图像。如果 imagegen 返回 Bad Request，使用重试提示和相同的输入图像重新尝试一次。

返回之前，视觉检查：精确帧数、与规范基础相同的宠物身份、平坦色度背景、完整的分离未剪辑姿势，以及没有分离效果或指南标记。提示的透明度和效果规则是强制性的：没有分离效果、没有 `waving` 的波浪标记、没有方向运行行的速度线或灰尘、没有非方向 `running` 行的字面脚步运行，以及仅当状态提示允许时才允许附加的不透明精灵状眼泪/烟雾/星星。

不要编辑清单、复制到解码、标记工作完成、镜像行、运行图像处理脚本、修复、打包或打开无关文件。
不要在最终响应中包含 Markdown 图像预览、base64 或额外附件。

返回：
selected_source=/absolute/path/to/selected-output.png
qa_note=<one sentence>
```

使用此最终视觉 QA 工作器提示：

```text
可视化检查最终完成的孵化宠物接触表。

运行目录：<绝对运行目录>
接触表：<绝对运行目录>/qa/contact-sheet.png
预览目录：<绝对运行目录>/qa/previews
评审 JSON：<绝对运行目录>/qa/review.json
验证 JSON：<绝对运行目录>/final/validation.json

通过可视化检查接触表和预览 GIF，确认所有行中宠物身份、风格、调色板、轮廓、面部、比例和道具的一致性：
0 待机，1 向右跑，2 向左跑，3 挥手，4 跳跃，5 失败，6 等待，7 跑步，8 评审。

失败行包括身份漂移、缺失/空白帧、复制的引导标记、白色/非透明背景、裁剪的身体、槽位重叠、分离的特效、阴影/辉光/涂抹/灰尘、色度键伪影、与行状态不符的运动、意外尺寸弹出、错误朝向、反向或非交替步态、静态的待机循环。

不要编辑文件、排队修复、打包、清理或检查无关文件。

返回以下内容：
visual_qa=pass|fail
qa_note=<一句话总结>
repair_rows=<逗号分隔的行 ID，或 none>
repair_notes=<简短的行特定注释，或 none>
```

## 修复工作流程

如果帧检查或最终可视化评审失败，请读取 `qa/review.json`，重新生成最小的失败范围，将替换行复制到相同的解码输出路径，并将该任务标记为完成，使用新的 `source_path` 和 `completed_at`。修复失败的行，而不是整个表格。

对于身份修复，使用规范基础图像、原始参考、接触表和精确的行失败注释作为基础上下文。给行工作者现有的行提示加上来自 `qa/review.json` 的紧凑修复注释；保留规范宠物身份和选择风格。

对于提取引起的运动弹出，首先不要重新生成图像。如果源条带已经保留行级比例和基线，请使用 `--method stable-slots` 重新运行确定性管道，使用 `--allow-stable-slots` 检查，然后重新检查预览 GIF。只有当原始条带本身被裁剪、不稳定或语义错误时，才重新生成行。

## 规则

- 保持 `$imagegen` 作为主要生成层。
- 对于没有具体头像描述或参考图像的品牌/产品/公司/潜在客户请求，在基础生成之前运行品牌发现，并将紧凑的简要信息传递给运行。
- 仅使用 `$imagegen` 作为唯一的可视化生成层。不要调用图像 API、图像 CLI、本地光栅生成器或一次性生成脚本。
- 当选择路径支持参考时，始终将参考图像附加/可见于 `$imagegen`。
- 将行的 `references/layout-guides/<state>.png` 图像附加到每个行条带作业，作为仅布局的引导，并且不接受复制引导像素的输出。
- 默认使用轻量级可视化工作者进行基础生成、行条带可视化生成和最终接触表评审；父级拥有清单更新、确定性图像脚本、打包和清理。
- 使用 `$imagegen` 生成所有正常可视化作业：基础加上所有未明确批准为 `running-left` 镜像衍生的行条带。
- 仅将基础作业视为仅提示生成合格的作业；每个行作业必须附加其列出的基础图像。
- 在决定是否可以镜像 `running-left` 之前，先生成 `running-right`。
- 当 `running-left` 被镜像时，保留帧顺序和时序语义；通过确定性脚本导出，而不是整体镜像整个条带。
- 不要从其他状态派生或重用 `waiting`、`running`、`failed`、`review`、`jumping` 或 `waving`；每个都有独特的应用语义，必须作为自己的行生成。
- 不要用本地绘制、平铺、变换或代码生成的行条带替代缺失的 `$imagegen` 输出。
- 仅在选定输出已复制到解码输出路径后，才标记可视化作业完成。
- 不要依赖生成图像进行精确的图集几何；使用此技能的确定性图像脚本。
- 使用存储在 `pet_request.json` 中的色度键；不要强制固定绿幕。
- 在所有行中保持宠物的轮廓、面部、材质、调色板、风格和道具一致。
- 即使 `qa/review.json` 和 `final/validation.json` 没有错误，也要将视觉身份或风格漂移视为阻断器。
- 将显示裁剪参考、重复平铺、白色单元格背景或非精灵碎片接触表视为失败。
- 将显示提取引起的尺寸弹出、反向方向时序、错误朝向或惰性待机循环的预览 GIF 视为失败。
- 将禁止分离的特效、色度键相邻伪影、阴影、辉光、涂抹、灰尘、着陆标记、挥手标记、速度线或运动轨迹视为失败行。
- 将 `qa/review.json` 错误视为阻断器。警告需要可视化评审。

## 接受标准

- 最终图集是 PNG 或 WebP，`1536x1872`，支持透明，基于 `192x208` 单元格。
- 使用单元格非空，未使用单元格完全透明。
- 图集遵循 `references/animation-rows.md` 中的行/帧计数。
- 接触表和每行运动预览已由轻量级可视化评审工作者生成和检查。
- `qa/review.json` 没有错误。
- 行级评审确认动画循环足够完整，适用于 Codex 应用。
- 运动预览没有显示意外的尺寸弹出、反向方向节奏或错误行语义。
- 当宠物尺寸可读且行间一致时，接受非像素风格。
- `${CODEX_HOME:-$HOME/.codex}/pets/<pet-name>/pet.json` 和 `${CODEX_HOME:-$HOME/.codex}/pets/<pet-name>/spritesheet.webp` 对于自定义宠物一起准备。
