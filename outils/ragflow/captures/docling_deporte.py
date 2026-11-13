"""Captures du manuel 06 de RAGFlow, section « Confier la lecture des PDF à un serveur Docling séparé » (étapes 31 à 33).

Prérequis : outils/ragflow/docling_deporte.sh brancher (serveur rag-docling-serve, DOCLING_SERVER_URL, ALLOW_ANY_HOST=1).
Lancement : outils/communs/captures/lancer.sh outils/ragflow/captures/docling_deporte.py <phase> [...]
Phases : choix (base « Manuel-Docling » créée à la souris, « Analyseur PDF » réglé sur « Docling » et enregistré),
lecture (contrat scanné téléversé et analysé, passage lu). Base supprimée ensuite par outils/ragflow/nettoyer_manuel.py.
Images : docs/ragflow/img/04-deepdoc/31-*.png à 33-*.png, à côté de 18-analyseurs-pdf.png (étape 30).
"""
import sys
import time
import traceback

from playwright.sync_api import sync_playwright

from captures import Session, cap, bouton, texte  # noqa: F401
from manuels_03_06 import (CORPUS, ECHEC, attendre, creer_base_simple, haut, ligne, ouvrir_base, popover,
                           segments)

M = "04-deepdoc"
BASE = "Manuel-Docling"
SCAN = "contrat-batterix-scan.pdf"


def choix(s):
    creer_base_simple(s, BASE)
    ouvrir_base(s, BASE, "Configuration")
    lab = lambda t: s.pg.locator("label").filter(has_text=t).first
    haut(bouton(s, "PDF"))
    declencheur = lab("Analyseur PDF").locator("xpath=following::button[1]")
    declencheur.click(); attendre(s, 1200)
    pop = popover(s)
    pop.get_by_text("Docling", exact=True).first.click(); attendre(s, 1500)
    print("après choix de Docling :", " | ".join(x for x in s.pg.inner_text("body").splitlines() if x.strip())[:2500],
          flush=True)
    enregistrer = s.pg.get_by_role("button", name="Enregistrer", exact=True).last
    haut(declencheur)
    cap(s, M, "31-analyseur-docling", [(declencheur, "Analyseur PDF"), (enregistrer, "Enregistrer")])
    enregistrer.click(); attendre(s, 2500)
    s.pg.reload(); attendre(s, 3500)
    haut(bouton(s, "PDF"))
    valeur = lab("Analyseur PDF").locator("xpath=following::button[1]").inner_text()
    print("valeur relue après rechargement :", valeur, flush=True)


def lecture(s):
    ouvrir_base(s, BASE)
    if not ligne(s, SCAN).count():
        bouton(s, "Ajouter un fichier").click(); attendre(s, 1000)
        s.pg.get_by_role("menuitem").filter(has_text="Téléverser un fichier").first.click(); attendre(s, 1500)
        dlg = s.pg.get_by_role("dialog")
        dlg.locator("input[type=file]").first.set_input_files([CORPUS + SCAN]); attendre(s, 1500)
        sw = dlg.get_by_role("switch").first
        if sw.get_attribute("aria-checked") != "true":
            sw.click(); attendre(s, 500)
        dlg.get_by_role("button", name="Enregistrer").click()
        t0 = time.time(); attendre(s, 2500)
        while time.time() - t0 < 600:
            s.pg.reload(); attendre(s, 2000)
            if segments(s, SCAN):
                break
        print(f"scan analysé par Docling en moins de {time.time() - t0:.0f} s (relevé toutes les 2 s environ) : "
              f"{segments(s, SCAN)} segment(s)", flush=True)
    l = ligne(s, SCAN)
    cap(s, M, "32-scan-lu-par-docling", [(l.get_by_text(SCAN), SCAN), (l.locator("td").nth(4), "Nombre de segments"),
                                         (l.locator("[data-testid=document-parse-status] button").last, "état de l'analyse")])
    l.get_by_text(SCAN).click(); attendre(s, 4000)
    passage = s.pg.get_by_text("CONTRAT D'APPROVISIONNEMENT", exact=False).first
    print("passage :", passage.inner_text()[:400], flush=True)
    cap(s, M, "33-passage-docling", [(passage, "texte du scan")])


if __name__ == "__main__":
    with sync_playwright() as p:
        s = Session(p)
        s.pg.set_default_timeout(15000)
        try:
            s.connexion(); s.francais()
            for phase in sys.argv[1:] or ["choix", "lecture"]:
                globals()[phase](s)
        except Exception:
            traceback.print_exc()
            ECHEC.mkdir(parents=True, exist_ok=True)
            s.pg.screenshot(path=str(ECHEC / "echec-docling.png"))
            (ECHEC / "echec-docling.txt").write_text(s.pg.inner_text("body"))
            sys.exit(1)
        finally:
            s.b.close()
