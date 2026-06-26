# Banque de séances vélo — catalogue maître (double calibration)

Toutes les séances sont écrites en **%FTP + RPE** → **universelles**.
Pour un athlète : `watts = round(%FTP/100 × FTP_athlète)`.
Échauffement (10–15 min Z1→Z2, + activations si intense) et retour au calme
(5–10 min Z1) implicites sauf mention. Récup = active Z1 sauf indication.

Légende phase : **B** = Base · **U** = Build · **S** = Spécifique/affûtage.
⭐ = pilier des prépas longue distance / triathlon (endurance, tempo/SS, force).

**Banque UNIVERSELLE** : valable pour tout athlète et toute course. Les fichiers
`.zwo` correspondants (dans `bank_zwo/`) sont en %FTP → importables tels quels
dans Nolio pour n'importe quel athlète. Spécificités par épreuve = surcouche :
- Demi-distance (half) : allure vélo de course **IF ≈ 0,78** (RPE 5–6) → RACE-HD.
- Distance complète (L / Ironman, ex. Bayman) : allure **IF ≈ 0,70** (RPE 3–4) →
  RACE-LD ; voir `bayman.md`.
- Distances courtes (S/M) : tolérer un IF plus haut, plus de seuil/VO2.

---

## A. Récupération / endurance

| Code | Nom | Contenu (%FTP · RPE) | Durée | Phase | Note |
|------|-----|----------------------|-------|-------|------|
| END-1 | Récup active | continu 50–60 % · RPE 2 · 90 rpm | 30–45 min | B/U/S | lendemain de séance dure |
| END-2 | Endurance fond ⭐ | continu 65–75 % · RPE 3–4 · 85–90 rpm | 1 h30–3 h | B/U/S | durabilité, base half |
| END-3 | Endurance + cadence | 3×10 min @ 70 % · RPE 4 à **100–105 rpm**, récup 5 min | 1 h30 | B | vélocité |
| END-4 | Longue spécifique ⭐ | 2 h30–4 h @ 65–75 %, dont 3×20 min @ 80 % (RPE 5) | 2 h30–4 h | U/S | tenue d'allure course |

## B. Tempo / Sweet Spot (cœur de la prépa endurance) ⭐

| Code | Nom | Contenu (%FTP · RPE) | Durée | Phase | Note |
|------|-----|----------------------|-------|-------|------|
| TMP-1 | Tempo 3×15 | 3×15 min @ 80–85 % · RPE 5–6 · 90 rpm, récup 5 min | 1 h15 | B/U | allure vélo de course |
| TMP-2 | Tempo continu | 1×40–60 min @ 78–83 % · RPE 5 | 1 h15 | U/S | tenue mentale |
| SS-1 | Sweet Spot 3×12 | 3×12 min @ 88–92 % · RPE 6–7, récup 5 min | 1 h10 | B/U | meilleur rapport charge/fatigue |
| SS-2 | Sweet Spot 2×20 | 2×20 min @ 88–93 % · RPE 6–7, récup 8 min | 1 h15 | U | progression de SS-1 |
| SS-3 | SS sur longue ⭐ | sur sortie 2 h30 : 3×20 min @ 88–90 % · RPE 6, récup 10 min | 2 h30 | U/S | spécificité Bayman |

## C. Seuil (FTP) ⭐

| Code | Nom | Contenu (%FTP · RPE) | Durée | Phase | Note |
|------|-----|----------------------|-------|-------|------|
| SEU-1 | Seuil 2×15 | 2×15 min @ 95–100 % · RPE 7–8, récup 8 min | 1 h10 | U | élève la FTP |
| SEU-2 | Seuil progressif 3×(8/4/2) | 3 blocs : 8'@92 % / 4'@97 % / 2'@103 % · RPE 7→8, récup 4 min | 1 h15 | U | déjà utilisé par Johan |
| SEU-3 | Over-under ⭐ | 4×(2'@90 % + 2'@105 %) ×... · RPE 6↔8, récup 5 min entre séries | 1 h10 | U/S | relances après bosses |
| SEU-4 | Seuil 6x1 / 2x4 / 6x1 | format mixte court-long-court (Johan) · RPE 7–8 | 1 h15 | U | variété |

## D. VO2max / PMA

| Code | Nom | Contenu (%FTP · RPE) | Durée | Phase | Note |
|------|-----|----------------------|-------|-------|------|
| VO2-1 | VO2 5×3' | 5×3 min @ 110–118 % · RPE 8–9, récup 3 min @ 50 % | 1 h | U | plafond aérobie |
| VO2-2 | 30/30 | 2×8×(30"@115 % / 30"@50 %) · RPE 9/2, récup 5 min | 55 min | U | cylindrée |
| VO2-3 | 40/20 | 3×6×(40"@115 % / 20"@50 %) · RPE 9/2 | 1 h | U | densité |

## E. Force / spécifique côte ⭐

| Code | Nom | Contenu (%FTP · RPE) | Durée | Phase | Note |
|------|-----|----------------------|-------|-------|------|
| FOR-1 | Force basse cadence | 6×3 min @ 88–95 % à **50–55 rpm** · RPE jambes 7–8 / cardio 5–6, récup 3 min | 1 h | B/U | efficience en côte |
| FOR-2 | Force 7×2'30 | 7×2'30 @ 90–95 % à 55 rpm · RPE jambes 8, récup 2'30 (Johan) | 1 h | B/U | recrutement |
| FOR-3 | Sprints côte | 8×15" max @ 150 %+ · RPE 10, récup 3 min | 50 min | U | force-vitesse |
| SPE-1 | Simulation parcours vallonné ⭐ | 5×(côte 4 min @ 95–100 % RPE 7-8 + relance 1 min @ 105 % RPE 8 + retour allure 75 % RPE 5) | ~1 h45 | S | profil accordéon |

## F. Spécifique course (partie vélo des bricks) ⭐

| Code | Nom | Contenu | Durée | Phase | Note |
|------|-----|---------|-------|-------|------|
| RACE-LD | Allure course longue distance | 2 h continu @ 68–72 % (IF ~0,70) · RPE 3–4 — + CAP enchaînée hors .zwo | 2 h | S | full / Ironman, ex. Bayman |
| RACE-HD | Allure course demi-distance | 1 h continu @ 78–80 % (IF ~0,78) · RPE 5–6 — + CAP enchaînée hors .zwo | 1 h | S | half / 70.3 |

> Brick complet (vélo + CAP) : jouer la partie vélo RACE-LD/HD dans Nolio puis
> enchaîner la CAP planifiée séparément (le .zwo ne couvre que le vélo).

---

## Comment piocher selon la phase (toute prépa endurance)

- **Base (semaines lointaines)** : END-2, END-3, SS-1, FOR-1/FOR-2. Volume ↑↑ (durabilité), intensité modérée.
- **Build** : SS-2/SS-3, SEU-1/2 (entretien), SEU-3, VO2-1 (1×/sem max, build précoce), FOR-1, END-4. Endurance longue prioritaire.
- **Spécifique** : END-4, SS-3, SPE-1, RACE-LD/HD (selon distance), bricks. Tout devient "couleur course" (longue distance → IF ~0,70, longues sorties 5–6 h ; demi → IF ~0,78).
- **Taper (7–10 j)** : volume −40 à −50 %, garder 1–2 piqûres d'intensité courtes
  (ex. 3×3 min seuil), fraîcheur prioritaire.

Cycle par défaut **3:1** (3 semaines de charge, 1 semaine allégée −30/40 %).
