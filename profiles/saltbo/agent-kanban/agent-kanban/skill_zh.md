# Agent Kanban v2分配代理

使用已分配到机构代理的Realmroot身份。切勿运行已移除的`ak` CLI或创建AK凭证、机器、运行时会话、邮箱状态、签名密钥或代理角色。

## 任务生命周期

1. 使用通用工具箱资源操作读取任务：

   ```bash
   realmroot toolbox get agent-kanban/tasks/<task-id> --include --json
   ```

   将返回的表示视为权威。任务PATCH操作执行自己的乐观并发检查；如果返回`409`，则在决定是否重试之前重新读取任务。

2. 在更改目标存储库之前声明它：

   ```bash
   realmroot toolbox post agent-kanban/tasks/<task-id>/claims --json
   ```

   如果声明被拒绝，则不要修改存储库。只有当前分配到任务的已验证Realmroot代理行为者才能声明它。

3. 将有用进度记录为任务笔记资源：

   ```bash
   realmroot toolbox post agent-kanban/tasks/<task-id>/notes \
     --content-type application/json \
     '{"detail":"实现了解析器并验证了格式错误的输入。"}' --json
   ```

   Realmroot工具箱v0.5.0或更新版本会生成所需的幂等性密钥并在此调用的临时重试中重复使用它。仅在用已知密钥从先前调用中恢复且结果仍未知时提供显式的`Idempotency-Key`。

4. 执行工作并运行最小的检查以证明更改的行为和边界。将存储库工作放在可审查的分支上。对于认证的GitHub命令，使用Realmroot的GitHub资源，例如`realmroot exec github -- git push`或`realmroot exec github -- gh ...`。

5. 发布包含结果、确切检查和任何剩余阻塞性的最终笔记，然后提交任务以供审查：

   ```bash
   realmroot toolbox get agent-kanban/tasks/<task-id> --include --json
   realmroot toolbox patch agent-kanban/tasks/<task-id> \
     --content-type application/merge-patch+json \
     '{"status":"in-review","pullRequestUrl":"https://github.com/owner/repo/pull/123"}' --json
   ```

   当任务没有拉取请求时，提交一个显式的空表示：

   ```bash
   realmroot toolbox patch agent-kanban/tasks/<task-id> \
     --content-type application/merge-patch+json \
     '{"status":"in-review"}' --json
   ```

   在机构工作会话停止之前，其声明的任务必须提交以供审查。如果工作无法继续，请在最终任务笔记中解释阻塞性并提交当前状态；不要留下表示为`in_progress`的未活动会话。

## 发布命令

使用工具箱的通用动词优先操作来处理AK资源：

```bash
realmroot toolbox get agent-kanban/tasks/<task-id> --json
realmroot toolbox get agent-kanban/tasks/<task-id>/notes --json
realmroot toolbox post agent-kanban/tasks/<task-id>/notes \
  --content-type application/json @note.json --json
realmroot toolbox post agent-kanban/tasks/<task-id>/claims --json
realmroot toolbox patch agent-kanban/tasks/<task-id> \
  --content-type application/merge-patch+json \
  '{"status":"in-review"}' --json
realmroot toolbox agent-kanban task wait <task-id> in-review --wait-seconds 25 --json
```

`task wait`是唯一一个由AK生成的资源优先的便利命令。不要使用已移除的`task claim`、`task release`、`task review`、`task reject`、`task complete`或`task cancel`别名。

如果工具箱在服务器合约部署后仍然显示这些已移除的别名，请刷新其缓存的操作清单一次：

```bash
realmroot toolbox sync agent-kanban
```

如果生成的命令的请求形状不明确，请检查合约而不是猜测标志：

```bash
realmroot toolbox patch agent-kanban/tasks/<task-id> --generate-body
```

分配会直接启动Enbor会话。其初始提示会提供任务ID和确切的AK上下文ID。使用该上下文进行每个工具箱操作，然后在采取行动之前读取任务。使用您自己的已附加的代理身份声明任务；切勿写入或猜测会话ID。AK的会话注释记录了创建收据，而声明记录了经过验证的执行身份。

审查拒绝会将反馈发送到同一会话。重新读取任务和笔记，在现有声明下继续，并在完成后提交新的审查。完成和取消会关闭相关会话。收箱消息不是启动或继续机制。

对于具有作为`user:<subject-id>`编码的个人所有者ID的历史业务参考，上下文ID是`<subject-id>`；使用组织所有者ID不变。未实现延迟调度。

## 错误处理

- `401`或无效DPoP：Realmroot权限不可用；不要创建后备凭证。
- `403`：已验证的行为者或授权缺乏所需权限；更改请求正文不能授予它。
- `409`：重新读取受影响资源并根据其当前状态决定；不要盲目重放冲突的转换。
- `412`：条件删除使用了过时的资源ETag；在决定删除是否仍然合适之前重新读取。
- `429`或`503`：尊重`Retry-After`。在未知任务PATCH结果后，在决定是否重试之前重新读取其当前表示。声明创建受幂等性密钥保护。
