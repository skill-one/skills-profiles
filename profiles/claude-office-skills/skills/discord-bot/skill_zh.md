# Discord Bot

构建用于社区管理、 moderation、通知和 AI 集成的 Discord 机器人。基于 n8n 的 Discord 工作流模板。

## 概述

本技能涵盖：
- 机器人设置和配置
- 剪辑命令和交互
- moderation 自动化
- 通知工作流
- AI 驱动的功能

---

## 机器人设置

### 创建 Discord 机器人

```yaml
setup_steps:
  1. create_application:
      url: https://discord.com/developers/applications
      action: "New Application"
      
  2. create_bot:
      section: "Bot"
      action: "Add Bot"
      copy: token
      
  3. configure_intents:
      enable:
        - PRESENCE_INTENT
        - SERVER_MEMBERS_INTENT
        - MESSAGE_CONTENT_INTENT
        
  4. invite_bot:
      section: "OAuth2 > URL Generator"
      scopes: [bot, applications.commands]
      permissions: [based_on_needs]
      generate: invite_link
```

### 剪辑命令

```yaml
slash_commands:
  - name: help
    description: "显示机器人帮助"
    
  - name: ping
    description: "检查机器人延迟"
    
  - name: poll
    description: "创建投票"
    options:
      - name: question
        type: STRING
        required: true
      - name: options
        type: STRING
        required: true
        
  - name: remind
    description: "设置提醒"
    options:
      - name: time
        type: STRING
        required: true
      - name: message
        type: STRING
        required: true
```

---

## Moderation Bot

### 自动化 Moderation

```yaml
auto_moderation:
  spam_detection:
    triggers:
      - repeated_messages: 5_in_10_seconds
      - mass_mentions: more_than_5
      - link_spam: multiple_links_no_text
    actions:
      - delete_messages
      - timeout: 5_minutes
      - log_to_mod_channel
      
  word_filter:
    blocked_words: [list_of_words]
    action:
      - delete_message
      - warn_user
      
  link_filter:
    allowed_domains: [youtube.com, github.com]
    action: delete_if_not_allowed
    
  raid_protection:
    triggers:
      - join_rate: 10_per_minute
    actions:
      - enable_verification
      - notify_mods
      - slow_mode: enable
```

### Moderation 命令

```yaml
mod_commands:
  /warn:
    permission: MODERATE_MEMBERS
    action: |
      1. 记录警告
      2. 通过私信通知用户原因
      3. 记录到 mod 频道
      
  /timeout:
    permission: MODERATE_MEMBERS
    options: [user, duration, reason]
    action: |
      1. 应用 timeout
      2. 通过私信通知用户
      3. 记录操作
      
  /ban:
    permission: BAN_MEMBERS
    options: [user, reason, delete_messages]
    action: |
      1. 禁用用户
      2. 记录到 mod 频道
      3. 可选：发布到 #bans
      
  /warnings:
    permission: MODERATE_MEMBERS
    action: show_user_warning_history
```

---

## 社区功能

### 欢迎系统

```yaml
welcome_system:
  on_member_join:
    actions:
      - assign_role: "New Member"
      - send_dm:
          template: |
            👋 欢迎加入 {server_name}!
            
            如何开始：
            1. 阅读 #rules
            2. 在 #roles 获取角色
            3. 在 #introductions 介绍自己
            
            需要帮助？请在 #support 发问
            
      - post_welcome:
          channel: "#welcome"
          template: |
            🎉 欢迎加入服务器 {user_mention}!
            
            他们是第 #{member_count} 位成员
            
  on_member_leave:
    channel: "#logs"
    template: "{user} 离开了服务器。加入时长：{time_since_join}"
```

### 角色管理

```yaml
reaction_roles:
  channel: "#roles"
  message: |
    通过反应获取角色：
    
    🎮 - 游戏玩家
    💻 - 开发者
    🎨 - 艺术家
    📚 - 学生
    
  mappings:
    "🎮": role_id_gamer
    "💻": role_id_developer
    "🎨": role_id_artist
    "📚": role_id_student
    
level_roles:
  system: xp_based
  roles:
    - level: 5
      role: "Active Member"
    - level: 10
      role: "Regular"
    - level: 25
      role: "Veteran"
    - level: 50
      role: "Legend"
```

### 工单系统

```yaml
ticket_system:
  create_ticket:
    trigger: button_click OR /ticket
    action:
      - create_channel: "ticket-{user}-{number}"
      - set_permissions: [user, support_team]
      - send_initial_message:
          template: |
            🎫 **Support Ticket**
            
            用户：{user_mention}
            创建时间：{timestamp}
            
            请描述您的问题，我们的团队将尽快协助您。
            
            通过 ✅ 反应关闭此工单。
            
  close_ticket:
    trigger: reaction OR /close
    action:
      - save_transcript: to_logs_channel
      - delete_channel: after_5_seconds
      - dm_user: transcript_link
```

---

## 通知工作流

### n8n 集成

```yaml
workflow: "Discord Notifications"

triggers:
  github_release:
    action:
      channel: "#releases"
      embed:
        title: "🚀 新版本发布：{version}"
        description: "{release_notes}"
        color: 0x00ff00
        fields:
          - name: "下载"
            value: "[链接]({download_url})"
            
  twitch_live:
    action:
      channel: "#streams"
      message: "@everyone {streamer} 现在正在直播！"
      embed:
        title: "{stream_title}"
        image: "{thumbnail}"
        
  youtube_video:
    action:
      channel: "#videos"
      embed:
        title: "{video_title}"
        description: "{description}"
        thumbnail: "{thumbnail}"
```

### 定时发布

```yaml
scheduled_posts:
  daily_question:
    schedule: "10am daily"
    channel: "#daily-discussion"
    template: |
      🤔 **每日问题**
      
      {random_question}
      
      在下方分享您的想法！ 👇
      
  weekly_recap:
    schedule: "Sunday 6pm"
    channel: "#announcements"
    template: |
      📊 **每周服务器回顾**
      
      新成员：{new_members}
      消息数：{message_count}
      最活跃频道：{top_channel}
      顶级贡献者：{top_user}
      
      感谢您成为我们社区的一员！ ❤️
```

---

## AI 集成

### AI 聊天机器人

```yaml
ai_bot:
  trigger: mention OR dm
  
  configuration:
    model: gpt-4
    system_prompt: |
      你是一个有帮助的 Discord 机器人助手。
      - 友善并使用适合 Discord 的语言
      - 自然地使用表情符号
      - 保持回复简洁
      - 帮助回答与服务器相关的问题
      
  features:
    - conversation_memory: per_channel
    - rate_limiting: 10_per_minute
    - content_filter: enabled
    
  commands:
    /ask:
      description: "向 AI 提问"
      action: ai_response
      
    /summarize:
      description: "总结最近的消息"
      action: summarize_channel_history
```

### 图像生成

```yaml
image_generation:
  command: /imagine
  
  options:
    - prompt: STRING (required)
    - style: CHOICE [realistic, anime, cartoon, abstract]
    - size: CHOICE [square, portrait, landscape]
    
  workflow:
    1. receive_command
    2. send_generating_message
    3. call_dalle_api
    4. send_result_with_buttons:
        - Regenerate
        - Upscale
        - Variations
```

---

## Embeds & Components

### Rich Embed

```yaml
embed:
  title: "服务器信息"
  description: "欢迎加入我们的社区！"
  color: 0x5865F2  # Discord blurple
  
  thumbnail:
    url: "{server_icon}"
    
  fields:
    - name: "📊 成员"
      value: "{member_count}"
      inline: true
    - name: "💬 频道"
      value: "{channel_count}"
      inline: true
    - name: "🎭 角色"
      value: "{role_count}"
      inline: true
    - name: "📅 创建时间"
      value: "{creation_date}"
      inline: false
      
  footer:
    text: "最后更新"
    icon_url: "{bot_avatar}"
    
  timestamp: "{current_time}"
```

### 按钮组件

```yaml
buttons:
  row_1:
    - type: button
      style: primary
      label: "接受规则"
      custom_id: "accept_rules"
      
    - type: button
      style: secondary
      label: "查看规则"
      custom_id: "view_rules"
      
  row_2:
    - type: button
      style: link
      label: "网站"
      url: "https://example.com"
      
    - type: button
      style: danger
      label: "离开"
      custom_id: "leave_confirm"
```

---

## 输出示例

**请求**: "创建一个 Discord 欢迎机器人"

**输出**:

```markdown
# Discord 欢迎机器人

## 配置

```yaml
events:
  - guildMemberAdd
  - guildMemberRemove
```

## 欢迎消息

```javascript
// On member join
const welcomeEmbed = {
  title: '👋 欢迎加入服务器!',
  description: `嘿 ${member.user}, 欢迎加入 **${guild.name}**!`,
  color: 0x00ff00,
  fields: [
    { name: '📜 规则', value: '检查 <#rules-channel>', inline: true },
    { name: '🎭 角色', value: '在 <#roles> 获取角色', inline: true },
    { name: '💬 聊天', value: '在 <#general> 打招呼', inline: true }
  ],
  thumbnail: { url: member.user.displayAvatarURL() },
  footer: { text: `成员 #${guild.memberCount}` }
};

welcomeChannel.send({ embeds: [welcomeEmbed] });
```

## 自动分配角色

```javascript
// 分配 "New Member" 角色
await member.roles.add(newMemberRole);
```

## DM 欢迎消息

```javascript
// 发送 DM 服务器信息
await member.send({
  content: `欢迎加入 ${guild.name}! 这里是您需要了解的一切...`,
  embeds: [infoEmbed]
});
```

## n8n 工作流

```yaml
trigger: Discord - On Member Join
actions:
  - Discord - 发送频道消息 (welcome)
  - Discord - 添加角色
  - Discord - 发送 DM
  - Google Sheets - 记录新成员
```
```

---

*Discord Bot 技能 - Claude 办公技能的一部分*
