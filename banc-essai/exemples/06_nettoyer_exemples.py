"""Supprime l'assistant et le dataset créés par les exemples 03 et 04."""
import json
from ragflow_sdk import RAGFlow

cle = json.load(open("donnees/ragflow/compte.json"))["api_key"]
rag = RAGFlow(api_key=cle, base_url="http://127.0.0.1:9380")
chats = rag.list_chats(name="Exemple-04"); rag.delete_chats(ids=[c.id for c in chats]) if chats else None
dss = rag.list_datasets(name="Exemple-03"); rag.delete_datasets(ids=[d.id for d in dss]) if dss else None
print(f"supprimés : {len(chats)} assistant(s), {len(dss)} dataset(s)")
