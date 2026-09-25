# rev-dex-dumper - Android DEX 文件转储工具

使用 `panda-dex-dumper` 通过 ADB 从正在运行的 Android 应用程序的内存中转储 DEX 文件。

---

## 工具位置

`panda-dex-dumper` 可执行文件包含在此技能的目录中。相对于此 `SKILL.md` 文件解析其绝对路径：

```
skills/rev-dex-dumper/panda-dex-dumper
```

---

## 工作流程

### 1. 将工具推送到设备

```bash
adb push <路径到>/panda-dex-dumper /data/local/tmp/
adb shell chmod +x /data/local/tmp/panda-dex-dumper
```

### 2. 确定目标包名

如果用户提供包名，直接使用。否则，获取前台应用：

```bash
adb shell dumpsys activity top | grep 'ACTIVITY' | tail -1 | awk '{print $2}' | cut -d/ -f1
```

### 3. 运行转储器

```bash
adb shell "cd /data/local/tmp && ./panda-dex-dumper -p $(adb shell pidof <包名>)"
```

转储的 DEX 文件保存在设备的 `/data/local/tmp/panda/` 目录下。

### 4. 将 DEX 文件拉取到主机

```bash
adb pull /data/local/tmp/panda/ ./
```

拉取到用户当前工作目录。

### 5. 清理设备缓存

```bash
adb shell rm -rf /data/local/tmp/panda/
adb shell rm /data/local/tmp/panda-dex-dumper
```

---

## 指南

1. **始终先验证 ADB 连接** — 运行 `adb devices` 并确认设备已列出后再继续。
2. **可能需要 root 权限** — `panda-dex-dumper` 使用 `ptrace` 附加到目标进程。如果设备未 root，转储会失败。建议使用 `adb root` 或通过 `su` 运行（如果需要）。
3. **等待应用完全加载** — 如果用户转储的是打包应用，真实 DEX 只有在打包器的类加载器解密后才能获取。建议用户在转储前导航过启动画面。
4. **处理 pidof 失败** — 如果 `pidof` 返回空，应用可能未运行。使用 `adb shell monkey -p <包名> -c android.intent.category.LAUNCHER 1` 先启动它。
5. **多个 DEX 文件是正常的** — 打包应用通常会生成多个 DEX 文件。应拉取 `/data/local/tmp/panda/` 中的所有文件。
6. **始终清理** — 拉取结果后，从设备中删除转储的 DEX 文件和工具可执行文件，以避免留下残留物。
