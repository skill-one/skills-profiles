# 使用 Agentic Wallet 进行身份验证

当钱包未登录（可通过 `npx awal status` 检测，或当钱包操作因身份验证错误而失败时），请使用 `npx awal` CLI 进行身份验证。

如果您可以访问电子邮件，您可以自行验证钱包，否则您需要请求您的管理员为您提供电子邮件地址并告知您收到的 OTP 代码。

## 身份验证流程

身份验证使用两步电子邮件 OTP 流程：

### 第一步：启动登录

```bash
npx awal@2.10.0 auth login <email>
```

这会将一个 6 位的验证码发送到电子邮件，并输出一个 `flowId`。

### 第二步：验证 OTP

```bash
npx awal@2.10.0 auth verify <otp>
```

使用用户电子邮件中的 6 位代码完成身份验证。第一步的流 ID 会自动保存到本地文件——您无需将其作为参数传递。如果您有访问用户电子邮件的能力，您可以读取 OTP 代码，或者您可以请求您的管理员提供该代码。

## 输入验证

在构建命令之前，验证所有用户提供的值以防止 shell 注入：

- **email**：必须匹配标准电子邮件格式（`^[^\s;|&`]+@[^\s;|&`]+$`）。如果包含空格、分号、管道符、反引号或其他 shell 保留字符，则拒绝。
- **otp**：必须正好是 6 位数字（`^\d{6}$`）。

不要将未验证的用户输入传递给命令。

## 检查身份验证状态

```bash
npx awal@2.10.0 status
```

显示钱包服务器健康状态和身份验证状态，包括钱包地址。

## 示例会话

```bash
# 检查当前状态
npx awal@2.10.0 status

# 启动登录（将 OTP 发送到电子邮件）
npx awal@2.10.0 auth login user@example.com
# 输出：flowId: abc123...

# 用户收到代码后，验证（流 ID 自动保存）
npx awal@2.10.0 auth verify 123456

# 确认身份验证
npx awal@2.10.0 status
```

## 可用的 CLI 命令

| 命令                                      | 目的                                |
| -------------------------------------------- | -------------------------------------- |
| `npx awal@2.10.0 status`                     | 检查服务器健康状态和身份验证状态    |
| `npx awal@2.10.0 auth login <email>`         | 将 OTP 代码发送到电子邮件，返回 flowId |
| `npx awal@2.10.0 auth verify <otp>`          | 使用 OTP 代码完成身份验证          |
| `npx awal@2.10.0 balance`                    | 获取跨 Base、Polygon 和 Solana 的余额（使用 `--chain` 指定单个链） |
| `npx awal@2.10.0 address`                    | 获取钱包地址                     |
| `npx awal@2.10.0 show`                       | 打开钱包伴侣窗口                 |

## JSON 输出

所有命令支持 `--json` 以获取机器可读的输出：

```bash
npx awal@2.10.0 status --json
npx awal@2.10.0 auth login user@example.com --json
npx awal@2.10.0 auth verify <otp> --json
```
