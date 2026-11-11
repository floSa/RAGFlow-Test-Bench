"""Carte de l'interface RAGFlow (kit/PROMPT.md, phase C) : parcours de chaque page et menu, connecté et en français.

Lancement : outils/communs/captures/lancer.sh outils/ragflow/captures/carte.py carte
Sorties : une capture de repérage par page dans docs/ragflow/img/carte/NN-nom.png ; texte de la page, adresse et
inventaire des éléments visibles (boutons, onglets, champs, liens) dans outils/resultats/ragflow/captures/carte/NN-nom.txt.
Lecture seule : les fenêtres de création sont ouvertes puis fermées par « Échap » sans rien enregistrer.
Le jeu de démonstration (base, assistant et agent « Démo Vélanor ») sert de page d'exemple, sans modification.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from captures import Session, URL, _INVENTAIRE  # noqa: E402
from annoter import capture  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

IMG = Path("docs/ragflow/img/carte")
TXT = Path("outils/resultats/ragflow/captures/carte")


def releve(s, base, plein=False, masques=()):
    """Capture de repérage et texte de la page (adresse, texte visible, inventaire des éléments).
    `base` : NN-nom, numéro fixe pour pouvoir rejouer une seule section."""
    s.pg.wait_for_timeout(1500)
    capture(s.pg, IMG / f"{base}.png", masques=masques, plein=plein)
    TXT.mkdir(parents=True, exist_ok=True)
    inv = s.pg.evaluate(_INVENTAIRE)
    (TXT / f"{base}.txt").write_text(
        f"adresse : {s.pg.url.replace(URL, '')}\n\n== texte ==\n{s.pg.inner_text('body')}\n\n== éléments visibles ==\n"
        + "\n".join(inv) + "\n")


def clic(s, texte, attente=2500, exact=True, role=None):
    loc = s.pg.get_by_role(role, name=texte, exact=exact) if role else s.pg.get_by_text(texte, exact=exact)
    loc.first.click()
    s.pg.wait_for_timeout(attente)


def echap(s):
    s.pg.keyboard.press("Escape"); s.pg.wait_for_timeout(800)


def etape(f):
    """Chaque page est relevée indépendamment : un échec est noté et le parcours continue."""
    def g(s, *a):
        try:
            f(s, *a)
        except Exception as e:  # noqa: BLE001
            print("ÉCHEC", f.__name__, str(e).splitlines()[0][:200], flush=True)
            s.pg.screenshot(path=f"donnees/captures-explorer/echec-{f.__name__}.png")
    return g


def plus(s):
    """Bouton de création à icône « + » de la page courante (en haut à droite, ou au centre d'une liste vide)."""
    s.pg.locator("button:has(svg.lucide-plus), div:has(> svg.lucide-plus)").last.click()
    s.pg.wait_for_timeout(2000)


def nav(s, libelle):
    """Clic dans la barre du haut, en repartant de l'accueil (certaines pages, comme « Artifacts », n'ont pas d'en-tête)."""
    s.aller("/", 2000)
    s.pg.locator("header, nav").get_by_text(libelle, exact=True).first.click()
    s.pg.wait_for_timeout(3000)


@etape
def accueil(s):
    s.aller("/")
    releve(s, "01-accueil")
    s.pg.get_by_text("Français", exact=True).first.click(); s.pg.wait_for_timeout(800)
    releve(s, "02-menu-langue"); echap(s)


@etape
def bases(s):
    nav(s, "Base de connaissances"); releve(s, "03-bases-de-connaissances")
    clic(s, "Créer une base de connaissances", role="button", exact=False)
    releve(s, "04-base-creation"); echap(s)


@etape
def base_demo(s):
    nav(s, "Base de connaissances")
    clic(s, "Démo Vélanor", 4000); releve(s, "05-base-fichiers")
    clic(s, "contrat-batterix-scan.pdf", 5000); releve(s, "06-base-passages")
    s.pg.go_back(); s.pg.wait_for_timeout(3000)
    for onglet, nom in [("Test de récupération", "07-base-test-de-recuperation"), ("Journaux", "08-base-journaux"),
                        ("Configuration", "09-base-configuration"), ("Artifacts", "10-base-artifacts")]:
        clic(s, onglet, 4000)
        releve(s, nom, plein=("configuration" in nom))
    s.pg.get_by_role("combobox").first.click(); s.pg.wait_for_timeout(1000)
    releve(s, "11-base-artifacts-types"); echap(s)


@etape
def discussions(s):
    nav(s, "Discussion"); releve(s, "12-discussions")
    clic(s, "Créer un chat", role="button", exact=False); releve(s, "13-discussion-creation"); echap(s)
    clic(s, "Démo Vélanor", 4000); releve(s, "14-discussion-assistant")
    clic(s, "Contrat Batterix", 4000); releve(s, "15-discussion-conversation")
    s.pg.locator("button:has(svg.lucide-settings), [class*=setting]").last.click(); s.pg.wait_for_timeout(2500)
    releve(s, "16-discussion-parametres")
    clic(s, "Paramètres du modèle", 1500); clic(s, "Paramètres avancés", 1500)
    releve(s, "16-discussion-parametres-detail", plein=True); echap(s)


@etape
def recherche(s):
    nav(s, "Recherche"); releve(s, "17-recherche")
    plus(s); releve(s, "18-recherche-creation"); echap(s)


@etape
def agents(s):
    nav(s, "Agent"); releve(s, "19-agents-workflow")
    for onglet, nom in [("Ingestion pipeline", "20-agents-ingestion-pipeline"),
                        ("Compilation operator", "21-agents-compilation-operator")]:
        clic(s, onglet, 3000); releve(s, nom)
    clic(s, "Workflow", 3000)
    plus(s); releve(s, "22-agents-menu-creation")
    clic(s, "Créer depuis un modèle", 4000, exact=False); releve(s, "23-agents-gabarits")
    nav(s, "Agent"); clic(s, "Agent démo Vélanor", 6000); releve(s, "24-agent-canevas")


@etape
def memoire(s):
    nav(s, "Mémoire"); releve(s, "25-memoire")
    plus(s); releve(s, "26-memoire-creation"); echap(s)


@etape
def fichiers(s):
    nav(s, "Gestion des fichiers"); releve(s, "27-gestion-des-fichiers")


@etape
def compte(s):
    s.aller("/", 2000)
    s.pg.locator("header a").filter(has_text="BR").first.click()
    s.pg.wait_for_timeout(3000)
    for entree, nom in [("Fournisseurs de modèles", "28-compte-fournisseurs-de-modeles"),
                        ("Sources de données", "29-compte-sources-de-donnees"), ("Canaux de chat", "30-compte-canaux-de-chat"),
                        ("MCP", "31-compte-mcp"), ("Équipe", "32-compte-equipe"), ("Profil", "33-compte-profil"),
                        ("API", "34-compte-api")]:
        clic(s, entree, 3000)
        releve(s, nom, masques=cles(s))


def cles(s):
    """Champs qui affichent une clé d'API (valeur « ragflow-… ») : masqués sur la capture."""
    return [c for c in s.pg.locator("input:visible").all() if (c.input_value() or "").startswith("ragflow-")]


def carte(s, *pages):
    s.connexion(); s.francais()
    for p in pages or ["accueil", "bases", "base_demo", "discussions", "recherche", "agents", "memoire", "fichiers", "compte"]:
        globals()[p](s)


if __name__ == "__main__":
    scenario, *args = sys.argv[1:]
    with sync_playwright() as p:
        s = Session(p)
        try:
            globals()[scenario](s, *args)
        finally:
            s.b.close()
