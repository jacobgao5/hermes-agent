#!/usr/bin/env python3
"""
Hermes Agent 一键配置脚本 - 阿里云百炼 qwen3.5-plus

使用方法:
    python scripts/setup-qwen-config.py

脚本会自动:
1. 检查并创建 ~/.hermes/ 目录
2. 交互式输入 API Key
3. 配置 .env 文件
4. 配置 config.yaml
5. 验证配置
"""

import os
import sys
from pathlib import Path

# Hermes 配置目录
HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
CONFIG_FILE = HERMES_HOME / "config.yaml"
ENV_FILE = HERMES_HOME / ".env"


def print_banner():
    print("=" * 60)
    print("  Hermes Agent - 阿里云百炼 qwen3.5-plus 配置向导")
    print("=" * 60)
    print()


def get_api_key():
    """交互式获取 API Key"""
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
    if not HERMES_HOME.exists():
        print(f"📁 创建配置目录：{HERMES_HOME}")
        HERMES_HOME.mkdir(parents=True, exist_ok=True)
    else:
        print(f"✅ 配置目录已存在：{HERMES_HOME}")


def setup_env_file(api_key):
    """配置 .env 文件"""
    print()
    print("⚙️  配置 .env 文件...")
    
    env_content = f"""# Hermes Agent 环境变量配置

# 阿里云百炼 API Key
DASHSCOPE_API_KEY={api_key}

# 国内版百炼 endpoint
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
"""
    
    # 备份现有文件
    if ENV_FILE.exists():
        backup_file = ENV_FILE.with_suffix(".env.bak")
        ENV_FILE.rename(backup_file)
        print(f"  📦 已备份现有 .env 文件：{backup_file}")
    
    # 写入新配置
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.write(env_content)
    
    print(f"  ✅ 已写入：{ENV_FILE}")


def setup_config_yaml():
    """配置 config.yaml 文件"""
    print()
    print("⚙️  配置 config.yaml...")
    
    # 最小配置
    config_content = """model: alibaba/qwen3.5-plus
providers: {}
fallback_providers: []
toolsets:
  - hermes-cli
agent:
  max_turns: 90
terminal:
  backend: local
  timeout: 180
display:
  personality: kawaii
  skin: default
"""
    
    # 备份现有文件
    if CONFIG_FILE.exists():
        backup_file = CONFIG_FILE.with_suffix(".yaml.bak")
        CONFIG_FILE.rename(backup_file)
        print(f"  📦 已备份现有 config.yaml：{backup_file}")
    
    # 写入新配置
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(config_content)
    
    print(f"  ✅ 已写入：{CONFIG_FILE}")


def verify_config():
    """验证配置"""
    print()
    print("🔍 验证配置...")
    
    # 检查 .env
    if ENV_FILE.exists():
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            if "DASHSCOPE_API_KEY=" in content:
                print("  ✅ .env 文件配置正确")
            else:
                print("  ❌ .env 文件缺少 DASHSCOPE_API_KEY")
                return False
    else:
        print("  ❌ .env 文件不存在")
        return False
    
    # 检查 config.yaml
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            if "alibaba/qwen3.5-plus" in content:
                print("  ✅ config.yaml 配置正确")
            else:
                print("  ❌ config.yaml 未设置 qwen3.5-plus 模型")
                return False
    else:
        print("  ❌ config.yaml 文件不存在")
        return False
    
    return True


def print_summary():
    """打印配置摘要"""
    print()
    print("=" * 60)
    print("  ✅ 配置完成！")
    print("=" * 60)
    print()
    print("📁 配置文件位置:")
    print(f"  - .env:       {ENV_FILE}")
    print(f"  - config.yaml: {CONFIG_FILE}")
    print()
    print("🚀 启动 Hermes:")
    print("  cd ~/hermes-agent")
    print("  source venv/bin/activate")
    print("  hermes")
    print()
    print("📌 验证模型:")
    print("  在 Hermes CLI 中输入：/model")
    print("  应显示：Current: qwen3.5-plus on alibaba")
    print()


def main():
    print_banner()
    
    # 1. 创建目录
    create_hermes_home()
    
    # 2. 获取 API Key
    api_key = get_api_key()
    
    # 3. 配置 .env
    setup_env_file(api_key)
    
    # 4. 配置 config.yaml
    setup_config_yaml()
    
    # 5. 验证配置
    if verify_config():
        print_summary()
        return 0
    else:
        print()
        print("❌ 配置验证失败，请检查配置文件")
        return 1


if __name__ == "__main__":
    sys.exit(main())
