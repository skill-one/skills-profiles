## 设置

1. 在服务器配置中添加 `organization()` 插件
2. 在客户端配置中添加 `organizationClient()` 插件
3. 运行 `npx auth@latest migrate`（内置适配器）或为 Drizzle/Prisma 生成 + 推送
4. 验证：检查数据库中是否存在组织、成员、邀请表

```ts
import { betterAuth } from "better-auth";
import { organization } from "better-auth/plugins";

export const auth = betterAuth({
  plugins: [
    organization({
      allowUserToCreateOrganization: true,
      organizationLimit: 5, // 每个用户最多组织数量
      membershipLimit: 100, // 每个组织最多成员数量
    }),
  ],
});
```

### 客户端设置

```ts
import { createAuthClient } from "better-auth/client";
import { organizationClient } from "better-auth/client/plugins";

export const authClient = createAuthClient({
  plugins: [organizationClient()],
});
```

## 创建组织

创建者将自动被分配 `owner` 角色。

```ts
const createOrg = async () => {
  const { data, error } = await authClient.organization.create({
    name: "我的公司",
    slug: "my-company",
    logo: "https://example.com/logo.png",
    metadata: { plan: "pro" },
  });
};
```

### 控制组织创建

根据用户属性限制谁可以创建组织：

```ts
organization({
  allowUserToCreateOrganization: async (user) => {
    return user.emailVerified === true;
  },
  organizationLimit: async (user) => {
    // 高级用户可以获得更多组织
    return user.plan === "premium" ? 20 : 3;
  },
});
```

### 代表用户创建组织

管理员可以代表其他用户创建组织（仅服务器端）：

```ts
await auth.api.createOrganization({
  body: {
    name: "客户组织",
    slug: "client-org",
    userId: "将成为所有者的用户ID", // `userId` 是必需的
  },
});
```

**注意**：`userId` 参数不能与会话头一起使用。

## 活动组织

存储在会话中，并作用后续的 API 调用。在用户选择一个组织后设置。

```ts
const setActive = async (organizationId: string) => {
  const { data, error } = await authClient.organization.setActive({
    organizationId,
  });
};
```

许多端点在未提供 `organizationId` 时使用活动组织（例如 `listMembers`、`listInvitations`、`inviteMember` 等）。

使用 `getFullOrganization()` 获取活动组织及其所有成员、邀请和团队。

## 成员

### 添加成员（服务器端）

```ts
await auth.api.addMember({
  body: {
    userId: "用户ID",
    role: "member",
    organizationId: "组织ID",
  },
});
```

客户端添加成员时，请使用邀请系统。

### 分配多个角色

```ts
await auth.api.addMember({
  body: {
    userId: "用户ID",
    role: ["admin", "moderator"],
    organizationId: "组织ID",
  },
});
```

### 移除成员

使用 `removeMember({ memberIdOrEmail })`。最后一个所有者不能被移除——首先将所有权分配给其他成员。

### 更新成员角色

使用 `updateMemberRole({ memberId, role })`。

### 成员数量限制

```ts
organization({
  membershipLimit: async (user, organization) => {
    if (organization.metadata?.plan === "enterprise") {
      return 1000;
    }
    return 50;
  },
});
```

## 邀请

### 设置邀请邮件

```ts
import { betterAuth } from "better-auth";
import { organization } from "better-auth/plugins";
import { sendEmail } from "./email";

export const auth = betterAuth({
  plugins: [
    organization({
      sendInvitationEmail: async (data) => {
        const { email, organization, inviter, invitation } = data;

        await sendEmail({
          to: email,
          subject: `加入 ${organization.name}`,
          html: `
            <p>${inviter.user.name} 邀请你加入 ${organization.name}</p>
            <a href="https://yourapp.com/accept-invite?id=${invitation.id}">
              接受邀请
            </a>
          `,
        });
      },
    }),
  ],
});
```

### 发送邀请

```ts
await authClient.organization.inviteMember({
  email: "newuser@example.com",
  role: "member",
});
```

### 可分享的邀请链接

```ts
const { data } = await authClient.organization.getInvitationURL({
  email: "newuser@example.com",
  role: "member",
  callbackURL: "https://yourapp.com/dashboard",
});

// 通过任何渠道分享 data.url
```

此端点不会调用 `sendInvitationEmail`——请自行处理发送。

### 邀请配置

```ts
organization({
  invitationExpiresIn: 60 * 60 * 24 * 7, // 7 天（默认：48 小时）
  invitationLimit: 100, // 每个组织最多待处理的邀请
  cancelPendingInvitationsOnReInvite: true, // 重新邀请时取消旧的邀请
});
```

## 角色与权限

默认角色：`owner`（完全访问权限）、`admin`（管理成员/邀请/设置）、`member`（基本访问权限）。

### 检查权限

```ts
const { data } = await authClient.organization.hasPermission({
  permission: "member:write",
});

if (data?.hasPermission) {
  // 用户可以管理成员
}
```

使用 `checkRolePermission({ role, permissions })` 进行客户端 UI 渲染（静态仅）。对于动态访问控制，使用 `hasPermission` 端点。

## 团队

### 启用团队

```ts
import { organization } from "better-auth/plugins";

export const auth = betterAuth({
  plugins: [
    organization({
        teams: {
            enabled: true
        }
    }),
  ],
});
```

### 创建团队

```ts
const { data } = await authClient.organization.createTeam({
  name: "工程部",
});
```

### 管理团队成员

使用 `addTeamMember({ teamId, userId })`（成员必须先在组织中）和 `removeTeamMember({ teamId, userId })`（成员仍留在组织中）。

使用 `setActiveTeam({ teamId })` 设置活动团队。

### 团队数量限制

```ts
organization({
  teams: {
      maximumTeams: 20, // 每个组织最多团队数量
      maximumMembersPerTeam: 50, // 每个团队最多成员数量
      allowRemovingAllTeams: false, // 防止移除最后一个团队
  }
});
```

## 动态访问控制

### 启用动态访问控制

```ts
import { organization } from "better-auth/plugins";
import { dynamicAccessControl } from "@better-auth/organization/addons";

export const auth = betterAuth({
  plugins: [
    organization({
        dynamicAccessControl: {
            enabled: true
        }
    }),
  ],
});
```

### 创建自定义角色

```ts
await authClient.organization.createRole({
  role: "moderator",
  permission: {
    member: ["read"],
    invitation: ["read"],
  },
});
```

使用 `updateRole({ roleId, permission })` 和 `deleteRole({ roleId })`。预定义角色（owner、admin、member）不能被删除。分配给成员的角色在重新分配之前不能被删除。

## 生命周期钩子

在组织生命周期的各个阶段执行自定义逻辑：

```ts
organization({
  hooks: {
    organization: {
      beforeCreate: async ({ data, user }) => {
        // 创建前验证或修改数据
        return {
          data: {
            ...data,
            metadata: { ...data.metadata, createdBy: user.id },
          },
        };
      },
      afterCreate: async ({ organization, member }) => {
        // 创建后逻辑（例如，发送欢迎邮件，创建默认资源）
        await createDefaultResources(organization.id);
      },
      beforeDelete: async ({ organization }) => {
        // 删除前清理
        await archiveOrganizationData(organization.id);
      },
    },
    member: {
      afterCreate: async ({ member, organization }) => {
        await notifyAdmins(organization.id, `新成员加入`);
      },
    },
    invitation: {
      afterCreate: async ({ invitation, organization, inviter }) => {
        await logInvitation(invitation);
      },
    },
  },
});
```

## 模式自定义

自定义表名、字段名，并添加额外字段：

```ts
organization({
  schema: {
    organization: {
      modelName: "workspace", // 重命名表
      fields: {
        name: "workspaceName", // 重命名字段
      },
      additionalFields: {
        billingId: {
          type: "string",
          required: false,
        },
      },
    },
    member: {
      additionalFields: {
        department: {
          type: "string",
          required: false,
        },
        title: {
          type: "string",
          required: false,
        },
      },
    },
  },
});
```

## 安全注意事项

### 所有者保护

- 最后一个所有者不能被移出组织
- 最后一个所有者不能离开组织
- 所有者角色不能被移除到最后一个所有者

在移除当前所有者之前，始终确保所有权转移：

```ts
// 首先转移所有权
await authClient.organization.updateMemberRole({
  memberId: "新所有者成员ID",
  role: "owner",
});

// 然后之前的所有者可以被降级或移除
```

### 组织删除

删除组织会删除所有相关数据（成员、邀请、团队）。防止意外删除：

```ts
organization({
  disableOrganizationDeletion: true, // 通过配置禁用
});
```

或通过钩子实现软删除：

```ts
organization({
  hooks: {
    organization: {
      beforeDelete: async ({ organization }) => {
        // 软删除而不是硬删除
        await archiveOrganization(organization.id);
        throw new Error("组织已归档，未删除");
      },
    },
  },
});
```

### 邀请安全

- 邀请默认在 48 小时后过期
- 只有被邀请的邮箱地址可以接受邀请
- 组织管理员可以取消待处理的邀请

## 完整配置示例

```ts
import { betterAuth } from "better-auth";
import { organization } from "better-auth/plugins";
import { sendEmail } from "./email";

export const auth = betterAuth({
  plugins: [
    organization({
      // 组织限制
      allowUserToCreateOrganization: true,
      organizationLimit: 10,
      membershipLimit: 100,
      creatorRole: "owner",

      // Slugs
      defaultOrganizationIdField: "slug",

      // 邀请
      invitationExpiresIn: 60 * 60 * 24 * 7, // 7 天
      invitationLimit: 50,
      sendInvitationEmail: async (data) => {
        await sendEmail({
          to: data.email,
          subject: `加入 ${data.organization.name}`,
          html: `<a href="https://app.com/invite/${data.invitation.id}">接受</a>`,
        });
      },

      // 钩子
      hooks: {
        organization: {
          afterCreate: async ({ organization }) => {
            console.log(`组织 ${organization.name} 已创建`);
          },
        },
      },
    }),
  ],
});
```
