# 创建管理员用户

在 Medusa 中使用指定的邮箱和密码创建一个新的管理员用户。

用户将提供两个参数：
- 第一个参数：邮箱地址
- 第二个参数：密码

例如：`/medusa-dev:user admin@test.com supersecret`

使用 Bash 工具执行命令 `npx medusa user -e <email> -p <password>`，将 `<email>` 替换为第一个参数，将 `<password>` 替换为第二个参数。

向用户报告结果，包括：

- 确认管理员用户是否创建成功
- 创建用户的邮箱地址
- 任何发生的错误
- 下一步操作（例如，登录到管理员控制面板）
