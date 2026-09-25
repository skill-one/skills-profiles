## 步骤

1. **将专家的照片添加到以下两个路径**：
   - `packages/docs/static/img/freelancers/<firstname>.png`
   - `packages/promo-pages/public/img/freelancers/<firstname>.png`

   图片应为方形头像（PNG格式）。两个路径必须使用相同的文件。

2. **在 `packages/promo-pages/src/components/experts/experts-data.tsx` 中的 `experts` 数组中添加一条记录**：

   ```tsx
   {
       slug: 'firstname-lastname',
       name: 'First Last',
       image: '/img/freelancers/<firstname>.png',
       website: 'https://example.com' | null,
       x: 'twitter_handle' | null,
       github: 'github_username' | null,
       linkedin: 'in/linkedin-slug/' | null,
       email: 'email@example.com' | null,
       videocall: 'https://cal.com/...' | null,
       since: new Date('YYYY-MM-DD').getTime(),
       description: (
           <div>
               专家的工作和专长简短描述。
               可以使用 `<a>` 标签包含项目链接。
           </div>
       ),
   },
   ```

   - `since` 应设置为今天的日期
   - `slug` 必须是名称的小写连字符版本
   - 将未使用的社交字段设置为 `null`
   - 该记录位于 `experts` 数组的末尾（在闭合 `]` 之前）

3. **通过在 `packages/docs` 中运行以下命令来渲染专家卡片**：

   ```
   bun render-cards
   ```

   这将生成 `packages/docs/static/generated/experts-<slug>.png`。验证其内容为 "Rendered experts-\<slug\>"（而不是 "Existed"）。
