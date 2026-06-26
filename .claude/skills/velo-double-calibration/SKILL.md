---
name: velo-double-calibration
description: >-
  Outil COACH pour rédiger des séances et banques de séances vélo en DOUBLE
  CALIBRATION : chaque bloc est prescrit simultanément en pourcentage de FTP
  (cible objective, convertie en watts pour l'athlète concerné) ET en RPE (cible
  subjective sur 10). À utiliser pour créer/générer/planifier des séances vélo
  pour SOI ou pour un athlète coaché : séance unique, banque thématique, ou plan
  périodisé vers une course (triathlon S/M/L/half, dont le Bayman). Gère
  plusieurs athlètes via des profils paramétrables. Produit des fiches lisibles
  et, si demandé, des fichiers .zwo importables dans Zwift.
---

# Séances vélo — Double calibration %FTP + RPE (mode coach)

## 0. Première chose à faire : identifier l'athlète

La skill fonctionne pour **plusieurs athlètes**. Avant de générer, déterminer
QUI est concerné :

1. Si l'utilisateur nomme un athlète coaché → charger son profil dans
   `references/athletes/<nom>.md`. S'il n'existe pas, le **créer** à partir de
   `references/profil-athlete-template.md` en demandant les infos manquantes
   (au minimum : **FTP**, poids, niveau, course cible + date, volume dispo,
   points forts/faibles).
2. Si l'utilisateur parle de lui-même (Johan) sans préciser → profil par défaut
   `references/athletes/johan.md` (FTP 228 W, triathlète half). Revérifier la
   FTP via Strava si dispo (`get_athlete_zones`).
3. En cas de doute sur quel athlète → **demander**.

> ⚠️ Ne jamais réutiliser la FTP d'un athlète pour un autre. Les watts se
> recalculent toujours à partir de la FTP du profil chargé.

## 1. Principe : pourquoi deux calibrations

Chaque bloc d'effort porte **deux ancrages en parallèle** :

1. **Cible objective — %FTP** (→ watts absolus pour l'athlète). Consigne maître
   sur home-trainer/Zwift où la puissance est stable.
2. **Cible subjective — RPE** (perception de l'effort /10). Garde-fou qui valide
   ou corrige la cible puissance.

**Règle de pilotage :**
- Tenir la **puissance** comme référence principale (indoor).
- Surveiller le **RPE** : si à la puissance cible le RPE dépasse la fourchette
  (fatigue, chaleur, sommeil, FTP surestimée) → **baisser les watts** pour rester
  dans la fourchette RPE.
- RPE durablement trop bas sur les blocs durs → **FTP sous-estimée**, re-tester.
- En **extérieur** (vent, bosses, relances), le RPE devient l'ancre dominante et
  la puissance une fourchette indicative.

Avantage clé pour un coach : la banque s'écrit **en %FTP + RPE**, donc elle est
**indépendante de l'athlète**. On la réutilise pour chaque coaché en injectant
simplement sa FTP.

## 2. Table de calibration (en %FTP — universelle)

| Zone | Nom | %FTP | RPE /10 | Sensation repère | Usage |
|------|-----|------|---------|------------------|-------|
| Z1 | Récup | < 55 % | 1–2 | je peux chanter | échauffement, récup |
| Z2 | Endurance | 56–75 % | 3–4 | conversation fluide | volume, fond |
| Z3 | Tempo | 76–90 % | 5–6 | phrases courtes | spécifique L/half |
| SS | Sweet Spot | 88–94 % | 6–7 | inconfortable tenable | charge/fatigue optimal |
| Z4 | Seuil | 91–105 % | 7–8 | mots isolés | élever la FTP |
| Z5 | VO2max | 106–120 % | 8–9 | respiration max | PMA |
| Z6 | Anaérobie | 121–150 % | 9–10 | brûlant, court | capacité anaérobie |
| Z7 | Neuromusc. | > 150 % | 10 | sprint | force-vitesse |

**Conversion watts** : `watts = round(%FTP / 100 × FTP_athlète)`.
**Force (50–60 rpm)** : zone Z3–Z4, dissocier RPE jambes (7–8) / cardio (5–6).
Détail complet + zones FC dans `references/zones-rpe.md`.

## 3. Construire une séance

Paramètres (déduire du contexte ou demander) : filière, durée, support
(Zwift/route), forme du jour, place dans la périodisation.

Structure imposée : **Échauffement** (progressif, + activations si intense) →
**Corps** (blocs en double calibration, récup explicitée) → **Retour au calme**.

Dosage : seuil 20–40 min cumulées ; VO2 8–20 min ; récup VO2 ~1:1, seuil ~3-4:1 ;
cadence par défaut 85–95 rpm (force 50–60, vélocité 100+). Nom court façon Zwift.

## 4. Générer une BANQUE de séances

Quand on demande une « banque », un « catalogue » ou « des séances pour la prépa » :

1. Charger le profil athlète (FTP, course, points faibles).
2. Partir de `references/banque-seances.md` (catalogue maître en %FTP + RPE,
   classé par filière). **Personnaliser** : convertir en watts pour l'athlète,
   ajuster les volumes au niveau et au temps dispo, prioriser les filières selon
   les points faibles et la spécificité de la course (voir `references/bayman.md`
   pour le Bayman : **distance complète vallonnée** → accent endurance longue +
   tempo/sweet-spot longs à l'allure de course (IF ~0,70) + force en côte ;
   VO2 secondaire).
3. Sortie : un tableau/catalogue de séances nommées, chacune avec ses blocs en
   `%FTP (watts) + RPE`, durée et objectif. Regrouper par filière. Si demandé,
   produire aussi les `.zwo`.

## 5. Générer un PLAN périodisé (optionnel)

Si on demande un plan daté jusqu'à la course :
- Calculer le nb de semaines jusqu'à la date de course (profil athlète).
- Phaser : **Base** (endurance/SS, force) → **Build** (seuil/VO2 + spécifique) →
  **Spécifique/Affûtage** (allure course, volume qui baisse, intensité maintenue)
  → **Taper** (7–10 j). Cycles 3:1 (3 sem charge / 1 sem récup) par défaut.
- Pour chaque semaine, piocher dans la banque les séances adaptées à la phase et
  au volume vélo hebdo de l'athlète. Donner objectif de la semaine + charge.

## 6. Format de sortie

Fiche unique → `templates/fiche-seance.md`. **Toujours afficher les deux
calibrations** : `% FTP (watts) + RPE`, + cadence + durée. Terminer par l'encart
« Pilotage double calibration ».

Exemple de ligne :
```
🟥 3 × 12 min @ 88–92 % FTP ([watts] W) · RPE 6–7 · 90 rpm — récup 5 min @ 55 % · RPE 2
```

## 6 bis. Sortie Nolio (.zwo) — séances importables et JOUABLES

Nolio importe `.zwo`, `.erg`, `.mrc`, `.json` (intervals.icu) et `.fit` pour créer
des séances structurées jouables (envoyées home-trainer/montre). Format retenu :
**`.zwo`**, car :
- la puissance y est en **fraction de FTP** → **athlète-indépendant** : Nolio
  applique la FTP de chaque athlète. Une seule banque sert tous les coachés.
- le **RPE** s'affiche pendant la séance via `<textevent>` (double calibration).

**Banque .zwo déjà générée** : dossier `bank_zwo/` (22 séances, voir
`bank_zwo/INDEX.md`). Pour (re)générer ou étendre :
```
python3 scripts/generate_bank.py
```
Le script définit la banque comme données (puissances en %FTP, RPE en textevents)
et écrit les `.zwo` + un INDEX. Pour ajouter/modifier une séance : éditer la liste
`BANK` dans le script puis relancer.

**Import dans Nolio** (à transmettre au coach) : Calendrier → menu « … » →
« Importer un fichier de séance » → glisser le/les `.zwo` (ou un `.zip`). La
séance devient structurée (graphe en bas) et peut être planifiée puis envoyée au
home-trainer / à la montre.

Si l'utilisateur veut une **séance ponctuelle** au format Nolio (hors banque) :
générer un `.zwo` à la volée depuis `templates/seance.zwo` (`Power` = fraction de
FTP ; RPE + cadence dans `Cadence` et `<textevent>`).

## 7. Garde-fous

- Jamais d'intensité Z4+ sans échauffement complet.
- « Reprise »/« fatigué » → plafonner à tempo, baisser le haut des fourchettes.
- FTP datée (> 6 sem) → watts indicatifs, le RPE prime ; suggérer un re-test.
- Extérieur → donner la **puissance moyenne cible** du bloc + l'ancre RPE.
- Adapter TOUJOURS volumes/répétitions au niveau réel de l'athlète chargé : un
  débutant ne reçoit pas les mêmes volumes qu'un athlète confirmé.
