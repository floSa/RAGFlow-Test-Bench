"""Captures et vérifications demandées par la relecture du manuel par un lecteur novice (chapitres 02, 03, 10, 13).

Scénarios (tout à la souris, objets nommés « Manuel-… », supprimés ensuite par outils/ragflow/nettoyer_manuel.py) :
- reperage <quoi> : relevés sans capture (textes et éléments visibles dans donnees/captures-explorer/) ;
- inscription : formulaire « Create an account » rempli, non validé (chapitre 02) ;
- modeles : nouvelle instance VLLM « Manuel-instance », modèles listés, modèle en double retiré, instance supprimée ;
  enregistrement des modèles par défaut (chapitre 03) ;
- export : agent « Manuel-Agent-Export » créé depuis un blanc, menu « Gestion », « Exporter » (chapitre 10) ;
- invitation : compte « Manuel-Invite » inscrit à la souris, invité dans l'équipe, invitation acceptée côté invité, base
  « Manuel-Partage » passée en « Équipe » et vue par l'invité, puis membre retiré (chapitre 13).
Usage : outils/communs/captures/lancer.sh outils/ragflow/captures/relecture_novice.py <scénario> [phases]
"""
import json
import re
import secrets
import sys
import traceback
from pathlib import Path

from playwright.sync_api import sync_playwright

from captures import Session, URL, TXT, COMPTE, cap, bouton, texte, _INVENTAIRE  # noqa: F401
from manuels_03_06 import attendre, popover, ligne, ouvrir_base, creer_base_simple  # noqa: F401
from manuels_07_15 import log, page_compte  # noqa: F401
from manuels_10_14 import dialogue, toasts, avatar  # noqa: F401

ECHEC = Path("donnees/captures-explorer")
INVITE = Path("donnees/ragflow/compte-invite.json")


def releve(s, nom):
    """Texte de la page et éléments visibles, sans capture annotée (repérage)."""
    ECHEC.mkdir(parents=True, exist_ok=True)
    s.pg.screenshot(path=str(ECHEC / f"relecture-{nom}.png"))
    (ECHEC / f"relecture-{nom}.txt").write_text(s.pg.url + "\n" + s.pg.inner_text("body") + "\n== éléments ==\n"
                                               + "\n".join(s.pg.evaluate(_INVENTAIRE)))
    log("relevé", nom)


def deconnexion(s):
    s.pg.context.clear_cookies()
    s.pg.evaluate("() => { const l = localStorage.getItem('lng'); localStorage.clear(); if (l) localStorage.setItem('lng', l); }")
    s.aller("/login", 3000)


def fr(s):
    if s.pg.get_by_text("English", exact=True).count():
        s.francais()


def connexion_compte(s, email, mdp):
    s.aller("/", 1500)
    deconnexion(s)
    s.pg.locator("input[name=email]:visible, input[type=email]:visible").first.fill(email)
    s.pg.locator("input[type=password]:visible").first.fill(mdp)
    s.pg.locator("button[type=submit]:visible").first.click()
    s.pg.wait_for_url(lambda u: "login" not in u, timeout=20000); attendre(s, 3000)


# ---------------------------------------------------------------- chapitre 02 : inscription

def inscription(s):
    m = "01-installation"
    s.aller("/login", 3000)
    texte(s, "Sign up").click(); attendre(s, 1500)
    champ = lambda n: s.pg.locator(f"input[name={n}]:visible").first
    champ("email").fill("manuel.compte@exemple.fr")
    champ("nickname").fill("Manuel-Compte")
    champ("password").fill("NePasUtiliser-0000")
    lien = s.pg.get_by_text("Sign in", exact=True).filter(visible=True).last
    log("lien de retour :", lien.evaluate("e => e.outerHTML")[:200])
    cap(s, m, "01-inscription", [
        (champ("email"), "Email"), (champ("nickname"), "Nickname"), (champ("password"), "Password"),
        (bouton(s, "Continue"), "Continue"), (lien, "Sign in")], masques=[champ("password")])


# ---------------------------------------------------------------- chapitre 03 : modèles

def modeles(s, *phases):
    phases = phases or ("instance", "defauts", "langue")
    s.connexion(); s.francais()
    for ph in phases:
        log("== phase", ph)
        globals()["modeles_" + ph](s)


def modeles_instance(s):
    m = "01-installation"
    s.aller("/user-setting/model", 4000)
    texte(s, "VLLM").click(); attendre(s, 3000)
    ajout = s.pg.get_by_role("button", name="Add instance")
    ajout.scroll_into_view_if_needed(); ajout.click(); attendre(s, 2000)
    nom = s.pg.get_by_placeholder("Please input instance name")
    nom.evaluate("e => e.scrollIntoView({block: 'start'})"); attendre(s, 800)
    nom.fill("Manuel-instance")
    s.pg.get_by_placeholder("http://host.docker.internal:8000/v1").last.fill("http://vllm-embed:8000/v1")
    s.pg.get_by_role("button", name="Lister les modèles").last.click(); attendre(s, 5000)
    garde = s.pg.locator(":text-is('bge-m3')").last
    double = s.pg.locator(":text-is('BAAI/bge-m3')").last
    retirer_double = s.pg.get_by_role("button", name="Remove BAAI/bge-m3").last
    log("boutons de la carte :", s.pg.get_by_role("button", name=re.compile("^(Remove|Add) ")).evaluate_all(
        "l => l.map(e => e.getAttribute('aria-label'))"))
    cap(s, m, "06-modeles-listes", [
        (garde, "bge-m3"), (retirer_double, "retirer BAAI/bge-m3"),
        (s.pg.get_by_role("button", name="Enregistrer").last, "Enregistrer")])
    retirer_double.click(); attendre(s, 1200)
    conf = s.pg.get_by_role("alertdialog").or_(s.pg.get_by_role("dialog")).filter(visible=True).last
    log("confirmation du retrait :", conf.inner_text().replace("\n", " | "))
    conf.get_by_role("button", name="Retirer").click(); attendre(s, 1200)
    log("après retrait : boutons", s.pg.get_by_role("button", name=re.compile("^(Remove|Add) ")).evaluate_all(
        "l => l.map(e => e.getAttribute('aria-label'))"))
    s.pg.get_by_role("button", name="Enregistrer").last.click(); attendre(s, 3000)
    log("messages :", toasts(s).all_inner_texts())
    s.pg.reload(); attendre(s, 3000)
    texte(s, "VLLM").click(); attendre(s, 3000)
    titre = s.pg.locator(":text-is('Manuel-instance')").first
    log("instance enregistrée présente :", titre.count())
    carte = titre.locator("xpath=ancestor::*[.//button[@aria-label='Delete instance']][1]")
    if titre.count():
        titre.click(); attendre(s, 1500)
        log("carte enregistrée :", carte.inner_text().replace("\n", " | ")[:400])
        carte.get_by_role("button", name="Delete instance").first.click(); attendre(s, 1500)
        dlg = s.pg.get_by_role("alertdialog").or_(s.pg.get_by_role("dialog")).first
        dlg.get_by_role("button").filter(has_text=re.compile("Supprimer|Delete")).last.click(); attendre(s, 2500)
        s.pg.reload(); attendre(s, 3000)
        texte(s, "VLLM").click(); attendre(s, 3000)
        log("instance encore présente après suppression :", s.pg.locator(":text-is('Manuel-instance')").count())


def modeles_defauts(s):
    """Fenêtre « Définir les modèles par défaut » : boutons présents, requête envoyée au choix d'un modèle, relecture."""
    s.aller("/user-setting/model", 4000)
    requetes = []
    s.pg.on("request", lambda r: requetes.append(f"{r.method} {r.url.replace(URL, '')}") if "/api/" in r.url
            and r.method != "GET" else None)
    bouton(s, "Définir les modèles par défaut").click(); attendre(s, 2500)
    pan = s.pg.locator("label").filter(has_text="Modèle de chat").first.locator(
        "xpath=ancestor::*[.//label[contains(., 'Modèle TTS')]][1]")
    log("boutons de la fenêtre :", pan.locator("button").evaluate_all(
        "l => l.map(e => (e.innerText || e.getAttribute('aria-label') || '').trim()).filter(Boolean)"))
    releve(s, "modeles-par-defaut")
    ligne_chat = s.pg.locator("label").filter(has_text="Modèle de chat").first.locator("xpath=..")
    ligne_chat.get_by_text("gemma4:e4b").click(); attendre(s, 1500)
    s.pg.locator("[data-radix-popper-content-wrapper]").last.get_by_text("gemma4:e4b", exact=True).last.click()
    attendre(s, 2500)
    log("requêtes d'écriture après choix du même modèle de chat :", requetes)
    s.pg.keyboard.press("Escape"); attendre(s, 800)
    s.pg.reload(); attendre(s, 3000)
    bouton(s, "Définir les modèles par défaut").click(); attendre(s, 2500)
    log("valeur relue après rechargement :", s.pg.locator("label").filter(has_text="Modèle de chat").first.locator(
        "xpath=..").inner_text().replace("\n", " | "))


def modeles_langue(s):
    """Libellé du bouton de connexion quand le navigateur a déjà choisi le français."""
    deconnexion(s)
    log("bouton de connexion (français mémorisé) :", s.pg.locator("button[type=submit]:visible").first.inner_text(),
        "; titre :", s.pg.locator("body").inner_text()[:120].replace("\n", " | "))


# ---------------------------------------------------------------- chapitre 10 : exporter un agent

AGENT = "Manuel-Agent-Export"


def export(s):
    m = "08-agents"
    s.connexion(); s.francais()
    s.aller("/agents", 3000)
    if not s.pg.get_by_text(AGENT, exact=True).count():
        s.pg.locator("button:has(svg.lucide-plus)").first.click(); attendre(s, 1000)
        s.pg.get_by_text("Créer depuis un blanc", exact=True).first.click(); attendre(s, 1500)
        dlg = dialogue(s)
        dlg.locator("input").first.fill(AGENT)
        dlg.get_by_role("button", name="Confirmer").click(); attendre(s, 4000)
    else:
        texte(s, AGENT).click(); attendre(s, 4000)
    gestion = s.pg.locator("button").filter(has_text=re.compile(r"^\s*Gestion\s*$")).first  # rôle masqué menu ouvert
    gestion.click(); attendre(s, 1200)
    items = s.pg.get_by_role("menuitem")
    libelles = [t.strip() for t in items.all_inner_texts()]
    log("menu « Gestion » :", libelles)
    exporter = items.filter(has_text="Exporter").first
    cap(s, m, "16-menu-gestion", [(gestion, "Gestion")] + [(items.nth(i), libelles[i]) for i in range(len(libelles))])
    with s.pg.expect_download(timeout=20000) as dl:
        exporter.click()
    f = dl.value
    cible = ECHEC / f"relecture-{f.suggested_filename}"
    ECHEC.mkdir(parents=True, exist_ok=True)
    f.save_as(str(cible))
    contenu = json.loads(cible.read_text())
    log("fichier téléchargé :", f.suggested_filename, "; taille", cible.stat().st_size, "octets ; clés",
        list(contenu.keys())[:10])
    attendre(s, 1500)
    log("messages :", toasts(s).all_inner_texts())


# ---------------------------------------------------------------- chapitre 13 : invitation côté invité

BASE_PARTAGE = "Manuel-Partage"


def compte_invite():
    if INVITE.exists():
        return json.loads(INVITE.read_text())
    c = {"email": "manuel.invite@exemple.fr", "nickname": "Manuel-Invite", "password": "Mi-" + secrets.token_urlsafe(12)}
    INVITE.write_text(json.dumps(c, ensure_ascii=False, indent=2))
    return c


def invitation(s, *phases):
    phases = phases or ("inscrire", "inviter", "accepter", "partager", "voir", "retirer")
    for ph in phases:
        log("== phase", ph)
        globals()["invitation_" + ph](s)


def invitation_inscrire(s):
    c = compte_invite()
    s.aller("/login", 3000)
    texte(s, "Sign up").click(); attendre(s, 1500)
    champ = lambda n: s.pg.locator(f"input[name={n}]:visible").first
    champ("email").fill(c["email"]); champ("nickname").fill(c["nickname"]); champ("password").fill(c["password"])
    champ("password").press("Enter"); attendre(s, 3000)  # le bouton est recouvert par le formulaire retourné
    log("après inscription :", s.pg.url.replace(URL, ""), toasts(s).all_inner_texts())


def invitation_inviter(s):
    c = compte_invite()
    s.connexion(); s.francais()
    page_compte(s, "Équipe")
    bouton(s, "Inviter").click(); attendre(s, 1500)
    dlg = dialogue(s)
    dlg.locator("input").first.fill(c["email"])
    dlg.get_by_role("button", name="Oui").click(); attendre(s, 2500)
    log("après invitation :", toasts(s).all_inner_texts())
    s.pg.reload(); attendre(s, 3000)
    log("ligne du membre :", ligne(s, c["email"]).inner_text().replace("\n", " | ").replace("\t", " | ")
        if ligne(s, c["email"]).count() else "absente")


def invitation_accepter(s):
    c = compte_invite()
    connexion_compte(s, c["email"], c["password"]); fr(s)
    page_compte_invite(s)
    releve(s, "equipe-invite")
    rang = ligne(s, "Banc RAGFlow")
    log("ligne de l'équipe reçue :", rang.inner_text().replace("\n", " | ").replace("\t", " | ") if rang.count() else "absente")
    boutons = rang.locator("button")
    log("boutons de la ligne :", boutons.evaluate_all(
        "l => l.map(e => (e.innerText || e.getAttribute('aria-label') || e.querySelector('svg')?.getAttribute('class') || '').trim())"))
    accepter = rang.get_by_role("button").filter(has_text=re.compile("Accepter|Accept|Rejoindre|Join", re.I)).first
    if not accepter.count():
        accepter = boutons.first
    refuser = rang.get_by_role("button").filter(has_text=re.compile("Refuser|Reject|Decline", re.I)).first
    el = [(texte(s, "Équipes rejointes"), "Équipes rejointes"), (rang, "équipe qui invite"), (accepter, "accepter")]
    if refuser.count():
        el.append((refuser, "refuser"))
    cap(s, "13-exploitation", "10-invitation-recue", el)
    accepter.click(); attendre(s, 2500)
    conf = s.pg.get_by_role("alertdialog").or_(s.pg.get_by_role("dialog")).filter(visible=True)
    if conf.count():
        log("confirmation :", conf.last.inner_text().replace("\n", " | "))
        conf.last.get_by_role("button").filter(has_text=re.compile("Oui|Confirmer|OK|Accepter", re.I)).last.click()
        attendre(s, 2000)
    log("messages :", toasts(s).all_inner_texts())
    s.pg.reload(); attendre(s, 3000)
    rang = ligne(s, "Banc RAGFlow")
    log("après acceptation :", rang.inner_text().replace("\n", " | ").replace("\t", " | ") if rang.count() else "absente")
    releve(s, "equipe-invite-apres")


def page_compte_invite(s):
    s.aller("/", 2000)
    s.pg.locator("header a").last.click(); attendre(s, 3000)
    bouton(s, "Équipe").click(); attendre(s, 2500)


def invitation_partager(s):
    connexion_compte(s, COMPTE["email"], COMPTE["password"]); fr(s)
    s.aller("/datasets", 3000)
    if not s.pg.get_by_text(BASE_PARTAGE, exact=True).count():
        creer_base_simple(s, BASE_PARTAGE)
    ouvrir_base(s, BASE_PARTAGE, "Configuration")
    lab = s.pg.locator("label").filter(has_text="Autorisations").first
    champ = lab.locator("xpath=following::button[1]")
    log("autorisations avant :", champ.inner_text())
    champ.click(); attendre(s, 1000)
    log("choix proposés :", s.pg.get_by_role("option").all_inner_texts())
    s.pg.get_by_role("option").filter(has_text="Équipe").first.click(); attendre(s, 800)
    bouton(s, "Enregistrer").click(); attendre(s, 2500)
    log("messages :", toasts(s).all_inner_texts())
    s.pg.reload(); attendre(s, 3000)
    log("autorisations après rechargement :", s.pg.locator("label").filter(has_text="Autorisations").first.locator(
        "xpath=following::button[1]").inner_text())


def invitation_voir(s):
    c = compte_invite()
    connexion_compte(s, c["email"], c["password"]); fr(s)
    s.aller("/datasets", 3000)
    log("bases vues par l'invité :", s.pg.locator("main").inner_text().replace("\n", " | ")[:600])
    releve(s, "bases-invite")
    if s.pg.get_by_text(BASE_PARTAGE, exact=True).count():
        texte(s, BASE_PARTAGE).click(); attendre(s, 3000)
        log("base ouverte par l'invité :", s.pg.url.replace(URL, ""), s.pg.locator("body").inner_text()[:300].replace("\n", " | "))


def invitation_retirer(s):
    c = compte_invite()
    connexion_compte(s, COMPTE["email"], COMPTE["password"]); fr(s)
    page_compte(s, "Équipe")
    rang = ligne(s, c["email"])
    if rang.count():
        rang.locator("button").last.click(); attendre(s, 1500)
        conf = s.pg.get_by_role("alertdialog").or_(s.pg.get_by_role("dialog")).filter(visible=True)
        conf.last.get_by_role("button").filter(has_text=re.compile("Oui|Supprimer|Confirmer|OK")).last.click(); attendre(s, 2000)
    s.pg.reload(); attendre(s, 3000)
    log("membre encore présent :", bool(ligne(s, c["email"]).count()))


# ---------------------------------------------------------------- repérage

def reperage(s, quoi):
    if quoi == "inscription":
        s.aller("/login", 3000); texte(s, "Sign up").click(); attendre(s, 1500); releve(s, "inscription")
    elif quoi == "gestion":
        s.connexion(); s.francais(); s.aller("/agents", 3000); releve(s, "agents")


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
            s.pg.screenshot(path=str(ECHEC / "echec-relecture.png"))
            (ECHEC / "echec-relecture.txt").write_text(s.pg.url + "\n" + s.pg.inner_text("body"))
            sys.exit(1)
        finally:
            s.b.close()
