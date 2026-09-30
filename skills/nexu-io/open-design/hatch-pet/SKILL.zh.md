---
name: hatch-pet
description: 创建、修复、验证、预览和打包与Codex兼容的动画宠物精灵图集，可从角色艺术、截图、生成图像或视觉参考中创建。当用户想要孵化Codex宠物、创建自定义动画宠物，或构建具有8x9图集、透明未使用单元格、逐行动画提示、QA联系图集、预览视频和pet.json打包的内置宠物资源时使用。此技能组合了已安装的图像生成系统技能，并使用捆绑脚本进行确定性精灵图集组装。
---

# Hatch Pet

> **OpenDesign 集成。** 这是未经修改的 Codex `hatch-pet` 技能，
> 在 `skills/hatch-pet/` 下进行封装，以便任何 OpenDesign 代理都可以运行它。技能打包完成后，生成的 `spritesheet.webp`
> （位于 `${CODEX_HOME:-$HOME/.codex}/pets/<pet-name>/` 下）可以导入到浮动宠物伙伴中，通过 **设置 → 常规 → 宠物 → 导入 Codex 矢贴**。导入流程会自动检测 8×9 / `192×208` 的图集，并允许用户选择要播放的动画行（空闲、向右跑、挥手、…）。

## 概述

从一个概念、一个或多个参考图像或两者创建一个与 Codex 兼容的动画宠物。此技能拥有宠物特定的提示规划、动画行、帧提取、图集几何形状、问答、预览和打包。它将视觉生成委托给 `$imagegen`。

面向用户的输入是可选的。如果用户省略宠物名称，则从概念或参考文件名中推断一个名称；如果无法做到这一点，则选择一个简短合适的名称。如果用户省略描述，则从概念或参考中推断一个描述。如果用户省略参考图像，则首先从文本生成基础宠物，然后使用该基础作为每个动画行的规范参考。

## 生成委托

对所有正常视觉生成使用 `$imagegen`。

在生成基础艺术、行条或修复行之前，加载并遵循已安装的图像生成技能：

```text
${CODEX_HOME:-$HOME/.codex}/skills/.system/imagegen/SKILL.md
```

不要直接调用图像 API 进行正常路径。让 `$imagegen` 选择它自己的内置优先路径和它自己的 CLI 回退规则。如果 `$imagegen` 说回退需要确认，则在继续之前询问用户。

从此技能中调用 `$imagegen` 时，将生成的宠物提示作为权威的视觉规范。不要将其包装在通用的 `$imagegen` 共享提示模式中，也不要添加额外的抛光、英雄艺术、照片、产品或插图风格增强。宠物提示应保持简洁、矢量特定和数字宠物导向；仅添加输入图像的角色标签和任何必要的用户约束。

仅使用此技能的脚本进行确定性工作：准备提示和清单、导入选定的 `$imagegen` 输出、提取帧、验证行、组合最终图集、创建问答媒体和打包。

硬边界：不要使用本地 Python/Pillow 脚本、SVG、画布、HTML/CSS 或其他代码原生艺术来创建、绘制、平铺、扭曲、镜像或合成宠物视觉效果，以此替代 `$imagegen`。对于正常宠物运行，预期最多 10 个视觉生成任务：1 个基础宠物加上 9 个行条任务。唯一的例外是 `running-left`，它只能在 `running-right` 已生成、视觉检查并明确批准为可以镜像后，通过镜像 `running-right` 来派生。如果镜像不合适，则作为正常的 `$imagegen` 行生成 `running-left`。如果这些调用过于昂贵、被阻塞或不可用，则停止并解释阻塞原因，而不是在本地伪造行条。

不要通过编辑 `imagegen-jobs.json`、将文件复制到 `decoded/` 或编写填充行输出的辅助脚本来标记视觉任务完成。使用 `record_imagegen_result.py` 来记录选定的内置 `$imagegen` 输出，或仅使用 `generate_pet_images.py` 来记录文档中说明的次要回退。确定性脚本只能处理已生成的视觉输出。

只有基础任务可以是提示仅任务。通过 `$imagegen` 生成的每个行条任务都必须使用 `imagegen-jobs.json` 中列出的输入图像，包括在基础任务记录后创建的规范基础参考。将任何没有附加接地图像的行生成视为无效。

## Codex 数字宠物风格

默认宠物艺术应与 Codex 应用的内置数字宠物匹配：小型类似像素艺术的角色，紧凑的 chibi 比例，粗略可读的轮廓，厚重的深色 1-2 px 轮廓，可见的阶梯/像素边缘，有限的调色板，平面赛璐璐着色，简单的表情，微小的肢体。即使参考艺术更详细、更复杂或更逼真，生成的宠物也应简化为此风格。

**不要**生成抛光的插图、绘画渲染、动画关键艺术、3D 渲染、光泽应用图标处理、逼真的毛发或材质纹理、柔和渐变、高细节抗锯齿和复杂的微小配饰。比此更详细的参考应在行生成之前简化为房屋风格。

## 透明度和效果

宠物行被处理为透明的 192x208 单元，因此每个生成的像素必须要么属于宠物矢量，要么是干净可移除的色度键背景。优先考虑姿势、表情和轮廓变化，而不是装饰效果。

允许的效果必须满足所有这些条件：

- 效果与状态相关，并有助于解释动画。
- 效果与宠物轮廓物理连接、接触或重叠，而不是悬浮在附近。
- 效果位于与宠物相同的帧槽中，并且不会创建单独的矢量组件。
- 效果是-opaque、硬边、像素风格，并使用非色度键颜色。
- 效果足够小，在 192x208 下保持可读性，不会杂乱。

允许的效果示例：一滴眼泪接触脸部，一个小的烟雾团接触盒子或头部，或在小星星在失败/头晕反应期间重叠宠物时。

默认情况下避免这些，因为它们通常会破坏透明背景清理或组件提取：

- 波浪标记、运动弧线、速度线、动作条纹、残像、模糊或涂抹
- 分离的星星、松散的闪光、悬浮的标点符号、悬浮的图标、落下的泪滴、分离的烟雾云或松散的灰尘
- 投影阴影、接触阴影、阴影、椭圆地板阴影、地板补丁、着陆标记、冲击爆发、发光、光晕、光环或柔和透明效果
- 文本、标签、帧编号、可见网格、引导标记、对话气泡、思想气泡、UI 面板、代码片段、棋盘透明度、白色背景、黑色背景或场景
- 宠物、道具、效果、高光或阴影中的色度键相邻颜色
- 迷失像素、断开的轮廓碎片、斑点/噪声、裁剪的身体部分、重叠姿势或任何跨越到相邻帧槽的姿势

状态特定指南：

- `waving`：仅通过爪子姿势显示波浪。不要绘制波浪标记、运动弧线、线条、闪光或符号围绕爪子。
- `jumping`：仅通过身体位置显示垂直运动。不要绘制阴影、灰尘、着陆标记、冲击爆发、弹跳垫或地板提示。
- `failed`：如果它们遵守允许效果规则，允许眼泪、附加的烟雾团或附加的星星；不要使用红色 X 标记、悬浮符号、分离的烟雾、分离的星星或分离的泪滴。
- `review`：通过倾斜、眨眼、眼睛、头部倾斜或爪子位置显示焦点。除非该道具已在基础宠物身份中存在，否则不要添加放大镜、纸张、代码、UI、标点符号或符号。
- `running-right`、`running-left` 和 `running`：仅通过身体、肢体和道具运动显示运动。不要绘制速度线、灰尘云、地板阴影或运动轨迹。

## 宠物命名

当用户没有提供宠物名称并且对话自然允许时，询问用户宠物名称。如果询问会减慢直接执行请求的速度，则从宠物概念、参考图像或个性中选择一个简短合适的名称，然后使用该名称始终如一地作为显示名称和作为包文件夹缩写的来源。

内置风格的良好示例：

- Codex - The original Codex companion.
- Dewey - A tidy duck for calm workspace days.
- Fireball - Hot path energy for fast iteration.
- Rocky - A steady rock when the diff gets large.
- Seedy - Small green shoots for new ideas.
- Stacky - A balanced stack for deep work.
- BSOD - A tiny blue-screen gremlin.
- Null Signal - Quiet signal from the void.

## 可见进度计划

对于每个宠物运行，保持一个可见的清单，以便用户可以看到工作进度。在开始之前创建清单，一次保持一个步骤激活，并在每个步骤完成后更新它。

在创建清单之前，尽可能确定宠物名称。使用用户提供的名称；否则从概念或参考中推断一个简短合适的名称。如果名称太长、未确定或不适合友好的清单，则使用 `your pet`。

使用此清单进行正常宠物运行，将 `<Pet>` 替换为宠物的名称或 `your pet`：

1. Getting `<Pet>` ready.
2. Imagining `<Pet>`'s main look.
3. Picturing `<Pet>`'s poses.
4. Hatching `<Pet>`.

每个步骤的含义：

- `Getting <Pet> ready.` 选择或确认宠物名称、描述、源图像和工作文件夹。
- `Imagining <Pet>'s main look.` 生成宠物的主参考图像。即使用户没有提供图像，这也是必需的，因为它成为视觉真相来源。
- `Picturing <Pet>'s poses.` 创建姿势行，从 `idle` 和 `running-right` 开始以确认宠物仍然看起来一致。仅在 `running-right` 明确翻转时工作时，才镜像 `running-left`。
- `Hatching <Pet>.` 将批准的姿势转换为最终宠物文件，检查接触表、预览和验证结果，修复任何损坏的部分，将 `pet.json` 和 `spritesheet.webp` 保存到宠物文件夹中，然后告诉用户宠物和问答文件保存的位置。

仅在真实文件、图像或决策存在时才标记步骤完成。如果这只是修复运行，则从第一个相关步骤开始，而不是重新启动整个清单。

## 默认工作流程

1. 准备宠物运行文件夹和 imagegen 任务清单：

```bash
SKILL_DIR="${CODEX_HOME:-$HOME/.codex}/skills/hatch-pet"
python "$SKILL_DIR/scripts/prepare_pet_run.py" \
  --pet-name "<Name>" \
  --description "<one sentence>" \
  --reference /absolute/path/to/reference.png \
  --output-dir /absolute/path/to/run \
  --pet-notes "<stable pet description>" \
  --style-notes "<style notes>" \
  --force
```

上述所有参数除了一些必要的标志来表示用户约束外都是可选的。对于纯文本请求，通过 `--pet-notes` 传递概念，省略 `--reference`；`prepare_pet_run.py` 将根据需要推断名称、描述、色度键和输出目录。

2. 检查下一个准备好的 `$imagegen` 任务：

```bash
python "$SKILL_DIR/scripts/pet_job_status.py" --run-dir /absolute/path/to/run
```

3. 对于每个准备好的任务，使用以下方式调用 `$imagegen`：

- 列表在 `imagegen-jobs.json` 中的提示文件
- 每个任务列出的输入图像及其角色标签
- 除非 `$imagegen` 自己路由否则使用默认内置 `image_gen` 路径

基础任务必须首先完成。如果用户参考存在，基础任务将使用它们。如果没有参考，基础任务可能是提示仅任务。记录基础后，`record_imagegen_result.py` 会写入 `decoded/base.png` 和 `references/canonical-base.png`；所有行任务使用原始参考（如果存在）加上那些规范基础图像。

`prepare_pet_run.py` 还在 `references/layout-guides/` 下创建 9 个行特定布局指南图像，每个动画状态一个。行任务将匹配的指南作为仅布局输入附加，以便模型可以遵循正确的帧数、间距、居中和安全填充。将这些指南视为不可见的施工参考：生成的行条不得包含可见的框、边框、中心标记、标签、指南颜色或指南背景。

在生成行条时，保持行提示中的身份锁定为权威：不要重新设计宠物，并保留相同头部形状、脸部、标记、调色板、道具设计、道具侧、轮廓、身体比例和轮廓。看起来像相关但不同的宠物的行即使确定性几何 QA 通过也会失败。

在决定如何完成 `running-left` 之前，生成并记录 `running-right`。检查 `running-right` 与基础和参考。如果宠物在视觉上足够对称，以至于水平镜像可以保留身份、道具位置、左右手、标记、光照、无文本细节和方向语义，则使用以下方式从 `running-right` 派生 `running-left`：

```bash
python "$SKILL_DIR/scripts/derive_running_left_from_running_right.py" \
  --run-dir /absolute/path/to/run \
  --confirm-appropriate-mirror \
  --decision-note "<why mirroring preserves this pet's identity>"
```

如果有任何不对称的侧特定标记、可读文本、非镜像标志、左右手道具、单边配饰、光照提示或方向特定姿势在翻转时会出错，则不要镜像。使用 `$imagegen` 和其行提示以及所有列出的接地图像生成 `running-left`，包括 `decoded/running-right.png` 作为步态参考。

对于内置路径，记录从 `$CODEX_HOME/generated_images/.../ig_*.png` 选择的源图像。不要记录来自运行目录、`tmp/`、手工固定装置、确定性行文件夹或后处理的副本作为视觉任务来源。

4. 选择一个生成的输出后，导入它：

```bash
python "$SKILL_DIR/scripts/record_imagegen_result.py" \
  --run-dir /absolute/path/to/run \
  --job-id <job-id> \
  --source /absolute/path/to/generated-output.png
```

这将图像复制到确定性管道期望的确切解码路径，并在 `imagegen-jobs.json` 中记录源元数据。

5. 当所有任务完成时，最终化：

```bash
python "$SKILL_DIR/scripts/finalize_pet_run.py" \
  --run-dir /absolute/path/to/run
```

预期输出：

```text
run/
  pet_request.json
  imagegen-jobs.json
  prompts/
  decoded/
  frames/frames-manifest.json
  final/spritesheet.png
  final/spritesheet.webp
  final/validation.json
  qa/contact-sheet.png
  qa/review.json
  qa/run-summary.json
  qa/videos/*.mp4
```

包输出默认情况下写在运行目录外。如果设置了 `CODEX_HOME`，则使用它；否则使用 `$HOME/.codex`。

```text
${CODEX_HOME:-$HOME/.codex}/pets/<pet-name>/
  pet.json
  spritesheet.webp
```

在接受宠物之前，检查 `qa/contact-sheet.png`、`qa/review.json`、`final/validation.json` 和 `qa/videos/`。

确定性验证是必要的，但不是充分的。在调用宠物完成之前，视觉检查接触表以检查身份一致性。如果任何行更改物种/身体类型、脸部、标记、调色板、道具设计、道具侧意外地、或整体轮廓，则阻止接受。

## 子代理行生成

在基础任务记录后且 `references/canonical-base.png` 存在时，除非用户明确表示此会话不使用子代理，否则行条视觉生成必须使用子代理。在行生成之前，声明正在使用子代理以及哪些行任务被委托。如果由于当前环境或工具策略阻止而无法生成子代理，则在行条生成之前停止，解释阻塞原因，并在继续顺序之前询问明确的用户指示。

父代理必须拥有清单和包写入权。

默认流程：

1. 父代理运行 `prepare_pet_run.py`。
2. 父代理生成并记录 `base`。
3. 父代理运行 `pet_job_status.py`。
4. 父代理首先为 `idle` 和 `running-right` 生成子代理，作为身份和步态检查。
5. 父代理记录子代理返回的选定的 `idle` 和 `running-right` 结果。
6. 父代理决定 `running-left` 是否安全通过镜像派生；如果不是，父代理将其视为一个正常的接地行任务，委托给子代理。
7. 父代理为每个剩余的非派生行图像生成任务生成子代理。
8. 每个子代理接收行提示和每个列出的输入图像路径，调用 `$imagegen`，并仅返回选定的 `$CODEX_HOME/generated_images/.../ig_*.png` 源路径。
9. 父代理单独运行 `record_imagegen_result.py`、`derive_running_left_from_running_right.py`、修复队列、最终化、问答和打包。

子代理写入边界：不要让子代理编辑 `imagegen-jobs.json`，将文件复制到 `decoded/` 中，运行 `record_imagegen_result.py`，运行 `derive_running_left_from_running_right.py`，运行 `finalize_pet_run.py`，或打包宠物。这可以避免清单竞争并保持溯源检查集中化。

子代理交接合同：

- 除非有意将相邻的简单行批量处理，否则给每个子代理恰好一行工作。
- 包括行 ID、绝对提示文件路径、完整提示文本或读取该确切提示文件的指令，以及来自 `imagegen-jobs.json` 的每个输入图像路径及其角色标签。
- 明确提醒子代理提示的透明度和效果规则是强制性的：没有分离的效果，没有用于 `waving` 的波浪标记，没有用于跑步行的速度线或灰尘，并且仅在状态提示允许时才使用附加的完全不透明精灵状泪痕/烟雾/星星。
- 告知子代理在返回之前检查生成的候选帧数、身份一致性、干净的平坦色度键背景、安全间距和禁止的分离效果。
- 告知子代理仅返回选定的原始 `$CODEX_HOME/generated_images/.../ig_*.png` 源路径加上一句 QA 备注。父代决定是否记录或修复它。

为每个子代理使用此模板：

```text
为这个孵化宠物运行生成 `<row-id>` 行。

运行目录： <绝对运行目录>
提示文件： <绝对提示文件>
输入图像：
- <绝对路径> — <角色>
- <绝对路径> — <角色>

精确读取并遵循行提示，包括透明度和效果规则。仅使用 `$imagegen`；不要使用本地脚本绘制、平铺、编辑或合成精灵。

返回之前，进行视觉检查：
- 精确请求的帧数
- 与规范基础相同的宠物身份
- 干净的平坦色度键背景
- 完整、分离、未裁剪的姿态
- 没有禁止的分离效果或槽交叉伪影

不要编辑清单，复制到 decoded，记录结果，镜像行，最终确定，修复或打包。仅返回：
selected_source=/绝对路径/to/$CODEX_HOME/generated_images/.../ig_*.png
qa_note=<一句话>
```

无声顺序降级：如果子代理不能用于行带视觉生成，则在继续使用它们之前停止并请求明确的用户指令。只有明确的用户指令，如“不要使用子代理”或“按此顺序运行”，才授权正常顺序行生成路径。最终答案必须报告哪些行工作被委托给子代理，以及哪些，如果有，被父代镜像或修复。

## 修复工作流程

如果最终确定因行 QA 失败而停止，请排队有针对性的修复工作：

```bash
python "$SKILL_DIR/scripts/queue_pet_repairs.py" \
  --run-dir /绝对路径/to/run
```

然后对每个重新打开的行工作重复 `$imagegen` 生成和 `record_imagegen_result.py` 摄入循环。重新生成最小的失败范围：失败的行，而不是整个表格。

对于身份修复，使用规范基础图像、原始参考、接触表和确切的行失败备注作为基础上下文。仅修复失败的行，同时保留规范宠物身份。

## 次要图像生成降级

`scripts/generate_pet_images.py` 是此技能的次要降级。

仅在安装的 `$imagegen` 系统技能不可用或无法在当前环境中调用的情祝下使用它。正常的宠物创建应将视觉生成委托给 `$imagegen`，因为 `$imagegen` 拥有内置第一图像生成策略及其自己的 CLI 降级行为。

仅在解释为什么不能使用 `$imagegen` 之后才运行次要降级：

```bash
python "$SKILL_DIR/scripts/generate_pet_images.py" \
  --run-dir /绝对路径/to/run \
  --model gpt-image-2 \
  --states all
```

次要降级需要 `OPENAI_API_KEY`。

## 规则

- 保持 `$imagegen` 作为主要生成层。
- 在选择的路径支持参考时，始终将参考图像附加/可见给 `$imagegen`。
- 将行的 `references/layout-guides/<state>.png` 图像作为仅布局指南附加到每个行带工作，并且不接受复制指南像素的输出。
- 在父代记录基础图像后，使用子代理进行行带视觉生成。父代可以生成基础，但行带工作属于子代理，除非用户明确表示在此会话中不要使用子代理。
- 使用 `$imagegen` 生成每个正常视觉工作：基础加上所有未明确批准为 `running-left` 镜像衍生的行带。
- 仅将基础工作视为仅提示生成合格的；每个行工作必须附加其列出的基础图像。
- 首先委托 `running-right`，然后仅在视觉检查确认镜像保留身份和语义时才镜像 `running-left`；否则将 `running-left` 作为正常的基础 `$imagegen` 行委托。
- 永远不要用本地绘制、平铺、转换或代码生成的行带代替缺失的 `$imagegen` 输出。
- 永远不要手动修改 `imagegen-jobs.json` 来声称一个视觉工作已完成。
- 不要依赖生成的图像来获取精确的图集几何形状；使用此技能的确定性脚本。
- 使用存储在 `pet_request.json` 中的色度键；不要强制固定绿幕。
- 在所有行中保持宠物的轮廓、面部、材质、调色板和道具一致。
- 在每个基础、行和修复提示中执行上述透明度和效果规则。
- 即使 `qa/review.json` 和 `final/validation.json` 没有错误，也要将视觉身份漂移视为阻止因素。
- 将显示裁剪参考、重复平铺、白色单元格背景或非精灵碎片接触表视为失败。
- 将禁止的分离效果、色度键相邻伪影、阴影、辉光、涂抹、灰尘、着陆标记、波浪标记、速度线或运动轨迹视为失败行。
- 将 `qa/review.json` 错误视为阻止因素。警告需要视觉审查。

## 接受标准

- 最终图集是 PNG 或 WebP，`1536x1872`，支持透明度，并基于 `192x208` 单元格。
- 已使用的单元格非空，未使用的单元格完全透明。
- 图集遵循 `references/animation-rows.md` 中的行/帧计数。
- 除非明确跳过，否则已生成接触表和预览视频。
- `qa/review.json` 没有错误。
- 逐行审查确认动画循环对 Codex 应用程序足够完整。
- `${CODEX_HOME:-$HOME/.codex}/pets/<pet-name>/pet.json` 和 `${CODEX_HOME:-$HOME/.codex}/pets/<pet-name>/spritesheet.webp` 对于自定义宠物一起准备。
