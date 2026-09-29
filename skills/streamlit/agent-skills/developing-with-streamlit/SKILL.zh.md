---
name: developing-with-streamlit
description: 用于所有 Streamlit 任务：创建、编辑、调试、美化、样式设置、主题化、优化或部署 Streamlit 应用。还包括自定义组件、st.components.v2、HTML/JS/CSS 工作。从用户已安装的 Streamlit（>=1.57）中发现并加载版本匹配的参考文档。触发器：streamlit、st.、dashboard、app.py、beautify、style、CSS、颜色、背景、主题、按钮、组件样式、自定义组件、st.components、CCv2、会话状态、性能、缓存、片段、慢速重跑、部署。
---

# 使用 Streamlit 开发

Streamlit (>=1.57) 在其 pip 包中提供了详细的参考文档，用于在 Streamlit 应用内部进行开发。捆绑的功能包括一个路由 `SKILL.md`，以及一个 `references/` 文件夹，其中包含针对特定主题的参考文档（仪表板、主题、布局、会话状态、自定义组件等）。

## 使用方法

使用用户的工程目录运行发现脚本：

```bash
python <SKILL_DIR>/scripts/discover.py --project-dir <USER_PROJECT_DIR>
```

该脚本会打印：

- **标准输出上的路径**（退出码 0）— 捆绑的 `SKILL.md`。阅读它；它会指向 `references/`。
- **标准错误上的 `ERROR:` 块**（非零退出）。按照打印的指示操作并重新运行。

`<SKILL_DIR>` 是包含此文件的目录；`<USER_PROJECT_DIR>` 是用户工程的绝对路径。传递 `--project-dir` 很重要，因为脚本会相对于它解析 `.venv`、`../.venv`、`Pipfile`、`poetry.lock`、`pdm.lock` 和 `uv.lock`。
