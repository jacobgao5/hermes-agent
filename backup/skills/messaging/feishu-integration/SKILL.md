---
name: feishu-integration
description: Integrate Feishu (飞书/Lark) messaging platform with Hermes Agent using the built-in platform adapter
version: 1.0.0
metadata:
  hermes:
    tags: [messaging, feishu, lark, integration, china]
    homepage: https://open.feishu.cn/
prerequisites:
  commands: [pip, hermes]
---

# Feishu (飞书/Lark) Integration with Hermes

Hermes has a **built-in Feishu platform adapter** at `gateway/platforms/feishu.py`. This skill covers the complete integration process.

## Capabilities

The Feishu adapter supports:
- ✅ WebSocket long connection and Webhook transport modes
- ✅ Direct messages and group messages (@mention-gated)
- ✅ Image/file/audio/media file handling with caching
- ✅ Interactive card messages with button click events
- ✅ Message deduplication and batch processing
- ✅ Allowlist integration via `FEISHU_ALLOWED_USERS`
- ✅ Per-chat serial message processing
- ✅ Persistent ACK emoji reactions

---

## Quick Start (3 Steps)

### Step 1: Install Dependencies

```bash
cd ~/hermes-agent
source venv/bin/activate
pip install lark-oapi qrcode aiohttp websockets
```

### Step 2: Run Configuration Wizard

```bash
python scripts/feishu_setup.py
```

This interactive script will:
1. Check dependencies
2. Prompt for App ID, App Secret, and other credentials
3. Save configuration to `~/.hermes/config.yaml` and `~/.hermes/.env`
4. Provide next steps

### Step 3: Start Gateway

```bash
hermes gateway run
```

---

## Manual Configuration

### Option A: config.yaml

Edit `~/.hermes/config.yaml`:

```yaml
platforms:
  feishu:
    enabled: true
    extra:
      app_id: "cli_xxxxxxxxxxxxxxxx"
      app_secret: "your_app_secret"
      domain: "feishu"  # or "lark" for international
      connection_mode: "websocket"  # or "webhook"
      encrypt_key: "your_encrypt_key"
      verification_token: "your_verification_token"
      group_policy: "mention_only"  # mention_only | open | disabled | allowlist
      
      # Webhook mode only
      webhook_host: "0.0.0.0"
      webhook_port: 8765
      webhook_path: "/feishu/webhook"
```

### Option B: Environment Variables

Add to `~/.hermes/.env`:

```bash
FEISHU_ENABLED=true
FEISHU_APP_ID=cli_xxxxxxxxxxxxxxxx
FEISHU_APP_SECRET=your_app_secret
FEISHU_DOMAIN=feishu
FEISHU_CONNECTION_MODE=websocket
FEISHU_ENCRYPT_KEY=your_encrypt_key
FEISHU_VERIFICATION_TOKEN=your_verification_token
FEISHU_GROUP_POLICY=mention_only
```

---

## Create Feishu Application

### Option A: QR Code Auto-Registration (if supported)

```bash
hermes gateway feishu onboard
```

This generates a QR code. Scan with Feishu app to auto-create the application.

### Option B: Manual Creation

1. Visit [Feishu Open Platform](https://open.feishu.cn/)
2. Login with enterprise developer account
3. Click "Create Enterprise Self-Built App"
4. Fill in app name and icon
5. Get credentials from "Credentials & Basic Info":
   - **App ID** (starts with `cli_`)
   - **App Secret**

### Required Permissions

In the app management page, add these permissions:

**Bot Capabilities:**
- Send messages
- Read and reply to group messages
- Get user info

**Event Subscriptions:**
- Receive messages (`im.message.receive_v1`)
- Message read (`im.message.message_read_v1`)
- Card action trigger (`card.action.trigger`)

**Security Settings:**
- Enable encryption → get **Encrypt Key**
- Set **Verification Token**

---

## Connection Modes

### WebSocket Mode (Recommended)

- Long-polling connection to Feishu servers
- No public URL required
- Better for development and internal deployments

```yaml
extra:
  connection_mode: "websocket"
```

### Webhook Mode

- Feishu pushes events to your server
- Requires public URL and HTTPS
- Better for production with load balancers

```yaml
extra:
  connection_mode: "webhook"
  webhook_host: "0.0.0.0"
  webhook_port: 8765
  webhook_path: "/feishu/webhook"
```

Configure webhook URL in Feishu Open Platform:
```
https://your-domain.com:8765/feishu/webhook
```

---

## Group Policy Options

| Policy | Description |
|--------|-------------|
| `mention_only` | Bot only responds when @mentioned (default) |
| `open` | Anyone in group can interact |
| `disabled` | Bot disabled in groups |
| `allowlist` | Only specific users can interact |

### Per-Group Rules

```yaml
extra:
  group_policy: "mention_only"
  group_rules:
    "chat_id_1":
      policy: "open"
    "chat_id_2":
      policy: "allowlist"
      allowlist:
        - "ou_xxxxx1"  # user open_id
        - "ou_xxxxx2"
    "chat_id_3":
      policy: "disabled"
```

---

## Testing

### Test Private Chat
1. Find your bot in Feishu
2. Send: `你好`
3. Check gateway logs for response

### Test Group Chat
1. Add bot to a group
2. Send: `@BotName 你好`
3. Verify response

### Check Logs
```bash
tail -f ~/.hermes/logs/gateway.log | grep feishu
```

---

## Supported Message Types

| Type | Support | Notes |
|------|---------|-------|
| Text | ✅ | Markdown supported |
| Image | ✅ | Auto-cached and processed |
| File | ✅ | Common document formats |
| Audio | ✅ | Common audio formats |
| Video | ✅ | Auto-downloaded and cached |
| Card | ✅ | Interactive card messages |
| Forwarded | ✅ | Parsed to plain text |

---

## Troubleshooting

### "app_id or app_secret is required"
Check config.yaml or .env for correct credentials.

### "verification token mismatch"
Ensure Verification Token in Feishu platform matches config.

### "encrypt key validation failed"
Check Encrypt Key is correctly copied without extra spaces.

### WebSocket connection fails
- Check network connectivity
- Verify domain setting (feishu vs lark)
- Check gateway logs for detailed errors

### Not receiving group messages
- Ensure bot is added to the group
- Check group_policy setting
- Verify "Receive group messages" permission is enabled

### Dependencies not found
```bash
# Install missing packages
pip install lark-oapi qrcode aiohttp websockets
```

---

## Advanced Configuration

### Batch Processing Tuning

```yaml
extra:
  # Text message batching
  text_batch_delay_seconds: 0.6
  text_batch_max_messages: 8
  text_batch_max_chars: 4000
  
  # Media message batching
  media_batch_delay_seconds: 0.8
```

### Allowlist by User

```bash
# Environment variable
FEISHU_ALLOWED_USERS=ou_xxxxx1,ou_xxxxx2,ou_xxxxx3
```

### Domain Selection

```yaml
extra:
  domain: "feishu"  # China mainland
  # or
  domain: "lark"    # International
```

---

## Commands Reference

```bash
# Check gateway status
hermes gateway status

# Reload configuration
hermes gateway reload

# View bot info (if implemented)
hermes gateway feishu info

# Check platform status
hermes gateway feishu list
```

---

## Related Files

- Adapter code: `gateway/platforms/feishu.py`
- Setup script: `scripts/feishu_setup.py`
- Documentation: `docs/feishu-setup-guide.md`
- Config location: `~/.hermes/config.yaml`
- Logs: `~/.hermes/logs/gateway.log`

---

## Resources

- Feishu Open Platform: https://open.feishu.cn/
- Feishu API Docs: https://open.feishu.cn/document/ukTMukTMukTM
- Lark Open Platform (International): https://open.larksuite.com/
