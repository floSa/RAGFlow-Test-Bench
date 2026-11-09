#!/usr/bin/env python3
"""Configuration de RAGFlow après installation, par l'API HTTP (bibliothèque standard seulement), idempotente.

1. compte local fictif (inscription puis connexion) ;
2. clé d'API du compte ;
3. fournisseur VLLM : une instance par serveur de LLM-Service (chat sur vllm-central, embedding sur vllm-embed) ;
4. modèles par défaut du compte (chat, embedding, transcription) ;
5. interface en français.

Identifiants : donnees/IDENTIFIANTS-LOCAUX.txt et donnees/ragflow/compte.json (ignorés par git).
Journal (secrets masqués) : outils/resultats/ragflow/configuration-<date>.log
Usage : python3 outils/ragflow/configurer.py
"""
import datetime, json, secrets, sys, urllib.error, urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
API = "http://127.0.0.1:9380/api/v1"
COMPTE = RACINE / "donnees/ragflow/compte.json"
IDENT = RACINE / "donnees/IDENTIFIANTS-LOCAUX.txt"
JOURNAL = RACINE / f"outils/resultats/ragflow/configuration-{datetime.date.today()}.log"

# Modèles de LLM-Service (branche service-vllm) ; contexte déclaré au chat : 16 384 jetons, taille commune de la série.
# Transcription (asr) : serveur de voix commun rag-speaches (faster-whisper-small), réseau rag-local.
MODELES = {
    "chat": {"fournisseur": "VLLM", "instance": "llm-service-chat", "base_url": "http://vllm-central:8000/v1",
             "model_name": "gemma4:e4b", "max_tokens": 16384},
    "embedding": {"fournisseur": "VLLM", "instance": "llm-service-embed", "base_url": "http://vllm-embed:8000/v1",
                  "model_name": "bge-m3", "max_tokens": 8192},
    "asr": {"fournisseur": "OpenAI-API-Compatible", "instance": "voix-locale", "base_url": "http://rag-speaches:8000/v1",
            "model_name": "Systran/faster-whisper-small", "max_tokens": 0},
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
    for v in (compte.get("password"), compte.get("api_key")):
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
r = appel("POST", "/users", {"email": compte["email"], "nickname": compte["nickname"], "password": compte["password"]})
log(f"inscription : {masque(r)}")
r, h = appel("POST", "/auth/login", {"email": compte["email"], "password": compte["password"]}, entetes=True)
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

for fournisseur in sorted({m["fournisseur"] for m in MODELES.values()}):
    r = appel("PUT", "/providers", {"provider_name": fournisseur}, jeton)
    log(f"fournisseur {fournisseur} : {masque(r)}")
for type_, m in MODELES.items():
    FOURNISSEUR = m["fournisseur"]
    r = appel("POST", f"/providers/{FOURNISSEUR}/instances", {
        "instance_name": m["instance"], "api_key": "sans-cle", "base_url": m["base_url"],
        "model_info": [{"model_name": m["model_name"], "model_type": [type_], "max_tokens": m["max_tokens"]}]}, jeton)
    log(f"instance {m['instance']} ({type_}) : {masque(r)}")
    r = appel("PATCH", "/models/default", {"model_provider": FOURNISSEUR, "model_instance": m["instance"],
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
