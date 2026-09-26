# Mermaid 工具

## 概述

该技能能够从 Markdown 文件中提取 Mermaid 图表，并生成高质量的 PNG 图片。该技能将所有必要的脚本（`extract-and-generate.sh`、`extract_diagrams.py` 和 `puppeteer-config.json`）打包在 `scripts/` 目录中，以确保可移植性和可靠性。

## 核心工作流程

### 标准图表提取和生成

使用打包的 `extract-and-generate.sh` 脚本从 Markdown 文件中提取 Mermaid 图表并生成 PNG 图片：

```bash
cd "${CLAUDE_SKILL_DIR}/scripts"
./extract-and-generate.sh "<markdown_file>" "<output_directory>"
```

**参数：**
- `<markdown_file>`：包含 Mermaid 图表的 Markdown 文件路径
- `<output_directory>`：(可选) 输出文件目录。默认为 `<markdown_file_directory>/diagrams`

**示例：**
```bash
cd "${CLAUDE_SKILL_DIR}/scripts"
./extract-and-generate.sh "<markdown_file>" "<output_directory>"
```

### 脚本功能

1. **提取** Markdown 文件中的所有 Mermaid 代码块
2. **按顺序** 对其进行编号（01、02、03 等）
3. **为每个图表生成** `.mmd` 文件
4. **创建** 高分辨率 PNG 图片并智能调整大小
5. **验证** 所有生成的 PNG 文件

### 输出文件

对于每个图表，脚本会生成：
- `01-diagram-name.mmd` - 提取的 Mermaid 代码
- `01-diagram-name.png` - 高分辨率 PNG 图片

编号确保图表保持其在源文档中的顺序。

## 高级用法

### 自定义尺寸和缩放

使用环境变量覆盖默认尺寸：

```bash
cd "${CLAUDE_SKILL_DIR}/scripts"
MERMAID_WIDTH=1600 MERMAID_HEIGHT=1200 ./extract-and-generate.sh "<markdown_file>" "<output_directory>"
```

**可用变量：**
- `MERMAID_WIDTH` (默认值：1200) - 基础宽度（像素）
- `MERMAID_HEIGHT` (默认值：800) - 基础高度（像素）
- `MERMAID_SCALE` (默认值：2) - 高分辨率输出的缩放因子

### 演示文稿用的高分辨率输出

```bash
cd "${CLAUDE_SKILL_DIR}/scripts"
MERMAID_WIDTH=2400 MERMAID_HEIGHT=1800 MERMAID_SCALE=4 ./extract-and-generate.sh "<markdown_file>" "<output_directory>"
```

### 打印质量输出

```bash
cd "${CLAUDE_SKILL_DIR}/scripts"
MERMAID_SCALE=5 ./extract-and-generate.sh "<markdown_file>" "<output_directory>"
```

## 智能尺寸功能

脚本会根据图表类型（从文件名检测）自动调整尺寸：

- **时间线/Gantt**：2400×400（宽而短）
- **架构/系统/缓存**：2400×1600（大而详细）
- **监控/工作流/序列/API**：2400×800（宽，适用于流程图）
- **默认**：1200×800（标准尺寸）

提取过程中的上下文感知命名有助于触发适当的智能尺寸调整。

## 重要原则

### 使用打包的脚本

**关键**：使用该技能的 `scripts/` 目录中的 `extract-and-generate.sh` 脚本。所有必要的依赖项都已打包在一起。

### 切换到脚本目录

从脚本所在目录运行脚本，以正确定位依赖项（`extract_diagrams.py` 和 `puppeteer-config.json`）：

```bash
cd "${CLAUDE_SKILL_DIR}/scripts"
./extract-and-generate.sh "<markdown_file>" "<output_directory>"
```

在切换到脚本目录之前运行脚本可能会导致因缺少依赖项而失败。

## 依赖项验证

在运行脚本之前，验证依赖项是否已安装：

1. **mermaid-cli**：`mmdc --version`
2. **Google Chrome**：`google-chrome-stable --version`
3. **Python 3**：`python3 --version`

如果有任何缺失，请参考 `references/setup_and_troubleshooting.md` 获取安装说明。

## 故障排除

有关详细的故障排除指南，请参阅 `references/setup_and_troubleshooting.md`，其中涵盖了：

- 浏览器启动失败
- 权限问题
- 未找到图表
- Python 提取失败
- 输出质量问题
- 图表特定的尺寸问题

常见问题的快速修复：

**权限被拒绝：**
```bash
chmod +x "${CLAUDE_SKILL_DIR}/scripts/extract-and-generate.sh"
```

**输出质量低：**
```bash
MERMAID_SCALE=3 ./extract-and-generate.sh "<markdown_file>" "<output_directory>"
```

**Chrome/Puppeteer 错误：**
验证所有 WSL2 依赖项是否已安装（请参阅参考资料获取完整列表）。

## 打包资源

### scripts/

该技能打包了所有必要的 Mermaid 图表生成脚本：

- **extract-and-generate.sh** - 主脚本，用于协调提取和 PNG 生成
- **extract_diagrams.py** - 用于从 Markdown 提取 Mermaid 代码块的 Python 脚本
- **puppeteer-config.json** - 用于 WSL2 环境的 Chrome/Puppeteer 配置

所有脚本都必须从 `scripts/` 目录运行，以确保正确定位依赖项。

### references/setup_and_troubleshooting.md

综合参考文档，包括：
- 完整的依赖项安装说明
- 详细的环境变量参考
- 广泛的故障排除指南
- WSL2 特定的 Chrome 依赖项设置
- 验证程序

在处理设置问题、安装问题或高级自定义需求时，请加载此参考文档。
