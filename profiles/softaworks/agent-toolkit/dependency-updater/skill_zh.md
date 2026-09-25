# 依赖更新器

适用于任何语言的智能依赖管理，支持自动检测和安全更新。

---

## 快速入门

```
update my dependencies
```

该工具会自动检测您的项目类型并处理后续操作。

---

## 触发词

| 触发词 | 示例 |
|---------|---------|
| 更新依赖 | "update dependencies", "update deps" |
| 检查过时 | "check for outdated packages" |
| 修复依赖问题 | "fix my dependency problems" |
| 安全审计 | "audit dependencies for vulnerabilities" |
| 诊断依赖 | "diagnose dependency issues" |

---

## 支持的语言

| 语言 | 包文件 | 更新工具 | 审计工具 |
|----------|--------------|-------------|------------|
| **Node.js** | package.json | `taze` | `npm audit` |
| **Python** | requirements.txt, pyproject.toml | `pip-review` | `safety`, `pip-audit` |
| **Go** | go.mod | `go get -u` | `govulncheck` |
| **Rust** | Cargo.toml | `cargo update` | `cargo audit` |
| **Ruby** | Gemfile | `bundle update` | `bundle audit` |
| **Java** | pom.xml, build.gradle | `mvn versions:*` | `mvn dependency:*` |
| **.NET** | *.csproj | `dotnet outdated` | `dotnet list package --vulnerable` |

---

## 快速参考

| 更新类型 | 版本变更 | 操作 |
|-------------|----------------|--------|
| **固定** | 没有 `^` 或 `~` | 跳过（有意固定） |
| **PATCH** | `x.y.z` → `x.y.Z` | 自动应用 |
| **MINOR** | `x.y.z` → `x.Y.0` | 自动应用 |
| **MAJOR** | `x.y.z` → `X.0.0` | 单独提示用户 |

---

## 工作流程

```
用户请求
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ 步骤 1：检测项目类型                         │
│ • 扫描包文件（package.json, go.mod...） │
│ • 识别包管理器                          │
├─────────────────────────────────────────────────────┤
│ 步骤 2：检查先决条件                         │
│ • 验证所需工具是否已安装               │
│ • 如缺失则建议安装                   │
├─────────────────────────────────────────────────────┤
│ 步骤 3：扫描更新                            │
│ • 运行语言特定的过时检查              │
│ • 分类：MAJOR / MINOR / PATCH / Fixed         │
├─────────────────────────────────────────────────────┤
│ 步骤 4：自动应用安全更新                     │
│ • 自动应用 MINOR 和 PATCH                   │
│ • 报告已更新的内容                           │
├─────────────────────────────────────────────────────┤
│ 步骤 5：提示 MAJOR 更新                    │
│ • 对每个 MAJOR 更新提示用户             │
│ • 显示当前版本 → 新版本                        │
├─────────────────────────────────────────────────────┤
│ 步骤 6：应用批准的 MAJOR                    │
│ • 仅更新已批准的包                     │
├─────────────────────────────────────────────────────┤
│ 步骤 7：最终化                                    │
│ • 运行安装命令                               │
│ • 运行安全审计                                │
└─────────────────────────────────────────────────────┘
```

---

## 各语言命令

### Node.js (npm/yarn/pnpm)

```bash
# 检查先决条件
scripts/check-tool.sh taze "npm install -g taze"

# 扫描更新
taze

# 应用 minor/patch
taze minor --write

# 应用特定 majors
taze major --write --include pkg1,pkg2

# 单一项目支持
taze -r  # 递归

# 安全
npm audit
npm audit fix
```

### Python

```bash
# 检查过时
pip list --outdated

# 更新所有（小心！）
pip-review --auto

# 更新特定
pip install --upgrade package-name

# 安全
pip-audit
safety check
```

### Go

```bash
# 检查过时
go list -m -u all

# 更新所有
go get -u ./...

# 整理
go mod tidy

# 安全
govulncheck ./...
```

### Rust

```bash
# 检查过时
cargo outdated

# 在语义版本内更新
cargo update

# 安全
cargo audit
```

### Ruby

```bash
# 检查过时
bundle outdated

# 更新所有
bundle update

# 更新特定
bundle update --conservative gem-name

# 安全
bundle audit
```

### Java (Maven)

```bash
# 检查过时
mvn versions:display-dependency-updates

# 更新到最新
mvn versions:use-latest-releases

# 安全
mvn dependency:tree
mvn dependency-check:check
```

### .NET

```bash
# 检查过时
dotnet list package --outdated

# 更新特定
dotnet add package PackageName

# 安全
dotnet list package --vulnerable
```

---

## 诊断模式

当依赖损坏时，运行诊断：

### 常见问题及修复

| 问题 | 症状 | 修复 |
|-------|----------|-----|
| **版本冲突** | "Cannot resolve dependency tree" | 清理安装，使用覆盖/解决方案 |
| **同伴依赖** | "Peer dependency not satisfied" | 安装所需同伴版本 |
| **安全漏洞** | `npm audit` 显示问题 | `npm audit fix` 或手动更新 |
| **未使用依赖** | 膨胀的包 | 运行 `depcheck`（Node）或等效工具 |
| **重复依赖** | 安装多个版本 | 运行 `npm dedupe` 或等效工具 |

### 紧急修复

```bash
# Node.js - 核心重置
rm -rf node_modules package-lock.json
npm cache clean --force
npm install

# Python - 清理虚拟环境
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Go - 重置模块
rm go.sum
go mod tidy
```

---

## 安全审计

对任何项目运行安全检查：

```bash
# Node.js
npm audit
npm audit --json | jq '.metadata.vulnerabilities'

# Python
pip-audit
safety check

# Go
govulncheck ./...

# Rust
cargo audit

# Ruby
bundle audit

# .NET
dotnet list package --vulnerable
```

### 严重性响应

| 严重性 | 操作 |
|----------|--------|
| **关键** | 立即修复 |
| **高** | 24小时内修复 |
| **中等** | 1周内修复 |
| **低** | 在下一个版本中修复 |

---

## 反模式

| 避免 | 原因 | 而应 |
|-------|-----|---------|
| 更新固定版本 | 有意固定 | 跳过它们 |
| 自动应用 MAJOR | 可能导致破坏性变更 | 提示用户 |
| 批量 MAJOR 提示 | 丢失上下文 | 单独提示 |
| 跳过锁文件 | 不可重复的构建 | 始终提交锁文件 |
| 忽略安全警报 | 漏洞 | 按严重性处理 |

---

## 验证检查清单

更新后：

- [ ] 更新扫描无错误
- [ ] MINOR/PATCH 自动应用
- [ ] MAJOR 更新单独提示
- [ ] 固定版本未更改
- [ ] 锁文件已更新
- [ ] 运行安装命令
- [ ] 安全审计通过（或记录问题）

---

<details>
<summary><strong>深入解析：项目检测</strong></summary>

该工具通过扫描包文件自动检测项目类型：

| 文件找到 | 语言 | 包管理器 |
|------------|----------|-----------------|
| `package.json` | Node.js | npm/yarn/pnpm |
| `requirements.txt` | Python | pip |
| `pyproject.toml` | Python | pip/poetry |
| `Pipfile` | Python | pipenv |
| `go.mod` | Go | go modules |
| `Cargo.toml` | Rust | cargo |
| `Gemfile` | Ruby | bundler |
| `pom.xml` | Java | Maven |
| `build.gradle` | Java/Kotlin | Gradle |
| `*.csproj` | .NET | dotnet |

**对于单一项目，检测顺序很重要：**
1. 首先检查当前目录
2. 然后检查工作区/单一项目模式
3. 如适用，提供递归运行选项

</details>

<details>
<summary><strong>深入解析：Node.js with taze</strong></summary>

### 先决条件

```bash
# 全局安装 taze（推荐）
npm install -g taze

# 或使用 npx
npx taze
```

### 智能更新流程

```bash
# 1. 扫描所有更新
taze

# 2. 应用安全更新（minor + patch）
taze minor --write

# 3. 对每个 major，提示用户：
#    "更新 @types/node 从 ^20.0.0 到 ^22.0.0?"
#    如是，添加到批准列表

# 4. 应用批准的 majors
taze major --write --include approved-pkg1,approved-pkg2

# 5. 安装
npm install  # 或 pnpm install / yarn
```

### 自动批准列表

某些包经常有 major 更新但向后兼容：

| 包 | 原因 |
|---------|--------|
| `lucide-react` | 图标库，major 更新是累积的 |
| `@types/*` | 类型定义，通常安全 |

</details>

<details>
<summary><strong>深入解析：版本策略</strong></summary>

### 语义版本控制

```
MAJOR.MINOR.PATCH (例如，2.3.1)

MAJOR: 破坏性变更 - 需要代码变更
MINOR: 新功能 - 向后兼容
PATCH: 修复错误 - 向后兼容
```

### 版本范围指定符

| 指定符 | 含义 | 示例 |
|-----------|---------|---------|
| `^1.2.3` | Minor + Patch OK | `>=1.2.3 <2.0.0` |
| `~1.2.3` | 仅 Patch | `>=1.2.3 <1.3.0` |
| `1.2.3` | 精确（固定） | 仅 `1.2.3` |
| `>=1.2.3` | 至少 | 任何 `>=1.2.3` |
| `*` | 任何 | 最新（危险） |

### 推荐策略

```json
{
  "dependencies": {
    "critical-lib": "1.2.3",      // 精确固定关键依赖
    "stable-lib": "~1.2.3",       // 仅 Patch 稳定依赖
    "modern-lib": "^1.2.3"        // active 依赖允许 Minor 更新
  }
}
```

</details>

<details>
<summary><strong>深入解析：冲突解决</strong></summary>

### Node.js 冲突

**诊断：**
```bash
npm ls package-name      # 查看依赖树
npm explain package-name # 为什么安装
yarn why package-name    # Yarn 对等工具
```

**使用覆盖解决：**
```json
// package.json
{
  "overrides": {
    "lodash": "^4.18.0"
  }
}
```

**使用解决方案（Yarn）：**
```json
{
  "resolutions": {
    "lodash": "^4.18.0"
  }
}
```

### Python 冲突

**诊断：**
```bash
pip check
pipdeptree -p package-name
```

**解决：**
```bash
# 使用虚拟环境
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 或使用约束
pip install -c constraints.txt -r requirements.txt
```

</details>

---

## 脚本参考

| 脚本 | 目的 |
|--------|---------|
| `scripts/check-tool.sh` | 验证工具是否已安装 |
| `scripts/run-taze.sh` | 使用正确标志运行 taze |

---

## 相关工具

| 工具 | 语言 | 目的 |
|------|----------|---------|
| [taze](https://github.com/antfu-collective/taze) | Node.js | 智能依赖更新 |
| [npm-check-updates](https://github.com/raineorshine/npm-check-updates) | Node.js | taze 的替代方案 |
| [pip-review](https://github.com/jgonggrijp/pip-review) | Python | 交互式 pip 更新 |
| [cargo-edit](https://github.com/killercup/cargo-edit) | Rust | Cargo 依赖管理 |
| [bundler-audit](https://github.com/rubysec/bundler-audit) | Ruby | 安全审计 |
