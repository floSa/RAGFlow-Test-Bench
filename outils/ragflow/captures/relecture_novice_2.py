"""Captures de la seconde relecture du manuel par un lecteur novice (chapitres 03, 07, 10 et 13).

Scénarios (tout à la souris, objets nommés « Manuel-… », supprimés ensuite par outils/ragflow/nettoyer_manuel.py ;
le jeu de démonstration n'est qu'ouvert, jamais modifié) :
- reperage <quoi> : relevés sans capture (donnees/captures-explorer/) ;
- modeles [phases] : carte « voix-locale » du fournisseur « OpenAI-API-Compatible » (clé masquée), instance VLLM
  « Manuel-instance » enregistrée avec le seul modèle bge-m3 puis supprimée, crayon « Modifier le modèle » au survol ;
- actions : icônes d'une réponse au survol, conversation « Contrat Batterix » de l'assistant « Démo Vélanor » (lecture) ;
- agent [phases] : agent « Manuel-Agent-Documentaire » créé depuis le modèle d'agent, exporté par « Gestion » ›
  « Exporter », réimporté sous « Manuel-Agent-Importe » (canevas importé, même base) ;
- equipe [phases] : compte « Manuel-Invite » inscrit à la souris, invité, invitation acceptée côté invité, membre
  retiré ; compte invité supprimé par l'API d'administration (phase « supprimer »).
Usage : outils/communs/captures/lancer.sh outils/ragflow/captures/relecture_novice_2.py <scénario> [phases]
"""
import base64
import json
import re
import sys
import traceback
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

from captures import Session, URL, COMPTE, cap, bouton, texte, _INVENTAIRE  # noqa: F401
from manuels_03_06 import attendre, popover, ligne, centre  # noqa: F401
import manuels_07_15
from manuels_07_15 import log, page_compte, fit, noeud, ouvrir_agent, fermer_panneau  # noqa: F401
from manuels_10_14 import dialogue, toasts  # noqa: F401
from relecture_novice import releve, connexion_compte, compte_invite, fr, page_compte_invite, deconnexion  # noqa: F401

ECHEC = Path("donnees/captures-explorer")
M03, M07, M10, M13 = "01-installation", "05-assistants-et-citations", "08-agents", "13-exploitation"


def phases_de(s, prefixe, phases, defaut):
    for ph in phases or defaut:
        log("== phase", ph)
        globals()[prefixe + "_" + ph](s)


# ---------------------------------------------------------------- chapitre 03 : modèles

def modeles(s, *phases):
    s.connexion(); s.francais()
    phases_de(s, "modeles", phases, ("voix", "instance", "crayon"))


def fournisseur(s, nom):
    s.aller("/user-setting/model", 4000)
    s.pg.get_by_placeholder("Rechercher").first.fill(nom); attendre(s, 1200)
    texte(s, nom).click(); attendre(s, 3000)


def deplier(s, titre, carte=None):
    """Déplie la carte d'instance de `titre` si besoin (bouton « Voir les modèles ») ; renvoie la carte complète
    (en-tête et champs : le plus proche ancêtre qui contient un champ de saisie)."""
    rangee = titre.locator("xpath=ancestor::*[@data-testid='instance-name-row'][1]")
    bascule = rangee.locator("[data-testid=instance-collapse]")
    if bascule.get_attribute("aria-label") == "Voir les modèles":
        bascule.click(); attendre(s, 2000)
    log("état de la carte :", bascule.get_attribute("aria-label"))
    return titre.locator("xpath=ancestor::*[.//input][1]")


def modeles_voix(s):
    fournisseur(s, "OpenAI-API-Compatible")
    titre = s.pg.locator(":text-is('voix-locale')").first
    carte = deplier(s, titre)
    log("carte voix-locale :", carte.inner_text().replace("\n", " | ")[:600])
    entrees = carte.locator("input")
    log("champs :", entrees.evaluate_all("l => l.map(e => [e.placeholder, e.type, e.value && e.type !== 'password' ? e.value : '***'])"))
    cle = carte.get_by_placeholder("Clear this field", exact=False).first
    url = carte.get_by_placeholder("Veuillez saisir votre URL de base").first
    titre.evaluate("e => e.scrollIntoView({block: 'start'})"); attendre(s, 800)
    modele = carte.locator(":text-is('Systran/faster-whisper-small')").first
    cap(s, M03, "11-instance-voix", [
        (titre, "voix-locale"), (cle, "Clé API"), (url, "URL de base"), (modele, "Systran/faster-whisper-small"),
        (carte.get_by_role("button", name="Enregistrer").first, "Enregistrer")], masques=[cle])


def modeles_instance(s):
    fournisseur(s, "VLLM")
    if s.pg.locator(":text-is('Manuel-instance')").count():
        raise RuntimeError("Manuel-instance existe déjà : lancer nettoyer_manuel.py d'abord")
    ajout = s.pg.get_by_role("button", name="Add instance")
    ajout.scroll_into_view_if_needed(); ajout.click(); attendre(s, 2000)
    nom = s.pg.get_by_placeholder("Please input instance name")
    nom.evaluate("e => e.scrollIntoView({block: 'start'})"); attendre(s, 800)
    nom.fill("Manuel-instance")
    s.pg.get_by_placeholder("http://host.docker.internal:8000/v1").last.fill("http://vllm-embed:8000/v1")
    s.pg.get_by_role("button", name="Lister les modèles").last.click(); attendre(s, 5000)
    s.pg.get_by_role("button", name="Remove BAAI/bge-m3").last.click(); attendre(s, 1200)
    conf = s.pg.get_by_role("alertdialog").or_(s.pg.get_by_role("dialog")).filter(visible=True).last
    log("confirmation du retrait :", conf.inner_text().replace("\n", " | "))
    conf.get_by_role("button", name="Retirer").click(); attendre(s, 1200)
    s.pg.get_by_role("button", name="Enregistrer").last.click(); attendre(s, 3000)
    log("messages :", toasts(s).all_inner_texts())
    s.pg.reload(); attendre(s, 3000)
    texte(s, "VLLM").click(); attendre(s, 3000)
    titre = s.pg.locator(":text-is('Manuel-instance')").first
    carte = deplier(s, titre)
    contenu = carte.inner_text().replace("\n", " | ")
    log("carte enregistrée :", contenu[:500])
    log("modèles de la carte : bge-m3", "bge-m3" in contenu, "; BAAI/bge-m3", "BAAI/bge-m3" in contenu)
    titre.evaluate("e => e.scrollIntoView({block: 'start'})"); attendre(s, 800)
    garde = carte.locator(":text-is('bge-m3')").first
    poubelle = carte.get_by_role("button", name="Delete instance").first
    cap(s, M03, "07-instance-enregistree", [(titre, "Manuel-instance"), (garde, "bge-m3"), (poubelle, "Delete instance")])
    poubelle.click(); attendre(s, 1500)
    dlg = s.pg.get_by_role("alertdialog").or_(s.pg.get_by_role("dialog")).first
    dlg.get_by_role("button").filter(has_text=re.compile("Supprimer|Delete")).last.click(); attendre(s, 2500)
    s.pg.reload(); attendre(s, 3000)
    texte(s, "VLLM").click(); attendre(s, 3000)
    log("instance encore présente après suppression :", s.pg.locator(":text-is('Manuel-instance')").count())


def modeles_crayon(s):
    fournisseur(s, "VLLM")
    titre = s.pg.locator(":text-is('llm-service-chat')").first
    carte = deplier(s, titre)
    g = carte.locator(":text-is('gemma4:e4b')").first
    centre(g); g.hover(); attendre(s, 800)
    crayon = s.pg.locator("[data-testid='models-edit-gemma4:e4b']")
    rang = g.locator("xpath=ancestor::*[.//*[@data-testid='models-edit-gemma4:e4b']][1]")
    log("ligne du modèle :", rang.inner_text().replace("\n", " | "))
    badge = rang.get_by_text(re.compile(r"^(LLM|Chat)$")).first
    el = [(g, "gemma4:e4b")] + ([(badge, badge.inner_text())] if badge.count() else []) + [(crayon, "Modifier le modèle")]
    cap(s, M03, "12-crayon-modifier-le-modele", el)


def modeles_personnalise(s):
    """« … » › « Ajouter un modèle personnalisé » : fenêtre remplie, liste « Type de modèle » ouverte, refermée par « Non »."""
    fournisseur(s, "VLLM")
    carte = deplier(s, s.pg.locator(":text-is('llm-service-embed')").first)
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
    liste = dlg.get_by_role("button").filter(has_text="Sélectionner une valeur").first
    liste.click(); attendre(s, 1000)
    popover(s).get_by_text("Rerank", exact=True).first.click(); attendre(s, 600)
    popover(s).get_by_text("Fermer", exact=True).first.click(); attendre(s, 800)
    typ = lab("Type de modèle").locator("xpath=following::button[1]")
    log("type choisi :", typ.inner_text())
    cap(s, M03, "14-modele-personnalise", [(nom, "Nom du modèle"), (typ, "Type de modèle"), (jetons, "Tokens maximum"),
                                           (dlg.get_by_role("button", name="Non"), "Non"),
                                           (dlg.get_by_role("button", name="Confirmer"), "Confirmer")])
    s.pg.keyboard.press("Escape"); attendre(s, 600)
    if dlg.is_visible():
        dlg.get_by_role("button", name="Non").click(); attendre(s, 1000)
    s.pg.reload(); attendre(s, 3000)
    log("modèle d'exemple absent après rechargement :", s.pg.locator(":text-is('nom-exact-du-modele')").count() == 0)


# ---------------------------------------------------------------- chapitre 07 : actions d'une réponse (lecture seule)

def actions(s):
    s.connexion(); s.francais()
    s.aller("/chats", 3000)
    texte(s, "Démo Vélanor").click(); attendre(s, 4000)
    texte(s, "Contrat Batterix").click(); attendre(s, 4000)
    reponse = s.pg.get_by_text(re.compile(r"tokens \(\d+ input")).last
    bloc = reponse.locator("xpath=ancestor::*[.//button][1]")
    reponse.hover(); attendre(s, 400)
    s.pg.mouse.move(600, (reponse.bounding_box() or {"y": 400})["y"] - 30); attendre(s, 800)
    releve(s, "actions-reponse")
    boutons = s.pg.locator("button:visible").filter(has=s.pg.locator("svg"))
    infos = boutons.evaluate_all("l => l.map(e => { const r = e.getBoundingClientRect(); return [Math.round(r.x), Math.round(r.y), "
                                 "(e.querySelector('svg').getAttribute('class') || '').split(' ').find(c => c.startsWith('lucide-')) || ''] })")
    log("boutons visibles (x, y, icône) :", infos)
    return bloc


def actions_capture(s, indices, libelles):
    """Capture des icônes repérées (indices dans la liste des boutons visibles)."""
    boutons = s.pg.locator("button:visible").filter(has=s.pg.locator("svg"))
    cap(s, M07, "23-actions-sur-une-reponse", [(boutons.nth(i), l) for i, l in zip(indices, libelles)])


# ---------------------------------------------------------------- chapitre 10 : export et import de l'agent du chapitre

AGENT, IMPORT = "Manuel-Agent-Documentaire", "Manuel-Agent-Importe"


def agent(s, *phases):
    s.connexion(); s.francais()
    phases_de(s, "agent", phases, ("creer", "exporter", "importer"))


def agent_creer(s):
    manuels_07_15.RETENUES = {}  # gestes du chapitre 10, étapes 1 à 3, rejoués sans capture (déjà montrés)
    s.aller("/agents", 2500)
    if s.pg.get_by_text(AGENT, exact=True).count():
        log("agent déjà présent")
        return
    manuels_07_15.agents_modele(s)
    bouton(s, "Save draft").click(); attendre(s, 2000)


def fichier_export():
    f = sorted(ECHEC.glob(f"export-*{AGENT}*.json")) or sorted(ECHEC.glob("export-*.json"))
    return f[-1] if f else None


def agent_exporter(s):
    ouvrir_agent(s, None, AGENT)
    gestion = s.pg.locator("button").filter(has_text=re.compile(r"^\s*Gestion\s*$")).first
    gestion.click(); attendre(s, 1200)
    items = s.pg.get_by_role("menuitem")
    libelles = [t.strip() for t in items.all_inner_texts()]
    log("menu « Gestion » :", libelles)
    titre = s.pg.get_by_text(AGENT, exact=True).first
    cap(s, M10, "16-menu-gestion", [(gestion, "Gestion")] + [(items.nth(i), libelles[i]) for i in range(len(libelles))]
        + ([(titre, AGENT)] if titre.is_visible() else []))
    with s.pg.expect_download(timeout=20000) as dl:
        items.filter(has_text="Exporter").first.click()
    f = dl.value
    ECHEC.mkdir(parents=True, exist_ok=True)
    cible = ECHEC / f"export-{f.suggested_filename}"
    f.save_as(str(cible))
    contenu = json.loads(cible.read_text())
    texte_json = json.dumps(contenu, ensure_ascii=False)
    log("fichier téléchargé :", f.suggested_filename, "; taille", cible.stat().st_size, "octets ; clés", list(contenu)[:10],
        "; mentionne la base Démo Vélanor :", "Démo Vélanor" in texte_json or "kb_ids" in texte_json)


def agent_importer(s):
    src = fichier_export()
    nom_reel = src.name.removeprefix("export-")
    dossier = ECHEC / "import"
    dossier.mkdir(parents=True, exist_ok=True)
    f = dossier / nom_reel
    f.write_bytes(src.read_bytes())
    s.aller("/agents", 2500)
    s.pg.locator("button:has(svg.lucide-plus)").first.click(); attendre(s, 1200)
    s.pg.get_by_role("menuitem").filter(has_text="Importer un fichier JSON").first.click(); attendre(s, 1500)
    dlg = s.pg.get_by_role("dialog")
    dlg.locator("input").first.fill(IMPORT)
    dlg.locator("input[type=file]").set_input_files(str(f)); attendre(s, 1200)
    cap(s, M10, "11-importer-json", [(dlg.locator("input").first, "Nom"), (dlg.get_by_text("DSL").first, "DSL"),
                                      (dlg.get_by_text(nom_reel).first, nom_reel),
                                      (dlg.get_by_role("button", name="Enregistrer"), "Enregistrer")])
    dlg.get_by_role("button", name="Enregistrer").click(); attendre(s, 6000)
    log("après import :", s.pg.url.replace(URL, ""))
    fit(s)
    noeuds = s.pg.locator(".react-flow__node")
    log("blocs du canevas importé :", [t.replace("\n", " ")[:40] for t in noeuds.all_inner_texts()])
    s.pg.locator(".react-flow__node-toolNode").first.locator("section").last.click(); attendre(s, 1500)
    lab = lambda x: s.pg.locator("label").filter(has_text=x).first
    base = s.pg.get_by_role("button").filter(has_text="Démo Vélanor").first
    log("base de l'outil de recherche :", base.inner_text() if base.count() else "absente")
    titre = s.pg.get_by_text(IMPORT, exact=True).first
    el = ([(titre, IMPORT)] if titre.count() and titre.is_visible() else []) + [
        (s.pg.locator(".react-flow__node-agentNode").first, "bloc agent"),
        (s.pg.locator(".react-flow__node-toolNode").first, "Retrieval"),
        (lab("Récupération depuis"), "Récupération depuis"), (base, "Démo Vélanor")]
    cap(s, M10, "17-agent-importe", el)


# ---------------------------------------------------------------- chapitre 13 : inviter un collègue

def equipe(s, *phases):
    phases_de(s, "equipe", phases, ("inscrire", "inviter", "accepter", "retirer", "supprimer"))


def equipe_inscrire(s):
    from relecture_novice import invitation_inscrire
    invitation_inscrire(s)


def equipe_inviter(s):
    c = compte_invite()
    connexion_compte(s, COMPTE["email"], COMPTE["password"]); fr(s)
    page_compte(s, "Équipe")
    bouton(s, "Inviter").click(); attendre(s, 1500)
    dlg = dialogue(s)
    champ = dlg.locator("input").first
    champ.fill(c["email"])
    consigne = dlg.get_by_text("Only registered users", exact=False).first
    cap(s, M13, "02-inviter", [(champ, "Adresse e-mail"), (consigne, "consigne"), (dlg.get_by_role("button", name="Oui"), "Oui")])
    dlg.get_by_role("button", name="Oui").click(); attendre(s, 2500)
    log("après invitation :", toasts(s).all_inner_texts())
    s.pg.reload(); attendre(s, 3000)
    rang = ligne(s, c["email"])
    log("ligne du membre :", rang.inner_text().replace("\n", " | ").replace("\t", " | "))
    cellules = rang.locator("td")
    role = rang.get_by_text("Invite", exact=True).first
    cap(s, M13, "03-membre-invite", [(rang, "Manuel-Invite"), (role, "Invite"), (rang.locator("button").last, "corbeille")])


def equipe_accepter(s):
    c = compte_invite()
    connexion_compte(s, c["email"], c["password"]); fr(s)
    page_compte_invite(s)
    releve(s, "equipe-invite-2")
    rang = ligne(s, "Banc RAGFlow")
    log("ligne de l'équipe reçue :", rang.inner_text().replace("\n", " | ").replace("\t", " | "))
    rang.get_by_role("button").filter(has_text="Accepter").first.click(); attendre(s, 2500)
    log("messages :", toasts(s).all_inner_texts())
    s.pg.reload(); attendre(s, 3000)
    releve(s, "equipe-invite-2-apres")
    connexion_compte(s, COMPTE["email"], COMPTE["password"]); fr(s)
    page_compte(s, "Équipe")
    rang = ligne(s, c["email"])
    log("ligne du membre après acceptation :", rang.inner_text().replace("\n", " | ").replace("\t", " | ") if rang.count() else "absente")


def equipe_retirer(s):
    from relecture_novice import invitation_retirer
    invitation_retirer(s)


def equipe_supprimer(s):
    """Compte invité désactivé puis supprimé par l'API d'administration (pas de suppression dans l'interface ordinaire)."""
    env = Path("donnees/ragflow/ragflow.env").read_text()
    mdp = re.findall(r"^ADMIN_DEFAULT_PASSWORD=(\S+)", env, re.M)[-1]
    b = "http://rag-ragflow-server:9381/api/v1/admin"

    def appel(m, chemin, corps=None, jeton=None):
        req = urllib.request.Request(b + chemin, method=m, data=None if corps is None else json.dumps(corps).encode(),
                                     headers={"Content-Type": "application/json", **({"Authorization": jeton} if jeton else {})})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read() or b"{}"), r.headers

    _, h = appel("POST", "/login", {"email": "admin@ragflow.io", "password": base64.b64encode(mdp.encode()).decode()})
    j = h.get("Authorization")
    email = compte_invite()["email"]
    log("désactivation :", appel("PUT", f"/users/{email}/activate", {"activate_status": "off"}, j)[0].get("message"))
    log("suppression :", appel("DELETE", f"/users/{email}", None, j)[0].get("message", "")[:120].replace("\n", " "))
    log("comptes restants :", [u.get("email") for u in (appel("GET", "/users", None, j)[0].get("data") or [])])


# ---------------------------------------------------------------- repérage

def reperage(s, quoi):
    s.connexion(); s.francais()
    if quoi == "voix":
        fournisseur(s, "OpenAI-API-Compatible")
        s.pg.locator(":text-is('voix-locale')").first.click(); attendre(s, 2000); releve(s, "voix")
    elif quoi == "carte":
        fournisseur(s, "OpenAI-API-Compatible")
        rangee = s.pg.locator(":text-is('voix-locale')").first.locator("xpath=ancestor::*[.//button][1]")
        for k in range(3):
            log(k, "html :", rangee.evaluate("e => e.outerHTML")[:1500])
            log(k, "inputs page :", s.pg.locator("input:visible").count())
            rangee.locator("button").first.click(); attendre(s, 2000)
        releve(s, "carte")
    elif quoi == "plus":
        fournisseur(s, "OpenAI-API-Compatible")
        carte = deplier(s, s.pg.locator(":text-is('voix-locale')").first)
        lister = carte.get_by_role("button", name="Lister les modèles").first
        autre = lister.locator("xpath=following::button[1]")
        log("bouton voisin :", autre.evaluate("e => e.outerHTML")[:300])
        autre.click(); attendre(s, 1500)
        log("après clic « … » :", popover(s).inner_text().replace("\n", " | ") if popover(s).count() else "aucun menu")
        releve(s, "plus")
        s.pg.get_by_role("menuitem").filter(has_text="Ajouter un modèle personnalisé").first.click(); attendre(s, 1500)
        dlg = dialogue(s)
        log("fenêtre :", dlg.inner_text().replace("\n", " | "))
        releve(s, "personnalise")
        dlg.get_by_role("button").filter(has_text="Sélectionner une valeur").first.click(); attendre(s, 1000)
        log("types :", popover(s).inner_text().replace("\n", " | "))
        s.pg.keyboard.press("Escape"); attendre(s, 600)
        icone = carte.get_by_placeholder("Rechercher").locator("xpath=following::button[1]")
        log("bouton à droite de Rechercher :", icone.evaluate("e => (e.getAttribute('aria-label') || '') + ' ' + e.outerHTML.slice(0, 200)"))
    elif quoi == "actions":
        actions(s)


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
            s.pg.screenshot(path=str(ECHEC / "echec-relecture-2.png"))
            (ECHEC / "echec-relecture-2.txt").write_text(s.pg.url + "\n" + s.pg.inner_text("body"))
            sys.exit(1)
        finally:
            s.b.close()
