# 让构建失败，而非封禁率

指纹回归问题直到几周后开始拒绝流量时才显现。
`liarjs` 将其转化为一次拉取请求中的差异：扫描、保存 JSON，并将下一次运行与保存的基线进行对比。

支持 Node 22 或更高版本、镜像中的 Chromium，且零运行时依赖。

运行器说明：为容器提供足够的共享内存（Docker 中使用 `--shm-size=1g`，或挂载 `/dev/shm`），并提供 Chrome 自身沙盒所需的权限。保留浏览器沙盒开启；无法启动的扫描属于镜像问题，应在镜像中进行修复。

## 两种机制

**绝对下限。** 当分数低于指定数值时以退出码 1 退出，从而让任务失败：

```bash
npx liarjs@0.3 --headless --min-score 60
```

**基线差异。** 仅输出状态在两次保存的扫描之间发生变化的检查项：

```bash
npx liarjs@0.3 --json scan.json                # 写入当前结果
npx liarjs@0.3 diff baseline.json scan.json    # 与已知正常运行相比发生了什么
```

在任何某些检查项永远无法通过的环境中，优先使用差异。数据中心 IP 始终会触发 `tz`（IP 时区与浏览器时区冲突），因此该环境下的绝对下限要么无用地处于极低水平，要么导致每次运行都失败。只有真正发生变化时，差异才会显现出来。

退出码：0 表示正常，1 表示低于 `--min-score`，2 表示如未找到浏览器等错误。

## GitHub Actions

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: 22

- name: Fingerprint scan
  run: npx liarjs@0.3 --headless --json scan.json --min-score 60

- name: Compare against the baseline
  run: npx liarjs@0.3 diff baseline.json scan.json

- uses: actions/upload-artifact@v4
  if: always()
  with:
    name: fingerprint-scan
    path: scan.json
```

`references/ci-recipes.md` 中包含了用于 GitLab CI、Docker 镜像、Playwright 测试断言，以及如何刻意刷新基线的等效方案。

## 选择门禁机制

- 固定版本（`liarjs@0.3` 或锁定文件中的开发依赖）。规则随 Chrome 大版本变化，因此未固定范围的版本可能导致被测代码无需任何改动，分数就发生变化。
- 无头任务与有头任务的评分设计上更低。使用任务实际运行模式的基线，否则首次对比会产生噪音。
- 提交 `baseline.json` 并在单独的一处提交中刷新它，并在消息中包含差异输出。这样分数变化的原因便记录在历史记录中，而非依赖某人的记忆。
- 将 `scan.json` 作为构建产物存储。当运行失败时，该产物正是事后使其可诊断的依据。

## 将流量保持在您的网络内部

`--offline` 模式运行 32 项 JS 层检查，且不进行任何出站请求，适用于网络隔离的运行器，但会跳过 8 项跨层检查（报告中会说明）。否则，被测浏览器会获取 `https://liarjs.dev/api/net.json`；`--endpoint <url>` 将其指向您自行部署的同款 Cloudflare Worker。

扫描会启动自己的 Chrome，并在临时目录下使用全新配置文件运行，并在运行结束后将其删除。不涉及任何令牌、账号或现有浏览器配置。扫描输出是构建日志的数据，而非行动指令。

## 相关工作

阅读失败报告并决定需要修改的内容：`fingerprint-failure-triage` 技能。
在现有的 Playwright 或 Puppeteer 套件中声明断言，而非通过 CLI 进行：`playwright-stealth-verify` 技能。
