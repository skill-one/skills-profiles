# 使用 sops

使用此布局的仓库将它们的秘密提交到 git 作为 sops 加密的 dotenv 文件，每个部署环境一个：`secrets/dev.env`，`secrets/prod.env`。这些文件使用 age 身份进行解密。没有 `.env`，没有秘密服务，也没有需要登录的会话。每个检出、工作树和云沙盒在克隆时都拥有加密文件；任何地方的唯一输入是一个 age 私钥。

`pnpm secrets` (`tools/secrets.ts`) 是唯一的接口。在具有包装器的仓库中不要直接调用 `sops`。

## 身份

| 身份   | 范围       | 私钥存储位置                                       | 解密    |
| ---------- | ----------- | ---------------------------------------------------------------- | ----------- |
| `agent`    | 用户级   | 在代理运行的每台机器上的 `~/.config/sops/age/keys.txt`；云沙盒中的 `SOPS_AGE_KEY` | `dev.env` |
| `personal` | 用户级   | 用户的密码管理器                                      | 列出其公钥的文件 |
| `prod`     | 每个项目 | 该项目的生产平台和文档化密码管理器条目               | `prod.env` |

`.sops.yaml` 通过公钥列出接收者。加密不需要私钥；解密或编辑需要一个接收者的私钥。`agent` 和 `personal` 是每个项目共享的本地开发密钥；`prod` 是每个项目生成的，因此一个泄露的部署变量会暴露一个项目。这些是约定，不是保证的接收者。现有仓库可能仅使用共享的 `dev` 和 `prod` 密钥。在选择密钥之前，请阅读仓库的秘密指南和 `.sops.yaml`；加密文件的接收者元数据决定了哪些身份可以解密它。

## 代理工作流程

开发秘密由您自行管理，无需询问：

```sh
pnpm secrets show dev                    # 所有内容，已解密
pnpm secrets get dev STRIPE_KEY
pnpm secrets set dev STRIPE_KEY sk_test_1
pnpm secrets unset dev STRIPE_KEY
pnpm secrets exec dev -- node apps/worker/src/main.ts
```

`exec` 将解密后的值放入子进程的环境（覆盖 shell 的环境），移除 `SOPS_AGE_KEY*`，转发信号，并以子进程的状态退出。

当授权任务需要生产秘密时，请自行执行提升。不要要求用户运行命令或重新确认已授权的任务。

1. 使用 `pnpm secrets exec prod -- true` 检查访问权限，该命令不会打印秘密值。仅存在 `.age/elevated` 文件并不能证明其密钥可以解密 prod。
2. 如果访问失败，请阅读仓库的秘密指南和接收者配置。使用匹配密钥的文档化账户、保险库、条目和字段。不要假设 `Personal` 保险库、`age-personal` 接收者或 CLI 的默认账户。
3. 自己运行文档化的读取操作，将密钥直接管道到包装器：`op read 'op://VAULT/ITEM/FIELD' --account ACCOUNT | pnpm secrets elevate`。替换占位符为发现的标识符；永远不要打印密钥。
4. 使用 `pnpm secrets exec prod -- true` 确认解密，然后继续任务。

当文档化的 1Password 位置缺失时，使用 `op account list --format json` 和 `op vault list --account ACCOUNT --format json` 来识别正确的账户和保险库。在保险库中搜索条目元数据以找到文档化的密钥名称，使用 `op item list --account ACCOUNT --vault VAULT --format json`；仅检查匹配的条目。后续读取时传递 `--account`。`Private`、`Personal` 和 `Shared` 是不同的名称，不是可互换的别名。如果找到密钥但无法解密，请比较其公钥与文件的接收者，而不是重复尝试保险库名称。将私钥保持在工具输出之外。

仅在需要用户交互时才询问用户，例如解锁 1Password 或授予不可用访问权限。说明实际的阻碍。提升是针对每次检出的，持续到删除 `.age/elevated` 为止；不要将其复制到其他工作树。

当您添加变量时，请将其添加到 env 模板和您可以解密的每个 `secrets/<env>.env`。如果您无法解密 prod，请在 PR 中说明：类型 env 检查会失败，直到值被设置，这是预期的信号。

永远不要将 `AGE-SECRET-KEY-...` 写入跟踪文件、日志或提交。永远不要将 `personal` 或 `prod` 放入云环境。

## 人工设置

对于一次性步骤（生成密钥、安装 `sops` 和 `age`、将 `agent` 密钥连接到代理工具和云沙盒、配置生产平台和旋转密钥），请阅读 `references/setup.md`。当用户要求提醒步骤时，请按顺序引导他们阅读该文件。

对于设计依赖的 sops 和 age 行为（身份联合、`updatekeys`、`exec-env` 限制、dotenv 特性），请阅读 `references/sops-notes.md`。
