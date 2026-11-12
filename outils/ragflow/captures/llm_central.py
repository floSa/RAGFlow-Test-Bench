"""Captures du branchement sur le service LLM central (chapitre 03, réglage du reranker du chapitre 08).

Scénarios (tout à la souris ; la clé du service est lue dans .env, saisie dans le champ puis masquée sur les captures) :
- reperage <quoi> : relevés sans capture (donnees/captures-explorer/) ;
- modeles [phases] : phases « fournisseurs » (liste des fournisseurs), « instance » (instance « llm-central » du
  fournisseur « OpenAI-API-Compatible » déclarée à la souris, quatre noms fixes gardés, alias retirés), « jetons »
  (« Tokens maximum » de chat, embed et rerank), « personnalise » (menu « … » et fenêtre « Ajouter un modèle
  personnalisé », refermée sans rien ajouter), « defauts » (« Définir les modèles par défaut », dont « Modèle de
  rerank »), « supprimer » (instance « voix-locale », remplacée par « transcribe », retirée) ;
- reranker : « Modèle de réordonnancement » de l'assistant « Démo Vélanor » (liste ouverte, refermée sans enregistrer).
Prérequis de « instance » : aucune instance « llm-central » (retirer celle du script de configuration avant).
Usage : outils/communs/captures/lancer.sh outils/ragflow/captures/llm_central.py <scénario> [phases]
"""
import re
import sys
import traceback
from pathlib import Path

from playwright.sync_api import sync_playwright

from captures import Session, cap, bouton, texte, _INVENTAIRE  # noqa: F401
from manuels_03_06 import attendre, popover, centre, haut  # noqa: F401
from manuels_07_15 import log
from manuels_10_14 import dialogue, toasts
from relecture_novice_2 import fournisseur, deplier

ECHEC = Path("donnees/captures-explorer")
M03, M08, M12 = "01-installation", "05-assistants-et-citations", "12-qualite-et-performances"
FOURN, INST = "OpenAI-API-Compatible", "llm-central"
FIXES = ["chat", "embed", "rerank", "transcribe"]
JETONS = {"chat": "16384", "embed": "8192", "rerank": "8192"}


def env():
    d = {}
    for l in Path(".env").read_text().splitlines():
        if "=" in l and not l.lstrip().startswith("#"):
            k, v = l.split("=", 1)
            d[k.strip()] = v.strip()
    return d


ENV = env()
URL_CENTRAL = ENV.get("LLM_CENTRAL_URL", "http://llm-central:8080/v1")


def releve(s, nom):
    ECHEC.mkdir(parents=True, exist_ok=True)
    s.pg.screenshot(path=str(ECHEC / f"central-{nom}.png"))
    (ECHEC / f"central-{nom}.txt").write_text(s.pg.url + "\n" + s.pg.inner_text("body") + "\n== éléments ==\n"
                                              + "\n".join(s.pg.evaluate(_INVENTAIRE)))
    log("relevé", nom)


def phases_de(s, prefixe, phases, defaut):
    for ph in phases or defaut:
        log("== phase", ph)
        globals()[prefixe + "_" + ph](s)


def carte_central(s):
    return deplier(s, s.pg.locator(f":text-is('{INST}')").first)


def confirmer(s, libelle):
    conf = s.pg.get_by_role("alertdialog").or_(s.pg.get_by_role("dialog")).filter(visible=True).last
    log("confirmation :", conf.inner_text().replace("\n", " | "))
    conf.get_by_role("button", name=libelle).click(); attendre(s, 1200)


# ---------------------------------------------------------------- chapitre 03 : modèles

def modeles(s, *phases):
    s.connexion(); s.francais()
    phases_de(s, "modeles", phases, ("fournisseurs", "instance", "jetons", "personnalise", "defauts", "supprimer", "ouvert"))


def modeles_fournisseurs(s):
    s.aller("/user-setting/model", 4000)
    s.pg.get_by_placeholder("Rechercher").first.fill(FOURN); attendre(s, 1200)
    cap(s, M03, "02-fournisseurs-de-modeles", [
        (texte(s, "Fournisseurs de modèles"), "Fournisseurs de modèles"),
        (bouton(s, "Définir les modèles par défaut"), "Définir les modèles par défaut"),
        (s.pg.get_by_placeholder("Rechercher").first, "Rechercher"),
        (texte(s, FOURN).locator("xpath=ancestor::button[1]"), FOURN)])


def modeles_liste(s):
    """Reprise des captures 05 et 06 sans enregistrer (la carte non enregistrée disparaît au rechargement)."""
    modeles_instance(s, enregistrer=False)


def modeles_instance(s, enregistrer=True):
    fournisseur(s, FOURN)
    if enregistrer and s.pg.locator(f":text-is('{INST}')").count():
        raise RuntimeError(f"{INST} existe déjà : la retirer avant ce scénario")
    ajout = s.pg.get_by_role("button", name="Add instance")
    ajout.scroll_into_view_if_needed(); ajout.click(); attendre(s, 2000)
    nom = s.pg.get_by_placeholder("Please input instance name")
    nom.evaluate("e => e.scrollIntoView({block: 'start'})"); attendre(s, 800)
    nom.fill(INST)
    cle = s.pg.get_by_placeholder("Veuillez saisir la clé API", exact=False).last
    cle.fill(ENV["LLM_CENTRAL_KEY"])
    entrees = s.pg.locator("input:visible")
    log("champs :", entrees.evaluate_all("l => l.map(e => [e.placeholder, e.type])"))
    url = cle.locator("xpath=following::input[1]")
    url.fill(URL_CENTRAL)
    lister = s.pg.get_by_role("button", name="Lister les modèles").last
    cap(s, M03, "05-ajout-instance", [(nom, "Nom de l'instance"), (cle, "Clé API"), (url, "URL de base"),
                                      (lister, "Lister les modèles")], masques=[cle])
    lister.click(); attendre(s, 5000)
    # la nouvelle carte seule (la carte « voix-locale » a aussi des boutons « Remove … »)
    carte = nom.locator("xpath=ancestor::*[.//button[normalize-space()='Lister les modèles']][1]")
    log("modèles listés :", carte.inner_text().replace("\n", " | ")[:1500])
    noms = carte.locator("button[aria-label^='Remove ']").evaluate_all("l => l.map(e => e.getAttribute('aria-label'))")
    alias = [n[len("Remove "):] for n in noms if n[len("Remove "):] not in FIXES + ["all", "all models"]]
    log("alias à retirer :", alias)
    premier = carte.locator(f":text-is('{alias[0]}')").first
    nom.evaluate("e => e.scrollIntoView({block: 'start'})"); attendre(s, 800)
    for loc in (premier, carte.locator(":text-is('chat')").first):
        log("position :", loc.bounding_box())
    retire = carte.get_by_role("button", name=f"Remove {alias[0]}", exact=True).first
    cap(s, M03, "06-modeles-listes", [(premier, alias[0]), (retire, f"retirer {alias[0]}"),
                                      (carte.locator(":text-is('chat')").first, "chat"),
                                      (carte.get_by_role("button", name="Enregistrer").first, "Enregistrer")],
        masques=[carte.locator("input[type=password]").first])
    if not enregistrer:
        s.pg.reload(); attendre(s, 3000)
        return
    for a in alias:
        carte.get_by_role("button", name=f"Remove {a}", exact=True).first.click(); attendre(s, 1000)
        confirmer(s, "Retirer")
    log("modèles gardés :", carte.inner_text().replace("\n", " | ")[:800])
    carte.get_by_role("button", name="Enregistrer").first.click(); attendre(s, 3000)
    log("messages :", toasts(s).all_inner_texts())
    s.pg.reload(); attendre(s, 3000)
    texte(s, FOURN).click(); attendre(s, 3000)
    modeles_enregistree(s)


def modeles_enregistree(s):
    fournisseur(s, FOURN)
    carte = carte_central(s)
    contenu = carte.inner_text().replace("\n", " | ")
    log("carte enregistrée :", contenu[:800])
    titre = s.pg.locator(f":text-is('{INST}')").first
    haut(titre); attendre(s, 800)
    el = [(titre, INST)] + [(carte.locator(f":text-is('{m}')").first, m) for m in FIXES]
    cle = carte.get_by_placeholder("Clear this field", exact=False).first  # clé enregistrée, début et fin en clair
    cap(s, M03, "07-instance-enregistree", el, masques=[cle])


def modeles_ouvert(s):
    """Fournisseur ouvert, carte « llm-central » repliée (prise après la déclaration et le retrait de « voix-locale »)."""
    fournisseur(s, FOURN)
    titre = s.pg.locator(f":text-is('{INST}')").first
    bascule = titre.locator("xpath=ancestor::*[@data-testid='instance-name-row'][1]").locator("[data-testid=instance-collapse]")
    if bascule.get_attribute("aria-label") != "Voir les modèles":
        bascule.click(); attendre(s, 1500)
    entete = s.pg.get_by_text(re.compile(r"^Comment intégrer")).first
    cap(s, M03, "03-fournisseur-openai-compatible", [(texte(s, FOURN).last, FOURN), (entete, entete.inner_text()),
                                                     (titre, INST), (bascule, "Voir les modèles"),
                                                     (s.pg.get_by_role("button", name="Add instance"), "Add instance")])


def ouvrir_modifier(s, nom):
    carte = carte_central(s)
    g = carte.locator(f":text-is('{nom}')").first
    centre(g); g.hover(); attendre(s, 800)
    return g, s.pg.locator(f"[data-testid='models-edit-{nom}']")


def modeles_jetons(s):
    fournisseur(s, FOURN)
    for nom, val in JETONS.items():
        g, crayon = ouvrir_modifier(s, nom)
        if nom == "chat":
            rang = g.locator(f"xpath=ancestor::*[.//*[@data-testid='models-edit-{nom}']][1]")
            log("ligne du modèle :", rang.inner_text().replace("\n", " | "))
            badge = rang.get_by_text(re.compile(r"^(LLM|Chat)$")).first
            el = [(g, nom)] + ([(badge, badge.inner_text())] if badge.count() else []) + [(crayon, "Modifier le modèle")]
            cap(s, M03, "12-crayon-modifier-le-modele", el)
        crayon.click(); attendre(s, 1500)
        dlg = dialogue(s)
        lab = lambda x: dlg.locator("label").filter(has_text=x).first
        tokens = lab("Tokens maximum").locator("xpath=following::input[1]")
        log(f"{nom} avant :", dlg.inner_text().replace("\n", " | "), "; Tokens maximum =", tokens.input_value())
        tokens.fill(val)
        if nom == "chat":
            cap(s, M12, "02-tokens-maximum", [(lab("Type de modèle"), "Type de modèle"), (tokens, "Tokens maximum"),
                                              (dlg.get_by_text("Appel d'outil").first, "Appel d'outil"),
                                              (dlg.get_by_role("button", name="Non"), "Non"),
                                              (dlg.get_by_role("button", name="Confirmer"), "Confirmer")])
        dlg.get_by_role("button", name="Confirmer").click(); attendre(s, 2000)
        log(f"{nom} : messages", toasts(s).all_inner_texts())
    s.pg.reload(); attendre(s, 3000)
    texte(s, FOURN).click(); attendre(s, 3000)
    for nom in JETONS:
        _, crayon = ouvrir_modifier(s, nom)
        crayon.click(); attendre(s, 1500)
        dlg = dialogue(s)
        v = dlg.locator("label").filter(has_text="Tokens maximum").first.locator("xpath=following::input[1]").input_value()
        log(f"{nom} : Tokens maximum relu après rechargement =", v)
        dlg.get_by_role("button", name="Non").click(); attendre(s, 1000)


def modeles_personnalise(s):
    fournisseur(s, FOURN)
    carte = carte_central(s)
    carte.get_by_role("button", name="Lister les modèles").first.locator("xpath=following::button[1]").click(); attendre(s, 1200)
    item = s.pg.get_by_role("menuitem").filter(has_text="Ajouter un modèle personnalisé").first
    cap(s, M03, "13-menu-modele-personnalise", [(item, "Ajouter un modèle personnalisé"),
                                                (s.pg.get_by_role("menuitem").filter(has_text="Verify all models").first, "Verify all models")])
    item.click(); attendre(s, 1500)
    dlg = s.pg.get_by_role("dialog").filter(has_text="Ajouter un modèle personnalisé").first
    lab = lambda x: dlg.locator("label").filter(has_text=x).first
    nom = lab("Nom du modèle").locator("xpath=following::input[1]")
    jetons = dlg.locator("input[type=number]").first
    nom.fill("nom-exact-du-modele")
    jetons.fill("8192")
    dlg.get_by_role("button").filter(has_text="Sélectionner une valeur").first.click(); attendre(s, 1000)
    popover(s).get_by_text("Rerank", exact=True).first.click(); attendre(s, 600)
    if popover(s).get_by_text("Fermer", exact=True).count():
        popover(s).get_by_text("Fermer", exact=True).first.click(); attendre(s, 800)
    typ = lab("Type de modèle").locator("xpath=following::button[1]")
    log("type choisi :", typ.inner_text())
    cap(s, M03, "14-modele-personnalise", [(nom, "Nom du modèle"), (typ, "Type de modèle"), (jetons, "Tokens maximum"),
                                           (dlg.get_by_role("button", name="Non"), "Non"),
                                           (dlg.get_by_role("button", name="Confirmer"), "Confirmer")])
    dlg.get_by_role("button", name="Non").click(); attendre(s, 1000)
    s.pg.reload(); attendre(s, 3000)
    log("modèle d'exemple absent après rechargement :", s.pg.locator(":text-is('nom-exact-du-modele')").count() == 0)


def ligne_defaut(s, t):
    return s.pg.locator("label").filter(has_text=t).first.locator("xpath=..")


def choisir(s, libelle, modele, capture=None):
    """Ouvre la liste d'un modèle par défaut et choisit `modele` de l'instance llm-central."""
    ligne_defaut(s, libelle).locator("button[aria-haspopup]").first.click(); attendre(s, 1500)
    liste = s.pg.locator("[role=listbox], [data-radix-popper-content-wrapper]").last
    log(f"liste {libelle} :", liste.inner_text().replace("\n", " | ")[:400])
    opt = liste.get_by_text(modele, exact=True).first
    if capture:
        cap(s, M03, capture, [(liste, "liste des modèles de chat"), (opt, modele)])
    opt.click(); attendre(s, 1500)
    log(f"{libelle} : messages", toasts(s).all_inner_texts())


def modeles_defauts(s):
    s.aller("/user-setting/model", 4000)
    bouton(s, "Définir les modèles par défaut").click(); attendre(s, 2500)
    log("défauts avant :", s.pg.locator("main").inner_text().replace("\n", " | ")[:800])
    choisir(s, "Modèle de chat", "chat", "10-choix-modele-de-chat")
    choisir(s, "Modèle d'embedding", "embed")
    choisir(s, "Modèle Speech2txt", "transcribe")
    choisir(s, "Modèle de rerank", "rerank")
    s.pg.reload(); attendre(s, 3000)
    bouton(s, "Définir les modèles par défaut").click(); attendre(s, 2500)
    cap(s, M03, "09-modeles-par-defaut", [
        (ligne_defaut(s, "Modèle de chat"), "Modèle de chat"), (ligne_defaut(s, "Modèle d'embedding"), "Modèle d'embedding"),
        (ligne_defaut(s, "Modèle Img2txt"), "Modèle Img2txt"), (ligne_defaut(s, "Modèle Speech2txt"), "Modèle Speech2txt"),
        (ligne_defaut(s, "Modèle de rerank"), "Modèle de rerank"), (ligne_defaut(s, "Modèle TTS"), "Modèle TTS")])


def modeles_supprimer(s):
    fournisseur(s, FOURN)
    titre = s.pg.locator(":text-is('voix-locale')").first
    haut(titre); attendre(s, 800)
    poubelle = titre.locator("xpath=ancestor::*[.//button[@aria-label='Delete instance']][1]").get_by_role(
        "button", name="Delete instance").first
    poubelle.click(); attendre(s, 1500)
    dlg = s.pg.get_by_role("alertdialog").or_(s.pg.get_by_role("dialog")).first
    conf = dlg.get_by_role("button").filter(has_text=re.compile("Supprimer|Delete|Confirmer|OK", re.I)).last
    log("fenêtre :", dlg.inner_text().replace("\n", " | "))
    cap(s, M03, "08-suppression-instance", [(dlg, "confirmation"), (conf, conf.inner_text().strip())])
    conf.click(); attendre(s, 2500)
    s.pg.reload(); attendre(s, 3000)
    texte(s, FOURN).click(); attendre(s, 3000)
    log("voix-locale encore présente :", s.pg.locator(":text-is('voix-locale')").count())


# ---------------------------------------------------------------- chapitre 08 : reranker d'un assistant

def reranker(s):
    s.connexion(); s.francais()
    s.aller("/chats", 3000)
    texte(s, "Démo Vélanor").click(); attendre(s, 3000)
    releve(s, "assistant")


def reperage(s, quoi):
    s.connexion(); s.francais()
    if quoi == "ajout":
        fournisseur(s, FOURN)
        releve(s, "fournisseur")
        ajout = s.pg.get_by_role("button", name="Add instance")
        ajout.scroll_into_view_if_needed(); ajout.click(); attendre(s, 2000)
        log("champs :", s.pg.locator("input:visible").evaluate_all("l => l.map(e => [e.placeholder, e.type])"))
        releve(s, "ajout")
    elif quoi == "defauts":
        s.aller("/user-setting/model", 4000)
        bouton(s, "Définir les modèles par défaut").click(); attendre(s, 2500)
        l = ligne_defaut(s, "Modèle de chat")
        log("html ligne :", l.evaluate("e => e.outerHTML")[:2500])
        l.locator("button[aria-haspopup]").first.click(); attendre(s, 1500)
        releve(s, "defauts")


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
            s.pg.screenshot(path=str(ECHEC / "echec-central.png"))
            (ECHEC / "echec-central.txt").write_text(s.pg.url + "\n" + s.pg.inner_text("body"))
            sys.exit(1)
        finally:
            s.b.close()
