# OpenClaw 备份技能

使用 Claude Code 对 OpenClaw 代理工作区文件进行自动加密备份和恢复。

## 概述

此技能提供三个核心功能：

1. **上传备份** - 使用自动生成的密码加密并上传工作区文件到 soul-upload.com
2. **下载备份** - 使用存储的密码从 soul-upload.com 下载并解密备份
3. **删除备份** - 从远程存储删除备份

所有备份都使用 **AES-256-CBC 加密**（通过 openssl）和 **自动生成的随机密码**。每个备份都有一个唯一的密码，该密码存储在恢复文件中。

## 系统要求

在执行备份操作之前，请确保已安装以下工具：

- **Python 3.7+**（脚本运行环境）
- **requests 库**（`pip install requests`）
- **tar**（文件归档）
- **openssl**（加密/解密）
- **curl**（HTTP 请求，系统内置）

## 默认备份文件

如果用户未指定文件，则默认备份以下 OpenClaw 工作区文件：

- `SOUL.md` - 代理核心身份和目标
- `MEMORY.md` - 代理记忆和上下文
- `IDENTITY.md` - 代理身份定义
- `AGENTS.md` - 代理配置
- `TOOLS.md` - 工具配置

## 工作流程 1：上传备份

### 触发场景

当用户请求备份工作区文件时执行：

- "备份我的工作区文件"
- "将 SOUL.md 上传到 soul-upload"
- "创建我的代理文件的加密备份"
- "备份 SOUL.md 和 MEMORY.md"

### 执行步骤

1. **收集文件列表**
   - 如果用户指定了文件，则使用用户指定的文件
   - 否则，使用默认列表：`SOUL.md MEMORY.md IDENTITY.md AGENTS.md TOOLS.md`
   - 使用 Read 工具验证文件是否存在

2. **执行备份脚本**（密码自动生成）
   - 定位脚本路径（通常在技能目录中的 `scripts/backup.py`）
   - 执行命令时不带 `--password` 参数（脚本将自动生成）：
     ```bash
     python3 scripts/backup.py upload \
       --files "SOUL.md MEMORY.md IDENTITY.md"
     ```
   - 脚本自动生成一个 32 个字符的随机密码
   - 捕获 stdout（JSON 响应）和 stderr（包括生成的密码的进度信息）

3. **处理响应**
   - 成功时，脚本输出 JSON：
     ```json
     {
       "backupId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
       "downloadUrl": "https://soul-upload.com/backup/...",
       "sizeBytes": 12345,
       "sha256": "abc123...",
       "password": "auto-generated-32-char-random-password"
     }
     ```
   - 解析 JSON 并提取包括自动生成的密码在内的关键信息

4. **保存恢复信息**
   - 使用 Write 工具创建/更新 `.openclaw-backup-recovery.txt`
   - **关键**：在恢复文件中包含自动生成的密码
   - 格式：
     ```
     Backup ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
     Password: auto-generated-32-char-random-password
     Download URL: https://soul-upload.com/backup/...
     Created: 2024-01-15 10:30:00 UTC
     Size: 12.05 KB
     SHA256: abc123...
     Files: SOUL.md, MEMORY.md, IDENTITY.md
     ---
     ```
   - 追加到文件末尾（保留历史记录）

5. **显示成功消息**
   - 告知用户备份已完成
   - 显示 Backup ID 和文件大小
   - **重要**：告知用户密码已自动生成并保存到 `.openclaw-backup-recovery.txt`
   - 警告用户：恢复文件是关键 - 没有它，备份无法恢复

### 错误处理

| 错误场景 | 检测 | 用户指导 |
|----------------|-----------|---------------|
| 文件未找到 | 脚本返回错误： "Files not found: ..." | 列出缺失文件，询问用户是否要继续备份其他文件 |
| 文件太大 | 脚本返回错误： "Backup size ... exceeds limit ..." | 显示实际大小，建议删除大文件或分割备份 |
| 网络错误 | 脚本返回错误： "Network error: ..." | 建议检查网络连接，询问是否要重试 |
| 413 太大 | 脚本返回错误： "File too large (413 Payload Too Large)" | 指出 20MB 限制已超出，建议减小备份大小 |
| 加密失败 | 脚本返回错误： "openssl encryption failed: ..." | 检查 openssl 是否正确安装 |

### 示例对话

```
User: Back up my SOUL.md and MEMORY.md
Claude: I'll backup these files with auto-generated encryption.
       [执行备份脚本]
       Backup complete!
       - Backup ID: 3f8a2b1c-...
       - Size: 45.2 KB
       - Password: Auto-generated (32 chars)
       - Recovery info saved to .openclaw-backup-recovery.txt

       IMPORTANT: Keep .openclaw-backup-recovery.txt safe!
       It contains the password needed to restore this backup.
```

## 工作流程 2：下载备份

### 触发场景

当用户请求恢复备份时执行：

- "恢复我的备份"
- "下载我的最后一个备份"
- "恢复备份 [backup-id]"
- "从 [download-url] 恢复"

### 执行步骤

1. **获取 Backup ID 和密码**
   - 检查用户是否提供了 Backup ID 或 Download URL
   - 如果未提供，使用 Read 工具读取 `.openclaw-backup-recovery.txt`
   - 从文件中提取最新的 Backup ID 和密码
   - 如果文件不存在或为空，则无法继续（密码未知）

2. **确定输出目录**
   - 默认：当前工作目录（`.`）
   - 如果用户指定了目录，则使用用户指定的目录
   - 警告用户：可能覆盖现有文件

3. **执行恢复脚本**
   - 使用恢复文件中的密码执行命令：
     ```bash
     python3 scripts/backup.py download \
       --backup-id "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" \
       --password "password-from-recovery-file" \
       --output-dir "."
     ```
   - 捕获 stdout（JSON 响应）和 stderr（进度信息）

4. **处理响应**
   - 成功时，脚本输出 JSON：
     ```json
     {
       "success": true,
       "extractedFiles": ["SOUL.md", "MEMORY.md", "IDENTITY.md"],
       "outputDir": "/path/to/output"
     }
     ```
   - 解析提取的文件列表

5. **验证恢复结果**
   - 使用 Read 工具读取恢复文件的前几行
   - 向用户显示文件预览以确认内容正确
   - 提醒用户检查完整内容

6. **显示成功消息**
   - 列出恢复的文件
   - 显示输出目录
   - 建议用户验证文件内容

### 错误处理

| 错误场景 | 检测 | 用户指导 |
|----------------|-----------|---------------|
| Backup ID 不存在 | 脚本返回错误： "Backup not found: ..." | 检查 Backup ID 是否正确，可能已被删除 |
| 恢复文件缺失 | 未找到 `.openclaw-backup-recovery.txt` | 无法恢复 - 没有恢复文件，密码未知 |
| 密码错误 | 脚本返回错误： "Decryption failed - wrong password ..." | 恢复文件可能已损坏或来自不同的备份 |
| 网络错误 | 脚本返回错误： "Network error: ..." | 建议检查网络连接，询问是否要重试 |
| 提取失败 | 脚本返回错误： "tar extraction failed: ..." | 文件可能已损坏，尝试重新下载 |

### 示例对话

```
User: Restore my last backup
Claude: I found the most recent backup in .openclaw-backup-recovery.txt
       - Backup ID: 3f8a2b1c-...
       - Created: 2024-01-15 10:30:00 UTC
       Downloading and decrypting backup...
       Restoration complete! Extracted the following files:
       - SOUL.md
       - MEMORY.md
       - IDENTITY.md
       Files saved to current directory, please verify content is correct.
```

## 工作流程 3：删除备份

### 触发场景

当用户请求删除远程备份时执行：

- "删除我的备份"
- "移除备份 [backup-id]"
- "从 soul-upload 删除备份"

### 执行步骤

1. **获取 Backup ID**
   - 检查用户是否提供了 Backup ID
   - 如果未提供，使用 Read 工具读取 `.openclaw-backup-recovery.txt`
   - 显示可用的备份列表供用户选择
   - 如果文件不存在或为空，询问用户提供 Backup ID

2. **请求确认**
   - 警告：此操作不可逆，备份将被永久删除
   - 显示要删除的 Backup ID 和创建时间
   - 询问用户是否确认删除

3. **执行删除脚本**
   - 用户确认后，执行命令：
     ```bash
     python3 scripts/backup.py delete \
       --backup-id "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
     ```
   - 捕获 stdout（JSON 响应）和 stderr（进度信息）

4. **处理响应**
   - 成功时，脚本输出 JSON：
     ```json
     {
       "success": true,
       "backupId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
     }
     ```

5. **更新恢复信息文件**
   - 使用 Read 工具读取 `.openclaw-backup-recovery.txt`
   - 删除已删除的备份记录（包括其密码）
   - 使用 Write 工具保存更新后的文件
   - 如果文件为空，可以删除该文件

6. **显示成功消息**
   - 确认备份已删除
   - 显示已删除的 Backup ID
   - 提醒用户：如果需要备份，必须使用新的密码创建新的备份

### 错误处理

| 错误场景 | 检测 | 用户指导 |
|----------------|-----------|---------------|
| Backup ID 不存在 | 脚本返回错误： "Backup not found: ..." | 备份可能已被删除或 ID 不正确 |
| 网络错误 | 脚本返回错误： "Network error: ..." | 建议检查网络连接，询问是否要重试 |
| 用户取消 | 用户拒绝确认 | 操作取消，备份未删除 |

### 示例对话

```
User: Delete my backup
Claude: I found the following backups in .openclaw-backup-recovery.txt:
       1. Backup ID: 3f8a2b1c-... (2024-01-15 10:30:00)
       2. Backup ID: 7b2c9d4e-... (2024-01-14 08:20:00)
       Which backup would you like to delete? (1 or 2)
User: 1
Claude: Warning: This will permanently delete backup 3f8a2b1c-...
       This action cannot be undone. Confirm deletion? (yes/no)
User: yes
Claude: Backup deleted.
       - Backup ID: 3f8a2b1c-...
       To backup again, create a new backup with a new auto-generated password.
```

## 安全注意事项

### 密码策略（新）

- **自动生成密码**：每个备份都有一个唯一的 32 个字符的随机密码
- **密码不可重复**：根据 soul-upload.com 策略，不要跨备份重复密码
- **密码存储**：密码存储在 `.openclaw-backup-recovery.txt`（解密所必需）
- **用户责任**：用户必须安全地保存恢复文件 - 没有它，备份无法恢复

### 恢复文件安全

- **文件位置**：`.openclaw-backup-recovery.txt`（工作区根目录）
- **内容**：Backup ID、密码（关键）、Download URL、时间戳、SHA256
- **关键**：恢复文件是存储密码的唯一地方
- **建议**：
  - 添加到 `.gitignore` 如果敏感
  - 或提交到版本控制以供团队访问
  - 考虑将恢复文件本身备份到安全的位置

### 加密算法

- **算法**：AES-256-CBC（对称加密）
- **加盐**：openssl 自动添加盐以增强安全性
- **兼容性**：与 soul-upload.com 官方文档一致

### 临时文件清理

- 脚本使用 try-finally 确保临时文件被清理
- 避免在磁盘上留下未加密的敏感数据

## 文件大小限制

- **最大备份大小**：20 MB（压缩和加密）
- **检查时间**：在上传前自动检查
- **超出限制处理**：显示实际大小，建议用户：
  - 删除大文件（如日志、缓存）
  - 分割备份（分批备份不同文件）

## API 参考

soul-upload.com 备份 API:

| 端点 | 方法 | 功能 | 响应 |
|----------|--------|----------|----------|
| `/backup` | POST | 上传备份 | `{backupId, downloadUrl, sizeBytes, sha256}` |
| `/backup/:backupId` | GET | 下载备份 | 302 重定向到 R2 存储 URL |
| `/backup/:backupId` | DELETE | 删除备份 | `{success: true, backupId}` |

常见状态码：

- **200** - 成功
- **404** - 备份不存在
- **413** - 文件太大（超过 20MB）
- **415** - 不支持的文件类型
- **500** - 服务器错误

## 故障排除

### 缺少依赖项

**问题**：脚本错误 "Missing required tools: tar, openssl"

**解决方案**：
- macOS: `brew install openssl`（tar 内置）
- Ubuntu/Debian: `sudo apt-get install tar openssl`
- 验证安装：`tar --version` 和 `openssl version`

### Python requests 库缺失

**问题**：脚本错误 "Error: 'requests' library not found"

**解决方案**：
```bash
pip install requests
# or
pip3 install requests
```

### 恢复文件丢失

**问题**：无法恢复备份 - 恢复文件丢失

**解决方案**：
- 恢复文件是关键 - 包含密码的唯一副本
- 没有恢复文件，备份无法恢复
- 建议将恢复文件备份到安全的位置
- 如果丢失，备份将永久无法访问

### 网络超时

**问题**：上传/下载期间超时

**解决方案**：
- 检查网络连接
- 减小备份文件大小（删除不必要的文件）
- 脚本默认超时为 5 分钟，通常足够

### 文件已存在

**问题**：恢复期间覆盖现有文件

**解决方案**：
- 在恢复前备份现有文件
- 指定不同的输出目录
- 手动将现有文件移动到其他位置

## 使用示例

### 示例 1：备份所有默认文件

```
User: Back up my workspace files
Claude: [执行上传工作流，使用默认文件列表]
       [自动生成密码并保存到恢复文件]
```

### 示例 2：备份特定文件

```
User: Back up only SOUL.md and MEMORY.md
Claude: [执行上传工作流，备份仅指定的文件]
       [自动生成密码并保存到恢复文件]
```

### 示例 3：恢复最新备份

```
User: Restore my last backup
Claude: [从 .openclaw-backup-recovery.txt 读取最新的 Backup ID 和密码]
       [执行下载工作流]
```

### 示例 4：恢复特定备份

```
User: Restore backup 3f8a2b1c-1234-5678-90ab-cdef12345678
Claude: [从恢复文件中读取此 Backup ID 的密码]
       [执行下载工作流]
```

### 示例 5：删除旧备份

```
User: Delete my old backups
Claude: [从恢复文件中显示可用的备份列表]
       [用户选择要删除的备份]
       [执行删除工作流]
       [从恢复文件中删除条目]
```

## 最佳实践

1. **定期备份**：建议每周备份或在重要更改后备份
2. **恢复文件管理**：安全地保存并备份 `.openclaw-backup-recovery.txt`
3. **验证恢复**：定期测试备份恢复过程以确保备份可用
4. **清理旧备份**：定期删除不需要的旧备份以节省存储空间
5. **多个副本**：考虑将恢复文件保存在多个安全位置

## 脚本路径

脚本文件位于技能目录中的 `scripts/backup.py`。

执行 Bash 命令时，请确保使用正确的相对或绝对路径。通常：
- 如果当前在工作技能目录中：`python3 scripts/backup.py ...`
- 如果在其他目录中：使用绝对路径或先 `cd` 到技能目录

## 参考文档

- [soul-upload.com 备份指南](https://soul-upload.com/guides/how-to-backup-soul-md)
- [soul-upload.com 恢复指南](https://soul-upload.com/guides/how-to-restore-soul-md)
- [OpenClaw 代理文档](https://openclaw.com)

---

**版本**：2.0.0
**作者**：Claude Code
**许可证**：MIT
**密码策略**：每个备份自动生成唯一密码（v2.0.0 新增）
