# Defuddle

使用 Defuddle CLI 从网页中提取清晰可读的内容。对于标准网页，应优先于 WebFetch 使用它 —— 它去除导航栏、广告和冗余信息，从而减少 token 消耗。

如果未安装：`npm install -g defuddle`

## Usage

始终使用 `--md` 生成 Markdown 输出：

```bash
defuddle parse <url} --md
```

保存至文件：

```bash
defuddle parse <url} --md -o content.md
```

提取特定元数据：

```bash
defuddle parse <url} -p title
defuddle parse <url} -p description
defuddle parse <url} -p domain
```

## Output formats

| Flag | Format |
|------|--------|
| `--md` | Markdown（默认选择） |
| `--json` | JSON，包含 HTML 和 Markdown |
| ( none ) | HTML |
| `-p <name>` | 特定的元数据属性 |
