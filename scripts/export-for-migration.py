#!/usr/bin/env python3
"""
Hermes Agent 配置导出脚本

将可迁移的配置导出到项目 backup 目录，不包含敏感信息和 Python 依赖。
导出的内容可以安全提交到 Git。

使用方法:
    python scripts/export-for-migration.py
"""

import os
import shutil
import yaml
from pathlib import Path
from datetime import datetime

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
BACKUP_DIR = PROJECT_ROOT / "backup"

# 源目录
HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
KNOWLEDGE_BASE = PROJECT_ROOT / "mydocs" / "knowledgebase"


def print_banner():
    print("=" * 60)
    print("  Hermes Agent - 配置导出脚本")
    print("=" * 60)
    print()


def clean_sensitive_data(config_data):
    """清理配置文件中的敏感信息"""
    cleaned = {}
    
    for key, value in config_data.items():
        # 跳过敏感配置
        if key in ['providers', 'credential_pool_strategies']:
            continue
        
        # 清理 auxiliary 中的 API key
        if key == 'auxiliary' and isinstance(value, dict):
            cleaned[key] = {}
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, dict):
                    cleaned[key][sub_key] = {
                        k: v for k, v in sub_value.items() 
                        if k not in ['api_key', 'base_url']
                    }
                else:
                    cleaned[key][sub_key] = sub_value
            continue
        
        # 清理 delegation 中的 API key
        if key == 'delegation' and isinstance(value, dict):
            cleaned[key] = {
                k: v for k, v in value.items() 
                if k not in ['api_key', 'base_url']
            }
            continue
        
        # 清理 display.platforms 中的敏感信息
        if key == 'display' and isinstance(value, dict):
            cleaned[key] = {}
            for sub_key, sub_value in value.items():
                if sub_key == 'platforms':
                    # 保留平台启用状态，清理密钥
                    cleaned[key][sub_key] = {}
                    if isinstance(sub_value, dict):
                        for platform, config in sub_value.items():
                            if isinstance(config, dict):
                                cleaned[key][sub_key][platform] = {
                                    'enabled': config.get('enabled', False)
                                }
                else:
                    cleaned[key][sub_key] = sub_value
            continue
        
        # 保留其他配置
        if key not in ['fallback_providers']:
            cleaned[key] = value
    
    return cleaned


def export_config_yaml():
    """导出清理后的 config.yaml"""
    print("📄 导出 config.yaml...")
    
    config_file = HERMES_HOME / "config.yaml"
    if not config_file.exists():
        print("  ⚠️  config.yaml 不存在，跳过")
        return False
    
    # 读取配置
    with open(config_file, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)
    
    # 清理敏感信息
    cleaned_config = clean_sensitive_data(config_data)
    
    # 写入清理后的配置
    output_file = BACKUP_DIR / "config.yaml"
    with open(output_file, "w", encoding="utf-8") as f:
        yaml.dump(cleaned_config, f, default_flow_style=False, allow_unicode=True)
    
    print(f"  ✅ 已导出：{output_file}")
    print("  ℹ️  已清理：API Keys, Base URLs, Provider 配置")
    return True


def export_skills():
    """导出自定义 Skills"""
    print()
    print("📦 导出 Skills...")
    
    skills_dir = HERMES_HOME / "skills"
    if not skills_dir.exists():
        print("  ⚠️  Skills 目录不存在，跳过")
        return False
    
    # 创建目标目录
    target_dir = BACKUP_DIR / "skills"
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # 复制自定义技能目录
    custom_categories = ['smart-home', 'messaging']
    exported = []
    
    for category in custom_categories:
        category_dir = skills_dir / category
        if category_dir.exists():
            target_category = target_dir / category
            shutil.copytree(category_dir, target_category, dirs_exist_ok=True)
            exported.append(category)
            print(f"  ✅ 已导出：skills/{category}/")
    
    if not exported:
        print("  ⚠️  未找到自定义 Skills")
        return False
    
    return True


def export_knowledge_base():
    """导出知识库"""
    print()
    print("📚 导出知识库...")
    
    if not KNOWLEDGE_BASE.exists():
        print("  ⚠️  知识库目录不存在，跳过")
        return False
    
    # 创建目标目录
    target_dir = BACKUP_DIR / "knowledgebase"
    
    # 复制知识库
    shutil.copytree(KNOWLEDGE_BASE, target_dir, dirs_exist_ok=True)
    
    # 统计文件
    file_count = sum(1 for _ in target_dir.rglob("*") if _.is_file())
    print(f"  ✅ 已导出：{file_count} 个文件")
    
    return True


def export_scripts():
    """导出自定义脚本"""
    print()
    print("🔧 导出自定义脚本...")
    
    scripts_dir = PROJECT_ROOT / "scripts"
    if not scripts_dir.exists():
        print("  ⚠️  Scripts 目录不存在，跳过")
        return False
    
    # 创建目标目录
    target_dir = BACKUP_DIR / "scripts"
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # 复制脚本（排除导出脚本本身）
    exported = []
    for script in scripts_dir.glob("*.py"):
        if script.name != "export-for-migration.py":
            shutil.copy(script, target_dir / script.name)
            exported.append(script.name)
    
    if exported:
        print(f"  ✅ 已导出：{', '.join(exported)}")
        return True
    else:
        print("  ℹ️  无自定义脚本")
        return False


def export_docs():
    """导出自定义文档"""
    print()
    print("📖 导出文档...")
    
    mydocs_dir = PROJECT_ROOT / "mydocs"
    if not mydocs_dir.exists():
        print("  ⚠️  文档目录不存在，跳过")
        return False
    
    # 创建目标目录
    target_dir = BACKUP_DIR / "mydocs"
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # 复制文档（排除 knowledgebase，已单独导出）
    exported = []
    for doc in mydocs_dir.glob("*.md"):
        shutil.copy(doc, target_dir / doc.name)
        exported.append(doc.name)
    
    if exported:
        print(f"  ✅ 已导出：{', '.join(exported)}")
        return True
    else:
        print("  ℹ️  无自定义文档")
        return False


def export_sessions_and_memory():
    """导出会话和记忆数据"""
    print()
    print("💾 导出会话和记忆数据...")
    
    # Hermes 使用 state.db 存储会话和记忆数据
    state_db = HERMES_HOME / "state.db"
    sessions_db = HERMES_HOME / "sessions.db"
    memory_db = HERMES_HOME / "memory.db"
    
    exported = []
    target_dir = BACKUP_DIR / "data"
    
    # 导出 state.db（主要数据库）
    if state_db.exists():
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(state_db, target_dir / "state.db")
        exported.append("state.db")
        file_size = state_db.stat().st_size / 1024 / 1024  # MB
        print(f"  ✅ 已导出：state.db ({file_size:.1f} MB)")
    else:
        print("  ℹ️  state.db 不存在，跳过")
    
    # 导出 sessions.db（如果存在）
    if sessions_db.exists():
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(sessions_db, target_dir / "sessions.db")
        exported.append("sessions.db")
        file_size = sessions_db.stat().st_size / 1024 / 1024
        print(f"  ✅ 已导出：sessions.db ({file_size:.1f} MB)")
    
    # 导出 memory.db（如果存在）
    if memory_db.exists():
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(memory_db, target_dir / "memory.db")
        exported.append("memory.db")
        file_size = memory_db.stat().st_size / 1024 / 1024
        print(f"  ✅ 已导出：memory.db ({file_size:.1f} MB)")
    
    if exported:
        print(f"  📊 共导出 {len(exported)} 个数据库文件")
        return True
    else:
        print("  ℹ️  无会话/记忆数据可导出")
        return False


def create_manifest():
    """创建导出清单"""
    print()
    print("📋 创建导出清单...")
    
    # 检查是否有会话/记忆数据
    has_sessions = (HERMES_HOME / "sessions.db").exists()
    has_memory = (HERMES_HOME / "memory.db").exists()
    
    manifest = {
        "export_date": datetime.now().isoformat(),
        "hermes_version": "0.8.0+",
        "contents": {
            "config": "清理后的 config.yaml（不含 API Keys）",
            "skills": "自定义 Skills（smart-home, messaging）",
            "knowledgebase": "知识库文件（PDF, 文本）",
            "scripts": "自定义脚本",
            "docs": "自定义文档",
            "data": {
                "sessions": "会话数据库" if has_sessions else "无",
                "memory": "记忆数据库" if has_memory else "无"
            }
        },
        "excluded": [
            ".env (包含 API Keys)",
            "Python 依赖 (venv/)",
            "Provider 配置",
            "所有 API Keys 和 Base URLs"
        ],
        "next_steps": [
            "1. 提交 backup 目录到 Git",
            "2. 在新环境执行 scripts/import-from-backup.py",
            "3. 根据提示输入 API Key"
        ]
    }
    
    import json
    manifest_file = BACKUP_DIR / "manifest.json"
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"  ✅ 已创建：{manifest_file}")
    return True


def create_gitignore():
    """创建 backup/.gitignore 提醒"""
    print()
    print("📝 创建 .gitignore 提示...")
    
    gitignore_content = """# Hermes Agent Backup Directory
# 此目录包含可安全提交的配置
# 
# ⚠️ 提交前请确认：
# - config.yaml 已清理敏感信息
# - 不包含 .env 文件
# - 不包含 API Keys

# 如果包含敏感文件，请勿提交
*.env
*.key
*.secret
"""
    
    gitignore_file = BACKUP_DIR / ".gitignore"
    with open(gitignore_file, "w", encoding="utf-8") as f:
        f.write(gitignore_content)
    
    print(f"  ✅ 已创建：{gitignore_file}")
    return True


def print_summary():
    """打印导出摘要"""
    print()
    print("=" * 60)
    print("  ✅ 导出完成！")
    print("=" * 60)
    print()
    print(f"📁 导出目录：{BACKUP_DIR}")
    print()
    print("📦 导出内容:")
    print("  - config.yaml (已清理敏感信息)")
    print("  - skills/ (自定义技能)")
    print("  - knowledgebase/ (知识库)")
    print("  - scripts/ (自定义脚本)")
    print("  - mydocs/ (自定义文档)")
    print("  - data/ (会话和记忆数据，如有)")
    print()
    print("🚫 未导出（需手动配置）:")
    print("  - .env (API Keys)")
    print("  - Python 依赖")
    print()
    print("📌 下一步:")
    print("  1. 检查 backup/ 目录内容")
    print("  2. 提交到 Git:")
    print("     git add backup/")
    print("     git commit -m 'backup: add migration files'")
    print("     git push")
    print()
    print("  3. 在新环境运行:")
    print("     python scripts/import-from-backup.py")
    print()


def main():
    print_banner()
    
    # 创建 backup 目录
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    print(f"📁 备份目录：{BACKUP_DIR}")
    print()
    
    # 执行导出
    results = []
    results.append(("config.yaml", export_config_yaml()))
    results.append(("skills", export_skills()))
    results.append(("knowledgebase", export_knowledge_base()))
    results.append(("scripts", export_scripts()))
    results.append(("docs", export_docs()))
    results.append(("sessions/memory", export_sessions_and_memory()))
    results.append(("manifest", create_manifest()))
    results.append(("gitignore", create_gitignore()))
    
    # 打印摘要
    print_summary()
    
    # 返回成功计数
    success_count = sum(1 for _, result in results if result)
    print(f"✅ 成功导出 {success_count}/{len(results)} 项")
    
    return 0 if success_count >= 5 else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
