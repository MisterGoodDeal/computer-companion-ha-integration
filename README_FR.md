# Computer Companion · Home Assistant

**Langue :** Français · [English →](README.md)

<div align="center">

**Contrôle ton PC Windows depuis Home Assistant** — alimentation, liste du menu Démarrer, lancement d’exécutables — via une API HTTP locale sécurisée par jeton Bearer.

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.1+-41BDF5.svg)](https://www.home-assistant.io/)

</div>

---

## Architecture

Cette intégration dialogue avec l’agent **Computer Companion** : une application desktop (Electron + Express) qui expose une API REST sur le réseau local.

| Composant | Rôle |
|-----------|------|
| **[computer-companion-desktop-agent](https://github.com/MisterGoodDeal/computer-companion-desktop-agent)** | À installer sur le PC Windows à piloter. Génère le jeton Bearer et sert l’API (`/health`, `/api/v1/…`). |
| **Cette intégration** | S’installe dans Home Assistant et se connecte à l’agent (IP ou nom d’hôte + port + jeton). |

Sans l’agent installé et configuré sur la machine cible, l’intégration ne peut rien contrôler.

---

## Prérequis

1. **Home Assistant** (version minimale indiquée dans [`hacs.json`](hacs.json)).
2. **Computer Companion (desktop)** sur le PC Windows — dépôt officiel :  
   **[github.com/MisterGoodDeal/computer-companion-desktop-agent](https://github.com/MisterGoodDeal/computer-companion-desktop-agent)**  
   - Lance l’agent, configure l’écoute réseau (souvent `0.0.0.0` si Home Assistant est sur un autre appareil) et le **port** (défaut **8745**).
   - **Génère un jeton Bearer** dans l’application et conserve-le pour l’étape de configuration HA.
3. **Réseau** : le serveur Home Assistant doit joindre le PC (IP fixe, nom d’hôte ou mDNS). Ouvre le pare-feu Windows sur le port choisi si besoin.

---

## Installation

### Option A — via HACS (recommandé)

1. Installe **[HACS](https://hacs.xyz/docs/setup/download)** si ce n’est pas déjà fait.
2. Dans HACS : **⋮** → **Dépôts personnalisés**.
3. Ajoute **l’URL Git de ce dépôt**, catégorie **Intégration**.
4. Recherche **Computer Companion** dans les intégrations HACS, puis **Télécharger**.
5. **Redémarre** Home Assistant.
6. **Paramètres** → **Appareils et services** → **Ajouter une intégration** → **Computer Companion**.

### Option B — installation manuelle

1. Copie le dossier `custom_components/computer_companion/` à la racine de ta config HA (à côté de `configuration.yaml`).
2. Redémarre Home Assistant.
3. Ajoute l’intégration comme ci-dessus.

---

## Configuration

L’assistant te demande :

| Champ | Description |
|--------|-------------|
| **Hôte** | IP ou nom d’hôte du PC où tourne l’agent (ex. `192.168.1.42` ou `mon-pc.local`). |
| **Port** | Port HTTP de l’agent (souvent **8745**). |
| **Jeton Bearer** | Jeton généré dans l’application desktop (champ masqué). |

Au premier ajout, l’intégration vérifie `GET /health` puis `GET /api/v1/status` avec authentification.

---

## Fonctionnalités

- **Capteurs** : plate-forme (`win32`, etc.), binaire **Windows**, **Présence** (joignabilité de l’API via le polling `/api/v1/status`).
- **Select + texte + boutons** : actualiser la liste du menu Démarrer, choisir une app dans la liste **ou** saisir un chemin complet vers un `.exe` dans **Chemin d'exécutable personnalisé**, puis appuyer sur **Lancer l'application sélectionnée** (Windows uniquement).
- **Services** : `computer_companion.power` (shutdown, restart, sleep, hibernate, abort) et `computer_companion.launch` (chemin + arguments optionnels).

Les actions sensibles (arrêt, lancement d’exe) exigent un **réseau de confiance** et un **jeton bien protégé**.

### Pourquoi un champ texte plutôt qu’un select « libre » ?

Les entités **`select`** de Home Assistant ne permettent que de choisir parmi une **liste fixe** d’options : pas de saisie libre. Pour lancer un chemin absent du scan **depuis l’interface avec le même bouton de lancement**, utilise l’entité **`text`** **Chemin d'exécutable personnalisé** : si elle n’est pas vide, **Lancer l'application sélectionnée** utilise ce chemin en priorité ; sinon elle utilise l’option choisie dans **Application à lancer**.

### Applications « custom » (n’importe quel exécutable)

Une app n’a **pas** besoin d’apparaître dans la liste scannée. L’agent desktop accepte **n’importe quel chemin absolu** vers un `.exe` existant (voir l’API : `POST /api/v1/apps/launch`).

**Depuis l’UI :** renseigne **Chemin d'exécutable personnalisé** (ex. `D:\Apps\Tool\tool.exe`) puis **Lancer l'application sélectionnée**. Vide le champ texte pour que le bouton se base uniquement sur le **select** **Application à lancer**.

**Depuis YAML / automations**, tu peux soit remplir cette entité texte puis appuyer sur le bouton, soit appeler le service **`computer_companion.launch`** :

| Champ | Description |
|-------|-------------|
| `config_entry` | Identifiant de l’entrée de config Computer Companion (comme dans **Outils de développement → Actions** quand tu choisis l’intégration dans l’UI). |
| `path` | Chemin complet vers l’exécutable, ex. `C:\Games\SomeGame\game.exe`. |
| `args` | Liste optionnelle d’arguments en ligne de commande (chaînes). |

Exemple (adapte `config_entry` — copie depuis **Paramètres → Appareils et services → Computer Companion** → menu trois points sur l’intégration, ou remplis une fois via l’UI **Actions**) :

```yaml
action: computer_companion.launch
data:
  config_entry: YOUR_CONFIG_ENTRY_ID
  path: "D:\\Apps\\MyApp\\app.exe"
  args: ["--some-flag"]
```

### Exemple de script : lancer une app de la liste scannée

Utilise le **select** **Application à lancer** (la valeur **option** doit correspondre à un libellé de la liste, ex. `Steam`) puis **Lancer l'application sélectionnée**.

Copie les vrais `entity_id` depuis **Outils de développement → États** ou depuis la page de l’appareil — ils dépendent du nom d’hôte et de la langue de l’UI (suffixes du type `application_to_launch` en anglais vs `application_a_lancer` en français, etc.).

```yaml
alias: Lancer Steam
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

En interface anglaise, les mêmes entités peuvent ressembler à `select.192_168_1_33_application_to_launch` et `button.192_168_1_33_launch_selected_application`. Utilise la **chaîne exacte** affichée pour l’option du select (y compris désambiguïsation du type `Steam (1)` si besoin).

### Exemple de script : chemin perso + même bouton de lancement

Mets le chemin complet dans l’entité texte **Chemin d'exécutable personnalisé**, puis **Lancer l'application sélectionnée** (les `entity_id` dépendent de l’hôte / de la langue) :

```yaml
alias: Lancer un exe perso
mode: single
sequence:
  - action: text.set_value
    target:
      entity_id: text.192_168_1_33_chemin_d_executable_personnalise
    data:
      value: "D:\\Games\\Launcher\\game.exe"
  - action: button.press
    target:
      entity_id: button.192_168_1_33_lancer_l_application_selectionnee
    data: {}
```

Utilise ton vrai `text.*` depuis les **Outils de développement** (le suffixe peut varier, ex. `custom_executable_path` en anglais).

---

## Mises à jour

Les versions suivent le champ `version` dans `manifest.json`. Avec HACS, publie des **releases / tags** sur GitHub (ex. `v0.3.0`) pour que les utilisateurs voient les mises à jour. Un script d’aide est fourni : [`scripts/release.sh`](scripts/release.sh).

---

## Dépannage

| Problème | Piste |
|----------|--------|
| Échec à la configuration | IP/port, pare-feu, et que l’agent écoute sur la bonne interface (pas seulement `127.0.0.1` si HA est ailleurs). |
| `401` / jeton refusé | Régénère le jeton dans l’app desktop et mets à jour l’intégration. |
| Liste d’apps lente | Scan PowerShell côté Windows — patience, ou augmente les timeouts côté agent si c’est configurable. |

---

## Liens

| Ressource | URL |
|-----------|-----|
| Agent desktop (Windows) | [MisterGoodDeal/computer-companion-desktop-agent](https://github.com/MisterGoodDeal/computer-companion-desktop-agent) |
| HACS | [hacs.xyz](https://hacs.xyz/) |
| Home Assistant | [home-assistant.io](https://www.home-assistant.io/) |
