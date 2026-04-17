# Hermes Agent 配置指南 - 阿里云百炼 qwen3.5-plus

本文档记录如何配置 Hermes Agent 使用阿里云百炼 qwen3.5-plus 模型。

---

## 一、快速启动

```bash
cd ~/hermes-agent
source venv/bin/activate
hermes
```

---

## 二、配置阿里云百炼 qwen3.5-plus

### 方式 A：一键配置脚本（推荐）

```bash
cd ~/hermes-agent
python scripts/setup-qwen-config.py
```

脚本会自动：
1. 创建 `~/.hermes/` 目录
2. 交互式输入 API Key
3. 配置 `.env` 和 `config.yaml`
4. 验证配置

### 方式 B：手动配置

**1. 配置文件位置**

| 文件 | 路径 | 用途 |
|------|------|------|
| API Keys | `~/.hermes/.env` | 存储密钥等敏感信息 |
| 配置文件 | `~/.hermes/config.yaml` | 存储模型、provider 等设置 |

**2. 配置 .env 文件**

编辑 `~/.hermes/.env`：

```bash
# 阿里云百炼 API Key（替换为你的实际密钥）
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx

# 国内版百炼 endpoint
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

**3. 配置 config.yaml**

编辑 `~/.hermes/config.yaml`，设置模型（第 1 行）：

```yaml
model: alibaba/qwen3.5-plus
```

---

## 三、获取百炼 API Key

1. 访问阿里云百炼控制台：https://bailian.console.aliyun.com/
2. 登录阿里云账号
3. 进入「我的应用」→「API-KEY 管理」
4. 创建新的 API Key
5. 复制密钥到 `~/.hermes/.env` 的 `DASHSCOPE_API_KEY`

---

## 四、运行时切换模型

在 Hermes CLI 中：

```bash
# 切换到百炼 qwen3.5-plus
/model alibaba:qwen3.5-plus

# 持久化保存到配置文件
/model alibaba:qwen3.5-plus --global

# 查看当前模型
/model
```

---

## 五、验证配置

```bash
# 启动 Hermes
hermes

# 输入查看模型命令
/model

# 应显示：Current: qwen3.5-plus on alibaba
```

---

## 六、常用 CLI 命令

| 命令 | 作用 |
|------|------|
| `/help` | 显示帮助 |
| `/model` | 查看/切换模型 |
| `/new` | 开始新对话 |
| `/tools` | 查看可用工具 |
| `/skills` | 浏览技能 |
| `Ctrl+D` | 退出 |

---

## 七、常见问题

### Q: 切换模型时报错 "no matching model"？

需要指定完整格式：
```bash
/model alibaba:qwen3.5-plus
```

### Q: 如何使用国内版百炼？

在 `~/.hermes/.env` 中设置：
```bash
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

### Q: 配置文件在哪里？

```bash
# 查看配置文件
cat ~/.hermes/config.yaml

# 查看环境变量
cat ~/.hermes/.env
```

---

## 八、相关链接

- 百炼控制台：https://bailian.console.aliyun.com/
- Hermes GitHub: https://github.com/NousResearch/hermes-agent
