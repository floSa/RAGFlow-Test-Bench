"""Jeu de démonstration laissé en place à la fin de la mission.

- base de connaissances « Démo Vélanor » : corpus complet, gabarit General ;
- assistant « Démo Vélanor » : réglages du meilleur banc (poids des vecteurs 0,7, top_n 8), réponse vide en français ;
- trois conversations exemples avec citations (scan, multi-documents, anglais).
Idempotent : les objets « Démo Vélanor » existants sont recréés.
Usage : uv run python outils/ragflow/demo.py   Journal : outils/resultats/ragflow/demo-<date>.log
"""
import datetime, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from client import RACINE, attendre_analyse, client, demander  # noqa: E402

NOM = "Démo Vélanor"
QUESTIONS = [
    ("Contrat Batterix", "Quel est le prix unitaire des batteries et le délai de livraison prévus par le contrat Batterix ?"),
    ("Objectifs 2026", "Quel chiffre d'affaires Vélanor vise-t-elle en 2026 et combien d'embauches sont prévues ?"),
    ("Audit fournisseur", "What overall score did Batterix get at the supplier audit, and what was the cell defect rate?"),
]
lignes = [f"== {datetime.datetime.now().isoformat(timespec='seconds')} jeu de démonstration"]


def log(m):
    print(m, flush=True)
    lignes.append(m)


rag = client()
for c in rag.list_chats(name=NOM):
    rag.delete_chats(ids=[c.id])
for d in rag.list_datasets(name=NOM):
    rag.delete_datasets(ids=[d.id])
ds = rag.create_dataset(name=NOM, parser_id="general")
fichiers = sorted(f for f in (RACINE / "corpus/documents").iterdir() if f.is_file())
docs = ds.upload_documents([{"display_name": f.name, "blob": f.read_bytes()} for f in fichiers])
ds.async_parse_documents([d.id for d in docs])
etats, duree = attendre_analyse(ds.id, [d.id for d in docs], delai_max=3600)
log(f"base de connaissances {NOM} : {len(docs)} documents, {sum(e['chunks'] or 0 for e in etats.values())} passages, "
    f"analyse en {duree:.0f} s")
chat = rag.create_chat(name=NOM, dataset_ids=[ds.id], top_n=8, vector_similarity_weight=0.7)
pc = chat.prompt_config.to_json()  # objet Base du SDK
pc["empty_response"] = "Aucune information pertinente n'a été trouvée dans les documents."
pc["prologue"] = "Bonjour, je réponds aux questions sur les documents fictifs de Vélanor, avec mes sources."
chat.update({"prompt_config": pc})
log(f"assistant {NOM} : top_n 8, poids des vecteurs 0,7, réponse vide et accueil en français")
for titre, q in QUESTIONS:
    sess = chat.create_session(titre)
    r, d = demander(chat.id, sess.id, q)
    data = r.get("data") or {}
    docs_cites = sorted({c.get("document_name") for c in (data.get("reference") or {}).get("chunks") or []})
    log(f"conversation « {titre} » ({d:.1f} s) : {q}\n  réponse : {data.get('answer')!r}\n  documents cités : {docs_cites}")
(RACINE / f"outils/resultats/ragflow/demo-{datetime.date.today()}.log").write_text("\n".join(lignes) + "\n")
