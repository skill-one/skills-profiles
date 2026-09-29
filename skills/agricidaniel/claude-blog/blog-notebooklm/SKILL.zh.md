---
name: blog-notebooklm
description: 查询 Google NotebookLM 笔记本，从用户上传的文档中获取基于来源、有引用支持的答案。管理笔记本库，处理 Google 身份验证，并支持智能发现。可通过 /blog notebooklm 独立运行，或从 blog-write 和 blog-researcher 内部调用以实现基于来源的研究上下文。在未配置时能优雅地回退。当用户说“notebooklm”、“笔记本”、“查询笔记本”、“询问笔记本”、“笔记本研究”、“基于来源的研究”、“文档查询”、“笔记本库”时使用。
---

# 博客 NotebookLM：从您的文档中获取源根研究

直接从 Claude 代码中查询 Google NotebookLM 笔记本，以获取来自 Gemini 的、有引用支持的答案。每个问题都会打开一个无头浏览器会话，从您上传的文档中检索答案，然后关闭。响应是源根模型答案，而不是真理的证据：上传的文档可能是原始文献或次级文献，答案仍然可能省略上下文。

只有当返回的引用包括一个可验证的底层来源 URL 以及一个出版或检索日期时，答案才满足 FLOW 证据三元组。使用底层来源标题作为内联引用。不要将私有的 NotebookLM URL 作为公共内容的参考文献条目。

## 快速参考

| 命令 | 它的作用 |
|------|--------|
| `/blog notebooklm ask <问题>` | 查询笔记本以获取源根答案 |
| `/blog notebooklm discover <url>` | 在编目之前智能发现笔记本内容 |
| `/blog notebooklm library list` | 列出库中的所有笔记本 |
| `/blog notebooklm library add <url>` | 将笔记本添加到库中 |
| `/blog notebooklm library search <查询>` | 按关键字搜索笔记本 |
| `/blog notebooklm library remove <id>` | 从库中删除笔记本 |
| `/blog notebooklm setup` | 一次性 Google 身份验证（浏览器可见） |
| `/blog notebooklm status` | 检查身份验证状态 |
| `/blog notebooklm cleanup` | 清理浏览器状态（保留库） |

## 前置条件

- 具有 NotebookLM 访问权限的 Google 账户
- Python 3.11+（venv 由 `run.py` 自动管理）
- Google Chrome（在第一次运行时通过 Patchright 自动安装）
- 一次性身份验证设置（在可见浏览器中进行交互式 Google 登录）

## 始终使用 run.py 包装器

**绝对不要直接调用脚本。始终使用 `python3 scripts/run.py [脚本]`：**

```bash
# 正确的：
python3 scripts/run.py auth_manager.py status
python3 scripts/run.py ask_question.py --question "..."

# 不要直接调用 scripts/ 下的文件。包装器拥有 venv 设置。
```

`run.py` 包装器会自动创建 `.venv`，安装依赖项，设置 Chrome，并执行目标脚本。

## 身份验证检查（门模式）

在进行任何查询操作之前，检查身份验证：

```bash
python3 scripts/run.py auth_manager.py status
```

- 如果已通过身份验证：继续进行查询
- 如果未通过身份验证：通知用户并指导设置：
  "NotebookLM 需要 Google 登录。运行 `/blog notebooklm setup` 进行身份验证。"
- **在内部调用时**（来自 blog-write 或 blog-researcher）：如果未通过身份验证，则静默返回，不显示错误。永远不要阻塞写作工作流。

## 设置工作流程

对于 `/blog notebooklm setup`：

```bash
# 打开一个可见的浏览器进行手动 Google 登录（一次性）
python3 scripts/run.py auth_manager.py setup
```

告诉用户："将打开一个浏览器窗口。请登录到您的 Google 账户。"
身份验证通过浏览器配置文件 + Cookie 注入（混合方法）持久保存。

其他身份验证命令：
```bash
python3 scripts/run.py auth_manager.py status   # 检查身份验证
python3 scripts/run.py auth_manager.py reauth   # 重新身份验证
python3 scripts/run.py auth_manager.py clear     # 清除所有身份验证数据
```

## 查询工作流程

对于 `/blog notebooklm ask <问题>`：

### 第 1 步：检查身份验证
运行身份验证检查（见上述门模式）。如果未通过身份验证，则指导设置。

### 第 2 步：解析笔记本
确定要查询哪个笔记本：
- 如果提供了 `--notebook-url`：验证它是否是 NotebookLM 笔记本 URL，然后使用它
- 如果提供了 `--notebook-id`：在库中查找
- 如果都没有：使用库中的活动笔记本
- 如果没有活动笔记本：显示库并要求用户选择

### 第 3 步：提问
```bash
# 基本查询（使用活动笔记本）
python3 scripts/run.py ask_question.py --question "您的提问内容"

# 通过 ID 查询特定笔记本
python3 scripts/run.py ask_question.py --question "..." --notebook-id notebook-id

# 直接通过 URL 查询
python3 scripts/run.py ask_question.py --question "..." --notebook-url "https://..."

# JSON 输出（用于内部/程序使用）
python3 scripts/run.py ask_question.py --question "..." --json

# 显示浏览器进行调试
python3 scripts/run.py ask_question.py --question "..." --show-browser
```

### 第 4 步：分析和跟进
每个响应都以跟进提示结束。**必须行为：**
1. **停止**：不要立即回复用户
2. **分析**：将答案与用户的原始请求进行比较
3. **识别差距**：确定是否需要更多信息
4. **提问跟进**：如果存在差距，立即提出跟进问题
5. **重复**：继续直到信息完整
6. **综合**：在回复用户之前组合所有答案

## 智能发现工作流程

对于 `/blog notebooklm discover <url>`：

在不知道笔记本内容的情况下添加笔记本时，先查询它：

```bash
# 第 1 步：发现内容
python3 scripts/run.py ask_question.py \
  --question "这个笔记本的内容是什么？涵盖了哪些主题？提供简要而全面的概述" \
  --notebook-url "<URL>"

# 第 2 步：使用发现的元数据添加
python3 scripts/run.py notebook_manager.py add \
  --url "<URL>" \
  --name "<基于内容>" \
  --description "<基于内容>" \
  --topics "<提取的主题>"
```

**绝对不要猜测或使用通用描述。** 始终发现或询问用户。

## 库管理

```bash
# 列出所有笔记本
python3 scripts/run.py notebook_manager.py list

# 添加笔记本（所有参数都必需 -- 发现或询问用户！）
python3 scripts/run.py notebook_manager.py add \
  --url "https://notebooklm.google.com/notebook/..." \
  --name "描述性名称" \
  --description "笔记本包含的内容" \
  --topics "topic1,topic2,topic3"

# 按关键字搜索
python3 scripts/run.py notebook_manager.py search --query "关键字"

# 设置活动笔记本
python3 scripts/run.py notebook_manager.py activate --id notebook-id

# 删除笔记本
python3 scripts/run.py notebook_manager.py remove --id notebook-id

# 库统计信息
python3 scripts/run.py notebook_manager.py stats
```

## 内部 API（用于 blog-write / blog-researcher）

作为从 blog-write 或 blog-researcher 调用的任务子代理时：

**输入**（由调用技能提供）：
- `question`：与博客主题相关的调研问题
- `notebook_id` 或 `notebook_url`：要查询哪个笔记本
- `context`："internal"（表示优雅的回退模式）

**处理：**
1. 检查身份验证状态：如果未通过身份验证，则静默返回空结果
2. 使用调研问题查询笔记本
3. 解析并返回结构化响应

**输出**（返回给调用技能）：
```markdown
### NotebookLM 研究
- **来源**：[笔记本名称]
- **问题**：[被问什么]
- **答案**：[来自用户文档的源根响应]
- **底层来源**：[公共来源 URL 或文档标识符]
- **底层来源日期**：[出版日期或检索日期]
- **来源质量**：[对底层文档进行分类后的 1-3 级]
```

**优雅回退**：如果身份验证缺失或查询失败，则立即返回，不显示错误。调用工作流继续使用基于 Web 的搜索进行调研。永远不要因为 NotebookLM 不可用而阻塞 blog-write 或 blog-rewrite。

## 数据存储

所有数据存储在技能目录中：
- `data/library.json`：笔记本元数据和库
- `data/auth_info.json`：身份验证状态
- `data/browser_state/`：带有 Cookie 的 Chrome 配置文件

**安全性**：所有数据目录都被 git 忽略。永远不要提交身份验证或浏览器状态。

## 错误处理

| 错误 | 解决方案 |
|------|--------|
| 未通过身份验证 | 运行 `/blog notebooklm setup` |
| ModuleNotFoundError | 始终使用 `run.py` 包装器 |
| 浏览器崩溃 | `cleanup_manager.py --confirm --preserve-library`，然后重新身份验证 |
| 频率限制（每天 50 次） | 等待太平洋标准时间午夜或切换 Google 账户 |
| 笔记本未找到 | 使用 `notebook_manager.py list` 检查 |
| 查询超时（120 秒） | 重试使用更简单的问题或 `--show-browser` 进行调试 |
| MCP 不可用（内部） | 静默返回：写作工作流使用 WebSearch |

## 限制

- 没有会话持久性（每个问题 = 新的浏览器会话）
- 免费Google账户的频率限制（每天 50 个查询）
- 需要手动上传（用户必须将文档添加到 NotebookLM 网页界面）
- 浏览器开销（每个问题启动和销毁需要几秒钟）
- 仅限本地 Claude Code（网页界面不可用）

## 参考文档

按需加载：不要在启动时加载所有内容：
- `references/commands.md`：完整的 CLI 命令、参数和工作流模式
- `references/troubleshooting.md`：错误解决方案、恢复程序、调试
