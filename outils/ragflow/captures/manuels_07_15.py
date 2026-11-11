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
    """Ferme le panneau de réglages par sa croix d'en-tête (en haut à droite). Les autres croix du panneau retirent
    un élément (un outil d'un agent, par exemple) : ne jamais les viser."""
    for x in s.pg.locator("svg.lucide-x").filter(visible=True).all():
        b = x.bounding_box()
        if b and b["y"] < 140 and b["x"] > 1300:
            x.click(); attendre(s, 600)
            break
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


# ---------------------------------------------------------------- manuel 08

M08 = "08-agents"
AG_08 = "Manuel-Agent-Documentaire"
BLANC_08 = "Manuel-Agent-Vierge"
IMPORT_08 = "Manuel-Agent-Importe"
MEM_08 = "Manuel-Memoire"
Q_08 = "Qui est le directeur de production de Vélanor ?"
EXPORT_08 = Path("donnees/captures-explorer/agent-exporte.json")


def menu_gestion(s, item):
    bouton(s, "Gestion").click(); attendre(s, 1000)
    return popover(s).get_by_text(item, exact=True)


def agents_liste(s):
    """Page « Agent », onglet « Workflow », menu de création."""
    m = M08
    s.aller("/agents", 2500)
    plus = s.pg.locator("button:has(svg.lucide-plus)").first
    carte = texte(s, "Agent démo Vélanor").locator("xpath=ancestor::div[.//*[contains(text(),'Dernière')]][1]")
    cap(s, m, "01-workflow", [(s.pg.locator("[role=radio]").filter(has_text="Workflow"), "Workflow"),
                              (carte, "Agent démo Vélanor"), (s.pg.get_by_role("searchbox").first, "Rechercher"),
                              (s.pg.locator("button:has(svg.lucide-funnel)").first, "filtre"), (plus, "+")])
    plus.click(); attendre(s, 1200)
    it = lambda x: s.pg.get_by_role("menuitem").filter(has_text=x).first
    cap(s, m, "02-menu-de-creation", [(it("Créer depuis un blanc"), "Créer depuis un blanc"),
                                      (it("Créer depuis un modèle"), "Créer depuis un modèle"),
                                      (it("Importer un fichier JSON"), "Importer un fichier JSON")])
    s.pg.keyboard.press("Escape"); attendre(s, 600)


def agents_modele(s):
    """Agent « Manuel-Agent-Documentaire » créé depuis le gabarit « Your starter dataset chatbot »."""
    m = M08
    s.aller("/agents", 2500)
    s.pg.locator("button:has(svg.lucide-plus)").first.click(); attendre(s, 1200)
    s.pg.get_by_role("menuitem").filter(has_text="Créer depuis un modèle").first.click(); attendre(s, 3000)
    carte = s.pg.get_by_text("Your starter").first.locator("xpath=ancestor::div[.//button or contains(@class,'border')][1]")
    carte.hover(); attendre(s, 800)
    utiliser = carte.get_by_role("button", name="Utiliser").first
    cat = lambda x: s.pg.get_by_role("button", name=x, exact=True).first
    cap(s, m, "03-gabarits", [(cat("Recommandé"), "Recommandé"), (cat("Agent"), "Agent"), (cat("Autre"), "Autre"),
                              (carte, "Your starter dataset chatbot"), (utiliser, "Utiliser")])
    for c in ("Recommandé", "Agent", "Support client", "Marketing", "Application grand public", "Autre"):
        cat(c).click(); attendre(s, 800)
        log(f"catégorie {c} :", " | ".join(x.strip() for x in s.pg.locator("main h3, main [class*=font-semibold]").all_inner_texts()[:20]) or
            s.pg.locator("body").inner_text()[300:900].replace("\n", " | "))
    cat("Recommandé").click(); attendre(s, 800)
    carte.hover(); attendre(s, 600)
    utiliser.click(); attendre(s, 2000)
    dlg = s.pg.get_by_role("dialog")
    nom = dlg.locator("input").first
    nom.fill(AG_08)
    modele = dlg.locator("button").filter(has=s.pg.locator("svg.lucide-chevron-down")).first
    bases = dlg.get_by_role("button").filter(has_text="Sélectionner une valeur")
    cap(s, m, "04-create-workflow", [(nom, "Nom"), (modele, "Modèle"),
                                     (dlg.get_by_text("This template contains", exact=False), "message du gabarit"),
                                     (bases, "Bases de connaissances")])
    modele.click(); attendre(s, 1000)
    g = s.pg.get_by_text("gemma4:e4b").last
    cap(s, m, "05-choix-du-modele", [(g, "gemma4:e4b")])
    g.click(); attendre(s, 800)
    bases.click(); attendre(s, 1000)
    dv = s.pg.get_by_text("Démo Vélanor").last
    cap(s, m, "06-choix-de-la-base", [(dv, "Démo Vélanor")])
    dv.click(); attendre(s, 800); s.pg.keyboard.press("Escape"); attendre(s, 500)
    cap(s, m, "07-workflow-rempli", [(dlg.locator("button").filter(has_text="gemma4").first, "Modèle"),
                                     (dlg.get_by_text("Démo Vélanor").first, "Bases de connaissances"),
                                     (dlg.get_by_role("button", name="Confirmer"), "Confirmer")])
    dlg.get_by_role("button", name="Confirmer").click(); attendre(s, 6000)
    log("agent créé :", s.pg.url.replace(URL, ""))


def agents_canevas(s):
    """Canevas de l'agent : blocs et panneaux de réglages."""
    m = M08
    ouvrir_agent(s, None, AG_08)
    fit(s)
    outil = s.pg.locator(".react-flow__node-toolNode").first
    cap(s, m, "08-canevas", [(noeud(s, "Commencer"), "Commencer"), (s.pg.locator(".react-flow__node-agentNode").first, "Docs QA Agent"),
                             (outil, "Retrieval"), (s.pg.locator(".react-flow__node-messageNode").first, "Message_0"),
                             (s.pg.locator(".react-flow__node-noteNode").first, "note")])
    cap(s, m, "09-barre-du-canevas", [(bouton(s, "Save draft"), "Save draft"), (bouton(s, "Exécuter"), "Exécuter"),
                                      (bouton(s, "Lancer"), "Lancer"), (bouton(s, "Publier"), "Publier"), (bouton(s, "Gestion"), "Gestion")])
    noeud(s, "Commencer").click(); attendre(s, 1500)
    lab = lambda x: s.pg.locator("label").filter(has_text=x).first
    cap(s, m, "10-commencer", [(lab("Mode"), "Mode"), (lab("Activation de l'accueil"), "Activation de l'accueil"),
                               (lab("Message de bienvenue"), "Message de bienvenue"), (bouton(s, "Entrée"), "Entrée")])
    fermer_panneau(s); fit(s)
    s.pg.locator(".react-flow__node-agentNode").first.click(); attendre(s, 1500)
    cap(s, m, "11-agent", [(lab("Modèle"), "Modèle"), (lab("Invite système"), "Invite système"),
                           (s.pg.locator("button:has(svg.lucide-circle-play)").first, "essai du bloc")])
    outils = bouton(s, "Ajouter des outils")
    haut(lab("Invite utilisateur"))
    cap(s, m, "12-agent-suite", [(lab("Invite utilisateur"), "Invite utilisateur"), (outils, "Ajouter des outils"),
                                 (bouton(s, "Ajouter un agent"), "Ajouter un agent"), (bouton(s, "Paramètres avancés"), "Paramètres avancés")])
    if not lab("Afficher les citations").is_visible():  # dépliant ouvert par défaut
        bouton(s, "Paramètres avancés").click(); attendre(s, 800)
    haut(lab("Afficher les citations"))
    cap(s, m, "13-agent-parametres-avances", [
        (lab("Afficher les citations"), "Afficher les citations"), (lab("Nombre maximum de cycles"), "Nombre maximum de cycles de réflexion"),
        (lab("Taille de la fenêtre"), "Taille de la fenêtre d'historique des messages"),
        (lab("Nombre maximum de tentatives"), "Nombre maximum de tentatives"), (lab("Méthode d'exception"), "Méthode d'exception")])
    outils.scroll_into_view_if_needed(); outils.click(); attendre(s, 1200)
    log("outils proposés :", popover(s).inner_text().replace("\n", " | ")[:1500])
    pop = popover(s)
    cap(s, m, "14-ajouter-des-outils", [(pop.get_by_text("Intégré", exact=True), "Intégré"), (pop.get_by_text("MCP", exact=True), "MCP"),
                                        (pop.locator("input").first, "recherche"), (pop.get_by_text("DuckDuckGo", exact=True), "DuckDuckGo")])
    s.pg.keyboard.press("Escape"); attendre(s, 600)
    fermer_panneau(s); fit(s)
    s.pg.locator(".react-flow__node-toolNode").first.locator("section").last.click(); attendre(s, 1500)
    cap(s, m, "15-retrieval", [(lab("Récupération depuis"), "Récupération depuis"),
                               (s.pg.get_by_role("button").filter(has_text="Démo Vélanor").first, "Démo Vélanor"),
                               (bouton(s, "Paramètres avancés"), "Paramètres avancés")])
    if not lab("Seuil de similarité").is_visible():
        bouton(s, "Paramètres avancés").click(); attendre(s, 800)
    haut(lab("Seuil de similarité"))
    cap(s, m, "16-retrieval-avance", [(lab("Seuil de similarité"), "Seuil de similarité"),
                                      (lab("Poids de similarité par mots-clés"), "Poids de similarité par mots-clés"),
                                      (lab("Top N"), "Top N"), (lab("Modèle de réordonnancement"), "Modèle de réordonnancement"),
                                      (lab("Métadonnées"), "Métadonnées")])
    fermer_panneau(s); fit(s)
    s.pg.locator(".react-flow__node-messageNode").first.click(); attendre(s, 1500)
    cap(s, m, "17-message", [(lab("Messages"), "Messages"), (bouton(s, "Ajouter un message"), "Ajouter un message"),
                             (lab("Type de fichier"), "Type de fichier à télécharger"),
                             (lab("Lecture automatique audio"), "Lecture automatique audio"), (lab("Enregistrer en mémoire"), "Enregistrer en mémoire")])
    fermer_panneau(s)
    bouton(s, "Save draft").click(); attendre(s, 2000)


def agents_essai(s):
    """« Exécuter » (essai dans le canevas), « Lancer » (conversation), « Publier »."""
    m = M08
    ouvrir_agent(s, None, AG_08)
    bouton(s, "Exécuter").click(); attendre(s, 2500)
    zone = s.pg.get_by_placeholder("Saisissez votre message ici...").last
    zone.fill(Q_08)
    cap(s, m, "18-executer", [(zone, "question"), (s.pg.get_by_role("button", name="Send message").last, "Send message")])
    t0 = time.time()
    s.pg.get_by_role("button", name="Send message").last.click()
    s.pg.get_by_text(re.compile("Julien Moreau|not found|ne trouve", re.I)).last.wait_for(timeout=180000)
    attendre(s, 3000)
    log(f"réponse dans « Exécuter » en {time.time() - t0:.1f} s (relevé à l'apparition du nom)")
    log("panneau d'essai :", s.pg.locator("body").inner_text()[-2500:].replace("\n", " | "))
    rep = s.pg.get_by_text(re.compile("Julien Moreau")).last
    cap(s, m, "19-reponse-executer", [(rep, "réponse")])
    s.pg.keyboard.press("Escape"); attendre(s, 800)
    fermer_panneau(s)
    bouton(s, "Lancer").click(); attendre(s, 3000)
    plus = s.pg.locator("button:has(svg.lucide-plus)").first
    cap(s, m, "20-lancer", [(s.pg.get_by_text("Sessions", exact=True).first, "Sessions"), (plus, "+"),
                            (s.pg.get_by_placeholder("Rechercher des sessions").first, "Rechercher des sessions"),
                            (s.pg.get_by_placeholder("Saisissez votre message ici...").last, "zone de saisie")])
    zone = s.pg.get_by_placeholder("Saisissez votre message ici...").last
    zone.fill("Quel est le plafond des pénalités de retard du contrat Batterix ?")
    t0 = time.time()
    zone.press("Enter")
    s.pg.get_by_text(re.compile(r"8 ?%")).last.wait_for(timeout=180000)
    attendre(s, 3000)
    log(f"réponse dans « Lancer » en {time.time() - t0:.1f} s")
    agents_conversation(s)


def agents_conversation(s):
    """Conversation de « Lancer » relue (session existante), puis « Publier » et « Historique des versions »."""
    m = M08
    if "/explore" not in s.pg.url:
        ouvrir_agent(s, None, AG_08)
        bouton(s, "Lancer").click(); attendre(s, 3000)
    session = s.pg.get_by_text("Quel est le plafond des pénalités", exact=False).first
    session.click(); attendre(s, 2500)
    log("conversation :", s.pg.locator("body").inner_text()[:2500].replace("\n", " | "))
    cap(s, m, "21-conversation", [(session, "session"), (s.pg.get_by_text(re.compile(r"capped at 8 ?%")).last, "réponse")])
    ouvrir_agent(s, None, AG_08)
    bouton(s, "Publier").click(); attendre(s, 1500)
    dlg = s.pg.get_by_role("dialog")
    alias = dlg.get_by_placeholder("Alias")
    alias.fill("v1")
    cap(s, m, "22-publier", [(alias, "Alias"), (dlg.get_by_role("button", name="Confirmer"), "Confirmer")])
    dlg.get_by_role("button", name="Confirmer").click(); attendre(s, 3000)
    menu_gestion(s, "Historique des versions").click(); attendre(s, 2000)
    dlg = s.pg.get_by_role("dialog").last
    log("historique :", dlg.inner_text().replace("\n", " | ")[:600])
    cap(s, m, "23-historique-des-versions", [(dlg.get_by_text(re.compile("v1")).first, "version v1"),
                                             (dlg.locator("button:has(svg.lucide-arrow-down-to-line)"), "télécharger"),
                                             (dlg.locator("button:has(svg.lucide-rotate-ccw)"), "restaurer"),
                                             (dlg.locator("button:has(svg.lucide-trash)"), "supprimer")])
    s.pg.keyboard.press("Escape"); attendre(s, 800)


def agents_gestion(s):
    """Menu « Gestion » : variables, paramètres, intégration, export."""
    m = M08
    ouvrir_agent(s, None, AG_08)
    bouton(s, "Gestion").click(); attendre(s, 1000)
    pop = popover(s)
    cap(s, m, "24-menu-gestion", [(pop.get_by_text(x, exact=True), x) for x in
                                  ("Variable de conversation", "Historique des versions", "Exporter", "Paramètres", "Intégrer dans la page web")])
    pop.get_by_text("Variable de conversation", exact=True).click(); attendre(s, 1500)
    cap(s, m, "25-variables", [(bouton(s, "Ajouter"), "Ajouter")])
    s.pg.keyboard.press("Escape"); attendre(s, 800); fermer_panneau(s)
    menu_gestion(s, "Paramètres").click(); attendre(s, 1500)
    lab = lambda x: s.pg.locator("label").filter(has_text=x).first
    cap(s, m, "26-parametres", [(lab("Titre"), "Titre"), (lab("Photo"), "Photo"), (lab("Description"), "Description"),
                                (lab("Autorisations"), "Autorisations"), (bouton(s, "Enregistrer"), "Enregistrer")])
    s.pg.keyboard.press("Escape"); attendre(s, 800); fermer_panneau(s)
    menu_gestion(s, "Intégrer dans la page web").click(); attendre(s, 2000)
    dlg = s.pg.get_by_role("dialog").last
    jetons = [c for c in dlg.locator("input:visible, textarea:visible, pre:visible, code:visible").all()
              if re.search(r"(auth|token|ragflow-)[=:\w-]{8,}", c.input_value() if c.evaluate("e => 'value' in e") else c.inner_text())]
    cap(s, m, "27-integrer", [(dlg.get_by_role("tab", name="Embed Setup"), "Embed Setup"),
                              (dlg.get_by_role("tab", name="Widget Customization"), "Widget Customization"),
                              (lab("Type d'intégration"), "Type d'intégration"), (lab("Paramètres régionaux"), "Paramètres régionaux"),
                              (dlg.get_by_role("button", name="Ouvrir dans un nouvel onglet"), "Ouvrir dans un nouvel onglet")],
        masques=jetons)
    caviarder(m, "27-integrer")
    s.pg.keyboard.press("Escape"); attendre(s, 800); fermer_panneau(s)
    bouton(s, "Gestion").click(); attendre(s, 1000)
    with s.pg.expect_download() as dl:
        popover(s).get_by_text("Exporter", exact=True).click()
    d = dl.value
    EXPORT_08.parent.mkdir(parents=True, exist_ok=True)
    d.save_as(str(EXPORT_08))
    log("export :", d.suggested_filename, EXPORT_08.stat().st_size, "octets ; clés :", list(json.loads(EXPORT_08.read_text()).keys())[:10])


def agents_json(s):
    """« Importer un fichier JSON » avec le fichier exporté."""
    m = M08
    s.aller("/agents", 2500)
    s.pg.locator("button:has(svg.lucide-plus)").first.click(); attendre(s, 1200)
    s.pg.get_by_role("menuitem").filter(has_text="Importer un fichier JSON").first.click(); attendre(s, 1500)
    dlg = s.pg.get_by_role("dialog")
    dlg.locator("input").first.fill(IMPORT_08)
    dlg.locator("input[type=file]").set_input_files(str(EXPORT_08)); attendre(s, 1200)
    cap(s, m, "28-importer-json", [(dlg.locator("input").first, "Nom"), (dlg.get_by_text("DSL").first, "DSL"),
                                   (dlg.get_by_text(EXPORT_08.name).first, EXPORT_08.name),
                                   (dlg.get_by_role("button", name="Enregistrer"), "Enregistrer")])
    dlg.get_by_role("button", name="Enregistrer").click(); attendre(s, 5000)
    log("après import :", s.pg.url.replace(URL, ""))
    s.aller("/agents", 2500)
    cap(s, m, "29-agent-importe", [(texte(s, IMPORT_08).locator("xpath=ancestor::div[.//*[contains(text(),'Dernière')]][1]"), IMPORT_08)])


def agents_blanc(s):
    """« Créer depuis un blanc » et ajout d'un bloc par le menu « Étape suivante »."""
    m = M08
    s.aller("/agents", 2500)
    s.pg.locator("button:has(svg.lucide-plus)").first.click(); attendre(s, 1200)
    s.pg.get_by_role("menuitem").filter(has_text="Créer depuis un blanc").first.click(); attendre(s, 1500)
    dlg = s.pg.get_by_role("dialog"); dlg.locator("input").first.fill(BLANC_08)
    dlg.get_by_role("button", name="Confirmer").click(); attendre(s, 5000)
    fit(s)
    menu = etape_suivante(s, "Commencer")
    t = lambda x: menu.get_by_text(x, exact=True).first
    log("blocs proposés :", menu.inner_text().replace("\n", " | "))
    cap(s, m, "30-menu-des-blocs", [(poignee(s, "Commencer"), "+"), (t("Fondation"), "Fondation"), (t("Agent"), "Agent"),
                                    (t("Flux"), "Flux"), (t("Manipulation des données"), "Manipulation des données"), (t("Outils"), "Outils")])
    t("Récupération").click(); attendre(s, 1500)
    bouton(s, "Save draft").click(); attendre(s, 2000)
    fermer_panneau(s); fit(s)
    cap(s, m, "31-bloc-ajoute", [(noeud(s, "Commencer"), "Commencer"), (s.pg.locator(".react-flow__node").nth(1), "Récupération")])


def agents_memoire(s):
    """Page « Mémoire » : création de « Manuel-Memoire » ; liaison au bloc Message de l'agent ; contenu après une question."""
    m = M08
    s.aller("/memories", 2500)
    plus = s.pg.get_by_text("Aucune mémoire créée pour le moment").locator("xpath=..").locator("svg").last
    cap(s, m, "32-memoire-vide", [(s.pg.get_by_text("Aucune mémoire créée pour le moment"), "Aucune mémoire créée pour le moment"),
                                  (plus, "+")])
    plus.click(); attendre(s, 1500)
    dlg = s.pg.get_by_role("dialog")
    dlg.get_by_placeholder("nom de la mémoire").fill(MEM_08)
    lab = lambda x: dlg.locator("label").filter(has_text=x).first
    cap(s, m, "33-creer-une-memoire", [(dlg.get_by_placeholder("nom de la mémoire"), "Nom"), (lab("Type de mémoire"), "Type de mémoire"),
                                       (lab("Modèle d'embedding"), "Modèle d'embedding"), (lab("LLM"), "LLM"),
                                       (dlg.get_by_role("button", name="Confirmer"), "Confirmer")])
    dlg.get_by_role("button").filter(has_text="brut").click(); attendre(s, 1000)
    o = lambda x: s.pg.get_by_role("option", name=x, exact=True)
    cap(s, m, "34-types-de-memoire", [(o("(Tout sélectionner)"), "(Tout sélectionner)"), (o("brut"), "brut"),
                                      (o("sémantique"), "sémantique"), (o("épisodique"), "épisodique"),
                                      (o("procédural"), "procédural"), (o("Fermer"), "Fermer")])
    o("Fermer").click(); attendre(s, 600)
    dlg.get_by_role("button", name="Confirmer").click(); attendre(s, 3000)
    log("après création de la mémoire :", s.pg.url.replace(URL, ""), s.pg.locator("body").inner_text()[:600].replace("\n", " | "))
    s.aller("/memories", 2500)
    carte = texte(s, MEM_08)
    cap(s, m, "35-memoire-creee", [(carte, MEM_08)])
    agents_memoire_page(s)


def ouvrir_memoire(s):
    s.aller("/memories", 2500)
    texte(s, MEM_08).click(); attendre(s, 3000)


def agents_memoire_page(s):
    m = M08
    ouvrir_memoire(s)
    log("page de la mémoire :", s.pg.url.replace(URL, ""), s.pg.locator("body").inner_text()[:1500].replace("\n", " | "))
    lien = lambda x: s.pg.get_by_role("link", name=x, exact=True).or_(s.pg.get_by_role("button", name=x, exact=True)).first
    cap(s, m, "36-page-de-la-memoire", [(lien("Messages"), "Messages"), (lien("Configuration"), "Configuration"),
                                        (s.pg.locator("th").filter(has_text="ID de session").first, "ID de session"),
                                        (s.pg.get_by_text("Aucune donnée disponible").first, "Aucune donnée disponible")])
    lien("Configuration").click(); attendre(s, 2500)
    log("configuration de la mémoire :", s.pg.locator("body").inner_text()[:2500].replace("\n", " | "))
    labs = [l for l in s.pg.locator("main label, label").all() if l.is_visible() and l.inner_text().strip()][:6]
    cap(s, m, "37-configuration-de-la-memoire", [(l, l.inner_text().strip()) for l in labs])


def agents_memoire_agent(s):
    """Bloc Message de l'agent relié à la mémoire, question posée par « Lancer », messages de la mémoire."""
    m = M08
    ouvrir_agent(s, None, AG_08)
    fit(s)
    s.pg.locator(".react-flow__node-messageNode").first.click(); attendre(s, 1500)
    champ = s.pg.locator("label").filter(has_text="Enregistrer en mémoire").first.locator("xpath=following::button[1]")
    champ.click(); attendre(s, 1000)
    choix = s.pg.get_by_text(MEM_08, exact=True).last
    cap(s, m, "38-enregistrer-en-memoire", [(choix, MEM_08)])
    choix.click(); attendre(s, 800)
    s.pg.keyboard.press("Escape"); attendre(s, 500)
    log("champ mémoire :", champ.inner_text())
    fermer_panneau(s)
    bouton(s, "Save draft").click(); attendre(s, 2000)
    bouton(s, "Lancer").click(); attendre(s, 3000)
    s.pg.locator("button:has(svg.lucide-plus)").first.click(); attendre(s, 1500)
    zone = s.pg.get_by_placeholder("Saisissez votre message ici...").last
    zone.fill("Combien de salariés compte Vélanor au 31 décembre 2025 ?")
    zone.press("Enter")
    s.pg.get_by_text(re.compile(r"412")).last.wait_for(timeout=180000)
    attendre(s, 3000)
    log("réponse avec mémoire :", s.pg.locator("body").inner_text()[-1200:].replace("\n", " | "))
    t0 = time.time()
    while time.time() - t0 < 300:
        ouvrir_memoire(s)
        if not s.pg.get_by_text("Aucune donnée disponible").count():
            break
        time.sleep(10)
    log(f"messages de la mémoire après {time.time() - t0:.0f} s :", s.pg.locator("body").inner_text()[:2500].replace("\n", " | "))
    ligne1 = s.pg.locator("tbody tr").first
    cap(s, m, "39-messages-de-la-memoire", [(ligne1, "message mémorisé"),
                                           (s.pg.locator("th").filter(has_text="Type").first, "Type"),
                                           (s.pg.locator("th").filter(has_text="Oublier").first, "Oublier le")])


def agents_mcp(s):
    """Menu du compte, « MCP » : page et fenêtre « Ajouter MCP » (non enregistrée)."""
    m = M08
    s.aller("/", 2000)
    s.pg.locator("header a").filter(has_text="BR").first.click(); attendre(s, 3000)
    bouton(s, "MCP").click(); attendre(s, 2500)
    cap(s, m, "40-serveurs-mcp", [(bouton(s, "MCP"), "MCP"), (s.pg.get_by_placeholder("Rechercher").first, "Rechercher"),
                                  (bouton(s, "Gestion en masse"), "Gestion en masse"), (bouton(s, "Importer"), "Importer"),
                                  (bouton(s, "Ajouter MCP"), "Ajouter MCP")])
    bouton(s, "Ajouter MCP").click(); attendre(s, 1500)
    dlg = s.pg.get_by_role("dialog").last
    log("fenêtre Ajouter MCP :", dlg.inner_text().replace("\n", " | "))
    labs = dlg.locator("label").all()[:5]
    cap(s, m, "41-ajouter-mcp", [(l, l.inner_text().strip() or "champ") for l in labs if l.is_visible()][:5]
        + [(dlg.get_by_role("button").last, dlg.get_by_role("button").last.inner_text().strip() or "bouton")])
    s.pg.keyboard.press("Escape"); attendre(s, 800)


def agents(s, *phases):
    for ph in phases or ("liste", "modele", "canevas", "essai", "gestion", "json", "blanc", "memoire", "memoire_agent", "mcp"):
        log("== phase", ph)
        globals()["agents_" + ph](s)


# ---------------------------------------------------------------- manuel 09

M09 = "09-sources-externes"
SRC_09 = "Manuel-Source-Sitemap"
BASE_09 = "Manuel-Sources"
SITEMAP_09 = "http://rag-site-test/sitemap.xml"


def page_compte(s, entree):
    s.aller("/", 2000)
    s.pg.locator("header a").filter(has_text="BR").first.click(); attendre(s, 3000)
    bouton(s, entree).click(); attendre(s, 2500)


def carte_source(s, nom):
    return s.pg.get_by_text(nom, exact=True).first.locator("xpath=ancestor::article[1]")


def sources_ajout(s):
    """« Sources de données » : liste, ajout d'une source Sitemap vers le site local, test refusé, enregistrement."""
    m = M09
    page_compte(s, "Sources de données")
    cap(s, m, "01-sources-de-donnees", [
        (bouton(s, "Sources de données"), "Sources de données"),
        (s.pg.get_by_text("Aucune source de données ajoutée", exact=False).first, "Aucune source de données ajoutée"),
        (s.pg.get_by_text("Sources disponibles").filter(visible=True).first, "Sources disponibles"),
        (carte_source(s, "Confluence"), "Confluence")])
    log("sources disponibles :", " | ".join(s.pg.locator("article h3").all_inner_texts()))
    carte = carte_source(s, "Sitemap")
    centre(carte); carte.hover(); attendre(s, 800)
    ajout = carte.get_by_role("button").filter(has_text="Ajouter").first
    cap(s, m, "02-carte-sitemap", [(carte, "Sitemap"), (ajout, "Ajouter")])
    ajout.click(); attendre(s, 2000)
    dlg = s.pg.get_by_role("dialog").last
    dlg.get_by_placeholder("name").or_(dlg.locator("input[name=name]")).first.fill(SRC_09)
    url = dlg.get_by_placeholder("https://example.com/sitemap.xml")
    url.fill(SITEMAP_09)
    lab = lambda x: dlg.locator("label").filter(has_text=x).first
    cap(s, m, "03-ajout-sitemap", [(lab("Name"), "Name"), (url, "URL du sitemap"), (lab("Filtre"), "Filtre d'URL (regex)"),
                                   (lab("Suivre les liens PDF"), "Suivre les liens PDF"),
                                   (dlg.get_by_role("button", name="Test connection"), "Test connection"),
                                   (dlg.get_by_role("button", name="Confirmer"), "Confirmer")])
    with s.pg.expect_response(lambda r: "/connectors/" in r.url and r.url.endswith("/test")) as rep:
        dlg.get_by_role("button", name="Test connection").click()
    log("test du connecteur (réponse de l'API) :", rep.value.status, rep.value.text()[:300])
    msg = s.pg.get_by_text(re.compile("non-public")).last
    msg.wait_for(state="visible", timeout=8000)
    log("message affiché :", msg.inner_text())
    cap(s, m, "04-test-refuse", [(msg, "message de refus"), (dlg.get_by_role("button", name="Test connection"), "Test connection")])
    dlg.get_by_role("button", name="Confirmer").click(); attendre(s, 3000)
    log("après Confirmer :", s.pg.locator("body").inner_text()[:900].replace("\n", " | "))
    sources_detail(s)


def sources_detail(s):
    """Source enregistrée : ligne de la liste, roue dentée (réglages et journal)."""
    m = M09
    page_compte(s, "Sources de données")
    nom = s.pg.get_by_text(SRC_09, exact=True).first
    rangee = nom.locator("xpath=ancestor::div[.//button][1]")
    roue = rangee.locator("button:has(svg.lucide-settings)").first
    corb = rangee.locator("button:has(svg.lucide-trash-2), button:has(svg.lucide-trash)").first
    cap(s, m, "05-source-ajoutee", [(texte(s, "Sitemap"), "Sitemap"), (nom, SRC_09), (roue, "réglages"), (corb, "supprimer")])
    roue.click(); attendre(s, 3000)
    log("réglages de la source :", s.pg.url.replace(URL, ""), s.pg.locator("body").inner_text()[:2500].replace("\n", " | "))
    labs = [l for l in s.pg.locator("label").all() if l.is_visible() and l.inner_text().strip()][:6]
    cap(s, m, "06-detail-de-la-source", [(l, l.inner_text().strip()) for l in labs])
    freq = s.pg.locator("label").filter(has_text="Refresh Freq").first
    haut(freq)
    cap(s, m, "07-frequence-et-journal", [(freq, "Refresh Freq"), (s.pg.locator("label").filter(has_text="Timeout Secs").first, "Timeout Secs"),
                                          (bouton(s, "Test connection"), "Test connection"), (bouton(s, "Enregistrer"), "Enregistrer"),
                                          (s.pg.get_by_text("Journal", exact=True).first, "Journal")])


def sources_liaison(s):
    """Base « Manuel-Sources » liée à la source par « Lier une source de données » ; synchronisation refusée."""
    m = M09
    s.aller("/datasets", 2500)
    bouton(s, "Créer une base de connaissances").click(); attendre(s, 1500)
    dlg = s.pg.get_by_role("dialog")
    dlg.get_by_placeholder("Veuillez saisir un nom !").fill(BASE_09)
    dlg.get_by_role("button", name="Enregistrer").click(); attendre(s, 4000)
    s.pg.get_by_role("link", name="Configuration", exact=True).first.click(); attendre(s, 3000)
    lier = bouton(s, "Lier une source de données")
    centre(lier)
    cap(s, m, "08-lier-une-source", [(lier, "Lier une source de données"), (bouton(s, "Enregistrer"), "Enregistrer")])
    lier.click(); attendre(s, 1500)
    dlg = s.pg.get_by_role("dialog").last
    log("fenêtre de liaison :", dlg.inner_text().replace("\n", " | ")[:800])
    choix = dlg.get_by_text(SRC_09, exact=False).first
    cap(s, m, "09-choix-de-la-source", [(choix, SRC_09), (dlg.get_by_role("button").last, dlg.get_by_role("button").last.inner_text().strip() or "valider")])
    choix.click(); attendre(s, 800)
    dlg.get_by_role("button").last.click(); attendre(s, 2000)
    log("après liaison :", s.pg.locator("body").inner_text()[-1500:].replace("\n", " | "))
    lie = s.pg.get_by_text(SRC_09, exact=False).last
    centre(lie)
    cap(s, m, "10-source-liee", [(lie.locator("xpath=.."), SRC_09), (bouton(s, "Enregistrer"), "Enregistrer")])
    bouton(s, "Enregistrer").click(); attendre(s, 3000)
    t0 = time.time()
    while time.time() - t0 < 180:
        ouvrir_base(s, BASE_09, "Journaux")
        bouton(s, "Data source").click(); attendre(s, 2500)
        if s.pg.locator("tbody tr").count() and "Aucun" not in s.pg.locator("tbody").inner_text():
            break
        time.sleep(15)
    log(f"journal « Data source » après {time.time() - t0:.0f} s :", s.pg.locator("body").inner_text()[:2500].replace("\n", " | "))
    l = s.pg.locator("tbody tr").first
    cap(s, m, "11-journal-data-source", [(bouton(s, "Data source"), "Data source"), (l, "synchronisation")])
    oeil = l.locator("td").last.locator("button").first
    if oeil.count():
        l.hover(); oeil.click(); attendre(s, 1500)
        dlg = s.pg.get_by_role("dialog").last
        log("détail de la synchronisation :", dlg.inner_text().replace("\n", " | ")[:2500])
        cap(s, m, "12-detail-de-la-synchronisation", [(dlg.get_by_text("Détails").first.locator("xpath=.."), "Détails")])
        s.pg.keyboard.press("Escape"); attendre(s, 800)
    s.pg.get_by_role("link", name="Fichiers", exact=True).first.click(); attendre(s, 2500)
    cap(s, m, "13-base-vide", [(texte(s, BASE_09), BASE_09), (s.pg.locator("tbody").first, "aucun fichier")])


def sources_journaux(s):
    """Journal « Data source » de la base, puis journal de la source (échec de synchronisation)."""
    m = M09
    ouvrir_base(s, BASE_09, "Journaux")
    bouton(s, "Data source").click(); attendre(s, 2500)
    log("journal « Data source » de la base :", s.pg.locator("main, body").first.inner_text()[-800:].replace("\n", " | "))
    cap(s, m, "11-journal-data-source", [(bouton(s, "Data source"), "Data source"), (s.pg.locator("tbody").first, "tâches"),
                                         (s.pg.get_by_text(re.compile(r"^Total")).last, "Total")])
    page_compte(s, "Sources de données")
    rangee = s.pg.get_by_text(SRC_09, exact=True).first.locator("xpath=ancestor::div[.//button][1]")
    rangee.locator("button:has(svg.lucide-settings)").first.click(); attendre(s, 3000)
    j = s.pg.get_by_text("Journal", exact=True).first
    haut(j); attendre(s, 600)
    log("journal de la source :", s.pg.locator("body").inner_text()[-1200:].replace("\n", " | "))
    l = s.pg.locator("tbody tr").first
    cap(s, m, "12-journal-de-la-source", [(j, "Journal"), (l, "synchronisation"),
                                          (l.get_by_text(re.compile("non-public")).first if l.get_by_text(re.compile("non-public")).count() else l.locator("td").last, "Summary")])


def sources_canaux(s):
    """« Canaux de chat » : liste et fenêtre d'ajout Telegram, refermée sans enregistrer."""
    m = M09
    page_compte(s, "Canaux de chat")
    log("canaux disponibles :", " | ".join(s.pg.locator("article h3").all_inner_texts()))
    cap(s, m, "14-canaux-de-chat", [(bouton(s, "Canaux de chat"), "Canaux de chat"),
                                    (carte_source(s, "Discord"), "Discord"), (carte_source(s, "Telegram"), "Telegram"),
                                    (carte_source(s, "WhatsApp"), "WhatsApp")])
    carte = carte_source(s, "Telegram")
    carte.hover(); attendre(s, 800)
    carte.get_by_role("button").filter(has_text="Ajouter").first.click(); attendre(s, 2000)
    dlg = s.pg.get_by_role("dialog").last
    log("fenêtre Telegram :", dlg.inner_text().replace("\n", " | "))
    labs = [l for l in dlg.locator("label").all() if l.is_visible() and l.inner_text().strip()][:5]
    cap(s, m, "15-ajout-telegram", [(l, l.inner_text().strip()) for l in labs])
    annuler = dlg.get_by_role("button", name="Annuler")
    (annuler if annuler.count() else dlg.locator("button:has(svg.lucide-x)").first).click(); attendre(s, 800)


def sources(s, *phases):
    for ph in phases or ("ajout", "liaison", "journaux", "canaux"):
        log("== phase", ph)
        globals()["sources_" + ph](s)


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
