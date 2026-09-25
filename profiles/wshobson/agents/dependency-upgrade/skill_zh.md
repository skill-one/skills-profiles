# 依赖升级

掌握主要依赖版本升级、兼容性分析、分阶段升级策略和全面测试方法。

## 使用此技能的场景

- 升级主要框架版本
- 更新存在安全漏洞的依赖
- 现代化遗留依赖
- 解决依赖冲突
- 规划增量升级路径
- 测试兼容性矩阵
- 自动化依赖更新

## 语义化版本控制审查

```
MAJOR.MINOR.PATCH (例如，2.3.1)

MAJOR：破坏性变更
MINOR：新功能，向后兼容
PATCH：修复错误，向后兼容

^2.3.1 = >=2.3.1 <3.0.0 (次要更新)
~2.3.1 = >=2.3.1 <2.4.0 (补丁更新)
2.3.1 = 精确版本
```

## 依赖分析

### 审计依赖

```bash
# npm
npm outdated
npm audit
npm audit fix

# yarn
yarn outdated
yarn audit

# 检查主要更新
npx npm-check-updates
npx npm-check-updates -u  # 更新 package.json
```

### 分析依赖树

```bash
# 查看为何安装了某个包
npm ls package-name
yarn why package-name

# 查找重复的包
npm dedupe
yarn dedupe

# 可视化依赖
npx madge --image graph.png src/
```

## 兼容性矩阵

```javascript
// compatibility-matrix.js
const compatibilityMatrix = {
  react: {
    "16.x": {
      "react-dom": "^16.0.0",
      "react-router-dom": "^5.0.0",
      "@testing-library/react": "^11.0.0",
    },
    "17.x": {
      "react-dom": "^17.0.0",
      "react-router-dom": "^5.0.0 || ^6.0.0",
      "@testing-library/react": "^12.0.0",
    },
    "18.x": {
      "react-dom": "^18.0.0",
      "react-router-dom": "^6.0.0",
      "@testing-library/react": "^13.0.0",
    },
  },
};

function checkCompatibility(packages) {
  // 验证包版本与矩阵的兼容性
}
```

## 分阶段升级策略

### 第一阶段：规划

```bash
# 1. 确定当前版本
npm list --depth=0

# 2. 检查破坏性变更
# 阅读CHANGELOG.md和MIGRATION.md

# 3. 创建升级计划
echo "升级顺序：
1. TypeScript
2. React
3. React Router
4. 测试库
5. 构建工具" > UPGRADE_PLAN.md
```

### 第二阶段：增量更新

```bash
# 不要一次性升级所有内容！

# 第一步：更新TypeScript
npm install typescript@latest

# 测试
npm run test
npm run build

# 第二步：更新React（一次一个主要版本）
npm install react@17 react-dom@17

# 再次测试
npm run test

# 第三步：继续更新其他包
npm install react-router-dom@6

# 以此类推...
```

### 第三阶段：验证

```javascript
// tests/compatibility.test.js
describe("依赖兼容性", () => {
  it("应该有兼容的React版本", () => {
    const reactVersion = require("react/package.json").version;
    const reactDomVersion = require("react-dom/package.json").version;

    expect(reactVersion).toBe(reactDomVersion);
  });

  it("不应该有伙伴依赖警告", () => {
    // 运行npm ls并检查警告
  });
});
```

## 破坏性变更处理

### 识别破坏性变更

```bash
# 直接查看CHANGELOG
curl https://raw.githubusercontent.com/facebook/react/master/CHANGELOG.md
```

### 代码转换自动修复

```bash
# 使用转换URL运行jscodeshift
npx jscodeshift -t <transform-url> <路径>

# 示例：重命名不安全的生命周期方法
npx jscodeshift -t https://raw.githubusercontent.com/reactjs/react-codemod/master/transforms/rename-unsafe-lifecycles.js src/

# 对于TypeScript文件
npx jscodeshift -t https://raw.githubusercontent.com/reactjs/react-codemod/master/transforms/rename-unsafe-lifecycles.js --parser=tsx src/

# 模拟运行预览变更
npx jscodeshift -t https://raw.githubusercontent.com/reactjs/react-codemod/master/transforms/rename-unsafe-lifecycles.js --dry src/
```

### 自定义迁移脚本

```javascript
// migration-script.js
const fs = require("fs");
const glob = require("glob");

glob("src/**/*.tsx", (err, files) => {
  files.forEach((file) => {
    let content = fs.readFileSync(file, "utf8");

    // 用新API替换旧API
    content = content.replace(
      /componentWillMount/g,
      "UNSAFE_componentWillMount",
    );

    // 更新导入
    content = content.replace(
      /import { Component } from 'react'/g,
      "import React, { Component } from 'react'",
    );

    fs.writeFileSync(file, content);
  });
});
```

## 测试策略

### 单元测试

```javascript
// 升级前后确保测试通过
npm run test

// 如需，更新测试工具
npm install @testing-library/react@latest
```

### 集成测试

```javascript
// tests/integration/app.test.js
describe("App集成", () => {
  it("应该正常渲染", () => {
    render(<App />);
  });

  it("应该处理导航", () => {
    const { getByText } = render(<App />);
    fireEvent.click(getByText("导航"));
    expect(screen.getByText("新页面")).toBeInTheDocument();
  });
});
```

### 视觉回归测试

```javascript
// visual-regression.test.js
describe("视觉回归", () => {
  it("应该匹配快照", () => {
    const { container } = render(<App />);
    expect(container.firstChild).toMatchSnapshot();
  });
});
```

### E2E测试

```javascript
// cypress/e2e/app.cy.js
describe("E2E测试", () => {
  it("应该完成用户流程", () => {
    cy.visit("/");
    cy.get('[data-testid="login"]').click();
    cy.get('input[name="email"]').type("user@example.com");
    cy.get('button[type="submit"]').click();
    cy.url().should("include", "/dashboard");
  });
});
```

## 自动化依赖更新

### Renovate配置

```json
// renovate.json
{
  "extends": ["config:base"],
  "packageRules": [
    {
      "matchUpdateTypes": ["minor", "patch"],
      "automerge": true
    },
    {
      "matchUpdateTypes": ["major"],
      "automerge": false,
      "labels": ["major-update"]
    }
  ],
  "schedule": ["周一凌晨3点前"],
  "timezone": "America/New_York"
}
```

### Dependabot配置

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "每周"
    open-pull-requests-limit: 5
    reviewers:
      - "team-leads"
    commit-message:
      prefix: "chore"
      include: "scope"
```

## 回滚计划

```javascript
// rollback.sh
#!/bin/bash

# 保存当前状态
git stash
git checkout -b upgrade-branch

# 尝试升级
npm install package@latest

# 运行测试
if npm run test; then
  echo "升级成功"
  git add package.json package-lock.json
  git commit -m "chore: 升级包"
else
  echo "升级失败，回滚"
  git checkout main
  git branch -D upgrade-branch
  npm install  # 从package-lock.json恢复
fi
```

## 常见升级模式

### 锁文件管理

```bash
# npm
npm install --package-lock-only  # 仅更新锁文件
npm ci  # 从锁文件干净安装

# yarn
yarn install --frozen-lockfile  # CI模式
yarn upgrade-interactive  # 交互式升级
```

### 伙伴依赖解析

```bash
# npm 7+: 严格伙伴依赖
npm install --legacy-peer-deps  # 忽略伙伴依赖

# npm 8+: 覆盖伙伴依赖
npm install --force
```

### 工作区升级

```bash
# 更新所有工作区包
npm install --workspaces

# 更新特定工作区
npm install package@latest --workspace=packages/app
```
