# Changelog

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
