/*
 * Volets Intelligents — panneau d'administration (custom element
 * `volets-intelligents-panel`).
 *
 * Contrat de données : docs/API.md. JavaScript pur, module ES, sans
 * dépendance. Aucune donnée dynamique n'est insérée via innerHTML : le DOM est
 * construit avec createElement/textContent (voir `el`).
 */

const WS = "volets_intelligents/";

/* ------------------------------------------------------------------ */
/* Traductions (fr complet, en complet ; langue = hass.language, repli fr) */
/* ------------------------------------------------------------------ */

const I18N = {
  fr: {
    "app.title": "Volets Intelligents",
    "menu.open": "Ouvrir le menu latéral",
    "tabs.aria": "Sections",
    "tab.dashboard": "Tableau de bord",
    "tab.covers": "Volets",
    "tab.facades": "Façades",
    "tab.scenarios": "Scénarios",
    "tab.settings": "Réglages",
    "tab.entities": "Entités",
    "ent.intro": "Les identifiants réels des entités créées par l'intégration, à utiliser dans vos tableaux de bord, automatisations et modèles.",
    "ent.loading": "Chargement des entités…",
    "ent.error": "Impossible de lire les entités : {error}",
    "ent.global": "Entités globales",
    "ent.mode": "Mode global",
    "ent.scenario": "Scénario actif",
    "ent.outdoor": "Température extérieure utilisée",
    "ent.perCover": "Entités par volet",
    "ent.switch": "Gestion automatique",
    "ent.status": "Statut",
    "ent.missing": "non créée",
    "ent.noCovers": "Aucun volet configuré : aucune entité par volet.",
    "ent.copy": "Copier",
    "ent.copied": "Copié dans le presse-papiers.",
    "ent.copyFailed": "Copie automatique impossible : sélectionnez le texte et copiez-le manuellement.",
    "ent.copyId": "Copier l'identifiant {id}",
    "ent.values": "Valeurs possibles",
    "ent.valuesStatus": "Statut d'un volet",
    "ent.valuesMode": "Mode global",
    "ent.valuesScenario": "Scénario",
    "ent.attrs": "Attributs du capteur de statut",
    "ent.attr.reason": "phrase en français qui explique la situation",
    "ent.attr.cover": "entité du volet piloté",
    "ent.attr.position": "position actuelle en pourcentage",
    "ent.attr.room_temp": "température de la pièce utilisée",
    "ent.attr.exposed": "la façade reçoit le soleil (vrai ou faux, vide si inconnu)",
    "ent.attr.paused_until": "fin de la pause, si en pause",
    "ent.attr.shaded_by_us": "vrai si l'intégration a abaissé le volet",
    "ent.attr.last_action": "dernière action : close ou open",
    "ent.attr.last_action_at": "date et heure de cette action",
    "ent.attr.window_state": "fenêtres : open, closed ou unknown (vide si aucun capteur)",
    "ent.examples": "Exemples avec vos identifiants",
    "ent.exGlobal": "Pilotage global",
    "ent.exCovers": "Tous les volets, par façade",
    "ent.exReasons": "Pourquoi chaque volet est dans son état",
    "ent.windowRow": "Fenêtre",
    "ent.thresholds": "Seuils des scénarios",
    "ent.thresholdsHelp": "Réglages modifiables depuis un tableau de bord : seuils de température de l'été (protection contre la chaleur) et de l'hiver (gain solaire).",
    "ent.th.summer.close_outdoor": "Été : fermeture si extérieur ≥",
    "ent.th.summer.close_room": "Été : fermeture si pièce ≥",
    "ent.th.summer.open_outdoor": "Été : réouverture si extérieur ≤",
    "ent.th.summer.open_room": "Été : réouverture si pièce ≤",
    "ent.th.winter.gain_outdoor_below": "Hiver : gain solaire si extérieur <",
    "ent.th.winter.gain_room_below": "Hiver : gain solaire si pièce <",
    "ent.reasonRow": "Pourquoi",
    "ent.window": "Plage active",
    "ent.windowActive": "Plage active en ce moment",
    "ent.windowStart": "Début de la plage (lecture)",
    "ent.windowEnd": "Fin de la plage (lecture)",
    "ent.windowStartSetting": "Réglage : heure de début",
    "ent.windowEndSetting": "Réglage : heure de fin (fixe ou repli)",
    "ent.windowEndMode": "Réglage : mode de fin",
    "ent.windowSunset": "Réglage : décalage coucher du soleil (min)",
    "ent.windowHelp": "Les entités « Réglage » sont modifiables depuis un tableau de bord. L'entité qui donne la fin de plage se choisit dans le panneau (Réglages).",
    "ent.endMode.fixed": "Heure fixe",
    "ent.endMode.entity": "Lue dans une entité",
    "ent.endMode.sunset": "Coucher du soleil",
    "ent.facades": "Façades : exposition et horaires",
    "ent.facadeExposed": "Exposée au soleil",
    "ent.facadeStart": "Début de la plage d'ensoleillement",
    "ent.facadeEnd": "Fin de la plage d'ensoleillement",
    "ent.facadeHelp": "Début et fin concernent la plage d'ensoleillement en cours, sinon la prochaine du jour (vide quand il n'y en a plus). Toutes les plages du jour sont dans l'attribut windows.",
    "ent.exWindow": "Plage active (lecture et réglage)",
    "ent.exFacades": "Façades : exposition et horaires",
    "ent.on": "oui",
    "ent.off": "non",

    "common.retry": "Réessayer",
    "common.add": "Ajouter",
    "common.cancel": "Annuler",
    "common.save": "Enregistrer",
    "common.saving": "Enregistrement…",
    "common.delete": "Supprimer",
    "common.confirmDelete": "Confirmer la suppression",
    "common.up": "↑ Monter",
    "common.down": "↓ Descendre",
    "common.remove": "Retirer {id}",
    "common.loading": "Chargement de la configuration…",

    "err.notInstalled": "L'intégration « Volets Intelligents » n'est pas installée ou n'est pas démarrée.",
    "err.unknown": "Erreur inconnue.",
    "err.unauthorized": "Vous n'avez pas le droit d'effectuer cette action",
    "err.configUnavailable": "Configuration indisponible",
    "err.configNotLoaded": "La configuration n'a pas pu être chargée.",
    "err.statusUnavailable": "Statut indisponible",
    "err.subInterrupted": "Abonnement interrompu : {error}",
    "err.command": "Commande impossible : {error}",
    "err.save": "Échec de l'enregistrement : {error}",

    "mode.auto": "Automatique",
    "mode.manual": "Manuel",
    "mode.off": "Arrêt",
    "mode.auto.desc": "Le moteur décide et envoie les ordres aux volets : fermeture et réouverture selon le scénario, l'exposition au soleil et les températures.",
    "mode.manual.desc": "Aucun ordre n'est envoyé : vous pilotez les volets vous-même. Les volets affichent « Mode manuel » ; la sécurité vent reste prioritaire.",
    "mode.off.desc": "Gestion arrêtée : aucune décision n'est prise ni aucun ordre envoyé. Seule la sécurité vent reste prioritaire.",
    "scenario.summer": "Été",
    "scenario.winter": "Hiver",
    "scenario.vacation": "Vacances",
    "scenario.off": "Désactivé",
    "scenario.summer.desc": "Protection contre la chaleur : ferme les volets exposés au soleil quand il fait chaud, les rouvre quand la chaleur retombe.",
    "scenario.winter.desc": "Gain solaire : rouvre un volet fermé et ensoleillé quand la pièce et l'extérieur sont frais. Ne ferme jamais.",
    "scenario.vacation.desc": "Absence : ferme les volets dès qu'ils sont exposés au soleil, sans condition de température, et les remonte quand le soleil part.",
    "scenario.off.desc": "Aucune action liée au soleil ni aux températures.",
    "kind.heat_protection": "Protection contre la chaleur",
    "kind.solar_gain": "Apport solaire",
    "kind.hold_shaded": "Maintien à l'ombre",
    "kind.off": "Désactivé",

    "status.disabled": "Désactivé",
    "status.mode_manual": "Mode manuel",
    "status.mode_off": "Arrêté",
    "status.scenario_off": "Scénario désactivé",
    "status.grace": "Démarrage",
    "status.outside_window": "Hors plage",
    "status.no_data": "Données manquantes",
    "status.paused": "En pause",
    "status.window_open": "Fenêtre ouverte",
    "status.wind_protected": "Protégé du vent",
    "status.shaded": "Protégé du soleil",
    "status.watching": "Surveillance",
    "status.cooldown": "Anti-usure",
    "status.unavailable": "Indisponible",

    "orient.north": "Nord",
    "orient.east": "Est",
    "orient.south": "Sud",
    "orient.west": "Ouest",
    "orient.custom": "Personnalisée",
    "method.position": "Aller à une position",
    "method.button": "Appuyer sur un bouton",
    "method.close": "Fermer complètement",

    "cond.sunny": "Ensoleillé",
    "cond.partlycloudy": "Partiellement nuageux",
    "cond.cloudy": "Nuageux",
    "cond.clear-night": "Nuit dégagée",
    "cond.fog": "Brouillard",
    "cond.rainy": "Pluie",
    "cond.pouring": "Pluie battante",
    "cond.lightning": "Orage",
    "cond.lightning-rainy": "Orage et pluie",
    "cond.hail": "Grêle",
    "cond.snowy": "Neige",
    "cond.snowy-rainy": "Neige fondue",
    "cond.windy": "Venteux",
    "cond.windy-variant": "Venteux et nuageux",
    "cond.exceptional": "Exceptionnel",

    "dash.connecting": "Connexion au statut en cours…",
    "dash.control": "Pilotage",
    "dash.globalMode": "Mode global",
    "dash.scenario": "Scénario",
    "dash.evaluate": "Évaluer maintenant",
    "dash.evaluateDone": "Évaluation lancée.",
    "dash.pauseAll": "Tout mettre en pause",
    "dash.pauseAllDone": "Tous les volets sont en pause.",
    "dash.resumeAll": "Tout reprendre",
    "dash.resumeAllDone": "Reprise de tous les volets.",
    "dash.conditions": "Conditions",
    "dash.outdoor": "Température extérieure effective",
    "dash.rawTemp": "Mesure brute : {value}",
    "dash.wind": "Vent",
    "dash.noMeasure": "Aucune mesure",
    "dash.windExceeded": "Seuil dépassé",
    "dash.windOk": "Sous le seuil",
    "dash.weather": "Météo",
    "dash.sunCounts": "Soleil pris en compte",
    "dash.sunIgnored": "Soleil neutralisé",
    "dash.sunCountsSub": "Condition météo ensoleillée",
    "dash.sunIgnoredSub": "La météo neutralise le soleil",
    "dash.sun": "Position du soleil",
    "dash.sunValue": "Azimut {az} · hauteur {el}",
    "dash.sunBelow": "Le soleil est sous l'horizon",
    "dash.sunAbove": "Orientation de la maison : {deg}",
    "dash.window": "Plage active",
    "dash.inWindow": "Dans la plage",
    "dash.outWindow": "Hors plage",
    "dash.grace": "Délai de démarrage en cours",
    "dash.facades": "Façades",
    "dash.noFacades": "Aucune façade.",
    "dash.covers": "Volets ({n})",
    "dash.noCovers": "Aucun volet configuré.",
    "dash.byFacade": "Par façade",
    "dash.flatList": "Liste unique",
    "dash.view": "Affichage des volets",
    "dash.noFacadeGroup": "Sans façade",
    "dash.moveUp": "Monter {name}",
    "dash.moveDown": "Descendre {name}",
    "dash.drag": "Glisser pour déplacer {name}",
    "dash.orderHint": "Utilisez les flèches (ou glissez la poignée sur ordinateur) pour changer l'ordre. L'ordre est enregistré tout de suite.",
    "dash.orderSaved": "Ordre des volets enregistré.",
    "dash.window.open": "Fenêtre ouverte",
    "dash.window.closed": "Fenêtre fermée",
    "dash.window.unknown": "Capteur de fenêtre indisponible",
    "err.reorder": "Impossible d'enregistrer l'ordre : {error}",
    "dash.position": "Position : {value}",
    "dash.room": "Pièce : {value}",
    "dash.pausedUntil": "Pause jusqu'à {time}",
    "dash.pause": "Pause",
    "dash.resume": "Reprendre",
    "dash.pauseAria": "Mettre en pause {name}",
    "dash.auto": "Auto",
    "dash.autoAria": "Gestion automatique de {name}",
    "dash.resumeAria": "Reprendre {name}",

    "fcard.exposed": "Exposée",
    "fcard.notExposed": "Non exposée",
    "fcard.unknown": "Exposition inconnue",
    "fcard.azimuth": "Azimut {deg}",
    "fcard.sun": "Plages d'ensoleillement : {windows}",
    "fcard.sourceEntity": "via un capteur",
    "fcard.coversOne": "{n} volet affecté",
    "fcard.coversOther": "{n} volets affectés",

    "start.title": "Premiers pas",
    "start.intro": "Aucun volet n'est encore configuré. Suivez ces trois étapes pour démarrer.",
    "start.s1": "Orientation de la maison",
    "start.s1d": "Indiquez vers où regarde la façade que vous appelez « Sud ».",
    "start.s2": "Capteur de température extérieure",
    "start.s2d": "Choisissez le capteur qui mesure la température dehors.",
    "start.s3": "Ajouter vos volets",
    "start.s3d": "Sélectionnez vos volets et affectez-les à une façade.",
    "start.open": "Ouvrir",
    "start.done": "Déjà renseigné",

    "bar.dirty": "Modifications non enregistrées",
    "flash.saved": "Configuration enregistrée.",
    "flash.imported": "Configuration importée dans le brouillon. Cliquez sur « Enregistrer » pour l'appliquer.",

    "covers.add": "Ajouter un volet",
    "covers.needFacade": "Créez d'abord une façade (onglet « Façades ») pour pouvoir ajouter des volets.",
    "covers.empty": "Aucun volet. Ajoutez-en un pour commencer.",
    "covers.new": "Nouveau volet",
    "covers.disabled": "Désactivé",
    "covers.entity": "Entité volet",
    "covers.name": "Nom",
    "covers.namePlaceholder": "Volet salon",
    "covers.facade": "Façade",
    "covers.facadeHelp": "Le côté de la maison où se trouve ce volet : il se ferme quand cette façade est exposée au soleil.",
    "covers.enabled": "Volet géré (activé)",
    "covers.closeMethod": "Méthode de fermeture",
    "covers.buttonEntity": "Entité bouton (fermeture)",
    "covers.closePosition": "Position de fermeture (protégé)",
    "covers.openPosition": "Position d'ouverture",
    "covers.roomTemp": "Température de la pièce",
    "covers.windows": "Fenêtres / portes (capteurs d'ouverture)",
    "covers.windowSensor": "capteur d'ouverture",
    "covers.addWindow": "Ajouter : {label}",
    "covers.blockClose": "Ne pas fermer si une fenêtre est ouverte",
    "covers.allowOpenClosed": "Autoriser à remonter un volet fermé à 100 %",
    "covers.allowOpenClosedHelp": "Par défaut, un volet fermé à 100 % n'est jamais remonté par l'intégration, quelle que soit la façon dont il a été fermé. Activez un scénario pour lever cette règle dans ce scénario seulement.",
    "covers.windSensitive": "Sensible au vent (mise en sécurité si vent fort)",
    "covers.windAction": "Action de mise en sécurité par vent fort",
    "covers.windActionHelp": "Ce que fait cet équipement quand le vent dépasse le seuil : un volet se remonte, un store ou une banne se rentre.",
    "covers.windOpen": "Remonter le volet (ouvrir)",
    "covers.windClose": "Rentrer le store ou la banne (fermer)",

    "bulk.title": "Ajout groupé de volets",
    "bulk.help": "Cochez plusieurs volets Home Assistant et affectez-les d'un coup à une façade.",
    "bulk.facade": "Façade de destination",
    "bulk.search": "Rechercher un volet…",
    "bulk.searchAria": "Rechercher parmi les volets disponibles",
    "bulk.none": "Aucun volet disponible (tous sont déjà ajoutés ou ne correspondent pas à la recherche).",
    "bulk.add": "Ajouter la sélection ({n})",

    "facades.add": "Ajouter une façade",
    "facades.empty": "Aucune façade. Ajoutez-en une pour pouvoir affecter des volets.",
    "facades.intro": "Une façade regroupe les volets d'un même côté de la maison. Son orientation détermine quand le soleil l'éclaire.",
    "facade.newName": "Nouvelle façade",
    "facade.id": "Identifiant (généré depuis le nom)",
    "facade.idHelp": "Lettres minuscules, chiffres et _ uniquement.",
    "facade.idRequired": "L'identifiant est obligatoire.",
    "facade.idDuplicate": "Cet identifiant est déjà utilisé.",
    "facade.name": "Nom",
    "facade.orientation": "Orientation",
    "facade.orientationHelp": "Côté de la maison concerné. Les côtés tournent avec l'orientation de la maison (onglet « Réglages »).",
    "facade.customAzimuth": "Azimut personnalisé (°)",
    "facade.customAzimuthHelp": "Direction absolue de la boussole : 0 = nord, 90 = est, 180 = sud, 270 = ouest. Non modifiée par l'orientation de la maison.",
    "facade.mode": "Mode d'exposition",
    "facade.modeSun": "Position du soleil (recommandé)",
    "facade.modeEntity": "Capteur existant",
    "facade.modeHelp": "Position du soleil : calcul automatique selon la date, l'heure et la position GPS de Home Assistant.",
    "facade.entity": "Capteur d'exposition",
    "facade.entityHelp": "binary_sensor, input_boolean ou switch. L'état « on » signifie que la façade est exposée.",
    "facade.halfAngle": "Angle d'éclairage",
    "facade.halfAngleHelp": "Angle d'éclairage autour de la façade : le soleil éclaire la façade s'il est à moins de cet angle de sa perpendiculaire. 80° convient à la plupart des cas.",
    "facade.elevationMin": "Hauteur minimale du soleil (°)",
    "facade.elevationMinHelp": "Masque d'horizon : arbres, voisins, relief. Sous cette hauteur, le soleil est ignoré.",
    "facade.defaultClose": "Position de fermeture par défaut",
    "facade.defaultCloseHelp": "Proposée à l'ajout d'un volet sur cette façade.",
    "facade.effAzimuth": "Azimut effectif",
    "facade.preview": "calculé, non enregistré",
    "facade.sunWindows": "Plages d'ensoleillement du jour",
    "facade.noSun": "Pas de soleil direct aujourd'hui",
    "facade.windowsEntity": "Non calculées : l'exposition vient d'un capteur.",
    "facade.windowsPending": "Disponibles après l'enregistrement.",
    "facade.inUse": "Impossible de supprimer cette façade : elle est utilisée par {names}.",
    "facade.reassignTo": "Réaffecter à",
    "facade.reassignDelete": "Réaffecter les volets et supprimer",
    "facade.noOtherFacade": "Affectez d'abord ces volets à une autre façade, ou créez-en une.",
    "facade.sourceSun": "position du soleil",
    "facade.sourceEntity": "capteur",

    "scn.label": "Libellé",
    "scn.kind": "Type (lecture seule)",
    "scn.code": "Code : {kind}",
    "scn.noThresholds": "Ce scénario n'a pas de seuils : seul son libellé est modifiable.",
    "scn.closeOutdoor": "Fermeture : température extérieure (°C)",
    "scn.closeRoom": "Fermeture : température de la pièce (°C)",
    "scn.openOutdoor": "Réouverture : température extérieure (°C)",
    "scn.openRoom": "Réouverture : température de la pièce (°C)",
    "scn.release": "Condition de réouverture",
    "scn.releaseRoom": "Pièce seulement",
    "scn.releaseOutdoor": "Extérieur seulement",
    "scn.alarmTitle": "Alarme",
    "scn.blockAlarm": "Ne pas ouvrir les volets quand l'alarme est activée",
    "scn.blockAlarmHelp": "Aucune ouverture automatique tant que l'alarme est armée (états armed_*) ou déclenchée. Il faut choisir l'entité d'alarme dans Réglages.",
    "scn.blockAlarmWindow": "Ne pas ouvrir les volets quand l'alarme est activée ET qu'une fenêtre est ouverte",
    "scn.blockAlarmWindowHelp": "Comme ci-dessus, mais seulement pour un volet dont une fenêtre ou porte est ouverte (ou son capteur indisponible). Inutile si la case précédente est cochée.",
    "set.alarmEntity": "Alarme (alarm_control_panel)",
    "set.alarmEntityHelp": "Utilisée par les options « Ne pas ouvrir quand l'alarme est activée » des scénarios. Sans entité, ou si elle est indisponible, rien n'est bloqué.",
    "scn.releaseAll": "Pièce ET extérieur (all)",
    "scn.releaseAny": "Pièce OU extérieur (any)",
    "scn.releaseHelp": "all : le volet ne se rouvre que lorsque l'extérieur ET la pièce sont redescendus sous leurs seuils de réouverture. any : il se rouvre dès que l'un des deux (extérieur OU pièce) est redescendu sous son seuil. Pièce seulement ou extérieur seulement : un seul seuil compte, l'autre est ignoré.",
    "scn.gainRoom": "Pièce : en dessous de (°C)",
    "scn.gainOutdoor": "Extérieur : en dessous de (°C)",
    "scn.gainCondition": "Condition d'ouverture",
    "scn.gainBoth": "Pièce ET extérieur",
    "scn.gainAny": "Pièce OU extérieur",
    "scn.gainMinEnabled": "Limite extérieure basse : ne plus ouvrir en dessous",
    "scn.gainMinHelp": "Quand la température extérieure est inférieure ou égale à cette limite (peut être négative), le volet n'est plus ouvert, même si le soleil et les autres conditions sont réunis.",
    "scn.gainMin": "Limite extérieure (°C)",
    "scn.gainRoomOnly": "Pièce seulement",
    "scn.gainOutdoorOnly": "Extérieur seulement",
    "scn.gainConditionHelp": "Pièce ET extérieur : le volet s'ouvre quand la pièce et l'extérieur sont sous leurs seuils. Pièce OU extérieur : un seul des deux suffit. Pièce seulement ou extérieur seulement : un seul seuil compte, l'autre est ignoré.",

    "set.house": "Maison",
    "set.houseOrientation": "Orientation de la maison (°)",
    "set.houseHelp": "Vers quel point cardinal regarde la façade que vous appelez « Sud » (azimut de boussole : 0 = nord, 90 = est, 180 = sud, 270 = ouest). 180 : maison alignée sur les points cardinaux. 135 : façade principale orientée au sud-est. Toutes les façades tournent avec la maison.",
    "compass.aria": "Plan de la maison, façade « Sud » orientée à {deg}°",
    "compass.n": "N",
    "compass.e": "E",
    "compass.s": "S",
    "compass.w": "O",
    "set.sensors": "Capteurs et météo",
    "set.outdoor": "Température extérieure",
    "set.feels": "Température ressentie",
    "set.useMax": "Utiliser le maximum mesure / ressentie",
    "set.useMaxHelp": "La température extérieure effective est le maximum des deux.",
    "set.weather": "Entité météo",
    "set.windEntity": "Capteur de vent",
    "set.windThreshold": "Seuil de vent",
    "set.windThresholdHelp": "Même unité que le capteur de vent.",
    "set.windRatio": "Ratio de relâche du vent",
    "set.windRatioHelp": "Entre 0,1 et 1. Le vent est considéré comme retombé quand il passe sous seuil × ratio.",
    "set.sunny": "Conditions météo où le soleil compte",
    "set.sunnyHelp": "Aucune condition cochée = filtre météo désactivé.",
    "set.eval": "Évaluation et anti-usure",
    "set.interval": "Intervalle d'évaluation (minutes)",
    "set.grace": "Délai après démarrage (secondes)",
    "set.minMove": "Intervalle minimal entre deux mouvements (minutes)",
    "set.minMoveHelp": "Protège les moteurs contre l'usure.",
    "set.tolerance": "Tolérance de position (%)",
    "set.overridePause": "Durée de pause après action manuelle (minutes)",
    "set.overrideWindow": "Pause jusqu'à la fin de la plage active",
    "set.overrideWindowHelp": "Remplace la durée ci-contre quand une action manuelle est détectée.",
    "set.window": "Plage active",
    "set.windowStart": "Début",
    "set.windowEndMode": "Fin de plage",
    "set.endEntity": "Selon une entité",
    "set.endFixed": "Heure fixe",
    "set.endSunset": "Coucher du soleil",
    "set.endTime": "Heure de fin",
    "set.endEntityField": "Entité heure de fin",
    "set.endEntityHelp": "L'état doit être une heure « HH:MM », « HH:MM:SS » ou une date ISO.",
    "set.windowStartHelp": "Si l'heure de fin est avant l'heure de début, la plage passe minuit (ex. 20:00 → 02:00).",
    "set.windowEndHelp": "Si l'heure de fin est avant l'heure de début, la plage passe minuit (ex. 20:00 → 02:00).",
    "set.windowEndEntityHelp": " Formats lus depuis l'entité : HH:MM, HH:MM:SS ou date ISO.",
    "set.sunsetOffset": "Décalage par rapport au coucher du soleil (minutes)",
    "set.sunsetOffsetHelp": "Valeur négative = avant le coucher du soleil.",
    "set.auto": "Scénario automatique",
    "set.autoEnabled": "Choisir été / hiver selon le mois",
    "set.summerMonths": "Mois d'été",
    "set.summerMonthsHelp": "Les autres mois utilisent le scénario d'hiver.",

    "backup.title": "Sauvegarde et import",
    "backup.help": "L'import remplace le brouillon sans rien envoyer au serveur : cliquez ensuite sur « Enregistrer » pour l'appliquer.",
    "backup.area": "Configuration au format JSON",
    "backup.placeholder": "Cliquez sur « Exporter », ou collez ici une configuration JSON à importer.",
    "backup.export": "Exporter",
    "backup.copy": "Copier",
    "backup.import": "Importer",
    "backup.exported": "Configuration courante exportée dans la zone de texte.",
    "backup.copied": "Texte copié dans le presse-papiers.",
    "backup.copyFailed": "Copie automatique impossible : le texte est sélectionné, copiez-le manuellement.",
    "backup.invalidJson": "JSON invalide : {error}",
    "backup.notObject": "Le JSON doit être un objet de configuration (et non une liste ou une valeur simple).",
    "backup.incomplete": "Configuration incomplète : les clés « settings », « scenarios », « facades » et « covers » sont requises.",

    "input.unknownValue": "{value} (valeur inconnue)",
  },

  en: {
    "app.title": "Volets Intelligents",
    "menu.open": "Open the sidebar",
    "tabs.aria": "Sections",
    "tab.dashboard": "Dashboard",
    "tab.covers": "Shutters",
    "tab.facades": "Facades",
    "tab.scenarios": "Scenarios",
    "tab.settings": "Settings",
    "tab.entities": "Entities",
    "ent.intro": "The actual identifiers of the entities created by the integration, to use in your dashboards, automations and templates.",
    "ent.loading": "Loading entities…",
    "ent.error": "Could not read the entities: {error}",
    "ent.global": "Global entities",
    "ent.mode": "Global mode",
    "ent.scenario": "Active scenario",
    "ent.outdoor": "Outdoor temperature used",
    "ent.perCover": "Entities per shutter",
    "ent.switch": "Automatic management",
    "ent.status": "Status",
    "ent.missing": "not created",
    "ent.noCovers": "No shutter configured: no per-shutter entity.",
    "ent.copy": "Copy",
    "ent.copied": "Copied to the clipboard.",
    "ent.copyFailed": "Automatic copy failed: select the text and copy it manually.",
    "ent.copyId": "Copy identifier {id}",
    "ent.values": "Possible values",
    "ent.valuesStatus": "Shutter status",
    "ent.valuesMode": "Global mode",
    "ent.valuesScenario": "Scenario",
    "ent.attrs": "Status sensor attributes",
    "ent.attr.reason": "plain-language sentence explaining the situation",
    "ent.attr.cover": "the controlled shutter entity",
    "ent.attr.position": "current position in percent",
    "ent.attr.room_temp": "room temperature used",
    "ent.attr.exposed": "the facade receives sun (true or false, empty if unknown)",
    "ent.attr.paused_until": "end of the pause, if paused",
    "ent.attr.shaded_by_us": "true if the integration lowered the shutter",
    "ent.attr.last_action": "last action: close or open",
    "ent.attr.last_action_at": "date and time of that action",
    "ent.attr.window_state": "windows: open, closed or unknown (empty if no sensor)",
    "ent.examples": "Examples with your identifiers",
    "ent.exGlobal": "Global control",
    "ent.exCovers": "All shutters, by facade",
    "ent.exReasons": "Why each shutter is in its state",
    "ent.windowRow": "Window",
    "ent.thresholds": "Scenario thresholds",
    "ent.thresholdsHelp": "Settings that can be changed from a dashboard: summer (heat protection) and winter (solar gain) temperature thresholds.",
    "ent.th.summer.close_outdoor": "Summer: close if outdoor ≥",
    "ent.th.summer.close_room": "Summer: close if room ≥",
    "ent.th.summer.open_outdoor": "Summer: reopen if outdoor ≤",
    "ent.th.summer.open_room": "Summer: reopen if room ≤",
    "ent.th.winter.gain_outdoor_below": "Winter: solar gain if outdoor <",
    "ent.th.winter.gain_room_below": "Winter: solar gain if room <",
    "ent.reasonRow": "Why",
    "ent.window": "Active window",
    "ent.windowActive": "Active window right now",
    "ent.windowStart": "Window start (read-only)",
    "ent.windowEnd": "Window end (read-only)",
    "ent.windowStartSetting": "Setting: start time",
    "ent.windowEndSetting": "Setting: end time (fixed or fallback)",
    "ent.windowEndMode": "Setting: end mode",
    "ent.windowSunset": "Setting: sunset offset (min)",
    "ent.windowHelp": "The \"Setting\" entities can be changed from a dashboard. The entity that provides the end of the window is chosen in the panel (Settings).",
    "ent.endMode.fixed": "Fixed time",
    "ent.endMode.entity": "Read from an entity",
    "ent.endMode.sunset": "Sunset",
    "ent.facades": "Facades: exposure and times",
    "ent.facadeExposed": "Exposed to the sun",
    "ent.facadeStart": "Start of the sunlight window",
    "ent.facadeEnd": "End of the sunlight window",
    "ent.facadeHelp": "Start and end are for the current sunlight window, otherwise the next one of the day (empty when none is left). All the day's windows are in the windows attribute.",
    "ent.exWindow": "Active window (read and adjust)",
    "ent.exFacades": "Facades: exposure and times",
    "ent.on": "yes",
    "ent.off": "no",

    "common.retry": "Retry",
    "common.add": "Add",
    "common.cancel": "Cancel",
    "common.save": "Save",
    "common.saving": "Saving…",
    "common.delete": "Delete",
    "common.confirmDelete": "Confirm deletion",
    "common.up": "↑ Move up",
    "common.down": "↓ Move down",
    "common.remove": "Remove {id}",
    "common.loading": "Loading configuration…",

    "err.notInstalled": "The “Volets Intelligents” integration is not installed or not running.",
    "err.unknown": "Unknown error.",
    "err.unauthorized": "You are not allowed to perform this action",
    "err.configUnavailable": "Configuration unavailable",
    "err.configNotLoaded": "The configuration could not be loaded.",
    "err.statusUnavailable": "Status unavailable",
    "err.subInterrupted": "Subscription interrupted: {error}",
    "err.command": "Command failed: {error}",
    "err.save": "Could not save: {error}",

    "mode.auto": "Automatic",
    "mode.manual": "Manual",
    "mode.off": "Off",
    "mode.auto.desc": "The engine decides and sends commands to the shutters: closing and reopening according to the scenario, sun exposure and temperatures.",
    "mode.manual.desc": "No command is sent: you operate the shutters yourself. Shutters show Manual mode; wind safety still takes priority.",
    "mode.off.desc": "Management stopped: no decision is made and no command is sent. Only the wind safety still takes priority.",
    "scenario.summer": "Summer",
    "scenario.winter": "Winter",
    "scenario.vacation": "Vacation",
    "scenario.off": "Disabled",
    "scenario.summer.desc": "Heat protection: closes sun-exposed shutters when it is hot and reopens them when the heat drops.",
    "scenario.winter.desc": "Solar gain: reopens a closed, sunny shutter when the room and the outdoors are cool. Never closes.",
    "scenario.vacation.desc": "Away: closes shutters as soon as they are sun-exposed, with no temperature condition, and raises them when the sun leaves.",
    "scenario.off.desc": "No action based on the sun or temperatures.",
    "kind.heat_protection": "Heat protection",
    "kind.solar_gain": "Solar gain",
    "kind.hold_shaded": "Stay shaded",
    "kind.off": "Disabled",

    "status.disabled": "Disabled",
    "status.mode_manual": "Manual mode",
    "status.mode_off": "Stopped",
    "status.scenario_off": "Scenario disabled",
    "status.grace": "Starting up",
    "status.outside_window": "Outside active hours",
    "status.no_data": "Missing data",
    "status.paused": "Paused",
    "status.window_open": "Window open",
    "status.wind_protected": "Wind protection",
    "status.shaded": "Sun protection",
    "status.watching": "Watching",
    "status.cooldown": "Wear protection",
    "status.unavailable": "Unavailable",

    "orient.north": "North",
    "orient.east": "East",
    "orient.south": "South",
    "orient.west": "West",
    "orient.custom": "Custom",
    "method.position": "Go to a position",
    "method.button": "Press a button",
    "method.close": "Close completely",

    "cond.sunny": "Sunny",
    "cond.partlycloudy": "Partly cloudy",
    "cond.cloudy": "Cloudy",
    "cond.clear-night": "Clear night",
    "cond.fog": "Fog",
    "cond.rainy": "Rainy",
    "cond.pouring": "Pouring",
    "cond.lightning": "Thunderstorm",
    "cond.lightning-rainy": "Thunderstorm and rain",
    "cond.hail": "Hail",
    "cond.snowy": "Snowy",
    "cond.snowy-rainy": "Sleet",
    "cond.windy": "Windy",
    "cond.windy-variant": "Windy and cloudy",
    "cond.exceptional": "Exceptional",

    "dash.connecting": "Connecting to the status feed…",
    "dash.control": "Control",
    "dash.globalMode": "Global mode",
    "dash.scenario": "Scenario",
    "dash.evaluate": "Evaluate now",
    "dash.evaluateDone": "Evaluation started.",
    "dash.pauseAll": "Pause all",
    "dash.pauseAllDone": "All shutters are paused.",
    "dash.resumeAll": "Resume all",
    "dash.resumeAllDone": "All shutters resumed.",
    "dash.conditions": "Conditions",
    "dash.outdoor": "Effective outdoor temperature",
    "dash.rawTemp": "Raw reading: {value}",
    "dash.wind": "Wind",
    "dash.noMeasure": "No reading",
    "dash.windExceeded": "Threshold exceeded",
    "dash.windOk": "Below threshold",
    "dash.weather": "Weather",
    "dash.sunCounts": "Sun taken into account",
    "dash.sunIgnored": "Sun ignored",
    "dash.sunCountsSub": "Sunny weather condition",
    "dash.sunIgnoredSub": "The weather cancels the sun",
    "dash.sun": "Sun position",
    "dash.sunValue": "Azimuth {az} · elevation {el}",
    "dash.sunBelow": "The sun is below the horizon",
    "dash.sunAbove": "House orientation: {deg}",
    "dash.window": "Active hours",
    "dash.inWindow": "Within active hours",
    "dash.outWindow": "Outside active hours",
    "dash.grace": "Startup delay in progress",
    "dash.facades": "Facades",
    "dash.noFacades": "No facades.",
    "dash.covers": "Shutters ({n})",
    "dash.noCovers": "No shutters configured.",
    "dash.byFacade": "By facade",
    "dash.flatList": "Single list",
    "dash.view": "Shutter display",
    "dash.noFacadeGroup": "No facade",
    "dash.moveUp": "Move {name} up",
    "dash.moveDown": "Move {name} down",
    "dash.drag": "Drag to move {name}",
    "dash.orderHint": "Use the arrows (or drag the handle on a computer) to change the order. The order is saved immediately.",
    "dash.orderSaved": "Shutter order saved.",
    "dash.window.open": "Window open",
    "dash.window.closed": "Window closed",
    "dash.window.unknown": "Window sensor unavailable",
    "err.reorder": "Could not save the order: {error}",
    "dash.position": "Position: {value}",
    "dash.room": "Room: {value}",
    "dash.pausedUntil": "Paused until {time}",
    "dash.pause": "Pause",
    "dash.resume": "Resume",
    "dash.pauseAria": "Pause {name}",
    "dash.auto": "Auto",
    "dash.autoAria": "Automatic control of {name}",
    "dash.resumeAria": "Resume {name}",

    "fcard.exposed": "Sunlit",
    "fcard.notExposed": "Not sunlit",
    "fcard.unknown": "Exposure unknown",
    "fcard.azimuth": "Azimuth {deg}",
    "fcard.sun": "Sunny periods: {windows}",
    "fcard.sourceEntity": "via a sensor",
    "fcard.coversOne": "{n} shutter assigned",
    "fcard.coversOther": "{n} shutters assigned",

    "start.title": "Getting started",
    "start.intro": "No shutters are configured yet. Follow these three steps to get going.",
    "start.s1": "House orientation",
    "start.s1d": "Tell us which way the facade you call “South” is facing.",
    "start.s2": "Outdoor temperature sensor",
    "start.s2d": "Pick the sensor that measures the outdoor temperature.",
    "start.s3": "Add your shutters",
    "start.s3d": "Select your shutters and assign them to a facade.",
    "start.open": "Open",
    "start.done": "Already set",

    "bar.dirty": "Unsaved changes",
    "flash.saved": "Configuration saved.",
    "flash.imported": "Configuration imported into the draft. Click “Save” to apply it.",

    "covers.add": "Add a shutter",
    "covers.needFacade": "Create a facade first (“Facades” tab) before adding shutters.",
    "covers.empty": "No shutters yet. Add one to get started.",
    "covers.new": "New shutter",
    "covers.disabled": "Disabled",
    "covers.entity": "Shutter entity",
    "covers.name": "Name",
    "covers.namePlaceholder": "Living room shutter",
    "covers.facade": "Facade",
    "covers.facadeHelp": "The side of the house where this shutter is: it closes when this facade is in the sun.",
    "covers.enabled": "Shutter managed (enabled)",
    "covers.closeMethod": "Closing method",
    "covers.buttonEntity": "Button entity (closing)",
    "covers.closePosition": "Closing position (protected)",
    "covers.openPosition": "Opening position",
    "covers.roomTemp": "Room temperature",
    "covers.windows": "Windows / doors (opening sensors)",
    "covers.windowSensor": "opening sensor",
    "covers.addWindow": "Add: {label}",
    "covers.blockClose": "Do not close if a window is open",
    "covers.allowOpenClosed": "Allow raising a shutter that is 100% closed",
    "covers.allowOpenClosedHelp": "By default, a shutter that is 100% closed is never raised by the integration, however it was closed. Turn on a scenario to lift this rule for that scenario only.",
    "covers.windSensitive": "Wind sensitive (safety move in strong wind)",
    "covers.windAction": "Safety action in strong wind",
    "covers.windActionHelp": "What this device does when the wind exceeds the threshold: a shutter is raised, an awning or blind is retracted.",
    "covers.windOpen": "Raise the shutter (open)",
    "covers.windClose": "Retract the awning or blind (close)",

    "bulk.title": "Bulk add shutters",
    "bulk.help": "Tick several Home Assistant covers and assign them to a facade in one go.",
    "bulk.facade": "Destination facade",
    "bulk.search": "Search for a shutter…",
    "bulk.searchAria": "Search among available shutters",
    "bulk.none": "No shutter available (all are already added or none matches the search).",
    "bulk.add": "Add selection ({n})",

    "facades.add": "Add a facade",
    "facades.empty": "No facades. Add one so you can assign shutters.",
    "facades.intro": "A facade groups the shutters on the same side of the house. Its orientation decides when the sun shines on it.",
    "facade.newName": "New facade",
    "facade.id": "Identifier (generated from the name)",
    "facade.idHelp": "Lowercase letters, digits and _ only.",
    "facade.idRequired": "The identifier is required.",
    "facade.idDuplicate": "This identifier is already in use.",
    "facade.name": "Name",
    "facade.orientation": "Orientation",
    "facade.orientationHelp": "Side of the house concerned. Sides rotate with the house orientation (“Settings” tab).",
    "facade.customAzimuth": "Custom azimuth (°)",
    "facade.customAzimuthHelp": "Absolute compass direction: 0 = north, 90 = east, 180 = south, 270 = west. Not rotated by the house orientation.",
    "facade.mode": "Exposure mode",
    "facade.modeSun": "Sun position (recommended)",
    "facade.modeEntity": "Existing sensor",
    "facade.modeHelp": "Sun position: computed automatically from the date, the time and Home Assistant's GPS location.",
    "facade.entity": "Exposure sensor",
    "facade.entityHelp": "binary_sensor, input_boolean or switch. State “on” means the facade is sunlit.",
    "facade.halfAngle": "Illumination angle",
    "facade.halfAngleHelp": "Illumination angle around the facade: the sun lights the facade when it is within this angle of its perpendicular. 80° suits most cases.",
    "facade.elevationMin": "Minimum sun elevation (°)",
    "facade.elevationMinHelp": "Horizon mask: trees, neighbours, terrain. Below this elevation the sun is ignored.",
    "facade.defaultClose": "Default closing position",
    "facade.defaultCloseHelp": "Suggested when adding a shutter to this facade.",
    "facade.effAzimuth": "Effective azimuth",
    "facade.preview": "computed, not saved",
    "facade.sunWindows": "Today's sunny periods",
    "facade.noSun": "No direct sun today",
    "facade.windowsEntity": "Not computed: exposure comes from a sensor.",
    "facade.windowsPending": "Available after saving.",
    "facade.inUse": "This facade cannot be deleted: it is used by {names}.",
    "facade.reassignTo": "Reassign to",
    "facade.reassignDelete": "Reassign shutters and delete",
    "facade.noOtherFacade": "Assign these shutters to another facade first, or create one.",
    "facade.sourceSun": "sun position",
    "facade.sourceEntity": "sensor",

    "scn.label": "Label",
    "scn.kind": "Type (read-only)",
    "scn.code": "Code: {kind}",
    "scn.noThresholds": "This scenario has no thresholds: only its label can be edited.",
    "scn.closeOutdoor": "Closing: outdoor temperature (°C)",
    "scn.closeRoom": "Closing: room temperature (°C)",
    "scn.openOutdoor": "Reopening: outdoor temperature (°C)",
    "scn.openRoom": "Reopening: room temperature (°C)",
    "scn.release": "Reopening condition",
    "scn.releaseRoom": "Room only",
    "scn.releaseOutdoor": "Outdoor only",
    "scn.alarmTitle": "Alarm",
    "scn.blockAlarm": "Do not open shutters while the alarm is armed",
    "scn.blockAlarmHelp": "No automatic opening while the alarm is armed (armed_* states) or triggered. Pick the alarm entity in Settings.",
    "scn.blockAlarmWindow": "Do not open shutters while the alarm is armed AND a window is open",
    "scn.blockAlarmWindowHelp": "Same as above, but only for a shutter that has an open window or door (or an unavailable sensor). Pointless if the previous box is ticked.",
    "set.alarmEntity": "Alarm (alarm_control_panel)",
    "set.alarmEntityHelp": "Used by the scenarios' \"do not open when the alarm is armed\" options. With no entity, or if it is unavailable, nothing is blocked.",
    "scn.releaseAll": "Room AND outdoor (all)",
    "scn.releaseAny": "Room OR outdoor (any)",
    "scn.releaseHelp": "all: the shutter only reopens once BOTH the outdoor and the room temperatures are back under their reopening thresholds. any: it reopens as soon as either one (outdoor OR room) is back under its threshold. Room only or outdoor only: a single threshold counts, the other is ignored.",
    "scn.gainRoom": "Room: below (°C)",
    "scn.gainOutdoor": "Outdoor: below (°C)",
    "scn.gainCondition": "Opening condition",
    "scn.gainBoth": "Room AND outdoor",
    "scn.gainAny": "Room OR outdoor",
    "scn.gainMinEnabled": "Low outdoor limit: stop opening below",
    "scn.gainMinHelp": "When the outdoor temperature is at or below this limit (can be negative), the shutter is no longer opened, even if sun and the other conditions are met.",
    "scn.gainMin": "Outdoor limit (°C)",
    "scn.gainRoomOnly": "Room only",
    "scn.gainOutdoorOnly": "Outdoor only",
    "scn.gainConditionHelp": "Room AND outdoor: the shutter opens when both the room and the outdoors are below their thresholds. Room OR outdoor: either one is enough. Room only or outdoor only: a single threshold counts, the other is ignored.",

    "set.house": "House",
    "set.houseOrientation": "House orientation (°)",
    "set.houseHelp": "Which compass direction the facade you call “South” is facing (compass azimuth: 0 = north, 90 = east, 180 = south, 270 = west). 180: house aligned with the cardinal points. 135: main facade facing south-east. All facades rotate with the house.",
    "compass.aria": "House plan, “South” facade facing {deg}°",
    "compass.n": "N",
    "compass.e": "E",
    "compass.s": "S",
    "compass.w": "W",
    "set.sensors": "Sensors and weather",
    "set.outdoor": "Outdoor temperature",
    "set.feels": "Feels-like temperature",
    "set.useMax": "Use the maximum of measured / feels-like",
    "set.useMaxHelp": "The effective outdoor temperature is the maximum of the two.",
    "set.weather": "Weather entity",
    "set.windEntity": "Wind sensor",
    "set.windThreshold": "Wind threshold",
    "set.windThresholdHelp": "Same unit as the wind sensor.",
    "set.windRatio": "Wind release ratio",
    "set.windRatioHelp": "Between 0.1 and 1. Wind is considered calmed when it drops below threshold × ratio.",
    "set.sunny": "Weather conditions where the sun counts",
    "set.sunnyHelp": "No condition ticked = weather filter disabled.",
    "set.eval": "Evaluation and wear protection",
    "set.interval": "Evaluation interval (minutes)",
    "set.grace": "Startup delay (seconds)",
    "set.minMove": "Minimum interval between two movements (minutes)",
    "set.minMoveHelp": "Protects the motors against wear.",
    "set.tolerance": "Position tolerance (%)",
    "set.overridePause": "Pause duration after a manual action (minutes)",
    "set.overrideWindow": "Pause until the end of the active hours",
    "set.overrideWindowHelp": "Replaces the duration beside when a manual action is detected.",
    "set.window": "Active hours",
    "set.windowStart": "Start",
    "set.windowEndMode": "End of active hours",
    "set.endEntity": "From an entity",
    "set.endFixed": "Fixed time",
    "set.endSunset": "Sunset",
    "set.endTime": "End time",
    "set.endEntityField": "End time entity",
    "set.endEntityHelp": "The state must be a “HH:MM” or “HH:MM:SS” time, or an ISO date.",
    "set.windowStartHelp": "If the end time is before the start time, the period runs past midnight (e.g. 20:00 → 02:00).",
    "set.windowEndHelp": "If the end time is before the start time, the period runs past midnight (e.g. 20:00 → 02:00).",
    "set.windowEndEntityHelp": " Formats read from the entity: HH:MM, HH:MM:SS or ISO date.",
    "set.sunsetOffset": "Offset from sunset (minutes)",
    "set.sunsetOffsetHelp": "Negative value = before sunset.",
    "set.auto": "Automatic scenario",
    "set.autoEnabled": "Pick summer / winter according to the month",
    "set.summerMonths": "Summer months",
    "set.summerMonthsHelp": "Other months use the winter scenario.",

    "backup.title": "Backup and import",
    "backup.help": "Importing replaces the draft without sending anything to the server: click “Save” afterwards to apply it.",
    "backup.area": "Configuration as JSON",
    "backup.placeholder": "Click “Export”, or paste a JSON configuration here to import it.",
    "backup.export": "Export",
    "backup.copy": "Copy",
    "backup.import": "Import",
    "backup.exported": "Current configuration exported to the text area.",
    "backup.copied": "Text copied to the clipboard.",
    "backup.copyFailed": "Automatic copy failed: the text is selected, copy it manually.",
    "backup.invalidJson": "Invalid JSON: {error}",
    "backup.notObject": "The JSON must be a configuration object (not a list or a plain value).",
    "backup.incomplete": "Incomplete configuration: the “settings”, “scenarios”, “facades” and “covers” keys are required.",

    "input.unknownValue": "{value} (unknown value)",
  },
};

/** Traduit une clé dans la langue donnée (repli fr, puis la clé elle-même). */
function translate(lang, key, vars) {
  const dict = I18N[lang] || I18N.fr;
  const text = dict[key] ?? I18N.fr[key] ?? key;
  return vars ? text.replace(/\{(\w+)\}/g, (m, k) => (k in vars ? String(vars[k]) : m)) : text;
}

/* ------------------------------------------------------------------ */
/* Constantes                                                          */
/* ------------------------------------------------------------------ */

const TAB_IDS = ["dashboard", "covers", "facades", "scenarios", "entities", "settings"];
const MODE_IDS = ["auto", "manual", "off"];
const SCENARIO_IDS = ["summer", "winter", "vacation", "off"];
const ORIENTATIONS = ["north", "east", "south", "west"];
const CLOSE_METHODS = ["position", "button", "close"];
const WEATHER_CONDITIONS = [
  "sunny", "partlycloudy", "cloudy", "clear-night", "fog", "rainy", "pouring",
  "lightning", "lightning-rainy", "hail", "snowy", "snowy-rainy", "windy",
  "windy-variant", "exceptional",
];

// Azimut de boussole de chaque côté de la maison quand celle-ci est alignée (orientation 180).
const CARDINAL_AZIMUTH = { north: 0, east: 90, south: 180, west: 270 };

// Code de statut -> couleur (contrat §3).
const STATUS_COLORS = {
  disabled: "grey", mode_manual: "grey", mode_off: "grey", scenario_off: "grey",
  grace: "grey", outside_window: "grey", no_data: "red", paused: "blue",
  window_open: "purple", wind_protected: "purple", shaded: "orange",
  watching: "green", cooldown: "grey", unavailable: "red",
};

// Listes de complétion : identifiant -> domaines d'entités proposés.
const DATALISTS = {
  cover: ["cover"],
  button: ["button"],
  sensor: ["sensor"],
  binary_sensor: ["binary_sensor"],
  weather: ["weather"],
  alarm: ["alarm_control_panel"],
  exposure: ["binary_sensor", "input_boolean", "switch"],
};

const SVG_NS = "http://www.w3.org/2000/svg";

/* ------------------------------------------------------------------ */
/* Utilitaires                                                         */
/* ------------------------------------------------------------------ */

/**
 * Crée un élément DOM. Les textes passent toujours par textContent / nœuds
 * texte : aucune interprétation HTML. `props` : class, text, on<evt>, et
 * toute autre clé (propriété pour value/checked/disabled/hidden/open, sinon
 * attribut).
 */
function el(tag, props = {}, ...children) {
  const node = document.createElement(tag);
  let value;
  for (const [key, val] of Object.entries(props)) {
    if (val === undefined || val === null || val === false) continue;
    if (key === "class") node.className = val;
    else if (key === "text") node.textContent = val;
    else if (key.startsWith("on")) node.addEventListener(key.slice(2), val);
    else if (key === "value") value = val; // appliquée après les enfants (select)
    else if (key === "checked" || key === "disabled" || key === "hidden") node[key] = val;
    else node.setAttribute(key, val === true ? "" : String(val));
  }
  const append = (child) => {
    if (child === null || child === undefined || child === false) return;
    if (Array.isArray(child)) child.forEach(append);
    else node.append(child instanceof Node ? child : document.createTextNode(String(child)));
  };
  children.forEach(append);
  if (value !== undefined) node.value = value;
  return node;
}

/** Élément SVG (construit avec createElementNS, texte via textContent). */
function svgEl(tag, attrs = {}, text) {
  const node = document.createElementNS(SVG_NS, tag);
  for (const [key, val] of Object.entries(attrs)) node.setAttribute(key, String(val));
  if (text !== undefined) node.textContent = text;
  return node;
}

const clone = (obj) => JSON.parse(JSON.stringify(obj));

/** Identifiant [a-z0-9_]+ dérivé d'un nom (accents retirés). */
function slugify(text) {
  const slug = String(text || "")
    .normalize("NFD").replace(/[̀-ͯ]/g, "")
    .toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "");
  return slug || "facade";
}

/** Appelle une fonction de désabonnement sans laisser fuiter d'erreur. */
function safeUnsub(unsub) {
  try {
    const result = unsub();
    if (result && typeof result.catch === "function") result.catch(() => {});
  } catch (_err) {
    /* connexion déjà fermée : rien à faire */
  }
}

/** Pause en cours pour ce volet ? */
const isPaused = (c) => c.status === "paused" || Boolean(c.paused_until);

const isObject = (v) => v !== null && typeof v === "object" && !Array.isArray(v);

/** Azimut effectif d'une façade : cardinal + orientation maison − 180 (ou azimut absolu si personnalisée). */
function computeAzimuth(facade, houseOrientation) {
  if (facade.orientation === "custom") {
    return Number.isFinite(facade.custom_azimuth) ? facade.custom_azimuth : null;
  }
  const base = CARDINAL_AZIMUTH[facade.orientation];
  if (base === undefined || !Number.isFinite(houseOrientation)) return null;
  return (((base + houseOrientation - 180) % 360) + 360) % 360;
}

/* ------------------------------------------------------------------ */
/* Styles                                                              */
/* ------------------------------------------------------------------ */

const CSS = `
:host {
  display: block; min-height: 100%;
  background: var(--primary-background-color, #fafafa);
  color: var(--primary-text-color, #212121);
  font-family: var(--paper-font-body1_-_font-family, Roboto, "Segoe UI", sans-serif);
  font-size: 15px; line-height: 1.4; --c: var(--disabled-color, #9e9e9e);
}
* { box-sizing: border-box; }
[hidden] { display: none !important; }
h1, h2, h3, p { margin: 0; }
button, input, select, textarea { font: inherit; }

.c-orange { --c: var(--warning-color, #ffa600); }
.c-green { --c: var(--success-color, #43a047); }
.c-blue { --c: var(--info-color, #039be5); }
.c-purple { --c: var(--purple-color, #8e24aa); }
.c-red { --c: var(--error-color, #db4437); }
.c-grey { --c: var(--disabled-color, #9e9e9e); }

.top {
  position: sticky; top: 0; z-index: 3;
  background: var(--app-header-background-color, var(--primary-color, #03a9f4));
  color: var(--app-header-text-color, var(--text-primary-color, #fff));
  box-shadow: 0 2px 4px rgba(0, 0, 0, .25);
}
.bar { display: flex; align-items: center; gap: 4px; min-height: 56px; padding: 0 8px 0 16px; }
.bar h1 { font-size: 20px; font-weight: 400; }
.icon-btn {
  min-width: 44px; min-height: 44px; border: 0; background: none;
  color: inherit; font-size: 22px; cursor: pointer; border-radius: 50%;
}
.tabs { display: flex; overflow-x: auto; scrollbar-width: none; -webkit-overflow-scrolling: touch; }
.tabs::-webkit-scrollbar { display: none; }
.tab {
  flex: 0 0 auto; min-height: 44px; padding: 0 16px; border: 0;
  border-bottom: 3px solid transparent; background: none; color: inherit;
  opacity: .75; cursor: pointer; white-space: nowrap;
}
.tab[aria-selected="true"] { opacity: 1; border-bottom-color: currentColor; font-weight: 500; }

main { max-width: 960px; margin: 0 auto; padding: 16px; padding-bottom: 96px; }
.stack { display: flex; flex-direction: column; gap: 16px; }
.card {
  background: var(--card-background-color, #fff); border-radius: 12px;
  border: 1px solid var(--divider-color, #e0e0e0); padding: 16px;
  display: flex; flex-direction: column; gap: 12px;
}
.card h2 { font-size: 17px; font-weight: 500; }
.card h3 { font-size: 15px; font-weight: 500; }
.muted { color: var(--secondary-text-color, #727272); }
.ok { color: var(--success-color, #43a047); }
.small { font-size: 13px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; }
.fgrid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px; }
.fields { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px 16px; }
.row { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.row > input, .row > select { flex: 1 1 180px; }
.lbl-row { display: flex; flex-direction: column; gap: 6px; }

.flash {
  margin: 12px 16px 0; padding: 12px 16px; border-radius: 8px;
  border: 1px solid var(--c); color: var(--primary-text-color, #212121);
  background: var(--card-background-color, #fff);
}
.notice { padding: 12px 16px; border-radius: 8px; border: 1px solid var(--c); display: flex; flex-direction: column; gap: 8px; align-items: flex-start; }
.notice .row { width: 100%; }
.empty { padding: 24px 0; text-align: center; color: var(--secondary-text-color, #727272); }

.btn {
  min-height: 44px; padding: 0 16px; border-radius: 8px; cursor: pointer;
  border: 1px solid var(--divider-color, #ccc);
  background: var(--card-background-color, #fff); color: var(--primary-text-color, #212121);
}
.btn.primary { background: var(--primary-color, #03a9f4); color: var(--text-primary-color, #fff); border-color: transparent; }
.btn.danger { color: var(--error-color, #db4437); border-color: var(--error-color, #db4437); }
.btn:disabled { opacity: .5; cursor: default; }
button:focus-visible, input:focus-visible, select:focus-visible, textarea:focus-visible, summary:focus-visible {
  outline: 2px solid var(--primary-color, #03a9f4); outline-offset: 2px;
}

.seg { display: flex; border: 1px solid var(--primary-color, #03a9f4); border-radius: 8px; overflow: hidden; }
.seg-btn {
  flex: 1 1 0; min-width: 0; min-height: 44px; padding: 0 8px; border: 0;
  background: transparent; color: var(--primary-text-color, #212121); cursor: pointer;
}
.seg-btn + .seg-btn { border-left: 1px solid var(--primary-color, #03a9f4); }
.seg-btn.on { background: var(--primary-color, #03a9f4); color: var(--text-primary-color, #fff); }
.seg-btn:disabled { opacity: .5; cursor: default; }

.tile { border: 1px solid var(--divider-color, #e0e0e0); border-radius: 8px; padding: 12px; display: flex; flex-direction: column; gap: 2px; }
.tile .v { font-size: 20px; font-weight: 500; }
.fcard { border: 1px solid var(--divider-color, #e0e0e0); border-radius: 8px; padding: 12px; display: flex; flex-direction: column; gap: 6px; }
.fcard-head { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 6px; font-weight: 500; }

.steps { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 12px; }
.step { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 12px; }
.step-n {
  flex: none; width: 32px; height: 32px; border-radius: 50%; display: flex;
  align-items: center; justify-content: center; font-weight: 500;
  background: var(--primary-color, #03a9f4); color: var(--text-primary-color, #fff);
}
.step-txt { flex: 1 1 200px; display: flex; flex-direction: column; }

.dot { width: 14px; height: 14px; border-radius: 50%; background: var(--c); flex: none; }
.badge { display: inline-flex; align-items: center; gap: 6px; padding: 2px 10px 2px 8px; border: 1px solid var(--c); border-radius: 999px; font-size: 13px; }
.badge .dot { width: 10px; height: 10px; }

.cover-row { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 12px; padding: 12px 0; border-top: 1px solid var(--divider-color, #e0e0e0); }
.cover-row:first-child, .group-title + .cover-row { border-top: 0; }
.cover-main { flex: 1 1 240px; min-width: 0; display: flex; flex-direction: column; gap: 4px; }
.cover-title { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; font-weight: 500; }
.cover-meta { display: flex; flex-wrap: wrap; gap: 4px 16px; }
.section-head { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 8px 16px; }
.group-title { margin: 16px 0 0; padding-bottom: 4px; border-bottom: 2px solid var(--primary-color, #03a9f4); color: var(--primary-text-color, #212121); }
.cover-group:first-of-type .group-title { margin-top: 8px; }
.drag-handle { flex: none; min-width: 28px; min-height: 44px; display: inline-flex; align-items: center; justify-content: center; cursor: grab; color: var(--secondary-text-color, #727272); user-select: none; letter-spacing: -2px; }
.move-btns { display: flex; gap: 4px; flex: none; }
.cover-actions { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; flex: none; }
.btn.icon { min-width: 44px; padding: 0; }
.ent-cover { display: flex; flex-direction: column; gap: 6px; padding: 10px 0; }
.ent-row { display: flex; flex-wrap: wrap; align-items: center; gap: 4px 12px; }
.ent-label { flex: 1 1 100%; color: var(--secondary-text-color, #727272); font-size: 13px; }
.ent-id { flex: 1 1 140px; min-width: 0; overflow-wrap: anywhere; font-size: 13px; }
.ent-state { flex: none; }
.ent-row .btn { padding: 0 12px; }
.vals { margin: 0 0 8px; padding-left: 20px; display: flex; flex-direction: column; gap: 2px; }
.vals code, .ent-id { font-family: monospace; }
.yaml { display: flex; flex-direction: column; gap: 6px; margin-top: 12px; }
.code { margin: 0; padding: 10px 12px; border-radius: 8px; max-width: 100%; box-sizing: border-box; overflow: auto; max-height: 320px; font-size: 12px; background: var(--secondary-background-color, #f5f5f5); border: 1px solid var(--divider-color, #e0e0e0); user-select: all; }
.cover-row.dragging { opacity: .5; }
.cover-row.drop-target { outline: 2px dashed var(--primary-color, #03a9f4); outline-offset: -2px; }

details.card > summary {
  list-style: none; cursor: pointer; min-height: 44px; display: flex;
  align-items: center; gap: 12px; justify-content: space-between;
}
details.card > summary::-webkit-details-marker { display: none; }
details.card > summary::after { content: "▾"; color: var(--secondary-text-color, #727272); }
details.card[open] > summary::after { content: "▴"; }
.sum-text { display: flex; flex-direction: column; min-width: 0; flex: 1; }
.sum-text > * { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.ct { font-weight: 500; }
.body { display: flex; flex-direction: column; gap: 12px; margin-top: 12px; }
.info-box { border-radius: 8px; border: 1px dashed var(--divider-color, #ccc); padding: 10px 12px; display: flex; flex-direction: column; gap: 2px; }

.field { display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.field > label, .field > .group { display: flex; flex-direction: column; gap: 4px; }
.lbl { font-size: 13px; color: var(--secondary-text-color, #727272); }
.help { font-size: 13px; color: var(--secondary-text-color, #727272); }
.err { font-size: 13px; color: var(--error-color, #db4437); }
input[type="text"], input[type="number"], input[type="time"], select, textarea {
  width: 100%; min-height: 44px; padding: 0 12px; font-size: 16px;
  border: 1px solid var(--divider-color, #ccc); border-radius: 8px;
  background: var(--card-background-color, #fff); color: var(--primary-text-color, #212121);
}
textarea { font-family: monospace; font-size: 13px; padding: 8px 12px; min-height: 160px; resize: vertical; }
.range { display: flex; align-items: center; gap: 12px; min-height: 44px; }
.range input { flex: 1; min-width: 0; height: 44px; accent-color: var(--primary-color, #03a9f4); }
.range output { min-width: 56px; text-align: right; }
.toggle { flex-direction: row !important; align-items: center; gap: 12px !important; min-height: 44px; cursor: pointer; }
.toggle input { width: 22px; height: 22px; flex: none; accent-color: var(--primary-color, #03a9f4); }
.toolbar { display: flex; flex-wrap: wrap; gap: 8px; }

.chips { display: flex; flex-wrap: wrap; gap: 8px; max-width: 100%; min-width: 0; }
.chip {
  display: inline-flex; flex-wrap: wrap; align-items: center; min-height: 44px; padding-left: 12px;
  max-width: 100%; min-width: 0; box-sizing: border-box;
  border: 1px solid var(--divider-color, #ccc); border-radius: 22px; gap: 0 8px;
}
.chip > span { min-width: 0; overflow-wrap: anywhere; word-break: break-word; }
.chip button { min-width: 44px; min-height: 44px; border: 0; background: none; color: var(--secondary-text-color, #727272); font-size: 20px; cursor: pointer; }
.chip-id { font-size: 12px; color: var(--secondary-text-color, #727272); }
.chip-toggle { min-height: 44px; padding: 0 14px; border-radius: 22px; border: 1px solid var(--divider-color, #ccc); background: transparent; color: var(--primary-text-color, #212121); cursor: pointer; }
.chip-toggle[aria-pressed="true"] { background: var(--primary-color, #03a9f4); color: var(--text-primary-color, #fff); border-color: transparent; }

.bulk-list { max-height: 260px; overflow-y: auto; border: 1px solid var(--divider-color, #ccc); border-radius: 8px; }
.bulk-row { display: flex; align-items: center; gap: 12px; min-height: 44px; padding: 0 12px; cursor: pointer; }
.bulk-row + .bulk-row { border-top: 1px solid var(--divider-color, #e0e0e0); }
.bulk-row input { width: 22px; height: 22px; flex: none; accent-color: var(--primary-color, #03a9f4); }
.bulk-row span { display: flex; flex-direction: column; min-width: 0; }

.house-row { display: flex; flex-wrap: wrap; gap: 16px 24px; align-items: center; }
.house-row .field { flex: 1 1 260px; }
.compass { width: 200px; max-width: 100%; height: auto; flex: none; }
.cp-ring { fill: none; stroke: var(--divider-color, #ccc); stroke-width: 2; }
.cp-house { fill: var(--secondary-background-color, #eee); stroke: var(--secondary-text-color, #727272); stroke-width: 2; }
.cp-front { stroke: var(--primary-color, #03a9f4); stroke-width: 5; stroke-linecap: round; }
.cp-dir { fill: var(--secondary-text-color, #727272); font-size: 11px; }
.cp-label { fill: var(--primary-text-color, #212121); font-size: 11px; }
.cp-south { fill: var(--primary-color, #03a9f4); font-weight: 600; }

.savebar {
  position: sticky; bottom: 0; z-index: 3; display: flex; flex-wrap: wrap;
  align-items: center; gap: 8px 12px; padding: 12px 16px;
  background: var(--card-background-color, #fff);
  border-top: 2px solid var(--warning-color, #ffa600);
  box-shadow: 0 -2px 6px rgba(0, 0, 0, .2);
}
.savebar .msg { flex: 1 1 220px; display: flex; flex-direction: column; gap: 2px; }
.savebar .msg strong { font-weight: 500; }
.savebar .errtxt { color: var(--error-color, #db4437); }

@media (max-width: 600px) {
  main { padding: 12px; }
  .savebar .btn { flex: 1 1 120px; }
  .house-row { justify-content: center; }
}
`;

/* ------------------------------------------------------------------ */
/* Panneau                                                             */
/* ------------------------------------------------------------------ */

class VoletsIntelligentsPanel extends HTMLElement {
  constructor() {
    super();
    this._hass = null;
    this._narrow = false;
    this._lang = "fr";
    this._tab = "dashboard";
    this._config = null; // dernière config connue du serveur
    this._draft = null; // brouillon édité (copie profonde)
    this._status = null;
    this._loading = false;
    this._loadError = null;
    this._subError = null;
    this._saving = false;
    this._saveError = null;
    this._barSig = "";
    this._busy = new Set(); // commandes en cours (clé -> boutons désactivés)
    this._openCards = new WeakSet(); // cartes dépliées (clé = objet du brouillon)
    this._facadeIds = new WeakMap(); // dernier id valide de chaque façade (suivi des renommages)
    this._infoUpdaters = new Set(); // rafraîchissent les infos de statut de l'onglet Façades
    this._unsub = null;
    this._subGen = 0;
    this._started = false;
    this._flashTimer = null;
    this.attachShadow({ mode: "open" });
    this._buildShell();
  }

  /* ---------- Traduction et formats ---------- */

  _t(key, vars) {
    return translate(this._lang, key, vars);
  }

  _num(value, unit, digits = 1) {
    if (typeof value !== "number" || !Number.isFinite(value)) return "—";
    const text = value.toLocaleString(this._lang, { maximumFractionDigits: digits });
    return unit ? `${text} ${unit}` : text;
  }

  _deg(value) {
    return typeof value === "number" && Number.isFinite(value) ? `${Math.round(value)}°` : "—";
  }

  _time(iso) {
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return String(iso);
    return d.toLocaleTimeString(this._lang, { hour: "2-digit", minute: "2-digit" });
  }

  /** Message d'erreur lisible à partir d'une erreur WebSocket de HA. */
  _err(err) {
    if (err && err.code === "unauthorized") return this._t("err.unauthorized");
    if (err && err.code === "unknown_command") return this._t("err.notInstalled");
    if (err && typeof err.message === "string" && err.message) return err.message;
    return this._t("err.unknown");
  }

  _statusLabel(code) {
    return code in STATUS_COLORS ? this._t(`status.${code}`) : String(code);
  }

  _orientLabel(facade) {
    if (facade.orientation === "custom") {
      return `${this._t("orient.custom")} ${this._deg(facade.custom_azimuth)}`;
    }
    return ORIENTATIONS.includes(facade.orientation) ? this._t(`orient.${facade.orientation}`) : String(facade.orientation);
  }

  /* ---------- Propriétés HA ---------- */

  set hass(hass) {
    this._hass = hass;
    const lang = String((hass && hass.language) || "fr").slice(0, 2).toLowerCase();
    this._setLang(lang in I18N ? lang : "fr");
    this._start();
  }
  get hass() {
    return this._hass;
  }

  set narrow(value) {
    this._narrow = Boolean(value);
    this._menuBtn.hidden = !this._narrow;
  }
  get narrow() {
    return this._narrow;
  }

  connectedCallback() {
    this._start();
  }

  disconnectedCallback() {
    this._started = false;
    this._subGen++; // invalide un abonnement encore en cours d'établissement
    if (this._unsub) {
      safeUnsub(this._unsub);
      this._unsub = null;
    }
    clearTimeout(this._flashTimer);
  }

  /** Change la langue de l'interface (le brouillon est conservé). */
  _setLang(lang) {
    if (lang === this._lang) return;
    this._lang = lang;
    this._renderChrome();
    this._barSig = "";
    this._updateBar();
    this._renderMain();
  }

  /* ---------- Démarrage : config + abonnement ---------- */

  _start() {
    if (this._started || !this.isConnected || !this._hass) return;
    this._started = true;
    // Accès complet : administrateurs et personnes désignées. Les autres voient un message.
    this._hass.callWS({ type: `${WS}get_access` }).then(
      (res) => this._applyAccess(Boolean(res && res.full)),
      () => this._applyAccess(!(this._hass.user && this._hass.user.is_admin === false)),
    );
    this._subscribe();
  }

  _applyAccess(full) {
    this._limited = !full;
    for (const [id, btn] of this._tabButtons) btn.hidden = !full && id !== "dashboard";
    if (full) {
      if (!this._config) this._loadConfig();
    } else {
      this._renderMain();
    }
  }

  async _loadConfig() {
    this._loading = true;
    this._loadError = null;
    this._renderMain();
    try {
      const res = await this._hass.callWS({ type: `${WS}get_config` });
      this._config = res.config;
      this._draft = clone(res.config);
      this._saveError = null;
    } catch (err) {
      this._loadError = this._err(err);
    } finally {
      this._loading = false;
      this._updateBar();
      this._renderMain();
    }
  }

  async _subscribe() {
    const gen = ++this._subGen;
    if (this._unsub) {
      safeUnsub(this._unsub);
      this._unsub = null;
    }
    this._subError = null;
    try {
      const unsub = await this._hass.connection.subscribeMessage(
        (status) => this._onStatus(status),
        { type: `${WS}subscribe_status` }
      );
      if (gen !== this._subGen) {
        safeUnsub(unsub); // démonté ou réabonné entre-temps
        return;
      }
      this._unsub = unsub;
    } catch (err) {
      if (gen !== this._subGen) return;
      this._subError = this._err(err);
      this._refreshDashboard();
    }
  }

  /** Événement de statut : seuls le tableau de bord et les infos en lecture seule sont rafraîchis. */
  _onStatus(status) {
    this._status = status;
    this._subError = null;
    this._refreshDashboard();
    if (this._tab === "entities" && this._entityMap) this._renderMain();
    this._infoUpdaters.forEach((update) => update());
  }

  _refreshDashboard() {
    if (this._tab === "dashboard") this._renderMain();
  }

  /* ---------- Coque (construite une seule fois) ---------- */

  _buildShell() {
    this._menuBtn = el("button", {
      class: "icon-btn", type: "button", text: "☰", hidden: true,
      onclick: () => this.dispatchEvent(new CustomEvent("hass-toggle-menu", { bubbles: true, composed: true })),
    });
    this._titleEl = el("h1");
    this._tabButtons = new Map();
    this._tabsEl = el("nav", { class: "tabs", role: "tablist" });
    for (const id of TAB_IDS) {
      const btn = el("button", {
        class: "tab", type: "button", role: "tab",
        "aria-selected": String(id === this._tab),
        onclick: () => this._setTab(id),
      });
      this._tabButtons.set(id, btn);
      this._tabsEl.append(btn);
    }
    this._flashEl = el("div", { class: "flash", role: "status", "aria-live": "polite", hidden: true });
    this._main = el("main");
    this._datalists = el("div", { hidden: true });
    this._bar = el("div", { class: "savebar", hidden: true });
    this.shadowRoot.append(
      el("style", { text: CSS }),
      el("header", { class: "top" }, el("div", { class: "bar" }, this._menuBtn, this._titleEl), this._tabsEl),
      this._flashEl,
      this._main,
      this._datalists,
      this._bar
    );
    this._renderChrome();
  }

  /** Textes de la coque (titre, onglets) dans la langue courante. */
  _renderChrome() {
    this._titleEl.textContent = this._t("app.title");
    this._menuBtn.setAttribute("aria-label", this._t("menu.open"));
    this._tabsEl.setAttribute("aria-label", this._t("tabs.aria"));
    for (const [id, btn] of this._tabButtons) btn.textContent = this._t(`tab.${id}`);
  }

  _setTab(id) {
    this._tab = id;
    if (id === "entities") this._entityMap = null; // relu à chaque ouverture
    for (const [tabId, btn] of this._tabButtons) {
      btn.setAttribute("aria-selected", String(tabId === id));
    }
    const active = this._tabButtons.get(id);
    if (active && active.scrollIntoView) active.scrollIntoView({ inline: "center", block: "nearest" });
    this._renderMain();
  }

  /** Message éphémère (succès / erreur de commande). */
  _flash(text, kind = "green") {
    clearTimeout(this._flashTimer);
    this._flashEl.className = `flash c-${kind}`;
    this._flashEl.textContent = text;
    this._flashEl.hidden = false;
    this._flashTimer = setTimeout(() => { this._flashEl.hidden = true; }, kind === "red" ? 8000 : 4000);
  }

  /* ---------- Rendu de la zone principale ---------- */

  _renderMain() {
    this._infoUpdaters.clear();
    if (this._tab === "dashboard") {
      this._main.replaceChildren(this._dashboardView());
      return;
    }
    if (this._loading) {
      this._main.replaceChildren(el("p", { class: "empty", text: this._t("common.loading") }));
      return;
    }
    if (!this._draft) {
      this._main.replaceChildren(el("div", { class: "notice c-red" },
        el("strong", { text: this._t("err.configUnavailable") }),
        el("span", { text: this._loadError || this._t("err.configNotLoaded") }),
        el("button", { class: "btn", type: "button", text: this._t("common.retry"), onclick: () => this._loadConfig() })));
      return;
    }
    this._buildDatalists();
    const views = {
      covers: () => this._coversView(),
      facades: () => this._facadesView(),
      scenarios: () => this._scenariosView(),
      entities: () => this._entitiesView(),
      settings: () => this._settingsView(),
    };
    this._main.replaceChildren(views[this._tab]());
  }

  /** <datalist> par type de sélecteur, alimentées par hass.states (friendly_name en label). */
  _buildDatalists() {
    const states = (this._hass && this._hass.states) || {};
    const ids = Object.keys(states).sort();
    this._datalists.replaceChildren(...Object.entries(DATALISTS).map(([name, domains]) =>
      el("datalist", { id: `vi-dl-${name}` },
        ids.filter((id) => domains.some((d) => id.startsWith(`${d}.`))).map((id) =>
          el("option", { value: id, label: this._friendly(id) || id })))));
  }

  _friendly(entityId) {
    const st = this._hass && this._hass.states && this._hass.states[entityId];
    return (st && st.attributes && st.attributes.friendly_name) || "";
  }

  /* ---------- Tableau de bord ---------- */

  _dashboardView() {
    const st = this._status;
    if (!st) {
      if (!this._subError) return el("p", { class: "empty", text: this._t("dash.connecting") });
      return el("div", { class: "notice c-red" },
        el("strong", { text: this._t("err.statusUnavailable") }),
        el("span", { text: this._subError }),
        el("button", { class: "btn", type: "button", text: this._t("common.retry"), onclick: () => this._subscribe() }));
    }

    const cfgFacades = new Map(((this._config && this._config.facades) || []).map((f) => [f.id, f]));
    const scenarioKeys = this._config ? Object.keys(this._config.scenarios) : SCENARIO_IDS.slice();
    if (!scenarioKeys.includes(st.scenario)) scenarioKeys.push(st.scenario);
    const scenarioOptions = scenarioKeys.map((key) => {
      const conf = this._config && this._config.scenarios[key];
      const fallback = SCENARIO_IDS.includes(key) ? this._t(`scenario.${key}`) : key;
      return [key, (key === st.scenario && st.scenario_label) || (conf && conf.label) || fallback];
    });
    const busyAll = this._busy.size > 0;
    const cmd = (payload, key, done) => () => this._command(payload, key, done);

    const control = el("section", { class: "card" },
      el("h2", { text: this._t("dash.control") }),
      el("div", { class: "lbl-row" },
        el("span", { class: "lbl", text: this._t("dash.globalMode") }),
        this._segmented(MODE_IDS.map((m) => [m, this._t(`mode.${m}`)]), st.mode,
          (v) => this._command({ command: "set_mode", value: v }, "mode"), this._t("dash.globalMode"), busyAll)),
      el("small", { class: "help", role: "note", text: MODE_IDS.includes(st.mode) ? this._t(`mode.${st.mode}.desc`) : "" }),
      el("div", { class: "lbl-row" },
        el("span", { class: "lbl", text: this._t("dash.scenario") }),
        this._segmented(scenarioOptions, st.scenario,
          (v) => this._command({ command: "set_scenario", value: v }, "scenario"), this._t("dash.scenario"), busyAll)),
      el("small", { class: "help", role: "note", text: SCENARIO_IDS.includes(st.scenario) ? this._t(`scenario.${st.scenario}.desc`) : "" }),
      el("div", { class: "toolbar" },
        el("button", { class: "btn primary", type: "button", text: this._t("dash.evaluate"), disabled: busyAll,
          onclick: cmd({ command: "evaluate" }, "evaluate", this._t("dash.evaluateDone")) }),
        el("button", { class: "btn", type: "button", text: this._t("dash.pauseAll"), disabled: busyAll,
          onclick: cmd({ command: "pause" }, "pause-all", this._t("dash.pauseAllDone")) }),
        el("button", { class: "btn", type: "button", text: this._t("dash.resumeAll"), disabled: busyAll,
          onclick: cmd({ command: "resume" }, "resume-all", this._t("dash.resumeAllDone")) })));

    const windRaw = typeof st.wind === "number";
    const tiles = [
      this._tile(this._t("dash.outdoor"), this._num(st.outdoor_effective, "°C"),
        this._t("dash.rawTemp", { value: this._num(st.outdoor_temp, "°C") })),
      this._tile(this._t("dash.wind"), this._num(st.wind),
        !windRaw ? this._t("dash.noMeasure") : st.wind_exceeded ? this._t("dash.windExceeded") : this._t("dash.windOk")),
      this._tile(this._t("dash.weather"),
        st.sunny ? this._t("dash.sunCounts") : this._t("dash.sunIgnored"),
        st.sunny ? this._t("dash.sunCountsSub") : this._t("dash.sunIgnoredSub")),
    ];
    if (st.sun) {
      tiles.push(this._tile(this._t("dash.sun"),
        this._t("dash.sunValue", { az: this._deg(st.sun.azimuth), el: this._deg(st.sun.elevation) }),
        st.sun.elevation < 0 ? this._t("dash.sunBelow")
          : this._t("dash.sunAbove", { deg: this._deg(st.house_orientation) })));
    }
    const conditions = el("section", { class: "card" },
      el("h2", { text: this._t("dash.conditions") }), el("div", { class: "grid" }, tiles));

    const activeWindow = el("section", { class: "card" },
      el("h2", { text: this._t("dash.window") }),
      el("div", { class: "row" },
        this._badge(st.in_window ? "green" : "grey", st.in_window ? this._t("dash.inWindow") : this._t("dash.outWindow")),
        el("span", { text: `${st.window_start || "—"} → ${st.window_end || "—"}` }),
        st.grace_active ? this._badge("blue", this._t("dash.grace")) : null));

    const facadeEntries = Object.entries(st.facades || {});
    const facades = el("section", { class: "card" },
      el("h2", { text: this._t("dash.facades") }),
      facadeEntries.length
        ? el("div", { class: "fgrid" }, facadeEntries.map(([id, f]) =>
          this._facadeStatusCard(id, f, cfgFacades.get(id), (st.covers || []).filter((c) => c.facade === id).length)))
        : el("p", { class: "muted", text: this._t("dash.noFacades") }));

    const covers = this._coversSection(st, busyAll);

    return el("div", { class: "stack" },
      this._subError ? el("div", { class: "notice c-red" },
        el("span", { text: this._t("err.subInterrupted", { error: this._subError }) }),
        el("button", { class: "btn", type: "button", text: this._t("common.retry"), onclick: () => this._subscribe() })) : null,
      this._gettingStarted(),
      control, conditions, activeWindow, facades, covers);
  }

  /** Assistant « Premiers pas » : affiché tant que la config ne contient aucun volet. */
  _gettingStarted() {
    const cfg = this._config;
    if (!cfg || cfg.covers.length > 0) return null;
    const steps = [
      ["start.s1", "start.s1d", "settings", false],
      ["start.s2", "start.s2d", "settings", Boolean(cfg.settings.outdoor_temp_entity)],
      ["start.s3", "start.s3d", "covers", false],
    ];
    return el("section", { class: "card" },
      el("h2", { text: this._t("start.title") }),
      el("p", { class: "muted", text: this._t("start.intro") }),
      el("ol", { class: "steps" }, steps.map(([title, desc, tab, done], i) => el("li", { class: "step" },
        el("span", { class: "step-n", "aria-hidden": "true", text: String(i + 1) }),
        el("span", { class: "step-txt" },
          el("strong", { text: this._t(title) }),
          el("span", { class: "muted small", text: this._t(desc) }),
          done ? el("span", { class: "small ok", text: `✓ ${this._t("start.done")}` }) : null),
        el("button", { class: "btn", type: "button", text: this._t("start.open"),
          "aria-label": `${this._t("start.open")} : ${this._t(title)}`, onclick: () => this._setTab(tab) })))));
  }

  /** Texte des plages d'ensoleillement d'une entrée de statut de façade. */
  _windowsText(info) {
    if (!info || !Array.isArray(info.windows)) return "—";
    if (!info.windows.length) return this._t("facade.noSun");
    return info.windows.map((w) => `${w.start} – ${w.end}`).join(", ");
  }

  _facadeStatusCard(id, info, cfg, count) {
    const unknown = info.exposed === null || info.exposed === undefined;
    const exposed = info.exposed === true;
    const orientation = cfg ? `${this._orientLabel(cfg)} · ` : "";
    return el("div", { class: "fcard" },
      el("div", { class: "fcard-head" },
        el("span", { text: (cfg && cfg.name) || id }),
        this._badge(exposed ? "orange" : "grey",
          unknown ? this._t("fcard.unknown") : exposed ? this._t("fcard.exposed") : this._t("fcard.notExposed"))),
      el("span", { class: "small muted",
        text: `${orientation}${this._t("fcard.azimuth", { deg: this._deg(info.azimuth) })}` +
          (info.source === "entity" ? ` · ${this._t("fcard.sourceEntity")}` : "") }),
      info.source === "entity" ? null
        : el("span", { class: "small", text: this._t("fcard.sun", { windows: this._windowsText(info) }) }),
      el("span", { class: "small muted", text: this._t(count === 1 ? "fcard.coversOne" : "fcard.coversOther", { n: count }) }));
  }

  /** Préférence d'affichage (par façade ou liste unique), mémorisée dans le navigateur. */
  _groupByFacade() {
    if (this._grouped !== undefined) return this._grouped;
    let value = true;
    try { value = window.localStorage.getItem("volets_intelligents.grouped") !== "0"; } catch (_) { /* stockage indisponible */ }
    this._grouped = value;
    return value;
  }

  _setGrouped(value) {
    this._grouped = value;
    try { window.localStorage.setItem("volets_intelligents.grouped", value ? "1" : "0"); } catch (_) { /* ignoré */ }
    this._renderMain();
  }

  _coversSection(st, busyAll) {
    const covers = st.covers || [];
    const header = el("div", { class: "section-head" },
      el("h2", { text: this._t("dash.covers", { n: covers.length }) }),
      covers.length > 1 ? this._segmented(
        [["facade", this._t("dash.byFacade")], ["flat", this._t("dash.flatList")]],
        this._groupByFacade() ? "facade" : "flat",
        (v) => this._setGrouped(v === "facade"), this._t("dash.view"), false) : null);
    if (!covers.length) {
      return el("section", { class: "card" }, header, el("p", { class: "muted", text: this._t("dash.noCovers") }));
    }
    const reorderable = Boolean(this._config) && !this._reordering;
    const hint = covers.length > 1
      ? el("p", { class: "small muted", text: this._t("dash.orderHint") }) : null;
    let body;
    if (this._groupByFacade()) {
      const names = new Map(Object.entries(st.facades || {}).map(([id, f]) => [id, f.name || id]));
      const order = [...names.keys()];
      covers.forEach((c) => { if (!order.includes(c.facade)) order.push(c.facade); });
      body = order.map((id) => {
        const group = covers.filter((c) => c.facade === id);
        if (!group.length) return null;
        return el("div", { class: "cover-group" },
          el("h3", { class: "group-title", text: names.get(id) || this._t("dash.noFacadeGroup") }),
          group.map((c, i) => this._coverRow(c, busyAll, group, i, reorderable)));
      });
    } else {
      body = covers.map((c, i) => this._coverRow(c, busyAll, covers, i, reorderable));
    }
    return el("section", { class: "card" }, header, hint, body);
  }

  /** Enregistre un nouvel ordre des volets (liste d'entity_id) dans la configuration. */
  async _saveCoverOrder(ids) {
    if (this._reordering || !this._config) return;
    const rank = new Map(ids.map((id, i) => [id, i]));
    const sortByRank = (list) => list
      .map((c, i) => [c, i])
      .sort((a, b) => (rank.has(a[0].entity_id) ? rank.get(a[0].entity_id) : 1e6 + a[1])
        - (rank.has(b[0].entity_id) ? rank.get(b[0].entity_id) : 1e6 + b[1]))
      .map(([c]) => c);
    this._reordering = true;
    const next = clone(this._config);
    next.covers = sortByRank(next.covers);
    try {
      const res = await this._hass.callWS({ type: `${WS}set_config`, config: next });
      this._config = clone(res && res.config ? res.config : next);
      // Un brouillon en cours suit le même ordre, sans perdre ses modifications.
      if (this._draft) this._draft.covers = sortByRank(this._draft.covers);
      this._flash(this._t("dash.orderSaved"), "green");
    } catch (err) {
      this._flash(this._t("err.reorder", { error: this._err(err) }), "red");
    } finally {
      this._reordering = false;
      this._refreshDashboard();
    }
  }

  /** Échange deux volets voisins dans l'ordre global (`group` = liste affichée). */
  _swapCovers(group, i, j) {
    if (j < 0 || j >= group.length) return;
    const ids = this._config.covers.map((c) => c.entity_id);
    const a = ids.indexOf(group[i].entity_id);
    const b = ids.indexOf(group[j].entity_id);
    if (a < 0 || b < 0) return;
    [ids[a], ids[b]] = [ids[b], ids[a]];
    this._saveCoverOrder(ids);
  }

  /** Déplace `from` à la place de `to` (glisser-déposer). */
  _dropCover(from, to) {
    if (!from || !to || from === to) return;
    const ids = this._config.covers.map((c) => c.entity_id);
    const a = ids.indexOf(from);
    const b = ids.indexOf(to);
    if (a < 0 || b < 0) return;
    ids.splice(a, 1);
    ids.splice(b, 0, from);
    this._saveCoverOrder(ids);
  }

  _windowBadge(c) {
    if (!c.window_state) return null;
    const color = { open: "orange", closed: "green", unknown: "red" }[c.window_state] || "grey";
    const badge = this._badge(color, this._t(`dash.window.${c.window_state}`));
    const sensors = (c.window_sensors || []).map((w) => `${this._friendly(w.entity_id) || w.entity_id} : ${this._t(`dash.window.${w.state}`)}`);
    if (sensors.length) badge.setAttribute("title", sensors.join("\n"));
    return badge;
  }

  _coverRow(c, busyAll, group = [c], index = 0, reorderable = false) {
    const color = STATUS_COLORS[c.status] || "grey";
    const paused = isPaused(c);
    const name = c.name || c.entity_id;
    const row = el("div", { class: "cover-row" });
    const canMove = reorderable && group.length > 1;
    const handle = canMove ? el("span", {
      class: "drag-handle", draggable: "true", role: "img", title: this._t("dash.drag", { name }),
      "aria-label": this._t("dash.drag", { name }), text: "⋮⋮",
      ondragstart: (e) => {
        e.dataTransfer.setData("text/plain", c.entity_id);
        e.dataTransfer.effectAllowed = "move";
        this._dragId = c.entity_id;
        row.classList.add("dragging");
      },
      ondragend: () => { row.classList.remove("dragging"); this._dragId = null; },
    }) : null;
    if (canMove) {
      row.addEventListener("dragover", (e) => {
        if (this._dragId && group.some((g) => g.entity_id === this._dragId)) {
          e.preventDefault();
          row.classList.add("drop-target");
        }
      });
      row.addEventListener("dragleave", () => row.classList.remove("drop-target"));
      row.addEventListener("drop", (e) => {
        e.preventDefault();
        row.classList.remove("drop-target");
        const from = this._dragId;
        this._dragId = null;
        if (from && group.some((g) => g.entity_id === from)) this._dropCover(from, c.entity_id);
      });
    }
    const arrows = canMove ? el("div", { class: "move-btns" },
      el("button", { class: "btn icon", type: "button", text: "↑", disabled: index === 0,
        "aria-label": this._t("dash.moveUp", { name }), title: this._t("dash.moveUp", { name }),
        onclick: () => this._swapCovers(group, index, index - 1) }),
      el("button", { class: "btn icon", type: "button", text: "↓", disabled: index === group.length - 1,
        "aria-label": this._t("dash.moveDown", { name }), title: this._t("dash.moveDown", { name }),
        onclick: () => this._swapCovers(group, index, index + 1) })) : null;
    row.append(
      ...[handle,
        el("div", { class: "cover-main" },
          el("div", { class: "cover-title" }, el("span", { text: name }), this._badge(color, this._statusLabel(c.status)),
            this._windowBadge(c)),
          c.reason ? el("span", { class: "muted", text: c.reason }) : null,
          el("div", { class: "cover-meta small muted" },
            el("span", { text: this._t("dash.position", { value: this._num(c.position, "%", 0) }) }),
            el("span", { text: this._t("dash.room", { value: this._num(c.room_temp, "°C") }) }),
            c.paused_until ? el("span", { text: this._t("dash.pausedUntil", { time: this._time(c.paused_until) }) }) : null)),
        el("div", { class: "cover-actions" }, arrows,
          el("button", {
            class: "chip-toggle", type: "button", text: this._t("dash.auto"),
            "aria-pressed": String(c.enabled !== false), disabled: busyAll,
            "aria-label": this._t("dash.autoAria", { name }),
            onclick: () => this._command(
              { command: "set_enabled", entity_id: c.entity_id, enabled: c.enabled === false }, `cover-${c.entity_id}`),
          }),
          el("button", {
            class: "btn", type: "button", text: paused ? this._t("dash.resume") : this._t("dash.pause"),
            disabled: busyAll || c.enabled === false,
            "aria-label": this._t(paused ? "dash.resumeAria" : "dash.pauseAria", { name }),
            onclick: () => this._command(
              { command: paused ? "resume" : "pause", entity_id: c.entity_id }, `cover-${c.entity_id}`),
          }))].filter(Boolean));
    return row;
  }

  _tile(label, value, sub) {
    return el("div", { class: "tile" },
      el("span", { class: "lbl", text: label }),
      el("span", { class: "v", text: value }),
      el("span", { class: "small muted", text: sub }));
  }

  _badge(color, text) {
    return el("span", { class: `badge c-${color}` }, el("span", { class: "dot", "aria-hidden": "true" }), text);
  }

  _segmented(options, active, onPick, label, disabled) {
    return el("div", { class: "seg", role: "group", "aria-label": label },
      options.map(([value, text]) => el("button", {
        class: `seg-btn${value === active ? " on" : ""}`, type: "button", text,
        "aria-pressed": String(value === active), disabled,
        onclick: () => onPick(value),
      })));
  }

  /** Envoie une commande ; `key` verrouille les boutons pendant l'appel. */
  async _command(payload, key, successMessage) {
    if (this._busy.has(key)) return;
    this._busy.add(key);
    this._refreshDashboard();
    try {
      await this._hass.callWS({ type: `${WS}command`, ...payload });
      if (successMessage) this._flash(successMessage, "green");
    } catch (err) {
      this._flash(this._t("err.command", { error: this._err(err) }), "red");
    } finally {
      this._busy.delete(key);
      this._refreshDashboard();
    }
  }

  /* ---------- Brouillon : suivi des modifications et enregistrement ---------- */

  _isDirty() {
    return Boolean(this._draft) && JSON.stringify(this._draft) !== JSON.stringify(this._config);
  }

  /** À appeler après toute modification du brouillon (sans re-rendu du formulaire). */
  _touch() {
    this._saveError = null;
    this._updateBar();
  }

  _updateBar() {
    const dirty = this._isDirty();
    const sig = `${dirty}|${this._saving}|${this._saveError}`;
    if (sig === this._barSig) return;
    this._barSig = sig;
    this._bar.hidden = !(dirty || this._saving || this._saveError);
    this._bar.replaceChildren(
      el("div", { class: "msg" },
        el("strong", { text: this._t("bar.dirty") }),
        this._saveError ? el("span", { class: "errtxt", role: "alert", text: this._saveError }) : null),
      el("button", { class: "btn", type: "button", text: this._t("common.cancel"), disabled: this._saving,
        onclick: () => this._loadConfig() }),
      el("button", { class: "btn primary", type: "button", disabled: this._saving,
        text: this._saving ? this._t("common.saving") : this._t("common.save"), onclick: () => this._save() }));
  }

  async _save() {
    if (this._saving || !this._isDirty()) return;
    this._saving = true;
    this._saveError = null;
    this._updateBar();
    try {
      const res = await this._hass.callWS({ type: `${WS}set_config`, config: this._draft });
      const saved = res && res.config ? res.config : this._draft;
      this._config = clone(saved);
      this._draft = clone(saved);
      this._entityMap = null;
      this._saving = false;
      this._updateBar();
      this._renderMain();
      this._flash(this._t("flash.saved"), "green");
    } catch (err) {
      this._saving = false;
      const msg = this._err(err);
      // invalid_config : le serveur renvoie déjà un message exploitable, affiché tel quel.
      this._saveError = err && err.code === "invalid_config" ? msg : this._t("err.save", { error: msg });
      this._updateBar();
    }
  }

  /* ---------- Briques de formulaire (modifient le brouillon en place) ---------- */

  /** Champ avec libellé ; `group` = true pour un contrôle contenant des boutons. */
  _field(label, control, help, group = false) {
    return el("div", { class: "field" },
      group
        ? el("div", { class: "group", role: "group", "aria-label": label }, el("span", { class: "lbl", text: label }), control)
        : el("label", {}, el("span", { class: "lbl", text: label }), control),
      help ? el("small", { class: "help", text: help }) : null);
  }

  /** Saisie texte ; `nullable` : vide -> null. `list` : id d'une datalist. */
  _text(obj, key, { list, placeholder, nullable = true, onChange } = {}) {
    return el("input", {
      type: "text", value: obj[key] ?? "", list, placeholder, autocomplete: "off",
      autocapitalize: "off", spellcheck: "false",
      oninput: (e) => {
        const v = e.target.value.trim();
        obj[key] = nullable && v === "" ? null : (nullable ? v : e.target.value);
        this._touch();
      },
      onchange: onChange ? (e) => onChange(e.target) : null,
    });
  }

  _numberInput(obj, key, { min, max, step = "any", onInput } = {}) {
    return el("input", {
      type: "number", inputmode: "decimal", min, max, step, value: obj[key] ?? "",
      oninput: (e) => {
        obj[key] = e.target.value === "" ? null : Number(e.target.value);
        if (onInput) onInput();
        this._touch();
      },
    });
  }

  _timeInput(obj, key) {
    return el("input", {
      type: "time", value: obj[key] ?? "",
      oninput: (e) => { obj[key] = e.target.value; this._touch(); },
    });
  }

  _range(obj, key, { min = 0, max = 100, step = 1, unit = "%", onInput } = {}) {
    const out = el("output", { text: `${obj[key] ?? min} ${unit}` });
    return el("div", { class: "range" },
      el("input", {
        type: "range", min, max, step, value: obj[key] ?? min,
        oninput: (e) => {
          obj[key] = Number(e.target.value);
          out.textContent = `${obj[key]} ${unit}`;
          if (onInput) onInput();
          this._touch();
        },
      }), out);
  }

  _toggle(obj, key, label, help) {
    return el("div", { class: "field" },
      el("label", { class: "toggle" },
        el("input", { type: "checkbox", checked: Boolean(obj[key]),
          onchange: (e) => { obj[key] = e.target.checked; this._touch(); } }),
        el("span", { text: label })),
      help ? el("small", { class: "help", text: help }) : null);
  }

  /** Liste déroulante ; une valeur inconnue du serveur est conservée et signalée. */
  _select(obj, key, options, onChange) {
    const opts = options.slice();
    // Champ absent (config plus ancienne) : on affiche la première option sans modifier le brouillon.
    const current = obj[key] === undefined ? opts[0][0] : obj[key];
    if (!opts.some(([v]) => v === current)) {
      opts.push([current, this._t("input.unknownValue", { value: current })]);
    }
    const sel = el("select", {
      onchange: (e) => { obj[key] = e.target.value; if (onChange) onChange(e.target.value); this._touch(); },
    }, opts.map(([v, l]) => el("option", { value: v, text: l })));
    sel.value = current;
    return sel;
  }

  /** Boutons à bascule pour un tableau de valeurs (mis à jour sur place). */
  _toggleChips(arr, options, sort = false) {
    return el("div", { class: "chips" }, options.map(([value, label]) => {
      const btn = el("button", {
        class: "chip-toggle", type: "button", text: label,
        "aria-pressed": String(arr.includes(value)),
        onclick: () => {
          const i = arr.indexOf(value);
          if (i >= 0) arr.splice(i, 1); else arr.push(value);
          if (sort) arr.sort((a, b) => a - b);
          btn.setAttribute("aria-pressed", String(i < 0));
          this._touch();
        },
      });
      return btn;
    }));
  }

  /** Liste de puces d'entités avec ajout / suppression (dessinée sur place). */
  _entityChips(arr, { list, placeholder, label }) {
    const chips = el("div", { class: "chips" });
    const input = el("input", {
      type: "text", list, placeholder, autocomplete: "off", autocapitalize: "off",
      spellcheck: "false", "aria-label": this._t("covers.addWindow", { label }),
    });
    const draw = () => chips.replaceChildren(...arr.map((id, i) => el("span", { class: "chip" },
      el("span", { title: id, text: this._friendly(id) || id }),
      this._friendly(id) ? el("span", { class: "chip-id", text: id }) : null,
      el("button", { type: "button", text: "×", "aria-label": this._t("common.remove", { id }),
        onclick: () => { arr.splice(i, 1); this._touch(); draw(); } }))));
    const add = () => {
      const id = input.value.trim();
      input.value = "";
      if (!id || arr.includes(id)) return;
      arr.push(id);
      this._touch();
      draw();
    };
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") { e.preventDefault(); add(); }
    });
    draw();
    return el("div", { class: "lbl-row" }, chips,
      el("div", { class: "row" }, input, el("button", { class: "btn", type: "button", text: this._t("common.add"), onclick: add })));
  }

  /**
   * Bouton de suppression en deux temps (évite les suppressions accidentelles au doigt).
   * `beforeArm` (optionnel) peut refuser la suppression en renvoyant false.
   */
  _deleteButton(onConfirm, beforeArm) {
    let armed = false;
    let timer = null;
    const btn = el("button", { class: "btn danger", type: "button", text: this._t("common.delete") });
    btn.addEventListener("click", () => {
      if (armed) { clearTimeout(timer); onConfirm(); return; }
      if (beforeArm && beforeArm() === false) return;
      armed = true;
      btn.textContent = this._t("common.confirmDelete");
      timer = setTimeout(() => { armed = false; btn.textContent = this._t("common.delete"); }, 4000);
    });
    return btn;
  }

  /* ---------- Façades : helpers partagés ---------- */

  /** Options du sélecteur de façade : nom et orientation de chacune. */
  _facadeOptions() {
    return this._draft.facades.map((f) => [f.id, `${f.name || f.id} (${this._orientLabel(f)})`]);
  }

  /** Nouveau volet pré-rempli ; close_position = position par défaut de la façade. */
  _newCover(entityId, name, facadeId) {
    const facade = this._draft.facades.find((f) => f.id === facadeId);
    return {
      entity_id: entityId, name, facade: facadeId, enabled: true,
      close_method: "position", close_position: facade ? facade.default_close_position : 10,
      button_entity: null, open_position: 100, room_temp_entity: null,
      window_entities: [], block_close_if_open: true, wind_sensitive: false, wind_action: "open",
      allow_open_closed_in: [],
    };
  }

  /* ---------- Onglet « Volets » ---------- */

  _coversView() {
    const covers = this._draft.covers;
    const noFacade = this._draft.facades.length === 0;
    return el("div", { class: "stack" },
      noFacade ? el("p", { class: "muted", text: this._t("covers.needFacade") }) : null,
      el("div", { class: "toolbar" },
        el("button", { class: "btn primary", type: "button", text: this._t("covers.add"), disabled: noFacade, onclick: () => {
          const cover = this._newCover("", "", this._draft.facades[0].id);
          covers.push(cover);
          this._openCards.add(cover);
          this._touch();
          this._renderMain();
        } })),
      noFacade ? null : this._bulkAddCard(),
      covers.length ? covers.map((c, i) => this._coverCard(c, i)) : el("p", { class: "empty", text: this._t("covers.empty") }));
  }

  /** Ajout groupé : recherche + cases à cocher sur les entités cover non encore gérées. */
  _bulkAddCard() {
    const target = { facade: this._draft.facades[0].id };
    const selected = new Set();
    const search = el("input", {
      type: "text", placeholder: this._t("bulk.search"), "aria-label": this._t("bulk.searchAria"),
      autocomplete: "off", spellcheck: "false", oninput: () => draw(),
    });
    const list = el("div", { class: "bulk-list" });
    const addBtn = el("button", { class: "btn primary", type: "button", onclick: () => {
      const facade = target.facade;
      for (const id of [...selected].sort()) {
        this._draft.covers.push(this._newCover(id, this._friendly(id) || id, facade));
      }
      this._touch();
      this._renderMain();
    } });
    const syncButton = () => {
      addBtn.textContent = this._t("bulk.add", { n: selected.size });
      addBtn.disabled = selected.size === 0;
    };
    const draw = () => {
      const used = new Set(this._draft.covers.map((c) => c.entity_id));
      const query = search.value.trim().toLowerCase();
      const rows = Object.keys((this._hass && this._hass.states) || {}).sort()
        .filter((id) => id.startsWith("cover.") && !used.has(id))
        .filter((id) => !query || id.includes(query) || this._friendly(id).toLowerCase().includes(query));
      list.replaceChildren(...(rows.length ? rows.map((id) => el("label", { class: "bulk-row" },
        el("input", { type: "checkbox", checked: selected.has(id),
          onchange: (e) => { if (e.target.checked) selected.add(id); else selected.delete(id); syncButton(); } }),
        el("span", {}, el("span", { text: this._friendly(id) || id }),
          this._friendly(id) ? el("small", { class: "muted", text: id }) : null)))
        : [el("p", { class: "empty", text: this._t("bulk.none") })]));
    };
    draw();
    syncButton();
    return el("details", { class: "card" },
      el("summary", {}, el("span", { class: "sum-text" },
        el("span", { class: "ct", text: this._t("bulk.title") }),
        el("span", { class: "muted small", text: this._t("bulk.help") }))),
      el("div", { class: "body" },
        this._field(this._t("bulk.facade"), this._select(target, "facade", this._facadeOptions())),
        search, list, el("div", { class: "toolbar" }, addBtn)));
  }

  _coverCard(cover, index) {
    const covers = this._draft.covers;
    if (!Array.isArray(cover.window_entities)) cover.window_entities = [];
    if (!Array.isArray(cover.allow_open_closed_in)) cover.allow_open_closed_in = [];
    const facadeName = () => {
      const f = this._draft.facades.find((x) => x.id === cover.facade);
      return f ? f.name : cover.facade;
    };

    // En-tête replié : mis à jour sur place quand on édite nom / entité / activation.
    const title = el("span", { class: "ct" });
    const sub = el("span", { class: "muted small" });
    const off = this._badge("grey", this._t("covers.disabled"));
    const refresh = () => {
      title.textContent = cover.name || cover.entity_id || this._t("covers.new");
      sub.textContent = [cover.entity_id, facadeName()].filter(Boolean).join(" · ");
      off.hidden = cover.enabled !== false;
    };

    const buttonField = this._field(this._t("covers.buttonEntity"),
      this._text(cover, "button_entity", { list: "vi-dl-button", placeholder: "button.…" }));
    const syncMethod = () => { buttonField.hidden = cover.close_method !== "button"; };

    const nameInput = this._text(cover, "name", { nullable: false, placeholder: this._t("covers.namePlaceholder") });
    nameInput.addEventListener("input", refresh);
    const entityInput = this._text(cover, "entity_id", {
      list: "vi-dl-cover", nullable: false, placeholder: "cover.…",
      onChange: (input) => {
        // Pré-remplit le nom avec le nom convivial si le champ est vide.
        if (!cover.name && this._friendly(cover.entity_id)) {
          cover.name = this._friendly(cover.entity_id);
          nameInput.value = cover.name;
          this._touch();
        }
        input.value = cover.entity_id;
        refresh();
      },
    });

    const facadeSelect = this._select(cover, "facade", this._facadeOptions(), refresh);
    const enabledToggle = this._toggle(cover, "enabled", this._t("covers.enabled"));
    enabledToggle.querySelector("input").addEventListener("change", refresh);

    // Action par vent fort : visible seulement si le volet est sensible au vent.
    const windActionField = this._field(this._t("covers.windAction"),
      this._select(cover, "wind_action", [["open", this._t("covers.windOpen")], ["close", this._t("covers.windClose")]]),
      this._t("covers.windActionHelp"));
    const syncWind = () => { windActionField.hidden = !cover.wind_sensitive; };
    const windToggle = this._toggle(cover, "wind_sensitive", this._t("covers.windSensitive"));
    windToggle.querySelector("input").addEventListener("change", syncWind);

    const card = el("details", { class: "card", open: this._openCards.has(cover) },
      el("summary", {},
        el("span", { class: "sum-text" }, title, sub),
        off),
      el("div", { class: "body" },
        el("div", { class: "toolbar" },
          el("button", { class: "btn", type: "button", text: this._t("common.up"), disabled: index === 0,
            onclick: () => this._moveCover(index, -1) }),
          el("button", { class: "btn", type: "button", text: this._t("common.down"), disabled: index === covers.length - 1,
            onclick: () => this._moveCover(index, 1) }),
          this._deleteButton(() => { covers.splice(index, 1); this._touch(); this._renderMain(); })),
        el("div", { class: "fields" },
          this._field(this._t("covers.entity"), entityInput),
          this._field(this._t("covers.name"), nameInput),
          this._field(this._t("covers.facade"), facadeSelect, this._t("covers.facadeHelp")),
          enabledToggle,
          this._field(this._t("covers.closeMethod"),
            this._select(cover, "close_method", CLOSE_METHODS.map((m) => [m, this._t(`method.${m}`)]), syncMethod)),
          buttonField,
          this._field(this._t("covers.closePosition"), this._range(cover, "close_position")),
          this._field(this._t("covers.openPosition"), this._range(cover, "open_position")),
          this._field(this._t("covers.roomTemp"), this._text(cover, "room_temp_entity",
            { list: "vi-dl-sensor", placeholder: "sensor.…" })),
          this._field(this._t("covers.windows"),
            this._entityChips(cover.window_entities, { list: "vi-dl-binary_sensor", placeholder: "binary_sensor.…", label: this._t("covers.windowSensor") }),
            null, true),
          this._toggle(cover, "block_close_if_open", this._t("covers.blockClose")),
          this._field(this._t("covers.allowOpenClosed"), this._scenarioToggles(cover), this._t("covers.allowOpenClosedHelp"), true),
          windToggle, windActionField)));
    card.addEventListener("toggle", () => {
      if (card.open) this._openCards.add(cover); else this._openCards.delete(cover);
    });
    refresh();
    syncMethod();
    syncWind();
    return card;
  }

  /** Un bouton par scénario : actif = l'ouverture d'un volet fermé à 100 % est permise dans ce scénario. */
  _scenarioToggles(cover) {
    const keys = ["summer", "winter", "vacation"];
    return el("div", { class: "chips" }, keys.map((key) => {
      const conf = this._draft.scenarios && this._draft.scenarios[key];
      const label = (conf && conf.label) || this._t(`scenario.${key}`);
      const btn = el("button", { class: "chip-toggle", type: "button", text: label,
        "aria-pressed": String(cover.allow_open_closed_in.includes(key)) });
      btn.addEventListener("click", () => {
        const list = cover.allow_open_closed_in;
        const i = list.indexOf(key);
        if (i >= 0) list.splice(i, 1); else list.push(key);
        btn.setAttribute("aria-pressed", String(i < 0));
        this._touch();
      });
      return btn;
    }));
  }

  _moveCover(index, delta) {
    const covers = this._draft.covers;
    const target = index + delta;
    if (target < 0 || target >= covers.length) return;
    [covers[index], covers[target]] = [covers[target], covers[index]];
    this._touch();
    this._renderMain();
  }

  /* ---------- Onglet « Façades » ---------- */

  _facadesView() {
    const facades = this._draft.facades;
    return el("div", { class: "stack" },
      el("p", { class: "muted", text: this._t("facades.intro") }),
      el("div", { class: "toolbar" },
        el("button", { class: "btn primary", type: "button", text: this._t("facades.add"), onclick: () => {
          const name = this._t("facade.newName");
          const facade = {
            id: this._uniqueFacadeId(slugify(name)), name, orientation: "south", custom_azimuth: 180,
            default_close_position: 10,
            exposure: { mode: "sun", entity: null, half_angle: 80, elevation_min: 10 },
          };
          facades.push(facade);
          this._openCards.add(facade);
          this._touch();
          this._renderMain();
        } })),
      facades.length ? facades.map((f, i) => this._facadeCard(f, i)) : el("p", { class: "empty", text: this._t("facades.empty") }));
  }

  /** Premier identifiant libre de la forme base, base_2, base_3… */
  _uniqueFacadeId(base, except) {
    let id = base;
    for (let n = 2; this._draft.facades.some((f) => f !== except && f.id === id); n++) id = `${base}_${n}`;
    return id;
  }

  /** Change l'id d'une façade et suit le renommage dans les volets qui l'utilisent. */
  _renameFacadeId(facade, newId) {
    const previous = this._facadeIds.get(facade);
    facade.id = newId;
    for (const c of this._draft.covers) if (c.facade === previous) c.facade = newId;
    this._facadeIds.set(facade, newId);
  }

  _moveFacade(index, delta) {
    const facades = this._draft.facades;
    const target = index + delta;
    if (target < 0 || target >= facades.length) return;
    [facades[index], facades[target]] = [facades[target], facades[index]];
    this._touch();
    this._renderMain();
  }

  /** Azimut effectif : valeur du statut si la façade n'a pas changé, sinon calcul local. */
  _facadeAzimuth(facade) {
    const saved = this._config && this._config.facades.find((f) => f.id === facade.id);
    const info = this._status && this._status.facades && this._status.facades[facade.id];
    const house = this._draft.settings.house_orientation;
    const unchanged = Boolean(saved) && saved.orientation === facade.orientation &&
      saved.custom_azimuth === facade.custom_azimuth && this._config.settings.house_orientation === house;
    if (unchanged && info && typeof info.azimuth === "number") return { value: info.azimuth, preview: false };
    return { value: computeAzimuth(facade, house), preview: !unchanged };
  }

  /** Plages d'ensoleillement : uniquement si la géométrie de la façade est celle du serveur. */
  _facadeWindows(facade) {
    if (facade.exposure.mode === "entity") return this._t("facade.windowsEntity");
    const saved = this._config && this._config.facades.find((f) => f.id === facade.id);
    const info = this._status && this._status.facades && this._status.facades[facade.id];
    const a = saved && saved.exposure;
    const b = facade.exposure;
    const unchanged = Boolean(saved) && saved.orientation === facade.orientation &&
      saved.custom_azimuth === facade.custom_azimuth && a.mode === b.mode &&
      a.half_angle === b.half_angle && a.elevation_min === b.elevation_min &&
      this._config.settings.house_orientation === this._draft.settings.house_orientation;
    if (!unchanged) return this._t("facade.windowsPending");
    return this._windowsText(info);
  }

  _facadeCard(facade, index) {
    const facades = this._draft.facades;
    const exposure = facade.exposure;
    this._facadeIds.set(facade, facade.id);

    // Infos en lecture seule, mises à jour sur place (édition ou nouvel événement de statut).
    const title = el("span", { class: "ct" });
    const sub = el("span", { class: "muted small" });
    const azValue = el("strong");
    const winValue = el("strong");
    const updateInfo = () => {
      const az = this._facadeAzimuth(facade);
      const azText = this._deg(az.value) + (az.preview && az.value !== null ? ` (${this._t("facade.preview")})` : "");
      title.textContent = facade.name || facade.id;
      sub.textContent = `${this._orientLabel(facade)} · ${azText}`;
      azValue.textContent = azText;
      winValue.textContent = this._facadeWindows(facade);
    };
    this._infoUpdaters.add(updateInfo);

    // Identifiant : slug [a-z0-9_]+, généré depuis le nom tant qu'on ne l'a pas modifié à la main.
    const idError = el("small", { class: "err", role: "alert", hidden: true });
    const idInput = this._text(facade, "id", {
      nullable: false,
      onChange: (input) => {
        const slug = input.value.toLowerCase().replace(/[^a-z0-9_]+/g, "_");
        input.value = slug;
        const duplicate = facades.some((f) => f !== facade && f.id === slug);
        idError.hidden = !(duplicate || !slug);
        idError.textContent = !slug ? this._t("facade.idRequired") : this._t("facade.idDuplicate");
        if (slug && !duplicate) this._renameFacadeId(facade, slug);
        else facade.id = slug;
        this._touch();
        updateInfo();
      },
    });
    const nameInput = this._text(facade, "name", { nullable: false, placeholder: this._t("orient.south") });
    let previousName = facade.name;
    nameInput.addEventListener("input", () => {
      if (facade.id === slugify(previousName) || facade.id === this._uniqueFacadeId(slugify(previousName), facade)) {
        const id = this._uniqueFacadeId(slugify(facade.name), facade);
        this._renameFacadeId(facade, id);
        idInput.value = id;
        idError.hidden = true;
      }
      previousName = facade.name;
      updateInfo();
    });

    // Champs propres à l'orientation et au mode d'exposition, affichés / masqués sur place.
    const customField = this._field(this._t("facade.customAzimuth"),
      this._numberInput(facade, "custom_azimuth", { min: 0, max: 360, step: 1, onInput: updateInfo }),
      this._t("facade.customAzimuthHelp"));
    const entityField = this._field(this._t("facade.entity"),
      this._text(exposure, "entity", { list: "vi-dl-exposure", placeholder: "binary_sensor.…" }),
      this._t("facade.entityHelp"));
    const halfAngleField = this._field(this._t("facade.halfAngle"),
      this._range(exposure, "half_angle", { min: 10, max: 90, step: 1, unit: "°", onInput: updateInfo }),
      this._t("facade.halfAngleHelp"));
    const elevationField = this._field(this._t("facade.elevationMin"),
      this._numberInput(exposure, "elevation_min", { min: -10, max: 60, step: 1, onInput: updateInfo }),
      this._t("facade.elevationMinHelp"));
    const syncVisibility = () => {
      customField.hidden = facade.orientation !== "custom";
      entityField.hidden = exposure.mode !== "entity";
      halfAngleField.hidden = exposure.mode !== "sun";
      elevationField.hidden = exposure.mode !== "sun";
    };

    const notice = el("div", { class: "notice c-orange", role: "alert", hidden: true });
    const remove = () => { facades.splice(facades.indexOf(facade), 1); this._touch(); this._renderMain(); };
    const deleteBtn = this._deleteButton(remove, () => this._explainFacadeInUse(facade, notice, remove));

    const card = el("details", { class: "card", open: this._openCards.has(facade) },
      el("summary", {}, el("span", { class: "sum-text" }, title, sub)),
      el("div", { class: "body" },
        el("div", { class: "toolbar" },
          el("button", { class: "btn", type: "button", text: this._t("common.up"), disabled: index === 0,
            onclick: () => this._moveFacade(index, -1) }),
          el("button", { class: "btn", type: "button", text: this._t("common.down"), disabled: index === facades.length - 1,
            onclick: () => this._moveFacade(index, 1) }),
          deleteBtn),
        notice,
        el("div", { class: "info-box" },
          el("span", {}, `${this._t("facade.effAzimuth")} : `, azValue),
          el("span", {}, `${this._t("facade.sunWindows")} : `, winValue)),
        el("div", { class: "fields" },
          this._field(this._t("facade.name"), nameInput),
          el("div", { class: "field" },
            this._field(this._t("facade.id"), idInput, this._t("facade.idHelp")), idError),
          this._field(this._t("facade.orientation"),
            this._select(facade, "orientation", ORIENTATIONS.map((o) => [o, this._t(`orient.${o}`)])
              .concat([["custom", this._t("orient.custom")]]), () => { syncVisibility(); updateInfo(); }),
            this._t("facade.orientationHelp")),
          customField,
          this._field(this._t("facade.mode"),
            this._select(exposure, "mode", [["sun", this._t("facade.modeSun")], ["entity", this._t("facade.modeEntity")]],
              () => { syncVisibility(); updateInfo(); }),
            this._t("facade.modeHelp")),
          entityField, halfAngleField, elevationField,
          this._field(this._t("facade.defaultClose"), this._range(facade, "default_close_position"),
            this._t("facade.defaultCloseHelp")))));
    card.addEventListener("toggle", () => {
      if (card.open) this._openCards.add(facade); else this._openCards.delete(facade);
    });
    syncVisibility();
    updateInfo();
    return card;
  }

  /**
   * Suppression d'une façade : refusée si des volets l'utilisent. Affiche alors
   * la liste des volets concernés et propose de les réaffecter. Renvoie false
   * pour bloquer l'armement du bouton, true si la suppression peut continuer.
   */
  _explainFacadeInUse(facade, notice, remove) {
    const users = this._draft.covers.filter((c) => c.facade === facade.id);
    if (!users.length) {
      notice.hidden = true;
      return true;
    }
    const others = this._draft.facades.filter((f) => f !== facade);
    const target = { facade: others.length ? others[0].id : "" };
    notice.replaceChildren(
      el("span", { text: this._t("facade.inUse", { names: users.map((c) => c.name || c.entity_id).join(", ") }) }),
      others.length
        ? el("div", { class: "row" },
          this._field(this._t("facade.reassignTo"),
            this._select(target, "facade", others.map((f) => [f.id, `${f.name || f.id} (${this._orientLabel(f)})`]))),
          el("button", { class: "btn danger", type: "button", text: this._t("facade.reassignDelete"), onclick: () => {
            for (const c of users) c.facade = target.facade;
            remove();
          } }))
        : el("span", { class: "muted", text: this._t("facade.noOtherFacade") }));
    notice.hidden = false;
    return false;
  }

  /* ---------- Onglet « Scénarios » ---------- */

  _scenariosView() {
    const scenarios = this._draft.scenarios;
    const keys = SCENARIO_IDS.filter((k) => k in scenarios)
      .concat(Object.keys(scenarios).filter((k) => !SCENARIO_IDS.includes(k)));
    return el("div", { class: "stack" }, keys.map((key) => this._scenarioCard(key, scenarios[key])));
  }

  _scenarioCard(key, sc) {
    const temp = (field, label) => this._field(label, this._numberInput(sc, field, { step: 0.5 }));
    let specific;
    if (sc.kind === "heat_protection") {
      specific = [
        el("div", { class: "fields" },
          temp("close_outdoor", this._t("scn.closeOutdoor")),
          temp("close_room", this._t("scn.closeRoom")),
          temp("open_outdoor", this._t("scn.openOutdoor")),
          temp("open_room", this._t("scn.openRoom"))),
        this._field(this._t("scn.release"),
          this._select(sc, "release_mode", [["all", this._t("scn.releaseAll")], ["any", this._t("scn.releaseAny")],
            ["room", this._t("scn.releaseRoom")], ["outdoor", this._t("scn.releaseOutdoor")]]),
          this._t("scn.releaseHelp")),
      ];
    } else if (sc.kind === "solar_gain") {
      specific = el("div", { class: "fields" },
        temp("gain_room_below", this._t("scn.gainRoom")),
        temp("gain_outdoor_below", this._t("scn.gainOutdoor")));
      specific = [specific,
        this._field(this._t("scn.gainCondition"),
          this._select(sc, "gain_condition", [["both", this._t("scn.gainBoth")], ["any", this._t("scn.gainAny")],
            ["room", this._t("scn.gainRoomOnly")], ["outdoor", this._t("scn.gainOutdoorOnly")]]),
          this._t("scn.gainConditionHelp")),
        this._toggle(sc, "gain_outdoor_min_enabled", this._t("scn.gainMinEnabled"), this._t("scn.gainMinHelp")),
        el("div", { class: "fields" }, temp("gain_outdoor_min", this._t("scn.gainMin")))];
    } else if (sc.kind === "hold_shaded") {
      specific = [el("p", { class: "muted small", text: this._t("scn.noThresholds") })];
    } else {
      specific = el("p", { class: "muted small", text: this._t("scn.noThresholds") });
    }
    if (["heat_protection", "solar_gain", "hold_shaded"].includes(sc.kind)) {
      specific = [].concat(specific, [
        el("h3", { text: this._t("scn.alarmTitle") }),
        this._toggle(sc, "block_open_alarm", this._t("scn.blockAlarm"), this._t("scn.blockAlarmHelp")),
        this._toggle(sc, "block_open_alarm_window", this._t("scn.blockAlarmWindow"), this._t("scn.blockAlarmWindowHelp"))]);
    }
    return el("section", { class: "card" },
      el("h2", { text: SCENARIO_IDS.includes(key) ? this._t(`scenario.${key}`) : key }),
      el("div", { class: "fields" },
        this._field(this._t("scn.label"), this._text(sc, "label", { nullable: false })),
        el("div", { class: "field" },
          el("span", { class: "lbl", text: this._t("scn.kind") }),
          el("span", { text: `kind.${sc.kind}` in I18N.fr ? this._t(`kind.${sc.kind}`) : String(sc.kind) }),
          el("small", { class: "help", text: this._t("scn.code", { kind: sc.kind }) }))),
      specific);
  }

  /* ---------- Onglet « Réglages » ---------- */

  /** Petit plan de maison : les 4 côtés tournent avec l'orientation (SVG via createElementNS). */
  _compass() {
    const svg = svgEl("svg", { viewBox: "0 0 200 200", class: "compass", role: "img" });
    svg.append(svgEl("circle", { cx: 100, cy: 100, r: 92, class: "cp-ring" }));
    // Points cardinaux fixes de la boussole (nord en haut).
    [["n", 0], ["e", 90], ["s", 180], ["w", 270]].forEach(([key, az]) => {
      const rad = (az * Math.PI) / 180;
      svg.append(svgEl("text", {
        x: (100 + 82 * Math.sin(rad)).toFixed(1), y: (100 - 82 * Math.cos(rad)).toFixed(1),
        "text-anchor": "middle", "dominant-baseline": "central", class: "cp-dir",
      }, this._t(`compass.${key}`)));
    });
    const house = svgEl("g");
    house.append(
      svgEl("rect", { x: 68, y: 68, width: 64, height: 64, rx: 4, class: "cp-house" }),
      svgEl("line", { x1: 72, y1: 132, x2: 128, y2: 132, class: "cp-front" }));
    svg.append(house);
    const labels = ORIENTATIONS.map((o) => {
      const node = svgEl("text", {
        "text-anchor": "middle", "dominant-baseline": "central",
        class: o === "south" ? "cp-label cp-south" : "cp-label",
      }, this._t(`orient.${o}`));
      svg.append(node);
      return [o, node];
    });
    const update = (value) => {
      const h = Number.isFinite(value) ? value : 180;
      house.setAttribute("transform", `rotate(${h - 180} 100 100)`);
      for (const [o, node] of labels) {
        const rad = (computeAzimuth({ orientation: o }, h) * Math.PI) / 180;
        node.setAttribute("x", (100 + 56 * Math.sin(rad)).toFixed(1));
        node.setAttribute("y", (100 - 56 * Math.cos(rad)).toFixed(1));
      }
      svg.setAttribute("aria-label", this._t("compass.aria", { deg: Math.round(h) }));
    };
    return { svg, update };
  }

  /* ---------- Onglet « Entités » ---------- */

  async _loadEntityMap() {
    if (this._entityLoading) return;
    this._entityLoading = true;
    try {
      this._entityMap = await this._hass.callWS({ type: `${WS}get_entities` });
      this._entityError = null;
    } catch (err) {
      this._entityError = this._err(err);
    } finally {
      this._entityLoading = false;
      if (this._tab === "entities") this._renderMain();
    }
  }

  _entitiesView() {
    if (this._entityMap) return el("div", { class: "stack" }, this._entitiesContent(this._entityMap));
    if (this._entityError) {
      return el("div", { class: "notice c-red" },
        el("span", { text: this._t("ent.error", { error: this._entityError }) }),
        el("button", { class: "btn", type: "button", text: this._t("common.retry"),
          onclick: () => { this._entityError = null; this._renderMain(); } }));
    }
    this._loadEntityMap();
    return el("p", { class: "empty", text: this._t("ent.loading") });
  }

  /** Copie dans le presse-papiers ; repli : message pour copier à la main. */
  async _copyText(text) {
    try {
      if (!navigator.clipboard) throw new Error("clipboard unavailable");
      await navigator.clipboard.writeText(text);
      this._flash(this._t("ent.copied"), "green");
    } catch (_err) {
      this._flash(this._t("ent.copyFailed"), "red");
    }
  }

  /** Libellé lisible de l'état courant d'une entité de l'intégration. */
  _entityStateText(entityId, kind) {
    const st = this._hass && this._hass.states && this._hass.states[entityId];
    if (!st) return "—";
    const v = st.state;
    if (v === "unavailable" || v === "unknown") return v;
    if (kind === "status") return this._statusLabel(v);
    if (kind === "mode" && MODE_IDS.includes(v)) return this._t(`mode.${v}`);
    if (kind === "scenario" && SCENARIO_IDS.includes(v)) return this._t(`scenario.${v}`);
    if (kind === "switch") return v === "on" ? "on" : "off";
    if (kind === "temp") return this._num(Number(v), "°C");
    if (kind === "bool") return v === "on" ? this._t("ent.on") : this._t("ent.off");
    if (kind === "ts") return this._time(v);
    if (kind === "time") return String(v).slice(0, 5);
    if (kind === "endmode") return ["fixed", "entity", "sunset"].includes(v) ? this._t(`ent.endMode.${v}`) : v;
    if (kind === "minutes") return `${v} min`;
    return v;
  }

  _entityRow(label, entityId, kind) {
    if (!entityId) {
      return el("div", { class: "ent-row" },
        el("span", { class: "ent-label", text: label }),
        el("span", { class: "muted small", text: this._t("ent.missing") }));
    }
    return el("div", { class: "ent-row" },
      el("span", { class: "ent-label", text: label }),
      el("code", { class: "ent-id", text: entityId }),
      el("span", { class: "ent-state small", text: this._entityStateText(entityId, kind) }),
      el("button", { class: "btn", type: "button", text: this._t("ent.copy"),
        "aria-label": this._t("ent.copyId", { id: entityId }), onclick: () => this._copyText(entityId) }));
  }

  _yamlBlock(title, text) {
    return el("div", { class: "yaml" },
      el("div", { class: "section-head" },
        el("h3", { text: title }),
        el("button", { class: "btn", type: "button", text: this._t("ent.copy"), onclick: () => this._copyText(text) })),
      el("pre", { class: "code", tabindex: "0", text }));
  }

  _entitiesContent(map) {
    const q = (v) => JSON.stringify(String(v)); // chaîne YAML entre guillemets
    const covers = map.covers || [];
    const cfgCovers = new Map(((this._config && this._config.covers) || []).map((c) => [c.entity_id, c]));
    const facadeName = new Map(((this._config && this._config.facades) || []).map((f) => [f.id, f.name || f.id]));
    const order = [...facadeName.keys()];
    covers.forEach((c) => { if (!order.includes(c.facade)) order.push(c.facade); });
    const groups = order.map((id) => [id, covers.filter((c) => c.facade === id)]).filter(([, list]) => list.length);

    const globals = el("section", { class: "card" },
      el("h2", { text: this._t("ent.global") }),
      this._entityRow(this._t("ent.mode"), map.mode, "mode"),
      this._entityRow(this._t("ent.scenario"), map.scenario, "scenario"),
      this._entityRow(this._t("ent.outdoor"), map.outdoor, "temp"));

    const perCover = el("section", { class: "card" },
      el("h2", { text: this._t("ent.perCover") }),
      groups.length ? groups.map(([id, list]) => el("div", { class: "cover-group" },
        el("h3", { class: "group-title", text: facadeName.get(id) || this._t("dash.noFacadeGroup") }),
        list.map((c) => el("div", { class: "ent-cover" },
          el("strong", { text: c.name || c.cover }),
          this._entityRow(this._t("ent.switch"), c.switch, "switch"),
          this._entityRow(this._t("ent.status"), c.status, "status")))))
        : el("p", { class: "muted", text: this._t("ent.noCovers") }));

    const w = map.window || {};
    const windowCard = el("section", { class: "card" },
      el("h2", { text: this._t("ent.window") }),
      this._entityRow(this._t("ent.windowActive"), w.active, "bool"),
      this._entityRow(this._t("ent.windowStart"), w.start, "ts"),
      this._entityRow(this._t("ent.windowEnd"), w.end, "ts"),
      this._entityRow(this._t("ent.windowStartSetting"), w.start_setting, "time"),
      this._entityRow(this._t("ent.windowEndSetting"), w.end_setting, "time"),
      this._entityRow(this._t("ent.windowEndMode"), w.end_mode, "endmode"),
      this._entityRow(this._t("ent.windowSunset"), w.sunset_offset, "minutes"),
      el("p", { class: "small muted", text: this._t("ent.windowHelp") }));

    const thresholdsCard = el("section", { class: "card" },
      el("h2", { text: this._t("ent.thresholds") }),
      (map.thresholds || []).map((t) =>
        this._entityRow(this._t(`ent.th.${t.scenario}.${t.key}`), t.entity_id, "temp")),
      el("p", { class: "small muted", text: this._t("ent.thresholdsHelp") }));

    const facadeList = map.facades || [];
    const facadesCard = el("section", { class: "card" },
      el("h2", { text: this._t("ent.facades") }),
      el("p", { class: "small muted", text: this._t("ent.facadeHelp") }),
      facadeList.map((f) => el("div", { class: "ent-cover" },
        el("strong", { text: f.name || f.id }),
        this._entityRow(this._t("ent.facadeExposed"), f.exposed, "bool"),
        this._entityRow(this._t("ent.facadeStart"), f.start, "ts"),
        this._entityRow(this._t("ent.facadeEnd"), f.end, "ts"))));

    const attrNames = ["reason", "cover", "position", "room_temp", "exposed", "paused_until",
      "shaded_by_us", "last_action", "last_action_at", "window_state"];
    const values = el("section", { class: "card" },
      el("h2", { text: this._t("ent.values") }),
      el("h3", { text: this._t("ent.valuesStatus") }),
      el("ul", { class: "vals" }, Object.keys(STATUS_COLORS).map((code) =>
        el("li", {}, el("code", { text: code }), ` : ${this._statusLabel(code)}`))),
      el("h3", { text: this._t("ent.valuesMode") }),
      el("ul", { class: "vals" }, MODE_IDS.map((m) => el("li", {}, el("code", { text: m }), ` : ${this._t(`mode.${m}`)} — ${this._t(`mode.${m}.desc`)}`))),
      el("h3", { text: this._t("ent.valuesScenario") }),
      el("ul", { class: "vals" }, SCENARIO_IDS.map((k) => el("li", {}, el("code", { text: k }), ` : ${this._t(`scenario.${k}`)} — ${this._t(`scenario.${k}.desc`)}`))),
      el("h3", { text: this._t("ent.attrs") }),
      el("ul", { class: "vals" }, attrNames.map((n) => el("li", {}, el("code", { text: n }), ` : ${this._t(`ent.attr.${n}`)}`))));

    // --- Exemples YAML avec les vrais identifiants
    const globalYaml = ["type: entities", `title: ${q("Volets intelligents")}`, "entities:"];
    [[map.mode, "ent.mode"], [map.scenario, "ent.scenario"], [map.outdoor, "ent.outdoor"]].forEach(([id, key]) => {
      if (id) globalYaml.push(`  - entity: ${id}`, `    name: ${q(this._t(key))}`);
    });

    const coverYaml = ["type: vertical-stack", "cards:"];
    groups.forEach(([id, list]) => {
      coverYaml.push("  - type: entities", `    title: ${q(facadeName.get(id) || id)}`, "    entities:");
      list.forEach((c) => {
        const name = c.name || c.cover;
        if (c.switch) coverYaml.push(`      - entity: ${c.switch}`, `        name: ${q(`${name} : ${this._t("ent.switch").toLowerCase()}`)}`);
        if (c.status) {
          coverYaml.push(`      - entity: ${c.status}`, `        name: ${q(name)}`,
            "      - type: attribute", `        entity: ${c.status}`, "        attribute: reason",
            `        name: ${q(this._t("ent.reasonRow"))}`);
          const conf = cfgCovers.get(c.cover);
          if (conf && (conf.window_entities || []).length) {
            coverYaml.push("      - type: attribute", `        entity: ${c.status}`, "        attribute: window_state",
              `        name: ${q(this._t("ent.windowRow"))}`);
          }
        }
      });
    });

    const reasonLines = ["type: markdown", `title: ${q(this._t("ent.exReasons"))}`, "content: >"];
    covers.filter((c) => c.status).forEach((c, i) => {
      if (i) reasonLines.push("");
      reasonLines.push(`  **${(c.name || c.cover).replace(/[*_`]/g, "")}** : {{ state_attr('${c.status}', 'reason') }}`);
    });

    const windowYaml = ["type: entities", `title: ${q(this._t("ent.window"))}`, "entities:"];
    [[w.active, "ent.windowActive"], [w.start, "ent.windowStart"], [w.end, "ent.windowEnd"],
      [w.start_setting, "ent.windowStartSetting"], [w.end_setting, "ent.windowEndSetting"],
      [w.end_mode, "ent.windowEndMode"], [w.sunset_offset, "ent.windowSunset"]].forEach(([id, key]) => {
      if (id) windowYaml.push(`  - entity: ${id}`, `    name: ${q(this._t(key))}`);
    });

    const facadeYaml = ["type: entities", `title: ${q(this._t("ent.facades"))}`, "entities:"];
    facadeList.forEach((f) => {
      const label = f.name || f.id;
      [[f.exposed, "ent.facadeExposed"], [f.start, "ent.facadeStart"], [f.end, "ent.facadeEnd"]].forEach(([id, key]) => {
        if (id) facadeYaml.push(`  - entity: ${id}`, `    name: ${q(`${label} : ${this._t(key).toLowerCase()}`)}`);
      });
    });

    const examples = el("section", { class: "card" },
      el("h2", { text: this._t("ent.examples") }),
      this._yamlBlock(this._t("ent.exGlobal"), globalYaml.join("\n")),
      this._yamlBlock(this._t("ent.exWindow"), windowYaml.join("\n")),
      facadeList.length ? this._yamlBlock(this._t("ent.exFacades"), facadeYaml.join("\n")) : null,
      covers.length ? this._yamlBlock(this._t("ent.exCovers"), coverYaml.join("\n")) : null,
      covers.some((c) => c.status) ? this._yamlBlock(this._t("ent.exReasons"), reasonLines.join("\n")) : null);

    return [el("p", { class: "muted", text: this._t("ent.intro") }), globals, windowCard, thresholdsCard, facadesCard, perCover, examples, values];
  }

  _settingsView() {
    const s = this._draft.settings;
    const w = s.window;
    const a = s.auto_scenario;
    const num = (obj, key, label, opts, help) => this._field(label, this._numberInput(obj, key, opts), help);
    const ent = (obj, key, label, list, placeholder) =>
      this._field(label, this._text(obj, key, { list, placeholder }));

    // Conditions météo : connues + éventuelles valeurs inconnues déjà présentes dans la config.
    const conditionOptions = WEATHER_CONDITIONS.map((c) => [c, this._t(`cond.${c}`)]).concat(
      s.sunny_conditions.filter((c) => !WEATHER_CONDITIONS.includes(c)).map((c) => [c, c]));

    // Sous-champs de la plage active selon le mode de fin, masqués sur place.
    const endFields = {
      fixed: this._field(this._t("set.endTime"), this._timeInput(w, "end_time")),
      entity: this._field(this._t("set.endEntityField"), this._text(w, "end_entity",
        { list: "vi-dl-sensor", placeholder: "sensor.…" }), this._t("set.endEntityHelp")),
      sunset: this._field(this._t("set.sunsetOffset"),
        this._numberInput(w, "sunset_offset_minutes", { min: -240, max: 240, step: 5 }),
        this._t("set.sunsetOffsetHelp")),
    };
    const endModeField = this._field(this._t("set.windowEndMode"), this._select(w, "end_mode", [
      ["entity", this._t("set.endEntity")], ["fixed", this._t("set.endFixed")], ["sunset", this._t("set.endSunset")],
    ], () => syncEnd()), this._t("set.windowEndHelp"));
    const syncEnd = () => {
      for (const [mode, node] of Object.entries(endFields)) node.hidden = w.end_mode !== mode;
      endModeField.querySelector(".help").textContent = this._t("set.windowEndHelp") +
        (w.end_mode === "entity" ? this._t("set.windowEndEntityHelp") : "");
    };

    const compass = this._compass();
    compass.update(s.house_orientation);

    const view = el("div", { class: "stack" },
      el("section", { class: "card" },
        el("h2", { text: this._t("set.house") }),
        el("div", { class: "house-row" },
          this._field(this._t("set.houseOrientation"),
            this._numberInput(s, "house_orientation", { min: 0, max: 360, step: 1,
              onInput: () => compass.update(s.house_orientation) }),
            this._t("set.houseHelp")),
          compass.svg)),

      el("section", { class: "card" },
        el("h2", { text: this._t("set.sensors") }),
        el("div", { class: "fields" },
          ent(s, "outdoor_temp_entity", this._t("set.outdoor"), "vi-dl-sensor", "sensor.…"),
          ent(s, "feels_like_entity", this._t("set.feels"), "vi-dl-sensor", "sensor.…"),
          this._toggle(s, "use_max_feels_like", this._t("set.useMax"), this._t("set.useMaxHelp")),
          ent(s, "weather_entity", this._t("set.weather"), "vi-dl-weather", "weather.…"),
          ent(s, "wind_entity", this._t("set.windEntity"), "vi-dl-sensor", "sensor.…"),
          this._field(this._t("set.alarmEntity"),
            this._text(s, "alarm_entity", { list: "vi-dl-alarm", placeholder: "alarm_control_panel.…" }),
            this._t("set.alarmEntityHelp")),
          num(s, "wind_threshold", this._t("set.windThreshold"), {}, this._t("set.windThresholdHelp")),
          num(s, "wind_release_ratio", this._t("set.windRatio"), { min: 0.1, max: 1, step: 0.05 },
            this._t("set.windRatioHelp"))),
        this._field(this._t("set.sunny"), this._toggleChips(s.sunny_conditions, conditionOptions),
          this._t("set.sunnyHelp"), true)),

      el("section", { class: "card" },
        el("h2", { text: this._t("set.eval") }),
        el("div", { class: "fields" },
          num(s, "evaluation_interval_minutes", this._t("set.interval"), { min: 1, max: 60, step: 1 }),
          num(s, "startup_grace_seconds", this._t("set.grace"), { min: 0, max: 900, step: 1 }),
          num(s, "min_move_interval_minutes", this._t("set.minMove"), { min: 0, max: 240, step: 1 },
            this._t("set.minMoveHelp")),
          num(s, "position_tolerance", this._t("set.tolerance"), { min: 0, max: 20, step: 1 }),
          num(s, "override_pause_minutes", this._t("set.overridePause"), { min: 0, max: 1440, step: 1 }),
          this._toggle(s, "override_until_window_end", this._t("set.overrideWindow"),
            this._t("set.overrideWindowHelp")))),

      el("section", { class: "card" },
        el("h2", { text: this._t("set.window") }),
        el("div", { class: "fields" },
          this._field(this._t("set.windowStart"), this._timeInput(w, "start"), this._t("set.windowStartHelp")),
          endModeField,
          endFields.entity, endFields.fixed, endFields.sunset)),

      el("section", { class: "card" },
        el("h2", { text: this._t("set.auto") }),
        this._toggle(a, "enabled", this._t("set.autoEnabled")),
        this._field(this._t("set.summerMonths"),
          this._toggleChips(a.summer_months, this._monthOptions(), true),
          this._t("set.summerMonthsHelp"), true)),

      this._backupSection());
    syncEnd();
    return view;
  }

  /** Mois 1..12 avec noms abrégés dans la langue courante (données de locale du navigateur). */
  _monthOptions() {
    return Array.from({ length: 12 }, (_, i) => [
      i + 1, new Date(2000, i, 1).toLocaleDateString(this._lang, { month: "short" }),
    ]);
  }

  /** Section d'export / import de la configuration au format JSON (brouillon uniquement). */
  _backupSection() {
    const area = el("textarea", {
      rows: 10, spellcheck: "false", "aria-label": this._t("backup.area"),
      placeholder: this._t("backup.placeholder"),
    });
    const msg = el("small", { class: "help", role: "status" });
    const say = (text, isError = false) => {
      msg.textContent = text;
      msg.className = isError ? "err" : "help";
    };
    const exportDraft = () => {
      area.value = JSON.stringify(this._draft, null, 2);
      say(this._t("backup.exported"));
    };
    const copy = async () => {
      area.select();
      try {
        if (!navigator.clipboard) throw new Error("clipboard unavailable");
        await navigator.clipboard.writeText(area.value);
        say(this._t("backup.copied"));
      } catch (_err) {
        say(this._t("backup.copyFailed"));
      }
    };
    const importDraft = () => {
      let parsed;
      try {
        parsed = JSON.parse(area.value);
      } catch (err) {
        say(this._t("backup.invalidJson", { error: err.message }), true);
        return;
      }
      if (!isObject(parsed)) {
        say(this._t("backup.notObject"), true);
        return;
      }
      if (!isObject(parsed.settings) || !isObject(parsed.scenarios) ||
          !Array.isArray(parsed.facades) || !Array.isArray(parsed.covers)) {
        say(this._t("backup.incomplete"), true);
        return;
      }
      this._draft = parsed;
      this._touch();
      this._renderMain();
      this._flash(this._t("flash.imported"), "orange");
    };
    return el("section", { class: "card" },
      el("h2", { text: this._t("backup.title") }),
      el("p", { class: "muted small", text: this._t("backup.help") }),
      area,
      el("div", { class: "toolbar" },
        el("button", { class: "btn", type: "button", text: this._t("backup.export"), onclick: exportDraft }),
        el("button", { class: "btn", type: "button", text: this._t("backup.copy"), onclick: copy }),
        el("button", { class: "btn primary", type: "button", text: this._t("backup.import"), onclick: importDraft })),
      msg);
  }
}

if (!customElements.get("volets-intelligents-panel")) {
  customElements.define("volets-intelligents-panel", VoletsIntelligentsPanel);
}
