# Hatch Pet

## 概述

根据概念、品牌提示、公司/潜在客户名称、一个或多个参考图像，或这些输入的组合来创建兼容Codex的动画宠物。此工作流程保留用于图谱几何、验证、视觉质量保证和打包的确定性hatch-pet管道，同时使用简洁的状态特定提示，并允许任何宠物安全的视觉风格。

面向用户的输入是可选的。如果用户省略宠物名称，则从概念、品牌、公司或参考文件名中推断一个；如果无法做到这一点，则选择一个简短友好的名称。如果用户省略描述，则从概念或参考中推断一个。如果用户省略参考图像，则首先从文本生成基本宠物，然后使用该基本宠物作为每个动画行的规范参考。

## 生成委托

对所有正常视觉生成使用`$imagegen`。

在生成基本艺术、行条或修复行之前，加载并遵循已安装的图像生成技能：

```text
${CODEX_HOME:-$HOME/.codex}/skills/.system/imagegen/SKILL.md
```

不要直接调用图像API、图像CLI或任何其他图像生成路径。让`$imagegen`选择其自己的内置优先路径和回退规则。如果`$imagegen`说回退需要确认，则在继续之前询问用户。

在调用`$imagegen`时，将生成的宠物提示作为权威的视觉规范。宠物提示应保持简洁、状态特定、面向精灵生产，并基于列出的输入图像。将更长的策略和QA规则保留在此技能和确定性审查脚本中，而不是将它们扩展到每个图像提示中。不要将提示包装在通用的`$imagegen`共享提示模式中。

仅使用此技能的脚本进行确定性图像工作：准备布局指南和提示、镜像批准的`running-left`、提取帧、验证行、组合最终图谱，以及创建联系表和运动预览QA媒体。父拥有的shell/`jq`步骤处理清单更新、打包和清理。

## 存储控制

内置的`$imagegen`路径将生成的PNG字节存储在调用它的滚动中，即使它也在`${CODEX_HOME:-$HOME/.codex}/generated_images`下写入文件。删除文件后可以减少文件系统使用，但它不会缩小已写入的滚动。保持图像生成隔离和边界：

- 每个视觉工作使用一个轻量级生成工作进程。不要将多个基本/行工作批量到同一个工作进程。
- 工作进程必须仅返回`selected_source=...`和`qa_note=...`；它们不得在其最终响应中包含Markdown图像预览、base64或额外的视觉附件。
- 父进程不得视觉上打开每个生成的PNG。使用工作进程QA，并仅检查最终联系表。
- 将选定的生成输出复制到`decoded/`后，当它存在于`${CODEX_HOME:-$HOME/.codex}/generated_images`中时，删除选定的原始文件，然后删除其现在空的生成目录（如果可能）。
- 对于存储敏感的完整运行，当可用时，询问用户是否要使用`$imagegen` CLI回退。该路径需要本地API凭证和明确用户确认，但它可以避免内置图像有效负载嵌入到滚动事件中。

## 品牌发现

如果用户提供一个品牌、公司、产品或潜在客户名称，而不是具体的头像描述或参考图像，则在准备宠物运行之前运行轻量级发现子代理。发现工作必须使用网络搜索，并优先考虑官方来源，例如品牌网站、产品页面、文档、关于页面、新闻页面或品牌页面。仅在官方页面过于稀疏时使用信誉良好的二级来源。保持搜索范围：足够提取视觉和个性提示，而不是市场研究摘要。

当用户已经提供具体的吉祥物/头像描述或参考图像时，除非用户明确要求品牌研究，否则跳过发现。

发现工作职责：

- 在网上搜索2-4个相关来源，优先考虑官方页面
- 写一个自适应的markdown简报，而不是僵化的字段转储
- 涵盖身份/类别、受众/使用上下文、视觉系统、个性/语气、产品/领域主题、吉祥物翻译提示、避免事项和证据/信心
- 将从来源推断的吉祥物指导标记为推断
- 避免复制标志、可读标记、UI截图、口号或文本
- 以包含仅`brand_name`、`brand_brief`、`avatar_seed`、`avoid`和`brand_sources`的紧凑`Generation handoff`部分结束
- 不要生成图像、准备运行文件夹或编辑不相关的文件

使用此发现工作提示：

```text
为hatch-pet吉祥物创建品牌研究。

品牌/产品/潜在客户：<品牌名称>
用户上下文：<简短用户请求>
输出文件：<绝对路径到brand-discovery.md>

使用网络搜索。优先考虑官方品牌、产品、文档、关于、新闻或品牌页面。如果官方来源过于稀疏，则仅使用信誉良好的二级来源。编写自适应的markdown简报到输出文件。标题可以按品牌灵活，但简报必须涵盖：
- 身份/类别：规范名称、产品类型、用途
- 受众/使用上下文：它服务于谁以及它出现在哪里
- 视觉系统：调色板、形状、线条质量、材料、排版感觉、图标、模式
- 个性/语气：情感特征、能量、正式性、俏皮
- 产品/领域主题：对象、工作流程、动词、隐喻、环境
- 吉祥物翻译提示：候选形式、标志性特征、道具、宠物尺寸必须读取的内容
- 避免事项：标志/文本、商标敏感元素、误导性提示、竞争对手混淆、不合适的吉祥物
- 证据/信心：来源URL加上证据薄弱或推断的注释

不要复制标志、可读标记、UI截图、口号或文本。清楚地标记推断而不是直接来源的吉祥物指导。

以`Generation handoff`部分结束简报，其中包含正好：
- brand_name=<规范品牌/产品名称>
- brand_brief=<一句话，最多45个字，涵盖调色板/语气/领域主题/个性>
- avatar_seed=<简短的吉祥物安全视觉想法，不复制标志>
- avoid=<简短的逗号分隔列表>
- brand_sources=<逗号分隔的来源URL>

返回正好：
brand_discovery_file=<绝对输出文件路径>
brand_name=<规范品牌/产品名称>
brand_brief=<来自Generation handoff的相同紧凑句子>
avatar_seed=<来自Generation handoff的相同简短种子>
avoid=<来自Generation handoff的相同简短避免列表>
brand_sources=<来自Generation handoff的相同逗号分隔URL>
```

父进程应在准备运行之前保存markdown简报，然后将其作为`--brand-discovery-file`传递给`prepare_pet_run.py`，并一起传递`--brand-name`、`--brand-brief`，当用户没有提供更好的头像描述时，重复`--brand-source`，并根据`avatar_seed`提供一个简洁的`--pet-notes`值。

对于品牌请求，首先运行发现工作，保存markdown简报，然后将简报路径通过`--brand-discovery-file`传递，`avatar_seed`通过`--pet-notes`传递，`brand_name`通过`--brand-name`传递，`brand_brief`通过`--brand-brief`传递，每个来源URL通过重复的`--brand-source`传递。

对于正常的宠物运行，预期最多10个视觉生成工作：1个基本宠物加上9个行条工作。Codex应用程序合同目前使用所有9个状态：`idle`、`running-right`、`running-left`、`waving`、`jumping`、`failed`、`waiting`、`running`和`review`。唯一确定性视觉派生是`running-left`，它可能仅在生成、视觉检查并明确批准为安全后，通过镜像`running-right`来生成。如果镜像不合适，则作为正常的基于`$imagegen`的行生成`running-left`。

选择视觉输出后，将精确的图像复制到作业的`decoded/`路径中，并在`imagegen-jobs.json`中标记作业完成。不要编写填充行输出的辅助脚本。确定性Python脚本只能处理已生成的视觉输出。

仅基本工作可以是提示工作。通过`$imagegen`生成的每个行条工作必须使用在`imagegen-jobs.json`中列出的输入图像，包括在选定基本输出复制后创建的规范基本参考。将任何没有附加接地图像的行生成视为无效。

## 宠物安全风格

默认风格是`auto`：从用户的提示和参考中推断宠物的风格，然后在每一行中保留该风格。如果用户指定了风格，则尊重它。支持的风格预设包括`pixel`、`plush`、`clay`、`sticker`、`flat-vector`、`3d-toy`、`painterly`、`brand-inspired`和`auto`。

只要风格保持宠物安全，任何风格都是可接受的：

- 整体身体轮廓在`192x208`单元内可读
- 在所有行中保持一致的 face、比例、材料、调色板和道具
- 清洁可移除的chroma-key背景
- 足够大的细节可以在宠物尺寸下阅读
- 除非用户提供批准的参考艺术并要求它们，否则不显示文本、标签、UI或可读标志

非像素风格是一流。Plush、clay、sticker、vector、3D toy、painterly吉祥物、ink和brand-inspired外观应在满足图谱和可读性约束时被接受。

## 透明度和效果

宠物行被处理成透明的`192x208`单元，因此每个生成的像素必须要么属于宠物精灵，要么是清洁可移除的chroma-key背景。优先考虑姿势、表情和轮廓变化，而不是装饰性效果。

确定性光栅管道拥有透明度不变量：变为完全透明的像素被标准化，以便它们不会保留隐藏的RGB残留，并且如果导出的文件违反该不变量，则图谱验证应失败。不要通过接受视觉不一致的输出来掩盖彩色光晕或透明像素残留。

允许的效果必须满足所有这些条件：

- 效果与状态相关，有助于解释动画。
- 效果与宠物轮廓物理连接、接触或重叠，而不是附近浮动。
- 效果与宠物位于同一帧槽内，并且不会创建单独的精灵组件。
- 效果是不透明的，边缘足够硬以便清洁提取，并使用非chroma-key颜色。
- 效果足够小，以便在`192x208`下保持可读性，而不会杂乱。

默认情况下应避免这些，因为它们通常会破坏透明背景清理或组件提取：

- 波浪标记、运动弧、速度线、动作条纹、运动残留、模糊或涂抹
- 分离的星星、松散的火花、漂浮的标点符号、漂浮的图标、下落的泪滴、分离的烟雾云或松散的灰尘
- 投影阴影、接触阴影、落地阴影、椭圆形地板阴影、地板补丁、着陆标记、冲击爆发、发光、光晕、光环或软透明效果
- 文本、标签、帧编号、可见网格、指南标记、对话气泡、思想气泡、UI面板、代码片段、棋盘透明度、白色背景、黑色背景或场景
- 宠物、道具、效果、高光或阴影中的chroma-key相邻颜色
- 杂乱的像素、断开的轮廓碎片、斑点/噪声、裁剪的身体部分、重叠的姿势或任何跨越到相邻帧槽的姿势

状态特定指导：

- `idle`：保持此平静且低干扰。仅使用微妙的呼吸、微小的眨眼、轻微的头部或身体摆动、非常小的材料摇摆或另一个安静的人格保留动作。循环必须仍然包含可见的微观变化；不要接受六个实际上相同的副本。不要显示挥手、行走、跑步、跳跃、说话、工作、审查、情绪反应、大型手势、项目交互或新道具。
- `waving`：仅通过爪子、手、翅膀或肢体姿势显示挥手。不要绘制波浪标记、运动弧、线条、火花、符号或漂浮效果围绕手势。
- `jumping`：仅通过身体位置显示垂直运动。不要绘制阴影、灰尘、着陆标记、冲击爆发、弹跳垫或地板提示。
- `failed`：如果它们遵守允许的效果规则，则允许眼泪、附着的烟雾泡或附着的星星；不要使用红色X标记、漂浮符号、分离的烟雾、分离的星星或分离的泪滴。
- `waiting`：通过期待性的提问姿势显示Codex需要批准、帮助或用户输入。将其与普通的idle和审查区分开来。
- `running`：显示积极任务工作、处理、思考、扫描、输入或专注努力。不要显示字面的脚跑步、慢跑、冲刺、跑步机运动、抬起的膝盖、长步、挥动手臂、方向旅行、速度线、灰尘云、地板阴影、运动轨迹或分离的运动效果。
- `review`：通过倾斜、眨眼、眼睛、头部倾斜或爪子/手位置显示关注。不要添加放大镜、纸张、代码、UI、标点符号、符号或除非它们已经存在于基本宠物身份中的其他新道具。

## 可见进度计划

对于每个宠物运行，保持一个可见的清单，以便用户可以看到工作的进度。在开始之前创建清单，一次保持一个步骤活跃，并在每个步骤完成后更新它。

使用此清单进行正常宠物运行，将`<Pet>`替换为宠物的名称或`your pet`：

1. 准备`<Pet>`。
2. 想象`<Pet>`的主要外观。
3. 想象`<Pet>`的姿势。
4. Hatch`<Pet>`。

每个步骤的含义：

- `准备 <Pet> .` 选择或确认宠物名称、描述、源图像、风格预设、风格注释和工作文件夹。对于仅品牌/产品/公司请求，首先运行品牌发现工作并捕获紧凑的品牌简报、来源URL和avatar seed。
- `想象 <Pet> 的主要外观.` 生成宠物的主要参考图像。这成为视觉真相。
- `想象 <Pet> 的姿势.` 通过轻量级工作生成姿势行，从`idle`和`running-right`开始确认身份和步态。仅在`running-right`明确工作翻转时才镜像`running-left`。
- `Hatching <Pet> .` 将批准的姿势转换为最终的宠物文件，审查联系表、预览和验证结果，修复任何损坏的部分，保存`pet.json`和`spritesheet.webp`，然后报告输出路径。

仅当实际文件、图像或决策存在时才标记步骤完成。如果是修复运行，则从第一个相关步骤开始，而不是重新启动整个清单。

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

上述所有参数除任何需要表达用户约束的标志外都是可选的。对于纯文本请求，通过`--pet-notes`传递概念，并省略`--reference`；`prepare_pet_run.py`将推断名称、描述、chroma key和输出目录按需。
对于仅品牌请求，首先运行发现工作，保存markdown简报，然后将简报路径通过`--brand-discovery-file`传递，`avatar_seed`通过`--pet-notes`传递，`brand_name`通过`--brand-name`传递，`brand_brief`通过`--brand-brief`传递，每个来源URL通过重复的`--brand-source`传递。

2. 检查`imagegen-jobs.json`以查找下一个准备好的`$imagegen`工作。当工作的`status`不是`complete`并且`depends_on`中的每个id都已完成后，工作才准备好。优先直接使用`jq`或编辑器读取清单，而不是添加辅助脚本以显示状态：

```bash
jq '.jobs[] | {id, kind, status, depends_on, prompt_file, retry_prompt_file, input_images, output_path, derivation_policy}' /absolute/path/to/run/imagegen-jobs.json
```

3. 默认使用轻量级工作进程生成视觉工作：

- 首先生成并复制`base`，使用轻量级基本工作。
- 接下来生成并复制`idle`和`running-right`，作为身份和步态检查，每个行使用一个轻量级工作进程。
- 检查`running-right`；仅在视觉身份、道具放置、标记、照明和方向语义保持正确时镜像`running-left`。
- 当镜像会改变意义或身份时，使用轻量级工作进程正常生成`running-left`。
- 使用轻量级工作进程生成其余行，使用每个工作列出的所有输入图像。

对于每个准备好的视觉工作，使用`imagegen-jobs.json`中列出的提示文件调用`$imagegen`，使用其角色标签的每个列出的输入图像，除非`$imagegen`本身路由否则使用默认内置的`image_gen`路径。父代理必须保持其图像处理最小：不要在父滚动中打开每个生成的基线或行。工作进程仅返回`selected_source=/absolute/path/to/selected-output.png`和`qa_note=<one sentence>`；父代理必须将选定的源路径记录在清单中。

`prepare_pet_run.py`在`references/layout-guides/`下创建9个行特定布局指南图像，每个动画状态一个，并将匹配的指南作为布局仅输入附加到每个行条工作，以便模型遵循正确的帧数、间距、居中和安全填充。将这些指南视为不可见的施工参考：生成的行条不得包含可见的框、边框、中心标记、标签、指南颜色或指南背景。

在生成行条时，保持行提示中的身份锁权威。保留与规范基线相同的风格、脸、标记、调色板、材料、道具设计、身体比例和轮廓。行工作默认附加布局指南和规范基线；解码基线保存在运行文件夹中以便确定性处理，而不是作为冗余生成输入发送。

如果`$imagegen`返回传输级别的`Bad Request`对于行，使用生成的`retry_prompt_file`对该行重试一次。重试提示保留了行id、帧数、chroma key、规范基线身份和状态动作。保留规范基线。如果重试仍然失败，则停止并报告失败的行和提示路径，而不是切换到任何其他生成路径。

4. 选择作业的生成输出后，将其复制到解码输出路径，并在`imagegen-jobs.json`中标记作业完成。对于`base`，还创建规范身份参考：

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

如果复制的源位于`${CODEX_HOME:-$HOME/.codex}/generated_images`中，则在解码副本存在后删除原始生成的文件：

```bash
GENERATED_ROOT="${CODEX_HOME:-$HOME/.codex}/generated_images"
case "$SOURCE" in
  "$GENERATED_ROOT"/*)
    rm -f "$SOURCE"
    rmdir "$(dirname "$SOURCE")" 2>/dev/null || true
    ;;
esac
```

5. 仅当视觉安全时才派生`running-left`：

```bash
python "$SKILL_DIR/scripts/derive_running_left_from_running_right.py" \
  --run-dir /absolute/path/to/run \
  --confirm-appropriate-mirror \
  --decision-note "<为什么镜像保留了这只宠物的身份>"
```

该脚本将每个生成的帧槽就地镜像，以便左侧行保留右侧行的时序顺序。不要用镜像整个条带来颠倒动画时序。

6. 当所有工作都完成时，直接运行图像处理脚本：

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

如果预览GIF显示由每帧拟合到单元引起的尺寸弹出或基线跳跃，并且原始行条本身具有稳定的比例和位置，则使用显式行稳定性模式重新运行帧提取，然后重新运行检查、图谱组合、验证、联系表生成和预览：

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

使用`stable-slots`作为故意的QA驱动的更正，而不是默认值。它应减少提取引起的运动弹出，而不会隐藏剪辑的宽姿势或不良源条带。

预期清理前的输出：

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

打包输出默认写在运行目录外部。如果设置了`CODEX_HOME`，则使用它；否则使用`$HOME/.codex`。

```text
${CODEX_HOME:-$HOME/.codex}/pets/<pet-name>/
  pet.json
  spritesheet.webp
```

使用shell和`jq`打包输出：

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

打包后写入`qa/run-summary.json`：

```bash
jq -n --arg run_dir "$RUN_DIR" --arg spritesheet "$RUN_DIR/final/spritesheet.webp" --arg validation "$RUN_DIR/final/validation.json" --arg contact_sheet "$RUN_DIR/qa/contact-sheet.png" --arg review "$RUN_DIR/qa/review.json" --arg package "$PET_DIR" '{ok: true, run_dir: $run_dir, spritesheet: $spritesheet, validation: $validation, contact_sheet: $contact_sheet, review: $review, package: $package}' > "$RUN_DIR/qa/run-summary.json"
```

在确定性图像处理之后，使用轻量级视觉QA工作进程检查`qa/contact-sheet.png`和`qa/previews/`下的行GIFs，使用`qa/review.json`和`final/validation.json`作为文本上下文，当有用时：

- 验证所有9行匹配Codex应用程序状态合同并具有相同的宠物身份
- 返回紧凑的结果：`visual_qa=pass`或`visual_qa=fail`，以及行特定修复注释

## 接受标准

- 最终图谱是PNG或WebP、`1536x1872`、支持透明度，基于`192x208`单元。
- 使用单元是非空的，未使用的单元是完全透明的。
- 图谱遵循`references/animation-rows.md`中的行/帧计数。
- 已经生成并检查了联系表和每行运动预览，并由轻量级视觉QA工作进程检查。
- `qa/review.json`没有错误。
- 逐行审查确认动画循环足够完整，可以使用Codex应用程序。
- 运动预览不显示意外的尺寸弹出、反向的方向节奏或错误的行语义。
- 非像素风格在宠物尺寸下可读且跨行一致时被接受。
- `${CODEX_HOME:-$HOME/.codex}/pets/<pet-name>/pet.json`和`${CODEX_HOME:-$HOME/.codex}/pets/<pet-name>/spritesheet.webp`为自定义宠物一起准备。
