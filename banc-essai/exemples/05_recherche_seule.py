"""Recherche de passages sans génération (retrieval) dans le dataset Exemple-03 : utile pour régler le seuil et le top-k."""
import json
from ragflow_sdk import RAGFlow

cle = json.load(open("donnees/ragflow/compte.json"))["api_key"]
rag = RAGFlow(api_key=cle, base_url="http://127.0.0.1:9380")
ds = rag.list_datasets(name="Exemple-03")[0]
for c in rag.retrieve(question="garantie du cadre", dataset_ids=[ds.id], similarity_threshold=0.2, page_size=3):
    print(f"similarité {c.similarity:.3f} | {c.document_name} | {c.content[:90]!r}")
