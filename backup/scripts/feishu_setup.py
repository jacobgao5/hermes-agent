#!/usr/bin/env python3
"""
Feishu/Lark Quick Setup Script for Hermes Agent

This script helps you configure Feishu platform adapter interactively.
Run with: python scripts/feishu_setup.py
"""

import os
import sys
import yaml
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
CONFIG_FILE = HERMES_HOME / "config.yaml"
ENV_FILE = HERMES_HOME / ".env"


def print_banner():
    print("=" * 60)
    print("  Hermes Agent - Feishu/Lark Setup Wizard")
    print("=" * 60)
    print()


def check_dependencies():
    """Check if required dependencies are installed."""
    print("📦 Checking dependencies...")
    
    missing = []
    try:
        import lark_oapi
        print("  ✅ lark-oapi")
    except ImportError:
        missing.append("lark-oapi")
        print("  ❌ lark-oapi (not installed)")
    
    try:
        import qrcode
        print("  ✅ qrcode")
    except ImportError:
        missing.append("qrcode")
        print("  ❌ qrcode (not installed)")
    
    try:
        import aiohttp
        print("  ✅ aiohttp")
    except ImportError:
        missing.append("aiohttp")
        print("  ❌ aiohttp (not installed)")
    
    try:
        import websockets
        print("  ✅ websockets")
    except ImportError:
        missing.append("websockets")
        print("  ❌ websockets (not installed)")
    
    print()
    
    if missing:
        print("⚠️  Missing dependencies. Install with:")
        print(f"   pip install {' '.join(missing)}")
        print()
        return False
    
    print("✅ All dependencies installed!")
    print()
    return True


def load_existing_config():
    """Load existing configuration if available."""
    config = {}
    
    # Check environment variables
    env_vars = {
        "app_id": os.getenv("FEISHU_APP_ID"),
        "app_secret": os.getenv("FEISHU_APP_SECRET"),
        "domain": os.getenv("FEISHU_DOMAIN"),
        "connection_mode": os.getenv("FEISHU_CONNECTION_MODE"),
        "encrypt_key": os.getenv("FEISHU_ENCRYPT_KEY"),
        "verification_token": os.getenv("FEISHU_VERIFICATION_TOKEN"),
        "group_policy": os.getenv("FEISHU_GROUP_POLICY"),
    }
    
    # Check config.yaml
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                full_config = yaml.safe_load(f) or {}
                platform_config = full_config.get("platforms", {}).get("feishu", {})
                if platform_config:
                    config = platform_config.get("extra", {})
        except Exception as e:
            print(f"⚠️  Could not read config.yaml: {e}")
    
    # Environment variables take precedence
    for key, value in env_vars.items():
        if value:
            config[key] = value
    
    return config


def get_input(prompt, default=None, sensitive=False):
    """Get user input with optional default."""
    if default:
        prompt = f"{prompt} [{default}]"
    
    if sensitive:
        import getpass
        value = getpass.getpass(prompt + ": ")
    else:
        value = input(prompt + ": ")
    
    return value.strip() if value.strip() else (default or "")


def configure_feishu():
    """Interactive configuration."""
    print("🔧 Feishu Configuration")
    print("-" * 40)
    print()
    
    existing = load_existing_config()
    
    # App ID
    app_id = get_input(
        "App ID",
        default=existing.get("app_id", ""),
        sensitive=False
    )
    
    # App Secret
    app_secret = get_input(
        "App Secret",
        default=existing.get("app_secret", ""),
        sensitive=True
    )
    
    # Domain
    domain = get_input(
        "Domain",
        default=existing.get("domain", "feishu"),
    )
    if domain not in ("feishu", "lark"):
        print("⚠️  Invalid domain. Must be 'feishu' or 'lark'")
        domain = "feishu"
    
    # Connection Mode
    connection_mode = get_input(
        "Connection Mode",
        default=existing.get("connection_mode", "websocket"),
    )
    if connection_mode not in ("websocket", "webhook"):
        print("⚠️  Invalid mode. Must be 'websocket' or 'webhook'")
        connection_mode = "websocket"
    
    # Encrypt Key
    encrypt_key = get_input(
        "Encrypt Key",
        default=existing.get("encrypt_key", ""),
        sensitive=True
    )
    
    # Verification Token
    verification_token = get_input(
        "Verification Token",
        default=existing.get("verification_token", ""),
        sensitive=True
    )
    
    # Group Policy
    group_policy = get_input(
        "Group Policy",
        default=existing.get("group_policy", "mention_only"),
    )
    if group_policy not in ("mention_only", "open", "disabled", "allowlist"):
        print("⚠️  Invalid policy. Using 'mention_only'")
        group_policy = "mention_only"
    
    print()
    
    return {
        "app_id": app_id,
        "app_secret": app_secret,
        "domain": domain,
        "connection_mode": connection_mode,
        "encrypt_key": encrypt_key,
        "verification_token": verification_token,
        "group_policy": group_policy,
    }


def save_config(config):
    """Save configuration to config.yaml and .env."""
    print("💾 Saving configuration...")
    
    # Update config.yaml
    full_config = {}
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                full_config = yaml.safe_load(f) or {}
        except:
            pass
    
    if "platforms" not in full_config:
        full_config["platforms"] = {}
    
    full_config["platforms"]["feishu"] = {
        "enabled": True,
        "extra": config
    }
    
    # Add webhook settings if using webhook mode
    if config.get("connection_mode") == "webhook":
        full_config["platforms"]["feishu"]["extra"].update({
            "webhook_host": "0.0.0.0",
            "webhook_port": 8765,
            "webhook_path": "/feishu/webhook"
        })
    
    with open(CONFIG_FILE, "w") as f:
        yaml.dump(full_config, f, default_flow_style=False, allow_unicode=True)
    
    print(f"  ✅ Saved to {CONFIG_FILE}")
    
    # Update .env file
    env_content = ""
    if ENV_FILE.exists():
        with open(ENV_FILE) as f:
            env_content = f.read()
    
    # Remove old FEISHU_* entries
    env_lines = [
        line for line in env_content.split("\n")
        if not line.startswith("FEISHU_")
    ]
    
    # Add new entries
    env_entries = [
        f"FEISHU_ENABLED=true",
        f"FEISHU_APP_ID={config['app_id']}",
        f"FEISHU_DOMAIN={config['domain']}",
        f"FEISHU_CONNECTION_MODE={config['connection_mode']}",
        f"FEISHU_GROUP_POLICY={config['group_policy']}",
    ]
    
    # Only add sensitive info if provided
    if config.get("app_secret"):
        env_entries.append(f"FEISHU_APP_SECRET={config['app_secret']}")
    if config.get("encrypt_key"):
        env_entries.append(f"FEISHU_ENCRYPT_KEY={config['encrypt_key']}")
    if config.get("verification_token"):
        env_entries.append(f"FEISHU_VERIFICATION_TOKEN={config['verification_token']}")
    
    env_content = "\n".join(env_lines + env_entries) + "\n"
    
    with open(ENV_FILE, "w") as f:
        f.write(env_content)
    
    print(f"  ✅ Saved to {ENV_FILE}")
    print()


def print_next_steps(config):
    """Print next steps for the user."""
    print("🎉 Configuration complete!")
    print()
    print("Next steps:")
    print()
    print("1. Start the gateway:")
    print("   hermes gateway run")
    print()
    
    if config.get("connection_mode") == "webhook":
        print("2. Configure webhook URL in Feishu Open Platform:")
        print(f"   https://your-domain.com:8765/feishu/webhook")
        print()
    
    print("3. Test the connection:")
    print("   - Send a message to your bot in Feishu")
    print("   - Or @mention the bot in a group chat")
    print()
    
    print("4. Check logs:")
    print("   tail -f ~/.hermes/logs/gateway.log | grep feishu")
    print()
    
    print("📖 For detailed documentation, see:")
    print("   docs/feishu-setup-guide.md")
    print()


def main():
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("Please install missing dependencies and run this script again.")
        return 1
    
    # Configure
    config = configure_feishu()
    
    # Validate
    if not config.get("app_id") or not config.get("app_secret"):
        print("❌ App ID and App Secret are required!")
        return 1
    
    # Save
    save_config(config)
    
    # Next steps
    print_next_steps(config)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
