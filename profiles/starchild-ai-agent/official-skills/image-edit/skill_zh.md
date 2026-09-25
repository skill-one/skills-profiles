# 图像编辑

在 Starchild 上使用此技能处理**所有图像编辑和增强请求**。

涵盖：常规编辑、背景替换、超分辨率、老照片修复、上色、人物移除、人像润饰（皮肤平滑、瑕疵移除、牙齿美白）、瘦身、色彩分级、艺术滤镜、图像融合、图像扩展、局部编辑、文本渲染、多角度生成、前后对比、汽车改色、汽车贴膜预览以及健身/医疗转换对比。

**核心原则**：调用提供的脚本。不要重新实现代理/计费管道。

**何时使用 image-edit 而不是其他图像技能**：
- **image-edit** → 用户想要编辑、增强或转换现有图像
- **image-portrait** → 用户想要从参考照片中保留面部/身份的人像
- **image-create** → 用户想要从文本描述中创建内容（无源图像）

---

## 1. 快速入门 — 基本编辑（最常见）

> **⚠️ 执行上下文 — 首先阅读此内容。**
> 以下代码块是 **Python**，不是 shell 命令。Starchild 的 `bash` 工具
> 运行 `/bin/bash -c`，无法解析 `exec(open(...))` — 直接将其粘贴到 bash 命令中将会出现 `语法错误 near unexpected token 'open'`。
> 此外，`exec(open(...))` 在 `python3 -c` 中失败，因为脚本使用 `__file__` 进行路径解析。
>
> **通过 bash 工具调用时使用 `python3 - <<'EOF'` 与 `from exports import`：**
>
> ```bash
> python3 - <<'EOF'
> import sys
> sys.path.insert(0, "skills/image-edit")
> from exports import edit_image
> result = edit_image(
>     image_path="uploads/photo.jpg",
>     prompt="使天空更具戏剧性，使用金色日落色调",
>     action="enhance",
> )
> print(result)
> EOF
> ```
>
> 她源文档 (`<<'EOF'`) 保留所有引号和换行符 — 无需转义。

```python
exec(open('skills/image-edit/edit_image.py').read())
result = edit_image(
    image_path="uploads/photo.jpg",
    prompt="使天空更具戏剧性，使用金色日落色调",
    action="enhance",
)
# result -> {"success": True, "images": [{"local_path": "output/images/..."}], ...}
```

脚本读取本地文件，将其 base64 编码，并作为数据 URI 发送到 fal.ai — 无需手动发布 URL。

## 2. 快速入门 — 公开 URL

```python
exec(open('skills/image-edit/edit_image.py').read())
result = edit_image(
    image_url="https://example.com/photo.jpg",
    prompt="用热带海滩替换背景",
    action="replace_bg",
)
```

### 将结果交付给用户 — 重要提示

**永远不要直接将用户 raw fal.media URL。** fal 使用限制性 CSP 头部提供服务。唯一可靠的交付路径是**已下载的本地文件**：

1. 使用每个图像的 `local_path`（例如 `output/images/xxx.png`）— 脚本在成功时始终会下载。
2. 告知用户文件保存在 `output/images/` 中，并在工作区文件面板中可见。
3. 在 Web 渠道中，内嵌以使用户可以在聊天中预览：
   ```markdown
   ![edited](output/images/<filename>.png)
   ```
4. 在 Telegram / WeChat：通过 `send_to_telegram(file_path="output/images/...", message_type="image")` 或 `send_to_wechat(file_path="output/images/...", message_type="image")` 发送。

---

## 3. 参数

| 参数 | 必填 | 默认 | 描述 |
|-----------|----------|---------|-------------|
| `image_path` | 是* | — | 源图像的本地工作区文件路径 |
| `image_url` | 是* | — | 源图像的公共 HTTPS URL |
| `prompt` | 否 | auto | 编辑指令（要更改的内容） |
| `action` | 否 | `"edit"` | 操作类型（见 §4） |
| `model` | 否 | `"nanopro"` | 模型：`"nanopro"`（快速 ~25s）或 `"gpt"`（最佳质量 ~150s） |
| `aspect_ratio` | 否 | `None` | 输出比例：`1:1`，`3:4`，`4:3`，`9:16`，`16:9`。`None` = 保留原始比例。 |

*必须提供 `image_path` 或 `image_url` 之一。如果两者都提供，`image_path` 优先。

---

## 4. 操作类型 — 操作类型

### F: 多图像/常规编辑

| 操作 | 键 | 描述 |
|--------|-----|-------------|
| 常规编辑 | `edit` | 根据提示修改图像 |
| 图像融合 | `blend` | 将人物/主题放置到新的背景或场景中 |
| 图像扩展 | `extend` | 将图像扩展到当前边界之外 |
| 局部编辑 | `local_edit` | 仅修改图像的特定区域 |
| 结构重新设计 | `restructure` | 改变布局/网格/列数或重新排列元素 — 覆盖“保留构图” |
| 文本渲染 | `text_render` | 在图像中添加或修改文本 |
| 多角度 | `multi_angle` | 从一张照片生成不同的视角 |
| 前后对比 | `before_after` | 生成并排比较图像 |

### G: 专业编辑

| 操作 | 键 | 描述 |
|--------|-----|-------------|
| 背景替换 | `replace_bg` | 保留主体同时替换背景 |
| 超分辨率 | `upscale` | 提升和增强图像分辨率 |
| 照片修复 | `restore` | 修复老照片中的划痕、撕裂、褪色 |
| 上色 | `colorize` | 为黑白照片添加逼真的颜色 |
| 人物移除 | `remove_person` | 从照片中移除特定人物 |

### V: 润饰/美容

| 操作 | 键 | 描述 |
|--------|-----|-------------|
| 人像润饰 | `retouch` | 皮肤平滑、瑕疵移除、牙齿美白 |
| 瘦身 | `slim` | 微妙调整面部和身体比例 |
| 增强 | `enhance` | 色彩校正、光照改善、质量提升 |
| 艺术滤镜 | `filter` | 应用特定的艺术风格或滤镜效果 |

### W: 医疗/健身对比

| 操作 | 键 | 描述 |
|--------|-----|-------------|
| 转换对比 | `comparison` | 医疗、健身或转换的前后对比 |

### X: 汽车相关

| 操作 | 键 | 描述 |
|--------|-----|-------------|
| 汽车改色 | `car_color` | 更改车辆颜色 |
| 汽车贴膜预览 | `car_wrap` | 在车辆上可视化贴膜或薄膜 |

---

## 5. 模型选择指南

| 模型 | 键 | 速度 | 质量 | 最适合 |
|-------|-----|-------|---------|----------|
| NanoPro | `nanopro` | ~25s | 良好 | 默认用于所有请求。快速迭代。 |
| GPT Image 2 | `gpt` | ~150s | 最佳 | 当用户明确要求“最高质量”或“最佳质量”时。复杂编辑。 |

**决策规则：**
1. **默认：** 除非用户明确要求更高质量，否则始终使用 `nanopro`。
2. **使用 `gpt` 当：** 用户说“最高质量”、“最佳质量”、“高级”或编辑需要非常精确的细节保留（例如，复杂的文本渲染、精细的修复）。
3. **使用 `nanopro` 当：** 用户想要快速结果、正在迭代编辑或编辑内容简单。

```python
# 默认（快速）
result = edit_image(image_path="photo.jpg", prompt="移除背景", action="replace_bg")

# 高质量（用户请求）
result = edit_image(image_path="photo.jpg", prompt="移除背景", action="replace_bg", model="gpt")
```

---

## 6. 意图识别指南

使用此表格将用户请求映射到正确的操作：

### 常规编辑

| 用户说 | 操作 | 提示提示 |
|-----------|--------|-------------|
| "编辑这张照片"、"修改这张图像" | `edit` | 将用户的指令作为提示传递 |
| "把我放到海滩上"、"改变场景" | `blend` | 描述目标场景 |
| "扩展图像"、"让它更宽"、"outpaint" | `extend` | 描述要添加的内容 |
| "只改变衬衫颜色"、"编辑天空" | `local_edit` | 指定区域和更改 |
| "较少列"、"简化网格"、"重新排列布局"、"最多7列" | `restructure` | 明确指定目标结构（行/列/排列） |
| "添加文本"、"在图像上写 'Hello'" | `text_render` | 指定文本内容和位置 |
| "从侧面显示"、"不同角度" | `multi_angle` | 描述所需的视角 |
| "前后对比"、"显示差异" | `before_after` | 描述转换 |

### 专业编辑

| 用户说 | 操作 | 提示提示 |
|-----------|--------|-------------|
| "移除背景"、"更换背景"、"换背景" | `replace_bg` | 描述新背景 |
| "提升"、"使其更高分辨率"、"提升质量" | `upscale` | 可选地指定目标质量 |
| "修复老照片"、"修复这张损坏的照片"、"修复老照片" | `restore` | 描述要修复的特定损坏 |
| "上色"、"为黑白照片添加颜色"、"上色" | `colorize` | 可选地描述预期的颜色 |
| "移除这个人"、"P掉某人" | `remove_person` | 描述要移除的人物 |

### 润饰/美容

| 用户说 | 操作 | 提示提示 |
|-----------|--------|-------------|
| "润饰"、"平滑皮肤"、"移除瑕疵"、"磨皮美白" | `retouch` | 指定润饰级别 |
| "让我更瘦"、"瘦脸" | `slim` | 指定要调整的区域 |
| "增强颜色"、"改善光照"、"调色" | `enhance` | 描述期望的外观 |
| "应用滤镜"、"让它看起来复古"、"滤镜" | `filter` | 描述滤镜风格 |

### 医疗/健身

| 用户说 | 操作 | 提示提示 |
|-----------|--------|-------------|
| "手术前后"、"健身转换" | `comparison` | 描述转换背景 |

### 汽车相关

| 用户说 | 操作 | 提示提示 |
|-----------|--------|-------------|
| "改变汽车颜色"、"让它变成红色"、"汽车改色" | `car_color` | 指定目标颜色和光泽 |
| "汽车贴膜"、"贴膜预览"、"贴膜预览" | `car_wrap` | 描述贴膜材料和颜色 |

---

## 7. 提示工程最佳实践

### 提示模板系统

每个操作都有一个内置的提示模板，用于包装用户的指令以获得最佳结果。您只需要传递用户的特定意图 — 模板会自动添加技术质量指令。

例如，如果用户说“使背景成为日落海滩”：
```python
result = edit_image(
    image_path="photo.jpg",
    prompt="一个美丽的日落海滩，有棕榈树和金色光芒",
    action="replace_bg",
)
# 脚本将此包装为： "替换此图像的背景：一个美丽的日落海滩，有棕榈树和金色光芒。保持前景主体完美无损，边缘干净。匹配光照方向..."
```

### 关键原则（来自参考技能）

1. **具体说明更改** — 模糊的提示会产生差结果：
   - ❌ "让它更好"
   - ✅ "增加对比度，添加温暖的金色调，锐化细节"

2. **描述要保留的内容** — 特别是对于局部编辑：
   - ❌ "改变衬衫"
   - ✅ "将衬衫颜色改为海军蓝，保持相同的织物纹理和皱纹"

3. **指定材料和光泽** — 对于汽车和产品编辑：
   - ❌ "让它变成蓝色"
   - ✅ "深色金属蓝色，带有光泽的透明漆面"

4. **参考现实世界风格** — 对于滤镜和艺术效果：
   - ❌ "让它变得艺术"
   - ✅ "应用温暖的电影色彩分级，如伍迪·艾伦电影"

5. **描述修复/上色的时代**：
   - ❌ "上色"
   - ✅ "为这张1940年代的家庭照片上色，使用符合那个时代的服装颜色"

6. **对于润饰，指定级别**：
   - 轻度： "轻微皮肤平滑，保持自然纹理"
   - 中度： "专业润饰，移除瑕疵，均匀肤色"
   - 重度： "完整美容润饰，平滑皮肤，提亮眼睛，美白牙齿"

---

## 8. 按场景使用示例

### 背景替换

```python
exec(open('skills/image-edit/edit_image.py').read())

# 简单背景交换
result = edit_image(
    image_path="uploads/portrait.jpg",
    prompt="一个现代化的办公室，有落地窗和城市天际线视图",
    action="replace_bg",
)

# 工作室背景
result = edit_image(
    image_path="uploads/product.jpg",
    prompt="干净的白色工作室背景，带有柔和阴影",
    action="replace_bg",
)
```

### 老照片修复

```python
# 修复损坏的照片
result = edit_image(
    image_path="uploads/old_family_photo.jpg",
    prompt="修复所有划痕、撕裂和污渍；恢复褪色的颜色；增强清晰度",
    action="restore",
)

# 黑白照片上色
result = edit_image(
    image_path="uploads/grandpa_1945.jpg",
    prompt="使用符合1940年代时代的历史准确颜色上色，自然肤色，符合那个时代的服装",
    action="colorize",
)
```

### 人像润饰

```python
# 专业润饰
result = edit_image(
    image_path="uploads/selfie.jpg",
    prompt="专业人像润饰：平滑皮肤同时保持自然纹理，移除瑕疵，轻微牙齿美白，提亮眼睛",
    action="retouch",
)

# 瘦身
result = edit_image(
    image_path="uploads/photo.jpg",
    prompt="轻微面部瘦身，稍微更清晰的下巴线条，自然比例",
    action="slim",
)
```

### 图像增强

```python
# 色彩分级
result = edit_image(
    image_path="uploads/landscape.jpg",
    prompt="电影色彩分级，带有温暖的金色调，增强对比度，鲜艳但自然颜色",
    action="enhance",
)

# 艺术滤镜
result = edit_image(
    image_path="uploads/photo.jpg",
    prompt="油画风格，可见笔触，丰富的温暖调色板，印象派感觉",
    action="filter",
)
```

### 超分辨率提升

```python
result = edit_image(
    image_path="uploads/low_res.jpg",
    prompt="提升到最高质量，增强精细细节，减少噪声和压缩伪影",
    action="upscale",
)
```

### 人物移除

```python
result = edit_image(
    image_path="uploads/group_photo.jpg",
    prompt="移除右侧最远的人，与公园背景无缝填充",
    action="remove_person",
)
```

### 图像扩展（图像扩展）

```python
result = edit_image(
    image_path="uploads/cropped.jpg",
    prompt="向左右扩展图像，自然地继续山脉风景",
    action="extend",
    aspect_ratio="16:9",
)
```

### 汽车定制

```python
# 汽车改色
result = edit_image(
    image_path="uploads/my_car.jpg",
    prompt="改为深樱桃红色金属漆，带有光泽的透明漆面",
    action="car_color",
)

# 汽车贴膜预览
result = edit_image(
    image_path="uploads/my_car.jpg",
    prompt="哑光黑色乙烯基贴膜，车顶和后视镜有碳纤维装饰",
    action="car_wrap",
)
```

### 前后对比

```python
# 健身转换
result = edit_image(
    image_path="uploads/fitness_photo.jpg",
    prompt="创建健身转换对比，显示更健美和健壮的版本",
    action="comparison",
)
```

### 局部编辑

```python
# 更改特定元素
result = edit_image(
    image_path="uploads/outfit.jpg",
    prompt="仅更改连衣裙颜色从红色到祖母绿，保持相同的织物纹理",
    action="local_edit",
)
```

### 文本渲染

```python
result = edit_image(
    image_path="uploads/poster_bg.jpg",
    prompt="在顶部居中添加 'SUMMER SALE' 的粗白字，带有微妙的阴影",
    action="text_render",
)
```

### 高质量编辑

```python
# 使用 GPT 模型以获得最佳质量
result = edit_image(
    image_path="uploads/important_photo.jpg",
    prompt="专业色彩校正和增强，用于印刷出版",
    action="enhance",
    model="gpt",
)
```

---

## 9. 提供的脚本

| 文件 | 目的 |
|------|---------|
| `edit_image.py` | 核心脚本：解析图像 → 构建提示 → 提交 → 池化 → 下载。处理本地文件（base64）和 URL，所有操作，两个模型。 |
| `exports.py` | 重新导出 `edit_image`，`ACTIONS`，`ACTION_PROMPTS`，`MODELS` 以供其他技能程序化使用。 |
| `_cost_track.py` | 成本跟踪辅助程序 — 通过 sc-proxy 头部记录每次调用的成本。 |

---

## 10. 本地测试

设置 `FAL_KEY` 环境变量以直接调用 fal.ai（绕过 sc-proxy）：

```bash
# 基本编辑
FAL_KEY=your-fal-key python3 skills/image-edit/edit_image.py photo.jpg "让它更亮" enhance nanopro

# 参数：<image_path_or_url> [prompt] [action] [model]
```

---

## 11. 故障排除

| 问题 | 解决方法 |
|---------|-----|
| `File not found: ...` | 检查工作区路径；文件必须存在 |
| `Unsupported image format` | 使用 `.jpg`，`.jpeg`，`.png`，`.webp` 或 `.bmp` |
| `Image too large` | 调整到小于 10 MB 再上传 |
| `image_url must be a public HTTP(S) URL` | 使用 `image_path` 对于本地文件，或提供有效的 `https://` URL |
| `Unknown action` | 检查 §4 中的有效操作 |
| `HTTP 402 insufficient_credits` | 充值余额；成本在提交时预扣 |
| `HTTP 403 endpoint_not_allowed` | sc-proxy 仅允许批准的 fal 端点；联系管理员 |
| 编辑 `FAILED` 上游 | 简化提示，确保源图像清晰，重试 |
| 任务卡在 `IN_PROGRESS` >10 min | 保存 `request_id`，稍后重试 |
| 编辑质量差 | 尝试 `model="gpt"` 以获得更高质量；在提示中更具体 |
| 布局/网格/列数无论如何迭代都不会改变 | 优先使用 `action="restructure"` 进行结构更改 — 其模板强制执行布局更改。普通的 `edit` 现在具有优先级回退（显式结构指令覆盖构图保留），但将其仅视为兼容性网，而不是主要路径 |
| 背景未完全移除 | 使用 `replace_bg` 操作并明确描述背景 |
| 润饰看起来不自然 | 在提示中添加 "保持自然纹理" 或 "轻微" |

---

## 12. 基础设施（参考）

- 调用者 → `sc-proxy` → `queue.fal.run/{model}` → fal 模型提供者
- 所有请求都必须包含 `Authorization: Key fake-falai-key-12345`（代理注入真实的 `FAL_KEY`）
- 提交时发生预扣。轮询/结果调用是免费的。
- 本地文件作为数据 URI base64 编码 — 无需单独的上传步骤。
- 最终图像位于 `https://*.fal.media/...` — 公共 CDN，下载无需认证。
- 通过 `_cost_track.py` 进行成本跟踪 — 记录 `X-Credits-Used` 从 sc-proxy 响应头部。
