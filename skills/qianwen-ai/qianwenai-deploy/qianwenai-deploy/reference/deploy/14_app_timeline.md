# 应用档案 app_timeline（步骤 14）

`app_timeline.jsonl` 是应用的连续档案，与 `.qianwenai-deploy` 同级。deploy、observe、operate
三个 skill 都向它追加一行 JSON，串起一个应用从部署到热更、每次体检、每次运维动作的全过程。
observe 汇总时读它了解近期变更，operate 诊断时读它对上最近发生的事。

---

## 调用方式

deploy skill 用本脚本写入 `event=deploy` / `event=hotfix`：

```bash
python3 scripts/append_timeline.py \
  --skill qianwenai-deploy \
  --event deploy \
  --summary "全栈部署完成：systemd + Nginx，公网 47.x.x.x" \
  --data-json '{"stack_id":"stk-xxx","region":"cn-hangzhou","app_type":"systemd"}'
```

observe / operate 是独立 skill，各自按下方格式向同一文件直接追加一行（`event=observe` / `event=operate`），
`skill` 字段填自己的名字。

---

## 记录格式

每行一条 JSON，公共字段：

| 字段 | 值 |
|------|-----|
| `ts` | 事件时间戳（UTC，ISO 8601） |
| `skill` | 写入方：`qianwenai-deploy` / `qianwenai-observe` / `qianwenai-operate` |
| `event` | `deploy` / `hotfix` / `observe` / `operate` |
| `summary` | 一行人类可读摘要 |

事件专属字段（deploy 经 `--data-json` 传入，observe / operate 直接写进那一行）：

| event | 建议字段 |
|-------|----------|
| `deploy` | `stack_id`、`region`、`app_type` |
| `hotfix` | `artifact`（更新的产物）、`verification`（探活结果） |
| `observe` | `score`、`grade`、`fault_layer`（有故障时） |
| `operate` | `target`、`action`、`confirmation`、`request_id`、`verification` |

---

## 安全

只写脱敏后的只读信息。**绝不**写入密码、Token、连接串或签名 URL。追加文件按 0600 落盘。
`record_state.py` 已将 `.qianwenai-deploy` / `.qianwenai-deploy.local` 加入 `.gitignore`；
`app_timeline.jsonl` 不含机密，可随项目提交，如需忽略由用户自行决定。
