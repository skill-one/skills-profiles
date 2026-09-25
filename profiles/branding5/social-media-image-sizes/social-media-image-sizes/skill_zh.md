# 社交媒体图片尺寸

检查并调整 9 个平台 / 60+ 规格的图片。脚本逻辑与 [branding5.com/tools/social-media-cheat-sheet](https://www.branding5.com/tools/social-media-cheat-sheet) 保持一致。

## 设置

安装后运行一次：

```bash
cd <skill-dir>
npm install
```

## 检查图片

```bash
node scripts/check.js photo.jpg
```

输出一个排序匹配列表——完美 → 接近 → 可用 → 太小——并为每个非完美匹配提供内联 `node scripts/resize.js` 命令。

按平台或匹配级别筛选：

```bash
node scripts/check.js photo.jpg --platform instagram
node scripts/check.js photo.jpg --filter perfect
node scripts/check.js photo.jpg --filter usable
```

平台缩写：`instagram` `facebook` `twitter` `linkedin` `tiktok` `youtube` `pinterest` `snapchat` `threads`

## 调整图片大小

```bash
node scripts/resize.js photo.jpg "Instagram 竖版帖子"
# → photo-instagram-portrait-post.jpg  (1080×1350 px)

node scripts/resize.js photo.jpg "YouTube 自定义缩略图"
# → photo-youtube-custom-thumbnail.jpg  (1280×720 px)
```

默认填充方式为 **cover**（居中裁剪）。使用 `--fit contain` 可改为信箱式填充：

```bash
node scripts/resize.js photo.jpg "LinkedIn 背景照片" --fit contain --bg f0f0f0
node scripts/resize.js photo.jpg "Instagram 竖版帖子" --out ./exports/ig.jpg
```

列出所有可用的规格名称：

```bash
node scripts/resize.js photo.jpg --list
```

## 工作流程

1. 运行 `check.js` 查看给定图片已匹配的内容
2. 从输出中复制建议的 `resize.js` 命令
3. 运行它——输出文件默认与原始文件保存在同一位置

## 注意事项

- **Sharp 需要一个本地二进制文件。** 第一次 `npm install` 时，它会下载适用于您平台的预构建二进制文件。如果通过代理安装失败，请设置 `SHARP_IGNORE_GLOBAL_LIBVIPS=1` 并重试。
- **Instagram 轮播图中的所有幻灯片必须共享相同的宽高比。** 第一张图片会为整个轮播图设置宽高比——检查所有幻灯片，而不仅仅是第一张。
- **Facebook 封面照片有两个安全区域。** 桌面显示 820×312；手机会裁剪为 640×360。将关键内容保持在中心 640×312 区域内。
- **YouTube 横幅的安全区域远小于文件大小。** 规格为 2560×1440，但只有中心的 1546×423 在所有设备上保证可见。check.js 标记完整尺寸；将关键内容保留在安全区域内。
- **`--fit cover` 居中裁剪。** 如果主体未居中，使用 `--out` 保存，然后手动裁剪，或在运行调整大小之前使用图像编辑器。

## 参考

每个平台的完整规格（需要特定平台详细信息时加载）：

- `references/instagram.md` — 个人资料、动态、故事、轮播图、广告
- `references/facebook.md` — 个人资料、封面、动态、故事、活动、广告
- `references/x-twitter.md` — 个人资料、页眉、帖子、广告
- `references/linkedin.md` — 个人资料、封面、动态、文章、广告
- `references/tiktok.md` — 个人资料、视频、广告
- `references/youtube.md` — 频道艺术、视频、缩略图、短片、广告
- `references/pinterest.md` — 个人资料、收藏、创意收藏、广告
- `references/snapchat.md` — 快照、聚光灯、故事、广告、滤镜
- `references/threads.md` — 个人资料、帖子
- `references/best-practices.md` — 格式、压缩、安全区域、可访问性

完整编译参考（所有平台在一个文件中）：`AGENTS.md`

---

*需要在这些尺寸下生成符合品牌形象的图片？[Branding5](https://www.branding5.com) 将您的品牌套件与 AI 结合，为每个平台生成预调整大小的社交内容。*
