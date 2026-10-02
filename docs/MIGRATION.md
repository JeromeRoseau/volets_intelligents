# Migrer depuis l'automatisation « VOLETS : Thermique »

Ne désactivez rien avant d'avoir validé le nouveau système. Les deux ne doivent jamais
piloter les mêmes volets en même temps.

## Correspondances

| Ancienne automatisation | Volets Intelligents |
|---|---|
| `input_select.mode_volets` = Automatique | `select.volets_mode` = Automatique |
| `input_boolean.auto_volet_*` | `switch.volets_<nom>_auto` (ou l'interrupteur dans l'onglet Volets) |
| `binary_sensor.volets_exposition_est/sud/ouest` | Façades Est, Sud, Ouest en mode « capteur existant » (l'export le configure ainsi). Vous pourrez passer en mode « position du soleil » quand vous aurez réglé l'orientation de la maison. |
| `sensor.volets_heure_remontee` (et 08:00) | Réglages > Plage active (début 08:00, fin = capteur) |
| `input_number.volets_seuil_fermeture_ext` / `_piece` | Scénarios > Été (25 et 24 par défaut) |
| `input_number.volets_seuil_ouverture_ext` / `_piece` | Scénarios > Été (22 et 22 par défaut) |
| max(température, ressentie) | Réglages > « Utiliser le maximum avec la température ressentie » |
| `button.*_position_favorite` | Méthode « position » avec 10 % (la position favorite actuelle) |
| Remontée à l'heure de `sensor.volets_heure_remontee` | Fin de plage active : remonte les volets protégés |

## Comportements qui changent

1. **Relâche** : par défaut le volet remonte seulement quand l'extérieur ET la pièce sont redescendus
   (`all`). L'ancienne automatisation rouvrait dès que la pièce passait sous 22 °C, ce qui pouvait
   faire osciller le volet. Choisissez `any` pour retrouver l'ancien comportement.
2. **Capteur extérieur indisponible** : plus aucune action (l'ancienne version comptait 0 °C et pouvait rouvrir).
3. **Volets fermés à la main** : jamais rouverts automatiquement. Seuls les volets abaissés
   par l'intégration sont remontés.
4. **Action manuelle** : pause de 120 minutes par défaut.
5. **Remontée de fin de plage** : ne touche que les volets protégés par l'intégration (l'ancienne
   version ouvrait tous les volets « auto » non fermés).
6. **Démarrage** : 120 secondes sans action après un redémarrage de Home Assistant.

## Procédure conseillée

1. Installez l'intégration et configurez vos volets et façades dans le panneau.
2. Dans l'onglet Volets, laissez `enabled` actif sur un ou deux volets seulement.
3. Mettez `automation.volets_thermique` en pause (désactivée) seulement pour ces volets, ou
   désactivez les `input_boolean.auto_volet_*` correspondants le temps du test.
4. Observez quelques jours le tableau de bord : la phrase d'explication de chaque volet doit
   correspondre à ce que vous attendez.
5. Élargissez volet par volet, puis désactivez l'ancienne automatisation.

## À vérifier chez vous

- Renseignez l'orientation de la maison (Réglages) avant de passer une façade en mode « position du soleil » : l'export garde 180°.
- Les autres automatisations qui bougent les volets pendant la journée (alarme, fenêtre ouverte)
  seront vues comme des actions manuelles et mettront le volet en pause.
- Ajoutez vos capteurs de fenêtre dans l'onglet Volets (`window_entities`) : l'export n'en contient pas.
- `close_position` est à 10 % comme vos positions favorites actuelles ; ajustez volet par volet.
