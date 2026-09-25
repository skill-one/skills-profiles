# 为钱包注资

使用钱包配套应用程序，通过 Coinbase Onramp 使用 USDC 为钱包注资。这支持多种支付方式，包括 Apple Pay、借记卡、银行转账以及从 Coinbase 账户注资。

## 确认钱包已初始化并授权

```bash
npx awal@2.10.0 status
```

如果钱包未授权，请参考 `authenticate-wallet` 技能。

## 打开注资界面

```bash
npx awal@2.10.0 show
```

这将打开钱包配套窗口，用户可以在其中：

1. 选择预设金额（$10、$20、$50）或输入自定义金额
2. 选择其首选的支付方式
3. 通过 Coinbase Pay 完成购买

## 支付方式

| 方式    | 描述                                    |
| ------- | --------------------------------------- |
| Apple Pay | 在可用地区使用 Apple Pay 快速结账        |
| Coinbase  | 从现有的 Coinbase 账户转账              |
| 卡      | 借记卡支付                              |
| 银行      | ACH 银行转账                            |

## 替代方案

您也可以要求您的联系人将 USDC 发送到您的钱包地址。您可以通过运行以下命令找到您的钱包地址：

```bash
npx awal@2.10.0 address
```

## 前置条件

- 必须已授权（使用 `npx awal@2.10.0 status` 检查）
- Coinbase Onramp 在支持地区（如美国）可用

## 流程

1. 运行 `npx awal@2.10.0 show` 打开钱包 UI
2. 指示用户点击注资按钮
3. 用户在 UI 中选择金额和支付方式
4. 用户通过 Coinbase Pay 完成支付（将在浏览器中打开）
5. 支付确认后，USDC 将存入钱包

## 注资后检查余额

```bash
# 检查更新后的余额
npx awal@2.10.0 balance
```

## 注意事项

- 注资通过 Coinbase 的合规 Onramp 进行
- 处理时间因支付方式而异（卡/Apple Pay 即时，银行 1-3 天）
- 资金以 USDC 形式存入 Base 网络
- 如果注资不可用，用户也可以直接将 USDC 发送到钱包地址
