# Defuddle

使用 Defuddle CLI 从网页中提取干净易读的内容。对于标准网页，优先于 WebFetch — 它会移除导航、广告和杂乱信息，减少 token 使用。

未安装：`npm install -g defuddle`

## 使用方法

始终使用 `--md` 获取 markdown 输出：

```bash
defuddle parse <url> --md
```

保存到文件：

```bash
defuddle parse <url> --md -o content.md
```

提取特定元数据：

```bash
defuddle parse <url> -p title
defuddle parse <url> -p description
defuddle parse <url> -p domain
```

## 输出格式

| 标志 | 格式 |
|------|------|
| `--md` | Markdown（默认选择） |
| `--json` | 同时包含 HTML 和 markdown 的 JSON |
| (无) | HTML |
| `-p <name>` | 特定元数据属性 |
