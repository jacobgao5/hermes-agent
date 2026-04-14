#!/usr/bin/env python3
"""
Hermes Agent 配置导入脚本

从项目 backup 目录导入配置到新环境，并提示用户输入 API Key。

使用方法:
    python scripts/import-from-backup.py
"""

import os
import sys
import yaml
import shutil
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
BACKUP_DIR = PROJECT_ROOT / "backup"

# 目标目录
HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
KNOWLEDGE_BASE = PROJECT_ROOT / "mydocs" / "knowledgebase"


def print_banner():
    print("=" * 60)
    print("  Hermes Agent - 配置导入脚本")
    print("=" * 60)
    print()


def check_backup_dir():
    """检查 backup 目录是否存在"""
    print("🔍 检查 backup 目录...")
    
    if not BACKUP_DIR.exists():
        print("  ❌ backup 目录不存在！")
        print()
        print("请先在旧环境运行:")
        print("  python scripts/export-for-migration.py")
        print()
        print("然后提交并拉取 backup 目录:")
        print("  git add backup/")
        print("  git commit -m 'backup: add migration files'")
        print("  git push")
        print()
        print("在新环境拉取:")
        print("  git pull")
        return False
    
    # 检查必要文件
    required_files = ['config.yaml', 'skills', 'knowledgebase']
    missing = []
    
    for item in required_files:
        if not (BACKUP_DIR / item).exists():
            missing.append(item)
    
    if missing:
        print(f"  ❌ backup 目录缺少必要文件：{', '.join(missing)}")
        return False
    
    print("  ✅ backup 目录检查通过")
    return True


def get_api_key():
    """交互式获取 API Key"""
    print()
    print("=" * 60)
    print("  配置 API Key")
    print("=" * 60)
    print()
    
    print("📌 请输入阿里云百炼 API Key")
    print()
    print("获取方式:")
    print("  1. 访问 https://bailian.console.aliyun.com/")
    print("  2. 登录阿里云账号")
    print("  3. 进入「我的应用」→「API-KEY 管理」")
    print("  4. 创建新的 API Key")
    print()
    
    while True:
        api_key = input("请输入 API Key: ").strip()
        if api_key:
            if api_key.startswith("sk-"):
                return api_key
            else:
                print("⚠️  API Key 通常以 sk- 开头，确认输入正确？(y/n): ", end="")
                if input().strip().lower() == 'y':
                    return api_key
        else:
            print("❌ API Key 不能为空，请重新输入")


def create_hermes_home():
    """创建 Hermes 配置目录"""
    print()
    print("📁 创建配置目录...")
    
    if not HERMES_HOME.exists():
        HERMES_HOME.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ 已创建：{HERMES_HOME}")
    else:
        print(f"  ✅ 目录已存在：{HERMES_HOME}")


def import_config_yaml():
    """导入 config.yaml"""
    print()
    print("⚙️  导入 config.yaml...")
    
    backup_file = BACKUP_DIR / "config.yaml"
    target_file = HERMES_HOME / "config.yaml"
    
    # 备份现有文件
    if target_file.exists():
        backup_path = target_file.with_suffix(".yaml.bak")
        shutil.copy(target_file, backup_path)
        print(f"  📦 已备份现有配置：{backup_path}")
    
    # 复制文件
    shutil.copy(backup_file, target_file)
    print(f"  ✅ 已导入：{target_file}")
    
    return True


def import_env_file(api_key):
    """创建 .env 文件"""
    print()
    print("⚙️  创建 .env 文件...")
    
    env_file = HERMES_HOME / ".env"
    
    # 备份现有文件
    if env_file.exists():
        backup_path = env_file.with_suffix(".env.bak")
        shutil.copy(env_file, backup_path)
        print(f"  📦 已备份现有 .env：{backup_path}")
    
    # 创建新文件
    env_content = f"""# Hermes Agent 环境变量配置

# 阿里云百炼 API Key
DASHSCOPE_API_KEY={api_key}

# 国内版百炼 endpoint
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
"""
    
    with open(env_file, "w", encoding="utf-8") as f:
        f.write(env_content)
    
    # 设置权限
    os.chmod(env_file, 0o600)
    
    print(f"  ✅ 已创建：{env_file}")
    print("  🔒 权限已设置为 600（仅所有者可读写）")
    
    return True


def import_skills():
    """导入 Skills"""
    print()
    print("📦 导入 Skills...")
    
    backup_skills = BACKUP_DIR / "skills"
    target_skills = HERMES_HOME / "skills"
    
    if not backup_skills.exists():
        print("  ⚠️  backup 中无 Skills，跳过")
        return False
    
    # 创建目标目录
    target_skills.mkdir(parents=True, exist_ok=True)
    
    # 复制技能
    imported = []
    for category in backup_skills.iterdir():
        if category.is_dir():
            target_category = target_skills / category.name
            shutil.copytree(category, target_category, dirs_exist_ok=True)
            imported.append(category.name)
            print(f"  ✅ 已导入：skills/{category.name}/")
    
    if imported:
        print(f"  📊 共导入 {len(imported)} 个技能类别")
        return True
    else:
        print("  ℹ️  无 Skills 可导入")
        return False


def import_knowledge_base():
    """导入知识库"""
    print()
    print("📚 导入知识库...")
    
    backup_kb = BACKUP_DIR / "knowledgebase"
    
    if not backup_kb.exists():
        print("  ⚠️  backup 中无知识库，跳过")
        return False
    
    # 创建目标目录
    KNOWLEDGE_BASE.mkdir(parents=True, exist_ok=True)
    
    # 复制文件
    file_count = 0
    for item in backup_kb.rglob("*"):
        if item.is_file():
            target = KNOWLEDGE_BASE / item.relative_to(backup_kb)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(item, target)
            file_count += 1
    
    print(f"  ✅ 已导入：{file_count} 个文件")
    
    return True


def import_scripts():
    """导入自定义脚本"""
    print()
    print("🔧 导入自定义脚本...")
    
    backup_scripts = BACKUP_DIR / "scripts"
    target_scripts = PROJECT_ROOT / "scripts"
    
    if not backup_scripts.exists():
        print("  ⚠️  backup 中无脚本，跳过")
        return False
    
    # 复制脚本（排除导入脚本本身）
    imported = []
    for script in backup_scripts.glob("*.py"):
        if script.name != "import-from-backup.py":
            target = target_scripts / script.name
            shutil.copy(script, target)
            imported.append(script.name)
    
    if imported:
        print(f"  ✅ 已导入：{', '.join(imported)}")
        return True
    else:
        print("  ℹ️  无脚本可导入")
        return False


def import_docs():
    """导入文档"""
    print()
    print("📖 导入文档...")
    
    backup_docs = BACKUP_DIR / "mydocs"
    target_docs = PROJECT_ROOT / "mydocs"
    
    if not backup_docs.exists():
        print("  ⚠️  backup 中无文档，跳过")
        return False
    
    # 复制文档（排除 knowledgebase，已单独导入）
    imported = []
    for doc in backup_docs.glob("*.md"):
        target = target_docs / doc.name
        shutil.copy(doc, target)
        imported.append(doc.name)
    
    if imported:
        print(f"  ✅ 已导入：{', '.join(imported)}")
        return True
    else:
        print("  ℹ️  无文档可导入")
        return False


def import_sessions_and_memory():
    """导入会话和记忆数据"""
    print()
    print("💾 导入会话和记忆数据...")
    
    backup_data = BACKUP_DIR / "data"
    
    if not backup_data.exists():
        print("  ℹ️  backup 中无会话/记忆数据，跳过")
        return False
    
    imported = []
    
    # 导入会话数据库
    sessions_backup = backup_data / "sessions.db"
    sessions_target = HERMES_HOME / "sessions.db"
    
    if sessions_backup.exists():
        # 备份现有文件
        if sessions_target.exists():
            backup_path = sessions_target.with_suffix(".db.bak")
            shutil.copy(sessions_target, backup_path)
            print(f"  📦 已备份现有 sessions.db: {backup_path}")
        
        shutil.copy(sessions_backup, sessions_target)
        imported.append("sessions.db")
        file_size = sessions_backup.stat().st_size / 1024 / 1024
        print(f"  ✅ 已导入：sessions.db ({file_size:.1f} MB)")
    
    # 导入记忆数据库
    memory_backup = backup_data / "memory.db"
    memory_target = HERMES_HOME / "memory.db"
    
    if memory_backup.exists():
        # 备份现有文件
        if memory_target.exists():
            backup_path = memory_target.with_suffix(".db.bak")
            shutil.copy(memory_target, backup_path)
            print(f"  📦 已备份现有 memory.db: {backup_path}")
        
        shutil.copy(memory_backup, memory_target)
        imported.append("memory.db")
        file_size = memory_backup.stat().st_size / 1024 / 1024
        print(f"  ✅ 已导入：memory.db ({file_size:.1f} MB)")
    
    if imported:
        print(f"  📊 共导入 {len(imported)} 个数据库文件")
        return True
    else:
        print("  ℹ️  无会话/记忆数据可导入")
        return False


def verify_import():
    """验证导入结果"""
    print()
    print("🔍 验证导入结果...")
    
    checks = []
    
    # 检查 config.yaml
    if (HERMES_HOME / "config.yaml").exists():
        with open(HERMES_HOME / "config.yaml", "r") as f:
            content = f.read()
            if "alibaba/qwen3.5-plus" in content:
                checks.append(("config.yaml", True, "模型配置正确"))
            else:
                checks.append(("config.yaml", False, "模型配置缺失"))
    else:
        checks.append(("config.yaml", False, "文件不存在"))
    
    # 检查 .env
    if (HERMES_HOME / ".env").exists():
        with open(HERMES_HOME / ".env", "r") as f:
            content = f.read()
            if "DASHSCOPE_API_KEY=" in content:
                checks.append((".env", True, "API Key 已配置"))
            else:
                checks.append((".env", False, "API Key 缺失"))
    else:
        checks.append((".env", False, "文件不存在"))
    
    # 检查 Skills
    skills_dir = HERMES_HOME / "skills"
    if skills_dir.exists():
        custom_skills = list(skills_dir.glob("smart-home/*")) + list(skills_dir.glob("messaging/*"))
        if custom_skills:
            checks.append(("skills", True, f"已导入 {len(custom_skills)} 个技能"))
        else:
            checks.append(("skills", False, "无自定义技能"))
    else:
        checks.append(("skills", False, "目录不存在"))
    
    # 检查知识库
    if KNOWLEDGE_BASE.exists():
        kb_files = list(KNOWLEDGE_BASE.glob("*.pdf")) + list(KNOWLEDGE_BASE.glob("*.txt"))
        if kb_files:
            checks.append(("knowledgebase", True, f"已导入 {len(kb_files)} 个文件"))
        else:
            checks.append(("knowledgebase", False, "无文件"))
    else:
        checks.append(("knowledgebase", False, "目录不存在"))
    
    # 检查会话数据
    sessions_db = HERMES_HOME / "sessions.db"
    if sessions_db.exists():
        file_size = sessions_db.stat().st_size / 1024 / 1024
        checks.append(("sessions.db", True, f"已导入 ({file_size:.1f} MB)"))
    else:
        checks.append(("sessions.db", False, "文件不存在"))
    
    # 检查记忆数据
    memory_db = HERMES_HOME / "memory.db"
    if memory_db.exists():
        file_size = memory_db.stat().st_size / 1024 / 1024
        checks.append(("memory.db", True, f"已导入 ({file_size:.1f} MB)"))
    else:
        checks.append(("memory.db", False, "文件不存在"))
    
    # 打印检查结果
    all_passed = True
    for name, passed, message in checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {name}: {message}")
        if not passed:
            all_passed = False
    
    return all_passed


def print_summary():
    """打印导入摘要"""
    print()
    print("=" * 60)
    print("  ✅ 导入完成！")
    print("=" * 60)
    print()
    print("📁 配置位置:")
    print(f"  - config.yaml: {HERMES_HOME / 'config.yaml'}")
    print(f"  - .env:        {HERMES_HOME / '.env'}")
    print(f"  - skills:      {HERMES_HOME / 'skills/'}")
    print(f"  - knowledge:   {KNOWLEDGE_BASE}")
    print(f"  - sessions:    {HERMES_HOME / 'sessions.db'}")
    print(f"  - memory:      {HERMES_HOME / 'memory.db'}")
    print()
    print("🚀 启动 Hermes:")
    print("  cd ~/hermes-agent")
    print("  source venv/bin/activate")
    print("  hermes")
    print()
    print("📌 验证:")
    print("  1. 输入 /model 确认模型")
    print("  2. 输入 /skills list 查看技能")
    print("  3. 输入 /sessions 查看历史会话（如有）")
    print("  4. 测试对话功能")
    print()
    print("⚠️  安全提示:")
    print("  - .env 文件包含敏感信息，不要提交到 Git")
    print("  - 已设置权限为 600（仅所有者可读写）")
    print()


def main():
    print_banner()
    
    # 1. 检查 backup 目录
    if not check_backup_dir():
        return 1
    
    # 2. 创建配置目录
    create_hermes_home()
    
    # 3. 获取 API Key
    api_key = get_api_key()
    
    # 4. 执行导入
    results = []
    results.append(("config.yaml", import_config_yaml()))
    results.append((".env", import_env_file(api_key)))
    results.append(("skills", import_skills()))
    results.append(("knowledgebase", import_knowledge_base()))
    results.append(("scripts", import_scripts()))
    results.append(("docs", import_docs()))
    results.append(("sessions/memory", import_sessions_and_memory()))
    
    # 5. 验证导入
    verified = verify_import()
    
    # 6. 打印摘要
    print_summary()
    
    # 返回状态
    if verified:
        print("🎉 所有检查通过，配置成功！")
        return 0
    else:
        print("⚠️  部分检查未通过，请检查配置")
        return 1


if __name__ == "__main__":
    sys.exit(main())
