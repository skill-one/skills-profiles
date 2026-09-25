# Markdown to Feishu 文档

将本地 Markdown 文件转换为 Feishu 文档，并自动上传图片。

## 用户输入

用户只需提供 **Markdown 文件路径**。标题是可选的——如果未提供，将自动提取（见下文）。

## 第 1 步：确定文档标题

1. 读取 Markdown 文件并查找第一个 `# 标题`——将其用作标题。
2. 如果不存在 `# 标题`，扫描内容并基于主题生成简洁的描述性标题。
3. 如果用户明确提供标题，则使用该标题。

## 第 2 步：检查运行环境

按顺序尝试每个选项。使用**第一个可用的选项**。

### 选项 A：uvx（推荐）

```bash
which uvx
```

如果 `uvx` 可用，运行命令为：

```bash
uvx feishu-docx create "<标题>" -f <Markdown文件路径>
```

如果 `uvx` 运行时 Python < 3.11，请添加 `--python 3.11`：

```bash
uvx --python 3.11 feishu-docx create "<标题>" -f <Markdown文件路径>
```

### 选项 B：feishu-docx 已安装

```bash
which feishu-docx
```

如果找到，检查 Python 版本：

```bash
python3 --version
```

如果 Python >= 3.11，运行命令为：

```bash
feishu-docx create "<标题>" -f <Markdown文件路径>
```

### 选项 C：无可用选项——安装指南

如果既未找到 `uvx` 也未找到 `feishu-docx`，请告知用户：

> `feishu-docx` 需要 Python >= 3.11。使用以下任一方式安装：
>
> ```bash
> # 推荐：安装 uv，然后直接运行，无需全局安装
> curl -LsSf https://astral.sh/uv/install.sh | sh
> uvx feishu-docx create "标题" -f file.md
>
> # 或：使用 pip 全局安装（需要 Python >= 3.11）
> pip install feishu-docx
> ```
>
> 必须先配置 Feishu 凭证：
> ```bash
> feishu-docx config set --app-id <APP_ID> --app-secret <APP_SECRET>
> ```

然后停止并等待用户设置环境。

## 第 3 步：预处理 Mermaid 代码块

`feishu-docx` 工具无法处理 Mermaid 代码块。上传前，检查 Markdown 是否包含任何 ` ```mermaid ` 代码块，并先将它们转换为图片。

### 3a：扫描 Mermaid 代码块

读取 Markdown 文件并检查是否包含任何 ` ```mermaid ` 围栏代码块。如果**未找到，跳至第 4 步**。

### 3b：创建临时副本

将原始 Markdown 文件复制到同一目录下的临时文件（以便相对图片路径仍然有效）：

```
<原始文件名>.feishu-tmp.md
```

例如：`blog_post.md` → `blog_post.feishu-tmp.md`

后续所有修改都在此临时副本上进行。原始文件不会被修改。

### 3c：将 Mermaid 图表渲染为 PNG

对临时文件中的每个 ` ```mermaid ... ``` ` 代码块，使用 mermaid.ink API 将其渲染为 PNG 图片：

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

**重要提示：** 需要 `User-Agent` 头部——没有它会返回 403。

将渲染的图片保存到 Markdown 文件相同的目录下，使用基于图表内容的描述性文件名：

- 好：`mermaid-architecture-overview.png`，`mermaid-data-flow.png`
- 不好：`mermaid-1.png`，`diagram.png`

### 3d：用图片引用替换 Mermaid 代码块

在临时副本中，将每个 ` ```mermaid ... ``` ` 代码块替换为 Markdown 图片引用：

```markdown
![架构概述](mermaid-architecture-overview.png)
```

使用从临时文件到渲染图片的相对路径。

### 3e：使用临时文件进行上传

从这一步起，**临时文件**成为第 4 步中使用的 `<Markdown文件路径>`。

## 第 4 步：运行命令

- 在 Markdown 文件所在的目录（或相对图片路径能正确解析的目录）中运行，以便本地图片引用能正常工作。
- 工具将：
  - 将 Markdown 块转换为 Feishu 格式
  - 自动上传 Markdown 中引用的本地图片
  - 等待约 10 秒以保持块一致性，然后上传图片

## 第 5 步：清理

如果第 3 步创建了临时文件：
- 删除临时 Markdown 文件（`*.feishu-tmp.md`）
- 删除第 3c 步创建的所有渲染的 Mermaid PNG 文件（它们仅用于上传）

## 第 6 步：报告结果

向用户显示：
- 转换的块数量和上传的图片数量
- 创建的文档 ID
- 成功或失败状态

如果因认证错误失败，请提醒用户配置凭证：
```bash
feishu-docx config set --app-id <APP_ID> --app-secret <APP_SECRET>
```
