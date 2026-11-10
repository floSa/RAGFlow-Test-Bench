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
        # la page contient deux formulaires (connexion et inscription) dont un masqué : champs visibles seulement
        self.pg.locator("input[name=email]:visible, input[type=email]:visible").first.fill(COMPTE["email"])
        self.pg.locator("input[type=password]:visible").first.fill(COMPTE["password"])
        self.pg.locator("button[type=submit]:visible").first.click()
        try:
            self.pg.wait_for_url(lambda u: "login" not in u, timeout=20000)
        except Exception:
            self.shot(None, "echec-connexion"); self.texte("echec-connexion")
            raise
        self.pg.wait_for_timeout(3000)

    def francais(self, manuel=None):
        """Langue de l'interface : sélecteur de l'en-tête (« English » -> « Français »), mémorisé par le navigateur
        (localStorage « lng ») ; le réglage de langue du compte ne change pas l'interface au chargement."""
        self.pg.get_by_text("English", exact=True).first.click()
        self.pg.wait_for_timeout(800)
        if manuel:
            self.shot(manuel, "02-choix-langue")
        self.pg.get_by_text("Français", exact=True).first.click()
        self.pg.wait_for_timeout(2500)


def diag_connexion(s):
    """Repérage : requêtes réseau émises pendant la connexion (statut et début de réponse)."""
    s.pg.on("response", lambda r: print("réponse", r.status, r.request.method, r.url[:90],
                                        (r.text()[:200] if "/api/" in r.url else ""), flush=True))
    s.pg.on("console", lambda m: print("console", m.type, m.text[:200], flush=True))
    try:
        s.connexion()
    except Exception as e:
        print("échec", str(e)[:200])


def explorer(s, *chemins):
    s.connexion()
    s.francais()
    s.shot(None, "00-apres-connexion"); s.texte("00-apres-connexion")
    for c in chemins or ["/home", "/datasets", "/chats", "/agents", "/searches", "/files", "/memories",
                         "/user-setting/model", "/profile-setting/model", "/data-source", "/agent-templates"]:
        nom = c.strip("/").replace("/", "_") or "racine"
        s.aller(c)
        s.shot(None, nom); s.texte(nom)


def cliquer(s, texte, attente=2500):
    s.pg.get_by_text(texte, exact=True).first.click()
    s.pg.wait_for_timeout(attente)


def installation(s):
    m = "01-installation"
    s.connexion(); s.francais()
    s.aller("/user-setting/model"); s.shot(m, "01-modeles-par-defaut")
    cliquer(s, "VLLM"); s.shot(m, "02-fournisseur-vllm")


def prise_en_main(s):
    m = "02-prise-en-main"
    s.connexion(m)
    s.francais(m)
    s.aller("/home"); s.shot(m, "03-accueil")
    s.aller("/datasets"); s.shot(m, "04-bases-de-connaissances")
    cliquer(s, "Démo Vélanor", 4000); s.shot(m, "05-documents"); s.texte("02-documents")
    cliquer(s, "contrat-batterix-scan.pdf", 5000); s.shot(m, "06-passages"); s.texte("02-passages")
    s.aller("/chats"); s.shot(m, "07-discussions")
    cliquer(s, "Démo Vélanor", 4000); s.texte("02-assistant")
    cliquer(s, "Contrat Batterix", 4000); s.shot(m, "08-conversation"); s.texte("02-conversation")


def decoupage(s):
    m = "03-datasets-et-decoupage"
    s.connexion(); s.francais()
    s.aller("/datasets"); cliquer(s, "Démo Vélanor", 4000)
    cliquer(s, "Configuration", 3000); s.shot(m, "01-configuration", plein=True); s.texte("03-configuration")
    cliquer(s, "Test de récupération", 3000)
    champ = s.pg.locator("textarea:visible").first
    champ.fill("pénalités de retard du contrat Batterix")
    s.pg.get_by_role("button", name="Test", exact=True).first.click()
    s.pg.wait_for_timeout(5000); s.shot("05-assistants-et-citations", "01-test-de-recuperation"); s.texte("05-test-recuperation")


def assistant_reglages(s):
    m = "05-assistants-et-citations"
    s.connexion(); s.francais()
    s.aller("/chats"); cliquer(s, "Démo Vélanor", 4000)
    s.pg.locator("button:has(svg.lucide-settings), [class*=setting]").last.click()
    s.pg.wait_for_timeout(2500); s.shot(m, "02-reglages-assistant", plein=True); s.texte("05-reglages")


def agentique(s):
    m = "06-agentic-rag"
    s.connexion(); s.francais()
    s.aller("/chats"); cliquer(s, "Démo Vélanor", 4000); cliquer(s, "Audit fournisseur", 3000)
    s.pg.get_by_text("Naive", exact=True).first.click(); s.pg.wait_for_timeout(1500)
    s.shot(m, "01-modes-de-reponse"); s.texte("06-modes")


def agents(s):
    m = "08-agents"
    s.connexion(); s.francais()
    s.aller("/agent-templates"); s.shot(m, "01-gabarits")
    s.aller("/agents"); s.shot(m, "02-liste"); cliquer(s, "Agent démo Vélanor", 6000)
    s.shot(m, "03-canevas"); s.texte("08-canevas")


def compilation(s, base):
    m = "07-knowledge-compilation"
    s.connexion(); s.francais()
    s.aller("/datasets"); cliquer(s, base, 4000)
    cliquer(s, "Artifacts", 5000)
    s.pg.get_by_text("Wiki", exact=True).first.click(); s.pg.wait_for_timeout(1200)
    s.shot(m, "01-types-d-artefacts"); s.texte("07-types")
    import re
    s.pg.get_by_role("option").filter(has_text=re.compile("mind", re.I)).first.click()
    s.pg.wait_for_timeout(6000); s.shot(m, "02-carte-mentale"); s.texte("07-carte")


if __name__ == "__main__":
    scenario, *args = sys.argv[1:]
    with sync_playwright() as p:
        s = Session(p)
        try:
            globals()[scenario.replace("-", "_")](s, *args)
        finally:
            s.b.close()
