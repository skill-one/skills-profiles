# 使用 ImageMagick 进行图像处理

此技能可使用 ImageMagick 在 Windows、Linux 和 macOS 系统上进行图像处理和操作。

## 使用场景

当您需要执行以下操作时，请使用此技能：

- 调整图像大小（单个或批量）
- 获取图像尺寸和元数据
- 在不同图像格式之间转换
- 创建缩略图
- 处理不同屏幕尺寸的壁纸
- 根据特定标准批量处理多个图像

## 前置条件

- 系统上已安装 ImageMagick
- **Windows**：PowerShell 中可用 `magick`（或位于 `C:\Program Files\ImageMagick-*\magick.exe`）
- **Linux/macOS**：通过包管理器（`apt`、`brew` 等）安装的 Bash

## 核心功能

### 1. 图像信息

- 获取图像尺寸（宽度 x 高度）
- 检索详细元数据（格式、色彩空间等）
- 识别图像格式

### 2. 图像调整大小

- 调整单个图像大小
- 批量调整多个图像大小
- 创建具有特定尺寸的缩略图
- 保持宽高比

### 3. 批量处理

- 基于尺寸处理图像
- 筛选并处理特定文件类型
- 对多个文件应用转换

## 使用示例

### 示例 0：解析 `magick` 可执行文件

**PowerShell (Windows):**
```powershell
# 优先选择 PATH 上的 ImageMagick
$magick = (Get-Command magick -ErrorAction SilentlyContinue)?.Source

# 备用：Program Files 下的常见安装路径
if (-not $magick) {
    $magick = Get-ChildItem "C:\\Program Files\\ImageMagick-*\\magick.exe" -ErrorAction SilentlyContinue |
        Select-Object -First 1 -ExpandProperty FullName
}

if (-not $magick) {
    throw "未找到 ImageMagick。请安装它并/或将 'magick' 添加到 PATH。"
}
```

**Bash (Linux/macOS):**
```bash
# 检查 PATH 上是否可用 magick
if ! command -v magick &> /dev/null; then
    echo "未找到 ImageMagick。请使用您的包管理器安装它："
    echo "  Ubuntu/Debian: sudo apt install imagemagick"
    echo "  macOS: brew install imagemagick"
    exit 1
fi
```

### 示例 1：获取图像尺寸

**PowerShell (Windows):**
```powershell
# 对于单个图像
& $magick identify -format "%wx%h" path/to/image.jpg

# 对于多个图像
Get-ChildItem "path/to/images/*" | ForEach-Object { 
    $dimensions = & $magick identify -format "%f: %wx%h`n" $_.FullName
    Write-Host $dimensions 
}
```

**Bash (Linux/macOS):**
```bash
# 对于单个图像
magick identify -format "%wx%h" path/to/image.jpg

# 对于多个图像
for img in path/to/images/*; do
    magick identify -format "%f: %wx%h\n" "$img"
done
```

### 示例 2：调整图像大小

**PowerShell (Windows):**
```powershell
# 调整单个图像大小
& $magick input.jpg -resize 427x240 output.jpg

# 批量调整图像大小
Get-ChildItem "path/to/images/*" | ForEach-Object { 
    & $magick $_.FullName -resize 427x240 "path/to/output/thumb_$($_.Name)"
}
```

**Bash (Linux/macOS):**
```bash
# 调整单个图像大小
magick input.jpg -resize 427x240 output.jpg

# 批量调整图像大小
for img in path/to/images/*; do
    filename=$(basename "$img")
    magick "$img" -resize 427x240 "path/to/output/thumb_$filename"
done
```

### 示例 3：获取详细图像信息

**PowerShell (Windows):**
```powershell
# 获取图像的详细信息
& $magick identify -verbose path/to/image.jpg
```

**Bash (Linux/macOS):**
```bash
# 获取图像的详细信息
magick identify -verbose path/to/image.jpg
```

### 示例 4：根据尺寸处理图像

**PowerShell (Windows):**
```powershell
Get-ChildItem "path/to/images/*" | ForEach-Object { 
    $dimensions = & $magick identify -format "%w,%h" $_.FullName
    if ($dimensions) {
        $width,$height = $dimensions -split ','
        if ([int]$width -eq 2560 -or [int]$height -eq 1440) {
            Write-Host "处理 $($_.Name)"
            & $magick $_.FullName -resize 427x240 "path/to/output/thumb_$($_.Name)"
        }
    }
}
```

**Bash (Linux/macOS):**
```bash
for img in path/to/images/*; do
    dimensions=$(magick identify -format "%w,%h" "$img")
    if [[ -n "$dimensions" ]]; then
        width=$(echo "$dimensions" | cut -d',' -f1)
        height=$(echo "$dimensions" | cut -d',' -f2)
        if [[ "$width" -eq 2560 || "$height" -eq 1440 ]]; then
            filename=$(basename "$img")
            echo "处理 $filename"
            magick "$img" -resize 427x240 "path/to/output/thumb_$filename"
        fi
    fi
done
```

## 指导原则

1. **始终使用引号包裹文件路径** - 对可能包含空格的文件路径使用引号
2. **使用 PowerShell 中的 `&` 运算符** - 在 PowerShell 中使用 `&` 调用 magick 可执行文件
3. **将路径存储在变量中 (PowerShell)** - 将 ImageMagick 路径分配给 `$magick` 以使代码更简洁
4. **使用循环** - 处理多个文件时，使用 `ForEach-Object` (PowerShell) 或 `for` 循环 (Bash)
5. **先验证尺寸** - 在处理前检查图像尺寸，以避免不必要的操作
6. **使用适当的调整大小标志** - 考虑使用 `!` 强制精确尺寸或 `^` 最小尺寸

## 常见模式

### PowerShell 模式

#### 模式：存储 ImageMagick 路径

```powershell
$magick = (Get-Command magick).Source
```

#### 模式：将尺寸作为变量获取

```powershell
$dimensions = & $magick identify -format "%w,%h" $_.FullName
$width,$height = $dimensions -split ','
```

#### 模式：条件处理

```powershell
if ([int]$width -gt 1920) {
    & $magick $_.FullName -resize 1920x1080 $outputPath
}
```

#### 模式：创建缩略图

```powershell
& $magick $_.FullName -resize 427x240 "thumbnails/thumb_$($_.Name)"
```

### Bash 模式

#### 模式：检查 ImageMagick 安装

```bash
command -v magick &> /dev/null || { echo "需要 ImageMagick"; exit 1; }
```

#### 模式：将尺寸作为变量获取

```bash
dimensions=$(magick identify -format "%w,%h" "$img")
width=$(echo "$dimensions" | cut -d',' -f1)
height=$(echo "$dimensions" | cut -d',' -f2)
```

#### 模式：条件处理

```bash
if [[ "$width" -gt 1920 ]]; then
    magick "$img" -resize 1920x1080 "$outputPath"
fi
```

#### 模式：创建缩略图

```bash
filename=$(basename "$img")
magick "$img" -resize 427x240 "thumbnails/thumb_$filename"
```

## 限制

- 大型批量操作可能内存密集
- 某些复杂操作可能需要额外的 ImageMagick 代表
- 在较旧的 Linux 系统上，使用 `convert` 而不是 `magick`（ImageMagick 6.x vs 7.x）
