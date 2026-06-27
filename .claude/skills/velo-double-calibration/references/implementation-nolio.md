# Implémenter la bibliothèque dans Nolio

La bibliothèque = **60 séances** (75 fichiers/​format avec les
alternatives home-trainer `-HT`). Puissance en %FTP → **Nolio applique la FTP de
chaque athlète** ; le RPE s'affiche pendant la séance. Charge route = charge HT (UA).

## Option A — Import groupé (recommandé)

1. Choisir le format : **`.zwo`** ou **`.mrc`** (universels, %FTP). `.erg` = watts
   fixes pour FTP 228 W (régénérer avec `--ftp` pour un autre athlète).
2. Récupérer l'archive : `bank_zwo.zip` (ou `bank_mrc.zip` / `bank_erg.zip`).
3. Dans Nolio : Calendrier → menu **« … »** → **« Importer un fichier de séance »**
   → déposer le `.zip` (Nolio accepte une archive contenant tous les fichiers).
4. Les séances arrivent **structurées** (graphe) → réutilisables comme modèles,
   planifiables, et envoyées au home-trainer / à la montre.

## Option B — Saisie manuelle dans le constructeur

Suivre `references/specification-complete.md` : chaque séance y est détaillée
bloc par bloc (durée · %FTP · watts · cadence · RPE). Recréer chaque bloc dans
le workout builder Nolio (échauffement / intervalle Répéter N / récup / retour au calme).

## Avant d'importer : régler l'athlète

- Renseigner la **FTP** de l'athlète dans Nolio (les % se convertissent en watts).
- Vérifier/définir les zones si besoin (voir `references/zones-rpe.md`).

## Fichiers de référence

- `references/catalogue-seances.md` — catalogue (filière, durée, UA, qualités)
- `references/alternatives-ht.md` — durées + alternatives HT à charge égale
- `references/specification-complete.md` — détail bloc par bloc
- `references/qualites.md` — taxonomie des qualités
- `bank_zwo/INDEX.md` — index des fichiers

## Régénérer / personnaliser

```
python3 scripts/generate_bank.py            # FTP .erg = 228 W
python3 scripts/generate_bank.py --ftp 250  # .erg pour FTP 250 W
```
Ajouter une séance = une entrée `add(...)` ; une alternative HT = une entrée
`HT_ALTS` (sa durée se cale automatiquement sur l'UA de la séance route).

