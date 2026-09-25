# 电商图片工作流

从真实产品参考图像创建一套紧凑的电商图片。
此 V1 技能有意设计得狭窄：它仅支持**参考产品模式**。如果用户仅描述产品而未提供产品照片，则请求照片并停止。在此版本中不要创建仅基于简报的概念产品。

## 资源映射

```text
ecommerce-image-workflow/
|-- SKILL.md
|-- example.html
`-- references/
    `-- checklist.md
```

## 此技能生成的内容

默认情况下，为单个产品生成三个电商就绪的图像资源：

1. **主图像** - 干净的产品优先包装照片，背景为白色或柔和的中性色。
2. **特性图像** - 清晰展示一个卖点，并具有受控的标注空间，不依赖图像内微小的不可读文字。
3. **生活方式图像** - 产品在合理的使用环境中展示，同时保持产品忠实于参考图像。

还生成：

- `image-manifest.json` 描述参考输入、插槽、提示、输出、宽高比和保真度说明。
- `ecommerce-gallery.html` 作为一个小型预览画廊，链接生成的文件并总结图像角色。

## 输入合约

必需：

- 活动项目中至少上传一张产品参考图像。

仅请求缺失的基本要素：

- 如果产品名称或简短标签不明显，则请求产品名称或简短标签。
- 如果无法安全推断特性图像的主要卖点，则请求主要卖点。
- 仅当用户请求平台特定的构图时，才请求目标市场或宽高比。

不要问广泛探索性问题。保持工作流推进。

## 工作流

### 第 0 步 - 确认参考产品模式

在规划之前，验证当前项目是否包含真实的产品参考图像。

如果没有产品图像可用，回复：

> 请先上传至少一张产品参考图像。此 V1 工作流从参考照片保留真实产品；仅基于简报的概念生成将推迟到后续版本。

然后停止。

### 第 1 步 - 提取产品身份锚点

检查参考图像并编写简短内部身份锁定：

- 产品类别和形状。
- 形状和轮廓。
- 主要颜色和材料。
- 标志、标签、图案、纽扣、端口、肩带、把手或其他固定细节。
- 尺度提示和比例。
- 必须保持不变的内容。

在每次生成提示时使用这些锚点。

### 第 2 步 - 构建三插槽拍摄计划

在发送之前创建紧凑的拍摄计划：

| 插槽 | 默认宽高比 | 目标 |
|---|---:|---|
| main | 1:1 | 产品优先的电商平台图像，背景为白色或柔和的中性色 |
| feature | 4:5 | 清晰展示一个卖点，带有特写细节或简单标注空间 |
| lifestyle | 4:5 | 真实的使用环境，产品在视觉上仍忠实于参考 |

如果项目元数据提供 `imageAspect`，当用户期望整个集合使用单一宽高比时使用它。否则使用上述插槽默认值。

### 第 3 步 - 使用保真度锁定编写提示

每个提示必须在顶部附近包含此产品保真度指令：

```text
从参考图像保留精确的产品身份：形状、轮廓、颜色、材料、标志/标签位置、可见的构造细节和比例。不要重新设计产品。不要添加、删除或重新定位产品功能。
```

然后添加插槽特定指令：

#### 主图像提示

- 产品居中且完全可见。
- 白色、浅白色或非常浅的灰色背景。
- 柔和的影棚灯光和干净的阴影。
- 除非用户请求，否则不要使用道具。
- 不要使用帧内营销文字。

#### 特性图像提示

- 聚焦于用户提供的或安全推断的一个特性。
- 使用特写构图、切割式裁剪或干净的负空间，供后续设计师添加标注。
- 保持产品在画面中视觉平衡。如果没有生成明确的标注结构，则居中放置产品。如果需要标注空间，仅轻微偏移产品，并使空白空间感觉是故意的。
- 不要编造认证、性能数据、材料或声明。
- 避免微小的渲染文字；保留标注空间。

#### 生活方式图像提示

- 使用与产品类别匹配的逼真环境。
- 保持产品为焦点。
- 仅在它有助于解释使用且不会遮挡产品的情况下显示人类互动。
- 保留产品尺度和结构。

### 第 4 步 - 通过媒体合约发送

使用统一的 OpenDesign 媒体调度器。不要直接调用提供方 API 或自定义模型命令。

对于每个插槽，运行标准的生成/等待循环：

```bash
# POSIX bash。不要直接调用提供方 API。
out=$("$OD_NODE_BIN" "$OD_BIN" media generate \
  --project "$OD_PROJECT_ID" \
  --surface image \
  --model "<从元数据中获取的 imageModel>" \
  --aspect "<插槽宽高比或从元数据中获取的 imageAspect>" \
  --image "<项目相对的产品参考图像>" \
  --output "<产品缩写>-<插槽>.png" \
  --prompt "<完整插槽提示>")
ec=$?
if [ "$ec" -ne 0 ]; then echo "$out" >&2; exit "$ec"; fi

last=$(printf '%s\n' "$out" | tail -1)
task_id=$(printf '%s\n' "$last" |
  python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('taskId',''))" 2>/dev/null)
since=$(printf '%s\n' "$last" |
  python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('nextSince',0))" 2>/dev/null)
since="${since:-0}"

while [ -n "$task_id" ]; do
  out=$("$OD_NODE_BIN" "$OD_BIN" media wait "$task_id" --since "$since")
  ec=$?
  last=$(printf '%s\n' "$out" | tail -1)
  since=$(printf '%s\n' "$last" |
    python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('nextSince',0))" 2>/dev/null)
  since="${since:-0}"
  if [ "$ec" -eq 0 ]; then
    task_id=""
  elif [ "$ec" -ne 2 ]; then
    echo "$out" >&2
    exit "$ec"
  fi
done

printf '%s\n' "$last"
```

最后一行必须是包含 `{"file": {"name": "...", ...}}` 的 JSON。
将每个最终返回的文件名记录在 `image-manifest.json` 中。

如果活动图像模型或提供方无法使用 `--image`，停止并告诉用户此工作流需要一个参考能力的产品保真度生成路径。

### 第 5 步 - 编写 `image-manifest.json`

生成后，创建一个名为 `image-manifest.json` 的项目文件：

```json
{
  "workflow": "ecommerce-image-workflow",
  "mode": "reference-product",
  "productName": "示例产品",
  "referenceImages": ["reference-product.png"],
  "fidelityNotes": [
    "保留产品身份、颜色、材料、构造和比例。",
    "未经人工审核，不要将这些输出视为平台合规证明。"
  ],
  "slots": [
    {
      "id": "main",
      "role": "市场平台包装",
      "aspect": "1:1",
      "output": "example-product-main.png",
      "promptSummary": "产品优先的包装照片，背景为干净的中性色。"
    },
    {
      "id": "feature",
      "role": "单一特性突出",
      "aspect": "4:5",
      "output": "example-product-feature.png",
      "promptSummary": "特写或负空间构图，用于一个经过验证的卖点。"
    },
    {
      "id": "lifestyle",
      "role": "使用环境",
      "aspect": "4:5",
      "output": "example-product-lifestyle.png",
      "promptSummary": "产品为焦点的逼真场景。"
    }
  ]
}
```

保持清单诚实。如果细节未知，请写 `null` 或简短说明，而不是编造声明。

### 第 6 步 - 编写 `ecommerce-gallery.html`

创建一个简单的单文件 HTML 画廊，它：

- 首先显示参考图像。
- 显示三个生成的插槽及其角色名称。
- 列出产品保真度说明。
- 链接到 `image-manifest.json`。
- 仅使用系统字体和本地项目文件；不导入 CDN。

### 第 7 步 - 交接

回复：

- 生成的文件名。
- 使用保真度锁定的简短说明。
- 提醒市场特定合规性、最终文本叠加和声明/法律审核仍需人工审核。

不要发出 `<artifact>` 标签。

## 硬性规则

- V1 要求真实产品参考图像。没有仅基于简报的概念产品。
- 每次运行一个产品。
- 默认为三个插槽：主、特性、生活方式。
- 保留产品；不要重新设计它。
- 不要编造声明、认证、测量值、成分或性能数据。
- 使用 `"$OD_NODE_BIN" "$OD_BIN" media generate`；不要直接调用提供方 API。
- 生成后始终创建 `image-manifest.json`。
- 交接前运行 `references/checklist.md`。
