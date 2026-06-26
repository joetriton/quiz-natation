#!/usr/bin/env python3
"""
Générateur de la banque de séances vélo (double calibration %FTP + RPE).

Source unique = liste de SEGMENTS neutres par séance. Chaque séance porte aussi
sa FILIÈRE et ses QUALITÉS développées (principale + secondaire).

Trois renderers d'export, tous importables dans Nolio :
  - .zwo  (Zwift / Nolio)            : puissance en fraction de FTP  -> universel
  - .mrc  (TrainerRoad / PerfPRO...) : puissance en % de FTP         -> universel
  - .erg  (idem)                     : puissance en WATTS absolus    -> par FTP

Sorties additionnelles :
  - bank_zwo/INDEX.md                : index 3 formats + qualités
  - references/catalogue-seances.md  : catalogue lisible groupé par filière
  - references/qualites.md           : taxonomie des qualités

Usage:
    python3 generate_bank.py [--ftp 228] [--out DOSSIER_RACINE]
"""
import os
import sys
import re
import argparse
from xml.sax.saxutils import escape

# --------------------------------------------------------------------------
# Taxonomie des qualités développées
# --------------------------------------------------------------------------
QUALITIES = {
    "RECUP":  "Récupération / régénération",
    "ENDUR":  "Endurance aérobie fondamentale",
    "LIPOX":  "Métabolisme lipidique (fat-max, oxydation des graisses)",
    "DURAB":  "Durabilité / résistance à la fatigue (tenue de puissance)",
    "VELO":   "Vélocité & coordination neuromusculaire (cadence, fluidité)",
    "TEMPO":  "Endurance soutenue sous-seuil (capacité aérobie / tempo)",
    "SS":     "Charge aérobie optimisée (sweet spot)",
    "SEUIL":  "Puissance au seuil (FTP / seuil lactique)",
    "VO2":    "Consommation maximale d'oxygène (PMA / VO2max)",
    "TOLLAC": "Tolérance lactique / capacité à répéter l'effort",
    "ANA":    "Capacité anaérobie (production lactique)",
    "FORCE":  "Force spécifique / recrutement musculaire",
    "FENDUR": "Force-endurance (force tenue dans la durée)",
    "FMAX":   "Force maximale (couple, basse cadence forte résistance)",
    "SPRINT": "Puissance neuromusculaire / explosivité (sprint)",
    "SPEC":   "Spécifique course (allure cible, gestion d'effort, nutrition)",
}
FILIERE_ORDER = ["Récupération / Endurance", "Vélocité / Technique", "Tempo",
                 "Sweet Spot", "Seuil", "VO2max", "Anaérobie / Lactique",
                 "Force", "Sprint / Neuromusculaire", "Spécifique course"]

# --------------------------------------------------------------------------
# Représentation neutre : segment = rampe p0->p1 (fractions FTP) sur dur s.
# --------------------------------------------------------------------------
def seg(dur, p0, p1=None, cad=None, msg=None):
    return {"dur": int(dur), "p0": float(p0),
            "p1": float(p0 if p1 is None else p1), "cad": cad, "msg": msg}

def wu(dur, p0, p1, msg="Échauffement progressif — RPE 2->4"):
    return [seg(dur, p0, p1, msg=msg)]

def cd(dur=480, p0=0.60, p1=0.45, msg="Retour au calme — RPE 2"):
    return [seg(dur, p0, p1, msg=msg)]

def ss(dur, p, cad=None, msg=None):
    return [seg(dur, p, p, cad=cad, msg=msg)]

def ints(repeat, on_dur, on_p, off_dur, off_p, cad=None, cad_rest=None,
         rpe_on="EFFORT", rpe_off="RÉCUP"):
    out = []
    for _ in range(int(repeat)):
        out.append(seg(on_dur, on_p, on_p, cad=cad, msg=rpe_on))
        out.append(seg(off_dur, off_p, off_p, cad=cad_rest, msg=rpe_off))
    return out

WU = wu(600, 0.50, 0.72)
WU_INT = (wu(600, 0.50, 0.72)
          + ints(3, 30, 1.05, 60, 0.50, rpe_on="RPE 8 (activation)", rpe_off="RPE 2")
          + ss(120, 0.55, msg="Transition avant le corps — RPE 2"))
CD = cd(480)

# --------------------------------------------------------------------------
# BANQUE  ~50 séances. add(code, nom, filière, q_principale, q_secondaire, desc, segments)
# --------------------------------------------------------------------------
BANK = []
def add(code, name, filiere, q1, q2, desc, segs):
    BANK.append({"code": code, "name": name, "filiere": filiere,
                 "q1": q1, "q2": q2, "desc": desc, "segs": segs})

# ===== A. Récupération / Endurance =====
add("REC-1", "Spin facile 30'", "Récupération / Endurance", "RECUP", "VELO",
    "Récupération pure 30 min, < 50% FTP, cadence souple.",
    wu(300, 0.40, 0.50) + ss(1500, 0.50, cad=95, msg="Spin facile <50% FTP · RPE 1-2") + cd(300, 0.50, 0.40))

add("END-1", "Récup active", "Récupération / Endurance", "RECUP", "ENDUR",
    "Récupération active. 50-60% FTP, RPE 2.",
    wu(300, 0.45, 0.55) + ss(2100, 0.55, cad=90, msg="Récup active 50-60% FTP · RPE 2 — je peux chanter") + cd(300, 0.55, 0.45))

add("END-2", "Endurance fond 70'", "Récupération / Endurance", "ENDUR", "LIPOX",
    "Endurance fondamentale. 65-75% FTP, RPE 3-4. Base aérobie.",
    WU + ss(4200, 0.70, cad=88, msg="Endurance 65-75% FTP · RPE 3-4 — conversation fluide") + CD)

add("END-3", "Endurance + cadence", "Récupération / Endurance", "ENDUR", "VELO",
    "Endurance + vélocité. Blocs à 100-105 rpm.",
    WU + ints(3, 600, 0.70, 300, 0.60, cad=103, cad_rest=90,
              rpe_on="68-72% FTP · RPE 4 — 100-105 rpm", rpe_off="55-65% FTP · RPE 2 — cadence libre") + CD)

add("END-4", "Longue spécifique allure", "Récupération / Endurance", "DURAB", "SPEC",
    "Sortie longue avec blocs à l'allure de course. Durabilité.",
    WU + ss(1800, 0.70, cad=88, msg="Endurance 65-75% FTP · RPE 3-4")
    + ints(3, 1200, 0.80, 600, 0.68, cad=88, rpe_on="Allure course 78-82% FTP · RPE 5", rpe_off="Endurance 65-72% FTP · RPE 3")
    + ss(1800, 0.70, msg="Retour endurance 65-75% FTP · RPE 3-4") + CD)

add("END-5", "Endurance longue 2h30", "Récupération / Endurance", "ENDUR", "DURAB",
    "Sortie longue continue Z2. Volume / durabilité aérobie.",
    WU + ss(8400, 0.70, cad=88, msg="Endurance 65-75% FTP · RPE 3-4 — régulier, boire/manger") + CD)

add("END-6", "Endurance progressive", "Récupération / Endurance", "ENDUR", "DURAB",
    "Endurance montant de 65% à 78% FTP. Tenue d'allure croissante.",
    WU + ss(1200, 0.65, cad=88, msg="65% FTP · RPE 3") + ss(1200, 0.70, cad=88, msg="70% FTP · RPE 3-4")
    + ss(1200, 0.74, cad=88, msg="74% FTP · RPE 4") + ss(900, 0.78, cad=90, msg="78% FTP · RPE 5") + CD)

add("END-7", "Fat-max 90'", "Récupération / Endurance", "LIPOX", "ENDUR",
    "Endurance basse 60-65% FTP, respiration nasale. Oxydation des graisses.",
    WU + ss(5400, 0.62, cad=85, msg="Fat-max 60-65% FTP · RPE 3 — respiration nasale") + CD)

end8 = list(WU)
for i in range(8):
    end8 += ss(174, 0.70, cad=90, msg="Endurance 70% FTP · RPE 3-4")
    end8 += ss(6, 1.50, cad=100, msg="Micro-burst 6s ~150% FTP · RPE 9 — rester assis")
end8 += CD
add("END-8", "Endurance + micro-bursts", "Récupération / Endurance", "ENDUR", "SPRINT",
    "Endurance avec micro-sprints de 6s toutes les 3 min. Recrutement sans fatigue.", end8)

add("END-9", "Endurance negative split", "Récupération / Endurance", "DURAB", "ENDUR",
    "1ère moitié à 66%, 2e à 74% FTP. Finir plus fort (durabilité).",
    WU + ss(2400, 0.66, cad=88, msg="1ère moitié 66% FTP · RPE 3") + ss(2400, 0.74, cad=90, msg="2e moitié 74% FTP · RPE 4-5 — finir fort") + CD)

add("END-10", "Sortie longue 3h30", "Récupération / Endurance", "DURAB", "ENDUR",
    "Sortie longue Z2 ~3h30. Socle de volume longue distance.",
    WU + ss(11400, 0.68, cad=86, msg="Endurance 65-72% FTP · RPE 3-4 — boire/manger régulièrement") + CD)

add("END-11", "Longue IM + 3x30' tempo", "Récupération / Endurance", "DURAB", "SPEC",
    "Sortie longue ~4h15 avec 3x30' tempo. Volume + tenue d'allure full distance.",
    WU + ss(3000, 0.68, cad=86, msg="Endurance 65-70% FTP · RPE 3")
    + ints(3, 1800, 0.80, 600, 0.66, cad=86, rpe_on="Tempo 78-82% FTP · RPE 5", rpe_off="Endurance 64-68% FTP · RPE 3")
    + ss(4200, 0.66, cad=86, msg="Endurance retour 64-68% FTP · RPE 3 — nutrition") + CD)

add("END-12", "Très longue endurance 5h", "Récupération / Endurance", "ENDUR", "DURAB",
    "Très longue sortie Z2 ~5h. Durabilité maximale, simulation de durée IM.",
    WU + ss(16800, 0.66, cad=85, msg="Endurance 63-70% FTP · RPE 3 — nutrition +++ / gestion") + CD)

# ===== B. Vélocité / Technique =====
add("VEL-1", "Vélocité 6x3'", "Vélocité / Technique", "VELO", "ENDUR",
    "6x3 min à 108-112 rpm, 70% FTP. Fluidité du coup de pédale.",
    WU + ints(6, 180, 0.70, 60, 0.55, cad=110, cad_rest=85,
              rpe_on="70% FTP · 108-112 rpm · RPE 4 — rond", rpe_off="récup · RPE 2") + CD)

vel2 = list(WU)
for i in range(8):
    vel2 += ss(30, 0.55, cad=80, msg="Jambe DROITE seule · RPE 3 — gainage") + ss(30, 0.55, cad=80, msg="Jambe GAUCHE seule · RPE 3")
    vel2 += ss(60, 0.65, cad=95, msg="2 jambes · RPE 3")
vel2 += CD
add("VEL-2", "Jambe seule (single-leg)", "Vélocité / Technique", "VELO", "FORCE",
    "8x(30s jambe droite / 30s gauche / 1' deux jambes). Coordination & déséquilibres.", vel2)

add("VEL-3", "Spin-ups 10x30\"", "Vélocité / Technique", "VELO", "SPRINT",
    "10x30s à 115-125 rpm sans rebond. Vitesse gestuelle.",
    WU + ints(10, 30, 0.60, 90, 0.50, cad=120, cad_rest=85,
              rpe_on="115-125 rpm · 60% FTP · RPE 5 — rester rond", rpe_off="récup · RPE 2") + CD)

add("VEL-4", "Pyramide de cadence", "Vélocité / Technique", "VELO", "ENDUR",
    "Cadence 80->110->80 rpm à 62% FTP. Plage de cadence.",
    WU + ss(180, 0.62, cad=80, msg="62% · 80 rpm") + ss(180, 0.62, cad=90, msg="62% · 90 rpm")
    + ss(180, 0.62, cad=100, msg="62% · 100 rpm") + ss(180, 0.62, cad=110, msg="62% · 110 rpm")
    + ss(180, 0.62, cad=100, msg="62% · 100 rpm") + ss(180, 0.62, cad=90, msg="62% · 90 rpm") + CD)

# ===== C. Tempo =====
add("TMP-1", "Tempo 3x15", "Tempo", "TEMPO", None,
    "Tempo 3x15 min à 80-85% FTP, RPE 5-6.",
    WU + ints(3, 900, 0.83, 300, 0.55, cad=90, rpe_on="Tempo 80-85% FTP · RPE 5-6 — phrases courtes", rpe_off="Récup 50-58% FTP · RPE 2") + CD)

add("TMP-2", "Tempo continu 50'", "Tempo", "TEMPO", "DURAB",
    "Tempo continu 50 min à 78-83% FTP, RPE 5.",
    WU + ss(3000, 0.80, cad=90, msg="Tempo continu 78-83% FTP · RPE 5 — régulier") + CD)

add("TMP-3", "Tempo 2x25", "Tempo", "TEMPO", "DURAB",
    "Tempo 2x25 min à 80-84% FTP. Tenue mentale longue.",
    WU + ints(2, 1500, 0.82, 420, 0.55, cad=90, rpe_on="Tempo 80-84% FTP · RPE 5-6", rpe_off="récup · RPE 2") + CD)

tmp4 = list(WU)
for i in range(4):
    tmp4 += ss(180, 0.84, cad=60, msg="Tempo 84% FTP · 60 rpm (côte) · RPE jambes 6")
    tmp4 += ss(180, 0.80, cad=95, msg="Tempo 80% FTP · 95 rpm (plat) · RPE 5")
tmp4 += CD
add("TMP-4", "Tempo vallonné (cadence variée)", "Tempo", "TEMPO", "FORCE",
    "Alternance 60 rpm (côte) / 95 rpm (plat) à tempo. Spécifique terrain.", tmp4)

add("TMP-5", "Tempo progressif 3x12", "Tempo", "TEMPO", "SS",
    "3x12 min montant 80->84->88% FTP. Transition tempo vers sweet spot.",
    WU + ss(720, 0.80, cad=90, msg="12' @ 80% FTP · RPE 5") + ss(300, 0.55, msg="récup · RPE 2")
    + ss(720, 0.84, cad=90, msg="12' @ 84% FTP · RPE 6") + ss(300, 0.55, msg="récup · RPE 2")
    + ss(720, 0.88, cad=90, msg="12' @ 88% FTP · RPE 6-7") + CD)

add("TMP-6", "Tempo sur longue 3x30'", "Tempo", "TEMPO", "DURAB",
    "Sur sortie ~2h15 : 3x30 min à 78-82% FTP. Gros volume tempo full distance.",
    WU + ints(3, 1800, 0.80, 600, 0.65, cad=87, rpe_on="Tempo 78-82% FTP · RPE 5", rpe_off="Endurance 62-68% FTP · RPE 3") + CD)

# ===== D. Sweet Spot =====
add("SS-1", "Sweet Spot 3x12", "Sweet Spot", "SS", None,
    "Sweet Spot 3x12 min à 88-92% FTP, RPE 6-7.",
    WU_INT + ints(3, 720, 0.90, 300, 0.55, cad=90, rpe_on="Sweet Spot 88-92% FTP · RPE 6-7 — tenable", rpe_off="Récup 50-58% FTP · RPE 2") + CD)

add("SS-2", "Sweet Spot 2x20", "Sweet Spot", "SS", "SEUIL",
    "Sweet Spot 2x20 min à 88-93% FTP, RPE 6-7.",
    WU_INT + ints(2, 1200, 0.91, 480, 0.55, cad=90, rpe_on="Sweet Spot 88-93% FTP · RPE 6-7", rpe_off="Récup 50-58% FTP · RPE 2") + CD)

add("SS-3", "Sweet Spot sur longue 3x20", "Sweet Spot", "SS", "DURAB",
    "Sur sortie longue : 3x20 min à 88-90% FTP, RPE 6.",
    WU + ss(1200, 0.70, msg="Endurance 65-75% FTP · RPE 3-4")
    + ints(3, 1200, 0.89, 600, 0.68, cad=88, rpe_on="Sweet Spot 88-90% FTP · RPE 6", rpe_off="Endurance 65-72% FTP · RPE 3")
    + ss(900, 0.68, msg="Retour endurance 65-72% FTP · RPE 3") + CD)

add("SS-4", "Sweet Spot 4x10", "Sweet Spot", "SS", None,
    "Sweet Spot 4x10 min à 88-92% FTP, récup 4 min.",
    WU_INT + ints(4, 600, 0.90, 240, 0.55, cad=90, rpe_on="Sweet Spot 88-92% FTP · RPE 6-7", rpe_off="récup · RPE 2") + CD)

add("SS-5", "Sweet Spot 2x30", "Sweet Spot", "SS", "DURAB",
    "Sweet Spot 2x30 min à 88-90% FTP. Gros volume sous-seuil.",
    WU_INT + ints(2, 1800, 0.89, 600, 0.55, cad=90, rpe_on="Sweet Spot 88-90% FTP · RPE 6-7", rpe_off="récup · RPE 2") + CD)

add("SS-6", "Sweet Spot sur longue 4x25'", "Sweet Spot", "SS", "DURAB",
    "Sur sortie ~2h30 : 4x25 min à 88-90% FTP. Gros volume sous-seuil full distance.",
    WU_INT + ints(4, 1500, 0.89, 420, 0.60, cad=88, rpe_on="Sweet Spot 88-90% FTP · RPE 6-7", rpe_off="Endurance 58-62% FTP · RPE 3") + CD)

# ===== E. Seuil =====
add("SEU-1", "Seuil 2x15", "Seuil", "SEUIL", None,
    "Seuil 2x15 min à 95-100% FTP, RPE 7-8.",
    WU_INT + ints(2, 900, 0.98, 480, 0.50, cad=90, rpe_on="Seuil 95-100% FTP · RPE 7-8 — mots isolés", rpe_off="Récup 45-55% FTP · RPE 2") + CD)

seu2 = list(WU_INT)
for i in range(3):
    seu2 += (ss(480, 0.92, cad=90, msg=f"Bloc {i+1} — 8' @ 92% FTP · RPE 7")
             + ss(240, 0.97, cad=90, msg=f"Bloc {i+1} — 4' @ 97% FTP · RPE 7,5")
             + ss(120, 1.03, cad=90, msg=f"Bloc {i+1} — 2' @ 103% FTP · RPE 8"))
    if i < 2:
        seu2 += ss(240, 0.52, msg="Récup · RPE 2")
seu2 += CD
add("SEU-2", "Seuil progressif 3x(8-4-2)", "Seuil", "SEUIL", None,
    "3 blocs 8'@92% / 4'@97% / 2'@103% FTP, RPE 7->8, récup 4 min.", seu2)

seu3 = list(WU_INT)
for s in range(2):
    for _ in range(4):
        seu3 += ss(120, 0.90, cad=90, msg="UNDER 90% FTP · RPE 6") + ss(120, 1.05, cad=90, msg="OVER 105% FTP · RPE 8")
    if s < 1:
        seu3 += ss(300, 0.52, msg="Récup série · RPE 2")
seu3 += CD
add("SEU-3", "Seuil over-under 2x(4x2-2)", "Seuil", "SEUIL", "TOLLAC",
    "2 séries de 4x(2'@90% + 2'@105% FTP), RPE 6<->8, récup 5 min.", seu3)

add("SEU-4", "Seuil 6x1 / 2x4 / 6x1", "Seuil", "SEUIL", None,
    "Format mixte court-long-court à 97-100% FTP, RPE 7-8.",
    WU_INT + ints(6, 60, 1.00, 60, 0.55, cad=95, rpe_on="1' @ 100% FTP · RPE 7-8", rpe_off="RPE 2")
    + ss(300, 0.52, msg="Récup bloc · RPE 2")
    + ints(2, 240, 0.97, 180, 0.52, cad=90, rpe_on="4' @ 97% FTP · RPE 7-8", rpe_off="RPE 2")
    + ss(300, 0.52, msg="Récup bloc · RPE 2")
    + ints(6, 60, 1.00, 60, 0.55, cad=95, rpe_on="1' @ 100% FTP · RPE 7-8", rpe_off="RPE 2") + CD)

add("SEU-5", "Seuil 3x10", "Seuil", "SEUIL", None,
    "Seuil 3x10 min à 96-100% FTP, récup 5 min.",
    WU_INT + ints(3, 600, 0.98, 300, 0.50, cad=90, rpe_on="Seuil 96-100% FTP · RPE 7-8", rpe_off="récup · RPE 2") + CD)

add("SEU-6", "Seuil 2x20", "Seuil", "SEUIL", "DURAB",
    "Seuil 2x20 min à 93-97% FTP. Gros volume au seuil.",
    WU_INT + ints(2, 1200, 0.95, 480, 0.50, cad=90, rpe_on="Seuil 93-97% FTP · RPE 7-8", rpe_off="récup · RPE 2") + CD)

seu7 = list(WU_INT)
for s in range(3):
    for _ in range(3):
        seu7 += ss(120, 0.90, cad=90, msg="under 90% FTP · RPE 6") + ss(60, 1.05, cad=90, msg="over 105% FTP · RPE 8")
    if s < 2:
        seu7 += ss(180, 0.52, msg="récup · RPE 2")
seu7 += CD
add("SEU-7", "Seuil over-under 3x9", "Seuil", "SEUIL", "TOLLAC",
    "3 blocs de 9 min en 2'under/1'over (90%/105% FTP). Relances au seuil.", seu7)

# ===== F. VO2max =====
add("VO2-1", "VO2 5x3'", "VO2max", "VO2", None,
    "VO2max 5x3 min à 110-118% FTP, RPE 8-9, récup 3 min.",
    WU_INT + ints(5, 180, 1.13, 180, 0.50, cad=95, rpe_on="VO2 110-118% FTP · RPE 8-9 — respiration max", rpe_off="Récup 45-55% FTP · RPE 2") + CD)

vo2_2 = list(WU_INT)
for s in range(2):
    vo2_2 += ints(8, 30, 1.15, 30, 0.50, cad=100, rpe_on="30s @ 115% FTP · RPE 9", rpe_off="30s · RPE 2")
    if s < 1:
        vo2_2 += ss(300, 0.50, msg="Récup série · RPE 2")
vo2_2 += CD
add("VO2-2", "VO2 30-30 2x8", "VO2max", "VO2", "TOLLAC",
    "30/30 : 2 séries de 8x(30s@115% / 30s@50% FTP), RPE 9/2.", vo2_2)

vo2_3 = list(WU_INT)
for s in range(3):
    vo2_3 += ints(6, 40, 1.15, 20, 0.50, cad=100, rpe_on="40s @ 115% FTP · RPE 9", rpe_off="20s · RPE 2")
    if s < 2:
        vo2_3 += ss(240, 0.50, msg="Récup série · RPE 2")
vo2_3 += CD
add("VO2-3", "VO2 40-20 3x6", "VO2max", "VO2", "TOLLAC",
    "40/20 : 3 séries de 6x(40s@115% / 20s@50% FTP), RPE 9/2.", vo2_3)

add("VO2-4", "VO2 5x4'", "VO2max", "VO2", "DURAB",
    "VO2max 5x4 min à 108-112% FTP, récup 3 min. Format long, soutenable.",
    WU_INT + ints(5, 240, 1.10, 180, 0.50, cad=95, rpe_on="VO2 108-112% FTP · RPE 8-9", rpe_off="récup · RPE 2") + CD)

add("VO2-5", "VO2 6x2'", "VO2max", "VO2", None,
    "VO2max 6x2 min à 113-118% FTP, récup 2 min. Intensité haute.",
    WU_INT + ints(6, 120, 1.15, 120, 0.50, cad=100, rpe_on="VO2 113-118% FTP · RPE 9", rpe_off="récup · RPE 2") + CD)

vo2_6 = list(WU_INT)
for s in range(3):
    vo2_6 += ints(10, 15, 1.20, 15, 0.50, cad=105, rpe_on="15s @ 120% FTP · RPE 9", rpe_off="15s · RPE 2")
    if s < 2:
        vo2_6 += ss(240, 0.50, msg="Récup série · RPE 2")
vo2_6 += CD
add("VO2-6", "VO2 15-15 3x10", "VO2max", "VO2", "VELO",
    "15/15 : 3 séries de 10x(15s@120% / 15s@50% FTP). Densité + vitesse.", vo2_6)

add("VO2-7", "VO2 4x5'", "VO2max", "VO2", "DURAB",
    "VO2max 4x5 min à 106-110% FTP, récup 5 min. Tenue longue à PMA.",
    WU_INT + ints(4, 300, 1.08, 300, 0.50, cad=95, rpe_on="VO2 106-110% FTP · RPE 8-9", rpe_off="récup · RPE 2") + CD)

# ===== G. Anaérobie / Lactique =====
add("ANA-1", "Anaérobie 5x1'", "Anaérobie / Lactique", "ANA", "TOLLAC",
    "5x1 min à 118-122% FTP, récup 4 min. Capacité anaérobie.",
    WU_INT + ints(5, 60, 1.20, 240, 0.50, cad=100, rpe_on="Anaérobie 118-122% FTP · RPE 9", rpe_off="récup longue · RPE 2") + CD)

add("ANA-2", "Lactique 6x40\"", "Anaérobie / Lactique", "ANA", "TOLLAC",
    "6x40s à ~130% FTP, récup 3 min. Production/tolérance lactique.",
    WU_INT + ints(6, 40, 1.30, 200, 0.50, cad=100, rpe_on="Lactique ~130% FTP · RPE 9-10", rpe_off="récup · RPE 2") + CD)

ana3 = list(WU_INT)
for s in range(4):
    ana3 += ints(4, 15, 1.50, 45, 0.50, cad=110, rpe_on="Attaque 15s ~150% FTP · RPE 10", rpe_off="récup 45s · RPE 2")
    if s < 3:
        ana3 += ss(180, 0.50, msg="récup série · RPE 2")
ana3 += CD
add("ANA-3", "Attaques 4x(4x15\")", "Anaérobie / Lactique", "ANA", "SPRINT",
    "4 séries de 4x15s à ~150% FTP. Répétition d'attaques.", ana3)

# ===== H. Force =====
add("FOR-1", "Force basse cadence 6x3'", "Force", "FORCE", "SEUIL",
    "6x3 min à 88-95% FTP en 50-55 rpm. Efficience en côte.",
    WU + ints(6, 180, 0.92, 180, 0.55, cad=55, cad_rest=90,
              rpe_on="Force 88-95% FTP · 50-55 rpm · RPE jambes 7-8 / cardio 5-6", rpe_off="Récup 90 rpm · RPE 2") + CD)

add("FOR-2", "Force 7x2'30", "Force", "FORCE", None,
    "7x2'30 à 90-95% FTP en 55 rpm. Recrutement musculaire.",
    WU + ints(7, 150, 0.93, 150, 0.55, cad=55, cad_rest=90,
              rpe_on="Force 90-95% FTP · 55 rpm · RPE jambes 8", rpe_off="Récup · RPE 2") + CD)

add("FOR-3", "Sprints force-vitesse 8x15\"", "Force", "SPRINT", "FMAX",
    "8 sprints de 15s max, récup 3 min. Force-vitesse.",
    WU_INT + ints(8, 15, 1.60, 180, 0.45, cad=100, rpe_on="SPRINT MAX · RPE 10", rpe_off="Récup complète · RPE 2") + CD)

add("FOR-4", "Force-endurance 4x8'", "Force", "FENDUR", "TEMPO",
    "4x8 min à 78-82% FTP en 55 rpm. Force tenue dans la durée.",
    WU + ints(4, 480, 0.80, 180, 0.55, cad=55, cad_rest=90,
              rpe_on="Force-end. 78-82% FTP · 55 rpm · RPE jambes 6-7", rpe_off="Récup 90 rpm · RPE 2") + CD)

add("FOR-5", "Force max 10x30\"", "Force", "FMAX", "FORCE",
    "10x30s à ~100% FTP en 45-50 rpm (couple max), récup 2'30.",
    WU + ints(10, 30, 1.00, 150, 0.50, cad=48, cad_rest=90,
              rpe_on="Force max ~100% FTP · 45-50 rpm · couple max · RPE jambes 8-9", rpe_off="Récup · RPE 2") + CD)

# ===== I. Sprint / Neuromusculaire =====
add("SPR-1", "Sprints départ arrêté 10x10\"", "Sprint / Neuromusculaire", "SPRINT", "FMAX",
    "10 sprints de 10s départ lent (couple + vitesse), récup 2'50.",
    WU_INT + ints(10, 10, 1.60, 170, 0.45, cad=95, rpe_on="Sprint départ lent · couple+vitesse · RPE 10", rpe_off="Récup complète · RPE 2") + CD)

add("SPR-2", "Sprints lancés 8x12\"", "Sprint / Neuromusculaire", "SPRINT", None,
    "8 sprints lancés de 12s à haute cadence, récup 3'48.",
    WU_INT + ints(8, 12, 1.70, 228, 0.45, cad=110, rpe_on="Sprint lancé 110+ rpm · RPE 10", rpe_off="Récup · RPE 2") + CD)

spr3 = list(WU_INT)
for s in range(2):
    spr3 += ints(8, 20, 1.40, 10, 0.40, cad=105, rpe_on="20s @ 140% FTP · RPE 10", rpe_off="10s · RPE 1")
    if s < 1:
        spr3 += ss(300, 0.50, msg="Récup série · RPE 2")
spr3 += CD
add("SPR-3", "Tabata 2x8x(20-10)", "Sprint / Neuromusculaire", "SPRINT", "VO2",
    "2 séries de 8x(20s@140% / 10s) type Tabata. Explosivité + VO2.", spr3)

# ===== J. Spécifique course =====
spe1 = list(WU_INT)
for i in range(5):
    spe1 += (ss(240, 0.97, cad=70, msg=f"Côte {i+1} — 4' @ 97% FTP · RPE 7-8")
             + ss(60, 1.05, cad=85, msg=f"Relance sommet {i+1} — 1' @ 105% FTP · RPE 8")
             + ss(300, 0.75, cad=90, msg="Retour allure course 75% FTP · RPE 5"))
spe1 += CD
add("SPE-1", "Simulation parcours vallonné", "Spécifique course", "SPEC", "SEUIL",
    "Profil accordéon : 5x(côte 4'@97% + relance 1'@105% + retour 75% FTP).", spe1)

add("SPE-2", "Allure course + finish surge", "Spécifique course", "SPEC", "DURAB",
    "1h à 70-74% FTP puis 15 min à 85% (finir fort). Gestion d'effort.",
    WU + ss(3600, 0.72, cad=88, msg="Allure course 70-74% FTP · RPE 4 — nutrition")
    + ss(900, 0.85, cad=90, msg="Finish surge 85% FTP · RPE 6 — finir fort") + CD)

add("RACE-LD", "Allure course longue distance (IF 0.70)", "Spécifique course", "SPEC", "DURAB",
    "2h continu à 68-72% FTP, RPE 3-4. Partie vélo d'un brick longue distance.",
    WU + ss(7200, 0.70, cad=88, msg="Allure course LD 68-72% FTP · RPE 3-4 · IF 0.70 — boire/manger") + CD)

add("RACE-HD", "Allure course demi-distance (IF 0.78)", "Spécifique course", "SPEC", None,
    "1h continu à 78-80% FTP, RPE 5-6. Partie vélo d'un brick demi-distance.",
    WU + ss(3600, 0.79, cad=90, msg="Allure course HD 78-80% FTP · RPE 5-6 · IF 0.78") + CD)

add("RACE-LD-4H", "Allure course IM ~4h (IF 0.68)", "Spécifique course", "SPEC", "DURAB",
    "~3h50 continu à 67-71% FTP. Allure et nutrition de course full distance.",
    WU + ss(12600, 0.69, cad=87, msg="Allure IM 67-71% FTP · RPE 3-4 · IF 0.68 — nutrition course") + CD)

add("RACE-LD-5H", "Allure course IM ~5h (IF 0.68)", "Spécifique course", "SPEC", "DURAB",
    "~4h40 continu à 66-70% FTP. Simulation longue de la partie vélo IM.",
    WU + ss(15600, 0.68, cad=86, msg="Allure IM 66-70% FTP · RPE 3-4 · IF 0.68 — nutrition / pacing") + CD)

# --------------------------------------------------------------------------
# Alternatives HOME-TRAINER (versions compressées des séances longues / route).
# Principe : indoor = puissance continue (pas de roue libre) -> même stimulus en
# ~55-70% du temps. Les séances déjà structurées (intervalles) sont optimales en
# HT telles quelles : pas d'alternative dédiée (on joue la séance elle-même).
# Clé = code ; valeur = (description, segments de l'alternative HT).
# --------------------------------------------------------------------------
HT_ALTS = {
    "END-2": ("Endurance continue indoor 70-75% FTP (sans roue libre).",
              WU + ss(2400, 0.72, cad=90, msg="Endurance 70-75% FTP · RPE 3-4 (HT continu)") + CD),
    "END-4": ("Endurance + blocs à l'allure de course (densifié indoor).",
              WU + ss(900, 0.72, cad=88, msg="Endurance 70% FTP · RPE 3-4")
              + ints(3, 600, 0.80, 300, 0.68, cad=88, rpe_on="Allure course 78-82% FTP · RPE 5", rpe_off="Endurance 68% FTP · RPE 3") + CD),
    "END-5": ("Endurance continue avec touches de tempo.",
              WU + ss(1500, 0.72, cad=88, msg="Endurance 70-75% FTP · RPE 3-4") + ss(300, 0.78, msg="Touche tempo 78% · RPE 5")
              + ss(1500, 0.72, cad=88, msg="Endurance 70-75% FTP · RPE 3-4") + ss(300, 0.78, msg="Touche tempo 78% · RPE 5") + CD),
    "END-6": ("Endurance progressive 68->80% FTP.",
              WU + ss(900, 0.68, cad=88, msg="68% FTP · RPE 3") + ss(900, 0.74, cad=88, msg="74% FTP · RPE 4")
              + ss(600, 0.80, cad=90, msg="80% FTP · RPE 5") + CD),
    "END-7": ("Fat-max continu 60-65% FTP, respiration nasale.",
              WU + ss(3000, 0.63, cad=85, msg="Fat-max 60-65% FTP · RPE 3 — respiration nasale") + CD),
    "END-9": ("Negative split 68% puis 76% FTP.",
              WU + ss(1500, 0.68, cad=88, msg="66-70% FTP · RPE 3") + ss(1500, 0.76, cad=90, msg="74-78% FTP · RPE 4-5 — finir fort") + CD),
    "SS-3": ("Sweet spot indoor (sans le volume endurance de la route).",
             WU + ints(3, 900, 0.90, 240, 0.55, cad=90, rpe_on="Sweet Spot 88-92% FTP · RPE 6-7", rpe_off="récup · RPE 2") + CD),
    "RACE-LD": ("Allure course longue distance continue.",
                WU + ss(3600, 0.73, cad=88, msg="Allure course LD 70-74% FTP · RPE 4 (HT continu) — nutrition") + CD),
    "END-10": ("Endurance + tempo (densifié indoor).",
               WU + ss(1800, 0.70, cad=86, msg="Endurance 68-72% FTP · RPE 3-4")
               + ints(2, 1500, 0.84, 420, 0.60, cad=86, rpe_on="Tempo 82-85% FTP · RPE 5-6", rpe_off="Endurance 58-62% FTP · RPE 3") + CD),
    "END-11": ("Endurance + tempo (équivalent indoor).",
               WU + ss(1200, 0.70, cad=86, msg="Endurance 68-72% FTP · RPE 3")
               + ints(3, 1500, 0.82, 360, 0.60, cad=86, rpe_on="Tempo 80-84% FTP · RPE 5", rpe_off="Endurance 58-62% FTP · RPE 3") + CD),
    "END-12": ("Tempo bas répété (compresse la très longue).",
               WU + ints(3, 1800, 0.78, 300, 0.62, cad=85, rpe_on="Tempo bas 76-80% FTP · RPE 5", rpe_off="Endurance 60-64% FTP · RPE 3") + CD),
    "SS-6": ("Sweet spot indoor à charge égale (sans le volume route).",
             WU + ints(3, 1200, 0.90, 360, 0.55, cad=88, rpe_on="Sweet Spot 88-92% FTP · RPE 6-7", rpe_off="récup · RPE 2") + CD),
    "TMP-6": ("Tempo indoor (compressé).",
              WU + ints(3, 1200, 0.82, 300, 0.60, cad=87, rpe_on="Tempo 80-84% FTP · RPE 5", rpe_off="récup · RPE 3") + CD),
    "RACE-LD-4H": ("Allure IM continue 70-74% FTP.",
                   WU + ss(5400, 0.72, cad=87, msg="Allure IM 70-74% FTP · RPE 4 (HT continu) — nutrition") + CD),
    "RACE-LD-5H": ("Allure IM continue 70-73% FTP.",
                   WU + ss(6600, 0.72, cad=86, msg="Allure IM 70-73% FTP · RPE 4 (HT continu) — nutrition / pacing") + CD),
}
def ua(segs):
    """Charge estimée en UA (type TSS) : 100 x somme(durée_h x IF²).
    Pour une rampe, IF² intégré = (p0²+p0·p1+p1²)/3."""
    tot = 0.0
    for s in segs:
        if2 = (s["p0"]**2 + s["p0"]*s["p1"] + s["p1"]**2) / 3.0
        tot += (s["dur"] / 3600.0) * if2
    return tot * 100.0

def scale_ht_to_load(ht, target):
    """Cale l'alternative HT pour que son UA == target, en ajustant la durée des
    blocs centraux (échauffement = 1er seg et retour au calme = dernier, fixes ;
    intensités conservées)."""
    if len(ht) < 3:
        return ht
    first, mid, last = ht[0], [dict(s) for s in ht[1:-1]], ht[-1]
    mid_target = target - ua([first]) - ua([last])
    cur = ua(mid)
    if cur <= 0 or mid_target <= 0:
        return ht
    k = mid_target / cur
    for s in mid:
        s["dur"] = max(5, int(round(s["dur"] * k)))
    # correction fine sur le bloc steady le plus long
    resid = mid_target - ua(mid)
    steady = [i for i, s in enumerate(mid) if s["p0"] == s["p1"] and s["p0"] > 0]
    if steady:
        i = max(steady, key=lambda i: mid[i]["dur"])
        per = (mid[i]["p0"]**2) / 3600.0 * 100.0
        if per > 0:
            mid[i]["dur"] = max(5, mid[i]["dur"] + int(round(resid / per)))
    return [first] + mid + [last]

for _w in BANK:
    if _w["code"] in HT_ALTS:
        _w["support"] = "Route"
        _desc, _raw = HT_ALTS[_w["code"]]
        _w["ht_desc"] = _desc
        _w["ht"] = scale_ht_to_load(_raw, ua(_w["segs"]))  # UA(HT) == UA(route)
    else:
        _w["support"], _w["ht_desc"], _w["ht"] = "HT", "", None

# --------------------------------------------------------------------------
# Renderers
# --------------------------------------------------------------------------
def _attr(s):
    return escape(s, {'"': "&quot;", "'": "&apos;"})

def total_dur(segs):
    return sum(s["dur"] for s in segs)

def dur_str(sec):
    h, m = sec // 3600, (sec % 3600) // 60
    return f"{h}h{m:02d}" if h else f"{m} min"

def quality_str(w):
    out = QUALITIES[w["q1"]]
    if w["q2"]:
        out += " + " + QUALITIES[w["q2"]]
    return out

def render_zwo(name, desc, segs):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<workout_file>',
             '  <author>Skill velo-double-calibration</author>',
             f'  <name>{escape(name)}</name>',
             f'  <description>{escape(desc)}</description>',
             '  <sportType>bike</sportType>',
             '  <tags><tag name="DoubleCalibration"/></tags>', '  <workout>']
    n = len(segs)
    for i, s in enumerate(segs):
        cad = f' Cadence="{s["cad"]}"' if s["cad"] else ""
        txt = f'\n      <textevent timeoffset="0" message="{_attr(s["msg"])}"/>\n    ' if s["msg"] else ""
        ramp = s["p0"] != s["p1"]
        tag = ("Warmup" if (ramp and i == 0) else "Cooldown" if (ramp and i == n - 1)
               else "Ramp" if ramp else "SteadyState")
        if tag == "SteadyState":
            attrs = f'Duration="{s["dur"]}" Power="{round(s["p0"],3)}"{cad}'
        else:
            attrs = f'Duration="{s["dur"]}" PowerLow="{round(s["p0"],3)}" PowerHigh="{round(s["p1"],3)}"{cad}'
        lines.append(f'    <{tag} {attrs}>{txt}</{tag}>' if txt else f'    <{tag} {attrs}/>')
    lines += ['  </workout>', '</workout_file>', '']
    return "\n".join(lines)

def _course_data(segs, scale, as_watts=False):
    pts, t = [], 0.0
    fmt = (lambda v: str(int(round(v)))) if as_watts else (lambda v: f"{v:.1f}")
    for s in segs:
        pts.append(f'{t/60:.2f}\t{fmt(s["p0"]*scale)}')
        t += s["dur"]
        pts.append(f'{t/60:.2f}\t{fmt(s["p1"]*scale)}')
    return pts

def _course_text(segs):
    out, t = [], 0
    for s in segs:
        if s["msg"]:
            out.append(f'{t}\t{s["msg"]}\t{s["dur"]}')
        t += s["dur"]
    return out

def render_mrc(name, desc, segs):
    head = ["[COURSE HEADER]", "VERSION = 2", "UNITS = ENGLISH",
            f"DESCRIPTION = {desc}", f"FILE NAME = {name}",
            "MINUTES PERCENT", "[END COURSE HEADER]", "[COURSE DATA]"]
    tail = ["[END COURSE DATA]", "[COURSE TEXT]"] + _course_text(segs) + ["[END COURSE TEXT]", ""]
    return "\n".join(head + _course_data(segs, 100.0) + tail)

def render_erg(name, desc, segs, ftp):
    head = ["[COURSE HEADER]", "VERSION = 2", "UNITS = ENGLISH",
            f"DESCRIPTION = {desc} (FTP {ftp} W)", f"FILE NAME = {name}",
            "MINUTES WATTS", "[END COURSE HEADER]", "[COURSE DATA]"]
    tail = ["[END COURSE DATA]", "[COURSE TEXT]"] + _course_text(segs) + ["[END COURSE TEXT]", ""]
    return "\n".join(head + _course_data(segs, float(ftp), as_watts=True) + tail)

# --------------------------------------------------------------------------
def slug(s):
    s = s.replace("'", "").replace('"', "")
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-")

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("--ftp", type=int, default=228)
    ap.add_argument("--out", default=os.path.join(here, ".."))
    a = ap.parse_args()
    root = os.path.abspath(a.out)
    refs = os.path.join(root, "references")
    dirs = {fmt: os.path.join(root, f"bank_{fmt}") for fmt in ("zwo", "mrc", "erg")}
    for d in list(dirs.values()) + [refs]:
        os.makedirs(d, exist_ok=True)

    idx = ["# Banque générée — importable dans Nolio (.zwo / .mrc / .erg)\n",
           ".zwo et .mrc = puissance relative (%FTP) -> **athlète-indépendants**.",
           f".erg = watts absolus pour **FTP = {a.ftp} W** (régénérer avec --ftp).\n",
           f"**{len(BANK)} séances.** UA = charge estimée (type TSS).\n",
           "| Code | Séance | Durée | UA | Qualités développées | .zwo | .mrc | .erg |",
           "|------|--------|-------|----|----------------------|------|------|------|"]
    def write_all(base, name, desc, segs):
        open(os.path.join(dirs["zwo"], base + ".zwo"), "w", encoding="utf-8").write(render_zwo(name, desc, segs))
        open(os.path.join(dirs["mrc"], base + ".mrc"), "w", encoding="utf-8").write(render_mrc(name, desc, segs))
        open(os.path.join(dirs["erg"], base + ".erg"), "w", encoding="utf-8").write(render_erg(name, desc, segs, a.ftp))

    for w in BANK:
        full = f'{w["code"]} {w["name"]}'
        full_desc = f'{w["desc"]} | Qualités : {quality_str(w)}. Double calibration %FTP + RPE.'
        base = f'{w["code"]}_{slug(w["name"])}'
        write_all(base, full, full_desc, w["segs"])
        idx.append(f'| {w["code"]} | {w["name"]} | {dur_str(total_dur(w["segs"]))} | {round(ua(w["segs"]))} | {quality_str(w)} | `{base}.zwo` | `{base}.mrc` | `{base}.erg` |')
        if w["ht"]:
            ht_name = f'{w["code"]}-HT {w["name"]} (home-trainer)'
            ht_desc = f'{w["ht_desc"]} | Alternative HT de {w["code"]}. Qualités : {quality_str(w)}.'
            ht_base = f'{w["code"]}-HT_{slug(w["name"])}'
            write_all(ht_base, ht_name, ht_desc, w["ht"])
    open(os.path.join(dirs["zwo"], "INDEX.md"), "w", encoding="utf-8").write("\n".join(idx) + "\n")

    # Document des alternatives home-trainer
    nb_ht = sum(1 for w in BANK if w["ht"])
    alt = [f"# Alternatives home-trainer ({len(BANK)} séances)\n",
           "Durée et **charge estimée en UA** (type TSS) de chaque séance + son",
           "équivalent **home-trainer**, calé à **charge égale**.\n",
           "- **Support HT** : séance déjà structurée → jouée telle quelle (durée et UA identiques).",
           "- **Support Route** : séance longue/extérieure → **alternative HT calée à UA égale**",
           "  (intensité plus haute indoor → même charge en moins de temps). Fichiers",
           "  jouables `<CODE>-HT_*` dans `bank_zwo/` `bank_mrc/` `bank_erg/`.\n",
           f"> {nb_ht} alternatives HT générées, chacune à la **même UA** que sa séance route.\n",
           "| Code | Séance | Durée route | UA route | Alternative home-trainer | Durée HT | UA HT |",
           "|------|--------|-------------|----------|--------------------------|----------|-------|"]
    for w in BANK:
        d = dur_str(total_dur(w["segs"]))
        u = round(ua(w["segs"]))
        if w["ht"]:
            alt.append(f'| {w["code"]} | {w["name"]} | {d} | {u} | {w["ht_desc"]} (`{w["code"]}-HT_*`) | {dur_str(total_dur(w["ht"]))} | {round(ua(w["ht"]))} |')
        else:
            alt.append(f'| {w["code"]} | {w["name"]} | {d} | {u} | Identique — déjà conçue pour HT | {d} | {u} |')
    open(os.path.join(refs, "alternatives-ht.md"), "w", encoding="utf-8").write("\n".join(alt) + "\n")

    # Catalogue lisible groupé par filière
    cat = [f"# Catalogue des séances vélo ({len(BANK)} séances)\n",
           "Banque universelle, double calibration **%FTP + RPE**. Chaque séance",
           "indique la/les **qualité(s) développée(s)**. Fichiers jouables dans",
           "`bank_zwo/` `bank_mrc/` `bank_erg/` (voir `bank_zwo/INDEX.md`).\n",
           "> Généré par `scripts/generate_bank.py` — ne pas éditer à la main.\n"]
    for fil in FILIERE_ORDER:
        ws = [w for w in BANK if w["filiere"] == fil]
        if not ws:
            continue
        cat += [f"\n## {fil}\n",
                "| Code | Séance | Durée | UA | Qualité principale | Qualité secondaire | Contenu |",
                "|------|--------|-------|----|--------------------|--------------------|---------|"]
        for w in ws:
            q2 = QUALITIES[w["q2"]] if w["q2"] else "—"
            cat.append(f'| {w["code"]} | {w["name"]} | {dur_str(total_dur(w["segs"]))} | {round(ua(w["segs"]))} | {QUALITIES[w["q1"]]} | {q2} | {w["desc"]} |')
    open(os.path.join(refs, "catalogue-seances.md"), "w", encoding="utf-8").write("\n".join(cat) + "\n")

    # Taxonomie des qualités
    qd = ["# Taxonomie des qualités développées\n",
          "Codes utilisés par le générateur et le catalogue.\n",
          "| Code | Qualité | Filière physiologique |", "|------|---------|-----------------------|"]
    phys = {"RECUP": "Régénération", "ENDUR": "Aérobie I (Z2)", "LIPOX": "Aérobie lipidique",
            "DURAB": "Aérobie / fatigue", "VELO": "Neuromusculaire (coordination)",
            "TEMPO": "Aérobie II (Z3)", "SS": "Sweet spot (Z3-Z4)", "SEUIL": "Seuil (Z4)",
            "VO2": "Aérobie max (Z5)", "TOLLAC": "Z5-Z6 (répétition)", "ANA": "Anaérobie (Z6)",
            "FORCE": "Force (Z3-Z4 basse cadence)", "FENDUR": "Force-endurance",
            "FMAX": "Force max (couple)", "SPRINT": "Neuromusculaire (Z7)", "SPEC": "Spécifique course"}
    for k, v in QUALITIES.items():
        qd.append(f"| {k} | {v} | {phys.get(k,'')} |")
    open(os.path.join(refs, "qualites.md"), "w", encoding="utf-8").write("\n".join(qd) + "\n")

    print(f'{len(BANK)} séances x 3 formats + catalogue + qualités générés [FTP .erg = {a.ftp} W]')

if __name__ == "__main__":
    main()
