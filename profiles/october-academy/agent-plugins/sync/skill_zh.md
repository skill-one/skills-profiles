# 同步技能

快速与远程仓库进行git同步。

## 使用方法

### 命令

```bash
/sync              # 从origin main拉取
/sync develop      # 从origin develop拉取
/sync upstream     # 从upstream main拉取（分支）
```

### 韩语触发词

- "동기화"
- "원격에서 가져와"
- "풀 받아"

## 工作流程

### 1. 同步前检查

```bash
git status
```

如果工作目录中有未提交的更改：

**选项：**
1. **暂存**: `git stash` → 同步 → `git stash pop`
2. **先提交**: 建议使用 `/cp`
3. **丢弃**: 仅当用户确认使用 `git checkout .`

### 2. 获取和拉取

默认（origin main）：

```bash
git pull origin main
```

带rebase（更干净的历史记录）：

```bash
git pull --rebase origin main
```

### 3. 报告结果

同步成功后：

```
已与origin/main同步
- 拉取了3个提交
- 文件变更：5
- 无冲突
```

## 处理冲突

如果出现合并冲突：

1. 列出冲突文件
2. 提供帮助解决冲突
3. 解决后：`git add <文件>` → `git commit`

## 常见场景

### 分支工作流程

```bash
# 如果不存在，添加上游
git remote add upstream <原始仓库URL>

# 与上游同步
git fetch upstream
git merge upstream/main
```

### 分叉的分支

如果本地和远程分支已分叉：

```bash
# 选项1：合并（默认）
git pull origin main

# 选项2：rebase（更干净）
git pull --rebase origin main

# 选项3：重置（破坏性，需用户确认）
git fetch origin
git reset --hard origin/main
```

## 错误处理

| 错误 | 解决方案 |
|-------|----------|
| "Uncommitted changes" | 先暂存或提交 |
| "Merge conflict" | 帮助解决冲突 |
| "Remote not found" | 检查 `git remote -v` |
