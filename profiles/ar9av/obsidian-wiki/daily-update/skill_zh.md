# 每日更新 — 维护周期

您对维基进行轻量级维护：检查源新鲜度、刷新索引、更新 hot.md，并写入终端通知读取的状态文件。

## 开始前

1. **解析配置** — 遵循 `llm-wiki/SKILL.md` 中的配置解析协议（行内 `@name` 覆盖 → 向上遍历 CWD 查找 `.env` → 全局配置 → 提示设置）。这会提供 `OBSIDIAN_VAULT_PATH` 和 `OBSIDIAN_WIKI_REPO`。
2. **派生仓库名称范围的状态目录** — 所有运行时状态都限定于解析的仓库，而不是全局：
   ```bash
   VAULT_ID=$(echo "$OBSIDIAN_VAULT_PATH" | md5sum 2>/dev/null | cut -c1-8 || md5 -q - <<< "$OBSIDIAN_VAULT_PATH" | cut -c1-8)
   STATE_DIR="$(obsidian_wiki_config_dir)/state/$VAULT_ID"
   mkdir -p "$STATE_DIR"
   ```
3. 读取 `$OBSIDIAN_VAULT_PATH/.manifest.json`。

## 模式

### 运行模式（默认 — 由 cron 或 `/daily-update` 触发）

执行维护周期：

**步骤 1：源新鲜度检查**

比较 `.manifest.json` 中的每个源与其文件的修改时间。分类为：
- **新鲜** — `mtime ≤ ingested_at`
- **陈旧** — `mtime > ingested_at`（存在新内容，尚未摄入）
- **缺失** — 源文件不再存在

**步骤 2：索引刷新**

```bash
obsidian-wiki memory index --vault "$OBSIDIAN_VAULT_PATH"
```

这会通过内存锁对 `index.md` 与磁盘上的页面进行协调 — 添加缺失的条目，删除已删除页面的条目，保留所有者的自有部分。注意输出中的 `added`/`removed`，用于步骤 6 中的日志行。不要用 `find` 列出页面并手动编辑索引。

**步骤 3：hot.md 更新**

```bash
obsidian-wiki memory hot --vault "$OBSIDIAN_VAULT_PATH"
```

最近活动、活跃线程和标记的矛盾会从日志、待办索引和页面元数据中重新生成；`## 关键要点` 会保持不变。如果要点比 ~48 小时旧 *并且* 仓库发生了实质性变化，请刷新它们：读取最近更新的 10 页，并使用 `--takeaways -` 将约 500 字的快照传递到 stdin。否则保留它们 — 没有新要点的重建是廉价且正确的。

如果任一命令报告仓库是 **未迁移**，请停止并告诉用户运行 `obsidian-wiki memory migrate`（预览）然后 `--apply`；不要回退到手动编辑。

**步骤 4：写入状态**

写入到“开始前”派生的 `$STATE_DIR`：

```bash
date +%s > "$STATE_DIR/.last_update"
echo "<stale_count>" > "$STATE_DIR/.pending_delta"
echo "$OBSIDIAN_VAULT_PATH" > "$STATE_DIR/.vault_path"
```

**步骤 4a：计划健康检查（wiki-lint）**

`LINT_SCHEDULE`（默认 `weekly`）控制此周期运行 `wiki-lint` 的频率：

- `manual` — 永不自动运行；完全跳过此步骤。
- `daily` — 每个周期运行 `wiki-lint`。
- `weekly` — 仅当 `$STATE_DIR/.last_lint` 缺失或比 7 天旧时运行 `wiki-lint`。

```bash
LINT_SCHEDULE="${LINT_SCHEDULE:-weekly}"
NOW=$(date +%s)
LAST_LINT=$(cat "$STATE_DIR/.last_lint" 2>/dev/null || echo 0)
```

如果计划要求运行，则调用 `wiki-lint` 技能，然后记录运行：

```bash
date +%s > "$STATE_DIR/.last_lint"
```

将其摘要（断开的链接、孤儿、发现的陈旧页面）折叠到步骤 7 的报告中作为 `Health check:` 行；在未运行 lint 的周期中完全省略该行。

**步骤 5：生成 impl-validator**

周期结束后，作为子代理生成 `impl-validator`：

```
impl-validator check:
  目标: "每日维基维护 — 索引已协调，hot.md 已刷新，状态文件已写入"
  产物:
    - $OBSIDIAN_VAULT_PATH/index.md
    - $OBSIDIAN_VAULT_PATH/hot.md
    - $STATE_DIR/.last_update
    - $STATE_DIR/.pending_delta
  检查:
    - .last_update 是否包含最近的 Unix 时间戳（在过去 60 秒内）？
    - .pending_delta 是否包含非负整数？
    - hot.md 是否设置了更新的 frontmatter 字段为今天？
    - index.md 是否列出的页面至少与仓库中存在的页面一样多？
```

在记录之前应用任何 FAIL。

**步骤 6：记录**

追加到 `$OBSIDIAN_VAULT_PATH/log.md`：
```
obsidian-wiki memory log DAILY-UPDATE fresh=<N> stale=<N> missing=<N> index_added=<N> hot_refreshed=<true|false> lint=<ran|skipped>
```

**步骤 7：向用户报告**

```
## 每日维基更新

- 源：N 新鲜 · N 陈旧 · N 缺失
- 索引：N 页面（N 添加，N 删除）
- hot.md：已刷新 / 仍然最新
- 健康检查：N 断开链接，N 孤儿，N 陈旧页面（如果此周期未运行 lint，则省略此行）

陈旧源（运行以同步）：
  /wiki-history-ingest claude   — 自上次摄入以来 N 会话
  /wiki-history-ingest codex    — 自上次摄入以来 N 会话
```

### 设置模式（由“设置每日 cron”或“安装终端通知”触发）

引导用户完成首次设置：

**步骤 1：验证脚本存在**

检查 `$OBSIDIAN_WIKI_REPO/scripts/daily-update.sh` 是否存在且可执行。如果不存在，请指向它。

**步骤 2：安装调度器** — 根据平台 (`uname -s`) 选择。

macOS (`Darwin`) — launchd：

```bash
# 替换 plist 中的占位符
sed "s|OBSIDIAN_WIKI_REPO|$OBSIDIAN_WIKI_REPO|g" \
  "$OBSIDIAN_WIKI_REPO/scripts/com.obsidian-wiki.daily-update.plist" \
  > "$HOME/Library/LaunchAgents/com.obsidian-wiki.daily-update.plist"

# 加载它
launchctl load "$HOME/Library/LaunchAgents/com.obsidian-wiki.daily-update.plist"
```

Linux with systemd (`systemctl --user` 可用) — 一个用户定时器：

```bash
UNIT_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
mkdir -p "$UNIT_DIR"
sed "s|OBSIDIAN_WIKI_REPO|$OBSIDIAN_WIKI_REPO|g" \
  "$OBSIDIAN_WIKI_REPO/scripts/obsidian-wiki-daily-update.service" \
  > "$UNIT_DIR/obsidian-wiki-daily-update.service"
cp "$OBSIDIAN_WIKI_REPO/scripts/obsidian-wiki-daily-update.timer" "$UNIT_DIR/"
systemctl --user daemon-reload
systemctl --user enable --now obsidian-wiki-daily-update.timer
```

在无头服务器上，用户定时器仅在用户登录时运行，除非开启 lingering — 建议 `sudo loginctl enable-linger "$USER"`。

任何其他情况（没有 systemd、容器、WSL 而没有 systemd） — crontab。通过 `crontab -e` 追加此行，如果已存在 `obsidian-wiki` daily-update 行则跳过：

```cron
0 9 * * * /bin/bash "$OBSIDIAN_WIKI_REPO/scripts/daily-update.sh" >> /tmp/obsidian-wiki-daily.log 2>&1
```

将字面仓库路径替换 `$OBSIDIAN_WIKI_REPO` — cron 不会加载您的 shell 环境。

**步骤 3：安装终端通知（可选）**

询问用户：“您希望在维基陈旧时收到终端提醒吗？(y/n)” — 如果他们说不，或者环境是无头的/VPS，则跳过此步骤。

如果同意，检测用户的 shell 并指向正确的 rc 文件：

```bash
SHELL_NAME=$(basename "$SHELL")   # zsh, bash, fish, 等。
case "$SHELL_NAME" in
  zsh)  RC_FILE="$HOME/.zshrc" ;;
  bash) RC_FILE="$HOME/.bashrc" ;;
  *)    echo "Shell '$SHELL_NAME' 未自动检测。将源行手动添加到您的 shell rc 文件中。" ; return ;;
esac
```

检查该 rc 文件中是否已源 `wiki-notify.sh`。如果没有，追加：

```bash
echo "" >> "$RC_FILE"
echo "# obsidian-wiki 终端通知" >> "$RC_FILE"
echo "source $OBSIDIAN_WIKI_REPO/scripts/wiki-notify.sh" >> "$RC_FILE"
```

对于 Fish shell，源语法不同 — 提供手动说明：
```fish
# 添加到 ~/.config/fish/config.fish:
bass source $OBSIDIAN_WIKI_REPO/scripts/wiki-notify.sh
# (需要 bass 插件，或原生复制逻辑)
```

**步骤 4：运行脚本一次**

```bash
bash "$OBSIDIAN_WIKI_REPO/scripts/daily-update.sh"
```

这将初始化 `$STATE_DIR/.last_update`，以便终端通知立即工作。

**步骤 5：确认**

告诉用户：
- 调度器每天 9 点运行（launchd 和 systemd 定时器如果错过会话/启动则捕获；纯 cron 不会）
- `wiki-lint` 健康检查按 `LINT_SCHEDULE` 频率（默认 `weekly`）运行作为该周期的一部分 — 在 `.env` 中设置 `LINT_SCHEDULE=daily` 或 `manual` 以更改它
- 终端通知在维基超过 20 小时陈旧时出现
- 状态存储在 `<全局配置目录>/state/<仓库名称>/`（默认为 XDG 风格 `~/.config/obsidian-wiki`，如果已存在则为 `~/.obsidian-wiki`） — 支持多个独立仓库
- 他们可以随时运行 `/daily-update` 强制同步
- 日志转到 `/tmp/obsidian-wiki-daily.log`（launchd, cron）或 `journalctl --user -u obsidian-wiki-daily-update`（systemd）

## QMD 刷新在仓库名称写入后

QMD 是一个搜索索引，不是真相来源。如果 `$QMD_WIKI_COLLECTION` 为空或未设置，跳过此步骤。仅在当前技能写入或重写仓库名称标记后运行。如果 QMD 刷新失败，不要回滚仓库名称更改；单独报告 QMD 状态。

如果设置了 `$QMD_CLI`，则使用它；否则使用 `qmd`。

```bash
${QMD_CLI:-qmd} update
```

如果输出说需要向量或嵌入可能过时，运行：

```bash
${QMD_CLI:-qmd} embed
```

使用以下任一方式验证集合：

```bash
${QMD_CLI:-qmd} ls "$QMD_WIKI_COLLECTION"
```

或，当知道特定页面路径时：

```bash
${QMD_CLI:-qmd} get "qmd://$QMD_WIKI_COLLECTION/<page>.md" -l 5
```

记录以下之一：
- `QMD refreshed: update + embed + verified`
- `QMD refreshed: update only + verified`
- `QMD skipped: QMD_WIKI_COLLECTION unset`
- `QMD skipped: qmd CLI unavailable`
- `QMD failed: <简短错误摘要>`
