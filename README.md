# Computer Companion · Home Assistant

<div align="center">

**Control your Windows PC from Home Assistant** — power, Start Menu app list, launching executables — over a local HTTP API secured with a Bearer token.

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.1+-41BDF5.svg)](https://www.home-assistant.io/)

</div>

---

## Architecture

This integration talks to the **Computer Companion** agent: a desktop app (Electron + Express) that exposes a REST API on the local network.

| Component | Role |
|-----------|------|
| **[computer-companion-desktop-agent](https://github.com/MisterGoodDeal/computer-companion-desktop-agent)** | Install on the Windows PC you want to control. Generates the Bearer token and serves the API (`/health`, `/api/v1/…`). |
| **This integration** | Installs in Home Assistant and connects to the agent using IP/hostname + port + token. |

Without the agent installed and configured on the target machine, the integration cannot control anything.

---

## Prerequisites

1. **Home Assistant** (minimum version is listed in [`hacs.json`](hacs.json)).
2. **Computer Companion (desktop)** on the Windows PC — official repo:  
   **[github.com/MisterGoodDeal/computer-companion-desktop-agent](https://github.com/MisterGoodDeal/computer-companion-desktop-agent)**  
   - Run the agent, set the bind address (often `0.0.0.0` if Home Assistant runs on another device) and the **port** (default **8745**).
   - **Generate a Bearer token** in the app and keep it for the HA setup step.
3. **Network**: the Home Assistant host must reach the PC (static IP, hostname, or mDNS). Open the Windows firewall on the chosen port if needed.

---

## Installation

### Option A — HACS (recommended)

1. Install **[HACS](https://hacs.xyz/docs/setup/download)** if you have not already.
2. In HACS: **⋮** → **Custom repositories**.
3. Add **this repository’s Git URL**, category **Integration**.
4. Search for **Computer Companion** under HACS integrations, then **Download**.
5. **Restart** Home Assistant.
6. **Settings** → **Devices & services** → **Add integration** → **Computer Companion**.

### Option B — Manual install

1. Copy the `custom_components/computer_companion/` folder into your HA configuration root (next to `configuration.yaml`).
2. Restart Home Assistant.
3. Add the integration as above.

---

## Configuration

The setup flow asks for:

| Field | Description |
|--------|-------------|
| **Host** | IP or hostname of the PC running the agent (e.g. `192.168.1.42` or `my-pc.local`). |
| **Port** | HTTP port of the agent (often **8745**). |
| **Bearer token** | Token generated in the desktop app (masked field). |

On first setup, the integration checks `GET /health` then `GET /api/v1/status` with authentication.

---

## Features

- **Sensors**: platform (`win32`, etc.), **Windows** binary, **Presence** (API reachability based on `/api/v1/status` polling).
- **Select + buttons**: refresh the Start Menu app list, launch the selected app (Windows only).
- **Services**: `computer_companion.power` (shutdown, restart, sleep, hibernate, abort) and `computer_companion.launch` (path + optional arguments).

Sensitive actions (shutdown, launching executables) require a **trusted network** and a **well-protected token**.

---

## Updates

Versions follow the `version` field in `manifest.json`. With HACS, publish **releases / tags** on GitHub (e.g. `v0.3.0`) so users get update notifications. A helper script lives at [`scripts/release.sh`](scripts/release.sh).

---

## Troubleshooting

| Issue | What to check |
|-------|----------------|
| Setup fails | IP/port, firewall, and that the agent listens on the right interface (not only `127.0.0.1` if HA is on another host). |
| `401` / token rejected | Regenerate the token in the desktop app and update the integration. |
| Slow app list | PowerShell scan on Windows — wait, or increase timeouts on the agent if configurable. |

---

## Links

| Resource | URL |
|----------|-----|
| Desktop agent (Windows) | [MisterGoodDeal/computer-companion-desktop-agent](https://github.com/MisterGoodDeal/computer-companion-desktop-agent) |
| HACS | [hacs.xyz](https://hacs.xyz/) |
| Home Assistant | [home-assistant.io](https://www.home-assistant.io/) |

---

<div align="center">

*Not affiliated with Home Assistant or the desktop agent authors — use at your own risk on your network.*

</div>
