# firebase-firestore (`firebase/agent-skills/firebase-firestore`)

## whitebox

- 接收到 Firestore 相关任务 (建库/数据模型/索引/SDK 集成) 后, 先跑 `npx -y firebase-tools@latest firestore:databases:list` 列出现有数据库实例
- 对每个实例执行 `firestore:databases:get <id>` 检查其 `edition` 字段, 并询问用户要操作哪个实例、还是新建
- 若无实例或用户要新建: 默认创建 Enterprise 版, 先用 `firestore:locations` 让用户选地域, 再 `firestore:databases:create --edition="enterprise"` 建库
- 按已确定的 edition 打开对应参考文档目录: STANDARD → references/standard/, ENTERPRISE/原生模式 → references/enterprise/
- 参照其中的 provisioning / data_model / indexes / 各平台 SDK 用法文档执行具体任务

- CLI 驱动: 全部库操作依赖 Firebase CLI, 经 `npx -y firebase-tools@latest` 免安装调用, list/get/create/locations 都是单条命令
- edition 分流: 实例的 `edition` 字段 (STANDARD vs ENTERPRISE) 是唯一的文档路由开关, 决定加载哪套参考指南
- 强制阅读门禁: 给 Enterprise 写/改任何应用代码前, 必须先读目标平台 (Web/Python/Android/iOS/Flutter) 的 SDK 参考文档; 安全规则不在本技能内, 移交给 `firestore-rules-creation` 技能
