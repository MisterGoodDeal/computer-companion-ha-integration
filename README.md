# Computer Companion · Home Assistant

**Language:** English · [Français →](README_FR.md)

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
- **Select + text + buttons**: refresh the Start Menu app list, pick an app from the list **or** type a full `.exe` path in **Custom executable path**, then press **Launch selected application** (Windows only).
- **Power buttons** (Windows): shut down, restart, sleep, hibernate, abort pending shutdown — same actions as the `computer_companion.power` service.
- **Wake on LAN**: button that sends a magic packet using the MAC from `GET /api/v1/network/mac` (cached while the agent is reachable so you can wake the PC when it is off).
- **Services**: `computer_companion.power` (shutdown, restart, sleep, hibernate, abort) and `computer_companion.launch` (path + optional arguments).

Sensitive actions (shutdown, launching executables) require a **trusted network** and a **well-protected token**.

### Why a text field instead of a “free” select?

Home Assistant **`select`** entities only allow choosing from a **fixed list** of options. They cannot accept arbitrary typed text. To launch a path that is not in the scanned list **from the UI with the same launch button**, use the **`text`** entity **Custom executable path**: when it is non-empty, **Launch selected application** uses that path first; otherwise it uses the option selected in **Application to launch**.

### Custom applications (any executable)

You do **not** need an app to appear in the scanned list. The desktop agent accepts **any absolute path** to an existing `.exe` (see its API: `POST /api/v1/apps/launch`).

**From the UI:** set **Custom executable path** (e.g. `D:\Apps\Tool\tool.exe`) and press **Launch selected application**. Clear the text field when you want the button to use only the **Application to launch** select again.

**From YAML / automations**, you can either set that text entity then press the button, or call the service **`computer_companion.launch`**:

| Field | Description |
|-------|-------------|
| `config_entry` | Your Computer Companion config entry ID (same as in **Developer tools → Services** when you pick the integration in the UI). |
| `path` | Full path to the executable, e.g. `C:\Games\SomeGame\game.exe`. |
| `args` | Optional list of command-line arguments (strings). |

Example (adjust `config_entry` — copy from **Settings → Devices & services → Computer Companion** → the three-dot menu on the integration, or use the **Services** UI once to fill it automatically):

```yaml
action: computer_companion.launch
data:
  config_entry: YOUR_CONFIG_ENTRY_ID
  path: "D:\\Apps\\MyApp\\app.exe"
  args: ["--some-flag"]
```

### Example script: launch an app from the scanned list

Use the **Application to launch** select (the **option** value must match a label from the list, e.g. `Steam`) and then press **Launch selected application**.

Copy the real `entity_id` values from **Developer tools → States** or from the device — they depend on the host name and UI language (suffixes like `application_to_launch` vs French `application_a_lancer`, etc.).

```yaml
alias: Launch Steam
description: ""
mode: single
sequence:
  - action: select.select_option
    target:
      entity_id: select.192_168_1_33_application_a_lancer
    data:
      option: Steam
  - action: button.press
    target:
      entity_id: button.192_168_1_33_lancer_l_application_selectionnee
    data: {}
```

If your UI is in English, the same entities might look like `select.192_168_1_33_application_to_launch` and `button.192_168_1_33_launch_selected_application`. Use the **exact** option string shown for the select (including duplicate disambiguation like `Steam (1)` if applicable).

### Example script: custom path + same launch button

Set the full path in the **Custom executable path** text entity, then press **Launch selected application** (entity IDs depend on your host / language):

```yaml
alias: Launch custom exe
mode: single
sequence:
  - action: text.set_value
    target:
      entity_id: text.192_168_1_33_custom_executable_path
    data:
      value: "D:\\Games\\Launcher\\game.exe"
  - action: button.press
    target:
      entity_id: button.192_168_1_33_lancer_l_application_selectionnee
    data: {}
```

Use your real `text.*` entity id from **Developer tools** (suffix may differ, e.g. `custom_executable_path` in English).

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
