# 探测与方法论路由器

这是针对新目标和不明确攻击面的起始路由器。

## 使用场景

- 你刚刚获得了一个新目标，还不清楚首先应该测试什么
- 你需要从应用程序开始绘制攻击面，然后进行资产发现、指纹识别和测试路线规划
- 你希望基于结构化方法论来构建后续测试，而不是随机载荷枚举

## 技能图谱

- [攻击面绘制](../attack-surface-mapping/SKILL.md) — 从一个URL/一个应用程序出发，绘制主机、API、密钥和对象图
- [探测与方法论](../recon-and-methodology/SKILL.md)
- [不安全源代码管理](../insecure-source-code-management/SKILL.md) — .git/.svn/.hg暴露检测
- [依赖混淆](../dependency-confusion/SKILL.md) — 内部包名称的供应链侦察

## 推荐流程

1. 确认范围内的资产和目标类型
2. 从应用程序绘制攻击面：[攻击面绘制](../attack-surface-mapping/SKILL.md)
3. 将清单路由到 [api-sec](../api-sec/SKILL.md)、[auth-sec](../auth-sec/SKILL.md)、[injection-checking](../injection-checking/SKILL.md) 或 [business-logic-vuln](../business-logic-vuln/SKILL.md)
