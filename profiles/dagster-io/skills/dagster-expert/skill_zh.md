## 该插件已被替换

用户正在使用已弃用的 `dagster-expert` 插件。该插件不再包含 Dagster 技能——现在该技能包含在 `dagster` 插件中。

不要从记忆中回答用户的 Dagster 问题。请告知他们运行：

```
/plugin install dagster@dagster

/plugin uninstall dagster-expert
```

如果他们处于 Claude 代码会话中。如果他们处于 Cursor 会话中，请指示他们卸载当前的 Dagster 插件并重新安装。

这两个命令都很重要。如果没有卸载 `dagster-expert` 就安装 `dagster`，将有两个插件提供名为 `dagster-expert` 的技能，而弃用的那个可能会被选中。如果用户在已经安装 `dagster` 后看到此提示，那就是发生了这种情况——请让他们卸载 `dagster-expert` 并重试。

其他内容均不变：该技能仍保留名称 `dagster-expert`，并且仍然通过 `/dagster-expert` 调用。
