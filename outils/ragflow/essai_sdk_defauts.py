"""Reproduit les comportements du SDK ragflow-sdk 1.0.0 cités dans les manuels, et les consigne.
Crée un assistant temporaire relié à « Démo Vélanor », puis le supprime.
Usage : uv run python outils/ragflow/essai_sdk_defauts.py   Sortie : outils/resultats/ragflow/essai-<date>-sdk-defauts.log
"""
import datetime, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from client import RACINE, client, http  # noqa: E402

lignes = [f"== {datetime.datetime.now().isoformat(timespec='seconds')} comportements du SDK ragflow-sdk 1.0.0"]
rag = client()
ds = rag.list_datasets(name="Démo Vélanor")[0]
chat = rag.create_chat(name="Essai-sdk", dataset_ids=[ds.id], vector_similarity_weight=0.7)
try:
    sess = chat.create_session("sdk")
    g = sess.ask("Quel est le prix public du Vilaine Compact ?", stream=False)
    lignes.append(f"1. type renvoyé par Session.ask(stream=False) : {type(g).__name__}")
    try:
        g.content
    except AttributeError as e:
        lignes.append(f"   accès direct à .content : AttributeError: {e}")
    try:
        next(iter(g))
    except Exception as e:
        lignes.append(f"   next(iter(...)) pour un assistant : {type(e).__name__}: {str(e)[:150]}")
    try:
        dict(chat.prompt_config)
    except TypeError as e:
        lignes.append(f"2. dict(chat.prompt_config) : TypeError: {e} ; chat.prompt_config.to_json() -> clés {sorted(chat.prompt_config.to_json())[:4]}…")
    d = http("GET", "/chats", params={"page_size": 100})["data"]
    d = d.get("chats", d) if isinstance(d, dict) else d
    serveur = next((c for c in d if c.get("id") == chat.id), None)
    lignes.append(f"3. créé avec vector_similarity_weight=0.7 ; objet SDK : vector_similarity_weight={getattr(chat, 'vector_similarity_weight', None)}, "
                  f"keywords_similarity_weight={getattr(chat, 'keywords_similarity_weight', None)} ; "
                  f"serveur (GET /api/v1/chats) : {json.dumps({k: (serveur or {}).get(k) for k in ('vector_similarity_weight', 'keywords_similarity_weight')})}")
finally:
    rag.delete_chats(ids=[chat.id])
    lignes.append("assistant temporaire supprimé")
print("\n".join(lignes))
(RACINE / f"outils/resultats/ragflow/essai-{datetime.date.today()}-sdk-defauts.log").write_text("\n".join(lignes) + "\n")
