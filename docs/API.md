# Volets Intelligents — contrat de données et API WebSocket

Ce document est le contrat entre l'intégration (Python) et le frontend
(panneau + carte Lovelace). Tout le texte visible par l'utilisateur est en français.

## 1. Configuration (`config`)

Stockée dans `.storage/volets_intelligents.config`. Envoyée/reçue en entier par le panneau.

```jsonc
{
  "version": 1,
  "settings": {
    "outdoor_temp_entity": "sensor.temperature_rossignole",   // str|null (sensor)
    "feels_like_entity": "sensor.temperature_rossignole_ressentie", // str|null (sensor)
    "house_orientation": 180,          // 0–360 : azimut (boussole) vers lequel regarde la façade « Sud » de la maison. 180 = maison alignée N/E/S/O. Toutes les façades tournent avec elle.
    "use_max_feels_like": true,        // température extérieure effective = max(mesure, ressentie)
    "weather_entity": null,            // str|null (weather.*)
    "sunny_conditions": ["sunny", "partlycloudy"], // conditions météo où le soleil "compte"; [] = désactivé
    "wind_entity": null,               // str|null (sensor, vitesse du vent)
    "wind_threshold": 50,              // nombre, même unité que le capteur
    "wind_release_ratio": 0.8,         // 0.1–1.0, relâche quand vent < seuil × ratio
    "evaluation_interval_minutes": 5,  // 1–60
    "startup_grace_seconds": 120,      // 0–900
    "min_move_interval_minutes": 10,   // 0–240, anti-usure moteur
    "position_tolerance": 3,           // 0–20 (%)
    "override_pause_minutes": 120,     // 0–1440
    "override_until_window_end": false,// true = pause jusqu'à la fin de la plage active
    "window": {
      "start": "08:00",                // "HH:MM"
      "end_mode": "entity",            // "entity" | "fixed" | "sunset"
      "end_time": "19:00",             // "HH:MM" (mode fixed, et repli des autres modes). Si end <= start la plage passe minuit (ex. 20:00 -> 02:00) ; end == start : plage vide
      "end_entity": "sensor.volets_heure_remontee", // obligatoire en mode entity (sensor, input_datetime, input_text) ; états lus : "HH:MM", "HH:MM:SS[.ffffff][±HH:MM]" ou datetime ISO ; indisponible => repli sur end_time
      "sunset_offset_minutes": -60     // -240..240 (mode sunset)
    },
    "auto_scenario": {
      "enabled": false,                // choisit "summer" ou "winter" selon le mois
      "summer_months": [5, 6, 7, 8, 9]
    }
  },
  "scenarios": {
    // clés fixes : summer, winter, vacation, off. Le "kind" n'est PAS modifiable.
    "summer":   { "label": "Été",      "kind": "heat_protection",
                  "close_outdoor": 25, "close_room": 24,
                  "open_outdoor": 22,  "open_room": 22,
                  "release_mode": "all" },            // "all" | "any"
    "winter":   { "label": "Hiver",    "kind": "solar_gain",
                  "gain_room_below": 20, "gain_outdoor_below": 15 },
    "vacation": { "label": "Vacances", "kind": "hold_shaded" },
    "off":      { "label": "Désactivé","kind": "off" }
  },
  "facades": [
    // 4 façades par défaut (nord, est, sud, ouest), toutes modifiables : renommer, supprimer, ajouter.
    // N'importe quel volet peut être affecté à n'importe quelle façade (covers[].facade).
    {
      "id": "est",                      // slug unique [a-z0-9_]+
      "name": "Est",
      "orientation": "east",            // "north" | "east" | "south" | "west" | "custom"
      "custom_azimuth": 180,            // 0–360, utilisé seulement si orientation = "custom" (azimut absolu, non tourné par la maison)
      "default_close_position": 10,     // 0–100 (valeur proposée à l'ajout d'un volet)
      "exposure": {
        "mode": "sun",                  // "sun" = calcul selon la date, l'heure, la position GPS de HA et l'orientation de la façade
                                        // "entity" = un capteur existant (binary_sensor, input_boolean, switch) à "on"
        "entity": null,                 // mode entity
        "half_angle": 80,               // 10–90 : le soleil éclaire la façade s'il est à moins de ce nombre de degrés de sa normale
        "elevation_min": 10             // -10..60 : hauteur minimale du soleil (masque d'horizon, arbres, voisins)
      }
    }
  ],
  "covers": [
    {
      "entity_id": "cover.calyps_home_volet_bureau",  // unique
      "name": "Volet bureau Jérôme",
      "facade": "est",                  // id d'une façade
      "enabled": true,                  // équivalent de input_boolean.auto_volet_*
      "close_method": "position",       // "position" | "button" | "close"
      "close_position": 10,             // 0–100, position voulue quand protégé
      "button_entity": null,            // button.* (close_method = "button")
      "open_position": 100,             // 0–100
      "room_temp_entity": "sensor.thermo_bureau_jerome_temperature", // str|null
      "window_entities": [],            // binary_sensor.* (fenêtre/porte ouverte). Un capteur indisponible compte comme OUVERT (sécurité)
      "block_close_if_open": true,      // ne jamais fermer si une fenêtre/porte est ouverte
      "wind_sensitive": false,          // mise en sécurité si vent fort (prioritaire sur le mode, le scénario, la pause et le délai de démarrage ; seul enabled=false y échappe)
      "wind_action": "open",            // "open" (volet remonté) | "close" (store/banne rentré) ; ordres simples open_cover/close_cover,
      "allow_open_closed_in": []        // scénarios (summer|winter|vacation) où l'intégration PEUT remonter ce volet quand il est fermé à 100 % (position 0, ou état closed sans position). Vide = jamais. Exception : si la protection est la fermeture totale (close_method "close" ou close_position 0) et que l'intégration a fermé le volet, il est remonté.
    }
  ]
}
```

## 2. Statut (`status`)

```jsonc
{
  "mode": "auto",              // "auto" | "manual" | "off"
  "scenarios": { "summer": "Été", "winter": "Hiver", "vacation": "Vacances", "off": "Désactivé" }, // libellés, lisibles par tous les utilisateurs
  "scenario": "summer",        // clé de scenarios
  "scenario_label": "Été",
  "scenario_kind": "heat_protection",
  "in_window": true,
  "window_start": "08:00",
  "window_end": "18:40",       // "HH:MM" ou null
  "window_start_at": "2026-09-30T08:00:00+02:00",  // ISO, début de la plage du moment
  "window_end_at": "2026-09-30T18:40:00+02:00",    // ISO ou null
  "grace_active": false,
  "outdoor_temp": 26.1,        // mesure brute ou null
  "outdoor_effective": 27.4,   // valeur utilisée ou null
  "wind": null,
  "wind_exceeded": false,
  "sunny": true,               // false si la météo neutralise le soleil
  "sun": { "azimuth": 190.5, "elevation": 64.2 },   // position du soleil maintenant (degrés)
  "house_orientation": 180,
  "facades": {
    "est": {
      "name": "Est",           // nom de la façade (lisible aussi par les non-admins)
      "orientation": "east",
      "exposed": true,         // exposée maintenant (météo comprise) ; null = capteur d'exposition indisponible (aucune action)
      "source": "sun",         // "sun" | "entity"
      "azimuth": 90.0,         // azimut effectif de la façade, orientation de la maison comprise
      "next_start": "2026-09-30T08:10:00+02:00",  // plage d'ensoleillement en cours, sinon la prochaine du jour, sinon la dernière du jour (ISO) ; null si la façade n'est jamais exposée ce jour-là
      "next_end": "2026-09-30T12:30:00+02:00",
      "windows": [ { "start": "08:10", "end": "12:30" } ]  // plages d'ensoleillement THÉORIQUES du jour (géométrie seule, sans météo), 0, 1 ou 2 plages
    }
  },
  "covers": [
    {
      "entity_id": "cover.calyps_home_volet_bureau",
      "name": "Volet bureau Jérôme",
      "facade": "est",
      "enabled": true,
      "status": "shaded",       // voir §3
      "reason": "Soleil sur la façade Est et 27,4 °C dehors",  // phrase FR
      "position": 10,           // position courante ou null
      "state": "open",          // état HA du cover
      "room_temp": 24.6,
      "exposed": true,
      "paused_until": null,     // ISO ou null
      "shaded_by_us": true,
      "last_action": "close",   // "close" | "open" | null
      "last_action_at": "2026-09-30T11:05:00+02:00",
      "window_state": "closed",  // null (aucun capteur) | "open" | "closed" | "unknown" (capteur indisponible)
      "window_sensors": [ { "entity_id": "binary_sensor.fenetre_bureau", "state": "closed" } ]  // "open" | "closed" | "unknown"
    }
  ],
  "version": 1
}
```

## 3. Codes de statut d'un volet

| code | libellé FR | sens |
|---|---|---|
| `disabled` | Désactivé | volet non géré (enabled=false) |
| `mode_manual` | Mode manuel | mode global = manual |
| `mode_off` | Arrêté | mode global = off |
| `scenario_off` | Scénario désactivé | scénario kind=off |
| `grace` | Démarrage | délai après redémarrage |
| `outside_window` | Hors plage | hors plage active |
| `no_data` | Données manquantes | température extérieure indisponible |
| `paused` | En pause | action manuelle détectée |
| `window_open` | Fenêtre ouverte | fermeture bloquée |
| `wind_protected` | Protégé du vent | remonté à cause du vent |
| `shaded` | Protégé du soleil | volet fermé/abaissé par l'intégration |
| `watching` | Surveillance | rien à faire pour le moment |
| `cooldown` | Anti-usure | attend l'intervalle minimal entre deux mouvements |
| `unavailable` | Indisponible | entité cover indisponible |

Couleurs suggérées : shaded = orange, watching = vert, paused = bleu, window_open/wind_protected = violet,
no_data/unavailable = rouge, le reste = gris.

## 4. API WebSocket (préfixe `volets_intelligents/`)

| type | droits | payload | résultat |
|---|---|---|---|
| `volets_intelligents/get_config` | admin | — | `{ "config": <config>, "defaults": <config par défaut> }` |
| `volets_intelligents/set_config` | admin | `{ "config": <config> }` | `{ "config": <config normalisée> }` ; erreur `code="invalid_config"` avec `message` en français |
| `volets_intelligents/get_entities` | admin | — | `{ "mode", "scenario", "outdoor", "window": { "active", "start", "end", "start_setting", "end_setting", "end_mode", "sunset_offset" }, "facades": [ { "id", "name", "exposed", "start", "end" } ], "covers": [ { "cover", "name", "facade", "switch", "status" } ] }` : identifiants réels des entités (null si absente) |
| `volets_intelligents/get_status` | utilisateur | — | `{ "status": <status> }` |
| `volets_intelligents/subscribe_status` | utilisateur | — | abonnement : un événement `<status>` à chaque évaluation (+ un initial) |
| `volets_intelligents/command` | utilisateur | `{ "command": ..., ... }` | `{ "ok": true }` |

Droits (suivent ceux de Home Assistant) : `get_config` et `set_config` exigent un administrateur ;
`get_status` et `subscribe_status` sont ouverts à tout utilisateur ; `command` exige le droit de
**contrôle** sur les entités concernées (`select.volets_mode` pour `set_mode`, `select.volets_scenario`
pour `set_scenario`, les `cover.*` visés pour `pause`/`resume`, tous les volets gérés si aucun n'est
précisé). Erreurs : `unauthorized`, `invalid_config` (message français), `command_failed`
(message français, ex. changement de scénario refusé quand le scénario automatique est actif), `not_loaded`.

Commandes (`command`) :
- `set_mode` : `value` ∈ `auto|manual|off`
- `set_scenario` : `value` ∈ clés de `scenarios`
- `pause` : `entity_id` (optionnel = tous), `minutes` (défaut = override_pause_minutes)
- `resume` : `entity_id` (optionnel = tous)
- `set_enabled` : `entity_id` (requis), `enabled` (booléen requis) — active/désactive la gestion du volet (équivaut à `switch.volets_*_auto`)
- `evaluate` : force une évaluation immédiate

Côté frontend : `hass.callWS({type: "volets_intelligents/get_config"})` et
`hass.connection.subscribeMessage(cb, {type: "volets_intelligents/subscribe_status"})` (retourne une fonction de désabonnement, à appeler dans `disconnectedCallback`).

## 5. Fichiers frontend

Servis sous `/volets_intelligents_static/`.

- `frontend/volets-panel.js` : custom element `volets-intelligents-panel` (panneau latéral, propriétés `hass`, `narrow`).
- `frontend/volets-card.js` : custom element `volets-intelligents-card` (carte Lovelace ; `setConfig`, `getCardSize`, `getStubConfig`, enregistrée dans `window.customCards`).
