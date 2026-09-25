# anthropic-cybersecurity-skills

> 技能由 [ara.so](https://ara.so) 提供 — 安全技能集合。

## 概述

Anthropic Cybersecurity Skills 库提供了涵盖 26 个安全领域的 754 个生产级网络安全技能。每个技能都遵循 agentskills.io 标准，并映射到五个行业框架：MITRE ATT&CK、NIST CSF 2.0、MITRE ATLAS、MITRE D3FEND 和 NIST AI RMF。这使得 AI 代理能够在专家级指导下执行安全操作。

## 安装

```bash
# 选项 1：使用 npx（推荐）
npx skills add mukul975/Anthropic-Cybersecurity-Skills

# 选项 2：Git 克隆
git clone https://github.com/mukul975/Anthropic-Cybersecurity-Skills.git
cd Anthropic-Cybersecurity-Skills

# 选项 3：作为子模块添加
git submodule add https://github.com/mukul975/Anthropic-Cybersecurity-Skills.git skills/cybersecurity
```

## 目录结构

```
skills/
├── {skill-name}/
│   ├── SKILL.md              # 技能定义，带有 YAML 前置文本
│   ├── references/
│   │   ├── standards.md      # 框架映射
│   │   └── workflows.md      # 技术流程
│   ├── scripts/
│   │   └── *.py              # 辅助脚本
│   └── assets/
│       └── *.md              # 模板和清单
```

## 发现技能

### 按领域

技能被组织成 26 个领域。列出所有领域：

```python
import os
import yaml

def list_domains():
    domains = {}
    for skill_dir in os.listdir('skills'):
        skill_path = f'skills/{skill_dir}/SKILL.md'
        if os.path.exists(skill_path):
            with open(skill_path, 'r') as f:
                content = f.read()
                # 提取 YAML 前置文本
                if content.startswith('---'):
                    yaml_end = content.find('---', 3)
                    frontmatter = yaml.safe_load(content[3:yaml_end])
                    domain = frontmatter.get('domain', 'unknown')
                    subdomain = frontmatter.get('subdomain', 'general')
                    
                    if domain not in domains:
                        domains[domain] = {}
                    if subdomain not in domains[domain]:
                        domains[domain][subdomain] = []
                    domains[domain][subdomain].append(frontmatter['name'])
    
    return domains

# 使用
domains = list_domains()
for domain, subdomains in domains.items():
    print(f"\n{domain.upper()}")
    for subdomain, skills in subdomains.items():
        print(f"  {subdomain}: {len(skills)} 个技能")
```

### 按框架映射

查找映射到特定 ATT&CK 技术的技能：

```python
def find_by_attack_technique(technique_id):
    """查找映射到特定 ATT&CK 技术的技能"""
    matching_skills = []
    
    for skill_dir in os.listdir('skills'):
        skill_path = f'skills/{skill_dir}/SKILL.md'
        if os.path.exists(skill_path):
            with open(skill_path, 'r') as f:
                content = f.read()
                if content.startswith('---'):
                    yaml_end = content.find('---', 3)
                    frontmatter = yaml.safe_load(content[3:yaml_end])
                    
                    # 检查 ATT&CK 映射在 references 中
                    refs_path = f'skills/{skill_dir}/references/standards.md'
                    if os.path.exists(refs_path):
                        with open(refs_path, 'r') as ref_file:
                            if technique_id in ref_file.read():
                                matching_skills.append({
                                    'name': frontmatter['name'],
                                    'description': frontmatter['description'],
                                    'path': skill_path
                                })
    
    return matching_skills

# 使用
skills = find_by_attack_technique('T1003')  # 凭据转储
for skill in skills:
    print(f"{skill['name']}: {skill['description']}")
```

### 按标签

通过标签搜索技能：

```python
def search_by_tags(search_tags):
    """查找匹配提供的任何标签的技能"""
    results = []
    
    for skill_dir in os.listdir('skills'):
        skill_path = f'skills/{skill_dir}/SKILL.md'
        if os.path.exists(skill_path):
            with open(skill_path, 'r') as f:
                content = f.read()
                if content.startswith('---'):
                    yaml_end = content.find('---', 3)
                    frontmatter = yaml.safe_load(content[3:yaml_end])
                    
                    skill_tags = frontmatter.get('tags', [])
                    if any(tag in skill_tags for tag in search_tags):
                        results.append(frontmatter)
    
    return results

# 使用
malware_skills = search_by_tags(['malware-analysis', 'reverse-engineering'])
for skill in malware_skills:
    print(f"{skill['name']}: {', '.join(skill['tags'])}")
```

## 加载和执行技能

### 渐进式加载模式

仅加载前置文本（低 token 成本），当需要时再加载完整内容：

```python
class SkillLoader:
    def __init__(self, skills_dir='skills'):
        self.skills_dir = skills_dir
    
    def scan_all_frontmatter(self):
        """扫描所有技能前置文本（每个约 30 个 token）"""
        skills_index = []
        
        for skill_dir in os.listdir(self.skills_dir):
            skill_path = f'{self.skills_dir}/{skill_dir}/SKILL.md'
            if os.path.exists(skill_path):
                with open(skill_path, 'r') as f:
                    content = f.read()
                    if content.startswith('---'):
                        yaml_end = content.find('---', 3)
                        frontmatter = yaml.safe_load(content[3:yaml_end])
                        frontmatter['path'] = skill_path
                        skills_index.append(frontmatter)
        
        return skills_index
    
    def load_full_skill(self, skill_name):
        """加载完整技能内容（约 500-2000 个 token）"""
        skill_path = f'{self.skills_dir}/{skill_name}/SKILL.md'
        
        with open(skill_path, 'r') as f:
            content = f.read()
        
        # 解析前置文本和正文
        if content.startswith('---'):
            yaml_end = content.find('---', 3)
            frontmatter = yaml.safe_load(content[3:yaml_end])
            body = content[yaml_end + 3:].strip()
            
            return {
                'metadata': frontmatter,
                'content': body,
                'references': self._load_references(skill_name),
                'scripts': self._load_scripts(skill_name)
            }
    
    def _load_references(self, skill_name):
        """加载框架映射和工作流"""
        refs = {}
        refs_dir = f'{self.skills_dir}/{skill_name}/references'
        
        if os.path.exists(refs_dir):
            for ref_file in os.listdir(refs_dir):
                with open(f'{refs_dir}/{ref_file}', 'r') as f:
                    refs[ref_file.replace('.md', '')] = f.read()
        
        return refs
    
    def _load_scripts(self, skill_name):
        """加载辅助脚本"""
        scripts = {}
        scripts_dir = f'{self.skills_dir}/{skill_name}/scripts'
        
        if os.path.exists(scripts_dir):
            for script_file in os.listdir(scripts_dir):
                with open(f'{scripts_dir}/{script_file}', 'r') as f:
                    scripts[script_file] = f.read()
        
        return scripts

# 使用
loader = SkillLoader()

# 第 1 步：扫描所有技能（轻量级）
all_skills = loader.scan_all_frontmatter()
print(f"找到 {len(all_skills)} 个技能")

# 第 2 步：查找相关技能
memory_forensics = [s for s in all_skills if 'memory-analysis' in s.get('tags', [])]

# 第 3 步：加载前三个匹配的完整技能
for skill in memory_forensics[:3]:
    full_skill = loader.load_full_skill(skill['name'])
    print(f"\n{skill['name']}")
    print(f"内容长度: {len(full_skill['content'])} 字符")
```

## 常见使用模式

### 事件响应工作流

```python
def incident_response_guide(incident_type):
    """获取与事件类型相关的事件响应技能"""
    loader = SkillLoader()
    all_skills = loader.scan_all_frontmatter()
    
    # 将事件类型映射到技能领域
    incident_mappings = {
        'ransomware': ['malware-analysis', 'incident-response', 'forensics'],
        'data_breach': ['threat-hunting', 'forensics', 'cloud-security'],
        'phishing': ['email-security', 'threat-intelligence', 'endpoint-security'],
        'insider_threat': ['behavior-analytics', 'iam', 'forensics']
    }
    
    relevant_tags = incident_mappings.get(incident_type, [])
    relevant_skills = [
        s for s in all_skills 
        if any(tag in s.get('tags', []) for tag in relevant_tags)
    ]
    
    # 按子领域优先排序
    prioritized = sorted(
        relevant_skills,
        key=lambda s: (
            s.get('subdomain') == 'incident-response',
            len(set(s.get('tags', [])) & set(relevant_tags))
        ),
        reverse=True
    )
    
    return prioritized[:5]

# 使用
ransomware_skills = incident_response_guide('ransomware')
for skill in ransomware_skills:
    print(f"- {skill['name']}: {skill['description']}")
```

### ATT&CK 技术覆盖范围

```python
def check_attack_coverage(technique_id):
    """检查哪些技能覆盖特定 ATT&CK 技术"""
    loader = SkillLoader()
    
    coverage = []
    for skill_dir in os.listdir('skills'):
        refs_path = f'skills/{skill_dir}/references/standards.md'
        if os.path.exists(refs_path):
            with open(refs_path, 'r') as f:
                content = f.read()
                if technique_id in content:
                    skill = loader.load_full_skill(skill_dir)
                    coverage.append({
                        'name': skill['metadata']['name'],
                        'description': skill['metadata']['description'],
                        'domain': skill['metadata']['subdomain']
                    })
    
    return coverage

# 使用
t1003_coverage = check_attack_coverage('T1003')  # 凭据转储
print(f"覆盖 T1003 的技能: {len(t1003_coverage)}")
for skill in t1003_coverage:
    print(f"  {skill['domain']}: {skill['name']}")
```

### 多框架合规性检查

```python
def compliance_mapper(skill_name):
    """显示技能的所有框架映射"""
    loader = SkillLoader()
    skill = loader.load_full_skill(skill_name)
    
    frameworks = {
        'MITRE ATT&CK': skill['metadata'].get('attack_techniques', []),
        'NIST CSF 2.0': skill['metadata'].get('nist_csf', []),
        'MITRE ATLAS': skill['metadata'].get('atlas_techniques', []),
        'MITRE D3FEND': skill['metadata'].get('d3fend_techniques', []),
        'NIST AI RMF': skill['metadata'].get('nist_ai_rmf', [])
    }
    
    print(f"\n{skill_name} 的框架映射\n")
    for framework, mappings in frameworks.items():
        if mappings:
            print(f"{framework}:")
            for mapping in mappings:
                print(f"  - {mapping}")

# 使用
compliance_mapper('performing-memory-forensics-with-volatility3')
```

## 使用技能脚本

许多技能在 `scripts/` 目录中包含辅助脚本：

```python
import subprocess
import json

def execute_skill_script(skill_name, script_name, **kwargs):
    """执行技能的辅助脚本，带参数"""
    script_path = f'skills/{skill_name}/scripts/{script_name}'
    
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"脚本未找到: {script_path}")
    
    # 构建带参数的命令
    cmd = ['python', script_path]
    for key, value in kwargs.items():
        cmd.extend([f'--{key}', str(value)])
    
    # 执行
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    return {
        'stdout': result.stdout,
        'stderr': result.stderr,
        'returncode': result.returncode
    }

# 使用示例，内存取证技能
result = execute_skill_script(
    'performing-memory-forensics-with-volatility3',
    'process.py',
    dump_file='/path/to/memory.dmp',
    plugin='windows.pslist'
)

if result['returncode'] == 0:
    print(result['stdout'])
else:
    print(f"错误: {result['stderr']}")
```

## 环境配置

需要 API 密钥或凭证的技能参考环境变量：

```bash
# .env 文件，用于需要外部服务的技能
export VIRUSTOTAL_API_KEY=your_vt_key_here
export SHODAN_API_KEY=your_shodan_key_here
export MISP_URL=https://your-misp-instance.com
export MISP_API_KEY=your_misp_key_here
export SPLUNK_HOST=your-splunk-host
export SPLUNK_TOKEN=your_splunk_token
```

在 Python 中加载：

```python
import os
from dotenv import load_dotenv

load_dotenv()

# 技能将参考这些
vt_key = os.getenv('VIRUSTOTAL_API_KEY')
misp_url = os.getenv('MISP_URL')
```

## 集成示例

### 与 Claude Code / Cursor

放在项目的 `.claud/` 或 `.cursorrules` 中：

```markdown
# Cybersecurity Skills Context

此项目有访问 `skills/` 目录中的 754 个网络安全技能。

当我问安全问题时：
1. 扫描 skills/*/SKILL.md 中的技能前置文本
2. 按领域、子领域或标签匹配
3. 完全加载前三个相关技能
4. 按照工作流部分逐步执行
5. 使用验证部分验证结果

示例: "分析这个内存转储"
→ 加载 performing-memory-forensics-with-volatility3/SKILL.md
→ 执行 Volatility3 命令来自工作流
→ 使用验证清单验证结果
```

### 与自定义 AI 代理（Python）

```python
class CybersecurityAgent:
    def __init__(self, skills_dir='skills'):
        self.loader = SkillLoader(skills_dir)
        self.skill_index = self.loader.scan_all_frontmatter()
    
    def handle_query(self, user_query):
        """使用相关技能处理安全查询"""
        # 第 1 步：查找相关技能
        relevant = self._match_skills(user_query)
        
        # 第 2 步：加载前三个匹配项
        top_skills = [
            self.loader.load_full_skill(s['name']) 
            for s in relevant[:3]
        ]
        
        # 第 3 步：提取工作流步骤
        workflows = []
        for skill in top_skills:
            content = skill['content']
            # 提取 Workflow 部分
            if '## Workflow' in content:
                start = content.index('## Workflow')
                end = content.index('##', start + 1) if '##' in content[start + 1:] else len(content)
                workflows.append(content[start:end])
        
        return {
            'matched_skills': [s['metadata']['name'] for s in top_skills],
            'workflows': workflows,
            'framework_mappings': self._get_mappings(top_skills)
        }
    
    def _match_skills(self, query):
        """简单关键字匹配（替换为语义搜索）"""
        query_lower = query.lower()
        scores = []
        
        for skill in self.skill_index:
            score = 0
            desc = skill['description'].lower()
            tags = ' '.join(skill.get('tags', [])).lower()
            
            # 通过关键字匹配得分
            for word in query_lower.split():
                if word in desc:
                    score += 2
                if word in tags:
                    score += 1
            
            if score > 0:
                scores.append((score, skill))
        
        return [s for _, s in sorted(scores, reverse=True)]
    
    def _get_mappings(self, skills):
        """从加载的技能中提取框架映射"""
        mappings = {
            'attack': set(),
            'nist_csf': set(),
            'atlas': set()
        }
        
        for skill in skills:
            meta = skill['metadata']
            mappings['attack'].update(meta.get('attack_techniques', []))
            mappings['nist_csf'].update(meta.get('nist_csf', []))
            mappings['atlas'].update(meta.get('atlas_techniques', []))
        
        return {k: list(v) for k, v in mappings.items()}

# 使用
agent = CybersecurityAgent()
response = agent.handle_query("investigate credential dumping attack")

print("匹配的技能:", response['matched_skills'])
print("\nATT&CK 技术:", response['framework_mappings']['attack'])
print("\n第一个工作流:")
print(response['workflows'][0][:500])
```

## 故障排除

### 技能未找到

```python
def verify_skill_exists(skill_name):
    """检查技能是否存在且格式正确"""
    skill_path = f'skills/{skill_name}/SKILL.md'
    
    if not os.path.exists(skill_path):
        print(f"❌ 技能未找到: {skill_path}")
        return False
    
    with open(skill_path, 'r') as f:
        content = f.read()
    
    if not content.startswith('---'):
        print(f"❌ 无效格式: 缺少 YAML 前置文本")
        return False
    
    try:
        yaml_end = content.find('---', 3)
        frontmatter = yaml.safe_load(content[3:yaml_end])
        required_fields = ['name', 'description', 'domain', 'subdomain']
        
        for field in required_fields:
            if field not in frontmatter:
                print(f"❌ 缺少必填字段: {field}")
                return False
        
        print(f"✅ 技能有效: {skill_name}")
        return True
        
    except Exception as e:
        print(f"❌ YAML 解析错误: {e}")
        return False
```

### 框架映射缺失

如果技能不显示框架映射，请检查 `references/standards.md`：

```python
def audit_framework_mappings(skill_name):
    """检查技能的哪些框架映射存在"""
    refs_path = f'skills/{skill_name}/references/standards.md'
    
    if not os.path.exists(refs_path):
        print(f"⚠️  未找到 references/standards.md")
        return
    
    with open(refs_path, 'r') as f:
        content = f.read()
    
    frameworks = {
        'ATT&CK': r'T\d{4}',
        'NIST CSF': r'[A-Z]{2}\.[A-Z]{2}',
        'ATLAS': r'AML\.T\d{4}',
        'D3FEND': r'D3-[A-Z]+',
        'AI RMF': r'[A-Z]+-\d+\.\d+'
    }
    
    import re
    for name, pattern in frameworks.items():
        matches = re.findall(pattern, content)
        if matches:
            print(f"✅ {name}: {', '.join(set(matches))}")
        else:
            print(f"⚠️  {name}: 未找到映射")
```

## 主要功能总结

- **754 个技能** 跨 26 个安全领域
- **5 个框架映射**: ATT&CK、NIST CSF、ATLAS、D3FEND、AI RMF
- **渐进式加载**: 扫描前置文本（约 30 个 token），仅在需要时加载完整内容
- **结构化工作流**: 每个技能中的逐步流程
- **辅助脚本**: `scripts/` 目录中的工作 Python 脚本
- **框架标准**: `references/standards.md` 中的完整映射
- **agentskills.io 兼容**: 兼容 26+ AI 编码平台

## 许可证

Apache 2.0 — 请查看仓库以获取完整许可证文本。

## 贡献

欢迎按照项目的 CONTRIBUTING.md 指南进行贡献。所有技能都必须包含 YAML 前置文本、结构化 Markdown 部分 和框架映射。
