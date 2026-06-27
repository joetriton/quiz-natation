# Référence — Calibration %FTP ↔ RPE ↔ Watts

FTP de référence : **228 W** (Johan, 64,2 kg ≈ 3,55 W/kg).
Source zones : Strava `get_athlete_zones` (modèle 7 zones type Coggan).

## Table maîtresse

| Zone | Nom | %FTP bas | %FTP haut | W bas | W haut | RPE bas | RPE haut | FC indicative |
|------|-----|---------:|----------:|------:|------:|--------:|---------:|---------------|
| Z1 | Récupération | 0 | 55 | 0 | 125 | 1 | 2 | < 119 |
| Z2 | Endurance | 56 | 75 | 128 | 171 | 3 | 4 | 119–147 |
| Z3 | Tempo | 76 | 90 | 173 | 205 | 5 | 6 | 148–162 |
| SS | Sweet Spot | 88 | 94 | 200 | 214 | 6 | 7 | 158–165 |
| Z4 | Seuil | 91 | 105 | 207 | 239 | 7 | 8 | 163–177 |
| Z5 | VO2max | 106 | 120 | 242 | 274 | 8 | 9 | 178+ |
| Z6 | Anaérobie | 121 | 150 | 276 | 342 | 9 | 10 | n/a (trop court) |
| Z7 | Neuromusculaire | 151 | 300 | 343 | — | 10 | 10 | n/a |

Zones FC issues du profil (FCmax-based) : Z1 ≤118, Z2 119–147, Z3 148–162,
Z4 163–177, Z5 178+. La FC réagit avec retard : ne pas piloter les intervalles
courts (< 3 min) à la FC.

## Échelle RPE détaillée (CR10 simplifiée)

| RPE | Description | Test de parole |
|----:|-------------|----------------|
| 1–2 | Très facile, récup | Je chante |
| 3 | Facile | Phrases complètes sans effort |
| 4 | Confortable | Conversation fluide |
| 5 | Modéré | Phrases longues, léger essoufflement |
| 6 | Soutenu | Phrases courtes |
| 7 | Dur | Quelques mots |
| 8 | Très dur | Un mot à la fois |
| 9 | Extrêmement dur | Monosyllabes |
| 10 | Maximal | Parole impossible |

## Conversion rapide

```
watts_cible = round(pourcentage_FTP / 100 * FTP)
fraction_zwo = pourcentage_FTP / 100        # ex. 97 % -> 0.97
```

Pour une autre FTP, recalculer uniquement les colonnes Watts. Les colonnes %FTP
et RPE restent valides (le RPE est par construction indépendant de la valeur
absolue de FTP — c'est tout l'intérêt de la double calibration).

## Cas particuliers

- **Force basse cadence (50–60 rpm)** : dissocier RPE_jambes (7–8) et
  RPE_cardio (5–6). Puissance Z3–Z4.
- **Vélocité (100–110 rpm)** : puissance Z2, RPE cardio 4–5, focus gestuel.
- **Extérieur** : la puissance fluctue ±10–15 % ; donner la moyenne cible du bloc
  et laisser le RPE arbitrer dans les bosses / le vent.
- **FTP douteuse** : si RPE > fourchette de 1 pt sur les blocs seuil pendant
  2–3 séances → baisser la FTP de 3–5 W ou re-tester. Si RPE < fourchette →
  FTP probablement sous-estimée.
