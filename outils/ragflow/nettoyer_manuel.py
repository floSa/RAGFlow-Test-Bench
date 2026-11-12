"""Supprime les objets créés à la souris par les scénarios de captures des manuels (noms commençant par « Manuel- »).

Option « assistants » : ne supprime que les assistants (pour rejouer la phase assistant du manuel 02).
Couvre aussi (lot 3) : agents et pipelines d'ingestion, opérateurs de compilation, applications de recherche,
mémoires et sources de données nommés « Manuel-… ». Option « garder=<nom>,<nom> » : objets à laisser en place.
Ne touche à rien d'autre : le jeu de démonstration (« Démo Vélanor », « Agent démo Vélanor », « Essai-KC-mind_map-0816 »)
reste en place. Usage : uv run python outils/ragflow/nettoyer_manuel.py   (sortie affichée, à archiver par l'appelant)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from client import client, http  # noqa: E402

PREFIXE = "Manuel-"
rag = client()
for c in rag.list_chats(page_size=100):
    if c.name.startswith(PREFIXE) and c.name not in {n for a in sys.argv[1:] if a.startswith("garder=") for n in a[7:].split(",")}:
        rag.delete_chats(ids=[c.id]); print("assistant supprimé :", c.name)
SEULS_ASSISTANTS = "assistants" in sys.argv[1:]
GARDER = {n for a in sys.argv[1:] if a.startswith("garder=") for n in a[7:].split(",")}


def a_supprimer(nom):
    return (nom or "").startswith(PREFIXE) and nom not in GARDER


def liste(chemin, *cles, **params):
    """Liste renvoyée par l'API, quelle que soit l'enveloppe (liste directe ou dictionnaire)."""
    d = http("GET", chemin, params={"page_size": 100, **params}).get("data") or []
    for c in cles:
        if isinstance(d, dict) and c in d:
            d = d[c]
    return d if isinstance(d, list) else []


if not SEULS_ASSISTANTS:
    for cat in ("agent_canvas", "dataflow_canvas"):
        for a in liste("/agents", "canvas", canvas_category=cat):
            if a_supprimer(a.get("title")):
                print("agent ou pipeline supprimé :", a["title"], http("DELETE", f"/agents/{a['id']}").get("code"))
    for g in liste("/compilation-template-groups", "groups"):
        if a_supprimer(g.get("name")):
            print("opérateur de compilation supprimé :", g["name"],
                  http("DELETE", f"/compilation-template-groups/{g['id']}").get("code"))
    for r in liste("/searches", "search_apps", "searches"):
        if a_supprimer(r.get("name")):
            print("recherche supprimée :", r["name"], http("DELETE", f"/searches/{r['id']}").get("code"))
    for mem in liste("/memories", "memory_list", "memories"):
        if a_supprimer(mem.get("name")):
            print("mémoire supprimée :", mem["name"], http("DELETE", f"/memories/{mem['id']}").get("code"))
    for c in liste("/connectors", "connectors"):
        if a_supprimer(c.get("name")):
            print("source de données supprimée :", c["name"], http("DELETE", f"/connectors/{c['id']}").get("code"))
for d in [] if SEULS_ASSISTANTS else rag.list_datasets(page_size=100):
    if a_supprimer(d.name):
        rag.delete_datasets(ids=[d.id]); print("base supprimée :", d.name)
for fournisseur in () if SEULS_ASSISTANTS else ("VLLM", "OpenAI-API-Compatible"):
    data = http("GET", f"/providers/{fournisseur}/instances").get("data") or []
    data = data.get("instances", data) if isinstance(data, dict) else data
    for i in data if isinstance(data, list) else []:
        nom = i.get("instance_name") or i.get("name") or ""
        if nom.startswith(PREFIXE):
            r = http("DELETE", f"/providers/{fournisseur}/instances", json={"instances": [nom]})
            print("instance supprimée :", fournisseur, nom, r.get("code"))
print("restent : bases", sorted(d.name for d in rag.list_datasets(page_size=100)), "; assistants",
      sorted(c.name for c in rag.list_chats(page_size=100)))
