"""Adaptateur du banc commun (outils/communs/banc/commun.py) pour RAGFlow v1.0.0.

Indexation : dataset « Banc-<gabarit> » (gabarit General par défaut), corpus complet téléversé par le SDK, analyse
lancée sur tous les documents, attente de la fin (outils/ragflow/client.py, attendre_analyse).
Questions : assistant de chat « Banc-<étiquette> » lié au dataset ; une session neuve par question (aucun historique) ;
question posée par l'API HTTP POST /api/v1/chat/completions (Session.ask du SDK 1.0.0 répond 404 pour un assistant).
Citations : reference.chunks (document_name ; une citation par page couverte, tirée de positions).

Usage : uv run python outils/ragflow/banc.py --etiquette defaut [--gabarit general] [--reindexer] [--limite N]
        [--top-n 6] [--seuil 0.1] [--poids-vecteurs 0.3] [--agentic] [--juge]
Sortie : outils/resultats/ragflow/banc-<date>-<étiquette>.json et .md
"""
import argparse, json, sys, time
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
sys.path.insert(0, str(ICI.parent / "communs/banc"))
import commun  # noqa: E402
from client import attendre_analyse, client, demander, documents, http  # noqa: E402

APP = ["rag-ragflow-server", "rag-ragflow-es01", "rag-ragflow-mysql", "rag-ragflow-minio", "rag-ragflow-kvrocks",
       "rag-ragflow-nats"]
MODELES = ["vllm-central", "vllm-embed", "rag-speaches"]


def contexte_declare():
    """max_tokens déclaré du modèle de chat dans RAGFlow (réglé par outils/ragflow/contexte.py)."""
    try:
        modeles = http("GET", "/providers/VLLM/instances/llm-service-chat/models")["data"]
        return next(m["max_tokens"] for m in modeles if m["name"] == "gemma4:e4b")
    except Exception as e:
        return f"inconnu ({e})"


class AdaptateurRAGFlow:
    nom = "ragflow"

    def __init__(self, gabarit="general", etiquette="defaut", reindexer=False, reglages=None, extra=None):
        self.rag, self.gabarit, self.etiquette = client(), gabarit, etiquette
        self.reglages, self.extra = reglages or {}, extra or {}
        nom = f"Banc-{gabarit}"
        existants = self.rag.list_datasets(name=nom)
        if existants and reindexer:
            self.rag.delete_datasets(ids=[d.id for d in existants])
            existants = []
        self.ds = existants[0] if existants else None
        self.chat = None

    def indexer(self, fichiers):
        self.ds = self.rag.create_dataset(name=f"Banc-{self.gabarit}", parser_id=self.gabarit)
        docs = self.ds.upload_documents([{"display_name": f.name, "blob": f.read_bytes()} for f in fichiers])
        ids = [d.id for d in docs]
        self.ds.async_parse_documents(ids)
        etats, duree = attendre_analyse(self.ds.id, ids, delai_max=3600)
        print(json.dumps(etats, ensure_ascii=False, indent=1), flush=True)
        return {"dataset": self.ds.id, "gabarit": self.gabarit, "documents": etats, "attente_s": round(duree, 1),
                "passages": sum(e["chunks"] or 0 for e in etats.values())}

    def _assistant(self):
        if self.chat:
            return self.chat
        if self.ds is None:
            raise RuntimeError("aucun dataset Banc : lancer avec --reindexer")
        nom = f"Banc-{self.etiquette}"
        for c in self.rag.list_chats(name=nom):
            self.rag.delete_chats(ids=[c.id])
        self.chat = self.rag.create_chat(name=nom, dataset_ids=[self.ds.id], **self.reglages)
        return self.chat

    def demander(self, question):
        chat = self._assistant()
        sess = chat.create_session("banc")
        r, _ = demander(chat.id, sess.id, question, **self.extra)
        if r.get("code") != 0:
            raise RuntimeError(json.dumps(r, ensure_ascii=False)[:300])
        data = r["data"]
        ref = data.get("reference") or {}
        citations = []
        for c in (ref.get("chunks") or []):
            # positions : [[page, x1, x2, y1, y2], ...] (pages numérotées à partir de 1) ; un passage peut couvrir
            # plusieurs pages : une citation par page couverte, dans l'ordre d'apparition
            pages = list(dict.fromkeys(p[0] for p in (c.get("positions") or []) if isinstance(p, list) and p)) or [None]
            for page in pages:
                citations.append({"document": c.get("document_name"), "page": page,
                                  "extrait": (c.get("content") or "")[:200]})
        return {"reponse": data.get("answer") or "", "citations": citations}

    def config(self):
        chat = self._assistant() if self.ds else None
        cfg = {"version": "v1.0.0", "gabarit": self.gabarit, "modele": "gemma4:e4b (vLLM, LLM-Service service-vllm)",
               "embedding": "bge-m3 (vLLM)", "contexte_declare": contexte_declare(), "extra_question": self.extra}
        if chat:
            cfg.update({k: getattr(chat, k, None) for k in ("top_n", "top_k", "similarity_threshold",
                                                          "vector_similarity_weight", "keywords_similarity_weight",
                                                          "rerank_id", "llm_id")})
        return cfg


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--etiquette", default="defaut")
    p.add_argument("--gabarit", default="general")
    p.add_argument("--reindexer", action="store_true")
    p.add_argument("--limite", type=int)
    p.add_argument("--ids", nargs="*")
    p.add_argument("--top-n", type=int)
    p.add_argument("--seuil", type=float)
    p.add_argument("--poids-vecteurs", type=float)
    p.add_argument("--agentic", action="store_true", help="mode Agentic RAG (champ reasoning=5)")
    p.add_argument("--juge", action="store_true", help="juge LLM (Ollama) ; absent du banc GPU, désactivé par défaut")
    a = p.parse_args()
    reglages = {k: v for k, v in {"top_n": a.top_n, "similarity_threshold": a.seuil,
                                  "vector_similarity_weight": a.poids_vecteurs}.items() if v is not None}
    ad = AdaptateurRAGFlow(a.gabarit, a.etiquette, a.reindexer, reglages, {"reasoning": 5} if a.agentic else None)
    res = commun.lancer(ad, a.etiquette, APP, MODELES, indexer=ad.ds is None, juge=a.juge, limite=a.limite, ids=a.ids)
    res["config"] = ad.config()  # réglages de l'assistant, créé après l'indexation
    commun.ecrire(res, commun.RACINE / "outils/resultats/ragflow")
    print(json.dumps(res["synthese"], ensure_ascii=False, indent=1))
