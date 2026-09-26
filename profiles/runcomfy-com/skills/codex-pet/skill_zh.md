# Codex Pet — Pro Pack on RunComfy

[runcomfy.com](https://www.runcomfy.com/?utm_source=skills.sh&utm_medium=skill&utm_campaign=codex-pet) · [GPT Image 2 edit endpoint](https://www.runcomfy.com/models/openai/gpt-image-2/edit?utm_source=skills.sh&utm_medium=skill&utm_campaign=codex-pet) · [docs](https://docs.runcomfy.com/cli/introduction?utm_source=skills.sh&utm_medium=skill&utm_campaign=codex-pet)

**RunComfy上的Codex Pet生成器。** 将一张源图像转换为Codex兼容的自定义Codex Pet — `pet.json` + `spritesheet.webp` — 放入 `${CODEX_HOME:-$HOME/.codex}/pets/<name>/`，Codex将在8个内置Codex Pet旁边自动识别它。

```bash
npx skills add agentspace-so/runcomfy-agent-skills --skill codex-pet -g
```

## Codex Pet是什么

OpenAI Codex Pets（2026年5月发布）是像素风格的动画伙伴，它们在Codex编码时漂浮在你的桌面上——它们会对鼠标交互和Codex状态做出反应（思考时挠头，任务完成时冒出对话框）。Codex自带8个内置Codex Pet，并支持本地安装的自定义Codex Pet，作为 `${CODEX_HOME:-$HOME/.codex}/pets/` 下的文件夹。

每个自定义Codex Pet文件夹包含恰好两个文件：

- `pet.json` — 包含 `id`、`displayName`、`description`、`spritesheetPath` 的清单。
- `spritesheet.webp` — Codex Pet精灵图集，**1536x1872** PNG或WebP，8列x9行，192x208单元格，透明背景。

9行对应Codex播放的9个动画状态。每行使用固定数量的引导帧；尾随单元格保持完全透明。

## 为什么使用这个Codex Pet技能（与OpenAI的官方 `hatch-pet` 相比）

OpenAI提供了一个官方的 [`hatch-pet`](https://github.com/openai/skills/blob/main/skills/.curated/hatch-pet/SKILL.md) 技能，通过Codex内部的 `$imagegen` 系统技能（需要Codex Pro + `$imagegen` 配置）生成相同的Codex Pet工件。

**这个Codex Pet技能是一个即插即用的替代方案，通过RunComfy CLI运行**：一个 `RUNCOMFY_TOKEN` 加上 `runcomfy` 和 `magick` 二进制文件——不需要Codex Pro，不需要 `$imagegen`，不需要 OPENAI_API_KEY。输出的Codex Pet工件是相同的——相同的 `pet.json` 结构，相同的 `spritesheet.webp` 1536x1872图集，相同的9个动画行——因此Codex将这个Codex Pet与 `hatch-pet` 制造的Codex Pet完全一样对待。

这个技能遵循Codex内置Codex Pet使用的相同模式：**一个标准的姿势，通过ImageMagick微变换在整个单元格中复制**，以实现微妙的动画（1-2 px位移，眨眼帧，倾斜帧）。这与官方 `hatch-pet` 输出的实际单元格外观相匹配——Codex桌面应用中可见的Codex Pet动画是故意设计得微妙的。

选择这个技能的情况：

- 你想要一个自定义的Codex Pet，但没有Codex Pro / `$imagegen`。
- 你想要通过RunComfy模型API构建自定义Codex Pet。
- 你想要**批量Codex Pet生成**，从源图像文件夹中（每个宠物一个标准的调用）。
- 你正在使用不同的模型在OpenAI Codex Pet比赛中展示视觉效果。
- 你明确说了“codex pet”，"/hatch"，"make me a codex pet"，"spritesheet.webp"，"desktop pet for codex"。

## Codex Pet动画行

Codex读取一个固定的图集：8列，9行，192x208单元格。每个Codex Pet行对应一个特定的动画状态，并具有特定数量的引导帧。

| 行 | 状态 | 使用列 | 帧 | Codex Pet行为 |
|---|---|---|---|---|
| 0 | 空闲 | 0-5 | 6 | 平静的呼吸/眨眼；Codex Pet的减少运动第一帧 |
| 1 | 向右跑 | 0-7 | 8 | Codex Pet向右移动 |
| 2 | 向左跑 | 0-7 | 8 | 镜像的向左移动 |
| 3 | 挥手 | 0-3 | 4 | 礼貌/注意力手势 |
| 4 | 跳跃 | 0-4 | 5 | 期待，上升，顶峰，下降，稳定 |
| 5 | 失败 | 0-7 | 8 | 错误/悲伤/沮丧的反应 |
| 6 | 等待 | 0-5 | 6 | 耐心的空闲变体 |
| 7 | 跑步 | 0-5 | 6 | 积极工作/进行中循环（不是脚跑） |
| 8 | 审查 | 0-5 | 6 | 专注/检查/思考 |

每行的尾随单元格必须在最后使用的列之后保持完全透明。

## Codex Pet风格

Codex Pet的视觉风格：

- **夸张的chibi比例**：头部占据总高度约60%；身体和腿都很小很短。整个角色应该适合一个接近正方形的边界框。
- 像素艺术相邻的低分辨率吉祥物，粗大的轮廓
- 粗暗的1-2 px轮廓线，可见的阶梯状像素边缘
- 有限的调色板，平面赛璐璐着色，简单的表情，微小的肢体
- 透明背景

避免：运动线，阴影，发光，闪光，漂浮效果，文本标签，场景，白/黑背景。

## 前置条件

1. **RunComfy CLI** — `npm i -g @runcomfy/cli`
2. **RunComfy账户** — `runcomfy login`。CI替代方案：`RUNCOMFY_TOKEN=<token>`。
3. **ImageMagick** — `brew install imagemagick`（macOS）或 `apt-get install imagemagick`（Linux）。提供 `magick` 命令以进行确定性图集组装。
4. **一个源图像URL** — 公开可获取的HTTPS，JPEG/PNG/WebP，Codex Pet将基于此建模的主题。

## Codex Pet流程（1个GPT Image 2调用，约2分钟）

1. **标准的Codex Pet** — 单个 `runcomfy run openai/gpt-image-2/edit` 调用，生成一个1024x1024的chibi姿势，背景为品红色色度键。
2. **单元格标准化** — 色度键品红色到alpha 0，修剪，按纵横比适应到192x208，带有透明填充。
3. **9行条带，程序化** — 对于9个动画状态中的每一个，通过ImageMagick微变换构建行的8个单元格（平移/遮罩/镜像）。尾随单元格填充透明192x208。
4. **图集** — 将9行条带垂直堆叠到1536x1872的Codex Pet图集中。
5. **WebP** — 将图集PNG转换为WebP。
6. **清单+安装** — 编写 `pet.json`，将两个文件都复制到 `${CODEX_HOME:-$HOME/.codex}/pets/<pet-name>/`。

微变换方法与Codex内置Codex Pet实际执行的操作相匹配——Codex Pet动画是故意设计得微妙的，因此每个单元格的1-2 px位移和眨眼遮罩就足以产生正确的视觉效果，而无需消耗72个GPT Image 2调用。

### 第1步：生成标准的Codex Pet（1个调用）

```bash
PET_NAME="my-pet"
PET_DESC="一个友好的伙伴，适合深夜重构。"
SOURCE_URL="https://.../source.png"
RUN_DIR="./codex-pet-run/${PET_NAME}"
CHROMA="#FF00FF"   # 品红色色度键
mkdir -p "${RUN_DIR}"

runcomfy run openai/gpt-image-2/edit \
  --input "{
    \"prompt\": \"生成一个基于输入图像的标准Codex数字宠物精灵。夸张的chibi比例：头部占据约60%的总高度；身体和腿都很小很短。整个宠物角色必须适合一个接近正方形的边界框（整体纵横比接近1:1）。像素艺术相邻的低分辨率吉祥物，粗大的全身轮廓，粗暗的1-2 px轮廓线，可见的阶梯状像素边缘，有限的调色板，平面赛璐璐着色，简单的表情，微小的肢体。居中显示。没有精致的插图，没有画家风格的渲染，没有动画关键艺术，没有3D渲染，没有光泽的应用图标抛光，没有逼真的细节。背景：品红色 ${CHROMA} 色度键填充，宠物轮廓线外。宠物本身不得使用色度键颜色或任何接近品红色的亮色。没有渐变，没有阴影，没有光晕，没有场景，没有文本。保留从输入图像中提取的身份特征。\",
    \"images\": [\"${SOURCE_URL}\"],
    \"size\": \"1024*1024\"
  }" \
  --output-dir "${RUN_DIR}/decoded/"

BASE=$(ls "${RUN_DIR}/decoded/"*.png | head -1)
echo "标准Codex Pet: ${BASE}"
```

### 第2步：将标准规范化为192x208的Codex Pet单元格

色度键品红色到alpha，修剪到宠物精灵边界框，按纵横比适应到192x208，带有透明填充。

```bash
magick "${BASE}" \
  -fuzz 18% -transparent "${CHROMA}" \
  -alpha set \
  -trim +repage \
  -resize 192x208 \
  -gravity center \
  -background none \
  -extent 192x208 \
  "${RUN_DIR}/cell.png"
```

18%的模糊度是为GPT Image 2的抗锯齿品红色边缘调优的。如果Codex Pet有更宽的品红色光晕，请将其调整为25%；如果宠物有接近品红色的亮色，则将其调整为8-10%，以免被裁剪。

### 第3步：程序化构建9个Codex Pet行条带

对于每一行，通过ImageMagick微变换从标准构建8个单元格，用透明填充未使用的尾随单元格，然后将它们垂直连接成一个1536x208的行条带。

```bash
SRC="${RUN_DIR}/cell.png"
mkdir -p "${RUN_DIR}/cells"

# 辅助函数
shift_cell() { magick "$SRC" -background none -roll "+${1}+${2}" -alpha set "$3"; }
rotate_cell() { magick "$SRC" -background none -distort SRT "$1" -alpha set "$2"; }
make_blink() {
  # 眼睛大致位于208高单元格的y=80-100处。
  # 用肤色在水平带中柔化。
  magick "$SRC" \
    -region 80x6+56+82 -fill "#f4e6d8" -colorize 70% -blur 0x0.5 +region "$1"
}
blank_cell() { magick -size 192x208 xc:none -alpha set "PNG32:$1"; }

build_row() {
  local row=$1; shift
  local i=0
  for spec in "$@"; do
    local out="${RUN_DIR}/cells/row${row}-frame${i}.png"
    case "$spec" in
      base)      cp "$SRC" "$out" ;;
      blink)     make_blink "$out" ;;
      shift:*)   IFS=':' read -r _ x y <<< "$spec"; shift_cell "$x" "$y" "$out" ;;
      rotate:*)  IFS=':' read -r _ ang <<< "$spec"; rotate_cell "$ang" "$out" ;;
    esac
    i=$((i+1))
  done
  while [ "$i" -lt 8 ]; do
    blank_cell "${RUN_DIR}/cells/row${row}-frame${i}.png"
    i=$((i+1))
  done
  magick "${RUN_DIR}/cells/row${row}-frame"*.png +append -alpha set \
    "${RUN_DIR}/cells/row${row}-strip.png"
}

# 9个Codex Pet行，每个行对应一个动画状态及其特定数量的引导帧
build_row 0 base base blink base base blink                                       # 空闲（6）
build_row 1 base shift:1:0 shift:2:-1 shift:1:0 base shift:-1:0 shift:-2:-1 shift:-1:0  # 向右跑（8）
# 行 2 = 向左跑 = 行 1 的水平翻转，下面构建
build_row 3 base shift:0:-1 base shift:0:-1                                       # 挥手（4）
build_row 4 shift:0:2 base shift:0:-8 shift:0:-2 base                              # 跳跃（5）——垂直弧线
build_row 5 base shift:0:1 rotate:1 shift:0:1 shift:0:2 shift:0:1 rotate:-1 base  # 失败（8）
build_row 6 base base shift:0:-1 base base shift:0:1                              # 等待（6）
build_row 7 base shift:0:-1 base shift:0:-1 base shift:0:-1                       # 跑步（6）
build_row 8 base rotate:-2 base rotate:2 base base                                # 审查（6）

# 行 2：向左跑 = 行 1 的镜像
magick "${RUN_DIR}/cells/row1-strip.png" -flop -alpha set "${RUN_DIR}/cells/row2-strip.png"
```

微变换表是Codex Pet在Codex桌面应用中可读但微妙的运动感的来源。根据个人喜好调整每行的数字；这些增量被故意设计得很小（1-2 px），以便Codex Pet感觉生动而不分散注意力。

### 第4步：组成Codex Pet图集

将9行条带垂直堆叠到1536x1872的Codex Pet图集中，然后转换为WebP。

```bash
magick \
  "${RUN_DIR}/cells/row0-strip.png" \
  "${RUN_DIR}/cells/row1-strip.png" \
  "${RUN_DIR}/cells/row2-strip.png" \
  "${RUN_DIR}/cells/row3-strip.png" \
  "${RUN_DIR}/cells/row4-strip.png" \
  "${RUN_DIR}/cells/row5-strip.png" \
  "${RUN_DIR}/cells/row6-strip.png" \
  "${RUN_DIR}/cells/row7-strip.png" \
  "${RUN_DIR}/cells/row8-strip.png" \
  -append -alpha set "${RUN_DIR}/spritesheet.png"

magick "${RUN_DIR}/spritesheet.png" "${RUN_DIR}/spritesheet.webp"
```

### 第5步：编写Codex Pet清单

```bash
cat > "${RUN_DIR}/pet.json" <<EOF
{
  "id": "${PET_NAME}",
  "displayName": "${PET_NAME}",
  "description": "${PET_DESC}",
  "spritesheetPath": "spritesheet.webp"
}
EOF
```

### 第6步：安装Codex Pet

```bash
DEST="${CODEX_HOME:-$HOME/.codex}/pets/${PET_NAME}"
mkdir -p "${DEST}"
cp "${RUN_DIR}/pet.json" "${RUN_DIR}/spritesheet.webp" "${DEST}/"
echo "Codex Pet安装于 ${DEST}"
```

重启Codex（或重新加载宠物列表），自定义Codex Pet将出现在8个内置Codex Pet旁边。

## 引导Codex Pet——什么有效

单个GPT Image 2调用决定了所有内容。如果这个提示正确，其余的就是确定性的。

**首先锁定chibi比例。** "夸张的chibi比例，头部约60%的身高"是区分一个瘦高的角色（不适合192x208单元格，会变形）和一个头部主导的chibi（自然填充单元格）的关键。后者是Codex内置Codex Pet的样子。

**明确要求在Codex Pet基础提示中指定品红色 `#FF00FF` 色度键。** GPT Image 2只输出RGB（没有alpha），因此唯一的方法是在后处理中移除透明Codex Pet的已知背景颜色。

**宠物本身不得使用色度键颜色。** 添加： "宠物本身不得使用色度键颜色或任何接近品红色的亮色。" 否则，色度键步骤会移除恰好是品红色-ish的Codex Pet身体部位。

**锁定风格。** "像素艺术相邻，粗大的轮廓，1-2 px轮廓线，有限的调色板，平面赛璐璐着色"——锁定使Codex Pet符合Codex风格的每个术语。

**禁止错误风格。** "没有精致的插图，没有画家风格的渲染，没有动画关键艺术，没有3D渲染，没有光泽的应用图标抛光，没有逼真的细节。" 没有这个，GPT Image 2会倾向于过度渲染的动漫艺术。

**反模式**：
- 通用"透明背景"——GPT Image 2会以接近白色绘制。使用色度键。
- 允许模型自由发挥比例——它会画一个瘦高的chibi，不适合192x208。
- 在一个提示中混合风格——锁定一个风格锚点并坚持它。

## 调整微动画

步骤3中的默认ImageMagick配方产生的Codex Pet动画与内置Codex Pet相似——微妙的上下浮动，偶尔眨眼，跳跃弧线，头部倾斜。要使动画更或更不明显，调整增量：

- **更大的空闲浮动**：将行0中的 `shift:0:-1` 改为 `shift:0:-2`。
- **更快的跑步周期**：增加行1中的水平位移（例如 `shift:3:0` 而不是 `shift:2:-1`）。
- **更高的跳跃**：将行4的顶峰从 `shift:0:-8` 改为 `shift:0:-12`。
- **审查中更强的头部倾斜**：将 `rotate:-2` / `rotate:2` 改为 `rotate:-4` / `rotate:4`。

保持增量小（≤ 4 px或≤ 4°），这样Codex Pet不会变得分散注意力。

## 常见问题解答——Codex Pet

**Codex Pet是什么？** OpenAI Codex Pets是2026年5月发布的像素风格动画伙伴，它们在Codex编码时漂浮在你的桌面上，并对Codex的编码状态做出反应（思考时挠头，任务完成时冒出对话框）。自定义Codex Pets作为 `pet.json` + `spritesheet.webp` 文件存在于 `${CODEX_HOME:-$HOME/.codex}/pets/<name>/` 下。

**为什么使用这个Codex Pet技能而不是 `hatch-pet`？** 官方的 `hatch-pet` 需要Codex内部的 `$imagegen` 系统技能（需要Codex Pro）。这个技能只需要 `RUNCOMFY_TOKEN` 并通过RunComfy CLI运行相同的动画行规范，总共只调用一次GPT Image 2。

**一个Codex Pet生成需要多长时间？** 约2分钟——1个GPT Image 2编辑调用（约90秒）加上几秒钟的ImageMagick图集组装。

**为什么只调用一次API？** Codex桌面应用中的Codex Pet动画是故意设计得微妙的（你可以通过检查任何内置Codex Pet的图集——72个几乎相同的姿势，每个姿势只有微小的变化））。一个标准姿势加上确定性ImageMagick微变换就能产生相同的动画感觉，而无需消耗72个单独的生成调用。

**Codex Pet技能能否使用非人类主题？** 是的——宠物、吉祥物、物体、食物都适用。基础提示会自动将源简化为Codex Pet风格。

**我如何安装我的Codex Pet？** 将 `pet.json` 和 `spritesheet.webp` 复制到 `${CODEX_HOME:-$HOME/.codex}/pets/<pet-name>/` 并重新加载Codex。

**如果标准Codex Pet偏离了身份怎么办？** 重新运行步骤1，使用更紧密的身份保留提示（例如：命名特定特征：头发颜色、眼镜、配饰）。步骤2-6是确定性的，不需要改变。

**每个Codex Pet帧的大小是多少？** 192x208 px。每行条带是 1536x208（8帧）。最终Codex Pet图集是 1536x1872（9个堆叠的行）。

**我能添加自定义姿势或替换行吗？** 是的——修改步骤3中的 `build_row` 调用。每行的图集槽位数量必须与Codex合同匹配（空闲=6，向右/向左跑=8，挥手=4，跳跃=5，失败=8，等待/跑步/审查=6），以便Codex能够正确播放它们。

## 限制

- **每个Codex Pet只有一个标准姿势**——动画是通过ImageMagick变换实现的，而不是多帧模型生成。这匹配了内置Codex Pets的微妙动画，但不会产生剧烈的运动（例如，不同的帧到帧跑步周期）。
- **GPT Image 2不输出alpha**——品红色色度键+后处理是一个解决方案。如果Codex Pet有接近品红色的颜色（对于chibi调色板来说很少见），请在提示和后处理中将色度键更改为不同的纯色（`#00FFFF` 青色或 `#00FF00` 绿色）。
- **身份漂移**——GPT Image 2可能会将源图像身份简化为Codex Pet风格；特定的小特征（例如耳环、道具颜色）可能会发生变化。
- **Codex Pet没有音频/声音**——Codex Pets是纯视觉的。

## 退出代码

`runcomfy` CLI使用sysexits风格的代码：

| 代码 | 含义 |
|---|---|
| 0  | Codex Pet标准生成成功 |
| 64 | 命令行参数错误 |
| 65 | Codex Pet调用的输入JSON错误/模式不匹配（例如 `size: "1024_1024"` 而不是 `"1024*1024"`) |
| 69 | 上游5xx |
| 75 | 可重试：超时/429 |
| 77 | 未登录或token被拒绝 |

`magick`（ImageMagick）在干净的Codex Pet图集上返回0；非零值表示缺少输入帧或输出路径权限问题。

完整参考：[docs.runcomfy.com/cli/troubleshooting](https://docs.runcomfy.com/cli/troubleshooting?utm_source=skills.sh&utm_medium=skill&utm_campaign=codex-pet).

## 工作原理

1. 技能调用 `runcomfy run openai/gpt-image-2/edit` 一次，使用用户的源图像和紧密的chibi比例提示，生成一个1024x1024的标准Codex Pet，背景为品红色。
2. ImageMagick将品红色色度键为alpha 0，修剪精灵bbox，按纵横比适应到一个192x208单元格。
3. ImageMagick程序化构建9行条带，通过ImageMagick微变换（1-2 px平移，眨眼遮罩，旋转，镜像）到标准单元格。
4. 9行条带堆叠到1536x1872的Codex Pet图集；图集转换为WebP。
5. 编写一个 `pet.json` 清单；两个文件都复制到 `${CODEX_HOME:-$HOME/.codex}/pets/<name>/`，Codex自动识别自定义Codex Pet。

## 致谢

9行Codex Pet图集规范——列数、帧数、单元格尺寸——来自OpenAI官方的 [`hatch-pet`](https://github.com/openai/skills/tree/main/skills/.curated/hatch-pet) 技能（MIT授权）。动画行合同和色度键策略在那里有说明。这个技能重用了规范，但将视觉生成器（`$imagegen` → RunComfy GPT Image 2）和图集组装（Python → ImageMagick）进行了替换，因此无需Codex Pro即可运行。

## 这个技能不是什么

不是Codex客户端。当 `$imagegen` 可用时不是 `hatch-pet` 的替代方案——当Codex Pro可用时，官方 `hatch-pet` 更可取。不是自托管GPT Image 2——取决于一个有效的RunComfy账户。

## 安全与隐私

- **令牌存储**：`runcomfy login` 将API令牌写入 `~/.config/runcomfy/token.json`，权限为0600。设置 `RUNCOMFY_TOKEN` 环境变量以在CI中绕过文件。
- **输入边界**：Codex Pet提示作为JSON通过 `--input` 传递。CLI不会进行命令行扩展。没有shell注入表面。
- **第三方内容**：源图像URL由RunComfy服务器获取。将外部URL视为不受信任——基于图像的提示注入是任何图像编辑模型已知的风险。
- **出站端点**：仅 `model-api.runcomfy.net` 和 `*.runcomfy.net` / `*.runcomfy.com`。
- **生成文件大小上限**：CLI中止任何单个Codex Pet标准下载大于2 GiB。
- **本地安装路径**：最终的Codex Pet写入 `${CODEX_HOME:-$HOME/.codex}/pets/<pet-name>/`。没有远程上传。
