---
name: smartthings-cli
description: Query and manage SmartThings devices via CLI, with China region support using --environment flag.
version: 1.0.0
author: community
license: Apache-2.0
metadata:
  hermes:
    tags: [Smart-Home, SmartThings, IoT, Samsung, China-Region]
    homepage: https://github.com/SmartThingsCommunity/smartthings-cli
prerequisites:
  commands: [smartthings]
---

# SmartThings CLI

Command-line interface for managing SmartThings devices, especially for China region users.

## Installation

```bash
npm install -g @smartthings/cli
```

**Requirements:** Node.js >= 22 (or at least 20.x may work with warnings)

## China Region Support

The SmartThings CLI supports both global and China regions. Use the `--environment` flag:

```bash
# Query devices in China region
smartthings devices --environment china

# Query devices in global region (default)
smartthings devices --environment global
```

## Common Commands

### List Devices
```bash
# All devices in China
smartthings devices --environment china

# With verbose output (includes location/room)
smartthings devices --environment china --verbose

# JSON output
smartthings devices --environment china --json

# Filter by capability
smartthings devices --environment china --capability switch

# Filter by device type
smartthings devices --environment china --type zigbee --type zwave
```

### Device Details
```bash
# Get specific device by ID
smartthings devices <device-id> --environment china

# Get device status
smartthings devices:status <device-id> --environment china

# Get device health
smartthings devices:health <device-id> --environment china

# Get device history
smartthings devices:history <device-id> --environment china
```

### Locations & Rooms
```bash
# List locations
smartthings locations --environment china

# List rooms in a location
smartthings locations:rooms <location-id> --environment china
```

### Scenes & Rules
```bash
# List scenes
smartthings scenes --environment china

# Execute a scene
smartthings scenes:execute <scene-id> --environment china

# List rules
smartthings rules --environment china
```

## Configuration

### Config File Location
- **Linux:** `~/.config/@smartthings/cli/config.yaml`
- **MacOS:** `~/Library/Preferences/@smartthings/cli/config.yaml`
- **Windows:** `%LOCALAPPDATA%\@smartthings\cli\config.yaml`

### Set Default Environment
To avoid typing `--environment china` every time, add to config:

```yaml
default:
  environment: china
```

### Multiple Profiles
```yaml
default:
  environment: global

china:
  environment: china
  indent: 2
```

Use with `--profile` flag:
```bash
smartthings devices --profile china
```

## Authentication

### Browser Login (Recommended)
The CLI automatically opens a browser window for OAuth login on first use.

### Personal Access Token (PAT)
For headless servers or account switching:

1. Generate PAT in SmartThings developer portal
2. Add to config:
```yaml
default:
  token: <your-pat-uuid>
  environment: china
```

Or use inline:
```bash
smartthings devices --token <uuid> --environment china
```

## Device Integration Types

Available `--type` filters:
- `ZIGBEE`, `ZWAVE`, `MATTER`
- `LAN`, `MQTT`, `OCF`
- `BLE`, `BLE_D2D`
- `VIRTUAL`, `MOBILE`
- `HUB`, `GROUP`
- `IR`, `IR_OCF`
- `ENDPOINT_APP`, `DTH`
- `PENGYOU`, `SHP`, `VIDEO`, `VIPER`, `WATCH`
- `EDGE_CHILD`

## Troubleshooting

### Node Version Warnings
If you see `EBADENGINE` warnings about Node version:
```bash
# Upgrade Node.js to >= 22
# Or ignore warnings if CLI works
```

### Authentication Issues
```bash
# Force re-login
smartthings logout
smartthings devices --environment china
```

### API Differences
China region uses different API endpoints. Some features available globally may not be available in China region and vice versa.

## Useful One-liners

```bash
# Count devices by type
smartthings devices --environment china --json | jq '[.[] | .type] | group_by(.) | map({type: .[0], count: length})'

# List all switch devices
smartthings devices --environment china --capability switch --json | jq '.[].label'

# Export device list to file
smartthings devices --environment china --json > devices.json
```

## Related Resources

- GitHub: https://github.com/SmartThingsCommunity/smartthings-cli
- API Docs: https://developer.smartthings.com/docs/api/public/
- Core SDK: https://github.com/SmartThingsCommunity/smartthings-core-sdk
