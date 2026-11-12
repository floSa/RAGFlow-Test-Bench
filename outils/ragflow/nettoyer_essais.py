"""Nettoyage des artefacts d'essai dans RAGFlow, sans toucher au jeu de démonstration.

Gardés : base et assistant « Démo Vélanor », agent « Agent démo Vélanor », base « Essai-KC-mind_map-0816 »
(carte mentale montrée au manuel 07) avec son pipeline et son groupe de gabarits.
Supprimés : bases et assistants « Banc-* », autres bases « Essai-* » et « Exemple-* », pipelines et groupes de
compilation des autres essais.
Usage : uv run python outils/ragflow/nettoyer_essais.py   Sortie : outils/resultats/ragflow/nettoyage-<date>.log
"""
import datetime, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from client import RACINE, client, http  # noqa: E402

GARDER_BASES = {"Démo Vélanor", "Essai-KC-mind_map-0816"}
GARDER_CHATS = {"Démo Vélanor"}
GARDER_AGENTS = {"Agent démo Vélanor", "Essai-KC-mind_map-0816"}
lignes = [f"== {datetime.datetime.now().isoformat(timespec='seconds')} nettoyage des essais"]
rag = client()
for c in rag.list_chats():
    if c.name not in GARDER_CHATS:
        rag.delete_chats(ids=[c.id]); lignes.append(f"assistant supprimé : {c.name}")
for d in rag.list_datasets():
    if d.name not in GARDER_BASES:
        rag.delete_datasets(ids=[d.id]); lignes.append(f"base supprimée : {d.name}")
data = http("GET", "/agents", params={"page_size": 100}).get("data") or {}
agents = data.get("canvas", data) if isinstance(data, dict) else data
for a in agents if isinstance(agents, list) else []:
    if a.get("title") not in GARDER_AGENTS:
        r = http("DELETE", f"/agents/{a['id']}", json={}); lignes.append(f"agent ou pipeline supprimé : {a.get('title')} ({r.get('code')})")
g = http("GET", "/compilation-template-groups").get("data") or []
g = g.get("groups", g) if isinstance(g, dict) else g
for grp in g if isinstance(g, list) else []:
    if not str(grp.get("name", "")).startswith("Essai-KC-mind_map-0816"):
        r = http("DELETE", f"/compilation-template-groups/{grp['id']}", json={})
        lignes.append(f"groupe de compilation supprimé : {grp.get('name')} ({r.get('code')})")
lignes.append(f"restent : bases {sorted(d.name for d in rag.list_datasets())} ; assistants {sorted(c.name for c in rag.list_chats())} ; "
              f"agents {sorted(a.title for a in rag.list_agents())}")
print("\n".join(lignes))
(RACINE / f"outils/resultats/ragflow/nettoyage-{datetime.date.today()}.log").write_text("\n".join(lignes) + "\n")
