# image-3d

使用此技能处理 Starchild 上的所有 **3D 风格图像生成请求**。

涵盖：3D 角色设计（Q版、写实、卡通、奇幻）、3D 产品渲染（悬浮、分解、转盘）、等距场景与微缩场景、3D 应用图标（iOS、Material、游戏）、3D 文本效果（铬色、霓虹、木纹、糖果）、室内设计可视化（现代、奢华、舒适、工业）、建筑渲染（现代、传统、未来、俯视、夜景）、3D 场景（奇幻、科幻、自然、城市）、游戏资源渲染（武器、环境、道具、车辆）。

**核心原则**：调用提供的脚本。不要重新实现代理/计费管道。

**⚠️ 重要区别 — 3D 风格图像与 3D 模型文件：**
- **此技能** 生成 **3D 风格的 2D 图像**（PNG/JPG）— 看起来像 3D 的渲染图片
- 此技能 **不** 生成 3D 模型文件 (.glb, .obj, .fbx, .usdz)
- 对于实际的 3D 模型文件，用户需要专门的 3D 建模服务（Meshy 等）

**何时使用 image-3d 与其他图像技能：**
- **image-3d** → 用户想要 3D 渲染效果：3D 角色、等距场景、3D 图标、建筑渲染、室内设计渲染、3D 文本效果
- **image-create** → 用户想要一般创意图像（标志、海报、插画、表情包）— image-create 有基本的 `3d` 分类，但 image-3d 提供更细粒度的控制
- **image-ecommerce** → 用户想要用于电子商务列表的产品照片（白色背景、生活方式照片）
- **image-edit** → 用户想要编辑/转换现有图像
- **image-portrait** → 用户想要保留面部/身份信息的肖像

---

## 1. 快速入门 — 文本到 3D 图像（最常见）

> **⚠️ 执行上下文 — 首先阅读此内容。**
> 以下代码块是 **Python**，不是 shell 命令。Starchild 的 `bash` 工具
> 运行 `/bin/bash -c`，无法解析 `exec(open(...))` — 直接粘贴
> 到 bash 命令会因 `语法错误 near unexpected token 'open'` 失败。
> 此外，`exec(open(...))` 在 `python3 -c` 内部因使用 `__file__`
> 进行路径解析而失败。
>
> **通过 bash 工具调用时使用 `python3 - <<'EOF'` 与 `from exports import`：**
>
> ```bash
> python3 - <<'EOF'
> import sys
> sys.path.insert(0, "skills/image-3d")
> from exports import generate_3d
> result = generate_3d(
>     prompt="一个可爱的机器人助手，大眼睛和天线",
>     category="character",
>     style="chibi",
> )
> print(result)
> EOF
> ```
>
> 她文档 (`<<'EOF'`) 保留所有引号和换行符 — 无需转义。

```python
exec(open('skills/image-3d/generate_3d.py').read())
result = generate_3d(
    prompt="一个可爱的机器人助手，大眼睛和天线",
    category="character",
    style="chibi",
)
# result -> {"success": True, "images": [{"local_path": "output/images/..."}], ...}
```

## 2. 快速入门 — 仅类别 + 风格（无自定义提示）

```python
exec(open('skills/image-3d/generate_3d.py').read())
result = generate_3d(
    category="diorama",
    style="isometric",
)
# 使用内置的风格模板作为完整提示
```

## 3. 快速入门 — 参考图像 → 3D 风格

```python
exec(open('skills/image-3d/generate_3d.py').read())
result = generate_3d(
    prompt="转换为 3D 渲染角色",
    reference_path="uploads/sketch.jpg",
    category="character",
    style="cartoon",
)
```

### 将结果交付给用户 — 重要

**永远不要直接交给用户 raw fal.media URL。** fal 使用限制性的 CSP 头部服务文件。唯一可靠的交付路径是 **已经下载的本地文件**：

1. 使用每个图像的 `local_path`（例如 `output/images/xxx.png`）— 脚本在成功时始终下载。
2. 告知用户文件保存在 `output/images/`，可在工作区文件面板中查看。
3. 在 Web 渠道，内嵌以供用户在聊天中预览：
   ```markdown
   ![3d-render](output/images/<filename>.png)
   ```
4. 在 Telegram / WeChat：通过 `send_to_telegram(file_path="output/images/...", message_type="image")` 或 `send_to_wechat(file_path="output/images/...", message_type="image")` 发送。

---

## 4. 参数

| 参数 | 必填 | 默认 | 描述 |
|-------|------|------|------|
| `prompt` | 是* | — | 想要的 3D 图像的文本描述 |
| `reference_path` | 否 | — | 参考图像的本地文件路径（用于 3D 样式化） |
| `reference_url` | 否 | — | 参考图像的公共 HTTPS URL |
| `category` | 否 | `"character"` | 3D 类别预设（见 §5） |
| `style` | 否 | `"default"` | 类别内的子风格（见 §5） |
| `model` | 否 | `"nanopro"` | 模型：`"nanopro"`（快速 ~25 秒）或 `"gpt"`（最佳质量 ~150 秒） |
| `count` | 否 | `1` | 要生成的图像数量（1–4） |
| `aspect_ratio` | 否 | auto | 输出比例：`1:1`，`3:4`，`4:3`，`9:16`，`16:9`。如果没有设置，则由类别自动选择。 |

*`prompt` 对于文本到图像模式是必需的，除非指定了非默认的 `style`（这提供了内置模板）。

**提示优先级：** `prompt + category/style`（增强）> `prompt` 仅 > `category + style` 模板 > `category` 默认。

**自动选择宽高比：** 当未显式设置时，脚本为类别选择最佳比例：
- `3:4` 用于角色（纵向）
- `1:1` 用于产品、场景、图标、游戏资源（方形展示）
- `16:9` 用于文本、室内设计、建筑、场景（宽电影感）

---

## 5. 类别和风格预设

### N: 3D 角色 (`category="character"`)

| 风格 | 关键 | 适合 |
|------|------|------|
| Q版 / 皮克斯 | `chibi` | 可爱风格化角色、吉祥物、头像 |
| 写实 | `realistic` | 游戏角色、详细解剖 |
| 卡通 | `cartoon` | 迪士尼/皮克斯风格、家庭友好 |
| 奇幻 | `fantasy` | RPG 角色、战士、法师 |
| 一般 | `default` | 任何 3D 角色 |

**角色提示：**
- 描述姿势、服装、表情和配饰
- 指定“白色背景”或“干净背景”用于角色表
- 对于游戏角色，提及“T-pose”或“动作姿势”
- 示例：`"一个女性精灵游侠，绿色斗篷，手持弓，森林背景"`

### N: 3D 产品渲染 (`category="product"`)

| 风格 | 关键 | 适合 |
|------|------|------|
| 悬浮 3/4 角度 | `floating` | 主角产品照片、营销 |
| 分解视图 | `exploded` | 技术插图、内部结构 |
| 转盘 / 360° | `turntable` | 多角度展示 |
| 一般 | `default` | 任何产品渲染 |

**产品提示：**
- 描述材质（哑光、光泽、金属、木材、玻璃）
- 指定照明（工作室、戏剧性、柔和、轮廓光）
- 提及产品类型和关键特性
- 示例：`"无线耳机在充电盒中，哑光白色，悬浮角度"`

### N: 3D 场景 / 等距 (`category="diorama"`)

| 风格 | 关键 | 适合 |
|------|------|------|
| 等距 | `isometric` | 微缩世界、街区、游戏地图 |
| 低多边形 | `lowpoly` | 风格化场景、独立游戏美学 |
| 写实 | `realistic` | 建筑模型、详细微缩 |
| 一般 | `default` | 任何场景 |

**场景提示：**
- 描述场景内容（建筑、树木、角色、车辆）
- 提及比例（“微缩”、“微小”、“玩具屋”）
- 指定氛围（温暖、舒适、戏剧性、奇幻）
- 示例：`"夜晚的舒适日式拉面店，店内微缩顾客，温暖光芒"`

### N: 3D 图标 (`category="icon"`)

| 风格 | 关键 | 适合 |
|------|------|------|
| iOS 风格 | `ios` | Apple App Store 图标、光泽玻璃 |
| Material Design | `material` | Google Play 图标、平面带深度 |
| 游戏图标 | `game` | RPG 物品、幻想游戏 UI |
| 一般 | `default` | 任何 3D 图标 |

**图标提示：**
- 简单描述图标主题（一个主要元素）
- 指定形状上下文（“圆角方形”、“圆形”）
- 保持简单 — 图标在小尺寸下应可识别
- 示例：`"一个带有彩虹镜头光晕的相机图标"`

### N: 3D 文本 (`category="text"`)

| 风格 | 关键 | 适合 |
|------|------|------|
| 铬色 / 金属 | `chrome` | 粗体标题、电影风格文本 |
| 霓虹发光 | `neon` | 科幻、夜生活、标志 |
| 木材 | `wood` | 乡村、手工艺、自然品牌 |
| 糖果 | `candy` | 欢乐、儿童、甜主题 |
| 一般 | `default` | 任何 3D 文本效果 |

**文本提示：**
- ⚠️ AI 文本渲染不可靠 — 文本应保持简短（最多 1-3 个字）
- 用引号描述文本内容：`"the word 'HELLO'"`
- 指定材质和环境
- 示例：`"chrome 金属字母的 'GAME OVER'，暗背景"`

### L: 室内设计 (`category="interior"`)

| 风格 | 关键 | 适合 |
|------|------|------|
| 现代简约 | `modern` | 斯堪的纳维亚、简洁线条、自然光 |
| 奢华 | `luxury` | 高端、大理石、金色装饰 |
| 舒适 / 暖居 | `cozy` | 温暖、舒适、邀请 |
| 工业 | `industrial` | 楼下、裸露砖墙、都市时尚 |
| 一般 | `default` | 任何室内渲染 |

**室内提示：**
- 描述房间类型（客厅、卧室、厨房、浴室、办公室）
- 提及关键家具和材质
- 指定照明（自然日光、温暖傍晚、戏剧性）
- 如果重要，指定调色板
- 示例：`"现代斯堪的纳维亚客厅，大窗户，浅木地板，灰色沙发，室内植物"`

### L: 建筑 (`category="architecture"`)

| 风格 | 关键 | 适合 |
|------|------|------|
| 现代 | `modern` | 当代建筑、玻璃与钢铁 |
| 传统 | `traditional` | 经典、遗产、石材与木材 |
| 未来 | `futuristic` | 科幻、有机形态、绿色科技 |
| 俯视 | `aerial` | 鸟瞰、总平面图、场地环境 |
| 夜景 | `night` | 戏剧性照明、立面照明 |
| 一般 | `default` | 任何建筑渲染 |

**建筑提示：**
- 描述建筑类型（房屋、办公室、塔楼、博物馆、学校）
- 提及材质（混凝土、玻璃、钢铁、木材、石材、砖块）
- 指定环境（城市、郊区、山坡、滨水）
- 提及一天中的时间以用于照明（黄金时刻、中午、黄昏、夜晚）
- 示例：`"现代三层房屋，平屋顶，大型玻璃窗户，花园环绕，黄金时刻"`

### N: 3D 场景 (`category="scene"`)

| 风格 | 关键 | 适合 |
|------|------|------|
| 奇幻 | `fantasy` | 魔法世界、浮空岛屿 |
| 科幻 | `scifi` | 空间站、未来科技 |
| 自然 | `nature` | 森林、风景、自然美景 |
| 城市 | `urban` | 城市街道、赛博朋克、霓虹 |
| 一般 | `default` | 任何 3D 场景 |

### N: 游戏资源 (`category="game_asset"`)

| 风格 | 关键 | 适合 |
|------|------|------|
| 武器 | `weapon` | 剑、枪、魔法武器 |
| 环境 | `environment` | 游戏关卡、世界设计 |
| 道具 | `prop` | 物品、对象、收藏品 |
| 车辆 | `vehicle` | 汽车、船只、飞机 |
| 一般 | `default` | 任何游戏资源 |

---

## 6. 3D 渲染关键词指南

在构建自定义提示时，使用这些关键词来控制 3D 外观：

### 材质
| 关键词 | 效果 |
|------|------|
| `PBR 材质` | 物理渲染，真实表面 |
| `次表面散射` | 半透明皮肤、蜡、大理石 |
| `金属 / 铬色` | 反射金属表面 |
| `光泽 / 哑光` | 表面光洁度控制 |
| `玻璃 / 透明` | 透明材料 |
| `粘土渲染` | 哑光灰色，无纹理，形状焦点 |

### 照明
| 关键词 | 效果 |
|------|------|
| `工作室照明` | 干净、专业、受控 |
| `HDRI 照明` | 环境基础，自然反射 |
| `轮廓光` | 边缘高亮，主体分离 |
| `体积照明` | 光线束、大气深度 |
| `接触阴影` | 柔和接触阴影，深度 |
| `全局照明` | 真实光线反弹 |

### 相机 / 构图
| 关键词 | 效果 |
|------|------|
| `等距视图` | 45° 俯视，无透视变形 |
| `3/4 角度` | 经典产品/角色展示角度 |
| `视线高度` | 自然人类视角 |
| `鸟瞰` | 俯视空中视角 |
| `倾斜位移` | 微缩/场景效果 |
| `景深` | 背景模糊，主体聚焦 |

### 渲染引擎风格
| 关键词 | 效果 |
|------|------|
| `Octane 渲染` | 高质量，照片真实 |
| `Blender Cycles` | 真实路径追踪 |
| `Unreal Engine 5` | 游戏质量，实时外观 |
| `V-Ray` | 建筑可视化质量 |
| `Cinema 4D` | 干净，风格化 3D |
| `KeyShot` | 产品可视化质量 |

---

## 7. 模型选择指南

| 模型 | 关键 | 速度 | 质量 | 适合 |
|------|------|------|------|------|
| Nano Banana Pro | `nanopro` | ~25 秒 | 良好 | 快速迭代，草稿，大多数 3D 风格 |
| GPT Image 2 | `gpt` | ~150 秒 | 最佳 | 最终渲染，复杂场景，精细细节 |

**按类别推荐：**
- **角色** → `nanopro` 用于草稿，`gpt` 用于最终角色表
- **产品** → `gpt` 用于照片真实渲染，`nanopro` 用于快速概念
- **场景** → `nanopro` 处理等距效果良好；`gpt` 用于详细微缩
- **图标** → `nanopro` 对大多数图标足够
- **文本** → `gpt` 用于更好的文本渲染（仍然不可靠）
- **室内/建筑** → `gpt` 用于照片真实建筑可视化，`nanopro` 用于概念
- **场景** → `gpt` 用于电影感，`nanopro` 用于快速情绪板

---

## 8. 宽高比指南

| 类别 | 默认 | 推荐替代方案 |
|------|------|--------------|
| 角色 | `3:4` | `1:1` 用于头像，`9:16` 用于全身 |
| 产品 | `1:1` | `4:3` 用于横向展示 |
| 场景 | `1:1` | `16:9` 用于全景场景 |
| 图标 | `1:1` | 始终 `1:1` |
| 文本 | `16:9` | `1:1` 用于方形横幅 |
| 室内 | `16:9` | `4:3` 用于房间视图，`3:4` 用于垂直 |
| 建筑 | `16:9` | `3:4` 用于高建筑，`1:1` 用于俯视 |
| 场景 | `16:9` | `9:16` 用于垂直场景 |
| 游戏资源 | `1:1` | `3:4` 用于角色资源 |

---

## 9. 意图识别指南

将用户请求映射到正确的类别 + 风格：

| 用户说... | 类别 | 风格 | 备注 |
|----------|------|------|------|
| "3D 角色", "皮克斯风格角色" | `character` | `chibi` 或 `cartoon` | |
| "游戏角色", "RPG 英雄" | `character` | `fantasy` | |
| "写实 3D 人物" | `character` | `realistic` | |
| "3D 产品渲染", "产品可视化" | `product` | `floating` | |
| "分解视图", "内部结构" | `product` | `exploded` | |
| "等距", "微缩场景", "微小世界" | `diorama` | `isometric` | |
| "低多边形场景", "风格化环境" | `diorama` | `lowpoly` | |
| "应用图标", "iOS 图标" | `icon` | `ios` | |
| "游戏图标", "RPG 物品图标" | `icon` | `game` | |
| "3D 文本", "铬色文本", "金属字母" | `text` | `chrome` | |
| "霓虹标志", "发光文本" | `text` | `neon` | |
| "室内设计", "房间设计", "装修效果图" | `interior` | `modern` | |
| "奢华室内", "顶层公寓" | `interior` | `luxury` | |
| "舒适房间", "温暖室内" | `interior` | `cozy` | |
| "建筑渲染", "建筑可视化" | `architecture` | `modern` | |
| "夜景渲染", "建筑在夜晚" | `architecture` | `night` | |
| "俯视", "总平面图" | `architecture` | `aerial` | |
| "奇幻世界", "魔法场景" | `scene` | `fantasy` | |
| "科幻场景", "空间站" | `scene` | `scifi` | |
| "游戏武器", "剑渲染" | `game_asset` | `weapon` | |
| "游戏环境", "关卡设计" | `game_asset` | `environment` | |

---

## 10. 错误处理

| 错误 | 原因 | 修复 |
|------|------|------|
| `"Unknown model"` | 无效模型键 | 使用 `"nanopro"` 或 `"gpt"` |
| `"Unknown category"` | 无效类别 | 检查 §5 以获取有效类别 |
| `"Unknown style"` | 类别中不存在风格 | 检查该类别的风格表 |
| `"File not found"` | `reference_path` 不存在 | 验证文件路径 |
| `"Image too large"` | 参考图像 > 10 MB | 调整或压缩图像 |
| `"Submit failed"` | API 错误 | 检查 FAL_KEY，重试 |
| `"Generation timed out"` | 模型耗时过长 | 重试，或切换到 `nanopro` |

---

## 11. 高级示例

### 3D 角色表（多个角度）

```python
exec(open('skills/image-3d/generate_3d.py').read())
result = generate_3d(
    prompt="一个蒸汽朋克发明家角色，戴眼镜，皮夹克和机械臂，角色表显示正面和侧面视图",
    category="character",
    style="realistic",
    model="gpt",
    aspect_ratio="16:9",
)
```

### 等距城市街区

```python
exec(open('skills/image-3d/generate_3d.py').read())
result = generate_3d(
    prompt="一个繁忙的东京街角，拉面店，自动售货机，樱花树，微缩行人",
    category="diorama",
    style="isometric",
)
```

### 建筑夜景渲染

```python
exec(open('skills/image-3d/generate_3d.py').read())
result = generate_3d(
    prompt="一个现代艺术博物馆，弯曲的玻璃立面，前方的反射池，戏剧性照明",
    category="architecture",
    style="night",
    model="gpt",
)
```

### 室内设计 — 现代客厅

```python
exec(open('skills/image-3d/generate_3d.py').read())
result = generate_3d(
    prompt="宽敞的客厅，落地窗俯瞰城市天际线，简约家具，温暖木材装饰，室内植物",
    category="interior",
    style="modern",
    model="gpt",
)
```

### 参考图像 → 3D 风格

```python
exec(open('skills/image-3d/generate_3d.py').read())
result = generate_3d(
    prompt="转换为 3D 皮克斯风格角色，特征夸张",
    reference_path="uploads/photo.jpg",
    category="character",
    style="cartoon",
)
```

### 3D 游戏武器

```python
exec(open('skills/image-3d/generate_3d.py').read())
result = generate_3d(
    prompt="带有发光符文的传奇火焰剑，火星粒子，暗背景",
    category="game_asset",
    style="weapon",
)
```

### 3D 霓虹文本

```python
exec(open('skills/image-3d/generate_3d.py').read())
result = generate_3d(
    prompt="单词 'CYBER' 用粉色和蓝色霓虹字母，湿街道反射",
    category="text",
    style="neon",
)
```

### 多个图像用于比较

```python
exec(open('skills/image-3d/generate_3d.py').read())
result = generate_3d(
    prompt="一个舒适的咖啡店室内，裸露砖墙和温暖照明",
    category="interior",
    style="cozy",
    count=3,
    model="nanopro",
)
# 生成 3 个变体供用户选择
