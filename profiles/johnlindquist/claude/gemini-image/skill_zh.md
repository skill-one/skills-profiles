# Gemini 图像分析

使用 Gemini Pro 的视觉能力分析图像。

## 前置条件

```bash
pip install google-generativeai
export GEMINI_API_KEY=your_api_key
```

## 命令行参考

### 基本图像分析

```bash
# 分析图像
gemini -m pro -f /path/to/image.png "详细描述此图像"

# 带有特定问题
gemini -m pro -f screenshot.png "显示什么错误信息？"

# 多个图像
gemini -m pro -f image1.png -f image2.png "比较这两张图像"
```

## 分析操作

### 一般描述

```bash
gemini -m pro -f image.png "全面描述此图像：
1. 主要主题/内容
2. 颜色和构图
3. 可见文本（如有）
4. 上下文和目的
5. 值得注意的细节"
```

### 提取文本（OCR）

```bash
gemini -m pro -f screenshot.png "从图像中提取所有文本。
以纯文本格式显示，尽可能保留布局。
包括按钮、标签或 UI 元素中的任何文本。"
```

### 截图中的代码

```bash
gemini -m pro -f code-screenshot.png "从此截图中提取代码。
以正确缩进的格式提供代码。
注意任何不清晰或部分可见的部分。"
```

### UI 分析

```bash
gemini -m pro -f ui-screenshot.png "分析此 UI：
1. 这是哪个应用程序/网站？
2. 显示的是哪个页面/屏幕？
3. 主要 UI 元素及其目的
4. 可用的用户流程/操作
5. 任何 UX 问题或建议"
```

### 错误分析

```bash
gemini -m pro -f error-screenshot.png "分析此错误：
1. 显示什么错误？
2. 可能的原因是什么？
3. 如何修复？
4. 是否有任何可见的相关信息？"
```

### 图表理解

```bash
gemini -m pro -f diagram.png "解释此图表：
1. 这是什么类型的图表？
2. 主要组件及其关系
3. 数据/流程
4. 关键要点"
```

## 特定用例

### 调试截图

```bash
gemini -m pro -f debug-screen.png "我正在调试问题。从这张截图：
1. 当前状态是什么？
2. 可见什么错误或警告？
3. 我应该查看什么？
4. 建议的下一步操作"
```

### 比较前后

```bash
gemini -m pro -f before.png -f after.png "比较这些前后图像：
1. 有什么变化？
2. 这是改进吗？
3. '后'版本中有任何问题？
4. 有什么缺失？"
```

### 设计反馈

```bash
gemini -m pro -f design.png "提供设计反馈：
1. 视觉层次结构
2. 颜色使用
3. 字体
4. 间距和对齐
5. 可访问性问题
6. 改进建议"
```

### 数据提取

```bash
gemini -m pro -f chart.png "从此图表中提取数据：
1. 图表类型
2. 数据系列和值
3. 轴标签和范围
4. 关键趋势或见解
5. 如果可能，以结构化数据输出"
```

### 表单分析

```bash
gemini -m pro -f form.png "分析此表单：
1. 表单目的
2. 字段及其类型
3. 必填项与可选项
4. 可见验证规则
5. UX 建议"
```

## 工作流模式

### 截图到问题

```bash
# 捕获截图（macOS）
screencapture -i /tmp/bug.png

# 分析并格式化为问题
gemini -m pro -f /tmp/bug.png "从这张截图创建问题报告：

## 摘要
[一句话描述]

## 复现步骤
[根据截图推断]

## 预期行为
[应该发生什么]

## 实际行为
[截图显示的内容]

## 环境
[任何可见的系统信息]"
```

### UI 到代码

```bash
gemini -m pro -f ui-design.png "生成重新创建此 UI 的 React 组件代码：
- 使用 Tailwind CSS 进行样式设计
- 使其响应式
- 包括正确的 TypeScript 类型
- 添加适当的可访问性属性"
```

### 文档

```bash
gemini -m pro -f app-screen.png "为此屏幕编写用户文档：
- 此屏幕的用途
- 如何使用每个功能
- 常见任务
- 提示和笔记"
```

## 支持的图像类型

- PNG、JPEG、GIF、WebP
- 截图
- 照片
- 图表和图表
- UI 模板
- 代码片段
- 文档

## 最佳实践

1. **使用清晰的图像** - 质量越高 = 分析越好
2. **裁剪到相关区域** - 移除不必要的上下文
3. **提出具体问题** - 模糊的提示会得到模糊的答案
4. **提供上下文** - 告诉 Gemini 你在寻找什么
5. **验证提取的文本** - OCR 并非完美
6. **多个角度** - 使用多个图像分析复杂主题
