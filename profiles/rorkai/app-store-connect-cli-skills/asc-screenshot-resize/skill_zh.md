# asc 窗口截图调整大小

使用此技能为 App Store Connect 准备截图。不要依赖此技能中的硬编码尺寸表；CLI 拥有当前尺寸矩阵。

## 真实来源

始终首先从 `asc` 中发现当前接受的尺寸：

```bash
asc screenshots sizes --output table
asc screenshots sizes --all --output table
```

上传前的本地验证：

```bash
asc screenshots validate --path "./screenshots/iphone" --device-type "IPHONE_65" --output table
asc screenshots validate --path "./screenshots/ipad" --device-type "IPAD_PRO_3GEN_129" --output table
```

常见的当前设备类型锚点：

- `IPHONE_65` 用于常见的 6.5 英寸 iPhone 截图集。
- `IPAD_PRO_3GEN_129` 用于常见的 12.9/13 英寸 iPad 截图集。

针对其他显示类型（如 6.9 英寸 iPhone、Apple TV、Mac、Vision Pro、iMessage 或 Watch）时，运行 `asc screenshots sizes --all`。

## 工作流程

### 1. 清理文件名

macOS 截图可能包含隐藏的 Unicode 空格，这会导致工具因“不是有效文件”而失败。在批量处理前进行清理：

```bash
python3 -c "
import os
for f in os.listdir('.'):
    clean = f.replace('\u202f', ' ')
    if f != clean:
        os.rename(f, clean)
        print(f'Renamed: {clean}')
"
```

### 2. 检查尺寸和元数据

```bash
sips -g pixelWidth -g pixelHeight screenshot.png
sips -g hasAlpha -g space screenshot.png
```

App Store Connect 会拒绝带有 alpha 透明度的截图。通过 JPEG 转换去除 alpha：

```bash
sips -s format jpeg input.png --out /tmp/asc-screenshot-no-alpha.jpg
sips -s format png /tmp/asc-screenshot-no-alpha.jpg --out output.png
rm /tmp/asc-screenshot-no-alpha.jpg
```

批量去除 PNG 中的 alpha：

```bash
for f in *.png; do
  if sips -g hasAlpha "$f" | grep -q "yes"; then
    sips -s format jpeg "$f" --out /tmp/asc-screenshot-no-alpha.jpg
    sips -s format png /tmp/asc-screenshot-no-alpha.jpg --out "$f"
    rm /tmp/asc-screenshot-no-alpha.jpg
    echo "Stripped alpha: $f"
  fi
done
```

### 3. 仅在从 asc 选择目标后调整大小

从 `asc screenshots sizes --all` 中选择宽度和高度。`sips -z` 首先使用高度，然后使用宽度：

```bash
# 示例：横屏 IPHONE_65 1284 x 2778
sips -z 2778 1284 input.png --out output.png
```

批量调整到选定目标：

```bash
mkdir -p resized
for f in *.png; do
  sips -z 2778 1284 "$f" --out "resized/$f"
done
```

### 4. 使用 asc 验证输出

```bash
sips -g pixelWidth -g pixelHeight -g hasAlpha resized/*.png
asc screenshots validate --path "./resized" --device-type "IPHONE_65" --output table
```

### 5. 验证后上传

```bash
asc screenshots upload --version-localization "LOC_ID" --path "./resized" --device-type "IPHONE_65" --dry-run --output table
asc screenshots upload --version-localization "LOC_ID" --path "./resized" --device-type "IPHONE_65"
```

## 安全措施

- 将 `asc screenshots sizes --all` 视为权威；Apple 尺寸要求会变化。
- 除非用户接受视觉权衡，否则不要拉伸不兼容的宽高比的截图。
- 始终输出到单独的文件或目录以保留原始文件。
- 截图必须是 PNG 或 JPEG，且不能包含 alpha 透明度。
- 当需要时将 Display P3 或其他色彩空间转换为 sRGB：

```bash
sips -m "/System/Library/ColorSync/Profiles/sRGB IEC61966-2.1.icc" input.png --out output.png
```

- 上传前优先使用 `asc screenshots validate` 而不是视觉检查。
