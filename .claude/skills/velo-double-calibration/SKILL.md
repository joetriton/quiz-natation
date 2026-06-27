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
2. Partir de `references/catalogue-seances.md` (**60 séances** classées par
   filière, chacune avec sa/ses **qualité(s) développée(s)** et sa durée ;
   taxonomie dans `references/qualites.md`, guide dans `references/banque-seances.md`).
   Sélectionner selon les **qualités à travailler** (points faibles de l'athlète
   + phase + spécificité course). **Personnaliser** : convertir en watts,
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

## 6 bis. Sortie Nolio (.zwo / .mrc / .erg) — séances importables et JOUABLES

Nolio importe `.zwo`, `.erg`, `.mrc`, `.json` (intervals.icu) et `.fit` pour créer
des séances structurées jouables (envoyées home-trainer/montre). La banque est
générée dans **3 formats** (source unique = segments neutres, donc identiques) :

| Format | Dossier | Intensité | Athlète-indépendant ? |
|--------|---------|-----------|-----------------------|
| `.zwo` | `bank_zwo/` | fraction de FTP | **Oui** (Nolio applique la FTP) |
| `.mrc` | `bank_mrc/` | % de FTP | **Oui** |
| `.erg` | `bank_erg/` | **watts absolus** | Non — calculés pour une FTP donnée |

Le **RPE** apparaît à l'écran : `<textevent>` (.zwo) et `[COURSE TEXT]` (.mrc/.erg).

> Recommandation : privilégier **`.zwo` ou `.mrc`** (universels). N'utiliser
> `.erg` que si un athlète a besoin de watts fixes ; il faut alors le régénérer à
> sa FTP.

**Charge en UA :** chaque séance porte une charge estimée en UA (type TSS),
`UA = 100 × Σ(durée_h × IF²)` (IF = %FTP du bloc ; rampe intégrée). Affichée dans
le catalogue, l'INDEX et `alternatives-ht.md`.

**Alternative home-trainer (à charge égale) :** chaque séance a une durée + UA et
un équivalent HT dans `references/alternatives-ht.md`. Les séances structurées
sont déjà optimales en HT (jouées telles quelles, UA identique) ; les séances
longues/route ont une **alternative HT calée pour avoir exactement la même UA**
que la séance route (intensité plus haute indoor → même charge en moins de temps ;
fichiers `<CODE>-HT_*`). Ainsi, remplacer une séance route par sa version HT **ne
change pas la charge planifiée**. Le calage UA est automatique dans le générateur
(`scale_ht_to_load`) : pour modifier une alternative, éditer son entrée dans
`HT_ALTS` (intensités/structure) et relancer — la durée se recale sur l'UA cible.

**(Re)générer / étendre la banque :**
```
python3 scripts/generate_bank.py                 # .erg calculé pour FTP 228 W
python3 scripts/generate_bank.py --ftp 250       # .erg pour un athlète à 250 W
```
La banque est définie comme données dans la liste `BANK` du script (puissances en
%FTP, RPE en messages). Pour ajouter/modifier une séance : éditer `BANK` et
relancer. Index dans `bank_zwo/INDEX.md`.

**Import dans Nolio** (à transmettre au coach) : Calendrier → menu « … » →
« Importer un fichier de séance » → glisser le/les fichiers (ou un `.zip`). La
séance devient structurée (graphe en bas), planifiable et envoyable au
home-trainer / à la montre.

**Implémentation complète de la bibliothèque** — voir
`references/implementation-nolio.md` (guide pas-à-pas). Deux voies :
- **Import groupé** : archives `bank_zwo.zip` / `bank_mrc.zip` / `bank_erg.zip`
  (toutes les séances + alternatives HT) déposées d'un coup dans Nolio.
- **Saisie manuelle** : `references/specification-complete.md` détaille chaque
  séance bloc par bloc (durée · %FTP · watts@FTP · cadence · RPE) pour la
  recréer dans le constructeur Nolio.

Pour une **séance ponctuelle** hors banque : ajouter une entrée temporaire dans
`BANK` et régénérer, ou produire un `.zwo` à la volée depuis `templates/seance.zwo`.

## 7. Garde-fous

- Jamais d'intensité Z4+ sans échauffement complet.
- « Reprise »/« fatigué » → plafonner à tempo, baisser le haut des fourchettes.
- FTP datée (> 6 sem) → watts indicatifs, le RPE prime ; suggérer un re-test.
- Extérieur → donner la **puissance moyenne cible** du bloc + l'ancre RPE.
- Adapter TOUJOURS volumes/répétitions au niveau réel de l'athlète chargé : un
  débutant ne reçoit pas les mêmes volumes qu'un athlète confirmé.
