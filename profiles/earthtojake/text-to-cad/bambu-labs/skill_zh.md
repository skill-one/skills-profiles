# Bambu Labs

来源：维护在 [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) 中。
使用已安装的本地技能文件作为运行时真实来源；仓库链接仅用于来源追溯和发布审核。

在本地网络 Bambu Lab 打印交接时使用此技能，前提是已经存在并验证了纯 `.gcode` 文件。此技能不会切片模型。

## 安全规则

- 默认使用干运行计划。实际打印机流量需要 `--execute`。
- 未使用 `--execute --confirm-start-print` 的情况下，切勿启动打印。
- 暂停和取消控制是实时打印机请求；默认使用干运行计划。
  取消打印需要 `--execute --confirm-cancel-print`。
- 将显式用户请求打印或启动特定任务的命令视为实时启动授权；不要仅为了物理检查而等待二次确认。
  仍然需要验证 G-code，检查干运行负载，读取打印机状态，优先考虑上传-only 而不是 upload-start，说明物理检查，如果验证/状态/意图不安全或不明确，则停止。
- 默认情况下不要询问打印机序列号；通过 `serial` 从打印机 TLS 证书中获取，或让 `send` 缓存它。
- 优先使用工作区根目录 `bambu-printers.json` 而不是在命令中重复访问码。该文件是本地配置，应被 Git 忽略。
- 在实时启动前，说明物理检查：清理打印板，正确设置板/线材/喷嘴，确保周围安全，操作员在附近。
- 发布 MQTT 仅是启动请求。通过打印机状态/UI 和物理观察确认接受。

## CAD 查看器交接

在完成创建或修改本地 `.3mf` 打印实物的 Bambu 工作后，当该技能安装时，你必须始终将显式文件路径传递给 `$cad-viewer`。CAD 查看器不会打开 `.gcode`，因此纯 G-code 实物不会进行交接。`$cad-viewer` 必须在未运行时启动 CAD 查看器并返回相关创建或更新文件链接；如果 `$cad-viewer` 不可用或启动失败，应报告该问题，而不是静默忽略交接。

## 工作流程

1. 使用 `$gcode` 生成和验证纯 G-code。
   如果未安装切片器，安装 OrcaSlicer 并重试；不要将缺失切片器视为障碍。在 macOS 上，优先使用 `brew install --cask orcaslicer`。
2. 配置打印机。用户可以在线程中提供 IP/访问码让代理写入 JSON，或直接编辑 `bambu-printers.json`。
   对于新打印机设置或入职请求，首先阅读 `references/new-printer-onboarding.md`。引导用户通过特定触摸屏步骤找到 IP 和 LAN 访问码，并在运行本地启动工作流前明确 **仅启用 LAN** 和 **启用开发者模式**。

```bash
python scripts/bambu_lan_print.py config set \
  --printer a1-mini \
  --host 192.168.1.34 \
  --access-code 12345678 \
  --model a1-mini \
  --fetch-serial
```

手动 JSON 结构：

```json
{
  "printers": {
    "a1-mini": {
      "host": "192.168.1.34",
      "access_code": "12345678",
      "model": "a1-mini"
    }
  }
}
```

在 A1/A1 Mini 上，在打印机触摸屏的网络/LAN 设置下找到 IP 和 LAN 访问码。当被提示时启用 **仅启用 LAN** 和 **启用开发者模式**，然后重启后再尝试本地启动命令。

3. 在实时工作前读取状态：

```bash
python scripts/bambu_lan_print.py status \
  --printer a1-mini \
  --push-all \
  --wait-seconds 10
```

4. 干运行精确交接，检查 JSON 负载，然后运行 upload-only。
   仅在上传成功后才能运行 upload-start。如果用户明确要求打印或启动任务，在验证、状态和上传检查通过后，继续 `upload-start --execute --confirm-start-print`。如果用户仅要求准备、切片、上传或审查，则在启动请求前停止。

## 交接模式

`--handoff template-project` 是经过 LAN 真实打印机验证的 A1 Mini 路径。它从验证的纯 `.gcode` 开始，复制已知良好的相同打印机 `.gcode.3mf` 模板，替换 `Metadata/plate_N.gcode`，写入板 MD5，将项目上传到 FTPS 根目录，并发布 `print.project_file`，其中 `url: ftp:///<name>.gcode.3mf`。

```bash
python scripts/bambu_lan_print.py send \
  --printer a1-mini \
  --gcode /tmp/job.gcode \
  --handoff template-project \
  --template-project /path/to/same-printer-template.gcode.3mf \
  --action upload-start
```

在用户明确要求打印或启动时，或在意图不明确时进行物理确认后执行：

```bash
python scripts/bambu_lan_print.py send \
  --printer a1-mini \
  --gcode /tmp/job.gcode \
  --handoff template-project \
  --template-project /path/to/same-printer-template.gcode.3mf \
  --action upload-start \
  --execute \
  --confirm-start-print
```

`--handoff plain` 上传 `cache/<name>.gcode` 并发布 `print.gcode_file`。保留它用于诊断或已知该路径在打印机/固件中有效。在测试的 A1 Mini 上，直接纯 G-code 上传成功，但 `gcode_file` 失败或被忽略，因此不要将其用作 A1 Mini 实时启动路径。

`--handoff bambox-project` 将纯 `.gcode` 与 `bambox` 打包，将 `.gcode.3mf` 项目上传到 FTPS 根目录，并发布 `print.project_file`。
目前仅对 `p1s-0.4` 使用 PLA、ASA 或 PETG-CF 时启用。
已知但未验证的配置：`a1-mini-0.4`、`a1-0.4`、`x1c-0.4` 和 `p1p-0.4`。

## 常见调试命令

获取/缓存序列号：

```bash
python scripts/bambu_lan_print.py serial \
  --printer a1-mini \
  --json
```

在修复根本原因后清除陈旧的打印机错误：

```bash
python scripts/bambu_lan_print.py clear-error \
  --printer a1-mini \
  --execute
```

在调试打印机是否确认 MQTT 发布以及立即报告的状态时，在 `send` 上使用 `--mqtt-qos 1 --wait-after-publish 10`。

## 打印控制

对于正在运行的打印，使用专用的打印控制命令而不是临时的 MQTT 段。这些命令仅发布控制请求；它们不会上传文件或启动新任务。执行后读取状态以确认打印机状态已更改。

干运行暂停负载：

```bash
python scripts/bambu_lan_print.py pause \
  --printer a1-mini
```

执行暂停并收集打印机报告：

```bash
python scripts/bambu_lan_print.py pause \
  --printer a1-mini \
  --execute \
  --mqtt-qos 1 \
  --wait-after-publish 10
```

干运行取消负载。发送到打印机的 Bambu LAN 命令是 `stop`：

```bash
python scripts/bambu_lan_print.py cancel \
  --printer a1-mini
```

仅在用户明确要求取消/停止打印，或在意图不明确时确认后执行取消：

```bash
python scripts/bambu_lan_print.py cancel \
  --printer a1-mini \
  --execute \
  --confirm-cancel-print \
  --mqtt-qos 1 \
  --wait-after-publish 10
```

## 失败模式

- `gcode_file` 返回 `result: fail` 或将打印机置于 `IDLE`：纯 G-code 上传成功，但固件拒绝了或忽略了直接本地启动。对于 A1 Mini，切换到 `template-project`。
- 在 `cache/` 下上传的项目启动后失败，显示 `print_error: 83935248` 或 `0500-C010`：清除错误，将项目交接上传到 FTPS 根目录，并使用 `ftp:///<name>.gcode.3mf`。
- `file:///sdcard/cache/...` 或本地 HTTP URL 被接受但未启动：停止使用这些 URL 形式用于此工作流。
- macOS 上的 Bambu Studio 或 OrcaSlicer 项目导出崩溃：不要持续尝试基于 GUI 的项目导出。使用 OrcaSlicer 生成纯 `.gcode`，然后使用此技能进行交接。
- 启用开发者模式后出现陈旧的 `gcode_state: FAILED` 或 HMS：清除打印机错误并重启前重试。
- FTPS 登录成功但上传失败，显示 `553` 或缺少 `cache/`：在 MQTT 启动前检查打印机存储/SD 卡状态。
- MQTT 状态正常但启动失败：在重试前确认序列号、访问码、开发者模式/LAN 仅模式状态和精确的交接负载。

阅读 `references/new-printer-onboarding.md` 了解新打印机设置，`references/local-lan-protocol.md` 了解协议细节，并在新打印机首次实时使用前阅读 `references/real-printer-checklist.md`。
