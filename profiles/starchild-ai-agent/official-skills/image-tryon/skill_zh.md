# image-tryon

使用此技能处理 Starchild 上的所有虚拟试穿请求。

涵盖：服装试穿、配饰试穿、发型预览、妆容预览、眼镜试穿、帽子试穿、鞋子试穿、手表试穿。

**核心原则**：调用提供的脚本。不要重新实现代理/计费管道。

**与 image-edit 的关键区别**：试穿始终需要**两张图片**——一张人物照片和一件服装/物品照片。

---

## 1. 快速入门——服装试穿（最常见）

> **⚠️ 执行上下文——请先阅读。**
> 以下代码块是**Python**，不是 shell 命令。Starchild 的 `bash` 工具运行 `/bin/bash -c`，无法解析 `exec(open(...))` —— 将它们直接粘贴到 bash 命令中会导致 `语法错误 near unexpected token 'open'`。此外，`python3 -c` 中的 `exec(open(...))` 会因脚本使用 `__file__` 进行路径解析而失败为 `NameError: __file__`。
>
> **通过 bash 工具调用时使用 `python3 - <<'EOF'` 并配合 `from exports import`：**
>
> ```bash
> python3 - <<'EOF'
> import sys
> sys.path.insert(0, "skills/image-tryon")
> from exports import try_on
> result = try_on(
>     person_path="uploads/person.jpg",
>     garment_path="uploads/dress.jpg",
>     category="clothing",
> )
> print(result)
> EOF
> ```
>
> 她文档 (`<<'EOF'`) 保留了所有引号和换行符——无需转义。

```python
exec(open('skills/image-tryon/try_on.py').read())
result = try_on(
    person_path="uploads/person.jpg",
    garment_path="uploads/dress.jpg",
    category="clothing",
)
# result -> {"success": True, "images": [{"local_path": "output/images/..."}], ...}
```

脚本读取两个本地文件，将它们 base64 编码，并作为数据 URI 发送到 fal.ai——无需手动发布 URL。

## 2. 快速入门——URL 输入

```python
exec(open('skills/image-tryon/try_on.py').read())
result = try_on(
    person_url="https://example.com/person.jpg",
    garment_url="https://example.com/jacket.jpg",
    category="clothing",
)
```

## 3. 快速入门——眼镜试穿

```python
exec(open('skills/image-tryon/try_on.py').read())
result = try_on(
    person_path="uploads/face.jpg",
    garment_path="uploads/sunglasses.jpg",
    category="glasses",
)
```

### 将结果交付给用户——重要

**永远不要直接将原始 fal.media URL 交给用户。** fal 使用限制性 CSP 头部服务文件。唯一可靠的交付路径是**已下载的本地文件**：

1. 使用每个图片的 `local_path`（例如 `output/images/xxx.png`）——脚本在成功时始终会下载。
2. 告知用户文件保存在 `output/images/`，可在工作区文件面板中查看。
3. 在 Web 渠道中，内嵌显示以便用户在聊天中预览：
   ```markdown
   ![try-on result](output/images/<filename>.png)
   ```
4. 在 Telegram / WeChat：通过 `send_to_telegram(file_path="output/images/...", message_type="image")` 或 `send_to_wechat(file_path="output/images/...", message_type="image")` 发送。

---

## 4. 参数

| 参数 | 必填 | 默认 | 描述 |
|-------|------|------|------|
| `person_path` | 是* | — | 人物照片的本地工作区文件路径 |
| `person_url` | 是* | — | 人物照片的公共 HTTPS URL |
| `garment_path` | 是* | — | 服装/物品照片的本地工作区文件路径 |
| `garment_url` | 是* | — | 服装/物品照片的公共 HTTPS URL |
| `category` | 否 | `"clothing"` | 试穿类别键（见 §5） |
| `prompt` | 否 | `None` | 自定义提示——设置时覆盖类别默认值 |
| `model` | 否 | `"nanopro"` | 模型：`"nanopro"`（快速 ~25 秒）或 `"gpt"`（最佳质量 ~150 秒） |
| `aspect_ratio` | 否 | `"3:4"` | 输出比例：`1:1`，`3:4`，`4:3`，`9:16`，`16:9` |

**图片输入规则：**
- **人物图片**：提供 `person_path` 或 `person_url`（必须有一个）。
- **服装/物品图片**：提供 `garment_path` 或 `garment_url`（必须有一个）。
- 如果同一图片同时提供了路径和 URL，路径优先。
- 两者图片都必需——仅一张图片无法进行试穿。

**提示优先级**：`prompt`（完全覆盖）> `category` 默认提示。

---

## 5. 试穿类别

### 意图识别——用户说什么 → 使用哪个类别

| 用户说 | 类别 | 键 |
|-------|------|----|
| "试穿这件连衣裙/衬衫/夹克/套装" | 服装 | `clothing` |
| "戴上这个项链/围巾/包" | 配饰 | `accessory` |
| "展示这个发型/发色" | 发型 | `hairstyle` |
| "应用这个妆容/口红效果" | 妆容 | `makeup` |
| "试戴这些眼镜/太阳镜" | 眼镜 | `glasses` |
| "戴上这个帽子/鸭舌帽/贝雷帽" | 帽子 | `hat` |
| "试穿这些鞋子/运动鞋/靴子" | 鞋子 | `shoes` |
| "戴上这块手表" | 手表 | `watch` |

### 类别详情

| 类别 | 键 | 适合 | 照片要求 |
|-------|----|------|----------|
| 服装 | `clothing` | 衬衫、连衣裙、夹克、裤子、外套、全套服装 | 全身或上半身人物照片 |
| 配饰 | `accessory` | 围巾、包、皮带、珠宝、项链、耳环 | 可见相关身体部位 |
| 发型 | `hairstyle` | 剪发、发色、造型变化 | 清晰的脸部/头部照片 |
| 妆容 | `makeup` | 口红、眼影、粉底、腮红、全套妆容 | 清晰的脸部特写 |
| 眼镜 | `glasses` | 处方眼镜、太阳镜、阅读眼镜 | 清晰的脸部照片，正面 |
| 帽子 | `hat` | 鸭舌帽、贝雷帽、费多拉帽、遮阳帽、头盔 | 头部和肩膀可见 |
| 鞋子 | `shoes` | 运动鞋、高跟鞋、靴子、凉鞋、乐福鞋 | 全身或下半身照片 |
| 手表 | `watch` | 指针式、智能手表、奢侈手表 | 手腕/前臂可见 |

---

## 6. 模型选择指南

| 模型 | 键 | 速度 | 质量 | 适合 |
|------|----|------|------|------|
| NanoPro | `nanopro` | ~25 秒 | 良好 | 默认所有请求。快速迭代。 |
| GPT Image 2 | `gpt` | ~150 秒 | 最佳 | 用户明确要求“最高质量”或“最佳质量”时。 |

**决策规则：**
1. **默认**：除非用户明确要求更高质量，始终使用 `nanopro`。
2. **使用 `gpt` 时**：用户说“最高质量”、“最佳质量”、“高级”，或结果需要专业用途的逼真效果。
3. **使用 `nanopro` 时**：用户需要快速结果、尝试多个物品或迭代造型。

```python
# 默认（快速）
result = try_on(person_path="me.jpg", garment_path="dress.jpg", category="clothing")

# 高质量（用户要求）
result = try_on(person_path="me.jpg", garment_path="dress.jpg", category="clothing", model="gpt")
```

---

## 7. 按类别使用示例

### 服装试穿
```python
exec(open('skills/image-tryon/try_on.py').read())
result = try_on(
    person_path="uploads/person_fullbody.jpg",
    garment_path="uploads/summer_dress.jpg",
    category="clothing",
)
```

### 配饰试穿
```python
exec(open('skills/image-tryon/try_on.py').read())
result = try_on(
    person_path="uploads/portrait.jpg",
    garment_path="uploads/gold_necklace.jpg",
    category="accessory",
)
```

### 发型预览
```python
exec(open('skills/image-tryon/try_on.py').read())
result = try_on(
    person_path="uploads/face.jpg",
    garment_path="uploads/bob_hairstyle.jpg",
    category="hairstyle",
)
```

### 妆容预览
```python
exec(open('skills/image-tryon/try_on.py').read())
result = try_on(
    person_path="uploads/face_closeup.jpg",
    garment_path="uploads/evening_makeup.jpg",
    category="makeup",
)
```

### 眼镜试穿
```python
exec(open('skills/image-tryon/try_on.py').read())
result = try_on(
    person_path="uploads/face_front.jpg",
    garment_path="uploads/aviator_sunglasses.jpg",
    category="glasses",
)
```

### 帽子试穿
```python
exec(open('skills/image-tryon/try_on.py').read())
result = try_on(
    person_path="uploads/head_shoulders.jpg",
    garment_path="uploads/fedora_hat.jpg",
    category="hat",
)
```

### 鞋子试穿
```python
exec(open('skills/image-tryon/try_on.py').read())
result = try_on(
    person_path="uploads/person_fullbody.jpg",
    garment_path="uploads/white_sneakers.jpg",
    category="shoes",
)
```

### 手表试穿
```python
exec(open('skills/image-tryon/try_on.py').read())
result = try_on(
    person_path="uploads/wrist_photo.jpg",
    garment_path="uploads/luxury_watch.jpg",
    category="watch",
)
```

### 自定义提示（覆盖默认）
```python
exec(open('skills/image-tryon/try_on.py').read())
result = try_on(
    person_path="uploads/person.jpg",
    garment_path="uploads/vintage_jacket.jpg",
    category="clothing",
    prompt="人物穿着第二张图片中的复古皮革夹克，搭配休闲街头风格造型。保持人物的面部和身体完全一致。添加逼真的皮革纹理和自然垂坠效果。",
)
```

### 不同宽高比
```python
exec(open('skills/image-tryon/try_on.py').read())
result = try_on(
    person_path="uploads/person.jpg",
    garment_path="uploads/outfit.jpg",
    category="clothing",
    aspect_ratio="9:16",  # 全身肖像
)
```

---

## 8. 照片要求——最佳实践

### 人物照片指南

| 类别 | 推荐照片类型 | 小贴士 |
|------|------------|-------|
| 服装 | 全身，正面 | 手臂略微远离身体，中性姿势 |
| 配饰 | 可见相关身体部位 | 配饰部位良好光照 |
| 发型 | 清晰头部/面部，正面或 3/4 视角 | 头发束起或当前造型清晰可见 |
| 妆容 | 脸部特写，正面 | 干净面部，均匀光照，无浓妆 |
| 眼镜 | 正面，眼睛可见 | 无现有眼镜，清晰眼部区域 |
| 帽子 | 头部和肩膀，正面 | 无现有帽子，头发可见 |
| 鞋子 | 全身或腿部/脚部可见 | 站立姿势，当前鞋子可见 |
| 手表 | 手腕/前臂可见 | 裸露手腕或当前手表可见 |

### 一般照片质量规则

1. **光照**：良好光照，均匀光照效果最佳。避免面部/身体出现硬阴影。
2. **分辨率**：推荐 1024×1024 或更高。低分辨率照片效果差。
3. **角度**：大多数类别正面照片效果最佳。
4. **背景**：任何背景均可，但干净背景效果更佳。
5. **姿势**：自然、放松的姿势。避免极端角度或严重裁剪。

### 服装/物品照片指南

1. **产品照片效果最佳**：白色/中性背景的官方产品图片。
2. **清晰可见**：物品应为焦点，不可遮挡。
3. **多角度**：服装最关键的是正面视图。
4. **颜色准确性**：确保照片显示真实颜色（无重滤镜）。
5. **高分辨率**：详细的产品图片产生更好的试穿结果。

---

## 9. 自定义试穿的提示工程

当默认类别提示无法产生预期结果时，使用自定义 `prompt`。遵循以下指南：

### 5 元素试穿提示结构

```
[人物保留] + [物品描述] + [贴合/定位] + [风格/氛围] + [质量锚点]
```

### 关键原则

1. **始终保留身份**："保持人物的面部、身体形状和姿势完全一致。"
2. **清晰描述物品**："穿着第二张图片中的红色皮革夹克"
3. **指定贴合和定位**："自然垂坠，肩部贴合得当，逼真褶皱"
4. **添加风格背景**："休闲街头风格造型"，"正式商务着装"
5. **质量锚点**："专业时尚摄影"，"编辑级质量"，"逼真阴影"

### 自定义提示示例

**正式套装：**
```
人物穿着第二张图片中的海军蓝西装。保持人物的面部、身体和姿势完全一致。西装应完美贴合，剪裁得当——清晰的肩线，正确的袖长，自然垂坠的领口。专业时尚摄影质量，工作室灯光。
```

**休闲街头风格：**
```
人物穿着第二张图片中的宽松连帽衫，搭配休闲街头风格。保持人物身份和姿势相同。连帽衫应自然垂坠，具有逼真的织物重量和休闲贴合感。都市摄影风格。
```

**珠宝组合：**
```
人物佩戴第二张图片中的钻石吊坠项链。保持人物的一切不变。项链应自然垂在锁骨上，具有逼真的闪光和光线反射。链长和吊坠大小应与人物身材比例协调。
```

---

## 10. 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| "人物图片错误：必须提供 person_path 或 person_url" | 缺少人物照片 | 请求用户提供照片 |
| "服装/物品图片错误：必须提供 garment_path 或 garment_url" | 缺少物品照片 | 请求用户提供物品照片 |
| "文件未找到" | 无效文件路径 | 检查文件路径并重试 |
| "不支持的图片格式" | 非图片文件 | 使用 JPG、PNG 或 WebP |
| "图片过大" | 文件 > 10 MB | 调整或压缩图片 |
| "未知类别" | 无效类别键 | 使用 8 个有效类别之一 |
| 低质量结果 | 输入照片质量差 | 使用高分辨率、良好光照的照片 |
| 物品定位错误 | 身体定位不清晰 | 使用正面照片，目标区域可见 |

---

## 11. 不应使用此技能的情况

- **单张图片编辑**（无服装/物品参考）→ 使用 `image-edit` 技能
- **肖像生成**（从单一参考生成造型照片）→ 使用 `image-portrait` 技能
- **文本到图片**（无参考照片）→ 使用 `image-create` 技能
- **时尚模特生成**（从零创建模特）→ 使用 `image-create` 技能
