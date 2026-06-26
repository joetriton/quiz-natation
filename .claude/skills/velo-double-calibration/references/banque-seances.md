# Banque de séances — guide d'utilisation (double calibration)

> 📁 **Le catalogue complet (60 séances) est généré dans
> `references/catalogue-seances.md`** (groupé par filière, avec la/les
> qualité(s) développée(s) et la durée). Les fichiers jouables sont dans
> `bank_zwo/`, `bank_mrc/`, `bank_erg/` — index : `bank_zwo/INDEX.md`.
> Taxonomie des qualités : `references/qualites.md`.
> Tout est produit par `scripts/generate_bank.py` (source unique).

Toutes les séances sont écrites en **%FTP + RPE** → universelles.
Pour un athlète : `watts = round(%FTP/100 × FTP_athlète)`.

## Filières du catalogue (préfixes de code)

| Préfixe | Filière | Qualités dominantes |
|---------|---------|---------------------|
| REC / END | Récupération / Endurance | récup, endurance, lipox, durabilité |
| VEL | Vélocité / Technique | coordination neuromusculaire, cadence |
| TMP | Tempo | endurance soutenue sous-seuil |
| SS | Sweet Spot | charge aérobie optimisée |
| SEU | Seuil | puissance au seuil (FTP) |
| VO2 | VO2max | PMA, tolérance lactique |
| ANA | Anaérobie / Lactique | capacité anaérobie, tolérance lactique |
| FOR | Force | force, force-endurance, force max |
| SPR | Sprint / Neuromusculaire | explosivité, sprint |
| SPE / RACE | Spécifique course | allure cible, gestion, durabilité |

## Allure vélo de course selon la distance (surcouche)
- **Demi-distance (half)** : IF ≈ 0,78 (RPE 5-6) → RACE-HD.
- **Distance complète (L / Ironman, ex. Bayman)** : IF ≈ 0,70 (RPE 3-4) →
  RACE-LD ; voir `bayman.md`.
- **Distances courtes (S/M)** : IF plus haut, plus de seuil/VO2.

## Comment piocher selon la phase (toute prépa endurance)

- **Base** : END-* (volume), VEL-*, SS-1/SS-4, FOR-1/FOR-2/FOR-4.
  Qualités visées : endurance, lipox, durabilité, vélocité, force.
- **Build** : SS-2/SS-3/SS-5, SEU-*, VO2-1/2/3/4/5 (1×/sem max), FOR-1.
  Qualités visées : seuil, sweet spot, PMA, tolérance lactique.
- **Spécifique** : END-4/END-5, SS-3, SPE-1/SPE-2, RACE-LD/HD, bricks.
  Qualités visées : spécifique course, durabilité.
- **Taper (7-10 j)** : volume −40 à −50 %, 1-2 piqûres courtes (ex. VO2-5, SEU-5).
- **Anaérobie/Sprint (ANA-*, SPR-*)** : optionnel, surtout formats courts (S/M)
  ou pour travailler relances/explosivité ; secondaire en longue distance.

Cycle par défaut **3:1** (3 semaines de charge, 1 semaine allégée −30/40 %).

## Repères de volume vélo (full distance / Ironman)

Pour un full, le volume prime. Ordres de grandeur (à caler sur le profil athlète) :
- **Volume vélo hebdo** en build : ~6–12 h (souvent 3–4 séances dont 1 longue clé).
- **Sortie longue clé** : progression **3h30 → 4h → 5h** (END-10/11/12, RACE-LD-5H),
  pic à la durée vélo de course visée. 1×/semaine, allongée graduellement.
- **2e séance d'endurance/tempo longue** : END-11, SS-6, TMP-6 (gros volume sous-seuil).
- **1 séance qualité** : seuil ou VO2 selon la phase.
- En home-trainer : utiliser les alternatives `-HT` (≈ 2 h max) pour remplacer les
  très longues, en acceptant un volume moindre compensé par une densité plus haute.

## Brick
Le `.zwo` ne couvre que le vélo : jouer RACE-LD/HD (ou SPE-2) puis enchaîner la
CAP planifiée séparément.
