"""Vérification fonctionnelle minimale après installation : import d'un document, une question, une citation.

Passe par le SDK ragflow-sdk 1.0.0 ; si `Session.ask` du SDK échoue, l'échec est consigné et la question est reposée
par l'API HTTP (`POST /api/v1/chat/completions`). Les objets créés (dataset et assistant « Essai-installation »)
sont supprimés à la fin.
Usage : uv run python outils/ragflow/verif_minimale.py   (sortie : outils/resultats/ragflow/installation-<date>-verif.log)
"""
import datetime, json, sys, time, traceback
from pathlib import Path

import requests
from ragflow_sdk import RAGFlow

sys.path.insert(0, str(Path(__file__).resolve().parent))
from client import attendre_analyse

RACINE = Path(__file__).resolve().parents[2]
BASE = "http://127.0.0.1:9380"
CLE = json.loads((RACINE / "donnees/ragflow/compte.json").read_text())["api_key"]
SORTIE = RACINE / f"outils/resultats/ragflow/installation-{datetime.date.today()}-verif.log"
lignes = []


def log(m):
    print(m)
    lignes.append(str(m))


rag = RAGFlow(api_key=CLE, base_url=BASE)
for ds in rag.list_datasets(name="Essai-installation"):
    rag.delete_datasets(ids=[ds.id])
for c in rag.list_chats(name="Essai-installation"):
    rag.delete_chats(ids=[c.id])

t0 = time.time()
ds = rag.create_dataset(name="Essai-installation")
log(f"dataset créé : {ds.id} gabarit={ds.parser_id} embedding={getattr(ds, 'embedding_model', '?')}")
doc_path = RACINE / "corpus/documents/cse-2025-10-14.md"
docs = ds.upload_documents([{"display_name": doc_path.name, "blob": doc_path.read_bytes()}])
log(f"document téléversé : {docs[0].name}")
t1 = time.time()
etat = ds.parse_documents([d.id for d in docs])
log(f"SDK parse_documents : {etat} en {time.time() - t1:.1f} s")
d = ds.list_documents(id=docs[0].id)[0]
log(f"document juste après : run={d.run} progress={d.progress} chunks={d.chunk_count} jetons={d.token_count}")
etats, duree = attendre_analyse(ds.id, [x.id for x in docs])
log(f"attente des compteurs (client.attendre_analyse) : {etats} après {duree:.1f} s de plus")

chat = rag.create_chat(name="Essai-installation", dataset_ids=[ds.id])
log(f"assistant créé : {chat.id} llm={getattr(chat, 'llm', None) or getattr(chat, 'llm_id', None)}")
sess = chat.create_session("verif")
question = "Quelle est la date de la réunion du CSE et quels sujets ont été abordés ?"
log(f"question : {question}")
reponse = None
try:
    t2 = time.time()
    msg = next(iter(sess.ask(question, stream=False)))  # ask est un générateur, même sans flux
    reponse = {"answer": msg.content, "reference": getattr(msg, "reference", None)}
    log(f"SDK Session.ask : réponse en {time.time() - t2:.1f} s")
except Exception as e:
    log(f"SDK Session.ask : ÉCHEC {type(e).__name__}: {str(e)[:300]}")
    t2 = time.time()
    r = requests.post(f"{BASE}/api/v1/chat/completions", headers={"Authorization": f"Bearer {CLE}"},
                      json={"chat_id": chat.id, "session_id": sess.id, "question": question, "stream": False}, timeout=300)
    log(f"HTTP POST /api/v1/chat/completions : statut {r.status_code} en {time.time() - t2:.1f} s")
    data = r.json()
    if data.get("code") == 0:
        reponse = data["data"]
    else:
        log(f"réponse : {json.dumps(data, ensure_ascii=False)[:500]}")
if reponse:
    log(f"réponse : {reponse.get('answer')}")
    ref = reponse.get("reference") or {}
    chunks = ref.get("chunks", []) if isinstance(ref, dict) else ref
    log(f"citations : {len(chunks)} passage(s)")
    for c in chunks[:3]:
        if isinstance(c, dict):
            log(f"  - {c.get('document_name')} | positions={c.get('positions')} | {str(c.get('content'))[:120]!r}")
        else:
            log(f"  - {c}")

rag.delete_chats(ids=[chat.id])
rag.delete_datasets(ids=[ds.id])
log(f"nettoyage : assistant et dataset d'essai supprimés ; durée totale {time.time() - t0:.1f} s")
SORTIE.write_text("\n".join(lignes) + "\n")
