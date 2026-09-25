# 小红书封面生成器

该技能根据用户提供的主题生成小红书风格的封面图片。

## 使用方法

当用户请求小红书封面图片时：

1. 如果主题不明确，请与用户确认
2. 检查API密钥（CANGHE_API_KEY环境变量或询问用户提供）
3. 使用主题运行生成脚本
4. 图片将保存到当前工作目录，文件名格式为：`xiaohongshu-cover-{timestamp}.png`

## 运行脚本

脚本位于`scripts/handler.ts`，需要以下参数：
- 主题（必填）：封面图片的主题
- API密钥（必填）：通过环境变量`CANGHE_API_KEY`或作为参数传递

执行方式：
```bash
cd ~/.codebuddy/skills/xiaohongshu-cover-generator
npx tsx scripts/handler.ts "<主题>" "<api-key-optional>"
```

或使用环境变量：
```bash
cd ~/.codebuddy/skills/xiaohongshu-cover-generator
CANGHE_API_KEY="your-api-key" npx tsx scripts/handler.ts "<主题>"
```

## API密钥

用户需要从 https://api.canghe.ai/ 获取有效的API密钥。

如果API密钥缺失或无效，请向用户提供清晰的获取指引。

## 输出

生成的图片将保存到**技能被调用的目录**（当前工作目录），而不是技能的目录。文件名格式为`xiaohongshu-cover-{timestamp}.png`，其中timestamp为毫秒级时间戳。

## 风格规范

生成的图片遵循以下规范：
- 纵向比例：3:4（垂直，适合移动端）
- 风格：简洁、精致、年轻化美学
- 自动去除水印和logo
- 高质量输出，适合移动端浏览
- 文字清晰易读，尺寸适当
