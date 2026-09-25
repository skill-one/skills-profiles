# Govilo To Go

将任何文件转换为付费解锁链接——只需一条命令即可打包、上传并收取加密货币支付。自动化流程的最后一公里：从创建到变现。

## 运行前准备

在执行 CLI 命令之前，务必向用户获取以下值——切勿猜测或使用占位符：

1. **title** — 产品名称是什么？
2. **price** — 收取多少费用（以 USDC 为单位）？
3. **description** — 产品的简短描述（可选，但必须询问）

## CLI 命令

> 需要 [uv](https://docs.astral.sh/uv/)。有关安装说明，请参阅 [references/setup-guide.md](references/setup-guide.md)。

从该技能的基本目录中运行。使用一个**专用**的 env 文件，其中仅包含 `GOVILO_API_KEY`（可选地包含 `SELLER_ADDRESS`）。切勿将 `--env-file` 指向包含无关密钥的项目 `.env` 文件。

```bash
cd <skill_base_directory>
uv run --env-file <path_to>/.env.govilo create-link \
  --input <path>         \
  --title "Product Name" \
  --price "5.00"         \
  --address "0x..."      \
  --description "optional"
```

如果不存在 `.env.govilo`，则在运行前创建一个：

```dotenv
GOVILO_API_KEY=sk_live_xxx
SELLER_ADDRESS=0x...
```

`--input` 接受 ZIP 文件、文件夹或单个文件（可重复）。非 ZIP 输入将自动打包。

所有输出都是 JSON `{"ok": true/false, ...}`，失败时退出码为 1。

## 参数

| 参数           | 必填 | 来源                     | 描述                |
| --------------- | ---- | ------------------------ | ------------------- |
| `--input`       | 是   | CLI (可重复)             | ZIP、文件夹或文件路径 |
| `--title`       | 是   | CLI                      | 产品标题            |
| `--price`       | 是   | CLI                      | USDC 价格           |
| `--address`     | 否   | CLI > `SELLER_ADDRESS` 环境变量 | 卖家 EVM 钱包       |
| `--description` | 否   | CLI                      | 产品描述            |

## 工作流程

1. 验证配置（API Key + 卖家地址）
2. 打包输入 → ZIP（如果尚未为 ZIP）
3. `POST /api/v1/bot/uploads/presign` → 获取 upload_url + session_id
4. `PUT upload_url` → 将 ZIP 上传到 R2
5. `POST /api/v1/bot/items` → 获取 unlock_url

## 文件限制

- 最大 ZIP 大小：20 MB
- ZIP 中的最大文件数：20

## 设置

需要两个值：

| 变量         | 必填 | 描述                              |
| ------------ | ---- | --------------------------------- |
| `GOVILO_API_KEY` | 是   | 从 [govilo.xyz][] 获取的机器人 API 密钥 |
| `SELLER_ADDRESS` | 是*  | **Base 链** 上的 EVM 钱包地址     |

[govilo.xyz]: https://govilo.xyz/

*`SELLER_ADDRESS` 也可以通过 `--address` CLI 参数传递。

有关逐步注册和钱包设置说明，请参阅 [references/setup-guide.md](references/setup-guide.md)。

## API 参考

有关机器人 API 端点和错误代码，请参阅 [references/bot-api-quick-ref.md](references/bot-api-quick-ref.md)。
