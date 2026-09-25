# 应用图标生成工作流

## 概述
使用 AI 生成专业应用图标，并在 Expo 应用中为 iOS（支持 iOS 26 液态玻璃效果）和 Android 平台进行配置。

## 第 0 步：验证 SnapAI 设置（关键 - 首先执行此步骤）

[SnapAI](https://github.com/betomoedano/snapai) 是由 [Code with Beto](https://codewithbeto.dev) 团队开发的免费、开源的命令行工具。它使用用户的 API 密钥直接调用所选的图像提供方。密钥可以存储在本地 `~/.snapai/config.json` 中，或通过环境变量提供。SnapAI 不发送任何遥测数据，也没有后端服务器。

在尝试生成图标之前，请检查 SnapAI 是否已配置：

1. 检查 SnapAI 是否已配置：
```bash
npx snapai config --show
```

2. **如果配置检查失败或未显示 API 密钥：**
   - SnapAI 需要一个 OpenAI API 密钥来生成图标
   - 询问用户："SnapAI 需要一个 OpenAI API 密钥。您有吗，还是需要我帮助您设置？"

3. **如果用户有 API 密钥：**
   - 不要要求用户将密钥粘贴到聊天、源代码或您将运行的命令中
   - 请他们使用自己的终端在本地配置：
   ```bash
   npx snapai config --openai-api-key "<他们的-api-key>"
   ```
   - 或者，他们可以在其 shell 或密钥管理器中设置 `SNAPAI_API_KEY` 或 `OPENAI_API_KEY`
   - 在用户确认设置完成后，验证它而不打印密钥：
   ```bash
   npx snapai config --show
   ```

4. **如果用户需要获取 API 密钥：**
   - 指导他们前往：https://platform.openai.com/api-keys
   - 解释："您需要：
     1. 如果还没有，创建一个 OpenAI 账户
     2. 导航到 API 密钥部分
     3. 点击 '创建新的密钥'
     4. 复制密钥（以 'sk-' 开头）
     5. 在本地配置，不要在聊天中共享"

**重要提示：**
- SnapAI 是开源的。API 请求直接发送到所选提供方；该工具没有中间后端
- 该工具本身是免费的；提供方 API 的使用费用根据用户的提供方账户计费
- 如果 SnapAI 未配置，请不要继续进行图标生成
- 不要在聊天、命令输出、日志或提交的文件中暴露凭证

## 第 1 步：了解应用上下文
- 阅读 `app.json` 以了解应用名称和当前图标配置
- 如果上下文不明确，请询问用户应用是关于什么的
- 确定应用的主题、目的和目标美学

## 第 2 步：获取样式偏好
询问用户他们希望图标的样式。可用样式：
- `minimalism` - 干净的、受苹果启发的极简主义（最多 2-3 种颜色）
- `glassy` - 高级的玻璃美学，带有半透明元素
- `gradient` - 活力四射的渐变，受 Instagram 启发
- `neon` - 赛博朋克，带有未来主义发光效果
- `material` - Google Material Design
- `ios-classic` - 传统的 iOS，带有微妙的渐变
- `pixel` - 复古的 8 位/16 位游戏艺术风格
- `geometric` - 粗犷的、有棱角的构图

或者让用户提供一个自定义的样式描述。

## 第 3 步：使用 SnapAI 生成图标

**预检：** 在运行之前验证 SnapAI 是否已配置（见第 0 步）

生成一个 1024x1024 的图标，**背景透明**（对两个平台都至关重要）：

```bash
npx snapai icon --prompt "YOUR_PROMPT_HERE" --background transparent --output-format png --style STYLE_NAME
```

**重要标志：**
- `--background transparent` - 必须为 iOS 26 和 Android 适应图标
- `--output-format png` - 确保为 PNG 格式
- `--style` - 可选，增强视觉效果
- `--quality high` - 可选，用于最终生产图标

图标将保存为 `./assets/icon-[timestamp].png`

## 第 4 步：创建 iOS 26 .icon 文件夹结构

创建新的 iOS 26 液态玻璃图标格式：

1. 创建文件夹结构：
```bash
mkdir -p assets/app-icon.icon/Assets
```

2. 复制生成的 PNG：
```bash
cp assets/icon-[timestamp].png assets/app-icon.icon/Assets/icon.png
```

3. 创建 `assets/app-icon.icon/icon.json` 并使用此基本配置：
```json
{
  "fill": "automatic",
  "groups": [
    {
      "layers": [
        {
          "glass": false,
          "image-name": "icon.png",
          "name": "icon"
        }
      ],
      "shadow": {
        "kind": "neutral",
        "opacity": 0.5
      },
      "translucency": {
        "enabled": true,
        "value": 0.5
      }
    }
  ],
  "supported-platforms": {
    "circles": ["watchOS"],
    "squares": "shared"
  }
}
```

## 第 4.5 步：创建 Android 优化的适应图标

与 iOS 相比，Android 适应图标的可用安全区域较小（约画布的 66%）。SnapAI 生成的图标针对 iOS 安全区域进行了优化，这意味着它可能会在具有圆形或圆角矩形遮罩的 Android 设备上显示过大并被裁剪。

为确保您的图标在所有 Android 设备形状（圆形、圆角矩形、圆角方形）上正确显示，创建一个缩小版的版本：

**使用 ImageMagick（推荐）：**
```bash
# 将图标缩放到 66%，并使其在 1024x1024 的透明画布上居中
magick assets/icon-[timestamp].png \
  -resize 66% \
  -gravity center \
  -background transparent \
  -extent 1024x1024 \
  assets/android-icon.png
```

**替代方法 - 使用 sips + ImageMagick（macOS）：**
```bash
# 第 1 步：缩放到 66%（676x676）
sips -Z 676 assets/icon-[timestamp].png --out /tmp/icon-resized.png

# 第 2 步：创建最终的居中图像
magick -size 1024x1024 xc:transparent /tmp/icon-resized.png \
  -gravity center -composite assets/android-icon.png
```

**注意：** 如果未安装 ImageMagick，请使用以下命令安装：
```bash
brew install imagemagick
```

## 第 5 步：更新 app.json

更新 `app.json` 以配置两个平台的图标：

### 对于 iOS：
```json
{
  "expo": {
    "ios": {
      "icon": "./assets/app-icon.icon"
    }
  }
}
```

### 对于 Android：

使用在第 4.5 步中创建的 Android 优化的图标：

**选项 1：简单（带有纯色背景）**
```json
{
  "expo": {
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/android-icon.png",
        "backgroundColor": "#ffffff"
      }
    }
  }
}
```

**选项 2：全面（推荐）**
由于图标具有透明背景，您可以使用它填充 Android 适应图标的三个字段：

```json
{
  "expo": {
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/android-icon.png",
        "backgroundImage": "./assets/android-icon.png",
        "monochromeImage": "./assets/android-icon.png"
      }
    }
  }
}
```

**选项 2 的优点：**
- `foregroundImage` - 主要图标显示
- `backgroundImage` - 在 Android 8.0+ 上提供分层深度效果
- `monochromeImage` - 用于 Android 13+ 上的主题图标（系统自动重新着色）

**注意：**
- 对于选项 1，询问用户他们喜欢的 `backgroundColor`，或使用白色 (#ffffff) 作为默认值
- 对于选项 2，相同的透明 PNG 完美适用于所有三个字段
- 选项 2 提供了更好的 Android Material You 主题集成

## 第 6 步：验证和测试

1. 验证文件夹结构是否存在：
```bash
ls -la assets/app-icon.icon/
```

2. 验证 app.json 是否为有效的 JSON：
```bash
cat app.json | jq .
```

3. 告知用户使用以下命令测试应用：
```bash
npx expo prebuild --clean
npx expo run:ios
npx expo run:android
```

## 重要提示

- **透明背景至关重要** - 图标必须有透明背景，以支持 iOS 液态玻璃效果和 Android 适应图标
- **iOS 26 .icon 格式** - `.icon` 文件夹启用 iOS 26+ 上的液态玻璃效果
- **双资源工作流** - 此技能生成两个图标资源：
  - `icon-[timestamp].png` - 优化的主要图标，用于 iOS 安全区域（用于 `.icon` 文件夹）
  - `android-icon.png` - 缩放到 66% 并居中，用于 Android 适应图标安全区域
- **为什么有两个资源？** - iOS 和 Android 具有不同的安全区域。iOS 允许内容更靠近边缘（~80-85%），而 Android 适应图标由于激进遮罩（圆形、圆角矩形等）仅保证中心约 66% 可见
- **Android 适应图标灵活性** - `android-icon.png` 可用于 `foregroundImage`、`backgroundImage` 和 `monochromeImage` 字段
- **Material You 支持** - 使用 `monochromeImage` 可启用 Android 13+ 上的主题图标，以适应用户的颜色方案
- **文件命名** - `.icon` 文件夹名称可以自定义（例如，`app-icon.icon`、`myapp.icon`）

## 故障排除

### SnapAI 配置问题
- **"未找到 API 密钥"** - 询问用户在本地运行 `npx snapai config --openai-api-key "<key>"`，或设置 `SNAPAI_API_KEY` / `OPENAI_API_KEY`
- **"无效的 API 密钥"** - 询问用户在 OpenAI 账户中验证或轮换密钥，不要在聊天中共享
- **认证错误** - 检查 API 密钥是否已被吊销或在 platform.openai.com 上是否有足够的信用额度
- **命令未找到** - 确保使用 `npx snapai`（而不是 `snapai`）

### 图标显示问题
- 如果图标未显示，请验证 app.json 中的路径是否与实际文件夹位置匹配
- 确保在 .icon 文件夹中的 PNG 精确为 1024x1024
- 对于 Android，确保所有图像路径（`foregroundImage`、`backgroundImage`、`monochromeImage`）正确且指向现有文件
- 运行 `npx expo prebuild --clean` 以重新生成原生项目，并在图标更改后

### ImageMagick 问题（用于 Android 图标）
- **"convert: 命令未找到"** - 使用 `brew install imagemagick` 安装 ImageMagick
- **权限被拒绝** - 确保您有写入 assets 文件夹的权限
- **图标在 Android 上仍然被裁剪** - 尝试将缩放百分比从 66% 减少到 60%，以更激进地符合安全区域
