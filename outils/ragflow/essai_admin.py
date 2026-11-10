"""API d'administration (port 9381) : connexion du compte admin@ragflow.io, version, utilisateurs, services.
Mot de passe : ADMIN_DEFAULT_PASSWORD de donnees/ragflow/ragflow.env, envoyé en base64 comme le fait l'interface.
Usage : uv run python outils/ragflow/essai_admin.py   Sortie : outils/resultats/ragflow/essai-<date>-admin.log
"""
import base64, datetime, json, re
from pathlib import Path

import requests

RACINE = Path(__file__).resolve().parents[2]
env = (RACINE / "donnees/ragflow/ragflow.env").read_text()
mdp = re.findall(r"^ADMIN_DEFAULT_PASSWORD=(\S+)", env, re.M)[-1]
B = "http://127.0.0.1:9381/api/v1/admin"
lignes = [f"== {datetime.datetime.now().isoformat(timespec='seconds')} API d'administration"]
for essai, motdepasse in (("base64", base64.b64encode(mdp.encode()).decode()), ("clair", mdp)):
    r = requests.post(f"{B}/login", json={"email": "admin@ragflow.io", "password": motdepasse}, timeout=30)
    jeton = r.headers.get("Authorization")
    lignes.append(f"connexion (mot de passe en {essai}) : HTTP {r.status_code}, code {r.json().get('code')}, "
                  f"jeton {'reçu' if jeton else 'absent'} ; {r.json().get('message')!r}")
    if jeton:
        break
h = {"Authorization": jeton} if jeton else {}
for chemin in ("/version", "/users", "/services", "/hardware"):
    r = requests.get(B + chemin, headers=h, timeout=30)
    corps = json.dumps(r.json(), ensure_ascii=False)
    corps = re.sub(r'"(password|access_token|api_key)":\s*"[^"]*"', r'"\1": "***"', corps)
    lignes.append(f"GET {chemin} : HTTP {r.status_code} ; {corps[:600]}")
print("\n".join(lignes))
(RACINE / f"outils/resultats/ragflow/essai-{datetime.date.today()}-admin.log").write_text("\n".join(lignes) + "\n")
