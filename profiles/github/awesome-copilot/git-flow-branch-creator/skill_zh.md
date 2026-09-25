### 说明

```xml
<instructions>
	<title>Git Flow 分支创建器</title>
	<description>此提示通过使用 git status 和 git diff（或 git diff --cached）分析您当前的 git 变更，然后根据 Git Flow 分支模型智能地确定适当的分支类型，并创建语义化的分支名称。</description>
	<note>
		只需运行此提示，Copilot 将为您分析变更并创建适当的 Git Flow 分支。
	</note>
</instructions>
```

### 工作流程

**请按照以下步骤操作：**

1. 运行 `git status` 以查看当前仓库状态和已更改的文件。
2. 运行 `git diff`（用于未暂存的变更）或 `git diff --cached`（用于已暂存的变更）以分析变更的性质。
3. 使用下方的 Git Flow 分支分析框架分析变更。
4. 根据分析确定适当的分支类型。
5. 遵循 Git Flow 规范生成语义化的分支名称。
6. 自动创建分支并切换到该分支。
7. 提供分析摘要和下一步操作。

### Git Flow 分支分析框架

```xml
<analysis-framework>
	<branch-types>
		<feature>
			<purpose>新功能、增强、非关键改进</purpose>
			<branch-from>develop</branch-from>
			<merge-to>develop</merge-to>
			<naming>feature/描述性名称 或 feature/工单号描述</naming>
			<indicators>
				<indicator>正在添加新功能</indicator>
				<indicator>UI/UX 改进</indicator>
				<indicator>新增 API 端点或方法</indicator>
				<indicator>数据库模式添加（非破坏性）</indicator>
				<indicator>新增配置选项</indicator>
				<indicator>非关键的性能改进</indicator>
			</indicators>
		</feature>

		<release>
			<purpose>发布准备、版本号更新、最终测试</purpose>
			<branch-from>develop</branch-from>
			<merge-to>develop AND master</merge-to>
			<naming>release-X.Y.Z</naming>
			<indicators>
				<indicator>版本号变更</indicator>
				<indicator>构建配置更新</indicator>
				<indicator>文档最终化</indicator>
				<indicator>发布前的次要 Bug 修复</indicator>
				<indicator>发布说明更新</indicator>
				<indicator>依赖版本锁定</indicator>
			</indicators>
		</release>

		<hotfix>
			<purpose>需要立即部署的关键生产 Bug 修复</purpose>
			<branch-from>master</branch-from>
			<merge-to>develop AND master</merge-to>
			<naming>hotfix-X.Y.Z 或 hotfix/关键问题描述</naming>
			<indicators>
				<indicator>安全漏洞修复</indicator>
				<indicator>关键生产 Bug</indicator>
				<indicator>数据损坏修复</indicator>
				<indicator>服务中断解决</indicator>
				<indicator>紧急配置变更</indicator>
			</indicators>
		</hotfix>
	</branch-types>
</analysis-framework>
```

### 分支命名规范

```xml
<naming-conventions>
	<feature-branches>
		<format>feature/[工单号-]描述性名称</format>
		<examples>
			<example>feature/user-authentication</example>
			<example>feature/PROJ-123-shopping-cart</example>
			<example>feature/api-rate-limiting</example>
			<example>feature/dashboard-redesign</example>
		</examples>
	</feature-branches>

	<release-branches>
		<format>release-X.Y.Z</format>
		<examples>
			<example>release-1.2.0</example>
			<example>release-2.1.0</example>
			<example>release-1.0.0</example>
		</examples>
	</release-branches>

	<hotfix-branches>
		<format>hotfix-X.Y.Z OR hotfix/关键描述</format>
		<examples>
			<example>hotfix-1.2.1</example>
			<example>hotfix/security-patch</example>
			<example>hotfix/payment-gateway-fix</example>
			<example>hotfix-2.1.1</example>
		</examples>
	</hotfix-branches>
</naming-conventions>
```

### 分析过程

```xml
<analysis-process>
	<step-1>
		<title>变更性质分析</title>
		<description>检查已修改的文件类型和变更的性质</description>
		<criteria>
			<files-modified>查看文件扩展名、目录结构和用途</files-modified>
			<change-scope>确定变更是否为添加性、纠正性或准备性</change-scope>
			<urgency-level>评估变更是否解决关键问题或为开发性变更</urgency-level>
		</criteria>
	</step-1>

	<step-2>
		<title>Git Flow 分类</title>
		<description>将变更映射到适当的 Git Flow 分支类型</description>
		<decision-tree>
			<question>这些是生产问题的关键修复吗？</question>
			<if-yes>考虑 hotfix 分支</if-yes>
			<if-no>
				<question>这些是发布准备变更（版本号更新、最终调整）吗？</question>
				<if-yes>考虑 release 分支</if-yes>
				<if-no>默认为 feature 分支</if-no>
			</if-no>
		</decision-tree>
	</step-2>

	<step-3>
		<title>分支名称生成</title>
		<description>创建语义化的、描述性的分支名称</description>
		<guidelines>
			<use-kebab-case>使用小写和连字符</use-kebab-case>
			<be-descriptive>名称应清晰地表明用途</be-descriptive>
			<include-context>在可用时添加工单号或项目上下文</include-context>
			<keep-concise>避免过长的名称</keep-concise>
		</guidelines>
	</step-3>
</analysis-process>
```

### 边缘情况和验证

```xml
<edge-cases>
	<mixed-changes>
		<scenario>变更包含功能和 Bug 修复</scenario>
		<resolution>优先考虑最关键的变更类型或建议拆分为多个分支</resolution>
	</mixed-changes>

	<no-changes>
		<scenario>git status/diff 中未检测到变更</scenario>
		<resolution>通知用户并建议检查 git status 或先进行变更</resolution>
	</no-changes>

	<existing-branch>
		<scenario>已在 feature/hotfix/release 分支上</scenario>
		<resolution>分析是否需要新分支或当前分支是否合适</resolution>
	</existing-branch>

	<conflicting-names>
		<scenario>建议的分支名称已存在</scenario>
		<resolution>追加增量后缀或建议替代名称</resolution>
	</conflicting-names>
</edge-cases>
```

### 示例

```xml
<examples>
	<example-1>
		<scenario>添加了新的用户注册 API 端点</scenario>
		<analysis>新功能、添加性变更、非关键</analysis>
		<branch-type>feature</branch-type>
		<branch-name>feature/user-registration-api</branch-name>
		<command>git checkout -b feature/user-registration-api develop</command>
	</example-1>

	<example-2>
		<scenario>修复了认证中的关键安全漏洞</scenario>
		<analysis>安全修复、关键，需要立即部署</analysis>
		<branch-type>hotfix</branch-type>
		<branch-name>hotfix/auth-security-patch</branch-name>
		<command>git checkout -b hotfix/auth-security-patch master</command>
	</example-2>

	<example-3>
		<scenario>更新版本到 2.1.0 并最终化发布说明</scenario>
		<analysis>发布准备、版本号更新、文档</analysis>
		<branch-type>release</branch-type>
		<branch-name>release-2.1.0</branch-name>
		<command>git checkout -b release-2.1.0 develop</command>
	</example-3>

	<example-4>
		<scenario>改进了数据库查询性能并更新了缓存</scenario>
		<analysis>性能改进、非关键增强</analysis>
		<branch-type>feature</branch-type>
		<branch-name>feature/database-performance-optimization</branch-name>
		<command>git checkout -b feature/database-performance-optimization develop</command>
	</example-4>
</examples>
```

### 验证清单

```xml
<validation>
	<pre-analysis>
		<check>仓库处于干净状态（没有会冲突的未提交变更）</check>
		<check>当前分支是合适的起点（develop 用于功能/发布，master 用于 hotfix）</check>
		<check>远程仓库是最新的</check>
	</pre-analysis>

	<analysis-quality>
		<check>变更分析涵盖了所有已修改的文件</check>
		<check>分支类型选择遵循 Git Flow 原则</check>
		<check>分支名称是语义化的并遵循规范</check>
		<check>考虑并处理了边缘情况</check>
	</analysis-quality>

	<execution-safety>
		<check>目标分支（develop/master）存在且可访问</check>
		<check>建议的分支名称不与现有分支冲突</check>
		<check>用户具有创建分支的适当权限</check>
	</execution-safety>
</validation>
```

### 最终执行

```xml
<execution-protocol>
	<analysis-summary>
		<git-status>git status 命令的输出</git-status>
		<git-diff>git diff 输出的相关部分</git-diff>
		<change-analysis>变更代表的详细分析</change-analysis>
		<branch-decision>解释为什么选择了特定分支类型</branch-decision>
	</analysis-summary>

	<branch-creation>
		<command>git checkout -b [branch-name] [source-branch]</command>
		<confirmation>验证分支创建和当前分支状态</confirmation>
		<next-steps>提供下一步操作指导（提交变更、推送分支等）</next-steps>
	</branch-creation>

	<fallback-options>
		<alternative-names>如果主要建议不合适，建议 2-3 个替代分支名称</alternative-names>
		<manual-override>如果分析似乎不正确，允许用户指定不同的分支类型</manual-override>
	</fallback-options>
</execution-protocol>
```

### Git Flow 参考

```xml
<gitflow-reference>
	<main-branches>
		<master>可生产代码，每个提交都是发布</master>
		<develop>功能集成分支，最新的开发变更</develop>
	</main-branches>

	<supporting-branches>
		<feature>从 develop 分支，合并回 develop</feature>
		<release>从 develop 分支，合并到 develop 和 master</release>
		<hotfix>从 master 分支，合并到 develop 和 master</hotfix>
	</supporting-branches>

	<merge-strategy>
		<flag>始终使用 --no-ff 标志以保留分支历史</flag>
		<tagging>在 master 分支上标记发布</tagging>
		<cleanup>成功合并后删除分支</cleanup>
	</merge-strategy>
</gitflow-reference>
```
