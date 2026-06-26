---
name: velo-double-calibration
description: >-
  Rédige des séances d'entraînement vélo structurées selon le principe de la
  DOUBLE CALIBRATION : chaque bloc est prescrit simultanément en pourcentage de
  FTP (cible objective, en watts) ET en RPE (cible subjective sur 10). À utiliser
  quand l'utilisateur (Johan, triathlète, FTP 228 W) demande de créer, générer
  ou planifier une ou plusieurs séances de vélo (home-trainer/Zwift ou route) :
  endurance, tempo, sweet spot, seuil, VO2max, force, séances mixtes, ou un
  microcycle. Produit une fiche séance lisible et, si demandé, un fichier .zwo
  importable dans Zwift.
---

# Séances vélo — Double calibration %FTP + RPE

## 1. Principe : pourquoi deux calibrations

Chaque bloc d'effort est prescrit avec **deux ancrages en parallèle** :

1. **Cible objective — %FTP** (convertie en watts absolus). C'est la *consigne maître*
   sur home-trainer/Zwift où la puissance est stable.
2. **Cible subjective — RPE** (échelle de perception de l'effort sur 10). C'est le
   *garde-fou* qui valide ou corrige la cible puissance.

**Règle de pilotage (la "double calibration" en pratique) :**

- On **tient la puissance** comme référence principale.
- Mais on **surveille le RPE** : si à la puissance cible le RPE est **plus haut
  que la fourchette prescrite** (fatigue, chaleur, sommeil, hypoglycémie, FTP
  surestimée) → on **réduit la puissance** pour rester dans la fourchette RPE.
- Si le RPE est **nettement plus bas** que prévu sur plusieurs séances seuil/VO2 →
  signal que la **FTP est sous-estimée** : proposer un re-test.
- En extérieur (vent, bosses, relances), où la puissance fluctue, le **RPE devient
  l'ancre dominante** et la puissance la fourchette indicative.

Cette double ancre rend la séance robuste aux mauvais jours et auto-corrige une
FTP qui dérive entre deux tests.

## 2. Données athlète de référence

> Toujours **revérifier la FTP du jour** avant de générer si l'outil Strava est
> disponible : appeler `mcp__Strava__get_athlete_zones` (champs `ftp`,
> `power_zones`, `ftp_is_estimated`). Sinon utiliser les valeurs ci-dessous.

- **FTP de référence : 228 W** (≈ 3,55 W/kg, 64,2 kg).
- **Profil** : triathlète, distance half/L (objectif type "Frenchman" : 89 km vélo).
  Bon endurant, habitué aux blocs seuil et aux longues sorties (jusqu'à ~4 h).
- **Contexte** : Zwift indoor pour les séances structurées + route pour le volume.
- **Vocabulaire séances déjà utilisé** : Endurance, Tempo, Sweet Spot, Seuil,
  Seuil-progressif, VO2 / Mixte, Force.

## 3. Table de calibration (FTP 228 W)

| Zone | Nom | %FTP | Watts (FTP 228) | RPE /10 | Sensation repère | Usage type |
|------|-----|------|-----------------|---------|------------------|------------|
| Z1 | Récup | < 55 % | < 125 W | 1–2 | très facile, je peux chanter | échauffement, récup active |
| Z2 | Endurance | 56–75 % | 128–171 W | 3–4 | conversation fluide | volume, fond, longues sorties |
| Z3 | Tempo | 76–90 % | 173–205 W | 5–6 | soutenu, phrases courtes | endurance "muscu", spécifique L/half |
| SS | Sweet Spot | 88–94 % | 200–214 W | 6–7 | inconfortable mais tenable longtemps | rapport charge/fatigue optimal |
| Z4 | Seuil | 91–105 % | 207–239 W | 7–8 | dur, mots isolés seulement | élever la FTP |
| Z5 | VO2max | 106–120 % | 242–274 W | 8–9 | très dur, respiration max | PMA / cylindrée aérobie |
| Z6 | Anaérobie | 121–150 % | 276–342 W | 9–10 | brûlant, court | capacité anaérobie, relances |
| Z7 | Neuromusculaire | > 150 % | > 343 W | 10 | sprint maximal | force-vitesse, sprints |

**Force (basse cadence)** : se prescrit à une zone de puissance Z3–Z4 **MAIS à
cadence 50–60 rpm** ; le RPE *musculaire* (jambes) monte à 7–8 alors que le RPE
*cardio* reste 5–6. Toujours préciser les deux quand c'est une séance de force.

> Si la FTP récupérée ≠ 228, recalculer la colonne watts : `watts = %FTP × FTP/100`,
> arrondir à l'entier. Garder les colonnes %FTP et RPE inchangées.

## 4. Comment construire une séance

Demander (ou déduire du contexte) ces paramètres ; si non précisés, choisir des
valeurs par défaut raisonnables et les annoncer :

- **Objectif/filière** : récup, endurance, tempo, sweet spot, seuil, VO2max, force,
  mixte, ou "spécifique course".
- **Durée totale** disponible (défaut 60 min indoor).
- **Support** : Zwift/home-trainer (ERG possible) ou route.
- **Contexte de forme** : frais / fatigué / reprise / proche compétition (ajuste le
  curseur dans la fourchette).

Structure imposée de toute séance :

1. **Échauffement** — progressif Z1→Z2(→Z3), 10–20 min. Pour les séances
   intenses : ajouter 2–3 activations courtes (ex. 3×30 s montée en Z4/Z5).
2. **Corps de séance** — blocs en double calibration, récup entre blocs explicitée
   (puissance + RPE).
3. **Retour au calme** — Z1, 5–10 min.

Règles de dosage :

- Séance intense (seuil/VO2) : viser un **temps passé dans la cible** réaliste
  (seuil : 20–40 min cumulées ; VO2 : 8–20 min cumulées).
- Récup entre intervalles : VO2 ratio ~1:1 à 1:0,5 ; seuil ~3:1 à 4:1.
- Toujours donner la **cadence cible** (défaut 85–95 rpm ; force 50–60 ; vélocité 100+).
- Nom de séance court façon Zwift, ex. `Seuil 3x(8/4/2)` ou `VO2 5x3'`.

## 5. Format de sortie

Par défaut, produire une **fiche Markdown** selon
`templates/fiche-seance.md`. Pour chaque bloc, **toujours afficher les deux
calibrations** : `% FTP (watts) + RPE`, plus cadence et durée.

Exemple de ligne de bloc :

```
🟥 Bloc principal — 3 × 8 min @ 95–100 % FTP (217–228 W) · RPE 7–8 · 90 rpm
   récup 4 min @ 55 % FTP (125 W) · RPE 2–3
```

Toujours terminer la fiche par un **encart "Pilotage double calibration"** qui
rappelle quoi faire si le RPE décolle (voir §1).

Si l'utilisateur demande un fichier importable (« .zwo », « pour Zwift »,
« importer »), générer aussi un fichier `.zwo` à partir de
`templates/seance.zwo` : les `<SteadyState>`/`<IntervalsT>` utilisent `Power`
en **fraction de FTP** (ex. 0,97 pour 97 %). Mettre les cibles RPE et la cadence
dans les attributs `Cadence` et dans des balises `<textevent>` pour qu'elles
s'affichent à l'écran pendant la séance.

## 6. Banque de séances types (toutes en double calibration)

- **Endurance fondamentale** — 1×(45–180 min) @ 65–75 % FTP (148–171 W) · RPE 3–4 · 85–90 rpm.
- **Tempo spécifique half** — 3×15 min @ 80–88 % FTP (182–200 W) · RPE 5–6, récup 5 min · simule l'allure vélo de course.
- **Sweet Spot** — 3×12 min @ 90–94 % FTP (205–214 W) · RPE 6–7, récup 5 min.
- **Seuil progressif** — 3×(8/4/2 min) @ 92/97/103 % FTP (210/221/235 W) · RPE 7/7,5/8, récup 4 min.
- **Seuil "over-under"** — 4×(2 min @ 105 % / 2 min @ 90 %) ×... · RPE oscillant 8↔6.
- **VO2max** — 5×3 min @ 110–118 % FTP (251–269 W) · RPE 8–9, récup 3 min @ 50 % · RPE 2.
- **VO2 court (30/30)** — 2 séries de 8×(30 s @ 115 % / 30 s @ 50 %) · RPE 9 / 2.
- **Force basse cadence** — 6×3 min @ 88–95 % FTP (200–217 W) à **50–55 rpm** · RPE jambes 7–8 / cardio 5–6, récup 3 min.
- **Mixte (réveil filières)** — alternance blocs tempo / VO2 courts, ex. tes séances `Mixte 5x(40/2'30…)`.

Adapter durées et répétitions au temps disponible et à la forme du jour.

## 7. Garde-fous

- Ne jamais prescrire d'intensité Z4+ sans échauffement complet.
- Si "reprise" / "fatigué" : rester ≤ tempo, abaisser le haut des fourchettes.
- Rappeler que les watts sont indicatifs si la FTP date de > 6 semaines, et que le
  RPE prime alors.
- En extérieur, prévenir que la puissance va fluctuer : donner la **puissance
  moyenne cible** du bloc + l'ancre RPE.
