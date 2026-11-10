"""Crée un dataset, téléverse un document du corpus, lance l'analyse et attend les passages (SDK ragflow-sdk 1.0.0)."""
import json, time
from ragflow_sdk import RAGFlow

cle = json.load(open("donnees/ragflow/compte.json"))["api_key"]
rag = RAGFlow(api_key=cle, base_url="http://127.0.0.1:9380")
for ds in rag.list_datasets(name="Exemple-03"):
    rag.delete_datasets(ids=[ds.id])
ds = rag.create_dataset(name="Exemple-03", parser_id="general")
doc = ds.upload_documents([{"display_name": "faq-sav.html", "blob": open("corpus/documents/faq-sav.html", "rb").read()}])[0]
ds.async_parse_documents([doc.id])
for _ in range(120):  # parse_documents peut rendre « DONE » avant la mise à jour des compteurs : attente explicite
    d = ds.list_documents(id=doc.id)[0]
    if float(d.progress or 0) >= 1 and d.chunk_count:
        break
    time.sleep(2)
print(f"dataset {ds.name} : {d.name}, {d.chunk_count} passage(s), {d.token_count} jetons")
for c in ds.list_documents(id=doc.id)[0].list_chunks()[:2]:
    print("  passage :", c.content[:100].replace("\n", " "))
