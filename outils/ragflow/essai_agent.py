"""Agent créé depuis le gabarit « Your starter dataset chatbot », relié à la base « Démo Vélanor », interrogé par l'API
HTTP puis par le SDK. L'agent « Agent démo Vélanor » est gardé pour le jeu de démonstration.
Usage : uv run python outils/ragflow/essai_agent.py   Sortie : outils/resultats/ragflow/essai-<date>-agent.log
"""
import datetime, json, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from client import RACINE, client, http  # noqa: E402

NOM = "Agent démo Vélanor"
LLM = "chat@llm-central@OpenAI-API-Compatible"
lignes = [f"== {datetime.datetime.now().isoformat(timespec='seconds')} essai d'agent"]


def log(m):
    print(m, flush=True)
    lignes.append(str(m))


def regler(noeud, ds_id, n=None):
    """Renseigne dataset_ids et les llm_id vides partout dans le DSL ; compte les remplacements."""
    n = n if n is not None else {"dataset_ids": 0, "llm_id": 0}
    if isinstance(noeud, dict):
        for k, v in noeud.items():
            if k == "dataset_ids":
                noeud[k] = [ds_id]; n["dataset_ids"] += 1
            elif k == "llm_id" and not v:
                noeud[k] = LLM; n["llm_id"] += 1
            else:
                regler(v, ds_id, n)
    elif isinstance(noeud, list):
        for v in noeud:
            regler(v, ds_id, n)
    return n


rag = client()
ds = rag.list_datasets(name="Démo Vélanor")[0]
modeles = http("GET", "/agents/templates")["data"]
titres = [(m.get("title") or {}).get("en") if isinstance(m.get("title"), dict) else m.get("title") for m in modeles]
log(f"gabarits d'agents : {len(modeles)} ; {titres}")
gab = next(m for m, t in zip(modeles, titres) if t and "starter dataset" in t.lower())
dsl = gab["dsl"]
log(f"gabarit retenu : {gab.get('id')} ; composants : {list(dsl.get('components', {}).keys())}")
log(f"réglages appliqués : {regler(dsl, ds.id)}")
for a in http("GET", "/agents", params={"page_size": 100})["data"].get("canvas", []) if isinstance(
        http("GET", "/agents", params={"page_size": 100})["data"], dict) else []:
    if a.get("title") == NOM:
        http("DELETE", f"/agents/{a['id']}", json={})
r = http("POST", "/agents", json={"title": NOM, "dsl": dsl})
log(f"création : code {r.get('code')} {r.get('message')!r}")
agents = rag.list_agents()
agent = next(a for a in agents if a.title == NOM)
log(f"agent : {agent.id}")
r = http("POST", f"/agents/{agent.id}/sessions", json={})
sid = r["data"]["id"]
for q in ["Qui est le directeur de production de Vélanor ?",
          "Quel est le plafond des pénalités de retard du contrat Batterix ?"]:
    t = time.time()
    r = http("POST", "/agents/chat/completions", json={"agent_id": agent.id, "session_id": sid, "question": q, "stream": False})
    d = (r.get("data") or {}).get("data") or {}
    chunks = (d.get("reference") or {}).get("chunks") or []
    if isinstance(chunks, dict):
        chunks = list(chunks.values())
    log(f"HTTP, question : {q}\n  {time.time() - t:.1f} s ; code {r.get('code')} ; réponse : {str(d.get('content'))[:300]!r}\n"
        f"  documents en référence : {sorted({c.get('document_name') or c.get('docnm_kwd') for c in chunks})}")
try:
    t = time.time()
    sess = agent.create_session()
    msg = next(iter(sess.ask("Combien de salariés compte Vélanor au 31 décembre 2025 ?", stream=False)))
    log(f"SDK Agent.create_session + Session.ask : {time.time() - t:.1f} s ; {msg.content[:200]!r}")
except Exception as e:
    log(f"SDK Agent.create_session + Session.ask : ÉCHEC {type(e).__name__}: {str(e)[:300]}")
(RACINE / f"outils/resultats/ragflow/essai-{datetime.date.today()}-agent.log").write_text("\n".join(lignes) + "\n")
