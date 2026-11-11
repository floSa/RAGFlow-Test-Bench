"""Captures des manuels 03 à 06 de RAGFlow (lot 2), tout à la souris dans l'interface en français.

Lancement : outils/communs/captures/lancer.sh outils/ragflow/captures/manuels_03_06.py <scénario> [phases...]
Scénarios : decoupage (manuel 03), deepdoc (04), assistants (05), agentique (06). Chaque scénario se découpe en phases
rejouables une à une ; sans phase, toutes sont jouées dans l'ordre.
Objets créés à la souris, tous nommés « Manuel-… » : bases « Manuel-Decoupage » et « Manuel-DeepDoc », assistants
« Manuel-Assistant-05 » et « Manuel-Agentic », dossier « Manuel-dossier » de « Gestion des fichiers » (supprimé à la
souris par le scénario). Bases et assistants sont supprimés ensuite par outils/ragflow/nettoyer_manuel.py. Le jeu de
démonstration (« Démo Vélanor ») n'est ouvert qu'en lecture : rien n'y est enregistré.
Helpers repris du lot 1 : outils/ragflow/captures/captures.py (Session, cap, bouton, texte).
"""
import re
import sys
import time
import traceback
from pathlib import Path

from playwright.sync_api import sync_playwright

from captures import Session, URL, TXT, cap, bouton, texte  # noqa: F401

CORPUS = "corpus/documents/"
ECHEC = Path("donnees/captures-explorer")


# ---------------------------------------------------------------- utilitaires

def caviarder(manuel, *noms):
    """Retire le jeton d'accès (« auth=… ») du code d'intégration dans les textes de pages archivés."""
    for nom in noms:
        f = TXT / manuel / f"{nom}.txt"
        if f.exists():
            f.write_text(re.sub(r"auth=[0-9A-Za-z_-]+", "auth=<masqué>", f.read_text()))


def attendre(s, ms=1200):
    s.pg.wait_for_timeout(ms)


def popover(s):
    """Dernier menu ou liste déroulante ouvert (Radix)."""
    return s.pg.locator("[data-radix-popper-content-wrapper]").last


def haut(loc):
    """Fait défiler le conteneur à ascenseur le plus proche (pas la fenêtre) pour amener l'élément en haut de la zone."""
    loc.evaluate("""e => {
      let p = e.parentElement;
      while (p && !(p.scrollHeight > p.clientHeight + 2 && /(auto|scroll)/.test(getComputedStyle(p).overflowY))) p = p.parentElement;
      if (p && p !== document.body && p !== document.documentElement)
        p.scrollTop += e.getBoundingClientRect().top - p.getBoundingClientRect().top - 12;
      else e.scrollIntoView({block: 'start'});
    }""")


def centre(loc):
    loc.evaluate("e => e.scrollIntoView({block: 'center'})")


def ouvrir_base(s, nom, onglet=None):
    s.aller("/datasets", 2500)
    texte(s, nom).click(); attendre(s, 3500)
    if onglet:
        s.pg.get_by_role("link", name=onglet, exact=True).first.click(); attendre(s, 3000)


def ligne(s, nom):
    return s.pg.locator("tr").filter(has_text=nom).first


def segments(s, nom):
    t = ligne(s, nom).locator("td").nth(4).inner_text().strip()
    return int(t) if t.isdigit() else 0


def attendre_analyse(s, noms, limite=600):
    """Recharge la page toutes les 3 s jusqu'à ce que chaque fichier ait des passages ; renvoie la durée."""
    t0 = time.time()
    while time.time() - t0 < limite:
        s.pg.reload(); attendre(s, 3000)
        n = [segments(s, x) for x in noms]
        if all(n):
            break
    d = time.time() - t0
    print(f"analyse terminée en moins de {d:.0f} s (relevé toutes les 3 s environ) : {dict(zip(noms, n))}", flush=True)
    return d


def ouvrir_menu_gabarit(s, nom, gabarit="General"):
    """Menu de la colonne « Analyser » : un clic sur le nom du gabarit ouvre un menu à une seule entrée."""
    item = s.pg.get_by_role("menuitem").filter(has_text="Changer ou configurer")
    declencheur = ligne(s, nom).get_by_role("button", name=gabarit, exact=True).first
    for geste in (lambda: declencheur.click(),
                  lambda: declencheur.locator("xpath=..").dispatch_event("pointerdown", {"button": 0, "pointerType": "mouse"}),
                  lambda: (declencheur.focus(), s.pg.keyboard.press("Enter"))):
        geste(); attendre(s, 1200)
        if item.count() and item.first.is_visible():
            return item.first
    raise RuntimeError("menu du gabarit introuvable")


# ---------------------------------------------------------------- manuel 03

M03 = "03-datasets-et-decoupage"
BASE_03 = "Manuel-Decoupage"
DOCS_03 = ["stocks-octobre-2025.xlsx", "procedure-batteries.docx", "cse-2025-10-14.md"]
XLSX_RENOMME = "stocks-octobre-2025-manuel.xlsx"


def decoupage_base(s):
    """Liste des bases, menu d'une carte, fenêtre de création, liste des gabarits, création."""
    m = M03
    s.aller("/datasets", 3000)
    carte = texte(s, "Démo Vélanor").locator("xpath=ancestor::div[contains(., 'Fichiers')][1]")
    carte.hover(); attendre(s, 600)
    menu = carte.locator("button").last
    cap(s, m, "01-liste-des-bases", [
        (s.pg.locator("button:has(svg.lucide-funnel)").first, "filtre"),
        (s.pg.get_by_role("searchbox").first, "Rechercher"),
        (bouton(s, "Créer une base de connaissances"), "Créer une base de connaissances"),
        (menu, "menu de la carte")])
    menu.click(); attendre(s, 800)
    cap(s, m, "02-menu-d-une-base", [
        (s.pg.get_by_role("menuitem").filter(has_text="Renommer").first, "Renommer"),
        (s.pg.get_by_role("menuitem").filter(has_text="Supprimer").first, "Supprimer")])
    s.pg.keyboard.press("Escape"); attendre(s, 600)
    bouton(s, "Créer une base de connaissances").click(); attendre(s, 1500)
    dlg = s.pg.get_by_role("dialog")
    nom = dlg.get_by_placeholder("Veuillez saisir un nom !")
    nom.fill(BASE_03)
    gabarit = dlg.get_by_role("button").filter(has_text="General")
    cap(s, m, "03-fenetre-de-creation", [
        (nom, "Nom"), (dlg.get_by_role("button").filter(has_text="bge-m3"), "Modèle d'embedding"),
        (gabarit, "gabarit"), (dlg.get_by_role("button", name="Enregistrer"), "Enregistrer")])
    gabarit.click(); attendre(s, 1200)
    pop = popover(s)
    cap(s, m, "04-liste-des-gabarits", [
        (pop.get_by_placeholder("Rechercher").first, "Rechercher"),
        (pop.get_by_text("Essai-KC-mind_map-1835").first, "pipeline personnalisé"),
        (pop.get_by_text("General", exact=True).first, "General"),
        (pop.get_by_text("Table", exact=True).first, "Table")])
    pop.get_by_text("General", exact=True).first.click(); attendre(s, 800)
    dlg.get_by_role("button", name="Enregistrer").click(); attendre(s, 4000)
    print("base créée :", s.pg.url.replace(URL, ""), flush=True)


def decoupage_fichiers(s):
    """Téléversement avec analyse à la création, tableau, actions d'une ligne, renommage, activation."""
    m = M03
    ouvrir_base(s, BASE_03)
    bouton(s, "Ajouter un fichier").click(); attendre(s, 1000)
    s.pg.get_by_role("menuitem").filter(has_text="Téléverser un fichier").first.click(); attendre(s, 1500)
    dlg = s.pg.get_by_role("dialog")
    dlg.locator("input[type=file]").first.set_input_files([CORPUS + d for d in DOCS_03]); attendre(s, 1500)
    interrupteur = dlg.get_by_role("switch").first
    if interrupteur.get_attribute("aria-checked") != "true":
        interrupteur.click(); attendre(s, 600)
    cap(s, m, "05-televersement-analyse", [
        (interrupteur.locator("xpath=.."), "Analyser à la création"),
        (dlg.get_by_role("tab", name="Dossier"), "Dossier"),
        (dlg.get_by_text(DOCS_03[0]).locator("xpath=ancestor::div[.//button][1]"), "fichier choisi"),
        (dlg.get_by_role("button", name="Enregistrer"), "Enregistrer")])
    dlg.get_by_role("button", name="Enregistrer").click(); attendre(s, 3000)
    attendre_analyse(s, DOCS_03)
    th = lambda t: s.pg.locator("th").filter(has_text=t).first
    cap(s, m, "06-tableau-des-fichiers", [
        (th("Nom"), "Nom"), (th("Date de"), "Date de téléversement"), (th("Activé"), "Activé"),
        (th("Nombre de"), "Nombre de segments"), (th("Métadonnées"), "Métadonnées"), (th("Analyser"), "Analyser")])
    l = ligne(s, DOCS_03[0])
    l.hover(); attendre(s, 600)
    actions = l.locator("td").last.locator("button")
    print("boutons d'action :", actions.count(), flush=True)
    oeil = actions.nth(actions.count() - 3)
    oeil.hover(); attendre(s, 1500)
    cap(s, m, "07-actions-d-un-fichier", [
        (actions.nth(actions.count() - 4), "renommer"), (oeil, "aperçu des propriétés"),
        (popover(s), "propriétés du fichier"),
        (actions.nth(actions.count() - 2), "télécharger"), (actions.nth(actions.count() - 1), "supprimer")])
    l.hover(); attendre(s, 400)
    actions.nth(actions.count() - 4).click(); attendre(s, 1200)
    dlg = s.pg.get_by_role("dialog")
    champ = dlg.locator("input").first
    champ.fill(XLSX_RENOMME)
    cap(s, m, "08-renommer", [(champ, "Nom"), (dlg.get_by_role("button", name="Enregistrer"), "Enregistrer")])
    dlg.get_by_role("button", name="Enregistrer").click(); attendre(s, 2500)
    md = ligne(s, DOCS_03[2])
    md.get_by_role("switch").click(); attendre(s, 1500)
    cap(s, m, "09-fichier-desactive", [(md.get_by_role("switch"), "Activé"),
                                       (md.locator("td").nth(1), DOCS_03[2])])
    md.get_by_role("switch").click(); attendre(s, 1500)
    print("activé après réactivation :", md.get_by_role("switch").get_attribute("aria-checked"), flush=True)


def decoupage_gabarit(s):
    """Gabarit d'un seul fichier (tableur passé en Table), relance d'une analyse, métadonnées."""
    m = M03
    ouvrir_base(s, BASE_03)
    avant = segments(s, XLSX_RENOMME)
    item = ouvrir_menu_gabarit(s, XLSX_RENOMME)
    cap(s, m, "10-menu-du-gabarit", [(item, "Changer ou configurer le pipeline d'ingestion.")])
    item.click(); attendre(s, 2000)
    dlg = s.pg.get_by_role("dialog").last
    choix = dlg.get_by_role("button").filter(has_text="General").first
    cap(s, m, "11-fenetre-du-gabarit", [(dlg.locator("h2, [role=heading]").first, "titre"), (choix, "gabarit du fichier")])
    choix.click(); attendre(s, 1200)
    pop = popover(s)
    table = pop.get_by_text("Table", exact=True).first
    cap(s, m, "12-choix-table", [(table, "Table")])
    table.click(); attendre(s, 1500)
    ok = dlg.get_by_role("button").filter(has_text=re.compile("^(Enregistrer|Confirmer|OK|Sauvegarder)$")).last
    cap(s, m, "13-gabarit-table-choisi", [(dlg.get_by_role("button").filter(has_text="Table").first, "Table"), (ok, ok.inner_text().strip())])
    ok.click(); attendre(s, 2000)
    conf = s.pg.get_by_role("alertdialog").or_(s.pg.get_by_role("dialog")).last
    if conf.is_visible():
        oui = conf.get_by_role("button").filter(has_text=re.compile("^(Oui|Yes|OK|Confirmer)$")).last
        cap(s, m, "14-confirmer-reanalyse", [(conf, "Analyser le fichier"), (oui, oui.inner_text().strip())])
        oui.click(); attendre(s, 2000)
    t0 = time.time()
    while time.time() - t0 < 300:
        s.pg.reload(); attendre(s, 3000)
        if segments(s, XLSX_RENOMME) and segments(s, XLSX_RENOMME) != avant:
            break
    print(f"tableur : {avant} segments avec General, {segments(s, XLSX_RENOMME)} avec Table "
          f"(relevé après {time.time() - t0:.0f} s)", flush=True)
    l = ligne(s, XLSX_RENOMME)
    cap(s, m, "15-gabarit-table-applique", [(l.get_by_text("Table", exact=True).first, "Table"),
                                           (l.locator("td").nth(4), "Nombre de segments")])
    decoupage_relance(s)


def decoupage_relance(s):
    m = M03
    if "/dataset/files" not in s.pg.url:
        ouvrir_base(s, BASE_03)
    docx = ligne(s, DOCS_03[1])
    relance = docx.get_by_test_id("document-parse-toggle")
    cap(s, m, "16-relancer-l-analyse", [(relance, "relancer l'analyse"),
                                       (docx.locator("[data-testid=document-parse-status] button").last, "état de l'analyse")])
    relance.click(); attendre(s, 1500)
    conf = s.pg.get_by_role("alertdialog").or_(s.pg.get_by_role("dialog")).last
    ok = conf.get_by_role("button").last
    cap(s, m, "17-confirmer-la-relance", [(conf, "confirmation"), (ok, ok.inner_text().strip())])
    ok.click(); attendre(s, 2000)
    attendre_analyse(s, [DOCS_03[1]])
    l = ligne(s, DOCS_03[1])
    l.get_by_role("button", name=re.compile("fields")).click(); attendre(s, 1500)
    dlg = s.pg.get_by_role("dialog").last
    cap(s, m, "18-metadonnees", [(dlg.get_by_role("button", name="Ajouter"), "Ajouter"),
                                 (dlg.locator("table").first, "tableau des champs"),
                                 (dlg.get_by_role("button", name="Enregistrer"), "Enregistrer")])
    dlg.get_by_role("button", name="Annuler").click(); attendre(s, 1000)


def decoupage_groupe(s):
    """Sélection et actions groupées, filtre, fichier vide créé puis supprimé."""
    m = M03
    ouvrir_base(s, BASE_03)
    for d in (XLSX_RENOMME, DOCS_03[1]):
        ligne(s, d).get_by_role("checkbox").click(); attendre(s, 500)
    mi = lambda n: s.pg.get_by_role("menuitem", name=n, exact=True).first
    cap(s, m, "19-actions-groupees", [
        (mi("Analyser"), "Analyser"), (mi("Annuler"), "Annuler"),
        (mi("Activé"), "Activé"), (mi("Désactivé"), "Désactivé"),
        (mi("Métadonnées"), "Métadonnées"), (mi("Supprimer"), "Supprimer")])
    for d in (XLSX_RENOMME, DOCS_03[1]):
        ligne(s, d).get_by_role("checkbox").click(); attendre(s, 400)
    s.pg.locator("button:has(svg.lucide-funnel)").first.click(); attendre(s, 1200)
    pop = popover(s)
    cap(s, m, "20-filtre-des-fichiers", [
        (pop.get_by_text("Type de fichier").first, "Type de fichier"), (pop.get_by_text("Statut", exact=True).first, "Statut"),
        (pop.get_by_text("Champ de métadonnée").first, "Champ de métadonnée"),
        (pop.get_by_role("button", name="Soumettre"), "Soumettre")])
    s.pg.keyboard.press("Escape"); attendre(s, 800)
    bouton(s, "Ajouter un fichier").click(); attendre(s, 1000)
    s.pg.get_by_role("menuitem").filter(has_text="Créer un fichier vide").first.click(); attendre(s, 1200)
    dlg = s.pg.get_by_role("dialog")
    champ = dlg.get_by_placeholder("Veuillez saisir le nom")
    champ.fill("Manuel-note.txt")
    cap(s, m, "21-fichier-vide", [(champ, "Nom"), (dlg.get_by_role("button", name="Enregistrer"), "Enregistrer")])
    dlg.get_by_role("button", name="Enregistrer").click(); attendre(s, 2500)
    l = ligne(s, "Manuel-note.txt")
    l.hover(); attendre(s, 500)
    poubelle = l.locator("td").last.locator("button").last
    cap(s, m, "22-fichier-vide-cree", [(l.locator("td").nth(1), "Manuel-note.txt"), (poubelle, "supprimer")])
    poubelle.click(); attendre(s, 1200)
    conf = s.pg.get_by_role("alertdialog").or_(s.pg.get_by_role("dialog")).last
    ok = conf.get_by_role("button").filter(has_text=re.compile("Supprimer|Delete|Oui|OK")).last
    cap(s, m, "23-suppression-d-un-fichier", [(conf, "confirmation"), (ok, ok.inner_text().strip())])
    ok.click(); attendre(s, 2000)
    print("fichier vide supprimé :", ligne(s, "Manuel-note.txt").count() == 0, flush=True)


def decoupage_config(s):
    """Onglet « Configuration », réglage par réglage ; langue passée en français et description saisie, enregistrées."""
    m = M03
    ouvrir_base(s, BASE_03, "Configuration")
    lab = lambda t: s.pg.locator("label").filter(has_text=t).first
    langue = lab("Langue").locator("xpath=following::*[@role='combobox'][1]")
    autor = lab("Autorisations").locator("xpath=following::*[@role='combobox'][1]")
    desc = s.pg.get_by_placeholder("Décrivez votre base de connaissances")
    cap(s, m, "24-configuration-informations", [
        (lab("Nom").locator("xpath=following::input[1]"), "Nom"), (langue, "Langue"),
        (bouton(s, "Télécharger"), "Avatar"), (desc, "Description"), (autor, "Autorisations"),
        (s.pg.get_by_role("button").filter(has_text="bge-m3").first, "Modèle d'embedding")])
    langue.click(); attendre(s, 1000)
    fr = s.pg.get_by_role("option", name="French", exact=True)
    centre(fr); attendre(s, 400)
    cap(s, m, "25-langue", [(fr, "French")])
    fr.click(); attendre(s, 800)
    autor.click(); attendre(s, 1000)
    cap(s, m, "26-autorisations", [(s.pg.get_by_role("option", name="Moi uniquement"), "Moi uniquement"),
                                   (s.pg.get_by_role("option", name="Équipe"), "Équipe")])
    s.pg.keyboard.press("Escape"); attendre(s, 600)
    desc.fill("Essai du manuel 03 : gabarits de découpage")
    rang = lab("Rang de page")
    haut(rang)
    mode = s.pg.get_by_role("button").filter(has_text="built in").first
    cap(s, m, "27-rang-et-mode-d-analyse", [
        (rang.locator("xpath=following::*[@role='slider'][1]"), "Rang de page"), (mode, "Mode d'analyse"),
        (s.pg.get_by_role("tab", name="Parser"), "Parser"), (s.pg.get_by_role("tab", name="General Chunker"), "General Chunker"),
        (s.pg.get_by_role("tab", name="Extractor"), "Extractor"), (s.pg.get_by_role("tab", name="Indexer"), "Indexer")])
    bouton(s, "Introduction au pipeline intégré").click(); attendre(s, 1200)
    cap(s, m, "28-introduction-au-pipeline", [(bouton(s, "Introduction au pipeline intégré"), "Introduction au pipeline intégré"),
                                              (s.pg.get_by_text("Description de la méthode", exact=False).first.locator("xpath=.."), "description du gabarit")])
    mode.click(); attendre(s, 1200)
    pop = popover(s)
    cap(s, m, "29-mode-d-analyse", [(pop.get_by_text("Essai-KC-mind_map-1835").first, "pipeline personnalisé"),
                                    (pop.get_by_text("General", exact=True).first, "General"),
                                    (pop.get_by_text("Q&A", exact=True).first, "Q&A")])
    s.pg.keyboard.press("Escape"); attendre(s, 600)
    s.pg.get_by_role("tab", name="Parser").click(); attendre(s, 1000)
    vision = lab("Enable vision enhancement")
    haut(vision)
    cap(s, m, "30-parser-formats", [
        (vision.locator("xpath=following::*[@role='switch'][1]"), "Enable vision enhancement"),
        (bouton(s, "DOC"), "DOC"), (bouton(s, "DOCX"), "DOCX"), (bouton(s, "Email"), "Email"),
        (s.pg.locator("label").filter(has_text="Champ").first.locator("xpath=following::button[1]"), "Champ"),
        (bouton(s, "HTML"), "HTML")])
    image = bouton(s, "Image")
    haut(image)
    cap(s, m, "31-parser-image", [
        (image, "Image"), (lab("OCR"), "OCR"), (s.pg.get_by_role("radio", name="DeepDoc"), "DeepDoc"),
        (s.pg.get_by_role("radio", name="External OCR model"), "External OCR model"), (bouton(s, "Markdown"), "Markdown")])
    pdf = bouton(s, "PDF")
    haut(pdf)
    cap(s, m, "32-parser-pdf", [
        (lab("Détecter la mise en page multi-colonnes"), "Détecter la mise en page multi-colonnes"),
        (lab("Supprimer la table des matières d'origine"), "Supprimer la table des matières d'origine"),
        (lab("Supprimer la table des matières d'origine").locator("xpath=following::label[1]"), "Supprimer en-tête et pied de page"),
        (lab("Analyseur PDF"), "Analyseur PDF"), (lab("Plages de pages"), "Plages de pages"),
        (bouton(s, "Ajouter une page"), "Ajouter une page")])
    s.pg.get_by_role("tab", name="General Chunker").click(); attendre(s, 1000)
    taille = lab("Taille de segment recommandée")
    haut(taille)
    cap(s, m, "34-general-chunker", [
        (taille, "Taille de segment recommandée"), (lab("Pourcentage de chevauchement"), "Pourcentage de chevauchement (%)"),
        (lab("Table context window"), "Table context window"), (lab("Image context window"), "Image context window"),
        (s.pg.get_by_text("Délimiteurs", exact=True).first, "Délimiteurs")])
    ajouter = bouton(s, "Ajouter")
    haut(s.pg.get_by_text("Splits at:", exact=False).first)
    cap(s, m, "35-general-chunker-suite", [
        (s.pg.get_by_text("Splits at:", exact=False).first.locator("xpath=.."), "Splits at:"), (ajouter, "Ajouter"),
        (s.pg.get_by_text("Les blocs enfants", exact=False).first, "Les blocs enfants sont utilisés pour la récupération")])
    s.pg.get_by_role("tab", name="Extractor").click(); attendre(s, 1000)
    modele = s.pg.get_by_role("combobox").filter(has_text="gemma4").first
    haut(modele)
    cap(s, m, "36-extractor-mots-cles", [
        (modele, "Modèle"), (bouton(s, "Mots-clés"), "Mots-clés"), (lab("Mots-clés automatiques"), "Mots-clés automatiques"),
        (lab("Invite système"), "Invite système")])
    questions = bouton(s, "Questions")
    haut(questions)
    cap(s, m, "37-extractor-questions-etiquettes", [
        (questions, "Questions"), (lab("Questions automatiques"), "Questions automatiques"),
        (bouton(s, "Étiquettes"), "Étiquettes")])
    resume = bouton(s, "Résumé")
    haut(resume)
    cap(s, m, "38-extractor-resume-metadonnees", [
        (resume, "Résumé"), (bouton(s, "Métadonnées"), "Métadonnées"), (s.pg.get_by_text("Paramètres", exact=True).last, "Paramètres")])
    s.pg.get_by_role("tab", name="Indexer").click(); attendre(s, 1000)
    methode = lab("Méthode de recherche")
    haut(methode)
    cap(s, m, "39-indexer", [
        (methode.locator("xpath=.."), "Méthode de recherche"),
        (lab("Poids d'embedding du nom de fichier").locator("xpath=.."), "Poids d'embedding du nom de fichier"),
        (s.pg.get_by_role("combobox").filter(has_text="Texte traité").first, "Champ")])
    lier = bouton(s, "Lier une source de données")
    haut(lier)
    cap(s, m, "40-source-et-enregistrement", [(lier, "Lier une source de données"), (bouton(s, "Annuler"), "Annuler"),
                                              (bouton(s, "Enregistrer"), "Enregistrer")])
    bouton(s, "Enregistrer").click(); attendre(s, 800)
    toast = s.pg.locator("[data-sonner-toast]").first
    print("après enregistrement :", s.pg.locator("[data-sonner-toast]").all_inner_texts(), flush=True)
    cap(s, m, "41-configuration-enregistree", [(toast, "message")] if toast.count() else [])
    s.pg.reload(); attendre(s, 3000)
    print("langue relue :", langue.inner_text(), "; description relue :", desc.input_value(), flush=True)


def decoupage_journaux(s):
    m = M03
    ouvrir_base(s, BASE_03, "Journaux")
    l = s.pg.locator("tbody tr").first
    l.hover(); attendre(s, 600)
    oeil = l.locator("td").last.locator("button").first
    cap(s, m, "42-journaux", [
        (s.pg.get_by_text("Fichiers totaux").first.locator("xpath=.."), "Fichiers totaux"),
        (s.pg.get_by_text("Téléchargement", exact=True).first.locator("xpath=.."), "Téléchargement"),
        (s.pg.get_by_text("Traitement", exact=True).first.locator("xpath=.."), "Traitement"),
        (bouton(s, "Fichier").locator("xpath=.."), "Fichier, Base de connaissances, Data source"),
        (l, "tâche"), (oeil, "détail")])
    oeil.click(); attendre(s, 1500)
    dlg = s.pg.get_by_role("dialog").last
    cap(s, m, "43-detail-d-une-tache", [(dlg.get_by_text("Durée").first.locator("xpath=.."), "Durée"),
                                        (dlg.get_by_text("Détails").first.locator("xpath=.."), "Détails")])
    s.pg.keyboard.press("Escape"); attendre(s, 800)


def supprimer_ligne_gestion(s, nom, m=None, capture=None):
    l = ligne(s, nom)
    l.hover(); attendre(s, 600)
    l.locator("td").last.locator("button").last.click(); attendre(s, 1200)
    conf = s.pg.get_by_role("alertdialog").or_(s.pg.get_by_role("dialog")).last
    ok = conf.get_by_role("button").filter(has_text=re.compile("Supprimer|Delete|Oui|OK")).last
    if capture:
        cap(s, m, capture, [(conf, "confirmation"), (ok, ok.inner_text().strip())])
    ok.click(); attendre(s, 2500)


def decoupage_gestion(s):
    """Page « Gestion des fichiers » : dossier créé, fichier téléversé, lié à la base, puis dossier supprimé."""
    m = M03
    s.aller("/files", 3000)
    attendre(s, 1000)
    if ligne(s, "Manuel-dossier").count():  # reste d'un passage interrompu : supprimé sans capture
        supprimer_ligne_gestion(s, "Manuel-dossier")
    cap(s, m, "45-gestion-des-fichiers", [
        (s.pg.get_by_role("searchbox").first, "Rechercher"), (bouton(s, "Ajouter un fichier"), "Ajouter un fichier"),
        (texte(s, ".knowledgebase"), ".knowledgebase"),
        (s.pg.locator("th").filter(has_text="Base de connaissances").first, "Base de connaissances")])
    bouton(s, "Ajouter un fichier").click(); attendre(s, 1000)
    items = s.pg.get_by_role("menuitem")
    print("menu d'ajout :", items.all_inner_texts(), flush=True)
    cap(s, m, "46-menu-d-ajout", [(items.nth(i), items.nth(i).inner_text().strip()) for i in range(items.count())])
    items.filter(has_text="Nouveau dossier").first.click(); attendre(s, 1200)
    dlg = s.pg.get_by_role("dialog")
    champ = dlg.locator("input").first
    champ.fill("Manuel-dossier")
    cap(s, m, "47-nouveau-dossier", [(champ, "Nom"), (dlg.get_by_role("button", name="Enregistrer"), "Enregistrer")])
    dlg.get_by_role("button", name="Enregistrer").click(); attendre(s, 2500)
    texte(s, "Manuel-dossier").click(); attendre(s, 2500)
    bouton(s, "Ajouter un fichier").click(); attendre(s, 1000)
    s.pg.get_by_role("menuitem").filter(has_text="Téléverser un fichier").first.click(); attendre(s, 1500)
    dlg = s.pg.get_by_role("dialog")
    dlg.locator("input[type=file]").first.set_input_files(CORPUS + "faq-sav.html"); attendre(s, 1500)
    cap(s, m, "48-televerser-dans-le-dossier", [(dlg.get_by_text("faq-sav.html").first, "faq-sav.html"),
                                                (dlg.get_by_role("button", name="Enregistrer"), "Enregistrer")])
    dlg.get_by_role("button", name="Enregistrer").click(); attendre(s, 3000)
    l = ligne(s, "faq-sav.html")
    l.hover(); attendre(s, 600)
    btn = l.locator("td").last.locator("button")
    print("actions d'un fichier :", btn.count(), flush=True)
    cap(s, m, "49-actions-gestion", [(btn.nth(i), f"action {i + 1}") for i in range(min(btn.count(), 6))])
    btn.first.click(); attendre(s, 1500)
    dlg = s.pg.get_by_role("dialog").last
    choix = dlg.get_by_role("combobox").or_(dlg.locator("button").filter(has_text="Veuillez sélectionner")).first
    choix.click(); attendre(s, 1000)
    opt = s.pg.get_by_role("option").filter(has_text=BASE_03).first
    opt.click(); attendre(s, 600)
    fermer = popover(s).get_by_text("Fermer", exact=True)
    cap(s, m, "50-lier-a-la-base", [(opt, BASE_03), (fermer, "Fermer")])
    fermer.click(); attendre(s, 600)
    ok = dlg.get_by_role("button", name=re.compile("Save|Enregistrer"))
    cap(s, m, "51-lier-enregistrer", [(dlg.locator("button").filter(has_text="Manuel-Decoup").first, BASE_03), (ok, ok.inner_text().strip())])
    ok.click(); attendre(s, 2500)
    cap(s, m, "52-fichier-lie", [(ligne(s, "faq-sav.html").locator("td").nth(4), BASE_03)])
    s.aller("/files", 2500)
    supprimer_ligne_gestion(s, "Manuel-dossier", m, "53-supprimer-le-dossier")
    print("dossier supprimé :", ligne(s, "Manuel-dossier").count() == 0, flush=True)


def decoupage_pipelines(s):
    m = M03
    s.aller("/agents", 3000)
    s.pg.get_by_text("Ingestion pipeline", exact=True).first.click(); attendre(s, 2500)
    cap(s, m, "54-pipelines-integres", [
        (s.pg.get_by_text("Ingestion pipeline", exact=True).first, "Ingestion pipeline"),
        (s.pg.get_by_text("Built-in pipelines", exact=False).first, "Built-in pipelines"),
        (s.pg.get_by_text("Table", exact=True).first, "Table")])


def decoupage(s, *phases):
    for ph in phases or ("base", "fichiers", "gabarit", "groupe", "config", "journaux", "gestion", "pipelines"):
        print("== phase", ph, flush=True)
        globals()["decoupage_" + ph](s)


# ---------------------------------------------------------------- manuel 04

M04 = "04-deepdoc"
BASE_04 = "Manuel-DeepDoc"
SCAN = "contrat-batterix-scan.pdf"
QUESTION_04 = "volume minimal annuel de 40 000 batteries"


def creer_base_simple(s, nom):
    """Création à la souris sans capture (procédure détaillée au manuel 03)."""
    s.aller("/datasets", 3000)
    if s.pg.get_by_text(nom, exact=True).count():
        return
    bouton(s, "Créer une base de connaissances").click(); attendre(s, 1500)
    dlg = s.pg.get_by_role("dialog")
    dlg.get_by_placeholder("Veuillez saisir un nom !").fill(nom)
    dlg.get_by_role("button", name="Enregistrer").click(); attendre(s, 4000)


def test_recuperation(s, m, nom, question, annoter_scores=True):
    """Onglet « Test de récupération » : question saisie, « Test », résultats ; renvoie le texte des résultats."""
    zone = s.pg.locator("textarea").first
    zone.fill(question)
    bouton(s, "Test").click(); attendre(s, 5000)
    res = s.pg.get_by_text("Résultats", exact=True).first.locator("xpath=ancestor::*[self::section or self::div][2]")
    txt = res.inner_text()
    print("résultats :", " | ".join(x for x in txt.splitlines() if x.strip())[:900], flush=True)
    return zone, res


def deepdoc_base(s):
    """Base « Manuel-DeepDoc », scan téléversé avec « Analyser à la création », durée relevée ; test avant correction."""
    m = M04
    creer_base_simple(s, BASE_04)
    ouvrir_base(s, BASE_04)
    if not ligne(s, SCAN).count():
        bouton(s, "Ajouter un fichier").click(); attendre(s, 1000)
        s.pg.get_by_role("menuitem").filter(has_text="Téléverser un fichier").first.click(); attendre(s, 1500)
        dlg = s.pg.get_by_role("dialog")
        dlg.locator("input[type=file]").first.set_input_files([CORPUS + SCAN, CORPUS + "cse-2025-10-14.md"]); attendre(s, 1500)
        sw = dlg.get_by_role("switch").first
        if sw.get_attribute("aria-checked") != "true":
            sw.click(); attendre(s, 500)
        dlg.get_by_role("button", name="Enregistrer").click()
        t0 = time.time(); attendre(s, 2500)
        etat = ligne(s, SCAN).locator("[data-testid=document-parse-status]")
        cap(s, m, "01-analyse-en-cours", [(etat, "progression de l'analyse")])
        while time.time() - t0 < 600:
            s.pg.reload(); attendre(s, 2000)
            if segments(s, SCAN) and segments(s, "cse-2025-10-14.md"):
                break
        print(f"scan analysé en moins de {time.time() - t0:.0f} s (relevé toutes les 2 s environ, rechargement compris) : "
              f"{segments(s, SCAN)} segment(s)", flush=True)
    l = ligne(s, SCAN)
    cap(s, m, "02-scan-analyse", [(l.locator("td").nth(4), "Nombre de segments"),
                                  (l.locator("[data-testid=document-parse-status] button").last, "état de l'analyse"),
                                  (l.get_by_text(SCAN), SCAN)])
    l.locator("[data-testid=document-parse-status] button").last.click(); attendre(s, 1500)
    dlg = s.pg.get_by_role("dialog").last
    print("journal d'analyse :", " | ".join(x for x in dlg.inner_text().splitlines() if x.strip())[:1200], flush=True)
    cap(s, m, "03-journal-d-analyse", [(dlg.get_by_text("Durée").first.locator("xpath=.."), "Durée"),
                                       (dlg.get_by_text("Détails").first.locator("xpath=.."), "Détails")])
    s.pg.keyboard.press("Escape"); attendre(s, 800)


def deepdoc_test(s, nom_image="04-test-avant-correction"):
    m = M04
    ouvrir_base(s, BASE_04, "Test de récupération")
    zone, res = test_recuperation(s, m, BASE_04, QUESTION_04)
    scores = s.pg.get_by_text(re.compile("Similarité hybride")).first.locator("xpath=..")
    cap(s, m, nom_image, [(zone, "question"), (bouton(s, "Test"), "Test"), (scores, "scores du premier passage"),
                          (s.pg.get_by_text(re.compile("^Total")).first, "Total")])


def carte_passage(s, extrait):
    return s.pg.get_by_text(extrait, exact=False).first.locator("xpath=ancestor::div[.//button[@role='switch']][1]")


def deepdoc_passages(s):
    """« Résultat du segment » : lecture, correction, désactivation, passage ajouté, actions groupées, filtre, recherche."""
    m = M04
    ouvrir_base(s, BASE_04)
    ligne(s, SCAN).get_by_text(SCAN).click(); attendre(s, 5000)
    carte = carte_passage(s, "APPROVISIONNEMENT")
    cap(s, m, "05-resultat-du-segment", [
        (bouton(s, "Aperçu"), "Aperçu"), (s.pg.locator("canvas, img").first, "page du document"),
        (carte, "passage"), (carte.get_by_role("switch"), "interrupteur du passage"),
        (bouton(s, "Texte complet").locator("xpath=.."), "Texte complet, Ellipse")])
    cap(s, m, "06-outils-des-passages", [
        (s.pg.locator("button:has(svg.lucide-funnel)").first, "filtre"), (s.pg.get_by_placeholder("Rechercher").first, "Recherche"),
        (s.pg.locator("button:has(svg.lucide-plus)").last, "ajouter un passage"),
        (s.pg.get_by_text("Tout sélectionner").first, "Tout sélectionner"), (bouton(s, "Retour"), "Retour")])
    s.pg.get_by_text("Volumeminimalannuel", exact=False).first.dblclick(); attendre(s, 1500)
    dlg = s.pg.get_by_role("dialog").last
    zone = dlg.locator("textarea").first
    lab = lambda t: dlg.locator("label").filter(has_text=t).first
    cap(s, m, "07-modifier-le-segment", [
        (zone, "Segment"), (lab("Type"), "Type"), (lab("Mot-clé"), "Mot-clé"), (lab("Question"), "Question"),
        (dlg.get_by_text("Ajouter une étiquette").first, "Étiquettes"), (dlg.get_by_role("switch").last, "Activé")])
    requetes = []
    s.pg.on("request", lambda r: requetes.append(f"{r.method} {r.url.replace(URL, '')[:110]}") if r.method != "GET" else None)
    zone.click()
    zone.evaluate("e => { const a = 'Volumeminimalannuel:40 0oo'; const i = e.value.indexOf(a); e.setSelectionRange(i, i + a.length); }")
    s.pg.keyboard.type("Volume minimal annuel : 40 000")
    zone.evaluate("e => { const i = e.value.indexOf('Volume minimal annuel'); e.setSelectionRange(i, i + 30); "
                  "e.scrollTop = Math.max(0, e.scrollHeight * i / e.value.length - 40); }")
    cap(s, m, "08-segment-corrige", [(zone, "Segment"), (dlg.get_by_role("button", name="Confirmer"), "Confirmer")])
    dlg.get_by_role("button", name="Confirmer").click(); attendre(s, 3000)
    print("requêtes après « Confirmer » (passage du PDF modifié) :", requetes, "; fenêtre encore ouverte :", dlg.is_visible(), flush=True)
    if dlg.is_visible():
        cap(s, m, "09-confirmer-sans-effet", [(dlg.get_by_text("Modifier le segment").first, "Modifier le segment"),
                                             (dlg.get_by_role("button", name="Annuler"), "Annuler")])
        dlg.get_by_role("button", name="Annuler").click(); attendre(s, 1500)
    carte = carte_passage(s, "APPROVISIONNEMENT")
    carte.get_by_role("switch").click(); attendre(s, 1500)
    cap(s, m, "10-passage-desactive", [(carte.get_by_role("switch"), "interrupteur du passage")])
    s.pg.locator("button:has(svg.lucide-funnel)").first.click(); attendre(s, 1000)
    pop = popover(s)
    cap(s, m, "11-filtre-des-passages", [(pop.get_by_text("Tous", exact=True), "Tous"), (pop.get_by_text("Activé", exact=True), "Activé"),
                                         (pop.get_by_text("Désactivé", exact=True), "Désactivé")])
    s.pg.keyboard.press("Escape"); attendre(s, 600)
    carte.get_by_role("switch").click(); attendre(s, 1500)
    print("passage réactivé :", carte.get_by_role("switch").get_attribute("aria-checked"), flush=True)
    s.pg.locator("button:has(svg.lucide-plus)").last.click(); attendre(s, 1500)
    dlg = s.pg.get_by_role("dialog").last
    dlg.locator("textarea").first.fill("Le contrat Batterix fixe un volume minimal annuel de 40 000 batteries 48 V.")
    for libelle, valeur in (("Mot-clé", "volume minimal annuel"), ("Question", "Quel est le volume minimal annuel du contrat Batterix ?")):
        dlg.locator("label").filter(has_text=libelle).first.locator("xpath=following::button[1]").click(); attendre(s, 500)
        champ = dlg.locator("input:visible").last
        champ.fill(valeur); champ.press("Enter"); attendre(s, 500)
    cap(s, m, "12-creer-un-segment", [
        (dlg.locator("textarea").first, "Segment"), (dlg.get_by_text("volume minimal annuel", exact=True).first, "Mot-clé"),
        (dlg.get_by_text("Quel est le volume minimal annuel", exact=False).first, "Question"),
        (dlg.get_by_role("button", name="Confirmer"), "Confirmer")])
    dlg.get_by_role("button", name="Confirmer").click(); attendre(s, 3000)
    s.pg.reload(); attendre(s, 4000)
    ajoute = carte_passage(s, "Le contrat Batterix fixe")
    cap(s, m, "13-passage-ajoute", [(ajoute, "passage ajouté"), (s.pg.get_by_text(re.compile("^Total")).first, "Total")])
    s.pg.get_by_text("Tout sélectionner").first.click(); attendre(s, 1000)
    cap(s, m, "14-actions-groupees", [(bouton(s, "Activer"), "Activer"), (bouton(s, "Désactiver"), "Désactiver"),
                                      (bouton(s, "Supprimer"), "Supprimer")])
    s.pg.get_by_text("Tout sélectionner").first.click(); attendre(s, 800)
    rech = s.pg.get_by_placeholder("Rechercher").first
    rech.fill("40 000"); rech.press("Enter"); attendre(s, 2500)
    cap(s, m, "15-recherche-dans-les-passages", [(rech, "Recherche"), (s.pg.get_by_text(re.compile("^Total")).first, "Total")])
    rech.fill(""); rech.press("Enter"); attendre(s, 1500)
    bouton(s, "Ellipse").click(); attendre(s, 1500)
    cap(s, m, "16-ellipse", [(bouton(s, "Ellipse"), "Ellipse"), (carte_passage(s, "APPROVISIONNEMENT"), "passage abrégé")])
    bouton(s, "Texte complet").click(); attendre(s, 800)


def deepdoc_markdown(s):
    """Même geste de correction sur un passage issu d'un fichier Markdown : enregistré."""
    m = M04
    ouvrir_base(s, BASE_04)
    ligne(s, "cse-2025-10-14.md").get_by_text("cse-2025-10-14.md").click(); attendre(s, 5000)
    requetes = []
    s.pg.on("request", lambda r: requetes.append(f"{r.method} {r.url.replace(URL, '')[:110]}") if r.method != "GET" else None)
    s.pg.get_by_text("intéressement", exact=False).last.dblclick(); attendre(s, 1500)
    dlg = s.pg.get_by_role("dialog").last
    dlg.locator("label").filter(has_text="Mot-clé").first.locator("xpath=following::button[1]").click(); attendre(s, 500)
    champ = dlg.locator("input:visible").last
    champ.fill("prime d'intéressement"); champ.press("Enter"); attendre(s, 500)
    cap(s, m, "19-passage-markdown", [(dlg.locator("textarea").first, "Segment"),
                                      (dlg.get_by_text("prime d'intéressement", exact=True).first, "Mot-clé"),
                                      (dlg.get_by_role("button", name="Confirmer"), "Confirmer")])
    dlg.get_by_role("button", name="Confirmer").click(); attendre(s, 3000)
    print("requêtes après « Confirmer » (passage Markdown, mot-clé ajouté) :", requetes, "; fenêtre encore ouverte :",
          dlg.is_visible(), flush=True)
    s.pg.reload(); attendre(s, 4000)
    print("mot-clé relu dans la page :", s.pg.get_by_text("prime d'intéressement", exact=False).count(), flush=True)


def deepdoc_config(s):
    """Analyseurs PDF proposés (liste ouverte, rien d'enregistré)."""
    m = M04
    ouvrir_base(s, BASE_04, "Configuration")
    lab = lambda t: s.pg.locator("label").filter(has_text=t).first
    haut(bouton(s, "PDF"))
    choix = lab("Analyseur PDF").locator("xpath=following::button[1]")
    choix.click(); attendre(s, 1200)
    pop = popover(s)
    print("analyseurs PDF :", pop.inner_text().replace("\n", " | "), flush=True)
    cap(s, m, "18-analyseurs-pdf", [(pop.get_by_text("DeepDOC", exact=True).first, "DeepDOC"),
                                    (pop.get_by_text("Naïf", exact=True).first, "Naïf"),
                                    (pop.get_by_text("Docling", exact=True).first, "Docling"),
                                    (pop.get_by_text("MonkeyOCRv2", exact=True).first, "MonkeyOCRv2")])
    s.pg.keyboard.press("Escape"); attendre(s, 600)
    bouton(s, "Annuler").click(); attendre(s, 800)


def deepdoc(s, *phases):
    for ph in phases or ("base", "test", "passages", "test_apres", "config", "markdown"):
        print("== phase", ph, flush=True)
        if ph == "test_apres":
            deepdoc_test(s, "17-test-apres-correction")
        else:
            globals()["deepdoc_" + ph](s)


# ---------------------------------------------------------------- manuel 05

M05 = "05-assistants-et-citations"
CHAT_05 = "Manuel-Assistant-05"
Q30 = "Quel est le délai de livraison contractuel de Batterix et quel délai moyen est réellement constaté ?"
Q35 = "Quel était le chiffre d'affaires de Vélanor en 2022 ?"
VIDE_05 = "Aucune information pertinente n'a été trouvée dans les documents."


def ouvrir_assistant(s, nom):
    s.aller("/chats", 2500)
    texte(s, nom).click(); attendre(s, 4000)


def panneau(s, ouvrir=True):
    """Panneau « Paramètres du chat » (ouvert par l'engrenage s'il est fermé)."""
    titre = s.pg.get_by_text("Paramètres du chat", exact=True)
    if ouvrir and not titre.is_visible():
        s.pg.locator("button:has(svg.lucide-settings)").last.click(); attendre(s, 2500)
    return titre.locator("xpath=ancestor::*[.//button[normalize-space()='Enregistrer']][1]")


def deplier(s, pan, libelle):
    b = pan.get_by_role("button", name=libelle, exact=True).first
    if b.get_attribute("aria-expanded") != "true" and b.get_attribute("data-state") != "open":
        b.click(); attendre(s, 900)
    return b


def assistants_creation(s):
    m = M05
    s.aller("/chats", 3000)
    carte = texte(s, "Démo Vélanor").locator("xpath=ancestor::div[contains(., 'Assistant')][1]")
    carte.hover(); attendre(s, 600)
    menu = carte.locator("button").last
    cap(s, m, "01-liste-des-assistants", [
        (s.pg.locator("button:has(svg.lucide-funnel)").first, "filtre"), (s.pg.get_by_role("searchbox").first, "Rechercher"),
        (bouton(s, "Créer un chat"), "Créer un chat"), (carte, "carte d'un assistant"), (menu, "menu de la carte")])
    menu.click(); attendre(s, 800)
    items = s.pg.get_by_role("menuitem")
    print("menu d'une carte d'assistant :", items.all_inner_texts(), flush=True)
    cap(s, m, "02-menu-d-un-assistant", [(items.nth(i), items.nth(i).inner_text().strip()) for i in range(items.count())])
    s.pg.keyboard.press("Escape"); attendre(s, 600)
    if s.pg.get_by_text(CHAT_05, exact=True).count() == 0:
        bouton(s, "Créer un chat").click(); attendre(s, 1500)
        dlg = s.pg.get_by_role("dialog")
        dlg.get_by_placeholder("Veuillez saisir le nom").fill(CHAT_05)
        dlg.get_by_role("button", name="Enregistrer").click(); attendre(s, 3500)
    texte(s, CHAT_05).click(); attendre(s, 4000)
    if s.pg.get_by_text("Paramètres du chat", exact=True).is_visible():
        s.pg.locator("button:has(svg.lucide-panel-right-close)").last.click(); attendre(s, 1500)
    cap(s, m, "03-page-d-un-assistant", [
        (s.pg.locator("button:has(svg.lucide-send)").first, "Intégrer dans la page web"),
        (s.pg.locator("button:has(svg.lucide-panel-left-close)").first, "replier la colonne"),
        (texte(s, "Conversations").locator("xpath=following::button[1]"), "nouvelle conversation"),
        (s.pg.locator("button:has(svg.lucide-copy-x)").first, "suppression groupée"),
        (s.pg.get_by_placeholder("Rechercher").first, "Rechercher"),
        (s.pg.locator("button:has(svg.lucide-settings)").last, "Paramètres du chat")])
    cap(s, m, "04-zone-de-saisie", [
        (bouton(s, "Plusieurs modèles"), "Plusieurs modèles"), (s.pg.get_by_placeholder("Saisissez votre message ici..."), "zone de saisie"),
        (s.pg.get_by_role("button", name="Attach file"), "Attach file"),
        (s.pg.get_by_role("combobox").filter(has_text="Naive").first, "Naive"),
        (s.pg.locator("button:has(svg.lucide-mic)").first, "micro"), (s.pg.get_by_role("button", name="Send message"), "Send message")])


def assistants_parametres(s):
    """Panneau « Paramètres du chat » réglage par réglage ; base « Démo Vélanor » reliée, réglages conseillés enregistrés."""
    m = M05
    ouvrir_assistant(s, CHAT_05)
    pan = panneau(s)
    lab = lambda t: pan.locator("label").filter(has_text=t).first
    modele = pan.get_by_role("button").filter(has_text="gemma4").first
    cap(s, m, "05-parametres-du-chat", [
        (pan.get_by_role("button", name="Télécharger"), "Télécharger"), (pan.get_by_role("button", name="Edit Nom"), "nom"),
        (pan.get_by_role("button", name="Edit common.description"), "description"), (modele, "Modèle"),
        (pan.get_by_role("button", name="Paramètres du modèle"), "Paramètres du modèle"),
        (lab("Message d'accueil").locator("xpath=following::textarea[1]"), "Message d'accueil")])
    modele.click(); attendre(s, 1200)
    pop = popover(s)
    print("modèles proposés :", pop.inner_text().replace("\n", " | ")[:300], flush=True)
    cap(s, m, "06-choix-du-modele", [(pop.get_by_text("gemma4:e4b").first, "gemma4:e4b")])
    s.pg.keyboard.press("Escape"); attendre(s, 700)
    pan = panneau(s)
    deplier(s, pan, "Paramètres du modèle")
    haut(lab("Liberté"))
    cap(s, m, "07-parametres-du-modele", [
        (lab("Liberté").locator("xpath=following::*[@role='combobox'][1]"), "Liberté"),
        (lab("Température"), "Température"), (lab("Top P"), "Top P"), (lab("Pénalité de présence"), "Pénalité de présence"),
        (lab("Pénalité de fréquence"), "Pénalité de fréquence"), (lab("Nombre max de tokens"), "Nombre max de tokens")])
    lib = lab("Liberté").locator("xpath=following::*[@role='combobox'][1]")
    lib.click(); attendre(s, 900)
    cap(s, m, "08-liberte", [(s.pg.get_by_role("option", name=n), n) for n in ("Improviser", "Précis", "Équilibre", "Personnalisé")])
    s.pg.keyboard.press("Escape"); attendre(s, 600)
    pan = panneau(s)
    think = lab("Thinking").locator("xpath=following::*[@role='combobox'][1]")
    haut(lab("Thinking"))
    think.click(); attendre(s, 900)
    cap(s, m, "09-thinking", [(s.pg.get_by_role("option", name=n).first, n) for n in ("System default", "Enabled", "Disabled")])
    s.pg.keyboard.press("Escape"); attendre(s, 600)
    pan = panneau(s)
    deplier(s, pan, "Paramètres du modèle")  # replie la section
    choix = lab("Bases de connaissances").locator("xpath=following::button[1]")
    haut(lab("Message d'accueil"))
    choix.click(); attendre(s, 1200)
    opt = s.pg.get_by_role("option").filter(has_text="Démo Vélanor").first
    cap(s, m, "10-choix-de-la-base", [(s.pg.get_by_placeholder("Rechercher...").last, "Rechercher..."), (opt, "Démo Vélanor")])
    if "Démo Vélanor" not in choix.inner_text():
        opt.click(); attendre(s, 800)
    s.pg.keyboard.press("Escape"); attendre(s, 800)
    pan = panneau(s)
    deplier(s, pan, "Paramètres avancés")
    haut(lab("Afficher la citation"))
    cap(s, m, "11-parametres-avances", [
        (lab("Afficher la citation"), "Afficher la citation"), (lab("Texte en parole"), "Texte en parole"),
        (lab("Web search provider").locator("xpath=following::*[self::button or @role='combobox'][1]"), "Web search provider"),
        (lab("Métadonnées").locator("xpath=following::*[@role='combobox'][1]"), "Métadonnées"),
        (pan.get_by_role("button", name="Naive", exact=True), "Naive"), (pan.get_by_role("button", name="Agentic", exact=True), "Agentic")])
    lab("Web search provider").locator("xpath=following::*[self::button or @role='combobox'][1]").click(); attendre(s, 1000)
    pop = popover(s)
    print("fournisseurs de recherche web :", pop.inner_text().replace("\n", " | ")[:300], flush=True)
    cap(s, m, "12-web-search-provider", [(pop, "fournisseurs proposés")])
    s.pg.keyboard.press("Escape"); attendre(s, 600)
    pan = panneau(s)
    lab("Métadonnées").locator("xpath=following::*[@role='combobox'][1]").click(); attendre(s, 1000)
    opts = s.pg.get_by_role("option")
    print("filtre de métadonnées :", opts.all_inner_texts(), flush=True)
    cap(s, m, "13-metadonnees", [(opts.nth(i), opts.nth(i).inner_text().strip()) for i in range(min(opts.count(), 4))])
    s.pg.keyboard.press("Escape"); attendre(s, 600)
    pan = panneau(s)
    deplier(s, pan, "Naive")
    vide = lab("Réponse vide").locator("xpath=following::textarea[1]")
    vide.fill(VIDE_05)
    haut(lab("Réponse vide"))
    cap(s, m, "14-naive-reponse-et-prompt", [
        (vide, "Réponse vide"), (lab("Analyse de mots-clés"), "Analyse de mots-clés"),
        (lab("Prompt système").locator("xpath=following::textarea[1]"), "Prompt système")])
    seuil = lab("Seuil de similarité")
    haut(seuil)
    num = lambda l: l.locator("xpath=following::input[@type='number'][1]")
    poids = lab("Poids de similarité par mots-clés")
    print("valeurs avant réglage : seuil", num(seuil).input_value(), "; poids mots-clés", num(poids).input_value(),
          "; rerank candidates", num(lab("Rerank candidates")).input_value(), "; Top N", num(lab("Top N")).input_value(), flush=True)
    num(poids).fill("0.3"); num(poids).press("Tab"); attendre(s, 400)
    num(lab("Top N")).fill("8"); num(lab("Top N")).press("Tab"); attendre(s, 400)
    haut(seuil)
    cap(s, m, "15-naive-recherche", [
        (seuil.locator("xpath=.."), "Seuil de similarité"), (poids.locator("xpath=.."), "Poids de similarité par mots-clés"),
        (lab("Rerank candidates").locator("xpath=.."), "Rerank candidates"), (lab("Top N").locator("xpath=.."), "Top N"),
        (lab("Modèle de réordonnancement"), "Modèle de réordonnancement"), (lab("Recherche inter-langues"), "Recherche inter-langues")])
    multi = lab("Optimisation multi-tours")
    haut(multi)
    cap(s, m, "16-naive-multi-tours-variables", [
        (multi, "Optimisation multi-tours"), (lab("Variable"), "Variable"),
        (lab("Variable").locator("xpath=following::input[1]"), "knowledge")])
    deplier(s, pan, "Agentic")
    dec = lab("Decision model")
    haut(dec)
    cap(s, m, "17-agentic", [(dec, "Decision model"), (lab("Agentic template"), "Agentic template"),
                             (pan.get_by_role("button", name="Reset to default"), "Reset to default")])
    enr = pan.get_by_role("button", name="Enregistrer")
    cap(s, m, "18-enregistrer", [(pan.get_by_role("button", name="Annuler"), "Annuler"), (enr, "Enregistrer")])
    enr.click(); attendre(s, 900)
    print("après enregistrement :", s.pg.locator("[data-sonner-toast]").all_inner_texts(), flush=True)
    s.pg.reload(); attendre(s, 4000)
    pan = panneau(s); deplier(s, pan, "Paramètres avancés"); deplier(s, pan, "Naive")
    print("relu : Top N", num(lab("Top N")).input_value(), "; poids mots-clés", num(lab("Poids de similarité par mots-clés")).input_value(),
          "; réponse vide", lab("Réponse vide").locator("xpath=following::textarea[1]").input_value(),
          "; base", lab("Bases de connaissances").locator("xpath=following::button[1]").inner_text(), flush=True)


def assistants_test(s):
    """« Test de récupération » de la base « Démo Vélanor » (rien n'est enregistré dans la base)."""
    m = M05
    ouvrir_base(s, "Démo Vélanor", "Test de récupération")
    lab = lambda t: s.pg.locator("label").filter(has_text=t).first
    cap(s, m, "19-test-reglages", [
        (lab("Seuil de similarité").locator("xpath=.."), "Seuil de similarité"),
        (lab("Poids de similarité par mots-clés").locator("xpath=.."), "Poids de similarité par mots-clés"),
        (lab("Modèle de réordonnancement").locator("xpath=.."), "Modèle de réordonnancement"),
        (lab("Recherche inter-langues").locator("xpath=.."), "Recherche inter-langues"),
        (lab("Métadonnées").locator("xpath=.."), "Métadonnées"), (lab("Top N").locator("xpath=.."), "Rerank candidates, Top N")])
    zone, res = test_recuperation(s, m, "Démo Vélanor", Q30)
    ligne_scores = s.pg.get_by_text(re.compile("Similarité hybride")).first.locator("xpath=..")
    cap(s, m, "20-test-resultats", [(zone, "question"), (bouton(s, "Test"), "Test"),
                                    (s.pg.get_by_text(re.compile("^Total")).first, "Total"), (ligne_scores, "scores"),
                                    (s.pg.get_by_text(re.compile(r"\.(pdf|xlsx|md|html|docx|pptx)$")).first, "document")])
    num = lab("Poids de similarité par mots-clés").locator("xpath=following::input[@type='number'][1]")
    num.fill("0.3"); num.press("Tab"); attendre(s, 400)
    bouton(s, "Test").click(); attendre(s, 5000)
    txt = s.pg.get_by_text("Résultats", exact=True).first.locator("xpath=ancestor::*[self::section or self::div][2]").inner_text()
    print("résultats avec mots-clés 0,3 :", " | ".join(x for x in txt.splitlines() if x.strip())[:900], flush=True)
    cap(s, m, "21-test-vecteurs-07", [(num.locator("xpath=.."), "Poids de similarité par mots-clés"),
                                      (s.pg.get_by_text(re.compile("^Total")).first, "Total"),
                                      (s.pg.get_by_text(re.compile("Similarité hybride")).first.locator("xpath=.."), "scores")])


def envoyer(s, question, mode=None):
    """Tape et envoie une question ; renvoie la durée jusqu'à l'affichage des jetons de la réponse."""
    zone = s.pg.get_by_placeholder("Saisissez votre message ici...")
    if mode:
        s.pg.get_by_role("combobox").filter(has_text=re.compile("Naive|Agentic")).first.click(); attendre(s, 800)
        s.pg.get_by_role("option").filter(has_text=mode).first.click(); attendre(s, 800)
    zone.fill(question)
    n = s.pg.get_by_text(re.compile(r"tokens \(\d+ input")).count()
    t0 = time.time()
    s.pg.get_by_role("button", name="Send message").click()
    s.pg.get_by_text(re.compile(r"tokens \(\d+ input")).nth(n).wait_for(timeout=300000)
    d = time.time() - t0
    attendre(s, 3500)
    rep = s.pg.get_by_text(re.compile(r"tokens \(\d+ input")).nth(n).locator("xpath=..").inner_text()
    mode_lu = s.pg.get_by_role("combobox").filter(has_text=re.compile("Naive|Agentic")).first.inner_text().strip()
    print(f"réponse (mode {mode_lu}) affichée après {d:.1f} s : {rep[:700]}", flush=True)
    return d


def assistants_conversation(s):
    """Question réelle, lecture de la réponse et des citations, actions, question piège, conversation supprimée."""
    m = M05
    ouvrir_assistant(s, CHAT_05)
    texte(s, "Conversations").locator("xpath=following::button[1]").click(); attendre(s, 2000)
    envoyer(s, Q30)
    jetons = s.pg.get_by_text(re.compile(r"tokens \(\d+ input")).last
    renvoi = s.pg.locator("[data-state]").filter(has_text=re.compile(r"^\[\d+\]$")).last  # déclencheur de survol
    vignettes = jetons.locator("xpath=following::button[contains(., '…') or contains(., '.')][1]")
    cap(s, m, "22-reponse-citee", [(renvoi, "renvoi"),
                                   (jetons, "jetons et durée"), (vignettes, "document cité"),
                                   (s.pg.get_by_role("button").filter(has_text=Q30[:20]).first, "conversation")])
    reponse = jetons.locator("xpath=../..")
    reponse.hover(); attendre(s, 1000)
    noms = {"copy": "copier", "refresh-cw": "régénérer", "trash": "supprimer", "volume-2": "lire à voix haute",
            "thumbs-up": "pouce haut", "thumbs-down": "pouce bas", "lightbulb": "ampoule"}
    icones = []
    for cle_, nom_ in noms.items():
        b = s.pg.locator(f"button:has(svg.lucide-{cle_}):visible")
        if b.count():
            icones.append((b.last, nom_))
    print("actions de la réponse :", [n for _, n in icones], flush=True)
    cap(s, m, "23-actions-sur-une-reponse", icones[:6])
    renvoi.hover(); attendre(s, 2000)
    cap(s, m, "24-citation-au-survol", [(popover(s), "extrait cité")])
    s.pg.mouse.move(5, 450); attendre(s, 800)
    vignettes.click(); attendre(s, 2500)
    dlg = s.pg.get_by_role("dialog").last
    cap(s, m, "25-document-cite", [(dlg.get_by_text("contrat-batterix-scan.pdf").first, "nom du document"),
                                   (dlg.locator("button").last, "fermer")])
    s.pg.keyboard.press("Escape"); attendre(s, 1000)
    envoyer(s, Q35)
    rep35 = s.pg.get_by_text(re.compile("ne se trouve pas|Aucune information")).last
    cap(s, m, "26-question-sans-reponse", [(rep35, "début de la réponse")])
    conv = s.pg.get_by_role("button").filter(has_text=Q30[:20]).first
    conv.hover(); attendre(s, 600)
    conv.locator("xpath=..").locator("button:has(svg.lucide-ellipsis)").first.click(); attendre(s, 1000)
    items = s.pg.get_by_role("menuitem")
    print("menu d'une conversation :", items.all_inner_texts(), flush=True)
    cap(s, m, "27-menu-d-une-conversation", [(items.nth(i), items.nth(i).inner_text().strip()) for i in range(items.count())])
    s.pg.keyboard.press("Escape"); attendre(s, 800)
    s.pg.locator("button:has(svg.lucide-copy-x)").first.click(); attendre(s, 1000)
    liste = texte(s, "Conversations").locator("xpath=ancestor::aside[1]")
    cases = liste.get_by_role("checkbox")
    for i in range(cases.count()):
        if cases.nth(i).get_attribute("aria-checked") != "true":
            cases.nth(i).click(); attendre(s, 400)
    btns = texte(s, "Conversations").locator("xpath=ancestor::div[.//button][1]").locator("button")
    print("boutons en mode sélection :", btns.count(), flush=True)
    cap(s, m, "28-suppression-groupee", [(cases.first, "case d'une conversation"), (btns.nth(0), "annuler la sélection"),
                                         (btns.nth(btns.count() - 1), "supprimer la sélection")])
    btns.nth(btns.count() - 1).click(); attendre(s, 1200)
    conf = s.pg.get_by_role("alertdialog").or_(s.pg.get_by_role("dialog")).last
    ok = conf.get_by_role("button").filter(has_text=re.compile("Supprimer|Delete|Oui|OK|Confirmer")).last
    cap(s, m, "29-confirmer-la-suppression", [(conf, "confirmation"), (ok, ok.inner_text().strip())])
    ok.click(); attendre(s, 2000)
    print("conversations restantes :", s.pg.get_by_text("Conversations", exact=True).first.locator("xpath=..").inner_text(), flush=True)


def assistants_ecran(s):
    """« Plusieurs modèles », pièce jointe, « Intégrer dans la page web » (adresse et jeton masqués)."""
    m = M05
    ouvrir_assistant(s, CHAT_05)
    s.pg.get_by_role("button", name="Attach file").click(); attendre(s, 1200)
    entree = s.pg.locator("input[type=file]").last
    entree.set_input_files(CORPUS + "faq-sav.html"); attendre(s, 2000)
    cap(s, m, "30-piece-jointe", [(s.pg.get_by_text("faq-sav.html").last.locator("xpath=.."), "fichier joint"),
                                  (s.pg.get_by_role("button", name="Attach file"), "Attach file")])
    bouton(s, "Plusieurs modèles").click(); attendre(s, 2500)
    plus = s.pg.locator("button:has(svg.lucide-plus)").last
    cap(s, m, "31-plusieurs-modeles", [(bouton(s, "Retour"), "Retour"),
                                       (s.pg.get_by_text("gemma4:e4b").first.locator("xpath=.."), "modèle de la colonne 1"),
                                       (plus.locator("xpath=preceding::button[1]"), "Appliquer la configuration du modèle"),
                                       (plus, "ajouter une colonne")])
    plus.click(); attendre(s, 1500)
    cap(s, m, "32-deux-colonnes", [(s.pg.get_by_text(re.compile(r"Plusieurs modèles \(\d/3\)")).first, "Plusieurs modèles (2/3)"),
                                   (s.pg.get_by_placeholder("Saisissez votre message ici..."), "zone de saisie commune")])
    bouton(s, "Retour").click(); attendre(s, 2500)
    s.pg.locator("button:has(svg.lucide-send)").first.click(); attendre(s, 2000)
    dlg = s.pg.get_by_role("dialog").last
    code = dlg.locator("pre, code").first
    url_id = dlg.get_by_text(re.compile("^[0-9a-f]{32}$")).first
    cap(s, m, "33-integrer-dans-la-page-web", [
        (dlg.get_by_text("Type d'intégration").first.locator("xpath=.."), "Type d'intégration"),
        (dlg.get_by_text("Thème", exact=True).first.locator("xpath=.."), "Thème"),
        (dlg.get_by_text("Cacher l'avatar").first.locator("xpath=.."), "Cacher l'avatar"),
        (dlg.get_by_text("Paramètres régionaux").first.locator("xpath=.."), "Paramètres régionaux"),
        (code, "Code d'intégration"), (dlg.get_by_text("Ouvrir dans un nouvel onglet").first, "Ouvrir dans un nouvel onglet")],
        masques=[code])
    dlg.get_by_text("Widget Customization").first.click(); attendre(s, 1200)
    print("onglet Widget Customization :", re.sub(r"auth=[0-9A-Za-z_-]+", "auth=<masqué>", dlg.inner_text()).replace("\n", " | ")[:600], flush=True)
    cap(s, m, "34-widget-customization", [(dlg.get_by_text("Widget Customization").first, "Widget Customization")],
        masques=[dlg.locator("pre, code").first] if dlg.locator("pre, code").count() else [])
    caviarder(m, "33-integrer-dans-la-page-web", "34-widget-customization")
    s.pg.keyboard.press("Escape"); attendre(s, 800)


def assistants(s, *phases):
    for ph in phases or ("creation", "parametres", "test", "conversation", "ecran"):
        print("== phase", ph, flush=True)
        globals()["assistants_" + ph](s)


# ---------------------------------------------------------------- manuel 06

M06 = "06-agentic-rag"
CHAT_06 = "Manuel-Agentic"


def agentique_assistant(s):
    """Assistant « Manuel-Agentic » créé à la souris (réglages par défaut), relié à « Démo Vélanor »."""
    s.aller("/chats", 3000)
    if s.pg.get_by_text(CHAT_06, exact=True).count() == 0:
        bouton(s, "Créer un chat").click(); attendre(s, 1500)
        dlg = s.pg.get_by_role("dialog")
        dlg.get_by_placeholder("Veuillez saisir le nom").fill(CHAT_06)
        dlg.get_by_role("button", name="Enregistrer").click(); attendre(s, 3500)
    texte(s, CHAT_06).click(); attendre(s, 4000)
    pan = panneau(s)
    choix = pan.locator("label").filter(has_text="Bases de connaissances").first.locator("xpath=following::button[1]")
    if "Démo Vélanor" not in choix.inner_text():
        choix.click(); attendre(s, 1200)
        s.pg.get_by_role("option").filter(has_text="Démo Vélanor").first.click(); attendre(s, 800)
        s.pg.keyboard.press("Escape"); attendre(s, 800)
        pan = panneau(s)
        pan.get_by_role("button", name="Enregistrer").click(); attendre(s, 1500)
        print("assistant relié :", s.pg.locator("[data-sonner-toast]").all_inner_texts(), flush=True)


def agentique_questions(s):
    m = M06
    ouvrir_assistant(s, CHAT_06)
    if s.pg.get_by_text("Paramètres du chat", exact=True).is_visible():
        s.pg.locator("button:has(svg.lucide-panel-right-close)").last.click(); attendre(s, 1500)
    texte(s, "Conversations").locator("xpath=following::button[1]").click(); attendre(s, 2000)
    sel = s.pg.get_by_role("combobox").filter(has_text=re.compile("Naive|Agentic")).first
    sel.click(); attendre(s, 1000)
    cap(s, m, "01-modes-de-reponse", [(s.pg.get_by_role("option").filter(has_text="Agentic").first, "Agentic"),
                                      (s.pg.get_by_role("option").filter(has_text="Naive").first, "Naive")])
    s.pg.get_by_role("option").filter(has_text="Agentic").first.click(); attendre(s, 800)
    zone = s.pg.get_by_placeholder("Saisissez votre message ici...")
    zone.fill(Q30)
    cap(s, m, "02-question-agentic", [(zone, "question"), (sel, "Agentic"), (s.pg.get_by_role("button", name="Send message"), "Send message")])
    zone.fill("")
    envoyer(s, Q30)
    jetons = s.pg.get_by_text(re.compile(r"tokens \(\d+ input")).last
    cap(s, m, "03-reponse-agentic", [(s.pg.get_by_text(Q30).last, "question"),
                                     (jetons.locator("xpath=preceding-sibling::*[1]"), "réponse"), (jetons, "jetons et durée")])
    texte(s, "Conversations").locator("xpath=following::button[1]").click(); attendre(s, 2000)
    envoyer(s, Q30, mode="Naive")
    jetons = s.pg.get_by_text(re.compile(r"tokens \(\d+ input")).last
    attendre(s, 2000)
    cap(s, m, "04-reponse-naive", [(jetons, "jetons et durée"),
                                   (s.pg.get_by_role("combobox").filter(has_text="Naive").first, "Naive")])


def agentique(s, *phases):
    for ph in phases or ("assistant", "questions"):
        print("== phase", ph, flush=True)
        globals()["agentique_" + ph](s)


if __name__ == "__main__":
    scenario, *args = sys.argv[1:]
    with sync_playwright() as p:
        s = Session(p)
        s.pg.set_default_timeout(15000)
        try:
            s.connexion(); s.francais()
            globals()[scenario](s, *args)
        except Exception:
            traceback.print_exc()
            ECHEC.mkdir(parents=True, exist_ok=True)
            s.pg.screenshot(path=str(ECHEC / "echec-lot2.png"))
            (ECHEC / "echec-lot2.txt").write_text(s.pg.inner_text("body"))
            sys.exit(1)
        finally:
            s.b.close()
