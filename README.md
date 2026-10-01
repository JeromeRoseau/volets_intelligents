# Volets Intelligents

Intégration Home Assistant (HACS) qui protège la maison de la chaleur en pilotant les volets
selon le soleil, les températures et l'activité des habitants, avec un **panneau de gestion
graphique** et une **carte Lovelace**. Aucun YAML à écrire.

## Ce que fait l'intégration

- **Protection thermique (scénario Été)** : un volet s'abaisse à la position voulue quand sa façade
  reçoit le soleil ET qu'il fait chaud dehors ou dans la pièce. Il remonte quand le soleil quitte
  la façade ou que les températures sont redescendues.
- **Hystérésis** : seuils de fermeture et d'ouverture distincts, plus un intervalle minimal entre
  deux mouvements (anti-usure).
- **Quatre façades, orientation de la maison** : nord, est, sud, ouest par défaut (renommables,
  supprimables, on peut en ajouter). Vous indiquez vers où regarde la façade que vous appelez « Sud » :
  toutes les façades tournent avec elle. Chaque volet est affecté à la façade de votre choix.
- **Soleil calculé selon le jour** : l'exposition de chaque façade est calculée avec la date, l'heure et
  la position GPS de Home Assistant (azimut et hauteur du soleil), donc elle suit les saisons sans
  aucun capteur. Réglages par façade : angle d'éclairage et hauteur minimale du soleil (arbres,
  voisins). Les plages d'ensoleillement du jour sont affichées pour chaque façade. Vous pouvez aussi
  utiliser un capteur existant (par exemple `binary_sensor.volets_exposition_*`).
- **Position voulue par volet** : chaque volet a sa propre position de protection (pourcentage,
  bouton « position favorite » ou fermeture complète).
- **Pause automatique après action manuelle** : si vous bougez un volet à la main, il est laissé
  tranquille pendant la durée choisie (ou jusqu'à la fin de la plage active).
- **Fenêtre ou porte ouverte** : la fermeture est bloquée (utile pour les portes-fenêtres). Un capteur de
  fenêtre indisponible compte comme « ouvert » : on ne prend pas le risque d'enfermer quelqu'un dehors.
- **Vent** (stores et bannes) : mise en sécurité automatique au-delà d'un seuil, avec hystérésis. Elle est
  prioritaire sur le mode (même « manuel » ou « arrêté »), le scénario, la pause et le délai de démarrage ;
  seul un volet dont la gestion automatique est désactivée y échappe. Pour chaque volet, choisissez l'ordre
  qui le met en sécurité : « ouvrir » (volet roulant remonté) ou « fermer » (store ou banne rentré).
- **Météo** : un ciel couvert peut neutraliser l'effet du soleil.
- **Scénarios** : Été (protection), Hiver (ouvre pour profiter du soleil quand la pièce est fraîche),
  Vacances (protège dès qu'il y a du soleil), Désactivé. Choix manuel ou automatique selon le mois.
- **Sécurités** : délai après redémarrage, aucune action si la température extérieure ou le capteur
  d'exposition est indisponible, jamais de réouverture d'un volet que vous avez fermé vous-même.
- **Transparence** : chaque volet affiche en français pourquoi il est dans son état.

## Installation

1. HACS > Intégrations > menu ⋮ > Dépôts personnalisés : ajoutez ce dépôt (catégorie Intégration).
2. Téléchargez « Volets Intelligents », puis redémarrez Home Assistant.
3. Paramètres > Appareils et services > Ajouter une intégration > Volets Intelligents.
4. Ouvrez le panneau **Volets** dans la barre latérale et configurez.

Version minimale de Home Assistant : 2026.3.0. Le panneau et la carte sont disponibles en français et en anglais.

### Premiers pas

1. **Orientation de la maison** (Réglages) : vers quel azimut regarde votre façade « Sud » ? 180 si votre
   maison est alignée sur les points cardinaux, 135 si la façade principale regarde le sud-est.
   Les coordonnées GPS viennent de la configuration de Home Assistant (Paramètres > Système > Général).
2. **Température extérieure** (Réglages) : un capteur de température, et éventuellement la température ressentie.
3. **Volets** : ajoutez vos volets (ajout groupé possible) et choisissez la façade de chacun.

## Configuration dans le panneau

| Onglet | Contenu |
|---|---|
| Tableau de bord | Mode global, scénario, températures, plage active, état de chaque volet, pause et reprise. |
| Volets | Liste des volets : façade, position de protection, méthode, température de la pièce, fenêtres. |
| Façades | Orientation, angle d'éclairage, masque d'horizon, plages d'ensoleillement du jour. |
| Scénarios | Seuils de chaque scénario. |
| Réglages | Capteurs extérieurs, plage active, pause manuelle, vent, météo, import et export JSON. |

Pour démarrer vite avec une configuration complète, collez le contenu d'`examples/config-jerome.json`
dans Réglages > Sauvegarde et import, puis cliquez sur **Importer** et **Enregistrer**.

### Comment le soleil est calculé

L'azimut d'une façade est sa direction cardinale (nord 0°, est 90°, sud 180°, ouest 270°) décalée de
« orientation de la maison − 180 ». Une façade « personnalisée » (lucarne, pan de toit) a son propre azimut.
Elle est éclairée quand le soleil est au-dessus de la hauteur minimale ET à moins de l'angle d'éclairage
(80° par défaut) de la perpendiculaire à la façade. Il s'agit d'une géométrie simple : elle ne connaît ni
les débords de toit ni les obstacles, que l'on compense avec la hauteur minimale ou un capteur d'exposition.

### Règles de la protection thermique

Un volet **non protégé** se ferme si : la façade est exposée ET (température extérieure effective
> seuil de fermeture extérieur OU température de la pièce > seuil de fermeture pièce).
La température extérieure effective est le maximum entre la mesure et la température ressentie.

Un volet **protégé par l'intégration** remonte si la façade n'est plus exposée, ou selon le mode de relâche :

- `all` (recommandé) : extérieur sous le seuil d'ouverture ET pièce sous le seuil d'ouverture. Évite
  que la pièce, refroidie par le volet fermé, le fasse rouvrir en plein soleil.
- `any` : comportement de l'ancienne automatisation, un seul des deux suffit.

À la fin de la plage active, les volets encore protégés remontent.

## Entités pour vos tableaux de bord

L'intégration crée un appareil « Volets Intelligents » qui regroupe toutes ses entités. Les identifiants
ci-dessous sont les identifiants **habituels** : Home Assistant les construit à partir du nom du volet au
moment de sa création. Vérifiez les vôtres dans Paramètres > Appareils et services > Volets Intelligents
(ou en cherchant « volets » dans Paramètres > Entités). Dans les exemples, `bureau` est à remplacer par le
nom de votre volet.

### Entités globales

| Entité | Type | Valeurs | Usage |
|---|---|---|---|
| `select.volets_mode` | select | `auto`, `manual`, `off` (affichés Automatique, Manuel, Arrêté) | Mode global. Modifiable depuis un tableau de bord. |
| `select.volets_scenario` | select | `summer`, `winter`, `vacation`, `off` (affichés Été, Hiver, Vacances, Désactivé) | Scénario actif. Modifiable, sauf quand le scénario automatique selon le mois est activé. |
| `sensor.volets_temperature_exterieure_effective` | sensor (°C) | nombre, ou indisponible | Température extérieure réellement utilisée par les règles (maximum entre la mesure et la température ressentie si l'option est activée). |

### Entités par volet

| Entité | Type | Description |
|---|---|---|
| `switch.volets_<nom>_auto` | switch | Gestion automatique du volet : `on` = géré, `off` = ignoré par l'intégration. Remplace les `input_boolean.auto_volet_*`. |
| `sensor.volets_<nom>_statut` | sensor (énumération) | Statut du volet (voir ci-dessous). L'explication en français et les autres informations sont dans les attributs. |

Valeurs du statut (`sensor.volets_<nom>_statut`) :

| Valeur | Affichage | Sens |
|---|---|---|
| `shaded` | Protégé du soleil | Le volet a été abaissé par l'intégration. |
| `watching` | Surveillance | Rien à faire pour le moment. |
| `paused` | En pause | Action manuelle détectée, ou pause demandée. |
| `window_open` | Fenêtre ouverte | Fermeture bloquée (ou capteur de fenêtre indisponible). |
| `wind_protected` | Protégé du vent | Mis en sécurité à cause du vent. |
| `cooldown` | Anti-usure | Attente de l'intervalle minimal entre deux mouvements. |
| `outside_window` | Hors plage | En dehors de la plage active. |
| `grace` | Démarrage | Délai de sécurité après un redémarrage. |
| `no_data` | Données manquantes | Température extérieure ou exposition indisponible : aucune action. |
| `mode_manual` | Mode manuel | Le mode global est « manuel ». |
| `mode_off` | Arrêté | Le mode global est « arrêté ». |
| `scenario_off` | Scénario désactivé | Le scénario actif ne commande aucun volet. |
| `disabled` | Désactivé | Volet non géré (interrupteur sur `off`). |
| `unavailable` | Indisponible | L'entité volet est indisponible. |

Attributs de `sensor.volets_<nom>_statut` :

| Attribut | Contenu |
|---|---|
| `reason` | Phrase en français qui explique la situation (par exemple « Soleil sur la façade Est et 27,4 °C dehors »). |
| `cover` | Entité du volet piloté (par exemple `cover.calyps_home_volet_bureau`). |
| `position` | Position actuelle en pourcentage, ou vide si le volet n'en rapporte pas. |
| `room_temp` | Température de la pièce utilisée, ou vide. |
| `exposed` | `true` si la façade reçoit le soleil (météo comprise), `false` sinon, vide si l'information est indisponible. |
| `paused_until` | Date et heure de fin de pause, ou vide. |
| `shaded_by_us` | `true` si l'intégration a abaissé le volet. |
| `last_action` | Dernière action de l'intégration : `close` ou `open`. |
| `last_action_at` | Date et heure de cette action. |
| `window_state` | État des capteurs d'ouverture du volet : `open`, `closed`, `unknown` (capteur indisponible), vide si aucun capteur. Une seule fenêtre ouverte suffit pour `open`. |

Les entités d'un volet apparaissent ou disparaissent quand vous ajoutez ou retirez le volet dans le panneau.

**Onglet « Entités » du panneau.** Il liste les identifiants réels des entités de votre installation (lus dans
Home Assistant, donc exacts même si vous les avez renommées), avec un bouton « Copier » par identifiant, la
liste des valeurs possibles et des exemples de cartes YAML déjà remplis avec vos identifiants.

### Exemples prêts à copier

Pilotage global (à adapter si vos identifiants diffèrent) :

```yaml
type: entities
title: Volets intelligents
entities:
  - entity: select.volets_mode
    name: Mode
  - entity: select.volets_scenario
    name: Scénario
  - entity: sensor.volets_temperature_exterieure_effective
    name: Température extérieure utilisée
```

Un volet avec son interrupteur, son statut et l'explication :

```yaml
type: entities
title: Bureau
entities:
  - entity: cover.calyps_home_volet_bureau
  - entity: switch.volets_bureau_auto
    name: Gestion automatique
  - entity: sensor.volets_bureau_statut
    name: Statut
  - type: attribute
    entity: sensor.volets_bureau_statut
    attribute: reason
    name: Pourquoi
```

Explication de plusieurs volets dans une carte Markdown :

```yaml
type: markdown
title: Volets, pourquoi ?
content: >
  **Bureau** : {{ state_attr('sensor.volets_bureau_statut', 'reason') }}

  **Salon** : {{ state_attr('sensor.volets_salon_statut', 'reason') }}
```

Compter les volets actuellement abaissés par l'intégration (un modèle prêt à coller dans une carte Markdown ou
dans un capteur modèle) :

```yaml
{{ states.sensor
   | selectattr('attributes.volets_intelligents', 'defined')
   | selectattr('state', 'eq', 'shaded')
   | list | count }}
```

Tous les capteurs de statut portent l'attribut `volets_intelligents: true`, ce qui permet de les retrouver
sans lister leurs noms, par exemple avec la carte `auto-entities` :

```yaml
type: custom:auto-entities
card:
  type: entities
  title: Statut des volets
filter:
  include:
    - domain: sensor
      attributes:
        volets_intelligents: true
```

### Services

| Service | Champs | Effet |
|---|---|---|
| `volets_intelligents.pause` | `entity_id` (volets, tous si vide), `minutes` (durée des réglages si vide) | Met des volets en pause. |
| `volets_intelligents.resume` | `entity_id` (tous si vide) | Reprend la gestion automatique. |
| `volets_intelligents.evaluate` | aucun | Force une évaluation immédiate. |

```yaml
type: button
name: Pause 2 h, salon
tap_action:
  action: perform-action
  perform_action: volets_intelligents.pause
  data:
    entity_id: cover.calyps_home_volet_canape
    minutes: 120
```

## Carte Lovelace

La carte est chargée automatiquement. Ajoutez-la depuis l'éditeur de tableau de bord
(« Volets Intelligents ») ou en YAML :

```yaml
type: custom:volets-intelligents-card
title: Volets
```

## Droits des utilisateurs

Les droits suivent ceux de Home Assistant : le panneau de gestion est réservé aux administrateurs. La
carte Lovelace est visible de tous, mais changer le mode ou le scénario, mettre en pause ou reprendre
un volet demande le droit de contrôle sur l'entité correspondante (`select.volets_mode`,
`select.volets_scenario`, le volet lui-même), comme pour n'importe quel appel de service.

## Plage active

La plage active va d'une heure de début à une heure de fin (fixe, lue dans une entité, ou relative
au coucher du soleil). Si la fin est avant le début, la plage passe minuit (ex. 20:00 → 02:00).
Si l'entité de fin est indisponible, l'heure de fin fixe sert de repli.

## Inspirations et différences

Le projet reprend la logique de l'automatisation « VOLETS : Thermique » de son auteur (exposition
prévue par orientation, températures par pièce, seuils, plage jusqu'à l'heure de remontée) et
s'inspire des idées du projet [CoverAutomatic](https://github.com/crandler/CoverAutomatic)
(hystérésis, pause après action manuelle, fenêtre ouverte, vent, délai de démarrage, scénarios).
Aucun code n'a été copié.

## Limites connues

- Les statuts `shaded` et les pauses se basent sur la position rapportée par le volet. Un volet
  qui ne rapporte aucune position est géré en tout ou rien.
- Avec le mode « bouton » (position favorite), la position atteinte peut différer de la position de
  protection réglée : l'intégration reconnaît quand même un volet qu'elle a abaissé et le remonte ensuite.
- Un mouvement venant d'une autre automatisation (alarme, fermeture du soir) pendant la plage active
  est traité comme une action manuelle et met le volet en pause.

## Développement

```bash
pip install pytest-homeassistant-custom-component ruff
ruff check . && pytest
```

Le moteur de décision (`engine.py`) et la validation (`schema.py`) n'importent pas Home Assistant
et se testent seuls. Le frontend (`frontend/`) est en JavaScript pur, sans étape de build.
Le contrat de données entre frontend et backend est décrit dans `docs/API.md`.

Les plages d'ensoleillement affichées sont théoriques (géométrie seule, sans météo).

Licence MIT.
