"""Fonctions partagées par les scripts d'essai RAGFlow (SDK ragflow-sdk 1.0.0 et API HTTP).

Contournements de comportements observés du SDK 1.0.0 (consignés dans outils/resultats/ragflow/) :
- `DataSet.parse_documents` peut rendre « DONE » avec 0 passage, avant la mise à jour des compteurs du document :
  `attendre_analyse` attend que `progress` vaille 1 et que les compteurs soient renseignés ;
- `Session.ask` (chat) : voir `demander`, qui reprend par `POST /api/v1/chat/completions` en cas d'échec.
"""
import json, time
from pathlib import Path

import requests
from ragflow_sdk import RAGFlow

RACINE = Path(__file__).resolve().parents[2]
BASE = "http://127.0.0.1:9380"


def cle():
    return json.loads((RACINE / "donnees/ragflow/compte.json").read_text())["api_key"]


def client():
    return RAGFlow(api_key=cle(), base_url=BASE)


def http(methode, chemin, **kw):
    r = requests.request(methode, f"{BASE}/api/v1{chemin}", headers={"Authorization": f"Bearer {cle()}"},
                         timeout=kw.pop("timeout", 600), **kw)
    return r.json()


def documents(ds_id, **params):
    d = http("GET", f"/datasets/{ds_id}/documents", params={"page_size": 100, **params})["data"]
    return d["docs"] if isinstance(d, dict) else d


def attendre_analyse(ds_id, doc_ids, delai_max=1800, pas=3):
    """Attend la fin de l'analyse : progress >= 1 et compteurs renseignés, ou échec. Renvoie {nom: état}."""
    t0, etats = time.time(), {}
    while time.time() - t0 < delai_max:
        etats = {}
        for d in documents(ds_id):
            if d["id"] not in doc_ids:
                continue
            fini = float(d.get("progress") or 0) >= 1 and (d.get("chunk_count") or 0) > 0
            echec = float(d.get("progress") or 0) < 0 or str(d.get("run")).upper() in ("FAIL", "CANCEL")
            etats[d["name"]] = {"fini": fini, "echec": echec, "progress": d.get("progress"),
                                "chunks": d.get("chunk_count"), "jetons": d.get("token_count"),
                                "message": (d.get("progress_msg") or "")[-300:]}
        if etats and all(e["fini"] or e["echec"] for e in etats.values()):
            break
        time.sleep(pas)
    return etats, time.time() - t0


def demander(chat_id, session_id, question, **extra):
    """Pose une question à un assistant par l'API HTTP (réponse complète, sans flux). Renvoie (données, durée)."""
    t = time.time()
    r = http("POST", "/chat/completions", json={"chat_id": chat_id, "session_id": session_id,
                                                "question": question, "stream": False, **extra})
    return r, time.time() - t
