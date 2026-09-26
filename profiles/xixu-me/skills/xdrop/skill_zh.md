使用此技能目录中的捆绑脚本。

## 可用脚本

- `scripts/upload.mjs` — 将本地文件或目录上传到 Xdrop 服务器并打印分享链接
- `scripts/download.mjs` — 下载 Xdrop 分享链接，本地解密并保存文件

环境要求：

- Bun
- 本地文件系统访问权限
- 到目标 Xdrop 服务器的网络访问权限

## 上传

```bash
bun scripts/upload.mjs --server <xdrop-site-url> <文件或目录> [...]
```

在相关情况下优先使用以下标志：

- `--quiet`：抑制进度输出并保持 stdout 清洁
- `--json`：返回 `transferId`、`shareUrl` 和 `expiresAt`
- `--expires-in <秒数>`：选择一个受支持的过期时间
- `--api-url <url>`：覆盖默认的 `<服务器>/api/v1`
- `--name <值>`：设置传输显示名称
- `--concurrency <n>`：限制每个文件的并行上传数量

有用的示例：

```bash
bun scripts/upload.mjs --server http://localhost:8080 ./dist/report.pdf
bun scripts/upload.mjs --server http://localhost:8080 --quiet ./archive.zip
bun scripts/upload.mjs --server http://localhost:8080 --expires-in 600 --json ./notes.txt
```

如果用户需要验证，请上传一个小的临时文件，然后确认公共传输 API 或浏览器可以打开返回的链接。

## 下载

需要包含 `#k=...` 的完整分享链接。没有片段密钥，传输将无法解密。

```bash
bun scripts/download.mjs "<分享链接>"
```

在相关情况下优先使用以下标志：

- `--output <目录>`：选择目标目录
- `--quiet`：抑制进度输出并保持 stdout 清洁
- `--json`：返回 `transferId`、`outputRoot` 和保存的文件路径
- `--api-url <url>`：覆盖默认的 `<分享源>/api/v1`

有用的示例：

```bash
bun scripts/download.mjs "http://localhost:8080/t/abc123#k=..."
bun scripts/download.mjs --output ./downloads "http://localhost:8080/t/abc123#k=..."
bun scripts/download.mjs --quiet --json --output ./downloads "http://localhost:8080/t/abc123#k=..."
```

默认情况下，下载器将写入 `./xdrop-<transferId>` 并保留清单的相对路径。

## 注意事项

- 没有 `#k=...` 片段的下载链接无法解密。请要求完整的原始分享 URL。
- 当另一个命令或调用者需要捕获 stdout 时，始终使用 `--quiet`。否则进度日志将输出到 stderr，但最终结果仍然重要。

## 安全措施

- 当另一个命令或脚本需要捕获 stdout 时，优先使用 `--quiet`。
- 下载时保持完整的分享链接片段完整。
- 除非用户明确要求，否则不要使用手动临时命令绕过脚本内置的路径清理或传输清理行为。
