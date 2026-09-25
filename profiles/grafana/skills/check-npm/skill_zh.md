# npm / yarn / pnpm 供应链审计

对工作区根目录进行只读审计。不要修改任何文件。

## 0. 检测包管理器

```bash
test -f package.json || { echo "STOP: 工作区根目录没有 package.json"; exit 1; }
jq -r '.packageManager // "unset"' package.json
ls -1 yarn.lock package-lock.json pnpm-lock.yaml 2>/dev/null || true
```

如果没有 `package.json`，则停止。优先级：`packageManager` → 锁文件 → 默认 npm。

## 1. 工具版本

```bash
npm --version    # 必须≥ 11.15.0
yarn --version   # 必须≥ 4.14.0
pnpm --version   # 必须≥ 11.0.0
```

使用 semver 比较方式。验证固定的 `packageManager` 是否满足阈值。

| 管理器 | 最小值 |
|---------|---------|
| npm | 11.15.0 |
| yarn | 4.14.0 |
| pnpm | 11.0.0 |

## 2. 禁用生命周期脚本

```bash
grep -E '^ignore-scripts=' .npmrc 2>/dev/null
grep -E 'enableScripts:' .yarnrc.yml 2>/dev/null
grep -E 'strictDepBuilds:|dangerouslyAllowAllBuilds:|allowBuilds:' pnpm-workspace.yaml 2>/dev/null
```

| 管理器 | 通过 | 失败 |
|---------|------|------|
| npm | `.npmrc` 中有 `ignore-scripts=true` | 缺失或 `false` |
| yarn | `enableScripts: false` 或键不存在 | `enableScripts: true` |
| pnpm ≥ 11 | `strictDepBuilds` 未设置/`true`，`dangerouslyAllowAllBuilds` 未设置/`false`，且 `allowBuilds` 未设置/`[]` | `strictDepBuilds: false`，`dangerouslyAllowAllBuilds: true`，或 `allowBuilds` 非空 |
| pnpm 10 | `.npmrc` `ignore-scripts=true` 或 `strictDepBuilds: true` | 两者均未设置 |

pnpm 11+ 忽略 `.npmrc` 和 `package.json#pnpm` 中的脚本设置。pnpm 10 / yarn 边缘情况：[references/managers.md](references/managers.md)。

## 3. 不安全的依赖协议

Registry：

```bash
grep -E '^allow-git=' .npmrc 2>/dev/null
grep -E 'approvedGitRepositories:' .yarnrc.yml 2>/dev/null
grep -E 'blockExoticSubdeps:' pnpm-workspace.yaml 2>/dev/null
```

扫描工作区 `package.json` 文件（`dependencies`，`devDependencies`，`optionalDependencies`，`peerDependencies`）。优先使用工作区成员发现（pnpm-workspace.yaml / 根工作区 / lerna / rush）[references/protocols.md](references/protocols.md)，然后仅扫描这些清单。回退（可能误匹配非工作区清单）：

    find . -name package.json -not -path '*/node_modules/*'

**仅安全值：** semver 范围，`workspace:`，`patch:`，`npm:` 别名到 semver。将其他所有内容（git URL，tarball，`user/repo` 简写，`file:`，`link:`，`exec:`，…）标记为 `path → name → value (协议)`。

| 管理器 | 通过 | 失败 |
|---------|------|------|
| npm | `allow-git=none` 或 `root` | 缺失或 `all` |
| yarn | `approvedGitRepositories: []` 或 grafana 范围列表，或带策略注释的干净扫描 | 不安全条目或广泛允许列表 |
| pnpm ≥ 11 | `blockExoticSubdeps` 未设置/`true` | `false` |
| pnpm 10.x | `blockExoticSubdeps: true` | 未设置（默认 `false`）或 `false` |

协议检测顺序和 yarn 姿态详情：[references/protocols.md](references/protocols.md)。

## 4. 最小发布年龄 ≥ 3 天

3 天 = 4320 分钟。npm 使用 **天**；yarn 和 pnpm 使用 **分钟**。

```bash
grep -E '^min(imum)?-release-age=' .npmrc 2>/dev/null
grep -E 'npmMinimalAgeGate:' .yarnrc.yml 2>/dev/null
grep -E 'minimumReleaseAge:|minimumReleaseAgeStrict:' pnpm-workspace.yaml 2>/dev/null
```

| 管理器 | 通过 | 失败 |
|---------|------|------|
| npm | `min-release-age` ≥ `3` | 缺失 |
| yarn | `npmMinimalAgeGate` ≥ 4320 min | 缺失或低于 |
| pnpm ≥ 11 | `minimumReleaseAge` ≥ `4320` | 未设置（默认 `1440`）或低于 |
| pnpm 10 | `minimum-release-age` / `minimumReleaseAge` ≥ `4320` | 缺失 |

在 pnpm 11 中标记 `minimumReleaseAgeStrict: false`。

## 5. 报告

| # | 检查 | 状态 | 详情 |
|---|---|---|---|
| 0 | 包管理器 | (npm / yarn / pnpm) | 版本：x.y.z (固定：y.y.y 如果设置) |
| 1 | 工具版本 ≥ 阈值 | 通过 / 失败 | `实际` vs `要求` |
| 2 | 脚本禁用 | 通过 / 失败 | 配置行或 "缺失" |
| 3 | 不安全的依赖协议 | 通过 / 失败 | registry 状态 + 标记条目 |
| 4 | 最小发布年龄 ≥ 3 天 | 通过 / 失败 | 配置 + 值 |

仅使用 `通过` / `失败` — 无表情符号。

对于每个失败，提供一个可粘贴的修复方案：

```ini
# npm — .npmrc
ignore-scripts=true
allow-git=none
min-release-age=3
```

```yaml
# pnpm 11 — pnpm-workspace.yaml
strictDepBuilds: true
dangerouslyAllowAllBuilds: false
allowBuilds: []
minimumReleaseAge: 4320
blockExoticSubdeps: true
```

```yaml
# yarn — .yarnrc.yml
npmMinimalAgeGate: 4320
```

更多修复方案（工具升级，yarn git 允许列表，pnpm 10）：[references/fix-snippets.md](references/fix-snippets.md)。

如果所有检查通过：显示 "All checks passed." 并停止。
