# 依赖项修复

查找并修复 **$ARGUMENTS**（如果未提供参数，则为根 `package.json`）中的所有依赖项问题——漏洞、过时的包、弃用的依赖项、许可证问题和供应链风险。此技能会生成 Flows 应用程序审核流程所需的 `review-packages.md` 产物。

---

## 第 1 步 — 读取并列出所有依赖项

```bash
# 列出所有依赖项和 devDependencies
node -e "
  const pkg = require('./package.json');
  console.log('=== 依赖项 ===');
  Object.entries(pkg.dependencies || {}).forEach(([name, ver]) => console.log(name + ' @ ' + ver));
  console.log('\\n=== Dev 依赖项 ===');
  Object.entries(pkg.devDependencies || {}).forEach(([name, ver]) => console.log(name + ' @ ' + ver));
"
```

记录依赖项和 devDependencies 的总数。

---

## 第 2 步 — 查询 npm 元数据并更新过时的包

对于每个包，收集：
- **npm 上的最新版本**
- **每周下载量**
- **最后发布日期**
- **弃用** 标志

```bash
# 批量查询——为每个包运行（示例为单个包）
npm view <package-name> --json 2>/dev/null | node -e "
  const data = JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));
  console.log(JSON.stringify({
    name: data.name,
    latest: data['dist-tags']?.latest,
    modified: data.time?.modified,
    deprecated: data.deprecated || false,
  }));
"

# 对于每周下载量，使用 npm API
curl -s "https://api.npmjs.org/downloads/point/last-week/<package-name>" | node -e "
  const data = JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));
  console.log(data.downloads);
"
```

为了效率，批量进行多个查询。如果项目有大量依赖项，使用脚本：

```bash
node -e "
  const { execSync } = require('child_process');
  const pkg = require('./package.json');
  const allDeps = { ...pkg.dependencies, ...pkg.devDependencies };

  for (const [name, usedVersion] of Object.entries(allDeps)) {
    try {
      const info = JSON.parse(execSync('npm view ' + name + ' --json 2>/dev/null', { encoding: 'utf8' }));
      const latest = info['dist-tags']?.latest || 'unknown';
      const modified = info.time?.modified || 'unknown';
      const deprecated = info.deprecated ? 'YES' : 'No';
      console.log([name, usedVersion, latest, modified, deprecated].join(' | '));
    } catch {
      console.log(name + ' | ' + usedVersion + ' | 查询失败');
    }
  }
"
```

### 修复：更新过时的包

对于每个版本落后于 1 个主版本的包，更新它：

```bash
pnpm update <package>@latest
```

对于版本落后于 1 个以上次版本的包，更新到最新次版本：

```bash
pnpm update <package>
```

更新后，运行 `pnpm install` 和 `pnpm run build` 以验证没有问题。如果主版本更新导致构建失败，回滚该特定更新并记为手动修复项。

---

## 第 3 步 — 运行安全审计并修复漏洞

```bash
# 使用项目的包管理器运行审计
pnpm audit --json 2>/dev/null || npm audit --json 2>/dev/null

# 也运行仅生产环境的审计（发送给用户的部分）
pnpm audit --prod --json 2>/dev/null || npm audit --production --json 2>/dev/null
```

解析 JSON 输出以获取：
- 严重性计数（严重、高、中等、低）
- 每个漏洞的详细信息（包、严重性、标题、修复版本、公告 URL）

任何已知存在 CVE 的包在健康列中自动 **失败**。

### 修复：解决漏洞

运行 `pnpm audit fix` 以自动修复可以修复的问题。对于无法自动修复的高/严重 CVE，手动在 `package.json` 中将易受攻击的包更新为修复版本，并运行 `pnpm install`。如果修复版本有破坏性变更，应用最小的代码更改以适应。如果漏洞存在于传递依赖项中，使用 `pnpm overrides` 在 `package.json` 中强制使用修复版本：

```json
{
  "pnpm": {
    "overrides": {
      "vulnerable-package": ">=2.1.0"
    }
  }
}
```

应用修复后，重新运行 `pnpm audit` 以确认漏洞已解决。运行 `pnpm run build` 以验证没有问题。

---

## 第 4 步 — 分配健康分数并修复失败分数的包

对于每个包，分配一个健康指示器：

| 健康 | 标准 |
|------|------|
| **通过** | >100k 每周下载量 **AND** 最近 12 个月内更新 **AND** 未弃用 **AND** 版本为当前或接近当前（1 个主版本内） |
| **警告** | 10k–100k 每周下载量 **OR** 自上次发布以来超过 12 个月 **OR** 落后于 1 个以上主版本 |
| **失败** | <10k 每周下载量 **OR** 2 年以上未更新 **OR** 弃用 **OR** 已知 CVE |

边缘情况：
- `@cognite/*` 包：即使下载量低也信任 Cognite 内部包
- `@types/*` 包：信任 DefinitelyTyped 包；关注版本是否与主包匹配
- 新发布的包（<6 个月）：标记为 **警告** 以供审核，低下载量不自动失败

### 修复：替换失败分数的包

对于每个失败分数的包：

- **如果弃用：** 查找并安装推荐的替代包。更新整个代码库的所有导入。
- **如果未维护（2 年以上）：** 查找一个功能等效的活跃维护替代包。替换它。
- **如果下载量低且不是 `@cognite/*`：** 评估是否确实需要。如果存在原生 JS/TS 等效项或功能简单，移除依赖项并内联实现。

每次替换后，运行 `pnpm install` 和 `pnpm run build` 以验证替换是否正常工作。

---

## 第 5 步 — 检查供应链风险并缓解

```bash
# 检查安装脚本（preinstall、postinstall、prepare）
node -e "
  const { execSync } = require('child_process');
  const pkg = require('./package.json');
  const allDeps = Object.keys({ ...pkg.dependencies, ...pkg.devDependencies });

  for (const name of allDeps) {
    try {
      const info = JSON.parse(execSync('npm view ' + name + ' --json 2>/dev/null', { encoding: 'utf8' }));
      const scripts = info.scripts || {};
      const risky = ['preinstall', 'install', 'postinstall'].filter(s => scripts[s]);
      if (risky.length > 0) {
        console.log('安装脚本：' + name + ' — ' + risky.join(', '));
      }
    } catch {}
  }
"

# 检查维护者很少的包（单点故障）
# 这是信息性的，不阻塞
```

### 修复：评估和缓解安装脚本风险

对于每个具有安装脚本的依赖项，确定脚本是否合法（例如，`sharp`、`esbuild`、`better-sqlite3` 的原生模块编译）。已知构建工具和原生模块包预期会有安装脚本。

如果包不是已知构建工具且具有可疑的安装脚本，用更安全的替代包替换它。替换后，运行 `pnpm install` 和 `pnpm run build` 以验证。

---

## 第 6 步 — 检查许可证兼容性并替换有问题的包

```bash
# 列出所有许可证
npx license-checker --summary 2>/dev/null || node -e "
  const { execSync } = require('child_process');
  const pkg = require('./package.json');
  const allDeps = Object.keys({ ...pkg.dependencies, ...pkg.devDependencies });

  for (const name of allDeps) {
    try {
      const info = JSON.parse(execSync('npm view ' + name + ' --json 2>/dev/null', { encoding: 'utf8' }));
      console.log(name + ': ' + (info.license || '未知'));
    } catch {}
  }
"
```

Flows 应用程序可接受的许可证（商业分发）：
- MIT、Apache-2.0、BSD-2-Clause、BSD-3-Clause、ISC、0BSD、Unlicense、CC0-1.0

需要法律审核的许可证：
- GPL-2.0、GPL-3.0、LGPL-2.1、LGPL-3.0、AGPL-3.0、MPL-2.0、EUPL-1.1
- 任何 "未知" 或缺失的许可证

### 修复：替换具有问题许可证的包

对于生产依赖项中的每个具有 Copyleft 许可证（GPL、AGPL）或未知许可证的包，找到一个 MIT/Apache-2.0 许可证替代包并替换它。更新整个代码库的所有导入。

对于 devDependencies 中的 Copyleft 许可证，这些风险较低但仍需注意。

每次替换后，运行 `pnpm install` 和 `pnpm run build` 以验证。

---

## 第 7 步 — 生成 `review-packages.md` 产物（修复后状态）

在应用所有修复后重新运行元数据查询以捕获修复后的状态。然后按 Flows 应用程序审核流程所需的格式生成输出：

```markdown
## 包审核：[应用名称]

### 依赖项

| 包 | 使用版本 | 最新 | 每周下载量 | 最后发布 | 弃用 | CVE | 健康 |
|----|----------|------|------------|----------|------|----|------|
| react | ^18.2.0 | 18.3.1 | 25M | 2024-04-26 | 否 | 0 | 通过 |
| some-old-lib | ^1.0.0 | 1.0.3 | 5k | 2021-03-15 | 否 | 0 | 失败 |

### Dev 依赖项

| 包 | 使用版本 | 最新 | 每周下载量 | 最后发布 | 弃用 | CVE | 健康 |
|----|----------|------|------------|----------|------|----|------|
| vitest | ^1.6.0 | 2.0.1 | 8M | 2024-07-01 | 否 | 0 | 通过 |

### 安全审核

| 严重性 | 计数 |
|--------|------|
| 严重 | 0 |
| 高 | 0 |
| 中等 | 0 |
| 低 | 0 |

#### 漏洞

| 包 | 严重性 | 标题 | 修复版本 | 公告 |
|----|--------|------|----------|------|
| (未找到) | — | — | — | — |

### 许可证摘要

| 许可证 | 计数 | 包 |
|--------|------|------|
| MIT | 45 | react, react-dom, ... |
| Apache-2.0 | 3 | ... |

### 供应链标志

| 包 | 风险 | 详情 |
|----|------|------|
| (未找到) | — | — |
```

---

## 第 8 步 — 报告剩余问题

总结已修复和剩余的问题：

### 已修复

| 类别 | 计数 | 详情 |
|------|------|------|
| 更新包 | N | 包和版本变更列表 |
| 修复 CVE | N | 已修复的 CVE 列表 |
| 替换弃用依赖项 | N | 旧包 -> 新包 |
| 解决许可证问题 | N | 旧包 -> 新包 |

### 剩余（无法自动修复）

仅列出无法自动修复的问题：
- 主版本更新导致的破坏性变更，需要手动代码适配
- 需要法律审核的许可证（例如，传递依赖项中的 LGPL）
- 没有可维护替代项的包
- 尚无修复版本的漏洞

对于每个剩余项，解释为什么无法自动修复以及应用作者需要做什么。

---

## 完成

声明整体健康判定：修复后的 Pass/警告/失败数量、已解决的问题数量以及应用作者需要手动处理的剩余项。
