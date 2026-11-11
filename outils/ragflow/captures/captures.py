"""Captures des manuels RAGFlow (interface en français : langue du compte réglée par outils/ragflow/configurer.py).

Lancement : outils/communs/captures/lancer.sh outils/ragflow/captures/captures.py <scénario> [...]
Scénarios : explorer (repérage, images dans donnees/captures-explorer, non versionnées), puis un scénario par manuel ;
les manuels 03 à 06 ont leur propre script, outils/ragflow/captures/manuels_03_06.py, qui reprend ces helpers.
Images des manuels : docs/ragflow/img/<manuel>/NN-nom.png. Aucun secret n'est saisi à l'écran avant capture.
Le conteneur Playwright rejoint rag-local : RAGFlow s'ouvre sous http://rag-ragflow-server (port 80 interne).
"""
import json, re, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright
from annoter import capture

URL = "http://rag-ragflow-server"
COMPTE = json.loads(Path("donnees/ragflow/compte.json").read_text())
IMG = Path("docs/ragflow/img")
EXPLO = Path("donnees/captures-explorer")
TXT = Path("outils/resultats/ragflow/captures")

_INVENTAIRE = """
() => {
  const vis = e => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  const sel = 'button, a[href], [role=tab], [role=menuitem], [role=switch], [role=checkbox], [role=combobox], '
    + '[role=radio], [role=slider], [role=option], input, textarea, select, label';
  const out = [], vu = new Set();
  for (const e of document.querySelectorAll(sel)) {
    if (!vis(e) || e.closest('.rag-annotation-manuel')) continue;
    const t = (e.innerText || e.getAttribute('aria-label') || e.getAttribute('placeholder') || e.getAttribute('title')
      || e.getAttribute('name') || '').trim().replace(/\\s+/g, ' ').slice(0, 90)
      || ((e.querySelector('svg') || {}).getAttribute ? '[icône ' + ((e.querySelector('svg').getAttribute('class') || '')
           .split(' ').find(c => c.startsWith('lucide-')) || 'sans nom') + ']' : '');
    const genre = e.getAttribute('role') || (e.tagName.toLowerCase() + (e.type && e.tagName !== 'BUTTON' ? ':' + e.type : ''));
    const k = genre + ' | ' + t;
    if (!vu.has(k)) { vu.add(k); out.push(k); }
  }
  return out;
}
"""


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


def cap(s, manuel, nom, elements=(), masques=(), plein=False, clip=None):
    """Capture annotée d'une étape : image dans docs/ragflow/img/<manuel>/, texte de la page et inventaire des
    éléments visibles dans outils/resultats/ragflow/captures/<manuel>/ (traçabilité, kit/PROMPT.md §6 bis)."""
    s.pg.wait_for_timeout(800)
    txt = TXT / manuel / f"{nom}.txt"
    lib = capture(s.pg, IMG / manuel / f"{nom}.png", elements=elements, masques=masques, plein=plein, clip=clip, texte=txt)
    with txt.open("a") as f:
        f.write(f"\n\n== adresse ==\n{s.pg.url.replace(URL, '')}\n== pastilles ==\n"
                + "\n".join(f"{n}. {l}" for n, l in lib) + "\n== éléments visibles ==\n"
                + "\n".join(s.pg.evaluate(_INVENTAIRE)) + "\n")
    return lib


def bouton(s, nom, exact=True):
    return s.pg.get_by_role("button", name=nom, exact=exact).first


def texte(s, t, exact=True):
    return s.pg.get_by_text(t, exact=exact).first


def visite(s):
    """Manuel 00 : visite générale de l'accueil (barre du haut numérotée)."""
    m = "00-notions-fondamentales"
    s.connexion(); s.francais()
    s.aller("/", 3000)
    nav = texte(s, "Base de connaissances").locator("xpath=ancestor::*[.//a[normalize-space()='Gestion des fichiers']][1]")
    haut = {"x": 0, "y": 0, "width": 1440, "height": 240}
    cap(s, m, "01-barre-de-navigation", [
        (nav.locator("a").first, "Accueil"),
        (nav.get_by_text("Base de connaissances", exact=True), "Base de connaissances"),
        (nav.get_by_text("Discussion", exact=True), "Discussion"),
        (nav.get_by_text("Recherche", exact=True), "Recherche"),
        (nav.get_by_text("Agent", exact=True), "Agent"),
        (nav.get_by_text("Mémoire", exact=True), "Mémoire")], clip=haut)
    cap(s, m, "02-en-tete-droite", [
        (nav.get_by_text("Gestion des fichiers", exact=True), "Gestion des fichiers"),
        (s.pg.locator("a[href*=discord]").first, "Discord"),
        (s.pg.locator("a[href*=github]").first, "GitHub"),
        (bouton(s, "Français"), "Français"),
        (s.pg.locator("a:has(svg.lucide-circle-question-mark)").first, "aide"),
        (s.pg.locator("button:has(svg.lucide-moon)").first, "thème")], clip=haut)
    cap(s, m, "03-accueil", [
        (texte(s, "Bienvenue sur RAGFlow", exact=False), "Bienvenue"),
        (texte(s, "Démo Vélanor").locator("xpath=ancestor::div[contains(., 'Fichiers')][1]"), "carte de base"),
        (texte(s, "Voir tout"), "Voir tout"),
        (bouton(s, "Recherche").last.locator("xpath=.."), "onglets"),
        (s.pg.locator("a").filter(has_text="BR").first, "compte")])


def installation(s):
    """Manuel 01 : inscription du premier compte (écran rempli, non validé), fournisseurs de modèles, ajout d'une
    instance à la souris (nom « Manuel-… », supprimée ensuite), modèles par défaut."""
    m = "01-installation"
    s.aller("/login", 3000)
    texte(s, "Sign up").click(); s.pg.wait_for_timeout(1500)
    champ = lambda n: s.pg.locator(f"input[name={n}]:visible").first
    champ("email").fill("manuel.compte@exemple.fr")
    champ("nickname").fill("Manuel-Compte")
    champ("password").fill("NePasUtiliser-0000")
    cap(s, m, "01-inscription", [
        (champ("email"), "Email"), (champ("nickname"), "Nickname"), (champ("password"), "Password"),
        (bouton(s, "Continue"), "Continue"), (s.pg.locator(":text-is('Sign in'):visible").first, "Sign in")], masques=[champ("password")])
    s.connexion(); s.francais()
    s.aller("/user-setting/model", 4000)
    cap(s, m, "02-fournisseurs-de-modeles", [
        (texte(s, "Fournisseurs de modèles"), "Fournisseurs de modèles"),
        (bouton(s, "Définir les modèles par défaut"), "Définir les modèles par défaut"),
        (s.pg.get_by_placeholder("Rechercher").first, "Rechercher"),
        (texte(s, "VLLM").locator("xpath=ancestor::button[1]"), "VLLM")])
    texte(s, "VLLM").click(); s.pg.wait_for_timeout(3000)
    titre = s.pg.locator(":text-is('llm-service-embed')").first
    # cartes d'instance dans l'ordre du document : llm-service-embed (dépliée), llm-service-chat, puis la nouvelle
    cap(s, m, "03-fournisseur-vllm", [
        (titre, "llm-service-embed"), (s.pg.get_by_placeholder("http://host.docker.internal:8000/v1").first, "URL de base"),
        (bouton(s, "Lister les modèles"), "Lister les modèles"),
        (s.pg.get_by_role("button", name="Remove bge-m3").first, "retirer bge-m3"),
        (bouton(s, "Enregistrer"), "Enregistrer")])
    ajout = s.pg.get_by_role("button", name="Add instance")
    ajout.scroll_into_view_if_needed(); s.pg.wait_for_timeout(500)
    cap(s, m, "04-add-instance", [(ajout, "Add instance")])
    ajout.click(); s.pg.wait_for_timeout(2000)
    nom = s.pg.get_by_placeholder("Please input instance name")
    nom.evaluate("e => e.scrollIntoView({block: 'start'})"); s.pg.wait_for_timeout(800)
    nom.fill("Manuel-instance")
    carte = s.pg  # la nouvelle carte est la dernière : localisateurs en .last
    url = carte.get_by_placeholder("http://host.docker.internal:8000/v1").last
    url.fill("http://vllm-embed:8000/v1")
    cap(s, m, "05-ajout-instance", [
        (nom, "Nom de l'instance"), (carte.get_by_placeholder("Veuillez saisir la clé API", exact=False).last, "Clé API"),
        (url, "URL de base"), (carte.get_by_role("button", name="Lister les modèles").last, "Lister les modèles")])
    carte.get_by_role("button", name="Lister les modèles").last.click(); s.pg.wait_for_timeout(5000)
    cap(s, m, "06-modeles-listes", [
        (carte.locator(":text-is('bge-m3')").last, "bge-m3"),
        (carte.get_by_role("button", name="Remove bge-m3").last, "retirer le modèle"),
        (carte.get_by_role("button", name="Enregistrer").last, "Enregistrer")])
    carte.get_by_role("button", name="Enregistrer").last.click(); s.pg.wait_for_timeout(3000)
    titre = s.pg.locator(":text-is('Manuel-instance')").first
    titre.evaluate("e => e.scrollIntoView({block: 'start'})"); s.pg.wait_for_timeout(800)
    poubelle = s.pg.get_by_role("button", name="Delete instance").first  # première carte : Manuel-instance
    cap(s, m, "07-instance-enregistree", [(titre, "Manuel-instance"), (poubelle, "Delete instance")])
    poubelle.click(); s.pg.wait_for_timeout(1500)
    dlg = s.pg.get_by_role("alertdialog").or_(s.pg.get_by_role("dialog")).first
    conf = dlg.get_by_role("button").filter(has_text=re.compile("Supprimer|Delete|Confirmer|OK", re.I)).last
    cap(s, m, "08-suppression-instance", [(dlg, "confirmation"), (conf, conf.inner_text().strip())])
    conf.click(); s.pg.wait_for_timeout(2500)
    bouton(s, "Définir les modèles par défaut").click(); s.pg.wait_for_timeout(2500)
    ligne = lambda t: s.pg.locator("label").filter(has_text=t).first.locator("xpath=..")
    cap(s, m, "09-modeles-par-defaut", [
        (ligne("Modèle de chat"), "Modèle de chat"), (ligne("Modèle d'embedding"), "Modèle d'embedding"),
        (ligne("Modèle Img2txt"), "Modèle Img2txt"), (ligne("Modèle Speech2txt"), "Modèle Speech2txt"),
        (ligne("Modèle de rerank"), "Modèle de rerank"), (ligne("Modèle TTS"), "Modèle TTS")])
    ligne("Modèle de chat").get_by_text("gemma4:e4b").click()
    s.pg.wait_for_timeout(1500)
    liste = s.pg.locator("[role=listbox], [role=dialog], [data-radix-popper-content-wrapper]").last
    cap(s, m, "10-choix-modele-de-chat", [(liste, "liste des modèles de chat")])
    s.pg.keyboard.press("Escape")


BASE_02, CHAT_02 = "Manuel-Prise-en-main", "Manuel-Assistant"
DOCS_02 = ["corpus/documents/cse-2025-10-14.md", "corpus/documents/faq-sav.html"]
QUESTION_02 = "Quel est le montant de la prime d'intéressement 2025 ?"


def prise_en_main(s, *phases):
    """Manuel 02, tout à la souris : connexion, langue, base de connaissances « Manuel-Prise-en-main » créée, deux
    fichiers importés et analysés, passages lus, assistant « Manuel-Assistant » créé et relié, question, citations.
    Phases : base, assistant, saisie (question tapée sans envoi), envoi (demande le modèle de chat), demo (réponse
    citée déjà présente dans le jeu de démonstration) ; par défaut base, assistant, envoi. Objets « Manuel-… » supprimés ensuite par
    outils/ragflow/nettoyer_manuel.py."""
    m = "02-prise-en-main"
    phases = phases or ("base", "assistant", "envoi")
    s.aller("/login", 3000)
    champ = lambda n: s.pg.locator(f"input[name={n}]:visible").first
    champ("email").fill(COMPTE["email"]); champ("password").fill(COMPTE["password"])
    cap(s, m, "01-connexion", [
        (champ("email"), "Email"), (champ("password"), "Password"),
        (s.pg.locator("label:visible").filter(has_text="Remember me").first, "Remember me"),
        (s.pg.locator("button[type=submit]:visible").first, "Sign in")], masques=[champ("password")])
    s.pg.locator("button[type=submit]:visible").first.click()
    s.pg.wait_for_url(lambda u: "login" not in u, timeout=20000); s.pg.wait_for_timeout(3000)
    texte(s, "English").click(); s.pg.wait_for_timeout(800)
    cap(s, m, "02-choix-langue", [(texte(s, "English"), "English"), (texte(s, "Français"), "Français")])
    texte(s, "Français").click(); s.pg.wait_for_timeout(2500)
    nav = texte(s, "Base de connaissances").locator("xpath=ancestor::*[.//a[normalize-space()='Gestion des fichiers']][1]")
    cap(s, m, "03-accueil", [(nav.get_by_text("Base de connaissances", exact=True), "Base de connaissances"),
                             (nav.get_by_text("Discussion", exact=True), "Discussion"),
                             (bouton(s, "Français"), "Français")])
    for ph in phases:
        s.aller("/", 2500)  # chaque phase repart de l'accueil (les passages s'ouvrent sans barre du haut)
        globals()["phase_" + ph](s, m, nav)


def phase_base(s, m, nav):
    nav.get_by_text("Base de connaissances", exact=True).click(); s.pg.wait_for_timeout(3000)
    creer = bouton(s, "Créer une base de connaissances")
    cap(s, m, "04-bases-de-connaissances", [
        (creer, "Créer une base de connaissances"), (s.pg.get_by_role("searchbox").first, "Rechercher"),
        (texte(s, "Démo Vélanor").locator("xpath=ancestor::div[contains(., 'Fichiers')][1]"), "carte d'une base")])
    creer.click(); s.pg.wait_for_timeout(1500)
    dlg = s.pg.get_by_role("dialog")
    dlg.get_by_placeholder("Veuillez saisir un nom !").fill(BASE_02)
    cap(s, m, "05-creation-base", [(dlg.get_by_placeholder("Veuillez saisir un nom !"), "Nom"),
                                   (dlg.get_by_role("button").filter(has_text="bge-m3"), "Modèle d'embedding"),
                                   (dlg.get_by_role("button").filter(has_text="General"), "General (built in)"),
                                   (dlg.get_by_role("button", name="Enregistrer"), "Enregistrer")])
    dlg.get_by_role("button", name="Enregistrer").click(); s.pg.wait_for_timeout(4000)
    ajout = bouton(s, "Ajouter un fichier")
    cap(s, m, "06-base-vide", [(texte(s, BASE_02), BASE_02), (s.pg.get_by_role("link", name="Fichiers", exact=True).first, "Fichiers"),
                               (ajout, "Ajouter un fichier")])
    ajout.click(); s.pg.wait_for_timeout(1200)
    cap(s, m, "07-menu-ajout", [(s.pg.get_by_role("menuitem").filter(has_text=t).first, t)
                                for t in ("Téléverser un fichier", "Créer un fichier vide")])
    s.pg.get_by_role("menuitem").filter(has_text="Téléverser un fichier").first.click(); s.pg.wait_for_timeout(1500)
    dlg = s.pg.get_by_role("dialog")
    dlg.locator("input[type=file]").set_input_files(DOCS_02); s.pg.wait_for_timeout(1500)
    cap(s, m, "08-televersement", [
        (dlg.get_by_role("switch").first.locator("xpath=.."), "Analyser à la création"),
        (dlg.get_by_role("tab", name="Fichiers").locator("xpath=.."), "Fichiers, Dossier"),
        (dlg.get_by_text("Glissez-déposez", exact=False).locator("xpath=.."), "zone de dépôt"),
        (dlg.get_by_text("cse-2025-10-14.md").locator("xpath=ancestor::div[.//button][1]"), "fichier choisi"),
        (dlg.get_by_role("button", name="Enregistrer"), "Enregistrer")])
    dlg.get_by_role("button", name="Enregistrer").click(); s.pg.wait_for_timeout(4000)
    ligne = lambda nom: s.pg.locator("tr").filter(has_text=nom).first
    lancer = lambda nom: ligne(nom).locator("xpath=.//button[normalize-space()='General']/following::button[1]")
    entete = lambda t: s.pg.locator("th").filter(has_text=t).first
    cap(s, m, "09-fichiers-importes", [
        (lancer("cse-2025-10-14.md"), "lancer l'analyse"), (entete("Nombre de segments"), "Nombre de segments"),
        (ligne("cse-2025-10-14.md").get_by_role("switch"), "Activé"),
        (ligne("cse-2025-10-14.md").get_by_role("button", name="General"), "General")])
    t0 = time.time()
    for nom in ("cse-2025-10-14.md", "faq-sav.html"):
        lancer(nom).click(); s.pg.wait_for_timeout(700)
    s.pg.wait_for_timeout(1500)
    etat = ligne("cse-2025-10-14.md").get_by_text(re.compile("En attente|En analyse|EN ATTENTE|EN ANALYSE")).first
    cap(s, m, "10-analyse-en-cours", [(etat, etat.inner_text().strip()),
                                      (bouton(s, "Cancel parsing tasks", exact=False), "Cancel parsing tasks")])
    while time.time() - t0 < 600:
        s.pg.reload(); s.pg.wait_for_timeout(3000)
        n = [ligne(d).locator("td").nth(4).inner_text().strip() for d in ("cse-2025-10-14.md", "faq-sav.html")]
        if all(x.isdigit() and int(x) > 0 for x in n):
            break
    print(f"analyse terminée en moins de {time.time() - t0:.0f} s (relevé toutes les 3 s environ) : segments {n}", flush=True)
    cap(s, m, "11-analyse-terminee", [
        (ligne("cse-2025-10-14.md").locator("td").nth(4), "Nombre de segments"),
        (ligne("faq-sav.html").locator("td").nth(4), "Nombre de segments"),
        (lancer("cse-2025-10-14.md"), "état et relance de l'analyse"),
        (ligne("cse-2025-10-14.md").get_by_text("cse-2025-10-14.md"), "nom du fichier")])
    ligne("cse-2025-10-14.md").get_by_text("cse-2025-10-14.md").click(); s.pg.wait_for_timeout(5000)
    carte = texte(s, "## Décisions", exact=False).locator("xpath=ancestor::div[.//button[@role='switch']][1]")
    cap(s, m, "12-passages", [
        (bouton(s, "Aperçu"), "Aperçu"), (carte, "passage"), (carte.get_by_role("switch"), "activation du passage"),
        (bouton(s, "Texte complet").locator("xpath=.."), "Texte complet, Ellipse"),
        (s.pg.locator("button:has(svg.lucide-plus)").last, "ajouter un passage"), (bouton(s, "Retour"), "Retour")])


def phase_assistant(s, m, nav):
    nav.get_by_text("Discussion", exact=True).click(); s.pg.wait_for_timeout(3000)
    creer = bouton(s, "Créer un chat")
    cap(s, m, "13-discussions", [(creer, "Créer un chat"),
                                 (texte(s, "Démo Vélanor").locator("xpath=ancestor::div[contains(., 'Assistant')][1]"), "carte d'un assistant")])
    creer.click(); s.pg.wait_for_timeout(1500)
    dlg = s.pg.get_by_role("dialog")
    dlg.get_by_placeholder("Veuillez saisir le nom").fill(CHAT_02)
    cap(s, m, "14-creation-assistant", [(dlg.get_by_placeholder("Veuillez saisir le nom"), "Nom"),
                                        (dlg.get_by_role("button", name="Enregistrer"), "Enregistrer")])
    dlg.get_by_role("button", name="Enregistrer").click(); s.pg.wait_for_timeout(4000)
    carte = texte(s, CHAT_02).locator("xpath=ancestor::div[contains(., '/')][1]")
    cap(s, m, "15-assistant-cree", [(carte, CHAT_02)])
    texte(s, CHAT_02).click(); s.pg.wait_for_timeout(4000)
    reglages = s.pg.locator("button:has(svg.lucide-settings)").last
    cap(s, m, "16-page-assistant", [(reglages, "Paramètres du chat")])
    if not s.pg.get_by_text("Paramètres du chat", exact=True).is_visible():
        reglages.click(); s.pg.wait_for_timeout(2500)
    choix = s.pg.locator("label").filter(has_text="Bases de connaissances").first.locator("xpath=following::button[1]")
    cap(s, m, "17-parametres-du-chat", [(texte(s, "Paramètres du chat"), "Paramètres du chat"),
                                        (s.pg.locator("label").filter(has_text="Modèle").first.locator("xpath=following::button[1]"), "Modèle"),
                                        (s.pg.locator("label").filter(has_text="Message d'accueil").first.locator("xpath=following::textarea[1]"), "Message d'accueil"),
                                        (choix, "Bases de connaissances"), (bouton(s, "Enregistrer").last, "Enregistrer")])
    choix.click(); s.pg.wait_for_timeout(1500)
    opt = s.pg.get_by_role("option").filter(has_text=BASE_02).first
    cap(s, m, "18-choix-base", [(s.pg.get_by_placeholder("Rechercher...").last, "Rechercher..."), (opt, BASE_02)])
    opt.click(); s.pg.wait_for_timeout(800)
    s.pg.keyboard.press("Escape"); s.pg.wait_for_timeout(800)
    if not s.pg.get_by_text("Paramètres du chat", exact=True).is_visible():  # Échap peut aussi fermer le panneau
        reglages.click(); s.pg.wait_for_timeout(2000)
    puce = s.pg.locator("label").filter(has_text="Bases de connaissances").first.locator("xpath=following::button[1]")
    cap(s, m, "19-base-choisie", [(puce, BASE_02), (bouton(s, "Enregistrer").last, "Enregistrer")])
    bouton(s, "Enregistrer").last.click(); s.pg.wait_for_timeout(1000)
    print("après enregistrement :", s.pg.locator("[data-sonner-toast]").all_inner_texts(), flush=True)


def phase_saisie(s, m, nav):
    """Question tapée dans « Manuel-Assistant », sans l'envoyer."""
    nav.get_by_text("Discussion", exact=True).click(); s.pg.wait_for_timeout(3000)
    texte(s, CHAT_02).click(); s.pg.wait_for_timeout(4000)
    zone = s.pg.get_by_placeholder("Saisissez votre message ici...")
    zone.fill(QUESTION_02)
    cap(s, m, "20-question", [
        (texte(s, "Conversations").locator("xpath=following::button[1]"), "nouvelle conversation"),
        (zone, "zone de saisie"), (s.pg.get_by_role("combobox").filter(has_text="Naive").first, "Naive"),
        (s.pg.get_by_role("button", name="Send message"), "Send message")])
    return zone


def citations(s, m, question):
    """Réponse citée affichée (captures 21 et 22) ; `question` : texte de la question dans la conversation."""
    renvoi = s.pg.get_by_text("[1]", exact=True).first
    cap(s, m, "21-reponse-citee", [
        (s.pg.get_by_text(question).last, "question"), (renvoi, "[1]"),
        (s.pg.get_by_text(re.compile(r"tokens \(\d+ input")).first, "jetons et durée"),
        (s.pg.get_by_role("button").filter(has_text=question[:20]).first, "conversation")])
    renvoi.hover(); s.pg.wait_for_timeout(2000)
    bulle = s.pg.locator("[data-radix-popper-content-wrapper]").last
    cap(s, m, "22-citation", [(bulle, "extrait cité")])


def phase_envoi(s, m, nav):
    """Envoi de la question à « Manuel-Assistant » : demande le modèle de chat (vllm-central)."""
    phase_saisie(s, m, nav)
    t0 = time.time()
    s.pg.get_by_role("button", name="Send message").click()
    s.pg.get_by_text(re.compile(r"tokens \(\d+ input")).first.wait_for(timeout=300000)
    s.pg.wait_for_timeout(1500)
    print(f"réponse affichée après {time.time() - t0:.1f} s (horloge du navigateur)", flush=True)
    citations(s, m, QUESTION_02)


def phase_demo(s, m, nav):
    """Réponse citée déjà présente : conversation « Contrat Batterix » de l'assistant « Démo Vélanor » (lecture seule)."""
    nav.get_by_text("Discussion", exact=True).click(); s.pg.wait_for_timeout(3000)
    texte(s, "Démo Vélanor").click(); s.pg.wait_for_timeout(4000)
    texte(s, "Contrat Batterix").click(); s.pg.wait_for_timeout(4000)
    citations(s, m, "Quel est le prix unitaire des batteries")


if __name__ == "__main__":
    scenario, *args = sys.argv[1:]
    with sync_playwright() as p:
        s = Session(p)
        try:
            globals()[scenario.replace("-", "_")](s, *args)
        finally:
            s.b.close()
