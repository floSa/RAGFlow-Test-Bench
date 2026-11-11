"""Captures du reranker (chapitres 03 et 08) et reprise de la capture du chapitre 04, étape 15.

Scénarios (tout à la souris ; objets d'essai nommés « Manuel-… », supprimés ensuite par outils/ragflow/nettoyer_manuel.py ;
le jeu de démonstration n'est qu'ouvert ou relié, jamais modifié) :
- reperage : relevés sans capture (donnees/captures-explorer/) ;
- brancher : fournisseur « VLLM » › « Add instance » « llm-service-rerank » (http://vllm-rerank:8000/v1, service
  vllm-rerank de LLM-Service, outils/ragflow/reranker.sh), « Lister les modèles », doublon BAAI/bge-reranker-v2-m3
  retiré, « Enregistrer » ; type « Rerank » vérifié sur la carte enregistrée ;
- defaut : « Définir les modèles par défaut » › « Modèle de rerank » › bge-reranker-v2-m3 ;
- assistant : assistant « Manuel-Reranker » relié à « Démo Vélanor », réglages conseillés, « Modèle de réordonnancement »
  choisi, enregistré, question Q30 posée ;
- choix_base : capture 02-prise-en-main/18-choix-base refaite avec une pastille sur « Fermer » (base
  « Manuel-Prise-en-main » préparée par outils/ragflow/reranker_preparer.py base04, assistant « Manuel-Assistant » créé à
  la souris comme au chapitre 04).
Usage : outils/communs/captures/lancer.sh outils/ragflow/captures/reranker.py <scénario> [...]
"""
import re
import sys
import traceback
from pathlib import Path

from playwright.sync_api import sync_playwright

from captures import Session, cap, bouton, texte  # noqa: F401
from manuels_03_06 import attendre, popover, haut, centre, ouvrir_assistant, panneau, envoyer, Q30, VIDE_05  # noqa: F401
from manuels_03_06 import deplier as deplier_section
from manuels_07_15 import log
from manuels_10_14 import toasts
from relecture_novice import releve
from relecture_novice_2 import fournisseur, deplier

ECHEC = Path("donnees/captures-explorer")
M03, M04, M08 = "01-installation", "02-prise-en-main", "05-assistants-et-citations"
INSTANCE, URL_RERANK, MODELE = "llm-service-rerank", "http://vllm-rerank:8000/v1", "bge-reranker-v2-m3"
CHAT = "Manuel-Reranker"


def connecte(s):
    s.connexion(); s.francais()


def carte_instance(s):
    titre = s.pg.locator(f":text-is('{INSTANCE}')").first
    return titre, deplier(s, titre)


def brancher(s):
    connecte(s)
    fournisseur(s, "VLLM")
    if s.pg.locator(f":text-is('{INSTANCE}')").count():
        raise RuntimeError(f"{INSTANCE} existe déjà")
    ajout = s.pg.get_by_role("button", name="Add instance")
    ajout.scroll_into_view_if_needed(); ajout.click(); attendre(s, 2000)
    nom = s.pg.get_by_placeholder("Please input instance name")
    nom.evaluate("e => e.scrollIntoView({block: 'start'})"); attendre(s, 800)
    nom.fill(INSTANCE)
    url = s.pg.get_by_placeholder("http://host.docker.internal:8000/v1").last
    url.fill(URL_RERANK)
    lister = s.pg.get_by_role("button", name="Lister les modèles").last
    lister.click(); attendre(s, 5000)
    carte = nom.locator("xpath=ancestor::*[.//button[normalize-space()='Enregistrer']][1]")
    contenu = carte.inner_text().replace("\n", " | ")
    log("modèles listés :", contenu[:600])
    garde = carte.locator(f":text-is('{MODELE}')").first
    rang = garde.locator("xpath=ancestor::*[.//button[starts-with(@aria-label, 'Remove')]][1]")
    log("ligne du modèle :", rang.inner_text().replace("\n", " | "))
    retirer = s.pg.get_by_role("button", name="Remove BAAI/bge-reranker-v2-m3").last
    centre(garde); attendre(s, 600)
    badge = rang.get_by_text(re.compile(r"^(Rerank|RERANK|rerank|Embedding|LLM|Chat)$")).first
    el = [(nom, "Nom de l'instance"), (url, "URL de base"), (garde, MODELE)]
    el += [(badge, badge.inner_text())] if badge.count() else []
    el += [(retirer, "retirer le doublon"), (carte.get_by_role("button", name="Enregistrer").last, "Enregistrer")]
    cap(s, M03, "15-instance-rerank", el)
    retirer.click(); attendre(s, 1200)
    conf = s.pg.get_by_role("alertdialog").or_(s.pg.get_by_role("dialog")).filter(visible=True).last
    conf.get_by_role("button", name="Retirer").click(); attendre(s, 1200)
    carte.get_by_role("button", name="Enregistrer").last.click(); attendre(s, 3000)
    log("messages :", toasts(s).all_inner_texts())
    s.pg.reload(); attendre(s, 3000)
    texte(s, "VLLM").click(); attendre(s, 3000)
    titre, carte = carte_instance(s)
    contenu = carte.inner_text().replace("\n", " | ")
    log("carte enregistrée :", contenu[:500])
    releve(s, "rerank-carte")


def defaut(s):
    connecte(s)
    s.aller("/user-setting/model", 4000)
    bouton(s, "Définir les modèles par défaut").click(); attendre(s, 2500)
    ligne = s.pg.locator("label").filter(has_text="Modèle de rerank").first.locator("xpath=..")
    log("ligne avant :", ligne.inner_text().replace("\n", " | "))
    ligne.locator("button, [role=combobox]").first.click(); attendre(s, 1500)
    liste = s.pg.locator("[role=listbox], [data-radix-popper-content-wrapper]").last
    log("liste :", liste.inner_text().replace("\n", " | ")[:400])
    choix = liste.get_by_text(MODELE, exact=True).first
    cap(s, M03, "16-modele-de-rerank", [(ligne, "Modèle de rerank"), (choix, MODELE)])
    choix.click(); attendre(s, 2000)
    log("messages :", toasts(s).all_inner_texts())
    s.pg.reload(); attendre(s, 3000)
    bouton(s, "Définir les modèles par défaut").click(); attendre(s, 2500)
    ligne = s.pg.locator("label").filter(has_text="Modèle de rerank").first.locator("xpath=..")
    log("ligne relue après rechargement :", ligne.inner_text().replace("\n", " | "))


def assistant(s, *phases):
    connecte(s)
    phases = phases or ("regler", "question")
    if "regler" in phases:
        s.aller("/chats", 3000)
        if s.pg.get_by_text(CHAT, exact=True).count() == 0:
            bouton(s, "Créer un chat").click(); attendre(s, 1500)
            dlg = s.pg.get_by_role("dialog")
            dlg.get_by_placeholder("Veuillez saisir le nom").fill(CHAT)
            dlg.get_by_role("button", name="Enregistrer").click(); attendre(s, 3500)
        ouvrir_assistant(s, CHAT)
        pan = panneau(s)
        lab = lambda t: pan.locator("label").filter(has_text=t).first
        choix = lab("Bases de connaissances").locator("xpath=following::button[1]")
        haut(lab("Message d'accueil"))
        choix.click(); attendre(s, 1200)
        s.pg.get_by_role("option").filter(has_text="Démo Vélanor").first.click(); attendre(s, 800)
        s.pg.keyboard.press("Escape"); attendre(s, 800)
        pan = panneau(s)
        lab = lambda t: pan.locator("label").filter(has_text=t).first
        deplier_section(s, pan, "Paramètres avancés")
        deplier_section(s, pan, "Naive")
        num = lambda l: l.locator("xpath=following::input[@type='number'][1]")
        poids = lab("Poids de similarité par mots-clés")
        haut(poids)
        num(poids).fill("0.3"); num(poids).press("Tab"); attendre(s, 400)
        rer = lab("Modèle de réordonnancement")
        champ = rer.locator("xpath=following::*[self::button or @role='combobox'][1]")
        log("Modèle de réordonnancement avant :", champ.inner_text())
        haut(lab("Rerank candidates"))
        champ.click(); attendre(s, 1500)
        pop = popover(s)
        log("rerankers proposés :", pop.inner_text().replace("\n", " | ")[:300])
        opt = pop.get_by_text(MODELE, exact=True).first
        cap(s, M08, "22-modele-de-reordonnancement", [
            (lab("Rerank candidates").locator("xpath=.."), "Rerank candidates"), (champ, "Modèle de réordonnancement"),
            (opt, MODELE)])
        opt.click(); attendre(s, 1000)
        s.pg.keyboard.press("Escape"); attendre(s, 600)
        pan = panneau(s)
        lab = lambda t: pan.locator("label").filter(has_text=t).first
        log("après choix : Top N", num(lab("Top N")).input_value(), "; poids", num(lab("Poids de similarité par mots-clés")).input_value(),
            "; candidats", num(lab("Rerank candidates")).input_value(),
            "; reranker", lab("Modèle de réordonnancement").locator("xpath=following::*[self::button or @role='combobox'][1]").inner_text())
        pan.get_by_role("button", name="Enregistrer").click(); attendre(s, 1200)
        log("après enregistrement :", toasts(s).all_inner_texts())
        s.pg.reload(); attendre(s, 4000)
        pan = panneau(s); deplier_section(s, pan, "Paramètres avancés"); deplier_section(s, pan, "Naive")
        lab = lambda t: pan.locator("label").filter(has_text=t).first
        log("relu : reranker", lab("Modèle de réordonnancement").locator("xpath=following::*[self::button or @role='combobox'][1]").inner_text(),
            "; Top N", num(lab("Top N")).input_value(), "; poids", num(lab("Poids de similarité par mots-clés")).input_value())
    if "question" in phases:
        ouvrir_assistant(s, CHAT)
        if s.pg.get_by_text("Paramètres du chat", exact=True).is_visible():
            s.pg.locator("button:has(svg.lucide-panel-right-close)").last.click(); attendre(s, 1500)
        for q in (Q30, "Quel est le plafond des pénalités de retard du contrat Batterix ?"):
            d = envoyer(s, q)
            log(f"question {q!r} : réponse affichée après {d:.1f} s")
        releve(s, "rerank-reponses")


def choix_base(s):
    """Chapitre 04, étape 15 : liste « Bases de connaissances » ouverte, « Manuel-Prise-en-main » et « Fermer »."""
    connecte(s)
    s.aller("/chats", 3000)
    if s.pg.get_by_text("Manuel-Assistant", exact=True).count() == 0:
        bouton(s, "Créer un chat").click(); attendre(s, 1500)
        dlg = s.pg.get_by_role("dialog")
        dlg.get_by_placeholder("Veuillez saisir le nom").fill("Manuel-Assistant")
        dlg.get_by_role("button", name="Enregistrer").click(); attendre(s, 3500)
    ouvrir_assistant(s, "Manuel-Assistant")
    pan = panneau(s)
    choix = pan.locator("label").filter(has_text="Bases de connaissances").first.locator("xpath=following::button[1]")
    choix.click(); attendre(s, 1500)
    opt = s.pg.get_by_role("option").filter(has_text="Manuel-Prise-en-main").first
    opt.click(); attendre(s, 800)
    fermer = s.pg.get_by_role("option").filter(has_text=re.compile(r"^\s*Fermer\s*$")).first
    if not fermer.count():
        fermer = s.pg.get_by_text("Fermer", exact=True).last
    log("liste :", popover(s).inner_text().replace("\n", " | ")[:300])
    cap(s, M04, "18-choix-base", [(s.pg.get_by_placeholder("Rechercher...").last, "Rechercher..."),
                                  (opt, "Manuel-Prise-en-main"), (fermer, "Fermer")])
    fermer.click(); attendre(s, 800)
    log("liste refermée par « Fermer » :", not s.pg.get_by_role("option").filter(has_text="Manuel-Prise-en-main").first.is_visible(),
        "; champ :", choix.inner_text())


def reperage(s, quoi):
    connecte(s)
    if quoi == "fournisseur":
        fournisseur(s, "VLLM"); releve(s, "rerank-vllm")
    elif quoi == "assistant":
        ouvrir_assistant(s, "Démo Vélanor")
        pan = panneau(s); deplier_section(s, pan, "Paramètres avancés"); deplier_section(s, pan, "Naive")
        releve(s, "rerank-assistant")


if __name__ == "__main__":
    scenario, *args = sys.argv[1:]
    with sync_playwright() as p:
        s = Session(p)
        s.pg.set_default_timeout(15000)
        try:
            globals()[scenario](s, *args)
        except Exception:
            traceback.print_exc()
            ECHEC.mkdir(parents=True, exist_ok=True)
            s.pg.screenshot(path=str(ECHEC / "echec-reranker.png"))
            (ECHEC / "echec-reranker.txt").write_text(s.pg.url + "\n" + s.pg.inner_text("body"))
            sys.exit(1)
        finally:
            s.b.close()
