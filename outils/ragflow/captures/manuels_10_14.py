"""Captures des manuels 10 à 14 de RAGFlow (lot 4), tout à la souris dans l'interface en français.

Lancement : outils/communs/captures/lancer.sh outils/ragflow/captures/manuels_10_14.py <scénario> [phases...]
Scénarios : reperage (non versionné, donnees/captures-explorer), cles (manuel 10), recettes (11), qualite (12),
exploitation (13), depannage (14). Une capture par écran nouveau ; les écrans déjà montrés ailleurs sont renvoyés.
Objets créés, tous nommés « Manuel-… » (clé d'API repérée par différence, assistant, base de la recette d'ingestion),
supprimés ensuite (clé : dans le scénario ; le reste : outils/ragflow/nettoyer_manuel.py).
Le jeu de démonstration (« Démo Vélanor », « Agent démo Vélanor », « Essai-KC-mind_map-1835 ») n'est ouvert qu'en
lecture : aucune question n'est posée à l'assistant « Démo Vélanor ».
Helpers repris des lots précédents : captures.py, manuels_03_06.py, manuels_07_15.py.
"""
import re
import sys
import time
import traceback
from pathlib import Path

from playwright.sync_api import sync_playwright

from captures import Session, URL, TXT, COMPTE, cap, bouton, texte, _INVENTAIRE  # noqa: F401
from manuels_03_06 import attendre, popover, haut, centre, ouvrir_base, ligne, caviarder, ouvrir_assistant, panneau, envoyer  # noqa: F401
from manuels_07_15 import log, page_compte  # noqa: F401

ECHEC = Path("donnees/captures-explorer")


def avatar(s):
    return s.pg.locator("header a").filter(has_text="BR").first


def reperer(s, nom):
    ECHEC.mkdir(parents=True, exist_ok=True)
    s.pg.screenshot(path=str(ECHEC / f"l4-{nom}.png"))
    t = s.pg.inner_text("body")
    t = re.sub(r"ragflow-[0-9A-Za-z_-]{8,}", "ragflow-<masqué>", t)
    (ECHEC / f"l4-{nom}.txt").write_text(s.pg.url + "\n" + t + "\n== éléments ==\n" + "\n".join(s.pg.evaluate(_INVENTAIRE)))
    log("repéré :", nom)


def reperage(s, *quoi):
    quoi = quoi or ("api", "equipe", "profil", "modele", "admin")
    if "api" in quoi:
        page_compte(s, "API")
        reperer(s, "api")
        bouton(s, "Clé API").click(); attendre(s, 2000)
        reperer(s, "api-cles")
        s.pg.keyboard.press("Escape"); attendre(s, 800)
        bouton(s, "Afficher le contenu").click(); attendre(s, 2000)
        reperer(s, "api-contenu")
    if "equipe" in quoi:
        page_compte(s, "Équipe")
        bouton(s, "Inviter").click(); attendre(s, 1500)
        reperer(s, "equipe-inviter")
        s.pg.keyboard.press("Escape"); attendre(s, 800)
    if "profil" in quoi:
        page_compte(s, "Profil")
        s.pg.get_by_role("button", name="Modifier").nth(1).click(); attendre(s, 1500)
        reperer(s, "profil-fuseau")
        s.pg.keyboard.press("Escape"); attendre(s, 800)
        s.pg.reload(); attendre(s, 3000)
        s.pg.get_by_text("Modifier", exact=True).last.click(); attendre(s, 1500)
        reperer(s, "profil-mot-de-passe")
        s.pg.keyboard.press("Escape"); attendre(s, 800)
    if "modele" in quoi:
        page_compte(s, "Fournisseurs de modèles")
        reperer(s, "fournisseurs")
        s.pg.get_by_text("VLLM", exact=True).first.click(); attendre(s, 2500)
        reperer(s, "vllm")
    if "chat" in quoi:
        page_compte(s, "Fournisseurs de modèles")
        s.pg.get_by_text("VLLM", exact=True).first.click(); attendre(s, 2500)
        s.pg.get_by_text("llm-service-chat", exact=True).first.click(); attendre(s, 2000)
        g = s.pg.get_by_text("gemma4:e4b", exact=True).first
        centre(g); g.hover(); attendre(s, 800)
        reperer(s, "chat-carte")
        log("boutons de la ligne :", g.locator("xpath=ancestor::div[.//button][1]").inner_html()[:1500])
        g.locator("xpath=ancestor::div[.//button][1]").locator("button").first.click(); attendre(s, 1500)
        reperer(s, "chat-modele")
        s.pg.keyboard.press("Escape"); attendre(s, 800)
    if "admin" in quoi:
        for c in ("/admin", "/admin/login"):
            s.aller(c, 3000)
            reperer(s, "admin" + c.replace("/", "-"))



def cle_masquee(m, *noms):
    """Remplace les clés d'API (« ragflow-… ») par « ragflow-<masqué> » dans les textes de pages archivés."""
    for nom in noms:
        f = TXT / m / f"{nom}.txt"
        if f.exists():
            f.write_text(re.sub(r"ragflow-[0-9A-Za-z_-]{8,}", "ragflow-<masqué>", f.read_text()))


def dialogue(s):
    return s.pg.get_by_role("dialog").last


def toasts(s):
    return s.pg.locator("[data-sonner-toast], .ant-message-notice, [role=status]").filter(visible=True)


# ---------------------------------------------------------------- manuel 10

M10 = "10-api-et-sdk"


def api_page(s):
    """Page « API » du menu du compte, fenêtre « Clé API » (création puis suppression d'une clé), documentation."""
    m = M10
    page_compte(s, "API")
    cap(s, m, "01-page-api", [(bouton(s, "API"), "API"), (bouton(s, "Clé API"), "Clé API"),
                              (texte(s, "Serveur API").locator("xpath=.."), "Serveur API"),
                              (s.pg.locator("button:has(svg.lucide-copy)").first, "copier"),
                              (bouton(s, "Afficher le contenu"), "Afficher le contenu")])
    log("adresse affichée par « Serveur API » :", texte(s, "Serveur API").locator("xpath=..").inner_text().replace("\n", " "))
    bouton(s, "Clé API").click(); attendre(s, 2000)
    dlg = dialogue(s)
    jeton = lambda r: r.locator("td").first.inner_text().strip()
    avant = {jeton(r) for r in dlg.locator("tbody tr").all()}
    log("clés avant :", len(avant))
    bouton(s, "Créer une nouvelle clé").click(); attendre(s, 2500)
    dlg = dialogue(s)
    lignes = dlg.locator("tbody tr").all()
    nouvelles = [r for r in lignes if jeton(r) not in avant]
    log("clés après création :", len(lignes), "; nouvelles :", len(nouvelles))
    neuve = nouvelles[0]
    cap(s, m, "02-cles-api", [(neuve, "nouvelle clé"), (dlg.get_by_text("Créé", exact=True).first, "Créé"),
                              (neuve.locator("button").first, "copier"), (neuve.locator("button").last, "supprimer"),
                              (bouton(s, "Créer une nouvelle clé"), "Créer une nouvelle clé")],
        masques=[r.locator("td").first for r in lignes])
    cle_masquee(m, "02-cles-api")
    neuve.locator("button").last.click(); attendre(s, 1500)
    conf = s.pg.get_by_role("dialog").filter(has_text="Êtes-vous sûr")
    log("confirmation de suppression :", conf.inner_text().replace("\n", " | "))
    cap(s, m, "03-supprimer-la-cle", [(conf.get_by_role("button", name="Non"), "Non"),
                                      (conf.get_by_role("button", name="Supprimer"), "Supprimer")],
        clip=conf.bounding_box())  # cadré sur la confirmation : les clés de la fenêtre restent hors champ
    cle_masquee(m, "03-supprimer-la-cle")
    conf.get_by_role("button", name="Supprimer").click(); attendre(s, 2000)
    fen = s.pg.get_by_role("dialog").filter(has_text="Créer une nouvelle clé")
    restants = {jeton(r) for r in fen.locator("tbody tr").all()}
    log("clés après suppression :", len(restants), "; identiques au départ :", restants == avant)
    fen.locator("button:has(svg.lucide-x)").first.click(); attendre(s, 1000)
    bouton(s, "Afficher le contenu").click(); attendre(s, 2000)
    log("sommaire de la documentation :", s.pg.locator("body").inner_text().split("Masquer le contenu", 1)[-1][:1500].replace("\n", " | "))
    cap(s, m, "04-documentation", [(bouton(s, "Masquer le contenu"), "Masquer le contenu"),
                                   (texte(s, "Migrate to 1.0"), "Migrate to 1.0"),
                                   (texte(s, "OpenAI-Compatible API"), "OpenAI-Compatible API"),
                                   (texte(s, "DATASET MANAGEMENT"), "DATASET MANAGEMENT")])


def cles(s, *phases):
    api_page(s)


# ---------------------------------------------------------------- manuel 11

M11 = "11-recettes"


def recettes_demo(s):
    """Recette 1 : base et assistant « Démo Vélanor » (lecture seule, aucune question posée)."""
    m = M11
    ouvrir_base(s, "Démo Vélanor")
    log("base Démo Vélanor :", s.pg.locator("body").inner_text()[:1500].replace("\n", " | "))
    th = lambda x: s.pg.locator("th").filter(has_text=x).first
    cap(s, m, "01-base-demo", [(ligne(s, "contrat-batterix-scan.pdf"), "contrat-batterix-scan.pdf"),
                               (ligne(s, "message-vocal-production.mp3"), "message-vocal-production.mp3"),
                               (th("Nombre de segments"), "Nombre de segments"), (th("Analyser"), "Analyser")])
    ouvrir_assistant(s, "Démo Vélanor")
    if s.pg.get_by_text("Paramètres du chat", exact=True).is_visible():
        s.pg.locator("button:has(svg.lucide-panel-right-close)").last.click(); attendre(s, 1500)
    conv = lambda x: s.pg.get_by_text(x, exact=True).first
    conv("Contrat Batterix").click(); attendre(s, 3000)
    log("conversation Contrat Batterix :", s.pg.locator("main, body").last.inner_text()[-1500:].replace("\n", " | "))
    rep = s.pg.get_by_text(re.compile("212 euros")).last
    cap(s, m, "02-assistant-demo", [(conv("Contrat Batterix"), "Contrat Batterix"), (conv("Objectifs 2026"), "Objectifs 2026"),
                                    (conv("Audit fournisseur"), "Audit fournisseur"), (rep, "réponse citée")])


def recettes_ingestion(s):
    """Recette 2 : base « Manuel-Ingestion » remplie par outils/ragflow/manuels_10_14_preparer.py ingestion."""
    m = M11
    ouvrir_base(s, "Manuel-Ingestion")
    log("base Manuel-Ingestion :", s.pg.locator("body").inner_text()[:1200].replace("\n", " | "))
    th = lambda x: s.pg.locator("th").filter(has_text=x).first
    cap(s, m, "03-base-ingestion", [(ligne(s, "cse-2025-10-14.md"), "cse-2025-10-14.md"), (ligne(s, "faq-sav.html"), "faq-sav.html"),
                                    (ligne(s, "procedure-batteries.docx"), "procedure-batteries.docx"),
                                    (th("Nombre de segments"), "Nombre de segments")])


def recettes(s, *phases):
    for ph in phases or ("demo", "ingestion"):
        log("== phase", ph)
        globals()["recettes_" + ph](s)


# ---------------------------------------------------------------- manuel 12

M12 = "12-qualite-et-performances"
CHAT = "Manuel-Reglages"
Q_PENALITES = "Quel est le plafond des pénalités de retard du contrat Batterix ?"


def nouvelle_conversation(s):
    ouvrir_assistant(s, CHAT)
    if s.pg.get_by_text("Paramètres du chat", exact=True).is_visible():
        s.pg.locator("button:has(svg.lucide-panel-right-close)").last.click(); attendre(s, 1500)
    texte(s, "Conversations").locator("xpath=following::button[1]").click(); attendre(s, 2000)


def qualite_jetons(s):
    """Jetons et durée d'une réponse, en gros plan."""
    m = M12
    nouvelle_conversation(s)
    envoyer(s, Q_PENALITES)
    jetons = s.pg.get_by_text(re.compile(r"tokens \(\d+ input")).last
    renvoi = s.pg.locator("[data-state]").filter(has_text=re.compile(r"^\[\d+\]$")).last
    rb = jetons.locator("xpath=../..").bounding_box()
    clip = {"x": max(0, rb["x"] - 40), "y": max(0, rb["y"] - 40), "width": min(1440 - max(0, rb["x"] - 40), rb["width"] + 80),
            "height": min(900 - max(0, rb["y"] - 40), rb["height"] + 80)}
    log("ligne des jetons :", jetons.inner_text(), "; zone :", clip)
    elements = [(jetons, "jetons et durée")] + ([(renvoi, "renvoi")] if renvoi.count() else [])
    cap(s, m, "01-jetons-et-duree", elements, clip=clip)


def ouvrir_modele_chat(s):
    page_compte(s, "Fournisseurs de modèles")
    s.pg.get_by_text("VLLM", exact=True).first.click(); attendre(s, 2500)
    s.pg.get_by_text("llm-service-chat", exact=True).first.click(); attendre(s, 2000)
    g = s.pg.get_by_text("gemma4:e4b", exact=True).first
    centre(g); g.hover(); attendre(s, 800)
    s.pg.locator("[data-testid='models-edit-gemma4:e4b']").click(); attendre(s, 1500)
    return dialogue(s)


def qualite_contexte(s):
    """Fenêtre « Modifier le modèle » : « Tokens maximum », taille de contexte déclarée (refermée par « Non »)."""
    m = M12
    dlg = ouvrir_modele_chat(s)
    lab = lambda x: dlg.locator("label").filter(has_text=x).first
    tokens = lab("Tokens maximum").locator("xpath=following::input[1]")
    log("fenêtre Modifier le modèle :", dlg.inner_text().replace("\n", " | "), "; Tokens maximum =", tokens.input_value())
    cap(s, m, "02-tokens-maximum", [(lab("Type de modèle"), "Type de modèle"), (tokens, "Tokens maximum"),
                                    (dlg.get_by_text("Appel d'outil").first, "Appel d'outil"),
                                    (dlg.get_by_role("button", name="Non"), "Non"), (dlg.get_by_role("button", name="Confirmer"), "Confirmer")])
    dlg.get_by_role("button", name="Non").click(); attendre(s, 1000)


def qualite(s, *phases):
    for ph in phases or ("jetons", "contexte"):
        log("== phase", ph)
        globals()["qualite_" + ph](s)


# ---------------------------------------------------------------- manuel 13

M13 = "13-exploitation"
INVITE_FICTIF = "manuel.invite@exemple.fr"
INVITE_REEL = "admin@ragflow.io"


def exploitation_equipe(s):
    """Menu du compte et page « Équipe » ; invitation refusée (adresse non inscrite), puis invitation d'un compte
    inscrit (compte d'administration local), retirée aussitôt."""
    m = M13
    page_compte(s, "Équipe")
    cap(s, m, "01-equipe", [(avatar(s), "avatar"), (bouton(s, "Équipe"), "Équipe"),
                            (texte(s, "Membres de l'équipe"), "Membres de l'équipe"), (bouton(s, "Inviter"), "Inviter"),
                            (texte(s, "Équipes rejointes"), "Équipes rejointes"), (bouton(s, "Déconnexion"), "Déconnexion")])
    bouton(s, "Inviter").click(); attendre(s, 1500)
    dlg = dialogue(s)
    champ = dlg.locator("input").first
    champ.fill(INVITE_FICTIF)
    dlg.get_by_role("button", name="Oui").click(); attendre(s, 1200)
    log("après invitation de", INVITE_FICTIF, ": messages", toasts(s).all_inner_texts(), "; fenêtre ouverte :", champ.is_visible())
    el = []
    if champ.is_visible():
        el += [(champ, "Adresse e-mail"), (dlg.get_by_text("Only registered users", exact=False).first, "consigne"),
               (dlg.get_by_role("button", name="Oui"), "Oui")]
    if toasts(s).count():
        el.append((toasts(s).last, "message"))
    cap(s, m, "02-invitation-refusee", el)
    if not champ.is_visible():
        bouton(s, "Inviter").click(); attendre(s, 1500)
        dlg = dialogue(s); champ = dlg.locator("input").first
    champ.fill(INVITE_REEL)
    dlg.get_by_role("button", name="Oui").click(); attendre(s, 2500)
    log("après invitation de", INVITE_REEL, ": messages", toasts(s).all_inner_texts())
    if dialogue(s).count() and dialogue(s).is_visible():
        s.pg.keyboard.press("Escape"); attendre(s, 800)
    s.pg.reload(); attendre(s, 3000)
    rang = ligne(s, INVITE_REEL)
    if not rang.count():
        log("membre absent de la liste après invitation :", s.pg.locator("body").inner_text()[-800:].replace("\n", " | "))
        return
    log("ligne du membre :", rang.inner_text().replace("\n", " | ").replace("\t", " | "))
    th = lambda x: s.pg.locator("th").filter(has_text=x).first
    cap(s, m, "03-membre-invite", [(rang, "membre invité"), (th("Rôle"), "Rôle"), (rang.locator("button").last, "Action")])
    rang.locator("button").last.click(); attendre(s, 1500)
    conf = s.pg.get_by_role("alertdialog").or_(s.pg.get_by_role("dialog")).or_(s.pg.locator("[data-radix-popper-content-wrapper]")).filter(visible=True)
    if conf.count():
        log("confirmation du retrait :", conf.last.inner_text().replace("\n", " | "))
        conf.last.get_by_role("button").filter(has_text=re.compile("Oui|Supprimer|Confirmer|OK|Retirer")).last.click(); attendre(s, 2000)
    s.pg.reload(); attendre(s, 3000)
    log("membre encore présent après retrait :", bool(ligne(s, INVITE_REEL).count()))


def exploitation_profil(s):
    """Page « Profil » ; fenêtres « Edit Time Zone » (capturée) et « Edit Password » (relevée), refermées sans enregistrer."""
    m = M13
    page_compte(s, "Profil")
    lab = lambda x: s.pg.locator("label").filter(has_text=x).first
    cap(s, m, "04-profil", [(lab("Nom d'utilisateur"), "Nom d'utilisateur"), (bouton(s, "Télécharger"), "Télécharger"),
                            (lab("Fuseau horaire"), "Fuseau horaire"), (lab("Adresse e-mail"), "Adresse e-mail"),
                            (lab("Mot de passe"), "Mot de passe")])
    s.pg.get_by_text("Modifier", exact=True).nth(1).click(); attendre(s, 1500)
    dlg = dialogue(s)
    choix = dlg.get_by_role("combobox").first
    if not choix.count():
        choix = dlg.locator("button").filter(has_text="GMT").first
    cap(s, m, "05-fuseau-horaire", [(choix, "Fuseau horaire"), (dlg.get_by_role("button", name="Annuler"), "Annuler"),
                                    (dlg.get_by_role("button", name="Enregistrer"), "Enregistrer")])
    choix.click(); attendre(s, 1200)
    log("fuseaux proposés (début) :", popover(s).inner_text().replace("\n", " | ")[:500] if popover(s).count() else "liste non trouvée")
    s.pg.keyboard.press("Escape"); attendre(s, 600)
    if dialogue(s).count() and dialogue(s).is_visible():
        dialogue(s).get_by_role("button", name="Annuler").click(); attendre(s, 800)
    s.pg.get_by_text("Modifier", exact=True).last.click(); attendre(s, 1500)
    log("fenêtre du mot de passe :", dialogue(s).inner_text().replace("\n", " | "))
    dialogue(s).get_by_role("button", name="Annuler").click(); attendre(s, 800)
    s.aller("/admin", 3000)
    log("adresse /admin :", s.pg.locator("body").inner_text()[:200].replace("\n", " | "))


def exploitation(s, *phases):
    for ph in phases or ("equipe", "profil"):
        log("== phase", ph)
        globals()["exploitation_" + ph](s)


# ---------------------------------------------------------------- manuel 14

M14 = "14-depannage"
Q_HORS_SUJET = "Quelle est la capitale de l'Australie ?"


def depannage_connexion(s):
    """Connexion refusée : mot de passe faux (déconnexion puis nouvel essai), puis reconnexion normale."""
    m = M14
    page_compte(s, "Profil")
    bouton(s, "Déconnexion").click(); attendre(s, 3000)
    if "login" not in s.pg.url:
        s.aller("/login", 3000)
    email = s.pg.locator("input[name=email]:visible, input[type=email]:visible").first
    mdp = s.pg.locator("input[type=password]:visible").first
    email.fill(COMPTE["email"]); mdp.fill("mot-de-passe-faux")
    envoi = s.pg.locator("button[type=submit]:visible").first
    envoi.click()
    msg = toasts(s)
    msg.first.wait_for(timeout=15000); attendre(s, 400)
    log("connexion refusée :", msg.all_inner_texts(), "; adresse :", s.pg.url.replace(URL, ""))
    cap(s, m, "01-connexion-refusee", [(email, "E-mail"), (mdp, "Mot de passe"), (envoi, envoi.inner_text().strip() or "connexion"),
                                       (msg.last, "message d'erreur")])
    attendre(s, 4000)
    s.connexion()


def depannage_contexte(s):
    """Réponse « **ERROR**: prompt uses … » : contexte déclaré réduit par outils/ragflow/contexte.py avant cette phase."""
    m = M14
    nouvelle_conversation(s)
    zone = s.pg.get_by_placeholder("Saisissez votre message ici...")
    zone.fill(Q_PENALITES)
    t0 = time.time()
    s.pg.get_by_role("button", name="Send message").click()
    err = s.pg.get_by_text(re.compile("ERROR")).last
    err.wait_for(timeout=180000); attendre(s, 3000)
    log(f"réponse d'erreur après {time.time() - t0:.1f} s :", err.inner_text()[:400])
    el = [(err, "réponse d'erreur")]
    if s.pg.get_by_text(re.compile(r"tokens \(\d+ input")).count():
        el.append((s.pg.get_by_text(re.compile(r"tokens \(\d+ input")).last, "jetons"))
    cap(s, m, "02-erreur-de-contexte", el)


def depannage_introuvable(s):
    """Réponse « not found » à une question hors du corpus (contexte remis à 16384), puis adresse inconnue (/admin)."""
    m = M14
    nouvelle_conversation(s)
    envoyer(s, Q_HORS_SUJET)
    rep = s.pg.get_by_text(re.compile("not found in the dataset")).last
    log("réponse :", rep.inner_text()[:300])
    cap(s, m, "03-reponse-not-found", [(rep, "réponse"), (s.pg.get_by_text(re.compile(r"tokens \(\d+ input")).last, "jetons et durée")])
    s.aller("/admin", 3000)
    b = s.pg.get_by_role("button").filter(has_text="Business").first
    cap(s, m, "04-page-introuvable", [(texte(s, "404"), "404"), (texte(s, "Page not found", exact=False), "Page not found"), (b, "Business")])
    b.click(); attendre(s, 2500)
    log("après « Business » :", s.pg.url.replace(URL, ""))


def depannage(s, *phases):
    for ph in phases or ("connexion", "contexte", "introuvable"):
        log("== phase", ph)
        globals()["depannage_" + ph](s)


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
            s.pg.screenshot(path=str(ECHEC / "echec-lot4.png"))
            (ECHEC / "echec-lot4.txt").write_text(s.pg.url + "\n" + s.pg.inner_text("body"))
            sys.exit(1)
        finally:
            s.b.close()
