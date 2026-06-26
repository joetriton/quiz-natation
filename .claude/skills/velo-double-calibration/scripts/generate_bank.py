#!/usr/bin/env python3
"""
Générateur de la banque de séances vélo en .zwo (double calibration %FTP + RPE).

Les fichiers .zwo encodent la puissance en FRACTION de FTP -> athlète-indépendants.
Importables dans Nolio (.zwo), Zwift, et exportables vers Garmin/Wahoo.
Le RPE et les consignes s'affichent via <textevent>.

Usage:
    python3 generate_bank.py [dossier_sortie]
Défaut: ../bank_zwo/  (relatif à ce script)
"""
import os
import sys
import re
from xml.sax.saxutils import escape

# --------------------------------------------------------------------------
# Helpers de construction des steps .zwo. Power = fraction de FTP (0.95 = 95%).
# --------------------------------------------------------------------------

def _attr(s):
    # échappe &, <, > ET les guillemets (le message est dans un attribut)
    return escape(s, {'"': "&quot;", "'": "&apos;"})

def _txt(offset, msg):
    return f'      <textevent timeoffset="{int(offset)}" message="{_attr(msg)}"/>'

def warmup(dur, p_low, p_high, cad=None, msg="Échauffement progressif — RPE 2→4"):
    cad_attr = f' Cadence="{cad}"' if cad else ""
    return (f'    <Warmup Duration="{int(dur)}" PowerLow="{p_low}" PowerHigh="{p_high}"{cad_attr}>\n'
            f'{_txt(0, msg)}\n    </Warmup>')

def cooldown(dur, p_high=0.60, p_low=0.45, cad=None, msg="Retour au calme — RPE 2"):
    cad_attr = f' Cadence="{cad}"' if cad else ""
    return (f'    <Cooldown Duration="{int(dur)}" PowerLow="{p_high}" PowerHigh="{p_low}"{cad_attr}>\n'
            f'{_txt(0, msg)}\n    </Cooldown>')

def steady(dur, power, cad=None, msg=None):
    cad_attr = f' Cadence="{cad}"' if cad else ""
    body = f'\n{_txt(0, msg)}\n    ' if msg else ""
    if msg:
        return f'    <SteadyState Duration="{int(dur)}" Power="{power}"{cad_attr}>{body}</SteadyState>'
    return f'    <SteadyState Duration="{int(dur)}" Power="{power}"{cad_attr}/>'

def intervals(repeat, on_dur, on_p, off_dur, off_p, cad=None, cad_rest=None,
              rpe_on="", rpe_off=""):
    cad_attr = f' Cadence="{cad}"' if cad else ""
    cadr_attr = f' CadenceResting="{cad_rest}"' if cad_rest else ""
    lines = [f'    <IntervalsT Repeat="{repeat}" OnDuration="{int(on_dur)}" '
             f'OnPower="{on_p}" OffDuration="{int(off_dur)}" OffPower="{off_p}"'
             f'{cad_attr}{cadr_attr}>']
    if rpe_on:
        lines.append(_txt(0, f"EFFORT — {rpe_on}"))
    if rpe_off:
        lines.append(_txt(on_dur, f"RÉCUP — {rpe_off}"))
    lines.append('    </IntervalsT>')
    return "\n".join(lines)

def freeride(dur, msg=""):
    if msg:
        return (f'    <FreeRide Duration="{int(dur)}">\n{_txt(0, msg)}\n    </FreeRide>')
    return f'    <FreeRide Duration="{int(dur)}"/>'

def build(name, desc, steps, tags=("DoubleCalibration",)):
    tag_xml = "".join(f'<tag name="{escape(t)}"/>' for t in tags)
    body = "\n".join(steps)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<workout_file>\n'
        '  <author>Skill velo-double-calibration</author>\n'
        f'  <name>{escape(name)}</name>\n'
        f'  <description>{escape(desc)}</description>\n'
        '  <sportType>bike</sportType>\n'
        f'  <tags>{tag_xml}</tags>\n'
        '  <workout>\n'
        f'{body}\n'
        '  </workout>\n'
        '</workout_file>\n'
    )

# --------------------------------------------------------------------------
# Définition de la BANQUE. Chaque entrée : (code, nom, description, steps).
# Puissances en fraction de FTP. RPE indiqué dans les textevents.
# Banque UNIVERSELLE : valable pour tout athlète et toute course.
# --------------------------------------------------------------------------

WU = warmup(600, 0.50, 0.72)          # échauffement standard 10 min
WU_INT = "\n".join([                    # échauffement séance intense (+ activations)
    warmup(600, 0.50, 0.72),
    intervals(3, 30, 1.05, 60, 0.50, rpe_on="RPE 8 (activation)", rpe_off="RPE 2"),
    steady(120, 0.55, msg="Transition avant le corps de séance — RPE 2"),
])
CD = cooldown(480)

BANK = []

# ---- A. Récupération / Endurance ----
BANK.append(("END-1", "Récup active",
    "Récupération active. 50-60% FTP, RPE 2, cadence souple.",
    [warmup(300, 0.45, 0.55),
     steady(2100, 0.55, cad=90, msg="Récup active — RPE 2 — je peux chanter"),
     cooldown(300, 0.55, 0.45)]))

BANK.append(("END-2", "Endurance fond",
    "Endurance fondamentale. 65-75% FTP, RPE 3-4. Base aérobie / durabilité.",
    [WU,
     steady(4200, 0.70, cad=88, msg="Endurance — RPE 3-4 — conversation fluide"),
     CD]))

BANK.append(("END-3", "Endurance + cadence",
    "Endurance avec travail de vélocité. Blocs à 100-105 rpm.",
    [WU,
     intervals(3, 600, 0.70, 300, 0.60, cad=103, cad_rest=90,
               rpe_on="RPE 4 — 100-105 rpm — gainage", rpe_off="RPE 2 — cadence libre"),
     CD]))

BANK.append(("END-4", "Longue spécifique allure course",
    "Sortie longue avec blocs à l'allure de course. Tenue d'allure / durabilité.",
    [WU,
     steady(1800, 0.70, cad=88, msg="Endurance — RPE 3-4"),
     intervals(3, 1200, 0.80, 600, 0.68, cad=88,
               rpe_on="Allure course — RPE 5", rpe_off="Endurance — RPE 3"),
     steady(1800, 0.70, msg="Retour endurance — RPE 3-4"),
     CD]))

# ---- B. Tempo / Sweet Spot ----
BANK.append(("TMP-1", "Tempo 3x15",
    "Tempo 3x15 min à 80-85% FTP, RPE 5-6. Allure d'endurance soutenue.",
    [WU,
     intervals(3, 900, 0.83, 300, 0.55, cad=90,
               rpe_on="Tempo — RPE 5-6 — phrases courtes", rpe_off="Récup — RPE 2"),
     CD]))

BANK.append(("TMP-2", "Tempo continu 50'",
    "Tempo continu 50 min à 78-83% FTP, RPE 5. Tenue mentale.",
    [WU,
     steady(3000, 0.80, cad=90, msg="Tempo continu — RPE 5 — rester régulier"),
     CD]))

BANK.append(("SS-1", "Sweet Spot 3x12",
    "Sweet Spot 3x12 min à 88-92% FTP, RPE 6-7. Meilleur rapport charge/fatigue.",
    [WU_INT,
     intervals(3, 720, 0.90, 300, 0.55, cad=90,
               rpe_on="Sweet Spot — RPE 6-7 — inconfortable mais tenable", rpe_off="Récup — RPE 2"),
     CD]))

BANK.append(("SS-2", "Sweet Spot 2x20",
    "Sweet Spot 2x20 min à 88-93% FTP, RPE 6-7. Progression de SS-1.",
    [WU_INT,
     intervals(2, 1200, 0.91, 480, 0.55, cad=90,
               rpe_on="Sweet Spot — RPE 6-7", rpe_off="Récup — RPE 2"),
     CD]))

BANK.append(("SS-3", "Sweet Spot sur longue 3x20",
    "Sur sortie longue : 3x20 min à 88-90% FTP, RPE 6. Spécificité endurance.",
    [WU,
     steady(1200, 0.70, msg="Endurance — RPE 3-4"),
     intervals(3, 1200, 0.89, 600, 0.68, cad=88,
               rpe_on="Sweet Spot — RPE 6", rpe_off="Endurance — RPE 3"),
     steady(900, 0.68, msg="Retour endurance — RPE 3"),
     CD]))

# ---- C. Seuil ----
BANK.append(("SEU-1", "Seuil 2x15",
    "Seuil 2x15 min à 95-100% FTP, RPE 7-8. Élève la FTP.",
    [WU_INT,
     intervals(2, 900, 0.98, 480, 0.50, cad=90,
               rpe_on="Seuil — RPE 7-8 — mots isolés", rpe_off="Récup — RPE 2"),
     CD]))

# Seuil progressif 3x(8'@92 / 4'@97 / 2'@103), récup 4 min — déroulé
seu2_steps = [WU_INT]
for i in range(3):
    seu2_steps += [
        steady(480, 0.92, cad=90, msg=f"Bloc {i+1} — 8' @ 92% — RPE 7"),
        steady(240, 0.97, cad=90, msg=f"Bloc {i+1} — 4' @ 97% — RPE 7,5"),
        steady(120, 1.03, cad=90, msg=f"Bloc {i+1} — 2' @ 103% — RPE 8"),
    ]
    if i < 2:
        seu2_steps.append(steady(240, 0.52, msg="Récup — RPE 2"))
seu2_steps.append(CD)
BANK.append(("SEU-2", "Seuil progressif 3x(8-4-2)",
    "Seuil progressif : 3 blocs de 8'@92% / 4'@97% / 2'@103%, RPE 7→8, récup 4 min.",
    seu2_steps))

# Over-under 4x(2'@90 + 2'@105), 2 séries, récup 5 min — déroulé
seu3_steps = [WU_INT]
for s in range(2):
    for i in range(4):
        seu3_steps.append(steady(120, 0.90, cad=90, msg=f"UNDER 90% — RPE 6"))
        seu3_steps.append(steady(120, 1.05, cad=90, msg=f"OVER 105% — RPE 8"))
    if s < 1:
        seu3_steps.append(steady(300, 0.52, msg="Récup série — RPE 2"))
seu3_steps.append(CD)
BANK.append(("SEU-3", "Seuil over-under 2x(4x2-2)",
    "Over-under : 2 séries de 4x(2'@90% + 2'@105%), RPE 6↔8, récup 5 min. Relances.",
    seu3_steps))

# Seuil mixte 6x1 / 2x4 / 6x1
seu4_steps = [WU_INT,
    intervals(6, 60, 1.00, 60, 0.55, cad=95, rpe_on="1' @ 100% — RPE 7-8", rpe_off="RPE 2"),
    steady(300, 0.52, msg="Récup bloc — RPE 2"),
    intervals(2, 240, 0.97, 180, 0.52, cad=90, rpe_on="4' @ 97% — RPE 7-8", rpe_off="RPE 2"),
    steady(300, 0.52, msg="Récup bloc — RPE 2"),
    intervals(6, 60, 1.00, 60, 0.55, cad=95, rpe_on="1' @ 100% — RPE 7-8", rpe_off="RPE 2"),
    CD]
BANK.append(("SEU-4", "Seuil 6x1 / 2x4 / 6x1",
    "Seuil format mixte court-long-court, RPE 7-8. Variété et densité.",
    seu4_steps))

# ---- D. VO2max ----
BANK.append(("VO2-1", "VO2 5x3'",
    "VO2max 5x3 min à 110-118% FTP, RPE 8-9, récup 3 min. Plafond aérobie.",
    [WU_INT,
     intervals(5, 180, 1.13, 180, 0.50, cad=95,
               rpe_on="VO2 — RPE 8-9 — respiration max", rpe_off="Récup — RPE 2"),
     CD]))

vo2_2 = [WU_INT]
for s in range(2):
    vo2_2.append(intervals(8, 30, 1.15, 30, 0.50, cad=100,
                           rpe_on="30\" @ 115% — RPE 9", rpe_off="30\" — RPE 2"))
    if s < 1:
        vo2_2.append(steady(300, 0.50, msg="Récup série — RPE 2"))
vo2_2.append(CD)
BANK.append(("VO2-2", "VO2 30/30 2x8",
    "30/30 : 2 séries de 8x(30\"@115% / 30\"@50%), RPE 9/2. Cylindrée.",
    vo2_2))

vo2_3 = [WU_INT]
for s in range(3):
    vo2_3.append(intervals(6, 40, 1.15, 20, 0.50, cad=100,
                           rpe_on="40\" @ 115% — RPE 9", rpe_off="20\" — RPE 2"))
    if s < 2:
        vo2_3.append(steady(240, 0.50, msg="Récup série — RPE 2"))
vo2_3.append(CD)
BANK.append(("VO2-3", "VO2 40/20 3x6",
    "40/20 : 3 séries de 6x(40\"@115% / 20\"@50%), RPE 9/2. Densité.",
    vo2_3))

# ---- E. Force / spécifique côte ----
BANK.append(("FOR-1", "Force basse cadence 6x3'",
    "Force 6x3 min à 88-95% FTP en 50-55 rpm. RPE jambes 7-8 / cardio 5-6. Efficience en côte.",
    [WU,
     intervals(6, 180, 0.92, 180, 0.55, cad=55, cad_rest=90,
               rpe_on="50-55 rpm — RPE jambes 7-8 / cardio 5-6", rpe_off="Récup 90 rpm — RPE 2"),
     CD]))

BANK.append(("FOR-2", "Force 7x2'30",
    "Force 7x2'30 à 90-95% FTP en 55 rpm. RPE jambes 8. Recrutement musculaire.",
    [WU,
     intervals(7, 150, 0.93, 150, 0.55, cad=55, cad_rest=90,
               rpe_on="55 rpm — RPE jambes 8", rpe_off="Récup — RPE 2"),
     CD]))

BANK.append(("FOR-3", "Sprints / force-vitesse 8x15\"",
    "8 sprints de 15\" max, RPE 10, récup 3 min. Force-vitesse.",
    [WU_INT,
     intervals(8, 15, 1.60, 180, 0.45, cad=100,
               rpe_on="SPRINT MAX — RPE 10", rpe_off="Récup complète — RPE 2"),
     CD]))

# Simulation parcours vallonné (générique, ex. profil accordéon)
spe_steps = [WU_INT]
for i in range(5):
    spe_steps += [
        steady(240, 0.97, cad=70, msg=f"Côte {i+1} — 4' @ 97% — RPE 7-8"),
        steady(60, 1.05, cad=85, msg=f"Relance sommet {i+1} — 1' @ 105% — RPE 8"),
        steady(300, 0.75, cad=90, msg=f"Retour allure course — RPE 5"),
    ]
spe_steps.append(CD)
BANK.append(("SPE-1", "Simulation parcours vallonné",
    "Profil 'accordéon' : 5x(côte 4'@97% + relance 1'@105% + retour allure 75%). Spécifique course vallonnée.",
    spe_steps))

# ---- F. Spécifique course (partie vélo des bricks) ----
BANK.append(("RACE-LD", "Allure course longue distance (IF ~0.70)",
    "Tenue d'allure longue distance : 2h continu à 68-72% FTP, RPE 3-4. Valider watts/RPE/nutrition. Partie vélo d'un brick.",
    [WU,
     steady(7200, 0.70, cad=88, msg="Allure course LD — RPE 3-4 — IF ~0.70 — boire/manger"),
     CD]))

BANK.append(("RACE-HD", "Allure course demi-distance (IF ~0.78)",
    "Tenue d'allure demi-distance : 1h continu à 78-80% FTP, RPE 5-6. Partie vélo d'un brick.",
    [WU,
     steady(3600, 0.79, cad=90, msg="Allure course HD — RPE 5-6 — IF ~0.78"),
     CD]))

# --------------------------------------------------------------------------
# Écriture des fichiers
# --------------------------------------------------------------------------

def slug(s):
    s = s.replace("'", "").replace("\"", "")
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-")
    return s

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "..", "bank_zwo")
    out = os.path.abspath(out)
    os.makedirs(out, exist_ok=True)
    index = ["# Banque .zwo générée (importable dans Nolio)\n",
             "Puissance = fraction de FTP -> athlète-indépendant. RPE affiché à l'écran.\n",
             "| Code | Séance | Fichier |", "|------|--------|---------|"]
    for code, name, desc, steps in BANK:
        full_name = f"{code} {name}"
        xml = build(full_name, f"{desc}\nDouble calibration %FTP + RPE.", steps)
        fname = f"{code}_{slug(name)}.zwo"
        with open(os.path.join(out, fname), "w", encoding="utf-8") as f:
            f.write(xml)
        index.append(f"| {code} | {name} | `{fname}` |")
    with open(os.path.join(out, "INDEX.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(index) + "\n")
    print(f"{len(BANK)} séances .zwo générées dans {out}")

if __name__ == "__main__":
    main()
