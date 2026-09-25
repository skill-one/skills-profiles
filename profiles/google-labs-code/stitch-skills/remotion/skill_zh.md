# Stitch to Remotion 走马灯视频教程

您是一位专注于从应用程序设计创建引人入胜的走马灯视频的视频制作专家。您结合 Stitch 的屏幕检索功能与 Remotion 的程序化视频生成技术，制作出流畅、专业的演示视频。

## 概述

这项技能使您能够创建展示应用程序屏幕的走马灯视频，具有专业的过渡效果、缩放效果和上下文文本叠加。工作流程从 Stitch 项目中检索屏幕，并将它们编排成一个 Remotion 视频合成。

## 前置条件

**必需:**
- Stitch MCP 服务器的访问权限
- Remotion MCP 服务器的访问权限（或 Remotion CLI）
- 已安装 Node.js 和 npm
- 一个具有设计屏幕的 Stitch 项目

**推荐:**
- 熟悉 Remotion 的视频功能
- 了解 React 组件（Remotion 使用 React）

## 检索和网络

### 第 1 步：发现可用的 MCP 服务器

运行 `list_tools` 来识别可用的 MCP 服务器及其前缀：
- **Stitch MCP**：查找 `stitch:` 或 `mcp_stitch:` 前缀
- **Remotion MCP**：查找 `remotion:` 或 `mcp_remotion:` 前缀

### 第 2 步：检索 Stitch 项目信息

1. **项目查找**（如果未提供项目 ID）：
   - 调用 `[stitch_prefix]:list_projects` 并使用 `filter: "view=owned"`
   - 通过标题（例如，“计算器应用程序”）识别目标项目
   - 从 `name` 字段中提取项目 ID（例如，`projects/13534454087919359824`）

2. **屏幕检索**：
   - 使用项目 ID（仅数字）调用 `[stitch_prefix]:list_screens`
   - 查看屏幕标题以识别所有用于走马灯的屏幕
   - 从每个屏幕的 `name` 字段中提取屏幕 ID

3. **屏幕元数据获取**：
   对于每个屏幕：
   - 使用 `projectId` 和 `screenId` 调用 `[stitch_prefix]:get_screen`
   - 检索：
     - `screenshot.downloadUrl` — 视频的视觉资源
     - `htmlCode.downloadUrl` — 可选：用于提取文本/内容
     - `width`, `height` — 屏幕尺寸以进行适当缩放
     - 屏幕标题和描述用于文本叠加

4. **资源下载**：
   - 使用 `web_fetch` 或 `Bash` 与 `curl` 下载截图
   - 保存到暂存目录：`assets/screens/{screen-name}.png`
   - 按照预期的走马灯流程组织资源

### 第 3 步：设置 Remotion 项目

1. **检查现有 Remotion 项目**：
   - 查找 `remotion.config.ts` 或带有 Remotion 依赖的 `package.json`
   - 如果存在，使用现有的项目结构

2. **创建新的 Remotion 项目**（如果需要）：
   ```bash
   npm create video@latest -- --blank
   ```
   - 选择 TypeScript 模板
   - 在专用的 `video/` 目录中设置

3. **安装依赖项**：
   ```bash
   cd video
   npm install @remotion/transitions @remotion/animated-emoji
   ```

## 视频合成策略

### 架构

创建一个模块化的 Remotion 合成，包含以下组件：

1. **`ScreenSlide.tsx`** — 单个屏幕显示组件
   - Props: `imageSrc`, `title`, `description`, `width`, `height`
   - 功能：缩放动画、淡入淡出过渡
   - 持续时间：可配置（每个屏幕默认 3-5 秒）

2. **`WalkthroughComposition.tsx`** — 主视频合成
   - 序列多个 `ScreenSlide` 组件
   - 处理屏幕之间的过渡
   - 添加文本叠加和注释

3. **`config.ts`** — 视频配置
   - 帧率（默认：30 fps）
   - 视频尺寸（匹配 Stitch 屏幕尺寸或适当缩放）
   - 总持续时间计算

### 过渡效果

使用 Remotion 的 `@remotion/transitions` 实现专业效果：

- **淡入淡出**：屏幕之间的平滑交叉淡入淡出
  ```tsx
  import {fade} from '@remotion/transitions/fade';
  ```

- **滑动**：方向性滑动过渡
  ```tsx
  import {slide} from '@remotion/transitions/slide';
  ```

- **缩放**：用于强调的缩放效果
  - 使用 `spring()` 动画实现平滑缩放
  - 应用于重要的 UI 元素

### 文本叠加

使用 Remotion 的文本渲染添加上下文信息：

1. **屏幕标题**：在每帧的顶部或底部显示
2. **功能标注**：使用动画指针突出显示特定 UI 元素
3. **描述**：为每个屏幕淡入描述性文本
4. **进度指示器**：显示走马灯中的当前屏幕位置

## 执行步骤

### 第 1 步：收集屏幕资源

1. 确定目标 Stitch 项目
2. 列出项目中的所有屏幕
3. 下载每个屏幕的截图
4. 按照走马灯流程组织
5. 创建一个清单文件 (`screens.json`)：

```json
{
  "projectName": "Calculator App",
  "screens": [
    {
      "id": "1",
      "title": "Home Screen",
      "description": "主计算器界面，带有数字键盘",
      "imagePath": "assets/screens/home.png",
      "width": 1200,
      "height": 800,
      "duration": 4
    },
    {
      "id": "2",
      "title": "History View",
      "description": "先前计算的历史视图",
      "imagePath": "assets/screens/history.png",
      "width": 1200,
      "height": 800,
      "duration": 3
    }
  ]
}
```

### 第 2 步：生成 Remotion 组件

遵循 Remotion 最佳实践创建视频组件：

1. **创建 `ScreenSlide.tsx`**：
   - 使用 `useCurrentFrame()` 和 `spring()` 实现动画
   - 实现缩放和淡入淡出效果
   - 添加具有适当时间的文本叠加

2. **创建 `WalkthroughComposition.tsx`**：
   - 导入屏幕清单
   - 使用 `<Sequence>` 组件序列屏幕
   - 应用屏幕之间的过渡
   - 计算适当的时间和偏移量

3. **更新 `remotion.config.ts`**：
   - 设置合成 ID
   - 配置视频尺寸
   - 设置帧率和持续时间

**参考资源:**
- 使用 `resources/screen-slide-template.tsx` 作为起点
- 按照 `resources/composition-checklist.md` 完整性检查
- 查看 `examples/` 目录中的示例

### 第 3 步：预览和优化

1. **启动 Remotion Studio**：
   ```bash
   npm run dev
   ```
   - 打开基于浏览器的预览
   - 允许实时编辑和优化

2. **调整时间**：
   - 确保每个屏幕具有适当的显示持续时间
   - 验证过渡是否平滑
   - 检查文本叠加时间

3. **微调动画**：
   - 调整 `spring()` 配置以实现缩放效果
   - 修改过渡的缓动函数
   - 确保文本始终可读

### 第 4 步：渲染视频

1. **使用 Remotion CLI 渲染**：
   ```bash
   npx remotion render WalkthroughComposition output.mp4
   ```

2. **替代方案：使用 Remotion MCP**（如果可用）：
   - 调用 `[remotion_prefix]:render` 并提供合成详细信息
   - 指定输出格式（MP4、WebM 等）

3. **优化选项**：
   - 设置质量级别 (`--quality`)
   - 配置编解码器 (`--codec h264` 或 `h265`)
   - 启用并行渲染 (`--concurrency`)

## 高级功能

### 交互热点

突出显示可点击元素或重要功能：

```tsx
import {interpolate, useCurrentFrame} from 'remotion';

const Hotspot = ({x, y, label}) => {
  const frame = useCurrentFrame();
  const scale = spring({
    frame,
    fps: 30,
    config: {damping: 10, stiffness: 100}
  });
  
  return (
    <div style={{
      position: 'absolute',
      left: x,
      top: y,
      transform: `scale(${scale})`
    }}>
      <div className="pulse-ring" />
      <span>{label}</span>
    </div>
  );
};
```

### 配音集成

为走马灯添加旁白：

1. 从屏幕描述生成旁白脚本
2. 使用文本转语音或录制音频
3. 使用 `<Audio>` 组件导入 Remotion 中的音频
4. 同步屏幕时间与旁白节奏

### 动态文本提取

从 Stitch HTML 代码中提取文本以自动注释：

1. 为每个屏幕下载 `htmlCode.downloadUrl`
2. 解析 HTML 以提取关键文本元素（标题、按钮、标签）
3. 为重要 UI 元素生成自动标注
4. 作为定时文本叠加添加到合成中

## 文件结构

```
project/
├── video/                      # Remotion 项目目录
│   ├── src/
│   │   ├── WalkthroughComposition.tsx
│   │   ├── ScreenSlide.tsx
│   │   ├── components/
│   │   │   ├── Hotspot.tsx
│   │   │   └── TextOverlay.tsx
│   │   └── Root.tsx
│   ├── public/
│   │   └── assets/
│   │       └── screens/        # 下载的 Stitch 截图
│   │           ├── home.png
│   │           └── history.png
│   ├── remotion.config.ts
│   └── package.json
├── screens.json                # 屏幕清单
└── output.mp4                  # 渲染的视频
```

## 与 Remotion 技能的集成

Remotion 维护自己的 Agent 技能，这些技能定义了最佳实践。查看这些以获取高级技术：

- **仓库**：https://github.com/remotion-dev/remotion/tree/main/packages/skills
- **安装**：`npx skills add remotion-dev/skills`

要利用的关键 Remotion 技能：
- 动画时间和缓动
- 合成架构模式
- 性能优化
- 音频同步

## 常见模式

### 模式 1：简单幻灯片

基本的走马灯，带有淡入淡出过渡：
- 每个屏幕 3-5 秒
- 交叉淡入淡出过渡
- 底部文本叠加显示屏幕标题
- 顶部显示进度条

### 模式 2：功能高亮

专注于特定 UI 元素：
- 缩放到特定区域
- 使用动画圆圈/箭头指向功能
- 关键交互的慢动作强调
- 并列显示前后对比

### 模式 3：用户流程

显示逐步的用户旅程：
- 带有方向性滑动的顺序屏幕流程
- 带有编号步骤的叠加
- 高亮用户操作（点击、轻点）
- 使用动画路径连接屏幕

## 故障排除

| 问题 | 解决方案 |
|-------|----------|
| **模糊截图** | 确保下载的图像为全分辨率；检查 `screenshot.downloadUrl` 质量设置 |
| **文本错位** | 验证屏幕尺寸与合成尺寸匹配；根据实际屏幕尺寸调整文本位置 |
| **动画卡顿** | 将帧率提高到 60fps；使用适当的 `spring()` 配置和阻尼 |
| **Remotion 构建失败** | 检查 Node 版本兼容性；确保所有依赖项已安装；查看 Remotion 文档 |
| **时间感觉不对** | 在清单中调整每个屏幕的持续时间；在 Remotion Studio 预览；测试实际用户 |

## 最佳实践

1. **保持宽高比**：使用实际 Stitch 屏幕尺寸或按比例缩放
2. **保持一致的时间**：除非强调特定屏幕，否则保持屏幕显示持续时间一致
3. **可读文本**：确保足够的对比度；使用适当的字体大小；避免杂乱的叠加
4. **平滑过渡**：使用 `spring` 动画实现自然运动；避免突兀的切换
5. **彻底预览**：始终在 Remotion Studio 中预览后再最终渲染
6. **优化资源**：适当压缩图像；使用高效格式（PNG 用于 UI，JPG 用于照片）

## 示例用法

**用户提示:**
```
查找我的 Stitch 项目 "Calculator App" 中的屏幕，并创建一个 remotion 视频 
展示屏幕的走马灯。
```

**代理工作流程:**
1. 列出 Stitch 项目 → 找到 "Calculator App" → 提取项目 ID
2. 列出项目中的屏幕 → 识别所有屏幕（主页、历史记录、设置）
3. 下载每个屏幕的截图 → 保存到 `assets/screens/`
4. 创建 `screens.json` 清单，包含屏幕元数据
5. 生成 Remotion 组件（`ScreenSlide.tsx`，`WalkthroughComposition.tsx`）
6. 在 Remotion Studio 中预览 → 优化时间和过渡
7. 渲染最终视频 → `calculator-walkthrough.mp4`
8. 使用视频预览链接报告完成

## 成功技巧

- **从简单开始**：在添加复杂动画之前，先使用基本淡入淡出
- **遵循 Remotion 模式**：利用 Remotion 的官方技能和文档
- **使用清单文件**：将屏幕数据组织在 JSON 中以便更新
- **频繁预览**：使用 Remotion Studio 早期发现问题
- **考虑可访问性**：添加字幕；确保文本可读；使用清晰的视觉效果
- **针对平台优化**：匹配视频尺寸以适应目标平台（YouTube、社交媒体等）

## 参考

- **Stitch 文档**：https://stitch.withgoogle.com/docs/
- **Remotion 文档**：https://www.remotion.dev/docs/
- **Remotion 技能**：https://www.remotion.dev/docs/ai/skills
- **Remotion MCP**：https://www.remotion.dev/docs/ai/mcp
- **Remotion 过渡**：https://www.remotion.dev/docs/transitions
