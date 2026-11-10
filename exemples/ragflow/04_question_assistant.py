"""Crée un assistant lié au dataset Exemple-03 et pose une question par l'API HTTP (réponse et citations).
Session.ask du SDK 1.0.0 appelle /api/v1/chats/<id>/completions, qui répond 404 : la question passe par
POST /api/v1/chat/completions."""
import json
import requests
from ragflow_sdk import RAGFlow

cle = json.load(open("donnees/ragflow/compte.json"))["api_key"]
rag = RAGFlow(api_key=cle, base_url="http://127.0.0.1:9380")
ds = rag.list_datasets(name="Exemple-03")[0]
for c in rag.list_chats(name="Exemple-04"):
    rag.delete_chats(ids=[c.id])
chat = rag.create_chat(name="Exemple-04", dataset_ids=[ds.id])
session = chat.create_session("exemple")
r = requests.post("http://127.0.0.1:9380/api/v1/chat/completions", headers={"Authorization": f"Bearer {cle}"},
                  json={"chat_id": chat.id, "session_id": session.id, "stream": False,
                        "question": "Combien de temps le cadre est-il garanti ?"}, timeout=120).json()
print("réponse :", r["data"]["answer"])
for c in r["data"]["reference"]["chunks"]:
    print("source :", c["document_name"], "|", c["content"][:80].replace("\n", " "))
