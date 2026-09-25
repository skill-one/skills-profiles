# 博客 NotebookLM：从您的文档中获取源导向研究

直接从 Claude Code 查询 Google NotebookLM 笔记本，以获取来自 Gemini 的基于引用的答案。每个问题都会打开一个无头浏览器会话，从您上传的文档中检索答案，然后关闭。响应是基于源的模型答案，而不是真理的证据：上传的文档可能是原始文献或次级文献，答案仍然可能省略上下文。

当返回的引用标识一个可验证的底层来源时，答案才会提供可用的出处。当该详细信息影响验证或解释时，记录一个稳定的来源 URL 以及出版日期、研究期间或检索日期。使用底层来源标题作为内联引用。不要将私有的 NotebookLM URL 作为公共内容的参考文献条目。

## 快速参考

| 命令 | 它的作用 |
|------|---------|
| `/blog notebooklm ask <问题>` | 查询笔记本以获取基于源的答案 |
| `/blog notebooklm discover <url>` | 在编目之前智能发现笔记本内容 |
| `/blog notebooklm library list` | 列出库中的所有笔记本 |
| `/blog notebooklm library add <url>` | 将笔记本添加到库中 |
| `/blog notebooklm library search <查询>` | 按关键词搜索笔记本 |
| `/blog notebooklm library remove <id>` | 从库中删除笔记本 |
| `/blog notebooklm setup` | 一次性 Google 身份验证（浏览器可见） |
| `/blog notebooklm status` | 检查身份验证状态 |
| `/blog notebooklm cleanup` | 清理浏览器状态（保留库） |

## 前置条件

- 具有 NotebookLM 访问权限的 Google 账户
- Python 3.11+（venv 由 `run.py` 自动管理）
- Google Chrome（在第一次运行时通过 Patchright 自动安装）
- 一次性身份验证设置（在可见浏览器中进行交互式 Google 登录）

## 使用 run.py 包装器

仅通过 run.py 包装器调用脚本：`python3 scripts/run.py [脚本]`：

```bash
# 正确的用法：
python3 scripts/run.py auth_manager.py status
python3 scripts/run.py ask_question.py --question "..."
```

不要直接调用 `scripts/` 下的文件。包装器拥有 venv 设置。

`run.py` 包装器会自动创建 `.venv`，安装依赖项，设置 Chrome，并执行目标脚本。

## 身份验证检查（门模式）

在任何查询操作之前，检查身份验证：

```bash
python3 scripts/run.py auth_manager.py status
```

- 如果已身份验证：继续执行查询
- 如果未身份验证：通知用户并引导设置：
  "NotebookLM 需要 Google 登录。运行 `/blog notebooklm setup` 进行身份验证。"
- **当内部调用时**（来自 blog-write 或 blog-researcher）：如果未身份验证，则静默返回，不显示错误。永远不要阻塞编写工作流程。

## 设置工作流程

对于 `/blog notebooklm setup`：

```bash
# 打开一个可见的浏览器进行手动 Google 登录（一次性）
python3 scripts/run.py auth_manager.py setup
```

告诉用户："将打开一个浏览器窗口。请登录到您的 Google 账户。"
身份验证通过浏览器配置文件 + Cookie 注入（混合方法）持久化。

其他身份验证命令：
```bash
python3 scripts/run.py auth_manager.py status   # 检查身份验证
python3 scripts/run.py auth_manager.py reauth   # 重新身份验证
python3 scripts/run.py auth_manager.py clear     # 清除所有身份验证数据
```

## 查询工作流程

对于 `/blog notebooklm ask <问题>`：

### 第 1 步：检查身份验证
运行身份验证检查（见门模式）。如果未身份验证，则引导设置。

### 第 2 步：解析笔记本
确定要查询哪个笔记本：
- 如果提供 `--notebook-url`：验证它是否是 NotebookLM 笔记本 URL，然后使用它
- 如果提供 `--notebook-id`：在库中查找
- 如果都不提供：使用库中的活动笔记本
- 如果没有活动笔记本：显示库并要求用户选择

### 第 3 步：提问
```bash
# 基本查询（使用活动笔记本）
python3 scripts/run.py ask_question.py --question "您的提问内容"

# 通过 ID 查询特定笔记本
python3 scripts/run.py ask_question.py --question "..." --notebook-id notebook-id

# 直接通过 URL 查询
python3 scripts/run.py ask_question.py --question "..." --notebook-url "https://..."

# JSON 输出（用于内部/程序化使用）
python3 scripts/run.py ask_question.py --question "..." --json

# 显示浏览器以进行调试
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
  --question "这个笔记本的内容是什么？涵盖了哪些主题？简要简洁地提供完整概述" \
  --notebook-url "<URL>"

# 第 2 步：使用发现的元数据添加
python3 scripts/run.py notebook_manager.py add \
  --url "<URL>" \
  --name "<基于内容>" \
  --description "<基于内容>" \
  --topics "<提取的主题>"
```

不要猜测描述；发现或询问用户。

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

# 按关键词搜索
python3 scripts/run.py notebook_manager.py search --query "keyword"

# 设置活动笔记本
python3 scripts/run.py notebook_manager.py activate --id notebook-id

# 删除笔记本
python3 scripts/run.py notebook_manager.py remove --id notebook-id

# 库统计
python3 scripts/run.py notebook_manager.py stats
```

## 内部 API（用于 blog-write / blog-researcher）

当作为 blog-write 或 blog-researcher 的 Task 子代理被调用时：

**输入**（由调用技能提供）：
- `question`：与博客主题相关的调研问题
- `notebook_id` 或 `notebook_url`：要查询的笔记本
- `context`："internal"（表示优雅的回退模式）

**处理：**
1. 检查身份验证状态：如果未身份验证，则静默返回空结果
2. 使用调研问题查询笔记本
3. 解析并返回结构化响应

**输出**（返回给调用技能）：
```markdown
### NotebookLM 研究
- **来源**：[笔记本名称]
- **问题**：[被问的内容]
- **答案**：[来自用户文档的基于源的响应]
- **底层来源**：[公共来源 URL 或文档标识符]
- **底层来源日期**：[出版日期或检索日期]
- **来源质量**：[分类底层文档后的 1-3 级]
```

**优雅回退**：如果身份验证缺失或查询失败，则立即返回，不显示错误。调用工作流程继续使用基于 WebSearch 的研究。永远不要因为 NotebookLM 不可用而阻塞 blog-write 或 blog-rewrite。

## 数据存储

所有数据存储在技能目录中：
- `data/library.json`：笔记本元数据和库
- `data/auth_info.json`：身份验证状态
- `data/browser_state/`：带有 Cookie 的 Chrome 配置文件

**安全性**：所有数据目录都被 git 忽略。永远不要提交身份验证或浏览器状态。

浏览器生命周期和身份验证上下文隔离集中在 `scripts/browser_session.py` 中。命令脚本必须使用该辅助工具，而不是打开额外的持久配置文件或将 Cookie 复制到另一个文件。

## 错误处理

| 错误 | 解决方案 |
|------|---------|
| 未身份验证 | 运行 `/blog notebooklm setup` |
| ModuleNotFoundError | 始终使用 `run.py` 包装器 |
| 浏览器崩溃 | `cleanup_manager.py --confirm --preserve-library`，然后重新身份验证 |
| 速率限制（每天 50 次） | 等待太平洋标准时间午夜或切换 Google 账户 |
| 笔记本未找到 | 使用 `notebook_manager.py list` 检查 |
| 查询超时（120 秒） | 重试使用更简单的问题或 `--show-browser` 进行调试 |
| MCP 不可用（内部） | 静默返回：编写工作流程使用 WebSearch |

## 限制

- 没有会话持久化（每个问题 = 新的浏览器会话）
- 免费Google账户的速率限制（每天 50 个查询）
- 需要手动上传（用户必须将文档添加到 NotebookLM 网页界面）
- 浏览器开销（每个问题启动 + 销毁需要几秒钟）
- 仅限本地 Claude Code（网页界面不可用）

## 参考文档

按需加载：不要在启动时加载所有内容：
- `references/commands.md`：完整的 CLI 命令、参数和工作流模式
- `references/troubleshooting.md`：错误解决方案、恢复程序、调试
