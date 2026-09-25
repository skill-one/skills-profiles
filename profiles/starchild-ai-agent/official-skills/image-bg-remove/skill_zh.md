# image-bg-remove

使用此技能处理 Starchild 上的所有**背景移除请求**。

覆盖范围：人像背景移除（身份证照、头像照）、产品抠图（电商白底图）、合影背景移除、宠物/动物抠图、物体隔离，以及为合成准备透明 PNG 文件。

**核心原则**：调用提供的脚本。不要重新实现代理/计费管道。

**与其他图像技能的关键区别**：此技能使用**专用背景移除模型**（`fal-ai/bria/background/remove` — Bria RMBG 2.0），而不是通用纳米模型或 GPT 模型。无需提示 — 只需提供图像。

---

## 1. 快速入门 — 本地文件（最常见）

> **⚠️ 执行上下文 — 首先阅读此内容。**
> 以下代码块是 **Python**，不是 shell 命令。Starchild 的 `bash` 工具运行 `/bin/bash -c`，无法解析 `exec(open(...))` — 直接将其粘贴到 bash 命令中会导致 `语法错误 near unexpected token 'open'`。
> 此外，`exec(open(...))` 在 `python3 -c` 内部会因 `NameError: __file__` 失败，因为脚本使用 `__file__` 进行路径解析。
>
> **通过 bash 工具调用时使用 `python3 - <<'EOF'` 并配合 `from exports import`：**
>
> ```bash
> python3 - <<'EOF'
> import sys
> sys.path.insert(0, "skills/image-bg-remove")
> from exports import remove_bg
> result = remove_bg(image_path="uploads/photo.jpg")
> print(result)
> EOF
> ```
>
> 她文档（`<<'EOF'`）保留了所有引号和换行符 — 无需转义。

```python
exec(open('skills/image-bg-remove/remove_bg.py').read())
result = remove_bg(image_path="uploads/photo.jpg")
# result -> {"success": True, "image": {"local_path": "output/images/..."}, "cost": 0.01, "duration_s": 3.2}
```

脚本读取本地文件，将其 base64 编码，并发送到 fal.ai 作为数据 URI — 无需手动发布 URL。

## 2. 快速入门 — 公开 URL

```python
exec(open('skills/image-bg-remove/remove_bg.py').read())
result = remove_bg(image_url="https://example.com/photo.jpg")
```

## 3. 快速入门 — 自定义输出路径

```python
exec(open('skills/image-bg-remove/remove_bg.py').read())
result = remove_bg(
    image_path="uploads/product.jpg",
    output_path="output/images/product_transparent.png",
)
```

### 将结果交付给用户 — 重要提示

**绝对不要直接将用户 fal.media URL。** fal 使用限制性 CSP 头部服务文件。唯一可靠的交付路径是**已下载的本地文件**：

1. 使用图像的 `local_path`（例如 `output/images/xxx.png`）— 脚本在成功时始终会下载。
2. 告知用户文件保存在 `output/images/`，并在工作区文件面板中可见。
3. 在 Web 渠道中，内联嵌入以便用户在聊天中预览：
   ```markdown
   ![transparent](output/images/<filename>.png)
   ```
4. 在 Telegram / 微信：通过 `send_to_telegram(file_path="output/images/...", message_type="image")` 或 `send_to_wechat(file_path="output/images/...", message_type="image")` 发送。

---

## 4. 参数

| 参数 | 必填 | 默认 | 描述 |
|-------|------|------|------|
| `image_path` | 是* | — | 源图像的工作区本地文件路径 |
| `image_url` | 是* | — | 源图像的公共 HTTPS URL |
| `output_path` | 否 | auto | 自定义输出文件路径。若未设置，将保存在 `output/images/` 并带时间戳。 |

*必须提供 `image_path` 或 `image_url` 中至少一个。如果两者都提供，`image_path` 优先。

**无提示参数** — 这是一个纯工具技能。专用模型会自动处理背景移除，无需任何文本指令。

---

## 5. 何时使用此技能

当用户想要执行以下操作时，使用 **image-bg-remove**：

| 用户说 | 使用此技能 |
|-------|----------|
| "remove the background" / "去背景" / "抠图" | ✅ 是 |
| "make it transparent" / "透明背景" | ✅ 是 |
| "create a cutout" / "cut out the person" | ✅ 是 |
| "product photo with white background" / "白底图" | ✅ 是 |
| "extract the foreground" / "isolate the subject" | ✅ 是 |
| "remove background from headshot" / "证件照去背景" | ✅ 是 |
| "transparent PNG" / "PNG cutout" | ✅ 是 |
| "remove background from pet photo" | ✅ 是 |
| "batch remove backgrounds" (多个图像) | ✅ 是 — 在循环中调用 `remove_bg()` |

---

## 6. 何时**不**使用此技能 — 使用 image-edit

| 用户说 | 使用 image-edit |
|-------|---------------|
| "replace background with a beach" / "换背景" | **image-edit** (`action="replace_bg"`) |
| "blur the background" / "背景虚化" | **image-edit** (`action="edit"`) |
| "change background color to blue" | **image-edit** (`action="replace_bg"`) |
| "edit the image" / "enhance the photo" | **image-edit** |
| "generate an image from text" | **image-create** |

**关键区别：**
- **image-bg-remove** → **移除**背景 → 输出透明 PNG
- **image-edit** (`replace_bg`) → **替换**背景，使用通用模型生成新场景

对于**背景替换工作流**，推荐的方法是：
1. 首先使用 **image-bg-remove** 获取干净的透明抠图
2. 然后使用 **image-edit** (`action="blend"`) 合成到新背景

这种两步方法比单次 `replace_bg` 调用效果更好，因为专用 RMBG 模型生成的边缘更干净。

---

## 7. 模型详情

| 属性 | 值 |
|------|----|
| 模型 | `fal-ai/bria/background/remove` (Bria RMBG 2.0) |
| 速度 | ~3 秒 |
| 成本 | ~$0.01 每个图像 |
| 输出 | 透明 PNG (RGBA) |
| 输入格式 | JPEG, PNG, WEBP, BMP |
| 最大输入大小 | 10 MB |

这是**唯一**使用专用单用途模型的图像技能。所有其他图像技能使用纳米模型或 GPT 通用模型。

---

## 8. 响应格式

```json
{
    "success": true,
    "image": {
        "url": "https://fal.media/files/...",
        "local_path": "output/images/20250531_153000_bg_removed.png",
        "size_bytes": 245760,
        "request_id": "abc123"
    },
    "cost": 0.01,
    "duration_s": 3.2
}
```

出错时：
```json
{
    "success": false,
    "error": "File not found: uploads/missing.jpg"
}
```

---

## 9. 用例示例

### 人像背景移除（身份证照 / 头像照）

```python
exec(open('skills/image-bg-remove/remove_bg.py').read())
result = remove_bg(image_path="uploads/headshot.jpg")
if result["success"]:
    print(f"透明头像保存：{result['image']['local_path']}")
```

### 电商产品抠图

```python
exec(open('skills/image-bg-remove/remove_bg.py').read())
result = remove_bg(image_path="uploads/product.jpg")
# 输出：准备用于白底产品列表的透明 PNG
```

### 批量处理多个图像

```python
exec(open('skills/image-bg-remove/remove_bg.py').read())
import glob

images = glob.glob("uploads/products/*.jpg")
for img in images:
    result = remove_bg(image_path=img)
    if result["success"]:
        print(f"✓ {img} → {result['image']['local_path']}")
    else:
        print(f"✗ {img}: {result['error']}")
```

### 背景移除 + 替换（两步工作流）

```python
# 第一步：使用专用模型移除背景（边缘更干净）
exec(open('skills/image-bg-remove/remove_bg.py').read())
result = remove_bg(image_path="uploads/portrait.jpg")
transparent_path = result["image"]["local_path"]

# 第二步：使用 image-edit 合成到新背景
exec(open('skills/image-edit/edit_image.py').read())
final = edit_image(
    image_path=transparent_path,
    prompt="将这个人放置在日落时的热带海滩上",
    action="blend",
)
```

---

## 10. 支持的输入格式

| 格式 | 扩展名 | 备注 |
|------|--------|------|
| JPEG | `.jpg`, `.jpeg` | 最常见的输入格式 |
| PNG | `.png` | 支持现有 alpha 通道 |
| WebP | `.webp` | 现代网络格式 |
| BMP | `.bmp` | 遗留格式 |

最大文件大小：10 MB。

---

## 11. 故障排除

| 问题 | 解决方案 |
|------|----------|
| "File not found" | 检查文件路径是否相对于工作区根目录 |
| "Unsupported image format" | 首先转换为 JPEG/PNG/WebP |
| "Image too large" | 调整到小于 10 MB 再处理 |
| "Submit failed: 401" | 检查 FAL_KEY 环境变量（本地）或 sc-proxy 配置（生产） |
| 超时 | 罕见 — 模型通常在 ~3s 内完成。重试一次。 |
