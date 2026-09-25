# 技能：不安全的源代码管理

> **AI 加载指令**：此技能涵盖暴露的版本控制元数据、常见备份文件和相关的配置错误检测与恢复。仅在 **授权** 评估中使用。将恢复的凭证和 URL 视为敏感信息；不要超出范围外泄真实数据。对于广泛的发现工作流，当工作区中存在这些技能时，请交叉加载 [recon-for-sec](../recon-for-sec/SKILL.md) 和 [recon-and-methodology](../recon-and-methodology/SKILL.md)。

## 0. 快速入门

首先探测高价值路径（使用 GET 或 HEAD，尊重速率限制）：

```http
/.git/HEAD
/.git/config
/.svn/entries
/.svn/wc.db
/.hg/requires
/.bzr/README
/.DS_Store
/.env
```

**路由说明**：首先快速探测这些路径；对于完整的发现工作流，在使用深层测试前，从 `recon-for-sec` 和 `recon-and-methodology` 加载方法学。

---

## 1. GIT 暴露

### 检测

- **`/.git/HEAD`** — 有效的仓库通常返回纯文本，例如：

```text
ref: refs/heads/main
```

- **`/.git/config`** — 可能暴露 `remote.origin.url`、用户身份或嵌入的凭证。
- **`/.git/index`**、**`/.git/objects/`** — 部分对象存储访问可使用正确工具进行重建。

### 403 与 404

- **`404`** — 路径可能不存在或已在边缘完全阻止。
- **`/.git` 的 403** — 目录可能存在，但列出被拒绝；仍尝试直接文件 URL：

```http
/.git/HEAD
/.git/config
/.git/logs/HEAD
/.git/refs/heads/main
```

目录上的 **403** 加上 **`HEAD` 的 200** 强烈表明存在暴露。

### 恢复工具（开源）

- **`arthaud/git-dumper`** — 当单个文件可获取时，转储可达的 `.git` 树。
- **`internetwache/GitTools`** — Dumper、Extractor、Finder 模块用于部分/损坏的转储。
- **`WangYihang/GitHacker`** — 标准转储器遗漏边缘情况时的替代恢复方法。

### 优先考虑的关键文件

| 路径 | 重要性原因 |
|------|----------------|
| `.git/config` | 远程、凭证、钩子路径 |
| `.git/logs/HEAD` | 提交历史、reflog 风格泄露 |
| `.git/refs/heads/*` | 分支尖端、提交 SHA |
| `.git/packed-refs` | 压缩分支/标签引用 |
| `.git/objects/**` | 用于重建的对象块 |

---

## 2. SVN 暴露

### 检测

- **SVN 1.7 之前**：**`/.svn/entries`** — XML 或文本元数据列出路径和版本。
- **SVN ≥ 1.7**：**`/.svn/wc.db`** — SQLite 工作副本数据库（下载后使用 `PRAGMA table_info`）。

示例探测：

```http
GET /.svn/entries HTTP/1.1
GET /.svn/wc.db HTTP/1.1
```

### 恢复

- **`anantshri/svn-extractor`** — 自动从暴露的 `.svn` 提取。
- **手动**：下载 `wc.db`，使用 `sqlite3` 查询文件路径和校验和，然后如果暴露，请求 **`/.svn/pristine/`** 块。

---

## 3. MERCURIAL 暴露

### 检测

- **`/.hg/requires`** — 小型文本文件列出仓库功能；确认 Mercurial 元数据。

```http
GET /.hg/requires HTTP/1.1
GET /.hg/store/ HTTP/1.1
```

### 恢复

- **`sahildhar/mercurial_source_code_dumper`** — 当存储路径可达时转储仓库。

---

## 4. 其他泄露

### Bazaar (Bzr)

- 探测 **`/.bzr/README`** 和 **`/.bzr/branch-format`** 以获取 Bazaar 元数据。

### macOS `.DS_Store`

- **`/.DS_Store`** 可编码目录和文件名列表。
- 工具：**`gehaxelt/ds-store`**、**`lijiejie/ds_store_exp`** — 离线解析 `.DS_Store`。

### 备份和配置文件

探测（根据应用根目录和命名约定调整）：

```text
/.env
/backup.zip
/backup.tar.gz
/wwwroot.rar
/backup.sql
/config.php.bak
/.config.php.swp
```

### Web 服务器配置错误信号（示例：NGINX）

- **`location /.git { deny all; }`** — 可能对 `/.git/` 返回 **403**，但根据规则仍允许或拒绝特定子路径。
- **受保护位置的 403** 可 **确认路径存在**；始终与 **不存在路径的 404** 区分。

---

## 5. 决策树

1. **探测 `/.git/HEAD`** → 返回 `ref: refs/heads/` 模式？ → 运行 **git-dumper / GitTools / GitHacker**；检查 `config` 和 `logs/HEAD` 寻找秘密。
2. **否则探测 `/.svn/wc.db` 或 `entries`** → 成功？ → **svn-extractor** 或手动 `wc.db` + pristine 恢复。
3. **否则探测 `/.hg/requires`** → 成功？ → **mercurial dumper**。
4. **否则探测 `/.bzr/README`** → Bazaar 工具或手动路径遍历。
5. **并行**：获取 **`/.DS_Store`**、**`/.env`**、应用根和父路径的常见 **备份扩展**。
6. **解释状态码**：**目录的 403** 加上 **特定文件的 200** → 视为 **高优先级** 进行逐文件提取。

---

## 6. 相关路由

- 从 **[recon-for-sec](../recon-for-sec/SKILL.md)** — 范围安全的发现、爬取和指纹识别，在进行深层 VCS 测试前。
- 从 **[recon-and-methodology](../recon-and-methodology/SKILL.md)** — 结构化方法学和证据处理。

**注意**：与发现技能协调——首先设置范围和请求速率，然后运行目标 VCS/备份验证。
