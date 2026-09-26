# Awwwards Landing Page

一个令人惊叹的Portfolio着陆页，使用Locomotive Scroll、GSAP和Framer Motion实现平滑的滚动动画。

## 技术栈

- **框架**: Next.js
- **动画**: Locomotive Scroll、GSAP、Framer Motion
- **包管理器**: pnpm或npm
- **开发端口**: 3000

## 设置

### 1. 克隆模板

```bash
git clone --depth 1 https://github.com/Eng0AI/awwwards-landing-page-template.git .
```

如果目录不为空：

```bash
git clone --depth 1 https://github.com/Eng0AI/awwwards-landing-page-template.git _temp_template
mv _temp_template/* _temp_template/.* . 2>/dev/null || true
rm -rf _temp_template
```

### 2. 删除Git历史记录（可选）

```bash
rm -rf .git
git init
```

### 3. 安装依赖

```bash
npm install
```

## 构建

```bash
npm run build
```

## 部署

> **关键**: 对于Vercel，你必须使用`vercel build --prod`然后`vercel deploy --prebuilt --prod`。绝对不要直接使用`vercel --prod`。

### Vercel（推荐）

```bash
vercel pull --yes -t $VERCEL_TOKEN
vercel build --prod -t $VERCEL_TOKEN
vercel deploy --prebuilt --prod --yes -t $VERCEL_TOKEN
```

### Netlify

```bash
netlify deploy --prod
```

## 开发

```bash
npm run dev
```

将在 http://localhost:3000 打开

## 注意事项

- 静态Next.js站点 - 无需环境变量
- 不要在虚拟机环境中运行`npm run dev`
