# PDFtk Server

PDFtk Server 是一款用于处理 PDF 文档的命令行工具。它可以合并、拆分、旋转、加密、解密、添加水印、盖章、填写表单、提取元数据，以及以多种方式操作 PDF 文件。

## 使用此技能的场景

- 将多个 PDF 文件合并成一个
- 将 PDF 拆分成单独的页面
- 旋转 PDF 页面
- 加密或解密 PDF 文件
- 从 FDF/XFDF 数据中填写 PDF 表单字段
- 应用背景水印或前景印章
- 提取 PDF 元数据、书签或表单字段信息
- 修复损坏的 PDF 文件
- 附加或提取 PDF 中嵌入的文件
- 从 PDF 中删除特定页面
- 合并单独扫描的奇偶页
- 压缩或解压缩 PDF 页面流

## 前置条件

- 系统上必须安装 PDFtk Server
  - **Windows**: `winget install --id PDFLabs.PDFtk.Server`
  - **macOS**: `brew install pdftk-java`
  - **Linux (Debian/Ubuntu)**: `sudo apt-get install pdftk`
  - **Linux (Red Hat/Fedora)**: `sudo dnf install pdftk`
- 可以访问终端或命令提示符
- 通过运行 `pdftk --version` 验证安装

## 分步工作流程

### 合并多个 PDF

```bash
pdftk file1.pdf file2.pdf cat output merged.pdf
```

使用句柄进行更多控制：

```bash
pdftk A=file1.pdf B=file2.pdf cat A B output merged.pdf
```

### 将 PDF 拆分成单独的页面

```bash
pdftk input.pdf burst
```

### 提取特定页面

提取第 1-5 页和第 10-15 页：

```bash
pdftk input.pdf cat 1-5 10-15 output extracted.pdf
```

### 删除特定页面

删除第 13 页：

```bash
pdftk input.pdf cat 1-12 14-end output output.pdf
```

### 旋转页面

将所有页面顺时针旋转 90 度：

```bash
pdftk input.pdf cat 1-endeast output rotated.pdf
```

### 加密 PDF

设置所有者密码和用户密码，使用 128 位加密（默认）：

```bash
pdftk input.pdf output secured.pdf owner_pw mypassword user_pw userpass
```

### 解密 PDF

使用已知密码移除加密：

```bash
pdftk secured.pdf input_pw mypassword output unsecured.pdf
```

### 填写 PDF 表单

从 FDF 文件中填充表单字段，并扁平化以防止进一步编辑：

```bash
pdftk form.pdf fill_form data.fdf output filled.pdf flatten
```

### 应用背景水印

将单页 PDF 放在输入的每一页后面（输入应具有透明度）：

```bash
pdftk input.pdf background watermark.pdf output watermarked.pdf
```

### 盖章

将单页 PDF 放在输入的每一页上面：

```bash
pdftk input.pdf stamp overlay.pdf output stamped.pdf
```

### 提取元数据

导出书签、页面指标和文档信息：

```bash
pdftk input.pdf dump_data output metadata.txt
```

### 修复损坏的 PDF

将损坏的 PDF 传递给 pdftk 以尝试自动修复：

```bash
pdftk broken.pdf output fixed.pdf
```

### 合并扫描页面

交错单独扫描的奇数页和偶数页：

```bash
pdftk A=even.pdf B=odd.pdf shuffle A B output collated.pdf
```

## 故障排除

| 问题 | 解决方案 |
|-------|----------|
| `pdftk` 命令未找到 | 验证安装；检查 pdftk 是否在系统 PATH 中 |
| 无法解密 PDF | 确保您通过 `input_pw` 提供了正确的所有者或用户密码 |
| 输出文件为空或损坏 | 检查输入文件完整性；首先尝试运行 `pdftk input.pdf output repaired.pdf` |
| 填写后表单字段不可见 | 使用 `flatten` 标志将字段合并到页面内容中 |
| 水印未显示 | 确保输入 PDF 具有透明区域；使用 `stamp` 进行不透明覆盖 |
| 权限错误 | 检查输入和输出路径的文件权限 |

## 参考

`references/` 文件夹中的捆绑参考文档：

- [pdftk-man-page.md](references/pdftk-man-page.md) - 包含所有操作、选项和语法的完整手册参考
- [pdftk-cli-examples.md](references/pdftk-cli-examples.md) - 常见任务的实用命令行示例
- [download.md](references/download.md) - 所有平台的安装和下载说明
- [pdftk-server-license.md](references/pdftk-server-license.md) - PDFtk Server 许可信息
- [third-party-materials.md](references/third-party-materials.md) - 第三方库许可证
