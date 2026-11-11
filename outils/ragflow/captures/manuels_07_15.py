"""Captures des manuels 07, 08, 09 et 15 de RAGFlow (lot 3), tout à la souris dans l'interface en français.

Lancement : outils/communs/captures/lancer.sh outils/ragflow/captures/manuels_07_15.py <scénario> [phases...]
Scénarios : compilation (manuel 07), agents (08), sources (09), recherche (15). Chaque scénario se découpe en phases
rejouables une à une ; sans phase, toutes sont jouées dans l'ordre.
Objets créés à la souris, tous nommés « Manuel-… » (opérateurs de compilation, pipelines, bases, agents, mémoire,
source de données, application de recherche) ; supprimés ensuite par outils/ragflow/nettoyer_manuel.py.
Le jeu de démonstration (« Démo Vélanor », « Agent démo Vélanor », « Essai-KC-mind_map-1835 ») n'est ouvert qu'en
lecture ; le canevas du pipeline « Essai-KC-mind_map-1835 » n'est jamais ouvert (l'enregistrement automatique du
canevas en retire le composant Compiler créé par l'API, voir manuel 07).
Helpers repris des lots 1 et 2 : captures.py (Session, cap, bouton, texte) et manuels_03_06.py.
"""
import json
import re
import sys
import time
import traceback
from pathlib import Path

from playwright.sync_api import sync_playwright

from captures import Session, URL, TXT, COMPTE, cap, bouton, texte  # noqa: F401
from manuels_03_06 import attendre, popover, haut, centre, ouvrir_base, ligne, segments, caviarder  # noqa: F401

CORPUS = "corpus/documents/"
ECHEC = Path("donnees/captures-explorer")


def log(*a):
    print(*a, flush=True)


def api(s, methode, chemin, **kw):
    """Appel de l'API HTTP depuis le navigateur de capture (lecture d'état seulement : suivi d'une compilation)."""
    r = s.pg.request.fetch(f"{URL}/api/v1{chemin}", method=methode,
                           headers={"Authorization": f"Bearer {COMPTE['api_key']}"}, **kw)
    return r.json()


# ---------------------------------------------------------------- canevas (pipelines et agents)

def fit(s):
    s.pg.get_by_role("button", name="Fit View").click(); attendre(s, 800)


def fermer_panneau(s):
    x = s.pg.locator("svg.lucide-x").filter(visible=True)
    if x.count():
        x.last.click(); attendre(s, 600)
    s.pg.mouse.click(300, 200); attendre(s, 400)


def noeud(s, nom):
    return s.pg.locator(".react-flow__node").filter(has_text=nom).last


def poignee(s, nom):
    return noeud(s, nom).locator("[data-handleid=start]")


def etape_suivante(s, nom):
    """Ouvre le menu « Étape suivante » par le « + » de la poignée de sortie du nœud `nom` ; renvoie le menu."""
    menu = s.pg.locator("[data-radix-popper-content-wrapper]").filter(has_text="Étape suivante")
    for essai in range(4):
        fermer_panneau(s); fit(s)
        nd = noeud(s, nom)
        nd.hover(); attendre(s, 600)
        b = poignee(s, nom).bounding_box()
        s.pg.mouse.move(b["x"] + b["width"] / 2, b["y"] + b["height"] / 2); attendre(s, 400)
        s.pg.mouse.click(b["x"] + b["width"] / 2, b["y"] + b["height"] / 2); attendre(s, 1200)
        if menu.count() and menu.last.is_visible():
            return menu.last
        log("menu « Étape suivante » absent, essai", essai)
    raise RuntimeError("menu « Étape suivante » absent")


def ouvrir_agent(s, onglet, nom):
    s.aller("/agents", 2500)
    if onglet:
        s.pg.get_by_role("radio", name=onglet).click(); attendre(s, 2000)
    texte(s, nom).click(); attendre(s, 5000)


# ---------------------------------------------------------------- manuel 07

M07 = "07-knowledge-compilation"
OP_07 = "Manuel-Operateur-Graphe"
PIPE_07 = "Manuel-Pipeline-Graphe"
BASE_07 = "Manuel-KC-Graphe"
DOC_07 = "cse-2025-10-14.md"
DEMO_KC = "Essai-KC-mind_map-1835"


def compilation_operateur(s):
    """Onglet « Compilation operator », création de l'opérateur « Manuel-Operateur-Graphe » (gabarit Graph)."""
    m = M07
    s.aller("/agents", 2500)
    s.pg.get_by_role("radio", name="Compilation operator").click(); attendre(s, 2000)
    plus = s.pg.locator("button:has(svg.lucide-plus)").first
    cap(s, m, "01-compilation-operator", [
        (s.pg.get_by_role("radio", name="Compilation operator"), "Compilation operator"),
        (texte(s, DEMO_KC).locator("xpath=ancestor::div[.//*[text()='Mindmap']][1]"), "opérateur existant"),
        (plus, "+")])
    plus.click(); attendre(s, 2500)
    nom = s.pg.get_by_placeholder("Veuillez saisir le nom")
    nom.fill(OP_07)
    desc = s.pg.get_by_placeholder("Saisir une description")
    desc.fill("Graphe des entités et relations, essai du manuel 07")
    gab = s.pg.get_by_role("combobox").first
    cap(s, m, "02-nouvel-operateur", [
        (nom, "Nom"), (desc, "Description"), (gab, "Template"),
        (s.pg.get_by_placeholder("Input global compilation rules"), "Global rules"),
        (bouton(s, "Enregistrer"), "Enregistrer")])
    gab.click(); attendre(s, 1000)
    opt = lambda t: s.pg.get_by_role("option", name=t, exact=True)
    cap(s, m, "03-liste-des-templates", [(opt("Graph"), "Graph"), (opt("Mindmap"), "Mindmap"),
                                         (opt("PageIndex"), "PageIndex"), (opt("Timeline"), "Timeline"),
                                         (opt("Tree"), "Tree"), (opt("Wiki"), "Wiki")])
    opt("Graph").click(); attendre(s, 1500)
    cap(s, m, "04-operateur-graph", [
        (s.pg.get_by_role("combobox").filter(has_text="Graph").first, "Graph"),
        (s.pg.get_by_placeholder("Input global compilation rules"), "Global rules"),
        (s.pg.locator("label").filter(has_text="Re-chunk parser output").first, "Re-chunk parser output")])
    ent = s.pg.get_by_role("tab", name="Entity specification")
    haut(ent); attendre(s, 600)
    cap(s, m, "05-specifications", [
        (ent, "Entity specification"), (s.pg.get_by_role("tab", name="Relation specification"), "Relation specification"),
        (s.pg.get_by_text("person", exact=True).first.locator("xpath=ancestor::div[contains(@class,'border')][1]"), "person"),
        (s.pg.get_by_text("Add field", exact=True).first, "Add field"), (bouton(s, "Enregistrer"), "Enregistrer")])
    s.pg.get_by_role("tab", name="Relation specification").click(); attendre(s, 1000)
    log("relations Graph :", s.pg.locator("body").inner_text()[-1200:].replace("\n", " | "))
    s.pg.get_by_role("tab", name="Entity specification").click(); attendre(s, 600)
    log("champs Graph :", s.pg.locator("main, body").first.inner_text()[:1500].replace("\n", " | "))
    bouton(s, "Enregistrer").click(); attendre(s, 3000)
    log("après Enregistrer :", s.pg.url.replace(URL, ""))
    s.aller("/agents", 2500)
    s.pg.get_by_role("radio", name="Compilation operator").click(); attendre(s, 2000)
    carte = texte(s, OP_07).locator("xpath=ancestor::div[.//*[text()='Graph']][1]")
    cap(s, m, "06-operateur-cree", [(carte, OP_07)])


def compilation_pipeline(s):
    """Pipeline d'ingestion « Manuel-Pipeline-Graphe » créé depuis un blanc : Parser, Chunker, Compiler, Indexeur."""
    m = M07
    s.aller("/agents", 2500)
    s.pg.get_by_role("radio", name="Ingestion pipeline").click(); attendre(s, 2000)
    plus = s.pg.locator("button:has(svg.lucide-plus)").first
    plus.click(); attendre(s, 1200)
    cap(s, m, "07-menu-de-creation", [
        (s.pg.locator("[role=radio]").filter(has_text="Ingestion pipeline"), "Ingestion pipeline"),
        (s.pg.get_by_role("menuitem").filter(has_text="Créer depuis un blanc").first, "Créer depuis un blanc"),
        (s.pg.get_by_role("menuitem").filter(has_text="Créer depuis un modèle").first, "Créer depuis un modèle"),
        (s.pg.get_by_role("menuitem").filter(has_text="Importer un fichier JSON").first, "Importer un fichier JSON")])
    s.pg.get_by_role("menuitem").filter(has_text="Créer depuis un blanc").first.click(); attendre(s, 1500)
    dlg = s.pg.get_by_role("dialog")
    dlg.locator("input").first.fill(PIPE_07)
    cap(s, m, "08-nom-du-pipeline", [(dlg.locator("input").first, "Nom"), (dlg.get_by_role("button", name="Confirmer"), "Confirmer")])
    dlg.get_by_role("button", name="Confirmer").click(); attendre(s, 5000)
    fit(s)
    cap(s, m, "09-canevas-initial", [
        (noeud(s, "Commencer"), "Commencer"), (noeud(s, "Parser"), "Parser"),
        (bouton(s, "Save draft"), "Save draft"), (bouton(s, "Publier"), "Publier"), (bouton(s, "Gestion"), "Gestion"),
        (s.pg.locator(".react-flow__controls").first, "commandes du canevas")])
    noeud(s, "Parser").click(); attendre(s, 1500)
    panneau = s.pg.get_by_text("PDF", exact=True).last
    cap(s, m, "10-parser", [(s.pg.get_by_text("Parser", exact=True).last, "Parser"),
                            (s.pg.get_by_role("button", name="Ajouter un parser").first if s.pg.get_by_role("button", name="Ajouter un parser").count() else panneau, "formats")])
    menu = etape_suivante(s, "Parser")
    cap(s, m, "11-etape-suivante-chunker", [(poignee(s, "Parser"), "+"),
                                            (menu.get_by_text("Découpeur par tokens", exact=True), "Découpeur par tokens"),
                                            (menu.get_by_text("Découpeur par titres", exact=True), "Découpeur par titres")])
    menu.get_by_text("Découpeur par tokens", exact=True).click(); attendre(s, 1500)
    bouton(s, "Save draft").click(); attendre(s, 2000)
    menu = etape_suivante(s, "Chunker")
    cap(s, m, "12-etape-suivante-compiler", [(poignee(s, "Chunker"), "+"),
                                             (menu.get_by_text("Indexeur", exact=True), "Indexeur"),
                                             (menu.get_by_text("Compiler", exact=True), "Compiler"),
                                             (menu.get_by_text("Transformateur", exact=True), "Transformateur")])
    menu.get_by_text("Compiler", exact=True).click(); attendre(s, 1500)
    bouton(s, "Save draft").click(); attendre(s, 2000)
    fermer_panneau(s); fit(s)
    noeud(s, "Compiler").click(); attendre(s, 1500)
    op = s.pg.get_by_role("combobox").filter(has_text="Sélectionner une valeur").first
    cap(s, m, "13-compiler", [
        (op, "Operator"), (s.pg.get_by_text("Create template", exact=False).first, "Create template"),
        (s.pg.get_by_role("button").filter(has_text="gemma4:e4b").last, "Modèle"),
        (s.pg.locator("label").filter(has_text="Température").first, "Température"),
        (s.pg.locator("label").filter(has_text="Thinking").first, "Thinking")])
    op.click(); attendre(s, 1000)
    choix = s.pg.get_by_role("option", name=OP_07)
    cap(s, m, "14-choix-de-l-operateur", [(choix, OP_07), (s.pg.get_by_role("option", name=DEMO_KC), DEMO_KC)])
    choix.click(); attendre(s, 1200)
    bouton(s, "Save draft").click(); attendre(s, 2000)
    menu = etape_suivante(s, "Compiler")
    cap(s, m, "15-etape-suivante-indexeur", [(poignee(s, "Compiler"), "+"),
                                             (menu.get_by_text("Indexeur", exact=True), "Indexeur"),
                                             (menu.get_by_text("Transformateur", exact=True), "Transformateur")])
    menu.get_by_text("Indexeur", exact=True).click(); attendre(s, 1500)
    bouton(s, "Save draft").click(); attendre(s, 2500)
    fermer_panneau(s); fit(s)
    cap(s, m, "16-pipeline-complet", [(noeud(s, "Parser"), "Parser"), (noeud(s, "Chunker"), "Chunker"),
                                      (noeud(s, "Compiler"), "Compiler"), (noeud(s, "Indexeur"), "Indexeur"),
                                      (bouton(s, "Save draft"), "Save draft")])
    bouton(s, "Publier").click(); attendre(s, 1500)
    dlg = s.pg.get_by_role("dialog")
    alias = dlg.get_by_placeholder("Alias")
    alias.fill("v1")
    cap(s, m, "17-publier", [(alias, "Alias"), (dlg.get_by_role("button", name="Confirmer"), "Confirmer")])
    dlg.get_by_role("button", name="Confirmer").click(); attendre(s, 3000)
    log("après publication :", s.pg.inner_text("body")[:300].replace("\n", " | "))
    s.aller("/agents", 2500)
    s.pg.get_by_role("radio", name="Ingestion pipeline").click(); attendre(s, 2000)
    carte = texte(s, PIPE_07).locator("xpath=ancestor::div[.//*[contains(text(),'Publié')]][1]")
    cap(s, m, "18-pipeline-publie", [(carte, PIPE_07)])


def compilation_base(s):
    """Base « Manuel-KC-Graphe » : pipeline choisi dans « Configuration », document importé et analysé."""
    m = M07
    s.aller("/datasets", 2500)
    bouton(s, "Créer une base de connaissances").click(); attendre(s, 1500)
    dlg = s.pg.get_by_role("dialog")
    dlg.get_by_placeholder("Veuillez saisir un nom !").fill(BASE_07)
    cap(s, m, "19-creation-de-la-base", [(dlg.get_by_placeholder("Veuillez saisir un nom !"), "Nom"),
                                         (dlg.get_by_role("button", name="Enregistrer"), "Enregistrer")])
    dlg.get_by_role("button", name="Enregistrer").click(); attendre(s, 4000)


def compilation_configuration(s):
    """« Configuration » de la base : « Mode d'analyse » passé sur le pipeline publié."""
    m = M07
    ouvrir_base(s, BASE_07, "Configuration")
    mode = s.pg.get_by_role("button").filter(has_text="built in").first
    haut(mode)
    mode.click(); attendre(s, 1200)
    pop = popover(s)
    item = pop.get_by_text(PIPE_07).first
    cap(s, m, "20-mode-d-analyse", [(item, PIPE_07), (pop.get_by_text("General", exact=True).first, "General")])
    item.click(); attendre(s, 1500)
    log("liste après clic sur le pipeline :", popover(s).inner_text().replace("\n", " | ")[:300])
    pop = popover(s)
    version = pop.get_by_text(re.compile(PIPE_07 + "_")).first
    cap(s, m, "21-version-du-pipeline", [(pop.get_by_text(PIPE_07, exact=True).first, PIPE_07),
                                         (version.locator("xpath=.."), "version publiée")])
    version.click(); attendre(s, 1500)
    enr = bouton(s, "Enregistrer")
    cap(s, m, "22-pipeline-choisi", [(s.pg.get_by_role("button").filter(has_text=PIPE_07).first, PIPE_07),
                                     (s.pg.get_by_role("tab", name="Compiler"), "Compiler"), (enr, "Enregistrer")])
    enr.click(); attendre(s, 2500)
    s.pg.reload(); attendre(s, 3000)
    log("mode d'analyse relu après rechargement :", s.pg.get_by_role("button").filter(has_text=PIPE_07).first.inner_text())


def compilation_import(s):
    """Document court importé avec « Analyser à la création » ; suivi de l'ingestion et de la compilation."""
    m = M07
    ouvrir_base(s, BASE_07)
    bouton(s, "Ajouter un fichier").click(); attendre(s, 1000)
    s.pg.get_by_role("menuitem").filter(has_text="Téléverser un fichier").first.click(); attendre(s, 1500)
    dlg = s.pg.get_by_role("dialog")
    dlg.locator("input[type=file]").first.set_input_files([CORPUS + DOC_07]); attendre(s, 1500)
    sw = dlg.get_by_role("switch").first
    if sw.get_attribute("aria-checked") != "true":
        sw.click(); attendre(s, 600)
    cap(s, m, "23-televersement", [(sw.locator("xpath=.."), "Analyser à la création"),
                                   (dlg.get_by_text(DOC_07).first, DOC_07),
                                   (dlg.get_by_role("button", name="Enregistrer"), "Enregistrer")])
    t0 = time.time()
    dlg.get_by_role("button", name="Enregistrer").click(); attendre(s, 3000)
    ds = next(d for d in api(s, "GET", "/datasets", params={"name": BASE_07})["data"] if d["name"] == BASE_07)
    etat = {}
    while time.time() - t0 < 1800:
        docs = api(s, "GET", f"/datasets/{ds['id']}/documents")["data"]
        doc = (docs.get("docs") if isinstance(docs, dict) else docs)[0]
        etat = api(s, "GET", f"/datasets/{ds['id']}/compilation/status", params={"kind": "graph"}).get("data") or {}
        if float(doc.get("progress") or 0) >= 1 and etat.get("last_completed_at") and not etat.get("backlog") \
                and not etat.get("inflight"):
            break
        if float(doc.get("progress") or 0) < 0:
            break
        time.sleep(5)
    log(f"ingestion et compilation : {time.time() - t0:.0f} s ; document progress={doc.get('progress')} "
        f"passages={doc.get('chunk_count')} ; état {json.dumps(etat, ensure_ascii=False)[:400]}")
    s.pg.reload(); attendre(s, 3000)
    l = ligne(s, DOC_07)
    cap(s, m, "24-analyse-terminee", [(l.locator("td").nth(1), DOC_07), (l.locator("td").nth(4), "Nombre de segments"),
                                     (l.locator("td").nth(6), "Analyser")])


def artefacts_page(s, base):
    ouvrir_base(s, base)
    s.pg.get_by_role("link", name="Artifacts", exact=True).first.click(); attendre(s, 5000)


def choisir_vue(s, vue):
    s.pg.get_by_role("combobox").first.click(); attendre(s, 1000)
    s.pg.get_by_role("option", name=vue, exact=True).click(); attendre(s, 5000)


def compilation_artefacts(s):
    """Onglet « Artifacts » de la base : sélecteur, vue « Graph » remplie, vue d'un autre type vide."""
    m = M07
    ouvrir_base(s, BASE_07)
    lien = s.pg.get_by_role("link", name="Artifacts", exact=True).first
    cap(s, m, "25-onglet-artifacts", [(lien, "Artifacts")])
    lien.click(); attendre(s, 5000)
    sel = s.pg.get_by_role("combobox").first
    sel.click(); attendre(s, 1000)
    o = lambda t: s.pg.get_by_role("option", name=t, exact=True)
    cap(s, m, "26-types-d-artefacts", [(o("Wiki"), "Wiki"), (o("Tree/PageIndex"), "Tree/PageIndex"), (o("Graph"), "Graph"),
                                       (o("Mind map"), "Mind map"), (o("Timeline"), "Timeline")])
    o("Graph").click(); attendre(s, 6000)
    cap(s, m, "27-vue-graph", [(s.pg.get_by_role("combobox").first, "Graph"),
                               (s.pg.get_by_role("combobox").nth(1), "Search entity"),
                               (s.pg.get_by_text(re.compile(r"\d+ / \d+ entities")).first, "entities"),
                               (s.pg.locator("canvas").filter(visible=True).last, "graphe")])
    ent = s.pg.get_by_role("combobox").nth(1)
    ent.click(); attendre(s, 1200)
    cap(s, m, "28-liste-des-entites", [(popover(s), "entités")])
    log("entités du graphe :", popover(s).inner_text().replace("\n", " | "))
    s.pg.keyboard.press("Escape"); attendre(s, 600)
    choisir_vue(s, "Wiki")
    cap(s, m, "29-vue-vide", [(s.pg.get_by_role("combobox").first, "Wiki"),
                              (s.pg.get_by_text(re.compile(r"^No .* yet$")).first, "No wiki yet")])
    ds = next(d for d in api(s, "GET", "/datasets", params={"name": BASE_07})["data"] if d["name"] == BASE_07)
    log("artefact graph (API) :", json.dumps(api(s, "GET", f"/datasets/{ds['id']}/artifacts/structure",
                                                   params={"kind": "graph"}), ensure_ascii=False)[:3000])


# Autres types : un opérateur, un pipeline et une base par type, mêmes gestes que la procédure, sans capture.
AUTRES = [("Wiki", "Wiki"), ("Tree", "Tree/PageIndex"), ("PageIndex", "Tree/PageIndex"), ("Timeline", "Timeline")]


def creer_operateur(s, nom, gabarit):
    s.aller("/agents", 2500)
    s.pg.get_by_role("radio", name="Compilation operator").click(); attendre(s, 2000)
    s.pg.locator("button:has(svg.lucide-plus)").first.click(); attendre(s, 2500)
    s.pg.get_by_placeholder("Veuillez saisir le nom").fill(nom)
    s.pg.get_by_role("combobox").first.click(); attendre(s, 1000)
    s.pg.get_by_role("option", name=gabarit, exact=True).click(); attendre(s, 1500)
    bouton(s, "Enregistrer").click(); attendre(s, 3000)


def creer_pipeline(s, nom, operateur):
    s.aller("/agents", 2500)
    s.pg.get_by_role("radio", name="Ingestion pipeline").click(); attendre(s, 2000)
    s.pg.locator("button:has(svg.lucide-plus)").first.click(); attendre(s, 1200)
    s.pg.get_by_role("menuitem").filter(has_text="Créer depuis un blanc").first.click(); attendre(s, 1500)
    dlg = s.pg.get_by_role("dialog")
    dlg.locator("input").first.fill(nom)
    dlg.get_by_role("button", name="Confirmer").click(); attendre(s, 5000)
    for amont, aval in (("Parser", "Découpeur par tokens"), ("Chunker", "Compiler")):
        etape_suivante(s, amont).get_by_text(aval, exact=True).click(); attendre(s, 1500)
        bouton(s, "Save draft").click(); attendre(s, 2000)
    fermer_panneau(s); fit(s)
    noeud(s, "Compiler").click(); attendre(s, 1500)
    s.pg.get_by_role("combobox").filter(has_text="Sélectionner une valeur").first.click(); attendre(s, 1000)
    s.pg.get_by_role("option", name=operateur).click(); attendre(s, 1200)
    bouton(s, "Save draft").click(); attendre(s, 2000)
    etape_suivante(s, "Compiler").get_by_text("Indexeur", exact=True).click(); attendre(s, 1500)
    bouton(s, "Save draft").click(); attendre(s, 2500)
    bouton(s, "Publier").click(); attendre(s, 1500)
    dlg = s.pg.get_by_role("dialog")
    dlg.get_by_placeholder("Alias").fill("v1")
    dlg.get_by_role("button", name="Confirmer").click(); attendre(s, 3000)


def creer_base_kc(s, nom, pipeline, doc=DOC_07):
    s.aller("/datasets", 2500)
    bouton(s, "Créer une base de connaissances").click(); attendre(s, 1500)
    dlg = s.pg.get_by_role("dialog")
    dlg.get_by_placeholder("Veuillez saisir un nom !").fill(nom)
    dlg.get_by_role("button", name="Enregistrer").click(); attendre(s, 4000)
    s.pg.get_by_role("link", name="Configuration", exact=True).first.click(); attendre(s, 3000)
    mode = s.pg.get_by_role("button").filter(has_text="built in").first
    haut(mode); mode.click(); attendre(s, 1200)
    popover(s).get_by_text(pipeline, exact=True).first.click(); attendre(s, 1200)
    popover(s).get_by_text(re.compile(pipeline + "_")).first.click(); attendre(s, 1500)
    bouton(s, "Enregistrer").click(); attendre(s, 2500)
    s.pg.get_by_role("link", name="Fichiers", exact=True).first.click(); attendre(s, 2500)
    bouton(s, "Ajouter un fichier").click(); attendre(s, 1000)
    s.pg.get_by_role("menuitem").filter(has_text="Téléverser un fichier").first.click(); attendre(s, 1500)
    dlg = s.pg.get_by_role("dialog")
    dlg.locator("input[type=file]").first.set_input_files([CORPUS + doc]); attendre(s, 1500)
    sw = dlg.get_by_role("switch").first
    if sw.get_attribute("aria-checked") != "true":
        sw.click(); attendre(s, 600)
    dlg.get_by_role("button", name="Enregistrer").click(); attendre(s, 3000)


def suivre_compilation(s, nom, limite=600):
    """Attend la fin de l'ingestion puis de la compilation (file vide et last_completed_at, tous types interrogés)."""
    t0 = time.time()
    ds = next(d for d in api(s, "GET", "/datasets", params={"name": nom})["data"] if d["name"] == nom)
    kinds = ("graph", "mindmap", "wiki", "tree", "page_index", "pageindex", "timeline")
    while time.time() - t0 < limite:
        docs = api(s, "GET", f"/datasets/{ds['id']}/documents")["data"]
        doc = (docs.get("docs") if isinstance(docs, dict) else docs)[0]
        etats = {k: api(s, "GET", f"/datasets/{ds['id']}/compilation/status", params={"kind": k}).get("data") or {}
                 for k in kinds}
        faits = {k: e for k, e in etats.items() if e.get("last_completed_at") and not e.get("backlog") and not e.get("inflight")}
        if float(doc.get("progress") or 0) < 0 or (float(doc.get("progress") or 0) >= 1 and faits):
            break
        time.sleep(5)
    if not faits:
        log(f"{nom} : rien de compilé après {time.time() - t0:.0f} s (échec, voir l'onglet « Journaux »)")
    log(f"{nom} : ingestion et compilation {time.time() - t0:.0f} s ; progress={doc.get('progress')} "
        f"passages={doc.get('chunk_count')} ; terminés {json.dumps(faits, ensure_ascii=False)[:500]}")
    return ds


def compilation_autres(s, *quels):
    for gabarit, _ in AUTRES:
        if quels and gabarit not in quels:
            continue
        t0 = time.time()
        creer_operateur(s, f"Manuel-Operateur-{gabarit}", gabarit)
        creer_pipeline(s, f"Manuel-Pipeline-{gabarit}", f"Manuel-Operateur-{gabarit}")
        creer_base_kc(s, f"Manuel-KC-{gabarit}", f"Manuel-Pipeline-{gabarit}")
        ds = suivre_compilation(s, f"Manuel-KC-{gabarit}")
        log(f"{gabarit} : chaîne complète en {time.time() - t0:.0f} s")
        for k in ("wiki", "tree", "page_index", "timeline"):
            r = api(s, "GET", f"/datasets/{ds['id']}/artifacts/structure", params={"kind": k})
            if r.get("data"):
                log(f"artefact {k} (API) :", json.dumps(r, ensure_ascii=False)[:2500])


def compilation_echec(s, relancer=True):
    """Base « Manuel-KC-Wiki » en échec : fichier, onglet « Journaux », détail de la tâche ; analyse relancée une fois."""
    m = M07
    base = "Manuel-KC-Wiki"
    ouvrir_base(s, base)
    l = ligne(s, DOC_07)
    etat = l.locator("[data-testid=document-parse-status] button").last
    etat.hover(); attendre(s, 1200)
    cap(s, m, "30-fichier-en-echec", [(l.locator("td").nth(4), "Nombre de segments"), (etat, "état de l'analyse"),
                                      (l.get_by_test_id("document-parse-toggle"), "relancer l'analyse")])
    s.pg.get_by_role("link", name="Journaux", exact=True).first.click(); attendre(s, 3000)
    t = s.pg.locator("tbody tr").first
    t.hover(); attendre(s, 600)
    oeil = t.locator("td").last.locator("button").first
    cap(s, m, "31-journaux-echec", [(s.pg.get_by_text("Échec", exact=True).last.locator("xpath=.."), "Échec"),
                                    (t.locator("td").nth(3), "Pipeline d'ingestion"),
                                    (t.get_by_text("Failed").first, "Failed"), (oeil, "détail")])
    oeil.click(); attendre(s, 1500)
    dlg = s.pg.get_by_role("dialog").last
    log("détail de la tâche en échec :", dlg.inner_text().replace("\n", " | ")[:1500])
    cap(s, m, "32-detail-de-l-echec", [(dlg.get_by_text("Détails").first.locator("xpath=.."), "Détails")])
    s.pg.keyboard.press("Escape"); attendre(s, 800)
    if not relancer:
        return
    s.pg.get_by_role("link", name="Fichiers", exact=True).first.click(); attendre(s, 2500)
    ligne(s, DOC_07).get_by_test_id("document-parse-toggle").click(); attendre(s, 1500)
    conf = s.pg.get_by_role("alertdialog").or_(s.pg.get_by_role("dialog"))
    if conf.count():  # pas de confirmation pour un fichier en échec : l'analyse repart tout de suite
        conf.last.get_by_role("button").last.click(); attendre(s, 2000)
    log("analyse relancée")
    suivre_compilation(s, base)


def compilation_vues(s):
    """Vues « Tree/PageIndex » et « Timeline » remplies ; carte mentale de la base de démonstration (lecture seule)."""
    m = M07
    artefacts_page(s, "Manuel-KC-Tree")
    choisir_vue(s, "Tree/PageIndex")
    log("vue Tree :", s.pg.locator("body").inner_text()[:1500].replace("\n", " | "))
    arbre = s.pg.get_by_text(re.compile(r"^Navigation tree")).first
    cap(s, m, "33-vue-tree", [(s.pg.get_by_role("combobox").first, "Tree/PageIndex"), (arbre, "Navigation tree"),
                              (s.pg.get_by_placeholder("Rechercher").first, "Rechercher")])
    cible = s.pg.get_by_text(re.compile(r" [0-9a-f]{8}$")).first
    cible.click(); attendre(s, 2500)
    log("détail d'un nœud :", s.pg.locator("body").inner_text()[:2500].replace("\n", " | "))
    cap(s, m, "34-detail-d-un-noeud", [(cible, "nœud de l'arbre"),
                                       (s.pg.get_by_text("Décisions du CSE").last.locator("xpath=.."), "détail")])
    artefacts_page(s, "Manuel-KC-Timeline")
    choisir_vue(s, "Timeline")
    log("vue Timeline :", s.pg.locator("body").inner_text()[:1500].replace("\n", " | "))
    cap(s, m, "35-vue-timeline", [(s.pg.get_by_role("combobox").first, "Timeline"),
                                  (s.pg.get_by_text("14 octobre 2025").first, "14 octobre 2025")])
    artefacts_page(s, DEMO_KC)
    choisir_vue(s, "Mind map")
    cap(s, m, "36-carte-mentale-demo", [(s.pg.get_by_role("combobox").first, "Mind map"),
                                        (s.pg.locator("svg").filter(visible=True).last, "carte mentale")])


def compilation(s, *phases):
    if phases and phases[0] == "autres":
        return compilation_autres(s, *phases[1:])
    if phases == ("echec", "sans-relance"):
        return compilation_echec(s, relancer=False)
    for ph in phases or ("operateur", "pipeline", "base", "configuration", "import", "artefacts", "autres", "echec", "vues"):
        log("== phase", ph)
        globals()["compilation_" + ph](s)


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
            s.pg.screenshot(path=str(ECHEC / "echec-lot3.png"))
            (ECHEC / "echec-lot3.txt").write_text(s.pg.url + "\n" + s.pg.inner_text("body"))
            sys.exit(1)
        finally:
            s.b.close()
