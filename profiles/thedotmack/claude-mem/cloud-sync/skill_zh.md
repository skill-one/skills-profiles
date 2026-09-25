# 云同步 (cmem.ai Pro)

已安装的 worker 通过 SyncHub 进行同步。有一个客户端、一个持久的操作日志，并且没有单独的同步守护进程。此功能检查状态或写入由 **cmem.ai → Connect** 发出的三个连接值。

**安全规则：** 绝不打印同步令牌，将其放入 argv 中或记录它。仅确认其长度。保留所有无关的设置并保持 `~/.claude-mem/settings.json` 模式 `0600`。

## 1. 检查状态

解析 worker 端口并查询始终注册的状态路由：

```bash
PORT="${CLAUDE_MEM_WORKER_PORT:-$(node -e "const fs=require('fs'),p=require('path'),os=require('os');const uid=(typeof process.getuid==='function'?process.getuid():77);const fallback=String(37700+(uid%100));try{const s=JSON.parse(fs.readFileSync(p.join(os.homedir(),'.claude-mem','settings.json'),'utf-8'));process.stdout.write(String(s.CLAUDE_MEM_WORKER_PORT||fallback));}catch{process.stdout.write(fallback);}" 2>/dev/null)}"
curl -s "http://127.0.0.1:${PORT}/api/sync/status"
```

- `configured: true` 和 `hub.reachable: true` → worker 已完成对 SyncHub 的认证 `GET /v1/sync/status` 请求。报告 `deviceId`、挂起计数、`lastFlushAt`、`lastError` 和 Hub 头/检查点；除非用户要求替换连接，否则停止。
- `configured: true` 和 `hub.reachable: false` → 报告 `hub.error` 并说明 SyncHub 连接未验证。挂起计数为零或 `lastError: null` 不算成功，因为空队列不会执行推送。
- `configured: false` → 继续。
- 重启后立即拒绝连接、404 或 503 → 在诊断 worker 之前，每三秒重试约 30 秒。

## 2. 获取连接

请求 **cmem.ai → Connect** 显示的所有三个值：

1. 同步令牌；
2. 用户 ID；
3. SyncHub URL。

Hub URL 必须是一个绝对 `https://` URL。不要替换 cmem.ai 应用程序 API URL；已安装的客户端仅与 SyncHub 通信。

## 3. 写入已安装客户端设置

将收集到的值替换在此引号内的 stdin 脚本中。在运行它之前或之后不要回显它们：

```bash
node - <<'EOF'
const fs = require('fs'), os = require('os'), path = require('path');
const token = 'PASTE_TOKEN_HERE';
const userId = 'PASTE_USER_ID_HERE';
const hubUrl = 'PASTE_HUB_URL_HERE';
if (!token || !userId || !/^https:\/\/[^\s]+$/.test(hubUrl)) {
  console.error('token、用户 ID 和一个 https SyncHub URL 是必需的');
  process.exit(1);
}
const dir = path.join(os.homedir(), '.claude-mem');
const file = path.join(dir, 'settings.json');
fs.mkdirSync(dir, { recursive: true });
const settings = fs.existsSync(file) ? JSON.parse(fs.readFileSync(file, 'utf8')) : {};
const target = settings.env && typeof settings.env === 'object' ? settings.env : settings;
target.CLAUDE_MEM_CLOUD_SYNC_TOKEN = token;
target.CLAUDE_MEM_CLOUD_SYNC_USER_ID = userId;
target.CLAUDE_MEM_CLOUD_SYNC_HUB_URL = hubUrl.replace(/\/+$/, '');
fs.writeFileSync(file, JSON.stringify(settings, null, 2) + '\n', { mode: 0o600 });
fs.chmodSync(file, 0o600);
console.log(`保存云连接：令牌长度 ${token.length}，用户 ID 长度 ${userId.length}`);
EOF
```

这些是唯一需要的连接键。worker 在首次启动时生成并持久化设备 ID，并将设备名称默认为主机名。

## 4. 重启并验证

```bash
curl -s -X POST "http://127.0.0.1:${PORT}/api/admin/restart"
```

在继任者启动期间，每五秒轮询状态路由一次，最多 30 秒。成功意味着 `configured: true`、`hub.reachable: true` 和 `lastError: null`。本地路由始终执行认证的只读 SyncHub 状态探测，即使所有挂起计数为零；它从不使用遗留的 cmem.ai Pro 状态路由，也从不追加或推进同步状态。挂起计数仅描述 SyncHub 启动基线之后的写入；设置不会迁移预启动的本地语料库。

如果 `hub.reachable` 为 false，报告 `hub.error`。如果 `lastError` 非空，也报告它。要求用户验证 **cmem.ai → Connect** 中的三个值。绝不包含令牌。

## 5. 报告

报告设备 ID、挂起计数、最后一次成功的刷新、Hub 可达性和检查点，以及任何 Hub/刷新错误。以以下隐私声明结束：

> 云同步将您的观察叙事和完整提示文本上传到您的 cmem.ai 账户。
