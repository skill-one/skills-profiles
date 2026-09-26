# 内存管理技能

## 目的
AgentDB内存系统结合HNSW向量搜索。提供150倍-12,500倍更快的模式检索、持久化存储和语义搜索功能，用于学习和知识管理。

## 触发时机
- 需要存储成功模式
- 搜索相似解决方案
- 对过往工作进行语义查找
- 从先前任务中学习
- 在智能体之间共享知识
- 构建知识库

## 跳过时机
- 无需学习
- 瞬时一次性任务
- 可用外部数据源
- 只读探索

## 命令

### 存储模式
将模式或知识项存储到内存中

```bash
npx @claude-flow/cli memory store --key "[key]" --value "[value]" --namespace patterns
```

**示例:**
```bash
npx @claude-flow/cli memory store --key "auth-jwt-pattern" --value "JWT验证与刷新令牌" --namespace patterns
```

### 语义搜索
使用语义相似性搜索内存

```bash
npx @claude-flow/cli memory search --query "[搜索词]" --limit 10
```

**示例:**
```bash
npx @claude-flow/cli memory search --query "身份验证最佳实践" --limit 5
```

### 检索条目
通过键检索特定内存条目

```bash
npx @claude-flow/cli memory get --key "[key]" --namespace [namespace]
```

**示例:**
```bash
npx @claude-flow/cli memory get --key "auth-jwt-pattern" --namespace patterns
```

### 列出条目
列出命名空间中的所有条目

```bash
npx @claude-flow/cli memory list --namespace [namespace]
```

**示例:**
```bash
npx @claude-flow/cli memory list --namespace patterns --limit 20
```

### 删除条目
删除内存条目

```bash
npx @claude-flow/cli memory delete --key "[key]" --namespace [namespace]
```

### 初始化HNSW索引
初始化HNSW向量搜索索引

```bash
npx @claude-flow/cli memory init --enable-hnsw
```

### 内存统计
显示内存使用统计信息

```bash
npx @claude-flow/cli memory stats
```

### 导出内存
将内存导出为JSON

```bash
npx @claude-flow/cli memory export --output memory-backup.json
```

## 脚本

| 脚本 | 路径 | 描述 |
|------|------|------|
| `memory-backup` | `.agents/scripts/memory-backup.sh` | 将内存备份到外部存储 |
| `memory-consolidate` | `.agents/scripts/memory-consolidate.sh` | 合并和优化内存 |

## 参考

| 文档 | 路径 | 描述 |
|------|------|------|
| `HNSW指南` | `docs/hnsw.md` | HNSW向量搜索配置 |
| `内存模式` | `docs/memory-schema.md` | 内存命名空间和模式参考 |

## 最佳实践
1. 开始前检查内存中是否已存在模式
2. 使用分层拓扑进行协调
3. 完成后存储成功模式
4. 记录任何新学习内容
