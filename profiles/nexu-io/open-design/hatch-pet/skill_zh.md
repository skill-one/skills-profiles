# Hatch Pet

> **OpenDesign 集成。** 这是未经修改的 Codex `hatch-pet` 技能，
> 在 `skills/hatch-pet/` 下进行封装，以便任何 OpenDesign 代理都可以运行它。技能完成打包后，
> 生成的 `spritesheet.webp`（位于 `${CODEX_HOME:-$HOME/.codex}/pets/<pet-name>/` 下）
> 可以通过 **设置 → 常规 → 宠物 → 导入 Codex 矢贴** 导入到浮动宠物伙伴中。导入流程自动检测 8×9 / `192×208` 图集，
> 并允许用户选择要播放的动画行（待机、向右跑、挥手、…）。


## 概述

从概念、一个或多个参考图像或两者创建一个与 Codex 兼容的动画宠物。此技能拥有宠物特定的提示规划、动画行、帧提取、图集几何、问答、预览和打包。它将视觉生成委托给 `$imagegen`。

面向用户的输入是可选的。如果用户省略宠物名称，则从概念或参考文件名中推断一个；如果无法做到这一点，则选择一个简短合适的名称。如果用户省略描述，则从概念或参考中推断一个。如果用户省略参考图像，则首先从文本生成基础宠物，然后使用该基础作为每个动画行的规范参考。

## 生成委托

对所有正常视觉生成使用 `$imagegen`。

在生成基础艺术、行条或修复行之前，加载并遵循已安装的图像生成技能：

```text
${CODEX_HOME:-$HOME/.codex}/skills/.system/imagegen/SKILL.md
```

不要直接调用图像 API 进行正常路径。让 `$imagegen` 选择它自己的内置优先路径和它自己的 CLI 回退规则。如果 `$imagegen` 说回退需要确认，则在继续之前询问用户。

从此技能中调用 `$imagegen` 时，将生成的宠物提示作为权威的视觉规范。不要将其包装在通用的 `$imagegen` 共享提示模式中，也不要添加额外的抛光、英雄艺术、照片、产品或插图风格增强。宠物提示应保持简洁、针对矢量图和数字宠物导向；仅添加输入图像的角色标签和任何必要的用户约束。

仅使用此技能的脚本进行确定性工作：准备提示和清单、导入选定的 `$imagegen` 输出、提取帧、验证行、组合最终图集、创建问答媒体和打包。

硬边界：不要使用本地 Python/Pillow 脚本、SVG、画布、HTML/CSS 或其他代码原生艺术来代替 `$imagegen` 创建、绘制、平铺、扭曲、镜像或合成宠物视觉。对于正常宠物运行，预期最多 10 个视觉生成任务：1 个基础宠物加上 9 个行条任务。唯一的例外是 `running-left`，它只能在 `running-right` 已生成、视觉检查并明确批准为可以镜像后，通过镜像 `running-right` 得到。如果镜像不合适，则作为正常的 `$imagegen` 行生成 `running-left`。如果这些调用太昂贵、被阻塞或不可用，则停止并解释阻塞原因，而不是在本地伪造行条。

不要通过编辑 `imagegen-jobs.json`、将文件复制到 `decoded/` 或编写填充行输出的辅助脚本来标记视觉任务完成。使用 `record_imagegen_result.py` 记录选定的内置 `$imagegen` 输出，或仅使用 `generate_pet_images.py` 记录文档中说明的次要回退。确定性脚本只能处理已生成的视觉输出。

只有基础任务可以是提示仅。通过 `$imagegen` 生成的每个行条任务都必须使用 `imagegen-jobs.json` 中列出的输入图像，包括在记录基础任务后创建的规范基础参考。将任何没有附加接地图像的行生成视为无效。

## Codex 数字宠物风格

默认宠物艺术应与 Codex 应用的内置数字宠物匹配：小型类似像素艺术的吉祥物，具有紧凑的 chibi 比例，块状易读的轮廓，粗暗的 1-2 px 轮廓，可见的阶梯/像素边缘，有限的调色板，平面赛璐璐着色，简单的表情丰富的脸，以及微小的四肢。即使参考艺术更详细、更复杂或更逼真，生成的宠物也应简化为此风格。

不要生成抛光的插图、绘画渲染、动画关键艺术、3D 渲染、光泽应用图标处理、逼真的毛发或材质纹理、柔和渐变、高细节抗锯齿和复杂的微小配饰。比此更详细的参考应在行生成之前简化为房屋风格。

## 透明度和效果

宠物行被处理为透明的 192x208 单元，因此每个生成的像素必须要么属于宠物矢量图，要么是干净可去除的色度键背景。优先考虑姿势、表情和轮廓变化而不是装饰效果。

允许的效果必须满足所有这些条件：

- 效果与状态相关，并有助于解释动画。
- 效果物理上附着在、接触或重叠宠物轮廓上，而不是悬浮在附近。
- 效果位于与宠物相同的帧槽内，并且不会创建单独的矢量图组件。
- 效果是完全不透明的、硬边界的、像素风格的，并使用非色度键颜色。
- 效果足够小，以便在 192x208 时保持可读性，不会杂乱。

允许的效果示例：一滴眼泪接触脸部，一个小的烟雾团接触盒子或头部，或在小失败/头晕反应期间宠物上重叠的微小星星。

默认情况下避免这些，因为它们通常会破坏透明背景清理或组件提取：

- 波浪标记、运动弧线、速度线、动作条纹、残留影像、模糊或涂抹
- 分离的星星、松散的闪光、悬浮的标点符号、悬浮的图标、落下的泪滴、分离的烟雾云或松散的灰尘
- 投影阴影、接触阴影、阴影、椭圆地板阴影、地板补丁、着陆标记、冲击爆发、发光、光晕、光环或柔和的透明效果
- 文本、标签、帧编号、可见网格、引导标记、对话气泡、思想气泡、UI 面板、代码片段、棋盘透明度、白色背景、黑色背景或场景
- 宠物、道具、效果、高光或阴影中与色度键相邻的颜色
- 逸散的像素、断开的轮廓碎片、斑点/噪声、裁剪的身体部分、重叠的姿势或任何跨越到相邻帧槽的姿势

状态特定指导：

- `waving`：仅通过爪子姿势显示波浪。不要绘制波浪标记、运动弧线、线条、闪光或符号围绕爪子。
- `jumping`：仅通过身体位置显示垂直运动。不要绘制阴影、灰尘、着陆标记、冲击爆发、弹跳垫或地板提示。
- `failed`：如果它们遵守允许效果规则，则允许眼泪、附加的烟雾团或附加的星星；不要使用红色 X 标记、悬浮符号、分离的烟雾、分离的星星或分离的泪滴。
- `review`：通过倾斜、眨眼、眼睛、头部倾斜或爪子位置显示焦点。除非基础宠物身份中已存在该道具，否则不要添加放大镜、纸张、代码、UI、标点符号或符号。
- `running-right`、`running-left` 和 `running`：仅通过身体、四肢和道具运动显示运动。不要绘制速度线、灰尘云、地板阴影或运动轨迹。

## 宠物命名

当用户没有提供名称且对话自然允许时，询问用户宠物名称。如果询问会减慢直接执行请求的速度，则从宠物概念、参考图像或个性中选择一个简短合适的名称，然后始终使用该名称作为显示名称和作为包文件夹缩写的来源。

良好的内置风格示例：

- Codex - The original Codex companion.
- Dewey - A tidy duck for calm workspace days.
- Fireball - Hot path energy for fast iteration.
- Rocky - A steady rock when the diff gets large.
- Seedy - Small green shoots for new ideas.
- Stacky - A balanced stack for deep work.
- BSOD - A tiny blue-screen gremlin.
- Null Signal - Quiet signal from the void.

## 可见进度计划

对于每个宠物运行，保持一个可见清单，以便用户可以看到工作进度。在开始之前创建清单，一次保持一个步骤激活，并在每个步骤完成后更新它。

在创建清单之前，尽可能建立宠物名称。使用用户提供的名称；否则从概念或参考中推断一个简短合适的名称。如果名称太长、未确定或不适合友好的清单，则使用 `your pet` 代替。

使用此清单进行正常宠物运行，将 `<Pet>` 替换为宠物的名称或 `your pet`：

1. 准备 `<Pet>`。
2. 想象 `<Pet>` 的主要外观。
3. 想象 `<Pet>` 的姿势。
4. 生成 `<Pet>`。

每个步骤的含义：

- `Preparing <Pet>.` 选择或确认宠物名称、描述、源图像和工作文件夹。
- `Imagining <Pet>'s main look.` 生成宠物的主要参考图像。这是新宠物所需的，即使用户没有提供图像，因为它成为视觉真实来源。
- `Picturing <Pet>'s poses.` 创建姿势行，从 `idle` 和 `running-right` 开始以确认宠物仍然看起来一致。只有在 `running-right` 翻转时明显有效时，才镜像 `running-left`。
- `Hatching <Pet>.` 将批准的姿势转换为最终宠物文件，检查接触表、预览和验证结果，修复任何损坏的部分，将 `pet.json` 和 `spritesheet.webp` 保存到宠物文件夹中，然后告诉用户宠物和 QA 文件保存的位置。

只有在实际文件、图像或决策存在时才标记步骤完成。如果这只是修复运行，则从第一个相关步骤开始，而不是重新启动整个清单。

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

所有参数中，除了表达用户约束所需的任何标志外，都是可选的。对于纯文本请求，通过 `--pet-notes` 传递概念，省略 `--reference`；`prepare_pet_run.py` 将推断名称、描述、色度键和输出目录。

2. 检查下一个准备好的 `$imagegen` 任务：

```bash
python "$SKILL_DIR/scripts/pet_job_status.py" --run-dir /absolute/path/to/run
```

3. 对于每个准备好的任务，使用以下方式调用 `$imagegen`：

- 列在 `imagegen-jobs.json` 中的提示文件
- 任务为每个输入图像，附带其角色标签
- 除非 `$imagegen` 自己路由否则使用默认内置 `image_gen` 路径

基础任务必须首先完成。如果用户参考存在，则基础任务使用它们。如果没有参考，则基础任务可能是提示仅。记录基础后，`record_imagegen_result.py` 写入 `decoded/base.png` 和 `references/canonical-base.png`；所有行任务使用原始参考（如果存在）加上那些规范基础图像。

`prepare_pet_run.py` 还在 `references/layout-guides/` 下为每个动画状态创建 9 个行特定布局指南图像，每个动画状态一个。行任务将匹配的指南作为仅布局输入附加，以便模型可以遵循正确的帧数、间距、居中和安全填充。将这些指南视为不可见的施工参考：生成的行条不得包含可见的框、边框、中心标记、标签、指南颜色或指南背景。

在生成行条时，保持行提示中的身份锁定权威：不要重新设计宠物，并保留相同的头部形状、脸部、标记、调色板、道具设计、道具侧、轮廓重量、身体比例和轮廓。看起来像相关但不同的宠物的行即使确定性几何 QA 通过也会失败。

在决定如何完成 `running-left` 之前，生成和记录 `running-right`。检查 `running-right` 对基础和参考。如果宠物在视觉上足够对称，以至于水平镜像可以保留身份、道具位置、左右、标记、照明、无文本细节和方向语义，则使用以下方式从 `running-right` 推导 `running-left`：

```bash
python "$SKILL_DIR/scripts/derive_running_left_from_running_right.py" \
  --run-dir /absolute/path/to/run \
  --confirm-appropriate-mirror \
  --decision-note "<why mirroring preserves this pet's identity>"
```

如果有任何不对称的侧特定标记、可读文本、非镜像标志、左右道具、单边配饰、照明提示或方向特定姿势在翻转时会变得错误，则不要镜像。使用 `$imagegen` 生成 `running-left`，使用其行提示和所有列出的接地图像，包括 `decoded/running-right.png` 作为步态参考。

对于内置路径，记录从 `$CODEX_HOME/generated_images/.../ig_*.png` 选择的源图像。不要记录来自运行目录、`tmp/`、手工固定件、确定性行文件夹或后处理的副本作为视觉任务源。

4. 选择生成任务的输出后，导入它：

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

在接受宠物之前，查看 `qa/contact-sheet.png`、`qa/review.json`、`final/validation.json` 和 `qa/videos/`。

确定性验证是必要的，但不是充分的。在调用宠物完成之前，视觉检查接触表以检查身份一致性。如果任何行更改物种/身体类型、脸部、标记、调色板、道具设计、道具侧意外地、或整体轮廓，则阻止接受。

## 子代理行生成

在记录基础图像后，行条视觉生成必须使用子代理，除非用户明确表示此会话不使用子代理。在行生成之前，声明正在使用子代理以及哪些行任务被委托。如果由于当前环境或工具策略阻止而无法生成子代理，则在行条生成之前停止，解释阻塞原因，并在继续之前询问明确的用户指令。

父代理必须拥有清单和包写入权。

默认流程：

1. 父运行 `prepare_pet_run.py`。
2. 父生成并记录 `base`。
3. 父运行 `pet_job_status.py`。
4. 父首先生成子代理用于 `idle` 和 `running-right`，作为身份和步态检查。
5. 父记录子代理返回的选定的 `idle` 和 `running-right` 结果。
6. 父决定 `running-left` 是否安全通过镜像推导；如果不是，父将其视为一个正常的接地 `$imagegen` 行任务委托给子代理。
7. 父生成子代理用于每个剩余的非推导行图像生成任务。
8. 每个子代理接收行提示和每个列出的输入图像路径，调用 `$imagegen`，并仅返回选定的 `$CODEX_HOME/generated_images/.../ig_*.png` 源路径。
9. 父单独运行 `record_imagegen_result.py`、`derive_running_left_from_running_right.py`、修复队列、最终化、QA 和打包。

子代理写入边界：不要让子代理编辑 `imagegen-jobs.json`、将文件复制到 `decoded/`、运行 `record_imagegen_result.py`、运行 `derive_running_left_from_running_right.py`、运行 `finalize_pet_run.py` 或打包宠物。这避免了清单竞争并使来源检查集中化。

子代理交接合同：

- 除非有意批量相邻简单行，否则给每个子代理恰好一个行任务。
- 包括行 ID、绝对提示文件路径、完整提示文本或读取该确切提示文件的指令，以及来自 `imagegen-jobs.json` 的每个输入图像路径及其角色标签。
- 明确提醒子代理提示的透明度和效果规则是强制性的：没有分离的效果，`waving` 没有波浪标记，运行行没有速度线或灰尘，并且仅当状态提示允许时才添加附加的、不透明的矢量图样式眼泪/烟雾/星星。
- 告诉子代理在返回之前检查生成的候选帧数、身份一致性、干净的平面色度键背景、安全间距和禁止的分离效果。
- 告诉子代理仅返回选定的原始 `$CODEX_HOME/generated_images/.../ig_*.png` 源路径加上一句 QA 注释。父决定是否记录或修复它。

使用此模板为每个子代理：

```text
Generate the `<row-id>` row for this hatch-pet run.

Run dir: <absolute run dir>
Prompt file: <absolute prompt file>
Input images:
- <absolute path> — <role>
- <absolute path> — <role>

准确读取并遵循行提示，包括透明度和伪影规则。仅使用 `$imagegen`；不要使用本地脚本绘制、平铺、编辑或合成矢量图。

返回之前，视觉检查：
- 精确请求的帧数
- 与规范基础相同的宠物身份
- 干净的平面色度键背景
- 完整、分离、未裁剪的姿势
- 没有禁止的分离效果或槽交叉伪影

不要编辑清单、复制到 decoded、记录结果、镜像行、最终化、修复或打包。仅返回：
selected_source=/absolute/path/to/$CODEX_HOME/generated_images/.../ig_*.png
qa_note=<one sentence>
```

没有静默顺序回退：如果子代理不能用于行条视觉生成，则在继续之前停止并询问明确的用户指令。只有明确的用户指令，如“不要使用子代理”或“按顺序运行此操作”，才授权正常顺序行生成路径。最终答案必须报告哪些行任务被委托给子代理，以及是否任何行被父代理镜像或修复。

## 修复工作流程

如果最终化因行 QA 失败而停止，则排队有针对性的修复任务：

```bash
python "$SKILL_DIR/scripts/queue_pet_repairs.py" \
  --run-dir /absolute/path/to/run
```

然后对重新打开的每个行任务重复 `$imagegen` 生成和 `record_imagegen_result.py` 导入循环。重新生成最小的失败范围：失败的行，而不是整个图集。

对于身份修复，使用规范基础图像、原始参考、接触表和确切的行失败笔记作为接地上下文。仅修复失败的行，同时保留规范宠物身份。

## 次要图像生成回退

`scripts/generate_pet_images.py` 是此技能的次要回退。

仅在已安装的 `$imagegen` 系统技能不可用或无法在当前环境中调用的环境中使用它。正常宠物创建应将视觉生成委托给 `$imagegen`，因为 `$imagegen` 拥有内置优先图像生成策略及其自己的 CLI 回退行为。

仅在解释为什么不能使用 `$imagegen` 后运行次要回退：

```bash
python "$SKILL_DIR/scripts/generate_pet_images.py" \
  --run-dir /absolute/path/to/run \
  --model gpt-image-2 \
  --states all
```

次要回退需要 `OPENAI_API_KEY`。

## 规则

- 保持 `$imagegen` 作为主要生成层。
- 在选择的路径支持参考时，始终将参考图像附加/可见于 `$imagegen`。
- 将行的 `references/layout-guides/<state>.png` 图像作为仅布局指南附加到每个行条任务，并且不要接受复制指南像素的输出。
- 在父记录基础图像后，使用子代理进行行条视觉生成。父可以生成基础，但行条任务属于子代理，除非用户明确表示此会话不使用子代理。
- 使用 `$imagegen` 生成每个正常视觉任务：基础加上所有未明确批准 `running-left` 镜像推导的行条。
- 仅将基础任务视为提示仅生成的合格任务；每个行任务都必须附加其列出的接地图像。
- 首先委托 `running-right`，然后在视觉检查确认镜像保留身份和语义时，才镜像 `running-left`；否则将 `running-left` 委托为正常的接地 `$imagegen` 行。
- 不要用本地绘制的、平铺的、转换的或代码生成的行条来代替缺少的 `$imagegen` 输出。
- 不要手动修改 `imagegen-jobs.json` 来声称视觉任务完成。
- 不要依赖生成图像进行精确图集几何；使用此技能的确定性脚本。
- 使用存储在 `pet_request.json` 中的色度键；不要强制固定绿色屏幕。
- 在所有行中保持宠物的轮廓、脸部、材质、调色板和道具一致。
- 在每个基础、行和修复提示中执行上述透明度和效果规则。
- 即使 `qa/review.json` 和 `final/validation.json` 没有错误，也要将视觉身份漂移视为阻塞。
- 将显示裁剪参考、重复平铺、白色单元格背景或非矢量图碎片的生产接触表视为失败。
- 将禁止的分离效果、色度键相邻的伪影、阴影、发光、涂抹、灰尘、着陆标记、波浪标记、速度线或运动轨迹视为失败行。
- 将 `qa/review.json` 错误视为阻塞。警告需要视觉审查。

## 接受标准

- 最终图集是 PNG 或 WebP、`1536x1872`、支持透明的，基于 `192x208` 单元。
- 使用单元格是非空的，未使用的单元格是完全透明的。
- 图集遵循 `references/animation-rows.md` 中的行/帧计数。
- 已生成接触表和预览视频，除非明确跳过。
- `qa/review.json` 没有错误。
- 逐行审查确认动画循环足够完整，可用于 Codex 应用。
- `${CODEX_HOME:-$HOME/.codex}/pets/<pet-name>/pet.json` 和 `${CODEX_HOME:-$HOME/.codex}/pets/<pet-name>/spritesheet.webp` 对于自定义宠物一起准备。
