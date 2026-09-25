# 技能：屏幕截图压缩

原地压缩屏幕截图图片（PNG/JPEG），同时保持原始格式。使用 `pngquant` 处理 PNG 文件，使用 `jpegoptim` 处理 JPEG 文件——这两种工具对于屏幕截图内容（UI 元素、文本、扁平色）都非常有效。

> **前提条件**：系统必须已安装 `pngquant` 和 `jpegoptim`。脚本将**不会**自动安装它们——它会检查这些工具是否存在，并在缺失时打印安装说明。

---

## 使用场景

用户拥有过大的屏幕截图文件，并希望在不改变格式的情况下减小文件大小。常见场景：
- 准备用于 GitHub README、博客文章或文档的图片
- 提交到仓库前减小图片大小
- 批量压缩截图目录

---

## 为什么要保持原始格式（不使用 WebP）

WebP 压缩效果更好，但在某些场景下兼容性较差：

| 场景 | WebP 支持 |
|------|----------|
| 浏览器（Chrome/Firefox/Safari/Edge） | 支持 |
| GitHub Issues/PRs | 支持 |
| 微信编辑器 | **不支持** |
| Word / PowerPoint | **不支持** |
| 部分论坛/博客后端 | 不确定 |

保持 PNG/JPEG 确保压缩后的图片可以在任何地方正常使用。

---

## 默认工作流程

```bash
python /path/to/skills/screenshot-compression/scripts/compress_screenshots.py <文件或目录>
```

脚本将：
1. 检查 `pngquant` 和 `jpegoptim` 是否已安装——如果未安装，则打印安装说明并退出
2. 通过文件扩展名自动检测文件格式
3. 原地压缩每个文件（覆盖原始文件）
4. 打印每个文件和总体的压缩摘要

---

## 依赖检查

脚本需要两个系统工具。如果其中任何一个缺失，它将打印安装说明并退出，而不是继续执行。**不要替用户安装它们**——只需传递错误消息，让用户自行安装。

安装命令：
```bash
# macOS
brew install pngquant jpegoptim

# Ubuntu / Debian
sudo apt install pngquant jpegoptim

# CentOS / RHEL
sudo yum install pngquant jpegoptim
```

---

## 脚本选项

| 标志 | 默认值 | 描述 |
|------|--------|------|
| `paths`（位置参数） | 必须提供 | 要压缩的图片文件或目录 |
| `-r`, `--recursive` | 关闭 | 递归处理目录 |
| `--png-quality` | `80-95` | pngquant 质量范围（最小-最大，0-100） |
| `--jpeg-quality` | `85` | jpegoptim 最大质量（0-100） |

---

## 示例

```bash
# 压缩单个文件
python .../compress_screenshots.py screenshot.png

# 压缩目录中的所有图片
python .../compress_screenshots.py ./images/

# 递归目录扫描
python .../compress_screenshots.py ./docs/ --recursive

# 高质量代码截图
python .../compress_screenshots.py *.png --png-quality 90-100

# 激进压缩缩略图
python .../compress_screenshots.py *.jpg --jpeg-quality 70
```

---

## 质量调整指南

| 场景 | `--png-quality` | `--jpeg-quality` |
|------|----------------|-----------------|
| 普通截图（文档、网页） | `80-95` | `85` |
| 代码截图（需要清晰的文本） | `90-100` | `90` |
| 缩略图/预览（优先考虑大小） | `60-80` | `70` |

---

## 工作原理

### PNG (`pngquant`)
- 将 24 位真彩色（1600 万色）量化为 8 位调色板（256 色）
- 使用 Floyd-Steinberg 邻域扩散算法处理平滑渐变
- 屏幕截图是理想候选——UI 颜色通常远少于 256 种唯一值
- 典型压缩率：**60-80%**

### JPEG (`jpegoptim`)
- 在指定质量级别重新编码
- 通过 `--strip-all` 删除元数据（EXIF、ICC 配置文件、缩略图）
- 优化霍夫曼表
- 典型压缩率：**20-50%**

---

## 重要说明

- 文件将原地压缩——原始文件将被覆盖。如有需要，请先备份文件。
- 仅处理 `.png`、`.jpg` 和 `.jpeg` 文件。其他格式将被静默跳过。
- 脚本不会安装依赖项。如果工具缺失，它将打印安装说明并退出。
