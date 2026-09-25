# 时间线报告

使用 claude-mem 的持久化记忆时间线生成项目整个开发历史的全面叙事分析。

## 使用场景

当用户询问以下内容时使用：

- "编写时间线报告"
- "探索 [项目]"
- "分析我的项目历史"
- "完整项目报告"
- "总结整个开发历史"
- "这个项目的故事是什么？"

## 前置条件

claude-mem 工作进程必须正在运行。项目必须有 claude-mem 观察记录。

**解决工作端口**（在开始时执行一次并在以下每个 curl 调用中重用 `$WORKER_PORT`）：

```bash
WORKER_PORT="${CLAUDE_MEM_WORKER_PORT:-$(node -e "const fs=require('fs'),p=require('path'),os=require('os');const uid=(typeof process.getuid==='function'?process.getuid():77);const fallback=String(37700+(uid%100));try{const s=JSON.parse(fs.readFileSync(p.join(os.homedir(),'.claude-mem','settings.json'),'utf-8'));process.stdout.write(String(s.CLAUDE_MEM_WORKER_PORT||fallback));}catch{process.stdout.write(fallback);}" 2>/dev/null)}"
```

这会优先使用 `CLAUDE_MEM_WORKER_PORT` 环境变量，然后是 `~/.claude-mem/settings.json`，最后回退到基于用户 ID 的默认端口 `37700 + (uid % 100)`——这与工作进程选择其端口的方式相同。对于多账户设置（#2101）以及任何已覆盖默认端口的用户（#2103）都是必需的。

## 工作流程

### 第 1 步：确定项目名称

如果上下文不明显，询问用户要分析哪个项目。项目名称通常是项目的目录名称（例如，"tokyo"、"my-app"）。如果用户说 "这个项目"，则使用当前工作目录的 basename。

**工作树检测**：在使用目录 basename 之前，检查当前目录是否是 git 工作树。在工作树中，数据源是**父项目**，而不是工作树目录本身。运行：

```bash
git_dir=$(git rev-parse --git-dir 2>/dev/null)
git_common_dir=$(git rev-parse --git-common-dir 2>/dev/null)
if [ "$git_dir" != "$git_common_dir" ]; then
  # 我们处于工作树中——解析父项目名称
  parent_project=$(basename "$(dirname "$git_common_dir")")
  echo "检测到 git 工作树。父项目：$parent_project"
else
  parent_project=$(basename "$PWD")
fi
echo "$parent_project"
```

如果检测到工作树，则使用 `$parent_project`（父存储库的 basename）作为所有 API 调用的项目名称。通知用户："检测到 git 工作树。使用父项目 '[名称]' 作为数据源。"

### 第 2 步：获取完整时间线

使用 Bash 从 claude-mem 工作进程 API 获取完整时间线：

```bash
curl -s "http://localhost:${WORKER_PORT}/api/context/inject?project=PROJECT_NAME&full=true"
```

这将返回整个压缩的时间线——项目整个历史中的每个观察记录、会话边界和摘要。响应是预格式化的 markdown，针对 LLM 优化。

**令牌估计**：完整时间线的大小取决于项目的历史：
- 小型项目（< 1,000 个观察记录）：~20-50K 令牌
- 中型项目（1,000-10,000 个观察记录）：~50-300K 令牌
- 大型项目（10,000-35,000 个观察记录）：~300-750K 令牌

如果响应为空或返回错误，工作进程可能未运行或项目名称可能不正确。尝试 `curl -s "http://localhost:${WORKER_PORT}/api/search?query=*&limit=1"` 来验证工作进程是否健康。

### 第 3 步：估计令牌数量

在继续之前，估计获取的时间线的令牌数量（大约每 4 个字符 1 个令牌）。向用户报告：

```
时间线获取：~X 个观察记录，估计 ~Yk 令牌。
此分析将消耗大约 Yk 输入令牌 + ~5-10k 输出令牌。
继续？(y/n)
```

如果时间线超过 100K 令牌，则在继续之前等待用户确认。

### 第 4 步：使用子代理分析

部署一个代理（使用 Task 工具），并将完整时间线和以下分析提示传递给代理。将整个时间线作为上下文传递给代理。代理还应该被指示查询 SQLite 数据库 `~/.claude-mem/claude-mem.db` 以获取 Token 经济部分。

**代理提示**：

```
你是一位技术历史学家，正在分析来自 claude-mem 持久化记忆系统的软件项目的完整开发时间线。以下时间线包含项目整个历史中记录的每个观察记录、会话边界和摘要。

你还能够访问 claude-mem SQLite 数据库 `~/.claude-mem/claude-mem.db`。使用它来运行查询以获取 Token 经济和 Memory ROI 部分。数据库有一个 "observations" 表，列包括：id、memory_session_id、project、text、type、title、subtitle、facts、narrative、concepts、files_read、files_modified、prompt_number、discovery_tokens、created_at、created_at_epoch、content_hash、generated_by_model、relevance_count、merged_into_project、agent_type、agent_id、metadata。

编写一个全面的叙事报告，标题为 "探索 [PROJECT_NAME]"，涵盖：

## 必须部分

1. **项目起源**——项目何时以及如何开始的。第一个提交是什么，最初的愿景是什么，最初的决策是什么？解决了什么问题？

2. **架构演变**——随着时间的推移，架构是如何变化的？哪些是主要的转折点？为什么发生？从初始设计到每次重大重构，跟踪演变过程。

3. **关键突破**——识别 "啊哈" 时刻：当最终解决了困难的问题，当新方法解锁了进展，当原型首次工作。这些是观察记录，其中语气从调查转变为解决。

4. **工作模式**——分析开发的节奏。识别调试周期（错误修复的集群）、功能冲刺（快速观察记录序列）、重构阶段（没有新功能的架构更改）和探索阶段（没有更改的许多发现）。

5. **技术债务**——跟踪何时采取了捷径以及何时偿还。识别积累模式（快速功能工作）和解决模式（专门的重构会话）。

6. **挑战和调试传奇**——遇到的 hardest 问题。多会话调试工作、需要回溯的架构死胡同、需要数天解决的特定平台问题。

7. **记忆和连续性**——持久化记忆（如果适用，claude-mem 本身）如何影响开发过程？是否有时刻从先前会话中回忆的上下文节省了时间或防止了重复错误？

8. **Token 经济和 Memory ROI**——定量分析记忆召回如何节省工作：
   - 直接使用 `sqlite3 ~/.claude-mem/claude-mem.db` 查询数据库以获取这些指标
   - 计算所有观察记录的总 discovery_tokens（所有工作的原始成本）
   - 计算有上下文注入可用（第一次之后的会话）的会话数量
   - 计算压缩比率：平均 discovery_tokens 与每个观察记录的平均 read_tokens
   - 识别最高价值的观察记录（最高的 discovery_tokens —— 这些是最昂贵的决策、错误和记忆防止重做的发现）
   - 识别明确的召回事件（观察记录，其中叙述提到 "召回"、"从记忆"、"先前会话"）
   - 估计被动召回节省：每个有上下文注入的会话接收 ~50 个观察记录。使用 30% 的相关性因子（保守估计 30% 的注入上下文防止重复工作）。节省 = sessions_with_context × avg_discovery_value_of_50_obs_window × 0.30
   - 估计明确的召回节省：每个明确的召回查询 ~10K 令牌
   - 计算净 ROI：total_savings / total_read_tokens_invested
   - 以月度分解的形式呈现表格
   - 突出显示 discovery_tokens 最高的前 5 个观察记录 —— 这些代表了系统中最有价值的记忆（架构决策、难缠的错误、产生 100K+ 令牌的原始实施计划）

   使用以下 SQL 查询作为起点：
   ```sql
   -- 总 discovery_tokens
   SELECT SUM(discovery_tokens) FROM observations WHERE project = 'PROJECT_NAME';

   -- 有上下文可用的会话（不是第一个会话）
   SELECT COUNT(DISTINCT memory_session_id) FROM observations WHERE project = 'PROJECT_NAME';

   -- 每个观察记录的平均令牌
   SELECT AVG(discovery_tokens) as avg_discovery, AVG(LENGTH(title || COALESCE(subtitle,'') || COALESCE(narrative,'') || COALESCE(facts,'')) / 4) as avg_read FROM observations WHERE project = 'PROJECT_NAME' AND discovery_tokens > 0;

   -- discovery_tokens 最高的前 5 个观察记录（最有价值的记忆）
   SELECT id, title, discovery_tokens FROM observations WHERE project = 'PROJECT_NAME' ORDER BY discovery_tokens DESC LIMIT 5;

   -- 月度分解
   SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as obs, SUM(discovery_tokens) as total_discovery, COUNT(DISTINCT memory_session_id) as sessions FROM observations WHERE project = 'PROJECT_NAME' GROUP BY month ORDER BY month;

   -- 明确的召回事件
   SELECT COUNT(*) FROM observations WHERE project = 'PROJECT_NAME' AND (narrative LIKE '%recalled%' OR narrative LIKE '%from memory%' OR narrative LIKE '%previous session%');
   ```

9. **时间线统计**——定量摘要：
   - 日期范围（第一个观察记录到最后一个）
   - 总观察记录和会话数量
   - 按观察记录类型分解（功能、错误修复、发现、决策、更改）
   - 最活跃的日期/周
   - 最长的调试会话

10. **教训和元观察记录**——从完整历史中出现了哪些模式？新开发者从阅读时间线中会了解什么关于这个代码库？哪些反复出现的主题或原则指导了开发？

## 写作风格

- 写作风格应为技术叙事，而不是要点列表
- 参考事件时使用具体的观察记录 ID 和时间戳（例如，"在 12 月 14 日 (#26766)，根本原因最终被确定..."）
- 跨时间连接事件——展示早期决策如何创造了后来的后果
- 坦诚面对挣扎和死胡同，而不仅仅是成功
- 根据项目大小，目标 3,000-6,000 字
- 在适当的地方使用 markdown 格式化，包括标题、强调和代码引用

## 重要提示

- 按时间顺序分析整个时间线——不要跳过早期历史
- 寻找叙事弧：问题 -> 调查 -> 解决
- 识别转折点，项目的方向发生了根本性变化
- 记录任何关于开发过程本身的观察记录（工具、工作流程、协作模式）

这是完整的项目时间线：

[TIMELINE CONTENT GOES HERE]
```

### 第 5 步：保存报告

将代理的输出保存为 markdown 文件。默认位置：

```
./journey-into-PROJECT_NAME.md
```

或者如果用户指定了不同的输出路径，则使用该路径。

### 第 6 步：报告完成

告诉用户：
- 报告保存的位置
- 大约的令牌成本（输入时间线 + 输出报告）
- 覆盖的日期范围
- 分析的观察记录数量

## 错误处理

- **空时间线**："未找到项目 'X' 的观察记录。使用以下命令检查项目名称：`curl -s \"http://localhost:${WORKER_PORT}/api/search?query=*&limit=1\"`"
- **工作进程未运行**："claude-mem 工作进程在端口 ${WORKER_PORT} 上没有响应。使用您通常的方法启动它或检查 `ps aux | grep worker-service`。"
- **时间线太大**：对于有 50,000+ 个观察记录的项目，时间线可能超过上下文限制。建议使用日期范围过滤：`curl -s "http://localhost:${WORKER_PORT}/api/context/inject?project=X&full=true"` —— 当前端点返回所有观察记录；对于极大型项目，用户可能希望按时间窗口分段分析。

## 示例

用户："为 tokyo 项目编写旅程报告"

1. 获取：`curl -s "http://localhost:${WORKER_PORT}/api/context/inject?project=tokyo&full=true"`
2. 估计："时间线获取：~34,722 个观察记录，估计 ~718K 令牌。继续？"
3. 用户确认
4. 部署带有完整时间线的分析代理
5. 保存到 `./journey-into-tokyo.md`
6. 报告："报告已保存。分析了 34,722 个观察记录，跨越 2025 年 10 月 - 2026 年 3 月（~718K 输入令牌，~8K 输出令牌）。"
