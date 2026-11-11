#!/usr/bin/env python3
"""Configuration de RAGFlow après installation, par l'API HTTP (bibliothèque standard seulement), idempotente.

1. compte local fictif (inscription puis connexion) ;
2. clé d'API du compte ;
3. fournisseur OpenAI-API-Compatible : une instance unique « llm-central » (service LLM central, LiteLLM) avec chat, embed, rerank, transcribe ;
4. modèles par défaut du compte (chat, embedding, rerank, transcription) ;
5. interface en français.

Identifiants : donnees/IDENTIFIANTS-LOCAUX.txt et donnees/ragflow/compte.json (ignorés par git).
Journal (secrets masqués) : outils/resultats/ragflow/configuration-<date>.log
Usage : python3 outils/ragflow/configurer.py
"""
import base64, datetime, json, secrets, sys, urllib.error, urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
API = "http://127.0.0.1:9380/api/v1"
COMPTE = RACINE / "donnees/ragflow/compte.json"
IDENT = RACINE / "donnees/IDENTIFIANTS-LOCAUX.txt"
JOURNAL = RACINE / f"outils/resultats/ragflow/configuration-{datetime.date.today()}.log"

# Service LLM central (LLM-Service, géré à part) : un seul point d'entrée LiteLLM, clé obligatoire lue dans .env.
# Contexte déclaré au chat : 16 384 jetons, taille commune de la série.
def lire_env():
    env = {}
    for l in (RACINE / ".env").read_text().splitlines() if (RACINE / ".env").exists() else []:
        if "=" in l and not l.lstrip().startswith("#"):
            k, v = l.split("=", 1)
            env[k.strip()] = v.strip()
    return env


ENV = lire_env()
if not ENV.get("LLM_CENTRAL_KEY"):
    sys.exit(".env absent ou LLM_CENTRAL_KEY vide : copier .env.example en .env et renseigner la clé")
CLE = ENV["LLM_CENTRAL_KEY"]
URL = ENV.get("LLM_CENTRAL_URL", "http://llm-central:8080/v1")
FOURNISSEUR_LLM = "OpenAI-API-Compatible"


def modele(type_, nom, max_tokens):
    return {"fournisseur": FOURNISSEUR_LLM, "instance": "llm-central", "base_url": URL, "model_name": nom,
            "max_tokens": max_tokens}


MODELES = {
    "chat": modele("chat", ENV.get("LLM_CENTRAL_CHAT", "chat"), 16384),
    "embedding": modele("embedding", ENV.get("LLM_CENTRAL_EMBED", "embed"), 8192),
    "rerank": modele("rerank", ENV.get("LLM_CENTRAL_RERANK", "rerank"), 8192),
    "asr": modele("asr", ENV.get("LLM_CENTRAL_TRANSCRIBE", "transcribe"), 0),
}

lignes = []


def log(msg):
    print(msg)
    lignes.append(msg)


def appel(methode, chemin, corps=None, jeton=None, entetes=False):
    req = urllib.request.Request(API + chemin, method=methode,
                                 data=None if corps is None else json.dumps(corps).encode(),
                                 headers={"Content-Type": "application/json"})
    if jeton:
        req.add_header("Authorization", jeton)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read() or b"{}")
            return (data, r.headers) if entetes else data
    except urllib.error.HTTPError as e:
        data = {"http": e.code, "corps": e.read().decode(errors="replace")[:500]}
        return (data, e.headers) if entetes else data


def masque(d):
    s = json.dumps(d, ensure_ascii=False)
    for v in (CLE, compte.get("password"), compte.get("api_key"), base64.b64encode(compte["password"].encode()).decode()):
        if v:
            s = s.replace(v, "***")
    return s[:400]


if COMPTE.exists():
    compte = json.loads(COMPTE.read_text())
else:
    compte = {"email": "banc.demo@exemple.fr", "nickname": "Banc RAGFlow", "password": secrets.token_urlsafe(14)}
    COMPTE.parent.mkdir(parents=True, exist_ok=True)
    COMPTE.write_text(json.dumps(compte, indent=2))
    COMPTE.chmod(0o600)

log(f"== configurer.py {datetime.datetime.now().isoformat(timespec='seconds')}")
# L'interface envoie RSA(base64(mot de passe)) ; le serveur déchiffre le RSA sans décoder le base64 et hache donc
# base64(mot de passe) (internal/common/password.go, DecryptPassword). Par l'API, base64(mot de passe) envoyé tel quel
# donne la même empreinte : le compte reste utilisable depuis l'interface. Un mot de passe envoyé en clair ne l'est pas.
mdp_api = base64.b64encode(compte["password"].encode()).decode()
r = appel("POST", "/users", {"email": compte["email"], "nickname": compte["nickname"], "password": mdp_api})
log(f"inscription : {masque(r)}")
r, h = appel("POST", "/auth/login", {"email": compte["email"], "password": mdp_api}, entetes=True)
jeton = h.get("Authorization")
log(f"connexion : code={r.get('code')} jeton={'reçu' if jeton else 'absent'} {masque(r) if not jeton else ''}")
if not jeton:
    sys.exit(1)

if not compte.get("api_key"):
    r = appel("POST", "/system/keys", {"name": "banc"}, jeton)
    cle = (r.get("data") or {}).get("token") or (r.get("data") or {}).get("key") if isinstance(r.get("data"), dict) else None
    log(f"clé d'API : {'créée' if cle else masque(r)}")
    if cle:
        compte["api_key"] = cle
        COMPTE.write_text(json.dumps(compte, indent=2))

# Non exécuté depuis la bascule vers le service central : la procédure à la main est dans le README (« Bascule vers le
# service LLM central »). [À tester] : une instance unique portant les quatre modèles, puis un défaut par type.
r = appel("PUT", "/providers", {"provider_name": FOURNISSEUR_LLM}, jeton)
log(f"fournisseur {FOURNISSEUR_LLM} : {masque(r)}")
r = appel("POST", f"/providers/{FOURNISSEUR_LLM}/instances", {
    "instance_name": "llm-central", "api_key": CLE, "base_url": URL,
    "model_info": [{"model_name": m["model_name"], "model_type": [t], "max_tokens": m["max_tokens"]}
                   for t, m in MODELES.items()]}, jeton)
log(f"instance llm-central : {masque(r)}")
for type_, m in MODELES.items():
    r = appel("PATCH", "/models/default", {"model_provider": FOURNISSEUR_LLM, "model_instance": m["instance"],
                                            "model_name": m["model_name"], "model_type": type_}, jeton)
    log(f"défaut {type_} : {masque(r)}")
r = appel("PATCH", "/users/me", {"language": "French"}, jeton)
log(f"langue de l'interface (French) : {masque(r)}")
r = appel("GET", "/models/default", None, jeton)
log(f"modèles par défaut : {masque(r)}")

IDENT.write_text(
    "Identifiants locaux de démonstration (fictifs, machine locale seulement)\n\n"
    f"RAGFlow — http://127.0.0.1:8088\n  courriel : {compte['email']}\n  mot de passe : {compte['password']}\n"
    f"  clé d'API : {compte.get('api_key', '(non créée)')}\n"
    "  administration (http://127.0.0.1:9381) : admin@ragflow.io, mot de passe = ADMIN_DEFAULT_PASSWORD "
    "dans donnees/ragflow/ragflow.env\n")
IDENT.chmod(0o600)
JOURNAL.parent.mkdir(parents=True, exist_ok=True)
with JOURNAL.open("a") as f:
    f.write("\n".join(lignes) + "\n")
