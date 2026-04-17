# Hermes Agent 完整迁移指南

将当前 Hermes Agent 迁移到新环境（新机器、新服务器、新配置等）的完整清单。

---

## 📋 迁移清单总览

| 类别 | 优先级 | 说明 |
|------|--------|------|
| **Skills** | 🔴 必须 | 自定义技能和技能配置 |
| **配置文件** | 🔴 必须 | config.yaml 和 .env |
| **知识库** | 🔴 必须 | mydocs/knowledgebase/ |
| **自定义脚本** | 🟡 推荐 | scripts/ 目录 |
| **会话数据** | 🟡 可选 | SQLite 数据库 |
| **记忆数据** | 🟡 可选 | memory 和 user profile |
| **Gateway 配置** | 🟢 按需 | 消息平台配置 |
| **虚拟环境** | 🔴 必须 | Python venv 和依赖 |

---

## 一、必须迁移的内容

### 1.1 Skills（技能）

**源位置:** `~/.hermes/skills/` 或 `~/hermes-agent/skills/`

**迁移内容:**
```bash
# 自定义技能目录
~/.hermes/skills/smart-home/smartthings-cli/
~/.hermes/skills/smart-home/appliance-fault-diagnosis/
~/.hermes/skills/messaging/feishu-integration/
```

**迁移方法:**
```bash
# 打包技能
cd ~/.hermes/skills/
tar -czvf hermes-skills.tar.gz \
    smart-home/smartthings-cli \
    smart-home/appliance-fault-diagnosis \
    messaging/feishu-integration

# 在新环境解压
tar -xzvf hermes-skills.tar.gz -C ~/.hermes/skills/
```

---

### 1.2 配置文件

**源位置:** `~/.hermes/`

**迁移内容:**
| 文件 | 说明 | 敏感度 |
|------|------|--------|
| `config.yaml` | 主配置文件（模型、工具、显示等） | 🟡 中等 |
| `.env` | 环境变量（API Keys、密钥） | 🔴 高密 |

**迁移方法:**
```bash
# 备份配置
cp ~/.hermes/config.yaml ~/backup/config.yaml.bak
cp ~/.hermes/.env ~/backup/.env.bak

# 在新环境恢复
cp config.yaml.bak ~/.hermes/config.yaml
cp .env.bak ~/.hermes/.env

# 设置权限（重要！）
chmod 600 ~/.hermes/.env
```

**⚠️ 安全提示:**
- `.env` 文件包含 API Keys，不要上传到 Git
- 使用加密传输（scp、rsync over SSH）
- 迁移后检查权限

---

### 1.3 知识库

**源位置:** `~/hermes-agent/mydocs/knowledgebase/`

**迁移内容:**
```bash
mydocs/knowledgebase/
├── BN81-27185G-690_EUG_ROPDVBCNF_CN_S-CHI_250818.0.pdf  # 电视手册
├── DA68-04798R-06_RF8500_Defeature_CN_SVC.pdf           # 冰箱手册
├── DB68-12848B-01_QG_FAC_MEMORY_SC_ZH-CH_2026.03.17.pdf # 空调手册
├── OID78248_IB_T-PJT_WD8000D_7LCD_ZH-CN_260113.pdf      # 洗衣机手册
├── 家电维修.txt                                          # 故障代码
└── images/                                               # 提取的图片
```

**迁移方法:**
```bash
# 打包知识库
cd ~/hermes-agent
tar -czvf knowledgebase.tar.gz mydocs/knowledgebase/

# 在新环境解压
tar -xzvf knowledgebase.tar.gz -C ~/hermes-agent/
```

---

### 1.4 自定义脚本

**源位置:** `~/hermes-agent/scripts/`

**迁移内容:**
| 脚本 | 说明 |
|------|------|
| `setup-qwen-config.py` | 阿里云百炼一键配置 |
| `feishu_setup.py` | 飞书配置向导 |
| 其他自定义脚本 | 你的个性化脚本 |

**迁移方法:**
```bash
# 打包脚本
cd ~/hermes-agent
tar -czvf scripts.tar.gz scripts/

# 在新环境解压
tar -xzvf scripts.tar.gz -C ~/hermes-agent/
```

---

### 1.5 虚拟环境和依赖

**源位置:** `~/hermes-agent/venv/`

**迁移方法:**
```bash
# 方法 A：重新安装（推荐）
cd ~/hermes-agent
python3 -m venv venv
source venv/bin/activate
pip install -e .
pip install -r requirements.txt

# 方法 B：复制整个 venv（不推荐，可能有路径问题）
# 仅当目标环境完全相同时使用
rsync -av venv/ new-machine:~/hermes-agent/venv/
```

**依赖包清单:**
```bash
# 导出当前依赖
pip freeze > requirements-custom.txt

# 在新环境安装
pip install -r requirements-custom.txt
```

---

## 二、可选迁移的内容

### 2.1 会话数据

**源位置:** `~/.hermes/sessions.db` 或 `~/.hermes/sessions/`

**说明:** 历史对话记录，可选迁移

**迁移方法:**
```bash
# 备份会话数据库
cp ~/.hermes/sessions.db ~/backup/sessions.db.bak

# 在新环境恢复
cp sessions.db.bak ~/.hermes/sessions.db
```

---

### 2.2 记忆数据

**源位置:** `~/.hermes/memory.db` 或内嵌在 sessions.db 中

**说明:** 长期记忆和用户画像，可选迁移

**迁移方法:**
```bash
# 查看记忆内容（在旧环境）
hermes memory list

# 导出记忆（如果有导出功能）
# 或手动复制数据库文件
cp ~/.hermes/memory.db ~/backup/memory.db.bak
```

---

### 2.3 Gateway 配置

**源位置:** `~/.hermes/config.yaml` 中的 `platforms` 部分

**说明:** 如果使用了消息平台（飞书、Telegram、Discord 等）

**迁移内容:**
```yaml
# config.yaml 中的配置
platforms:
  feishu:
    enabled: true
    extra:
      app_id: "cli_xxx"
      app_secret: "***"
      # ...
```

**⚠️ 注意:** Gateway 配置包含敏感信息，需安全传输

---

## 三、完整迁移流程

### 3.1 准备阶段（旧环境）

```bash
# 1. 创建备份目录
mkdir -p ~/hermes-backup/$(date +%Y%m%d)
cd ~/hermes-backup/$(date +%Y%m%d)

# 2. 备份 Skills
cp -r ~/.hermes/skills/smart-home/ ./
cp -r ~/.hermes/skills/messaging/ ./

# 3. 备份配置
cp ~/.hermes/config.yaml ./
cp ~/.hermes/.env ./

# 4. 备份知识库
cp -r ~/hermes-agent/mydocs/knowledgebase/ ./

# 5. 备份脚本
cp -r ~/hermes-agent/scripts/ ./

# 6. 导出依赖
cd ~/hermes-agent
pip freeze > ~/hermes-backup/$(date +%Y%m%d)/requirements.txt

# 7. 打包
cd ~/hermes-backup
tar -czvf hermes-full-backup-$(date +%Y%m%d).tar.gz $(date +%Y%m%d)/
```

### 3.2 恢复阶段（新环境）

```bash
# 1. 克隆 Hermes Agent 项目
git clone https://github.com/benx517/hermes-agent.git
cd hermes-agent
git pull origin main

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -e .
pip install -r requirements.txt

# 4. 创建 Hermes 配置目录
mkdir -p ~/.hermes

# 5. 恢复配置
cp backup/config.yaml ~/.hermes/
cp backup/.env ~/.hermes/
chmod 600 ~/.hermes/.env

# 6. 恢复 Skills
cp -r backup/smart-home/ ~/.hermes/skills/
cp -r backup/messaging/ ~/.hermes/skills/

# 7. 恢复知识库
cp -r backup/knowledgebase/ ~/hermes-agent/mydocs/

# 8. 恢复脚本
cp -r backup/scripts/* ~/hermes-agent/scripts/

# 9. 验证配置
hermes doctor
hermes skills list
hermes --model
```

---

## 四、迁移验证清单

### 4.1 基础验证

```bash
# ✅ 检查 Python 版本
python --version  # 应与原环境一致

# ✅ 检查虚拟环境
which python  # 应指向 venv/bin/python

# ✅ 检查 Hermes 安装
hermes --version

# ✅ 检查模型配置
hermes --model  # 应显示 alibaba/qwen3.5-plus
```

### 4.2 Skills 验证

```bash
# ✅ 检查技能列表
hermes skills list | grep -E "smartthings|feishu|appliance"

# 预期输出:
# - smartthings-cli
# - feishu-integration
# - appliance-fault-diagnosis
```

### 4.3 知识库验证

```bash
# ✅ 检查知识库文件
ls -la ~/hermes-agent/mydocs/knowledgebase/

# ✅ 测试 PDF 读取
python scripts/test-kb.py  # 如果有测试脚本
```

### 4.4 功能验证

```bash
# ✅ 启动 Hermes
hermes

# ✅ 测试对话
发送一条消息，确认模型响应正常

# ✅ 测试工具使用
询问需要调用工具的问题

# ✅ 测试技能
询问家电故障问题，验证 appliance-fault-diagnosis 技能
```

---

## 五、常见问题

### Q: 迁移后 Skills 不显示？

**解决:**
```bash
# 刷新技能列表
hermes skills refresh

# 检查技能目录
ls -la ~/.hermes/skills/

# 检查 SKILL.md 格式
cat ~/.hermes/skills/smart-home/smartthings-cli/SKILL.md
```

### Q: 迁移后 API 调用失败？

**解决:**
```bash
# 检查 .env 文件
cat ~/.hermes/.env

# 验证 API Key 格式
# DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx

# 检查文件权限
chmod 600 ~/.hermes/.env
```

### Q: 迁移后知识库无法读取？

**解决:**
```bash
# 检查文件路径
ls -la ~/hermes-agent/mydocs/knowledgebase/

# 检查文件权限
chmod 644 ~/hermes-agent/mydocs/knowledgebase/*.pdf

# 验证 pymupdf 安装
pip install pymupdf
```

### Q: 如何只迁移部分配置？

**解决:**
```bash
# 只迁移 Skills
cp -r ~/.hermes/skills/smart-home/ new-machine:~/.hermes/skills/

# 只迁移配置
scp ~/.hermes/config.yaml new-machine:~/.hermes/
scp ~/.hermes/.env new-machine:~/.hermes/

# 只迁移知识库
rsync -av mydocs/knowledgebase/ new-machine:~/hermes-agent/mydocs/
```

---

## 六、自动化迁移脚本

### 方式 A：使用导出/导入脚本（推荐）

**1. 在旧环境导出配置：**

```bash
cd ~/hermes-agent
python scripts/export-for-migration.py
```

脚本会自动：
- 导出清理后的 config.yaml（不含 API Keys）
- 导出自定义 Skills
- 导出知识库
- 导出自定义脚本和文档
- 创建 manifest.json 清单
- 所有文件保存到 `backup/` 目录

**2. 提交到 Git：**

```bash
git add backup/
git commit -m "backup: add migration files"
git push
```

**3. 在新环境导入配置：**

```bash
cd ~/hermes-agent
git pull
python scripts/import-from-backup.py
```

脚本会自动：
- 从 backup/ 目录恢复配置
- 交互式输入 API Key
- 创建 .env 文件（权限 600）
- 恢复 Skills 和知识库
- 验证导入结果

### 方式 B：手动导出（备选）

```python
#!/usr/bin/env python3
"""
Hermes Agent 配置导出脚本
导出所有配置、Skills、知识库到压缩包
"""

import os
import tarfile
import shutil
from pathlib import Path
from datetime import datetime

def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path.home() / f"hermes-backup-{timestamp}"
    backup_dir.mkdir()
    
    # 复制配置
    hermes_home = Path.home() / ".hermes"
    if hermes_home.exists():
        shutil.copytree(hermes_home / "skills", backup_dir / "skills")
        shutil.copy(hermes_home / "config.yaml", backup_dir / "config.yaml")
        shutil.copy(hermes_home / ".env", backup_dir / ".env")
    
    # 复制知识库
    kb_dir = Path.home() / "hermes-agent" / "mydocs" / "knowledgebase"
    if kb_dir.exists():
        shutil.copytree(kb_dir, backup_dir / "knowledgebase")
    
    # 复制脚本
    scripts_dir = Path.home() / "hermes-agent" / "scripts"
    if scripts_dir.exists():
        shutil.copytree(scripts_dir, backup_dir / "scripts")
    
    # 打包
    tar_path = Path.home() / f"hermes-backup-{timestamp}.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(backup_dir, arcname=backup_dir.name)
    
    # 清理临时目录
    shutil.rmtree(backup_dir)
    
    print(f"✅ 备份完成：{tar_path}")

if __name__ == "__main__":
    main()
```

---

## 七、安全建议

| 建议 | 说明 |
|------|------|
| 🔐 加密传输 | 使用 SSH/scp/rsync over SSH |
| 🔐 文件权限 | `.env` 文件设置为 600 |
| 🔐 不要上传 Git | `.env` 加入 `.gitignore` |
| 🔐 定期备份 | 使用自动化脚本定期导出 |
| 🔐 验证完整性 | 迁移后运行 `hermes doctor` |

---

## 八、迁移检查表

```
□ 1. 备份 Skills 目录
□ 2. 备份 config.yaml 和 .env
□ 3. 备份知识库
□ 4. 备份自定义脚本
□ 5. 导出依赖列表
□ 6. 在新环境克隆项目
□ 7. 创建虚拟环境
□ 8. 安装依赖
□ 9. 恢复配置
□ 10. 恢复 Skills
□ 11. 恢复知识库
□ 12. 验证配置 (hermes doctor)
□ 13. 测试对话
□ 14. 测试 Skills
□ 15. 测试知识库查询
```

---

**完成以上步骤后，你的 Hermes Agent 就成功迁移到新环境了！** 🎉
