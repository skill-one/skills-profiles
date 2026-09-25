# GitHub 研究技能

## 触发条件

在用户想要执行以下操作时激活此技能：
- "查找关于 [主题] 的仓库"，"GitHub 研究 [主题]"
- "分析关于 [主题] 的开源代码"
- "查找 [论文/技术] 的实现"
- "哪些仓库实现了 [算法]？"
- 使用 `/github-research <deep-research-output-dir>` 命令

## 概述

此技能系统地发现、评估和深入分析与研究主题相关的 GitHub 仓库。它读取 **deep-research** 输出（论文数据库、阶段报告、代码引用）并生成可操作的集成蓝图，用于重用开源代码。

**安装位置**：`~/.claude/skills/github-research/` — 脚本、参考和此技能定义。
**输出**：相对于当前工作目录的 `./github-research-output/{slug}/`。
**输入**：一个 deep-research 输出目录（包含 `paper_db.jsonl`、阶段报告、`code_repos.md` 等）

## 6阶段流程

```
阶段1：摄入     → 从 deep-research 输出中提取引用、URL、关键词
阶段2：发现     → 多源广泛 GitHub 搜索（50-200 个仓库）
阶段3：筛选     → 评分和排名 → 选择前 15-30 个仓库
阶段4：深入分析 → 克隆并深入分析前 8-15 个仓库（代码阅读）
阶段5：分析     → 每个仓库报告 + 交叉仓库比较
阶段6：蓝图     → 研究主题的集成/重用计划
```

## 输出目录结构

```
github-research-output/{slug}/
├── repo_db.jsonl                     # 主仓库数据库
├── phase1_intake/
│   ├── extracted_refs.jsonl          # URL、关键词、论文-仓库链接
│   └── intake_summary.md
├── phase2_discovery/
│   ├── search_results/               # 每次搜索的原始 JSONL
│   └── discovery_log.md
├── phase3_filtering/
│   ├── ranked_repos.jsonl            # 评分和排名的子集
│   └── filtering_report.md
├── phase4_deep_dive/
│   ├── repos/                        # 克隆的仓库（浅层）
│   ├── analyses/                     # 每个仓库分析的 .md 文件
│   └── deep_dive_summary.md
├── phase5_analysis/
│   ├── comparison_matrix.md          # 交叉仓库比较
│   ├── technique_map.md              # 论文概念 → 代码映射
│   └── analysis_report.md
└── phase6_blueprint/
    ├── integration_plan.md           # 如何组合仓库
    ├── reuse_catalog.md              # 可重用组件目录
    ├── final_report.md               # 完整编译报告
    └── blueprint_summary.md
```

## 脚本参考

所有脚本都是 Python 3，仅使用标准库，位于 `~/.claude/skills/github-research/scripts/`。

| 脚本               | 目的               | 关键标志             |
|--------------------|--------------------|----------------------|
| `extract_research_refs.py` | 解析 deep-research 输出中的 GitHub URL、论文引用、关键词 | `--research-dir`, `--output` |
| `search_github.py`  | 通过 `gh api` 搜索 GitHub 仓库 | `--query`, `--language`, `--min-stars`, `--sort`, `--max-results`, `--topic`, `--output` |
| `search_github_code.py` | 搜索 GitHub 代码以查找实现 | `--query`, `--language`, `--filename`, `--max-results`, `--output` |
| `search_paperswithcode.py` | 在 Papers With Code 中搜索论文→仓库映射 | `--paper-title`, `--arxiv-id`, `--query`, `--output` |
| `repo_db.py`        | JSONL 仓库数据库管理 | 子命令：`merge`, `filter`, `score`, `search`, `tag`, `stats`, `export`, `rank` |
| `repo_metadata.py`  | 通过 `gh api` 获取详细元数据 | `--repos`, `--input`, `--output`, `--delay` |
| `clone_repo.py`     | 浅层克隆仓库以进行分析 | `--repo`, `--output-dir`, `--depth`, `--branch` |
| `analyze_repo_structure.py` | 映射文件树、关键文件、LOC 统计 | `--repo-dir`, `--output` |
| `extract_dependencies.py` | 提取和解析依赖文件 | `--repo-dir`, `--output` |
| `find_implementations.py` | 在克隆的仓库中搜索特定代码模式 | `--repo-dir`, `--patterns`, `--output` |
| `repo_readme_fetch.py` | 获取 README 而不克隆 | `--repos`, `--input`, `--output`, `--max-chars` |
| `compare_repos.py`   | 生成跨仓库的比较矩阵 | `--input`, `--output` |
| `compile_github_report.py` | 从所有阶段组装最终报告 | `--topic-dir` |

---

## 阶段1：摄入

**目标**：从 deep-research 输出中提取所有相关引用、URL 和关键词。

### 步骤

1. **创建输出目录结构**：
   ```bash
   SLUG=$(echo "$TOPIC" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9-')
   mkdir -p github-research-output/$SLUG/{phase1_intake,phase2_discovery/search_results,phase3_filtering,phase4_deep_dive/{repos,analyses},phase5_analysis,phase6_blueprint}
   ```

2. **从 deep-research 输出中提取引用**：
   ```bash
   python ~/.claude/skills/github-research/scripts/extract_research_refs.py \
     --research-dir <deep-research-output-dir> \
     --output github-research-output/$SLUG/phase1_intake/extracted_refs.jsonl
   ```

3. **审查提取的引用**：阅读生成的 JSONL。注意：
   - 报告中直接发现的 GitHub URL
   - 论文标题和 arxiv ID（用于 Papers With Code 查找）
   - 研究关键词和主题（用于 GitHub 搜索查询）

4. **编写摄入摘要**：创建 `phase1_intake/intake_summary.md`，包含：
   - 直接找到的 GitHub URL 数量
   - 具有潜在代码链接的论文数量
   - 提取的关键研究主题
   - 为阶段2计划的搜索查询

### 检查点
- `extracted_refs.jsonl` 存在并包含条目
- `intake_summary.md` 已编写
- 记录搜索策略

---

## 阶段2：发现

**目标**：广泛搜索，从多个来源找到 50-200 个候选仓库。

### 步骤

1. **通过直接 URL 搜索**：任何来自阶段1的 GitHub URL → 获取元数据：
   ```bash
   python ~/.claude/skills/github-research/scripts/repo_metadata.py \
     --repos owner1/name1 owner2/name2 ... \
     --output github-research-output/$SLUG/phase2_discovery/search_results/direct_urls.jsonl
   ```

2. **搜索 Papers With Code**：对于每个具有 arxiv ID 的论文：
   ```bash
   python ~/.claude/skills/github-research/scripts/search_paperswithcode.py \
     --arxiv-id 2401.12345 \
     --output github-research-output/$SLUG/phase2_discovery/search_results/pwc_2401.12345.jsonl
   ```

3. **通过关键词搜索 GitHub**（基于研究主题的 3-8 个查询）：
   ```bash
   python ~/.claude/skills/github-research/scripts/search_github.py \
     --query "multi-agent LLM coordination" \
     --min-stars 10 --sort stars --max-results 50 \
     --output github-research-output/$SLUG/phase2_discovery/search_results/gh_query1.jsonl
   ```

4. **搜索 GitHub 代码**（用于特定实现）：
   ```bash
   python ~/.claude/skills/github-research/scripts/search_github_code.py \
     --query "class MultiAgentOrchestrator" \
     --language python --max-results 30 \
     --output github-research-output/$SLUG/phase2_discovery/search_results/code_query1.jsonl
   ```

5. **为缺少描述的仓库获取 README**：
   ```bash
   python ~/.claude/skills/github-research/scripts/repo_readme_fetch.py \
     --input <repos.jsonl> \
     --output github-research-output/$SLUG/phase2_discovery/search_results/readmes.jsonl
   ```

6. **合并所有结果到主数据库**：
   ```bash
   python ~/.claude/skills/github-research/scripts/repo_db.py merge \
     --inputs github-research-output/$SLUG/phase2_discovery/search_results/*.jsonl \
     --output github-research-output/$SLUG/repo_db.jsonl
   ```

7. **编写发现日志**：创建 `phase2_discovery/discovery_log.md`，包含：
   - 使用的搜索查询
   - 每个来源的结果
   - 找到的唯一仓库总数

### 速率限制
- GitHub 搜索 API：每分钟 30 个请求（认证）
- Papers With Code API：无严格限制但需尊重（1 请求/秒）
- 需要时在批量操作中添加 `--delay 1.0`

### 检查点
- `repo_db.jsonl` 包含 50-200 个仓库
- `discovery_log.md` 包含搜索详情

---

## 阶段3：筛选

**目标**：评分和排名仓库，选择 15-30 个进行深入分析。

### 步骤

1. **为所有仓库丰富元数据**：
   ```bash
   python ~/.claude/skills/github-research/scripts/repo_metadata.py \
     --input github-research-output/$SLUG/repo_db.jsonl \
     --output github-research-output/$SLUG/repo_db.jsonl \
     --delay 0.5
   ```

2. **评分仓库**（质量和活跃度评分）：
   ```bash
   python ~/.claude/skills/github-research/scripts/repo_db.py score \
     --input github-research-output/$SLUG/repo_db.jsonl \
     --output github-research-output/$SLUG/repo_db.jsonl
   ```

3. **LLM 相关性评分**：阅读排名前 ~50 的仓库，根据：
   - 直接与研究主题的相关性
   - 实现完整性
   - 代码质量信号（来自 README、描述）
   - 更新相关性分数：
   ```bash
   python ~/.claude/skills/github-research/scripts/repo_db.py tag \
     --input github-research-output/$SLUG/repo_db.jsonl \
     --ids owner/name --tags "relevance:0.85"
   ```

4. **计算复合分数和排名**：
   ```bash
   python ~/.claude/skills/github-research/scripts/repo_db.py score \
     --input github-research-output/$SLUG/repo_db.jsonl \
     --output github-research-output/$SLUG/repo_db.jsonl
   python ~/.claude/skills/github-research/scripts/repo_db.py rank \
     --input github-research-output/$SLUG/repo_db.jsonl \
     --output github-research-output/$SLUG/phase3_filtering/ranked_repos.jsonl \
     --by composite_score
   ```

5. **选择顶级仓库**：过滤到前 15-30：
   ```bash
   python ~/.claude/skills/github-research/scripts/repo_db.py filter \
     --input github-research-output/$SLUG/phase3_filtering/ranked_repos.jsonl \
     --output github-research-output/$SLUG/phase3_filtering/ranked_repos.jsonl \
     --max-repos 30 --not-archived
   ```

6. **编写筛选报告**：创建 `phase3_filtering/filtering_report.md`：
   - 筛选前后的统计数据
   - 评分分布
   - 前30个仓库的分数和理由

### 评分公式
```
activity_score = sigmoid((days_since_push < 90) * 0.4 + has_recent_commits * 0.3 + open_issues_ratio * 0.3)
quality_score  = normalize(log(stars+1) * 0.3 + log(forks+1) * 0.2 + has_license * 0.15 + has_readme * 0.15 + not_archived * 0.2)
composite_score = relevance * 0.4 + quality * 0.35 + activity * 0.25
```

### 检查点
- `ranked_repos.jsonl` 包含 15-30 个仓库
- `filtering_report.md` 包含评分详情

---

## 阶段4：深入分析

**目标**：克隆并深入分析前 8-15 个仓库。

### 步骤

1. **选择深入分析的仓库**：从排名列表中取前 8-15。

2. **克隆每个仓库**（浅层）：
   ```bash
   python ~/.claude/skills/github-research/scripts/clone_repo.py \
     --repo owner/name \
     --output-dir github-research-output/$SLUG/phase4_deep_dive/repos/
   ```

3. **分析每个克隆仓库的结构**：
   ```bash
   python ~/.claude/skills/github-research/scripts/analyze_repo_structure.py \
     --repo-dir github-research-output/$SLUG/phase4_deep_dive/repos/name/ \
     --output github-research-output/$SLUG/phase4_deep_dive/analyses/name_structure.json
   ```

4. **提取依赖**：
   ```bash
   python ~/.claude/skills/github-research/scripts/extract_dependencies.py \
     --repo-dir github-research-output/$SLUG/phase4_deep_dive/repos/name/ \
     --output github-research-output/$SLUG/phase4_deep_dive/analyses/name_deps.json
   ```

5. **查找实现**：搜索研究中的关键算法/概念：
   ```bash
   python ~/.claude/skills/github-research/scripts/find_implementations.py \
     --repo-dir github-research-output/$SLUG/phase4_deep_dive/repos/name/ \
     --patterns "class Transformer" "def forward" "attention" \
     --output github-research-output/$SLUG/phase4_deep_dive/analyses/name_impls.jsonl
   ```

6. **深入代码阅读**：对于每个仓库，阅读结构分析确定的关键源文件。在 `phase4_deep_dive/analyses/{name}_analysis.md` 中编写每个仓库分析：
   - 架构概述
   - 实现的关键算法
   - 代码质量评估
   - API / 接口设计
   - 依赖和需求
   - 优势和局限性
   - 可重用性评估（提取组件的容易程度）

7. **编写深入分析摘要**：`phase4_deep_dive/deep_dive_summary.md`

### 重要提示：实际阅读代码

不要只总结 README。你必须：
- 阅读主源文件（入口点、核心模块）
- 理解实际实现方法
- 识别实现研究概念的具体函数/类
- 记录代码模式、设计决策和权衡

### 检查点
- `repos/` 中克隆的仓库
- `analyses/` 中的每个仓库分析文件
- `deep_dive_summary.md` 已编写

---

## 阶段5：分析

**目标**：跨仓库比较和技术→代码映射。

### 步骤

1. **生成比较矩阵**：
   ```bash
   python ~/.claude/skills/github-research/scripts/compare_repos.py \
     --input github-research-output/$SLUG/phase4_deep_dive/analyses/ \
     --output github-research-output/$SLUG/phase5_analysis/comparison.json
   ```

2. **编写比较矩阵**：创建 `phase5_analysis/comparison_matrix.md`：
   - 比较仓库跨维度（语言、LOC、stars、框架、许可证、测试）的表格
   - 依赖重叠分析
   - 每个仓库的优缺点

3. **编写技术映射**：创建 `phase5_analysis/technique_map.md`：
   - 将每个论文概念/研究技术 → 具体仓库 + 文件 + 函数
   - 识别缺失（未找到实现的技术）
   - 记录同一概念的不同实现

4. **编写分析报告**：`phase5_analysis/analysis_report.md`：
   - 查找的执行摘要
   - 代码分析的要点
   - 建议使用哪些仓库及其用途

### 检查点
- `comparison_matrix.md` 包含仓库比较表
- `technique_map.md` 将概念映射到代码
- `analysis_report.md` 包含发现

---

## 阶段6：蓝图

**目标**：生成可操作的集成和重用计划。

### 步骤

1. **编写集成计划**：`phase6_blueprint/integration_plan.md`：
   - 推荐的组合仓库架构
   - 步骤式集成方法
   - 依赖解析策略
   - 潜在冲突及解决方法

2. **编写重用目录**：`phase6_blueprint/reuse_catalog.md`：
   - 对于每个可重用组件：源仓库、文件路径、函数/类、功能、如何提取
   - 许可证兼容性矩阵
   - 努力估计（容易/中等/困难）

3. **编译最终报告**：
   ```bash
   python ~/.claude/skills/github-research/scripts/compile_github_report.py \
     --topic-dir github-research-output/$SLUG/
   ```

4. **编写蓝图摘要**：`phase6_blueprint/blueprint_summary.md`：
   - 一页执行摘要
   - 前5个仓库及原因
   - 推荐的下一步行动

### 检查点
- `integration_plan.md` 完成
- `reuse_catalog.md` 包含组件目录
- `final_report.md` 编译
- `blueprint_summary.md` 作为执行摘要

---

## 质量规范

1. **仓库按复合分数排名**：`relevance × 0.4 + quality × 0.35 + activity × 0.25`
2. **深入分析需要阅读实际代码**，不只是 README
3. **集成蓝图必须将论文概念 → 具体代码文件/函数**
4. **增量保存**：每个阶段立即写入磁盘
5. **检查点恢复**：可以从任何阶段恢复，检查已存在的输出
6. **所有脚本仅使用标准库 Python** — 无需 pip 安装
7. **`gh` CLI 是必需的**，用于 GitHub API 访问（必须认证）
8. **按 `repo_id`（owner/name）跨所有搜索去重**
9. **速率限制意识**：尊重 GitHub 搜索 API 限制（每分钟 30 请求）

## 错误处理

- 如果 `gh` 未安装：警告用户并提供安装说明
- 如果仓库已归档/删除：优雅跳过，记录在日志中
- 如果克隆失败：跳过，记录在日志中，继续剩余仓库
- 如果 Papers With Code API 不可用：跳过，仅依赖 GitHub 搜索
- 始终将部分进度写入磁盘，以免丢失工作

## 参考

- 参考 `references/phase-guide.md` 获取详细的阶段执行指导
- Deep-research 技能：`~/.claude/skills/deep-research/SKILL.md`
- 论文数据库模式：`~/.claude/skills/deep-research/scripts/paper_db.py`
