# 标记发布版本

在仓库的既定版本格式和标签类型中标记当前 `origin` 默认分支的 HEAD。检查发布惯例，计算下一个版本，验证确切目标，推送标签，并监控发布直至变为绿色。

此请求授权创建和推送标签以及运行仓库的既定发布工作流。仅在无法推导出所需值或仓库状态使发布变得模糊时才请求。

## 1. 首先同步到 origin 默认分支

标签必须指向远程实际存在的版本，而不是你本地签出的任何版本。

```sh
git remote get-url origin
git ls-remote --symref origin HEAD
git fetch origin --tags --prune
```

- 从 `origin` URL 中解析 GitHub 的 `owner/repository`。使用 `--repo` 或 `-R` 将该值显式传递给每个 `gh` 命令，以便 `GH_REPO`、另一个远程或配置的默认值不会重定向发布操作。
- 从远程的符号 `HEAD` 解析默认分支，而不是从本地分支或可能过时的 `origin/HEAD`。记录其完整引用名称。
- 保持工作树和本地分支不变。一个脏的或分叉的签出不会影响直接从获取的远程跟踪引用创建的标签。
- 记录 `git rev-parse origin/<default-branch>` 作为候选发布提交。不要从红色的默认分支发布。如果仓库在 CI 上控制发布，请验证在该确切提交上的检查是绿色的。

## 2. 阅读先前的发布和仓库的惯例

不要发明格式。查看仓库已经如何操作：

```sh
gh release list -R <owner/repository>    # 如果发布是 forge Release 对象
git ls-remote --tags --refs origin 'refs/tags/<relevant-prefix>*'
```

在选择最新版本之前，选择相关的软件包或发布命名空间。仓库可能包含无关的产品标签、软件包标签或旧格式，这些格式会排在正在发布的系列之前。将远程标签引用视为权威的。本地标签即使在 `git fetch --tags --prune` 后也可能过时或仅本地使用。在识别出相关的远程系列后，才获取和检查匹配的标签对象。

从最新发布中读取：

- **版本格式**：开头的 `v` 或没有，任何组件或软件包前缀（单仓库可能标记 `pkg-name/v1.2.3`），以及任何预发布或构建后缀。
- **标签类型**：轻量级、有注解或已签名。使用 `git cat-file -t <tag>`（`tag` 对象表示有注解/已签名，`commit` 表示轻量级）和 `git verify-tag <tag>` 检查签名。
- **发布机制**：发布是否只是一个推送的标签（管道会获取它），或者使用 `gh release create` 显式创建的 forge Release。

如果没有先前的发布，就没有可提升的版本：使用仓库文档中指定的起始版本，或询问应使用哪个版本。

## 3. 计算下一个版本

从相关系列中的最新标签计算语义提升，保留其开头的 `v` 和任何软件包前缀：

- **补丁**：`x.y.(z+1)`
- **次要**：`x.(y+1).0`
- **主要**：`(x+1).0.0`

遵循仓库从预发布到稳定标签的既定转换。如果历史记录没有确定是否要推进、保留或删除预发布后缀，请询问用户。

记录计算出的标签、候选提交 SHA、标签类型和发布机制。

## 4. 创建标签，匹配惯例

在标记之前，重新获取并确认没有变动：

```sh
git ls-remote --symref origin HEAD
git fetch origin --tags --prune
git rev-parse origin/<default-branch>
git ls-remote --tags --refs origin 'refs/tags/<relevant-prefix>*'
gh api 'repos/<owner>/<repository>/commits/<release-sha>/check-runs'
gh api 'repos/<owner>/<repository>/commits/<release-sha>/status'
```

默认分支、其 SHA 和最新相关标签必须保持不变，提议的标签必须不存在，发布 SHA 上的所需检查必须为绿色。如果任何内容变动，重新计算发布并重复此检查。等待现有 CI 监控器上的待处理检查，然后重新检查目标。对于失败的检查，仅在授权范围内诊断和修复。在所需检查未解决时不要标记；继续独立的准备，如果修复需要新的授权或不可用访问，则报告阻塞器。

然后显式标记获取的远程 HEAD，匹配先前标签的类型：

```sh
# 轻量级（先前标签是轻量级的）：
git tag <version> origin/<default-branch>

# 有注解（先前标签是有注解的）：
git tag -a <version> origin/<default-branch> -m "<version>"
```

全局 `tag.gpgsign = true` 会将即使是轻量级或有注解的标签也静默地转换为已签名的标签。如果仓库现有的标签未签名，请传递 `--no-sign` 以使新标签匹配。如果已签名，则签名它。

## 5. 推送，然后监控发布直至变为绿色

```sh
git push origin <version>
```

如果惯例包括 forge 发布，仅在推送验证的本地标签后创建它。使用 `gh release create <version> --verify-tag ...`，匹配先前发布如何设置其标题、注释和资产，并传递 `--repo <owner/repository>`。然后验证结果：

```sh
git ls-remote origin 'refs/tags/<version>' 'refs/tags/<version>^{}'
gh run watch <run-id> -R <owner/repository> --exit-status --interval 20
gh release view <version> -R <owner/repository>
```

对于有注解或已签名的标签，比较剥离的 `^{}` 结果与发布提交 SHA。对于轻量级标签，比较直接标签结果。直到远程标签解析为发布提交、发布管道变为绿色且预期发布工件存在，才不要将其称为完成。

## 6. 报告

说明你切割的版本、它指向的提交 SHA、如何标记（轻量级 / 有注解 / 已签名），以及发布或管道结果。
