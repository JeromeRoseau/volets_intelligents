"""Constantes de l'intégration Volets Intelligents."""

from __future__ import annotations

DOMAIN = "volets_intelligents"
VERSION = "0.3.2"
NAME = "Volets Intelligents"

# Fichiers statiques du frontend
URL_BASE = "/volets_intelligents_static"
PANEL_URL_PATH = "volets-intelligents"
PANEL_ELEMENT = "volets-intelligents-panel"
PANEL_JS = "volets-panel.js"
CARD_JS = "volets-card.js"

# Stockage
STORAGE_KEY_CONFIG = f"{DOMAIN}.config"
STORAGE_KEY_RUNTIME = f"{DOMAIN}.runtime"
STORAGE_VERSION = 1
CONFIG_VERSION = 1

# Signaux (dispatcher)
SIGNAL_STATUS_UPDATED = f"{DOMAIN}_status_updated"
SIGNAL_CONFIG_CHANGED = f"{DOMAIN}_config_changed"

# Modes globaux
MODE_AUTO = "auto"
MODE_MANUAL = "manual"
MODE_OFF = "off"
MODES = (MODE_AUTO, MODE_MANUAL, MODE_OFF)

# Types de scénario
KIND_HEAT = "heat_protection"
KIND_GAIN = "solar_gain"
KIND_HOLD = "hold_shaded"
KIND_OFF = "off"

# Méthodes de fermeture
CLOSE_POSITION = "position"
CLOSE_BUTTON = "button"
CLOSE_FULL = "close"
CLOSE_METHODS = (CLOSE_POSITION, CLOSE_BUTTON, CLOSE_FULL)

# Modes d'exposition et de fin de plage
EXPOSURE_ENTITY = "entity"
EXPOSURE_SUN = "sun"
END_ENTITY = "entity"
END_FIXED = "fixed"
END_SUNSET = "sunset"

# Statuts d'un volet
ST_DISABLED = "disabled"
ST_MODE_MANUAL = "mode_manual"
ST_MODE_OFF = "mode_off"
ST_SCENARIO_OFF = "scenario_off"
ST_GRACE = "grace"
ST_OUTSIDE = "outside_window"
ST_NO_DATA = "no_data"
ST_PAUSED = "paused"
ST_WINDOW_OPEN = "window_open"
ST_WIND = "wind_protected"
ST_SHADED = "shaded"
ST_WATCHING = "watching"
ST_COOLDOWN = "cooldown"
ST_UNAVAILABLE = "unavailable"
STATUSES = (
    ST_DISABLED,
    ST_MODE_MANUAL,
    ST_MODE_OFF,
    ST_SCENARIO_OFF,
    ST_GRACE,
    ST_OUTSIDE,
    ST_NO_DATA,
    ST_PAUSED,
    ST_WINDOW_OPEN,
    ST_WIND,
    ST_SHADED,
    ST_WATCHING,
    ST_COOLDOWN,
    ST_UNAVAILABLE,
)

# Actions
ACTION_CLOSE = "close"
ACTION_OPEN = "open"

# Délai pendant lequel un mouvement suivant nos propres ordres n'est pas
# interprété comme une action manuelle (durée de course du volet incluse).
SETTLE_SECONDS = 120

# Un volet encore « en mouvement » jusqu'à ce délai après notre ordre est considéré
# comme suivant cet ordre (volets ou stores lents).
MOTION_GRACE_SECONDS = 600
