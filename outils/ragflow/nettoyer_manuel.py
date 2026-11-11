"""Supprime les objets créés à la souris par les scénarios de captures des manuels (noms commençant par « Manuel- »).

Option « assistants » : ne supprime que les assistants (pour rejouer la phase assistant du manuel 02).
Ne touche à rien d'autre : le jeu de démonstration (« Démo Vélanor », « Agent démo Vélanor », « Essai-KC-mind_map-1835 »)
reste en place. Usage : uv run python outils/ragflow/nettoyer_manuel.py   (sortie affichée, à archiver par l'appelant)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from client import client, http  # noqa: E402

PREFIXE = "Manuel-"
rag = client()
for c in rag.list_chats(page_size=100):
    if c.name.startswith(PREFIXE):
        rag.delete_chats(ids=[c.id]); print("assistant supprimé :", c.name)
SEULS_ASSISTANTS = sys.argv[1:] == ["assistants"]
for d in [] if SEULS_ASSISTANTS else rag.list_datasets(page_size=100):
    if d.name.startswith(PREFIXE):
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
