"""Captures des manuels RAGFlow (interface en français : langue du compte réglée par outils/ragflow/configurer.py).

Lancement : outils/communs/captures/lancer.sh outils/ragflow/captures/captures.py <scénario> [...]
Scénarios : explorer (repérage, images dans donnees/captures-explorer, non versionnées), puis un scénario par manuel.
Images des manuels : docs/ragflow/img/<manuel>/NN-nom.png. Aucun secret n'est saisi à l'écran avant capture.
Le conteneur Playwright rejoint rag-local : RAGFlow s'ouvre sous http://rag-ragflow-server (port 80 interne).
"""
import json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = "http://rag-ragflow-server"
COMPTE = json.loads(Path("donnees/ragflow/compte.json").read_text())
IMG = Path("docs/ragflow/img")
EXPLO = Path("donnees/captures-explorer")


class Session:
    def __init__(self, p):
        self.b = p.chromium.launch()
        self.pg = self.b.new_page(viewport={"width": 1440, "height": 900}, locale="fr-FR")

    def shot(self, manuel, nom, plein=False):
        d = (EXPLO if manuel is None else IMG / manuel); d.mkdir(parents=True, exist_ok=True)
        self.pg.wait_for_timeout(1500)
        self.pg.screenshot(path=str(d / f"{nom}.png"), full_page=plein)
        print("capture", d / f"{nom}.png", flush=True)

    def texte(self, nom):
        EXPLO.mkdir(parents=True, exist_ok=True)
        (EXPLO / f"{nom}.txt").write_text(self.pg.inner_text("body"))

    def aller(self, chemin, attente=3000):
        self.pg.goto(URL + chemin); self.pg.wait_for_load_state("load"); self.pg.wait_for_timeout(attente)

    def connexion(self, manuel=None):
        self.aller("/login")
        if manuel:
            self.shot(manuel, "01-connexion")
        self.pg.locator("input[type=email], input[name=email]").first.fill(COMPTE["email"])
        self.pg.locator("input[type=password]").first.fill(COMPTE["password"])
        self.pg.keyboard.press("Enter")
        self.pg.wait_for_timeout(4000)


def explorer(s, *chemins):
    s.connexion()
    s.shot(None, "00-apres-connexion"); s.texte("00-apres-connexion")
    for c in chemins or ["/home", "/datasets", "/chats", "/agents", "/searches", "/files", "/memories",
                         "/user-setting/model", "/profile-setting/model", "/data-source", "/agent-templates"]:
        nom = c.strip("/").replace("/", "_") or "racine"
        s.aller(c)
        s.shot(None, nom); s.texte(nom)


if __name__ == "__main__":
    scenario, *args = sys.argv[1:]
    with sync_playwright() as p:
        s = Session(p)
        try:
            globals()[scenario.replace("-", "_")](s, *args)
        finally:
            s.b.close()
