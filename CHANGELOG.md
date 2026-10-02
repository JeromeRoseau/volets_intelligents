# Changelog

## 2026.10.2

- Nouvelle option d'intégration « Personnes désignées » : des comptes non administrateurs choisis ont accès à tous les onglets du panneau et peuvent tout modifier (contrôlé côté serveur) ; les autres comptes non admin ne voient que le Tableau de bord. Nouvelle commande WebSocket `get_access`.
- Scénario Hiver : nouvelle condition d'ouverture « pièce OU extérieur » (en plus de pièce ET extérieur, pièce seulement, extérieur seulement).
- Scénario Hiver : limite extérieure basse optionnelle (peut être négative) : quand l'extérieur est à cette température ou en dessous, le volet n'est plus ouvert.
- Correction : les textes de la fenêtre « Configurer » (traductions des options) étaient mal placés dans `strings.json` et les traductions.

## 2026.10.1

Les versions suivent désormais le schéma `année.mois.numéro dans le mois` (2026.10.1 = première version d'octobre 2026).

- Panneau : chaque mode global (Automatique, Manuel, Arrêt) et chaque scénario (Été, Hiver, Vacances, Désactivé) est décrit sous son sélecteur du tableau de bord et dans l'onglet « Entités » (liste des valeurs).
- Scénario Hiver : condition d'ouverture au choix (onglet Scénarios) : pièce ET extérieur (par défaut), pièce seulement ou extérieur seulement. En mode « pièce seulement », une température extérieure indisponible ne bloque plus l'ouverture.
- Scénario Été : la condition de réouverture accepte aussi « pièce seulement » et « extérieur seulement » (en plus de « pièce ET extérieur » et « pièce OU extérieur »).
- Alarme : nouvelle entité `alarm_control_panel` dans Réglages. Chaque scénario (Été, Hiver, Vacances) a deux options : « Ne pas ouvrir quand l'alarme est activée » et « Ne pas ouvrir quand l'alarme est activée ET qu'une fenêtre est ouverte ». Alarme activée = états `armed_*` ou `triggered` ; entité absente ou indisponible : rien n'est bloqué. La mise en sécurité contre le vent n'est jamais bloquée.
- README : une capture d'écran par onglet du panneau (données de démonstration) ; README en anglais (`README.en.md`).
- Cumul des évolutions 0.3.x : bouton « Auto » par volet, seuils des scénarios (été et hiver) en entités `number`, capteurs de façade persistants sur la journée.

## 0.3.10

- Nouvelles entités `number.volets_seuil_hiver_gain_exterieur` et `number.volets_seuil_hiver_gain_piece` (seuils du scénario « winter », gain solaire), modifiables depuis les dashboards, comme les seuils d'été.
- Onglet « Entités » du panneau et README : liste des seuils des scénarios (identifiants réels, avec copie).

## 0.3.9

- Capteurs `sensor.volets_facade_*_debut/fin` : les heures d'ensoleillement restent affichées toute la journée (plage en cours, sinon prochaine, sinon la dernière du jour), façade exposée ou non.

## 0.3.8

- Tableau de bord du panneau : bouton « Auto » par volet pour activer/désactiver la gestion (commande WebSocket `set_enabled`).
- 4 entités `number.volets_seuil_ete_*` (fermeture/réouverture extérieur et pièce du scénario « summer »), modifiables depuis les dashboards.
- Le lien de la fenêtre Configurer s'appelle désormais « Interface de gestion » (le bouton « Visiter » de la page de l'appareil
  a un libellé fixe de Home Assistant, non modifiable par l'intégration ; l'entrée du menu latéral reste « Volets »).

## 0.3.7

- `icon.png` servi à `/volets_intelligents_static/icon.png` : permet de forcer l'icône dans la liste des mises à jour de HACS
  (voir le README), en attendant que HACS lise les icônes embarquées.

- menu de configuration de l'intégration (Configurer) : case pour afficher ou masquer « Volets » dans le menu latéral,
  avec un lien direct vers le panneau ;
- bouton « Visiter » sur la page de l'appareil « Volets Intelligents » : ouvre le panneau, même masqué du menu latéral.

## 0.3.6

- icône et logo de l'intégration (dossier `brand/`, clair et sombre, normal et @2x) : Home Assistant 2026.3 et plus les
  affiche à la place de « icon not available » ; la liste des mises à jour de HACS ne les utilise pas encore
  (voir hacs/integration#5171).

## 0.3.5

- un volet fermé à 100 % (position 0 %, ou état « fermé » sans position) n'est plus jamais remonté par
  l'intégration, quelle que soit la façon dont il a été fermé (fin de plage, soleil parti, scénario Hiver,
  protection contre le vent) ;
- option par volet `allow_open_closed_in` (boutons Été, Hiver, Vacances dans l'onglet Volets) pour lever cette règle
  dans les scénarios choisis ;
- exception : un volet dont la protection est la fermeture totale et que l'intégration a fermé reste remontable ;
- un volet fermé à 100 % que l'intégration avait abaissé est « oublié » : elle ne s'en occupe plus.

## 0.3.4

Nouvelles entités :

- plage active : `binary_sensor.volets_plage_active`, `sensor.volets_plage_debut` et `sensor.volets_plage_fin` ;
- réglages de la plage active modifiables depuis un tableau de bord : `time.volets_reglage_plage_debut`,
  `time.volets_reglage_plage_fin`, `select.volets_reglage_plage_mode_fin` et
  `number.volets_reglage_plage_decalage_coucher` ;
- par façade : `binary_sensor.volets_facade_<nom>_exposee`, `sensor.volets_facade_<nom>_debut` et
  `sensor.volets_facade_<nom>_fin` (créées et supprimées avec les façades) ;
- l'onglet « Entités » du panneau les liste, avec leurs états et des exemples YAML à jour.

## 0.3.3

- nouvel onglet « Entités » dans le panneau : identifiants réels des entités (boutons « Copier »),
  valeurs possibles, attributs et exemples de cartes YAML remplis avec vos identifiants ;
- le capteur de statut de chaque volet expose l'attribut `window_state` (`open`, `closed`, `unknown`) ;
- nouvelle commande WebSocket `volets_intelligents/get_entities` (administrateur).

## 0.3.2

Publication de la 0.3.1 sous un nouveau numéro : le navigateur recharge le panneau et la carte
(l'adresse des fichiers contient le numéro de version), ce qui rend visibles le regroupement par
façade, les flèches pour déplacer les volets et l'état des fenêtres. Aucun changement de code.

## 0.3.1

Tableau de bord :

- les volets sont groupés par façade (sous-titre par façade), avec un choix « Liste unique » ;
- l'ordre des volets se change avec les flèches (ou par glisser-déposer sur ordinateur) et s'enregistre tout de suite ;
- chaque volet affiche l'état de ses fenêtres et portes (ouverte, fermée, capteur indisponible) ;
- onglet Volets : les capteurs d'ouverture à nom long ne sortent plus du cadre ;
- un workflow crée automatiquement une version GitHub à chaque tag `vX.Y.Z` : HACS affiche alors un vrai numéro de version au lieu d'un hash.

## 0.3.0

Corrections issues d'une relecture indépendante (chaque point a un test de non-régression) :

- un capteur de fenêtre ou de porte indisponible bloque désormais la fermeture ;
- un volet qui s'arrête à une position différente de celle demandée (position favorite) n'est plus
  refermé en boucle et est bien remonté ensuite ;
- les volets lents ne sont plus pris pour une action manuelle ;
- la protection vent passe avant le mode, le scénario, la pause et le délai de démarrage, avec un ordre
  de mise en sécurité par volet (`wind_action`) et des ordres simples ouvrir/fermer ;
- une plage active qui passe minuit fonctionne ; formats d'heure de fin élargis ;
- un capteur d'exposition indisponible ne fait plus remonter les volets (aucune action) ;
- sans mesure de température extérieure, aucune action (même avec la température ressentie) ;
- le scénario Hiver respecte l'anti-usure ;
- droits WebSocket alignés sur ceux de Home Assistant (contrôle des entités concernées) ;
- validation renforcée (saut de ligne final, limites de taille, cohérences entre champs) ;
- traductions des champs de services ; carte Lovelace qui ne se redessine plus inutilement.

## 0.2.1

Optimisations sans changement de comportement :

- exposition de chaque façade calculée une seule fois par évaluation (au lieu de deux) ;
- volets indexés par identifiant (plus de recherche linéaire ni de reconstruction d'ensembles à chaque événement) ;
- pas de réabonnement aux capteurs quand rien n'a changé (ex. simple bascule d'un volet) ;
- planification synchrone du regroupement d'événements (plus de tâche créée par événement) ;
- état mémorisé écrit sur le disque seulement s'il a changé.

## 0.2.0

- Quatre façades par défaut (nord, est, sud, ouest), modifiables : renommer, ajouter, supprimer ;
  n'importe quel volet peut être affecté à n'importe quelle façade.
- Orientation de la maison : toutes les façades tournent avec elle (azimut de la façade « Sud »).
- Exposition calculée selon la date, l'heure et la position GPS de Home Assistant (plus besoin
  de capteur), avec angle d'éclairage et masque d'horizon réglables par façade.
  Les capteurs d'exposition existants restent utilisables.
- Plages d'ensoleillement théoriques du jour pour chaque façade, affichées dans le panneau.
- Interface du panneau et de la carte en français et en anglais.
- Assistant « Premiers pas » et ajout groupé de volets.

## 0.1.0

Première version : moteur de règles (protection thermique, gain solaire hiver, mode vacances),
panneau de gestion, carte Lovelace, détection d'action manuelle, blocage fenêtre ouverte,
protection vent, délai de sécurité au démarrage.
