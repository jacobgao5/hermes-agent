# 飞书 (Feishu/Lark) 对接 Hermes 配置指南

## 概述

Hermes 已内置完整的飞书平台适配器，支持：
- ✅ WebSocket 长连接和 Webhook 两种传输模式
- ✅ 私聊和群聊（@机器人）消息收发
- ✅ 图片/文件/音频媒体文件处理
- ✅ 交互式卡片消息
- ✅ 消息去重和批量处理
- ✅ 允许列表集成（FEISHU_ALLOWED_USERS）

---

## 步骤 1: 安装依赖

```bash
# 激活 Hermes 虚拟环境
source ~/hermes-agent/venv/bin/activate

# 安装飞书 SDK 和相关依赖
pip install lark-oapi qrcode aiohttp websockets
```

---

## 步骤 2: 创建飞书应用

### 方式 A: 扫码自动注册（推荐）

Hermes 支持飞书应用的扫码自动注册功能。运行：

```bash
# 在 Hermes CLI 中运行
hermes gateway feishu onboard
```

系统会：
1. 生成一个二维码
2. 用飞书 App 扫描二维码
3. 自动创建应用并获取 App ID 和 App Secret
4. 自动配置到 config.yaml

### 方式 B: 手动创建应用

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 登录企业开发者账号
3. 点击「创建企业自建应用」
4. 填写应用名称和图标
5. 在「凭证与基础信息」页面获取：
   - **App ID** (cli_xxx)
   - **App Secret**

---

## 步骤 3: 配置应用权限

在飞书开放平台应用管理页面，添加以下权限：

### 机器人能力
- ✅ 发送消息
- ✅ 读取与回复群消息
- ✅ 获取用户信息

### 事件订阅
- ✅ 接收消息
- ✅ 消息已读
- ✅ 卡片消息交互

### 安全设置
- 启用「加密」，获取 **Encrypt Key**
- 设置 **Verification Token**

---

## 步骤 4: 配置 Hermes

编辑 `~/.hermes/config.yaml`，添加飞书平台配置：

```yaml
platforms:
  feishu:
    enabled: true
    extra:
      app_id: "cli_xxxxxxxxxxxxxxxx"
      app_secret: "xxxxxxxxxxxxxxxxxxxxxxxx"
      domain: "feishu"  # 或 "lark" (国际版)
      connection_mode: "websocket"  # 或 "webhook"
      encrypt_key: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
      verification_token: "xxxxxxxxxxxxxxxx"
      
      # 可选：群组策略
      group_policy: "mention_only"  # mention_only | open | disabled
      allowed_users: []  # 允许列表（用户 open_id）
      
      # 可选：Webhook 模式配置
      webhook_host: "0.0.0.0"
      webhook_port: 8765
      webhook_path: "/feishu/webhook"
```

### 环境变量方式

也可以在 `~/.hermes/.env` 中配置：

```bash
# 飞书平台配置
FEISHU_ENABLED=true
FEISHU_APP_ID=cli_xxxxxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxx
FEISHU_DOMAIN=feishu
FEISHU_CONNECTION_MODE=websocket
FEISHU_ENCRYPT_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
FEISHU_VERIFICATION_TOKEN=xxxxxxxxxxxxxxxx

# 可选
FEISHU_GROUP_POLICY=mention_only
FEISHU_ALLOWED_USERS=open_id1,open_id2
```

---

## 步骤 5: 配置事件订阅（Webhook 模式）

如果使用 Webhook 模式（非 WebSocket）：

1. 在飞书开放平台「事件订阅」页面
2. 配置订阅地址：`https://your-domain.com/feishu/webhook`
3. 使用配置的 Verification Token 验证 URL
4. 订阅以下事件：
   - `im.message.receive_v1` - 接收消息
   - `im.message.message_read_v1` - 消息已读
   - `card.action.trigger` - 卡片交互

---

## 步骤 6: 启动网关

```bash
# 启动 Hermes 网关
hermes gateway run
```

或在 systemd 服务中：
```bash
systemctl --user start hermes-gateway
systemctl --user status hermes-gateway
```

---

## 步骤 7: 测试连接

### 测试私聊
1. 在飞书中找到你的机器人
2. 发送消息：`你好`
3. 检查网关日志是否有响应

### 测试群聊
1. 将机器人添加到群聊
2. @机器人 并发送消息：`@机器人 你好`
3. 检查响应

### 查看日志
```bash
# 查看网关日志
tail -f ~/.hermes/logs/gateway.log | grep -i feishu
```

---

## 常用命令

```bash
# 查看飞书平台状态
hermes gateway status

# 重新加载配置
hermes gateway reload

# 查看连接的机器人信息
hermes gateway feishu info
```

---

## 故障排查

### 1. "app_id or app_secret is required"
检查 config.yaml 或 .env 中是否正确配置了凭证。

### 2. "verification token mismatch"
确保飞书开放平台的 Verification Token 与配置一致。

### 3. "encrypt key validation failed"
检查 Encrypt Key 是否正确复制，没有多余空格。

### 4. WebSocket 连接失败
- 检查网络连接
- 确认 domain 设置正确（feishu vs lark）
- 查看网关日志详细错误

### 5. 收不到群消息
- 确保机器人已添加到群聊
- 检查群策略设置（group_policy）
- 确认已开启「接收群消息」权限

---

## 高级配置

### 群组策略

```yaml
extra:
  # 全局策略
  group_policy: "mention_only"  # 仅@机器人时响应
  
  # 或按群配置
  group_rules:
    "chat_id_1":
      policy: "open"  # 开放，任何人可交互
      allowlist: []
    "chat_id_2":
      policy: "allowlist"  # 仅允许列表用户
      allowlist:
        - "ou_xxxxx"  # 用户 open_id
    "chat_id_3":
      policy: "disabled"  # 禁用
```

### 批量处理优化

```yaml
extra:
  # 文本消息批量处理
  text_batch_delay_seconds: 0.6
  text_batch_max_messages: 8
  text_batch_max_chars: 4000
  
  # 媒体消息批量处理
  media_batch_delay_seconds: 0.8
```

### 允许列表

```bash
# 环境变量方式
FEISHU_ALLOWED_USERS=ou_xxxxx1,ou_xxxxx2,ou_xxxxx3
```

---

## 支持的消息类型

| 类型 | 支持 | 说明 |
|------|------|------|
| 文本 | ✅ | 支持 Markdown |
| 图片 | ✅ | 自动缓存和处理 |
| 文件 | ✅ | 支持常见文档格式 |
| 音频 | ✅ | 支持常见音频格式 |
| 视频 | ✅ | 自动下载缓存 |
| 卡片 | ✅ | 交互式卡片消息 |
| 合并转发 | ✅ | 解析为纯文本 |

---

## 相关资源

- 飞书开放平台：https://open.feishu.cn/
- 飞书 API 文档：https://open.feishu.cn/document/ukTMukTMukTM
- Hermes 飞书适配器代码：`gateway/platforms/feishu.py`

---

## 获取帮助

```bash
# 查看飞书适配器帮助
hermes gateway feishu --help

# 查看网关日志
tail -100 ~/.hermes/logs/gateway.log
```
