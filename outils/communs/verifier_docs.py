#!/usr/bin/env python3
"""Vérifie la documentation (règles du §7 de kit/PROMPT.md) et affiche le nombre de points.

- liens et images relatifs existants, ancres internes existantes ;
- en-tête des manuels docs/<solution>/NN-*.md : Objet, Prérequis, Version décrite, Statut des informations
  (avec les quatre étiquettes), Précautions ; sections Sommaire, Dépannage, Sources ;
- ton dans docs/ : aucun « vous », « nous », « notre », « nos », « vos », « votre », aucun pictogramme ni émoji
  (hors blocs de code).
- captures (kit/PROMPT.md §6 bis) : au moins une image dans chaque manuel NN-*.md à partir de 01 ; un tableau
  « N° | Élément | Rôle » après chaque image d'un manuel (avant l'image ou le titre suivants) ; aucune image inutilisée
  dans docs/<solution>/img/ ; docs/<solution>/carte-interface.md présent, sans cellule vide dans la colonne
  « Manuel qui le couvre ».
Fichiers vérifiés : docs/**/*.md, README.md, outils/README.md, RAPPORT-*.md (ton : docs/ seulement).
Code de sortie 1 s'il reste au moins un point.
"""
import re, sys, unicodedata
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
LIEN = re.compile(r"(!?)\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
ANCRE_HTML = re.compile(r'<a\s+(?:id|name)="([^"]+)"')
TITRE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
PRONOMS = re.compile(r"\b(vous|nous|notre|nos|vos|votre)\b", re.IGNORECASE)
ETIQUETTES = ["[Vérifié]", "[Source]", "[Estimation]", "[À tester]"]
CHAMPS = ["**Objet**", "**Prérequis**", "**Version décrite**", "**Statut des informations**", "**Précautions**"]


def slug(titre):
    t = re.sub(r"<[^>]+>", "", titre)
    t = re.sub(r"[`*_~]|\[([^\]]*)\]\([^)]*\)", lambda m: m.group(1) or "", t).strip().lower()
    t = "".join(c for c in t if c.isalnum() or c in " -_")
    return t.replace(" ", "-")


def sans_code(texte):
    """Remplace les blocs de code clôturés par des lignes vides (garde la numérotation)."""
    lignes, dedans = [], False
    for l in texte.split("\n"):
        if l.lstrip().startswith("```"):
            dedans = not dedans; lignes.append(""); continue
        lignes.append("" if dedans else l)
    return lignes


def ancres(fichier, cache={}):
    if fichier not in cache:
        vus, res = {}, set()
        for l in sans_code(fichier.read_text(encoding="utf-8")):
            m = TITRE.match(l)
            if m:
                s = slug(m.group(2)); n = vus.get(s, 0); vus[s] = n + 1
                res.add(s if n == 0 else f"{s}-{n}")
            res.update(ANCRE_HTML.findall(l))
        cache[fichier] = res
    return cache[fichier]


def pictogramme(c):
    o = ord(c)
    return (o >= 0x2100 and unicodedata.category(c) == "So") or 0x1F000 <= o <= 0x1FAFF or 0x2600 <= o <= 0x27BF or o == 0xFE0F


def captures():
    """Contrôles des captures annotées et de la carte de l'interface (kit/PROMPT.md §6 bis)."""
    points = []
    for sol in sorted(d for d in (RACINE / "docs").iterdir() if d.is_dir()):
        rel = sol.relative_to(RACINE)
        utilisees = set()
        for f in sorted(sol.glob("*.md")):
            lignes = sans_code(f.read_text(encoding="utf-8"))
            for l in lignes:
                for img, _, cible in LIEN.findall(l):
                    if img:
                        utilisees.add((f.parent / cible.partition("#")[0]).resolve())
            if not re.match(r"\d\d-", f.name) or f.name.startswith("00-"):
                continue
            images = [i for i, l in enumerate(lignes) if l.lstrip().startswith("![")]
            if not images:
                points.append(f"{f.relative_to(RACINE)} captures : aucune capture d'écran")
            for i in images:
                suite = []
                for l in lignes[i + 1:]:
                    if l.lstrip().startswith("![") or l.startswith("#"):
                        break
                    suite.append(l)
                if not any(re.match(r"\|\s*N°\s*\|", l) for l in suite):
                    points.append(f"{f.relative_to(RACINE)}:{i + 1} captures : image sans tableau N° | Élément | Rôle")
        img = sol / "img"
        if img.is_dir():
            for i in sorted(img.rglob("*.png")):
                if i.resolve() not in utilisees:
                    points.append(f"{i.relative_to(RACINE)} captures : image inutilisée")
        carte = sol / "carte-interface.md"
        if not carte.exists():
            points.append(f"{rel}/carte-interface.md absent")
        else:
            entete, col = None, None
            for l in carte.read_text(encoding="utf-8").splitlines():
                cells = [c.strip() for c in l.strip().strip("|").split("|")] if l.startswith("|") else None
                if not cells:
                    entete = None; continue
                if entete is None:
                    entete = cells
                    col = next((k for k, c in enumerate(cells) if "Manuel qui le couvre" in c), None)
                    continue
                if set("".join(cells)) <= set("-: "):
                    continue
                if col is not None and (col >= len(cells) or not cells[col]):
                    points.append(f"{rel}/carte-interface.md ligne sans manuel : {cells[0]}")
    return points


def main():
    fichiers = sorted(RACINE.glob("docs/**/*.md")) + [f for f in [RACINE / "README.md", RACINE / "outils/README.md"] if f.exists()] \
        + sorted(RACINE.glob("RAPPORT-*.md"))
    points = []
    for f in fichiers:
        rel = f.relative_to(RACINE)
        lignes = sans_code(f.read_text(encoding="utf-8"))
        dans_docs = rel.parts[0] == "docs"
        for i, l in enumerate(lignes, 1):
            l_sans_inline = re.sub(r"`[^`]*`", "", l)
            for img, _, cible in LIEN.findall(l_sans_inline):
                if re.match(r"^[a-z]+:", cible):
                    continue
                chemin, _, ancre = cible.partition("#")
                dest = (f.parent / chemin).resolve() if chemin else f
                if chemin and not dest.exists():
                    points.append(f"{rel}:{i} lien cassé : {cible}")
                elif ancre and dest.suffix == ".md" and ancre not in ancres(dest):
                    points.append(f"{rel}:{i} ancre absente : {cible}")
            if dans_docs:
                for m in PRONOMS.finditer(re.sub(r"«[^»]*»", "", l_sans_inline)):  # libellés cités tels quels
                    points.append(f"{rel}:{i} ton : « {m.group(0)} »")
                for c in l:
                    if pictogramme(c):
                        points.append(f"{rel}:{i} pictogramme : U+{ord(c):04X}"); break
        if dans_docs and re.match(r"\d\d-", f.name):
            texte = "\n".join(lignes)
            entete = texte[:3000]
            for ch in CHAMPS:
                if ch not in entete:
                    points.append(f"{rel} en-tête : champ {ch} absent")
            for e in ETIQUETTES:
                if e not in entete:
                    points.append(f"{rel} en-tête : étiquette {e} absente")
            for s in ("## Sommaire", "## Dépannage", "## Sources"):
                if s not in texte:
                    points.append(f"{rel} section « {s[3:]} » absente")
    points += captures()
    for p in points:
        print(p)
    print(f"{len(points)} point(s) sur {len(fichiers)} fichier(s)")
    return 1 if points else 0


if __name__ == "__main__":
    sys.exit(main())
