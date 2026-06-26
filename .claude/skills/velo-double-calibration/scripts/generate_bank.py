#!/usr/bin/env python3
"""
Générateur de la banque de séances vélo (double calibration %FTP + RPE).

Source unique = liste de SEGMENTS neutres par séance. Trois renderers :
  - .zwo  (Zwift / Nolio)            : puissance en fraction de FTP  -> universel
  - .mrc  (TrainerRoad / PerfPRO...) : puissance en % de FTP         -> universel
  - .erg  (idem)                     : puissance en WATTS absolus    -> par FTP

Tous importables dans Nolio (.zwo/.erg/.mrc/.json/.fit). Le RPE et les consignes
sont placés dans les textevents (.zwo) et dans [COURSE TEXT] (.mrc/.erg).

Usage:
    python3 generate_bank.py [--ftp 228] [--out DOSSIER_RACINE]
Sorties: <racine>/bank_zwo, <racine>/bank_mrc, <racine>/bank_erg
Défaut racine = dossier parent de ce script.
"""
import os
import sys
import re
import argparse
from xml.sax.saxutils import escape

# --------------------------------------------------------------------------
# Représentation neutre : un segment = rampe linéaire de p0 -> p1 (fractions FTP)
# sur 'dur' secondes, à 'cad' rpm (optionnel), avec un message 'msg' (RPE/consigne).
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

# --------------------------------------------------------------------------
# Briques communes
# --------------------------------------------------------------------------
WU = wu(600, 0.50, 0.72)
WU_INT = (wu(600, 0.50, 0.72)
          + ints(3, 30, 1.05, 60, 0.50, rpe_on="RPE 8 (activation)", rpe_off="RPE 2")
          + ss(120, 0.55, msg="Transition avant le corps — RPE 2"))
CD = cd(480)

# --------------------------------------------------------------------------
# BANQUE (universelle : tout athlète / toute course)
# Entrée : (code, nom, description, segments)
# --------------------------------------------------------------------------
BANK = []
def add(code, name, desc, segs): BANK.append((code, name, desc, segs))

# ---- A. Récupération / Endurance ----
add("END-1", "Récup active",
    "Récupération active. 50-60% FTP, RPE 2.",
    wu(300, 0.45, 0.55)
    + ss(2100, 0.55, cad=90, msg="Récup active — RPE 2 — je peux chanter")
    + cd(300, 0.55, 0.45))

add("END-2", "Endurance fond",
    "Endurance fondamentale. 65-75% FTP, RPE 3-4. Base aérobie / durabilité.",
    WU + ss(4200, 0.70, cad=88, msg="Endurance 65-75% FTP · RPE 3-4 — conversation fluide") + CD)

add("END-3", "Endurance + cadence",
    "Endurance + vélocité. Blocs à 100-105 rpm.",
    WU + ints(3, 600, 0.70, 300, 0.60, cad=103, cad_rest=90,
              rpe_on="68-72% FTP · RPE 4 — 100-105 rpm", rpe_off="55-65% FTP · RPE 2 — cadence libre") + CD)

add("END-4", "Longue spécifique allure course",
    "Sortie longue avec blocs à l'allure de course. Durabilité / tenue d'allure.",
    WU + ss(1800, 0.70, cad=88, msg="Endurance 65-75% FTP · RPE 3-4")
    + ints(3, 1200, 0.80, 600, 0.68, cad=88,
           rpe_on="Allure course 78-82% FTP · RPE 5", rpe_off="Endurance 65-72% FTP · RPE 3")
    + ss(1800, 0.70, msg="Retour endurance 65-75% FTP · RPE 3-4") + CD)

# ---- B. Tempo / Sweet Spot ----
add("TMP-1", "Tempo 3x15",
    "Tempo 3x15 min à 80-85% FTP, RPE 5-6.",
    WU + ints(3, 900, 0.83, 300, 0.55, cad=90,
              rpe_on="Tempo 80-85% FTP · RPE 5-6 — phrases courtes", rpe_off="Récup 50-58% FTP · RPE 2") + CD)

add("TMP-2", "Tempo continu 50'",
    "Tempo continu 50 min à 78-83% FTP, RPE 5.",
    WU + ss(3000, 0.80, cad=90, msg="Tempo continu 78-83% FTP · RPE 5 — rester régulier") + CD)

add("SS-1", "Sweet Spot 3x12",
    "Sweet Spot 3x12 min à 88-92% FTP, RPE 6-7.",
    WU_INT + ints(3, 720, 0.90, 300, 0.55, cad=90,
                  rpe_on="Sweet Spot 88-92% FTP · RPE 6-7 — tenable", rpe_off="Récup 50-58% FTP · RPE 2") + CD)

add("SS-2", "Sweet Spot 2x20",
    "Sweet Spot 2x20 min à 88-93% FTP, RPE 6-7.",
    WU_INT + ints(2, 1200, 0.91, 480, 0.55, cad=90,
                  rpe_on="Sweet Spot 88-93% FTP · RPE 6-7", rpe_off="Récup 50-58% FTP · RPE 2") + CD)

add("SS-3", "Sweet Spot sur longue 3x20",
    "Sur sortie longue : 3x20 min à 88-90% FTP, RPE 6.",
    WU + ss(1200, 0.70, msg="Endurance 65-75% FTP · RPE 3-4")
    + ints(3, 1200, 0.89, 600, 0.68, cad=88,
           rpe_on="Sweet Spot 88-90% FTP · RPE 6", rpe_off="Endurance 65-72% FTP · RPE 3")
    + ss(900, 0.68, msg="Retour endurance 65-72% FTP · RPE 3") + CD)

# ---- C. Seuil ----
add("SEU-1", "Seuil 2x15",
    "Seuil 2x15 min à 95-100% FTP, RPE 7-8.",
    WU_INT + ints(2, 900, 0.98, 480, 0.50, cad=90,
                  rpe_on="Seuil 95-100% FTP · RPE 7-8 — mots isolés", rpe_off="Récup 45-55% FTP · RPE 2") + CD)

seu2 = list(WU_INT)
for i in range(3):
    seu2 += (ss(480, 0.92, cad=90, msg=f"Bloc {i+1} — 8' @ 92% — RPE 7")
             + ss(240, 0.97, cad=90, msg=f"Bloc {i+1} — 4' @ 97% — RPE 7,5")
             + ss(120, 1.03, cad=90, msg=f"Bloc {i+1} — 2' @ 103% — RPE 8"))
    if i < 2:
        seu2 += ss(240, 0.52, msg="Récup — RPE 2")
seu2 += CD
add("SEU-2", "Seuil progressif 3x(8-4-2)",
    "Seuil progressif : 3 blocs 8'@92% / 4'@97% / 2'@103%, RPE 7->8, récup 4 min.", seu2)

seu3 = list(WU_INT)
for s in range(2):
    for _ in range(4):
        seu3 += ss(120, 0.90, cad=90, msg="UNDER 90% — RPE 6")
        seu3 += ss(120, 1.05, cad=90, msg="OVER 105% — RPE 8")
    if s < 1:
        seu3 += ss(300, 0.52, msg="Récup série — RPE 2")
seu3 += CD
add("SEU-3", "Seuil over-under 2x(4x2-2)",
    "Over-under : 2 séries de 4x(2'@90% + 2'@105%), RPE 6<->8, récup 5 min.", seu3)

add("SEU-4", "Seuil 6x1 / 2x4 / 6x1",
    "Seuil mixte court-long-court, RPE 7-8.",
    WU_INT
    + ints(6, 60, 1.00, 60, 0.55, cad=95, rpe_on="1' @ 100% — RPE 7-8", rpe_off="RPE 2")
    + ss(300, 0.52, msg="Récup bloc — RPE 2")
    + ints(2, 240, 0.97, 180, 0.52, cad=90, rpe_on="4' @ 97% — RPE 7-8", rpe_off="RPE 2")
    + ss(300, 0.52, msg="Récup bloc — RPE 2")
    + ints(6, 60, 1.00, 60, 0.55, cad=95, rpe_on="1' @ 100% — RPE 7-8", rpe_off="RPE 2")
    + CD)

# ---- D. VO2max ----
add("VO2-1", "VO2 5x3'",
    "VO2max 5x3 min à 110-118% FTP, RPE 8-9, récup 3 min.",
    WU_INT + ints(5, 180, 1.13, 180, 0.50, cad=95,
                  rpe_on="VO2 110-118% FTP · RPE 8-9 — respiration max", rpe_off="Récup 45-55% FTP · RPE 2") + CD)

vo2_2 = list(WU_INT)
for s in range(2):
    vo2_2 += ints(8, 30, 1.15, 30, 0.50, cad=100,
                  rpe_on="30s @ 115% — RPE 9", rpe_off="30s — RPE 2")
    if s < 1:
        vo2_2 += ss(300, 0.50, msg="Récup série — RPE 2")
vo2_2 += CD
add("VO2-2", "VO2 30-30 2x8",
    "30/30 : 2 séries de 8x(30s@115% / 30s@50%), RPE 9/2.", vo2_2)

vo2_3 = list(WU_INT)
for s in range(3):
    vo2_3 += ints(6, 40, 1.15, 20, 0.50, cad=100,
                  rpe_on="40s @ 115% — RPE 9", rpe_off="20s — RPE 2")
    if s < 2:
        vo2_3 += ss(240, 0.50, msg="Récup série — RPE 2")
vo2_3 += CD
add("VO2-3", "VO2 40-20 3x6",
    "40/20 : 3 séries de 6x(40s@115% / 20s@50%), RPE 9/2.", vo2_3)

# ---- E. Force / spécifique côte ----
add("FOR-1", "Force basse cadence 6x3'",
    "Force 6x3 min à 88-95% FTP en 50-55 rpm. RPE jambes 7-8 / cardio 5-6.",
    WU + ints(6, 180, 0.92, 180, 0.55, cad=55, cad_rest=90,
              rpe_on="Force 88-95% FTP · 50-55 rpm · RPE jambes 7-8 / cardio 5-6", rpe_off="Récup 90 rpm · RPE 2") + CD)

add("FOR-2", "Force 7x2'30",
    "Force 7x2'30 à 90-95% FTP en 55 rpm. RPE jambes 8.",
    WU + ints(7, 150, 0.93, 150, 0.55, cad=55, cad_rest=90,
              rpe_on="Force 90-95% FTP · 55 rpm · RPE jambes 8", rpe_off="Récup · RPE 2") + CD)

add("FOR-3", "Sprints force-vitesse 8x15s",
    "8 sprints de 15s max, RPE 10, récup 3 min.",
    WU_INT + ints(8, 15, 1.60, 180, 0.45, cad=100,
                  rpe_on="SPRINT MAX — RPE 10", rpe_off="Récup complète — RPE 2") + CD)

spe = list(WU_INT)
for i in range(5):
    spe += (ss(240, 0.97, cad=70, msg=f"Côte {i+1} — 4' @ 97% — RPE 7-8")
            + ss(60, 1.05, cad=85, msg=f"Relance sommet {i+1} — 1' @ 105% — RPE 8")
            + ss(300, 0.75, cad=90, msg=f"Retour allure course — RPE 5"))
spe += CD
add("SPE-1", "Simulation parcours vallonné",
    "Profil 'accordéon' : 5x(côte 4'@97% + relance 1'@105% + retour allure 75%).", spe)

# ---- F. Spécifique course (partie vélo des bricks) ----
add("RACE-LD", "Allure course longue distance (IF 0.70)",
    "Tenue d'allure longue distance : 2h continu à 68-72% FTP, RPE 3-4. Partie vélo d'un brick.",
    WU + ss(7200, 0.70, cad=88, msg="Allure course LD — RPE 3-4 — IF 0.70 — boire/manger") + CD)

add("RACE-HD", "Allure course demi-distance (IF 0.78)",
    "Tenue d'allure demi-distance : 1h continu à 78-80% FTP, RPE 5-6. Partie vélo d'un brick.",
    WU + ss(3600, 0.79, cad=90, msg="Allure course HD — RPE 5-6 — IF 0.78") + CD)

# --------------------------------------------------------------------------
# Renderers
# --------------------------------------------------------------------------

def _attr(s):
    return escape(s, {'"': "&quot;", "'": "&apos;"})

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
        if ramp and i == 0:
            tag = "Warmup"
        elif ramp and i == n - 1:
            tag = "Cooldown"
        elif ramp:
            tag = "Ramp"
        else:
            tag = "SteadyState"
        if tag == "SteadyState":
            attrs = f'Duration="{s["dur"]}" Power="{round(s["p0"],3)}"{cad}'
        else:
            attrs = f'Duration="{s["dur"]}" PowerLow="{round(s["p0"],3)}" PowerHigh="{round(s["p1"],3)}"{cad}'
        if txt:
            lines.append(f'    <{tag} {attrs}>{txt}</{tag}>')
        else:
            lines.append(f'    <{tag} {attrs}/>')
    lines += ['  </workout>', '</workout_file>', '']
    return "\n".join(lines)

def _course_data(segs, scale, as_watts=False):
    """Points (minutes, valeur). scale = 100 (%) ou FTP (watts)."""
    pts, t = [], 0.0
    for s in segs:
        v0 = s["p0"] * scale
        v1 = s["p1"] * scale
        fmt = (lambda v: str(int(round(v)))) if as_watts else (lambda v: f"{v:.1f}")
        pts.append(f'{t/60:.2f}\t{fmt(v0)}')
        t += s["dur"]
        pts.append(f'{t/60:.2f}\t{fmt(v1)}')
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
    body = _course_data(segs, 100.0, as_watts=False)
    tail = ["[END COURSE DATA]", "[COURSE TEXT]"] + _course_text(segs) + ["[END COURSE TEXT]", ""]
    return "\n".join(head + body + tail)

def render_erg(name, desc, segs, ftp):
    head = ["[COURSE HEADER]", "VERSION = 2", "UNITS = ENGLISH",
            f"DESCRIPTION = {desc} (FTP {ftp} W)", f"FILE NAME = {name}",
            "MINUTES WATTS", "[END COURSE HEADER]", "[COURSE DATA]"]
    body = _course_data(segs, float(ftp), as_watts=True)
    tail = ["[END COURSE DATA]", "[COURSE TEXT]"] + _course_text(segs) + ["[END COURSE TEXT]", ""]
    return "\n".join(head + body + tail)

# --------------------------------------------------------------------------
def slug(s):
    s = s.replace("'", "").replace('"', "")
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-")

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("--ftp", type=int, default=228, help="FTP (W) pour les fichiers .erg")
    ap.add_argument("--out", default=os.path.join(here, ".."), help="dossier racine de sortie")
    a = ap.parse_args()
    root = os.path.abspath(a.out)

    dirs = {fmt: os.path.join(root, f"bank_{fmt}") for fmt in ("zwo", "mrc", "erg")}
    for d in dirs.values():
        os.makedirs(d, exist_ok=True)

    idx = ["# Banque générée — importable dans Nolio (.zwo / .mrc / .erg)\n",
           ".zwo et .mrc = puissance relative (%FTP) -> **athlète-indépendants**.",
           f".erg = watts absolus, calculés ici pour **FTP = {a.ftp} W** (régénérer avec --ftp pour un autre athlète).\n",
           "| Code | Séance | .zwo | .mrc | .erg |", "|------|--------|------|------|------|"]
    for code, name, desc, segs in BANK:
        full = f"{code} {name}"
        full_desc = f"{desc} Double calibration %FTP + RPE."
        base = f"{code}_{slug(name)}"
        open(os.path.join(dirs["zwo"], base + ".zwo"), "w", encoding="utf-8").write(render_zwo(full, full_desc, segs))
        open(os.path.join(dirs["mrc"], base + ".mrc"), "w", encoding="utf-8").write(render_mrc(full, full_desc, segs))
        open(os.path.join(dirs["erg"], base + ".erg"), "w", encoding="utf-8").write(render_erg(full, full_desc, segs, a.ftp))
        idx.append(f"| {code} | {name} | `{base}.zwo` | `{base}.mrc` | `{base}.erg` |")
    open(os.path.join(root, "bank_zwo", "INDEX.md"), "w", encoding="utf-8").write("\n".join(idx) + "\n")
    print(f"{len(BANK)} séances x 3 formats générées dans {root}/bank_(zwo|mrc|erg)  [FTP .erg = {a.ftp} W]")

if __name__ == "__main__":
    main()
