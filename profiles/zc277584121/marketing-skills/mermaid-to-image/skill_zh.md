# 技能：Mermaid转图像

将 Markdown（或其他文本）文件中的 ` ```mermaid ` 代码块转换为 PNG 图像，并用图像引用替换代码块。适用于原生不渲染 Mermaid 的平台（GitHub Pages/Jekyll、Dev.to 等）。

---

## 使用场景

- 用户要求将文件中的 Mermaid 图表转换为图像
- 用户希望将特定的 Mermaid 代码块渲染为 PNG
- 发布工作流需要静态图像而不是 Mermaid 代码块

---

## 工作流程

### 第一步：识别目标文件

用户可以指定：
- 单个文件：`convert mermaid blocks in docs/architecture.md`
- 多个文件：`convert mermaid in all files under docs/`
- 特定的代码块：`convert the second mermaid block in README.md`

扫描目标文件，查找 ` ```mermaid ` 代码块。在继续之前，报告找到的代码块数量和所在文件。

### 第二步：确定图像输出目录

检查项目结构，找到通常存储图像的位置：

```bash
# 查找常见的图像目录
ls -d images/ img/ assets/ assets/images/ static/images/ docs/images/ 2>/dev/null
```

**如果存在明确的图像目录**（例如 `images/`、`assets/images/`），则使用它。如果合适，按主题创建子目录（例如 `images/<topic>/`）。

**如果没有明显的图像目录或存在多个候选目录**，询问用户：

```
我应该将渲染的 Mermaid 图像保存在哪里？

1. images/ (创建新目录)
2. assets/images/
3. docs/figures/
4. 自定义 — 输入路径
```

### 第三步：将每个图表渲染为 PNG

使用 [mermaid.ink](https://mermaid.ink) API 渲染图表。对每个代码块运行以下 Python 代码片段：

```python
import base64, urllib.request

def render_mermaid(code: str, output_path: str):
    """通过 mermaid.ink API 将 Mermaid 图表渲染为 PNG。"""
    encoded = base64.urlsafe_b64encode(code.encode()).decode()
    url = f"https://mermaid.ink/img/{encoded}?bgColor=white"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    resp = urllib.request.urlopen(req, timeout=30)
    with open(output_path, "wb") as f:
        f.write(resp.read())
```

**重要提示：** 需要设置 `User-Agent` 头部 — 没有它，mermaid.ink 会返回 403。

#### 命名规范

使用基于图表内容的描述性文件名，而不是通用名称：

- 良好：`architecture-overview.png`、`data-flow.png`、`heartbeat-sequence.png`
- 不良：`mermaid-1.png`、`diagram.png`、`image1.png`

### 第四步：用图像引用替换代码块

用从文件到图像的**相对路径**将每个 ` ```mermaid ... ``` ` 代码块替换为 Markdown 图像引用：

```markdown
![架构概述](images/topic/architecture-overview.png)
```

如果项目使用绝对 URL（例如 GitHub Pages），则使用它们：

```markdown
![架构概述](https://example.github.io/images/topic/architecture-overview.png)
```

选择与项目现有图像引用匹配的链接样式。如果不确定，请使用相对路径。

### 第五步：报告结果

处理完成后，总结：
- 转换了多少个图表
- 图像保存的位置
- 哪些文件被修改

---

## 边缘情况

- **大型图表**：对于非常复杂的图表，mermaid.ink 可能会超时。如果渲染失败，报告错误并建议用户简化图表或尝试其他渲染器。
- **单个文件中的多个代码块**：按顺序处理所有代码块，并为每个代码块分配唯一的描述性文件名。
- **已渲染的代码块**：如果 mermaid 代码块已经有一个对应的图像（被注释掉或相邻），则跳过它或询问用户。
- **非 Markdown 文件**：相同的方法适用于包含 mermaid 代码块的任何文本文件（例如 `.rst`、`.txt`）。
