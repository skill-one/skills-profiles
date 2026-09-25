# Codex Pet — Pro Pack on RunComfy

[runcomfy.com](https://www.runcomfy.com/?utm_source=skills.sh&utm_medium=skill&utm_campaign=codex-pet) · [GPT Image 2 edit endpoint](https://www.runcomfy.com/models/openai/gpt-image-2/edit?utm_source=skills.sh&utm_medium=skill&utm_campaign=codex-pet) · [docs](https://docs.runcomfy.com/cli/introduction?utm_source=skills.sh&utm_medium=skill&utm_campaign=codex-pet)

**RunComfy 上的 Codex Pet 生成器。** 将一张源图转化为兼容 Codex 的定制 Codex Pet —— `pet.json` + `spritesheet.webp` —— 将其放入 `${CODEX_HOME:-$HOME/.codex}/pets/<name>/`，Codex 会在 8 个内置 Codex Pet 旁边自动识别并加载它。

```bash
npx skills add agentspace-so/runcomfy-agent-skills --skill codex-pet -g
```

## 什么是 Codex Pet

OpenAI Codex Pet（2026 年 5 月发布）是像素风动画陪伴伙伴，会在 Codex 编写代码时在桌面端浮动，并对鼠标交互和 Codex 状态作出反应——思考时会挠头，任务完成时会弹出气泡。Codex 内置 8 个 Codex Pet，并支持在 `${CODEX_HOME:-$HOME/.codex}/pets/` 下的文件夹中本地安装定制 Codex Pet。

每个定制 Codex Pet 文件夹恰好包含两个文件：

- `pet.json` — 清单文件，包含 `id`、`displayName`、`description`、`spritesheetPath`。
- `spritesheet.webp` — Codex Pet 图集（sprite atlas），**1536x1872** PNG 或 WebP，8 列 x 9 行，每格 192x208 像素，透明背景。

9 行对应 Codex 播放的 9 种动画状态。每行使用固定数量的前导帧；尾部单元格保持完全透明。

## 为什么选择这个 Codex Pet 技能（而非 OpenAI 官方的 `hatch-pet`）

OpenAI 提供了官方的 [`hatch-pet`](https://github.com/openai/skills/blob/main/skills/.curated/hatch-pet/SKILL.md) 技能，通过 Codex 内部的 `$imagegen` 系统技能生成相同的 Codex Pet 产物（需要 Codex Pro 且已配置 `$imagegen`）。

**本 Codex Pet 技能是基于 RunComfy CLI 运行的即用型替代方案**：只需一个 `RUNCOMFY_TOKEN`，配合 `runcomfy` 和 `magick` 二进制文件即可——无需 Codex Pro、无需 `$imagegen`、无需 OPENAI_API_KEY。输出产物与官方 `hatch-pet` 完全一致——相同的 `pet.json` 结构、相同的 1536x1872 `spritesheet.webp` 图集、相同的 9 行动画行——因此 Codex 会将此 Codex Pet 视为由 `hatch-pet` 生成的产物，处理方式完全一致。

本技能遵循 Codex 内置 Codex Pet 所采用的一致模式：**单一标准姿态，通过 ImageMagick 微变换在单元格间复制**以实现细微动画（1-2 像素位移、眨眼帧、倾斜帧）。这与官方 `hatch-pet` 输出逐单元格实际呈现的效果一致——Codex 桌面应用中可见的 Codex Pet 动画是有意设计得较为细微的。

何时选择本技能：

- 想要定制 Codex Pet 但未使用 Codex Pro / `$imagegen`。
- 希望通过 RunComfy Model API 生成定制 Codex Pet。
- 需要从源图文件夹批量生成 Codex Pet（每只宠物仅需一次标准调用）。
- 以其他模型视觉呈现，参与 OpenAI Codex Pet 竞赛。
- 明确提及 "codex pet"、"/hatch"、"make me a codex pet"、"spritesheet.webp"、"desktop pet for codex" 等指令。

## Codex Pet 动画行

Codex 读取一张固定图集：8 列，9 行，每格 192x208 像素。每个 Codex Pet 行对应一种动画状态，且具有特定的前导帧数量。

| 行 | 状态 | 使用的列 | 帧数 | Codex Pet 行为 |
|---|---|---|---|---|
| 0 | idle（待机） | 0-5 | 6 | 平静呼吸/眨眼；Codex Pet 的 reduced-motion（减弱动画）首帧 |
| 1 | running-right（向右跑） | 0-7 | 8 | Codex Pet 向右移动 |
| 2 | running-left（向左跑） | 0-7 | 8 | 镜像向左移动 |
| 3 | waving（挥手） | 0-3 | 4 | 问候/致意动作 |
| 4 | jumping（跳跃） | 0-4 | 5 | 蓄力、抬升、峰值、下降、落定 |
| 5 | failed（失败） | 0-7 | 8 | 错误/难过/泄气反应 |
| 6 | waiting（等待） | 0-5 | 6 | 耐心待机变体 |
| 7 | running（运行中） | 0-5 | 6 | 活跃工作中/进行中循环（非腿部奔跑） |
| 8 | review（审阅） | 0-5 | 6 | 专注/检视/思考 |

每行最后一个使用列之后的尾部单元格必须完全透明。

## Codex Pet 风格

Codex Pet 视觉风格规范：

- **夸张的 Q 版比例**：头部占整体身高的约 60%；身体和四肢细小、短促。整个形象应适应近方形的外接框。
- 像素艺术风格的低分辨率吉祥物，粗轮廓
- 粗重的深色 1-2 像素边框，可见的阶梯式像素边缘
- 有限调色板，扁平赛璐璐上色，简洁有表现力的面部，细小四肢
- 透明背景

避免：运动线、投影、发光、闪光、浮动效果、文字标签、场景装饰、白底/黑底。

## 前提条件

1. **RunComfy CLI** — `npm i -g @runcomfy/cli`
2. **RunComfy 账户** — `runcomfy login`。CI 替代方案：`RUNCOMFY_TOKEN=<token>`。
3. **ImageMagick** — `brew install imagemagick`（macOS）或 `apt-get install imagemagick`（Linux）。提供 `magick` 命令，用于确定性地组装图集。
4. **源图 URL** — 可公开获取的 HTTPS 链接，JPEG/PNG/WebP，Codex Pet 将要模仿的对象图像。

## Codex Pet 流水线（1 次 GPT Image 2 调用，约 2 分钟）

1. **标准 Codex Pet** — 一次 `runcomfy run openai/gpt-image-2/edit` 调用，生成一张 1024x1024 的 Q 版姿态，背景为品红色色键（chroma-key）。
2. **单元格归一化** — 将品红色键转为 alpha 0，裁剪至宠物精灵边界框，调整为 192x208 并填充透明边距。
3. **9 行条带程序化生成** — 对每种动画状态，通过 ImageMagick 微变换（translate / mask / mirror）从标准单元格构建该行的 8 个单元格。未使用的尾部单元格填充为透明的 192x208 内容。
4. **图集** — 将 9 行条带垂直堆叠为 1536x1872 的 Codex Pet 图集。
5. **WebP 转换** — 将图集 PNG 转换为 WebP。
6. **清单与安装** — 写入 `pet.json`，将两个文件复制到 `${CODEX_HOME:-$HOME/.codex}/pets/<pet-name>/`。

微变换方案与 Codex 内置 Codex Pet 实际采用的方案一致——Codex Pet 动画有意识设计得较为细微，因此每个单元格的 1-2 像素位移和眨眼遮罩能提供正确的视觉效果，而无需消耗 72 次 GPT Image 2 调用。

### 步骤 1：生成标准 Codex Pet（1 次调用）

```bash
PET_NAME="my-pet"
PET_DESC="A friendly companion for late-night refactors."
SOURCE_URL="https://.../source.png"
RUN_DIR="./codex-pet-run/${PET_NAME}"
CHROMA="#FF00FF"   # 品红色色键
mkdir -p "${RUN_DIR}"

runcomfy run openai/gpt-image-2/edit \
  --input "{
    \"prompt\": \"Generate one canonical Codex digital pet sprite based on the input image. EXAGGERATED chibi proportions: the head occupies about 60 percent of the total figure height; body and legs are tiny stubby and short. The whole pet figure must fit within a near-square bounding box (overall aspect close to 1:1). Pixel-art-adjacent low-resolution mascot, chunky whole-body silhouette, thick dark 1-2 px outline, visible stepped pixel edges, limited palette, flat cel shading, simple expressive face, tiny limbs. Centered in the image. No polished illustration, no painterly render, no anime key art, no 3D render, no glossy app-icon polish, no realistic detail. Background: solid flat magenta ${CHROMA} chroma-key fill outside the pet silhouette. The pet itself must not use the chroma-key color or any close-to-magenta highlights. No gradients, no shadows, no halos, no scenery, no text. Identity preserved from the input image.\",
    \"images\": [\"${SOURCE_URL}\"],
    \"size\": \"1024*1024\"
  }" \
  --output-dir "${RUN_DIR}/decoded/"

BASE=$(ls "${RUN_DIR}/decoded/"*.png | head -1)
echo "canonical Codex Pet: ${BASE}"
```

### 步骤 2：将标准生成归一化为 192x208 Codex Pet 单元格

将品红色键转为 alpha，裁剪至宠物精灵边界框，调整为 192x208 并填充透明边距。

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

18% 的 fuzz 值是针对 GPT Image 2 抗锯齿品红边缘的调优。若 Codex Pet 品红边缘晕染较宽，可调整为 25%；若宠物带有接近品红的亮点导致被裁剪，可调整为 8-10%。

### 步骤 3：程序化构建 9 个 Codex Pet 行条带

对每行，从标准单元格通过 ImageMagick 微变换构建 8 个单元格，未使用的尾部单元格填充为透明内容，然后拼接为 1536x208 的行条带。

```bash
SRC="${RUN_DIR}/cell.png"
mkdir -p "${RUN_DIR}/cells"

# 辅助函数
shift_cell() { magick "$SRC" -background none -roll "+${1}+${2}" -alpha set "$3"; }
rotate_cell() { magick "$SRC" -background none -distort SRT "$1" -alpha set "$2"; }
make_blink() {
  # 眼睛大致位于 208 高单元格的 y=80-100 处。
  # 通过在该水平带应用肤色覆盖来柔化。
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

# 9 个 Codex Pet 行及其每帧微变换
build_row 0 base base blink base base blink                                       # idle（待机）（6）
build_row 1 base shift:1:0 shift:2:-1 shift:1:0 base shift:-1:0 shift:-2:-1 shift:-1:0  # running-right（向右跑）（8）
# 第 2 行 = running-left = 第 1 行水平镜像，下面构建
build_row 3 base shift:0:-1 base shift:0:-1                                       # waving（挥手）（4）
build_row 4 shift:0:2 base shift:0:-8 shift:0:-2 base                              # jumping（跳跃）（5）— 垂直弧线
build_row 5 base shift:0:1 rotate:1 shift:0:1 shift:0:2 shift:0:1 rotate:-1 base  # failed（失败）（8）
build_row 6 base base shift:0:-1 base base shift:0:1                              # waiting（等待）（6）
build_row 7 base shift:0:-1 base shift:0:-1 base shift:0:-1                       # running（运行中）（6）
build_row 8 base rotate:-2 base rotate:2 base base                                # review（审阅）（6）

# 第 2 行：running-left = running-right 的镜像
magick "${RUN_DIR}/cells/row1-strip.png" -flop -alpha set "${RUN_DIR}/cells/row2-strip.png"
```

微变换表赋予了 Codex Pet 在 Codex 中可读但细微的运动效果。请根据每行喜好微调数值；位移量有意保持较小（1-2 像素），使 Codex Pet 鲜活而不显分散。

### 步骤 4：组合 Codex Pet 图集

将 9 行条带垂直堆叠为 1536x1872 的 Codex Pet 图集，然后转换为 WebP。

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

### 步骤 5：写入 Codex Pet 清单

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

### 步骤 6：安装 Codex Pet

```bash
DEST="${CODEX_HOME:-$HOME/.codex}/pets/${PET_NAME}"
mkdir -p "${DEST}"
cp "${RUN_DIR}/pet.json" "${RUN_DIR}/spritesheet.webp" "${DEST}/"
echo "Codex Pet installed at ${DEST}"
```

重启 Codex（或重新加载宠物列表）后，定制 Codex Pet 将出现在 8 个内置宠物旁边。

## 提示生成标准 Codex Pet —— 有效做法

单次 GPT Image 2 调用决定了一切。提示词正确，后续步骤将确定性完成。

**以 Q 版比例锁定作为首要要点。** "EXAGGERATED chibi proportions, head ~60 percent of figure height"（夸张的 Q 版比例，头部约占整体身高 60%）是区分瘦高角色（与 192x208 单元格配合不佳，出现条形图效果）与头部占主导的 Q 版（自然填满单元格）的关键。后者正是 Codex 内置 Codex Pet 呈现的效果。

**在每次 Codex Pet 基础提示词中明确要求品红 `#FF00FF` 色键**。GPT Image 2 仅输出 RGB（无 alpha），因此获取透明 Codex Pet 的唯一方式是后处理时对已知背景颜色进行色键抠图。

**禁止宠物本身使用色键颜色**。添加："The pet itself must not use the chroma-key color or any close-to-magenta highlights."（宠物本身不得使用色键颜色或任何接近品红的亮点。）否则色键步骤会去除宠物身上恰好偏品红的部位。

**锁定风格**。"pixel-art-adjacent, chunky silhouette, 1-2 px outline, limited palette, flat cel shading"（像素艺术风格、粗轮廓、1-2 像素边框、有限调色板、扁平赛璐璐上色）——锁定所有使 Codex Pet 符合 Codex 风格规范的关键表述。

**禁止错误风格**。"No polished illustration, no painterly render, no anime key art, no 3D render, no glossy app-icon polish, no realistic detail."（无精修插画、无绘画渲染、无动漫 key art、无 3D 渲染、无光滑应用图标级打磨、无写实细节。）若省略此句，GPT Image 2 会倾向于过度渲染的动漫艺术。

**反模式**：
- 笼统的 "transparent background"（透明背景）—— GPT Image 2 会绘制近白色。应使用色键抠图。
- 让模型自由发挥比例——它会绘制高瘦窄 Q 版，无法适配 192x208。
- 在单次提示词中混合风格——锁定一种风格锚点并坚持到底。

## 微动画调优

步骤 3 中默认的 ImageMagick 方案生成的 Codex Pet 动画与内置 Codex Pet 相似——细微的上下浮动、偶尔眨眼、跳跃弧线、头部倾斜。如需使动画更或更不明显，可调整位移量：

- **更大的待机浮动**：将第 0 行的 `shift:0:-1` 改为 `shift:0:-2`。
- **更快的奔跑循环**：增大第 1 行的水平位移（例如将 `shift:2:-1` 改为 `shift:3:0`）。
- **更高的跳跃**：将第 4 行的峰值从 `shift:0:-8` 改为 `shift:0:-12`。
- **审阅时更强的头部倾斜**：将 `rotate:-2` / `rotate:2` 改为 `rotate:-4` / `rotate:4`。

保持位移量较小（≤ 4 像素或 ≤ 4°），使 Codex Pet 不显分散。

## FAQ — Codex Pet

**什么是 Codex Pet？** OpenAI Codex Pet 是 2026 年 5 月推出的像素风动画陪伴伙伴，在桌面端浮动，并对 Codex 的编程状态作出反应。定制 Codex Pet 以 `${CODEX_HOME:-$HOME/.codex}/pets/<name>/` 下的 `pet.json` + `spritesheet.webp` 文件形式存在。

**为什么使用本 Codex Pet 技能而非 `hatch-pet`？** 官方 `hatch-pet` 需要 Codex 内部的 `$imagegen` 系统技能（Codex Pro）。本技能仅需 `RUNCOMFY_TOKEN`，并通过 RunComfy CLI 执行相同的动画行规范，总共仅需 1 次 GPT Image 2 调用。

**Codex Pet 生成需要多长时间？** 约 2 分钟——1 次 GPT Image 2 编辑调用（约 90 秒）加数秒的 ImageMagick 图集组装。

**为何仅需一次 API 调用？** Codex 桌面应用中的 Codex Pet 动画是有意设计得较为细微的（可通过检查任意内置 Codex Pet 的图集确认——72 个单元格的姿态几乎完全一致，仅有细微差异）。一次标准姿态加上确定性的 ImageMagick 微变换，能在不消耗 72 次独立生成调用的前提下，产生相同的动画效果。

**Codex Pet 技能能否使用非人类主体？** 可以——宠物、吉祥物、物体、食物均可。基础提示词会自动将源图像简化为 Codex Pet 风格规范。

**如何安装我的 Codex Pet？** 将 `pet.json` 和 `spritesheet.webp` 复制到 `${CODEX_HOME:-$HOME/.codex}/pets/<pet-name>/` 并重新加载 Codex 即可。

**若标准 Codex Pet 偏离了原身份怎么办？** 重新运行步骤 1，使用更严格的身份保持提示词（例如具体指明特征：发色、眼镜、配饰等）。步骤 2-6 为确定性步骤，无需更改。

**每个 Codex Pet 帧的尺寸是多少？** 192x208 像素。每行条带为 1536x208（8 帧）。最终 Codex Pet 图集为 1536x1872（9 行堆叠）。

**能否添加自定义姿态或替换行？** 可以——修改步骤 3 中的 `build_row` 调用。每行的图集槽位数量必须符合 Codex 契约（idle=6，running-right/left=8，waving=4，jumping=5，failed=8，waiting/running/review=6），Codex 才能正确播放。

## 局限性

- **每个 Codex Pet 仅有一种标准姿态** — 动画通过 ImageMagick 变换实现，而非多帧模型生成。这与内置 Codex Pet 的细微动画一致，但无法产生戏剧性运动（如独特的逐帧奔跑循环）。
- **GPT Image 2 不输出 alpha** — 品红色键 + 后处理是变通方案。若 Codex Pet 带有接近品红的颜色（Q 版调色板中罕见），应将色键切换为其他纯色（`#00FFFF` 青色或 `#00FF00` 绿色），在提示词和后处理中均需如此。
- **身份偏移** — GPT Image 2 可能将源图像的特定身份简化为 Codex Pet 风格；特定小细节（如耳环、道具颜色）可能发生偏移。
- **Codex Pet 无音频/语音** — Codex Pet 仅支持视觉。

## 退出码

`runcomfy` CLI 使用 sysexits 风格编码：

| code | 含义 |
|---|---|
| 0 | Codex Pet 标准生成成功 |
| 64 | CLI 参数错误 |
| 65 | Codex Pet 调用/模式的输入 JSON 错误（如 `size: "1024_1024"` 而非 `"1024*1024"`） |
| 69 | 上游 5xx |
| 75 | 可重试：超时 / 429 |
| 77 | 未登录或令牌被拒绝 |

`magick`（ImageMagick）在 Codex Pet 图集生成成功时返回 0；非零值表示缺少输入帧或输出路径权限问题。

完整参考：[docs.runcomfy.com/cli/troubleshooting](https://docs.runcomfy.com/cli/troubleshooting?utm_source=skills.sh&utm_medium=skill&utm_campaign=codex-pet)。

## 工作原理

1. 该技能以用户源图和严格的 Q 版比例提示词调用一次 `runcomfy run openai/gpt-image-2/edit`，在品红背景上生成 1024x1024 的标准 Codex Pet。
2. ImageMagick 将品红色键抠图为 alpha 0，裁剪精灵边界框，调整为 192x208 单元格。
3. ImageMagick 通过微变换（1-2 像素位移、眨眼遮罩、旋转、镜像）程序化构建 9 行条带。
4. 9 行条带堆叠为 1536x1872 的 Codex Pet 图集；图集转换为 WebP。
5. 写入 `pet.json` 清单文件；将两个文件复制到 `${CODEX_HOME:-$HOME/.codex}/pets/<name>/`，Codex 将自动识别该定制 Codex Pet。

## 致谢

9 行 Codex Pet 图集规范——列数、帧数、单元格尺寸——源自 OpenAI 官方的 [`hatch-pet`](https://github.com/openai/skills/tree/main/skills/.curated/hatch-pet) 技能（MIT 许可）。动画行契约与色键策略在该文档中有所说明。本技能复用该规范，但将视觉生成器（`$imagegen` → RunComfy GPT Image 2）和图集组装（Python → ImageMagick）进行替换，因此无需 Codex Pro 即可运行。

## 本技能并非

- 非 Codex 客户端。
- 非官方 `hatch-pet` 替代——若可用 `$imagegen`，当 Codex Pro 可用时，官方 `hatch-pet` 更优。
- 非自托管的 GPT Image 2——依赖于可正常工作的 RunComfy 账户。

## 安全与隐私

- **令牌存储**：`runcomfy login` 将 API 令牌写入 `~/.config/runcomfy/token.json`，权限为模式 0600。CI 中可通过设置 `RUNCOMFY_TOKEN` 环境变量绕过该文件。
- **输入边界**：Codex Pet 提示词通过 `--input` 以 JSON 形式传递。CLI 不进行 shell 展开。不存在 shell 注入面。
- **第三方内容**：源图 URL 由 RunComfy 服务器获取。请将外部 URL 视为不可信——图像式提示注入是任何图像编辑模型的已知风险。
- **出站端点**：仅 `model-api.runcomfy.net` 及 `*.runcomfy.net` / `*.runcomfy.com`。
- **生成文件大小限制**：CLI 会中止任何单个 Codex Pet 标准下载大小超过 2 GiB 的操作。
- **本地安装路径**：最终的 Codex Pet 写入 `${CODEX_HOME:-$HOME/.codex}/pets/<pet-name>/`。无远程上传。
