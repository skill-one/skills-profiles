# impeccable (`pbakaus/impeccable/impeccable`)

## whitebox

- 加载上下文: 每会话运行一次 `impeccable context` 启动器, 载入 PRODUCT.md、DESIGN.md、界面简报及平台指引
- 路由请求: 按命令表把请求匹配到 reference/ 下的对应 playbook (无明确参数时只展示菜单, 绝不自动执行)
- 勘察现状: 编辑前先看目标代码/截图 (跑不起来时用视觉回归基线图), 并按界面类型选定模式 (Persuade/Operate/Read/Experience)
- 读取质量底线: 任何 UI 修改前立即读 craft-floor.md (质量下限、绝对禁令、直觉反射)
- 构建并限额验证: 完整实现 → 一轮批量截图检查 (桌面+移动同批) → 一批修完 → 至多一轮确认 → 停止打磨

- Playbook 路由系统: 每个命令 (craft/critique/polish/animate…) 对应一份 markdown 指南, 按'显式命令 > 隐含命令 > 泛设计工作'三级解析; 请求没有匹配命令时绝不自作主张跑命令
- 自包含启动器二进制: 首次运行时自动下载, 不依赖 Node 等运行时; Windows 无 sh 时改用 .cmd; 启动器失败则降级为直接读项目内现有 PRODUCT.md/DESIGN.md, 不凭空编造缺失上下文
- 有限次验证回路: 截图 → 缺陷扫描 → 批量微调 → 至多一轮确认, 硬性封顶, 杜绝无止境自检烧钱; 可选 hook 在 UI 文件编辑后自动运行设计探测器并汇报发现
